# -*- coding: utf-8 -*-
from setuptools import setup
import profiling
import os

# Utility function to read the README file.
# Used for the long_description. It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='django-profiler',
    version=profiling.__version__,
    description='util for profiling python code mainly in django projects, but can be used also on ordinary python code',
    long_description=read('README.rst'),
    author=u'Vladimír Gorej',
    author_email='gorej@codescale.net',
    url='http://www.codescale.net/en/community#django-profiler',
    download_url='http://github.com/char0n/django-profiler/tarball/master',
    license='BSD',
    keywords = 'django profiler profiling code profile',
    packages=['profiling', 'profiling.test'],
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Bug Tracking'
    ],
    test_suite='profiling.test'
)