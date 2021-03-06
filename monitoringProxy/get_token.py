#!/usr/bin/env python

from proxy_monitoring import get_token_auth
import sys
import base64

URL = "https://account.lab.fiware.org/oauth2/token"

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print "This script get token from IDM."
        print "Usage:"
        print sys.argv[0] + " <username> <password> <consumer_key> <consumer_secret>"
        sys.exit(-1)
    try:
        token = get_token_auth(username=sys.argv[1], password=sys.argv[2], url=URL, consumer_key=sys.argv[3], consumer_secret=sys.argv[4], convert_to_64=False)
        token64 = base64.b64encode(token)
        print "\nYour token id is: (base32){} (base64){}\n".format(token, token64)
        print "Use it in this way:"
        print "curl -H \"Authorization:Bearer {}\" -s <monitoring_ip>:<monitoring_port>/monitoring/regions".format(token64)
        print "or :"
        print "curl -H \"X-Auth-Token: {}\" -s <monitoring_ip>:<monitoring_port>/monitoring/regions".format(token)
    except Exception as e:
        print "Impossible to get token: " + str(e)
