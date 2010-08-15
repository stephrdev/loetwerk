#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='calculon',
      version='0.1a',
      description='calculon',
      author='Sebastian Hillig',
      author_email='sebastian.hillig@gmail.com',
      url='',
      test_suite = 'nose.collector',
      packages=find_packages('calculon')
     )

