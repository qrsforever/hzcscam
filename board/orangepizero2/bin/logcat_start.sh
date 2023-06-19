#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source /campi/_env

__echo_and_run() {
    echo "$*"
    /bin/bash -q "$*"
}

cd /tmp/

logdir=$(date +'%Y%m%d%H%M%S')

mkdir ${logdir}

# "==============/tmp/campi_*================"

for fil in `ls /tmp/campi_*`
do
    cp $fil ${logdir}
done

# "==============campi=================="

cp -aprf /campi/runtime ${logdir}
cp /campi/version.txt ${logdir}
if [[ -f /var/campi/archives/campi_sos.log ]]
then
    cp /var/campi/archives/campi_sos.log ${logdir}
fi

# "==============system================"

nmcli device status > ${logdir}/system.log
free >> ${logdir}/system.log
df >> ${logdir}/system.log

# "==============journalctl================"

for svc in ${CAMPI_ORDER_SVCS[@]}
do
    journalctl -u campi_${svc}.service --since "today" >> ${logdir}/${svc}_service.log
done

for svc in `ls ${RUNTIME_PATH}/start`
do
    journalctl -u campi_${svc}.service --since "today" >> ${logdir}/${svc}_service.log
done

tar zcf ${logdir}.tar.gz ${logdir}

rm -rf ${logdir}

# don't modify
echo "logzip:/tmp/${logdir}.tar.gz"
