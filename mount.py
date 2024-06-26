import os,sys,glob
import time
import numpy as np
import socket
import Zoo
import Date

import logging, logging.config

if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()
    time.sleep(5.0)

    # kuntaro_log
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "/staff/bl32xu/BLsoft/NewZoo/ZooLogs/zoo_%s.log" % time_str
    logging.config.fileConfig('/staff/bl32xu/BLsoft/NewZoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    print(len(sys.argv))

    zoo.mountSample(sys.argv[1],sys.argv[2])
    zoo.waitTillReady()
    zoo.disconnect()
