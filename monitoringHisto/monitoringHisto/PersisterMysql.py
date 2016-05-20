import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm.session import make_transient
from model import Process
from model import SanityCheck
from model import Aggregation
from model import SanityAggregation
from model import SanityMeasurement
from model_mysql import *
from copy import deepcopy, copy
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
        # engine.echo = True

        # Reflect the tables
        Base.prepare(engine, reflect=True)

        # Create the session
        self.__mysql_session = Session(engine)

    def persist_process(self, process):  # type: Process
        for measurement in process.aggregation.measurements:
            host_service = model_mysql_adapter.from_process_measurement_to_mysql_host_service(process, measurement)
            self.__mysql_session.add(host_service)
        self.__mysql_session.commit()

    def persist_sanity(self, sanity_check):  # type: SanityCheck
        if sanity_check.aggregation.code is 'd':
            # Convert sanity measurements to host_service list
            host_service_list = model_mysql_adapter.from_sanity_check_to_mysql_host_service_list(sanity_check)
            for host_service in host_service_list:
                # Spread daily sanity on the 24 hours and persist
                start_hour = host_service.timestampId
                host_service_day = []
                for _ in range(24):
                    my_host_service = deepcopy(host_service)
                    my_host_service.timestampId = start_hour + datetime.timedelta(hours=_)
                    my_host_service.aggregationType = 'h'
                    host_service_day.append(my_host_service)
                self.__mysql_session.add_all(host_service_day)
                self.__mysql_session.commit()
        else:
            # TODO: Move to ERR logger
            print "ERR: Persit of " + sanity_check.__class__.__name__ + " with aggregation different from daily (d) " \
                                                                        "not implemented. nothing imported"

    def persist_sanity_daily_avg(self, start, end):
        # Retrieve daily sanity check average for each region
        hs_list_daily_avg_res = self._get_host_service_list_daily_average(start, end, 'sanity', 'h')

        hs_list_daily_avg = []
        for hs_daily_avg_res in hs_list_daily_avg_res:
            # Detach object from the session otherwise in import will be duplicated
            make_transient(hs_daily_avg_res.HostService)
            hs = deepcopy(hs_daily_avg_res.HostService)  # type: HostService
            hs.aggregationType = 'd'
            hs.timestampId = hs.timestampId.replace(hour=0, minute=0, second=0)
            hs.avg_Uptime = hs_daily_avg_res.dailyUptime
            hs_list_daily_avg.append(hs)
        self.__mysql_session.add_all(hs_list_daily_avg)
        self.__mysql_session.commit()

    def persist_process_daily_avg(self, start, end, service_name):
        # Retrieve daily sanity check average for each region
        hs_list_daily_avg_res = self._get_host_service_list_daily_average(start, end, 'sanity', 'h')

        hs_list_daily_avg = []
        for hs_daily_avg_res in hs_list_daily_avg_res:
            # Detach object from the session otherwise in import will be duplicated
            make_transient(hs_daily_avg_res.HostService)
            hs = deepcopy(hs_daily_avg_res.HostService)  # type: HostService
            hs.aggregationType = 'd'
            hs.timestampId = hs.timestampId.replace(hour=0, minute=0, second=0)
            hs.avg_Uptime = hs_daily_avg_res.dailyUptime
            hs_list_daily_avg.append(hs)
        self.__mysql_session.add_all(hs_list_daily_avg)
        self.__mysql_session.commit()

    def _get_per_region_host_service_list(self, start, end, service_type, aggregation_type):
        return self.__mysql_session.query(HostService) \
            .group_by(HostService.entityId) \
            .group_by(func.date(HostService.timestampId))\
            .filter(HostService.serviceType == service_type) \
            .filter(HostService.aggregationType == aggregation_type) \
            .filter(HostService.timestampId >= start, HostService.timestampId <= end) \
            .all()

    def _get_per_host_service_average_uptime(self, start, end, host_service):
        r = self.__mysql_session.query(
            func.avg(HostService.avg_Uptime).label('dailyUptime')) \
            .filter(HostService.region == host_service.region) \
            .filter(HostService.serviceType == host_service.serviceType) \
            .filter(HostService.timestampId >= start, HostService.timestampId < end)
        return r.value(r.label('dailyUptime'))

    def _get_host_service_list_daily_average(self, start, end, service_type, aggregation_type):
        return self.__mysql_session.query(HostService, func.avg(HostService.avg_Uptime).label('dailyUptime')) \
            .group_by(HostService.entityId) \
            .group_by(func.date(HostService.timestampId)) \
            .filter(HostService.serviceType == service_type) \
            .filter(HostService.aggregationType == aggregation_type) \
            .filter(HostService.timestampId >= start, HostService.timestampId <= end) \
            .all()
