#!/usr/bin/env python
from __future__ import division
from bottle import route, run, request, error, response, Bottle, redirect, HTTPError, abort
from pymongo import MongoClient, database
from bottle.ext.mongo import MongoPlugin
from bson.json_util import dumps
from paste import httpserver
from multiprocessing.pool import Pool
from multiprocessing import TimeoutError
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

###Main bottle app
app = Bottle()
#####

HEADER_AUTH = "X-Auth-Token"


# Return if the token is authorized with auth_url
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
    if is_region_new(regionid):
        return app.config["newmonitoring"]["url"], app.config["newmonitoring"]["port"]
    else:
        return app.config["oldmonitoring"]["url"], app.config["oldmonitoring"]["port"]


'''
Return True if region use new monitoring system false otherwise
'''


def is_region_new(regionid):
    if is_region_on(regionid) and str2bool(app.config["main_config"]["regionNew"][regionid]):
        return True
    return False


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


def make_request(request_url, request, regionid=None):
    my_response = do_http_get(request_url, request, regionid)
    response.status = my_response.getcode()
    response.set_header("Content-Type", my_response.info().getheader("Content-Type"))
    return my_response


'''
Make the request to appropriate monitoringAPI and return raw http_response
args:   request in the form: "/" or "/monitoring/regions" etc.
return empty array if error
'''


def do_http_get(request_url, request, regionid=None):
    monitoring_url, monitoring_port = select_monitoring_to_forward(regionid)
    base_url = "http://" + monitoring_url + ":" + monitoring_port
    if request is None or not request.query_string:
        uri = base_url + request_url
    else:
        uri = base_url + request_url + "?" + request.query_string
    req = urllib2.Request(uri)
    token_map = get_token_from_response(request)
    if bool(token_map):
        req.headers[token_map.iteritems().next()[0]] = token_map.iteritems().next()[1]
    try:
        my_response = urllib2.urlopen(req)
    except urllib2.HTTPError, error:
        my_response = error
    return my_response


@app.route('/')
def root():
    return make_request("/", request=request)


@app.route('/monitoring/regions', method='GET')
@app.route('/monitoring/regions/', method='GET')
def get_all_regions(mongodb, mongodbOld):
    all_regions = get_all_regions_from_mongo(mongodb=mongodb, mongodbOld=mongodbOld)
    return json.dumps(all_regions)
    # return json.dumps(make_request("/monitoring/regions", request=request))


@app.route('/monitoring/regions/<regionid>', method='GET')
@app.route('/monitoring/regions/<regionid>/', method='GET')
def get_region(mongodb, regionid="ID of the region"):
    if not is_region_on(regionid):
        abort(404)
    if is_region_new(regionid) and request.params.getone("since") is None:
        region = get_region_from_mongo(mongodb=mongodb, regionid=regionid)
        if region is not None:
            return region
        else:
            abort(404)
    else:
        return make_request("/monitoring/regions/" + regionid, request=request, regionid=regionid)


@app.route('/monitoring/regions/<regionid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/services/', method='GET')
def get_all_services_by_region(db, regionid="ID of the region"):
    if is_region_on(regionid):
        return make_request("/monitoring/regions/" + regionid + "/services", request=request, regionid=regionid)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/hosts', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/', method='GET')
def get_all_hosts(mongodb, regionid="ID of the region"):
    if not is_region_on(regionid):
        abort(404)
    if is_region_new(regionid):
        hosts = get_hosts_from_mongo(mongodb=mongodb, regionid=regionid)
        if hosts is not None:
            return hosts
        else:
            abort(404)
    else:
        return make_request("/monitoring/regions/" + regionid + "/hosts", request=request, regionid=regionid)


@app.route('/monitoring/regions/<regionid>/hosts/<hostid>', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/', method='GET')
def get_host(mongodb, regionid="ID of the region", hostid="ID of the host"):
    if not is_region_on(regionid):
        abort(404)
    if is_region_new(regionid) and request.params.getone("since") is None:
        if not is_idm_authorized(auth_url=app.config["idm"]["account_url"], token_map=get_token_from_response(request)):
            abort(401)
        region = get_doc_region_from_mongo(mongodb, regionid)
        host = get_host_from_mongo(mongodb, region, hostid)
        if host is not None:
            return host
        else:
            abort(404)
    else:
        return make_request("/monitoring/regions/" + regionid + "/hosts/" + hostid, request=request, regionid=regionid)


@app.route('/monitoring/regions/<regionid>/vms', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/', method='GET')
def get_all_vms(regionid="ID of the region"):
    if is_region_on(regionid):
        return make_request("/monitoring/regions/" + regionid + "/vms/", request=request, regionid=regionid)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/vmsdetails', method='GET')
@app.route('/monitoring/regions/<regionid>/vmsdetails/', method='GET')
def get_all_vms(regionid="ID of the region"):
    if is_region_on(regionid):
        return make_request("/monitoring/regions/" + regionid + "/vmsdetails/", request=request, regionid=regionid)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/vms/<vmid>', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/', method='GET')
def get_vm(regionid="ID of the region", vmid="ID of the vm"):
    if is_region_on(regionid):
        return make_request("/monitoring/regions/" + regionid + "/vms/" + vmid, request=request, regionid=regionid)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/', method='GET')
def get_all_services_by_host(regionid="ID of the region", hostid="ID of the host"):
    if is_region_on(regionid):
        return make_request("/monitoring/regions/" + regionid + "/hosts/" + hostid + "/services", request=request,
                            regionid=regionid)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>/', method='GET')
def get_service_by_host(regionid="ID of the region", hostid="ID of the host", serviceName="Service name"):
    if is_region_on(regionid):
        return make_request("/monitoring/regions/" + regionid + "/hosts/" + hostid + "/services/" + serviceName,
                            request=request, regionid=regionid)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/', method='GET')
def get_all_services_by_vm(regionid="ID of the region", vmid="ID of the vm"):
    if is_region_on(regionid):
        return make_request("/monitoring/regions/" + regionid + "/vms/" + vmid + "/services", request=request,
                            regionid=regionid)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>/', method='GET')
def get_service_by_vm(regionid="ID of the region", vmid="ID of the vm", serviceName="Service name"):
    if is_region_on(regionid):
        return make_request("/monitoring/regions/" + regionid + "/vms/" + vmid + "services/" + serviceName,
                            request=request, regionid=regionid)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/nes', method='GET')
@app.route('/monitoring/regions/<regionid>/nes/', method='GET')
def get_all_nes(regionid="ID of the region"):
    if is_region_on(regionid):
        return make_request("/monitoring/regions/" + regionid + "/nes/", request=request, regionid=regionid)
    else:
        abort(404)


@app.route('/monitoring/regions/<regionid>/nes/<neid>', method='GET')
@app.route('/monitoring/regions/<regionid>/nes/<neid>/', method='GET')
def get_ne(regionid="ID of the region", neid="ID of the network"):
    if is_region_on(regionid):
        return make_request("/monitoring/regions/" + regionid + "/nes/" + neid, request=request, regionid=regionid)
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
    if is_idm_authorized(auth_url=app.config["idm"]["account_url"], token_map=get_token_from_response(response)):
        images = get_all_images_from_mongo(mongodb=mongodb)
    else:
        abort(401)
    return json.dumps(images)  # return {'To be implemented'}


@app.route('/monitoring/regions/<regionid>/images/<imageid>', method='GET')
@app.route('/monitoring/regions/<regionid>/images/<imageid>/', method='GET')
def get_image_by_region(mongodb, regionid="ID of the region", imageid="Image id"):
    if not is_region_on(regionid):
        abort(404)
    if is_idm_authorized(auth_url=app.config["idm"]["account_url"], token_map=get_token_from_response(response)):
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

all_region_parameters_mapping = {
    "total_nb_cores": "nb_cores",
    "total_nb_cores_enabled": "nb_cores_enabled",
    "total_nb_ram": "nb_ram",
    "total_nb_disk": "nb_disk",
    "total_nb_vm": "nb_vm",
    "total_ip_assigned": "ipAssigned",
    "total_ip_allocated": "ipAllocated",
    "total_ip": "ipTot"}


def get_all_regions_from_js():
    return json.loads(do_http_get("/monitoring/regions", request=None).read())


def get_all_regions_from_mongo(mongodb, mongodbOld):
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

    pool = Pool(processes=1)
    async_result = pool.apply_async(get_all_regions_from_js, ()) # Start thread for async http call

    new_regions = app.config["main_config"]["regionNew"]
    region_list = {}

    for region_id, is_new in new_regions.iteritems():
        if str2bool(is_new):
            region = get_region_from_mongo(mongodb, region_id)
            if region is not None:
                region_list[region_id] = region
        elif not str2bool(is_new):
            response = make_request("/monitoring/regions/" + region_id, request=None, regionid=region_id)
            if response.getcode() == 200:
                region_list[region_id] = json.loads(response.read())

    for region in region_list.iteritems():
        region = region[1]
        region_item = {"id": {}, "_links": {"self": {"href": {}}}}
        region_item["id"] = region["id"]
        region_item["_links"]["self"]["href"] = "/monitoring/regions/" + region["id"]
        regions_entity["_embedded"]["regions"].append(copy.deepcopy(region_item))
        # sum resources form each region entity
        if region["nb_cores"] != '':
            regions_entity["total_nb_cores"] += int(region["nb_cores"])
            regions_entity["total_nb_cores_enabled"] += int(region["nb_cores"])
        if region["nb_ram"] != '':
            regions_entity["total_nb_ram"] += int(region["nb_ram"])
        if region["nb_disk"] != '':
            regions_entity["total_nb_disk"] += int(region["nb_disk"])
        if region["nb_vm"] != '':
            regions_entity["total_nb_vm"] += int(region["nb_vm"])
        if region["measures"][0]["ipAssigned"] != '':
            regions_entity["total_ip_assigned"] += int(decimal.Decimal(region["measures"][0]["ipAssigned"]).normalize())
        if region["measures"][0]["ipAllocated"] != '':
            regions_entity["total_ip_allocated"] += int(
                decimal.Decimal(region["measures"][0]["ipAllocated"]).normalize())
        if region["measures"][0]["ipTot"] != '':
            regions_entity["total_ip"] += int(decimal.Decimal(region["measures"][0]["ipTot"]).normalize())

    # get IDM infos from oldMonitoring
    try:
        regions_tmp = async_result.get(10)  # get the return value from thread
        regions_entity["basicUsers"] = regions_tmp["basicUsers"]
        regions_entity["trialUsers"] = regions_tmp["trialUsers"]
        regions_entity["communityUsers"] = regions_tmp["communityUsers"]
        regions_entity["totalUsers"] = regions_tmp["totalUsers"]
        regions_entity["total_nb_users"] = regions_tmp["total_nb_users"]
        regions_entity["totalCloudOrganizations"] = regions_tmp["totalCloudOrganizations"]
        regions_entity["totalUserOrganizations"] = regions_tmp["totalUserOrganizations"]
        regions_entity["total_nb_organizations"] = regions_tmp["total_nb_organizations"]
    except TimeoutError:
        print("HTTP call to JS monitoringAPI to retrieve IDM info did not respond in 10 seconds. No IDM data returned")
    finally:
        pool.close()
        pool.join()
    return regions_entity


'''
mongodb is the local mongodb bottle plugin
filter_region should be the region name, used to filter the images.
If no filter_region append all region...
'''


def get_all_images_from_mongo(mongodb, filter_region=None):
    result = mongodb[app.config["mongodb"]["collectionname"]].find({"_id.type": "image"})
    result_dict = {"image": []}
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
    result = mongodb[app.config["mongodb"]["collectionname"]].find(
        {"$and": [{"_id.type": "image"}, {"_id.id": {"$regex": imageid}}]})
    result_dict = {"details": []}
    for image in result:
        result_dict["details"].append(image)
    return result_dict


def get_region_from_mongo(mongodb, regionid):
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
                "nb_cores_used": 0,
                # "nb_cores_enabled": 0,
                "nb_cores": 0,
                "nb_disk": 0,
                "nb_ram": 0,
                "nb_vm": 0,
                "ram_allocation_ratio": "",
                "cpu_allocation_ratio": "",
                "percRAMUsed": 0,
                "percDiskUsed": 0
            }
        ],
        "id": "",
        "name": "",
        "country": "",
        "latitude": "",
        "longitude": "",
        "nb_cores": 0,
        # "nb_cores_enabled": 0,
        "nb_cores_used": 0,
        "nb_ram": 0,
        "nb_disk": 0,
        "nb_vm": 0,
        "power_consumption": ""
    }
    # get sul mongo della entity region
    region = mongodb[app.config["mongodb"]["collectionname"]].find_one({"$and": [{"_id.type": "region"}, {"_id.id": regionid}]})
    if region is None: return None
    # for region in regions:
    if regionid is not None and region["_id"]["id"] == regionid:

        region_entity["_links"]["self"]["href"] = "/monitoring/regions/" + regionid
        region_entity["_links"]["hosts"]["href"] = "/monitoring/regions/" + regionid + "/hosts"
        d = datetime.datetime.fromtimestamp(int(region["modDate"]))
        region_entity["measures"][0]["timestamp"] = d.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        if region["attrs"].has_key('ipUsed'):
            region_entity["measures"][0]["ipAssigned"] = region["attrs"]["ipUsed"]["value"]
        if region["attrs"].has_key('ipAvailable'):
            region_entity["measures"][0]["ipAllocated"] = region["attrs"]["ipAvailable"]["value"]
        if region["attrs"].has_key('ipTot'):
            region_entity["measures"][0]["ipTot"] = region["attrs"]["ipTot"]["value"]

        if region["attrs"].has_key('ram_allocation_ratio'):
            region_entity["measures"][0]["ram_allocation_ratio"] = region["attrs"]["ram_allocation_ratio"]["value"]
        if region["attrs"].has_key('cpu_allocation_ratio'):
            region_entity["measures"][0]["cpu_allocation_ratio"] = region["attrs"]["cpu_allocation_ratio"]["value"]

        region_entity["id"] = region["_id"]["id"]
        region_entity["name"] = region["_id"]["id"]
        if region["attrs"].has_key('location'):
            region_entity["country"] = region["attrs"]["location"]["value"]
        if region["attrs"].has_key('latitude'):
            region_entity["latitude"] = region["attrs"]["latitude"]["value"]
        if region["attrs"].has_key('longitude'):
            region_entity["longitude"] = region["attrs"]["longitude"]["value"]

        # aggragation from virtual machines on region
        vms = get_cursor_active_vms_from_mongo(mongodb, regionid)
        if vms is not None:
            vms_data = aggr_vms_data(vms)
            region_entity["measures"][0]["nb_vm"] = vms_data["nb_vm"]
            region_entity["nb_vm"] = vms_data["nb_vm"]

        # aggragation from hosts on region
        hosts = get_cursor_hosts_from_mongo(mongodb, regionid)
        if hosts is not None:
            hosts_data = aggr_hosts_data(hosts)
            region_entity["nb_ram"] = hosts_data["ramTot"]
            region_entity["measures"][0]["nb_ram"] = hosts_data["ramTot"]
            region_entity["nb_disk"] = hosts_data["diskTot"]
            region_entity["measures"][0]["nb_disk"] = hosts_data["diskTot"]
            region_entity["nb_cores"] = hosts_data["cpuTot"]
            region_entity["measures"][0]["nb_cores"] = hosts_data["cpuTot"]
            region_entity["nb_cores_used"] = hosts_data["cpuNow"]
            region_entity["measures"][0]["nb_cores_used"] = hosts_data["cpuNow"]
            region_entity["measures"][0]["percRAMUsed"] = 0
            region_entity["measures"][0]["percDiskUsed"] = 0
            if hosts_data["ramTot"] != 0:
                region_entity["measures"][0]["percRAMUsed"] = hosts_data["ramNowTot"] / (
                hosts_data["ramTot"] * float(region["attrs"]["ram_allocation_ratio"]["value"]))
            if hosts_data["diskTot"] != 0:
                region_entity["measures"][0]["percDiskUsed"] = hosts_data["diskNowTot"] / hosts_data["diskTot"]
    else:
        return None
    return region_entity


def get_host_from_mongo(mongodb, region, hostid):
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

    regionid = region["_id"]["id"]
    ram_ratio = region["attrs"]["ram_allocation_ratio"]["value"] if region["attrs"].has_key(
        "ram_allocation_ratio") else false
    host = get_doc_host_from_mongo(mongodb, regionid, hostid)
    if host is None:
        return None
    else:
        host_entity["_links"]["self"]["href"] = "/monitoring/regions/" + regionid + "/hosts/" + hostid
        host_entity["_links"]["services"]["href"] = host_entity["_links"]["self"]["href"] + "/services"
        host_entity["regionid"] = regionid
        host_entity["hostid"] = hostid
        host_entity["role"] = "compute"
        if host["attrs"].has_key("_timestamp"):
            host_entity["measures"][0]["timestamp"] = host["attrs"]["_timestamp"]["value"]
        if host["attrs"].has_key("cpuPct"):
            cpu_pct = round(float(host["attrs"]["cpuPct"]["value"]), 2)
            host_entity["measures"][0]["percCPULoad"]["value"] = str(cpu_pct)
        else:
            del host_entity["measures"][0]["percCPULoad"]
        if host["attrs"].has_key("ramNow") and host["attrs"].has_key("ramTot") and ram_ratio:
            ram_used = int(host["attrs"]["ramNow"]["value"])
            ram_tot = int(host["attrs"]["ramTot"]["value"])
            ram_pct = round(100 * ram_used / (ram_tot * float(ram_ratio)))
            host_entity["measures"][0]["percRAMUsed"]["value"] = str(ram_pct)
        else:
            del host_entity["measures"][0]["percRAMUsed"]
        if host["attrs"].has_key("diskNow") and host["attrs"].has_key("diskTot"):
            disk_used = int(host["attrs"]["diskNow"]["value"])
            disk_tot = int(host["attrs"]["diskTot"]["value"])
            host_entity["measures"][0]["percDiskUsed"]["value"] = round((100 * disk_used / disk_tot), 2)
        else:
            del host_entity["measures"][0]["percDiskUsed"]
        return host_entity


def get_hosts_from_mongo(mongodb, regionid):
    hosts = get_cursor_hosts_from_mongo(mongodb, regionid)
    if hosts is None:
        return None
    result_dict = {"hosts": [], "links": {"self": {"href": "/monitoring/regions/" + regionid + "/hosts"}}}
    for host in hosts:
        hostid = host["_id"]["id"].split(":")[1]
        base_dict_list["_links"]["self"]["href"] = "/monitoring/regions/" + regionid + "/hosts/" + hostid
        base_dict_list["id"] = hostid
        result_dict["hosts"].append(copy.deepcopy(base_dict_list))
    return result_dict


def get_cursor_vms_from_mongo(mongodb, regionid):
    vms = mongodb[app.config["mongodb"]["collectionname"]].find(
        {"$and": [{"_id.type": "vm"}, {"_id.id": {"$regex": regionid + ':'}}]})
    if vms.count() >= 1:
        return vms
    else:
        return None


def get_cursor_active_vms_from_mongo(mongodb, regionid):
    vms = mongodb[app.config["mongodb"]["collectionname"]].find(
        {"$and": [{"_id.type": "vm"}, {"_id.id": {"$regex": regionid + ':'}}, {"attrs.status.value": "active"}]})
    if vms.count() >= 1:
        return vms
    else:
        return None


def get_cursor_hosts_from_mongo(mongodb, regionid):
    hosts = mongodb[app.config["mongodb"]["collectionname"]].find(
        {"$and": [{"_id.type": "host"}, {"_id.id": {"$regex": regionid + ':'}}]})
    if hosts.count() >= 1:
        return hosts
    else:
        return None


def get_doc_host_from_mongo(mongodb, regionid, hostid):
    return mongodb[app.config["mongodb"]["collectionname"]].find_one(
        {"$and": [{"_id.type": "host"}, {"_id.id": {"$regex": regionid + ':' + hostid}}]})


def get_doc_region_from_mongo(mongodb, regionid):
    return mongodb[app.config["mongodb"]["collectionname"]].find_one(
        {"$and": [{"_id.type": "region"}, {"_id.id": regionid}]})


def aggr_vms_data(vms):
    """
    Function that aggregate vm entity data given a collection (cursor retuned from mongo query) of vms
    """
    vms_data = {"nb_vm": 0}
    vms_data["nb_vm"] = vms.count()
    return vms_data


def aggr_hosts_data(hosts):
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
    return hosts_data


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


# Function to convert a string to boolean value.
# Used for load_regionNew
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
        app.config['main_config']['regionNew'] = dict(main_config._sections['regionNew'])
    except Exception as e:
        print("Problem parsing main config file: {}").format(e)
        sys.exit(-1)

    # Get a map with config declared in SECTION_TO_LOAD and insert it in bottle app
    SECTION_TO_LOAD = ["mysql", "mongodb", "mongodbOld", "api", "key", "idm", "oldmonitoring", "newmonitoring"]
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

    # App runs in infinite loop
    httpserver.serve(app, host=listen_url, port=listen_port)


if __name__ == '__main__':
    main()
