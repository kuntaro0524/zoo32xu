#!/bin/csh
\rm -f Libs/*pyc ?
\rm -f Libs/*png 
\rm -f Libs/*jpg 
\rm -f Libs/core*

# CentOS7
#git add --ignore-removal ./KAMO/ ./*.py *zoo*sh Libs/ ./ZooConfig/bss/ ./ZooConfig/header/ LargeHolder/*.py *.com *.sh *.csh ./*txt ZOOGUI/*.py

# CentOS6
git add  ./KAMO/ ./*.py *zoo*sh Libs/ ./ZooConfig/bss/ ./ZooConfig/header/ LargeHolder/*.py *.com *.sh *.csh ./*txt ZOOGUI/*.py
