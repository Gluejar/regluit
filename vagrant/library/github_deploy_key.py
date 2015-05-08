#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Raymond Yee <raymond.yee@gmail.com>

import os
import json
import base64
from StringIO import StringIO
   
from github import Github

DOCUMENTATION = '''
---
module: github_deploy_key
short_description: create a deploy key to a github repository
description:
     - create a deploy key to a github repository
options:
  repo_name:
    description:
      - the repository to write key to
    required: true
  github_auth_key:
    description:
      - The oauth key provided by github. It can be found/generated on github under "Edit Your Profile" >> "Applications" >> "Personal Access Tokens"
    required: true
  key_path:
    description:
      - location of the key to upload
  key_name:
    description:
      - name for the key


author: Raymond Yee, raymond.yee@gmail.com

dependency: pygithub
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            github_auth_key=dict(required=True),
            repo_name=dict(required=True),
            key_path=dict(required=True),
            key_name=dict(required=True),
        )
    )

    github_auth_key = module.params['github_auth_key']
    repo_name = module.params['repo_name']
    key_path = module.params['key_path']
    key_name = module.params['key_name']

    failed = True
    
    try:
        g = Github(github_auth_key)
        s = open(key_path).read()
        repo = g.get_repo(repo_name)
        key = repo.create_key(key_name, s)
        
        failed = False
    except Exception, e:
        failed = False
    
    # error handling and what to return with success?
    
    if not failed:
        msg = "None:success"
    else:
        msg = str(e) + " " + str(e.message) + " " + str(e.get(args))

        
    module.exit_json(
      changed = True,
      github_auth_key = github_auth_key,
      repo_name =  repo_name,
      key_path = key_path,
      key_name = key_name,
      msg = msg,
      failed = failed
    )
 

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

main()