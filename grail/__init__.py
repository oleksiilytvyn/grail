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

__version__ = '0.9.2'

import sys
import os

# PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.utils import *
from grail.grail import Grail

class Application(QApplication):

    def __init__( self, argv ):
        super(Application, self).__init__(argv)

        try:
            self.setAttribute( Qt.AA_UseHighDpiPixmaps )
        except:
            pass

        # use GTK style if available
        for style in QStyleFactory.keys():
            if "gtk" in style.lower():
                self.setStyle( QStyleFactory.create("gtk") )

        self.setStyleSheet( get_stylesheet() )

def main():
    os.chdir( get_path() )

    app = Application(sys.argv)
    win = Grail()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
