#!/usr/bin/env python

from __future__ import print_function
import sh
import argparse

# compute: inventory, private key, user and pass along all the other parameters to ansible-playbook

parser = argparse.ArgumentParser(description='Run the ansible playbook, using vagrant ssh-config parameters')

#parser.add_argument('node', metavar='n', type=str, nargs='?',
#                   help='node to run playbook on')

parser.add_argument('playbook_path', metavar='f', type=str, nargs='?',
                   help='path for the ansible playbook')

(args, unknown) = parser.parse_known_args()


ssh_config = dict([s.strip().split(" ") for s in str(sh.vagrant("ssh-config")).strip().split("\n")])
params = ["=".join(p) for p in (
            ("--private-key", ssh_config.get("IdentityFile")), 
            ("--user", ssh_config.get("User")),
            ("--inventory-file",".vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory")
         )] + unknown + [args.playbook_path]

# call ansible-playbook with


for line in sh.ansible_playbook(*params, _cwd=".", _iter=True):
    print(line, end="")
    