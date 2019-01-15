#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    setup
    ~~~~~

    Setup Script
    Run the build process by executing command 'python setup.py build'

    Additional build arguments:
        !fix-png: fix PNG color profile errors
"""

import os
import sys
import shutil
import platform

from PyQt5.QtCore import QFile, QIODevice
from PyQt5.QtGui import QPixmap, QGuiApplication
from cx_Freeze import setup, Executable

from grail import __version__ as GRAIL_VERSION


# os constants
OS_SYSTEM = platform.system()
OS_WIN = OS_SYSTEM == "Windows"
OS_MAC = OS_SYSTEM == "Darwin"
OS_UNIX = OS_SYSTEM == "Linux"

# Add support for custom arguments
USER_ARGS = [arg for arg in sys.argv if arg.startswith('!')]
sys.argv = [arg for arg in sys.argv if not arg.startswith('!')]

# used for png utility
if '!fix-png' in USER_ARGS:
    app = QGuiApplication(sys.argv)


def get_revision():
    """try to add revision number to version string"""

    revision = GRAIL_VERSION

    try:
        import hgapi

        repository = hgapi.Repo(os.path.abspath(os.curdir))
        revision = "%sb%d" % (GRAIL_VERSION, repository['tip'].rev)
    except ImportError:
        print("Failed to get revision number. Install 'hgapi' module.")
    except Exception as error:
        print("Unable to get revision number, following error occurred:")
        print(error)

    return revision


def compile_resources(source=None, destination=None, exclude=None):
    """try to build resources file

    Args:
        source (str): path to folder with resources
        destination (str): path to python resource file
        exclude (list): list of excluded files and folders relative to given source
    """

    data_path = './data'
    source_file = os.path.join(source, 'resources.qrc')
    qrc_source = '''<!DOCTYPE RCC>\n<RCC version="1.0">\n\t<qresource>\n'''

    if not exclude:
        exclude = []

    for index, path in enumerate(exclude):
        exclude[index] = os.path.abspath(os.path.join(data_path, path))

    print("\nGenerating QRC file:")
    print(" - source: %s" % source)
    print(" - destination: %s" % destination)
    print(" - qrc file: %s" % source_file)

    for directory, directories, file_names in os.walk("./data"):

        # exclude directories
        if os.path.abspath(directory) in exclude:
            continue

        qrc_source += '\n\t\t<!-- ./%s/ -->\n' % directory[len(data_path) + 1:]

        for name in file_names:
            # skip system files
            if name.startswith('.'):
                continue

            file_path = os.path.join(directory, name)[len(data_path)+1:]
            qrc_source += '\t\t<file alias="%s">%s</file>\n' % (file_path, file_path)

    qrc_source += '\t</qresource>\n</RCC>'

    qrc_file = open(source_file, 'w')
    qrc_file.write(qrc_source)
    qrc_file.close()

    try:
        print("\nBuilding resource file")
        print("pyrcc5 -o %s %s" % (destination, source_file))
        os.system("pyrcc5 -o %s %s" % (destination, source_file))
    except Exception as error:
        print("Failed to build resource file, following error occurred:\n %s" % error)


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

        print("\nVersion file created at %s" % path)
    except Exception as error:
        print("\nFailed to create a version file, following error occurred:")
        print(error)


def fix_png_profile(path, recursive=False, _main=True):
    """Fix annoying `libpng warning: iCCP: known incorrect sRGB profile`
    warning for files in given directory

    Args:
        path (str): path to directory
        recursive (bool): include sub-folders or not
        _main (bool): True if this is first non-recursive call
    """

    path = os.path.abspath(path)

    if not os.path.exists(path):
        return False

    if _main:
        print("\nFixing PNG warnings:")

    for name in os.listdir(path):
        link = os.path.join(path, name)

        if os.path.isfile(link) and link.endswith('.png'):
            try:
                pixmap = QPixmap()
                pixmap.load(link)

                file = QFile(link)
                file.open(QIODevice.WriteOnly)

                pixmap.save(link, "PNG")
                print('- %s' % link)
            except Exception as error:
                print(error)

        elif os.path.isdir(link):
            fix_png_profile(link, recursive, False)


# Constants
VERSION = get_revision()
VERSION_PATH = "build/.version"
TITLE = "Grail"
FILE = "grail.py"
BUNDLE_NAME = "%s-%s" % (TITLE, VERSION)
BUNDLE_FILE = "%s.app" % (BUNDLE_NAME,)
BUNDLE_CONTENTS = "build/%s/Contents" % BUNDLE_FILE
BUNDLE_RESOURCES = "%s/Resources" % BUNDLE_CONTENTS

packages = []
includes = ['atexit', 'PyQt5.QtNetwork']
excludes = ['nt',
            'pdb',
            '_ssl',
            "Pyrex",
            'doctest',
            "tkinter",
            'pyreadline',
            'matplotlib',
            'scipy.linalg',
            'scipy.special',
            'numpy']

files = [('LICENSE', 'LICENSE'),
         ('build/.version', '.version')]

# fix png warnings
if '!fix-png' in USER_ARGS:
    fix_png_profile('./data', recursive=True)

# compile Qt resources
compile_resources(source='./data', destination='./grail/resources.py', exclude=['./dist', '.'])

# Create new version file
create_version_file(VERSION_PATH, VERSION)

# Building executable
print("\n%s\n" % ('- ' * 30))

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

    requires=['grailkit', 'PyQt5', 'hgapi'],

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
            "silent": True,
            "packages": packages,
            'zip_include_packages': 'PyQt5'
            },
        "bdist_msi": {
            "add_to_path": True,
            "upgrade_code": "{1f82a4c1-681d-43c3-b1b6-d63788c147a0}"
            },
        "bdist_mac": {
            "bundle_name": BUNDLE_NAME,
            "custom_info_plist": "data/dist/Info.plist",
            "iconfile": "data/icon/grail.icns",
            "packages": packages
            },
        "bdist_dmg": {
            "volume_label": TITLE,
            "applications_shortcut": True
            }
        },
    executables=[Executable(FILE,
                            base="Win32GUI" if sys.platform == "win32" else None,
                            icon="data/icon/grail.ico",
                            shortcutName=TITLE,
                            shortcutDir="ProgramMenuFolder")])

# fix Mac OS app file
if OS_MAC and os.path.exists(BUNDLE_RESOURCES):
    shutil.copyfile("data/dist/qt.conf", BUNDLE_RESOURCES + '/qt.conf')

# Exit script as it uses Qt Application instance
sys.exit(0)
