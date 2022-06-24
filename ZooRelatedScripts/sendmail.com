#!/bin/csh
cat mail.txt | mail -s \"ZOO\" kunio.hirata@riken.jp
