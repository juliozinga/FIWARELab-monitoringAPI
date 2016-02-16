#!/usr/bin/env python
from __future__ import division
from bottle import route, run, request, error, response, Bottle, redirect, HTTPError, abort
from pymongo import MongoClient, database
from bottle.ext.mongo import MongoPlugin
from bson.json_util import dumps
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

#Main bottle app
app = Bottle()

def is_idm_authorized(auth_url, token_base64):
    try:
        token_string = token_base64
        #token_string = base64.b64decode(token_base64)
    except Exception as e:
        print("Error in decoding token. Maybe is not in base64 format")
        return False
    try:
        url_request = auth_url + "/user/?access_token=" + token_string
        headers = {}
        headers['accept'] = 'application/json'
        headers['user-group'] = 'none'
        req = urllib2.Request(url_request)
        req.headers = headers
        response = urllib2.urlopen(req)
        UserJson = response.read()
    except Exception as e:
        print "Error in authentication: " + str(e)
        return False
    return True

def get_keypass_token(username, password, url):
    data = { 'auth': {'identity': { 'methods': ['password'],
    'password': { 'user': { 'name': username , 'domain': { 'id': 'default' },
    'password': password } } } }}

    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(data))
    accepted_response = [200, 201, 202]
    if response.getcode() in accepted_response:
        return response.headers.get('X-Subject-Token')
    else:
        return None

def request_to_idm(username, password, keypass_url, url):
    token = get_keypass_token(username=username, password=password, url=keypass_url)
    req = urllib2.Request(url)
    if token:
        req.add_header('X-Auth-Token', token)
        response = urllib2.urlopen(req)
        return response
    return None

def get_token(response):
    if request.headers.get("Authorization") is not None:
        token = request.headers.get("Authorization").split(" ")[1]
    else:
        return None
    auth_map = {}
    if request.headers.get("Authorization").find("X-Auth-Token") != -1:
        auth_map["X-Auth-Token"] = token
    else:
        auth_map["Bearer"] = token
    return auth_map

@app.error(404)
def error404(error):
    response.content_type = 'application/json'
    return {'Request not found'}

@app.error(401)
def error401(error):
    response.content_type = 'application/json'
    return json.dumps('UNAUTHORIZED')

'''
Make the request to old monitoring api
args:   request in the form: "/" or "/monitoring/regions" etc.
return empty array if error
'''
def make_request(request_url, request):
    base_url = "http://" + app.config.get("old_monitoring_url") + ":" + app.config.get("old_monitoring_port")
    url_request = base_url + request_url + options_from_request(request)
    try:
        req = urllib2.Request(url_request)
        token_map = get_token(request)
        if token_map is not None:
            req.headers["Authorization"] = " ".join(token_map.iteritems().next())
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        return 'UNAUTHORIZED'
    except Exception as e:
        return {}
    return response.read()

'''
Given an API request return a map with the option after '?'
in the url
'''
def map_from_request(request):
    avaible_options = ["since", "h"]
    map = {}
    for i in avaible_options:
        if request.query.getone(i) is not None:
            map[i] = request.query.getone(i)
    return map

'''
Given an API request return a string to be used as options,
in the form: "?since=12345&key=value"
'''
def options_from_request(request):
    options = ""
    option_map = map_from_request(request)
    if len(option_map) != 0:
        options += "?"
        for item in option_map.iteritems():
            options += ( item[0] + "=" + item[1] + "&" )
    return options

@app.route('/')
def root():
    return make_request("/", request=request)

@app.route('/monitoring/regions', method='GET')
@app.route('/monitoring/regions/', method='GET')
def get_all_regions():
    out = make_request("/monitoring/regions", request=request)
    return json.dumps( make_request("/monitoring/regions", request=request) )

@app.route('/monitoring/regions/<regionid>', method='GET')
@app.route('/monitoring/regions/<regionid>/', method='GET')
def get_region(regionid="ID of the region"):
    return json.dumps(make_request(
        "/monitoring/regions/" + regionid, request=request))

@app.route('/monitoring/regions/<regionid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/services/', method='GET')
def get_all_services_by_region(db, regionid="ID of the region"):
    return json.dumps(make_request(
        "/monitoring/regions/" + regionid + "/services", request=request))

@app.route('/monitoring/regions/<regionid>/hosts', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/', method='GET')
def get_all_hosts(regionid="ID of the region"):
    return json.dumps(make_request(
        "/monitoring/regions/" + regionid + "/hosts", request=request))

@app.route('/monitoring/regions/<regionid>/hosts/<hostid>', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/', method='GET')
def get_host(regionid="ID of the region", hostid="ID of the host"):
    return json.dumps(make_request(
        "/monitoring/regions/" + regionid + "/hosts/" + hostid, request=request))

@app.route('/monitoring/regions/<regionid>/vms', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/', method='GET')
def get_all_vms(regionid="ID of the region"):
    return json.dumps(make_request(
        "/monitoring/regions/" + regionid + "/vms/" , request=request))

@app.route('/monitoring/regions/<regionid>/vms/<vmid>', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/', method='GET')
def get_vm(regionid="ID of the region", vmid="ID of the vm"):
    return json.dumps(make_request(
        "/monitoring/regions/" + regionid + "/vms/" + vmid, request=request))

@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/', method='GET')
def get_all_services_by_host(regionid="ID of the region", hostid="ID of the host"):
    return json.dumps(make_request(
        "/monitoring/regions/" + regionid + "/hosts/" + hostid + "/services", request=request))

@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>/', method='GET')
def get_service_by_host(regionid="ID of the region", hostid="ID of the host", serviceName="Service name"):
    return json.dumps(make_request(
        "/monitoring/regions/" + regionid + "/hosts/" + hostid + "/services/" + serviceName , request=request))

@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/', method='GET')
def get_all_services_by_vm(regionid="ID of the region", vmid="ID of the vm"):
    return json.dumps(make_request(
        "/monitoring/regions/" + regionid + "/vms/" + vmid + "/services", request=request))

@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>/', method='GET')
def get_service_by_vm(regionid="ID of the region", vmid="ID of the vm", serviceName="Service name"):
    return json.dumps(make_request(
        "/monitoring/regions/" + regionid + "/vms/" + vmid + "services/" + serviceName, request=request))

@app.route('/monitoring/regions/<regionid>/nes', method='GET')
@app.route('/monitoring/regions/<regionid>/nes/', method='GET')
def get_all_nes(regionid="ID of the region"):
    return json.dumps(make_request("/monitoring/regions/" + regionid + "/nes/", request=request))

@app.route('/monitoring/regions/<regionid>/nes/<neid>', method='GET')
@app.route('/monitoring/regions/<regionid>/nes/<neid>/', method='GET')
def get_ne(regionid="ID of the region", neid="ID of the network"):
    return json.dumps(make_request("/monitoring/regions/" + regionid + "/nes/" + neid, request=request))

@app.route('/monitoring/host2hosts', method='GET')
@app.route('/monitoring/host2hosts/', method='GET')
def get_host2hosts():
    print "Call to forward"
    return {}

@app.route('/monitoring/regions/<regionid>/images', method='GET')
@app.route('/monitoring/regions/<regionid>/images/', method='GET')
def get_all_images_by_region(db, regionid="ID of the region"):
    # 1)Check if is authorized
    if is_idm_authorized( auth_url=app.config.get("idm_account_url"), token_base64=get_token(response).iteritems().next()[1] ):
        print "is auth"
    else:
        abort(401)
    # 2)Get data from mongodb
    # 3)Return data
    return False#return {'To be implemented'}

@app.route('/monitoring/regions/<regionid>/images/<imageid>', method='GET')
@app.route('/monitoring/regions/<regionid>/images/<imageid>/', method='GET')
def get_all_images_by_region(mongodb, regionid="ID of the region", imageid="Image id"):
    # 1)Check if is authorized
    # 2)Get data from mongodb
    # 3)Return data
    return json.dumps("to be implemented here")

# /monitoring/host2hosts/source;dest?since=since
# /monitoring/host2hosts/source/dest?since=since

#Argument management
def arg_parser():
    parser = argparse.ArgumentParser(description='Monitoring python version')
    parser.add_argument("-c", "--config-file", help="Config file", required=False)
    return parser.parse_args()

#Function that return the dict of a section in a config file
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

#Return variables declared in config file in [api] section
def load_api_section(config):
    try:
        listen_url = ConfigSectionMap('api', config)['listen_url']
        listen_port = ConfigSectionMap('api', config)['listen_port']
    except Exception as e:
        print("Error in loading api section: {}").format(e)
        sys.exit(-1)
    return listen_url, listen_port

#Return map variables declared in config file in [mongodb] section
def load_mongo_section(config):
    mongo_config = {}
    try:
        if ConfigSectionMap('mongodb', config)['url']:
            mongo_config['uri'] = "mongodb://" + ConfigSectionMap('mongodb', config)['url']
        if ConfigSectionMap('mongodb', config)['dbname']:
            mongo_config['db'] = ConfigSectionMap('mongodb', config)['dbname']
        if ConfigSectionMap('mongodb', config)['collectionname']:
            app.config["collectionname"] = ConfigSectionMap('mongodb', config)['collectionname']
        mongo_config["json_mongo"] = True
        plugin = MongoPlugin(**mongo_config)
    except Exception as e:
        print("Error in mongodb: {}").format(e)
        sys.exit(-1)
    return mongo_config

#Load mysql configuration from config file
def load_mysql_section(config):
    mysql_config = {}
    try:
        mysql_config["dbuser"] = ConfigSectionMap('mysql', config)['user']
        mysql_config["dbpass"] = ConfigSectionMap('mysql', config)['password']
        mysql_config["dbname"] = ConfigSectionMap('mysql', config)['dbname']
        mysql_config["dbhost"] = ConfigSectionMap('mysql', config)['url']
        mysql_config["dbport"] = int(ConfigSectionMap('mysql', config)['port'])
    except Exception as e:
        print("Error in mongodb: {}").format(e)
        sys.exit(-1)
    return mysql_config

#Load variable from config file to bottle app config
def load_oldmonitoring_section(config):
    try:
        app.config["old_monitoring_url"] = ConfigSectionMap('oldmonitoring', config)['url']
        app.config["old_monitoring_port"] = ConfigSectionMap('oldmonitoring', config)['port']
    except Exception as e:
        print("Error in old monitoring section: {}").format(e)
        sys.exit(-1)
    return True

#Load variables declared in config file in [idm] section and load it to Bottle app.
#These variables can be getted from route function using app.config.get('variable')
def load_idm_section(config):
    try:
        app.config["token_url"] = ConfigSectionMap('idm', config)['token_url']
        app.config["service_url"] = ConfigSectionMap('idm', config)['service_url']
        app.config["idm_username"] = ConfigSectionMap('idm', config)['username']
        app.config["idm_password"] = ConfigSectionMap('idm', config)['password']
        app.config["idm_account_url"] = ConfigSectionMap('idm', config)['account_url']
    except Exception as e:
        print "Error in IDM config: " + str(e)
        sys.exit(-1) 

#Main function
def main():
    args = arg_parser()
    if args.config_file is not None:
        config_file = args.config_file
    else:
        config_file = "config.ini"

    #Read config file
    try:
        Config = ConfigParser.ConfigParser()
        Config.read(config_file)
    except Exception as e:
        print("Problem with config file: {}").format(e)
        sys.exit(-1)

    #Load from Config file
    listen_url, listen_port = load_api_section(Config)
    mongo_plugin = MongoPlugin(**load_mongo_section(Config))
    mysql_plugin = bottle_mysql.Plugin(**load_mysql_section(Config))
    load_idm_section(Config)
    load_oldmonitoring_section(Config)

    app.install(mongo_plugin)
    app.install(mysql_plugin)

    #App runs in infinite loop
    run(app, host=listen_url, port=listen_port, debug=True)

if __name__ == '__main__':
    main()