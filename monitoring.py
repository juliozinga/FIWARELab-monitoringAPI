#!/usr/bin/env python

from bottle import route, run, request, error, response, Bottle
from pymongo import MongoClient, database
from bottle.ext.mongo import MongoPlugin
from bson.json_util import dumps
import argparse
import ConfigParser
import sys

app = Bottle()
COLLECTION = 'entities'

@error(404)
def error404(error):
    response.content_type = 'application/json'
    return {'Request not found'}

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
    totalUsers = 0;
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
    tmp_res={"_links": {"self": { "href": "" }},"measures":[{}]}
    particular_region = ["Berlin", "Stockholm2", "SaoPaulo", "Mexico"]

    since = None
    if request.query.getone('since') is not None:
        since = request.query.getone('since')

    #import pdb; pdb.set_trace()
    result = mongodb['entities'].find({"_id.type":"region"})
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
                    total_vms = total_vms + 1

    tmp_res["_embedded"]["region"].append(tmp_reg)
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

def arg_parser():
    parser = argparse.ArgumentParser(description='Monitoring python version')
    parser.add_argument("-c", "--config-file", help="Config file", required=False)
    return parser.parse_args()

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

def main():
    args = arg_parser()
    if args.config_file is not None:
        config_file = args.config_file
    else:
        config_file = "config.ini"

    try:
        Config = ConfigParser.ConfigParser()
        Config.read(config_file)
    except Exception as e:
        print("Problem with config file: {}").format(e)
        sys.exit(-1)

    try:
        listen_url = ConfigSectionMap('api', Config)['listen_url']
        listen_port = ConfigSectionMap('api', Config)['listen_port']
    except Exception as e:
        print("Error in loading api section: {}").format(e)
        sys.exit(-1)

    try:
        mongo_config = {}
        if ConfigSectionMap('mongodb', Config)['url']:
            mongo_config['uri'] = "mongodb://" + ConfigSectionMap('mongodb', Config)['url']
        if ConfigSectionMap('mongodb', Config)['dbname']:
            mongo_config['db'] = ConfigSectionMap('mongodb', Config)['dbname']
        mongo_config["json_mongo"] = True
        plugin = MongoPlugin(**mongo_config)
    except Exception as e:
        print("Error in mongodb: {}").format(e)
        sys.exit(-1)

    #dumps(mongodb['entities'].find({"_id.type":"vm", "_id.id":{'$regex':'Trento'}}))
    app.install(plugin)
    run(app, host=listen_url, port=listen_port, debug=True)

if __name__ == '__main__':
    main()