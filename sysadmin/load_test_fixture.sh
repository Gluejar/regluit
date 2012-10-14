#!/bin/sh
./drop_tables.sh | django-admin.py dbshell
django-admin.py syncdb --migrate <<'EOF'
no
EOF
django-admin.py loaddata ../test/fixtures/basic_campaign_test.json 

