from monascaclient import client
from monascaclient import ksclient
import monascaclient.exc as exc

class Collector:

    __monasca_client = None

    def __init__(self, user, password, monasca_endpoint, keystone_endpoint):
        # Instantiate a monascaclient object to use for query
        api_version = '2_0'

        # Authenticate to Keystone
        ks = ksclient.KSClient(auth_url=keystone_endpoint, username=user, password=password)

        # construct the mon client
        self.__monasca_client = client.Client(api_version, monasca_endpoint, token=ks.token)

    def get_metrics(self, regionid):
        fields = {}
        dimensions = {'region' : regionid}
        fields['dimensions'] = dimensions
        try:
            resp = self.__monasca_client.metrics.list(**fields)
        except exc.HTTPException as he:
            print('HTTPException code=%s message=%s' % (he.code, he.message))
        else:
            print(resp)
            print('Successfully run')
        return resp