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

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.utils import *


class AboutDialog(QDialog):

    """About Window"""

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        self.setObjectName("about_dialog")

        self.ui_picture = QLabel(self)
        self.ui_picture.setPixmap(QPixmap(":/icons/128.png"))
        self.ui_picture.setAlignment(Qt.AlignCenter)
        self.ui_picture.setGeometry(0, 16, 400, 128)

        self.ui_title = QLabel("Grail", self)
        self.ui_title.setAlignment(Qt.AlignCenter)
        self.ui_title.setGeometry(0, 148, 400, 20)
        self.ui_title.setObjectName("about_title")

        self.ui_version = QLabel("Version %s" % (get_version(),), self)
        self.ui_version.setAlignment(Qt.AlignCenter)
        self.ui_version.setGeometry(0, 168, 400, 20)
        self.ui_version.setObjectName("about_version")

        self.ui_copyright = QLabel("Copyright © 2014-2015 Grail Team.\nAll rights reserved.", self)
        self.ui_copyright.setAlignment(Qt.AlignCenter)
        self.ui_copyright.setGeometry(0, 196, 400, 40)
        self.ui_copyright.setObjectName("about_copyright")

        self.setWindowTitle('About Grail')
        self.setWindowIcon(QIcon(':/icons/32.png'))
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setGeometry(100, 100, 400, 248)
        self.setFixedSize(400, 248)

    def className(self):
        return 'AboutDialog'
