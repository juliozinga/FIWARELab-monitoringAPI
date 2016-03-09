#!/usr/bin/env python
from __future__ import division
from bottle import route, run, request, error, response, Bottle, redirect, HTTPError, abort
from pymongo import MongoClient, database
from bottle.ext.mongo import MongoPlugin
from bson.json_util import dumps
from paste import httpserver
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

###Main bottle app
app = Bottle()
#####

HEADER_AUTH = "X-Auth-Token"

#Return if the token is authorized with auth_url
def is_idm_authorized(auth_url, token_map):
    try:
        if HEADER_AUTH in token_map:
            token_string = token_map[HEADER_AUTH]
        elif "Authorization" in token_map:
            token_string = base64.b64decode(token_map["Authorization"].split(" ")[1])
        else:
            raise Exception('Header not known') 
    except Exception as e:
        print "Error in decoding token: " + str(e)
        return False
    try:
        url_request = auth_url + "/user/?access_token=" + token_string
        headers = {}
        headers['accept'] = 'application/json'
        headers['user-group'] = 'none'
        req = urllib2.Request(url_request)
        req.headers = headers
        response_idm = urllib2.urlopen(req)
        UserJson = response_idm.read()
    except Exception as e:
        print "Error in authentication: " + str(e)
        return False
    return True

#Get token from IDM
def get_token_auth(url, consumer_key, consumer_secret, username, password, convert_to_64=True):
    response_dict = {}
    try:
        headers = {}
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Authorization"] = "Basic " + base64.b64encode(consumer_key + ":" + consumer_secret)
        data = {"grant_type":"password","username":username,"password":password}

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

def get_token_from_response(response):
    auth_map = {}
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
    return {'Request not found'}

@app.error(401)
def error401(error):
    response.content_type = 'application/json'
    return {"Error" : "UNAUTHORIZED"}
'''
Return the url and port of monitoring to which forward the request.
If the regionId has old monitoring return the old monitoring url,
If the region has new monitoring return the new one
'''
def select_monitoring_to_forward(regionid):
    if is_region_new(regionid):
        return app.config["newmonitoring"]["url"], app.config["newmonitoring"]["port"]
    else:
        return  app.config["oldmonitoring"]["url"], app.config["oldmonitoring"]["port"]
'''
Return True if region use new monitoring system false otherwise
'''
def is_region_new(regionid):
    try:
        if str2bool( app.config["regionNew"][regionid.lower()] ):
            return True
    except KeyError as e:
        print "Region id not found in configuration file: " + str(type(e)) + " " + str(e)
        pass
    return False

'regionNew'
'''
Make the request to old monitoring api
args:   request in the form: "/" or "/monitoring/regions" etc.
return empty array if error
'''
def make_request(request_url, request, regionid=None):
    monitoring_url, monitoring_port = select_monitoring_to_forward(regionid)
    base_url = "http://" + monitoring_url + ":" + monitoring_port
    url_request = base_url + request_url + options_from_request(request)
    req = urllib2.Request(url_request)
    token_map = get_token_from_response(request)

    if bool(token_map):
        req.headers[ token_map.iteritems().next()[0] ] = token_map.iteritems().next()[1]
    try:
        my_response = urllib2.urlopen(req)
    except urllib2.HTTPError, error:
        my_response = error
    response.status = my_response.getcode()
    response.set_header("Content-Type", my_response.info().getheader("Content-Type"))
    return my_response

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
def get_all_regions(mongodb, mongodbOld):
    all_regions = get_all_regions_from_mongo(mongodb=mongodb, mongodbOld=mongodbOld)
    return json.dumps(all_regions)
    #return json.dumps(make_request("/monitoring/regions", request=request))

@app.route('/monitoring/regions/<regionid>', method='GET')
@app.route('/monitoring/regions/<regionid>/', method='GET')
def get_region(regionid="ID of the region"):
    if is_region_new(regionid):
        region = get_region_from_mongo(mongodb=mongodb, regionid=regionid)
        # check region not empty and return
    else:
        return make_request("/monitoring/regions/" + regionid, request=request, regionid=regionid)

@app.route('/monitoring/regions/<regionid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/services/', method='GET')
def get_all_services_by_region(db, regionid="ID of the region"):
    return make_request("/monitoring/regions/" + regionid + "/services", request=request, regionid=regionid)

@app.route('/monitoring/regions/<regionid>/hosts', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/', method='GET')
def get_all_hosts(regionid="ID of the region"):
    return make_request("/monitoring/regions/" + regionid + "/hosts", request=request, regionid=regionid)

@app.route('/monitoring/regions/<regionid>/hosts/<hostid>', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/', method='GET')
def get_host(regionid="ID of the region", hostid="ID of the host"):
    return make_request("/monitoring/regions/" + regionid + "/hosts/" + hostid, request=request, regionid=regionid)

@app.route('/monitoring/regions/<regionid>/vms', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/', method='GET')
def get_all_vms(regionid="ID of the region"):
    return make_request("/monitoring/regions/" + regionid + "/vms/" , request=request, regionid = regionid)

@app.route('/monitoring/regions/<regionid>/vms/<vmid>', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/', method='GET')
def get_vm(regionid="ID of the region", vmid="ID of the vm"):
    return make_request("/monitoring/regions/" + regionid + "/vms/" + vmid, request=request, regionid=regionid)

@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/', method='GET')
def get_all_services_by_host(regionid="ID of the region", hostid="ID of the host"):
    return make_request("/monitoring/regions/" + regionid + "/hosts/" + hostid + "/services", request=request, regionid=regionid)

@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>/', method='GET')
def get_service_by_host(regionid="ID of the region", hostid="ID of the host", serviceName="Service name"):
    return make_request("/monitoring/regions/" + regionid + "/hosts/" + hostid + "/services/" + serviceName , request=request, regionid=regionid)

@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/', method='GET')
def get_all_services_by_vm(regionid="ID of the region", vmid="ID of the vm"):
    return make_request("/monitoring/regions/" + regionid + "/vms/" + vmid + "/services", request=request, regionid=regionid)

@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>/', method='GET')
def get_service_by_vm(regionid="ID of the region", vmid="ID of the vm", serviceName="Service name"):
    return make_request("/monitoring/regions/" + regionid + "/vms/" + vmid + "services/" + serviceName, request=request, regionid=regionid)

@app.route('/monitoring/regions/<regionid>/nes', method='GET')
@app.route('/monitoring/regions/<regionid>/nes/', method='GET')
def get_all_nes(regionid="ID of the region"):
    return make_request("/monitoring/regions/" + regionid + "/nes/", request=request, regionid=regionid)

@app.route('/monitoring/regions/<regionid>/nes/<neid>', method='GET')
@app.route('/monitoring/regions/<regionid>/nes/<neid>/', method='GET')
def get_ne(regionid="ID of the region", neid="ID of the network"):
    return make_request("/monitoring/regions/" + regionid + "/nes/" + neid, request=request, regionid=regionid)

@app.route('/monitoring/host2hosts', method='GET')
@app.route('/monitoring/host2hosts/', method='GET')
def get_host2hosts():
    print "Call to forward"
    return {}

@app.route('/monitoring/regions/<regionid>/images', method='GET')
@app.route('/monitoring/regions/<regionid>/images/', method='GET')
def get_all_images_by_region(mongodb, regionid="ID of the region"):
    if is_idm_authorized( auth_url=app.config["idm"]["account_url"], token_map=get_token_from_response(response) ):
        images = get_all_images_from_mongo(mongodb=mongodb)
    else:
        abort(401)
    return json.dumps(images) #return {'To be implemented'}

@app.route('/monitoring/regions/<regionid>/images/<imageid>', method='GET')
@app.route('/monitoring/regions/<regionid>/images/<imageid>/', method='GET')
def get_image_by_region(mongodb, regionid="ID of the region", imageid="Image id"):
    if is_idm_authorized( auth_url=app.config["idm"]["account_url"], token_map=get_token_from_response(response) ):
        image = get_image_from_mongo(mongodb=mongodb, imageid=imageid, regionid=regionid)
    else:
        abort(401)
    return json.dumps(image)

# /monitoring/host2hosts/source;dest?since=since
# /monitoring/host2hosts/source/dest?since=since

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
base_dict_region = {
        "_links": {
          "self": {
            "href": ""
          }
        },
        "id": ""
      }

base_dic_all_regions = {
  "_links": {
    "self": {
      "href": ""
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

parameters_mapping = {
  "total_nb_cores": "nb_cores",
  "total_nb_cores_enabled": "nb_cores_enabled",
  "total_nb_ram": "nb_ram",
  "total_nb_disk": "nb_disk",
  "total_nb_vm": "nb_vm",
  "total_ip_assigned": "ipAssigned",
  "total_ip_allocated": "ipAllocated",
  "total_ip": "ipTot"}

def get_all_regions_from_mongo(mongodb, mongodbOld):
    result_new = mongodb[app.config["mongodbOld"]["collectionname"]].find({"_id.type": "region"})

    region_list = []
    for region in result_new:
        region_id = region["_id"]["id"]
        base_dict_region["_links"]["self"]["href"] = "/monitoring/regions/" + region_id
        base_dict_region["id"] = region_id
        base_dic_all_regions["_embedded"]["regions"].append(copy.deepcopy(base_dict_region))
        region_list.append(region_id)

    result_old = mongodb[app.config["mongodb"]["collectionname"]].find({"_id.type": "region"})
    for region in result_old:
        if region["_id"]["id"] not in region_list:
            region_id = region["_id"]["id"]
            base_dict_region["_links"]["self"]["href"] = "/monitoring/regions/" + region_id
            base_dic_all_regions["_embedded"]["regions"].append(base_dict_region)
            region_list.append(region_id)
        # else:
        #     print region["_id"]["id"] + " already present"

    for regionid in region_list:
        region_info = get_region_from_mongo(mongodb, regionid)
        if region_info is not None:
            for attribute in parameters_mapping.iteritems():
                base_dic_all_regions[attribute(0)] = base_dic_all_regions[attribute(0)] + attribute(1)

    return base_dic_all_regions


'''
mongodb is the local mongodb bottle plugin
filter_region should be the region name, used to filter the images.
If no filter_region append all region... 
'''
def get_all_images_from_mongo(mongodb, filter_region=None):
    result = mongodb[app.config["mongodb"]["collectionname"]].find({"_id.type":"image"})
    result_dict = {"image" : []}
    for image in result:
        if filter_region is not None:
            if image["_id"]["id"].find(filter_region) != -1:
                base_dict_list["_links"]["self"]["href"] = "/monitoring/regions/" + filter_region + "/images/" + image["_id"]["id"]
                base_dict_list["id"] = image["_id"]["id"]
                result_dict["image"].append(base_dict_list)
        else:
            #This else will be removed. Used only for test as long as we have not a new mongodb in Spain and must use fake mongo
            base_dict_list["_links"]["self"]["href"] = "/monitoring/regions/--NOFILTER--/images/" + image["_id"]["id"]
            base_dict_list["id"] = image["_id"]["id"]
            result_dict["image"].append(base_dict_list)
    return result_dict

def get_image_from_mongo(mongodb, imageid, regionid):
    result = mongodb[app.config["mongodb"]["collectionname"]].find({"$and": [{"_id.type": "image" }, {"_id.id": {"$regex" : imageid}}] })
    result_dict = {"details":[]}
    for image in result:
        result_dict["details"].append(image)
    return result_dict

def get_region_from_mongo(mongodb, regionid):
    # preparo l'oggetto response
    # get sul mongo della entity region
    # get sul mongo delle entities hosts relative
    # get sul mongo delle entities vms relative
    pass

def get_vms_from_mongo(mongodb, regionid):
    pass

def get_hosts_from_mongo(mongodb, regionid):
    pass

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

#Function to convert a string to boolean value.
#Used for load_regionNew
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

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

#Main function
def main():
    #Loads and manages the input arguments
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

    #Get a map with config declared in SECTION_TO_LOAD and insert it in bottle app
    SECTION_TO_LOAD = ["mysql", "mongodb", "mongodbOld", "api", "key", "idm", "oldmonitoring", "newmonitoring", "regionNew"]
    config_map = config_to_dict(section_list = SECTION_TO_LOAD, config = Config, app=app)

    #Create and install plugin in bottle app
    mongo_map = dict(config_map["mongodb"])
    mongo_old_map = dict(config_map["mongodbOld"])
    mongo_map["keyword"] = "mongodb"
    mongo_old_map["keyword"] = "mongodbOld" #declares keyword to not conflict with mongodb instance
    mongo_old_map.pop("collectionname", None) #Remove this because MongoPlugin not recognize
    mongo_map.pop("collectionname", None)
    mongo_plugin = MongoPlugin(**mongo_map)
    mongo_plugin_old = MongoPlugin(**mongo_old_map)
    mysql_plugin = bottle_mysql.Plugin(**config_map["mysql"])

    app.install(mongo_plugin)
    app.install(mongo_plugin_old)
    app.install(mysql_plugin)
    ##

    listen_url = config_map['api']['listen_url']
    listen_port = config_map['api']['listen_port']
    
    #App runs in infinite loop
    httpserver.serve(app, host=listen_url, port=listen_port)

if __name__ == '__main__':
    main()