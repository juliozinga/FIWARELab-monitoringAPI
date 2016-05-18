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

    # Setup monasca collector
    CONF_M_SECTION = 'monasca'
    keystone_endpoint = config.get('keystone','uri')
    monasca_endpoint = config.get('monasca','uri')
    user = config.get('profile','user')
    password = config.get('profile','password')
    collector = CollectorMonasca(user, password, monasca_endpoint, keystone_endpoint)

    # Setup mysql persister
    persister = PersisterMysql(config._sections.get('mysql'))

    # Setup default temporal period in which to work
    # TODO: Set these values from arguments if presents
    end = utils.get_today_midnight_datetime()
    start = utils.get_yesterday_midnight_datetime()
    end_timestamp = utils.get_timestamp(end)
    start_timestamp = utils.get_timestamp(start)

    regions = ['Spain2']
    for region in regions:

        # Retrieve sanity checks aggregation
        day_agg = model.Aggregation('d', 86400, 'avg')
        sanities_data = collector.get_sanities_avg(region,day_agg.period, start_timestamp, end_timestamp)
        # Adapt and persist sanity checks aggregation
        for sanity_data in sanities_data:
            sanity = model_adapter.from_monasca_sanity_to_sanity(sanity_data, day_agg)
            persister.persist_sanity(sanity)
        # Write daily averaged aggregation for sanity checks
        persister.persist_sanity_daily_avg(start, end)
        # Write daily averaged aggregation for sanity checks
        # persister.persiste_sanity_montly_avg(start_timestamp, end_timestamp)

        # Retrieve processes aggregation
        hour_agg = model.Aggregation('h', 3600, 'avg')
        services_processes = collector.get_services_processes_avg(region, hour_agg.period, start_timestamp, end_timestamp)
        # Adapt and persist processes aggregation
        for service in services_processes:
            for process_name in services_processes[service].keys():
                process_values = services_processes[service][process_name][0]
                process = model_adapter.from_monasca_process_to_process(process_values, hour_agg)
                persister.persist_process(process)

    # Generate day, month hour_aggregation on database

# Argument management
def arg_parser():
    parser = argparse.ArgumentParser(description='Monitoring proxy')
    parser.add_argument("-c", "--config-file", help="Config file", required=False)
    return parser.parse_args()


if __name__ == '__main__':
    main()
