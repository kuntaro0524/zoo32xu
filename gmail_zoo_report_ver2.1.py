#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os
import smtplib
import datetime
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.Header import Header
from email.Utils import formatdate

def create_message(from_addr, to_addr, subject, body, encoding):
    msg = MIMEMultipart()
    msg['Subject'] = Header(subject, encoding)
    msg['From'] = from_addr 
    msg['To'] = to_addr
    msg['Date'] = formatdate()

    related = MIMEMultipart('related')
    alt = MIMEMultipart('alternative')
    related.attach(alt)

    print(body)
    content = MIMEText(body, 'plain', encoding)
    alt.attach(content)

    return msg
    pass

def create_message_text(self, to_addr, subject, body, encoding):
    msg = MIMEText(body)
    msg['Subject'] = Header(subject, encoding)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate()

    return msg
    pass


def send_via_gmail(from_addr, to_addr, msg):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login('bl32xu@gmail.com', 'microfocus')
    s.sendmail(from_addr, [to_addr], msg.as_string())
    s.close()

if __name__ == '__main__':
    from_addr = 'bl32xu@gmail.com'
    #to_addr = 'kunio.hirata@riken.jp; naoki.sakai@riken.jp'
    to_addr = 'kunio.hirata@riken.jp'
    #to_addr = 'narita.hirotaka@gmail.com; kunio.hirata@riken.jp'
    title = "Message from ZOO32XU"
    date="%s"%(datetime.datetime.now())
    body = "%s\n"%date

###################
    sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs")
    import Date
    import sqlite3,time,numpy
    import ESA
    import DBinfo

    time_date = Date.Date()

    while(1):
        esa = ESA.ESA(sys.argv[1])
        conds_dict = esa.getDict()

        logline=""
        lap_array = []
        n_collected = 0
        n_mounted = 0
        n_meas = 0
        n_planned = len(conds_dict)
        total_time = 0.0

        for p in conds_dict:
            dbinfo = DBinfo.DBinfo(p)
            good_flag = dbinfo.getGoodOrNot()

            if dbinfo.isMount != 0:
                n_mounted += 1

            if good_flag == True:
                n_meas += 1
                meas_time = dbinfo.getMeasTime()
                total_time += meas_time
                puckid, pinid = dbinfo.getPinInfo()
                nds = dbinfo.getNDS()
                logline+="PUCK:%s"%p['puckid']
                logline+="-%02d "%p['pinid']
                logline+=" %s"%p['sample_name']
                logline+=" %5.1f m %5d ds " % (meas_time, nds)
                ####
                mt = dbinfo.getMountTime()
                rt = dbinfo.getRasterTime()
                dt = dbinfo.getDStime()
                ct = dbinfo.getCenterTime()
                logline+="| M:%5.1fm | C:%5.1fm | R:%5.1fm | D:%5.1fm |\n" % (mt,ct,rt,dt)

        # Mean measure time
        if n_meas != 0:
            mean_meas_time = total_time / float(n_meas)
        else:
            mean_meas_time = -999.9999

        n_remain = n_planned - n_mounted

        # Residual time
        residual_mins = mean_meas_time * n_remain
        residual_time = mean_meas_time * n_remain / 60.0 # hours

        logline+=" Mean time/pin = %5.1f min.\n" % mean_meas_time
        logline+="Planned pins: %3d, Mounted(all): %3d, Remained: %3d\n" % (n_planned, n_mounted, n_remain)
        logline+="Expected remained time: %5.2f h  (%8.1f m)\n"%(residual_time, residual_mins)
        nowtime = datetime.datetime.now()
        exp_finish_time = nowtime + datetime.timedelta(hours = residual_time)
        logline+="Expected finishing time: %s\n"%(exp_finish_time)

        if n_remain <= 1:
            logline+="Finished\n"
            msg = create_message_text(from_addr, to_addr, title, logline, 'utf-8')
            send_via_gmail(from_addr, to_addr, msg)
            break

        msg = create_message_text(from_addr, to_addr, title, logline, 'utf-8')
        send_via_gmail(from_addr, to_addr, msg)
        print("Now sleeping for 15mins....")
        time.sleep(15*60)
