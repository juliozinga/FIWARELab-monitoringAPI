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
import datetime
import math


#Main bottle app
app = Bottle()

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

@app.error(404)
def error404(error):
    response.content_type = 'application/json'
    return {'Request not found'}

@app.error(401)
def error401(error):
    response.content_type = 'application/json'
    return {'UNAUTHORIZED'}

@app.route('/')
def root(mongodb):
    output = {
        "_links": {
            "self": {
                "href": "/"
            },
            "region": {
                "href": "/monitoring/regions",
                "templated": "true"
            },
            "host2hosts": {
                "href": "/monitoring/host2hosts",
                "templated": "true"
            }
        }
    }
    return output

@app.route('/monitoring/regions', method='GET')
@app.route('/monitoring/regions/', method='GET')
def get_all_regions(mongodb):
    base_url = "/monitoring/regions/"
    total_vms = 0
    basicUsers = 0
    trialUsers = 0
    communityUsers = 0
    totalUsers = 0
    total_nb_users = 0 #backward compatibility*/
    totalUserOrganizations = 0
    totalCloudOrganizations = 0
    total_nb_organizations = 0.0 #backward compatibility*/
    total_nb_cores = 0.0
    total_nb_cores_enabled = 0.0
    total_nb_ram = 0.0
    total_nb_disk = 0.0
    total_nb_vm = 0.0
    total_ip_used = 0
    total_ip_allocated = 0
    total_ip = 0
    tmp_reg = []
    tmp_res={"_links": {"self": { "href": "" }},"measures":[{}], "_embedded":{"regions":[]} }
    particular_region = ["Berlin", "Stockholm2", "SaoPaulo", "Mexico"]

    since = None
    if request.query.getone('since') is not None:
        since = request.query.getone('since')

    result = mongodb[app.config.get("collectionname")].find({"_id.type":"region"})
    now = int(time.time())
    for region in result:
        if region["_id"]["id"] not in particular_region:
            href_txt = "/monitoring/regions/"+region["_id"]["id"]
            tmp_reg.append({"_links" : {"self": { "href": href_txt}}, "id": region["_id"]["id"]})

            for att in region["attrs"]:

                #Copiato dal codice nodejs e tradotto in python
                if att["name"] and att["name"].find("coreEnabled") != -1:
                    if att["value"]:
                        #if now-regions[i].modDate<cfgObj.regionTTL:
                            total_nb_cores_enabled+=int(float(att["value"]))

                if att["name"] and att["name"].find("ipUsed") != -1:
                    if att["value"]:
                        #if now-regions[i].modDate<cfgObj.regionTTL:
                            total_ip_used+=int(float(att["value"]))

                if att["name"] and att["name"].find("ipAvailable") != -1:
                    if att["value"]:
                        #if now-regions[i].modDate<cfgObj.regionTTL:
                            total_ip_allocated+=int(float(att["value"]))

                if att["name"] and att["name"].find("ipTot") != -1:
                    if att["value"]:
                        #if now-regions[i].modDate<cfgObj.regionTTL:
                            total_ip+=int(float(att["value"]))

                if att["name"] and att["name"].find("coreTot") != -1:
                    if att["value"]:
                        #if now-regions[i].modDate<cfgObj.regionTTL:
                            total_nb_cores+=int(float(att["value"]))

                if att["name"] and att["name"].find("ramTot") != -1:
                    if att["value"]:
                        #if now-regions[i].modDate<cfgObj.regionTTL:
                            total_nb_ram+=int(float(att["value"]))

                if att["name"] and att["name"].find("hdTot") != -1:
                    if att["value"]:
                        #if now-regions[i].modDate<cfgObj.regionTTL:
                            total_nb_disk+=int(float(att["value"]))

                if att["name"] and att["name"].find("vmList") != -1:
                    for vm in att["value"].split(';'):
                        if vm.find('ACTIVE'):
                            total_vms = total_vms + 1

    tmp_res["_embedded"]["regions"].append(tmp_reg)
    tmp_res["total_nb_vm"] = total_vms
    tmp_res["basicUsers"] = basicUsers
    tmp_res["trialUsers"] = trialUsers
    tmp_res["communityUsers"] = communityUsers
    tmp_res["totalUsers"] = totalUsers
    tmp_res["total_nb_users"] = total_nb_users
    tmp_res["totalCloudOrganizations"] = totalCloudOrganizations
    tmp_res["totalUserOrganizations"] = totalUserOrganizations
    tmp_res["total_nb_organizations"] = total_nb_organizations
    tmp_res["total_nb_cores"] = total_nb_cores
    tmp_res["total_nb_cores_enabled"] = total_nb_cores_enabled
    tmp_res["total_nb_ram"] = total_nb_ram
    tmp_res["total_nb_disk"] = total_nb_disk
    tmp_res["total_ip_assigned"] =  total_ip_used
    tmp_res["total_ip_allocated"] =  total_ip_allocated
    tmp_res["total_ip"] = total_ip

    #Authentication part
    try:
        idm_body = request_to_idm(username=app.config.get("idm_username"),
                                password=app.config.get("idm_password"),
                                keypass_url=app.config.get("token_url"),
                                url=app.config.get("service_url"))
        idm_body_json = json.loads(idm_body.read())
    except Exception as e:
        abort(401)

    if idm_body_json["information"]["basicUsers"]:
        basicUsers = idm_body_json["information"]["basicUsers"]
    if idm_body_json["information"]["trialUsers"]:
        trialUsers = idm_body_json["information"]["trialUsers"]
    if idm_body_json["information"]["communityUsers"]:
        communityUsers = idm_body_json["information"]["communityUsers"]
    if idm_body_json["information"]["totalUsers"]:
        totalUsers = idm_body_json["information"]["totalUsers"]
    if idm_body_json["information"]["totalCloudOrganizations"]:
        totalCloudOrganizations = idm_body_json["information"]["totalCloudOrganizations"]
    if idm_body_json["information"]["totalUserOrganizations"]:
        totalUserOrganizations = idm_body_json["information"]["totalUserOrganizations"]

    total_nb_users = basicUsers + trialUsers + communityUsers
    total_nb_organizations = totalUserOrganizations + totalCloudOrganizations

    if len(tmp_reg) > 0:
        _embedded={}
        _embedded["regions"] = tmp_reg
        tmp_res["_embedded"] = _embedded

    tmp_res["basicUsers"] = basicUsers
    tmp_res["trialUsers"] = trialUsers

    tmp_res["communityUsers"] = communityUsers
    tmp_res["totalUsers"] = totalUsers

    tmp_res["total_nb_users"] = total_nb_users
    tmp_res["totalCloudOrganizations"] = totalCloudOrganizations

    tmp_res["totalUserOrganizations"] = totalUserOrganizations
    tmp_res["total_nb_organizations"] = total_nb_organizations

    tmp_res["total_nb_cores"] = total_nb_cores
    tmp_res["total_nb_cores_enabled"] = total_nb_cores_enabled

    tmp_res["total_nb_ram"] = total_nb_ram
    tmp_res["total_nb_disk"] =total_nb_disk

    tmp_res["total_nb_vm"] = total_nb_vm
    tmp_res["total_ip_assigned"] = total_ip_used

    tmp_res["total_ip_allocated"] = total_ip_allocated
    tmp_res["total_ip"] = total_ip

    return tmp_res

@app.route('/monitoring/regions/<regionid>', method='GET')
@app.route('/monitoring/regions/<regionid>/', method='GET')
def get_region(mongodb, regionid="ID of the region"):
    if regionid == "Berlin":
        abort(404)

    since = None
    if request.query.getone('since') is not None:
        since = request.query.getone('since')

    region = mongodb[app.config.get("collectionname")].find_one({"$and": [{"_id.type": "region" }, {"_id.id": regionid}] })

    tmp_res = {"_links": {"self": { "href": "" }, "hosts" : ""}, "measures":[]}
    tmp_res["_links"]["self"]["href"] = "/monitoring/regions/" + regionid
    tmp_A = {}
    ram_allocation_ratio = "1.5"
    cpu_allocation_ratio = "16.0"
    tmp_res["id"] = ""
    tmp_res["name"] = ""
    tmp_res["country"] = ""
    tmp_res["latitude"] = ""
    tmp_res["longitude"] = ""
    tmp_res["nb_cores"] = ""
    tmp_res["nb_cores_enabled"] = ""
    tmp_res["nb_cores_used"] = ""
    tmp_res["nb_ram"] = ""
    tmp_res["nb_disk"] = ""
    tmp_res["nb_vm"] = ""
    tmp_res["power_consumption"] = ""
    tmp_res["timestamp"] = datetime.datetime.now().isoformat()
    nb_ram_used = 0
    nb_disk_used = 0
    vms = 0

    tmp_res["_links"]["hosts"] = {"href":"/monitoring/regions/"+regionid+"/hosts"}
    tmp_res["id"] = regionid;
    tmp_res["name"] = regionid;

    for att in region["attrs"]:
        if att["name"] and att["name"].find("location") == 0:
            if att["value"]:
                tmp_res["country"] = att["value"]
        if att["name"] and att["name"].find("ipUsed") != -1:
             if att["value"]:
                 tmp_A[" "] = att["value"]
        if att["name"] and att["name"].find("ipAvailable") != -1:
             if att["value"]:
                 tmp_A["ipAllocated"] = att["value"]
        if att["name"] and att["name"].find("ipTot") != -1:
             if att["value"]:
                 tmp_A["ipTot"] = att["value"]
        if att["name"] and att["name"].find("cpu_allocation_ratio") != -1:
             if att["value"]:
                cpu_allocation_ratio = att["value"]
                tmp_A["cpu_allocation_ratio"] = att["value"]
        if att["name"] and att["name"].find("ram_allocation_ratio") != -1:
            if att["value"]:
                ram_allocation_ratio = att["value"]
                tmp_A["ram_allocation_ratio"] = att["value"]
        if att["name"] and att["name"].find("latitude") != -1:
             if att["value"]:
                 tmp_res["latitude"] = att["value"]
        if att["name"] and att["name"].find("longitude") != -1:
             if att["value"]:
                 tmp_res["longitude"] = att["value"]
        if att["name"] and att["name"].find("coreUsed") != -1:
             if att["value"]:
                 tmp_res["nb_cores_used"] = int(att["value"])
                 tmp_A["nb_cores_used"] = int(att["value"])
        if att["name"] and att["name"].find("coreEnabled") != -1:
             if att["value"]:
                 tmp_res["nb_cores_enabled"] = int(att["value"])
                 tmp_A["nb_cores_enabled"] = int(att["value"])
        if att["name"] and att["name"].find("coreTot") != -1:
             if att["value"]:
                 tmp_res["nb_cores"] = int(att["value"])
                 tmp_A["nb_cores"] = int(att["value"])
        if att["name"] and att["name"].find("ramTot") != -1:
             if att["value"]:
                 tmp_res["nb_ram"] = int(att["value"])
                 tmp_A["nb_ram"] = int(att["value"])
        if att["name"] and att["name"].find("ramUsed") != -1:
            if att["value"]:
                nb_ram_used=int(att["value"])
        if att["name"] and att["name"].find("hdTot") != -1:
             if att["value"]:
                 tmp_res["nb_disk"] = int(att["value"])
                 tmp_A["nb_disk"] = int(att["value"])
        if att["name"] and att["name"].find("hdUsed") != -1:
            if att["value"]:
                nb_disk_used = int(att["value"])
        if att["name"] and att["name"].find("vmList") != -1:
            for vm in att["value"].split(";"):
                if vm.find("ACTIVE") != -1:
                    vms = vms + 1
            tmp_res["nb_vm"] = vms
            tmp_A["nb_vm"] = vms

    tmp_res["measures"].append(tmp_A)

    if tmp_A["nb_ram"] != 0:
        tmp_A["percRAMUsed"] = nb_ram_used/(tmp_A["nb_ram"] * float(1.5))
    else:
        tmp_A["percRAMUsed"]  = 0

    if tmp_A["nb_disk"] != 0:
        tmp_A["percDiskUsed"] = nb_disk_used/tmp_A["nb_disk"]
    else:
        tmp_A["percDiskUsed"] = 0

    datetime.datetime.now().isoformat()

    return tmp_res

@app.route('/monitoring/regions/<regionid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/services/', method='GET')
def get_all_services_by_region(mongodb, regionid="ID of the region"):
    since = None
    if request.query.getone('since') is not None:
        since = request.query.getone('since')

    tmp_res={"_links": {"self": { "href": "" }},"measures":[{}]}
    novaActive = 0
    novaTot = 0
    cinderActive = 0
    cinderTot = 0
    quantumActive = 0
    quantumTot = 0
    qL3 = 0
    qL3Status = 0
    qDhcp = 0
    qDhcpStatus = 0
    glanceActive = 0
    glanceTot = 0
    servActive = 0
    servTot = 0
    kpActive = 0
    kpTot = 0
    sanActive = 0
    sanTot = 0
    sanTime = 0

    services = mongodb[app.config.get("collectionname")].find({"$and": [{"_id.type": "host_service" }, {"_id.id": {"$regex" : regionid+':'}}] })
    regionInfo = mongodb[app.config.get("collectionname")].find_one({"$and": [{"_id.type": "region" }, {"_id.id": regionid}] })
    now = int(time.time())

    for att in regionInfo["attrs"]:
        if att["name"].find("sanity") != -1:
            if att["name"] == "sanity_check_timestamp":
                sanTime = math.floor(float(att["value"])/1000)
            else:
                sanActive += 1
                tmp_val = 0
                if att["value"] == "OK":
                    tmp_val = 1
                if att["value"] == "POK":
                    tmp_val = 0.75
                if att["value"] == "NOK":
                    tmp_val = 0
                sanTot = sanTot + tmp_val

    service_list = ["nova", "cinder", "glance", "keystone-proxy"]
    for service in services:
        tmpId = service["_id"]["id"]
        if service["_id"]["id"].split(':')[0]:
            region_id = service["_id"]["id"].split(':')[0]
        if service["_id"]["id"].split(':')[1]:
            node_id = service["_id"]["id"].split(':')[1]
        if service["_id"]["id"].split(':')[2]:
            service_id = service["_id"]["id"].split(':')[2]

        if service_id and service["attrs"][0]["value"]:
            servVal = service["attrs"][0]["value"]
            servTot += 1
            if servVal == 1:
                servActive += 1
            if service_id.find("nova") != -1:
                novaTot += 1;
                if servVal==1:
                    novaActive += 1;
            elif service_id.find("cinder") != -1:
                cinderTot += 1;
                if servVal == 1:
                    cinderActive += 1
            elif service_id.find("glance") != -1:
                glanceTot += 1
                if servVal == 1:
                     glanceActive += 1
            elif service_id.find("keystone-proxy") != -1:
                kpTot += 1
                if servVal == 1:
                    kpActive += 1
            elif service_id.find("quantum-l3-agent") != -1:
                qL3 += 1
                if servVal == 1:
                    qL3Status = 1
            elif service_id.find("quantum-dhcp-agent") != -1:
                qDhcp += 1
                if servVal == 1:
                    qDhcpStatus = 1
            elif service_id.find("quantum-dhcp-agent") == -1 and service_id.find("quantum-l3-agent") == -1 and service_id.find("quantum") != -1:
                quantumTot += 1
                if servVal == 1:
                    quantumActive += 1

    nova = "undefined"
    cinder = "undefined"
    quantum = "undefined"
    glance = "undefined"
    idm = "undefined"
    serv = "undefined"
    kp = "undefined"
    san = "undefined"

    if qDhcpStatus == 1:
        quantumActive += 1
    if qDhcpStatus == 1:
        quantumActive += 1
    if qL3Status == 1:
        quantumActive += 1
    if novaActive and novaTot and novaTot > 0:
        if novaActive/novaTot >= 0.9:
            nova = "green"
        elif novaActive/novaTot < 0.99 and novaActive/novaTot >= 0.5:
            nova = "yellow"
        elif novaActive/novaTot < 0.5  and novaActive/novaTot > 0:
            nova = "red"

    if cinderActive and cinderTot and cinderTot>0:
        if cinderActive/cinderTot >= 0.99:
            cinder = "green"
        elif cinderActive/cinderTot<0.99 and cinderActive/cinderTot>=0.5:
            cinder="yellow"
        elif cinderActive/cinderTot<0.5  and cinderActive/cinderTot>0:
            cinder="red"

    if quantumActive and quantumTotand:
        quantumTot>0
        if quantumActive/quantumTot>=0.9:
            quantum="green"
        elif quantumActive/quantumTot<0.9 and quantumActive/quantumTot>=0.2:
            quantum="yellow"
        elif quantumActive/quantumTot<0.2  and quantumActive/quantumTot>0:
            quantum="red"

    if glanceActive and glanceTot and glanceTot>0:
        if glanceActive/glanceTot>=0.99:
            glance="green"
        elif glanceActive/glanceTot<0.99 and glanceActive/glanceTot>=0.5:
            glance="yellow"
        elif glanceActive/glanceTot<0.5 and glanceActive/glanceTot>0:
            glance="red"

    if kpActive and kpTot and kpTot>0:
        if kpActive/kpTot>=0.99:
            kp="green"
        elif kpActive/kpTot<0.99 and kpActive/kpTot>=0.5:
            kp="yellow"
        elif kpActive/kpTot<0.5 and kpActive/kpTot>0:
            kp="red"

    cnt = 0
    tot = 0

    if sanActive==0 or sanTot==0:
        san="red"
    elif sanActive and sanTot:
        if sanTot/sanActive>=0.9:
            san="green"
        elif sanTot/sanActive<0.9 and sanTot/sanActive>=0.5:
            san="yellow"
        elif sanTot/sanActive<0.5:
            san="red"

    if glance=="green":
        cnt += 1
        tot = tot+2
    elif glance=="yellow":
        cnt += 1
        tot = tot+1
    elif glance=="red":
        cnt += 1

    if cinder=="green":
        cnt += 1
        tot=tot+2
    elif cinder=="yellow":
        cnt += 1
        tot=tot+1
    elif cinder=="red":
        cnt += 1

    if quantum=="green":
        cnt += 1
        tot=tot+2
    elif quantum=="yellow":
        cnt += 1
        tot=tot+1
    elif quantum=="red":
        cnt += 1

    if nova=="green":
        cnt += 1
        tot=tot+2
    elif nova=="yellow":
        cnt += 1
        tot=tot+1
    elif nova=="red":
        cnt += 1

    if idm=="green":
        cnt += 1
        tot=tot+2
    elif idm=="yellow":
        cnt += 1
        tot=tot+1
    elif idm=="red":
        cnt += 1

    if kp=="green":
        cnt += 1
        tot=tot+2
    elif kp=="yellow":
        cnt += 1
        tot=tot+1
    elif kp=="red":
        cnt += 1

    if cnt == 0:
        serv = "undefined"
    else:
        if tot/(cnt*2)>=0.99:
            serv="green"
        elif (tot/(cnt*2)>=0.5 and tot/(cnt*2)<0.99):
            serv="yellow"
        elif (tot/(cnt*2)>=0 and tot/(cnt*2)<0.5):
            serv="red"

    kp="green"
    tmp_measures=[{"timestamp" : "2013-12-20 12.00",
                    "novaServiceStatus"   : {"value": nova,   "description": "desc"},
                    "neutronServiceStatus": {"value": quantum,"description": "desc"},
                    "cinderServiceStatus" : {"value": cinder, "description": "desc"},
                    "glanceServiceStatus" : {"value": glance, "description": "desc"},
                    "KPServiceStatus"     : {"value": kp,     "description": "desc"},
                    "OverallStatus"       : {"value": serv,   "description": "desc"},
                    "FiHealthStatus"      : {"value": san,    "description": "desc"} }]
    tmp_res["measures"]= tmp_measures
    return tmp_res

@app.route('/monitoring/regions/<regionid>/hosts', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/', method='GET')
def get_all_hosts(regionid="ID of the region"):
    return {regionid}

@app.route('/monitoring/regions/<regionid>/hosts/<hostid>', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/', method='GET')
def get_host(regionid="ID of the region", hostid="ID of the host"):
    since = request.query.getone('since')
    if request.query.getone('since') is not None:
        print request.query.getone('since')
    return {regionid, hostid}

@app.route('/monitoring/regions/<regionid>/vms', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/', method='GET')
def get_all_vms(regionid="ID of the region"):
    return {}

@app.route('/monitoring/regions/<regionid>/vms/<vmid>', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/', method='GET')
def get_vm(regionid="ID of the region", vmid="ID of the vm"):
    since = request.query.getone('since')
    return {}

@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/', method='GET')
def get_all_services_by_host(regionid="ID of the region", hostid="ID of the host"):
    return {}

@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>', method='GET')
@app.route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>/', method='GET')
def get_service_by_host(regionid="ID of the region", hostid="ID of the host", serviceName="Service name"):
    since = request.query.getone('since')
    return {}

@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/', method='GET')
def get_all_services_by_vm(regionid="ID of the region", vmid="ID of the vm"):
    return {}

@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>', method='GET')
@app.route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>/', method='GET')
def get_service_by_vm(regionid="ID of the region", vmid="ID of the vm", serviceName="Service name"):
    since = request.query.getone('since')
    return {}

@app.route('/monitoring/regions/<regionid>/nes', method='GET')
@app.route('/monitoring/regions/<regionid>/nes/', method='GET')
def get_all_nes(regionid="ID of the region"):
    return {}

@app.route('/monitoring/regions/<regionid>/nes/<neid>', method='GET')
@app.route('/monitoring/regions/<regionid>/nes/<neid>/', method='GET')
def get_ne(regionid="ID of the region", neid="ID of the network"):
    since = request.query.getone('since')
    return {}

@app.route('/monitoring/host2hosts', method='GET')
@app.route('/monitoring/host2hosts/', method='GET')
def get_host2hosts():
    return {}

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
    try:
        mongo_config = {}
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

#Load variables declared in config file in [idm] section and load it to Bottle app.
#These variables can be getted from route function using app.config.get('variable')
def load_idm_section(config):
    try:
        app.config["token_url"] = ConfigSectionMap('idm', config)['token_url']
        app.config["service_url"] = ConfigSectionMap('idm', config)['service_url']
        app.config["idm_username"] = ConfigSectionMap('idm', config)['username']
        app.config["idm_password"] = ConfigSectionMap('idm', config)['password']
    except Exception as e:
        print("Error in IDM config: {}").format(e)
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
    plugin = MongoPlugin(**load_mongo_section(Config))
    load_idm_section(Config) 

    app.install(plugin)

    #App runs in infinite loop
    run(app, host=listen_url, port=listen_port, debug=True)

if __name__ == '__main__':
    main()