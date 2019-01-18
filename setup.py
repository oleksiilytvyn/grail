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
import sys
import shutil

from cx_Freeze import setup, Executable
from PyQt5.QtGui import QGuiApplication

from scripts.util import *
from grailkit.util import *

# Constants
CMD_FIXPNG = '!fix-png'
VERSION = get_revision()
VERSION_PATH = "build/.version"
TITLE = "Grail"
FILE = "grail.py"
BUNDLE_NAME = "%s-%s" % (TITLE, VERSION)
BUNDLE_FILE = "%s.app" % (BUNDLE_NAME,)
BUNDLE_CONTENTS = "build/%s/Contents" % BUNDLE_FILE
BUNDLE_RESOURCES = "%s/Resources" % BUNDLE_CONTENTS
PACKAGES = []
INCLUDES = ['atexit', 'PyQt5.QtNetwork']
EXCLUDES = ['nt',
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

INCLUDE_FILES = [('LICENSE', 'LICENSE'),
                 ('build/.version', '.version')]

# Add support for custom arguments
USER_ARGS = [arg for arg in sys.argv if arg.startswith('!')]
sys.argv = [arg for arg in sys.argv if not arg.startswith('!')]

# used for png utility
if CMD_FIXPNG in USER_ARGS:
    app = QGuiApplication(sys.argv)
    fix_png_profile('./data', recursive=True)

# Generate stylesheet
print_step("Compiling theme.qss")
generate_stylesheet()

# compile Qt resources
print_step("Compiling Qt resource")
compile_resources(source='./data', destination='./grail/resources.py', exclude=['./dist', '.'])

# Create new version file
print_step("Creating .version file")
create_version_file(VERSION_PATH, VERSION)

# Building executable
print_step("Building executable")


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

    requires=['grailkit', 'PyQt5', 'cx_Freeze'],

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
            "includes": INCLUDES,
            "include_files": INCLUDE_FILES,
            "include_msvcr": True,
            "excludes": EXCLUDES,
            "silent": True,
            "packages": PACKAGES,
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
            "packages": PACKAGES
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
    print_step("Copying qt.conf to Bundle")
    shutil.copyfile("data/dist/qt.conf", BUNDLE_RESOURCES + '/qt.conf')

# Exit script as it uses Qt Application instance
sys.exit(0)
