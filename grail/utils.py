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

import sys
import os
import platform
import re
import grail
import shutil

from PyQt5.QtCore import QFile

PLATFORM_WIN = platform.system() == "Windows"
PLATFORM_MAC = platform.system() == "Darwin"
PLATFORM_UNIX = platform.system() == "Linux"


def get_path():
    """Get the path to this script no matter how it's run."""

    if hasattr(sys, 'frozen'):
        path = os.path.dirname(sys.executable)
    elif '__file__' in locals():
        path = os.path.dirname(__file__)
    else:
        path = sys.path[0]

    return path


def get_stylesheet():
    """Get application stylesheet"""

    data = ""
    stream = QFile(":/stylesheet/app.qss")

    if stream.open(QFile.ReadOnly):
        data = str(stream.readAll())
        stream.close()

    data = re.sub(r'\\n', '', data)
    data = re.sub(r'\\t', '', data)

    return data[2:-1]


def get_data_path():
    """Returns path to grail settings folder"""

    name = 'grail1'

    if sys.platform == 'win32':
        appdata = os.path.join(os.environ['APPDATA'], name)
    else:
        appdata = os.path.expanduser(os.path.join("~", "." + name))

    return appdata


def copy_file(a, b):
    """Copy file from source 'a' to destination 'b'

    Args:
        a (str): source path
        b (str): destination path
    """
    directory = os.path.dirname(os.path.realpath(b))

    if not os.path.exists(directory):
        os.makedirs(directory)

    if os.path.exists(a):
        shutil.copyfile(a, b)


def remove_file(path):
    """Remove file without throwing exception

    Args:
        path (str): path to file to be removed
    """

    try:
        os.remove(path)
    except OSError as e:
        pass


def get_version():
    """Returns grail version"""

    path = '.version'

    if os.path.isfile(path):
        return open(path).read()
    else:
        return grail.__version__
