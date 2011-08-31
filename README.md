regluit
=======

A 'monolithic' alternative to [unglu](http://github.com/gluejar/unglu) 
for the unglue.it website. It's just one code base that can be deployed
to as many ec2 instances as needed to support traffic.

Develop
-------

Here are some instructions for setting up regluit for development on 
an Ubuntu system:

1. `aptitude install python-setuptools`
1. `sudo easy_install virtualenv virtualenvwrapper`
1. `git clone git@github.com:Gluejar/regluit.git`
1. `cd reglueit`
1. `mkvirtualenv --no-site-packages regluit`
1. `pip install -r requirements.pip`
1. `add2virtualenv ..`
1. `echo 'export DJANGO_SETTINGS_MODULE=regluit.settings.dev' >> ~/.virtualenvs/regluit/bin/postactivate`
1. `deactivate ; workon regluit`
1. `django-admin.py syncdb --migrate`
1. `django-admin runserver`
