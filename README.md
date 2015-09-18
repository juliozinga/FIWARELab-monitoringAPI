# FIWARELab - Federation Monitoring API Component

This is the code repository for the federation monitoring API component, the FIWARE tool used to provide information to user/app by a RESTFUL service.

This project is part of [FIWARE](http://www.fiware.org).

Any feedback on this documentation is highly welcome, including bugs, typos
or things you think should be included but are not. You can use [github issues](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/issues/new) to provide feedback.

[Top](#top)

## Description

Federation Monitoring API is a [NodeJS](https://nodejs.org/) application that can be easily configured and modified. This application is based on Node.js: an open source, cross-platform runtime environment for server-side and networking applications. This application is a part of the structured monitoring system developed inside the FIWARE project. This component retrieves information by several distributed tools (i.e. Orion, Cosmos,) and export them to the end-users. Moreover he API service is protected by a [proxy](https://github.com/ging/fi-ware-pep-proxy) that evaluates the user's credentials through an oauth2 system.
![alt text](http://wiki.fi-xifi.eu/wiki/images/thumb/c/cf/Federation_Monitoring.png/800px-Federation_Monitoring.png "The federation monitoring architecture")
API provides information, for example about the [Openstack](https://www.openstack.org/) installation, the CPU usage (CPU, RAM, DISK). The information schema that can be provided by the Federation Monitoring API is the presented in this image.
![alt text](http://wiki.fi-xifi.eu/wiki/images/thumb/5/5d/Monitoring-dataModel.png/800px-Monitoring-dataModel.png "The federation monitoring API information schema")

An overview of the API information is described at this [page](http://docs.federationmonitoring.apiary.io/)

The official software repository (on GitHub) is composed by four files:
* monitoringAPI.js: the main program file
* api.cfg: the configuration file
* package.json: the dependencies file
* LICENSE: the license file
* README.md: the file with the main information

[Top](#top)

## Features Implemented

This tool provides information about the platform and export it through API interface. Users can obtain information about
* Region (%RAM, %CPU, %DISK, #IP, ...)
 * *list of regions*
 * *live information about a region*
 * *historical information about a region*
* Virtual machine (%RAM, %CPU, %DISK, ... )
 * *list of VMs per region*
 * *live information about a VM*
 * *historical information about a VM*
* Host (%RAM, %CPU, %DISK, ... )
 * *list of hosts per region*
 * *live information about a host*
 * *historical information about a host*
* Host service (nova, cinder, sanity_check, ...)
 * *live information about the host_services per region*
 * *historical information about the host_services per region*

The monitoringAPI, if integrated with the [FIWARE pep Proxy](https://github.com/ging/fi-ware-pep-proxy) will provide also an authentication/autorization system, that filters the available information taking into account the user's role inside the FIWARE project.

A complete reference about all the API can be found [here](http://docs.federationmonitoring.apiary.io/)

[Top](#top)

## Installation Manual

The recommended steps for installing this tool are:

1. install NodeJs (and also [npm](https://www.npmjs.com/) ), there are several guides or tutorials about that. User can install it from the official repositories: ["Nodejs download section"](https://nodejs.org/download/)
2. configure the file api.cfg with the proper values (i.e. samples temporal validity range, KP endpoint information)
3. install the dependencies
  * npm install
4. run the restful Nodejs application:
  * node monitoringAPI.js

### Requirements

Required softwares are:
* [git](https://github.com/) downloads and manages the software
* [NodeJS](https://nodejs.org/), the server side runtime environment
* [npm](https://www.npmjs.com/), the packages manager
  * the additional nodejs packages:
    * body-parser (nodejs package)
    * mongoose (nodejs package)
    * stylus (nodejs package)
*  the [FIWARE pep Proxy](https://github.com/ging/fi-ware-pep-proxy) used in order to protect the API
* the [mysql](https://www.mysql.com/) database
* [mongoDB](https://www.mongodb.org/)

In order to obtain a complete federation monitoring system please consider to install all the XIFI federation monitoring components in your region, following the official  [manual](http://wiki.fi-xifi.eu/Public:Federation_Monitoring#Installation_Manual)

### Installation

Once the main packages are downloaded, user has to install the NodeJS and the additional modules. This can be done by using npm inside the installation folder:
* npm install

### Configuration file

The configuration used by the Federation Monitoring API component is stored in the api.conf file. This fiel contains several fields, which values can be customized:

    {
    "KPurl":"xxx",
    "KPusr":"xxx",
    "KPpwd":"xxx",
    "IDMurl":"xxx",
    "mysql_host": "xxx",
    "mysql_user":"xxx",
    "mysql_password":"xxx",
    "mysql_database":"xxx",
    "apiIPaddress":"0.0.0.0",
    "apiPort": "000",
    "mongoIP":"000",
    "mongoDBname":"xxx",
    "regionTTL":"000",
    "hostTTL":"000",
    "vmTTL":"000",
    "serviceTTL":"000",
    "h2hTTL":"000",
    "defaultTTL":"000"
    }

These fields are mandatory, and they are used by the API filter and retrieve the information.
* KPurl: set the KeyStone URL or IP
* KPusr: set the KeyStone username that has been provided by the KP administrator
* KPpwd: set the KeyStone password
* IDMurl:set the Identity Manager IP address or URL
* mysql_host: set the mysql hostname
* mysql_user: set the mysql authorized user
* mysql_password: set the mysql authorized password
* mysql_database: set the mysql name of the database
* apiIPaddress: set the API IP on which API should run (usually "0.0.0.0")
* apiPort: set the API port
* mongoIP: set the mongo IP address
* mongoDBname: set the mongo database name
* regionTTL: set the valid time-range for the information of a region
* hostTTL: set the valid time-range for the information of a host
* vmTTL: set the valid time-range for the information of a vm
* serviceTTL: set the valid time-range for the information of a service
* h2hTTL: set the valid time-range for the information of a host2host
* defaultTTL: set the default valid time-range for a generic information

### How to run it

Once installed, the application can be run manually as:
* node monitoringAPI.js

However expert users can setup it a service (*i.e. using nohup*).
This tool can help the normal user to put the application working "like" a linux service. For more information have a look to this link:
* [nohup](http://linux.die.net/man/1/nohup) linux background

[Top](#top)

## Installation Verification

In order to check the status of this tool is sufficient to check the status of the NodeJS process. After that, it is possible to test also the Federation Monitoring API status by using CURL commands. This process is a tow steps process:
1. require a token to the IDM (oath2)
2. send a proper request (GET) to the pep-proxy that stands in front of the API

Another solution is using this simple [script](https://github.com/SmartInfrastructures/xifi-script/blob/master/testAPI.js) that has been developed (NodeJS) for testing purpose. This script manages the handshake for the token request (IDM), and then it is able to perform an API request to your test/production API installation.

[Top](#top)

## User Manual:
The user manual is not provided in this *Readme.md* file. User can easily use this restful webserver, by simple calling the API. For more information about some API URL examples have a look at the [apiary page](http://docs.federationmonitoring.apiary.io/)

[Top](#top)

## Known Issues
The main issues about this tools are linked to its interaction with the pep-proxy. This requires a bit of expertise on OAUTH2 system. As a matter of fat users do not interact directly with the API, but they communicate to the PEP proxy interface.

[Top](#top)

## Link to github
[This](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI) is the official Github repository:
* https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI

[Top](#top)

## License

This tool is licensed under Apache v2.0 license.


[Top](#top)
