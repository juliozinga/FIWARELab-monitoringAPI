#!/bin/bash

OLD_REGION=${1}
NEW_REGION=${2}
DB_USER=${3}
DB_NAME=${4}
DB_HOST=${5}
DB_PORT=${6}

HOST_SERVICE="host_service"
HOST="host"
VM="vm"
REGION="region"

QSTART_MSG="Starting query on DB..."
QEND_MSG="...Query done.\n"

HELP="\nHELP: This script is used to rename the region ID on the historical monitoring DB.\nYou need to provide the following arguments:\n
\t 1) Old region name\n
\t 2) New region name\n
\t 3) DB user\n
\t 4) DB name\n
Note: Since the DB is big you could have errors on update like this: \"ERROR 1206 (HY000): The total number of locks exceeds the lock table size\"
      If this is the case please add \"innodb_buffer_pool_size=256M\" on /etc/my.cnf and restart mysql server\n
      - passing optional argument other than the first implies the use of all optional arguments\n\n
Usage: bash ${0##*/} old_region_name new_region_name db_user db_name [db_host] [db_port]\n"

# Functions
run_query() {
    # Prepare query
    if [ ${1} == ${REGION} ]; then
        QUERY="update $1 SET entityId = REPLACE(entityId, '$OLD_REGION', '$NEW_REGION') where entityId = '$OLD_REGION';"
    else
        QUERY="update $1 SET entityId = REPLACE(entityId, '$OLD_REGION', '$NEW_REGION'), region = '$NEW_REGION' where region = '$OLD_REGION';"
    fi
    echo -e "\tRunning this query on DB:\n\t$QUERY"
    # Run query
    mysql -u ${DB_USER} -p${DB_PWD} ${DB_NAME} -h ${DB_HOST} --port ${DB_PORT} -e "$QUERY"
}

# Main
if [ $# -lt 4 ]; then
    echo "Please provide valid arguments"
    echo -e ${HELP}
    exit 1
else
    if [ -z "$DB_HOST" ]; then
        DB_HOST="127.0.0.1"
    fi
    if [ -z "$DB_PORT" ]; then
        DB_PORT="3306"
    fi
fi

# Requesting DB password
echo "Enter password for DB user $DB_USER"
read -s DB_PWD

# Updating host_service
echo -e "\nWould you like to update $HOST_SERVICE table ? N/y"
read INPUT
if [[ ${INPUT} == 'y' ]]; then
	echo ${QSTART_MSG}
	run_query ${HOST_SERVICE}
	echo -e ${QEND_MSG}
fi

# Updating host
echo "Would you like to update $HOST table ? N/y"
read INPUT
if [[ ${INPUT} == 'y' ]]; then
	echo ${QSTART_MSG}
	run_query ${HOST}
	echo -e ${QEND_MSG}
fi

# Updating vm
echo "Would you like to update $VM table ? N/y"
read INPUT
if [[ ${INPUT} == 'y' ]]; then
	echo ${QSTART_MSG}
	run_query ${VM}
	echo -e ${QEND_MSG}
fi

# Updating region
echo "Would you like to update $REGION table ? N/y"
read INPUT
if [[ ${INPUT} == 'y' ]]; then
	echo ${QSTART_MSG}
	run_query ${REGION}
	echo -e ${QEND_MSG}
fi