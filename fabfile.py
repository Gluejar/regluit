from fabric.api import run, local, env, cd

env.use_ssh_config = True
#env.hosts = ['ry-dev']

# fab rydev list_dir
# http://aws.amazon.com/articles/3997

key_path = '/Users/raymondyee/.ssh/id_rsa'

def rydev():
    env.hosts = ['ec2-107-21-211-134.compute-1.amazonaws.com']
    env.user = 'ubuntu'
    env.key_filename = key_path    

def get_dump():
    run("./dump.sh > unglue.it.sql ")
    run("gzip -f unglue.it.sql")
    local("scp web1:/home/ubuntu/unglue.it.sql.gz .")
    local("gunzip -f unglue.it.sql.gz")
        
def selenium():
    with cd('/Users/raymondyee/D/Document/Gluejar/Gluejar.github/regluit'):
        local("java -jar test/selenium-server-standalone-2.20.0.jar > selenium-rc.log 2>&1 &")
        
def test():
    local("django-admin.py test core api frontend payment")
    
def fetch():
    local("git fetch")

def list_dir():
    code_dir = '/home/ubuntu/regluit'
    with cd(code_dir):
        run("ls")

def list_dir2():
    code_dir = '/opt/regluit'
    with cd(code_dir):
        run("ls")            

def hello(name="world"):
    print("Hello %s!" % name)

def host_type():
    run('uname -s')