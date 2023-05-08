#!/usr/bin/python3
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText

DEBUG = False
EMAIL_SENDER = 'erlangai@qq.com'
EMAIL_PASSWD = 'napynuczfljubffa'
EMAIL_RECVER = 'erlang47@qq.com'

def main():
    sender = EMAIL_SENDER # os.environ.get('EMAIL_SENDER', None)
    passwd = EMAIL_PASSWD # os.environ.get('EMAIL_PASSWD', None)
    recver = EMAIL_RECVER # os.environ.get('EMAIL_RECVER', None)

    msg = MIMEText('hello', 'plain', 'utf-8')
    msg['From'] = sender
    msg['To'] = recver
    msg['Subject'] = '[TalentAI异常] %s' % 'aaaa'

    try:
        smtpObj = smtplib.SMTP('smtp.qq.com')
        smtpObj.login(sender, passwd)
        # smtpObj.sendmail(sender, recver.split(','), msg.as_string())
        smtpObj.send_message(msg)
        smtpObj.quit()
    except smtplib.SMTPException as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
    print('0')
