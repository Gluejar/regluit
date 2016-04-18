from fabric.api import run, local, env, cd

from regluit.sysadmin import aws

# allow us to use our ssh config files (e.g., ~/.ssh/config)
env.use_ssh_config = True

DATA_BACKUP_ACCOUNT = 'b235656@hanjin.dreamhost.com'

def rydev():
    """An example of using a function to define a host and use that definition in a command
    to run:
    
        fab rydev list_dir
    """
    
    env.hosts = ['ec2-107-21-211-134.compute-1.amazonaws.com']
    env.user = 'ubuntu'

def fps_key_local():
    """ """
    pass

def update_prod():
    """Updates the production serve by running /opt/regluit/deploy/update-prod"""
    with cd("/opt/regluit"):
        run("./deploy/update-prod")

def backup_db(name='unglue.it', server=DATA_BACKUP_ACCOUNT):
    """backup database on unglue.it or please with name to server"""
    run("""TS=`date +"%Y-%m-%dT%H:%M:%S"`; /home/ubuntu/dump.sh | gzip > {0}.${{TS}}.sql.gz; scp ./{0}.${{TS}}.sql.gz  {1}: ; rm -f {0}.${{TS}}.sql.gz""".format(name, server))

def list_backups(name='unglue.it', server=DATA_BACKUP_ACCOUNT):
    local("""echo "ls -lt {0}.*" | sftp {1}""".format(name, server))

def get_dump():
    """Dump the current db on remote server and scp it over to local machine.
    Note:  web1 has been hardcoded here to represent the name of the unglue.it server
    """
    run("./dump.sh > unglue.it.sql ")
    run("gzip -f unglue.it.sql")
    local("scp web1:/home/ubuntu/unglue.it.sql.gz .")
    local("gunzip -f unglue.it.sql.gz")
    
def copy_dump_to_ry_dev():
    """Dump the current db on remote server and scp it over to ry-dev.
    Note:  web1 has been hardcoded here to represent the name of the unglue.it server
    """
    run("./dump.sh > unglue.it.sql ")
    run("scp unglue.it.sql ry-dev.dyndns.org:")    
    
    
def build_prod_instance(ami_id='ami-a29943cb'):
    """Build a new instance to serve as server instance for unglue.it"""
    # http://my.safaribooksonline.com/book/-/9781449308100/2dot-ec2-recipes/id2529379
    # default ami-a29943cb' is Ubuntu 12.04 Precise EBS boot

def ecdsa():
    """Calculate the host ECSDA host fingerprint http://bridge.grumpy-troll.org/2011/01/openssh.html """
    run("""ssh-keygen -f /etc/ssh/ssh_host_ecdsa_key.pub -l""")
    
def ssh_fingerprint():
    """display ssh fingerprint of /etc/ssh/ssh_host_rsa_key.pub on remote machine"""
    run ("""ssh-keygen -l -f /etc/ssh/ssh_host_rsa_key.pub""")

def set_key_ry(name,value):
    """ry-dev is configured differently!"""
    with cd("/home/ubuntu"):
        run("""source /home/ubuntu/.virtualenvs/regluit/bin/activate; django-admin.py set_key {0} {1} --settings=regluit.settings.me""".format(name, value))
    
def set_key(name, value):
    """set encrypted key via the remote Django command -- works for web1, just, please"""
    with cd("/opt/regluit"):
        run("""source ENV/bin/activate; django-admin.py set_key {0} "{1}" --settings=regluit.settings.me""".format(name, value))
 
def ssh_fingerprint2():
    # http://stackoverflow.com/a/6682934/7782
    import base64,hashlib
    def lineToFingerprint(line):
        key = base64.b64decode(line.strip().partition('ssh-rsa ')[2])
        fp_plain = hashlib.md5(key).hexdigest()
        return ':'.join(a+b for a,b in zip(fp_plain[::2], fp_plain[1::2]))

def public_key_from_private_key():
    # ssh-keygen -y -f ~/.ssh/id_rsa
    pass
            
def email_addresses():
    """list email addresses in unglue.it"""
    with cd("/opt/regluit"):
        run("""source ENV/bin/activate; echo "import django; print ' \\n'.join([u.email for u in django.contrib.auth.models.User.objects.all() ]); quit()" | django-admin.py shell_plus --settings=regluit.settings.me > /home/ubuntu/emails.txt""")
    local("scp web1:/home/ubuntu/emails.txt .")
    run("""rm /home/ubuntu/emails.txt""")
    
def selenium():
    """setting up selenium to run in the background on RY's laptop"""
    with cd('/Users/raymondyee/D/Document/Gluejar/Gluejar.github/regluit'):
        local("java -jar test/selenium-server-standalone-2.53.0.jar > selenium-rc.log 2>&1 &")
        
def test():
    """run regluit tests locally"""
    local("django-admin.py test core api frontend payment")

def list_dir():
    """A simple command to do a ls on /home/ubuntu/regluit """
    code_dir = '/home/ubuntu/regluit'
    with cd(code_dir):
        run("ls")

def reboot():
    """Reboot from the command line -- USE WITH CARE"""
    run("sudo shutdown -r now")

def host_type():
    run('uname -s')
