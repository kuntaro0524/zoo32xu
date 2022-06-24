#!/bin/bash
tmp=`mktemp`

cat ZooLogs/zoo_191116.log | grep -v DEBUG | tail -n 100 >> $tmp
cat $tmp  | mail -a umena.tgz -s "subject" kuntaro0524@gmail.com
