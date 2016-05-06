from model import ProcessAggregation
from model import ProcessMeasurement
from model import Process

'''
Collection of functions to map external entities to internal monitoring model (model.py)
'''


def from_monasca_process_to_process(host_process, aggregation):

    p = Process()
    p.name = host_process['dimensions']['process_name']
    p.service_name = host_process['dimensions']['service']
    p.region = host_process['dimensions']['region']

    try:
        timestamp_idx = host_process['columns'].index('timestamp')
        aggregation_idx = host_process['columns'].index(aggregation.type)
        pa = ProcessAggregation()
        pa.timestamp_end = host_process['id']
        pa.type = aggregation.type
        pa.code = aggregation.code
        p.aggregation = pa

        for measurement in host_process['statistics']:
            pm = ProcessMeasurement()
            pm.timestamp = measurement[timestamp_idx]
            pm.value = measurement[aggregation_idx]
            pa.measurements.append(pm)

    except Exception as e:
        # TODO: Print to log file
        print 'Wrong columns in aggregated data mapping process: ' + str(p), e

    return p
