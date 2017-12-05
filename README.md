#<a name="top"></a>FIWARELab - Federation Monitoring API Component

[![License badge](https://camo.githubusercontent.com/651d047a62d409c28b23517069c652af8b8c429c/68747470733a2f2f636f636f61706f642d6261646765732e6865726f6b756170702e636f6d2f6c2f526573744b69742f62616467652e706e67)](http://www.apache.org/licenses/LICENSE-2.0)
[![Documentation badge](https://readthedocs.org/projects/fiware-orion/badge/?version=latest)](http://docs.federationmonitoring.apiary.io/#)

This is the code repository for the federation monitoring API component, the FIWARE tool used to provide information to user/app by a RESTFUL service.

This project is part of [FIWARE](http://www.fiware.org).

Any feedback on this documentation is highly welcome, including bugs, typos
or things you think should be included but are not. You can use [github issues](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/issues/new) to provide feedback.

**Table of Contents**


- [Description](#description)
- [Features Implemented](#features-implemented)
- [Installation Manual](#installation-manual)
- [Installation Verification](#installation-verification)
- [User Manual:](#user-manual)
- [API documentation](#api-documentation)
- [Development environment](#development-environment)
- [License](#license)


[Top](#top)

## Description

Federation Monitoring API is mainly composed by two modules:

- **monitoringProxy**: A [Python Bottle](http://bottlepy.org/docs/dev/index.html) based web-service
 *This web-service exposes, through a stable and documented API, the FIWARE monitoring informations retrieved querying other components on the underlying FIWARE monitoring. In particular this service has been implemented following a [Facade pattern](https://en.wikipedia.org/wiki/Facade_pattern) in order to rigorously respect the documented API, to hide the lower layers, standardising the access to monitoring information by clients and to adapt the monitoring API to the new FIWARE monitoring data model.*
- **nodeJS**: A [NodeJS](https://nodejs.org/) based web-service
 *This web-service was the previous main monitoring API, which is still in use to for backward compatibility towards regions still using the old FIWARE monitoring and to retrieve data from few APIs not completely migrated.*

Moreover, a third module, not strictly related with the API service, has been added to this project repository:

- **monitoringHisto**: A [Python](https://www.python.org/) based stand-alone application
 *This application is in charge of collecting, aggregating and storing periodically historical information from FIWARE Monasca API.*

The following picture depict the main architecture of the monitoringAPI system. It is possibile to see that the current architecture supports two different FIWARE federation monitoring: the first and the second enhanced version. This is needed to grant a lightweight and gradual migration process.

[FIWARE monitoringAPI architecture] (https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/raw/master/docs/raw/monitoringAPI-architecture.png "FIWARE monitoringAPI architecture")

The API service is protected by a [proxy](https://github.com/ging/fi-ware-pep-proxy) that evaluates the user's credentials through OAuth 2.0.

API provides status information about the [Openstack](https://www.openstack.org/) installation for each federated region, not only about CPU, RAM and DISK usage but also metrics regarding the status of the services and its versions. The information schema that can be provided by the Federation Monitoring API is the presented in this image.

![The federation monitoring API information schema] (https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/raw/master/docs/raw/800px-Monitoring-dataModel.png "The federation monitoring API information schema")

A detailed overview of the API contract is described at this [page](http://docs.federationmonitoring.apiary.io/)

[Top](#top)

## Features Implemented

Through the API interface users can obtain information about:

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
* FIWARE Usage data
    * *Aggregated data about the overall resource usage for the first X tenants*

The monitoringAPI, if integrated with the [FIWARE pep Proxy](https://github.com/ging/fi-ware-pep-proxy) will provide also an authentication/autorization system, that filters the available information taking into account the user's role inside the FIWARE project.

Please refer to the specific [documentation](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/tree/master/monitoringProxy) regarding the features available from the monitoringHisto module.


[Top](#top)

## Installation Manual

### Requirements
Required softwares are:

 * [git](https://github.com/) downloads and manages the software
 * [NodeJS](https://nodejs.org/), the server side runtime environment
 * [npm](https://www.npmjs.com/), the packages manager
     * the additional nodejs packages: body-parser (nodejs package)
     * mongoose (nodejs package)
     * stylus (nodejs package)
 *  the [FIWARE pep Proxy](https://github.com/ging/fi-ware-pep-proxy) used in order to protect the API
 * the [screen](https://www.gnu.org/software/screen/) utility
 * the [mysql](https://www.mysql.com/) database
 * [mongoDB](https://www.mongodb.org/)
 * [Python](https://www.python.org/) interpreter
 * Python [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)
   utility

In order to obtain a complete federation monitoring system please consider to install all the FIWARE federation monitoring components in your region, following the official  [manual](https://github.com/SmartInfrastructures/ceilometer-plugin-fiware)

### Configuration file
A [main configuration file](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/blob/master/conf/config.ini) is shared between all modules and it contains the list of available regions. For each region is specified the current status (`True -> New FIWARE monitoring`, `False -> Old FIWARE monitoring`) and the region canonical name. Moreover, an additional configuration file is specified for each module since it contains specific configuration parameters. The prototype configuration file present on each module folder can be used in order to create the main configuration file which has to be passed to the module on the command line at startup.

### monitoringAPI
This service is composed by [nodeJS](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/tree/master/nodeJS) and [monitoringProxy](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/tree/master/monitoringProxy) packages, therefore the recommended steps include the installation of both services:

1. Install NodeJs (and also [npm](https://www.npmjs.com/) ), there are several guides or tutorials about that. User can install it from the official repositories: ["Nodejs download section"](https://nodejs.org/download/)
2. Copy from nodeJS folder the `api.cfg` in `api-password.cfg` and customise it with the proper values (i.e. samples temporal validity range, KP endpoint information)
3. Install the dependencies

    ```
    cd nodeJS
    npm install
    ```
4. Install the [Python](https://www.python.org/) interpreter
5. Install the Python [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) utility
6. Create a virtual environment and access to it

    ```
    mkvirtualenv monitoringProd
    workon monitoringProd
    ```
7. Install the required dependencies

    ```
    cd monitoringProxy
    pip install -r requirements.txt
    ```
8. Copy from monitoringProxy folder the `config.ini` in `config-password.ini` and customise it with the proper values.
9. Start the services, see below for details.

### monitoringHisto
Please refer to the specific [documentation](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/tree/master/monitoringProxy) regarding the installation of this module.

### Start the web-service

Once installed, the two applications can be manually run respectively as follow:
*As a requirement, in order to enable the APIs that requires authentication, the pep-proxy service should already run*

**monitoringProxy**
```
python monitoringProxy/proxy_monitoring.py -c monitoringProxy/<config file>
```
**nodeJS**
Many instances of the nodeJS service can run at the same time and point to different datasources. In this case they must be started one by one. Each instance must point to a different configuration file.
```
node nodeJS/monitoringAPI.js nodeJS/<config file>
```

An alternative way is to start all the application's modules in an automatic way using the screen files present in the [start_scripts](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/tree/master/start_scripts) folder:
```
screen -c start_scripts/start.screen
```
In this way a screen session will be started and a screen tab will be created for each service. Navigating through the tabs allows the administrator of the service to have a complete monitoringAPI console in order to control the status and make adjustments if needed.

[Top](#top)

## Installation Verification

In order to check the status of this tool is sufficient to check the status of the following processes: `monitoringAPI.js`, `proxy_monitoring.py` and `pep-proxy2.js`. If the web-service has been started with the [start_scripts](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/tree/master/start_scripts) the status can be seen navigating the various tabs on the relative screen session `screen -r`.
After that, it is possible to test also the Federation Monitoring API status by using CURL commands. This can be done following these simple two steps:
1. Require a token to the IDM (oath2)
2. Send a proper request (GET) to the pep-proxy that stands in front of the API

### Obtain token:

See [get_token.js](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/blob/master/nodeJS/get_token.js) or [get_token.py](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/blob/master/monitoringProxy/get_token.py).

the below example shows how to obtain the token using [get_token.js](https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI/blob/master/nodeJS/get_token.js) script:

```
node get_token.js "username" "password" "auth_url"
```

It prints the token that can bu used in this way:

```
curl -H "Authorization:Bearer <token>" -s 127.0.0.1:1027/monitoring/regions/Trento/hosts
```

[Top](#top)

## User Manual:
The user manual is not provided in this *Readme.md* file. User can easily use this restful webserver, by simple calling the API.

Few examples following:

* Retrieve list of regions
```
curl -X GET -H "Cache-Control: no-cache" -H "http://MONITORING_API_ENDPOINT:MONITORING_API_PORT/monitoring/regions"
```

* Retrieve information for Spain region
```
curl -X GET -H "Cache-Control: no-cache" -H "http://MONITORING_API_ENDPOINT:MONITORING_API_PORT/monitoring/regions/Spain2"
```

* Retrieve hosts on Spain region *(this query requires authentication)*
```
curl -X GET -H "Authorization: Bearer BEARER_TOKEN" -H "Cache-Control: no-cache" -H "http://MONITORING_API_ENDPOINT:MONITORING_API_PORT/monitoring/regions/Spain2/hosts"
```



## API documentation

An updated and detailed documentation about the API available from this web-service have a look at the [apiary page](http://docs.federationmonitoring.apiary.io/).

[Top](#top)

## Development environment

Two development environments based on Vagrant are present:
    * The first can be used to simulate the source of data where monitoringAPI retrieve metrics and the Infographics GUI. It is available at this project page: [vagrant-FIWARELab-monitoringAPI](https://github.com/SmartInfrastructures/vagrant-FIWARELab-monitoringAPI).
    * The second is more oriented to monitoringAPI development, it includes all the services described above a the fiware-pep-proxy. It is present in the `vagrant` folder.


## License

This tool is licensed under Apache v2.0 license.


[Top](#top)
