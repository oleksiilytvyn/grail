#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    setup
    ~~~~~

    Setup Script
    Run the build process by executing command 'python setup.py build'
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import grail

# Constants
VERSION = grail.__version__
TITLE = "Grail"
FILE = "grail.py"
PACKAGES = []
INCLUDES = ['atexit', 'PyQt5.QtNetwork']
INCLUDE_FILES = [('LICENSE', 'LICENSE'),
                 ('build/.version', '.version')]

setup(
    name=TITLE,
    version=VERSION,
    url='http://grailapp.com/',

    author='Alex Litvin',
    author_email='programer95@gmail.com',
    description="Simple and fast lyrics application.",
    long_description="Simple and powerful media software for churches",
    keywords='open source osc church lyrics projection song bible display',
    license='GNU General Public License v3',
    platforms='any',
    packages=['grail'],
    requires=['grailkit', 'PyQt5'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Religion',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Desktop Environment :: Gnome',
        'Topic :: Desktop Environment :: K Desktop Environment (KDE)',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Video',
        'Topic :: Religion'],
    )
