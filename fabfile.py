from fabric.api import run, local, env, cd

# allow us to use our ssh config files (e.g., ~/.ssh/config)
env.use_ssh_config = True

def rydev():
    """An example of using a function to define a host and use that definition in a command
    to run:
    
        fab rydev list_dir
    """
    
    env.hosts = ['ec2-107-21-211-134.compute-1.amazonaws.com']
    env.user = 'ubuntu'

def update_prod():
    """Updates the production serve by running /opt/regluit/deploy/update-prod"""
    with cd("/opt/regluit"):
        run("./deploy/update-prod")

def backup_db():
    run("""TS=`date +"%Y-%m-%dT%H:%M:%S"`; /home/ubuntu/dump.sh | gzip > unglue.it.${TS}.sql.gz; scp ./unglue.it.${TS}.sql.gz  b235656@hanjin.dreamhost.com: ; rm -f unglue.it.${TS}.sql.gz""")

def get_dump():
    """Dump the current db on remote server and scp it over to local machine.
    Note:  web1 has been hardcoded here to represent the name of the unglue.it server
    """
    run("./dump.sh > unglue.it.sql ")
    run("gzip -f unglue.it.sql")
    local("scp web1:/home/ubuntu/unglue.it.sql.gz .")
    local("gunzip -f unglue.it.sql.gz")
            
def email_addresses():
    """list email addresses in unglue.it"""
    with cd("/opt/regluit"):
        run("""source ENV/bin/activate; echo "import django; print ', '.join([u.email for u in django.contrib.auth.models.User.objects.all() ]); quit()" | django-admin.py shell_plus --settings=regluit.settings.prod""")
    
def selenium():
    """setting up selenium to run in the background on RY's laptop"""
    with cd('/Users/raymondyee/D/Document/Gluejar/Gluejar.github/regluit'):
        local("java -jar test/selenium-server-standalone-2.20.0.jar > selenium-rc.log 2>&1 &")
        
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