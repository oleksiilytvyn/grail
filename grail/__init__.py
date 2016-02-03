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

__version__ = '1.0.0'

import sys
import os
import re

# PyQt5
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

# grail
from grail.sdk.utils import script_path
from grail.ui import MainWindow


class GrailApplication(QtWidgets.QApplication):
    """Grail application"""

    def __init__( self, argv ):
        super(GrailApplication, self).__init__(argv)

        self.shared_memory = None

        self.setOrganizationName("Oleksii Lytvyn")
        self.setOrganizationDomain("grailapp.com")
        self.setApplicationName("grail")

        # prevent from running more than one instance
        if self.is_already_running():
            self.quit()

        try:
            self.setAttribute( QtCore.Qt.AA_UseHighDpiPixmaps )
        except:
            pass

        # use GTK style if available
        for style in QtWidgets.QStyleFactory.keys():
            if "gtk" in style.lower():
                self.setStyle( QtWidgets.QStyleFactory.create("gtk") )

        self.setStyleSheet( self.get_stylesheet() )

    def is_already_running(self):
        """Check for another instances of Grail

        Returns: Boolean
        """

        self.shared_memory = QtCore.QSharedMemory('grail')

        if self.shared_memory.attach():

            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle("Grail")
            msgBox.setText("Another version of Grail is currently running")
            msgBox.setStandardButtons( QtGui.QMessageBox.Ok )
            msgBox.setDefaultButton( QtGui.QMessageBox.Ok )
            msgBox.setIcon( QtGui.QMessageBox.Warning )
            msgBox.setWindowIcon( QtGui.QIcon(':/icons/256.png') )

            msgBox.exec_()

            return True
        else:
            self.shared_memory.create(1)
        
        return False

    def quit( self ):
        """Quit application and close all connections"""

        self.shared_memory.detach()
        super(GrailApplication, self).quit()
        sys.exit()


    def hook_exception( self, exctype, value, traceback_object ):
        """Hook exception to be written to file"""

        out = open('error.log', 'a+')
        out.write("=== Exception ===\n" +
                  "Platform: %s\n" % ( platform.platform(), ) +
                  "Version: %s\n" % ( version(), ) +
                  "Traceback: %s\n" % ( ''.join(traceback.format_exception(exctype, value, traceback_object)), ) )
        out.close()

    def get_stylesheet( self ):
        """
        Get the application stylesheet

        :returns: string
        """

        data = ""
        stream = QtCore.QFile(":/stylesheet/app.qss")

        if stream.open(QtCore.QFile.ReadOnly):
            data = str(stream.readAll())
            stream.close()

        data = re.sub(r'\\n', '', data)
        data = re.sub(r'\\t', '', data)

        return data[2:-1]


def version():
    """Returns version of Grail"""

    path = '.version'

    if os.path.isfile( path ):
        return open( path ).read()
    else:
        return __version__


def main(args=None):
    """Launch Grail application"""

    os.chdir( script_path() )

    app = GrailApplication(sys.argv)
    win = MainWindow()

    sys.excepthook = app.hook_exception
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
