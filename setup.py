#!/usr/bin/env python
# -*- coding: utf-8

import os
from setuptools import setup
import tastycrust

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
VERSION = tastycrust.__version__

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-tastypie-crust',
    version=VERSION,
    packages=['tastycrust'],
    include_package_data=True,
    install_requires=['django-tastypie'],
    license='BSD License',
    description='Goodies for Tastypie.',
    long_description=README,
    url='https://github.com/uranusjr/django-tastypie-crust',
    author='Tzu-ping Chung',
    author_email='uranusjr@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
