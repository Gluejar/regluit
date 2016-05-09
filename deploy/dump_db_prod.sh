#!/bin/sh
mysqldump -h production.cboagmr25pjs.us-east-1.rds.amazonaws.com -u root --password=unglue1t --ignore-table=unglueit.core_key unglueit
