#!/bin/csh
# 2015/07/22 K.Hirata
# Special setting for automatic data collection
# Configure files are in this directory 

# 2015/09/26 K.Hirata
# For suno3 experiments
# ZooConfig directory is moved from ~/Staff/ZooTest/
# zoo.csh is modified in this directory

setenv BLCONFIG /isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/
echo "\n\n" | /usr/local/bss/bss_apr12_2016_eiger5 --server --console --notune
