#!/bin/bash

# run django-admin.py emit_notices

cd /opt/regluit
source /opt/regluit/ENV/bin/activate
/opt/regluit/ENV/bin/django-admin.py emit_notices --settings=regluit.settings.prod > /opt/regluit/deploy/emit_notices.log 2>&1
touch /opt/regluit/deploy/last-cron
