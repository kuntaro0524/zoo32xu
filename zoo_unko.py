import sys,math,numpy,os
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import Zoo
import ZooNavigator
import socket
import Date
import logging, logging.config

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))
    zoo=Zoo.Zoo()
    zoo.connect()

    esa_csv=sys.argv[1]

    # kuntaro_log
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_%s.log" % time_str
    logging.config.fileConfig('/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=True)
    navi.goAround()
    zoo.disconnect()
    ms.close()
