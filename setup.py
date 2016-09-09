#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    setup
    ~~~~~

    Setup Script
    Run the build process by running the command 'python setup.py build'
"""

import os
import sys
import grail
import shutil
import platform

from cx_Freeze import setup, Executable


# constants
PLATFORM_WIN = platform.system() == "Windows"
PLATFORM_MAC = platform.system() == "Darwin"
PLATFORM_UNIX = platform.system() == "Linux"

# Constants
version = grail.__version__
version_path = "build/.version"
application_title = "Grail"
application_file = "grail.py"

# try to add revision number to version
try:
    import hgapi

    repo = hgapi.Repo(os.path.abspath(os.curdir))
    version = "%sb%d" % (version, repo['tip'].rev)
except ImportError:
    print("Failed to get revision number. Install hgapi python library")
except:
    print("Unable to get revision number")

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

includefiles = [('LICENSE', 'LICENSE'),
                ('build/.version', '.version')]

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
            "include_msvcr": True,
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
    executables=[Executable(application_file,
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
