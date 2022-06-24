#!/bin/sh

finished=""

while true
do
 if [ ! -e ~/.zoo_current ]
 then
  sleep 10; continue
 fi

 cfg=(`cat ~/.zoo_current`)
 name=${cfg[0]}
 root=${cfg[1]}

 if [ "${root}" == "${finished}" ]
 then
  sleep 10; continue
 fi

 tmp=`mktemp`
 #tmp=/dev/stdout
 
 log=`ls -t /isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/log/bss_*.log | head -n1`
 
 echo "ROOT DIR= $root" > $tmp
 LANG=C date >> $tmp
 echo "" >> $tmp
 
 
 echo "Last 10 lines of $log" >> $tmp
 echo "  (`stat $log | grep Modify`)" >> $tmp
 echo "--------------------------------------------------------------------------" >> $tmp
 cat -n $log | tail -n10 | tr -d '\000' >> $tmp
 echo "" >> $tmp

 echo "Last errors in the log" >> $tmp
 echo "--------------------------------------------------------------------------" >> $tmp
 cat -n $log | egrep -i "(fail|error)" | tail -n10 | tr -d '\000' >> $tmp
 echo "" >> $tmp
 
 echo "" >> $tmp

 echo "Last 10 img files" >> $tmp
 echo "--------------------------------------------------------------------------" >> $tmp
 #find $root -type f -name \*.img -printf "%T+ %p\n" | sort | tail -n10 | sed -e "s,$root,," >> $tmp
 find `ls -drt $root/* | tail -n2 ` -type f -name \*master*.h5 -printf "%T+ %p\n" | sort | tail -n10 | sed -e "s,$root,," >> $tmp
 echo "" >> $tmp

 echo "Zoo progress log" >> $tmp
 echo "--------------------------------------------------------------------------" >> $tmp
 cat "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_progress.log" | tail -n40 | tr -d '\000' >> $tmp
 echo "" >> $tmp
 
 if [ "${cfg[2]}" == "finished" ]
 then
  echo "Job finished. Bye!" >> $tmp
  finished=$root
 fi

 nkf -j $tmp
 nkf -j $tmp | mail -s "[Message from ZOO] $name" hirata@spring8.or.jp
 
 rm $tmp

 echo "sleeping.."
 sleep 900

done
