import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from model import Process
from model import SanityCheck
from model import Aggregation
from model import SanityAggregation
from model import SanityMeasurement
from model_mysql import *
import model_mysql_adapter


class PersisterMysql:

    __mysql_session = None

    def __init__(self, db_conf):

        Base = automap_base()
        dbuser = db_conf.get('dbuser')
        dbpass = db_conf.get('dbpass')
        dbhost = db_conf.get('dbhost')
        dbport = db_conf.get('dbport')
        dbname = db_conf.get('dbname')

        engine = create_engine("mysql://" + dbuser + ":" + dbpass + "@" + dbhost + ":" + str(dbport) + "/" + dbname)

        # Reflect the tables
        Base.prepare(engine, reflect=True)

        # Create the session
        self.__mysql_session = Session(engine)

    def persist_process(self, process):  # type: Process
        for measurement in process.aggregation.measurements:
            host_service = model_mysql_adapter.from_process_measurement_to_mysql_host_service(process, measurement)
            self.__mysql_session.add(host_service)
        self.__mysql_session.commit()

    def persist_sanity(self, sanity_check): # type: SanityCheck
        if sanity_check.aggregation.code is 'd':
            # Convert aggregation to hours
            sanity_check.aggregation.code = 'h'
            sanity_check.aggregation.period = 3600
            start_hour = datetime.datetime.strptime(sanity_check.aggregation.timestamp_last, "%Y-%m-%dT%H:%M:%SZ")
            for _ in range(24):
                hour = start_hour + datetime.timedelta(hours=_)
                sanity_check.aggregation.measurements[0].timestamp = hour
                host_service = model_mysql_adapter.from_sanity_check_to_mysql_host_service(sanity_check)
                self.__mysql_session.add(host_service)
            self.__mysql_session.commit()
        else:
            # TODO: Move to ERR logger
            print "ERR: Persit of " + sanity_check.__class__.__name__ + " with aggregation different from daily (d)  not implemented. nothing imported"


    def persist_sanity_daily_avg(self, start, end):
        day = datetime.timedelta(days=1)

        # Filter sanity per region
        region_host_services = self.__mysql_session.query(HostService)\
            .group_by(HostService.region)\
            .filter(HostService.serviceType == "sanity") \
            .filter(HostService.aggregationType == "h") \
            .filter(HostService.timestampId >= start, HostService.timestampId <= end)\
            .all()

        while start < end:
            # Normalize to midnight
            datetime_agg = start.replace(hour=0)
            # Calculate daily average
            for host_service in region_host_services:
                r = self.__mysql_session.query(
                    func.avg(HostService.avg_Uptime).label('dailyUptime'))\
                    .filter(HostService.region == host_service.region) \
                    .filter(HostService.serviceType == host_service.serviceType)\
                    .filter(HostService.timestampId >= datetime_agg, HostService.timestampId < datetime_agg + day)
                daily_uptime = r.value(r.label('dailyUptime'))
                if daily_uptime:
                    # Insert daily average for this region
                    m = SanityMeasurement(timestamp=datetime_agg, value=daily_uptime)
                    sa = SanityAggregation(type='avg', code='d', measurements=m)
                    sanity_check = SanityCheck(name='sanity', region=host_service.region, aggregation=sa)
                    host_service = model_mysql_adapter.from_sanity_check_to_mysql_host_service(sanity_check)
                    self.__mysql_session.add(host_service)
                    self.__mysql_session.commit()
                else:
                    # TODO: Move to ERR logger
                    print "ERR: Persist of daily aggregation for " + SanityCheck.__class__.__name__  \
                          + ". Hourly values not present"

            # Next day in range
            start = start + day
