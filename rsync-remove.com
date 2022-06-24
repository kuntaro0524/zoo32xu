#!/bin/csh
rsync -auv --remove-source-files /isilon/users/target/target/AutoUsers/191210/arisawa/ target@oys08:/isilon/users/target/target/AutoUsers/191210/arisawa/
