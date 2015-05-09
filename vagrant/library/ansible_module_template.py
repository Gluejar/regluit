#!/Users/raymondyee/anaconda/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Raymond Yee <raymond.yee@gmail.com>


import json
import base64

DOCUMENTATION = '''
---
module: MODULE_NAME
short_description: MODULE_SHORT_DESCRIPTION
description:
     - Adds service hooks and removes service hooks that have an error status.
version_added: "1.4"
options:
  user:
    description:
      - Github username.
    required: true
  oauthkey:
    description:
      - The oauth key provided by github. It can be found/generated on github under "Edit Your Profile" >> "Applications" >> "Personal Access Tokens"
    required: true
    
   


author: Raymond Yee, raymond.yee@gmail.com
'''

EXAMPLES = '''
# Example creating a new service hook. It ignores duplicates.
- github_hooks: action=create hookurl=http://11.111.111.111:2222 user={{ gituser }} oauthkey={{ oauthkey }} repo=https://api.github.com/repos/pcgentry/Github-Auto-Deploy

# Cleaning all hooks for this repo that had an error on the last update. Since this works for all hooks in a repo it is probably best that this would be called from a handler.
- local_action: github_hooks action=cleanall user={{ gituser }} oauthkey={{ oauthkey }} repo={{ repo }}
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
        oauthkey=dict(required=True),
        repo=dict(required=True),
        user=dict(required=True),
        validate_certs=dict(default='yes', type='bool'),
        content_type=dict(default='json', choices=['json', 'form']),
        )
    )

    action = module.params['action']
    hookurl = module.params['hookurl']
    oauthkey = module.params['oauthkey']
    repo = module.params['repo']
    user = module.params['user']
    content_type = module.params['content_type']

    if action == "list":
        (rc, out) = _list(module, hookurl, oauthkey, repo, user)

    if action == "clean504":
        (rc, out) = _clean504(module, hookurl, oauthkey, repo, user)

    if action == "cleanall":
        (rc, out) = _cleanall(module, hookurl, oauthkey, repo, user)

    if action == "create":
        (rc, out) = _create(module, hookurl, oauthkey, repo, user, content_type)

    if rc != 0:
        module.fail_json(msg="failed", result=out)

    module.exit_json(msg="success", result=out)


# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

main()