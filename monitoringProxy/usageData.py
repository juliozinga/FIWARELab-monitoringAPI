from pymongo import MongoClient, database
from model import usagedata_resources
from distutils.util import strtobool
import utils
import copy


'''
Retrieve usage data of top tenants as a resoruce defined in the model
'''


def get_toptenants(mongodb, app_config):
    # Share globally few configurations
    global obfuscate_tid
    obfuscate_tid =  strtobool(app_config["usageData"]["obfuscate_tenant_id"])
    global tenants_num
    tenants_num =  int(app_config["usageData"]["tenants_num"])

    now = utils.get_timestamp()
    ts_limit = now - int(app_config["api"]["vmTTL"])
    if strtobool(app_config["api"]["vmCheckActive"]):
        vms = mongodb[app_config["mongodb"]["collectionname"]]\
            .find({"$and":[{"_id.type":"vm"},{"attrs.status.value":"active"},{"modDate":{"$gt":ts_limit}}]})
    else:
        vms = mongodb[app_config["mongodb"]["collectionname"]]\
            .find({"$and":[{"_id.type":"vm"},{"modDate":{"$gt":ts_limit}}]})
    tenants = tenants_from_vms(vms)
    usagedata_resources.toptenants_resource["_embedded"]["tenants"] = tenants
    return usagedata_resources.toptenants_resource


def tenants_from_vms(vms):
    # TODO: Convert with DEBUG Logger
    # print "Number of vms analysed: " + str(vms.count())
    tenants = {}

    for vm in vms:
        if 'tenant_id' not in vm["attrs"]:
            continue
        tid = vm["attrs"]["tenant_id"]["value"]
        if tid in tenants:
            tenant = tenants.get(tid)
            tenant_update(tenant, vm)
        else:
            tenant = copy.deepcopy(usagedata_resources.tenant_resource)
            # tenant["tenantId"] = tid
            tenant_update(tenant, vm)
            tenants[tid] = tenant

    tenant_list = sort_tenants(tenants)

    return tenant_list


def tenant_update(tenant, vm):

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

'''
Sort, obfuscate, clean and convert dict structure into a list
'''


def sort_tenants(tenants):
    tmp_list = []
    for key, values in tenants.iteritems():
        # Remove temporary fields
        values.pop("tmpSumCpuPct")
        values.pop("tmpSumRamPct")
        # Obfuscate tenant_id
        if obfuscate_tid:
            values["tenantId"] = values["tenantId"][:-6] + "XXXXXX"
        # Convert to list
        tmp_list.append(values)

    # TODO: Convert with DEBUG Logger
    # print "Number of tenants retrieved: " + str(len(tmp_list))

    # Sort on vms num
    sorted_tenant_list = sorted(tmp_list, key=lambda k: k['vmsActiveNum'], reverse=True)

    # Remove lasts based on conf
    tenant_list = sorted_tenant_list[:tenants_num-1]

    # Assign a rank
    i=0
    for t in tenant_list:
        i = i + 1
        t["ranking"] = i

    return tenant_list