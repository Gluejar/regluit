
# # Goals of this notebook
# 
# * instantiate a new EC2 instance with which to build a new image
# * configure the instance -- what's involved?  Essentially turn https://github.com/Gluejar/regluit/blob/master/README.md into a fabric script
# * security group
# * database
# * database security group
# * IAM
# * elastic IP
# 
# 
# I'm starting to figure out the pieces using this IPython notebook, but ultimately what am I producing?  Something that Eric and Andromeda can run:
# 
# * a set of fabric commands (https://github.com/Gluejar/regluit/blob/master/fabfile.py)?
# * some other form?
# 

# In[1]:
from regluit.sysadmin import aws
reload(aws)

# Out[1]:
#     <module 'regluit.sysadmin.aws' from '/Users/raymondyee/C/src/Gluejar/regluit/sysadmin/aws.pyc'>

# In[2]:
# look up Ubuntu EC2 image ids from alestic.com
# us-east-1 Ubuntu 12.04 LTS Precise
# EBS boot	ami-e7582d8e

#AMI_UBUNTU_12_04_ID = 'ami-79c0ae10' # older one
AMI_UBUNTU_12_04_ID = 'ami-e7582d8e'
image = aws.ec2.get_all_images(image_ids=[AMI_UBUNTU_12_04_ID])[0]

# In[3]:
# name of image follows Eric Hammond's convention of dating the images

image.id, image.name

# Out[3]:
#     (u'ami-e7582d8e',
#      u'ubuntu/images/ebs/ubuntu-precise-12.04-amd64-server-20130603')

# In[4]:
# sometimes we have an instance running or created already
# so we just need to get a reference to it (instead of creating a new one)

instance = aws.instance('new_test')
instance, instance.state

# Out[4]:
#     (Instance:i-4f64082f, u'running')

# In[ ]:
if instance.state == 'stopped':
    instance.start()

# In[ ]:
# launch a new instance
# use default security group for now -- probably want to make a new one

INSTANCE_NAME = 'new_test'
SECURITY_GROUP_NAME = 'testsg1'

(instance, cmd) = aws.launch_instance(ami=AMI_UBUNTU_12_04_ID, 
                                      instance_type='t1.micro',
                                      key_name='rdhyee_public_key',
                                      group_name=SECURITY_GROUP_NAME,
                                      tag='new_instance',
                                      cmd_shell=False)

# In[ ]:
instance.update()

# In[ ]:
# add name
INSTANCE_NAME = 'new_test'
instance.add_tag('Name', INSTANCE_NAME)

# In[ ]:
# configure security group testsg1

PORTS_TO_OPEN = [80, 443]

for port in PORTS_TO_OPEN:
    aws.ec2.authorize_security_group(group_name=SECURITY_GROUP_NAME, ip_protocol='tcp', from_port=port, to_port=port,
         cidr_ip='0.0.0.0/0')


# In[ ]:
console_output = instance.get_console_output()

# In[ ]:
# it takes time for the console output to show not be None -- I don't know exactly how long

print console_output.output

# In[ ]:
# http://ubuntu-smoser.blogspot.com/2010/07/verify-ssh-keys-on-ec2-instances.html

[line for line in console_output.output.split("\n") if line.startswith("ec2")]

# In[ ]:
instance_id = instance.id
instance_id

# In[ ]:
output = !source ~/gj_aws.sh; ec2-get-console-output $instance_id  | grep -i ec2

# In[ ]:
output

# In[ ]:
# copy a command to ssh into the instance

cmdstring = "ssh -oStrictHostKeyChecking=no ubuntu@{0}".format(instance.dns_name)
# works on a mac
! echo "$cmdstring" | pbcopy
cmdstring

## dynamic execution of fabric tasks to setup the instance

# In[6]:
# http://docs.fabfile.org/en/1.6/usage/execution.html#using-execute-with-dynamically-set-host-lists

import fabric
from fabric.api import run, local, env, cd, sudo
from fabric.operations import get

from regluit.sysadmin import aws
from StringIO import StringIO

import github

# uncomment for debugging
# github.enable_console_debug_logging()

from github import Github

from django.conf import settings 

# allow us to use our ssh config files (e.g., ~/.ssh/config)
env.use_ssh_config = True

GITHUB_REPO_NAME = "Gluejar/regluit"
#GITHUB_REPO_NAME = "rdhyee/working-open-data"

# maybe generate some random pw -- not sure how important it is to generate some complicated PW if we configure 
# security groups properly
MYSQL_ROOT_PW = "unglueit_pw_123"


# can use 3 different types of authn: https://github.com/jacquev6/PyGithub/issues/15
# can be empty, username/pw, or personal API token (https://github.com/blog/1509-personal-api-tokens)
g = Github(settings.GITHUB_AUTH_TOKEN)

def host_type():
    run('uname -s')
    
def deploy():
    sudo("aptitude update")
    sudo("yes | aptitude upgrade")
    sudo("yes | aptitude install git-core apache libapache2-mod-wsgi mysql-client python-virtualenv python-mysqldb redis-server python-lxml")
    sudo("yes | aptitude install python-dev")
    sudo("yes | aptitude install libmysqlclient-dev")
    # http://www.whatastruggle.com/postfix-non-interactive-install
    sudo("DEBIAN_FRONTEND='noninteractive' apt-get install -y -q --force-yes postfix")

    sudo ("mkdir /opt/regluit")
    sudo ("chown ubuntu:ubuntu /opt/regluit")

    run('git config --global user.name "Raymond Yee"')
    run('git config --global user.email "rdhyee@gluejar.com"')

    run('ssh-keygen -b 2048 -t rsa -f /home/ubuntu/.ssh/id_rsa -P ""')

    # how to get the key and push it to github
    s = StringIO()
    get('/home/ubuntu/.ssh/id_rsa.pub', s)
    repo = g.get_repo(GITHUB_REPO_NAME)
    key = repo.create_key('test deploy key', s.getvalue())    
    
    # http://debuggable.com/posts/disable-strict-host-checking-for-git-clone:49896ff3-0ac0-4263-9703-1eae4834cda3
    run('echo -e "Host github.com\n\tStrictHostKeyChecking no\n" >> ~/.ssh/config')
    
    # clone the regluit git repo into /opt/regluit
    with cd("/opt"):
        run("yes | git clone git@github.com:Gluejar/regluit.git")
        
    #  for configuring local mysql server (5.5)
    #  http://stackoverflow.com/a/7740571/7782
    sudo("debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password password {0}'".format(MYSQL_ROOT_PW))
    sudo("debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password_again password {0}'".format(MYSQL_ROOT_PW))
    sudo("apt-get -y install mysql-server")
    
    
def test_mysql_connection():
    # test connectivity to mysql-server
    command = """mysql -h 127.0.0.1 --user=root --password=unglueit_pw_123   <<'EOF'

SHOW VARIABLES;
EOF
"""
    run(command)   
    
def override_for_gluejar_repo():
    # https://github.com/Gluejar/gluejar_dot_com/settings/keys
    from StringIO import StringIO
    from django.conf import settings 
    
    
    GITHUB_REPO_NAME_2 = "Gluejar/gluejar_dot_com"
    
    from github import Github
    # can use 3 different types of authn: https://github.com/jacquev6/PyGithub/issues/15
    # can be empty, username/pw, or personal API token (https://github.com/blog/1509-personal-api-tokens)
    g = Github(settings.GITHUB_AUTH_TOKEN)
    
    s = StringIO()
    get('/home/ubuntu/.ssh/id_rsa.pub', s)
    repo = g.get_repo(GITHUB_REPO_NAME_2)
    key = repo.create_key('test deploy key', s.getvalue()) 
    
    # clone repo
    
    sudo ("mkdir /opt/gluejar_dot_com")
    sudo ("chown ubuntu:ubuntu /opt/gluejar_dot_com")
    # clone the regluit git repo into /opt/regluit
    with cd("/opt"):
        run("yes | git clone git@github.com:Gluejar/gluejar_dot_com.git")
        
    
    # create gdc db an user
    
    command = """mysql -h 127.0.0.1 --user=root --password=unglueit_pw_123   <<'EOF'

CREATE DATABASE gdc CHARACTER SET utf8 COLLATE utf8_bin;
CREATE USER 'gdc'@'localhost' IDENTIFIED BY 'gdc';

FLUSH PRIVILEGES;

GRANT ALL PRIVILEGES ON gdc.* TO 'gdc'@'localhost' WITH GRANT OPTION; 
EOF
"""
    run(command)       
    
    
def deploy_next():
     pass
        
    
#hosts = ['ubuntu@ec2-75-101-232-46.compute-1.amazonaws.com']
hosts = ["ubuntu@{0}".format(instance.dns_name)]

fabric.tasks.execute(deploy_next, hosts=hosts)

# Out[6]:
#     [ubuntu@ec2-50-17-12-93.compute-1.amazonaws.com] Executing task 'deploy_next'
#     [ubuntu@ec2-50-17-12-93.compute-1.amazonaws.com] run: mysql -h 127.0.0.1 --user=root --password=unglueit_pw_123   <<'EOF'
#     
#     CREATE DATABASE gdc CHARACTER SET utf8 COLLATE utf8_bin;
#     CREATE USER 'gdc'@'localhost' IDENTIFIED BY 'gdc';
#     
#     FLUSH PRIVILEGES;
#     
#     GRANT ALL PRIVILEGES ON gdc.* TO 'gdc'@'localhost' WITH GRANT OPTION; 
#     EOF
#     
#     [ubuntu@ec2-50-17-12-93.compute-1.amazonaws.com] out: ERROR 1007 (HY000) at line 2: Can't create database 'gdc'; database exists
#     [ubuntu@ec2-50-17-12-93.compute-1.amazonaws.com] out: 
#     
# 

    An exception has occurred, use %tb to see the full traceback.

    SystemExit: 1


#     
#     Fatal error: run() received nonzero return code 1 while executing!
#     
#     Requested: mysql -h 127.0.0.1 --user=root --password=unglueit_pw_123   <<'EOF'
#     
#     CREATE DATABASE gdc CHARACTER SET utf8 COLLATE utf8_bin;
#     CREATE USER 'gdc'@'localhost' IDENTIFIED BY 'gdc';
#     
#     FLUSH PRIVILEGES;
#     
#     GRANT ALL PRIVILEGES ON gdc.* TO 'gdc'@'localhost' WITH GRANT OPTION; 
#     EOF
#     
#     Executed: /bin/bash -l -c "mysql -h 127.0.0.1 --user=root --password=unglueit_pw_123   <<'EOF'
#     
#     CREATE DATABASE gdc CHARACTER SET utf8 COLLATE utf8_bin;
#     CREATE USER 'gdc'@'localhost' IDENTIFIED BY 'gdc';
#     
#     FLUSH PRIVILEGES;
#     
#     GRANT ALL PRIVILEGES ON gdc.* TO 'gdc'@'localhost' WITH GRANT OPTION; 
#     EOF
#     "
#     
#     Aborting.
#     To exit: use 'exit', 'quit', or Ctrl-D.

# ## Commands to add?
# 
# By the time we run through a lot of the fabric script, a reboot of the system is required.  After installing mysql locally, it seems that the instance needs to be rebooted.  Here's some code to do so.  Problem remaining is how to reboot, wait for reboot to be completed, and then pick up the next steps.
# 
# I could issue a fabric command to apply security upgrade: `sudo unattended-upgrade`
# 
# or 
# 
# I think there is a boto command to restart instance
# 
#     *  `sudo unattended-upgrade`
# 

# In[ ]:
rebooted_instance = instance.reboot()
rebooted_instance

# In[ ]:
# looks like reboot works, but that the instance status remains running throughout time reboot happens...
# maybe we wait a specific amount of time and the try to connect 

## hand-installing things for expedient job on gluejar.com

# * git repo

## EC2 security groups

# * listing key existing security groups
# * how to copy parameters
# 
# 

# In[ ]:
# security groups


security_groups = aws.ec2.get_all_security_groups()
security_groups

# In[ ]:
# pull out the security group used for unglue.it

web_prod_sgroup = [(group.id, group.name, group.description, group.rules) for group in security_groups if group.name=='web-production'][0]

# In[ ]:
web_prod_sgroup

# In[ ]:
# http://boto.readthedocs.org/en/latest/security_groups.html
rules = web_prod_sgroup[3]
[(rule.ip_protocol, rule.from_port, rule.to_port, rule.grants, rule.groups) for rule in rules]

# In[ ]:
[(grant.cidr_ip) for grant in rule.grants]

# In[ ]:
[(grant.owner_id, grant.group_id, grant.name, grant.cidr_ip) for grant in rule.grants]

# In[ ]:
# let's make a new security group to replicate the web-production sg

test8_sg = aws.ec2.create_security_group('test8', 'test8 sg')

# In[ ]:
# You need to pass in either src_group_name OR ip_protocol, from_port, to_port, and cidr_ip.

test8_sg.authorize('tcp', 80, 80, '0.0.0.0/0')
test8_sg.authorize('tcp', 22, 22, '0.0.0.0/0')
test8_sg.authorize('tcp', 443, 443, '0.0.0.0/0')

# In[ ]:
test9_sg = aws.ec2.create_security_group('test9', 'test9 sg')

# In[ ]:
test9_sg.authorize(src_group=test8_sg)

# In[ ]:
test8_sg.rules

# In[ ]:
rules = test9_sg.rules
rule = rules[0]
grant = rule.grants[0]

# In[ ]:
(rule.ip_protocol, rule.from_port, rule.to_port, rule.grants)

# In[ ]:
grant.owner_id, grant.group_id, grant.name, grant.cidr_ip

# In[ ]:
test9_sg = [(group.id, group.name, group.description, group.rules) for group in security_groups if group.name=='test9'][0]

# In[ ]:
rules = test9_sg[3]
[(rule.ip_protocol, rule.from_port, rule.to_port, [(grant.owner_id, grant.group_id, grant.name, grant.cidr_ip) for grant in rule.grants], rule.groups) for rule in rules]

# In[ ]:
aws.ec2.authorize_security_group(group_name='test8', ip_protocol='tcp', from_port=80, to_port=80, cidr_ip='0.0.0.0/0')

# In[ ]:
# let's compute the instances that are tied to the various security groups
# http://boto.readthedocs.org/en/latest/ref/ec2.html#module-boto.ec2.securitygroup
# This calculation is useful for reconstructing the relationships among instances and security groups


from boto.ec2 import securitygroup

for security_group in aws.ec2.get_all_security_groups():
    sg = securitygroup.SecurityGroup(name=security_group.name, connection=aws.ec2)
    print security_group, [inst.id for inst in sg.instances()]


# In[ ]:
# with the exception of frontend-lb, let's delete the security groups that have no attached instances 

for sg in [sg for sg in aws.ec2.get_all_security_groups() if len(sg.instances()) == 0 and sg.name != 'frontend-lb']:
    print sg.name, sg.id, aws.ec2.delete_security_group(group_id=sg.id)

## Setting up MySQL

# * plain old mysql on the server ( https://help.ubuntu.com/12.04/serverguide/mysql.html )
# * RDS parameters to figure out
# 
# to run mysql on server -- if you didn't have to worry about interactivity:
# 
# > `sudo apt-get install mysql-server`

# In[ ]:
"ubuntu@{0}".format(inst.dns_name)

# In[ ]:
# once mysql installed, how to test the basic connectivity?



# <pre>
# sudo debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password password unglueit_pw_123'
# sudo debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password_again password unglueit_pw_123'
# sudo apt-get -y install mysql-server
# </pre>
# 
# <pre>
# mysql -h 127.0.0.1 --user=root --password=unglueit_pw_123 
# </pre>

#     mysql -h 127.0.0.1 --user=root --password=unglueit_pw_123   <<'EOF'
# 
#     SHOW DATABASES;
#     EOF
# 
# 

## Creating an Image out of Instance

# In[ ]:
instance.id

# In[ ]:
new_image = aws.ec2.create_image(instance.id, "script_built_after_local_mysql_2013-05-24", 
     description="next step figure out RDS")

# In[ ]:
# sometimes it really does take a surprisingly long time to make an image out of an instance

# new_image = aws.ec2.get_image(image_id=u'ami-853a51ec')
new_image

# In[ ]:
new_image = aws.ec2.get_image(new_image)

# In[ ]:
new_image.state

# Fire up an instance

# In[ ]:
(instance, cmd) = aws.launch_instance(ami=u'ami-853a51ec', 
                                      instance_type='t1.micro',
                                      key_name='rdhyee_public_key',
                                      group_name=SECURITY_GROUP_NAME,
                                      tag='new_instance',
                                      cmd_shell=False) 


## RDS

# http://calculator.s3.amazonaws.com/calc5.html can be used to estimate costs
# 
# A barebones micro rds costs about $20/month
# 
# References:
# 
# * [boto rds intro](http://boto.readthedocs.org/en/latest/rds_tut.html)
# * [boto rds api ref](http://boto.readthedocs.org/en/latest/ref/rds.html)

# In[ ]:
dbs = aws.all_rds()
dbs

# In[ ]:

db = dbs[1]
(db.id, db.allocated_storage, db.instance_class, db.engine, db.master_username, 
 db.parameter_group, db.security_group, db.availability_zone, db.multi_az)

# In[ ]:
# I forgot I already have a working rds db info displayer
aws.db_info(db)

# In[ ]:
# parameter group
# http://boto.readthedocs.org/en/latest/ref/rds.html#module-boto.rds.parametergroup

# I think functionality is more primitive

# In[ ]:
pg = aws.rds.get_all_dbparameters('production1')

# In[ ]:
rds = aws.rds

def parameter_group_iteritems(group_name):

    first_page = True
    get_next_page = True
    
    while get_next_page:
        if first_page:
            pg = rds.get_all_dbparameters(group_name)
            first_page = False
        else:
            pg = rds.get_all_dbparameters(group_name, marker = pg.Marker)
            
        for key in pg.keys():
            yield (key, pg[key])
    
        get_next_page = hasattr(pg, 'Marker')


# In[ ]:
# try to turn parameter group into a dict to enable reproducibiity of group

pg_dict = {}
for (key, param) in parameter_group_iteritems('production1'):
    try:
        key, {'name':param.name, 'type':param.type, 'description':param.description, 'value':param.value}
        pg_dict[key] = {'name':param.name, 'type':param.type, 'description':param.description, 'value':param.value}
    except Exception as e:
        print key, e


# In[ ]:
sorted(pg_dict.keys())

# In[ ]:
# https://github.com/boto/boto/blob/2.8.0/boto/rds/parametergroup.py#L71

param = pg_dict.get('character_set_database')
{'name':param["name"], 'type':param["type"], 'description':param["description"], 'value':param["value"]}

# In[ ]:
# security group

# In[ ]:
# how to create RDS
# db = conn.create_dbinstance("db-master-1", 10, 'db.m1.small', 'root', 'hunter2')

## IAM

# good to get an automated handle of the IAM groups and users.  To use boto to manage IAM, you will need to have AWS keys with sufficient permissions.

# In[ ]:
from regluit.sysadmin import aws
iam = aws.boto.connect_iam()


IAM_POWER_USER_PERMISSION = """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "NotAction": "iam:*",
      "Resource": "*"
    }
  ]
}"""


# get group names

def all_iam_group_names():
    return [g.group_name for g in iam.get_all_groups()['list_groups_response']['list_groups_result']['groups']]

# get user names

def all_iam_user_names():
    return [u.user_name for u in iam.get_all_users()[u'list_users_response'][u'list_users_result']['users']]

# mapping between groups and users
# list users and their corresponding groups.

def iam_group_names_for_user(user_name):
    return [g.group_name for g in iam.get_groups_for_user(user_name)['list_groups_for_user_response'][u'list_groups_for_user_result']['groups']]

# for given groups, list corresponding users

def iam_user_names_for_group(group_name):
    return [u.user_name for u in iam.get_group(group_name=group_name)[u'get_group_response'][u'get_group_result']['users']]

# find keys associated with user

def access_keys_for_user_name(user_name):
    keys = iam.get_all_access_keys(user_name=user_name)['list_access_keys_response'][u'list_access_keys_result']['access_key_metadata']
    return keys

# can we use IAM to create new IAM user and get the key / secret?

def create_iam_user(user_name, generate_key=True):
    iam_user = iam.create_user(user_name=user_name)
    if generate_key:
        key_output = iam.create_access_key(user_name=user_name)
        access_key = key_output['create_access_key_response']['create_access_key_result']['access_key']
        (key, secret) = (access_key['access_key_id'], access_key['secret_access_key'])
        return (iam_user, key, secret)
    else:
        return (iam_user, key, None, None)

def delete_iam_user(user_name):
    
    # check to see whether there is such a user_name.
    try:
        iam.get_user(user_name)
    except boto.exception.BotoServerError as e:
        return None

    # delete associated keys
    
    keys = access_keys_for_user_name(user_name)
    
    for key in keys:
        # print key.access_key_id, key.status
        iam.delete_access_key(access_key_id=key.access_key_id, user_name=user_name)
        #result = iam.update_access_key(access_key_id=key.access_key_id, user_name=user_name, status='Inactive')
        
    # also need to delete associated policies
    
    policy_names = iam_policy_names_for_user(user_name)
    
    for policy_name in policy_names:
        iam.delete_user_policy(user_name=user_name,policy_name=policy_name)
        
    # once the keys associated with the user are deleted, then proceed to delete the user

    result = iam.delete_user(user_name)
    return result
    
# policies

def iam_policy_names_for_group(group_name):
    return iam.get_all_group_policies(group_name=group_name)['list_group_policies_response'][u'list_group_policies_result']['policy_names']

def iam_policy_names_for_user(user_name):
    return iam.get_all_user_policies(user_name=user_name)['list_user_policies_response'][u'list_user_policies_result']['policy_names']

def policy_document(policy_name, user_name=None, group_name=None):
    if group_name is not None:
        document = iam.get_group_policy(group_name=group_name, policy_name=policy_name)[u'get_group_policy_response'][u'get_group_policy_result'][u'policy_document']
        return urlparse.parse_qs("policy={0}".format(document))['policy'][0]
    if user_name is not None:
        document = iam.get_user_policy(user_name=user_name, policy_name=policy_name)[u'get_user_policy_response'][u'get_user_policy_result'][u'policy_document']
        return urlparse.parse_qs("policy={0}".format(document))['policy'][0]
    
# get general IAM stats

(iam.get_account_summary(), all_iam_group_names(), all_iam_user_names(),
 iam_group_names_for_user('eric'), iam_user_names_for_group('gluejar'),
 access_keys_for_user_name('ry-dev')
 )



# In[ ]:
# test -> grab all groups and list of corresponding users

for g in all_iam_group_names():
    print g, iam_user_names_for_group(g)

# In[ ]:
# list all keys by looping through users

for u in all_iam_user_names():
    print u, [(k.access_key_id, k.status) for k in access_keys_for_user_name(u)]

# In[ ]:
# look at permission structures of groups and users

from urllib import urlencode
import urlparse

policy_names = iam_policy_names_for_group('gluejar')

for p in policy_names:
    print policy_document(group_name='gluejar', policy_name=p)
    


# In[ ]:
iam_user, key, secret = create_iam_user('ry-dev-3', True)
iam.put_user_policy( user_name='ry-dev-3', policy_name='power_user_2013-06-12', policy_json=IAM_POWER_USER_PERMISSION)

# In[ ]:
# write out a shell script for configuring the environment with the keys for AWS

print """#!/bin/bash


export AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}

# EC2 API tools
export EC2_ACCESS_KEY=$AWS_ACCESS_KEY_ID
export EC2_SECRET_KEY=$AWS_SECRET_ACCESS_KEY""".format(**{'AWS_SECRET_ACCESS_KEY':secret, 'AWS_ACCESS_KEY_ID':key})

# In[ ]:
[policy_document(p, user_name='ry-dev-3') for p in iam_policy_names_for_user('ry-dev-3')]

# In[ ]:
delete_iam_user(user_name='ry-dev-3')

# # Different ways to pass in AWS keys to boto
# 
# http://boto.readthedocs.org/en/latest/boto_config_tut.html
# 
# * Credentials passed into Connection class constructor.
# * Credentials specified by environment variables
# * Credentials specified as options in the config file.
# 

# <pre>
# 
# #!/bin/bash
# 
# export AWS_ACCESS_KEY={AWS_ACCESS_KEY}
# export AWS_SECRET_KEY={AWS_SECRET_KEY}
# 
# # EC2 API tools
# export EC2_ACCESS_KEY=$AWS_ACCESS_KEY
# export EC2_SECRET_KEY=$AWS_SECRET_KEY
# 
# </pre>
# 

# In[ ]:
%%bash
# something to convert this notebook to Python source
cd /Users/raymondyee/D/Document/Gluejar/Gluejar.github/regluit; python ~/C/src/nbconvert/nbconvert.py python build_ec2_instances_for_django.ipynb

# In[ ]:
import fabric
from fabric.api import run, local, env, cd, sudo
from fabric.operations import get


def run_on_ry_dev():

    run("ls -lt")   
    
hosts = ["ubuntu@ry-dev.unglue.it"]

fabric.tasks.execute(run_on_ry_dev, hosts=hosts)

# In[ ]:
instance.state
