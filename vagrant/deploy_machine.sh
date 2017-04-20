#!/bin/bash

MY_PWD='r00tme'
YUM_INSTALL='yum install -y '

echo Provisioning...
yum update -y
echo -e "[mongodb-org-2.6]\nname=MongoDB 2.6 Repository\nbaseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/\ngpgcheck=0\nenabled=1"|sudo tee /etc/yum.repos.d/mongodb-org-2.6.repo
$YUM_INSTALL mongodb-org
$YUM_INSTALL wget
$YUM_INSTALL screen
$YUM_INSTALL emacs-nox
$YUM_INSTALL python-pip.noarch

# Install and customize git
yum -y install git
git config --global color.ui auto

#context broker install
wget -O /tmp/epel-release-latest-6.noarch.rpm https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm
rpm -i /tmp/epel-release-latest-6.noarch.rpm
yum install -y boost-system boost-filesystem boost-thread libmicrohttpd logrotate libcurl boost-regex
curl --insecure -o /tmp/contextBroker-0.26.1-1.x86_64.rpm https://forge.fiware.org/frs/download.php/1713/contextBroker-0.26.1-1.x86_64.rpm
rpm -i /tmp/contextBroker-0.26.1-1.x86_64.rpm

#NodeJs install
curl --silent --location https://rpm.nodesource.com/setup_4.x |sudo bash -
yum -y install nodejs
yum -y install gcc-c++ make
yum -y install npm

/etc/init.d/contextBroker start
/etc/init.d/mongod start

# monitoringAPI and dependencies
git clone https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI.git
pip install -r FIWARELab-monitoringAPI/monitoringHisto/requirements.txt
pip install -r FIWARELab-monitoringAPI/monitoringProxy/requirements.txt
cd FIWARELab-monitoringAPI/nodeJS
npm install
cd $OLDPWD

# Restore from Mongo DB dump
if [[ -d /vagrant/SHARED/mongodb_backup/ ]]; then
	echo "Restoring from mongoDB dump"
	mongorestore /vagrant/SHARED/mongodb_backup/
fi

#Mysql
yum -y install mysql-server
/sbin/service mysqld start
/usr/bin/mysqladmin -u root password $MY_PWD
/usr/bin/mysqladmin -u root -p$MY_PWD -h localhost.localdomain password $MY_PWD
chkconfig mysqld on

# Restore from MySQL DB dump
if [[ -d /vagrant/SHARED/backupMysql.dump ]]; then
	echo "Restoring from MySQL DB dump"
	mysql -u root -p$MY_PWD monitoring < /vagrant/SHARED/backupMysql.dump
fi

#fiware-pep-proxy
git clone https://github.com/ging/fiware-pep-proxy.git
cd fiware-pep-proxy
npm install
cd $OLDPWD

echo "----------------------------------------------------------------"
echo "-- Vagrant VM deployment ready, here is some info: --"
echo "MYSQL password is: $MY_PWD"
echo "-- To start monitoringAPI: --"
echo "1) Customise all configuration files"
echo "2) cd start_scripts"
echo "3) screen -c start.screen"
echo "More information here: https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI#start-the-web-service"
echo "----------------------------------------------------------------"