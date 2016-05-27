
class Aggregation:
    code = None
    period = None
    type = None

    def __init__(self, code, period, type):
        self.code = code
        self.period = period
        self.type = type


class Process:
    name = None
    service_name = None
    region = None
    aggregation = None

    def __init__(self, name=None, service_name=None, region=None, aggregation=None):
        self.name = name
        self.service_name = service_name
        self.region = region
        self.aggregation = aggregation


class ProcessAggregation:
    type = None
    code = None
    timestamp_last = None
    measurements = []

    def __init__(self, type=None, code=None, timestamp_end=None, measurements=None):
        self.type = type
        self.code = code
        self.measurements = []


class ProcessMeasurement:
    timestamp = None
    value = None
    hostname = None

    def __init__(self, timestamp=None, value=None, hostname=None):
        self.timestamp = timestamp
        self.value = value
        self.hostname = hostname


class SanityCheck:
    name = None
    region = None
    aggregation = None

    def __init__(self, name=None, region=None, aggregation=None):
        self.name = name
        self.region = region
        self.aggregation = aggregation


class SanityAggregation(Aggregation):
    timestamp_last = None
    measurements = []

    def __init__(self, type=None, code=None, timestamp_end=None, measurements=None):
        self.type = type
        self.code = code
        if not measurements:
            self.measurements = []
        else:
            self.measurements.append(measurements)

    def get_timestamp_end(self):
        return self.timestamp_last + self.period


class SanityMeasurement:
    timestamp = None
    value = None

    def __init__(self, timestamp=None, value=None):
        self.timestamp = timestamp
        self.value = value
