#!/bin/sh

ansible-playbook -vvvv \
          -i .vagrant/provisioners/ansible/inventory/ \
          --private-key=/Users/raymondyee/.ssh/id_rsa \
          -e aws_access_key=$AWS_ACCESS_KEY \
          -e aws_secret_key=$AWS_SECRET_ACCESS_KEY \
          -u ubuntu $1
