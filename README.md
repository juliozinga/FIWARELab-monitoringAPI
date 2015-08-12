# XIFI - Federation Monitoring API Component

This is the code repository for the federation monitoring API component, the FIWARE tool used to provide information to user/app by a restful serrvice.

This project is part of [FIWARE](http://www.fiware.org).

Any feedback on this documentation is highly welcome, including bugs, typos
or things you think should be included but are not. You can use [github issues](https://github.com/SmartInfrastructures/xifi-monitoringAPI/issues/new) to provide feedback.

## Overall description

Federation Monitoring API is a [NodeJS](https://nodejs.org/) application that can be easily configured and modified. Ths application is based on Node.js: an open source, cross-platform runtime environment for server-side and networking applications. Thi application is a part of structured minitoring system developed inside the XIFI project. This component retrieve information by several distributed tools (i.e. Orion, Cosmos,) and export them to the endusers.
![alt text](http://wiki.fi-xifi.eu/wiki/images/thumb/c/cf/Federation_Monitoring.png/800px-Federation_Monitoring.png "The federation monitoring architecture")
API provides information, for example about the [Openstack](https://www.openstack.org/) installation, the CPU utilzation (CPU, RAM, DISK). The information schema that can be provided by the Federation Monitoring API is the presented in this image.
![alt text](http://wiki.fi-xifi.eu/wiki/images/thumb/5/5d/Monitoring-dataModel.png/800px-Monitoring-dataModel.png "The federation monitoring API information schema")

An overview of the API information is described at this [page](http://docs.federationmonitoring.apiary.io/)

This repository is composed by 4 files:
* monitoringAPI.js: the main program file
* api.cfg: the configuration file
* package.json: the dependencies file
* LICENSE: the license file
* README.md: the file with the main information 

## Build and Install

The recommended procedure is to install follow the Nodejs standard:
1. install NodeJs (and also [npm](https://www.npmjs.com/) ), there are several guides or tutorial about that. User can install it from the official repositories or please have a look at the [Nodejs download section](https://nodejs.org/download/))
2. configure the file api.cfg with the proper values (i.e. samples temporal validity range, KP endpoint information)
3. install the dependencies 
..* npm install
4. run the restful Nodejs application
⋅⋅* node monitoringAPI.js
..* or in background nohup node monitoringAPI.js & 

### Requirements

The software that are required are:
* [git](https://github.com/) download and manage the software
* [NodeJS](https://nodejs.org/) the server side runtime environment
  * body-parser (nodejs package)
  * mongoose (nodejs package)
  * stylus (nodejs package)
* [npm](https://www.npmjs.com/) (the package manager)
* [FIWARE pep Proxy](https://github.com/ging/fi-ware-pep-proxy)
* [mysql](https://www.mysql.com/)
* [mongoDB](https://www.mongodb.org/)
In order to obtain a complete federetion monitoring system please consider to istall all the XIFI federation monitoring components in your region, following the [manual](http://wiki.fi-xifi.eu/Public:Federation_Monitoring#Installation_Manual)

### Installation

Once the main packages are installed only an additional steop is required: install the nodejs dependencies. This can be done by using npm
* npm install 

#### Optional packages

This tool can help the normal user to put the application working "like" a linux service: 
* [nohup](http://linux.die.net/man/1/nohup) linux background 

## Running

Once installed, there is a way to run this application manually
* node node monitoringAPI.js
However expert user can setup it a service

### Configuration file

The configuration used by the Federation Monitoring API component is stored in the
<directory>api.conf file, which typical content is:

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
These fields are mandatory, and they are used by the api in order to obtain the filter informarions.
* KPurl: set the KeyStone URL or IP
* KPusr: set the KeyStone username that has been provided by the KP administrator
* KPpwd: set the KeyStone password
* IDMurl:set the Identity Manager IP adderss or URL
* mysql_host: set the mysql hostname
* mysql_user: set the mysql authorized user
* mysql_password: set the mysql authorized password
* mysql_database: set the mysql name of the database
* apiIPaddress: set the API IP on wchich API should run (usually "0.0.0.0")
* apiPort: set the API port
* mongoIP: set the mongo IP address
* mongoDBname: set the mongo database name
* regionTTL: set the valid time-range for the information of a region
* hostTTL: set the valid time-range for the information of a host
* vmTTL: set the valid time-range for the information of a rvm
* serviceTTL: set the valid time-range for the information of a service
* h2hTTL: set the valid time-range for the information of a host2host
* defaultTTL: set the default valid time-range for a generic information

### Checking status

In order to check the status of the Federation Monitoring API, it is sufficient to check the status of the NodeJS process, or try to call the API (see the following section)

## Testing

In order to test the Federation Monitoring API, a user can use CURL commands by requiring a token to the IDM and then sending a proper request to the pep-proxy in front to the API. Another solution is using this simple [testAPI-script](https://github.com/SmartInfrastructures/xifi-script/blob/master/testAPI.js) that has been developed (NodeJS) for testing poupose. 

## Advanced topics:
missing

## License

GlanceSync is licensed under Apache v2.0 license.
