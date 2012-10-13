#!/bin/sh
echo 'SET FOREIGN_KEY_CHECKS = 0;'
# don't drop the core_key table
#echo 'SHOW TABLES;' | django-admin.py dbshell | sed -n "2,100000p" | sed '/core_key/ d' |  sed 's/.*/DROP TABLE IF EXISTS `&`;/'
echo 'SHOW TABLES;' | django-admin.py dbshell | sed -n "2,100000p" |  sed 's/.*/DROP TABLE IF EXISTS `&`;/'
echo 'SET FOREIGN_KEY_CHECKS = 1;'
