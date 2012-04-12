#!/usr/bin/env python

from distutils.core import setup

setup( name='IPMap',
        version='1.0',
        description='Map IPv4 addresses to Hilbert curve',
        author='Daniel Miller',
        author_email='bonsaiviking@gmail.com',
        url='https://github.com/bonsaiviking/IPMap',
        packages=['ipmap'],
        requires=['PIL'],
        )
