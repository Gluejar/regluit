from setuptools import setup, find_packages

setup(
    name='Regluit',
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