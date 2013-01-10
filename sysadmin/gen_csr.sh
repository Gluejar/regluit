#!/bin/bash
# gen_csr.sh - Generate CSR  for a host name.

HOSTNAME="$1";

if [ -z "${HOSTNAME}" ]; then
echo "Usage : gen_csr.sh HOSTNAME";
exit;
fi

# Country Name (2 letter code) [GB]:.
#  State or Province Name (full name) [Berkshire]:.
#  Locality Name (eg, city) [Newbury]:.
#  Organization Name (eg, company) [My Company Ltd]:.
#  Organizational Unit Name (eg, section) []:.
#  Common Name (eg, your name or your server's hostname) []:.
#  Email Address []:.
#  A challenge password []:
#  An optional company name []:

COUNTRY="US";
STATE="NJ";
LOCALITY="Montclair";
ORGNAME="Gluejar, Inc.";
ORGUNIT="";
CNAME=$HOSTNAME;
EMAIL="support@gluejar.com";
PASSWORD="";
OPTION_COMPANY_NAME="";

echo "$COUNTRY
$STATE
$LOCALITY
$ORGNAME
$ORGUNIT
$CNAME
$EMAIL
$PASSWORD
$OPTIONAL_COMPANY_NAME" | openssl req -new -key $HOSTNAME.key -out $HOSTNAME.csr

