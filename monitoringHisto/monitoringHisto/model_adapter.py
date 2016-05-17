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
    p.name = process_data['dimensions']['process_name']
    p.service_name = process_data['dimensions']['service']
    p.region = process_data['dimensions']['region']

    try:
        timestamp_idx = process_data['columns'].index('timestamp')
        aggregation_idx = process_data['columns'].index(aggregation.type)
        pa = ProcessAggregation()
        pa.timestamp_last = process_data['id']
        pa.type = aggregation.type
        pa.code = aggregation.code
        p.aggregation = pa

        for measurement in process_data['statistics']:
            pm = ProcessMeasurement()
            pm.timestamp = measurement[timestamp_idx]
            pm.value = measurement[aggregation_idx]
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