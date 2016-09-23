from pymongo import MongoClient, database
from model import usagedata_resources
from distutils.util import strtobool
import utils
import copy
import json


'''
Retrieve usage data of top tenants as a resoruce defined in the model
'''


def get_toptenants(mongodb, app_config, sort_criteria="vmsActiveNum"):
    # Share globally few configurations
    global obfuscate_tid
    obfuscate_tid =  strtobool(app_config["usageData"]["obfuscate_tenant_id"])
    global tenants_num
    tenants_num =  int(app_config["usageData"]["tenants_num"])
    global excluded_tenants
    excluded_tenants = json.loads(app_config["usageData"]["blacklist_tenants"])

    now = utils.get_timestamp()
    ts_limit = now - int(app_config["api"]["vmTTL"])
    if strtobool(app_config["api"]["vmCheckActive"]):
        vms = mongodb[app_config["mongodb"]["collectionname"]]\
            .find({"$and":[{"_id.type":"vm"},{"attrs.status.value":"active"},{"modDate":{"$gt":ts_limit}}]})
    else:
        vms = mongodb[app_config["mongodb"]["collectionname"]]\
            .find({"$and":[{"_id.type":"vm"},{"modDate":{"$gt":ts_limit}}]})
    tenants = _tenants_from_vms(vms)
    tenant_list = _pretty_tenant_list(tenants)
    sorted_tenants = _sort_tenants(tenant_list, sort_criteria)
    usagedata_resources.toptenants_resource["_embedded"]["tenants"] = sorted_tenants
    return usagedata_resources.toptenants_resource


def _tenants_from_vms(vms):
    # TODO: Convert with DEBUG Logger
    # print "Number of vms analysed: " + str(vms.count())
    tenants = {}

    for vm in vms:
        if 'tenant_id' not in vm["attrs"]:
            continue
        tid = vm["attrs"]["tenant_id"]["value"]
        if tid in tenants:
            tenant = tenants.get(tid)
            _tenant_update(tenant, vm)
        elif tid not in excluded_tenants:
            tenant = copy.deepcopy(usagedata_resources.tenant_resource)
            # tenant["tenantId"] = tid
            _tenant_update(tenant, vm)
            tenants[tid] = tenant

    return tenants


def _tenant_update(tenant, vm):

    tenant["tenantId"] = vm["attrs"]["tenant_id"]["value"]
    tenant["vmsActiveNum"] += 1
    if 'vcpus' in vm["attrs"]:
        tenant["vcpuAllocatedTot"] += int(vm["attrs"]["vcpus"]["value"])
    if 'ramTot' in vm["attrs"]:
        tenant["ramAllocatedTot"] += int(vm["attrs"]["ramTot"]["value"])

    if 'cpuLoadPct' in vm["attrs"]:
        tenant['tmpSumCpuPct'] += float(vm["attrs"]["cpuLoadPct"]["value"])
        tenant['cpuUsedPct'] = round(tenant['tmpSumCpuPct'] / tenant["vmsActiveNum"], 4)

    if 'usedMemPct' in vm["attrs"]:
        tenant['tmpSumRamPct'] += float(vm["attrs"]["usedMemPct"]["value"])
        tenant["ramUsedPct"] = round(tenant['tmpSumRamPct'] / tenant["vmsActiveNum"], 4)

    region = _region_from_vm(vm)
    if region not in tenant['regions']:
        tenant['regions'].append(region)

'''
Sort tenants bsaed on sort criteria and keep first X, based on conf (tenants_num)
'''


def _sort_tenants(tenant_list, sort_criteria):

    # TODO: Convert with DEBUG Logger
    # print "Number of tenants retrieved: " + str(len(tmp_list))

    # Sort based on sort_criteria
    sorted_tenant_list = sorted(tenant_list, key=lambda k: k[sort_criteria], reverse=True)

    # Remove lasts based on conf
    sorted_tenant_list = sorted_tenant_list[:tenants_num-1]

    # Assign a rank
    i = 0
    for t in sorted_tenant_list:
        i += 1
        t["ranking"] = i

    return sorted_tenant_list


'''
Obfuscate, clean and convert dict structure into a list
'''


def _pretty_tenant_list(tenants_dict):
    tmp_list = []
    for key, values in tenants_dict.iteritems():
        # Remove temporary fields
        values.pop("tmpSumCpuPct")
        values.pop("tmpSumRamPct")
        # Obfuscate tenant_id
        if obfuscate_tid:
            values["tenantId"] = values["tenantId"][:-6] + "XXXXXX"
        # Convert to list
        tmp_list.append(values)
    return tmp_list


'''
Check the validity of the sorting parameter
'''


def valid_sort(sort_criteria):
    valid_sorts = {"vmsActiveNum", "ramUsedPct" , "cpuUsedPct", "ramAllocatedTot", "vcpuAllocatedTot"}
    return sort_criteria in valid_sorts;

def _region_from_vm(vm):
    vm_id = vm["_id"]["id"].split(":")
    return vm_id[0]