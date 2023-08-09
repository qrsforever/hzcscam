#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

prog_name=$(basename $0)

__usage() {
    echo ""
    echo "$prog_name arguments:"
    echo "-s or --since Show entries not older than the specified date"
    echo "-n or --lines Number of journal entries to show"
    echo "-k or --dmesg Show kernel message log from the current boot"
    echo "-h or --help"
    echo ""
}

opts=$(getopt \
    --options "s:n:kh::" \
    --longoptions "since:,lines:,dmesg,help::" \
    --name "$prog_name" \
    -- "$@"
)

eval set --$opts

lines=0
dmesg=0
# format: 2019-04-18 7:21:48
since='today'

while [[ $# -gt 0 ]]; do
    case "$1" in
        -s|--since)
            since=$2
            shift 2
            ;;

        -n|--lines)
            if (( $2 > 0 ))
            then
                lines=$2
            fi
            shift 2
            ;;

        -k|--dmesg)
            dmesg=1
            shift 2
            ;;

        -h|--help)
            __usage && exit 1
            ;;

        *)
            break
            ;;
    esac
done

# echo "$since $lines $dmesg"

source /campi/_env

__echo_and_run() {
    echo "$*"
    /bin/bash -q "$*"
}

cd /tmp/

logdir=$(date +'%Y%m%d%H%M%S')

mkdir ${logdir}

# "==============/tmp/campi_*================"

for fil in `ls /tmp/campi_* 2>/dev/null`
do
    cp $fil ${logdir}
done

cp -arf ${LOGS_PATH} ${logdir}

# "==============campi=================="

cp -aprf /campi/runtime ${logdir}
cp /campi/version.txt ${logdir}
if [[ -f /var/campi/archives/campi_sos.log ]]
then
    cp /var/campi/archives/campi_sos.log ${logdir}
fi

# "==============system================"

nmcli device status > ${logdir}/system.log
echo "=================================" >> ${logdir}/system.log
free >> ${logdir}/system.log
echo "=================================" >> ${logdir}/system.log
df >> ${logdir}/system.log

# "==============journalctl================"

jargs=
if (( $lines > 0 ))
then
    jargs="--lines $lines"
else
    jargs="--since \"${since}\""
fi

for svc in ${CAMPI_ORDER_SVCS[@]}
do
    /bin/bash -c "journalctl -u campi_${svc}.service ${jargs}" >> ${logdir}/${svc}_service.log
done

for svc in `ls ${RUNTIME_PATH}/start`
do
    /bin/bash -c "journalctl -u campi_${svc}.service ${jargs}" >> ${logdir}/${svc}_service.log
done

if (( $dmesg > 0 ))
then
    journalctl -k >> ${logdir}/kernel.log
fi

# "==================end===================="

tar zcf ${logdir}.tar.gz ${logdir}

rm -rf ${logdir}

# don't modify
echo "logzip:/tmp/${logdir}.tar.gz"
