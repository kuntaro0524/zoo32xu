#!/bin/csh

pwd > pwd.txt
tar cvfz matome.tgz ./XSCALE.INP ./XSCALE.LP ./xscale.hkl ccp4/ pwd.txt
