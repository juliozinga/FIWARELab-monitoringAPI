from monascaclient import client
from monascaclient import ksclient
import monascaclient.exc as exc
import datetime
import utils
import os
import fcntl
from distutils.util import strtobool
import traceback
import time
import errno
import sys

#------------
from random import randint
#------------
class Mutex:
    
    def __init__(self, filename):
        self.filename = filename        
    
    def mutexExists(self):
        print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] check if mutex exists")
        if os.path.exists(self.filename):
            return True
        return False
    
    def isObsolete(self):
        sys.stderr.write(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] is obsolete?")
        if self.mutexExists():
            sys.stderr.write(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] is obsolete?Checking...")
            mutexTime = datetime.datetime.fromtimestamp(os.path.getmtime(self.filename))
            nowTime = datetime.datetime.now()
            difference = int((nowTime - mutexTime).total_seconds())
            if difference > 10:
                sys.stderr.write(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] MUTEX IS OBSOLETE")
                return True
        sys.stderr.write(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] MUTEX IS NOT OBSOLETE")
        return False
    
    def createMutex(self):
        #------------
        #MICROSECOND_DIVIDER = 1000000.0
        #SECONDS = randint(0, int(MICROSECOND_DIVIDER))
        #time.sleep(SECONDS/MICROSECOND_DIVIDER)
        #------------
        #sys.stderr.write(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] createMutex entered")
        if self.isObsolete():
            self.removeMutex()
        
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            file_handle = os.open(self.filename, flags)
            #sys.stderr.write(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] createMutex try ended")
        except OSError as e:
            #sys.stderr.write(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] createMutex ERROR")
            if e.errno == errno.EEXIST:  # Failed as the file already exists.
                #sys.stderr.write(e)
                pass
            else:
                sys.stderr.write(e)
                #sys.stderr.write(traceback.format_exc())
                self.removeMutex()
            return False
        except Exception as exc:
            #sys.stderr.write(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] createMutex strange exception")
            sys.stderr.write(e)
            #sys.stderr.write(traceback.format_exc())
            self.removeMutex()
            return False
        else:  # No exception, so the file must have been created successfully.
            #sys.stderr.write(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] createMutex")
            with os.fdopen(file_handle, 'w') as file_obj:
                file_obj.write("")
                file_obj.flush()
                file_obj.close()
                #sys.stderr.write(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"]try createMutex!!!")
            return True
            #except Exception as ex:
                ##sys.stderr.write(ex)
                #if self.mutexExists():
                    #return True
                #else:
                    #return False

    def removeMutex(self):
        #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] removeMutex")
        if self.mutexExists():
            os.remove(self.filename)
        
class Lock:
    
    def __init__(self, filename):
        self.filename = filename        
    
    def lockfileExists(self):
        #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] check if lockfile exists")
        if os.path.exists(self.filename):
            if os.path.isfile(self.filename):
                return True
        return False
    
    def openLockfile(self, mode):
        #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] openLockfile :: mode " + str(mode))
        self.handle = open(self.filename, mode)
    
    # Bitwise OR fcntl.LOCK_NB if you need a non-blocking lock 
    def acquire(self):
        #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] acquire Lockfile")
        fcntl.flock(self.handle, fcntl.LOCK_EX)
        
    def release(self):
        #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] release Lockfile")
        try:
            fcntl.flock(self.handle, fcntl.LOCK_UN)
        except Exception:
            return
        
    def write(self, token):
        #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] write Lockfile")
        #self.handle.truncate(0)
        self.handle.write(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+'\n'+token+'\n')
        self.handle.flush()
        self.handle.close()
    
    #read first 2 lines
    def read(self):
        #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] read Lockfile")
        myParams = []

        i=0
        for line in self.handle:
            if i<2:
                line = line.rstrip("\n")
                myParams.append(line)
                i+=1
            else:
                break

        #print(myParams)
        return myParams
     
    def closeLockfile(self):
        #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] closeLockfile")
        try:
            self.handle.close()
        except Exception:
            return
        
    def __del__(self):
        try:
            self.handle.close()
        except Exception:
            return

class MonascaFunction:
    LIST = 0
    LIST_MEASUREMENTS = 1
    LIST_STATISTICS = 2
    LIST_NAMES = 3
    LIST_DIMENSION_NAMES = 4
    LIST_DIMENSION_VALUES = 5
    
class CollectorMonasca:
    
    def __init__(self, user, password, monasca_endpoint, keystone_endpoint, config=None):
        
        self.__api_version = '2_0'
        self.__username = user
        self.__password = password
        self.__monasca_endpoint = monasca_endpoint
        self.__keystone_endpoint = keystone_endpoint
        self.__config = config
        self.__token = None
        
        self.__authenticate_monasca_client(1)
    
    def __authenticate_monasca_client(self, force = 0):        
        
        mutexfile = ""
        lockfile = ""
        if self.__config:
            mutexfile = self.__config['projectpath']['path']+"/mutex.tmp"
            lockfile = self.__config['projectpath']['path']+"/lock_token.tmp"
        else:
            mutexfile = "/tmp/mutex.tmp"
            lockfile = "/tmp/lock_token.tmp"
        mutex = Mutex(mutexfile)
        lock = Lock(lockfile)
        
        #It is used to check if a process can only read or also write inside tokenfile
        onlyReadMode = True
        
        #if we don't force the authentication (we force only first time)
        if not force:
            #if there is mutex, some process is already writing. But it could be dead                            
            if not mutex.mutexExists() or mutex.isObsolete():  
                #if the mutex has been created
                if mutex.createMutex():
                    onlyReadMode = False
   
                    if  lock.lockfileExists():
                        try:
                            #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Read token file")
                            lock.openLockfile('r')
                        except IOError:
                            mutex.removeMutex()
                            raise Exception("The token file could not be read and mutex was set")
                        parameters = lock.read()
                        lock.closeLockfile()
                        #if file is not empty
                        if parameters and len(parameters) == 2:
                            timestamp = utils.from_monasca_ts_to_datetime_ms(parameters[0])
                            difference = int((datetime.datetime.now()-timestamp).total_seconds())
                            #if token was got less than 300 sec(5 mins) ago
                            authenticate_retry_wait_secs = 300
                            if self.__config:
                                authenticate_retry_wait_secs = int(self.__config['keystone']['authenticate_retry_wait_secs'])
                                
                            if difference < authenticate_retry_wait_secs:
                                #check if token is equal to the one stored inside the locked file. If not, take the stored one
                                if parameters[1] != self.__token:
                                    #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] USE TOKEN IN FILE:"+parameters[1])
                                    #if the stored token is different from the one I have
                                    self.__token = parameters[1]
                                    # Instantiate a monascaclient object to use for query
                                    self.__monasca_client = client.Client(self.__api_version, self.__monasca_endpoint, token=self.__token)
                                    mutex.removeMutex()
                                    #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] USE TOKEN IN FILE:return")
                                    return
                                else:
                                    mutex.removeMutex()
                                    raise Exception("We need to wait "+authenticate_retry_wait_secs+" secs before reauthenticating to Keystone. The token in file is no more valid")
                            
                        else:
                            if self.__config and strtobool(self.__config["api"]["debugMode"]):
                                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] The lock file is empty")
                    else:
                        if self.__config and strtobool(self.__config["api"]["debugMode"]):
                            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] The token file doesn't exists and mutex was set")
                else:
                    if self.__config and strtobool(self.__config["api"]["debugMode"]):
                        print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] the fork tried to create mutex, but it was already set")
            
            #the mutex was set so the process can only read
            if mutex.mutexExists() and onlyReadMode:
                #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] --------ONLY READ MODE-------")
                #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] __authenticate_monasca_client::mutex.mutexExists")
                if  lock.lockfileExists():
                    #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] __authenticate_monasca_client::lock.lockfileExists")
                    try:
                        lock.openLockfile('r')
                    except IOError:
                        raise Exception("The token file could not be read and mutex was set by another process")
                    parameters = lock.read()
                    lock.closeLockfile()
                    #if file is not empty
                    if parameters and len(parameters) == 2:
                        #check if token is equal to the one stored inside the locked file. If not, take the stored one
                        if parameters[1] != self.__token:
                            #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] USE TOKEN IN FILE:"+parameters[1])
                            #if the stored token is different from the one I have
                            self.__token = parameters[1]
                            # Instantiate a monascaclient object to use for query
                            self.__monasca_client = client.Client(self.__api_version, self.__monasca_endpoint, token=self.__token)
                            #return
                            return
                        else:
                            raise Exception(str(os.getpid())+"] Keystone token in token file is no more valid. Mutex is set by another process.")
                    else:
                        raise Exception(str(os.getpid())+"] The token file is empty and mutex was set")
                else:
                    raise Exception(str(os.getpid())+"] The token file doesn't exists and mutex was set")
                
        #This part is executed when we need to generate a new token        
        if force or not onlyReadMode:
            try:
                # Authenticate to Keystone
                ks = ksclient.KSClient(auth_url=self.__keystone_endpoint, username=self.__username, password=self.__password)

                #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] autenticated to ks")

                self.__token = ks.token
                
                # Instantiate a monascaclient object to use for query
                self.__monasca_client = client.Client(self.__api_version, self.__monasca_endpoint, token=self.__token)
            
                lock.openLockfile('w')
                #Try to lock file. If already locked then exception
                lock.acquire()  
                
                if self.__config and strtobool(self.__config["api"]["debugMode"]):
                    print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Collector is writing inside locked file")
                    
                lock.write(ks.token) 
            except OSError as e:
                if self.__config and strtobool(self.__config["api"]["debugMode"]):
                    print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] OSError File already locked by another fork")
                lock.closeLockfile()
                lock.release()
                mutex.removeMutex()
                raise e
            except IOError as e:
                if self.__config and strtobool(self.__config["api"]["debugMode"]):
                    print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] IOError File already locked by another fork")
                lock.closeLockfile()
                lock.release()
                mutex.removeMutex()
                raise e
            except Exception as e:
                if self.__config and strtobool(self.__config["api"]["debugMode"]):
                    print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] Problem in Authenticating to Keystone")
                    print(traceback.format_exc())
                lock.closeLockfile()
                lock.release()
                mutex.removeMutex()
                raise e
            finally:                
                lock.closeLockfile()
                lock.release()                
                mutex.removeMutex()  
            
    #def set_token_from_token_file(self):
        #print(str(os.getpid())+"]["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"]")
        
    def update_token(self):
        if self.__config:
            tokenfile = self.__config['projectpath']['path']+"/lock_token.tmp"
        else:
            tokenfile = "/tmp/lock_token.tmp"
        
        lock = Lock(tokenfile)
        if  lock.lockfileExists():
            try:
                lock.openLockfile('r')
            except IOError:
                if self.__config and strtobool(self.__config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] CollectorMonasca.set_token_from_token_file: the token file could not be opened and read")
                return
            
            parameters = lock.read()
            lock.closeLockfile()
            #if file is not empty
            if parameters and len(parameters) == 2:
                timestamp = utils.from_monasca_ts_to_datetime_ms(parameters[0])
                difference = int((datetime.datetime.now()-timestamp).total_seconds())
                #if token was got less than 3600 sec(1 hour) ago
                token_ttl = 3600
                if self.__config:
                    token_ttl = int(self.__config['keystone']['token_ttl'])
                    
                if difference < token_ttl:
                    #check if token is equal to the one stored inside the locked file. If not, take the stored one
                    if parameters[1] != self.__token:
                        #if the stored token is different from the one I have
                        self.__token = parameters[1]
                        # Instantiate a monascaclient object to use for query
                        self.__monasca_client = client.Client(self.__api_version, self.__monasca_endpoint, token=self.__token)
                        
                        if self.__config and strtobool(self.__config["api"]["debugMode"]):
                            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] CollectorMonasca.set_token_from_token_file: the parent Collector is taking and storing the token from file")
                    else:
                        if self.__config and strtobool(self.__config["api"]["debugMode"]):
                            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] CollectorMonasca.set_token_from_token_file: the parent Collector has already an updated token")
                #we need to reauthenticate to keystone
                else:
                    if self.__config and strtobool(self.__config["api"]["debugMode"]):
                            print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] CollectorMonasca.set_token_from_token_file: the parent Collector is going to reauthenticate because the token file was older than "+str(token_ttl)+" seconds")
                    self.__authenticate_monasca_client(1)
            else:
                if self.__config and strtobool(self.__config["api"]["debugMode"]):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] CollectorMonasca.set_token_from_token_file: the token file is empty")
        else:
            if self.__config and strtobool(self.__config["api"]["debugMode"]):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] CollectorMonasca.set_token_from_token_file: the token file doesn't exists")
    
    def get_metrics(self, regionid):
        params = {}
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        return self.__perform_monasca_query(self.__monasca_client.metrics.list, params, MonascaFunction.LIST, 1)

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
        metrics = self.__perform_monasca_query(self.__monasca_client.metrics.list, params, MonascaFunction.LIST, 1)
        resources = set()
        if metrics:
            for metric in metrics:
                resources.add(metric['dimensions']['resource_id'])
        return resources
    
    def get_measurements_for_metric(self, metricName, start_timestamp, regionid = None):
        params = {}
        if regionid:
            dimensions = {'region' : regionid}
            params['dimensions'] = dimensions
        params['name'] = metricName
        params['start_time'] = start_timestamp
        params['group_by'] = "*"
        measurements = self.__perform_monasca_query(self.__monasca_client.metrics.list_measurements, params, MonascaFunction.LIST_MEASUREMENTS, 1)
        return measurements
    
    def get_measurements_resources_for_metric(self, regionid, metricName, start_timestamp):
        params = {}
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        params['name'] = metricName
        params['start_time'] = start_timestamp
        params['group_by'] = "*"
        measurements = self.__perform_monasca_query(self.__monasca_client.metrics.list_measurements, params, MonascaFunction.LIST_MEASUREMENTS, 1)
        resources = set()
        if measurements:
            for measurement in measurements:
                resources.add(measurement['dimensions']['resource_id'])
        return resources
    
    def get_measurements_for_hostname(self, regionid, metricName, hostname, start_timestamp):
        params = {}
        dimensions = {'region' : regionid, 'resource_id' : hostname}
        params['dimensions'] = dimensions
        params['name'] = metricName
        params['start_time'] = start_timestamp
        params['group_by'] = "*"
        measurements = self.__perform_monasca_query(self.__monasca_client.metrics.list_measurements, params, MonascaFunction.LIST_MEASUREMENTS, 1)
        return measurements

    def get_pool_ip_for_region(self, start_timestamp, regionid = None):
        return self.get_measurements_for_metric("region.pool_ip", start_timestamp, regionid)

    def get_allocated_ip_for_region(self, start_timestamp, regionid = None):
        return self.get_measurements_for_metric("region.allocated_ip", start_timestamp, regionid)

    def get_used_ip_for_region(self, start_timestamp, regionid = None):
        return self.get_measurements_for_metric("region.used_ip", start_timestamp, regionid)

#------------------------------------------------------------------

    def get_processes(self, regionid):
        params = {}
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        params['name'] = 'process.pid_count'
        return self.__perform_monasca_query(self.__monasca_client.metrics.list, params, MonascaFunction.LIST, 1)

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
        return self.__perform_monasca_query(self.__monasca_client.metrics.list, params, MonascaFunction.LIST, 1)

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
        return self.__perform_monasca_query(self.__monasca_client.metrics.list, params, MonascaFunction.LIST, 1)

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

                if not (statistics and measurements):
                    return None

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

        if not (statistics and measurements):
            return None

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
        return self.__perform_monasca_query(self.__monasca_client.metrics.list_statistics, params, MonascaFunction.LIST_STATISTICS, 1)

    def get_sanities_measurements(self, regionid, start_timestamp, end_timestamp=None):
        params = {}
        params['name'] = 'region.sanity_status'
        params['start_time'] = datetime.datetime.fromtimestamp(start_timestamp).isoformat()
        if end_timestamp:
            params['end_time'] = datetime.datetime.fromtimestamp(end_timestamp).isoformat()
        dimensions = {'region' : regionid}
        params['dimensions'] = dimensions
        return self.__perform_monasca_query(self.__monasca_client.metrics.list_measurements, params, MonascaFunction.LIST_MEASUREMENTS, 1)

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

    def __perform_monasca_query(self, f, params, f_type = None, loop = 0):
        resp = None
        try:
            resp = f(**params)
        except exc.HTTPException as he:
            # TODO Change with logger message
            if self.__config and strtobool(self.__config["api"]["debugMode"]):
                print('HTTPException code=%s message=%s' % (he.code, he.message))
        except exc.KeystoneException as ke:
            if self.__config and strtobool(self.__config["api"]["debugMode"]):
                print('KeystoneException code=%s message=%s' % (ke.code, ke.message))
                print('Reauthenticating')            
            #-----------------------------------
            # retry query still for loop times
            #-----------------------------------
            if loop > 0 and f_type != None:
                #reauthenticate 
                self.__authenticate_monasca_client()
                if(f_type == MonascaFunction.LIST):
                    resp = self.__perform_monasca_query(self.__monasca_client.metrics.list, params, f_type, loop-1)
                elif(f_type == MonascaFunction.LIST_MEASUREMENTS):
                    resp = self.__perform_monasca_query(self.__monasca_client.metrics.list_measurements, params, f_type, loop-1)
                elif(f_type == MonascaFunction.LIST_STATISTICS):
                    resp = self.__perform_monasca_query(self.__monasca_client.metrics.list_statistics, params, f_type, loop-1)
                elif(f_type == MonascaFunction.LIST_NAMES):
                    resp = self.__perform_monasca_query(self.__monasca_client.metrics.list_names, params, f_type, loop-1)
                elif(f_type == MonascaFunction.LIST_DIMENSION_NAMES):
                    resp = self.__perform_monasca_query(self.__monasca_client.metrics.list_dimension_names, params, f_type, loop-1)
                elif(f_type == MonascaFunction.LIST_DIMENSION_VALUES):
                    resp = self.__perform_monasca_query(self.__monasca_client.metrics.list_dimension_values, params, f_type, loop-1)
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

