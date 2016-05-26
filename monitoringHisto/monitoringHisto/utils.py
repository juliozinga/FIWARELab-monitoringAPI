from datetime import datetime, date, time, timedelta


def get_today_midnight_datetime():
    return datetime.combine(date.today(), time.min)


def get_yesterday_midnight_datetime():
    midnight = datetime.combine(date.today(), time.min)
    return midnight - timedelta(days=1)


def get_timestamp(origin_datetime=None):
    '''
    Return UNIX timestamp from datetime object
    :param origin_datetime: Origin date to convert to timestamp
    :type origin_datetime: datetime
    :return: The corresponding UNIX timestamp for date passed as parameter or current timestamp if no parameter
    :rtype: int
    '''
    if not origin_datetime:
        return int(time.time())
    else:
        timestamp = origin_datetime.strftime("%s")
        return int(timestamp)


def get_datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
    return datetime(year, month, day, hour, minute, second, microsecond, tzinfo)


def get_datetime_from_args(day):
    return datetime.strptime(day, "%Y-%m-%d")


def get_regions(main_config):
    regions = []
    conf_regions = dict(main_config._sections['regionNew'])
    for region_id, is_new in conf_regions.iteritems():
        if str2bool(is_new):
            regions.append(region_id)
    return regions


# Function to convert a string to boolean value.
# Used for load_regionNew
def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def from_monasca_ts_to_datetime_ms(m_timestamp):
    return datetime.strptime(m_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

def from_monasca_ts_to_datetime_se(m_timestamp):
    return datetime.strptime(m_timestamp, "%Y-%m-%dT%H:%M:%SZ")