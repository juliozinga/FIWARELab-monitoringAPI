import time
from datetime import timedelta, tzinfo

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


class UTC(tzinfo):
    """
    Class Representing a UTC tzinfo
    """
    ZERO = timedelta(0)

    def utcoffset(self, dt):
        return self.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.ZERO