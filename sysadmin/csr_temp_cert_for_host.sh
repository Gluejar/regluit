#!/bin/bash
# Cert4Host.sh - Generate SSL Certificates for a host name.

SERVER_KEY_PATH="/etc/ssl/private/server.key"
SERVER_CRT_PATH="/etc/ssl/certs/server.crt"

HOSTNAME="$1";

if [ -z "${HOSTNAME}" ]; then
echo "Usage : Cert4Host.sh HOSTNAME";
exit;
fi

if [ ! -e $SERVER_KEY_PATH ]; then
openssl genrsa  -out server.key 2048 
else
echo "Key already exists ... skipping ..."
  umask 77; cp $SERVER_KEY_PATH server.key
fi

umask 77; openssl rsa -in server.key -out $HOSTNAME.key

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
EMAIL="eric@gluejar.com";
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

openssl x509 -req -days 999 -in $HOSTNAME.csr -signkey $HOSTNAME.key -out $HOSTNAME.crt

cp $HOSTNAME.key $SERVER_KEY_PATH 
cp $HOSTNAME.crt $SERVER_CRT_PATH 
