#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    setup
    ~~~~~

    Setup Script
    Run the build process by executing command 'python setup.py build'
"""
import os
import re
import sys
import distutils.cmd
import distutils.log
import setuptools
import subprocess

# todo: make PyQt imports optional
from PyQt5.QtCore import QFile, QIODevice, QTimer, QFileSystemWatcher
from PyQt5.QtGui import QPixmap, QGuiApplication

from grailkit.util import OS_MAC, OS_LINUX, OS_WIN, default_key
import grail

# Constants
VERSION = grail.__version__
TITLE = "Grail"
FILE = "grail.py"
INCLUDE_FILES = [('LICENSE', 'LICENSE')]


class CSSPreprocessor:

    def __init__(self, text: str = ""):

        self.source = text
        self.code = text

        self.constants = {}

        self.define('MAC', OS_MAC)
        self.define('LINUX', OS_LINUX)
        self.define('WINDOWS', OS_WIN)

    def define(self, constant, value):
        """Define constant"""

        self.constants[constant] = value

    def reduce(self):
        """Remove comments and spaces"""

        code = self.code

        # remove comments
        code = re.sub(r'/\*[\s\S]*?\*/', "", code)

        # url() doesn't need quotes
        code = re.sub(r'url\((["\'])([^)]*)\1\)', r'url(\2)', code)

        # spaces may be safely collapsed as generated content will collapse them anyway
        code = re.sub(r'\s+', ' ', code)

        # shorten collapsible colors: #aabbcc to #abc
        code = re.sub(r'#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)', r'#\1\2\3\4', code)

        # fragment values can loose zeros
        code = re.sub(r':\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;', r':\1;', code)

        self.code = code

    def find_constants(self):
        """Collect all constants defined in source code"""

        regex = r'^@define\s+([a-zA-Z0-9_-]+)\s+(.*)$'
        pattern = re.compile(regex, re.MULTILINE | re.IGNORECASE)
        matches = pattern.findall(self.code)

        for match in matches:
            self.constants[match[0]] = match[1]

        self.code = re.sub(regex, '', self.code, flags=re.MULTILINE | re.IGNORECASE)

    def replace_constants(self):
        """Replace constants with values"""

        for key in sorted(self.constants, key=len, reverse=True):
            self.code = self.code.replace('$' + key, str(self.constants[key]))

    def fold_statements(self):
        """Find and fold @IF statements"""

        match = re.search(r'^@if ([\d\w_]+)', self.code, flags=re.MULTILINE | re.IGNORECASE)

        while match:
            key = match.group(1)
            value = default_key(self.constants, key, False)
            if_start = match.start(0)
            if_length = len(match.group(0))

            match_end = re.search(r'@end', self.code, flags=re.MULTILINE | re.IGNORECASE)
            end_start = match_end.start(0) if match_end else len(self.code)
            end_length = len(match_end.group(0)) if match_end else 0
            code = self.code

            if value:
                self.code = code[0:if_start] + code[if_start+if_length:end_start] + code[end_start+end_length:]
            else:
                self.code = code[0:if_start] + code[end_start+end_length:]

            match = re.search(r'^@if ([\d\w_]+)', self.code, flags=re.MULTILINE | re.IGNORECASE)

    def compile(self, optimize=False):
        """Compile code"""

        self.find_constants()
        self.replace_constants()
        self.fold_statements()

        if optimize:
            self.reduce()

        return self.code


class BuildResourcesCommand(distutils.cmd.Command):
    """A custom command to compile QSS/CSS and collect all files to package as resources.py."""

    description = 'Compile CSS and generate resources.py'
    user_options = [
        ('data=', None, "Path to resources folder"),
        ('data-exclude=', None, "Exclude files and folders from resources relative to data, list separated by ;"),
        ('rc=', None, "Path to QRC file where it must be generated"),
        ('pyrc=', None, "Path to resources.py to be created")
        ]

    def __init__(self, dist):
        super(BuildResourcesCommand, self).__init__(dist)

        self._INPUT_FILE_EXT = ".qss"
        self._OUTPUT_FILE_EXT = ".css"

        self.data = './data'
        self.data_exclude = './dist;.'
        self.rc = './data/resources.qrc'
        self.pyrc = './grail/resources.py'

    def print(self, *args):

        self.announce(" ".join([str(var) for var in args]), level=distutils.log.INFO)

    def initialize_options(self):
        """Set default values for options."""

        self.data = './data'
        self.data_exclude = './dist;.'
        self.rc = './data/resources.qrc'
        self.pyrc = './grail/resources.py'

    def finalize_options(self):
        """Post-process options."""

        if self.data:
            assert os.path.exists(self.data), ('Given location (%s) does not exist.' % self.data)

    def run(self):
        """Run command."""

        source_dir = self.data
        exclude = ['./dist', '.']
        destination_qrc = self.rc
        destination_pyrc = self.pyrc

        # 1. Create list of files
        self.print("Finding files in location\n", source_dir)
        files = self.build_files(source=source_dir, exclude=exclude)

        # 2. Compile QSS to CSS
        self.print("Compile QSS files")
        files = self.build_css(source=source_dir, files=files)

        # 3. Create resource file
        self.print("Create resource files\n", destination_qrc)
        self.build_qrc(source=source_dir, files=files, destination=destination_qrc)

        # 4. Compile resource file
        self.print("Create python resource file\n", destination_pyrc)
        self.build_rcc(source_file=destination_qrc, destination=destination_pyrc)

    def build_css(self, source: str, files: list):

        new_files = []

        for file_path in files:
            if file_path.endswith(self._INPUT_FILE_EXT):
                source_file = os.path.abspath(os.path.join(source, file_path))
                dest_file = source_file[:-len(self._INPUT_FILE_EXT)] + self._OUTPUT_FILE_EXT

                self.print("-->", source_file, dest_file)
                self.compile_css(source_file, dest_file)

                file_path = file_path[:-len(self._INPUT_FILE_EXT)] + self._OUTPUT_FILE_EXT

            if file_path not in new_files:
                new_files.append(file_path)

        return new_files

    def build_files(self, source=None, exclude=None):
        """Generate list of resource files

        Args:
            source (str): path to folder with resources
            exclude (list): list of excluded files and folders relative to given source
        """

        data_path = source
        files = []

        if not exclude:
            exclude = []

        for index, path in enumerate(exclude):
            exclude[index] = os.path.abspath(os.path.join(data_path, path))

        for directory, directories, file_names in os.walk(data_path):

            # exclude directories
            if os.path.abspath(directory) in exclude:
                continue

            for name in file_names:
                # skip system files
                if name.startswith('.'):
                    continue

                file_path = os.path.join(directory, name)[len(data_path) + 1:]
                files.append(file_path)

        return files

    def build_qrc(self, source: str, files: list, destination: str):

        qrc_source = ''

        for file_path in files:
            qrc_source += '\t\t<file alias="%s">%s</file>\n' % (file_path, file_path)

        qrc_file = open(os.path.abspath(destination), 'w')
        qrc_file.write('<!DOCTYPE RCC>\n<RCC version="1.0">\n\t<qresource>\n%s\t</qresource>\n</RCC>' % qrc_source)
        qrc_file.close()

    def build_rcc(self, destination, source_file):

        destination = os.path.abspath(destination)
        source_file = os.path.abspath(source_file)

        try:
            os.system("pyrcc5 -o %s %s" % (destination, source_file))
        except Exception as error:
            self.print("-- Failed to build resource file, following error occurred:\n %s" % error)

    def compile_css(self, in_file, out_file):

        try:
            source = open(in_file, 'r')
            code = source.read()
            source.close()

            destination = open(out_file, 'w+')
            destination.write(CSSPreprocessor(code).compile())
            destination.close()
        except Exception as error:
            self.print("-- Failed to generate theme.qss\n", error)


class FixImagesCommand(distutils.cmd.Command):
    """A custom command to fix PNG files"""

    description = 'Fix annoying `libpng warning: iCCP: known incorrect sRGB profile`'
    user_options = [
        # The format is (long option, short option, description).
        ('path=', None, 'path to direcotry with images'),
        ('recursive', None, 'specify that it should be recursive')
        ]

    def __init__(self, dist):
        super(FixImagesCommand, self).__init__(dist)

        self.path = './data'
        self.recursive = False

    def initialize_options(self):
        """Set default values for options."""

        self.path = './data'
        self.recursive = False

    def finalize_options(self):
        """Post-process options."""

        if self.path:
            assert os.path.exists(self.path), ('Given location (%s) does not exist.' % self.path)

    def run(self):
        """Run command."""

        self.announce("Fix PNG prfile", level=distutils.log.INFO)

        app = QGuiApplication(sys.argv)

        self.fix_png_profile(self.path, recursive=self.recursive)

        app.quit()

    def fix_png_profile(self, path, recursive=False, _main=True):
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

        for name in os.listdir(path):
            link = os.path.join(path, name)

            if os.path.isfile(link) and link.endswith('.png'):
                try:
                    pixmap = QPixmap()
                    pixmap.load(link)

                    file = QFile(link)
                    file.open(QIODevice.WriteOnly)

                    pixmap.save(link, "PNG")
                    self.announce("-- %s" % link, level=distutils.log.INFO)
                except Exception as error:
                    self.announce(error, level=distutils.log.WARN)

            elif os.path.isdir(link):
                self.fix_png_profile(link, recursive, False)


setuptools.setup(
    cmdclass={
        'build_data': BuildResourcesCommand,
        'build_png': FixImagesCommand
    },

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
