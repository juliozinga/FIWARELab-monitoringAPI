from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
from influxdb.exceptions import InfluxDBServerError
import datetime
from distutils.util import strtobool
import urllib2
import traceback

class CollectorInflux:
    
    def __init__(self, user, password, dbname, influx_host, influx_port, debugMode):
        
        self.__username = user
        self.__password = password
        self.__dbname = dbname
        self.__influx_host = influx_host
        self.__influx_port = influx_port
        self.__debugMode = debugMode
        #self.__keystone_endpoint = keystone_endpoint
        #self.__token = None
        
        self.__influx_client = InfluxDBClient(self.__influx_host, self.__influx_port, self.__username, self.__password, self.__dbname)
        
    def __perform_influx_query(self, query):
        return self.__influx_client.query(query)
    
    def get_all_region_vms(self, regionid, start_timestamp, active=True):     
    
        try:
            response = self.__perform_influx_query("SELECT last(value_meta) FROM instance WHERE value_meta =~ /active/ AND time>='"+start_timestamp+"' AND region='"+regionid+"' GROUP BY resource_id")
            
            try:
                response_list = list(response.items())
                return response_list
            except Exception as e:
                if strtobool(self.__debugMode):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_region_vms response.items() exception")
                    print(traceback.format_exc())  
                return None

        except InfluxDBClientError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_region_vms __perform_influx_query InfluxDBClientError")
                print(traceback.format_exc())
            return None
        
        except InfluxDBServerError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_region_vms __perform_influx_query InfluxDBServerError")
            return None
         
        except urllib2.HTTPError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_region_vms __perform_influx_query httperror")
            return None
            
        except urllib2.URLError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_region_vms __perform_influx_query urlerror")
            return None
            
        except Exception as e:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_all_region_vms __perform_influx_query exception")
                print(traceback.format_exc())  
            return None
        
    def get_region_vm(self, regionid, vmid, start_timestamp):     
    
        try:
            response = self.__perform_influx_query("SELECT last(value_meta) FROM instance WHERE time>='"+start_timestamp+"' AND region='"+regionid+"' AND resource_id='"+vmid+"';SELECT last(value) as value,unit FROM \"disk.usage\" WHERE time>='"+start_timestamp+"' AND region='"+regionid+"' AND resource_id='"+vmid+"';SELECT last(value) as value,unit FROM \"disk.capacity\" WHERE time>='"+start_timestamp+"' AND region='"+regionid+"' AND resource_id='"+vmid+"';SELECT last(value) as value,unit FROM \"memory_util\" WHERE time>='"+start_timestamp+"' AND region='"+regionid+"' AND resource_id='"+vmid+"';SELECT last(value) as value,unit FROM \"cpu_util\" WHERE time>='"+start_timestamp+"' AND region='"+regionid+"' AND resource_id='"+vmid+"'")
            
            try:
                #response_list = list(response.items())
                #print(list(response.get_points(measurement='disk.usage')))
                #return None
                return response
            except Exception as e:
                if strtobool(self.__debugMode):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_vm response.items() exception")
                    print(traceback.format_exc())  
                return None

        except InfluxDBClientError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_vm __perform_influx_query InfluxDBClientError")
                print(traceback.format_exc())
            return None
        
        except InfluxDBServerError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_vm __perform_influx_query InfluxDBServerError")
            return None
         
        except urllib2.HTTPError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_vm __perform_influx_query httperror")
            return None
            
        except urllib2.URLError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_vm __perform_influx_query urlerror")
            return None
            
        except Exception as e:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_vm __perform_influx_query exception")
                print(traceback.format_exc())  
            return None
        
    def get_number_of_active_vms_for_region(self, regionid, start_timestamp):
        try:
            response = self.__perform_influx_query("SELECT last(count) FROM n_vms_for_region WHERE time>='"+start_timestamp+"' AND region= '"+ regionid +"'")
            
            try:
                response_list = list(response.get_points())

                if response_list and len(response_list) and response_list[0].has_key("last"): 
                    return int(response_list[0]["last"])
                return 0
            except Exception as e:
                if strtobool(self.__debugMode):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms_for_region response.get_points() exception")
                    print(traceback.format_exc())  
                return 0

        except InfluxDBClientError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms_for_region __perform_influx_query InfluxDBClientError")
                print(traceback.format_exc())
            return 0
        
        except InfluxDBServerError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms_for_region __perform_influx_query InfluxDBServerError")
            return 0
         
        except urllib2.HTTPError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms_for_region __perform_influx_query httperror")
            return 0
            
        except urllib2.URLError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms_for_region __perform_influx_query urlerror")
            return 0
            
        except Exception as e:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms_for_region __perform_influx_query exception")
                print(traceback.format_exc())  
            return 0
        
    def get_number_of_active_vms(self, start_timestamp):
        try:
            response = self.__perform_influx_query("SELECT last(count) FROM n_vms_for_region WHERE time>='"+start_timestamp+"' GROUP BY region")
            
            try:
                tot = 0
                if response:
                    response_list = list(response.get_points())

                    if response_list and len(response_list): 
                        for region_vms in response_list:
                            if region_vms.has_key("last"):
                                tot += int(region_vms["last"])

                return tot
            except Exception as e:
                if strtobool(self.__debugMode):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms response.items() exception")
                    print(traceback.format_exc())  
                return 0

        except InfluxDBClientError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms __perform_influx_query InfluxDBClientError")
                print(traceback.format_exc())
            return 0
        
        except InfluxDBServerError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms __perform_influx_query InfluxDBServerError")
            return 0
         
        except urllib2.HTTPError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms __perform_influx_query httperror")
            return 0
            
        except urllib2.URLError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms __perform_influx_query urlerror")
            return 0
            
        except Exception as e:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_number_of_active_vms __perform_influx_query exception")
                print(traceback.format_exc())  
            return 0
        
    def get_region_host(self, regionid, hostid, start_timestamp):     
    
        try:
            response = self.__perform_influx_query("SELECT last(value) as value FROM /compute.node./ WHERE time>='"+start_timestamp+"' AND region='"+regionid+"' AND resource_id='"+hostid+"'")
            
            try:
                #response_list = list(response.items())
                #print(list(response.get_points(measurement='disk.usage')))
                #return None
                return response
            except Exception as e:
                if strtobool(self.__debugMode):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_host response.items() exception")
                    print(traceback.format_exc())  
                return None

        except InfluxDBClientError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_host __perform_influx_query InfluxDBClientError")
                print(traceback.format_exc())
            return None
        
        except InfluxDBServerError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_host __perform_influx_query InfluxDBServerError")
            return None
         
        except urllib2.HTTPError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_host __perform_influx_query httperror")
            return None
            
        except urllib2.URLError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_host __perform_influx_query urlerror")
            return None
            
        except Exception as e:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_host __perform_influx_query exception")
                print(traceback.format_exc())  
            return None
        
    def get_region_hosts_data(self, regionid, start_timestamp):     
    
        try:
            response = self.__perform_influx_query("SELECT last(value) as value FROM /compute.node./ WHERE time>='"+start_timestamp+"' AND region='"+regionid+"' GROUP BY resource_id")
            
            try:
                #response_list = list(response.items())
                #print(list(response.get_points(measurement='disk.usage')))
                #return None
                return response
            except Exception as e:
                if strtobool(self.__debugMode):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_hosts_data response.items() exception")
                    print(traceback.format_exc())  
                return None

        except InfluxDBClientError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_hosts_data __perform_influx_query InfluxDBClientError")
                print(traceback.format_exc())
            return None
        
        except InfluxDBServerError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_hosts_data __perform_influx_query InfluxDBServerError")
            return None
         
        except urllib2.HTTPError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_hosts_data __perform_influx_query httperror")
            return None
            
        except urllib2.URLError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_hosts_data __perform_influx_query urlerror")
            return None
            
        except Exception as e:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_region_hosts_data __perform_influx_query exception")
                print(traceback.format_exc())  
            return None
        
    def get_hosts_data(self, start_timestamp):     
    
        try:
            response = self.__perform_influx_query("SELECT last(value) as value FROM /compute.node./ WHERE time>='"+start_timestamp+"' GROUP BY region,resource_id")
            
            try:
                #response_list = list(response.items())
                #print(list(response.get_points(measurement='disk.usage')))
                #return None
                return response
            except Exception as e:
                if strtobool(self.__debugMode):
                    print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_hosts_data response.items() exception")
                    print(traceback.format_exc())  
                return None

        except InfluxDBClientError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_hosts_data __perform_influx_query InfluxDBClientError")
                print(traceback.format_exc())
            return None
        
        except InfluxDBServerError, error: 
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_hosts_data __perform_influx_query InfluxDBServerError")
            return None
         
        except urllib2.HTTPError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_hosts_data __perform_influx_query httperror")
            return None
            
        except urllib2.URLError, error:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_hosts_data __perform_influx_query urlerror")
            return None
            
        except Exception as e:
            if strtobool(self.__debugMode):
                print("["+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")+"] get_hosts_data __perform_influx_query exception")
                print(traceback.format_exc())  
            return None
