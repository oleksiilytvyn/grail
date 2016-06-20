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
from grail.data import Settings, BibleManager, Song, ConnectionManager
from grail.widgets import SearchListWidget, SearchListItem


class BibleDialog(QDialog):

    def __init__(self, parent=None):
        super(BibleDialog, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):

        self.ui_sidebar_layout = QVBoxLayout()
        self.ui_sidebar_layout.setSpacing(0)
        self.ui_sidebar_layout.setContentsMargins(0, 0, 0, 0)

        self.ui_sidebar_list = SearchListWidget()
        self.ui_sidebar_list.setObjectName("preferences_tabs")
        self.ui_sidebar_list.setAlternatingRowColors(True)
        self.ui_sidebar_list.itemClicked.connect(self.page_clicked)

        self.ui_sidebar = QWidget()
        self.ui_sidebar.setLayout(self.ui_sidebar_layout)
        self.ui_sidebar_layout.addWidget(self.ui_sidebar_list)

        self.ui_splitter = QSplitter()
        self.ui_splitter.setObjectName("splitter")

        self.ui_splitter.addWidget(self.ui_sidebar)
        self.ui_splitter.addWidget(self.ui_panel)
