#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Grail - Lyrics software. Simple.
# Copyright (C) 2014-2015 Oleksii Lytvyn
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

application_title = "Grail"
main_python_file = "grail.py"

import os
import sys
import grail
import shutil
import platform
from cx_Freeze import setup, Executable

PLATFORM_WIN = platform.system() == "Windows"
PLATFORM_MAC = platform.system() == "Darwin"
PLATFORM_UNIX = platform.system() == "Linux"

version = grail.__version__

# try to add revision number to version
try:
    import hgapi
    repo = hgapi.Repo( os.path.abspath(os.curdir) )
    version = "%sb%d" % (version, repo['tip'].rev)
except:
    pass


directory = os.path.dirname(os.path.realpath( "build/.version" ))

if not os.path.exists(directory):
    os.makedirs(directory)

# add version file to build
f = open("build/.version", "w+")
f.write(version)
f.close()

base = None
if sys.platform == "win32":
    base = "Win32GUI"

includes = ["atexit"]

excludes = ['_ssl',
            'pyreadline',
            'pdb',
            "matplotlib",
            'doctest',
            "scipy.linalg",
            "scipy.special",
            "Pyrex",
            "numpy.core._dotblas",
            "nt",
            "ntpath"]

includefiles = [('resources/bdist/bible.db-default', 'default/bible.db'),
                ('resources/bdist//songs.db-default', 'default/songs.db'),
                ('LICENSE', 'LICENSE'),
                ('build/.version', '.version')]

# add platform specific files
if PLATFORM_WIN:
    includefiles.append( ('resources/bdist/libEGL.dll', 'libEGL.dll') )

# try to build resources file
try:
    os.system("pyrcc5 -o grail/resources.py resources/resources.qrc")
except:
    pass

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
            "excludes": excludes},
        "bdist_mac": {
            "iconfile": "icon/grail.icns"},
        "bdist_dmg": {
            "volume_label": application_title,
            "applications-shortcut": True}},
    executables=[Executable(main_python_file,
                 base=base,
                 icon="icon/grail.ico",
                 compress=True,
                 shortcutName=application_title,
                 shortcutDir="ProgramMenuFolder")])

# fix app file
if PLATFORM_MAC:
    app_resources = "build/%s-%s.app/Contents/Resources" % (application_title, version)
    app_contents = "build/%s-%s.app/Contents" % (application_title, version)

    if os.path.exists( app_resources ):
        shutil.copyfile( "resources/bdist/qt.conf", app_resources + '/qt.conf' )

    if os.path.exists( app_contents ):
        shutil.copyfile( "resources/bdist/Info.plist", app_contents + '/Info.plist' )
