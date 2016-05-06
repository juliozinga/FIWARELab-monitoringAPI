from ConfigParser import ConfigParser
from Collector import Collector
import argparse
import os

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

    collector = Collector(user, password, monasca_endpoint, keystone_endpoint)
    print collector.get_metrics('Spain2')

    # Load and start data import to database

    # Generate day, month aggregation on database

# Argument management
def arg_parser():
    parser = argparse.ArgumentParser(description='Monitoring proxy')
    parser.add_argument("-c", "--config-file", help="Config file", required=False)
    return parser.parse_args()


if __name__ == '__main__':
    main()
