#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    setup
    ~~~~~

    Setup Script
    Run the build process by executing command 'python setup.py build'
"""

import os
import sys
import grail
import shutil
import platform

from cx_Freeze import setup, Executable


# constants
OS_WIN = platform.system() == "Windows"
OS_MAC = platform.system() == "Darwin"
OS_UNIX = platform.system() == "Linux"


def get_revision():
    """try to add revision number to version string"""

    revision = grail.__version__

    try:
        import hgapi

        repository = hgapi.Repo(os.path.abspath(os.curdir))
        revision = "%sb%d" % (grail.__version__, repository['tip'].rev)
    except ImportError:
        print("Failed to get revision number. Install 'hgapi' module.")
    except Exception as error:
        print("Unable to get revision number, following error occurred:")
        print(error)

    return revision


def compile_resources():
    """try to build resources file"""

    try:
        print("Building resource file")
        os.system("pyrcc5 -o grail/resources.py resources/resources.qrc")
    except Exception as error:
        print("Failed to build resource file, following error occurred:")
        print(error)


def create_version_file(path, revision):
    """Create .version file inside app directory"""

    directory = os.path.dirname(os.path.realpath(path))

    if not os.path.exists(directory):
        os.makedirs(directory)

    # add version file to build
    try:
        f = open(path, "w+")
        f.write(revision)
        f.close()
    except Exception as error:
        print("Failed to create a version file, following error occurred:")
        print(error)


# Constants
VERSION = get_revision()
VERSION_PATH = "build/.version"
TITLE = "Grail"
FILE = "grail.py"
BUNDLE_NAME = "%s-%s" % (TITLE, VERSION)
BUNDLE_FILE = "%s.app" % (BUNDLE_NAME,)
BUNDLE_CONTENTS = "build/%s/Contents" % BUNDLE_FILE
BUNDLE_RESOURCES = "%s/Resources" % BUNDLE_CONTENTS

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

files = [('LICENSE', 'LICENSE'),
         ('build/.version', '.version')]

# compile Qt resources
compile_resources()
# Create new version file
create_version_file(VERSION_PATH, VERSION)

setup(
    name=TITLE,
    version=VERSION,
    url='http://grailapp.com/',

    author='Oleksii Lytvyn',
    author_email='grailapplication@gmail.com',
    description="Simple and fast lyrics application.",
    long_description="Simple and powerful media software for churches",
    keywords='open source osc church lyrics projection song bible display',
    license='GNU General Public License v3',

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

    options={
        "build_exe": {
            "includes": includes,
            "include_files": files,
            "include_msvcr": True,
            "excludes": excludes,
            "silent": True
            },
        "bdist_msi": {
            "add_to_path": True,
            "upgrade_code": "{1f82a4c1-681d-43c3-b1b6-d63788c147a0}"
            },
        "bdist_mac": {
            "bundle_name": BUNDLE_NAME,
            "custom_info_plist": "resources/bdist/Info.plist",
            "iconfile": "icon/grail.icns"
            },
        "bdist_dmg": {
            "volume_label": TITLE,
            "applications_shortcut": True
            }
        },
    executables=[Executable(FILE,
                            base="Win32GUI" if sys.platform == "win32" else None,
                            icon="icon/grail.ico",
                            compress=True,
                            shortcutName=TITLE,
                            shortcutDir="ProgramMenuFolder")])

# fix Mac OS app file
if OS_MAC and os.path.exists(BUNDLE_RESOURCES):
    shutil.copyfile("resources/bdist/qt.conf", BUNDLE_RESOURCES + '/qt.conf')
