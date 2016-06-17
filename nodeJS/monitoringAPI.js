/***********************************/
// Copyright 2014 Create-net.org   //
// All Rights Reserved.            //
// date :04-06-2014                //
// author: attybro                 //
// monitoringAPI for XiFi project  //
/***********************************/
fs = require('fs');
http = require('http');
http1 = require('http');
https = require('https');
url = require('url');
Enum = require('enum');
mongoose = require('mongoose');
oAuth = require('oauth');
moment = require('moment');
request = require('request');
p = 0
var mysql = require('mysql');
var confObj = readConf();
var db_config = {
  host: confObj.mysql_host,
  user: confObj.mysql_user,
  port: confObj.mysql_port,
  password: confObj.mysql_password,
  database: confObj.mysql_database
};
var optionsKP = null
var optionsIDM = null
var xToken = null;
var lifeToken = null;
var connection;

function handleDisconnect() {
  connection = mysql.createConnection(db_config); // Recreate the connection, since
  // the old one cannot be reused.
  connection.connect(function(err) { // The server is either down
    if (err) { // or restarting (takes a while sometimes).
      console.log('error when connecting to db:', err);
      setTimeout(handleDisconnect, 2000); // We introduce a delay before attempting to reconnect,
    } // to avoid a hot loop, and to allow our node script to
  }); // process asynchronous requests in the meantime.
  // If you're also serving http, display a 503 error.
  connection.on('error', function(err) {
    console.log('db error', err);
    if (err.code === 'PROTOCOL_CONNECTION_LOST') { // Connection to the MySQL server is usually
      handleDisconnect(); // lost due to either server restart, or a
    } else { // connnection idle timeout (the wait_timeout
      throw err; // server variable configures this)
    }
  });
}
handleDisconnect();
var entitySchema = mongoose.Schema({
  _id: {},
  attrs: {},
  modDate: String,
  creDate: String
})
var Entity = mongoose.model('Entity', entitySchema)
var base_response = {
  "_links": {
    "self": {
      "href": ""
    }
  },
  "measures": [{}]
};
localEnum = new Enum({
  'ROOT': 0,
  'LIST_REGION': 1,
  'SINGLE_REGION': 2,
  'SINGLE_REGION_TIME': 3,
  'LIST_HOST': 4,
  'SINGLE_HOST': 5,
  'SINGLE_HOST_TIME': 6,
  'LIST_VM': 7,
  'SINGLE_VM': 8,
  'SINGLE_VM_TIME': 9,
  'LIST_H2H': 10,
  'SINGLE_H2H': 11,
  'SINGLE_H2H_TIME': 12,
  'LIST_SERVICE_H': 13,
  'SINGLE_SERVICE_H': 14,
  'SINGLE_SERVICE_H_TIME': 15,
  'LIST_SERVICE_VM': 16,
  'SINGLE_SERVICE_VM': 17,
  'SINGLE_SERVICE_VM_TIME': 18,
  'LIST_SERVICE_R': 19,
  'LIST_SERVICE_R_TIME': 20,
  'LIST_NES': 21,
  'SINGLE_NES': 22,
  'SINGLE_NES_TIME': 23,
  "LIST_DETAILS_VMS": 24,
  'OK': 200,
  'BAD_REQUEST': '400',
  'UNAUTHORIZED': '401',
  'NOT_FOUND': '404',
  'SERVER_ERROR': '500',
  'NOT_IMPLEMENTED': '501',
  'ADMIN': 191,
  'IO': 192,
  'FED_MAN': 193,
  'DEV': 194,
  'SLA': 1274,
  'TRUSTED_APP': ['aaa', 'bbb'],
  'TrentoNode': 350
});
// Load trusted app from configuration file
if (confObj.trusted_app != null) {
  localEnum.TRUSTED_APP.value = confObj.trusted_app;
}
connection.connect(function(err) {
  config_file = check_file(process.argv)
  main(config_file);
});
//connection.end();
//main();
function check_file(argv) {
  if (argv.length != 3) {
    console.log("No input config file.\nPlease use: " + argv[1] + " <config file>")
    process.exit(-1)
  } else {
    if (fs.existsSync(argv[2])) {
      return argv[2];
    } else {
      console.log('File ' + argv[2] + ' not found!');
      process.exit(-1)
    }
  }
  process.exit(-2)
}

function readConf() {
  var data = fs.readFileSync(check_file(process.argv), 'utf8');
  if (data && IsJsonString(data)) {
    return JSON.parse(data);
  }
}

function main(config_file) {
  fs.readFile(config_file, 'utf8', function(err, data) {
    if (err) {
      return console.log(err);
    } else if (data && IsJsonString(data)) {
      cfgObj = JSON.parse(data);
      if (cfgObj && cfgObj.KPurl && cfgObj.KPusr && cfgObj.KPpwd && cfgObj.IDMurl && cfgObj.apiIPaddress && cfgObj.apiPort && cfgObj.mongoIP && cfgObj.mongoDBname && cfgObj.mongoPort && cfgObj.regionTTL &&
        cfgObj.hostTTL && cfgObj.vmTTL && cfgObj.serviceTTL && cfgObj.h2hTTL) {
        //enable server
        optionsKP = {
          url: cfgObj.KPurl + '/v3/auth/tokens',
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          json: {
            'auth': {
              'identity': {
                'methods': ['password'],
                'password': {
                  'user': {
                    'name': cfgObj.KPusr,
                    'domain': {
                      'id': 'default'
                    },
                    'password': cfgObj.KPpwd
                  }
                }
              }
            }
          }
        };
        optionsIDM = {
          url: cfgObj.KPurl + '/v3/OS-SCIM/v2/ServiceProviderConfigs',
          method: 'GET',
          headers: {
            'X-Auth-Token': null
          }
        };
        IDMurl = cfgObj.IDMurl
        mongoPath = 'mongodb://' + cfgObj.mongoIP + ':' + cfgObj.mongoPort + '/' + cfgObj.mongoDBname;
        mongoose.connect(mongoPath);
        var server = http.createServer(function(req, res) {
          manageRequest(req, res);
        });
        server.listen(cfgObj.apiPort, cfgObj.apiIPaddress);
        console.log('Server running at http://' + cfgObj.apiIPaddress + ':' + cfgObj.apiPort + '/');
        var manageRequest = function(req, res) {
            var authToken = ''
            var regionId = '';
            var hostId = '';
            var vmId = '';
            var serviceId = '';
            var h2h = '';
            var nesId = '';
            var sinceValue = 0;
            var aggregate = 'h';
            authToken = getTokenHeader(req.headers);
            var url_parts = [];
            if (req.url) {
              caseId = localEnum.BAD_REQUEST;
              url_parts = url.parse(req.url, true);
              if (url_parts.pathname) {
                parts = url_parts.pathname.split('/').filter(function(n) {
                  return n
                });
                /*root case*/
                if (parts.length == 0) caseId = localEnum.ROOT;
                /*region case*/
                else if (parts.length == 2 && parts[0] == "monitoring" && parts[1] == "regions") caseId = localEnum.LIST_REGION; //monitoring/regions
                else if (parts.length == 3 && parts[0] == "monitoring" && parts[1] == "regions") {
                  if (!url_parts.query.since) {
                    sinceValue = 0
                    caseId = localEnum.SINGLE_REGION;
                    regionId = parts[2];
                  } else if (url_parts.query.since && url_parts.query.since) {
                    sinceValue = url_parts.query.since;
                    if (moment(sinceValue, "YYYY-MM-DDTHH:mm:ss").isValid()) {
                      caseId = localEnum.SINGLE_REGION_TIME;
                      regionId = parts[2];
                    }
                  }
                }
                /*VM*/ //monitoring/regions/{regionid}/vms    //monitoring/regions/{regionid}/vms/{vmid}{?since}
                else if ( parts.length == 4 && parts[0] == "monitoring" && parts[1] == "regions" && (parts[3].indexOf('vms') === 0) ) {
                  regionId = parts[2];
                  if ( parts[3] == "vms" ) {
                    caseId = localEnum.LIST_VM;
                  }
                  else if ( parts[3] == "vmsdetails" ) {
                    caseId = localEnum.LIST_DETAILS_VMS;
                  }
                } else if (parts.length == 5 && parts[0] == "monitoring" && parts[1] == "regions" && parts[3] == "vms") {
                  if (!url_parts.query.since) {
                    caseId = localEnum.SINGLE_VM;
                    regionId = parts[2];
                    vmId = parts[4]
                  } else if (url_parts.query.since && url_parts.query.since) {
                    sinceValue = url_parts.query.since;
                    if (moment(sinceValue, "YYYY-MM-DDTHH:mm:ss").isValid()) {
                      caseId = localEnum.SINGLE_VM_TIME;
                      regionId = parts[2];
                      vmId = parts[4]
                    }
                  }
                }
                /*HOST*/ //monitoring/regions/{regionid}/hosts     //monitoring/regions/{regionid}/hosts/{hostid}{?since}
                else if (parts.length == 4 && parts[0] == "monitoring" && parts[1] == "regions" && parts[3] == "hosts") {
                  regionId = parts[2];
                  caseId = localEnum.LIST_HOST;
                } else if (parts.length == 5 && parts[0] == "monitoring" && parts[1] == "regions" && parts[3] == "hosts") {
                  if (!url_parts.query.since) {
                    caseId = localEnum.SINGLE_HOST;
                    regionId = parts[2];
                    hostId = parts[4];
                  } else if (url_parts.query.since && url_parts.query.since) {
                    sinceValue = url_parts.query.since;
                    if (moment(sinceValue, "YYYY-MM-DDTHH:mm:ss").isValid()) {
                      caseId = localEnum.SINGLE_HOST_TIME;
                      regionId = parts[2];
                      hostId = parts[4];
                    } else caseId = localEnum.BAD_REQUEST
                  }
                }
                /*Services4Host*/ //monitoring/regions/{regionid}/hosts/{hostid}/services    //monitoring/regions/{regionid}/hosts/{hostid}/services/{serviceName}?since
                else if (parts.length == 6 && parts[0] == "monitoring" && parts[1] == "regions" && parts[3] == "hosts" && parts[5] == "services") {
                  regionId = parts[2];
                  hostId = parts[4];
                  caseId = localEnum.LIST_SERVICE_H;
                } else if (parts.length == 7 && parts[0] == "monitoring" && parts[1] == "regions" && parts[3] == "hosts" && parts[5] == "services") {
                  if (!url_parts.query.since) {
                    caseId = localEnum.SINGLE_SERVICE_H;
                    regionId = parts[2];
                    hostId = parts[4];
                    serviceId = parts[6];
                  } else if (url_parts.query.since && url_parts.query.since) {
                    caseId = localEnum.SINGLE_SERVICE_H_TIME;
                    regionId = parts[2];
                    hostId = parts[4];
                    serviceId = parts[6];
                    sinceValue = url_parts.query.since;
                  }
                }
                /*Service4VM*/ //monitoring/regions/{regionid}/vms/{vmid}/services        //monitoring/regions/{regionid}/vms/{vmid}/services/{serviceName}?{since}
                else if (parts.length == 6 && parts[0] == "monitoring" && parts[1] == "regions" && parts[3] == "vms" && parts[5] == "services") {
                  regionId = parts[2];
                  vmId = parts[4];
                  caseId = localEnum.LIST_SERVICE_VM;
                } else if (parts.length == 7 && parts[0] == "monitoring" && parts[1] == "regions" && parts[3] == "vms" && parts[5] == "services") {
                  if (!url_parts.query.since) {
                    caseId = localEnum.SINGLE_SERVICE_VM;
                    regionId = parts[2];
                    vmId = parts[4];
                    serviceId = parts[6];
                  } else if (url_parts.query.since && url_parts.query.since) {
                    caseId = localEnum.SINGLE_SERVICE_VM_TIME;
                    regionId = parts[2];
                    vmId = parts[4];
                    serviceId = parts[6];
                    sinceValue = url_parts.query.since;
                  }
                }
                /*Services4Region*/ //monitoring/regions/{regionid}/services?{since}
                else if ((parts.length == 4 || parts.length == 5) && parts[0] == "monitoring" && parts[1] == "regions" && parts[3] == "services") {
                  if (!url_parts.query.since) {
                    caseId = localEnum.LIST_SERVICE_R;
                    regionId = parts[2];
                  } else if (url_parts.query.since) {
                    //console.log(url_parts.query)
                    sinceValue = url_parts.query.since;
                    if (!url_parts.query.aggregate) {
                      aggregate = 'h';
                    } else if (url_parts.query.aggregate && (url_parts.query.aggregate == 'h' || url_parts.query.aggregate == 'd' || url_parts.query.aggregate == 'm')) aggregate = url_parts.query
                      .aggregate;
                    if (moment(sinceValue, "YYYY-MM-DDTHH:mm:ss").isValid()) {
                      caseId = localEnum.LIST_SERVICE_R_TIME;
                      regionId = parts[2];
                    }
                  }
                }
                /*Host2Host*/ //monitoring/host2hosts     //monitoring/host2hosts/{source};{dest}{?since}
                else if (parts.length == 2 && parts[0] == "monitoring" && parts[1] == "host2hosts") {
                  caseId = localEnum.LIST_H2H;
                } else if (parts.length == 3 && parts[0] == "monitoring" && parts[1] == "host2hosts") {
                  if (!url_parts.query.since) {
                    caseId = localEnum.SINGLE_H2H;
                    h2h = parts[2];
                    //console.log(h2h);
                  } else if (url_parts.query.since && url_parts.query.since) {
                    sinceValue = url_parts.query.since;
                    if (moment(sinceValue, "YYYY-MM-DDTHH:mm:ss").isValid()) {
                      caseId = localEnum.SINGLE_H2H_TIME;
                      h2h = parts[2];
                    }
                  }
                }
                /*NES*/ //monitoring/regions/{regionid}/nes   //monitoring/regions/{regionid}/nes/{neid}{?since}
                else if (parts.length == 4 && parts[0] == "monitoring" && parts[1] == "regions" && parts[3] == "nes") {
                  regionId = parts[2];
                  caseId = localEnum.LIST_NES;
                } else if (parts.length == 5 && parts[0] == "monitoring" && parts[1] == "regions" && parts[3] == "nes") {
                  if (!url_parts.query.since) {
                    caseId = localEnum.SINGLE_NES;
                    regionId = parts[2];
                    nesId = parts[4];
                  } else if (url_parts.query.since && url_parts.query.since) {
                    caseId = localEnum.SINGLE_NES_TIME;
                    regionId = parts[2];
                    nesId = parts[4];
                    sinceValue = url_parts.query.since;
                  }
                }
                //EndCase
              }
            } else { //no req.url
              caseId = localEnum.BAD_REQUEST;
            }
            /*Some debug information about url parsing*/
            /*
console.log(req.url);
console.log(caseId.key)
console.log(" regionId: "+regionId)
console.log(" hostId: "+hostId)
console.log(" vmId: "+vmId)
console.log(" serviceId: "+serviceId)
console.log(" h2h: "+h2h)
console.log(" nesId: "+nesId)
console.log(" sinceValue: "+sinceValue)
*/
            /*Start switch case*/
            switch (caseId.value) {
              case localEnum.ROOT.value:
                root(res, 200, authToken)
                break;
              case localEnum.LIST_REGION.value:
                getRegionList(res, 200, authToken)
                break;
              case localEnum.SINGLE_REGION.value:
                getRegion(res, 200, authToken, regionId)
                break;
              case localEnum.SINGLE_REGION_TIME.value:
                getRegionTime(res, 200, authToken, regionId, sinceValue)
                break;
              case localEnum.LIST_HOST.value:
                getHostList(res, 200, authToken, regionId)
                break;
              case localEnum.SINGLE_HOST.value:
                getHost(res, 200, authToken, regionId, hostId)
                break;
              case localEnum.SINGLE_HOST_TIME.value:
                getHostTime(res, 200, authToken, regionId, hostId, sinceValue)
                break;
              case localEnum.LIST_VM.value:
                getVmList(res, 200, authToken, regionId)
                break;
              case localEnum.LIST_DETAILS_VMS.value:
                getVmsDetails(res, 200, authToken, regionId)
                break;
              case localEnum.SINGLE_VM.value:
                getVm(res, 200, authToken, regionId, vmId)
                break;
              case localEnum.SINGLE_VM_TIME.value:
                getVmTime(res, 200, authToken, regionId, vmId, sinceValue)
                break;
              case localEnum.LIST_H2H.value:
                getH2HList(res, 200, authToken)
                break;
              case localEnum.SINGLE_H2H.value:
                getH2H(res, 200, authToken, h2h)
                break;
              case localEnum.SINGLE_H2H_TIME.value:
                getH2HTime(res, 200, authToken, h2h, sinceValue)
                break;
              case localEnum.LIST_SERVICE_R.value:
                getServiceRegion(res, 200, authToken, regionId, sinceValue)
                break;
              case localEnum.LIST_SERVICE_R_TIME.value:
                getServiceRegionTime(res, 200, authToken, regionId, sinceValue, aggregate)
                break;
              case localEnum.LIST_SERVICE_H.value:
                getServiceHList(res, 200, authToken, regionId, hostId)
                break;
              case localEnum.SINGLE_SERVICE_H.value:
                getServiceH(res, 200, authToken, regionId, hostId, serviceId)
                break;
              case localEnum.SINGLE_SERVICE_H_TIME.value:
                getServiceHTime(res, 200, authToken, regionId, hostId, serviceId, sinceValue)
                break;
              case localEnum.LIST_SERVICE_VM.value:
                getServiceVMList(res, 200, authToken, regionId, vmId)
                break;
              case localEnum.SINGLE_SERVICE_VM.value:
                getServiceVM(res, 200, authToken, regionId, vmId, serviceId)
                break;
              case localEnum.SINGLE_SERVICE_VM_TIME.value:
                getServiceVMTime(res, 200, authToken, regionId, vmId, serviceId, sinceValue)
                break;
              case localEnum.LIST_NES.value:
                getNesList(res, 200, authToken, regionId)
                break;
              case localEnum.SINGLE_NES.value:
                getNes(res, 200, authToken, regionId, nesId)
                break;
              case localEnum.SINGLE_NES_TIME.value:
                getNesTime(res, 200, authToken, regionId, nesId, sinceValue)
                break;
              default:
                errorFunction(res, localEnum.BAD_REQUEST, authToken)
            }
            /*End switch case*/
          } //end of manageReq
      } //ed if configuration is ok
    } //end if file is present
  });
}

function root(res, statusType, authToken) {
  res.writeHead(statusType, {
    'Content-Type': 'json'
  });
  res.end('{"_links": {"self": { "href": "/" },"regions": { "href": "/monitoring/regions", "templated": true }"host2hosts": { "href": "/monitoring/host2hosts", "templated": true }}}');
}

function errorFunction(res, errType, authToken) {
  res.writeHead(errType, {
    'Content-Type': 'json'
  });
  res.end('{"ERROR":' + errType + '}');
}

function getRegionList(res, statusType, authToken) {
  basicUsers = 0;
  trialUsers = 0;
  communityUsers = 0;
  totalUsers = 0;
  total_nb_users = 0; /*backward compatibility*/
  totalUserOrganizations = 0;
  totalCloudOrganizations = 0;
  total_nb_organizations = 0.0; /*backward compatibility*/
  total_nb_cores = 0.0;
  total_nb_cores_enabled = 0.0;
  total_nb_ram = 0.0;
  total_nb_disk = 0.0;
  total_nb_vm = 0.0;
  total_ip_used = 0;
  total_ip_allocated = 0;
  total_ip = 0;
  tmp_reg = [];
  var tmp_res = {
    "_links": {
      "self": {
        "href": ""
      }
    },
    "measures": [{}]
  };
  tmp_res._links.self.href = "/monitoring/regions";
  Entity.find({
    "_id.type": "region"
  }, function(err, regions) {
    if (regions && !(err)) {
      new Date().getTime();
      now = (Math.floor(Date.now() / 1000));
      for (i = 0; i < regions.length; i++) {
        //if(now-regions[i].modDate<cfgObj.regionTTL){
        if (regions[i]._id.id != "Berlin" && regions[i]._id.id != "Berlin2" && regions[i]._id.id != "Waterford" && regions[i]._id.id != "Stockholm" && regions[i]._id.id != "Stockholm2" &&
          regions[i]._id.id != "Mexico") {
          href_txt = "/monitoring/regions/" + regions[i]._id.id
          tmp_reg.push({
            "_links": {
              "self": {
                "href": href_txt
              }
            },
            "id": regions[i]._id.id
          })
          for (j = 0; j < regions[i].attrs.length; j++) {
            if (regions[i].attrs[j].name && regions[i].attrs[j].name.indexOf("coreEnabled") != -1)
              if (regions[i].attrs[j].value)
                if (now - regions[i].modDate < cfgObj.regionTTL) total_nb_cores_enabled += parseInt(regions[i].attrs[j].value);
            if (regions[i].attrs[j].name && regions[i].attrs[j].name.indexOf("ipUsed") != -1)
              if (regions[i].attrs[j].value)
                if (now - regions[i].modDate < cfgObj.regionTTL) total_ip_used += parseInt(regions[i].attrs[j].value);
            if (regions[i].attrs[j].name && regions[i].attrs[j].name.indexOf("ipAvailable") != -1)
              if (regions[i].attrs[j].value)
                if (now - regions[i].modDate < cfgObj.regionTTL) total_ip_allocated += parseInt(regions[i].attrs[j].value);
            if (regions[i].attrs[j].name && regions[i].attrs[j].name.indexOf("ipTot") != -1)
              if (regions[i].attrs[j].value)
                if (now - regions[i].modDate < cfgObj.regionTTL) total_ip += parseInt(regions[i].attrs[j].value);
            if (regions[i].attrs[j].name && regions[i].attrs[j].name.indexOf("coreTot") != -1)
              if (regions[i].attrs[j].value)
                if (now - regions[i].modDate < cfgObj.regionTTL) total_nb_cores += parseInt(regions[i].attrs[j].value);
            if (regions[i].attrs[j].name && regions[i].attrs[j].name.indexOf("ramTot") != -1)
              if (regions[i].attrs[j].value)
                if (now - regions[i].modDate < cfgObj.regionTTL) total_nb_ram += parseInt(regions[i].attrs[j].value);
            if (regions[i].attrs[j].name && regions[i].attrs[j].name.indexOf("hdTot") != -1)
              if (regions[i].attrs[j].value)
                if (now - regions[i].modDate < cfgObj.regionTTL) total_nb_disk += parseInt(regions[i].attrs[j].value);
            if (regions[i].attrs[j].name && regions[i].attrs[j].name.indexOf("vmList") != -1)
              if (regions[i].attrs[j].value) {
                var tList = regions[i].attrs[j].value;
                var ttL = tList.split(';');
                var numeroVM = 0;
                if (ttL.length && ttL.length) {
                  for (r = 0; r < ttL.length; r++) {
                    if (ttL[r].indexOf("ACTIVE") != -1) numeroVM++;
                  }
                }
                if (now - regions[i].modDate < cfgObj.regionTTL) total_nb_vm += numeroVM;
              }
          }
        } //end usable entry
        else {
          continue;
        }
      } //end region loop
      OAuth2 = oAuth.OAuth2;
      //ConsumerKey = '608';
      //ConsumerSecret = '';
      try {
        new Date().getTime();
        now = (Math.floor(Date.now() / 1000));
        sampleTimestamp = null;
        if (lifeToken != null) {
          var date = new Date(lifeToken.split(' ').join('T'))
          sampleTimestamp = (date.getTime() / 1000)
        }
        if (lifeToken == null || (sampleTimestamp != null && now > sampleTimestamp)) {
          request(optionsKP, function(errorTK, responseTK, bodyTK) {
            if (!errorTK && (responseTK.statusCode == 201 || responseTK.statusCode == 200)) {
              xToken = responseTK.headers['x-subject-token'];
              lifeToken = responseTK.body.token.expires_at;
              optionsIDM.headers['X-Auth-Token'] = xToken;
              request(optionsIDM, function(errorIDM, responseIDM, bodyIDM) {
                if (!errorIDM && (responseIDM.statusCode == 200)) {
                  info = JSON.parse(bodyIDM)
                  if (info.information.basicUsers) basicUsers = info.information.basicUsers;
                  if (info.information.trialUsers) trialUsers = info.information.trialUsers;
                  if (info.information.communityUsers) communityUsers = info.information.communityUsers;
                  if (info.information.totalUsers) totalUsers = info.information.totalUsers
                  if (info.information.totalCloudOrganizations) totalCloudOrganizations = info.information.totalCloudOrganizations;
                  if (info.information.totalUserOrganizations) totalUserOrganizations = info.information.totalUserOrganizations;
                  total_nb_users = basicUsers + trialUsers + communityUsers;
                  total_nb_organizations = totalUserOrganizations + totalCloudOrganizations;
                  if (tmp_reg.length > 0) {
                    _embedded = {}
                    _embedded.regions = tmp_reg;
                    tmp_res._embedded = _embedded;
                  }
                  tmp_res.basicUsers = basicUsers;
                  tmp_res.trialUsers = trialUsers;
                  tmp_res.communityUsers = communityUsers;
                  tmp_res.totalUsers = totalUsers;
                  tmp_res.total_nb_users = total_nb_users;
                  tmp_res.totalCloudOrganizations = totalCloudOrganizations;
                  tmp_res.totalUserOrganizations = totalUserOrganizations;
                  tmp_res.total_nb_organizations = total_nb_organizations;
                  tmp_res.total_nb_cores = total_nb_cores;
                  tmp_res.total_nb_cores_enabled = total_nb_cores_enabled;
                  tmp_res.total_nb_ram = total_nb_ram;
                  tmp_res.total_nb_disk = total_nb_disk;
                  tmp_res.total_nb_vm = total_nb_vm;
                  tmp_res.total_ip_assigned = total_ip_used;
                  tmp_res.total_ip_allocated = total_ip_allocated;
                  tmp_res.total_ip = total_ip
                  sendResponse(res, localEnum.OK.value, tmp_res);
                } else {
                  /*default answers*/
                  if (tmp_reg.length > 0) {
                    _embedded = {}
                    _embedded.regions = tmp_reg;
                    tmp_res._embedded = _embedded;
                  }
                  tmp_res.basicUsers = basicUsers;
                  tmp_res.trialUsers = trialUsers;
                  tmp_res.communityUsers = communityUsers;
                  tmp_res.totalUsers = totalUsers;
                  tmp_res.total_nb_users = total_nb_users;
                  tmp_res.totalCloudOrganizations = totalCloudOrganizations;
                  tmp_res.totalUserOrganizations = totalUserOrganizations;
                  tmp_res.total_nb_organizations = total_nb_organizations;
                  tmp_res.total_nb_cores = total_nb_cores;
                  tmp_res.total_nb_cores_enabled = total_nb_cores_enabled;
                  tmp_res.total_nb_ram = total_nb_ram;
                  tmp_res.total_nb_disk = total_nb_disk;
                  tmp_res.total_nb_vm = total_nb_vm;
                  tmp_res.total_ip_assigned = total_ip_used;
                  tmp_res.total_ip_allocated = total_ip_allocated;
                  tmp_res.total_ip = total_ip;
                  sendResponse(res, 200, tmp_res);
                }
              });
              //sendErrorResponse (res, localEnum.SERVER_ERROR.value, localEnum.SERVER_ERROR.key)
            } else {
              /*default answers*/
              if (tmp_reg.length > 0) {
                _embedded = {}
                _embedded.regions = tmp_reg;
                tmp_res._embedded = _embedded;
              }
              tmp_res.basicUsers = basicUsers;
              tmp_res.trialUsers = trialUsers;
              tmp_res.communityUsers = communityUsers;
              tmp_res.totalUsers = totalUsers;
              tmp_res.total_nb_users = total_nb_users;
              tmp_res.totalCloudOrganizations = totalCloudOrganizations;
              tmp_res.totalUserOrganizations = totalUserOrganizations;
              tmp_res.total_nb_organizations = total_nb_organizations;
              tmp_res.total_nb_cores = total_nb_cores;
              tmp_res.total_nb_cores_enabled = total_nb_cores_enabled;
              tmp_res.total_nb_ram = total_nb_ram;
              tmp_res.total_nb_disk = total_nb_disk;
              tmp_res.total_nb_vm = total_nb_vm;
              tmp_res.total_ip_assigned = total_ip_used;
              tmp_res.total_ip_allocated = total_ip_allocated;
              tmp_res.total_ip = total_ip;
              sendResponse(res, 200, tmp_res);
              //Problemi a riceve il token
              //sendErrorResponse (res, localEnum.SERVER_ERROR.value, localEnum.SERVER_ERROR.key)
            }
          }); //end of token request
        }
        ///I could implement a request without when the token is timed out
        else {
          optionsIDM.headers['X-Auth-Token'] = xToken;
          request(optionsIDM, function(errorIDM, responseIDM, bodyIDM) {
            if (!errorIDM && (responseIDM.statusCode == 200)) {
              info = JSON.parse(bodyIDM)
              if (info.information.basicUsers) basicUsers = info.information.basicUsers;
              if (info.information.trialUsers) trialUsers = info.information.trialUsers;
              if (info.information.communityUsers) communityUsers = info.information.communityUsers;
              if (info.information.totalUsers) totalUsers = info.information.totalUsers;
              if (info.information.totalCloudOrganizations) totalCloudOrganizations = info.information.totalCloudOrganizations;
              if (info.information.totalUserOrganizations) totalUserOrganizations = info.information.totalUserOrganizations;
              total_nb_users = basicUsers + trialUsers + communityUsers;
              total_nb_organizations = totalUserOrganizations + totalCloudOrganizations;
              if (tmp_reg.length > 0) {
                _embedded = {}
                _embedded.regions = tmp_reg;
                tmp_res._embedded = _embedded;
              }
              tmp_res.basicUsers = basicUsers;
              tmp_res.trialUsers = trialUsers;
              tmp_res.communityUsers = communityUsers;
              tmp_res.totalUsers = totalUsers;
              tmp_res.total_nb_users = basicUsers + trialUsers + communityUsers;
              tmp_res.totalCloudOrganizations = totalCloudOrganizations;
              tmp_res.totalUserOrganizations = totalUserOrganizations;
              tmp_res.total_nb_organizations = total_nb_organizations;
              tmp_res.total_nb_cores = total_nb_cores;
              tmp_res.total_nb_cores_enabled = total_nb_cores_enabled;
              tmp_res.total_nb_ram = total_nb_ram;
              tmp_res.total_nb_disk = total_nb_disk;
              tmp_res.total_nb_vm = total_nb_vm;
              tmp_res.total_ip_assigned = total_ip_used;
              tmp_res.total_ip_allocated = total_ip_allocated;
              tmp_res.total_ip = total_ip
              sendResponse(res, localEnum.OK.value, tmp_res);
              //console.log(info.information.totalUsers);
              //console.log(info.information.totalCloudOrganizations);
            } else {
              /*default answers*/
              if (tmp_reg.length > 0) {
                _embedded = {}
                _embedded.regions = tmp_reg;
                tmp_res._embedded = _embedded;
              }
              tmp_res.basicUsers = basicUsers;
              tmp_res.trialUsers = trialUsers;
              tmp_res.communityUsers = communityUsers;
              tmp_res.totalUsers = totalUsers;
              tmp_res.total_nb_users = total_nb_users;
              tmp_res.totalCloudOrganizations = totalCloudOrganizations;
              tmp_res.totalUserOrganizations = totalUserOrganizations;
              tmp_res.total_nb_organizations = total_nb_organizations;
              tmp_res.total_nb_cores = total_nb_cores;
              tmp_res.total_nb_cores_enabled = total_nb_cores_enabled;
              tmp_res.total_nb_ram = total_nb_ram;
              tmp_res.total_nb_disk = total_nb_disk;
              tmp_res.total_nb_vm = total_nb_vm;
              tmp_res.total_ip_assigned = total_ip_used;
              tmp_res.total_ip_allocated = total_ip_allocated;
              tmp_res.total_ip = total_ip;
              sendResponse(res, 200, tmp_res);
            }
          });
        }
      } catch (error) {
        /*default answers*/
        if (tmp_reg.length > 0) {
          _embedded = {}
          _embedded.regions = tmp_reg;
          tmp_res._embedded = _embedded;
        }
        tmp_res.basicUsers = basicUsers;
        tmp_res.trialUsers = trialUsers;
        tmp_res.communityUsers = communityUsers;
        tmp_res.totalUsers = totalUsers;
        tmp_res.total_nb_users = total_nb_users;
        tmp_res.totalCloudOrganizations = totalCloudOrganizations;
        tmp_res.totalUserOrganizations = totalUserOrganizations;
        tmp_res.total_nb_organizations = total_nb_organizations;
        tmp_res.total_nb_cores = total_nb_cores;
        tmp_res.total_nb_cores_enabled = total_nb_cores_enabled;
        tmp_res.total_nb_ram = total_nb_ram;
        tmp_res.total_nb_disk = total_nb_disk;
        tmp_res.total_nb_vm = total_nb_vm;
        tmp_res.total_ip_assigned = total_ip_used;
        tmp_res.total_ip_allocated = total_ip_allocated;
        tmp_res.total_ip = total_ip;
        sendResponse(res, 200, tmp_res);
      }
    } //end if entries are present
    else {
      sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
    }
  });
}

function getRegion(res, statusType, authToken, regionId) {
  var tmp_res = {
    "_links": {
      "self": {
        "href": ""
      }
    },
    "measures": []
  };
  tmp_res._links.self.href = "/monitoring/regions/" + regionId;
  Entity.findOne({
    $and: [{
      "_id.type": "region"
    }, {
      "_id.id": regionId
    }]
  }, function(err, region) {
    if (err) {
      sendErrorResponse(res, localEnum.SERVER_ERROR.value, localEnum.SERVER_ERROR.key)
    } else if (regionId == "Berlin") {
      sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
    } else if (region) {
      tmp_A = {};
      ram_allocation_ratio = '1.5';
      cpu_allocation_ratio = '16.0';
      tmp_res.id = '';
      tmp_res.name = '';
      tmp_res.country = '';
      tmp_res.latitude = '';
      tmp_res.longitude = '';
      tmp_res.nb_cores = '';
      tmp_res.nb_cores_enabled = '';
      tmp_res.nb_cores_used = '';
      tmp_res.nb_ram = '';
      nb_ram_used = 0;
      nb_disk_used = 0;
      tmp_res.nb_disk = '';
      tmp_res.nb_vm = '';
      //tmp_res.ipAssigned='';
      //tmp_res.ipAllocated='';
      //tmp_res.ipTot='';
      tmp_res.power_consumption = '';
      if (regionId && regionId != "Berlin") {
        tmp_res._links.hosts = {
          "href": "/monitoring/regions/" + regionId + "/hosts"
        };
        tmp_res.id = regionId;
        tmp_res.name = regionId;
      }
      new Date().getTime();
      now = (Math.floor(Date.now() / 1000));
      //if(now-region.modDate<cfgObj.regionTTL){
      if (1) {
        tmp_A.timestamp = new Date(region.modDate * 1000);
        //if ip info is not present -> return 0
        tmp_A.ipAssigned = 0;
        tmp_A.ipAllocated = 0;
        tmp_A.ipTot = 0;
        for (j = 0; j < region.attrs.length; j++) {
          if (region.attrs[j].name && region.attrs[j].name.indexOf("location") == 0)
            if (region.attrs[j].value) {
              tmp_res.country = region.attrs[j].value;
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("ipUsed") != -1)
            if (region.attrs[j].value) {
              tmp_A.ipAssigned = region.attrs[j].value;
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("ipAvailable") != -1)
            if (region.attrs[j].value) {
              tmp_A.ipAllocated = region.attrs[j].value;
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("ipTot") != -1)
            if (region.attrs[j].value) {
              tmp_A.ipTot = region.attrs[j].value;
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("cpu_allocation_ratio") != -1)
            if (region.attrs[j].value) {
              cpu_allocation_ratio = region.attrs[j].value;
              tmp_A.cpu_allocation_ratio = region.attrs[j].value;
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("ram_allocation_ratio") != -1)
            if (region.attrs[j].value) {
              ram_allocation_ratio = region.attrs[j].value;
              tmp_A.ram_allocation_ratio = region.attrs[j].value;
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("latitude") != -1)
            if (region.attrs[j].value) {
              tmp_res.latitude = region.attrs[j].value;
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("longitude") != -1)
            if (region.attrs[j].value) {
              tmp_res.longitude = region.attrs[j].value;
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("coreUsed") != -1)
            if (region.attrs[j].value) {
              tmp_res.nb_cores_used = parseInt(region.attrs[j].value);
              tmp_A.nb_cores_used = parseInt(region.attrs[j].value);
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("coreEnabled") != -1)
            if (region.attrs[j].value) {
              tmp_res.nb_cores_enabled = parseInt(region.attrs[j].value);
              tmp_A.nb_cores_enabled = parseInt(region.attrs[j].value);
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("coreTot") != -1)
            if (region.attrs[j].value) {
              tmp_res.nb_cores = parseInt(region.attrs[j].value);
              tmp_A.nb_cores = parseInt(region.attrs[j].value);
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("ramTot") != -1)
            if (region.attrs[j].value) {
              tmp_res.nb_ram = parseInt(region.attrs[j].value);
              tmp_A.nb_ram = parseInt(region.attrs[j].value);
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("ramUsed") != -1)
            if (region.attrs[j].value) {
              nb_ram_used = parseInt(region.attrs[j].value);
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("hdTot") != -1)
            if (region.attrs[j].value) {
              tmp_res.nb_disk = parseInt(region.attrs[j].value);
              tmp_A.nb_disk = parseInt(region.attrs[j].value);
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("hdUsed") != -1)
            if (region.attrs[j].value) {
              nb_disk_used = parseInt(region.attrs[j].value);
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("vmList") != -1)
            if (region.attrs[j].value) {
              var tList = region.attrs[j].value;
              var ttL = tList.split(';');
              var numeroVM = 0;
              if (ttL.length && ttL.length) {
                for (r = 0; r < ttL.length; r++) {
                  if (ttL[r].indexOf("ACTIVE") != -1) numeroVM++;
                }
              }
              tmp_res.nb_vm = numeroVM;
              tmp_A.nb_vm = numeroVM;
            }
        }
        if (tmp_A.nb_ram != 0) tmp_A.percRAMUsed = nb_ram_used / (tmp_A.nb_ram * parseFloat(ram_allocation_ratio));
        else tmp_A.percRAMUsed = 0;
        if (tmp_A.nb_disk != 0) tmp_A.percDiskUsed = nb_disk_used / tmp_A.nb_disk;
        else tmp_A.percDiskUsed = 0;
        if (regionId != "Berlin") tmp_res.measures.push(tmp_A);
        sendResponse(res, localEnum.OK.value, tmp_res);
      } //end usable entry
      else {
        sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
      }
    } else {
      sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
    }
  }); //end find
}

function getRegionTime(res, statusType, authToken, regionId, sinceValue) {
  /*HADOOP needed*/
  tmp_res = {
    "_links": {
      "self": {
        "href": ""
      }
    },
    "measures": [{}]
  };
  tmp_res._links.self.href = "/monitoring/regions/" + regionId;
  Entity.findOne({
    $and: [{
      "_id.type": "region"
    }, {
      "_id.id": regionId
    }]
  }, function(err, region) {
    if (err) {
      sendErrorResponse(res, localEnum.SERVER_ERROR.value, localEnum.SERVER_ERROR.key)
    } else if (regionId == "Berlin") {
      sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
    } else if (region) {
      tmpMesArray = []
      tmp_res.id = '';
      tmp_res.name = '';
      tmp_res.country = '';
      tmp_res.latitude = '';
      tmp_res.longitude = '';
      ram_allocation_ratio = '1.5';
      cpu_allocation_ratio = '16.0';
      //tmp_res.nb_cores='';
      //tmp_res.nb_cores_enabled='';
      //tmp_res.nb_ram='';
      //tmp_res.nb_disk='';
      //tmp_res.nb_vm='';
      //tmp_res.power_consumption='';
      if (regionId) {
        tmp_res._links.hosts = {
          "href": "/monitoring/regions/" + regionId + "/hosts"
        };
        tmp_res.id = regionId;
        tmp_res.name = regionId;
      }
      new Date().getTime();
      now = (Math.floor(Date.now() / 1000));
      //if(now-region.modDate<cfgObj.regionTTL){
      if (1) {
        for (j = 0; j < region.attrs.length; j++) {
          if (region.attrs[j].name && region.attrs[j].name.indexOf("location") != -1)
            if (region.attrs[j].value) tmp_res.country = region.attrs[j].value;
          if (region.attrs[j].name && region.attrs[j].name.indexOf("latitude") != -1)
            if (region.attrs[j].value) tmp_res.latitude = region.attrs[j].value;
          if (region.attrs[j].name && region.attrs[j].name.indexOf("longitude") != -1)
            if (region.attrs[j].value) tmp_res.longitude = region.attrs[j].value;
          if (region.attrs[j].name && region.attrs[j].name.indexOf("cpu_allocation_ratio") != -1)
            if (region.attrs[j].value) {
              cpu_allocation_ratio = region.attrs[j].value;
            }
          if (region.attrs[j].name && region.attrs[j].name.indexOf("ram_allocation_ratio") != -1)
            if (region.attrs[j].value) {
              ram_allocation_ratio = region.attrs[j].value;
            }
        }
        /*acquire historical data*/
        queryString = 'select * from region where entityId="' + regionId + '" and UNIX_TIMESTAMP(timestampId)>=UNIX_TIMESTAMP("' + sinceValue + '");';
        connection.query(queryString, function(err, rows, fields) {
          if (err) {
            sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
          } else {
            for (var i in rows) {
              tmpMes = {}
              tmpMes.timestamp = rows[i].timestampId
              tmpMes.percRAMUsed = 0;
              //tmpMes.percCPULoad=0;
              tmpMes.percDiskUsed = 0
              tmpMes.nb_cores_enabled = 0;
              tmpMes.nb_ram = 0;
              tmpMes.nb_ram_used = 0
              ram_used = 0;
              tmpMes.nb_disk = 0;
              tmpMes.nb_disk_used = 0;
              tmpMes.nb_vm = 0;
              tmpMes.power_consumption = '';
              tmpMes.ram_allocation_ratio = '';
              tmpMes.cpu_allocation_ratio = '';
              if (rows[i].avg_core_enabled) tmpMes.nb_cores_enabled = rows[i].avg_core_enabled;
              if (rows[i].avg_core_tot) tmpMes.nb_cores_tot = rows[i].avg_core_tot;
              if (rows[i].avg_ram_used) tmpMes.nb_ram_used = rows[i].avg_ram_used;
              if (rows[i].avg_ram_tot) tmpMes.nb_ram = rows[i].avg_ram_tot;
              if (rows[i].avg_hd_used) tmpMes.nb_disk_used = rows[i].avg_hd_used;
              if (rows[i].avg_hd_tot) tmpMes.nb_disk = rows[i].avg_hd_tot;
              if (rows[i].avg_vm_tot) tmpMes.nb_vm = rows[i].avg_vm_tot;
              if (rows[i].avg_power_consumption) tmpMes.power_consumption = rows[i].avg_power_consumption;
              if (ram_allocation_ratio) tmpMes.ram_allocation_ratio = ram_allocation_ratio;
              if (cpu_allocation_ratio) tmpMes.cpu_allocation_ratio = cpu_allocation_ratio;
              if (tmpMes.nb_ram) tmpMes.percRAMUsed = (tmpMes.nb_ram_used) / (tmpMes.nb_ram * parseFloat(ram_allocation_ratio)) //it is normalized
              if (tmpMes.nb_disk) tmpMes.percDiskUsed = (tmpMes.nb_disk_used) / tmpMes.nb_disk //it is normalized
              tmpMesArray.push(tmpMes);
            }
            tmp_res.measures = tmpMesArray;
          }
          sendResponse(res, localEnum.OK.value, tmp_res);
        });
        /*end of historical data*/
        //sendResponse (res, localEnum.OK.value, tmp_res);
      } //end usable entry
      else {
        sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
      }
    } else {
      sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
    }
  }); //end find
}

function getHostList(res, statusType, authToken, regionId) {
  if (authToken) {
    app_id = 0;
    var access_token = authToken;
    var options = {
      hostname: IDMurl,
      port: '443',
      path: "/user/?access_token=" + access_token,
      method: "GET",
      headers: {
        'accept': 'application/json',
        'user-group': 'none'
      } //end of headers
    }; //end of option
    try {
      https.get(options, function(responseCloud) {
        responseCloud.on('error', function(error) {
          console.log(error)
          sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
        });
        responseCloud.on('data', function(data) {
          //UserJson = eval('(' + data + ')');
          try {
            UserJson = eval('(' + data + ')');
          } catch (err) {
            sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          }
          var actorId = ''
          actorIdArray = []
          organizations = [];
          if (UserJson == null) {
            //console.log("Application")
            //sendErrorResponse (res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
            organizations.push({
              id: localEnum.TRUSTED_APP,
              actorId: localEnum.TRUSTED_APP,
              displayName: 'TrustedApp',
              roles: []
            })
          } else if (UserJson) {
            if (UserJson.actorId) actorId = UserJson.actorId;
            if (UserJson.app_id) app_id = UserJson.app_id
            if (UserJson.organizations) organizations = UserJson.organizations;
            if (actorId) {
              actorIdArray.push(actorId);
            }
            //else{
            //  sendErrorResponse (res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
            //}
          }
          //console.log(organizations);
          orgArray = []
          infraName = []
          if (organizations) {
            //console.log(organizations)
            for (it = 0; it < organizations.length; it++) {
              if (organizations[it].actorId) {
                actorIdArray.push(organizations[it].actorId);
                orgArray.push(organizations[it].id);
                //se appartine alla lista degli IO
                if (IsIO([organizations[it].id])) infraName.push(organizations[it].displayName);
              } //if
            } //for
          } //if
          if (IsTRUSTED_APP(app_id) || IsAdmin(orgArray) || IsSLA(orgArray) || IsFedMan(orgArray)) {
            //console.log("ADMIN IN");
            Entity.find({
              $and: [{
                "_id.type": /host_c/
              }, {
                "_id.id": {
                  $regex: regionId + ":*"
                }
              }]
            }, function(err, host) {
              if (host && !(err)) {
                var tmp_res = {
                  "_links": {
                    "self": {
                      "href": ""
                    }
                  },
                  "hosts": []
                };
                tmp_res._links.self = {
                  "href": "/monitoring/regions/" + regionId + "/hosts"
                }
                new Date().getTime();
                now = (Math.floor(Date.now() / 1000));
                for (var tmp_h in host) {
                  if (host[tmp_h]) {
                    //console.log(host[tmp_h]._id.type)
                    var attrPckt = host[tmp_h].attrs
                    for (var at in attrPckt) {
                      if (attrPckt[at].name && attrPckt[at].name == 'hostname' && attrPckt[at].value != 'none' && attrPckt[at].value.length < 10) {
                        addThis = {
                          "_links": {
                            "self": {
                              "href": "/monitoring/regions/" + regionId + "/hosts/" + attrPckt[at].value
                            }
                          },
                          "id": attrPckt[at].value
                        }
                        tmp_res.hosts.push(addThis);
                        break;
                      }
                    }
                  }
                }
                sendResponse(res, localEnum.OK.value, tmp_res);
              } else {
                sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
              }
            });
          }
          ///////////////ALTRO IF
          else if (IsDev(orgArray)) {
            Entity.find({
              $and: [{
                "_id.type": /host_c/
              }, {
                "_id.id": {
                  $regex: regionId + ":*"
                }
              }]
            }, function(err, host) {
              if (host && !(err)) {
                var tmp_res = {
                  "_links": {
                    "self": {
                      "href": ""
                    }
                  },
                  "hosts": []
                };
                tmp_res._links.self = {
                  "href": "/monitoring/regions/" + regionId + "/hosts"
                }
                new Date().getTime();
                now = (Math.floor(Date.now() / 1000));
                for (var tmp_h in host) {
                  if (host[tmp_h]) {
                    var attrPckt = host[tmp_h].attrs
                    if (host[tmp_h]._id.type == "host_compute") {
                      for (var at in attrPckt) {
                        if (attrPckt[at].name && attrPckt[at].name == 'hostname' && attrPckt[at].value != 'none' && attrPckt[at].value.length < 10) {
                          addThis = {
                            "_links": {
                              "self": {
                                "href": "/monitoring/regions/" + regionId + "/hosts/" + attrPckt[at].value
                              }
                            },
                            "id": attrPckt[at].value
                          }
                          tmp_res.hosts.push(addThis);
                          break;
                        }
                      } //end for
                    }
                  }
                }
                sendResponse(res, localEnum.OK.value, tmp_res);
              } else {
                sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
              }
            });
          } else if (IsIO(orgArray)) {
            Entity.find({
              $and: [{
                "_id.type": /host_c/
              }, {
                "_id.id": {
                  $regex: regionId + ":*"
                }
              }]
            }, function(err, host) {
              if (host && !(err)) {
                var tmp_res = {
                  "_links": {
                    "self": {
                      "href": ""
                    }
                  },
                  "hosts": []
                };
                tmp_res._links.self = {
                  "href": "/monitoring/regions/" + regionId + "/hosts"
                }
                new Date().getTime();
                now = (Math.floor(Date.now() / 1000));
                for (var tmp_h in host) {
                  if (host[tmp_h]) {
                    var attrPckt = host[tmp_h].attrs
                    if (host[tmp_h]._id.type == "host_compute" || (host[tmp_h]._id.type == "host_controller" && (infraName.indexOf((regionId)) != -1))) {
                      for (var at in attrPckt) {
                        if (attrPckt[at].name && attrPckt[at].name == 'hostname' && attrPckt[at].value != 'none' && attrPckt[at].value.length < 10) {
                          addThis = {
                            "_links": {
                              "self": {
                                "href": "/monitoring/regions/" + regionId + "/hosts/" + attrPckt[at].value
                              }
                            },
                            "id": attrPckt[at].value
                          }
                          tmp_res.hosts.push(addThis);
                          break;
                        }
                      } //end for
                    }
                  }
                }
                sendResponse(res, localEnum.OK.value, tmp_res);
              } else {
                sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
              }
            });
          } else {
            sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          } //unknown role
        });
      });
    } catch (err) {
      sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
    }
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  } else {
    sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
  }
}

function getHost(res, statusType, authToken, regionId, hostId) {
  //console.log(authToken)
  if (authToken) {
    app_id = 0;
    var access_token = authToken;
    var options = {
      hostname: IDMurl,
      port: '443',
      path: "/user/?access_token=" + access_token,
      method: "GET",
      headers: {
        'accept': 'application/json',
        'user-group': 'none'
      } //end of headers
    }; //end of option
    try {
      https.get(options, function(responseCloud) {
          responseCloud.on('error', function(error) {
            console.log(error)
            sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          });
          responseCloud.on('data', function(data) {
            //UserJson = eval('(' + data + ')');
            //console.log(UserJson)
            try {
              UserJson = eval('(' + data + ')');
            } catch (err) {
              sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
            }
            var actorId = ''
            actorIdArray = []
            organizations = [];
            if (UserJson == null) {
              //console.log("Application")
              //sendErrorResponse (res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
              organizations.push({
                id: localEnum.TRUSTED_APP,
                actorId: localEnum.TRUSTED_APP,
                displayName: 'TrustedApp',
                roles: []
              })
            } else if (UserJson) {
              actorId = UserJson.actorId;
              actorIdArray = []
              organizations = null;
              if (UserJson.app_id) app_id = UserJson.app_id
              if (UserJson.organizations) organizations = UserJson.organizations;
            }
            orgArray = []
            infraName = []
            if (organizations)
              for (it = 0; it < organizations.length; it++) {
                if (organizations[it].actorId) {
                  actorIdArray.push(organizations[it].actorId);
                  orgArray.push(organizations[it].id);
                  //se appartine alla lista degli IO
                  if (IsIO([organizations[it].id])) infraName.push(organizations[it].displayName);
                } //if
              } //for
            Entity.findOne({
              $and: [{
                "_id.type": /host_c/
              }, {
                "_id.id": {
                  $regex: regionId
                }
              }, {
                "attrs.value": hostId
              }]
            }, function(err, host) {
              if (host && !(err) && (IsAdmin(orgArray) || IsTRUSTED_APP(app_id) || IsFedMan(orgArray) || IsSLA(orgArray) || (IsDev(orgArray) && host._id.type == "host_compute") || (IsIO(
                orgArray)) && ((infraName.indexOf((regionId)) != -1) || host._id.type == "host_compute"))) {
                var tmp_res = {
                  "_links": {
                    "self": {
                      "href": ""
                    }
                  }
                };
                tmp_res._links.self = {
                  "href": "/monitoring/regions/" + regionId + "/hosts/" + hostId
                }
                tmp_res._links.services = {
                  "href": "/monitoring/regions/" + regionId + "/hosts/" + hostId + "/services"
                }
                new Date().getTime();
                now = (Math.floor(Date.now() / 1000));
                if (now - host.modDate < cfgObj.hostTTL) {
                  tmp_res.regionid = regionId;
                  tmp_res.hostid = hostId;
                  if (host._id.type == "host_controller") tmp_res.role = "controller";
                  if (host._id.type == "host_compute") tmp_res.role = "compute";
                  tmp_cpu = 0;
                  tmp_ram = 0;
                  tmp_disk = 0;
                  tmp_sys = 0;
                  tmp_owd = 0;
                  tmp_bwd = 0;
                  tmp_time = 0;
                  id_h = (host._id.id.split(":"))[1];
                  tmp_res.ipAddresses = [{
                    "ipAddress": id_h
                  }];
                  for (j = 0; j < host.attrs.length; j++) {
                    if (host.attrs[j].name && host.attrs[j].name.indexOf("ipAddresses") != -1) {
                      if (host.attrs[j].value) tmp_res.ipAddresses = host.attrs[j].value
                    } else if (host.attrs[j].name && host.attrs[j].name.indexOf("owd_endpoint_dest_default") != -1) {
                      if (host.attrs[j].value) tmp_res.owd_endpoint_dest_default = host.attrs[j].value
                    } else if (host.attrs[j].name && host.attrs[j].name.indexOf("bwd_endpoint_dest_default") != -1) {
                      if (host.attrs[j].value) tmp_res.bwd_endpoint_dest_default = host.attrs[j].value
                    } else if (host.attrs[j].name && host.attrs[j].name.indexOf("owd_frequency") != -1) {
                      if (host.attrs[j].value) tmp_res.owd_frequency = host.attrs[j].value
                    } else if (host.attrs[j].name && host.attrs[j].name.indexOf("bwd_frequency") != -1) {
                      if (host.attrs[j].value) tmp_res.bwd_frequency = host.attrs[j].value
                    } else if (host.attrs[j].name && host.attrs[j].name.indexOf("cpuLoadPct") != -1) {
                      if (host.attrs[j].value) tmp_cpu = host.attrs[j].value
                    } else if (host.attrs[j].name && host.attrs[j].name.indexOf("usedMemPct") != -1) {
                      if (host.attrs[j].value) tmp_ram = host.attrs[j].value
                    } else if (host.attrs[j].name && host.attrs[j].name.indexOf("freeSpacePct") != -1) {
                      if (host.attrs[j].value) tmp_disk = host.attrs[j].value
                    } else if (host.attrs[j].name && host.attrs[j].name.indexOf("_timestamp") != -1) {
                      if (host.attrs[j].value) tmp_time = new Date(Math.floor(host.attrs[j].value / 1000) * 1000)
                    } else if (host.attrs[j].name && host.attrs[j].name.indexOf("sysUptime") != -1) {
                      if (host.attrs[j].value) tmp_sys = host.attrs[j].value
                    } else if (host.attrs[j].name && host.attrs[j].name.indexOf("owd_status") != -1) {
                      if (host.attrs[j].value) tmp_owd = host.attrs[j].value
                    } else if (host.attrs[j].name && host.attrs[j].name.indexOf("bwd_status") != -1) {
                      if (host.attrs[j].value) tmp_bwd = host.attrs[j].value
                    }
                  }
                  tmp_res.measures = [{
                    "timestamp": tmp_time,
                    "percCPULoad": {
                      "value": tmp_cpu,
                      "description": "desc"
                    },
                    "percRAMUsed": {
                      "value": tmp_ram,
                      "description": "desc"
                    },
                    "percDiskUsed": {
                      "value": 100 - parseInt(tmp_disk),
                      "description": "desc"
                    },
                    "sysUptime": {
                      "value": tmp_sys,
                      "description": "desc"
                    },
                    "owd_status": {
                      "value": tmp_owd,
                      "description": "desc"
                    },
                    "bwd_status": {
                      "value": tmp_bwd,
                      "description": "desc"
                    }
                  }];
                }
                sendResponse(res, localEnum.OK.value, tmp_res);
              } else sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
            }); //Here the find one finishes
          }); //
          responseCloud.on('error', function(err) {
            sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          });
        }) //Cloud response
    } //end try
    catch (err) {
      console.log("Error")
      sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
    }
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  } else {
    sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
  }
}

function getHostTime(res, statusType, authToken, regionId, hostId, sinceValue) {
  if (authToken) {
    app_id = 0;
    var access_token = authToken;
    var options = {
      hostname: IDMurl,
      port: '443',
      path: "/user/?access_token=" + access_token,
      method: "GET",
      headers: {
        'accept': 'application/json',
        'user-group': 'none'
      } //end of headers
    }; //end of option
    try {
      https.get(options, function(responseCloud) {
        responseCloud.on('error', function(error) {
          //console.log(error)
          sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
        });
        responseCloud.on('data', function(data) {
          //UserJson = eval('(' + data + ')');
          try {
            UserJson = eval('(' + data + ')');
          } catch (err) {
            sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          }
          var actorId = ''
          actorIdArray = []
          organizations = [];
          if (UserJson) {
            actorId = UserJson.actorId;
            actorIdArray = []
            organizations = null;
            if (UserJson.app_id) app_id = UserJson.app_id
            if (UserJson.organizations) organizations = UserJson.organizations;
            if (actorId) actorIdArray.push(actorId);
          }
          orgArray = []
          infraName = []
          if (organizations)
            for (it = 0; it < organizations.length; it++) {
              if (organizations[it].actorId) {
                actorIdArray.push(organizations[it].actorId);
                orgArray.push(organizations[it].id);
                if (IsIO([organizations[it].id])) infraName.push(organizations[it].displayName);
              } //if
            } //for
          if (1) {
            //if(  (  IsAdmin(orgArray) ||  IsFedMan(orgArray) || IsSLA(orgArray)  || (IsIO (orgArray))  && (  (infraName.indexOf((regionId)) != -1)   ) ) ){
            var queryString = 'select * from host where host_id="' + hostId + '" and UNIX_TIMESTAMP(timestampId) >= UNIX_TIMESTAMP("' + sinceValue + '");'
            connection.query(queryString, function(err, rows, fields) {
              if (err) {
                sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
              } else if (rows && rows.length > 0) {
                //there are entries
                var tmp_res = {
                  "_links": {
                    "self": {
                      "href": ""
                    }
                  }
                };
                tmp_res._links.self = {
                  "href": "/monitoring/regions/" + regionId + "/hosts/" + hostId
                }
                tmp_res._links.services = {
                  "href": "/monitoring/regions/" + regionId + "/hosts/" + hostId + "/services"
                }
                tmp_res.regionid = regionId;
                tmp_res.hostid = hostId;
                tmp_res.role = "NaN";
                tmp_res.ipAddresses = [{
                  "ipAddress": "NaN"
                }]
                tmp_res.owd_endpoint_dest_default = "NaN",
                  tmp_res.bwd_endpoint_dest_default = "NaN",
                  tmp_res.owd_frequency = "NaN",
                  tmp_res.bwd_frequency = "NaN",
                  tmp_res.measures = [];
                counter = 0;
                for (var t_h in rows) {
                  if (counter == 0 && rows[t_h] && (( /* (IsTRUSTED_APP(orgArray) && rows[t_h].role=="compute")*/ IsTRUSTED_APP(app_id) || IsAdmin(orgArray) || IsFedMan(orgArray) ||
                    IsSLA(orgArray) || (IsDev(orgArray) && rows[t_h].role == "compute") || (IsIO(orgArray)) && ((infraName.indexOf((regionId)) != -1) || rows[t_h].role == "compute")
                  ))) {
                    counter = 1;
                    //console.log("OK rows")
                    tmp_res.role = rows[t_h].role;
                    tmp_res.ipAddresses[0]['ipAddress'] = rows[t_h].host_name
                  }
                  var tmp_entry = {
                      "timestamp": "NaN",
                      "percCPULoad": {
                        "value": "NaN",
                        "description": "desc"
                      },
                      "percRAMUsed": {
                        "value": "NaN",
                        "description": "desc"
                      },
                      "percDiskUsed": {
                        "value": "NaN",
                        "description": "desc"
                      },
                      "sysUptime": {
                        "value": "NaN",
                        "description": "desc"
                      },
                      "owd_status": {
                        "value": "NaN",
                        "description": "desc"
                      },
                      "bwd_status": {
                        "value": "NaN",
                        "description": "desc"
                      },
                      "sysUptime": {
                        "value": "NaN",
                        "description": "desc"
                      }
                    }
                    //console.log(rows[t_h]);
                  if (rows[t_h].timestampId) tmp_entry.timestamp = rows[t_h].timestampId
                  if (rows[t_h].avg_usedMemPct) tmp_entry.percRAMUsed.value = rows[t_h].avg_usedMemPct
                  if (rows[t_h].avg_freeSpacePct) tmp_entry.percDiskUsed.value = (100 - parseFloat(rows[t_h].avg_freeSpacePct)).toFixed(2);
                  if (rows[t_h].avg_cpuLoadPct) tmp_entry.percCPULoad.value = rows[t_h].avg_cpuLoadPct
                  if (rows[t_h].sysUptime) tmp_entry.sysUptime.value = (rows[t_h].sysUptime);
                  tmp_res.measures.push(tmp_entry);
                  // }
                } //end for
                sendResponse(res, localEnum.OK.value, tmp_res);
              } else {
                //there are not entries in the DB
                sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
              }
            }); //end of query
            ///////////////// }
            //else sendErrorResponse (res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key)
          } //if organizations
          else sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
        }); //onData
        responseCloud.on('error', function(err) {
          sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
        }); //onError
      }); //Cloud response
    } //end try
    catch (err) {
      sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
    }
  } //end if
  else {
    sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
  }
}

function getVmList(res, statusType, authToken, regionId) {
  app_id = 0;
  if (authToken) {
    var access_token = authToken;;
    //console.log(authToken)
    //console.log(part)
    //console.log(originaldata)
    //console.log(access_token)
    var options = {
      hostname: IDMurl,
      port: '443',
      path: "/user/?access_token=" + access_token,
      method: "GET",
      headers: {
        'accept': 'application/json',
        'user-group': 'none'
      } //end of headers
    }; //end of option
    try {
      https.get(options, function(responseCloud) {
        responseCloud.on('error', function(error) {
          //console.log(error)
          sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
        });
        responseCloud.on('data', function(data) {
          //sendErrorResponse (res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          /*********/
          new Date().getTime();
          now = (Math.floor(Date.now() / 1000));
          var tmp_res = {
            "_links": {
              "self": {
                "href": ""
              }
            },
            "measures": [{}]
          };
          vms = [];
          //UserJson = eval('(' + data + ')');
          try {
            UserJson = eval('(' + data + ')');
          } catch (err) {
            sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          }
          //console.log(UserJson)
          var actorIdArray = []
          var actorId = ''
          var orgArray = []
          var infraName = []
          if (UserJson == null) sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          else {
            if (UserJson.app_id) {
              app_id = UserJson.app_id
            }
            actorId = UserJson.actorId;
            organizations = UserJson.organizations;
            //nolonger used
            if (organizations) {
              for (it = 0; it < organizations.length; it++) {
                if (organizations[it].actorId) {
                  actorIdArray.push(organizations[it].actorId);
                } //endif
              } //end for organization
            } //endif present org
            if (organizations) {
              for (it = 0; it < organizations.length; it++) {
                if (organizations[it].actorId) {
                  actorIdArray.push(organizations[it].actorId);
                  orgArray.push(organizations[it].id);
                  if (IsIO([organizations[it].id])) infraName.push(organizations[it].displayName);
                } //if
              } //for
            }
          }
          var roles = null
            //console.log(actorIdArray)
          if (UserJson) roles = UserJson.roles;
          rolesArray = [];
          if (1) {
            if (roles)
              for (ir = 0; ir < roles.length; ir++) {
                if (roles[ir].id) {
                  rolesArray.push(roles[ir].id);
                } //endif
              }
            if (IsTRUSTED_APP(app_id) || IsAdmin(orgArray) || IsFedMan(orgArray) || IsSLA(orgArray) || (IsIO(orgArray) && infraName.indexOf(regionId))) {
              //( IsSLA(orgArray) || (IsDev(orgArray) && rows[t_h].role=="compute"  ) || (IsIO (orgArray))  && (  (infraName.indexOf((regionId)) != -1) || rows[t_h].role=="compute"   ) ) )
              //if(rolesArray.indexOf(localEnum.ADMIN.value) != -1 || rolesArray.indexOf(localEnum.FED_MAN.value) != -1 ||  ){
              /*******************************************************/
              /********************admin IN***************************/
              /*******************************************************/
              var filter = '___'
              if (IsTRUSTED_APP(app_id) || IsAdmin(orgArray) || IsFedMan(orgArray) || IsSLA(orgArray) || IsIO(orgArray) && infraName.indexOf(regionId)) filter = regionId
                //console.log('admin or Fed Man IN');
              Entity.find({
                $and: [{
                  "_id.type": "vm"
                }, {
                  "_id.id": {
                    $regex: filter
                  }
                }]
              }, function(err, vmx) {
                //Entity.find({"_id.type": "vm" } ,function (err, vmx){
                var tmp_vm = {}
                if (vmx) {
                  for (l = 0; l < vmx.length; l++) {
                    if (now - vmx[l].modDate < cfgObj.vmTTL) {
                      region_id = (vmx[l]._id.id).split(':')[0];
                      id_id = (vmx[l]._id.id).split(':')[1];
                      //vmList.forEach(function(entry) {
                      //console.log(entry[0]+" vs "+ip_id)
                      tmp_vm = {
                        "_links": {
                          "self": {
                            "href": "/monitoring/regions/" + region_id + "/vms/" + id_id
                          }
                        },
                        "id": id_id
                      };
                      vms.push(tmp_vm);
                      //});//end for each
                    } else continue;
                  } //endfor
                }
                tmp_res.vms = vms;
                sendResponse(res, localEnum.OK.value, tmp_res);
              }); //End find
            } else if (IsDev(orgArray)) {
              /*******************************************************/
              /*********************Drveloper IN**********************/
              /*******************************************************/
              //console.log('Developer IN');
              Entity.findOne({
                $and: [{
                  "_id.type": "region"
                }, {
                  "_id.id": regionId
                }]
              }, function(err, region) {
                if (err) {
                  sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                } else if (region && now - region.modDate < cfgObj.regionTTL) {
                  tmp_res._links.self.href = "/monitoring/regions/" + regionId + "/vms"
                  var vmList = [];
                  if (region)
                    for (i = 0; i < region.attrs.length; i++) {
                      if (region.attrs[i].name.indexOf("vmList") != -1) {
                        if (region.attrs[i].value != NaN && region.attrs[i].value.length > 0) {
                          tmpVmList = region.attrs[i].value.split(";")
                          for (j = 0; j < tmpVmList.length; j++) {
                            if (tmpVmList[j].split(",").length > 1) {
                              compareID = parseInt((tmpVmList[j].split(","))[8]);
                              if (actorIdArray.indexOf(compareID) > -1) {
                                vmList.push(tmpVmList[j].split(","));
                              } //endif actorIdArray
                            } //endif tmpVmList
                          } //endfor
                          Entity.find({
                            $and: [{
                              "_id.type": "vm"
                            }, {
                              "_id.id": {
                                $regex: regionId + ".*"
                              }
                            }]
                          }, function(err, vmx) {
                            if (vmx) {
                              for (l = 0; l < vmx.length; l++) {
                                if (now - vmx[l].modDate < cfgObj.vmTTL) {
                                  ip_id = (vmx[l]._id.id).split(':')[1];
                                  vmList.forEach(function(entry) {
                                    //console.log(entry[0]+" vs "+ip_id)
                                    if (entry[0].indexOf(ip_id) != -1) {
                                      tmp_vm = {};
                                      //id={};links={};self={};self.href=url_parts.pathname+'/'+ip_id;links.self=self;id=ip_id;tmp_vm._links=links;tmp_vm.id=id;
                                      tmp_vm = {
                                        "_links": {
                                          "self": {
                                            "href": "/monitoring/regions/" + regionId + "/vms/" + ip_id
                                          }
                                        },
                                        "id": ip_id
                                      };
                                      vms.push(tmp_vm);
                                    } //endif
                                  }); //end for each
                                } else continue;
                              } //endfor
                            } //endif vmx
                            tmp_res.vms = vms;
                            sendResponse(res, localEnum.OK.value, tmp_res);
                          }); //End find
                        } //if
                      } //if
                    } //for
                    //console.log(vms)
                } //elseif
                else {
                  sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                } //endelse
              }); //end finfOne
            } //End of developer case
            else {
              sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
            }
          } //if roles
        });
      });
    } catch (err) {
      sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
    }
  } //end if
  else {
    sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
  }
}

function getVm(res, statusType, authToken, regionId, vmId) {
  if (authToken) {
    access_token = authToken
    app_id = 0;
    var options = {
      hostname: IDMurl,
      port: '443',
      path: "/user/?access_token=" + access_token,
      method: "GET",
      headers: {
        'accept': 'application/json',
        'user-group': 'none'
      } //end of headers
    }; //end of option
    try {
      https.get(options, function(responseCloud) {
        responseCloud.on('error', function(error) {
          console.log(error)
          sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
        });
        responseCloud.on('data', function(data) {
          /*********/
          var tmp_res = {
            "_links": {
              "self": {
                "href": ""
              }
            },
            "measures": [{}]
          };
          tmp_res._links.self = {
            "href": "/monitoring/regions/" + regionId + "/vms/" + vmId
          }
          tmp_res._links.services = {
            "href": "/monitoring/regions/" + regionId + "/vms/" + vmId + "/services"
          }
          actorIdArray = []
          try {
            UserJson = eval('(' + data + ')');
          } catch (err) {
            sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          }
          if (UserJson == null || UserJson.hasOwnProperty('error')) sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          actorId = UserJson.actorId;
          organizations = null;
          if (UserJson.organizations) organizations = UserJson.organizations;
          if (UserJson.app_id) app_id = UserJson.app_id;
          //if (actorId){
          //  actorIdArray.push(actorId);}
          //else{
          //  sendErrorResponse (res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          // }
          if (organizations) {
            for (it = 0; it < organizations.length; it++) {
              if (organizations[it].actorId) {
                actorIdArray.push(organizations[it].actorId);
              } //if
            } //for
          } //if
          orgArray = []
          infraName = []
          if (organizations) {
            for (it = 0; it < organizations.length; it++) {
              if (organizations[it].actorId) {
                actorIdArray.push(organizations[it].actorId);
                orgArray.push(organizations[it].id);
                if (IsIO([organizations[it].id])) infraName.push(organizations[it].displayName);
              } //if
            } //for
          }
          //console.log(actorIdArray)
          roles = UserJson.roles;
          rolesArray = [];
          if (roles) {
            for (ir = 0; ir < roles.length; ir++) {
              if (roles[ir].id) {
                rolesArray.push(roles[ir].id);
              } //endif
            }
            if (IsTRUSTED_APP(app_id) || IsAdmin(orgArray) || IsFedMan(orgArray) || IsSLA(orgArray) || (IsIO(orgArray) && infraName.indexOf(regionId))) {
              // if(rolesArray.indexOf(localEnum.ADMIN.value) != -1 || rolesArray.indexOf(localEnum.FED_MAN.value) != -1){
              /*******************************************************/
              /******************Admin/FedMan owner IN****************/
              /*******************************************************/
              //console.log("Admin/FedMan owner IN")
              //console.log(vmId)
              tmp_cpu = '';
              tmp_ram = '';
              tmp_disk = '';
              tmp_host_name = '';
              tmp_time = '';
              tmp_sys = '';
              Entity.findOne({
                $and: [{
                  "_id.type": "vm"
                }, {
                  "_id.id": {
                    $regex: regionId + ":"+ vmId
                  }
                }]
              }, function(err, vmValue) {
                tmp_time = '';
                tmp_cpu = '';
                tmp_ram = '';
                tmp_disk = '';
                tmp_sys = '';
                tmp_hostname = '';
                if (!Array.isArray(vmValue.attrs)) {
                  arr = valuesToArray(vmValue.attrs);
                  vmValue.attrs = arr;
                }
                if (vmValue) {
                  for (j = 0; j < vmValue.attrs.length; j++) {
                    if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("cpuLoadPct") != -1 && (vmValue.attrs[j].value)) {
                      if (vmValue.attrs[j].value >= 1) tmp_cpu = 100;
                      else tmp_cpu = (100 * vmValue.attrs[j].value);
                    } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("usedMemPct") != -1 && (vmValue.attrs[j].value)) {
                      tmp_ram = vmValue.attrs[j].value
                    } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("freeSpacePct") != -1 && (vmValue.attrs[j].value)) {
                      tmp_disk = vmValue.attrs[j].value
                    } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("host_name") != -1 && (vmValue.attrs[j].value)) {
                      tmp_host_name = String(vmValue.attrs[j].value)
                    } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("_timestamp") != -1 && (vmValue.attrs[j].value)) {
                      //tmp_time=vmValue.attrs[j].value
                      tmp_time = new Date(Math.floor(vmValue.attrs[j].value / 1000) * 1000)
                    } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("sysUptime") != -1 && (vmValue.attrs[j].value)) {
                      tmp_sys = vmValue.attrs[j].value
                    }
                  } //endfor
                  tmp_res.measures = [{
                    "timestamp": "" + tmp_time,
                    "percCPULoad": {
                      "value": tmp_cpu,
                      "description": "desc"
                    },
                    "percRAMUsed": {
                      "value": tmp_ram,
                      "description": "desc"
                    },
                    "percDiskUsed": {
                      "value": (100 - parseInt(tmp_disk)),
                      "description": "desc"
                    },
                    "hostName": {
                      "value": tmp_host_name,
                      "description": "desc"
                    },
                    "sysUptime": {
                      "value": tmp_sys,
                      "description": "desc"
                    }
                  }];
                  sendResponse(res, localEnum.OK.value, tmp_res);
                } //endif
                else {
                  sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                }
                if (err) {
                  sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                }
              });
            } else if (IsDev(orgArray)) {
              /*******************************************************/
              /***********************Developer IN********************/
              /*******************************************************/
              //console.log("Developer IN")
              Entity.findOne({
                $and: [{
                  "_id.type": "region"
                }, {
                  "_id.id": regionId
                }]
              }, function(err, region) {
                if (err) {
                  sendErrorResponse(res, localEnum.SERVER_ERROR.value, localEnum.SERVER_ERROR.key);
                } //error
                else if (region) {
                  var vmList = [];
                  for (i = 0; i < region.attrs.length; i++) {
                    if (region.attrs[i].name.indexOf("vmList") != -1) {
                      if (region.attrs[i].value && region.attrs[i].value.length > 0) {
                        tmpVmList = region.attrs[i].value.split(";")
                        if (tmpVmList && region.attrs[i].value.indexOf(vmId) != -1) {
                          for (j = 0; j < tmpVmList.length; j++) {
                            if (tmpVmList[j].split(",").length > 1) {
                              compareID = parseInt((tmpVmList[j].split(","))[8]);
                              if (actorIdArray.indexOf(compareID) > -1 && tmpVmList[j].indexOf(vmId) != -1) {
                                vmList.push(tmpVmList[j].split(","));
                                Entity.findOne({
                                  $and: [{
                                    "_id.type": "vm"
                                  }, {
                                    "_id.id": regionId + ':' + vmId
                                  }]
                                }, function(err, vmValue) {
                                  tmp_time = '';
                                  tmp_cpu = '';
                                  tmp_ram = '';
                                  tmp_disk = '';
                                  tmp_sys = '';
                                  if (!Array.isArray(vmValue.attrs)) {
                                    arr = valuesToArray(vmValue.attrs);
                                    vmValue.attrs = arr;
                                  }
                                  if (vmValue) {
                                    for (j = 0; j < vmValue.attrs.length; j++) {
                                      if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("cpuLoadPct") != -1 && vmValue.attrs[j].value) {
                                        if (vmValue.attrs[j].value >= 1) tmp_cpu = 100;
                                        else tmp_cpu = (100 * vmValue.attrs[j].value);
                                      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("usedMemPct") != -1 && vmValue.attrs[j].value) {
                                        tmp_ram = vmValue.attrs[j].value
                                      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("freeSpacePct") != -1 && vmValue.attrs[j].value) {
                                        tmp_disk = vmValue.attrs[j].value
                                      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("timestamp") != -1 && vmValue.attrs[j].value) {
                                        tmp_time = vmValue.attrs[j].value
                                      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("sysUptime") != -1 && vmValue.attrs[j].value) {
                                        tmp_sys = vmValue.attrs[j].value
                                      }
                                    } //endfor
                                    tmp_res.measures = [{
                                      "timestamp": tmp_time,
                                      "percCPULoad": {
                                        "value": tmp_cpu,
                                        "description": "desc"
                                      },
                                      "percRAMUsed": {
                                        "value": tmp_ram,
                                        "description": "desc"
                                      },
                                      "percDiskUsed": {
                                        "value": 100 - parseInt(tmp_disk),
                                        "description": "desc"
                                      },
                                      "sysUptime": {
                                        "value": tmp_sys,
                                        "description": "desc"
                                      }
                                    }];
                                    sendResponse(res, localEnum.OK.value, tmp_res);
                                  } //endif
                                  else {
                                    sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                                  }
                                  if (err) {
                                    sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                                  }
                                });
                              } //endif actorID
                            } //end if element
                          } //end for vmList element
                        } //end if
                        else {
                          sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                        }
                      } //end if vmList notNull
                    } //end if vmList
                  } //end for region attrs
                } else {
                  sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                }
              });
            } //end developer
            else sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
          }
          /*********/
        });
      });
    } catch (err) {
      sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
    }
  } //enfd if oauth
  else {
    sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
  }
}

function buildVmResource(vmValue) {
  var vmId = '';
  var tmp_time = '';
  var tmp_cpu = '';
  var tmp_ram = '';
  var tmp_disk = '';
  var tmp_sys = '';
  var tmp_hostname = '';
  if (!Array.isArray(vmValue.attrs)) {
    arr = valuesToArray(vmValue.attrs);
    vmValue.attrs = arr;
  }
  if (vmValue) {
    var id = vmValue._id.id.split(':');
    var regionId = id[0]
    vmId = id[1]
    for (j = 0; j < vmValue.attrs.length; j++) {
      if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("cpuLoadPct") != -1 && (vmValue.attrs[j].value)) {
        if (vmValue.attrs[j].value >= 1) tmp_cpu = 100;
        else tmp_cpu = (100 * vmValue.attrs[j].value);
      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("usedMemPct") != -1 && (vmValue.attrs[j].value)) {
        tmp_ram = vmValue.attrs[j].value
      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("freeSpacePct") != -1 && (vmValue.attrs[j].value)) {
        tmp_disk = vmValue.attrs[j].value
      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("host_name") != -1 && (vmValue.attrs[j].value)) {
        tmp_host_name = String(vmValue.attrs[j].value)
      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("_timestamp") != -1 && (vmValue.attrs[j].value)) {
        //tmp_time=vmValue.attrs[j].value
        tmp_time = new Date(Math.floor(vmValue.attrs[j].value / 1000) * 1000)
      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("sysUptime") != -1 && (vmValue.attrs[j].value)) {
        tmp_sys = vmValue.attrs[j].value
      }
    } //endfor
    var tmp_res = {
      "_links": {
        "self": {
          "href": ""
        }
      },
      "regionid": regionId,
      "vmid": vmId,
      "ipAddresses": [{}],
      "measures": [{}],
      "traps":[{
        "description":"NYI"
      }]
    };
    tmp_res._links.self = {
      "href": "/monitoring/regions/" + regionId + "/vms/" + vmId
    }
    tmp_res._links.services = {
      "href": "/monitoring/regions/" + regionId + "/vms/" + vmId + "/services"
    }
    tmp_res.measures = [{
      "timestamp": "" + tmp_time,
      "percCPULoad": {
        "value": tmp_cpu,
        "description": "desc"
      },
      "percRAMUsed": {
        "value": tmp_ram,
        "description": "desc"
      },
      "percDiskUsed": {
        "value": (100 - parseInt(tmp_disk)),
        "description": "desc"
      },
      "hostName": {
        "value": tmp_host_name,
        "description": "desc"
      },
      "sysUptime": {
        "value": tmp_sys,
        "description": "desc"
      }
    }];
    return tmp_res;
  }
  else {
    return null;
  }
}

function getVmsDetails(res, statusType, authToken, regionId) {
  if (authToken) {
    access_token = authToken
    app_id = 0;
    var options = {
      hostname: IDMurl,
      port: '443',
      path: "/user/?access_token=" + access_token,
      method: "GET",
      headers: {
        'accept': 'application/json',
        'user-group': 'none'
      } //end of headers
    }; //end of option
    try {
      https.get(options, function(responseCloud) {
        responseCloud.on('error', function(error) {
          console.log(error)
          sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
        });
        responseCloud.on('data', function(data) {
          /*********/
          var tmp_res = {
            "_links": {
              "self": {
                "href": ""
              }
            },
            vms: []
          };
          tmp_res._links.self = {
            "href": "/monitoring/regions/" + regionId + "/vmsdetails"
          }
          actorIdArray = []
          try {
            UserJson = eval('(' + data + ')');
          } catch (err) {
            sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          }
          if (UserJson == null || UserJson.hasOwnProperty('error')) sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          actorId = UserJson.actorId;
          organizations = null;
          if (UserJson.organizations) organizations = UserJson.organizations;
          if (UserJson.app_id) app_id = UserJson.app_id;
          //if (actorId){
          //  actorIdArray.push(actorId);}
          //else{
          //  sendErrorResponse (res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          // }
          if (organizations) {
            for (it = 0; it < organizations.length; it++) {
              if (organizations[it].actorId) {
                actorIdArray.push(organizations[it].actorId);
              } //if
            } //for
          } //if
          orgArray = []
          infraName = []
          if (organizations) {
            for (it = 0; it < organizations.length; it++) {
              if (organizations[it].actorId) {
                actorIdArray.push(organizations[it].actorId);
                orgArray.push(organizations[it].id);
                if (IsIO([organizations[it].id])) infraName.push(organizations[it].displayName);
              } //if
            } //for
          }
          //console.log(actorIdArray)
          roles = UserJson.roles;
          rolesArray = [];
          if (roles) {
            for (ir = 0; ir < roles.length; ir++) {
              if (roles[ir].id) {
                rolesArray.push(roles[ir].id);
              } //endif
            }
            if (IsTRUSTED_APP(app_id) || IsAdmin(orgArray) || IsFedMan(orgArray) || IsSLA(orgArray) || (IsIO(orgArray) && infraName.indexOf(regionId))) {
              // if(rolesArray.indexOf(localEnum.ADMIN.value) != -1 || rolesArray.indexOf(localEnum.FED_MAN.value) != -1){
              /*******************************************************/
              /******************Admin/FedMan owner IN****************/
              /*******************************************************/
              //console.log("Admin/FedMan owner IN")
              //console.log(vmId)
              tmp_cpu = '';
              tmp_ram = '';
              tmp_disk = '';
              tmp_host_name = '';
              tmp_time = '';
              tmp_sys = '';
              Entity.find({
                $and: [{
                  "_id.type": "vm"
                }, {
                  "_id.id": {
                    $regex: regionId
                  }
                }]
              }, function(err, vmList) {


                  vmList.forEach(function (vmValue) {
                    var vmResource = buildVmResource(vmValue);
                    // Push vm in list
                    tmp_res.vms.push(vmResource);
                  })
                sendResponse(res, localEnum.OK.value, tmp_res);
                // Return response
              });
            } else if (IsDev(orgArray)) {
              /*******************************************************/
              /***********************Developer IN********************/
              /*******************************************************/
              //console.log("Developer IN")
              Entity.findOne({
                $and: [{
                  "_id.type": "region"
                }, {
                  "_id.id": regionId
                }]
              }, function(err, region) {
                if (err) {
                  sendErrorResponse(res, localEnum.SERVER_ERROR.value, localEnum.SERVER_ERROR.key);
                } //error
                else if (region) {
                  var vmList = [];
                  for (i = 0; i < region.attrs.length; i++) {
                    if (region.attrs[i].name.indexOf("vmList") != -1) {
                      if (region.attrs[i].value && region.attrs[i].value.length > 0) {
                        tmpVmList = region.attrs[i].value.split(";")
                        if (tmpVmList && region.attrs[i].value.indexOf(vmId) != -1) {
                          for (j = 0; j < tmpVmList.length; j++) {
                            if (tmpVmList[j].split(",").length > 1) {
                              compareID = parseInt((tmpVmList[j].split(","))[8]);
                              if (actorIdArray.indexOf(compareID) > -1 && tmpVmList[j].indexOf(vmId) != -1) {
                                vmList.push(tmpVmList[j].split(","));
                                Entity.findOne({
                                  $and: [{
                                    "_id.type": "vm"
                                  }, {
                                    "_id.id": regionId + ':' + vmId
                                  }]
                                }, function(err, vmValue) {
                                  tmp_time = '';
                                  tmp_cpu = '';
                                  tmp_ram = '';
                                  tmp_disk = '';
                                  tmp_sys = '';
                                  if (!Array.isArray(vmValue.attrs)) {
                                    arr = valuesToArray(vmValue.attrs);
                                    vmValue.attrs = arr;
                                  }
                                  if (vmValue) {
                                    for (j = 0; j < vmValue.attrs.length; j++) {
                                      if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("cpuLoadPct") != -1 && vmValue.attrs[j].value) {
                                        if (vmValue.attrs[j].value >= 1) tmp_cpu = 100;
                                        else tmp_cpu = (100 * vmValue.attrs[j].value);
                                      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("usedMemPct") != -1 && vmValue.attrs[j].value) {
                                        tmp_ram = vmValue.attrs[j].value
                                      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("freeSpacePct") != -1 && vmValue.attrs[j].value) {
                                        tmp_disk = vmValue.attrs[j].value
                                      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("timestamp") != -1 && vmValue.attrs[j].value) {
                                        tmp_time = vmValue.attrs[j].value
                                      } else if (vmValue.attrs[j].name && vmValue.attrs[j].name.indexOf("sysUptime") != -1 && vmValue.attrs[j].value) {
                                        tmp_sys = vmValue.attrs[j].value
                                      }
                                    } //endfor
                                    tmp_res.measures = [{
                                      "timestamp": tmp_time,
                                      "percCPULoad": {
                                        "value": tmp_cpu,
                                        "description": "desc"
                                      },
                                      "percRAMUsed": {
                                        "value": tmp_ram,
                                        "description": "desc"
                                      },
                                      "percDiskUsed": {
                                        "value": 100 - parseInt(tmp_disk),
                                        "description": "desc"
                                      },
                                      "sysUptime": {
                                        "value": tmp_sys,
                                        "description": "desc"
                                      }
                                    }];
                                    sendResponse(res, localEnum.OK.value, tmp_res);
                                  } //endif
                                  else {
                                    sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                                  }
                                  if (err) {
                                    sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                                  }
                                });
                              } //endif actorID
                            } //end if element
                          } //end for vmList element
                        } //end if
                        else {
                          sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                        }
                      } //end if vmList notNull
                    } //end if vmList
                  } //end for region attrs
                } else {
                  sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                }
              });
            } //end developer
            else sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
          }
          /*********/
        });
      });
    } catch (err) {
      sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
    }
  } //enfd if oauth
  else {
    sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
  }
}

function getVmTime(res, statusType, authToken, regionId, vmId, sinceValue) {
  /*HADOOP needed*/
  if (authToken) {
    access_token = authToken;
    app_id = 0;
    var options = {
      hostname: IDMurl,
      port: '443',
      path: "/user/?access_token=" + access_token,
      method: "GET",
      headers: {
        'accept': 'application/json',
        'user-group': 'none'
      } //end of headers
    }; //end of option
    try {
      https.get(options, function(responseCloud) {
        /*Error in order ro retrieve the user's info*/
        responseCloud.on('error', function(error) {
          sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
        });
        /* When response with data*/
        responseCloud.on('data', function(data) {
          if (IsJsonString(data)) {
            var tmp_res = {
              "_links": {
                "self": {
                  "href": ""
                }
              },
              "measures": [{}]
            };
            tmp_res._links.self = {
              "href": "/monitoring/regions/" + regionId + "/vms/" + vmId
            }
            tmp_res._links.services = {
              "href": "/monitoring/regions/" + regionId + "/vms/" + vmId + "/services"
            }
            actorIdArray = []
              //UserJson = eval('(' + data + ')');
            try {
              UserJson = eval('(' + data + ')');
            } catch (err) {
              sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
            }
            if (UserJson == null) sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
            actorId = UserJson.actorId;
            organizations = null;
            if (UserJson.organizations) {
              organizations = UserJson.organizations;
            }
            if (UserJson.app_id) {
              app_id = UserJson.app_id;
            }
            if (actorId) {
              actorIdArray.push(actorId);
            }
            //else{ sendErrorResponse (res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);  }
            if (organizations) {
              for (it = 0; it < organizations.length; it++) {
                if (organizations[it].actorId) {
                  actorIdArray.push(organizations[it].actorId);
                } //if
              } //for
            } //if
            orgArray = []
            infraName = []
            if (organizations) {
              for (it = 0; it < organizations.length; it++) {
                if (organizations[it].actorId) {
                  actorIdArray.push(organizations[it].actorId);
                  orgArray.push(organizations[it].id);
                  if (IsIO([organizations[it].id])) infraName.push(organizations[it].displayName);
                } //if
              } //for
            } //end if org
            //console.log(actorIdArray)
            roles = UserJson.roles;
            rolesArray = [];
            if (1) {
              if (roles)
                for (ir = 0; ir < roles.length; ir++) {
                  if (roles[ir].id) {
                    rolesArray.push(roles[ir].id);
                  } //endif
                }
              if (IsTRUSTED_APP(app_id) || IsAdmin(orgArray) || IsFedMan(orgArray) || IsSLA(orgArray) || (IsIO(orgArray) && infraName.indexOf(regionId))) {
                //if(rolesArray.indexOf(localEnum.ADMIN.value) != -1 || rolesArray.indexOf(localEnum.FED_MAN.value) != -1){
                /*******************************************************/
                /******************Admin/FedMan owner IN****************/
                /*******************************************************/
                //console.log("Admin/FedMan owner IN")
                var vmId_ = vmId.replace(/-/g, "_");
                queryString = 'select * from vm where entityId="' + regionId + '_' + vmId_ + '" and UNIX_TIMESTAMP(timestampId) >=  UNIX_TIMESTAMP("' + sinceValue +
                  '") order by timestampId';
                connection.query(queryString, function(err, rows, fields) {
                  ArrayVM = [];
                  if (err) {
                    sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                  } else {
                    tmp_res.redionid = regionId;
                    tmp_res.vmid = vmId;
                    //tmp_res.ipAddresses=ip;
                    for (var i in rows) {
                      var avl = "NaN"
                      var dsk = "NaN"
                      var cpu = "NaN"
                      var ram = "NaN"
                      if (rows[i].timestampId) avl = ((rows[i].availability / 60) * 100).toFixed(2);
                      if (rows[i].avg_freeSpacePct) dsk = 100 - rows[i].avg_freeSpacePct;
                      if (rows[i].avg_cpuLoadPct) cpu = rows[i].avg_cpuLoadPct;
                      if (rows[i].avg_usedMemPct) ram = rows[i].avg_usedMemPct;
                      ArrayVM.push({
                        "timestamp": rows[i].timestampId,
                        "percCPULoad": {
                          "value": cpu,
                          "description": "desc"
                        },
                        "percRAMUsed": {
                          "value": ram,
                          "description": "desc"
                        },
                        "percDiskUsed": {
                          "value": dsk,
                          "description": "desc"
                        },
                        "availability": {
                          "value": avl,
                          "description": "desc"
                        },
                        "sysUptime": {
                          "value": 0,
                          "description": "desc"
                        }
                      })
                    }
                    tmp_res.measures = ArrayVM
                    sendResponse(res, localEnum.OK.value, tmp_res);
                  }
                });
              } else if (IsDev(orgArray)) {
                //else if(rolesArray.indexOf(localEnum.DEV.value) != -1){
                /*******************************************************/
                /***********************Developer IN********************/
                /*******************************************************/
                //console.log("Developer IN")
                Entity.findOne({
                  $and: [{
                    "_id.type": "region"
                  }, {
                    "_id.id": regionId
                  }]
                }, function(err, region) {
                  if (err) {
                    sendErrorResponse(res, localEnum.SERVER_ERROR.value, localEnum.SERVER_ERROR.key);
                  } //error
                  else if (region) {
                    var vmList = [];
                    for (i = 0; i < region.attrs.length; i++) {
                      if (region.attrs[i].name.indexOf("vmList") != -1) {
                        if (region.attrs[i].value && region.attrs[i].value.length > 0) {
                          tmpVmList = region.attrs[i].value.split(";")
                          if (tmpVmList && region.attrs[i].value.indexOf(vmId) != -1) {
                            for (j = 0; j < tmpVmList.length; j++) {
                              if (tmpVmList[j].split(",").length > 1) {
                                compareID = parseInt((tmpVmList[j].split(","))[8]);
                                ip = ((tmpVmList[j].split(','))[10])
                                if (actorIdArray.indexOf(compareID) > -1 && tmpVmList[j].indexOf(vmId) != -1) {
                                  vmList.push(tmpVmList[j].split(","));
                                  //vmId="e3f7f1c4-47f9-4e52-9d3f-2ee58c80a7fb"
                                  var vmId_ = vmId.replace(/-/g, "_");
                                  queryString = 'select * from vm where entityId="' + regionId + '_' + vmId_ + '" and timestampId>="' + sinceValue + '" order by timestampId';
                                  connection.query(queryString, function(err, rows, fields) {
                                    ArrayVM = [];
                                    if (err) {
                                      sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                                    } else {
                                      tmp_res.redionid = regionId;
                                      tmp_res.vmid = vmId;
                                      tmp_res.ipAddresses = ip;
                                      for (var i in rows) {
                                        var avl = "NaN"
                                        var dsk = "NaN"
                                        var cpu = "NaN"
                                        var ram = "NaN"
                                        if (rows[i].timestampId) avl = ((rows[i].availability / 60) * 100).toFixed(2);
                                        if (rows[i].avg_freeSpacePct) dsk = 100 - rows[i].avg_freeSpacePct;
                                        if (rows[i].avg_cpuLoadPct) cpu = rows[i].avg_cpuLoadPct;
                                        if (rows[i].avg_usedMemPct) ram = rows[i].avg_usedMemPct;
                                        ArrayVM.push({
                                          "timestamp": rows[i].timestampId,
                                          "percCPULoad": {
                                            "value": cpu,
                                            "description": "desc"
                                          },
                                          "percRAMUsed": {
                                            "value": ram,
                                            "description": "desc"
                                          },
                                          "percDiskUsed": {
                                            "value": dsk,
                                            "description": "desc"
                                          },
                                          "availability": {
                                            "value": avl,
                                            "description": "desc"
                                          },
                                          "sysUptime": {
                                            "value": 0,
                                            "description": "desc"
                                          }
                                        })
                                      }
                                      tmp_res.measures = ArrayVM
                                      sendResponse(res, localEnum.OK.value, tmp_res);
                                    }
                                  })
                                } //endif actorID
                              } //end if element
                            } //end for vmLIst element
                          } else {
                            sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                          }
                        } //end if vmList notNull
                      } //end if vmList
                    } //end for region attrs
                  } else {
                    sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
                  }
                }); //endFindOne
              } else sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
            }
            /**************************************
         /*********USER without roles***********/
            /**************************************/
            else {
              sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
            } //end else
          } else {
            sendErrorResponse(res, localEnum.UNAUTHORIZED.value, localEnum.UNAUTHORIZED.key);
          }
        });
      }); //close  https.get
    } catch (err) {
      sendResponse(res, localEnum.NOT_IMPLEMENTED.value, {
        "Error": localEnum.NOT_IMPLEMENTED.key
      });
    } //close catch error
  } //end of IF authToken
}

function getH2HList(res, statusType, authToken) {
  Entity.find({
    "_id.type": "host2host"
  }, function(err, host2hosts) {
    if (host2hosts && !(err)) {
      var tmp_host2host = [];
      var tmp_res = {
        "_links": {
          "self": {
            "href": ""
          }
        },
        "measures": [{}]
      };
      tmp_res._links.self = {
        "href": "/monitoring/host2hosts"
      }
      new Date().getTime();
      var now = (Math.floor(Date.now() / 1000));
      for (i = 0; i < host2hosts.length; i++) {
        if (now - host2hosts[i].modDate < cfgObj.h2hTTL) {
          h2hId = host2hosts[i]._id.id;
          tmp_host2host.push({
            "_links": {
              "self": {
                "href": "/monitoring/host2hosts/" + h2hId
              }
            },
            "id": h2hId
          })
        } //and good host
      } //end for hosts
      if (tmp_host2host.length > 0) tmp_res.hosts = tmp_host2host;
      sendResponse(res, localEnum.OK.value, tmp_res);
    } else {
      sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key);
    }
  });
}

function getH2H(res, statusType, authToken, h2hId) {
  Entity.findOne({
    $and: [{
      "_id.type": "host2host"
    }, {
      "_id.id": h2hId
    }]
  }, function(err, h2h) {
    if (h2h && !(err)) {
      new Date().getTime();
      now = (Math.floor(Date.now() / 1000));
      if (now - h2h.modDate < cfgObj.h2hTTL) {
        var tmp_res = {
          "_links": {
            "self": {
              "href": ""
            }
          },
          "measures": [{}]
        };
        tmp_res._links.self = {
          "href": "/monitoring/host2hosts/" + h2h._id.id
        }
        if ((h2h._id.id).split(';')[0]) tmp_res.source = (h2h._id.id).split(';')[0];
        if ((h2h._id.id).split(';')[1]) tmp_res.dest = (h2h._id.id).split(';')[1];
        tmp_time = NaN;
        tmp_owd_m = NaN;
        tmp_owd_M = NaN;
        tmp_bw = NaN;
        tmp_sys = NaN;
        tmp_jit = NaN;
        tmp_pl = NaN;
        tmp_bw_av = NaN;
        tmp_interval = NaN;
        for (j = 0; j < h2h.attrs.length; j++) {
          if (h2h.attrs[j].name && h2h.attrs[j].name.indexOf("timestamp") != -1) {
            if (h2h.attrs[j].value) tmp_time = h2h.attrs[j].value
          } else if (h2h.attrs[j].name && h2h.attrs[j].name.indexOf("OWD_min") != -1) {
            if (h2h.attrs[j].value) tmp_owd_m = h2h.attrs[j].value
          } else if (h2h.attrs[j].name && h2h.attrs[j].name.indexOf("OWD_max") != -1) {
            if (h2h.attrs[j].value) tmp_owd_M = h2h.attrs[j].value
          } else if (h2h.attrs[j].name && h2h.attrs[j].name.indexOf("bandwidth_avg") != -1) {
            if (h2h.attrs[j].value) tmp_bw_av = h2h.attrs[j].value
          } else if (h2h.attrs[j].name && h2h.attrs[j].name.indexOf("bandwidth") != -1) {
            if (h2h.attrs[j].value) tmp_bw = h2h.attrs[j].value
          } else if (h2h.attrs[j].name && h2h.attrs[j].name.indexOf("sys_up") != -1) {
            if (h2h.attrs[j].value) tmp_sys = h2h.attrs[j].value
          } else if (h2h.attrs[j].name && h2h.attrs[j].name.indexOf("jitter") != -1) {
            if (h2h.attrs[j].value) tmp_jit = h2h.attrs[j].value
          } else if (h2h.attrs[j].name && h2h.attrs[j].name.indexOf("packet_loss") != -1) {
            if (h2h.attrs[j].value) tmp_pl = h2h.attrs[j].value
          } else if (h2h.attrs[j].name && h2h.attrs[j].name.indexOf("interval") != -1) {
            if (h2h.attrs[j].value) tmp_interval = h2h.attrs[j].value
          }
        } //end for attributes
        tmp_res.measures = [{
          "timestamp": tmp_time,
          "owd_min": {
            "value": tmp_owd_m,
            "description": "desc"
          },
          "owd_max": {
            "value": tmp_owd_M,
            "description": "desc"
          },
          "bandwidth": {
            "value": tmp_bw,
            "description": "desc"
          },
          "jitter": {
            "value": tmp_jit,
            "description": "desc"
          },
          "packet_loss": {
            "value": tmp_pl,
            "description": "desc"
          },
          "bandwidth_avg": {
            "value": tmp_bw_av,
            "description": "desc"
          },
          "interval": {
            "value": tmp_interval,
            "description": "desc"
          }
        }];
      }
      sendResponse(res, localEnum.OK.value, tmp_res);
    } else sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
  });
}

function getH2HTime(res, statusType, authToken, h2h, sinceValue) {
  /*HADOOP needed*/
  sendResponse(res, localEnum.NOT_IMPLEMENTED.value, {
    "Error": localEnum.NOT_IMPLEMENTED.key
  });
}

function getServiceRegion(res, statusType, authToken, regionId) {
  Entity.findOne({
    $and: [{
      "_id.type": "region"
    }, {
      "_id.id": regionId
    }]
  }, function(err1, regionInfo) {
    if (regionInfo && !(err1)) {
      time2print = "0000-00-00T00:00";
      if (regionInfo.modDate) {
        time2 = new Date(regionInfo.modDate * 1000)
        var yyyy = time2.getFullYear().toString();
        var mm = (time2.getMonth() + 1).toString(); // getMonth() is zero-based
        var dd = time2.getDate().toString();
        var hh = time2.getHours().toString();
        var m_m = time2.getMinutes().toString();
        time2print = yyyy + "-" + (mm[1] ? mm : "0" + mm[0]) + "-" + (dd[1] ? dd : "0" + dd[0]) + "T" + (hh[1] ? hh : "0" + hh[0]) + ":" + (m_m[1] ? m_m : "0" + m_m[0]) + ":00";
      }
      //console.log(regionInfo);
      //Entity.find({$and: [{"_id.type": "host_service" }, {"_id.id": '/'+regionId+':/'}] } ,function (err, services) {
      Entity.find({
        $and: [{
          "_id.type": "host_service"
        }, {
          "_id.id": {
            $regex: regionId + ':'
          }
        }]
      }, function(err, services) {
        //Entity.find({$and: [{"_id.type": "host_service" }, {"_id.id": regionId}] } ,function (err, services) {
        var tmp_res = {
          "_links": {
            "self": {
              "href": ""
            }
          },
          "measures": [{}]
        };
        tmp_res._links.self.href = "/monitoring/regions/" + regionId + "/services"
        novaActive = 0;
        novaTot = 0;
        cinderActive = 0;
        cinderTot = 0;
        quantumActive = 0;
        quantumTot = 0;
        qL3 = 0;
        qL3Status = 0;
        qDhcp = 0;
        qDhcpStatus = 0;
        glanceActive = 0;
        glanceTot = 0;
        servActive = 0;
        servTot = 0;
        kpActive = 0;
        kpTot = 0;
        sanActive = 0;
        sanTot = 0;
        sanTime = 0;
        if (services && !(err)) {
          new Date().getTime();
          now = (Math.floor(Date.now() / 1000));
          if (!Array.isArray(regionInfo.attrs)) {
            arr = valuesToArray(regionInfo.attrs);
            regionInfo.attrs = arr;
          }
          for (l in regionInfo.attrs) {
            if (regionInfo.attrs[l].name.indexOf("sanity") != -1) {
              if (regionInfo.attrs[l].name == "sanity_check_timestamp") {
                sanTime = (Math.floor(regionInfo.attrs[l].value / 1000));
              } else if (regionInfo.attrs[l].name == "sanity_status") {
                sanActive++
                tmp_val = 0
                if (regionInfo.attrs[l].value == "OK") tmp_val = 1
                if (regionInfo.attrs[l].value == "POK") tmp_val = 0.75
                if (regionInfo.attrs[l].value == "NOK") tmp_val = 0
                sanTot = sanTot + tmp_val;
              }
            } else continue;
          }
          for (i = 0; i < services.length; i++) {
            service = services[i];
            if (now - service.modDate < cfgObj.serviceTTL) {
              //if(1){
              tmpId = service._id.id;
              if ((service._id.id).split(':')[0]) region_id = (service._id.id).split(':')[0]
              if ((service._id.id).split(':')[1]) node_id = (service._id.id).split(':')[1]
              if ((service._id.id).split(':')[2]) service_id = (service._id.id).split(':')[2]
                /*starts to group info*/
              if (!Array.isArray(service.attrs)) {
                arr = valuesToArray(service.attrs);
                service.attrs = arr;
              }
              if (service_id && service.attrs[0].value) {
                servVal = service.attrs[0].value;
                servTot++;
                if (servVal > 0) {
                  servActive++;
                }
                /*Nova service*/
                if (service_id.indexOf("nova") != -1) {
                  novaTot++;
                  if (servVal > 0) novaActive++;
                }
                /*Cinder service*/
                else if (service_id.indexOf("cinder") != -1) {
                  cinderTot++;
                  if (servVal > 0) cinderActive++;
                }
                /*Glance*/
                else if (service_id.indexOf("glance") != -1) {
                  glanceTot++;
                  if (servVal > 0) glanceActive++;
                }
                /*Quantum service*/
                else if (service_id.indexOf("quantum") != -1) {
                  if (service_id.indexOf("quantum-l3-agent") != -1) {
                    if (qL3 == 0) quantumTot++;
                    qL3++;
                    if (servVal > 0) qL3Status = 1;
                  } else if (service_id.indexOf("quantum-dhcp-agent") != -1) {
                    if (qDhcp == 0) quantumTot++;
                    qDhcp++;
                    if (servVal > 0) qDhcpStatus = 1;
                  } else if ((service_id.indexOf("quantum-dhcp-agent") == -1) && (service_id.indexOf("quantum-l3-agent") == -1)) {
                    quantumTot++;
                    if (servVal > 0) quantumActive++;
                  }
                } else if (service_id.indexOf("neutron") != -1) {
                  quantumTot++;
                  if (servVal > 0) quantumActive++;
                } else if (service_id.indexOf("keystone-proxy") != -1) {
                  kpTot++;
                  if (servVal > 0) kpActive++;
                }
              }
            } else {
              continue;
            }
          } //endfor
          nova = "undefined";
          cinder = "undefined";
          quantum = "undefined";
          glance = "undefined";
          idm = "undefined";
          serv = "undefined";
          kp = "undefined";
          san = "undefined"
          nova_c = 0;
          cinder_c = 0;
          quantum_c = 0;
          glance_c = 0;
          kp_c = 0;
          serv_c = 0;
          san_c = 0;
          //console.log(sanTot)
          //console.log(sanActive)
          if (qDhcpStatus == 1) quantumActive++;
          if (qL3Status == 1) quantumActive++;
          if (novaActive && (novaTot && novaTot > 0)) {
            nova_c = novaActive / novaTot;
            if (novaActive / novaTot >= 0.9) nova = "green"
            else if (novaActive / novaTot < 0.99 && novaActive / novaTot >= 0.5) nova = "yellow"
            else if (novaActive / novaTot < 0.5 && novaActive / novaTot > 0) nova = "red"
          }
          if (cinderActive && (cinderTot && cinderTot > 0)) {
            cinder_c = cinderActive / cinderTot;
            if (cinderActive / cinderTot >= 0.99) cinder = "green"
            else if (cinderActive / cinderTot < 0.99 && cinderActive / cinderTot >= 0.5) cinder = "yellow"
            else if (cinderActive / cinderTot < 0.5 && cinderActive / cinderTot > 0) cinder = "red"
          }
          if (quantumActive && (quantumTot && quantumTot > 0)) {
            quantum_c = quantumActive / quantumTot;
            if (quantumActive / quantumTot >= 0.9) quantum = "green"
            else if (quantumActive / quantumTot < 0.9 && quantumActive / quantumTot >= 0.2) quantum = "yellow"
            else if (quantumActive / quantumTot < 0.2 && quantumActive / quantumTot > 0) quantum = "red"
          }
          if (glanceActive && (glanceTot && glanceTot > 0)) {
            glance_c = glanceActive / glanceTot;
            if (glanceActive / glanceTot >= 0.99) glance = "green"
            else if (glanceActive / glanceTot < 0.99 && glanceActive / glanceTot >= 0.5) glance = "yellow"
            else if (glanceActive / glanceTot < 0.5 && glanceActive / glanceTot > 0) glance = "red"
          }
          if (kpActive && (kpTot && kpTot > 0)) {
            kp_c = kpActive / kpTot;
            if (kpActive / kpTot >= 0.99) kp = "green"
            else if (kpActive / kpTot < 0.99 && kpActive / kpTot >= 0.5) kp = "yellow"
            else if (kpActive / kpTot < 0.5 && kpActive / kpTot > 0) kp = "red"
          }
          cnt = 0;
          tot = 0;
          if ( /*sanTime-service.modDate<cfgObj.serviceTTL &&*/ (sanActive == 0 || sanTot == 0)) san = "red";
          else if (sanActive && sanTot /*&& sanTime-service.modDate<cfgObj.serviceTTL*/ ) {
            san_c = sanTot / sanActive;
            if (sanTot / sanActive >= 0.9) {
              san = "green";
            } else if (sanTot / sanActive < 0.9 && sanTot / sanActive >= 0.5) {
              san = "yellow";
            } else if (sanTot / sanActive < 0.5) {
              san = "red";
            }
          }
          if (glance == "green") {
            cnt++;
            tot = tot + 2
          } else if (glance == "yellow") {
            cnt++;
            tot = tot + 1
          } else if (glance == "red") {
            cnt++;
          }
          if (cinder == "green") {
            cnt++;
            tot = tot + 2
          } else if (cinder == "yellow") {
            cnt++;
            tot = tot + 1
          } else if (cinder == "red") {
            cnt++;
          }
          if (quantum == "green") {
            cnt++;
            tot = tot + 2
          } else if (quantum == "yellow") {
            cnt++;
            tot = tot + 1
          } else if (quantum == "red") {
            cnt++;
          }
          if (nova == "green") {
            cnt++;
            tot = tot + 2
          } else if (nova == "yellow") {
            cnt++;
            tot = tot + 1
          } else if (nova == "red") {
            cnt++;
          }
          if (idm == "green") {
            cnt++;
            tot = tot + 2
          } else if (idm == "yellow") {
            cnt++;
            tot = tot + 1
          } else if (idm == "red") {
            cnt++;
          }
          if (kp == "green") {
            cnt++;
            tot = tot + 2
          } else if (kp == "yellow") {
            cnt++;
            tot = tot + 1
          } else if (kp == "red") {
            cnt++;
          }
          /*
      if (san=="green"){cnt++;tot=tot+2}
      else if (san=="yellow"){cnt++;tot=tot+1}
      else if (san=="red"){cnt++;}
      */
          if (cnt == 0) serv = "undefined"
          else {
            serv_c = tot / (cnt * 2);
            if (tot / (cnt * 2) >= 0.99) serv = "green"
            else if (tot / (cnt * 2) >= 0.5 && tot / (cnt * 2) < 0.99) serv = "yellow"
            else if (tot / (cnt * 2) >= 0 && tot / (cnt * 2) < 0.5) serv = "red"
          }
          /*implement check
           *
           *
           */
          kp = "green"
          var tmp_measures = [{
            "timestamp": time2print,
            "novaServiceStatus": {
              "value": nova,
              "value_clean": nova_c,
              "description": "desc"
            },
            "neutronServiceStatus": {
              "value": quantum,
              "value_clean": quantum_c,
              "description": "desc"
            },
            "cinderServiceStatus": {
              "value": cinder,
              "value_clean": cinder_c,
              "description": "desc"
            },
            "glanceServiceStatus": {
              "value": glance,
              "value_clean": glance_c,
              "description": "desc"
            },
            "KPServiceStatus": {
              "value": kp,
              "value_clean": kp_c,
              "description": "desc"
            },
            "OverallStatus": {
              "value": serv,
              "value_clean": serv_c,
              "description": "desc"
            },
            "FiHealthStatus": {
              "value": san,
              "value_clean": san_c,
              "description": "desc"
            }
          }];
          tmp_res.measures = (tmp_measures);
          //console.log(tmp_res);
          sendResponse(res, localEnum.OK.value, tmp_res);
        } else sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
      });
    } else sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
  }); //appena aggiunta
}

function getServiceRegionTime(res, statusType, authToken, regionId, sinceValue, aggregate) {
    /*HADOOP needed*/
    //console.log (aggregate);
    var tmp_res_t = {
      "_links": {
        "self": {
          "href": ""
        }
      },
      "measures": [{}]
    };;
    if (regionId) {
      var tmpMesArray = []
      tmp_res_t._links.hosts = {
        "href": "/monitoring/regions/" + regionId + "/services"
      };
      tmp_res_t.id = regionId;
      tmp_res_t.name = regionId;
      /*acquire historical data*/
      queryString = 'select * from host_service where region="' + regionId + '" and aggregationType="' + aggregate + '"  and UNIX_TIMESTAMP(timestampId) >= UNIX_TIMESTAMP("' + sinceValue +
        '") order by timestampId';
      //queryString = 'select entityId,region, entityType, serviceType, 'm' as aggregationType, timestampId, avg(avg_Uptime) as avg_Uptime from host_service where region="'+regionId+'" and aggregationType="d"  and UNIX_TIMESTAMP(timestampId) >= UNIX_TIMESTAMP("'+sinceValue+'") group by MONTH(timestampId) order by timestampId';
      connection.query(queryString, function(err, rows, fields) {
        if (err) {
          sendErrorResponse(res, localEnum.NOT_FOUND.value, localEnum.NOT_FOUND.key)
        } else {
          base_struct = {
            timestamp: 0,
            nova: 0,
            novaC: 0,
            neutron: 0,
            neutronC: 0,
            cinder: 0,
            cinderC: 0,
            glance: 0,
            glanceC: 0,
            kp: 0,
            kpC: 0,
            tot: 0,
            totC: 0
          }
          tmpMes = {};
          tmpMes.timestamp = null;
          tmpMes.novaServiceStatus = {
            "value": "undefined",
            "description": "description"
          };
          tmpMes.neutronServiceStatus = {
            "value": "undefined",
            "description": "description"
          };
          tmpMes.cinderServiceStatus = {
            "value": "undefined",
            "description": "description"
          };
          tmpMes.glanceServiceStatus = {
            "value": "undefined",
            "description": "description"
          };
          tmpMes.KPServiceStatus = {
            "value": "green",
            "description": "description"
          };
          tmpMes.FiHealthStatus = {
            "value": "undefined",
            "description": "description"
          };
          tmpMes.OverallStatus = {
            "value": "undefined",
            "description": "description"
          };
          arrayBuild = []
          for (var ii = 0; ii < rows.length; ii++) {
            i = rows[ii]
            present = 0;
            for (var jj = 0; jj < arrayBuild.length; jj++) {
              j = arrayBuild[jj]
              if ((new Date(arrayBuild[jj].timestamp).getTime() == new Date(rows[ii].timestampId).getTime())) {
                //aggiorna
                if (rows[ii].serviceType.indexOf("nova") != -1) {
                  arrayBuild[jj].nova += rows[ii].avg_Uptime;
                  arrayBuild[jj].novaC += 1;
                }
                if ( (rows[ii].serviceType.indexOf("quantum") != -1) || (rows[ii].serviceType.indexOf("neutron") != -1) ) {
                  arrayBuild[jj].neutron += rows[ii].avg_Uptime;
                  arrayBuild[jj].neutronC += 1;
                }
                if (rows[ii].serviceType.indexOf("cinder") != -1) {
                  arrayBuild[jj].cinder += rows[ii].avg_Uptime;
                  arrayBuild[jj].cinderC += 1;
                }
                if (rows[ii].serviceType.indexOf("glance") != -1) {
                  arrayBuild[jj].glance += rows[ii].avg_Uptime;
                  arrayBuild[jj].glanceC += 1;
                }
                if (rows[ii].serviceType.indexOf("sanity") != -1 /*&& rows[ii].avg_Uptime */ ) {
                  arrayBuild[jj].sanity = rows[ii].avg_Uptime;
                }
                present = 1;
                continue;
              }
            }
            if (present == 0) {
              t = {
                timestamp: new Date(rows[ii].timestampId),
                nova: 0,
                novaC: 0,
                neutron: 0,
                neutronC: 0,
                cinder: 0,
                cinderC: 0,
                glance: 0,
                glanceC: 0,
                kp: 0,
                kpC: 0,
                sanity: null
              };
              if (rows[ii].serviceType.indexOf("nova") != -1) {
                t.nova += rows[ii].avg_Uptime;
                t.novaC += 1;
              } else if ( (rows[ii].serviceType.indexOf("quantum") != -1) || (rows[ii].serviceType.indexOf("neutron") != -1) ) {
                t.neutron += rows[ii].avg_Uptime;
                t.neutronC += 1;
              } else if (rows[ii].serviceType.indexOf("cinder") != -1) {
                t.cinder += rows[ii].avg_Uptime;
                t.cinderC += 1;
              } else if (rows[ii].serviceType.indexOf("glance") != -1) {
                t.glance += rows[ii].avg_Uptime;
                t.glanceC += 1;
              } else if (rows[ii].serviceType.indexOf("sanity") != -1) {
                t.sanity = rows[ii].avg_Uptime;
              }
              arrayBuild.push(t);
            }
            //lastTimestamp=tmpMes.timestamp
            //tmpMesArray.push(tmpMes);
          }
          for (var f in arrayBuild) {
            var yyyy = arrayBuild[f].timestamp.getFullYear().toString();
            var mm = (arrayBuild[f].timestamp.getMonth() + 1).toString(); // getMonth() is zero-based
            var dd = arrayBuild[f].timestamp.getDate().toString();
            var hh = arrayBuild[f].timestamp.getHours().toString();
            data = yyyy + "-" + (mm[1] ? mm : "0" + mm[0]) + "-" + (dd[1] ? dd : "0" + dd[0]) + "T" + (hh[1] ? hh : "0" + hh[0] + ":00:00");
            tmpMes = {};
            tmpMes.timestamp = data;
            tmpMes.novaServiceStatus = {
              "value": "undefined",
              "value_clean": "undefined",
              "description": "description"
            };
            tmpMes.neutronServiceStatus = {
              "value": "undefined",
              "value_clean": "undefined",
              "description": "description"
            };
            tmpMes.cinderServiceStatus = {
              "value": "undefined",
              "value_clean": "undefined",
              "description": "description"
            };
            tmpMes.glanceServiceStatus = {
              "value": "undefined",
              "value_clean": "undefined",
              "description": "description"
            };
            //hardcoded part
            tmpMes.KPServiceStatus = {
              "value": "green",
              "value_clean": "undefined",
              "description": "description"
            };
            tmpMes.FiHealthStatus = {
              "value": "undefined",
              "value_clean": "undefined",
              "description": "description"
            };
            tmpMes.OverallStatus = {
              "value": "undefined",
              "value_clean": "undefined",
              "description": "description"
            };
            if (arrayBuild[f].novaC == 0) {
              tmpMes.novaServiceStatus.value = 0;
            }
            if (arrayBuild[f].novaC != 0) {
              tmpMes.novaServiceStatus.value = arrayBuild[f].nova / arrayBuild[f].novaC;
              if (arrayBuild[f].nova / arrayBuild[f].novaC >= 0.9) tmpMes.novaServiceStatus.value = "green"
              else if (arrayBuild[f].nova / arrayBuild[f].novaC >= 0.5 && arrayBuild[f].nova / arrayBuild[f].novaC < 0.9) tmpMes.novaServiceStatus.value = "yellow"
              else if (arrayBuild[f].nova / arrayBuild[f].novaC < 0.5) tmpMes.novaServiceStatus.value + "red"
            }
            if (arrayBuild[f].novaC == 0) {
              tmpMes.novaServiceStatus.value = "red";
              tmpMes.novaServiceStatus.value_clean = 0;
            }
            if (arrayBuild[f].novaC != 0) {
              tmpMes.novaServiceStatus.value_clean = arrayBuild[f].nova / arrayBuild[f].novaC;
              if (arrayBuild[f].nova / arrayBuild[f].novaC >= 0.9) tmpMes.novaServiceStatus.value = "green"
              else if (arrayBuild[f].nova / arrayBuild[f].novaC >= 0.5 && arrayBuild[f].nova / arrayBuild[f].novaC < 0.9) tmpMes.novaServiceStatus.value = "yellow"
              else if (arrayBuild[f].nova / arrayBuild[f].novaC < 0.5) tmpMes.novaServiceStatus.value = "red"
            }
            if (arrayBuild[f].neutronC == 0) {
              tmpMes.neutronServiceStatus.value = "red";
              tmpMes.neutronServiceStatus.value_clean = 0;
            }
            if (arrayBuild[f].neutronC != 0) {
              tmpMes.neutronServiceStatus.value_clean = arrayBuild[f].neutron / arrayBuild[f].neutronC;
              if (arrayBuild[f].neutron / arrayBuild[f].neutronC >= 0.9) tmpMes.neutronServiceStatus.value = "green"
              else if (arrayBuild[f].neutron / arrayBuild[f].neutronC >= 0.5 && arrayBuild[f].neutron / arrayBuild[f].neutronC < 0.9) tmpMes.neutronServiceStatus.value = "yellow"
              else if (arrayBuild[f].neutron / arrayBuild[f].neutronC < 0.5) tmpMes.neutronServiceStatus.value = "red"
            }
            if (arrayBuild[f].cinderC == 0) {
              tmpMes.cinderServiceStatus.value = "red";
              tmpMes.cinderServiceStatus.value_clean = 0;
            }
            if (arrayBuild[f].cinderC != 0) {
              tmpMes.cinderServiceStatus.value_clean = arrayBuild[f].cinder / arrayBuild[f].cinderC;
              if (arrayBuild[f].cinder / arrayBuild[f].cinderC >= 0.9) tmpMes.cinderServiceStatus.value = "green"
              else if (arrayBuild[f].cinder / arrayBuild[f].cinderC >= 0.5 && arrayBuild[f].cinder / arrayBuild[f].cinderC < 0.9) tmpMes.cinderServiceStatus.value = "yellow"
              else if (arrayBuild[f].cinder / arrayBuild[f].cinderC < 0.5) tmpMes.cinderServiceStatus.value = "red"
            }
            if (arrayBuild[f].glanceC == 0) {
              tmpMes.glanceServiceStatus.value = "red";
              tmpMes.glanceServiceStatus.value_clean = 0;
            }
            if (arrayBuild[f].glanceC != 0) {
              tmpMes.glanceServiceStatus.value_clean = arrayBuild[f].glance / arrayBuild[f].glanceC;
              if (arrayBuild[f].glance / arrayBuild[f].glanceC >= 0.9) tmpMes.glanceServiceStatus.value = "green"
              else if (arrayBuild[f].glance / arrayBuild[f].glanceC >= 0.5 && arrayBuild[f].glance / arrayBuild[f].glanceC < 0.9) tmpMes.glanceServiceStatus.value = "yellow"
              else if (arrayBuild[f].glance / arrayBuild[f].glanceC < 0.5) tmpMes.glanceServiceStatus.value = "red"
            }
            if (arrayBuild[f].sanity == null) {
              tmpMes.FiHealthStatus.value = "undefined"
              tmpMes.FiHealthStatus.value_clean = "undefined"
            } else {
              if (arrayBuild[f].sanity >= 0.9) {
                tmpMes.FiHealthStatus.value = "green";
                tmpMes.FiHealthStatus.value_clean = arrayBuild[f].sanity;
              } else if (arrayBuild[f].sanity >= 0.5 && arrayBuild[f].sanity < 0.9) {
                tmpMes.FiHealthStatus.value = "yellow";
                tmpMes.FiHealthStatus.value_clean = arrayBuild[f].sanity;
              } else if (arrayBuild[f].sanity < 0.5 && arrayBuild[f].sanity >= 0) {
                tmpMes.FiHealthStatus.value = "red";
                tmpMes.FiHealthStatus.value_clean = arrayBuild[f].sanity;
              }
            }
            denom = arrayBuild[f].novaC + arrayBuild[f].neutronC + arrayBuild[f].cinderC + arrayBuild[f].glanceC + 1;
            nom = arrayBuild[f].nova + arrayBuild[f].neutron + arrayBuild[f].cinder + arrayBuild[f].glance + 1;
            if (denom == 0) {
              tmpMes.OverallStatus.value = "red";
              tmpMes.OverallStatus.value_clean = 0;
            }
            if (denom != 0) {
              tmpMes.OverallStatus.value_clean = nom / denom;
              if ((nom / denom) >= 0.9) tmpMes.OverallStatus.value = "green"
              else if ((nom / denom) >= 0.5 && (nom / denom) < 0.9) tmpMes.OverallStatus.value = "yellow"
              else if ((nom / denom) < 0.5) tmpMes.OverallStatus.value = "red"
            }
            tmpMesArray.push(tmpMes)
          }
          //console.log (aggregate)
          /*fill empty days*/
          //dateTimestamp=(Math.floor(Date.now() / 1000));
          now = new Date()
          date = new Date(sinceValue.split(' ').join('T'))
          var yyyy = date.getFullYear().toString();
          var mm = (date.getMonth() + 1).toString(); // getMonth() is zero-based
          var dd = date.getDate().toString();
          var hh = date.getUTCHours().toString();
          //dataClean=yyyy +"-"+ (mm[1]?mm:"0"+mm[0]) +"-"+(dd[1]?dd:"0"+dd[0])+"T"+(hh[1]?hh:"0"+hh[0]+":00:00");
          if (aggregate == 'h') {
            dataClean = yyyy + "-" + (mm[1] ? mm : "0" + mm[0]) + "-" + (dd[1] ? dd : "0" + dd[0]) + "T" + (hh[1] ? hh : "0" + hh[0]);
            dataClean = dataClean + ":00"
          } else if (aggregate == 'd') dataClean = yyyy + "-" + (mm[1] ? mm : "0" + mm[0]) + "-" + (dd[1] ? dd : "0" + dd[0]) + "T00:00:00";
          else if (aggregate == 'm') dataClean = yyyy + "-" + (mm[1] ? mm : "0" + mm[0]) + "-01T00:00:00";
          dataC = new Date(dataClean);
          if (aggregate == "h") {
            //console.log ("hours...........")
            while (now > dataC) {
              equal = "NO"
              for (var pars in tmpMesArray) {
                if (tmpMesArray[pars].timestamp.split('T')[1].split(':').length == 1) {
                  tmpMesArray[pars].timestamp = tmpMesArray[pars].timestamp + ":00:00"
                } else if (tmpMesArray[pars].timestamp.split('T')[1].split(':').length == 2) tmpMesArray[pars].timestamp = tmpMesArray[pars].timestamp + ":00"
                  //console.log("empty")
                arrayDate = new Date(tmpMesArray[pars].timestamp);
                equal = "NO"
                if (arrayDate.getFullYear() == dataC.getFullYear() && arrayDate.getMonth() == dataC.getMonth() && arrayDate.getDate() == dataC.getDate() && arrayDate.getHours() == dataC.getHours()) {
                  equal = "SI"
                  break;
                }
              }
              if (equal == "NO" && (dataC.getFullYear() <= now.getFullYear() && dataC.getMonth() <= now.getMonth() && dataC.getDate() < now.getDate())) {
                var yyyy = dataC.getFullYear().toString();
                var mm = (dataC.getMonth() + 1).toString(); // getMonth() is zero-based
                var dd = dataC.getDate().toString();
                var hh = dataC.getHours().toString();
                dataToInsert = yyyy + "-" + (mm[1] ? mm : "0" + mm[0]) + "-" + (dd[1] ? dd : "0" + dd[0]) + "T" + (hh[1] ? hh : "0" + hh[0]) + ":00:00";
                tmpMes = {};
                tmpMes.timestamp = dataToInsert;
                tmpMes.novaServiceStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.neutronServiceStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.cinderServiceStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.glanceServiceStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.KPServiceStatus = {
                  "value": "green",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.FiHealthStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.OverallStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMesArray.push(tmpMes)
              }
              dataC.setHours(dataC.getHours() + 1)
            }
          } else if (aggregate == "d") {
            //console.log ("days...........")
            while (now > dataC) {
              equal = "NO"
              for (var pars in tmpMesArray) {
                arrayDate = new Date(tmpMesArray[pars].timestamp);
                equal = "NO"
                if (arrayDate.getFullYear() == dataC.getFullYear() && arrayDate.getMonth() == dataC.getMonth() && arrayDate.getDate() == dataC.getDate()) {
                  equal = "SI"
                  break;
                }
              }
              if (equal == "NO" && dataC.getDate() != now.getDate()) {
                var yyyy = dataC.getFullYear().toString();
                var mm = (dataC.getMonth() + 1).toString(); // getMonth() is zero-based
                var dd = dataC.getDate().toString();
                var hh = dataC.getHours().toString();
                dataToInsert = yyyy + "-" + (mm[1] ? mm : "0" + mm[0]) + "-" + (dd[1] ? dd : "0" + dd[0]) + "T00:00:00";
                tmpMes = {};
                tmpMes.timestamp = dataToInsert;
                tmpMes.novaServiceStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.neutronServiceStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.cinderServiceStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.glanceServiceStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.KPServiceStatus = {
                  "value": "green",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.FiHealthStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMes.OverallStatus = {
                  "value": "undefined",
                  "value_clean": "undefined",
                  "description": "description"
                };
                tmpMesArray.push(tmpMes)
              }
              dataC.setDate(dataC.getDate() + 1)
            }
          } else if (aggregate == "m") {
            while (now > dataC) {
              equal = "NO"
              for (pars in tmpMesArray) {
                arrayDate = new Date(tmpMesArray[pars].timestamp);
                equal = "NO"
                if (arrayDate.getFullYear() == dataC.getFullYear() && arrayDate.getMonth() == dataC.getMonth()) {
                  if (tmpMesArray[pars].timestamp == dataC) {
                    equal = "SI"
                    break;
                  }
                }
                //if (equal=="NO"){
                if (equal == "NO" && (dataC.getFullYear() != now.getFullYear() && dataC.getMonth() < now.getMonth())) {
                  var yyyy = dataC.getFullYear().toString();
                  var mm = (dataC.getMonth() + 1).toString(); // getMonth() is zero-based
                  var dd = dataC.getDate().toString();
                  var hh = dataC.getHours().toString();
                  dataToInsert = yyyy + "-" + (mm[1] ? mm : "0" + mm[0]) + "-01T00:00:00";
                  tmpMes = {};
                  tmpMes.timestamp = dataToInsert;
                  tmpMes.novaServiceStatus = {
                    "value": "undefined",
                    "value_clean": "undefined",
                    "description": "description"
                  };
                  tmpMes.neutronServiceStatus = {
                    "value": "undefined",
                    "value_clean": "undefined",
                    "description": "description"
                  };
                  tmpMes.cinderServiceStatus = {
                    "value": "undefined",
                    "value_clean": "undefined",
                    "description": "description"
                  };
                  tmpMes.glanceServiceStatus = {
                    "value": "undefined",
                    "value_clean": "undefined",
                    "description": "description"
                  };
                  tmpMes.KPServiceStatus = {
                    "value": "green",
                    "value_clean": "undefined",
                    "description": "description"
                  };
                  tmpMes.FiHealthStatus = {
                    "value": "undefined",
                    "value_clean": "undefined",
                    "description": "description"
                  };
                  tmpMes.OverallStatus = {
                    "value": "undefined",
                    "value_clean": "undefined",
                    "description": "description"
                  };
                  tmpMesArray.push(tmpMes)
                }
              }
              dataC.setMonth(dataC.getMonth() + 1)
            }
          }
          //for(var l = 0 in ;
          tmp_res_t.measures = tmpMesArray;
        }
        sendResponse(res, localEnum.OK.value, tmp_res_t);
      });
    }
  } //end usable entry

function getServiceHList(res, statusType, authToken, regionId, hostId) {
  sendResponse(res, localEnum.NOT_IMPLEMENTED.value, {
    "Error": localEnum.NOT_IMPLEMENTED.key
  });
}

function getServiceH(res, statusType, authToken, regionId, hostId, serviceId) {
  sendResponse(res, localEnum.NOT_IMPLEMENTED.value, {
    "Error": localEnum.NOT_IMPLEMENTED.key
  });
}

function getServiceHTime(res, statusType, authToken, regionId, hostId, serviceId, sinceValue) {
  /*HADOOP needed*/
  sendResponse(res, localEnum.NOT_IMPLEMENTED.value, {
    "Error": localEnum.NOT_IMPLEMENTED.key
  });
}

function getServiceVMList(res, statusType, authToken, regionId, vmId) {
  sendResponse(res, localEnum.NOT_IMPLEMENTED.value, {
    "Error": localEnum.NOT_IMPLEMENTED.key
  });
}

function getServiceVM(res, statusType, authToken, regionId, vmId, serviceId) {
  sendResponse(res, localEnum.NOT_IMPLEMENTED.value, {
    "Error": localEnum.NOT_IMPLEMENTED.key
  });
}

function getServiceVMTime(res, statusType, authToken, regionId, vmId, serviceId, sinceValue) {
  /*HADOOP needed*/
  sendResponse(res, localEnum.NOT_IMPLEMENTED.value, {
    "Error": localEnum.NOT_IMPLEMENTED.key
  });
}

function getNesList(res, statusType, authToken, regionId) {
  sendResponse(res, localEnum.NOT_IMPLEMENTED.value, {
    "Error": localEnum.NOT_IMPLEMENTED.key
  });
}

function getNes(res, statusType, authToken, regionId, nesId) {
  sendResponse(res, localEnum.NOT_IMPLEMENTED.value, {
    "Error": localEnum.NOT_IMPLEMENTED.key
  });
}

function getNesTime(res, statusType, authToken, regionId, nesId, sinceValue) {
  /*HADOOP needed*/
  sendResponse(res, localEnum.NOT_IMPLEMENTED.value, {
    "Error": localEnum.NOT_IMPLEMENTED.key
  });
}

function sendResponse(res, status, tmp_res) {
  res.writeHead(status, {
    'Content-Type': 'application/json'
  });
  //console.log(JSON.stringify(tmp_res))
  res.end(JSON.stringify(tmp_res));
}

function sendErrorResponse(res, status, errorTxt) {
  res.writeHead(status, {
    'Content-Type': 'application/json',
  });
  tmp_res = {}
  tmp_res = {
    "Error": errorTxt
  }
  res.end(JSON.stringify(tmp_res));
}

function IsJsonString(str) {
  try {
    JSON.parse(str);
  } catch (e) {
    return false;
  }
  return true;
}

function IsAdmin(idList) {
  if (idList.indexOf((localEnum.ADMIN.value)) != -1) return true;
  else return false
}

function IsFedMan(idList) {
  if (idList.indexOf((localEnum.FED_MAN.value)) != -1) return true;
  else return false
}

function IsIO(idList) {
  //set the list of all Infra ID
  if (idList.indexOf((localEnum.TrentoNode.value)) != -1) return true;
  else return false
}

function IsDev(idList) {
  if (idList.indexOf((localEnum.DEV.value)) != -1) return true;
  else return false
}

function IsSLA(idList) {
  if (idList.indexOf((localEnum.SLA.value)) != -1) return true;
  else return false
}

function IsTRUSTED_APP(idList) {
  //console.log(idList);
  listApp = localEnum.TRUSTED_APP.value
  if (listApp.indexOf(idList) != -1) {
    //console.log("True")
    return true;
  } else return false;
}

function extractBearerAccessToken(authHeaderValue) {
  var i = authHeaderValue.indexOf(" ");
  var authType = authHeaderValue.substring(0, i);
  var authToken = authHeaderValue.substring(i + 1);
  if (authType == "Bearer") {
    var tmpToken = new Buffer(authToken, 'base64');
    var authToken = tmpToken.toString('utf8')
  } else {
    console.log('WARNING: Authentication type not recognized');
  }
  return authToken;
}

function getTokenHeader(headers) {
    var authToken = '';
    if (headers['x-auth-token']) {
      authToken = headers['x-auth-token'];
    } else if (headers['authorization']) {
      authToken = extractBearerAccessToken(headers['authorization']);
    }
    return authToken;
  }
  /**
   * Convert an object into an array
   * @param {Object} obj
   * @return {Array} arr
   */

function valuesToArray(obj) {
  return Object.keys(obj).map(function(key) {
    obj[key].name = key;
    return obj[key];
  });
}