#!/bin/sh
echo "Starting Cheetah"
wget -O - http://192.168.163.33:8080/start/$(id -u)/$(id -g) 2>/dev/null


