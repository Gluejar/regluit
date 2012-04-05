regluit
=======

A 'monolithic' alternative to [unglu](http://github.com/gluejar/unglu) 
for the unglue.it website. regluit is essentially a Django project that 
contains three applications: `frontend`, `api` and `core` that can be deployed 
and configured on as many ec2 instances that are needed to support traffic. 
The key difference with [unglu](http://github.com/gluejar/unglu) is that the 
`frontend` app is able to access database models from `core` in the same 
way that the `api` is able to...which hopefully should simplify some things.

Develop
-------

Here are some instructions for setting up regluit for development on 
an Ubuntu system. If you are on OS X see notes below 
to install python-setuptools in step 1:

1. `aptitude install python-setuptools git python-lxml` 
1. `sudo easy_install virtualenv virtualenvwrapper`
1. `git clone git@github.com:Gluejar/regluit.git`
1. `cd regluit`
1. `mkvirtualenv regluit`
1. `pip install -r requirements.pip`
1. `add2virtualenv ..`
1. `cp settings/dev.py settings/me.py`
1. edit `settings/me.py` and set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`  to your gmail username and password, if you want to see that registration emails will work properly.
1. edit `settings/me.py` and look at the facebook, twitter and google auth settings to enable federated logins from those sites
1. `echo 'export DJANGO_SETTINGS_MODULE=regluit.settings.me' >> ~/.virtualenvs/regluit/bin/postactivate`
1. `deactivate ; workon regluit`
1. `django-admin.py syncdb --migrate --noinput`
1. `django-admin.py celeryd --loglevel=INFO` start the celery daemon to perform asynchronous tasks like adding related editions, and display logging information in the foreground.`
1. `django-admin.py celerybeat -l INFO` to start the celerybeat daemon to handle scheduled tasks.
1. `django-admin.py runserver 0.0.0.0:8000` (you can change the port number from the default value of 8000)
1. point your browser at http://localhost:8000/

Production Deployment
---------------------

Below are the steps for getting regluit running on EC2 with Apache and mod_wsgi, and talking to an Amazon Relational Data Store instance.
Instructions for setting please are slightly different.

1. create an ubuntu ec2 instance (e.g, go http://alestic.com/ to find various ubuntu images)
1. `sudo aptitude update`
1. `sudo aptitude upgrade`
1. `sudo aptitude install git-core apache libapache2-mod-wsgi mysql-client python-virtualenv python-mysqldb redis-server python-lxml postfix`
1. `sudo mkdir /opt/regluit`
1. `sudo chown ubuntu:ubuntu /opt/regluit`
1. `cd /opt`
1. `git config --global user.name "Ed Summers"`
1. `git config --global user.email "ehs@pobox.com"`
1. `ssh-keygen`
1. add `~/.ssh/id\_rsa.pub` as a deploy key on github https://github.com/Gluejar/regluit/admin/keys
1. `git clone git@github.com:Gluejar/regluit.git`
1. `cd /opt/regluit`
1. create an Amazon RDS instance
1. connect to it, e.g. `mysql -u root -h gluejardb.cboagmr25pjs.us-east-1.rds.amazonaws.com -p`
1. `CREATE DATABASE unglueit CHARSET utf8;`
1. `GRANT ALL ON unglueit.\* TO ‘unglueit’@’ip-10-244-250-168.ec2.internal’ IDENTIFIED BY 'unglueit' REQUIRE SSL;`
1. update settings/prod.py with database credentials
1. `virtualenv ENV`
1. `source ENV/bin/activate`
1. `pip install -r requirements.pip`
1. `echo "/opt/" > ENV/lib/python2.7/site-packages/regluit.pth`
1. `django-admin.py syncdb --migrate --settings regluit.settings.prod`
1. `sudo mkdir /var/www/static`
1. `sudo chown ubuntu:ubuntu /var/www/static`
1. `django-admin.py collectstatic --settings regluit.settings.prod`
1. `sudo ln -s /opt/regluit/deploy/regluit.conf /etc/apache2/sites-available/regluit`
1. `sudo a2ensite regluit`
1. `sudo a2enmod ssl rewrite`
1. `cd /home/ubuntu`
1. copy SSL server key to `/etc/ssl/private/server.key`
1. copy SSL certificate to `/etc/ssl/certs/server.crt`
1. `sudo /etc/init.d/apache2 restart`
1. `sudo adduser --no-create-home celery --disabled-password --disabled-login` (just enter return for all?)
1. `sudo cp deploy/celeryd /etc/init.d/celeryd`
1. `sudo chmod 755 /etc/init.d/celeryd`
1. `sudo cp deploy/celeryd.conf /etc/default/celeryd`
1. `sudo mkdir /var/log/celery`
1. `sudo chown celery:celery /var/log/celery`
1. `sudo /etc/init.d/celeryd start`
1. `sudo cp deploy/celerybeat /etc/init.d/celerybeat`
1. `sudo chmod 755 /etc/init.d/celerybeat`
1. `sudo cp deploy/celerybeat.conf /etc/default/celerybeat`
1. `sudo mkdir /var/log/celerybeat`
1. `sudo chown celery:celery /var/log/celerybeat`
1. `sudo /etc/init.d/celerybeat start`

Updating Production
--------------------

1. Study the latest changes in the master branch, especially keep in mind how
it has [changed from what's in production](https://github.com/Gluejar/regluit/compare/production...master).
1. Update the production branch accordingly.  If everything in `master` is ready to be moved into `production`, you can just merge `master` into `production`. Otherwise, you can grab specific parts.  (How to do so is something that should probably be described in greater detail.)
1. Login to unglue.it and run [`/opt/regluit/deploy/update-prod`](https://github.com/Gluejar/regluit/blob/master/deploy/update-prod)


OS X Developer Notes
-------------------

To run regluit on OS X you should have XCode installed

Install virtualenvwrapper according 
to the process at http://blog.praveengollakota.com/47430655:

1. `sudo easy\_install pip`
1. `sudo pip install virtualenv`
1. `pip install virtualenvwrapper`

Edit or create .bashrc in ~ to enable virtualenvwrapper commands:
1. `mkdir ~/.virtualenvs`
1. Edit .bashrc to include the following lines:

    export WORKON_HOME=$HOME/.virtualenvs
    source your_path_to_virtualenvwrapper.sh_here

In the above web site, the path to virtualenvwrapper.sh was
/Library/Frameworks/Python.framework/Versions/2.7/bin/virtualenvwrapper.sh
In Snow Leopard, this may be /usr/local/bin/virtualenvwrapper.sh

Configure Terminal to automatically notice this at startup:
Terminal –> Preferences –> Settings –> Shell
Click "run command"; add `source ~/.bashrc`

Selenium Install
---------------

Download the selenium server:
http://selenium.googlecode.com/files/selenium-server-standalone-2.5.0.jar

Start the selenium server:
'java -jar selenium-server-standalone-2.5.0.jar'

