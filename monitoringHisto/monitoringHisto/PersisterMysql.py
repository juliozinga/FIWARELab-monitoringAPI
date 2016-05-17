import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from model import Process
from model import SanityCheck
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
            start_hour = datetime.datetime.strptime(sanity_check.aggregation.timestamp_last, "%Y-%m-%dT%H:%M:%SZ")
            for _ in range(24):
                hour = start_hour + datetime.timedelta(hours=_)
                host_service = model_mysql_adapter.from_sanity_check_to_mysql_host_service(sanity_check, hour)
                self.__mysql_session.add(host_service)
            self.__mysql_session.commit()
        else:
            # TODO: Move to ERR logger
            print "ERR: Persit of " + sanity_check.__class__.__name__ + " with aggregation different from daily (d)  not implemented. nothing imported"
