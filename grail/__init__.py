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

import traceback

# PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.utils import *
from grail.grail import Grail

__version__ = '0.9.5'


class Application(QApplication):
    """Grail application"""

    def __init__(self, argv):
        super(Application, self).__init__(argv)

        self.shared_memory = None

        # prevent from running more than one instance
        if self.isAlreadyRunning():
            self.quit()

        try:
            self.setAttribute(Qt.AA_UseHighDpiPixmaps)
        except:
            pass

        # use GTK style if available
        for style in QStyleFactory.keys():
            if "gtk" in style.lower():
                self.setStyle(QStyleFactory.create("gtk"))

        self.setStyleSheet(get_stylesheet())

    def isAlreadyRunning(self):
        """Check for another instances of Grail

        Returns: Boolean
        """

        self.shared_memory = QSharedMemory('Grail')

        if self.shared_memory.attach():

            msgBox = QMessageBox()
            msgBox.setWindowTitle("Grail")
            msgBox.setText("Another version of Grail is currently running")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)

            if not PLATFORM_MAC:
                msgBox.setWindowIcon(QIcon(':/icons/32.png'))

            if PLATFORM_UNIX:
                msgBox.setWindowIcon(QIcon(':/icons/256.png'))

            msgBox.exec_()

            return True
        else:
            self.shared_memory.create(1)

        return False

    def quit(self):
        """Quit application and close all connections"""

        self.shared_memory.detach()
        super(Application, self).quit()

old_excepthook = sys.excepthook


def hook_exception(exctype, value, traceback_object):
    """Hook exception to be written to file"""

    old_excepthook(exctype, value, traceback_object)

    out = open('error.log', 'a+')
    out.write("=== Exception ===\n" +
              "Platform: %s\n" % (platform.platform(),) +
              "Version: %s\n" % (get_version(),) +
              "Traceback: %s\n" % (''.join(traceback.format_exception(exctype, value, traceback_object)),))
    out.close()


sys.excepthook = hook_exception


def main():
    """Launch Grail application"""
    os.chdir(get_path())

    app = Application(sys.argv)
    Grail()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
