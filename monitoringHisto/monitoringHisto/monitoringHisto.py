from ConfigParser import ConfigParser
from CollectorMonasca import CollectorMonasca
from PersisterMysql import PersisterMysql
import model_adapter
import model
import time
import argparse
import os
import utils

# Main function
import sys


def main():
    # Loads and manages the input arguments
    args = arg_parser()
    if args.config_file is not None:
        config_file = args.config_file
    else:
        config_file = "config.ini"

    # Read config file
    if not os.path.isfile(config_file):
        print("Configuration file not found: {}").format(config_file)
        sys.exit(-1)
    try:
        config = ConfigParser()
        config.optionxform = str
        config.read(config_file)
    except Exception as e:
        print("Problem parsing config file: {}").format(e)
        sys.exit(-1)

    # Load and start data collection from Monasca
    CONF_M_SECTION = 'monasca'
    keystone_endpoint = config.get('keystone','uri')
    monasca_endpoint = config.get('monasca','uri')
    user = config.get('profile','user')
    password = config.get('profile','password')

    collector = CollectorMonasca(user, password, monasca_endpoint, keystone_endpoint)
    # print collector.get_metrics('Spain2')
    # print collector.get_metrics_names('Spain2')
    # print "Services list: \n" + repr(collector.get_processes_names('Spain2'))
    # print "Regionid wrong: \n" + repr(collector.get_services_names('Spain2'))

    agg = model.Aggregation('h', 3600, 'avg')
    # services_proceses = collector.get_services_processes_avg('Spain2', (int(time.time()) - 36000), agg.period)
    end_timestamp = utils.get_timestamp(utils.get_today_midnight_datetime())
    start_timestamp = utils.get_timestamp(utils.get_yesterday_midnight_datetime())
    services_proceses = collector.get_services_processes_avg('Spain2', agg.period, start_timestamp, end_timestamp)
    if services_proceses:
        persister = PersisterMysql(config._sections.get('mysql'))
    for service in services_proceses:
        for process_name in services_proceses[service].keys():
            process_values = services_proceses[service][process_name][0]
            process_data = model_adapter.from_monasca_process_to_process(process_values, agg)
            # pass process_data to DB Adapter for importing
            persister.persist_process(process_data)



    # keys = result.keys()
    # print keys
    # print "Averaged processes for Spain2: \n" + repr( result )
    # Load and start data import to database

    # Generate day, month aggregation on database

# Argument management
def arg_parser():
    parser = argparse.ArgumentParser(description='Monitoring proxy')
    parser.add_argument("-c", "--config-file", help="Config file", required=False)
    return parser.parse_args()


if __name__ == '__main__':
    main()
