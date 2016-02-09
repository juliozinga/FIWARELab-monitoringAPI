#!/usr/bin/env python

from monitoring import get_keypass_token, request_to_idm
import sys

URL = "http://cloud.lab.fiware.org:4730/v3/auth/tokens"

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "This script get token from IDM."
        print "Usage:"
        print sys.argv[0] + " <username> <password> "
        sys.exit(-1)
    try:
        token = get_keypass_token(username=sys.argv[1], password=sys.argv[2], url=URL)
        print "\nYour token is: {}\n".format(token)
        print "Use it in this way:"
        print "curl -H \"Authorization:Bearer {}\" -s <monitoring_ip>:<monitoring_port>/monitoring/regions".format(token)
    except Exception as e:
        print "Impossible to get token: " + str(e)