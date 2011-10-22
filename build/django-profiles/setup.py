from distutils.core import setup

setup(name='django-profiles',
      version='0.2',
      description='User-profile application for Django',
      author='James Bennett',
      author_email='james@b-list.org',
      url='http://www.bitbucket.org/ubernostrum/django-profiles/wiki/',
      download_url='http://www.bitbucket.org/ubernostrum/django-profiles/get/v0.2.gz',
      packages=['profiles'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )
