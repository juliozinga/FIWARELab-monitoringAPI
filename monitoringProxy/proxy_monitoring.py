#!/usr/bin/env python
from __future__ import division
from bottle import route, run, request, error, response, Bottle, redirect, HTTPError, abort, HTTPResponse
from pymongo import MongoClient, database
from pymongo.errors import ServerSelectionTimeoutError
from bottle.ext.mongo import MongoPlugin
from bson.json_util import dumps
from paste import httpserver
from multiprocessing.pool import Pool
from multiprocessing import TimeoutError
from threading import Event, Thread
from usageData import *
import threading
import argparse
import ConfigParser
import sys
import time
import json
import urllib2
import requests
import datetime
import math
import bottle_mysql
import base64
import cookielib
import urllib
import copy
import decimal
import os
import traceback

###Main bottle app
app = Bottle()
#####

HEADER_AUTH = "X-Auth-Token"

class RepeatedTimer(object):
  def __init__(self, interval, function, *args):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.is_running = False
    self.next_call = time.time()
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args)

  def start(self):
    if not self.is_running:
      self.next_call += self.interval
      self._timer = threading.Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True
      print("token thread started")

  def stop(self):
    self._timer.cancel()
    self.is_running = False
    print("token thread stopped")
    
# Return if the token is authorized with auth_url
#def is_idm_authorized(auth_url, token_map):
    #try:
        #if HEADER_AUTH in token_map:
            #token_string = token_map[HEADER_AUTH]
        #elif "Authorization" in token_map:
            #token_string = base64.b64decode(token_map["Authorization"].split(" ")[1])
        #else:
            #raise Exception('Header not known')
    #except Exception as e:
        #print "Error in decoding token: " + str(e)
        #return False
    #try:
        #url_request = auth_url + "/user?access_token=" + token_string
        #headers = {}
        #headers['accept'] = 'application/json'
        #headers['user-group'] = 'none'
        #req = urllib2.Request(url_request)
        #req.headers = headers
        #response_idm = urllib2.urlopen(req)
        #UserJson = response_idm.read()
    #except Exception as e:
        #print "Error in authentication: " + str(e)
        #return False
    #return True

# Return if the org or app is authorized. Works with forked Pep-Proxy
def is_idm_authorized(request_headers, regionId):
    #if request_headers.get("Authorization") is not None:
        #token_string = base64.b64decode(request_headers.get("Authorization").split(" ")[1])
    #elif request_headers.get(HEADER_AUTH) is not None:
        #token_string = request_headers.get(HEADER_AUTH)
    
    if request_headers.get("X-App-Id") is not None:
        trusted_apps = json.loads(app.config['api']['trusted_app'])
        if request_headers.get("X-App-Id") in trusted_apps:
            return True
    elif request_headers.get("X-Organizations") is not None:
        for organization in request_headers.get("X-Organizations"):
            if organization["id"] == config_map['api']['admin_org'] or organization["id"] == config_map['api']['fed_man_org'] or organization["id"] == config_map['api']['sla_org'] or (organization["id"] == config_map['api']['io_org'] and organization["displayName"] == regionId):
                return True
    
    if strtobool(app.config["api"]["debugMode"]):
        print "["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] no X-App-Id or X-Organizations headers found"
    return False

# Get token from IDM
def get_token_auth(url, consumer_key, consumer_secret, username, password, convert_to_64=True):
    response_dict = {}
    try:
        headers = {}
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Authorization"] = "Basic " + base64.b64encode(consumer_key + ":" + consumer_secret)
        data = {"grant_type": "password", "username": username, "password": password}

        cookie_jar = cookielib.LWPCookieJar()
        cookie = urllib2.HTTPCookieProcessor(cookie_jar)
        opener = urllib2.build_opener(cookie)

        req = urllib2.Request(url, urllib.urlencode(data), headers)
        res = opener.open(req)
        response_dict = json.loads(res.read())
    except Exception as e:
        print (str)
        return None
    if convert_to_64:
        return base64.b64encode(response_dict["access_token"])
    else:
        return response_dict["access_token"]


'''
def request_to_idm(username, password, keypass_url, url):
    token = get_token_auth(username=username, password=password, url=keypass_url)
    req = urllib2.Request(url)
    if token:
        req.add_header('X-Subject-Token', token)
        response = urllib2.urlopen(req)
        return response
    return None
'''

def get_token_from_response(request):
    auth_map = {}
    if request is None:
        return auth_map
    if request.headers.get("Authorization") is not None:
        token = request.headers.get("Authorization").split(" ")[1]
        auth_map["Authorization"] = "Bearer " + token
    elif request.headers.get(HEADER_AUTH) is not None:
        token = request.headers.get(HEADER_AUTH)
        auth_map[HEADER_AUTH] = token
    return auth_map


@app.error(404)
def error404(error):
    response.content_type = 'application/json'
    return json.dumps({"ERROR": "NOT_FOUND"})


@app.error(401)
def error401(error):
    response.content_type = 'application/json'
    return json.dumps({"Error": "UNAUTHORIZED"})


'''
Return the url and port of monitoring to which forward the request.
If the regionId has old monitoring return the old monitoring url,
If the region has new monitoring return the new one
'''


def select_monitoring_to_forward(regionid):
    if is_region_new(regionid) or regionid is None:
        return app.config["newmonitoring"]["url"], app.config["newmonitoring"]["port"]
    else:
        return app.config["oldmonitoring"]["url"], app.config["oldmonitoring"]["port"]


'''
Return True if region use new monitoring system false otherwise
'''


def is_region_new(regionid):
    if is_region_on(regionid) and str2true(app.config["main_config"]["regionNew"][regionid]):
        return True
    return False


'''
Return region name of a region taht use new monitoring system regionid otherwise
'''


def get_region_name(regionid):
    region_name = app.config["main_config"]["regionNames"][regionid]
    if not region_name:
        return regionid
    return region_name

'''
Return region data(country,lat and lng) of a region that uses new monitoring system None otherwise
'''


def get_region_data(regionid):
    if regionid in app.config["main_config"]["regionData"]:
        region_data = app.config["main_config"]["regionData"][regionid]
        if not region_data:
            return []
        return json.loads(region_data)
    else:
        return None


'''
Return True if region is present (enabled) in configuration file
'''


def is_region_on(regionid):
    if regionid is None:
        return False
    if app.config["main_config"]["regionNew"].has_key(regionid):
        return True
    else:
        print "Region id not found in configuration file: " + str(regionid)
        return False


'''
Make the request to appropriate monitoringAPI and update the Bottle response
args:   request in the form: "/" or "/monitoring/regions" etc.
return empty array if error
'''


def fwd_request(request_url, request, regionid=None):
    try:
        my_response = do_http_get(request_url, request, regionid)
        response.status = my_response.getcode()
        if hasattr(my_response, 'headers'):
            response.set_header("Content-Type", my_response.info().getheader("Content-Type"))
        return my_response
    except urllib2.HTTPError, error:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request do_http_get httperror")
        raise error
        
    except urllib2.URLError, error:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request do_http_get urlerror")
        raise error
        
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request do_http_get exception")
        raise e
    


'''
Make the request to appropriate monitoringAPI and return raw http_response
args:   request in the form: "/" or "/monitoring/regions" etc.
return empty array if error
'''


def do_http_get(request_url, request, regionid=None):
    monitoring_url, monitoring_port = select_monitoring_to_forward(regionid)
    base_url = "http://" + monitoring_url + ":" + monitoring_port
    uri = ''
    if request is None or not request.query_string:
        uri = base_url + request_url
    else:
        uri = base_url + request_url + "?" + request.query_string
    req = urllib2.Request(uri)
    token_map = get_token_from_response(request)
    if bool(token_map):
        req.headers[token_map.iteritems().next()[0]] = token_map.iteritems().next()[1]
    my_response = None
    try:
        my_response = urllib2.urlopen(req)
    except urllib2.HTTPError, error:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] do_http_get httperror")
            print(traceback.format_exc())
        #print("In do_http_get except urllib2.HTTPError, error")
        #my_response = error
        raise error
    except urllib2.URLError, error:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] do_http_get urlerror")
            print(traceback.format_exc())
        #my_response = error
        raise error
        
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] do_http_get exception")
            print(traceback.format_exc())
        raise e
        
    return my_response


@app.route('/', method='GET')
def root():
    root_entity = {
        "_links": {
            "self": { 
                "href": "/" 
            },
            "regions": { 
                "href": "/monitoring/regions", 
                "templated": "true" 
            },
            "host2hosts": { 
                "href": "/monitoring/host2hosts", 
                "templated": "true" 
            }
        }
    }   
    
    return json.dumps(root_entity)


@app.route('/monitoring/regions', method='GET')
@app.route('/monitoring/regions/', method='GET')
def get_all_regions(mongodb, mongodbOld):
    all_regions = get_all_regions_from_monasca_influx()
    return all_regions


@app.route('/monitoring/regions/<regionid>', method='GET')
@app.route('/monitoring/regions/<regionid>/', method='GET')
def get_region(mongodb, regionid="ID of the region"):
    if not is_region_on(regionid):
        abort(404)
    if request.params.getone("since") is None:
        region = get_region_from_monasca_influx(regionid=regionid)
        
        if region is None:
            abort(404)
        elif region == 404:
            name = get_region_name(regionid)
            data = get_region_data(regionid)
            if data is None:
                abort(404)
            #print "{'name':"+name+", 'data':}"
            #print data
            #abort(404,{'name':name, 'data':data})
            response.status = 404
            response.content_type = 'application/json'
            return json.dumps({'name':name, 'data':data, 'ttl':int(app.config["api"]["regionTTL"])})
        else:
            return region
    else:
        #return fwd_request("/monitoring/regions/" + regionid, request=request, regionid=regionid)
        try:
            myresponse = fwd_request("/monitoring/regions/" + regionid, request=request, regionid=regionid)
            return myresponse
        except urllib2.HTTPError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/' httperror")
            abort(404)
        except urllib2.URLError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/' urlerror")
            abort(404)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/' exception")
            abort(404)


@app.route('/monitoring/regions/<regionid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/services/', method='GET')
def get_all_services_by_region(db, regionid="ID of the region"):
    if is_region_on(regionid):
        #return fwd_request("/monitoring/regions/" + regionid + "/services", request=request, regionid=regionid)
        try:
            myresponse = fwd_request("/monitoring/regions/" + regionid + "/services", request=request, regionid=regionid)
            return myresponse
        except urllib2.HTTPError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/services' httperror")
            abort(404)
        except urllib2.URLError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/services' urlerror")
            abort(404)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/services' exception")
            abort(404)
    else:
        abort(404)
        

@app.route('/monitoring/regions/<regionid>/hosts', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/', method='GET')
def get_all_hosts(mongodb, regionid="ID of the region"):    
    if not is_region_on(regionid):
        abort(404)
    if not is_idm_authorized(request.headers, regionid):
        abort(401)
    hosts = get_hosts_from_monasca(regionid)
    if hosts is not None:
        return hosts
    else:
        abort(404)
        

@app.route('/monitoring/regions/<regionid>/hosts/<hostid>', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/', method='GET')
def get_host(mongodb, regionid="ID of the region", hostid="ID of the host"):
    if not is_region_on(regionid):
        abort(404)
    if request.params.getone("since") is None:
        if not is_idm_authorized(request.headers, regionid):
            abort(401)
        #region = get_doc_region_from_mongo(mongodb, regionid)
        #host = get_host_from_mongo(mongodb, region, hostid)
        #host = get_host_from_monasca(regionid, hostid+"_"+hostid)
        host = get_host_from_influx(regionid, hostid+"_"+hostid)
        if host is not None:
            return host
        else:
            abort(404)
    else:
        #return fwd_request("/monitoring/regions/" + regionid + "/hosts/" + hostid, request=request, regionid=regionid)
        try:
            myresponse = fwd_request("/monitoring/regions/" + regionid + "/hosts/" + hostid, request=request, regionid=regionid)
            return myresponse
        except urllib2.HTTPError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/hosts/<hostid>' httperror")
            abort(404)
        except urllib2.URLError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/hosts/<hostid>' urlerror")
            abort(404)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/hosts/<hostid>' exception")
            abort(404)


@app.route('/monitoring/regions/<regionid>/vms', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/', method='GET')
def get_all_vms(regionid="ID of the region"):
    if not is_region_on(regionid):
        abort(404)
    if not is_idm_authorized(request.headers, regionid):
        abort(401)
    vms = get_vms_from_influx(regionid)
    if vms is not None:
        return vms
    else:
        abort(404)
        

@app.route('/monitoring/regions/<regionid>/vmsdetails', method='GET')
@app.route('/monitoring/regions/<regionid>/vmsdetails/', method='GET')
def get_all_vmsdetails(regionid="ID of the region"):
    if is_region_on(regionid):
        try:
            myresponse = fwd_request("/monitoring/regions/" + regionid + "/vmsdetails/", request=request, regionid=regionid)
            return myresponse
        except urllib2.HTTPError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/vmsdetails' httperror")
            abort(404)
        except urllib2.URLError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/vmsdetails' urlerror")
            abort(404)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/vmsdetails' exception")
            abort(404)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/vms/<vmid>', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/', method='GET')
def get_vm(regionid="ID of the region", vmid="ID of the vm"):        
    if not is_region_on(regionid):
        abort(404)
    if not is_idm_authorized(request.headers, regionid):
        abort(401)
    vm = get_vm_from_influx(regionid, vmid)
    if vm is not None:
        return vm
    else:
        abort(404)     


@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/', method='GET')
def get_all_services_by_host(regionid="ID of the region", hostid="ID of the host"):
    if is_region_on(regionid):
        try:
            myresponse = fwd_request("/monitoring/regions/" + regionid + "/hosts/" + hostid + "/services", request=request,
                           regionid=regionid)
            return myresponse
        except urllib2.HTTPError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/hosts/<hostid>/services' httperror")
            abort(404)
        except urllib2.URLError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/hosts/<hostid>/services' urlerror")
            abort(404)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/hosts/<hostid>/services' exception")
            abort(404)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>/', method='GET')
def get_service_by_host(regionid="ID of the region", hostid="ID of the host", serviceName="Service name"):
    if is_region_on(regionid):

        try:
            myresponse = fwd_request("/monitoring/regions/" + regionid + "/hosts/" + hostid + "/services/" + serviceName,
                           request=request, regionid=regionid)
            return myresponse
        except urllib2.HTTPError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>' httperror")
            abort(404)
        except urllib2.URLError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>' urlerror")
            abort(404)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>' exception")
            abort(404)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/', method='GET')
def get_all_services_by_vm(regionid="ID of the region", vmid="ID of the vm"):
    if is_region_on(regionid):
        
        try:
            myresponse = fwd_request("/monitoring/regions/" + regionid + "/vms/" + vmid + "/services", request=request,
                           regionid=regionid)
            return myresponse
        except urllib2.HTTPError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/vms/<vmid>/services' httperror")
            abort(404)
        except urllib2.URLError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/vms/<vmid>/services' urlerror")
            abort(404)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/vms/<vmid>/services' exception")
            abort(404)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>/', method='GET')
def get_service_by_vm(regionid="ID of the region", vmid="ID of the vm", serviceName="Service name"):
    if is_region_on(regionid):

        try:
            myresponse = fwd_request("/monitoring/regions/" + regionid + "/vms/" + vmid + "services/" + serviceName,
                           request=request, regionid=regionid)
            return myresponse
        except urllib2.HTTPError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>' httperror")
            abort(404)
        except urllib2.URLError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>' urlerror")
            abort(404)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>' exception")
            abort(404)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/nes', method='GET')
@app.route('/monitoring/regions/<regionid>/nes/', method='GET')
def get_all_nes(regionid="ID of the region"):
    if is_region_on(regionid):

        try:
            myresponse = fwd_request("/monitoring/regions/" + regionid + "/nes/", request=request, regionid=regionid)
            return myresponse
        except urllib2.HTTPError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/nes' httperror")
            abort(404)
        except urllib2.URLError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/nes' urlerror")
            abort(404)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/nes' exception")
            abort(404)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/nes/<neid>', method='GET')
@app.route('/monitoring/regions/<regionid>/nes/<neid>/', method='GET')
def get_ne(regionid="ID of the region", neid="ID of the network"):
    if is_region_on(regionid):

        try:
            myresponse = fwd_request("/monitoring/regions/" + regionid + "/nes/" + neid, request=request, regionid=regionid)
            return myresponse
        except urllib2.HTTPError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/nes/<neid>' httperror")
            abort(404)
        except urllib2.URLError, error:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/nes/<neid>' urlerror")
            abort(404)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] fwd_request @app.route '/monitoring/regions/<regionid>/nes/<neid>' exception")
            abort(404)
    else:
        abort(404)


@app.route('/monitoring/host2hosts', method='GET')
@app.route('/monitoring/host2hosts/', method='GET')
def get_host2hosts():
    print "Call to forward"
    return {}


@app.route('/monitoring/regions/<regionid>/images', method='GET')
@app.route('/monitoring/regions/<regionid>/images/', method='GET')
def get_all_images_by_region(mongodb, regionid="ID of the region"):
    if not is_region_on(regionid):
        abort(404)
    if is_idm_authorized(request.headers, regionid):
        images = get_all_images_from_mongo(mongodb=mongodb)
        return json.dumps(images)  # return {'To be implemented'}
    else:
        abort(401)    


@app.route('/monitoring/regions/<regionid>/images/<imageid>', method='GET')
@app.route('/monitoring/regions/<regionid>/images/<imageid>/', method='GET')
def get_image_by_region(mongodb, regionid="ID of the region", imageid="Image id"):
    if not is_region_on(regionid):
        abort(404)
    if is_idm_authorized(request.headers, regionid):
        image = get_image_from_mongo(mongodb=mongodb, imageid=imageid, regionid=regionid)
        return json.dumps(image)
    else:
        abort(401)    


@app.route('/usagedata/toptenants', method='GET')
@app.route('/usagedata/toptenants/', method='GET')
def get_ud_toptenants(mongodb):
    sort_criteria = request.params.getone("sort")
    if valid_sort(sort_criteria):
        toptenants = get_toptenants(mongodb, app.config, sort_criteria)
    else:
        toptenants = get_toptenants(mongodb, app.config)
    response.set_header("Content-Type", "application/json")
    return json.dumps(toptenants)


'''
Base structure to use in the list request
'''
base_dict_list = {
    "_links": {
        "self": {
            "href": ""
        }
    },
    "id": ""
}

all_region_parameters_mapping = {
    "total_nb_cores": "nb_cores",
    "total_nb_cores_enabled": "nb_cores_enabled",
    "total_nb_ram": "nb_ram",
    "total_nb_disk": "nb_disk",
    "total_nb_vm": "nb_vm",
    "total_ip_assigned": "ipAssigned",
    "total_ip_allocated": "ipAllocated",
    "total_ip": "ipTot"}

# Mongo --------------------------------------------------------------------------------

def get_all_regions_from_js():
    
    try:
        response = do_http_get("/monitoring/regions", request=None)
        if response.getcode() == 200:
            return json.loads(response.read())
        else:
            raise Exception('Call to /monitoring/regions did not return 200 code')
            
    except urllib2.HTTPError, error:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_regions_from_js do_http_get httperror")
        raise error
        
    except urllib2.URLError, error:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_regions_from_js do_http_get urlerror")
        raise error
        
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_regions_from_js do_http_get exception")
        raise e


#def get_all_regions_from_mongo(mongodb, mongodbOld):
    #regions_entity = {
        #"_links": {
            #"self": {
                #"href": "/monitoring/regions"
            #}
        #},
        #"_embedded": {
            #"regions": [
            #]
        #},
        #"basicUsers": 0,
        #"trialUsers": 0,
        #"communityUsers": 0,
        #"totalUsers": 0,
        #"total_nb_users": 0,
        #"totalCloudOrganizations": 0,
        #"totalUserOrganizations": 0,
        #"total_nb_organizations": 0,
        ##
        #"total_nb_cores": 0,
        #"total_nb_cores_enabled": 0,
        #"total_nb_ram": 0,
        #"total_nb_disk": 0,
        #"total_nb_vm": 0,
        #"total_ip_assigned": 0,
        #"total_ip_allocated": 0,
        #"total_ip": 0
    #}

    #pool = None
    #async_result= None
    
    #try:
        #pool = Pool(processes=1, maxtasksperchild=25)
        #async_result = pool.apply_async(get_all_regions_from_js, ()) # Start thread for async http call
    #except Exception as e:
        #if strtobool(app.config["api"]["debugMode"]):
            #print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_regions_from_js exception in creating fork.")
            #print(traceback.format_exc())
        #if pool:
            #pool.terminate()
            #pool.join()
            #pool = None
        #async_result= None

    #new_regions = app.config["main_config"]["regionNew"]
    #region_list = {}

    #for region_id, is_new in new_regions.iteritems():
        #if str2true(is_new):            
            #try:
                #region = get_region_from_mongo(mongodb, region_id)
                #if region is not None:
                    #region_list[region_id] = region
                ##if region is not in mongo, but we have its coordinates and country, we add it to the list
                #elif not region and get_region_data(region_id):
                    #region_item = {"id": {}, "_links": {"self": {"href": {}}}}
                    #region_item["id"] = region_id
                    #region_item["_links"]["self"]["href"] = "/monitoring/regions/" + region_id
                    #regions_entity["_embedded"]["regions"].append(copy.deepcopy(region_item))
            #except ServerSelectionTimeoutError as e:
                #if strtobool(app.config["api"]["debugMode"]):
                    #print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_regions_from_mongo get_region_from_mongo ServerSelectionTimeoutError for"+region_id)
                #break            
        #elif str2false(is_new):
            #try:
                #my_response = do_http_get("/monitoring/regions/" + region_id, request=None, regionid=region_id)
                #if my_response.getcode() == 200:
                    #region_list[region_id] = json.loads(my_response.read())
            #except urllib2.HTTPError, error:
                #if strtobool(app.config["api"]["debugMode"]):
                    #print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_regions_from_mongo do_http_get '/monitoring/regions/" + region_id +"' httperror")
                
            #except urllib2.URLError, error:
                #if strtobool(app.config["api"]["debugMode"]):
                    #print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_regions_from_mongo do_http_get '/monitoring/regions/" + region_id +"' urlerror")
                
            #except Exception as e:
                #if strtobool(app.config["api"]["debugMode"]):
                    #print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_regions_from_mongo do_http_get '/monitoring/regions/" + region_id +"' exception")     
        #else:
            #continue

    #if region_list:
        #for region in region_list.iteritems():
            #region = region[1]
            #region_item = {"id": {}, "_links": {"self": {"href": {}}}}
            #region_item["id"] = region["id"]
            #region_item["_links"]["self"]["href"] = "/monitoring/regions/" + region["id"]
            #regions_entity["_embedded"]["regions"].append(copy.deepcopy(region_item))
            ## sum resources form each region entity
            #if region["nb_cores"] != '':
                #regions_entity["total_nb_cores"] += int(region["nb_cores"])
                #regions_entity["total_nb_cores_enabled"] += int(region["nb_cores"])
            #if region["nb_ram"] != '':
                #regions_entity["total_nb_ram"] += int(region["nb_ram"])
            #if region["nb_disk"] != '':
                #regions_entity["total_nb_disk"] += int(region["nb_disk"])
            #if region["nb_vm"] != '':
                #regions_entity["total_nb_vm"] += int(region["nb_vm"])
            #if region["measures"][0]["ipAssigned"] != '':
                #regions_entity["total_ip_assigned"] += int(decimal.Decimal(region["measures"][0]["ipAssigned"]).normalize())
            #if region["measures"][0]["ipAllocated"] != '':
                #regions_entity["total_ip_allocated"] += int(
                    #decimal.Decimal(region["measures"][0]["ipAllocated"]).normalize())
            #if region["measures"][0]["ipTot"] != '':
                #regions_entity["total_ip"] += int(decimal.Decimal(region["measures"][0]["ipTot"]).normalize())
    #else:
        ##regions ids are taken from config file because mongo probably is down
        #for region in app.config["main_config"]["regionNew"]:
            #region_item = {"id": {}, "_links": {"self": {"href": {}}}}
            #region_item["id"] = region
            #region_item["_links"]["self"]["href"] = "/monitoring/regions/" + region
            #regions_entity["_embedded"]["regions"].append(copy.deepcopy(region_item))

    ## get IDM infos from oldMonitoring
    #regions_tmp = None
    #if async_result == None:
        #try:
            #my_response = do_http_get("/monitoring/regions", request=None)
            #if my_response.getcode() == 200:
                #regions_tmp = json.loads(my_response.read())
        #except Exception as e:
            #if strtobool(app.config["api"]["debugMode"]):
                #print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_regions_from_mongo do_http_get('/monitoring/regions', request=None) exception")
                #print(traceback.format_exc())
    #else:
        #try:
            #regions_tmp = async_result.get(timeout=int(app.config["monasca"]["timeout"]))  # get the return value from thread
        #except TimeoutError:
            #if strtobool(app.config["api"]["debugMode"]):
                #print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to JS monitoringAPI to retrieve IDM info did not respond in "+app.config["monasca"]["timeout"]+" seconds. No IDM data returned")
        #except Exception as e:
            #if strtobool(app.config["api"]["debugMode"]):
                #print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_regions_from_js exception")
                #print(traceback.format_exc())
        #finally:
            #pool.terminate()
            #pool.join()
    
    #if regions_tmp != None:
        #regions_entity["basicUsers"] = regions_tmp["basicUsers"]
        #regions_entity["trialUsers"] = regions_tmp["trialUsers"]
        #regions_entity["communityUsers"] = regions_tmp["communityUsers"]
        #regions_entity["totalUsers"] = regions_tmp["totalUsers"]
        #regions_entity["total_nb_users"] = regions_tmp["total_nb_users"]
        #regions_entity["totalCloudOrganizations"] = regions_tmp["totalCloudOrganizations"]
        #regions_entity["totalUserOrganizations"] = regions_tmp["totalUserOrganizations"]
        #regions_entity["total_nb_organizations"] = regions_tmp["total_nb_organizations"]
    
    #regions_entity["total_nb_vm"] = get_number_of_active_vms_from_influx()
    #return regions_entity


'''
mongodb is the local mongodb bottle plugin
filter_region should be the region name, used to filter the images.
If no filter_region append all region...
'''


def get_all_images_from_mongo(mongodb, filter_region=None):
    result = None
    try:
        result = mongodb[app.config["mongodb"]["collectionname"]].find({"_id.type": "image"})
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print(traceback.format_exc())

    result_dict = {"image": []}
    
    if result != None:
        for image in result:
            if filter_region is not None:
                if image["_id"]["id"].find(filter_region) != -1:
                    base_dict_list["_links"]["self"]["href"] = "/monitoring/regions/" + filter_region + "/images/" + \
                                                            image["_id"]["id"]
                    base_dict_list["id"] = image["_id"]["id"]
                    result_dict["image"].append(base_dict_list)
            else:
                # This else will be removed. Used only for test as long as we have not a new mongodb in Spain and must use fake mongo
                base_dict_list["_links"]["self"]["href"] = "/monitoring/regions/--NOFILTER--/images/" + image["_id"]["id"]
                base_dict_list["id"] = image["_id"]["id"]
                result_dict["image"].append(base_dict_list)
                
    return result_dict


def get_image_from_mongo(mongodb, imageid, regionid):
    result = None
    try:
        result = mongodb[app.config["mongodb"]["collectionname"]].find(
            {"$and": [{"_id.type": "image"}, {"_id.id": {"$regex": imageid}}]})
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print(traceback.format_exc())
            
    result_dict = {"details": []}
    
    if result != None:
        for image in result:
            result_dict["details"].append(image)
            
    return result_dict

def get_cursor_vms_from_mongo(mongodb, regionid):
    vms = []
    try:
        vms = mongodb[app.config["mongodb"]["collectionname"]].find(
            {"$and": [{"_id.type": "vm"}, {"_id.id": {"$regex": regionid + ':'}}]})
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_cursor_vms_from_mongo "+regionid)
            print(traceback.format_exc())                    
    
    if vms.count() >= 1:
        return vms
    else:
        return None


def get_cursor_active_vms_from_mongo(mongodb, regionid):

    now = utils.get_timestamp()
    ts_limit = now - int(app.config["api"]["vmTTL"])
    vms = []
    if strtobool(app.config["api"]["vmCheckActive"]):
        try:
            vms = mongodb[app.config["mongodb"]["collectionname"]].find(
                {"$and":[{"_id.type":"vm"},{"_id.id": {"$regex": regionid + ':'}},
                {"attrs.status.value":"active"},{"modDate":{"$gt":ts_limit}}]}
            )
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_cursor_active_vms_from_mongo "+regionid)
                print(traceback.format_exc())
    else:
        try:
            vms = mongodb[app.config["mongodb"]["collectionname"]] \
                .find({"$and":[{"_id.type":"vm"},{"_id.id": {"$regex": regionid + ':'}},{"modDate":{"$gt":ts_limit}}]})
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_cursor_active_vms_from_mongo "+regionid)
                print(traceback.format_exc())
         
    if vms.count() >= 1:
        return vms
    else:
        return None


def get_cursor_hosts_from_mongo(mongodb, regionid):
    hosts = []
    try:
        hosts = mongodb[app.config["mongodb"]["collectionname"]].find(
            {"$and": [{"_id.type": "host"}, {"_id.id": {"$regex": regionid + ':'}}]})
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_cursor_hosts_from_mongo "+regionid)
            print(traceback.format_exc())
                
    if hosts.count() >= 1:
        return hosts
    else:
        return None


def get_doc_host_from_mongo(mongodb, regionid, hostid):
    result = None
    try:
        result = mongodb[app.config["mongodb"]["collectionname"]].find_one(
            {"$and": [{"_id.type": "host"}, {"_id.id": {"$regex": regionid + ':' + hostid}}]})
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_doc_host_from_mongo "+regionid)
            print(traceback.format_exc())
    return result


def get_doc_region_from_mongo(mongodb, regionid):    
    result = None
    try:
        result = mongodb[app.config["mongodb"]["collectionname"]].find_one(
            {"$and": [{"_id.type": "region"}, {"_id.id": regionid}]})
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_doc_region_from_mongo "+regionid)
            print(traceback.format_exc())
    return result


def aggr_vms_data(vms):
    """
    Function that aggregate vm entity data given a collection (cursor retuned from mongo query) of vms
    """
    vms_data = {"nb_vm": 0}
    vms_data["nb_vm"] = vms.count()
    return vms_data


def aggr_hosts_data(hosts, regionid=None):
    """
    Function that aggregate host entity data given a collection (cursor retuned from mongo query) of hosts
    """
    hosts_data = {"ramTot": 0, "diskTot": 0, "cpuTot": 0, "cpuNow": 0, "ramNowTot": 0, "diskNowTot": 0}
    for host in hosts:
        if host.get("attrs", {}).has_key("ramTot"):
            hosts_data["ramTot"] += int(host["attrs"]["ramTot"]["value"])
        if host.get("attrs", {}).has_key("diskTot"):
            hosts_data["diskTot"] += int(host["attrs"]["diskTot"]["value"])
        if host.get("attrs", {}).has_key("cpuTot"):
            hosts_data["cpuTot"] += int(host["attrs"]["cpuTot"]["value"])
        if host.get("attrs", {}).has_key("cpuNow"):
            hosts_data["cpuNow"] += int(host["attrs"]["cpuNow"]["value"])
        if host.get("attrs", {}).has_key("ramNow"):
            hosts_data["ramNowTot"] += int(host["attrs"]["ramNow"]["value"])
        if host.get("attrs", {}).has_key("diskNow"):
            hosts_data["diskNowTot"] += int(host["attrs"]["diskNow"]["value"])
    # Workaround to adjust storage amount if Ceph is used
    cephStorageRegions = json.loads(app.config["api"]["regionsCephStorage"])
    if regionid in cephStorageRegions:
        hosts_data["diskTot"] = hosts_data["diskTot"] / hosts.count()
    return hosts_data

# end Mongo -----------------------------------------------------------------------------
# Monasca -------------------------------------------------------------------------------

#update the token in the parent collector
def update_token_of_parent_collector():
    collector.update_token()    

#get the last measurement looking its timestamp
def get_last_monasca_measurement(measurements_dict):
    if measurements_dict.has_key("measurements"):  
        measurements = measurements_dict["measurements"]
        if measurements and len(measurements) > 0:
            #sort measurements for timestamp and take the last one
            sorted_measurements = sorted(measurements, key=lambda x : x[0])
            last_measurement = sorted_measurements[len(sorted_measurements)-1]
            return last_measurement
    return None
  
#get from Monasca the updated metadata and the number of total ips (region.pool_ip) for all regions or for a specified one
def get_metadata_from_monasca(regionid = None):
    start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["regionTTL"]))
    start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    return collector.get_pool_ip_for_region(start_timestamp, regionid)

#get from Monasca the updated number of total ips and other metadata (region.pool_ip) for all regions as a Dictionary region:#ips,#basicUsers....
def get_total_ip_pool_normalized_from_monasca():
    total_ips = {}
    total_ip_for_regions = get_metadata_from_monasca()
    
    if total_ip_for_regions and len(total_ip_for_regions):
        
        for total_ip_for_region in total_ip_for_regions:
            
            if total_ip_for_region.has_key("dimensions") and total_ip_for_region["dimensions"].has_key("region") and is_region_on(total_ip_for_region["dimensions"]["region"]):
                
                last_total_ip_for_region = get_last_monasca_measurement(total_ip_for_region)
                if last_total_ip_for_region and len(last_total_ip_for_region) > 2:
                    pool_data = {}
                    pool_data["ips"] = last_total_ip_for_region[1]
                    pool_data["basicUsers"] = 0
                    pool_data["trialUsers"] = 0
                    pool_data["communityUsers"] = 0
                    pool_data["totalUsers"] = 0
                    pool_data["totalCloudOrganizations"] = 0
                    pool_data["totalUserOrganizations"] = 0 
                    if last_total_ip_for_region[2].has_key('basicUsers'):
                        pool_data["basicUsers"] = last_total_ip_for_region[2]["basicUsers"]
                    if last_total_ip_for_region[2].has_key('trialUsers'):
                        pool_data["trialUsers"] = last_total_ip_for_region[2]["trialUsers"]
                    if last_total_ip_for_region[2].has_key('communityUsers'):
                        pool_data["communityUsers"] = last_total_ip_for_region[2]["communityUsers"]
                    if last_total_ip_for_region[2].has_key('totalUsers'):
                        pool_data["totalUsers"] = last_total_ip_for_region[2]["totalUsers"]
                    if last_total_ip_for_region[2].has_key('totalCloudOrganizations'):
                        pool_data["totalCloudOrganizations"] = last_total_ip_for_region[2]["totalCloudOrganizations"]
                    if last_total_ip_for_region[2].has_key('totalUserOrganizations'):
                        pool_data["totalUserOrganizations"] = last_total_ip_for_region[2]["totalUserOrganizations"]
                    total_ips[total_ip_for_region["dimensions"]["region"]] = pool_data
                
    return total_ips

#get from Monasca the updated number of allocated ips (region.allocated_ip) for all regions or for a specified one
def get_ip_available_from_monasca(regionid = None):
    start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["regionTTL"]))
    start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    return collector.get_allocated_ip_for_region(start_timestamp, regionid)

#get from Monasca the updated number of allocated ips (region.allocated_ip) for all regions as a Dictionary region:#ips
def get_total_ip_available_normalized_from_monasca():
    allocated_ips = {}
    allocated_ip_for_regions = get_ip_available_from_monasca()
    
    if allocated_ip_for_regions and len(allocated_ip_for_regions):
        
        for allocated_ip_for_region in allocated_ip_for_regions:
            
            if allocated_ip_for_region.has_key("dimensions") and allocated_ip_for_region["dimensions"].has_key("region") and is_region_on(allocated_ip_for_region["dimensions"]["region"]):
                
                last_allocated_ip_for_region = get_last_monasca_measurement(allocated_ip_for_region)
                if last_allocated_ip_for_region and len(last_allocated_ip_for_region) > 1:
                    allocated_ips[allocated_ip_for_region["dimensions"]["region"]] = last_allocated_ip_for_region[1]
                
    return allocated_ips

#get from Monasca the updated number of used ips (region.used_ip) for all regions or for a specified one
def get_ip_used_from_monasca(regionid = None):
    start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["regionTTL"]))
    start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    return collector.get_used_ip_for_region(start_timestamp, regionid)

#get from Monasca the updated number of used ips (region.used_ip) for all regions as a Dictionary region:#ips
def get_total_ip_used_normalized_from_monasca():
    used_ips = {}
    used_ip_for_regions = get_ip_used_from_monasca()
    if used_ip_for_regions and len(used_ip_for_regions):
        
        for used_ip_for_region in used_ip_for_regions:
            
            if used_ip_for_region.has_key("dimensions") and used_ip_for_region["dimensions"].has_key("region") and is_region_on(used_ip_for_region["dimensions"]["region"]):
                
                last_used_ip_for_region = get_last_monasca_measurement(used_ip_for_region)
                if last_used_ip_for_region and len(last_used_ip_for_region) > 1:
                    used_ips[used_ip_for_region["dimensions"]["region"]] = last_used_ip_for_region[1]
                
    return used_ips

#get from Monasca a set of resources ids for a given metric and a region 
def get_resources_for_metric(regionid,metricName):
    return collector.get_resources_for_metric(regionid,metricName)

#get from Monasca a set of resources ids from measurements for a given metric and a region 
def get_measurements_resources_for_metric(regionid,metricName):
    start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["regionTTL"]))
    start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    return collector.get_measurements_resources_for_metric(regionid,metricName,start_timestamp)

#get from Monasca a set of measurements for a given metric and an optional region 
#def get_measurements_for_metric(metricName, regionid = None):
    #start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["regionTTL"]))
    #start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    #return [metricName,collector.get_measurements_for_metric(metricName,start_timestamp,regionid)]

#get from Monasca the updated hosts measurements for a given metric, region and host
#not used at the moment because Influx is more performant
#def get_measurements_for_hostname(regionid,metricName,hostname):	
    #start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["hostTTL"]))
    #start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    #return collector.get_measurements_for_hostname(regionid,metricName,hostname,start_timestamp)


#get a set of all hosts ids (active and inactive) for a given region (checking all the compute metrics specified in the config file)
'''
def get_all_region_hostnames(regionid, active = True):
    metricsNames = json.loads(app.config["metrics"]["computeMetrics"])
    hostnames = set()
    pool = None
    try:
        pool = Pool(processes=len(metricsNames),maxtasksperchild=25)
    
        async_results = [pool.apply_async(get_resources_for_metric, (regionid,metricName)) for metricName in metricsNames]
        for res in async_results:
            try:
                hostnames = hostnames.union(res.get(timeout=int(app.config["monasca"]["timeout"])))
            except TimeoutError:
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve '"+regionid+"' region metrics did not respond in "+app.config["monasca"]["timeout"]+" seconds. No metrics data returned")
            except Exception as e:
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_resources_for_metric exception (for '"+regionid+"')")
                    print(traceback.format_exc())
        
        pool.terminate()
        pool.join()
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_region_hostnames exception (for '"+regionid+"') in opening forks")
            print(traceback.format_exc())
        for metricName in metricsNames:
            try:
                result = get_resources_for_metric(regionid,metricName)
                hostnames = hostnames.union(result)
            except Exception as e:
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_resources_for_metric exception (for '"+regionid+"' and metric: '"+metricName+"')")
                    print(traceback.format_exc())
        if pool:
            pool.terminate()
            pool.join()
    
    pool = None
    if(active):        
        hostnames_active = []
        
        if(len(hostnames) >0):
            
            try:
                pool = Pool(processes=len(hostnames),maxtasksperchild=25)
        
                async_results = [pool.apply_async(is_region_hostname_active, (regionid,hostname)) for hostname in hostnames]
        
                for res in async_results:
                    try:
                        result = res.get(timeout=int(app.config["monasca"]["timeout"]))
                        if result and len(result) > 0:          
                            hostnames_active.append(result)
                
                    except TimeoutError:
                        if strtobool(app.config["api"]["debugMode"]):
                            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to check if hostname of region '"+regionid+"' was active (checking its measures) did not respond in "+app.config["monasca"]["timeout"]+" seconds. No measurements data returned")
                    except Exception as e:
                        if strtobool(app.config["api"]["debugMode"]):
                            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] is_region_hostname_active exception (for '"+regionid+"')")
                            print(traceback.format_exc())
                pool.terminate()
                pool.join()
            except Exception as e:
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_region_hostnames exception (for '"+regionid+"') in opening forks")
                    print(traceback.format_exc())
                for hostname in hostnames:
                    try:
                        result = is_region_hostname_active(regionid,hostname)
                        if result and len(result) > 0:          
                            hostnames_active.append(result)
                    except Exception as e:
                        if strtobool(app.config["api"]["debugMode"]):
                            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] is_region_hostname_active exception (for '"+regionid+"' and hostname: '"+hostname+"')")
                            print(traceback.format_exc())
                if pool:
                    pool.terminate()
                    pool.join()
        #for hostname in hostnames:
            #if is_region_hostname_active(regionid,hostname):
                #hostnames_active.append(hostname)
        return hostnames_active
    return hostnames
'''

#get a set of all hosts ids (active) for a given region (checking all the computeMetricForActiveHost specified in the config file)
def get_all_active_region_hostnames(regionid):
    
    metricsNames = json.loads(app.config["metrics"]["computeMetricForActiveHost"])
    hostnames = set()
    pool = None
    try:
        pool = Pool(processes=len(metricsNames),maxtasksperchild=25)
    
        async_results = [pool.apply_async(get_measurements_resources_for_metric, (regionid,metricName)) for metricName in metricsNames]
        for res in async_results:
            try:
                hostnames = hostnames.union(res.get(timeout=int(app.config["monasca"]["timeout"])))
            except TimeoutError:
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve '"+regionid+"' region metrics did not respond in "+app.config["monasca"]["timeout"]+" seconds. No metrics data returned")
            except Exception as e:
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_measurements_resources_for_metric exception (for '"+regionid+"')")
                    print(traceback.format_exc())
        
        pool.terminate()
        pool.join()
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_active_region_hostnames exception (for '"+regionid+"') in opening forks")
            print(traceback.format_exc())
        for metricName in metricsNames:
            try:
                result = get_measurements_resources_for_metric(regionid,metricName)
                hostnames = hostnames.union(result)
            except Exception as e:
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_measurements_resources_for_metric exception (for '"+regionid+"' and metric: '"+metricName+"')")
                    print(traceback.format_exc())
        if pool:
            pool.terminate()
            pool.join()
    
    pool = None
    return hostnames

#check if a region host is active or not, looking if all of its metrics' mesurements is updated
#def is_region_hostname_active(regionid,hostname):
    #metricsNames = json.loads(app.config["metrics"]["computeMetrics"])
    #pool = Pool(processes=len(metricsNames))
    
    #async_results = [pool.apply_async(get_measurements_for_hostname, (regionid,metricName,hostname)) for metricName in metricsNames]
    ##metric_not_empty_count = 0
    #for res in async_results:
        #try:
            #result = res.get(timeout=5)
            #if result and len(result) > 0 and result[0].has_key("measurements"):                
                #if len(result[0]["measurements"]) > 0:
                    #pool.terminate()
                    #pool.join()
                    ##metric_not_empty_count += 1
                    #return True
                
        #except TimeoutError:
            #print("HTTP call to monasca API to retrieve measurements for hostname did not respond in 5 seconds. No measurements data returned")
    #pool.terminate()
    #pool.join()
    ##if metric_not_empty_count == len(metricsNames):
        ##return True
    #return False

#check if a region host is active or not, looking if at least one of its metrics' mesurements is updated
#def is_region_hostname_active(regionid,hostname):
    #metricsNames = json.loads(app.config["metrics"]["computeMetrics"])
    
    #for metricName in metricsNames:
        #try:
            #result = get_measurements_for_hostname(regionid,metricName,hostname)
            #if result and len(result) > 0 and result[0].has_key("measurements"):                
                #if len(result[0]["measurements"]) > 0:
                    #return hostname               
        #except Exception:
            #if strtobool(app.config["api"]["debugMode"]):
                #print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve measurements for hostname (in order to check if it is active) gave error. No measurements data returned")
                #print(traceback.format_exc())
    #return False

#get host entity list dict for a given region
def get_hosts_from_monasca(regionid):
    hostnames = get_all_active_region_hostnames(regionid) 
    
    result_dict = {"hosts": [], "links": {"self": {"href": "/monitoring/regions/" + regionid + "/hosts"}}}
    if hostnames and len(hostnames):
        for hostname in hostnames:
            #if is_region_hostname_active(regionid,hostname):
            hostid = hostname.split("_")[0]
            base_dict_list["_links"]["self"]["href"] = "/monitoring/regions/" + regionid + "/hosts/" + hostid
            base_dict_list["id"] = hostid
            result_dict["hosts"].append(copy.deepcopy(base_dict_list))

    return result_dict 

#get host measurements for a given region and host (metrics specified in config file)
'''
def get_host_measurements_from_monasca(regionid,hostname,parallel = True):
    metricsNames = json.loads(app.config["metrics"]["computeMetrics"])
    
    if(parallel):
        pool = None
        try:

            pool = Pool(processes=len(metricsNames),maxtasksperchild=25)
    
            measurements = {}
    
            async_results = [pool.apply_async(get_measurements_for_hostname, (regionid,metricName,hostname)) for metricName in metricsNames]

            for res in async_results:
                try:
                    result = res.get(timeout=int(app.config["monasca"]["timeout"]))
                    if result and len(result) > 0 and result[0].has_key("name"):        
                        last_measurement = get_last_monasca_measurement(result[0])
                        if last_measurement and len(last_measurement) > 1:
                            measurements_data = {}                    
                            measurements_data["value"] = last_measurement[1]
                            #timestamp is a Datetime
                            measurements_data["timestamp"] =  histo_utils.from_monasca_ts_to_datetime_ms(last_measurement[0])
                            metric_name = result[0]["name"]
                            measurements[metric_name] = measurements_data
                            if (measurements.has_key("timestamp") and measurements["timestamp"] < measurements_data["timestamp"]) or not (measurements.has_key("timestamp")):
                                measurements["timestamp"] = measurements_data["timestamp"]
                            #print metric_name+" -- "+last_measurement[0]+" -- "+str(last_measurement[1])
                
                except TimeoutError:
                    if strtobool(app.config["api"]["debugMode"]):
                        print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve measurements for hostname '"+hostname+"' of region '"+regionid+"' did not respond in "+app.config["monasca"]["timeout"]+" seconds. No measurements data returned")
                except Exception as e:
                    if strtobool(app.config["api"]["debugMode"]):
                        print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_measurements_for_hostname exception (for hostname '"+hostname+"' of region '"+regionid+"')")
                        print(traceback.format_exc())
            pool.terminate()
            pool.join()
            return measurements
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_host_measurements_from_monasca exception (for hostname '"+hostname+"' of region '"+regionid+"') in creating fork")
                print(traceback.format_exc())
            if pool:
                pool.terminate()
                pool.join()

    measurements = {}
    for metricName in metricsNames:
        try:
            result = get_measurements_for_hostname(regionid,metricName,hostname)

            if result and len(result) > 0 and result[0].has_key("name"):        
                last_measurement = get_last_monasca_measurement(result[0])
                if last_measurement and len(last_measurement) > 1:
                    measurements_data = {}                    
                    measurements_data["value"] = last_measurement[1]
                    #timestamp is a Datetime
                    measurements_data["timestamp"] =  histo_utils.from_monasca_ts_to_datetime_ms(last_measurement[0])
                    metric_name = result[0]["name"]
                    measurements[metric_name] = measurements_data
                    if (measurements.has_key("timestamp") and measurements["timestamp"] < measurements_data["timestamp"]) or not (measurements.has_key("timestamp")):
                        measurements["timestamp"] = measurements_data["timestamp"]
        except Exception:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve measurements for hostname gave error. No measurements data returned")
                print(traceback.format_exc())
    
    return measurements
'''

#get hosts measurements for a given region(metrics specified in config file)
'''
def get_hosts_measurements_from_monasca(regionid, parallel = True):
    metricsNames = json.loads(app.config["metrics"]["computeMetrics"])
    
    hostnames = get_all_active_region_hostnames(regionid)
    hosts = {}
    
    if len(hostnames) > 0:
    
        if(parallel):
            pool = None
            try:

                pool = Pool(processes=len(metricsNames),maxtasksperchild=25)
        
                measurements = {}
        
                async_results = [pool.apply_async(get_measurements_for_metric, (metricName,regionid)) for metricName in metricsNames]

                for res in async_results:
                    try:
                        result = res.get(timeout=int(app.config["monasca"]["timeout"]))
                        if result and len(result) > 0 and result[1] and len(result[1]) > 0:  
                            if strtobool(app.config["api"]["debugMode"]):
                                print "["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Getting hosts' measurements of "+regionid+" ..."+result[0]
                            for element in result[1]:
                                if element.has_key("dimensions") and element["dimensions"].has_key("resource_id") and  element["dimensions"]["resource_id"] in hostnames:
                                    last_measurement = get_last_monasca_measurement(element)
                                    if last_measurement and len(last_measurement) > 1:                                 
                                        resource_id = element["dimensions"]["resource_id"]
                                        if not hosts.has_key(resource_id):
                                            hosts[resource_id] = {}
                                        measurements_data = {}                    
                                        measurements_data["value"] = last_measurement[1]
                                        #timestamp is a Datetime
                                        measurements_data["timestamp"] =  histo_utils.from_monasca_ts_to_datetime_ms(last_measurement[0])
                                        metric_name = result[0]
                                        hosts[resource_id][metric_name] = measurements_data
                                        if (hosts[resource_id].has_key("timestamp") and hosts[resource_id]["timestamp"] < measurements_data["timestamp"]) or not (hosts[resource_id].has_key("timestamp")):
                                            hosts[resource_id]["timestamp"] = measurements_data["timestamp"]
                    
                    except TimeoutError:
                        if strtobool(app.config["api"]["debugMode"]):
                            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve measurements for metric of region '"+regionid+"' did not respond in "+app.config["monasca"]["timeout"]+" seconds. No measurements data returned")
                    except Exception as e:
                        if strtobool(app.config["api"]["debugMode"]):
                            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_measurements_for_metric exception (for metric of region '"+regionid+"')")
                            print(traceback.format_exc())
                pool.terminate()
                pool.join()
                return hosts
            except Exception as e:
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_hosts_measurements_from_monasca exception (for metric of region '"+regionid+"') in creating fork")
                    print(traceback.format_exc())
                if pool:
                    pool.terminate()
                    pool.join()

        
        for metricName in metricsNames:
            try:
                result = get_measurements_for_metric(metricName,regionid)[1]

                if result and len(result) > 0:  
                    for element in result:
                        if element.has_key("dimensions") and element["dimensions"].has_key("resource_id") and  element["dimensions"]["resource_id"] in hostnames:
                            last_measurement = get_last_monasca_measurement(element)
                            if last_measurement and len(last_measurement) > 1:                                 
                                resource_id = element["dimensions"]["resource_id"]
                                if not hosts.has_key(resource_id):
                                    hosts[resource_id] = {}
                                measurements_data = {}                    
                                measurements_data["value"] = last_measurement[1]
                                #timestamp is a Datetime
                                measurements_data["timestamp"] =  histo_utils.from_monasca_ts_to_datetime_ms(last_measurement[0])
                                metric_name = metricName
                                hosts[resource_id][metric_name] = measurements_data
                                if (hosts[resource_id].has_key("timestamp") and hosts[resource_id]["timestamp"] < measurements_data["timestamp"]) or not (hosts[resource_id].has_key("timestamp")):
                                    hosts[resource_id]["timestamp"] = measurements_data["timestamp"]
            except Exception:
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve measurements for metric gave error. No measurements data returned")
                    print(traceback.format_exc())
        
        #print hosts
        return hosts
'''

#get host entity for a given region and hostId 
'''
def get_host_from_monasca(regionid,hostname):
    host_entity = {
        "_links": {
            "self": {
                "href": ""
            },
            "services": {
                "href": ""
            }
        },
        "regionid": "",
        "hostid": "",
        "role": "",
        "ipAddresses": [
            {
                "ipAddress": ""
            }
        ],
        "measures": [
            {
                "timestamp": "",
                "percCPULoad": {
                    "value": "",
                    "description": "desc"
                },
                "percRAMUsed": {
                    "value": "",
                    "description": "desc"
                },
                "percDiskUsed": {
                    "value": "",
                    "description": "desc"
                },
                "sysUptime": {
                    "value": "",
                    "description": "desc"
                },
                "owd_status": {
                    "value": "",
                    "description": "desc"
                },
                "bwd_status": {
                    "value": "",
                    "description": "desc"
                }
            }
        ]
    }

    host = get_host_measurements_from_monasca(regionid,hostname) 
    region_metadata = None
    async_result = None
    pool = None
    
    try:
        pool = Pool(processes=1,maxtasksperchild=25)
        async_result = pool.apply_async(get_metadata_from_monasca, (regionid,))
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_host_from_monasca exception (for region '"+regionid+"' and host '"+hostname+"') in creating fork")
            print(traceback.format_exc())
        try:
            region_metadata = get_metadata_from_monasca(regionid)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_host_from_monasca exception (for region '"+regionid+"' and host '"+hostname+"') method error get_metadata_from_monasca")
                print(traceback.format_exc())

    if async_result and pool:
        try:
            metadata_result = async_result.get(timeout=int(app.config["monasca"]["timeout"]))  # get the return value from thread
            if metadata_result and len(metadata_result):
                region_metadata = get_last_monasca_measurement(metadata_result[0])
        except TimeoutError:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve metadata measurements for region did not respond in "+app.config["monasca"]["timeout"]+" seconds. No measurements metadata returned")
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_metadata_from_monasca exception (for region '"+regionid+"')")
                print(traceback.format_exc())
        finally:
            pool.terminate()
            pool.join()
        
    ram_ratio = False
    if region_metadata and len(region_metadata) > 2:
        if region_metadata[2].has_key("ram_allocation_ratio"):
            ram_ratio = region_metadata[2]["ram_allocation_ratio"]
        else:
            ram_ratio = False

    if not bool(host):
        return None
    else:
        hostid = hostname.split("_")[0]
        host_entity["_links"]["self"]["href"] = "/monitoring/regions/" + regionid + "/hosts/" + hostid
        host_entity["_links"]["services"]["href"] = host_entity["_links"]["self"]["href"] + "/services"
        host_entity["regionid"] = regionid
        host_entity["hostid"] = hostid
        host_entity["role"] = "compute"
        #set timestamp = to the most recent timestamp of the metrics measures found
        if host.has_key("timestamp"):
            host_entity["measures"][0]["timestamp"] = host["timestamp"].strftime('%s')
        if host.has_key("compute.node.cpu.percent"):
            cpu_pct = round(float(host["compute.node.cpu.percent"]["value"]), 2)
            host_entity["measures"][0]["percCPULoad"]["value"] = str(cpu_pct)
        else:
            del host_entity["measures"][0]["percCPULoad"]
        if host.has_key("compute.node.ram.now") and host.has_key("compute.node.ram.tot") and ram_ratio:
            ram_used = int(host["compute.node.ram.now"]["value"])
            ram_tot = int(host["compute.node.ram.tot"]["value"])
            ram_pct = round(100 * ram_used / (ram_tot * float(ram_ratio)))
            host_entity["measures"][0]["percRAMUsed"]["value"] = str(ram_pct)
        else:
            del host_entity["measures"][0]["percRAMUsed"]
        if host.has_key("compute.node.disk.now") and host.has_key("compute.node.disk.tot"):
            disk_used = int(host["compute.node.disk.now"]["value"])
            disk_tot = int(host["compute.node.disk.tot"]["value"])
            host_entity["measures"][0]["percDiskUsed"]["value"] = round((100 * disk_used / disk_tot), 2)
        else:
            del host_entity["measures"][0]["percDiskUsed"]
        return host_entity	
'''

#def aggr_monasca_vms_data(vms):
    #"""
    #Function that aggregate vm entity data given a collection (cursor retuned from mongo query) of vms
    #"""
    #vms_data = {"nb_vm": 0}
    #vms_data["nb_vm"] = len(vms)
    #return vms_data

#def aggr_monasca_hosts_data(hosts, regionid=None):
    #"""
    #Function that aggregate host entity data given a collection (data retuned from monasca query) of hosts
    #"""
    #hosts_data = {"ramTot": 0, "diskTot": 0, "cpuTot": 0, "cpuNow": 0, "ramNowTot": 0, "diskNowTot": 0}
    #for host in hosts:
        #if host.has_key("compute.node.ram.tot"):
            #hosts_data["ramTot"] += int(host["compute.node.ram.tot"]["value"])
        #if host.has_key("compute.node.disk.tot"):
            #hosts_data["diskTot"] += int(host["compute.node.disk.tot"]["value"])
        #if host.has_key("compute.node.cpu.tot"):
            #hosts_data["cpuTot"] += int(host["compute.node.cpu.tot"]["value"])
        #if host.has_key("compute.node.cpu.now"):
            #hosts_data["cpuNow"] += int(host["compute.node.cpu.now"]["value"])
        #if host.has_key("compute.node.ram.now"):
            #hosts_data["ramNowTot"] += int(host["compute.node.ram.now"]["value"])
        #if host.has_key("compute.node.disk.now"):
            #hosts_data["diskNowTot"] += int(host["compute.node.disk.now"]["value"])
    ## Workaround to adjust storage amount if Ceph is used
    #cephStorageRegions = json.loads(app.config["api"]["regionsCephStorage"])
    #if regionid in cephStorageRegions:
        #hosts_data["diskTot"] = hosts_data["diskTot"] / len(hosts)
    #return hosts_data

# end Monasca -------------------------------------------------------------------------------

# Monasca-Influx ----------------------------------------------------------------------------

#get region entity for a given regionId
def get_region_from_monasca_influx(regionid):
        
    metadata_result = None
    available_ip_result = None
    used_ip_result = None
    hosts_data_result = None
    vms_result = None
    region_metadata_async_result = None
    region_available_ip_async_result = None
    region_used_ip_async_result = None
    hosts_data_async_result = None
    vms_async_result = None
    pool = None
    
    try:
        if strtobool(app.config["api"]["debugMode"]):
            print "["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Getting metadata of "+regionid+" ..."
        pool = Pool(processes=5,maxtasksperchild=25)
        region_metadata_async_result = pool.apply_async(get_metadata_from_monasca, (regionid,))
        region_available_ip_async_result = pool.apply_async(get_ip_available_from_monasca, (regionid,))
        region_used_ip_async_result = pool.apply_async(get_ip_used_from_monasca, (regionid,))
        hosts_data_async_result = pool.apply_async(get_hosts_measurements_for_region_from_influx, (regionid,))
        vms_async_result = pool.apply_async(get_number_of_active_vms_for_region_from_influx, (regionid,))
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_from_monasca_influx exception (for region '"+regionid+"') in creating fork")
            print(traceback.format_exc())
        if pool:
            pool.terminate()
            pool.join()
        try:
            metadata_result = get_metadata_from_monasca(regionid)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_metadata_from_monasca exception (for region '"+regionid+"')")
                print(traceback.format_exc())
        try:
            available_ip_result = get_ip_available_from_monasca(regionid)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_ip_available_from_monasca exception (for region '"+regionid+"')")
                print(traceback.format_exc())
        try:
            used_ip_result = get_ip_used_from_monasca(regionid)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_ip_used_from_monasca exception (for region '"+regionid+"')")
                print(traceback.format_exc())
        try:
            hosts_data_result = get_hosts_measurements_for_region_from_influx(regionid)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_hosts_measurements_for_region_from_influx exception (for region '"+regionid+"')")
                print(traceback.format_exc())
        try:
            vms_result = get_number_of_active_vms_for_region_from_influx(regionid)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms_for_region_from_influx exception (for region '"+regionid+"')")
                print(traceback.format_exc())
    
    region_entity = {
        "_links": {
            "self": {
                "href": ""
            },
            "hosts": {
                "href": ""
            }
        },
        "measures": [
            {
                "timestamp": "",
                "ipAssigned": "",
                "ipAllocated": "",
                "ipTot": "",
                "nb_cores": 0,
                "nb_cores_used": 0,
                # "nb_cores_enabled": 0,                
                "nb_disk": 0,
                "nb_ram": 0,
                "nb_vm": 0,
                "power_consumption": "",
                "ram_allocation_ratio": "",
                "cpu_allocation_ratio": "",
                "percRAMUsed": 0,
                "percDiskUsed": 0
            }
        ],
        "components": [
            {
                "ceilometer_version": "",
                "keystone_version": "",
                "neutron_version": "",
                "cinder_version": "",
                "nova_version": "",
                "glance_version": ""
            }
        ],
        "id": "",
        "name": "",
        "country": "",
        "latitude": "",
        "longitude": ""
    }
    
    # get from monasca the entity region
    region_metadata = None
    try:
        if metadata_result == None and region_metadata_async_result != None:
            metadata_result = region_metadata_async_result.get(timeout=int(app.config["monasca"]["timeout"]))  # get the return value from thread
        if metadata_result and len(metadata_result) > 0 and metadata_result[0].has_key("id") and metadata_result[0].has_key("dimensions") and metadata_result[0]["dimensions"].has_key("region"):
            region_metadata = {}
            #print(metadata_result[0])
            #region_metadata["timestamp"] = metadata_result[0]["id"]
            region_metadata["id"] = metadata_result[0]["dimensions"]["region"]
            region_metadata["measurements"] = get_last_monasca_measurement(metadata_result[0])
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Metadata of "+regionid+" loaded")
    except TimeoutError:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve metadata measurements for region did not respond in "+app.config["monasca"]["timeout"]+" seconds. No measurements metadata returned")
        if pool:
            pool.terminate()
            pool.join()
        return 404 
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_metadata_from_monasca exception (for region '"+regionid+"')")
            print(traceback.format_exc())
        if pool:
            pool.terminate()
            pool.join()
        return None
      
    #print region_metadata
    
    if region_metadata is None or region_metadata["measurements"] is None: 
        if pool:
            pool.terminate()
            pool.join()
        return 404

    if regionid is not None and region_metadata["id"] == regionid and len(region_metadata["measurements"])>2:

        region_entity["_links"]["self"]["href"] = "/monitoring/regions/" + regionid
        region_entity["_links"]["hosts"]["href"] = "/monitoring/regions/" + regionid + "/hosts"
        region_entity["measures"][0]["timestamp"] = region_metadata["measurements"][0]
        
        available_ip = None
        
        try:
            if available_ip_result == None and region_available_ip_async_result != None:
                available_ip_result = region_available_ip_async_result.get(timeout=int(app.config["monasca"]["timeout"]))  # get the return value from thread
            if available_ip_result and len(available_ip_result):
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Available ips of "+regionid+" loaded")
                last_available_ip = get_last_monasca_measurement(available_ip_result[0])
                if last_available_ip and len(last_available_ip) > 1:
                    available_ip = last_available_ip[1]
            
        except TimeoutError:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve available ip measurements for region did not respond in "+app.config["monasca"]["timeout"]+" seconds. No measurements ip returned")
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_ip_available_from_monasca exception (for region '"+regionid+"')")
                print(traceback.format_exc())
        
        used_ip = None
        
        try:
            if used_ip_result == None and region_used_ip_async_result != None:
                used_ip_result = region_used_ip_async_result.get(timeout=int(app.config["monasca"]["timeout"]))  # get the return value from thread
            if used_ip_result and len(used_ip_result):
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Used ips of "+regionid+" loaded")
                last_used_ip = get_last_monasca_measurement(used_ip_result[0])
                if last_used_ip and len(last_used_ip) > 1:
                    used_ip = last_used_ip[1]            
        except TimeoutError:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve used ip measurements for region did not respond in "+app.config["monasca"]["timeout"]+" seconds. No measurements ip returned")
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_ip_used_from_monasca exception (for region '"+regionid+"')")
                print(traceback.format_exc())
        
        try:
            if hosts_data_result == None and hosts_data_async_result != None:
                hosts_data_result = hosts_data_async_result.get(timeout=int(app.config["influxdb"]["timeout"]))  # get the return value from thread
            if hosts_data_result and len(hosts_data_result):
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Hosts data of "+regionid+" loaded")
                hosts = hosts_data_result.values()  
                if hosts and hosts!=[]:
                    hosts_data = aggr_influx_hosts_data_for_region(hosts, regionid)
                    if hosts_data:
                        region_entity["measures"][0]["nb_ram"] = hosts_data["ramTot"]
                        region_entity["measures"][0]["nb_disk"] = hosts_data["diskTot"]
                        region_entity["measures"][0]["nb_cores"] = hosts_data["cpuTot"]
                        region_entity["measures"][0]["nb_cores_used"] = hosts_data["cpuNow"]
                        region_entity["measures"][0]["percRAMUsed"] = 0
                        region_entity["measures"][0]["percDiskUsed"] = 0
                        if hosts_data["ramTot"] != 0:
                            if region_metadata["measurements"][2].has_key('ram_allocation_ratio'):
                                ram_allocation_ratio = float(region_metadata["measurements"][2]["ram_allocation_ratio"])
                            else:
                                ram_allocation_ratio = 1.0
                            region_entity["measures"][0]["percRAMUsed"] = hosts_data["ramNowTot"] / (
                            hosts_data["ramTot"] * ram_allocation_ratio)
                        if hosts_data["diskTot"] != 0:
                            region_entity["measures"][0]["percDiskUsed"] = hosts_data["diskNowTot"] / hosts_data["diskTot"]
                
        except TimeoutError:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to influx API to retrieve hosts data measurements for region did not respond in "+app.config["influxdb"]["timeout"]+" seconds. No measurements hosts data returned")
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_hosts_measurements_for_region_from_influx exception (for region '"+regionid+"')")
                print(traceback.format_exc())
                
        try:
            if vms_result == None and vms_async_result != None:
                vms_result = vms_async_result.get(timeout=int(app.config["influxdb"]["timeout"]))  # get the return value from thread
            if vms_result:
                if strtobool(app.config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Number of vms of region "+regionid+" loaded")
                #aggragation from virtual machines on region                
                region_entity["measures"][0]["nb_vm"] = vms_result
                
        except TimeoutError:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to influx API to retrieve number of vms for region did not respond in "+app.config["influxdb"]["timeout"]+" seconds. No measurements on vms returned")
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms_for_region_from_influx exception (for region '"+regionid+"')")
                print(traceback.format_exc())
        finally:
            if pool:
                pool.terminate()
                pool.join()

        if used_ip:
            region_entity["measures"][0]["ipAssigned"] = used_ip
        if available_ip:
            region_entity["measures"][0]["ipAllocated"] = available_ip
        if int(region_metadata["measurements"][1]) > 0:
            region_entity["measures"][0]["ipTot"] = region_metadata["measurements"][1]

        if region_metadata["measurements"][2].has_key('ram_allocation_ratio'):
            region_entity["measures"][0]["ram_allocation_ratio"] = region_metadata["measurements"][2]["ram_allocation_ratio"]
        if region_metadata["measurements"][2].has_key('cpu_allocation_ratio'):
            region_entity["measures"][0]["cpu_allocation_ratio"] = region_metadata["measurements"][2]["cpu_allocation_ratio"]

        region_entity["id"] = region_metadata["id"]
        region_entity["name"] = get_region_name(regionid)
        if region_metadata["measurements"][2].has_key('location'):
            region_entity["country"] = region_metadata["measurements"][2]["location"]
        if region_metadata["measurements"][2].has_key('latitude'):
            region_entity["latitude"] = region_metadata["measurements"][2]["latitude"]
        if region_metadata["measurements"][2].has_key('longitude'):
            region_entity["longitude"] = region_metadata["measurements"][2]["longitude"]

        # add components versions to region entity
        if region_metadata["measurements"][2].has_key('ceilometer_version'):
            region_entity["components"][0]["ceilometer_version"] = region_metadata["measurements"][2]["ceilometer_version"]
        if region_metadata["measurements"][2].has_key('keystone_version'):
            region_entity["components"][0]["keystone_version"] = region_metadata["measurements"][2]["keystone_version"]
        if region_metadata["measurements"][2].has_key('neutron_version'):
            region_entity["components"][0]["neutron_version"] = region_metadata["measurements"][2]["neutron_version"]
        if region_metadata["measurements"][2].has_key('cinder_version'):
            region_entity["components"][0]["cinder_version"] = region_metadata["measurements"][2]["cinder_version"]
        if region_metadata["measurements"][2].has_key('nova_version'):
            region_entity["components"][0]["nova_version"] = region_metadata["measurements"][2]["nova_version"]
        if region_metadata["measurements"][2].has_key('glance_version'):
            region_entity["components"][0]["glance_version"] = region_metadata["measurements"][2]["glance_version"]
    else:
        if pool:
            pool.terminate()
            pool.join()
        return None
    return region_entity

def get_all_regions_from_monasca_influx():
    regions_entity = {
        "_links": {
            "self": {
                "href": "/monitoring/regions"
            }
        },
        "_embedded": {
            "regions": [
            ]
        },
        "basicUsers": 0,
        "trialUsers": 0,
        "communityUsers": 0,
        "totalUsers": 0,
        "total_nb_users": 0,
        "totalCloudOrganizations": 0,
        "totalUserOrganizations": 0,
        "total_nb_organizations": 0,
        #
        "total_nb_cores": 0,
        "total_nb_cores_enabled": 0,
        "total_nb_ram": 0,
        "total_nb_disk": 0,
        "total_nb_vm": 0,
        "total_ip_assigned": 0,
        "total_ip_allocated": 0,
        "total_ip": 0
    }

    metadata_result = None
    available_ip_result = None
    used_ip_result = None
    hosts_data_result = None
    vms_result = None
    region_metadata_async_result = None
    region_available_ip_async_result = None
    region_used_ip_async_result = None
    hosts_data_async_result = None
    vms_async_result = None
    pool = None
    
    try:
        if strtobool(app.config["api"]["debugMode"]):
            print "["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Getting metadata for all regions ..."
        pool = Pool(processes=5,maxtasksperchild=25)
        region_metadata_async_result = pool.apply_async(get_total_ip_pool_normalized_from_monasca, ())
        region_available_ip_async_result = pool.apply_async(get_total_ip_available_normalized_from_monasca, ())
        region_used_ip_async_result = pool.apply_async(get_total_ip_used_normalized_from_monasca, ())
        hosts_data_async_result = pool.apply_async(get_hosts_measurements_from_influx, ())
        vms_async_result = pool.apply_async(get_number_of_active_vms_from_influx, ())
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_from_monasca_influx exception in creating fork")
            print(traceback.format_exc())
        if pool:
            pool.terminate()
            pool.join()
        try:
            metadata_result = get_total_ip_pool_normalized_from_monasca()
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_total_ip_pool_normalized_from_monasca exception")
                print(traceback.format_exc())
        try:
            available_ip_result = get_total_ip_available_normalized_from_monasca()
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_total_ip_available_normalized_from_monasca exception")
                print(traceback.format_exc())
        try:
            used_ip_result = get_total_ip_used_normalized_from_monasca()
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_total_ip_used_normalized_from_monasca exception")
                print(traceback.format_exc())
        try:
            hosts_data_result = get_hosts_measurements_from_influx()
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_hosts_measurements_from_influx exception")
                print(traceback.format_exc())
        try:
            vms_result = get_number_of_active_vms_from_influx()
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms_from_influx exception")
                print(traceback.format_exc())
                
    new_regions = app.config["main_config"]["regionNew"]
    
    for region in app.config["main_config"]["regionNew"]:
            region_item = {"id": {}, "_links": {"self": {"href": {}}}}
            region_item["id"] = region
            region_item["_links"]["self"]["href"] = "/monitoring/regions/" + region
            regions_entity["_embedded"]["regions"].append(copy.deepcopy(region_item))
            
    #return hosts from fork:aggregate returned data
    try:
        if hosts_data_result == None and hosts_data_async_result != None:
            hosts_data_result = hosts_data_async_result.get(timeout=int(app.config["influxdb"]["timeout"]))  # get the return value from thread
        if hosts_data_result and len(hosts_data_result):
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Hosts data for all regions loaded")
            hosts_data_aggregated = aggr_influx_hosts_data(hosts_data_result)
            regions_entity["total_nb_cores"] = hosts_data_aggregated["nb_cores"]
            regions_entity["total_nb_cores_enabled"] = hosts_data_aggregated["nb_cores"]
            regions_entity["total_nb_ram"] = hosts_data_aggregated["nb_ram"]
            regions_entity["total_nb_disk"] = hosts_data_aggregated["nb_disk"]        
    except TimeoutError:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to influx API to retrieve hosts  measurements for all regions did not respond in "+app.config["influxdb"]["timeout"]+" seconds. No hosts measurements returned")
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_hosts_measurements_from_influx exception")
            print(traceback.format_exc())
        
    try:
        if vms_result == None and vms_async_result != None:
            vms_result = vms_async_result.get(timeout=int(app.config["influxdb"]["timeout"]))  # get the return value from thread
        if vms_result:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Number of vms for all regions loaded")
            regions_entity["total_nb_vm"] = vms_result    
    except TimeoutError:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to influx API to retrieve number of vms for all regions did not respond in "+app.config["influxdb"]["timeout"]+" seconds. No number of vms returned")
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms_from_influx exception")
            print(traceback.format_exc())
    
    available_ip = 0
        
    try:
        if available_ip_result == None and region_available_ip_async_result != None:
            available_ip_result = region_available_ip_async_result.get(timeout=int(app.config["monasca"]["timeout"]))  # get the return value from thread
        if available_ip_result and len(available_ip_result):
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Available ips for all regions loaded")
            for region, n_ips in available_ip_result.iteritems():
                available_ip += int(n_ips)
        
    except TimeoutError:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve available ip measurements for all regions did not respond in "+app.config["monasca"]["timeout"]+" seconds. No measurements ip returned")
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_total_ip_available_normalized_from_monasca exception")
            print(traceback.format_exc())
            
    used_ip = 0
        
    try:
        if used_ip_result == None and region_used_ip_async_result != None:
            used_ip_result = region_used_ip_async_result.get(timeout=int(app.config["monasca"]["timeout"]))  # get the return value from thread
        if used_ip_result and len(used_ip_result):
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Used ips for all regions loaded")
            for region, n_ips in used_ip_result.iteritems():
                used_ip += int(n_ips)
        
    except TimeoutError:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve used ip measurements for all regions did not respond in "+app.config["monasca"]["timeout"]+" seconds. No measurements ip returned")
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_total_ip_used_normalized_from_monasca exception")
            print(traceback.format_exc())
            
    pool_ip = 0
    basicUsers = 0
    trialUsers = 0
    communityUsers = 0
    totalUsers = 0
    totalCloudOrganizations = 0
    totalUserOrganizations = 0    
        
    try:
        if metadata_result == None and region_metadata_async_result != None:
            metadata_result = region_metadata_async_result.get(timeout=int(app.config["monasca"]["timeout"]))  # get the return value from thread
        if metadata_result and len(metadata_result):
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Metadata for all regions loaded")
            for region, data in metadata_result.iteritems():
                pool_ip += int(data["ips"])
                if data.has_key("basicUsers"):
                    basicUsers += data["basicUsers"]
                if data.has_key("trialUsers"):
                    trialUsers += data["trialUsers"]
                if data.has_key("communityUsers"):
                    communityUsers += data["communityUsers"]
                if data.has_key("totalUsers"):
                    totalUsers += data["totalUsers"]
                if data.has_key("totalCloudOrganizations"):
                    totalCloudOrganizations += data["totalCloudOrganizations"]
                if data.has_key("totalUserOrganizations"):
                    totalUserOrganizations += data["totalUserOrganizations"]
        
    except TimeoutError:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve metadata measurements for all regions did not respond in "+app.config["monasca"]["timeout"]+" seconds. No measurements metadata returned")
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_total_ip_pool_normalized_from_monasca exception")
            print(traceback.format_exc())
    finally:
        if pool:
            pool.terminate()
            pool.join()
                
    regions_entity["total_ip_assigned"] = used_ip
    regions_entity["total_ip_allocated"] = available_ip
    regions_entity["total_ip"] = pool_ip
        
    regions_entity["basicUsers"] = basicUsers
    regions_entity["trialUsers"] = trialUsers
    regions_entity["communityUsers"] = communityUsers
    regions_entity["totalUsers"] = totalUsers
    regions_entity["total_nb_users"] = basicUsers + trialUsers + communityUsers
    regions_entity["totalCloudOrganizations"] = totalCloudOrganizations
    regions_entity["totalUserOrganizations"] = totalUserOrganizations
    regions_entity["total_nb_organizations"] = totalCloudOrganizations + totalUserOrganizations 
    
    return regions_entity

# end Monasca-Influx ------------------------------------------------------------------
# Influx -------------------------------------------------------------------------------

#get vm entity list dict for a given region
def get_vms_from_influx(regionid):
    start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["vmTTL"]))
    start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    vms = influx_collector.get_all_region_vms(regionid, start_timestamp)
    #print(vms)
    result_dict = {"vms": [], "links": {"self": {"href": "/monitoring/regions/" + regionid + "/vms"}}, "measures": [{}]}

    if vms and len(vms):
        for vm in vms:
            if len(vm) and len(vm[0])>1 and vm[0][1].has_key("resource_id"): 
                vmid = vm[0][1]["resource_id"]
                base_dict_list["_links"]["self"]["href"] = "/monitoring/regions/" + regionid + "/vms/" + vmid
                base_dict_list["id"] = vmid
                result_dict["vms"].append(copy.deepcopy(base_dict_list))
    #print(result_dict)
    return json.dumps(result_dict) 

#get vm entity for a given region
def get_vm_from_influx(regionid, vmid):
    start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["vmTTL"]))
    start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    vm = influx_collector.get_region_vm(regionid, vmid, start_timestamp) 
    result_dict = {"links": {"self": {"href": "/monitoring/regions/" + regionid + "/vms/"+ vmid}}, "measures": [{}]}
        
    timestamp = ""
    value_meta = ""
    disk_util = 0
    memory_util = 0
    cpu_util = 0
    
    disk_usage_vm = None
    disk_capacity_vm = None
    memory_util_vm = None
    cpu_util_vm = None
    instance_vm = None
    
    if vm and len(vm):
        for vm_elements in vm:
            if vm_elements:   
                if len(list(vm_elements.get_points(measurement='disk.usage'))):
                    disk_usage_vm = list(vm_elements.get_points(measurement='disk.usage'))
                if len(list(vm_elements.get_points(measurement='disk.capacity'))):
                    disk_capacity_vm = list(vm_elements.get_points(measurement='disk.capacity'))
                if len(list(vm_elements.get_points(measurement='memory_util'))):
                    memory_util_vm = list(vm_elements.get_points(measurement='memory_util'))
                if len(list(vm_elements.get_points(measurement='cpu_util'))):
                    cpu_util_vm = list(vm_elements.get_points(measurement='cpu_util'))
                if len(list(vm_elements.get_points(measurement='instance'))):
                    instance_vm = list(vm_elements.get_points(measurement='instance'))
        
    if disk_usage_vm and disk_capacity_vm:
        disk_usage = 0
        if disk_usage_vm[0].has_key("value"):
            disk_usage = int(disk_usage_vm[0]["value"])
        if disk_capacity_vm[0].has_key("value"):
            disk_capacity = int(disk_capacity_vm[0]["value"])
            if disk_capacity > 0:
                disk_util = disk_usage*100/disk_capacity
     
    if memory_util_vm:
        if memory_util_vm[0].has_key("value"):
            memory_util = float(memory_util_vm[0]["value"])
            
    if cpu_util_vm:
        if cpu_util_vm[0].has_key("value"):
            cpu_util = float(cpu_util_vm[0]["value"])
            
    if instance_vm:
        if instance_vm[0].has_key("time"):
            timestamp = instance_vm[0]["time"]
        if instance_vm[0].has_key("last"):
            value_meta_json = json.loads(instance_vm[0]["last"])
            if value_meta_json.has_key("host"):
                value_meta = value_meta_json["host"] 
    
    result_dict["measures"] = [{
        "timestamp": "" + timestamp,
        "percCPULoad": {
            "value": round(cpu_util,2),
            "description": "desc"
        },
        "percRAMUsed": {
            "value": round(memory_util,2),
            "description": "desc"
        },
        "percDiskUsed": {
            "value": round(disk_util,2),
            "description": "desc"
        },
        "hostName": {
            "value": value_meta,
            "description": "desc"
        },
        "sysUptime": {
            "value": 0,
            "description": "desc"
        }
    }]
        
    return json.dumps(result_dict) 

def get_number_of_active_vms_for_region_from_influx(regionid):
    start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["vmTTL"]))
    start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    return influx_collector.get_number_of_active_vms_for_region(regionid,start_timestamp)

def get_number_of_active_vms_from_influx():
    start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["vmTTL"]))
    start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    return influx_collector.get_number_of_active_vms(start_timestamp)

#returns the most recent timestamp
def get_most_recent_timestamp(timestamp_string_list):
    timestamp_list = []
    for timestamp in timestamp_string_list:
        try:
            timestamp_date = histo_utils.from_monasca_ts_to_datetime_se(timestamp)
            timestamp_list.append(timestamp_date)
        except Exception as e:
            timestamp_date = histo_utils.from_monasca_ts_to_datetime_ms(timestamp)
            timestamp_list.append(timestamp_date)
    #print(timestamp_list)        
    return max(timestamp_list)

#get host entity for a given region and hostId
def get_host_from_influx(regionid, hostname):
    host_entity = {
        "_links": {
            "self": {
                "href": ""
            },
            "services": {
                "href": ""
            }
        },
        "regionid": "",
        "hostid": "",
        "role": "",
        "ipAddresses": [
            {
                "ipAddress": ""
            }
        ],
        "measures": [
            {
                "timestamp": "",
                "percCPULoad": {
                    "value": "",
                    "description": "desc"
                },
                "percRAMUsed": {
                    "value": "",
                    "description": "desc"
                },
                "percDiskUsed": {
                    "value": "",
                    "description": "desc"
                },
                "sysUptime": {
                    "value": "",
                    "description": "desc"
                },
                "owd_status": {
                    "value": "",
                    "description": "desc"
                },
                "bwd_status": {
                    "value": "",
                    "description": "desc"
                }
            }
        ]
    }

    region_metadata = None
    async_result = None
    pool = None
    
    try:
        pool = Pool(processes=1,maxtasksperchild=25)
        async_result = pool.apply_async(get_metadata_from_monasca, (regionid,))
    except Exception as e:
        if strtobool(app.config["api"]["debugMode"]):
            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_host_from_influx exception (for region '"+regionid+"' and host '"+hostname+"') in creating fork")
            print(traceback.format_exc())
        try:
            region_metadata = get_metadata_from_monasca(regionid)
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_host_from_influx exception (for region '"+regionid+"' and host '"+hostname+"') method error get_metadata_from_monasca")
                print(traceback.format_exc())

    start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["hostTTL"]))
    start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    host = influx_collector.get_region_host(regionid, hostname, start_timestamp)
    
    if async_result and pool:
        try:
            metadata_result = async_result.get(timeout=int(app.config["monasca"]["timeout"]))  # get the return value from thread
            if metadata_result and len(metadata_result):
                region_metadata = get_last_monasca_measurement(metadata_result[0])
        except TimeoutError:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] HTTP call to monasca API to retrieve metadata measurements for region did not respond in "+app.config["monasca"]["timeout"]+" seconds. No measurements metadata returned")
        except Exception as e:
            if strtobool(app.config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_metadata_from_monasca exception (for region '"+regionid+"')")
                print(traceback.format_exc())
        finally:
            pool.terminate()
            pool.join()
        
    ram_ratio = False
    if region_metadata and len(region_metadata) > 2:
        if region_metadata[2].has_key("ram_allocation_ratio"):
            ram_ratio = region_metadata[2]["ram_allocation_ratio"]
        else:
            ram_ratio = False
    
    if host:
        
        cpu_percent = None
        cpu_now = None
        ram_now = None
        ram_tot = None
        disk_now = None
        disk_tot = None
        timestamp_list = []
        
        cpu_percent = list(host.get_points(measurement='compute.node.cpu.percent'))
        cpu_now = list(host.get_points(measurement='compute.node.cpu.now'))
        ram_now = list(host.get_points(measurement='compute.node.ram.now'))
        ram_tot = list(host.get_points(measurement='compute.node.ram.tot'))
        disk_now = list(host.get_points(measurement='compute.node.disk.now'))
        disk_tot = list(host.get_points(measurement='compute.node.disk.tot'))
        
        hostid = hostname.split("_")[0]
        host_entity["_links"]["self"]["href"] = "/monitoring/regions/" + regionid + "/hosts/" + hostid
        host_entity["_links"]["services"]["href"] = host_entity["_links"]["self"]["href"] + "/services"
        host_entity["regionid"] = regionid
        host_entity["hostid"] = hostid
        host_entity["role"] = "compute"
        
        if not cpu_now or len(cpu_now) == 0:
            return None
        
        if cpu_percent and len(cpu_percent) and cpu_percent[0].has_key("value"):
            cpu_pct = round(float(cpu_percent[0]["value"]), 2)
            host_entity["measures"][0]["percCPULoad"]["value"] = str(cpu_pct)
            if cpu_percent[0].has_key("time"):
                timestamp_list.append(cpu_percent[0]["time"])
        else:
            del host_entity["measures"][0]["percCPULoad"]
            
        if ram_now and len(ram_now) and ram_now[0].has_key("value") and ram_tot and len(ram_tot) and ram_tot[0].has_key("value") and ram_ratio and float(ram_tot[0]["value"]) > 0.0:
            ram_used = float(ram_now[0]["value"])
            ram_total = float(ram_tot[0]["value"])
            ram_pct = round((100 * ram_used / (ram_total * float(ram_ratio))), 2)
            host_entity["measures"][0]["percRAMUsed"]["value"] = str(ram_pct)
            if ram_now[0].has_key("time"):
                timestamp_list.append(ram_now[0]["time"])
            if ram_tot[0].has_key("time"):
                timestamp_list.append(ram_tot[0]["time"])
        else:
            del host_entity["measures"][0]["percRAMUsed"] 
            
        if disk_now and len(disk_now) and disk_now[0].has_key("value") and disk_tot and len(disk_tot) and disk_tot[0].has_key("value") and float(disk_tot[0]["value"]) > 0.0:
            disk_used = float(disk_now[0]["value"])
            disk_total = float(disk_tot[0]["value"])
            disk_pct = round((100 * disk_used / disk_total), 2)
            host_entity["measures"][0]["percDiskUsed"]["value"] = str(disk_pct)
            if disk_now[0].has_key("time"):
                timestamp_list.append(disk_now[0]["time"])
            if disk_tot[0].has_key("time"):
                timestamp_list.append(disk_tot[0]["time"])
        else:
            del host_entity["measures"][0]["percDiskUsed"]             
        
        #set timestamp = to the most recent timestamp of the metric measures found
        host_entity["measures"][0]["timestamp"] = get_most_recent_timestamp(timestamp_list)
    else:
        return None    
    
    return host_entity  
 
#get hosts measurements for a given region
def get_hosts_measurements_for_region_from_influx(regionid):
        
    start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["hostTTL"]))
    start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    hosts_data = influx_collector.get_region_hosts_data(regionid, start_timestamp)    

    hosts = {}
    if hosts_data:
        hosts_measurements = list(hosts_data.items())
        if hosts_measurements and len(hosts_measurements):
            for hosts_measurement in hosts_measurements:
                #print(hosts_measurement)
                if len(hosts_measurement) and len(hosts_measurement[0])>1 and hosts_measurement[0][1].has_key("resource_id"):
                    resource_id = hosts_measurement[0][1]["resource_id"]
                    measurement = hosts_measurement[0][0]
                    
                    metric_of_active_hosts = json.loads(app.config["metrics"]["computeMetricForActiveHost"])[0]
                    value_data_of_active_host = list(hosts_data.get_points(measurement=metric_of_active_hosts, tags={'resource_id': resource_id}))
                    if value_data_of_active_host and len(value_data_of_active_host) and value_data_of_active_host[0].has_key("value") and value_data_of_active_host[0].has_key("time"):
                    
                        value_data = list(hosts_data.get_points(measurement=measurement, tags={'resource_id': resource_id}))
                        if value_data and len(value_data) and value_data[0].has_key("value") and value_data[0].has_key("time"):
                            measurements_data = {}  
                            measurements_data["value"] = value_data[0]["value"]
                            
                            time = value_data[0]["time"]
                            
                            if not hosts.has_key(resource_id):
                                hosts[resource_id] = {}
                            
                            try:
                                measurements_data["timestamp"] = histo_utils.from_monasca_ts_to_datetime_se(time)
                            except Exception as e:
                                measurements_data["timestamp"] = histo_utils.from_monasca_ts_to_datetime_ms(time)
                            metric_name = measurement
                            hosts[resource_id][metric_name] = measurements_data
                            if (hosts[resource_id].has_key("timestamp") and hosts[resource_id]["timestamp"] < measurements_data["timestamp"]) or not (hosts[resource_id].has_key("timestamp")):
                                hosts[resource_id]["timestamp"] = measurements_data["timestamp"]
    #print(hosts)
    #print("------")
    #print(list(hosts_data.get_points(measurement="compute.node.cpu.now", tags={'resource_id': 'mmm'})))
    return hosts

#get hosts measurements for all regions
def get_hosts_measurements_from_influx():
        
    start = histo_utils.get_datetime_with_delta_sec(int(app.config["api"]["hostTTL"]))
    start_timestamp = histo_utils.from_datetime_ms_to_monasca_ts(start)
    hosts_data = influx_collector.get_hosts_data(start_timestamp)  
    
    hosts = {}
    
    if hosts_data:    
        
        hosts_measurements = list(hosts_data.items())
        if hosts_measurements and len(hosts_measurements):
            
            for hosts_measurement in hosts_measurements:
                #print(hosts_measurement)
                if len(hosts_measurement) and len(hosts_measurement[0])>1 and hosts_measurement[0][1].has_key("resource_id") and hosts_measurement[0][1].has_key("region"):
                    resource_id = hosts_measurement[0][1]["resource_id"]
                    measurement = hosts_measurement[0][0]
                    region = hosts_measurement[0][1]["region"]
                    
                    if is_region_on(region):
                    
                        metric_of_active_hosts = json.loads(app.config["metrics"]["computeMetricForActiveHost"])[0]
                        value_data_of_active_host = list(hosts_data.get_points(measurement=metric_of_active_hosts, tags={'resource_id': resource_id, 'region':region}))
                        if value_data_of_active_host and len(value_data_of_active_host) and value_data_of_active_host[0].has_key("value") and value_data_of_active_host[0].has_key("time"):
                        
                            value_data = list(hosts_data.get_points(measurement=measurement, tags={'resource_id': resource_id, 'region':region}))
                            if value_data and len(value_data) and value_data[0].has_key("value") and value_data[0].has_key("time"):
                                measurements_data = {}  
                                measurements_data["value"] = value_data[0]["value"]
                                
                                time = value_data[0]["time"]
                                
                                if not hosts.has_key(region):
                                    hosts[region] = {}
                                if not hosts[region].has_key(resource_id):
                                    hosts[region][resource_id] = {}
                                
                                try:
                                    measurements_data["timestamp"] = histo_utils.from_monasca_ts_to_datetime_se(time)
                                except Exception as e:
                                    measurements_data["timestamp"] = histo_utils.from_monasca_ts_to_datetime_ms(time)
                                metric_name = measurement
                                hosts[region][resource_id][metric_name] = measurements_data
                                if (hosts[region][resource_id].has_key("timestamp") and hosts[region][resource_id]["timestamp"] < measurements_data["timestamp"]) or not (hosts[region][resource_id].has_key("timestamp")):
                                    hosts[region][resource_id]["timestamp"] = measurements_data["timestamp"]
    #print(hosts)
    #print("------")
    #print(list(hosts_data.get_points(measurement="compute.node.cpu.now", tags={'resource_id': 'mmm'})))
    return hosts


def aggr_influx_hosts_data_for_region(hosts, regionid=None):
    """
    Function that aggregate host entity data given a collection (data retuned from influx query) of hosts
    """
    hosts_data = {"ramTot": 0, "diskTot": 0, "cpuTot": 0, "cpuNow": 0, "ramNowTot": 0, "diskNowTot": 0}
    for host in hosts:
        if host.has_key("compute.node.ram.tot"):
            hosts_data["ramTot"] += int(host["compute.node.ram.tot"]["value"])
        if host.has_key("compute.node.disk.tot"):
            hosts_data["diskTot"] += int(host["compute.node.disk.tot"]["value"])
        if host.has_key("compute.node.cpu.tot"):
            hosts_data["cpuTot"] += int(host["compute.node.cpu.tot"]["value"])
        if host.has_key("compute.node.cpu.now"):
            hosts_data["cpuNow"] += int(host["compute.node.cpu.now"]["value"])
        if host.has_key("compute.node.ram.now"):
            hosts_data["ramNowTot"] += int(host["compute.node.ram.now"]["value"])
        if host.has_key("compute.node.disk.now"):
            hosts_data["diskNowTot"] += int(host["compute.node.disk.now"]["value"])
    # Workaround to adjust storage amount if Ceph is used
    cephStorageRegions = json.loads(app.config["api"]["regionsCephStorage"])
    if regionid in cephStorageRegions:
        hosts_data["diskTot"] = int(hosts_data["diskTot"] / len(hosts))
    return hosts_data

def aggr_influx_hosts_data(hosts_data):
    """
    Function that aggregates host entity data given a collection (data retuned from influx query) of hosts
    """
    hosts_data_to_return = {"nb_cores": 0, "nb_ram": 0, "nb_disk": 0}
    if(hosts_data and len(hosts_data)):
        # Workaround to adjust storage amount if Ceph is used
        cephStorageRegions = json.loads(app.config["api"]["regionsCephStorage"])
        
        for region, region_hosts in hosts_data.iteritems():
            if region_hosts and len(region_hosts):
                ram_tot = 0
                disk_tot = 0
                cpu_tot = 0
                for host_name, host in region_hosts.iteritems():
                    if host.has_key("compute.node.ram.tot"):
                        ram_tot += int(host["compute.node.ram.tot"]["value"])
                    if host.has_key("compute.node.disk.tot"):                        
                        disk_tot += int(host["compute.node.disk.tot"]["value"])
                    if host.has_key("compute.node.cpu.tot"):
                        cpu_tot += int(host["compute.node.cpu.tot"]["value"])
                
                hosts_data_to_return["nb_ram"] += ram_tot
                hosts_data_to_return["nb_cores"] += cpu_tot
                
                if region in cephStorageRegions:
                    disk_tot = disk_tot / len(region_hosts)
                
                hosts_data_to_return["nb_disk"] += disk_tot
                    
    return hosts_data_to_return

# end Influx ------------------------------------------------------------------------------

# Argument management
def arg_parser():
    parser = argparse.ArgumentParser(description='Monitoring proxy')
    parser.add_argument("-c", "--config-file", help="Config file", required=False)
    return parser.parse_args()


# Function that return the dict of a section in a config file
def ConfigSectionMap(section, Config):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


# Function to convert a true string to boolean value.
# Used for load_regionNew
def str2true(v):
    return v.lower() in ("yes", "true", "t", "1")


# Function to convert a false string to boolean value.
# Used for load_regionNew
def str2false(v):
    return v.lower() in ("no", "false", "f", "0")


'''
Function that given a config file and a list of section
return the dict in the form:
<section_name> : <map of value>
For example: map["mongodb"] contains a map of mongodb section attributes
If app is passed load map also in the app
'''


def config_to_dict(section_list, config, app=None):
    if not isinstance(section_list, (list)):
        print "section_list must be a list"
    result_map = {}
    for item in section_list:
        item_map = dict(config._sections[item])
        del item_map["__name__"]
        app.config[item] = item_map
        result_map[item] = item_map
        if app:
            app.config[item] = item_map

    return result_map


# Main function
def main():
    # MonkeyPatch for use ThreadPool with Python 2.7.3. See http://goo.gl/MNefPF
    from multiprocessing import dummy as __mp_dummy

    # Now we can define a replacement and patch DummyProcess:
    def __DummyProcess_start_patch(self):  # pulled from an updated version of Python
        assert self._parent is __mp_dummy.current_process()  # modified to avoid further imports
        self._start_called = True
        if hasattr(self._parent, '_children'):
            self._parent._children[self] = None
        __mp_dummy.threading.Thread.start(self)  # modified to avoid further imports
    __mp_dummy.DummyProcess.start = __DummyProcess_start_patch

    # Loads and manages the input arguments
    args = arg_parser()
    if args.config_file is not None:
        config_file = args.config_file
    else:
        config_file = "config.ini"

    # Read config file
    if not os.path.isfile(config_file):
        print("Configuration file not found: {}").format(config_file)
        sys.exit(-1)
    try:
        config = ConfigParser.ConfigParser()
        # Preserve case when reading configfile
        config.optionxform = str
        config.read(config_file)
    except Exception as e:
        print("Problem parsing config file: {}").format(e)
        sys.exit(-1)

    # Read main config file
    mainconfig_file = config.get("mainconfig", "path")
    if not os.path.isfile(mainconfig_file):
        print("Main configuration file not found: {}").format(mainconfig_file)
        sys.exit(-1)
    try:
        main_config = ConfigParser.ConfigParser()
        # Preserve case when reading configfile
        main_config.optionxform = str
        main_config.read(mainconfig_file)
        app.config['main_config'] = dict()
        app.config['main_config']['regionNew'] = dict(main_config.items('regionNew'))
        app.config['main_config']['regionNames'] = dict(main_config.items('regionNames'))
        app.config['main_config']['regionData'] = dict(main_config.items('regionData'))
    except Exception as e:
        print("Problem parsing main config file: {}").format(e)
        sys.exit(-1)

    # Get a map with config declared in SECTION_TO_LOAD and insert it in bottle app
    SECTION_TO_LOAD = ["mysql", "profile", "monasca", "influxdb" , "keystone", "mongodb", "mongodbOld", "api", "key", "idm", "oldmonitoring", "newmonitoring", "usageData", "metrics", "projectpath"]
    config_map = config_to_dict(section_list=SECTION_TO_LOAD, config=config, app=app)

    # Create and install plugin in bottle app
    mongo_map = dict(config_map["mongodb"])
    mongo_old_map = dict(config_map["mongodbOld"])
    mongo_map["keyword"] = "mongodb"
    mongo_old_map["keyword"] = "mongodbOld"  # declares keyword to not conflict with mongodb instance
    mongo_old_map.pop("collectionname", None)  # Remove this because MongoPlugin not recognize
    mongo_map.pop("collectionname", None)
    mongo_plugin = MongoPlugin(**mongo_map)
    mongo_plugin_old = MongoPlugin(**mongo_old_map)
    config_map["mysql"]["dbport"] = int(config_map["mysql"]["dbport"])
    mysql_plugin = bottle_mysql.Plugin(**config_map["mysql"])

    app.install(mongo_plugin)
    app.install(mongo_plugin_old)
    app.install(mysql_plugin)
    ##

    listen_url = config_map['api']['listen_url']
    listen_port = config_map['api']['listen_port']

    project_path = config_map['projectpath']['path']
    sys.path.append(project_path)
    import monitoringHisto.monitoringHisto
    from monitoringHisto.monitoringHisto import utils as _histo_utils_
    from monitoringHisto.monitoringHisto import CollectorMonasca
    from CollectorInflux import CollectorInflux
    
    global histo_utils
    histo_utils = _histo_utils_

    # Setup monasca collector
    global collector
    CONF_M_SECTION = 'monasca'
    keystone_endpoint = config_map["keystone"]["uri"]
    monasca_endpoint = config_map["monasca"]["uri"]
    user = config_map["profile"]["user"]
    password = config_map["profile"]["password"]
    try:        
        collector = CollectorMonasca(user, password, monasca_endpoint, keystone_endpoint, config_map)
    except Exception as e:
        print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Problem creating Monasca Collector")
        print(traceback.format_exc())
        sys.exit(-1)
        
    # Setup influx collector
    global influx_collector
    influx_host = config_map["influxdb"]["host"]
    influx_port = config_map["influxdb"]["port"]
    dbname = config_map["influxdb"]["dbname"]
    user = config_map["influxdb"]["user"]
    password = config_map["influxdb"]["password"]
    debugMode = config_map["api"]["debugMode"]
    try:        
        influx_collector = CollectorInflux(user, password, dbname, influx_host, influx_port, debugMode)
    except Exception as e:
        print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Problem creating Influx Collector")
        print(traceback.format_exc())
        sys.exit(-1)

    rt = RepeatedTimer(float(config_map["keystone"]["token_ttl"]), update_token_of_parent_collector) # it auto-starts, no need of rt.start()
    try:
        # App runs in infinite loop
        httpserver.serve(app, host=listen_url, port=listen_port)
    finally:
        rt.stop() # better in a try/finally block to make sure the program ends!        


if __name__ == '__main__':
    main()
