regluit - "The Unglue.it web application and website"
=======

This repo - https://github.com/EbookFoundation/regluit will be the place for collaborative development for Unglue.it. Add issues and submit pull requests here. As of January 19, 2017, https://github.com/Gluejar/regluit is still being used for production builds.

The first version of the unglue.it codebase was a services-oriented project named "unglu".
We decided that "unglu" was too complicated, so we started over and named the new project "regluit".
regluit is a Django project that
contains four main applications: `core`, `frontend`, `api` and `payment` that can be deployed
and configured on as many ec2 instances that are needed to support traffic.
The partitioning between these modules is not as clean as would be ideal. `payment` is particularly messy because we had to retool it twice because we had to switch from Paypal to Amazon Payments to Stripe.

regluit was originally developed on Django 1.3 (python 2.7) and currently runs on Django 1.8.

Develop
-------

Here are some instructions for setting up regluit for development on
an Ubuntu system. If you are on OS X see notes below
to install python-setuptools in step 1:

1. Ensure MySQL and Redis are installed & running on your system.
1. Create a MySQL database and user for unglueit.
1. `sudo apt-get upgrade gcc`
1. `sudo apt-get install python-setuptools git python-lxml build-essential libssl-dev libffi-dev python2.7-dev libxml2-dev libxslt-dev libmysqlclient-dev`
1. `sudo easy_install virtualenv virtualenvwrapper`
1. `git clone git@github.com:Gluejar/regluit.git`
1. `cd regluit`
1. `mkvirtualenv regluit`
1. `pip install -r requirements_versioned.pip`
1. `add2virtualenv ..`
1. `cp settings/dev.py settings/me.py`
1. `mkdir settings/keys/`
1. `cp settings/dummy/* settings/keys/`
1. Edit `settings/me.py` with proper mysql and redis configurations.
1. Edit  `settings/keys/common.py` and `settings/keys/host.py` with account and key information OR if you have the ansible vault password, run `ansible-playbook create_keys.yml` inside the vagrant directory.
1. `echo 'export DJANGO_SETTINGS_MODULE=regluit.settings.me' >> ~/.virtualenvs/regluit/bin/postactivate`
1. `deactivate ; workon regluit`
1. `django-admin.py migrate --noinput`
1. `django-admin.py loaddata core/fixtures/initial_data.json core/fixtures/bookloader.json` populate database with test data to run properly.
1. `django-admin.py celeryd --loglevel=INFO` start the celery daemon to perform asynchronous tasks like adding related editions, and display logging information in the foreground.
1. `django-admin.py celerybeat -l INFO` to start the celerybeat daemon to handle scheduled tasks.
1. `django-admin.py runserver 0.0.0.0:8000` (you can change the port number from the default value of 8000)
1. make sure a [redis server](https://redis.io/topics/quickstart) is running
1. Point your browser to http://localhost:8000/

CSS development

1. We used Less version 2.8 for CSS. http://incident57.com/less/. We use minified CSS.
1. New CSS development is using SCSS. Install libsass and django-compressor.

Production Deployment
---------------------

OBSOLETE
Below are the steps for getting regluit running on EC2 with Apache and mod_wsgi, and talking to an Amazon Relational Data Store instance.
Instructions for setting please are slightly different.

1. create an ubuntu ec2 instance (e.g, go http://alestic.com/ to find various ubuntu images)
1. `sudo aptitude update`
1. `sudo aptitude upgrade`
1. `sudo aptitude install git-core apache libapache2-mod-wsgi mysql-client python-virtualenv python-mysqldb redis-server python-lxml postfix python-dev libmysqlclient-dev`
1. `sudo mkdir /opt/regluit`
1. `sudo chown ubuntu:ubuntu /opt/regluit`
1. `cd /opt`
1. `git config --global user.name "Raymond Yee"`
1. `git config --global user.email "rdhyee@gluejar.com"`
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
1. `pip install -r requirements_versioned.pip`
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
1. `sudo mkdir /var/run/celery`
1. `sudo chown celery:celery /var/log/celery /var/run/celery`
1. `sudo /etc/init.d/celeryd start`
1. `sudo cp deploy/celerybeat /etc/init.d/celerybeat`
1. `sudo chmod 755 /etc/init.d/celerybeat`
1. `sudo cp deploy/celerybeat.conf /etc/default/celerybeat`
1. `sudo mkdir /var/log/celerybeat`
1. `sudo chown celery:celery /var/log/celerybeat`
1. `sudo /etc/init.d/celerybeat start`

## setup to enable ckeditor to work properly

1. `mkdir /var/www/static/media/`
1. `sudo chown ubuntu:www-data /var/www/static/media/`


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

If you get 'EnvironmentError: mysql_config not found'
edit the line ~/.virtualenvs/regluit/build/MySQL-python/setup_posix.py
1. mysql_config.path = "mysql_config"
to be (using a path that exists on your system)
1. mysql_config.path = "/usr/local/mysql-5.5.20-osx10.6-x86_64/bin/mysql_config"

You may need to set utf8 in /etc/my.cnf
collation-server = utf8_unicode_ci

    init-connect='SET NAMES utf8'
    character-set-server = utf8

Selenium Install
---------------

Download the selenium server:
http://selenium.googlecode.com/files/selenium-server-standalone-2.5.0.jar

Start the selenium server:
'java -jar selenium-server-standalone-2.5.0.jar'

MARC Records
------------

### For unglued books with existing print edition MARC records
1. Get the MARCXML record for the print edition from the Library of Congress.
    1. Find the book in [catalog.loc.gov](http://catalog.loc.gov/)
    1. Click on the permalink in its record (will look something like [lccn.loc.gov/2009009516](http://lccn.loc.gov/2009009516))
    1. Download MARCXML
1. At /marc/ungluify/ , enter the _unglued edition_ in the Edition field, upload file, choose license
1. The XML record will be automatically...
    * converted to suitable MARCXML and .mrc records, with both direct and via-unglue.it download links
    * written to S3
    * added to a new instance of MARCRecord
    * provided to ungluers at /marc/

### For CC/PD books with existing records that link to the ebook edition
1. Use /admin to create a new MARC record instance
1. Upload the MARC records to s3 (or wherever)
1. Add the URLs of the .xml and/or .mrc record(s) to the appropriate field(s)
1. Select the relevant edition
1. Select an appropriate marc_format:
    * use DIRECT if it links directly to the ebook file
    * use UNGLUE if it links to the unglue.it download page
    * if you have records with both DIRECT and UNGLUE links, you'll need two MARCRecord instances
    * if you have both kinds of link, put them in _separate_ records, as marc_format can only take one value    
`ungluify_record.py` should only be used to modify records of print editions of unglued ebooks.  It will not produce appropriate results for CC/PD ebooks.

### For unglued ebooks without print edition MARC records, or CC/PD books without ebook MARC records
1. Get a contract cataloger to produce quality records (.xml and .mrc formats)
    * we are using ung[x] as the format for our accession numbers, where [x] is the id of the MARCRecord instance, plus leading zeroes
1. Upload those records to s3 (or wherever)
1. Create a MARCRecord instance in /admin
1. Add the URLs of the .xml and .mrc records to the appropriate fields
1. Select the relevant edition
1. Select an appropriate marc_format:
    * use DIRECT if it links directly to the ebook file
    * use UNGLUE if it links to the unglue.it download page
    * if you have records with both DIRECT and UNGLUE links, you'll need two MARCRecord instances
    * if you have both kinds of link, put them in _separate_ records, as marc_format can only take one value


# vagrant / ansible

[How to build machines using Vagrant/ansible](docs/vagrant_ansible.md)
