#!/usr/bin/env python

from __future__ import print_function
import sh
import argparse
import vagrant

# compute: inventory, private key, user and pass along all the other parameters to ansible-playbook

parser = argparse.ArgumentParser(description='Run the ansible playbook, using vagrant ssh-config parameters')

parser.add_argument('node', metavar='n', type=str, nargs='?',
                   help='node to run playbook on')
parser.add_argument('playbook_path', metavar='f', type=str, nargs='?',
                   help='path for the ansible playbook')

(args, unknown) = parser.parse_known_args()
print (args.node, args.playbook_path)

# for now if not multimachine, ignore node parameter
v = vagrant.Vagrant()

if len(v.status()) > 1:
    multimachine = True
    private_key = v.keyfile(args.node)
    user = v.user(args.node)
else:
    multimachine = False
    private_key = v.keyfile()
    user = v.user()

params = ["=".join(p) for p in (
            ("--private-key", private_key), 
            ("--user", user),
            ("--inventory-file",".vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory")
         )] + unknown + [args.playbook_path]


for line in sh.ansible_playbook(*params, _cwd=".", _iter=True):
    print(line, end="")
    