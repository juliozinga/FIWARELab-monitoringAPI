#!/bin/bash

OLD_DB=${1}
NEW_DB=${2}
DB_USER=${3}
REGION_ID=${4}
DB_HOST=${5}
DB_PORT=${6}
NEW_DB_USER=${7}

HOST_SERVICE_TABLE="host_service"
HOST_TABLE="host"
VM_TABLE="vm"
REGION_TABLE="region"
TMP_FOLDER="/tmp"
DATE=`date +%Y%m%d%H%M`

QSTART_MSG="Starting migration..."
QEND_MSG="...Migration done.\n"

HELP="\nHELP: This script is used to migrate the historical data from the old database to the new database.\nYou need to provide the following arguments:\n
\t 1) Old database name\n
\t 2) New database name\n
\t 3) DB user\n
\t 4) Region to migrate\n
Note: The migration is done saving the current table data into a temporary file on the $TMP_FOLDER folder. Please check the FS has enough free space.\n
      - mysqldump utility must be present on the system.\n
      - both databases must be present.\n
      - passing optional argument other than the first implies the use of all optional arguments
      - new db user can optionally specified if different from the old db user\n\n
Usage: bash ${0##*/} old_db_name new_db_name db_user region_id [db_host] [db_port] [new_db_user]\n"

# Functions
run_migration() {

    TMP_FILE=${TMP_FOLDER}/${REGION_ID}_${1}_${DATE}.sql

    if [ ${1} == ${REGION_TABLE} ]; then
        CMD="mysqldump -t -u $DB_USER -p$DB_PWD $OLD_DB $1 --where=entityId='$REGION_ID' -h $DB_HOST --port $DB_PORT"
    else
        CMD="mysqldump -t -u $DB_USER -p$DB_PWD $OLD_DB $1 --where=region='$REGION_ID' -h $DB_HOST --port $DB_PORT"
    fi

    # Export query
    echo -e "\tExporting from $OLD_DB using: $CMD"
    echo -e "\tInto file: $TMP_FILE"
    ${CMD} > ${TMP_FILE}

    # Import query
    CMD="mysql -u $NEW_DB_USER -p$DB_PWD $NEW_DB -h $DB_HOST --port $DB_PORT"

    echo -e "\tImporting to $NEW_DB using: $CMD"
    echo -e "\tFrom file: $TMP_FILE"
    ${CMD} < ${TMP_FILE}
}

# Main
if [ $# -lt 3 ]; then
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
    if [ -z "$NEW_DB_USER" ]; then
        NEW_DB_USER=${DB_USER}
    fi
fi

# Requesting DB password
echo "Enter password for DB user $DB_USER"
read -s DB_PWD

# Updating host_service
echo -e "\nWould you like to migrate $HOST_SERVICE_TABLE table ? N/y"
read INPUT
if [[ ${INPUT} == 'y' ]]; then
	echo ${QSTART_MSG}
	run_migration ${HOST_SERVICE_TABLE}
	echo -e ${QEND_MSG}
fi

# Updating host
echo "Would you like to migrate $HOST_TABLE table ? N/y"
read INPUT
if [[ ${INPUT} == 'y' ]]; then
	echo ${QSTART_MSG}
	run_migration ${HOST_TABLE}
	echo -e ${QEND_MSG}
fi

# Updating vm
echo "Would you like to migrate $VM_TABLE table ? N/y"
read INPUT
if [[ ${INPUT} == 'y' ]]; then
	echo ${QSTART_MSG}
	run_migration ${VM_TABLE}
	echo -e ${QEND_MSG}
fi

# Updating region
echo "Would you like to migrate $REGION_TABLE table ? N/y"
read INPUT
if [[ ${INPUT} == 'y' ]]; then
	echo ${QSTART_MSG}
	run_migration ${REGION_TABLE}
	echo -e ${QEND_MSG}
fi