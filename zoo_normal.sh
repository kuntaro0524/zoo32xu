#!/bin/sh
VIDEOSRV="/usr/local/bss/videosrv2"

### set for New videosrv on NVIDIA GPU
LIBGL_ALWAYS_INDIRECT=yes
xsetroot -cursor_name star

######### For VIDEOSRV (remote) #########
sleep 1
##ssh 192.168.163.6 "killall $VIDEOSRV"  # for ARTRAY
killall $VIDEOSRV    # for DFK72  YK@190315
sleep 2

# Please do not start videosrv with this script 161003
BLCONFIG=/blconfig $VIDEOSRV --v4l2 &  ### for WAT3921 YK@200119
xsetroot -cursor_name top_left_arrow

############### SHIKA Backend ##########################
# Cheetah

echo "Starting Cheetah"
#wget -O - http://ramchan:8080/start/$(id -u)/$(id -g) 2>/dev/null
/usr/local/bss/startcheetah.sh

for i in {1..10}
do
 sleep 1
 cheetah_ok=0
 ssh 192.168.163.34 "yamtbx.python /usr/local/cheetah_daemon/check_cheetah.py" && \
 ssh 192.168.163.31 "yamtbx.python /usr/local/cheetah_daemon/check_cheetah.py" && break
 notify-send "BSS startup" "Cheetah not up. retrying (${i})."
 notify-send "BSS startup" "`/usr/local/bss/startcheetah.sh`"
 cheetah_ok=1
done

if [ "$cheetah_ok" == "1" ]
then
 notify-send "BSS startup ERROR" "Can't start cheetah!!" -i gnome-log -t 10000
 aplay /usr/lib64/libreoffice/share/gallery/sounds/falling.wav > /dev/null 2>&1
 exit
fi

# Download server test
 #if ! ssh -oBatchMode=yes 192.168.163.10 hostname
 if ! ssh -oBatchMode=yes 192.168.163.9 hostname
 then
  notify-send "BSS startup ERROR" "SSH to local-raid NOT configured!!" -i gnome-log -t 10000
  aplay /usr/lib64/libreoffice/share/gallery/sounds/falling.wav > /dev/null 2>&1
  exit
 fi


# Hit-extract server test
if ! ssh -oBatchMode=yes 192.168.163.34 hostname
then
 notify-send "BSS startup ERROR" "SSH to 192.168.163.34 NOT configured!!" -i gnome-log -t 10000
 aplay /usr/lib64/libreoffice/share/gallery/sounds/falling.wav > /dev/null 2>&1
 exit
fi

# 171114 changed
echo "\n\n" | /usr/local/bss/bss --server --console 


# After BSS shutdown
sleep 1
##ssh 192.168.163.6 "killall $VIDEOSRV"    # for ARTRAY
killall $VIDEOSRV      # for DFK72 YK@190315

END:
