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
from grail.data import Settings
from grail.widgets import SearchListWidget, SearchListItem
from grail.dialogs.osc_source_dialog import OSCSourceWidget


class PreferencesDialog(QDialog):

    osc_in_changed = pyqtSignal(object)
    osc_out_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):

        self.ui_sidebar = SearchListWidget()
        self.ui_sidebar.setObjectName("library_list")
        self.ui_sidebar.setAlternatingRowColors(True)
        self.ui_sidebar.itemClicked.connect(self.page_clicked)

        items = ['General', 'OSC Output', 'Bible']

        for index, item in enumerate(items):
            listitem = SearchListItem()
            listitem.setText(item)
            listitem.setMessage(item)
            listitem.setItemData(index)

            self.ui_sidebar.addItem(listitem)

        self.ui_panel = QStackedWidget()
        self.ui_panel.addWidget(GeneralPanel())
        self.ui_panel.addWidget(OSCOutputPanel())
        self.ui_panel.addWidget(BiblePanel())

        # splitter
        self.ui_splitter = QSplitter()
        self.ui_splitter.setObjectName("spliter")

        self.ui_splitter.addWidget(self.ui_sidebar)
        self.ui_splitter.addWidget(self.ui_panel)

        self.ui_panel.setCurrentIndex(0)

        self.ui_splitter.setCollapsible(0, False)
        self.ui_splitter.setCollapsible(1, False)
        self.ui_splitter.setHandleWidth(1)
        self.ui_splitter.setSizes([200, 400])

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setSpacing(0)
        self.ui_layout.setContentsMargins(0, 0, 0, 0)
        self.ui_layout.addWidget(self.ui_splitter)

        self.setLayout(self.ui_layout)

        if not PLATFORM_MAC:
            self.setWindowIcon(QIcon(':/icons/32.png'))

        self.setWindowTitle('Preferences')
        self.setGeometry(300, 300, 600, 400)
        self.setMinimumSize(600, 400)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def page_clicked(self, item):

        self.ui_panel.setCurrentIndex(item.data)


class GeneralPanel(QWidget):

    def __init__(self, parent=None):
        super(GeneralPanel, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):
        self.ui_label = QLabel("General", self)
        self.ui_label.move(20, 20)


class OSCOutputPanel(OSCSourceWidget):
    pass


class BiblePanel(QWidget):
    pass
