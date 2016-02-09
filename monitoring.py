#!/usr/bin/env python

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

    result = mongodb['entities'].find({"_id.type":"region"})
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
def get_region(regionid="ID of the region"):
    if request.query.getone('since') is not None:
        print request.query.getone('since')
    return {regionid}

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

@app.route('/monitoring/regions/<regionid>/services', method='GET')
@app.route('/monitoring/regions/<regionid>/services/', method='GET')
def get_all_services_by_region(regionid="ID of the region"):
    since = request.query.getone('since')
    aggregate = request.query.getone('aggregate')
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