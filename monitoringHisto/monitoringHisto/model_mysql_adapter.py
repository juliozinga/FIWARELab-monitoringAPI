from model_mysql import *
from model import ProcessMeasurement
import utils

'''
Collection of functions to map internal monitoring model (model.py) to Mysql model (model_mysql.py)
'''


def from_process_measurement_to_mysql_host_service(process):  # type: ProcessMeasurement
    host_service_list = []
    uptime_avg = dict()
    hosts = set()

    for measurement in process.aggregation.measurements:
        ts = utils.from_monasca_ts_to_datetime_se(measurement.timestamp)
        hosts.add(measurement.hostname)
        if uptime_avg.has_key(ts):
            uptime_avg.update({ts: uptime_avg.get(ts) + (0 if measurement.value < 1 else 1)})
        else:
            uptime_avg.update({ts: (0 if measurement.value < 1 else 1)})

    for timestamp, avg in uptime_avg.iteritems():
        host_service = HostService()
        host_service.entityId = process.region + "-" + process.name
        host_service.region = process.region
        host_service.entityType = "host_service"
        host_service.serviceType = process.name
        host_service.aggregationType = process.aggregation.code
        host_service.timestampId = timestamp
        host_service.avg_Uptime = float(avg) / len(hosts)
        host_service_list.append(host_service)

    return host_service_list


def from_sanity_check_to_mysql_host_service(sanity_check):
    SANITY = "sanity"
    host_service = HostService()
    host_service.entityId = sanity_check.region + "-" + SANITY
    host_service.region = sanity_check.region
    host_service.entityType = "host_service"
    host_service.serviceType = SANITY
    host_service.aggregationType = sanity_check.aggregation.code
    host_service.timestampId = \
        utils.from_monasca_ts_to_datetime_se(sanity_check.aggregation.measurements[0].timestamp)
    # Set avg_Uptime value to max 1 --> 100%
    host_service.avg_Uptime = sanity_check.aggregation.measurements[0].value
    # return host_service
    return host_service


def from_sanity_check_to_mysql_host_service_list(sanity_check):
    host_service_list = []
    for measurement in sanity_check.aggregation.measurements:
        SANITY = "sanity"
        host_service = HostService()
        host_service.entityId = sanity_check.region + "-" + SANITY
        host_service.region = sanity_check.region
        host_service.entityType = "host_service"
        host_service.serviceType = SANITY
        host_service.aggregationType = sanity_check.aggregation.code
        host_service.timestampId = utils.from_monasca_ts_to_datetime_se(measurement.timestamp)
        # Set avg_Uptime value to max 1 --> 100%
        host_service.avg_Uptime = measurement.value
        host_service_list.append(host_service)
    # return host_service list
    return host_service_list