#!/bin/bash
files=`find . -name raster.jpg`

for file in $files
do
echo $file
eog $file
done


