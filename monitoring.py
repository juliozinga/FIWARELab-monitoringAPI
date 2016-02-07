#!/usr/bin/env python

from bottle import route, run, request, error, response
import argparse
import ConfigParser
import sys

@error(404)
def error404(error):
    response.content_type = 'application/json'
    return {'Request not found'}

@route('/')
def root():
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

@route('/monitoring/regions/<regionid>', method='GET')
@route('/monitoring/regions/<regionid>/', method='GET')
def get_region(regionid="ID of the region"):
    if request.query.getone('since') is not None:
        print request.query.getone('since')
    return {regionid}

@route('/monitoring/regions/<regionid>/hosts', method='GET')
@route('/monitoring/regions/<regionid>/hosts/', method='GET')
def get_all_hosts(regionid="ID of the region"):
    return {regionid}

@route('/monitoring/regions/<regionid>/hosts/<hostid>', method='GET')
@route('/monitoring/regions/<regionid>/hosts/<hostid>/', method='GET')
def get_host(regionid="ID of the region", hostid="ID of the host"):
    since = request.query.getone('since')
    if request.query.getone('since') is not None:
        print request.query.getone('since')
    return {regionid, hostid}

@route('/monitoring/regions/<regionid>/vms', method='GET')
@route('/monitoring/regions/<regionid>/vms/', method='GET')
def get_all_vms(regionid="ID of the region"):
    return {}

@route('/monitoring/regions/<regionid>/vms/<vmid>', method='GET')
@route('/monitoring/regions/<regionid>/vms/<vmid>/', method='GET')
def get_vm(regionid="ID of the region", vmid="ID of the vm"):
    since = request.query.getone('since')
    return {}

@route('/monitoring/regions/<regionid>/hosts/<hostid>/services', method='GET')
@route('/monitoring/regions/<regionid>/hosts/<hostid>/services/', method='GET')
def get_all_services_by_host(regionid="ID of the region", hostid="ID of the host"):
    return {}

@route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>', method='GET')
@route('/monitoring/regions/<regionid>/hosts/<hostid>/services/<serviceName>/', method='GET')
def get_service_by_host(regionid="ID of the region", hostid="ID of the host", serviceName="Service name"):
    since = request.query.getone('since')
    return {}

@route('/monitoring/regions/<regionid>/vms/<vmid>/services', method='GET')
@route('/monitoring/regions/<regionid>/vms/<vmid>/services/', method='GET')
def get_all_services_by_vm(regionid="ID of the region", vmid="ID of the vm"):
    return {}

@route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>', method='GET')
@route('/monitoring/regions/<regionid>/vms/<vmid>/services/<serviceName>/', method='GET')
def get_service_by_vm(regionid="ID of the region", vmid="ID of the vm", serviceName="Service name"):
    since = request.query.getone('since')
    return {}

@route('/monitoring/regions/<regionid>/services', method='GET')
@route('/monitoring/regions/<regionid>/services/', method='GET')
def get_all_services_by_region(regionid="ID of the region"):
    since = request.query.getone('since')
    aggregate = request.query.getone('aggregate')
    return {}

@route('/monitoring/regions/<regionid>/nes', method='GET')
@route('/monitoring/regions/<regionid>/nes/', method='GET')
def get_all_nes(regionid="ID of the region"):
    return {}

@route('/monitoring/regions/<regionid>/nes/<neid>', method='GET')
@route('/monitoring/regions/<regionid>/nes/<neid>/', method='GET')
def get_ne(regionid="ID of the region", neid="ID of the network"):
    since = request.query.getone('since')
    return {}

@route('/monitoring/host2hosts', method='GET')
@route('/monitoring/host2hosts/', method='GET')
def get_host2hosts():
    return {}

# /monitoring/host2hosts/source;dest?since=since
# /monitoring/host2hosts/source/dest?since=since

@route('/monitoring/regions', method='GET')
@route('/monitoring/regions/', method='GET')
def get_all_regions():
    output = {
      "_links": {
        "self": {
          "href": "/monitoring/regions"
        }
      },
      "_embedded": {
        "regions": [
          {
            "_links": {
              "self": {
                "href": "/monitoring/regions/Trento"
              }
            },
            "id": "Trento"
          }
        ]
      },
      "basicUsers": 12,
      "trialUsers": 12,
      "communityUsers": 12,
      "totalUsers": 12,
      "total_nb_users": 12,
      "totalCloudOrganizations": 12,
      "totalUserOrganizations": 12,
      "total_nb_organizations": 12,
      "total_nb_cores": 12,
      "total_nb_cores_enabled": 12,
      "total_nb_ram": 12,
      "total_nb_disk": 12,
      "total_nb_vm": 12,
      "total_ip_assigned": 12,
      "total_ip_allocated": 12,
      "total_ip": 12
    }
    return output


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

    run(host=listen_url, port=listen_port, debug=True)

if __name__ == '__main__':
    main()