#!/bin/csh
set VIDEOSRV="/isilon/Common/CentOS4/videosrv_jul02_2015a"

sleep 1
ssh 192.168.163.6 "killall $VIDEOSRV"

sleep 1
killall bss_apr12_2016_eiger5

# videosrv configure file backup -> copy
\cp -f $BLCONFIG/video/camera.inf.160615.bak $BLCONFIG/video/camera.inf.160615

echo "Please start BSS by double-clicking the desktop icon"
