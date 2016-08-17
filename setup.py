#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Grail - Lyrics software. Simple.
# Copyright (C) 2014-2016 Oleksii Lytvyn
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Setup Script
# Run the build process by running the command 'python setup.py build'

import os
import sys
import grail
import shutil
import platform
from cx_Freeze import setup, Executable

# constants
application_title = "Grail"
main_python_file = "grail.py"

PLATFORM_WIN = platform.system() == "Windows"
PLATFORM_MAC = platform.system() == "Darwin"
PLATFORM_UNIX = platform.system() == "Linux"

version = grail.__version__
version_path = "build/.version"

# try to add revision number to version
try:
    import hgapi

    repo = hgapi.Repo(os.path.abspath(os.curdir))
    version = "%sb%d" % (version, repo['tip'].rev)
except ImportError:
    print("Failed to get revision number. Install hgapi python library")

directory = os.path.dirname(os.path.realpath(version_path))

if not os.path.exists(directory):
    os.makedirs(directory)

# add version file to build
try:
    f = open(version_path, "w+")
    f.write(version)
    f.close()
except:
    print("Failed to create a version file")

includes = ["atexit"]
excludes = ["nt",
            'pdb',
            '_ssl',
            "Pyrex",
            "ntpath",
            'doctest',
            "tkinter",
            'pyreadline',
            "matplotlib",
            "scipy.linalg",
            "scipy.special",
            "numpy.core._dotblas"]

includefiles = [('resources/bdist/bible.db-default', 'default/bible.db'),
                ('resources/bdist//songs.db-default', 'default/songs.db'),
                ('LICENSE', 'LICENSE'),
                ('build/.version', '.version')]

# add platform specific files
if PLATFORM_WIN:
    includefiles.append(('resources/bdist/libEGL.dll', 'libEGL.dll'))

# try to build resources file
try:
    print("Building resource file")
    os.system("pyrcc5 -o grail/resources.py resources/resources.qrc")
except:
    print("Failed to build resource file")

setup(
    name=application_title,
    version=version,
    url='http://grailapp.com/',

    author='Oleksii Lytvyn',
    author_email='grailapplication@gmail.com',
    description="Simple and fast lyrics application.",
    long_description="",
    keywords='open source osc church lyrics projection song bible display',
    license='GNU General Public License v3',

    requires=['cx_Freeze', 'PyQt5', 'hgapi'],

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
        'Operating System :: POSIX :: BSD :: FreeBSD',
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

    options={
        "build_exe": {
            "includes": includes,
            "include_files": includefiles,
            # To-Do: test msvcr dll
            # "include_msvcr": True,
            "excludes": excludes,
            "silent": True
            },
        "bdist_msi": {
            "upgrade_code": "{1f82a4c1-681d-43c3-b1b6-d63788c147a0}"
            },
        "bdist_mac": {
            "bundle_name": "%s-%s" % (application_title, version),
            "custom_info_plist": "resources/bdist/Info.plist",
            "iconfile": "icon/grail.icns"
            },
        "bdist_dmg": {
            "volume_label": application_title
            }
        },
    executables=[Executable(main_python_file,
                            base="Win32GUI" if sys.platform == "win32" else None,
                            icon="icon/grail.ico",
                            compress=True,
                            shortcutName=application_title,
                            shortcutDir="ProgramMenuFolder")])

# fix Mac OS app file
if PLATFORM_MAC:
    app_resources = "build/%s-%s.app/Contents/Resources" % (application_title, version)
    app_contents = "build/%s-%s.app/Contents" % (application_title, version)

    if os.path.exists(app_resources):
        shutil.copyfile("resources/bdist/qt.conf", app_resources + '/qt.conf')
