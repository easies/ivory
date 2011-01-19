#!/usr/bin/env python

from distutils.core import setup


setup(
    name='ivory',
    version='0.0.0',
    description='',
    author='Alex Lee',
    author_email='lee@ccs.neu.edu',
    url='',
    package_dir={'ivory': 'ivory'},
    packages=['ivory', 'ivory.modules'],
    scripts=['scripts/ivory'],
)
