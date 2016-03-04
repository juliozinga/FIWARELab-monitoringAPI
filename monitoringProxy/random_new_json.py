#!/usr/bin/env python

# File name: random_nwe_json.py
# Author: Daniel Depaoli
# Date created: 03/02/2016
# Date last modified: 03/02/2016
# Python Version: 2.7
#
#Description: Generate random json to test monitoring api
#
#How to run: python random_nwe_json.py | sed s/\'/\"/g >> file.json
#How to import: mongoimport --host localhost --db orion --collection entities < file.json


import random
import string
from random import randrange

'''
Sample json
'''
IMAGE = {
    "_id": {
        "id": "c3fc71dc-f115-4f05-b8d1-f9eadaf598e9",
        "type": "image"
    },
    "attrs": [{
        "name": "size",
        "type": "string",
        "creDate": 1447318541,
        "value": "125000",
        "modDate": 1447318541
    },
    {
        "name": "status",
        "type": "string",
        "creDate": 1447318541,
        "value": "ACTIVE",
        "modDate": 1447318541
    },
    {
        "name": "name",
        "type": "string",
        "creDate": 1447318541,
        "value": "image_name",
        "modDate": 1447318541
    },
    {
        "name": "catalogue_ge_id",
        "type": "string",
        "creDate": 1447318541,
        "value": "ACTIVE",
        "modDate": 1447318541
    }]
}

HOST = {
    "_id": {
        "id": "Trento:host",
        "type": "host"
    },
    "attrs": [{
        "name": "cpuPct",
        "type": "string",
        "creDate": 1447318541,
        "value": "80",
        "modDate": 1447318541
    },
    {
        "name": "cpuNow",
        "type": "string",
        "creDate": 1447318541,
        "value": "80",
        "modDate": 1447318541
    },
    {
        "name": "cpuTot",
        "type": "string",
        "creDate": 1447318541,
        "value": "80",
        "modDate": 1447318541
    },
    {
        "name": "diskNow",
        "type": "string",
        "creDate": 1447318541,
        "value": "80",
        "modDate": 1447318541
    },
    {
        "name": "diskTot",
        "type": "string",
        "creDate": 1447318541,
        "value": "80",
        "modDate": 1447318541
    },
    {
        "name": "ramNow",
        "type": "string",
        "creDate": 1447318541,
        "value": "80",
        "modDate": 1447318541
    },
    {
        "name": "ramTot",
        "type": "string",
        "creDate": 1447318541,
        "value": "80",
        "modDate": 1447318541
    }
    ]
}

#City name list used to get randomly
CITY_LIST = ["Trento", "Zurich", "Berlin"]

def random_alphanumerical_string(len):
    return ''.join(random.choice(string.ascii_lowercase+'0123456789',) for i in range(len))

def random_num(min, max):
    return randrange(min, max)

def image_name():
    return( random_alphanumerical_string(8)+'-'+
            random_alphanumerical_string(4)+'-'+
            random_alphanumerical_string(4)+'-'+
            random_alphanumerical_string(4)+'-'+
            random_alphanumerical_string(12))

def random_host(host):
    new_host = host
    new_host["_id"]["id"] = random.choice(CITY_LIST) + ":" + random_alphanumerical_string(10)
    for item in new_host["attrs"]:
        item["creDate"] = 1451821830
        item["modDate"] = randrange(1451821831, 1454493294)
        item["value"] = randrange(1, 300)
    return new_host

def random_image(image):
    new_image = image
    new_image["_id"]["id"] = random.choice(CITY_LIST) + ":" + image_name()
    for item in new_image["attrs"]:
        item["creDate"] = 1451821830
        item["modDate"] = randrange(1451821831, 1454493294)
        item["value"] = randrange(1, 300)
    return new_image

def main():
    new_host = random_host(HOST)
    new_image = random_image(IMAGE)
    for i in range(1, 10):
        print random_host(HOST)
    for i in range(1, 10):
        print random_image(IMAGE)

if __name__ == '__main__':
    main()