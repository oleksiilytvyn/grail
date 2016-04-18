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
        """A basic about dialog"""

        super(AboutDialog, self).__init__(parent)

        self._window_title = "About Grail"
        self._title = "Grail %s" % (get_version(),)
        self._description = "Copyright © 2014-2016 Grail Team.\nAll rights reserved."

        self.url_report = "http://grailapp.com/"
        self.url_help = "http://grailapp.com/help"

        self._init_ui()

    def _init_ui(self):

        self._ui_icon = QLabel(self)
        self._ui_icon.setPixmap(QPixmap(":/icons/64.png"))
        self._ui_icon.setAlignment(Qt.AlignCenter)
        self._ui_icon.setGeometry(48, 52, 64, 64)

        self._ui_title = QLabel(self._title, self)
        self._ui_title.setGeometry(160, 34, 311, 26)
        self._ui_title.setObjectName("about_title")

        self._ui_description = QPlainTextEdit(self._description, self)
        self._ui_description.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._ui_description.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._ui_description.setReadOnly(True)
        self._ui_description.setGeometry(156, 74, 311, 88)
        self._ui_description.setObjectName("about_description")

        self._ui_btn_help = QPushButton("Help")
        self._ui_btn_help.clicked.connect(self.help)

        self._ui_btn_report = QPushButton("Web-page")
        self._ui_btn_report.clicked.connect(self.report)

        self.ui_btn_close = QPushButton("Close")
        self.ui_btn_close.setDefault(True)
        self.ui_btn_close.clicked.connect(self.close)

        self._ui_buttons_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self._ui_buttons_layout.addWidget(self._ui_btn_help)
        self._ui_buttons_layout.addStretch()
        self._ui_buttons_layout.addWidget(self._ui_btn_report)
        self._ui_buttons_layout.addWidget(self.ui_btn_close)

        self._ui_buttons = QWidget(self)
        self._ui_buttons.setLayout(self._ui_buttons_layout)
        self._ui_buttons.setGeometry(8, 172, 484 - 16, 50)

        self.setWindowTitle(self._window_title)
        self.setWindowIcon(QIcon(':/icons/32.png'))
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setGeometry(100, 100, 484, 224)
        self.setFixedSize(484, 224)

    def help(self):
        """Open a web page"""
        url = QUrl(self.url_help)
        QDesktopServices.openUrl(url)

    def report(self):
        """Open a web page"""
        url = QUrl(self.url_report)
        QDesktopServices.openUrl(url)

    def className(self):
        return 'AboutDialog'
