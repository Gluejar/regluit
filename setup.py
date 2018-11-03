import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='regluit',
    version='3.0.0',
    description='Web application for Unglue.it',
    author='Free Ebook Foundation',
    author_email='info@ebookfoundation.org',
    url='https://unglue.it',
    packages=find_packages(exclude=[
        'bookdata',
        'deploy'
        'logs',
        'selenium',
        'static',
        'vagrant',
    ]),
)