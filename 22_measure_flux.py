#!/bin/env python
import sys
import os
import socket
import time
import datetime

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")

import Device

if __name__ == "__main__":
    host = '172.24.242.59'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    dev = Device.Device(s, bl="bl32xu")
    dev.init()

    phosec = dev.measureFlux()
    print "Measured flux = %5.2e photons/sec" % phosec
