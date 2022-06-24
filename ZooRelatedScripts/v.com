#!/bin/csh
VIDEOSRV="/isilon/Common/CentOS4/videosrv_sep26_2016"

### set for New videosrv on NVIDIA GPU
LIBGL_ALWAYS_INDIRECT=yes
xsetroot -cursor_name star

######### For VIDEOSRV (remote) #########
sleep 1
ssh 192.168.163.6 "killall $VIDEOSRV"
sleep 2

# Please do not start videosrv with this script 161003
ssh -XC -c arcfour 192.168.163.6 "$VIDEOSRV --artray 3" &
