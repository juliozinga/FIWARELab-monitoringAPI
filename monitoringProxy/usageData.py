from pymongo import MongoClient, database
from model import usagedata_resources
import utils
import copy

'''

'''

def get_toptenants(mongodb, app_config):
    now = utils.get_timestamp()
    # TODO: Add 3600 seconds as default in the case no value is retrieved by vmTTL from conf file
    ts_limit = now - int(app_config["api"]["vmTTL"])
    vms = mongodb[app_config["mongodb"]["collectionname"]].find({"$and":[{"_id.type":"vm"},{"modDate":{"$gt":ts_limit}}]})
    usagedata_resources.toptenants_resource["_embedded"]["tenants"].append(copy.deepcopy(usagedata_resources.tenant_resource))
    return usagedata_resources.toptenants_resource

