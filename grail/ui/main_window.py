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

# generic imports
import re
import os
import sys
import sqlite3 as lite
import traceback
import time

# PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# OSC library
from osc import OSCMessage, OSCBundle, OSCClient

# grail
from grail import resources


class MainWindow(QMainWindow):
    """
    Grail application class
    """

    def __init__( self, parent=None ):
        super(MainWindow, self).__init__(parent)

        self.initUI()

    def initUI( self ):
        """
        Initialize UI
        """

        self.setWindowIcon( QIcon(':/icons/256.png') )

        self.setGeometry( 300, 300, 800, 480 )
        self.setMinimumSize( 320, 240 )
        self.setWindowTitle( "Grail" )
        self.center()
        self.show()

    def center( self ):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter( cp )
        self.move( qr.topLeft() )
