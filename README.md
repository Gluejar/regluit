regluit - "The Unglue.it web application and website"
=======

Another repo - https://github.com/EbookFoundation/regluit will eventually be the place for collaborative development for Unglue.it. Add issues and submit pull requests there. As of September 1, 2019, https://github.com/Gluejar/regluit is still being used for production builds.

The first version of the unglue.it codebase was a services-oriented project named "unglu".
We decided that "unglu" was too complicated, so we started over and named the new project "regluit".
regluit is a Django project that
contains four main applications: `core`, `frontend`, `api` and `payment` that can be deployed
and configured on as many ec2 instances that are needed to support traffic.
The partitioning between these modules is not as clean as would be ideal. `payment` is particularly messy because we had to retool it twice because we had to switch from Paypal to Amazon Payments to Stripe.

regluit was originally developed on Django 1.3 (python 2.7) and currently runs on Django 1.11 Python 3.8).

Develop
-------

Here are some instructions for setting up regluit for development on
an Ubuntu system. If you are on OS X see notes below.


- Ensure MySQL 5.7 and Redis are installed & running on your system.
1. Create a MySQL database and user for unglueit.
1. `sudo apt-get upgrade gcc`
1. `sudo apt-get install python-setuptools git python-lxml build-essential libssl-dev libffi-dev python3.8-dev libxml2-dev libxslt-dev libmysqlclient-dev`
1. `sudo easy_install virtualenv virtualenvwrapper`
1. `git clone git@github.com:Gluejar/regluit.git`
1. `cd regluit`
1. `mkvirtualenv regluit`
1. `pip install -r requirements.txt`
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
1. `redis-server` to start the task broker
1. `celery -A regluit worker --loglevel=INFO ` start the celery daemon to perform asynchronous tasks like adding related editions, and display logging information in the foreground. Add ` --logfile=logs/celery.log` if you want the logs to go into a log file.
1. `celery -A regluit beat --loglevel=INFO` to start the celerybeat daemon to handle scheduled tasks. 
1. `django-admin.py runserver 0.0.0.0:8000` (you can change the port number from the default value of 8000)
1. make sure a [redis server](https://redis.io/topics/quickstart) is running
1. Point your browser to http://localhost:8000/

CSS development

1. We used Less version 2.8 for CSS. http://incident57.com/less/. We use minified CSS.
1. New CSS development is using SCSS. Install libsass and django-compressor.

Production Deployment
---------------------

See http://github.com/EbookFoundation/regluit-provisioning

OS X Developer Notes
-------------------

To run regluit on OS X you should have XCode installed

Install MySQL:
    `brew install mysql@5.7`    
    `mysql_secure_installation`
    `mysqld_safe --user=root -p`
    

We use pyenv and pipenv to set up an environment.

Edit or create .bashrc in ~ to enable virtualenvwrapper commands:

1. `pipenv install -r requirements.txt`
1. Edit .zshrc to include the following lines:

    `eval "$(pyenv init -)"`
    `export PATH=$PATH:/Applications/Postgres.app/Contents/Versions/10/bin`
    `export PATH=$PATH:/usr/local/opt/mysql-client/bin:$PATH`
    `export ANSIBLE_VAULT_PASSWORD_FILE=PATH_TO_VAULT_PASSWORD`

If you get `EnvironmentError: mysql_config not found`
you might need to set a path to mysqlconfig

You may need to set utf8 in /etc/my.cnf
collation-server = utf8_unicode_ci

    init-connect='SET NAMES utf8'
    character-set-server = utf8

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

MySQL Migration
---------------

## 5.7 - 8.0 Notes

* Many migration blockers were removed by by dumping, then restoring the database.
* After that, RDS was able to migrate
* needed to create the unglueit user from the mysql client

