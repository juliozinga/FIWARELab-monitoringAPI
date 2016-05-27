from model import ProcessAggregation
from model import ProcessMeasurement
from model import Process
from model import SanityCheck
from model import SanityAggregation
from model import SanityMeasurement

'''
Collection of functions to map external entities to internal monitoring model (model.py)
'''

def from_monasca_process_to_process(process_data, aggregation):

    p = Process()
    first_host = process_data.values()[0][0]
    p.name = first_host.get('dimensions').get('process_name')
    p.service_name = first_host.get('dimensions').get('service')
    p.region = first_host.get('dimensions').get('region')

    try:
        timestamp_idx = first_host['columns'].index('timestamp')
        aggregation_idx = first_host['columns'].index(aggregation.type)
        pa = ProcessAggregation()
        pa.timestamp_last = first_host['id']
        pa.type = aggregation.type
        pa.code = aggregation.code
        p.aggregation = pa

        for host in process_data.itervalues():
            for measurement in host[0].get('statistics'):
                pm = ProcessMeasurement()
                pm.timestamp = measurement[timestamp_idx]
                pm.value = measurement[aggregation_idx]
                pm.hostname = host[0].get('dimensions').get('hostname')
                pa.measurements.append(pm)

    except Exception as e:
        # TODO: Print to log file
        print 'Wrong columns in aggregated data mapping on entity ' + s.__class__.__name__ + ': ' + str(p), e

    return p

def from_monasca_sanity_to_sanity(sanity_data, aggregation):

    s = SanityCheck()
    s.name = sanity_data['name']
    s.region = sanity_data['dimensions']['region']

    try:
        timestamp_idx = sanity_data['columns'].index('timestamp')
        aggregation_idx = sanity_data['columns'].index(aggregation.type)
        sa = SanityAggregation()
        sa.timestamp_last = sanity_data['id']
        sa.type = aggregation.type
        sa.code = aggregation.code
        s.aggregation = sa

        for measurement in sanity_data['statistics']:
            sm = SanityMeasurement()
            sm.timestamp = measurement[timestamp_idx]
            sm.value = measurement[aggregation_idx]
            sa.measurements.append(sm)

    except Exception as e:
        # TODO: Print to log file
        print 'Wrong columns in aggregated data mapping on entity ' + s.__class__.__name__ + ': ' + str(s), e

    return s