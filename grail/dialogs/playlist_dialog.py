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
from grail.data import Playlist, Settings
from grail.widgets import *

from .balloon_dialog import BalloonDialog


class PlaylistDialog(BalloonDialog):
    """List of playlist's dialog"""

    selected = pyqtSignal(int)
    renamed = pyqtSignal(int)

    def __init__(self, parent=None):
        super(PlaylistDialog, self).__init__(parent)

        self.setBackgroundColor(QColor(75, 80, 86))
        self._init_ui()

    def _init_ui(self):

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setSpacing(0)
        self.ui_layout.setContentsMargins(0, 0, 0, 0)

        self.ui_list = PlaylistTableWidget()
        self.ui_list.setObjectName("playlistList")
        self.ui_list.setColumnCount(2)
        self.ui_list.verticalHeader().setVisible(False)
        self.ui_list.horizontalHeader().setVisible(False)
        self.ui_list.setHorizontalHeaderLabels(["Label", "Button"])
        self.ui_list.setShowGrid(False)

        header = self.ui_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)

        self.ui_list.setColumnWidth(1, 42)
        self.ui_list.setAlternatingRowColors(True)
        self.ui_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui_list.cellChanged.connect(self._list_cell_changed)
        self.ui_list.itemSelectionChanged.connect(self._list_item_selected)

        self.ui_edit_action = QAction(QIcon(':/icons/edit.png'), 'Edit', self)
        self.ui_edit_action.triggered.connect(self.edit_action)

        self.ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add', self)
        self.ui_add_action.setIconVisibleInMenu(True)
        self.ui_add_action.triggered.connect(self.add_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ui_toolbar = QToolBar()
        self.ui_toolbar.setIconSize(QSize(16, 16))
        self.ui_toolbar.setObjectName("playlistDialogToolbar")
        self.ui_toolbar.addAction(self.ui_edit_action)
        self.ui_toolbar.addWidget(spacer)
        self.ui_toolbar.addAction(self.ui_add_action)

        self.ui_layout.addWidget(self.ui_list)
        self.ui_layout.addWidget(self.ui_toolbar)

        self.setLayout(self.ui_layout)
        self.setWindowTitle('Playlist')
        self.setGeometry(100, 300, 240, 300)
        self.setMinimumSize(240, 300)

        self.update_list()

    def add_action(self):
        """Add new playlist"""

        playlist = Playlist.get(Playlist.add("Untitled"))
        x = self.ui_list.rowCount()
        item = PlaylistDialogItem(playlist)
        button = PlaylistButton(self, playlist)
        button.triggered.connect(self._list_remove_clicked)

        self.ui_list.insertRow(x)
        self.ui_list.setItem(x, 0, item)
        self.ui_list.setCellWidget(x, 1, button)
        self.ui_list.setCurrentCell(x, 0)
        self.ui_list.editItem(self.ui_list.item(x, 0))

    def edit_action(self):
        """Edit selected playlist"""

        x = self.ui_list.rowCount()
        id = Settings.get('playlist')

        for i in range(0, x):
            item = self.ui_list.item(i, 0)

            if int(item.getPlaylist()['id']) == int(id):
                self._list_item_clicked(item)
                self.ui_list.editItem(item)

    def update_list(self):

        playlists = Playlist.getPlaylists()

        self.ui_list.setRowCount(len(playlists))

        x = 0
        id = int(Settings.get('playlist'))

        for playlist in playlists:
            item = PlaylistDialogItem(playlist)
            self.ui_list.setItem(x, 0, item)

            if int(playlist['id']) == id:
                self.ui_list.setCurrentItem(item)
                self._list_item_clicked(item)
                self.ui_list.scrollToItem(self.ui_list.item(x, 0))

            button = PlaylistButton(self, playlist)
            button.triggered.connect(self._list_remove_clicked)

            self.ui_list.setCellWidget(x, 1, button)

            x += 1

    def _list_cell_changed(self, row, column):

        item = self.ui_list.item(row, column)
        playlist = item.getPlaylist()
        Playlist.update(playlist['id'], item.text())

        self.renamed.emit(playlist['id'])

    def _list_remove_clicked(self, action):

        current = action.getPlaylist()['id']
        selected = self.ui_list.item(self.ui_list.currentRow(), 0)
        selected_id = selected.getPlaylist()['id']
        playlist_id = selected_id

        if current == selected_id:
            playlists = Playlist.getPlaylists()
            playlist_id = playlists[0]['id']

        Playlist.delete(current)

        self.update_list()
        self.selected.emit(playlist_id)

    def _list_item_clicked(self, item):

        x = self.ui_list.rowCount()
        y = self.ui_list.selectedIndexes()[0].row()

        for i in range(0, x):
            b = self.ui_list.cellWidget(i, 1)

            if b and y == i:
                b.setIconState(False)
            elif b:
                b.setIconState(True)

        self.selected.emit(item.getPlaylist()['id'])

    def _list_item_selected(self):

        item = self.ui_list.item(self.ui_list.currentRow(), 0)

        self._list_item_clicked(item)

    def showAt(self, point):

        super(PlaylistDialog, self).showAt(point)

        self.ui_list.update()


class PlaylistDialogItem(QTableWidgetItem):
    """Playlist item inside playlist dialog"""

    def __init__(self, item):
        super(PlaylistDialogItem, self).__init__(item['title'])

        self.playlist = item
        self.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def getPlaylist(self):
        return self.playlist


# optimization to prevent loading of same icons multiple times
PlaylistRemoveButtonICON = None
PlaylistRemoveButtonICON_HOVER = None


class PlaylistButton(QWidget):

    triggered = pyqtSignal("QWidget")

    def __init__(self, parent, playlist):
        super(PlaylistButton, self).__init__(parent)

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

        global PlaylistRemoveButtonICON
        global PlaylistRemoveButtonICON_HOVER

        if not PlaylistRemoveButtonICON:
            PlaylistRemoveButtonICON = QPixmap(':/icons/remove.png')
            PlaylistRemoveButtonICON_HOVER = QPixmap(':/icons/remove-white.png')

        self._icon = PlaylistRemoveButtonICON if flag else PlaylistRemoveButtonICON_HOVER



class PlaylistTableWidget(QTableWidget):
    """List widget with remove button"""

    def __init__(self, parent=None):
        """Initialize PlaylistTableWidget"""

        super(PlaylistTableWidget, self).__init__(parent)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAutoScroll(False)

        original = self.verticalScrollBar()

        self.scrollbar = QScrollBar(Qt.Vertical, self)
        self.scrollbar.valueChanged.connect(original.setValue)
        self.scrollbar.rangeChanged.connect(self.scroll_to_selected)

        original.valueChanged.connect(self.scrollbar.setValue)

        self.update_scrollbar()

    def paintEvent(self, event):
        """Draw widget"""

        QTableWidget.paintEvent(self, event)

        self.update_scrollbar()

        x = self.rowCount()
        y = self.selectedIndexes()[0].row()

        for i in range(0, x):
            b = self.cellWidget(i, 1)

            if b and y == i:
                b.setIconState(False)
            elif b:
                b.setIconState(True)

    def update(self):
        """Update ui components"""

        super(PlaylistTableWidget, self).update()

        self.update_scrollbar()

    def update_scrollbar(self):
        """Update scrollbar to draw properly"""

        original = self.verticalScrollBar()

        if not hasattr(self, 'scrollbar'):
            return

        if original.value() == original.maximum() and original.value() == 0:
            self.scrollbar.hide()
        else:
            self.scrollbar.show()

        self.scrollbar.setPageStep(original.pageStep())
        self.scrollbar.setRange(original.minimum(), original.maximum())
        self.scrollbar.resize(8, self.rect().height())
        self.scrollbar.move(self.rect().width() - 8, 0)

    def scroll_to_selected(self):
        """Scroll to selected item"""

        selected = self.selectedIndexes()

        if len(selected) == 0:
            x = 0
            self.setCurrentCell(x, 0)
        else:
            x = selected[0].row()

        self.scrollToItem(self.item(x, 0))
