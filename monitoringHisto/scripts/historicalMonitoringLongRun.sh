#!/bin/bash

aggregate() {
    2>&1 | tee -a ./historicalMonitoringLongRun-${YEAR}${MONTH}.log
    # Daily aggregation
    for d in {1..30}; do
	echo "---- START:${YEAR}-${MONTH}-$d END:${YEAR}-${MONTH}-$(( ${d}+1 )) -----"
	/root/.virtualenvs/monitoringProd/bin/monitoringHisto -c /root/monitoringPROD/FIWARELab-monitoringAPI/monitoringHisto/monitoringHisto/conf/config-password.ini -s ${YEAR}-${MONTH}-$d -e ${YEAR}-${MONTH}-$(( ${d}+1 ));
    done

    # Montly aggregation
    echo "---- START:${YEAR}-${MONTH}-${MONTH_DAYS} END:${YEAR}-$(( ${MONTH}+1 ))-01 -----"
    /root/.virtualenvs/monitoringProd/bin/monitoringHisto -c /root/monitoringPROD/FIWARELab-monitoringAPI/monitoringHisto/monitoringHisto/conf/config-password.ini -s ${YEAR}-${MONTH}-${MONTH_DAYS} -e ${YEAR}-$(( ${MONTH}+1 ))-01
}

YEAR=2017
MONTH=03
MONTH_DAYS=31
aggregate

YEAR=2017
MONTH=04
MONTH_DAYS=30
aggregate

YEAR=2017
MONTH=05
MONTH_DAYS=31
aggregate

YEAR=2017
MONTH=06
MONTH_DAYS=30
aggregate

YEAR=2017
MONTH=07
MONTH_DAYS=31
aggregate

YEAR=2017
MONTH=08
MONTH_DAYS=31
aggregate

YEAR=2017
MONTH=09
MONTH_DAYS=30
aggregate

YEAR=2017
MONTH=10
MONTH_DAYS=31
aggregate

