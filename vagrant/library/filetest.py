#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Raymond Yee <raymond.yee@gmail.com>

import os
import json

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *


DOCUMENTATION = '''
---
module: filetest
short_description: tests for existence of a path
description:
     - Checks on the existence of a given path
#options:
#  path:
#    description:
#      - path to test.
#    required: true
   

author: Raymond Yee, raymond.yee@gmail.com
'''

def main():
    cwd = str(os.getcwd())
    print ( json.dumps({
    "cwd" : cwd
}))

main()