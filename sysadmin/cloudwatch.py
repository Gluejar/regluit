from pprint import pprint
import boto

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
    
def modify_please1_pg_group():
    """kinda ugly
    http://stackoverflow.com/a/9085381/7782
    After doing this, I changed please db to talk to this parameter group and rebooted db
    """
    pg = conn.get_all_dbparameters('mygroup')
    pg2 = rds.get_all_dbparameters('mygroup', marker = pg.Marker)
    pg2['tx_isolation'].value = True
    pg2['tx_isolation'].apply(True)
    
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
    
if __name__ == '__main__':
    pprint (stats_for_instances(all_instances()))
    web1 = instance('web1')
    print instance_metrics(web1)

