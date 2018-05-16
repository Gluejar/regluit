# Deploying Regluit to Production

The current provisioning setup uses [Ansible](https://www.ansible.com/resources/get-started) to deploy code to production servers.

## Pre-requisites 
Before attempting to deploy, ensure you have done the following:
1. Install `ansible` on your local machine
1. Obtain the `ansible-vault` password and save it to a file
1. Set the path to the `ansible-vault` file via environment variable e.g. `export NSIBLE_VAULT_PASSWORD_FILE=[path]`
1. Create/obtain the secret key needed to SSH into the server
1. (optional) Add the secret key to your ssh agent 
    ```
    $ ssh-agent bash
    $ ssh-add /path/to/secret.pem
    ``` 


## Deploy
Deploying is as simple as running the `setup-prod` ansible playbook.  
Navigate to the `provisioning/` directory and run the following:  
```
$ ansible-playbook -i hosts setup-prod.yml
```   
If you successfully completed all the pre-requisite steps, the playbook should begin running through deploy tasks and finally restart apache.


## Additional Configuration

### Variables and Secrets
The necessary variables are pulled from `provisioning/group_vars/production/vars.yml` which in turn pulls certain secret values from `vault.yml`.  
The variables are split into two files to still allow for searching references in playbook tasks.
To add or view secret values, you must decrypt the file first: `$ ansible-vault decrypt vault.yml` however **always remember to encrypt secret files before pushing to git**.   This is done in a similar manner: `$ ansible-vault encrypt vault.yml`.   

Ansible also allows for overriding variables from the command line when running playbooks.  
This is useful for ad-hoc playbook runs without editing var files.   
For example, deploying code from another branch can be done as so:  
`$ ansible-playbook -i hosts setup-prod.yml -e git_branch=mybranch`  

### Inventory and Groups
Currently we are using a static inventory file `hosts` to define target server hosts and groups.  
This means that the `hosts` file must be manually updated to reflect things such as DNS changes or additional hosts being added.  
In the future, the static inventory file may be replaced with a dynamic inventory solution, such as ansible's [ec2 inventory script](http://docs.ansible.com/ansible/latest/user_guide/intro_dynamic_inventory.html#example-aws-ec2-external-inventory-script)  

One important aspect of the `hosts` file is that it defines the groups which a host or hosts are a part of.   
Currently, there is only one prod host called `regluit-prod` which is a member of the `production` group.   
Both of these designations are important, as the `setup-prod` playbook specifically targets the `regluit-prod` host, and only that host will inherit the variables in `group_vars/production/`.   
