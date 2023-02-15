import sys,math,numpy,os

beamline = "BL32XU"
if beamline == "BL32XU":
    sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
    sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
    blanc_address = '172.24.242.41'

elif beamline == "BL45XU":
    sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/")
    sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
    blanc_address = '172.24.242.59'

import Zoo
import datetime
import ZooNavigator
from MyException import *
import socket
import Date
import logging
import logging.config
import subprocess

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("connecting %s" % blanc_address)
    ms.connect((blanc_address, 10101))
    print("Success")

    # Logging setting
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "/isilon/%s/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_%s.log" % (beamline, time_str)
    print("changing mode of %s" % logname)
    logging.config.fileConfig('/isilon/%s/BLsoft/PPPP/10.Zoo/Libs/logging.conf' % beamline, defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')
    os.chmod(logname, 0o666)

    zoo=Zoo.Zoo()
    zoo.connect()

    total_pins = 0
    for input_file in sys.argv[1:]:
        logger.info("Start processing %s" % input_file)
        if input_file.rfind("csv") != -1:
            navi = ZooNavigator.ZooNavigator(zoo, ms, input_file, is_renew_db=True)
            num_pins = navi.goAround()
        elif input_file.rfind("db") != -1:
            esa_csv = "dummy.csv"
            navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=False)
            num_pins = navi.goAround(input_file)
        total_pins += num_pins

    if total_pins == 0:
        logger.info("ZOO did not process any pins")
    else:
        logger.info("Start cleaning after the measurements")
        zoo.dismountCurrentPin()
        zoo.cleaning()

    zoo.disconnect()
    ms.close()
