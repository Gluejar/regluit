from pprint import pprint

import os
import time
import boto
import boto.manage.cmdshell

# connect up parts of the Amazon infrastructure

# notes: to delete snapshots I have made of instances, one has to deregister the AMI first and then delete the snapshot

GLUEJAR_ACCOUNT_ID = 439256357102

ec2 = boto.connect_ec2()
cw = boto.connect_cloudwatch()
rds = boto.connect_rds()

def all_instances():
    reservations = ec2.get_all_instances()
    instances = [i for r in reservations for i in r.instances]
    return instances

def all_zones():
    print ec2.get_all_zones()
    
def all_rds():
    return rds.get_all_dbinstances()
    
def all_rds_parameter_groups():
    return rds.get_all_dbparameter_groups()
    
def modify_rds_parameter(group_name, parameter, value, apply_immediate=False):
    """change parameter in RDS parameter group_name to value
    http://stackoverflow.com/a/9085381/7782
    Remember to make sure that the parameter group is actually associated with the db.
    You will likely need to reboot db too.
    """
    
    pg = rds.get_all_dbparameters(group_name)
    while not pg.has_key(parameter) and hasattr(pg, 'Marker'):
        pg = rds.get_all_dbparameters(group_name, marker = pg.Marker)
    if pg.has_key(parameter):
        pg[parameter].value = value
        pg[parameter].apply(immediate=apply_immediate)
        return True
    else:
        return False

# how I associated the param_group to a db and then rebooted db
# rds.modify_dbinstance(id='production', param_group='production1', apply_immediately=True)
# rds.reboot_dbinstance(id='production')
    
def all_snapshots(owner=GLUEJAR_ACCOUNT_ID):
    """by default, return only snapshots owned by Gluejar  -- None returns all snapshots available to us"""
    return ec2.get_all_snapshots(owner=owner)

def instance(tag_name):
    try:
        return ec2.get_all_instances(filters={'tag:Name' : tag_name})[0].instances[0]
    except Exception, e:
        return None
    
def all_images(owners=(GLUEJAR_ACCOUNT_ID, )):
    return ec2.get_all_images(owners=owners)
    
def stop_instances(instances):
    return ec2.stop_instances(instance_ids=[instance.id for instance in instances])


def console_output(instance):
    """returnn console output of instance"""
    try:
        return instance.get_console_output().output
    except Exception, e:
        return None

def instance_metrics(instance):
    """metrics that apply to given instance"""
    metrics = cw.list_metrics() 
    my_metrics = []
    
    for metric in metrics: 
        if 'InstanceId' in metric.dimensions:
            if instance.id in metric.dimensions['InstanceId']:
                my_metrics.append(metric)
    
    return my_metrics
    
# how to get average CPU utilization of web1?
# filter(lambda x: x.name == 'CPUUtilization', m)
# metric.query(start_time, end_time,'Average', period=6000)

def instance_metric(instance, metric_name):
    m = instance_metrics(instance)
    return filter(lambda x: x.name == metric_name, m)

def launch_time(instance):
    return boto.utils.parse_ts(instance.launch_time)
    
def max_cpu(instance):
    pass
    
def stats_for_instances(instances=None):
    """return basic stats for input instances"""
    if instances is None:
        instances = all_instances()
    stats = []
    for instance in instances:
        instance.update()  # to get latest update
        stats.append((instance.id, instance.key_name, instance.state, instance.ip_address, instance.dns_name))
    
    return stats  
 

# http://my.safaribooksonline.com/book/-/9781449308100/2dot-ec2-recipes/id2529379
def launch_instance(ami='ami-a29943cb',
                    instance_type='t1.micro',
                    key_name='rdhyee_public_key',
                    key_extension='.pem',
                    key_dir='~/.ssh',
                    group_name='default',
                    ssh_port=22,
                    cidr='0.0.0.0/0',
                    tag='paws',
                    user_data=None,
                    cmd_shell=True,
                    login_user='ubuntu',
                    ssh_pwd=None):
    """
    Launch an instance and wait for it to start running.
    Returns a tuple consisting of the Instance object and the CmdShell
    object, if request, or None.

    ami        The ID of the Amazon Machine Image that this instance will
               be based on.  Default is a 64-bit Amazon Linux EBS image.

    instance_type The type of the instance.

    key_name   The name of the SSH Key used for logging into the instance.
               It will be created if it does not exist.

    key_extension The file extension for SSH private key files.
    
    key_dir    The path to the directory containing SSH private keys.
               This is usually ~/.ssh.

    group_name The name of the security group used to control access
               to the instance.  It will be created if it does not exist.

    ssh_port   The port number you want to use for SSH access (default 22).

    cidr       The CIDR block used to limit access to your instance.

    tag        A name that will be used to tag the instance so we can
               easily find it later.

    user_data  Data that will be passed to the newly started
               instance at launch and will be accessible via
               the metadata service running at http://169.254.169.254.

    cmd_shell  If true, a boto CmdShell object will be created and returned.
               This allows programmatic SSH access to the new instance.

    login_user The user name used when SSH'ing into new instance.  The
               default is 'ubuntu'

    ssh_pwd    The password for your SSH key if it is encrypted with a
               passphrase.
    """
    cmd = None
    
    # Create a connection to EC2 service.
    # You can pass credentials in to the connect_ec2 method explicitly
    # or you can use the default credentials in your ~/.boto config file
    # as we are doing here.
    ec2 = boto.connect_ec2()

    # Check to see if specified keypair already exists.
    # If we get an InvalidKeyPair.NotFound error back from EC2,
    # it means that it doesn't exist and we need to create it.
    try:
        key = ec2.get_all_key_pairs(keynames=[key_name])[0]
    except ec2.ResponseError, e:
        if e.code == 'InvalidKeyPair.NotFound':
            print 'Creating keypair: %s' % key_name
            # Create an SSH key to use when logging into instances.
            key = ec2.create_key_pair(key_name)
            
            # AWS will store the public key but the private key is
            # generated and returned and needs to be stored locally.
            # The save method will also chmod the file to protect
            # your private key.
            key.save(key_dir)
        else:
            raise

    # Check to see if specified security group already exists.
    # If we get an InvalidGroup.NotFound error back from EC2,
    # it means that it doesn't exist and we need to create it.
    try:
        group = ec2.get_all_security_groups(groupnames=[group_name])[0]
    except ec2.ResponseError, e:
        if e.code == 'InvalidGroup.NotFound':
            print 'Creating Security Group: %s' % group_name
            # Create a security group to control access to instance via SSH.
            group = ec2.create_security_group(group_name,
                                              'A group that allows SSH access')
        else:
            raise

    # Add a rule to the security group to authorize SSH traffic
    # on the specified port.
    try:
        group.authorize('tcp', ssh_port, ssh_port, cidr)
    except ec2.ResponseError, e:
        if e.code == 'InvalidPermission.Duplicate':
            print 'Security Group: %s already authorized' % group_name
        else:
            raise

    # Now start up the instance.  The run_instances method
    # has many, many parameters but these are all we need
    # for now.
    reservation = ec2.run_instances(ami,
                                    key_name=key_name,
                                    security_groups=[group_name],
                                    instance_type=instance_type,
                                    user_data=user_data)

    # Find the actual Instance object inside the Reservation object
    # returned by EC2.

    instance = reservation.instances[0]

    # The instance has been launched but it's not yet up and
    # running.  Let's wait for its state to change to 'running'.

    print 'waiting for instance'
    while instance.state != 'running':
        print '.'
        time.sleep(5)
        instance.update()
    print 'done'

    # Let's tag the instance with the specified label so we can
    # identify it later.
    instance.add_tag(tag)

    # The instance is now running, let's try to programmatically
    # SSH to the instance using Paramiko via boto CmdShell.
    
    if cmd_shell:
        key_path = os.path.join(os.path.expanduser(key_dir),
                                key_name+key_extension)
        cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
                                                          key_path,
                                                          user_name=login_user,
                                                          ssh_pwd=ssh_pwd)
                                                            
    return (instance, cmd)

def create_dbinstance(id, allocated_storage, instance_class, master_username, master_password,
                      port=3306, engine='MySQL5.1', db_name=None,
                      param_group=None, security_groups=None, availability_zone='us-east-1c', preferred_maintenance_window=None, backup_retention_period=None, preferred_backup_window=None, multi_az=False, engine_version=None, auto_minor_version_upgrade=True):
    """
    create rds instance    
    """
    # rds-create-db-instance
    
    return rds.create_dbinstance(id, allocated_storage, instance_class, master_username, master_password, port=port, engine=engine, db_name=db_name, param_group=param_group, security_groups=security_groups, availability_zone=availability_zone, preferred_maintenance_window=preferred_maintenance_window, backup_retention_period=backup_retention_period, preferred_backup_window=preferred_backup_window, multi_az=multi_az, engine_version=engine_version, auto_minor_version_upgrade=auto_minor_version_upgrade)

def ec2instance_info(e):
    return(
        {
          'id': e.id,
          'ip_address': e.ip_address,
        }
    )
    
def db_info(db, master_password=None):
    """given an rds instance db and master_password, return basic info"""
    django_setting = {
        'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': db.id,
        'USER': db.master_username,
        'PASSWORD': master_password,
        'HOST': db.endpoint[0],
        'PORT': db.endpoint[1]
        }
    }
    return({'id': db.id,
            'allocated_storage': db.allocated_storage,
            'availability_zone':db.availability_zone,
            'instance_class': db.instance_class,
            'multi_az': db.multi_az,
            'master_username': db.master_username,
            'engine': db.engine,
            'preferred_backup_window': db.preferred_backup_window,
            'preferred_maintenance_window': db.preferred_maintenance_window,
            'backup_retention_period':db.backup_retention_period, 
            'parameter_group': db.parameter_group,
            'security_group': db.security_group,
            'endpoint':db.endpoint,
            'status':db.status,
            'create_time': db.create_time, 
            'latest_restorable_time':db.latest_restorable_time,
            'django_setting': django_setting})
 
def test_ec2_user_data(ssh_pwd=None):
    script = """#!/bin/sh
echo "Hello World.  The time is now $(date -R)!" | tee /root/output.txt
"""
    return launch_instance(user_data=script, ssh_pwd=ssh_pwd)
 
if __name__ == '__main__':
    pprint (stats_for_instances(all_instances()))
    web1 = instance('web1')
    print instance_metrics(web1)

