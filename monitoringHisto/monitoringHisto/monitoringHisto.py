from ConfigParser import ConfigParser
from CollectorMonasca import CollectorMonasca
from PersisterMysql import PersisterMysql
import model_adapter
import model
import argparse
import os
import utils

# Main function
import sys


def main():
    # Loads and manages the input arguments
    args = arg_parser()

    # Config file
    if args.config_file is not None:
        config_file = args.config_file
    else:
        config_file = "config.ini"

    if args.start_day is None or args.end_day is None:
        # Setup default temporal period in which to work
        # TODO: Print on logger we are using default dates
        start = utils.get_yesterday_midnight_datetime()
        end = utils.get_today_midnight_datetime()
    else:
        # Setup user temporal period in which to work
        # TODO: Print on logger we are using user dates
        start = utils.get_datetime_from_args(args.start_day)
        end = utils.get_datetime_from_args(args.end_day)
    start_timestamp = utils.get_timestamp(start)
    end_timestamp = utils.get_timestamp(end)

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

    # Read main config file
    mainconfig_file = config.get("mainconfig", "path")
    if not os.path.isfile(mainconfig_file):
        print("Main configuration file not found: {}").format(mainconfig_file)
        sys.exit(-1)
    try:
        main_config = ConfigParser()
        # Preserve case when reading configfile
        main_config.optionxform = str
        main_config.read(mainconfig_file)
    except Exception as e:
        print("Problem parsing main config file: {}").format(e)
        sys.exit(-1)

    # Setup monasca collector
    CONF_M_SECTION = 'monasca'
    keystone_endpoint = config.get('keystone','uri')
    monasca_endpoint = config.get('monasca','uri')
    user = config.get('profile','user')
    password = config.get('profile','password')
    collector = CollectorMonasca(user, password, monasca_endpoint, keystone_endpoint)

    # Setup mysql persister
    persister = PersisterMysql(config, start, end)

    # Get list of regions
    regions = utils.get_regions(main_config)
    for region in regions:

        # Retrieve sanity checks aggregation
        day_agg = model.Aggregation('d', 86400, 'avg')
        sanities_data = collector.get_sanities_avg(region,day_agg.period, start_timestamp, end_timestamp)
        # Adapt and persist daily average of sanity checks aggregation into hourly base
        sanities = []
        for sanity_data in sanities_data:
            sanity = model_adapter.from_monasca_sanity_to_sanity(sanity_data, day_agg)
            sanities.append(sanity)
        persister.persist_sanity(sanities)

        # Retrieve processes aggregation
        hour_agg = model.Aggregation('h', 3600, 'avg')
        services_processes = collector.get_services_processes_avg(region, hour_agg.period, start_timestamp, end_timestamp)

        # Calculate and map processes aggregation
        processes = []
        for service in services_processes:
            for process_name in services_processes[service].keys():
                process_values = services_processes[service][process_name]
                process = model_adapter.from_monasca_process_to_process(process_values, hour_agg)
                processes.append(process)

        # Adapt and persist processes aggregation
        persister.persist_process(processes)

    # Calculate and persist host_service daily aggregation
    persister.persist_host_service_daily_avg(start, end)

    # Calculate and persist host_service daily aggregation
    if start.month != end.month:
        s_month, e_month = utils.get_range_for_daily_agg(start, end)
        persister.persist_host_service_monthly_avg(s_month, e_month)

# Argument management
def arg_parser():
    parser = argparse.ArgumentParser(description='Monitoring proxy')
    parser.add_argument("-c", "--config-file", help="Config file", required=False)
    parser.add_argument("-s", "--start-day", help="2016-01-01", required=False)
    parser.add_argument("-e", "--end-day", help="2016-01-02", required=False)
    return parser.parse_args()


if __name__ == '__main__':
    main()
