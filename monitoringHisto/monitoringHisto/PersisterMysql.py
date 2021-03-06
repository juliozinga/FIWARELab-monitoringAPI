import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm.session import make_transient
from model import Process
from model import SanityCheck
from model_mysql import *
from copy import deepcopy, copy
import model_mysql_adapter
import utils


class PersisterMysql:

    __mysql_session = None
    start = None
    end = None
    querylimit = None

    def __init__(self, config, start, end):

        db_conf = config._sections.get('mysql')
        dbuser = db_conf.get('dbuser')
        dbpass = db_conf.get('dbpass')
        dbhost = db_conf.get('dbhost')
        dbport = db_conf.get('dbport')
        dbname = db_conf.get('dbname')
        self.querylimit = int(db_conf.get('querylimit'))

        engine = create_engine("mysql://" + dbuser + ":" + dbpass + "@" + dbhost + ":" + str(dbport) + "/" + dbname)
        # engine.echo = True

        # Reflect the tables
        Base = automap_base()
        Base.prepare(engine, reflect=True)

        # Create the session
        self.__mysql_session = Session(engine)

        self.start = start
        self.end = end

    def persist_process(self, processes):  # type: Process

        # Retrieve host_service list in DB to check duplication
        hs_db_list = self._get_host_service_list_hourly(self.start, self.end)
        hs_db_set = set(hs_db_list)

        # Build collection of (not duplicated) measurements to persist
        host_services = []
        for process in processes:
            host_service_list = model_mysql_adapter.from_process_measurement_to_mysql_host_service(process)
            # Exclude duplicates
            for host_service in host_service_list:
                if host_service not in hs_db_set:
                    host_services.append(host_service)

        # Persist measurements
        self._smart_persist(host_services)

    def persist_sanity(self, sanities):  # type: SanityCheck

        # Retrieve host_service list in DB to check duplication
        hs_db_list = self._get_host_service_list_hourly(self.start, self.end)
        hs_db_set = set(hs_db_list)

        for sanity_check in sanities:
            if sanity_check.aggregation.code is 'd':
                # Convert sanity measurements to host_service list
                host_service_list = model_mysql_adapter.from_sanity_check_to_mysql_host_service_list(sanity_check)
                # Build collection of (not duplicated) measurements to persist
                host_service_day = []
                for host_service in host_service_list:
                    # Spread daily sanity on the 24 hours and persist
                    start_hour = host_service.timestampId
                    for _ in range(24):
                        my_host_service = deepcopy(host_service)
                        my_host_service.timestampId = start_hour + datetime.timedelta(hours=_)
                        my_host_service.aggregationType = 'h'
                        if my_host_service not in hs_db_set:
                            host_service_day.append(my_host_service)
                # Persist measurements
                self.__mysql_session.add_all(host_service_day)
                self._session_commit()
            else:
                # TODO: Move to ERR logger
                print "ERR: Persit of " + sanity_check.__class__.__name__ + " with aggregation different from daily (d) " \
                                                                        "not implemented. nothing imported"

    def persist_host_service_daily_avg(self, start, end):
        # Retrieve daily host_service average for each region
        hs_list_daily_avg_hours = self._get_host_service_list_daily_average_from_hours(start, end)
        hs_list_daily_avg = self._get_host_service_list_daily(start, end)
        hs_list_daily_avg_set = set(hs_list_daily_avg)

        hs_list_daily_avg = []
        for hs_daily_avg_res in hs_list_daily_avg_hours:
            # Detach object from the session otherwise in import will be duplicated
            make_transient(hs_daily_avg_res.HostService)
            hs = deepcopy(hs_daily_avg_res.HostService)  # type: HostService
            hs.aggregationType = 'd'
            hs.timestampId = hs.timestampId.replace(hour=0, minute=0, second=0)
            hs.avg_Uptime = hs_daily_avg_res.dailyUptime
            if hs not in hs_list_daily_avg_set:
                hs_list_daily_avg.append(hs)
        self.__mysql_session.add_all(hs_list_daily_avg)
        self._session_commit()

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

    def _get_host_service_list_daily_average_from_hours(self, start, end):
        return self.__mysql_session.query(HostService, func.avg(HostService.avg_Uptime).label('dailyUptime')) \
            .group_by(HostService.entityId) \
            .group_by(func.date(HostService.timestampId)) \
            .filter(HostService.aggregationType == 'h') \
            .filter(HostService.timestampId >= start, HostService.timestampId <= end) \
            .all()

    def _get_host_service_list_daily(self, start, end):
        return self.__mysql_session.query(HostService) \
            .filter(HostService.aggregationType == 'd') \
            .filter(HostService.timestampId >= start, HostService.timestampId <= end) \
            .all()

    def _get_host_service_list_hourly(self, start, end):
        return self.__mysql_session.query(HostService) \
            .filter(HostService.aggregationType == 'h') \
            .filter(HostService.timestampId >= start, HostService.timestampId <= end) \
            .all()

    def _smart_persist(self, entities):
        chunks = [entities[x:x+self.querylimit] for x in xrange(0, len(entities), self.querylimit)]
        for chunk in chunks:
            self.__mysql_session.add_all(chunk)
            self._session_commit()

    def _session_commit(self):
        try:
            self.__mysql_session.commit()
        except Exception as e:
            # TODO: Print from logger
            print "Mysql ERR: " + str(e)
            self.__mysql_session.rollback()

    def persist_host_service_monthly_avg(self, start, end):
        # Retrieve monthly host_service average for each region
        hs_list_monthly_avg_days = self._get_host_service_list_monthly_average_from_days(start, end)
        hs_list_monthly_avg = self._get_host_service_list_monthly(start, end)
        hs_list_monthly_avg_set = set(hs_list_monthly_avg)

        hs_list_monthly_avg = []
        for hs_monthly_avg_res in hs_list_monthly_avg_days:
            # Detach object from the session otherwise in import will be duplicated
            make_transient(hs_monthly_avg_res.HostService)
            hs = deepcopy(hs_monthly_avg_res.HostService)  # type: HostService
            hs.aggregationType = 'm'
            hs.timestampId = utils.get_last_day_datetime(hs.timestampId)
            hs.avg_Uptime = hs_monthly_avg_res.monthlyUptime
            if hs not in hs_list_monthly_avg_set:
                hs_list_monthly_avg.append(hs)
        self.__mysql_session.add_all(hs_list_monthly_avg)
        self._session_commit()

    def _get_host_service_list_monthly_average_from_days(self, start, end):
        return self.__mysql_session.query(HostService, func.avg(HostService.avg_Uptime).label('monthlyUptime')) \
            .group_by(HostService.entityId) \
            .group_by(func.month(HostService.timestampId)) \
            .filter(HostService.aggregationType == 'd') \
            .filter(HostService.timestampId >= start, HostService.timestampId <= end) \
            .all()

    def _get_host_service_list_monthly(self, start, end):
        return self.__mysql_session.query(HostService) \
            .filter(HostService.aggregationType == 'm') \
            .filter(HostService.timestampId >= start, HostService.timestampId <= end) \
            .all()
