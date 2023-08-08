#!/bin/bash

BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)
BINDIR=/campi/board/${BOARD}/bin

M=$(( RANDOM % 45 + 1 ))
H=$(( RANDOM % 6 ))

cat > /tmp/crontab <<EOF
SHELL=/bin/sh
PATH=${BINDIR}:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user	command
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )

${M} ${H} * * *	sleep 10 && reboot
@reboot root campi_safe_run.sh
EOF

mv /tmp/crontab /etc/crontab
chmod 644 /etc/crontab

# systemctl status cron.service
