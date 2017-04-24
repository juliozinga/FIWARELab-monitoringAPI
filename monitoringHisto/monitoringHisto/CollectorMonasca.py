from monascaclient import client
from monascaclient import ksclient
import monascaclient.exc as exc
import datetime
import utils


class CollectorMonasca:

    __monasca_client = None

    def __init__(self, user, password, monasca_endpoint, keystone_endpoint):
        # Instantiate a monascaclient object to use for query
        api_version = '2_0'

        # Authenticate to Keystone
        ks = ksclient.KSClient(auth_url=keystone_endpoint, username=user, password=password)

        # construct the mon client
        self.__monasca_client = client.Client(api_version, monasca_endpoint, token=ks.token)

    def get_metrics(self, regionid):
        params = {}
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        return self.__perform_monasca_query(self.__monasca_client.metrics.list, params)

    def get_metrics_names(self, regionid):
        metrics = self.get_metrics(regionid)
        names = set()
        for metric in metrics:
            names.add(metric['name'])
        return names
 
#------------------------------------------------------------------

    def get_resources_for_metric(self, regionid, metricName):
        params = {}
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        params['name'] = metricName
        metrics = self.__perform_monasca_query(self.__monasca_client.metrics.list, params)
        resources = set()
        if metrics:
            for metric in metrics:
                resources.add(metric['dimensions']['resource_id'])
        return resources
    
    def get_measurements_for_hostname(self, regionid, metricName, hostname, start_timestamp):
        params = {}
        dimensions = {'region' : regionid, 'resource_id' : hostname}
        params['dimensions'] = dimensions
        params['name'] = metricName
        params['start_time'] = start_timestamp
        measurements = self.__perform_monasca_query(self.__monasca_client.metrics.list_measurements, params)
        return measurements

    def get_pool_ip_for_region(self, regionid, start_timestamp):
        params = {}
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        params['name'] = "region.pool_ip"
        params['start_time'] = start_timestamp
        measurements = self.__perform_monasca_query(self.__monasca_client.metrics.list_measurements, params)
        return measurements

    def get_allocated_ip_for_region(self, regionid, start_timestamp):
        params = {}
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        params['name'] = "region.allocated_ip"
        params['start_time'] = start_timestamp
        measurements = self.__perform_monasca_query(self.__monasca_client.metrics.list_measurements, params)
        return measurements

    def get_used_ip_for_region(self, regionid, start_timestamp):
        params = {}
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        params['name'] = "region.used_ip"
        params['start_time'] = start_timestamp
        measurements = self.__perform_monasca_query(self.__monasca_client.metrics.list_measurements, params)
        return measurements

#------------------------------------------------------------------

    def get_processes(self, regionid):
        params = {}
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        params['name'] = 'process.pid_count'
        return self.__perform_monasca_query(self.__monasca_client.metrics.list, params)

    def get_processes_names(self, regionid):
        processes = self.get_processes(regionid)
        names = set()
        for process in processes:
            names.add(process['dimensions']['process_name'])
        return names

    def get_services_names(self, regionid):
        processes = self.get_processes(regionid)
        names = set()
        for process in processes:
            names.add(process['dimensions']['service'])
        return names

    def get_service_processes(self, regionid, service_name):
        params = {}
        dimensions = {'region' : regionid, 'service' : service_name}
        params['dimensions'] = dimensions
        params['name'] = 'process.pid_count'
        return self.__perform_monasca_query(self.__monasca_client.metrics.list, params)

    def get_service_processes_names(self, regionid, service_name):
        processes = self.get_service_processes(regionid, service_name)
        names = set()
        for process in processes:
            names.add(process['dimensions']['process_name'])
        return names

    def get_services_processes_avg(self, regionid, avg_period, start_timestamp, end_timestamp=None, services=[]):
        services_names = self.get_services_names(regionid)
        avg_services = {}
        for service_name in services_names:
            if services and service_name not in services:
                continue
            else:
                avg_services[service_name] = \
                    self.get_service_processes_avg(regionid, avg_period, service_name, start_timestamp, end_timestamp)
        return avg_services

    def get_process_metrics(self, regionid, process_name):
        params = {}
        dimensions = {'region' : regionid, 'process_name' : process_name}
        params['dimensions'] = dimensions
        params['name'] = 'process.pid_count'
        return self.__perform_monasca_query(self.__monasca_client.metrics.list, params)

    def get_process_hostnames_names(self, regionid, process_name):
        metrics = self.get_process_metrics(regionid, process_name)
        hostnames = set()
        for metric in metrics:
            hostnames.add(metric['dimensions']['hostname'])
        return hostnames

    def get_service_processes_avg(self, regionid, avg_period, service_name, start_timestamp, end_timestamp=None):

        processes_names = self.get_service_processes_names(regionid, service_name)
        avg_processes = {}
        # Retrieve averaged metrics for each service based on avg_period
        for process_name in processes_names:
            avg_processes[process_name] = dict()
            process_hostnames = self.get_process_hostnames_names(regionid,process_name)
            for process_hostname in process_hostnames:
                # Retrieve statistics from monasca
                statistics = self.get_process_statistics(process_name, process_hostname, service_name, regionid, avg_period, start_timestamp, end_timestamp)

                # Retrieve measurementes from monasca
                measurements = self.get_process_measurements(process_name, process_hostname, service_name, regionid, start_timestamp, end_timestamp)

                # Remove statistics for which no measurements are present in monasca and store
                m_days_set = self.from_dates_to_days_set(self.from_measurements_to_dates(measurements))
                self.clean_statistics(statistics, m_days_set)
                avg_processes[process_name][process_hostname] = statistics

        return avg_processes

    def get_sanities_avg(self, regionid, avg_period, start_timestamp, end_timestamp=None):
        # Retrieve statistics from monasca
        statistics = self.get_sanities_statistics(regionid, avg_period, start_timestamp, end_timestamp)

        # Retrieve measurementes from monasca
        measurements = self.get_sanities_measurements(regionid, start_timestamp, end_timestamp)

        # Remove statistics for which no measurements are present in monasca
        m_days_set = self.from_dates_to_days_set(self.from_measurements_to_dates(measurements))
        return self.clean_statistics(statistics, m_days_set)

    def get_sanities_statistics(self, regionid, avg_period, start_timestamp, end_timestamp=None):
        # Retrieve averaged metrics for each service based on avg_period
        params = {}
        params['name'] = 'region.sanity_status'
        params['start_time'] = datetime.datetime.fromtimestamp(start_timestamp).isoformat()
        if end_timestamp:
            params['end_time'] = datetime.datetime.fromtimestamp(end_timestamp).isoformat()
        params['statistics'] = 'avg'
        params['period'] = avg_period
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        return self.__perform_monasca_query(self.__monasca_client.metrics.list_statistics, params)

    def get_sanities_measurements(self, regionid, start_timestamp, end_timestamp=None):
        params = {}
        params['name'] = 'region.sanity_status'
        params['start_time'] = datetime.datetime.fromtimestamp(start_timestamp).isoformat()
        if end_timestamp:
            params['end_time'] = datetime.datetime.fromtimestamp(end_timestamp).isoformat()
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        return self.__perform_monasca_query(self.__monasca_client.metrics.list_measurements, params)

    @staticmethod
    def clean_statistics(statistics, measurement_days_set):
        timestamp_idx = statistics[0].get( 'columns').index('timestamp')
        for s in statistics[0]['statistics'][:]:
            d = utils.from_monasca_ts_to_datetime_se(s[timestamp_idx]).replace(hour=0, minute=0)
            if d not in measurement_days_set:
                statistics[0]['statistics'].remove(s)
        return statistics

    @staticmethod
    def from_measurements_to_dates(measurements):
        timestamp_idx = measurements[0].get( 'columns').index('timestamp')
        dates = []
        for m in measurements[0]['measurements']:
            d = utils.from_monasca_ts_to_datetime_ms(m[timestamp_idx])
            dates.append(d)
        return dates

    def from_dates_to_days_set(self, dates):
        days_set = set()
        for date in dates:
            date = date.replace(hour=0, minute=0, second=0)
            days_set.add(date)
        return days_set

    def __perform_monasca_query(self, f, params):
        resp = None
        try:
            resp = f(**params)
        except exc.HTTPException as he:
            # TODO Change with logger message
            print('HTTPException code=%s message=%s' % (he.code, he.message))
        return resp

    def get_process_statistics(self, process_name, hostname, service_name, regionid, avg_period, start_timestamp, end_timestamp):
        params = {}
        params['name'] = 'process.pid_count'
        params['start_time'] = datetime.datetime.fromtimestamp(start_timestamp).isoformat()
        if end_timestamp:
            params['end_time'] = datetime.datetime.fromtimestamp(end_timestamp).isoformat()
        params['statistics'] = 'avg'
        params['period'] = avg_period
        dimensions = {'region' : regionid, 'service' : service_name, 'process_name' : process_name, 'hostname' : hostname}
        params['dimensions'] = dimensions
        return self.__perform_monasca_query(self.__monasca_client.metrics.list_statistics, params)

    def get_process_measurements(self, process_name, hostname, service_name, regionid, start_timestamp, end_timestamp):
        params = {}
        params['name'] = 'process.pid_count'
        params['start_time'] = datetime.datetime.fromtimestamp(start_timestamp).isoformat()
        if end_timestamp:
            params['end_time'] = datetime.datetime.fromtimestamp(end_timestamp).isoformat()
        dimensions = {'region' : regionid, 'service' : service_name, 'process_name' : process_name, 'hostname' : hostname}
        params['dimensions'] = dimensions
        return self.__perform_monasca_query(self.__monasca_client.metrics.list_measurements, params)

