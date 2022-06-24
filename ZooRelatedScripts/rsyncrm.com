#!/bin/csh
rsync -auv --remove-source-files ./dose_exp target@oys19:/isilon/users/target/target/AutoUsers/191211/
