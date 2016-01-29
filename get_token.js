/************************************************************************/
// Copyright 2015 CREATE-NET, Via alla Cascata, 56, 38123 Trento, Italy //
// This file is part of Xifi project                                    //
// author attybro                                                       //
//                                                                      //
// This is an API tester for the XIFI monitoring APIs                   //
/************************************************************************/

var OAuth = require('oauth');
var http = require('http');
var OAuth2 = OAuth.OAuth2;

//create a key secret using the portal or ask in order to obtain the ConsumerKey and ConsumerSecret
var ConsumerKey='7f57c3020ea149bf93141830419d29ce';
var ConsumerSecret =  'fe50a466ffa24a9093303aa26187a032';
var IDMaddress='https://account.lab.fiware.org/';
;


var oauth2 = new OAuth2(ConsumerKey, ConsumerSecret, IDMaddress,  null, 'oauth2/token',  null);
oauth2._customHeaders={Authorization: 'Basic '+new Buffer(ConsumerKey+":"+ConsumerSecret).toString('base64')}

function testAPI(){
  if (process.argv.length==5){
    if (process.argv[2] && process.argv[3] && process.argv[4]){
      oauth2.getOAuthAccessToken( '', { 'grant_type':'password', 'username':process.argv[2], 'password':process.argv[3] }, manageCred);
    }
  }
  else{
    console.log("Not enough arugments. Usage:\nnode testAPI.js <username> <password> <url_path>");
  }
}

function manageCred(e, access_token, refresh_token, results){
var bearer=new Buffer(access_token).toString("base64");
console.log("token");
console.log(bearer);  
}


testAPI();



