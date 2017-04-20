#!/bin/bash

MY_PWD='r00tme'

echo Provisioning...
yum update -y
echo -e "[mongodb-org-2.6]\nname=MongoDB 2.6 Repository\nbaseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/\ngpgcheck=0\nenabled=1"|sudo tee /etc/yum.repos.d/mongodb-org-2.6.repo
yum install -y mongodb-org wget emacs-nox gpg screen

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

git clone https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI.git
npm install bootstrap enum mongoose oauth moment request mysql
mongorestore /vagrant/SHARED/mongodb_backup/

#Mysql
yum -y install mysql-server
/sbin/service mysqld start
/usr/bin/mysqladmin -u root password $MY_PWD
/usr/bin/mysqladmin -u root -p$MY_PWD -h localhost.localdomain password $MY_PWD
chkconfig mysqld on
echo "MYSQL password is: $MY_PWD"
mysql -u root -p$MY_PWD monitoring < /vagrant/SHARED/backupMysql.dump

# Ruby and Rails install
gpg2 --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
curl -sSL https://get.rvm.io | sudo bash -s stable
source /etc/profile.d/rvm.sh
rvm requirements
rvm install 2.0.0
gem install rails

#Infographics clone
git clone https://github.com/SmartInfrastructures/fi-lab-infographics.git
cd fi-lab-infographics
git checkout f58064ce597a324d4046d83682d409242f436bd2

#Decrypt infographics configurations and DB dump
echo $1 | gpg --passphrase-fd 0 --batch --yes -o /vagrant/infographics-deploy/infographics-dev-deploy.patch -d /vagrant/infographics-deploy/infographics-dev-deploy.patch.gpg
echo $1 | gpg --passphrase-fd 0 --batch --yes -o /vagrant/infographics-deploy/fiware_lab_infographics.sql -d /vagrant/infographics-deploy/fiware_lab_infographics.sql.gpg

#Infographics customize
git apply /vagrant/infographics-deploy/infographics-dev-deploy.patch
rm /vagrant/infographics-deploy/infographics-dev-deploy.patch

#Infographics install
yum install mysql-devel -y
bundle install
mysql -u root -pr00tme -e "create database infographics_development"
mysql -u root -p$MY_PWD infographics_development < /vagrant/infographics-deploy/fiware_lab_infographics.sql
rm /vagrant/infographics-deploy/fiware_lab_infographics.sql
rake fi_lab_app:install:migrations
rake db:migrate
echo "----------------------------------------------------------------"
echo "Vagrant VM deployment ready, to start Infographics use:"
echo "vagrant ssh"
echo "sudo su && cd fi-lab-infographics && rails server"
echo "----------------------------------------------------------------"
