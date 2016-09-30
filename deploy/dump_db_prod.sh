#!/bin/bash
PASSWORD=unglue1t
HOST=production.cboagmr25pjs.us-east-1.rds.amazonaws.com
USER=root
DATABASE=unglueit
DB_FILE=unglue.it.sql
EXCLUDED_TABLES=(
  core_key
)

IGNORED_TABLES_STRING=''
for TABLE in "${EXCLUDED_TABLES[@]}"
do :
   IGNORED_TABLES_STRING+=" --ignore-table=${DATABASE}.${TABLE}"
done

echo "Dump structure"
mysqldump --host=${HOST} --user=${USER} --password=${PASSWORD} --single-transaction --no-data ${DATABASE} > ${DB_FILE}

echo "Dump content"
mysqldump --host=${HOST} --user=${USER} --password=${PASSWORD}  --no-create-info ${DATABASE} ${IGNORED_TABLES_STRING} >> ${DB_FILE}