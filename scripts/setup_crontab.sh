#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(cd ${CUR_DIR}/..; pwd)
BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)

M=$(( RANDOM % 45 + 1 ))
H=$(( RANDOM % 6 ))

cp ${TOP_DIR}/board/${BOARD}/bin/campi_safe_run.sh /usr/local/bin/campi_safe_run.sh
cp ${TOP_DIR}/board/${BOARD}/bin/sysled /usr/local/bin/sysled

chmod +x /usr/local/bin/campi_safe_run.sh
chmod +x /usr/local/bin/sysled


cat > /tmp/crontab <<EOF
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user	command
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )

${M} ${H}	* * *	root    sleep 10 && reboot -f

@reboot root campi_safe_run.sh
EOF

mv /tmp/crontab /etc/crontab
chmod 644 /etc/crontab

# systemctl status cron.service
