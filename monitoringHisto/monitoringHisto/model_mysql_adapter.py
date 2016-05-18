from model import Process
from model_mysql import *
from model import ProcessMeasurement

'''
Collection of functions to map internal monitoring model (model.py) to Mysql model (model_mysql.py)
'''


def from_process_measurement_to_mysql_host_service(process, measurement):  # type: ProcessMeasurement
        host_service = HostService()
        host_service.entityId = process.region + "-" + process.name
        host_service.region = process.region
        host_service.entityType = "host_service"
        host_service.serviceType = process.name
        host_service.aggregationType = process.aggregation.code
        host_service.timestampId = measurement.timestamp
        # Set avg_Uptime value to max 1 --> 100%
        host_service.avg_Uptime = measurement.value if measurement.value < 1 else 1
        return host_service

def from_sanity_check_to_mysql_host_service(sanity_check):
        SANITY = "sanity"
        host_service = HostService()
        host_service.entityId = sanity_check.region + "-" + SANITY
        host_service.region = sanity_check.region
        host_service.entityType = "host_service"
        host_service.serviceType = SANITY
        host_service.aggregationType = sanity_check.aggregation.code
        host_service.timestampId = sanity_check.aggregation.measurements[0].timestamp
        # Set avg_Uptime value to max 1 --> 100%
        host_service.avg_Uptime = sanity_check.aggregation.measurements[0].value
        # return host_service
        return host_service