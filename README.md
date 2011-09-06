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
an Ubuntu system:

1. `aptitude install python-setuptools`
1. `sudo easy_install virtualenv virtualenvwrapper`
1. `git clone git@github.com:Gluejar/regluit.git`
1. `cd reglueit`
1. `mkvirtualenv --no-site-packages regluit`
1. `pip install -r requirements.pip`
1. `add2virtualenv ..`
1. `cp settings/dev.py settings/me.py`
1. edit `settings/me.py` and set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`  to your gmail username and password, so that registration emails will work properly.
1. edit `settings/me.py` and look at the facebook, twitter and google auth settings to enable federated logins from those sites
1. `echo 'export DJANGO_SETTINGS_MODULE=regluit.settings.me' >> ~/.virtualenvs/regluit/bin/postactivate`
1. `deactivate ; workon regluit`
1. `django-admin.py syncdb --migrate`
1. `django-admin testserver`
1. point your browser at http://localhost:8000/

