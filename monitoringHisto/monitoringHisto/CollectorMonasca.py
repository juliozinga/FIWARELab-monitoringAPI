from monascaclient import client
from monascaclient import ksclient
from sets import Set
import monascaclient.exc as exc
import datetime


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
        names = Set()
        for metric in metrics:
            names.add(metric['name'])
        return names

    def get_processes(self, regionid):
        params = {}
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        params['name'] = 'process.pid_count'
        return self.__perform_monasca_query(self.__monasca_client.metrics.list, params)

    def get_processes_names(self, regionid):
        processes = self.get_processes(regionid)
        names = Set()
        for process in processes:
            names.add(process['dimensions']['process_name'])
        return names

    def get_services_names(self, regionid):
        processes = self.get_processes(regionid)
        names = Set()
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
        names = Set()
        for process in processes:
            names.add(process['dimensions']['process_name'])
        return names

    def get_services_processes_avg(self, regionid, avg_period, start_timestamp, end_timestamp=None):
        services_names = self.get_services_names(regionid)
        avg_services = {}
        for service_name in services_names:
            avg_services[service_name] = self.get_service_processes_avg(regionid, avg_period,
                                                                        service_name, start_timestamp, end_timestamp)
        return avg_services

    def get_service_processes_avg(self, regionid, avg_period, service_name, start_timestamp, end_timestamp=None):
        processes_names = self.get_service_processes_names(regionid, service_name)
        avg_processes = {}
        for process_name in processes_names:
            # Retrieve averaged metrics for each service based on avg_period
            params = {}
            params['name'] = 'process.pid_count'
            params['start_time'] = datetime.datetime.fromtimestamp(start_timestamp).isoformat()
            if end_timestamp:
                params['end_time'] = datetime.datetime.fromtimestamp(end_timestamp).isoformat()
            params['statistics'] = 'avg'
            params['period'] = avg_period
            dimensions = {'region' : regionid, 'service' : service_name, 'process_name' : process_name}
            params['dimensions'] = dimensions
            proc = self.__perform_monasca_query(self.__monasca_client.metrics.list_statistics, params)
            avg_processes[process_name] = proc
        return avg_processes

    def __perform_monasca_query(self, f, params):
        resp = None
        try:
            resp = f(**params)
        except exc.HTTPException as he:
            # TODO Change with logger message
            print('HTTPException code=%s message=%s' % (he.code, he.message))
        return resp
