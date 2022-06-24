#!/bin/bash
while true
do
echo "<<<<<<<<<<<< Latest file list >>>>>>>>>>>>>>>>>>" > mail.txt
ls */scan00/ssrox/*h5 | tail -20 >> mail.txt
currlog=`ls ~/ZOO32XU/ZooLogs/zoo_220*.log | tail -1`
echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" >> mail.txt
echo "###### ZOOLOG start #####" >> mail.txt
tail -20 $currlog >> mail.txt
echo "###### ZOOLOG end #####" >> mail.txt
echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" >> mail.txt

# BSS log 
currbss=`ls /isilon/blconfig/bl32xu/log/bss_2022*.log | tail -1`
echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" >> mail.txt
echo "###### BSS log start #####" >> mail.txt
tail -20 $currbss >> mail.txt
echo "###### BSS log end #####" >> mail.txt
echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" >> mail.txt

sleep 2.0
echo "Sending an email"
mail -s "ZOO progress" kunio.hirata@riken.jp -c hiroaki.matsuura@riken.jp -c naoki.sakai@riken.jp -c yoshiaki.kawano@riken.jp < mail.txt
#mail -s "ZOO SSROX progress" kunio.hirata@riken.jp  < mail.txt

# Wait for 30mins
echo "wait for 1800 seconds"
sleep 1800

done
