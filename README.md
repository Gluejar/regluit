regluit
=======

A 'monolithic' alternative to [unglu](http://github.com/gluejar/unglu) 
for the unglue.it website. regluit essentially on Django project that contains 
three applications: `frontend`, `api` and `core` that can be deployed and 
configured to as many instances that are needed to support traffic. The key 
difference with [unglue](http://github.com/gluejar/unglu) is that the 
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
1. `echo 'export DJANGO_SETTINGS_MODULE=regluit.settings.dev' >> ~/.virtualenvs/regluit/bin/postactivate`
1. `deactivate ; workon regluit`
1. `django-admin.py syncdb --migrate`
1. `django-admin runserver`
1. point your browser at http://localhost:8000/

