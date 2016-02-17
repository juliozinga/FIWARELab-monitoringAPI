#!/usr/bin/env python

from proxy_monitoring import get_token_auth
import sys

URL = "https://account.lab.fiware.org/oauth2/token"

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print "This script get token from IDM."
        print "Usage:"
        print sys.argv[0] + " <username> <password> <url> <consumer_key> <consumer_secret>"
        sys.exit(-1)
    try:
        token64 = get_token_auth(username=sys.argv[1], password=sys.argv[2], url=URL, consumer_key=sys.argv[3], consumer_secret=sys.argv[4])
        print "\nYour token is: {}\n".format(token64)
        print "Use it in this way:"
        print "curl -H \"Authorization:Bearer {}\" -s <monitoring_ip>:<monitoring_port>/monitoring/regions".format(token64)
    except Exception as e:
        print "Impossible to get token: " + str(e)