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
from grail.widgets import *


class OSCSourceWidget(QWidget):

    changed = pyqtSignal(object)

    def __init__(self, parent=None):

        super(OSCSourceWidget, self).__init__(parent)

        self.initPort = 9000
        self.initHost = 1
        self.itemId = 1

        self._init_ui()

    def _init_ui(self):

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setObjectName("songsBar")
        self.ui_layout.setSpacing(0)
        self.ui_layout.setContentsMargins(0, 0, 0, 0)

        self.ui_list = SourcesTableWidget()
        self.ui_list.setObjectName("oscSourcesList")
        self.ui_list.setShowGrid(False)
        self.ui_list.setColumnCount(3)
        self.ui_list.horizontalHeader().setVisible(False)
        self.ui_list.verticalHeader().setVisible(False)
        self.ui_list.setHorizontalHeaderLabels(["Host", "Port", "Action"])
        self.ui_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui_list.setSelectionMode(QAbstractItemView.SingleSelection)

        self.ui_list.itemChanged.connect(self.listItemChanged)

        header = self.ui_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)

        self.ui_list.setColumnWidth(2, 42)

        clearAction = QAction(QIcon(':/icons/remove-white.png'), 'Clear', self)
        clearAction.triggered.connect(self.clearAction)

        addAction = QAction(QIcon(':/icons/add.png'), 'Add', self)
        addAction.setIconVisibleInMenu(True)
        addAction.triggered.connect(self.addAction)

        self.ui_itemsLabel = QLabel("0 sources")
        self.ui_itemsLabel.setObjectName("oscSourcesLabel")
        self.ui_itemsLabel.setAlignment(Qt.AlignCenter)
        self.ui_itemsLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ui_panel_label = QLabel("No sources", self.ui_list)
        self.ui_panel_label.setAlignment(Qt.AlignCenter)
        self.ui_panel_label.setFont(QFont('Decorative', 12))
        self.ui_panel_label.setObjectName("oscSourcesPanelLabel")

        self.ui_toolbar = QToolBar()
        self.ui_toolbar.setObjectName("oscSourcesDialogToolbar")
        self.ui_toolbar.setIconSize(QSize(16, 16))
        self.ui_toolbar.addAction(clearAction)
        self.ui_toolbar.addWidget(self.ui_itemsLabel)
        self.ui_toolbar.addAction(addAction)

        self.ui_layout.addWidget(self.ui_list)
        self.ui_layout.addWidget(self.ui_toolbar)

        self.setLayout(self.ui_layout)

        self.update()
        self.updateLabel()

    def clearAction(self):

        self.ui_list.setRowCount(0)
        self.updateLabel()

        self.listChangedEvent()

    def addItem(self, host, port):

        index = self.ui_list.rowCount()
        self.ui_list.insertRow(index)

        host_item = QTableWidgetItem(host)
        port_item = QTableWidgetItem(port)

        action = SourcesRemoveButton(self, self.itemId)
        action.triggered.connect(self.listRemoveClicked)

        self.ui_list.setItem(index, 0, host_item)
        self.ui_list.setItem(index, 1, port_item)
        self.ui_list.setCellWidget(index, 2, action)

        self.ui_list.setCurrentCell(index, 0)
        self.ui_list.editItem(host_item)
        self.updateLabel()

    def addAction(self):

        self.initHost += 1
        self.initPort += 1
        self.itemId += 1

        self.addItem("127.0.0." + str(self.initHost), str(self.initPort))

    def listRemoveClicked(self, action):

        for index in range(self.ui_list.rowCount()):
            item = self.ui_list.cellWidget(index, 2)

            if item and action.id == item.id:
                self.ui_list.removeRow(index)

        self.listChangedEvent()

    def resizeEvent(self, event):

        self.updateLabel()

    def updateLabel(self):

        self.ui_itemsLabel.setText("%d sources" % (self.ui_list.rowCount(),))

        qr = self.ui_panel_label.geometry()
        cp = self.rect().center()
        self.ui_panel_label.resize(self.rect().width(), qr.height())
        qr.moveCenter(cp)
        qr.setY(qr.y() - 47)
        self.ui_panel_label.move(qr.topLeft())

        if self.ui_list.rowCount() > 0:
            self.ui_panel_label.hide()
        else:
            self.ui_panel_label.show()

    def listChangedEvent(self):

        items = []

        for index in range(self.ui_list.rowCount()):
            host = self.ui_list.item(index, 0)
            port = self.ui_list.item(index, 1)

            if host and port:
                items.append([host.text(), port.text()])

        self.changed.emit(items)

    def listItemChanged(self, item):
        self.listChangedEvent()


class OSCSourceDialog(OSCSourceWidget):

    def __init__(self, parent=None):
        super(OSCSourceDialog, self).__init__(parent)

        if not PLATFORM_MAC:
            self.setWindowIcon(QIcon(':/icons/32.png'))

        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle('OSC Sources')
        self.setGeometry(300, 300, 240, 380)
        self.setMinimumSize(240, 380)


class SourcesTableWidget(QTableWidget):

    def __init__(self, parent=None):
        super(SourcesTableWidget, self).__init__(parent)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        original = self.verticalScrollBar()

        self.scrollbar = QScrollBar(Qt.Vertical, self)
        self.scrollbar.valueChanged.connect(original.setValue)

        original.valueChanged.connect(self.scrollbar.setValue)

        self.updateScrollbar()

    def paintEvent(self, event):
        QTableWidget.paintEvent(self, event)

        self.updateScrollbar()

        x = self.rowCount()
        y = self.selectedIndexes()

        for i in range(0, x):
            b = self.cellWidget(i, 2)

            if b and y and y[0].row() == i:
                b.setIconState(False)
            elif b:
                b.setIconState(True)

    def updateScrollbar(self):

        original = self.verticalScrollBar()

        if original.value() == original.maximum() and original.value() == 0:
            self.scrollbar.hide()
        else:
            self.scrollbar.show()

        self.scrollbar.setPageStep(original.pageStep())
        self.scrollbar.setRange(original.minimum(), original.maximum())
        self.scrollbar.resize(8, self.rect().height())
        self.scrollbar.move(self.rect().width() - 8, 0)

# optimization to prevent loading of same icons multiple times
SourcesRemoveButtonICON = None
SourcesRemoveButtonICON_HOVER = None


class SourcesRemoveButton(QWidget):

    triggered = pyqtSignal("QWidget")

    def __init__(self, parent, playlist):
        super(SourcesRemoveButton, self).__init__(parent)

        self.playlist = playlist
        self._icon = QPixmap(':/icons/remove-white.png')

    def paintEvent(self, event):

        size = 18

        p = QPainter()
        p.begin(self)

        p.drawPixmap(self.width() / 2 - size / 2, self.height() / 2 - size / 2, size, size, self._icon)

        p.end()

    def mousePressEvent(self, event):

        self.triggered.emit(self)

    def getPlaylist(self):
        """Get a playlist assigned to component"""

        return self.playlist

    def setIconState(self, flag):
        """Set icon state"""

        global SourcesRemoveButtonICON
        global SourcesRemoveButtonICON_HOVER

        if not SourcesRemoveButtonICON:
            SourcesRemoveButtonICON = QPixmap(':/icons/remove.png')
            SourcesRemoveButtonICON_HOVER = QPixmap(':/icons/remove-white.png')

        self._icon = SourcesRemoveButtonICON if flag else SourcesRemoveButtonICON_HOVER
