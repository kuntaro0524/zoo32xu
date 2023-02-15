#!/usr/bin/python
import sys,os
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs")
import Date
import sqlite3,time,numpy
import ESA
import DBinfo, datetime


current_dir = os.getcwd()

ofile = open(sys.argv[1], "a")
mail_addresses = sys.argv[2:]

ofile.write("# PATH = %s\n" % current_dir)
ofile.close()

command = "cat %s | mail -s 'File Transfer info from ISILON' -r oys@spring8.or.jp" % sys.argv[1]

for mail_address in mail_addresses:
    command += " %s" % mail_address

print(command)
os.system(command)
