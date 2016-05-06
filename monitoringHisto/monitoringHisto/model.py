
class Aggregation:
    code = None
    period = None
    type = None

    def __init__(self, code, period, type):
        self.code = code
        self.period = period
        self.type = type


class ProcessAggregation:
    type = None
    code = None
    timestamp_end = None
    measurements = []

    def __init__(self, type=None, code=None, timestamp_end=None, measurements=None):
        self.type = type
        self.code = code
        self.measurements = []


class ProcessMeasurement:
    timestamp = None
    value = None

    def __init__(self, timestamp=None, value=None):
        self.timestamp = timestamp
        self.value = value


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

