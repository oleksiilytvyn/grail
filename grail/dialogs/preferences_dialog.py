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

import os
import sys
import sqlite3 as lite

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.utils import *
from grail.data import Settings, BibleManager, Song, ConnectionManager
from grail.widgets import SearchListWidget, SearchListItem
from grail.dialogs.osc_source_dialog import OSCSourceWidget


class PreferencesDialog(QDialog):
    osc_in_changed = pyqtSignal(object)
    osc_out_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)

        self._init_ui()

    def className(self):
        return 'PreferencesDialog'

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

        items = ['General', 'OSC Input', 'OSC Output', 'Bible']

        for index, item in enumerate(items):
            listitem = SearchListItem()
            listitem.setText(item)
            listitem.setItemData(index)

            self.ui_sidebar_list.addItem(listitem)

        self.ui_panel = QStackedWidget()
        self.ui_panel.addWidget(GeneralPanel())

        osc_in_panel = OSCInputPanel()
        osc_in_panel.changed.connect(self.osc_in_changed_event)
        self.ui_panel.addWidget(osc_in_panel)

        self.osc_out_panel = OSCOutputPanel()
        self.osc_out_panel.changed.connect(self.osc_out_changed_event)
        self.ui_panel.addWidget(self.osc_out_panel)

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
        self.ui_splitter.setStretchFactor(0, 0)
        self.ui_splitter.setStretchFactor(1, 1)

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

        panel = self.ui_panel.widget(item.data)

        if panel:
            panel.update()

    def osc_in_changed_event(self, items):
        pass

    def osc_out_changed_event(self, items):

        Settings.deleteOSCOutputRules()

        for item in items:
            if item[0] and item[1]:
                Settings.addOSCOutputRule(item[0], int(item[1]))

        self.osc_out_changed.emit(items)


class GeneralPanel(QWidget):

    def __init__(self, parent=None):
        super(GeneralPanel, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):

        self.ui_reset_btn = QPushButton("Reset")
        self.ui_reset_btn.clicked.connect(self.reset_action)
        self.ui_reset_label = QLabel("Restore all settings to original state and clear library.")

        self.ui_import_btn = QPushButton("Import library")
        self.ui_import_btn.clicked.connect(self.import_action)
        self.ui_import_label = QLabel("Add songs from a library file.")

        self.ui_export_btn = QPushButton("Export library")
        self.ui_export_btn.clicked.connect(self.export_action)
        self.ui_export_label = QLabel("Save my library of songs to file.")

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setContentsMargins(12, 12, 12, 12)

        if PLATFORM_MAC:
            self.ui_layout.setSpacing(8)
        else:
            self.ui_layout.setSpacing(0)

        self.ui_layout.addWidget(self.ui_reset_btn, 0, Qt.AlignLeft)
        self.ui_layout.addWidget(self.ui_reset_label)
        self.ui_layout.addSpacing(24)

        self.ui_layout.addWidget(self.ui_import_btn, 0, Qt.AlignLeft)
        self.ui_layout.addWidget(self.ui_import_label)
        self.ui_layout.addSpacing(24)

        self.ui_layout.addWidget(self.ui_export_btn, 0, Qt.AlignLeft)
        self.ui_layout.addWidget(self.ui_export_label)

        self.ui_layout.addStretch()

        self.setLayout(self.ui_layout)

    def import_action(self):

        location = QStandardPaths.locate(QStandardPaths.DocumentsLocation, "",
                                         QStandardPaths.LocateDirectory)
        path, ext = QFileDialog.getOpenFileName(self, "Open File...", location, "*.grail1-lib")

        if not os.path.isfile(path):
            return

        connection = lite.connect(path)
        connection.row_factory = lite.Row
        cursor = connection.cursor()

        # add songs to library
        cursor.execute("SELECT * FROM songs")
        songs = cursor.fetchall()

        progress = QProgressDialog("Importing...", "Abort", 0, len(songs), None)
        progress.setWindowTitle("Grail")
        progress.setLabelText("Importing...")
        progress.setWindowModality(Qt.WindowModal)
        progress.setFixedSize(300, 60)
        progress.setCancelButton(None)

        if not PLATFORM_MAC:
            progress.setWindowIcon(QIcon(':/icons/32.png'))

        if PLATFORM_UNIX:
            progress.setWindowIcon(QIcon(':/icons/256.png'))

        index = 0
        for song in songs:
            available = False

            for search_item in Song.search(song['title']):

                test_availability = search_item['title'] == song['title'] and search_item['artist'] == song[
                    'artist'] and search_item['album'] == song['album'] and search_item['year'] == song['year']

                if test_availability:
                    available = True
                    sid = search_item['id']

            if not available:
                sid = Song.add(song['title'], song['artist'], song['album'], song['year'])

                cursor.execute("SELECT * FROM pages WHERE song = ? ORDER BY sort ASC", (song['id'],))

                for page in cursor.fetchall():
                    Song.addPage(sid, page['page'])

            progress.setValue(index)
            index += 1

        progress.setValue(len(songs))

        connection.close()

    def export_action(self):

        def rchop(thestring, ending):
            if thestring.endswith(ending):
                return thestring[:-len(ending)]
            return thestring

        location = QStandardPaths.locate(QStandardPaths.DocumentsLocation, "",
                                         QStandardPaths.LocateDirectory)
        location = os.path.join(location, "Grail library.grail1-lib")

        path, ext = QFileDialog.getSaveFileName(self, "Save file", location, "*.grail1-lib")
        filepath = rchop(path, '.grail1-lib') + '.grail1-lib'

        if not path:
            return

        directory = os.path.dirname(os.path.realpath(filepath))

        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.isfile(filepath):
            open(filepath, 'w+')
        else:
            open(filepath, 'w')

        connection = lite.connect(filepath)
        connection.row_factory = lite.Row

        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS songs")
        cursor.execute("""CREATE TABLE songs(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        artist TEXT,
                        album TEXT,
                        year INT)""")

        cursor.execute("DROP TABLE IF EXISTS pages")
        cursor.execute("CREATE TABLE pages(id INTEGER PRIMARY KEY AUTOINCREMENT, song INT, sort INT, page TEXT)")

        cursor.execute("DROP TABLE IF EXISTS playlists")
        cursor.execute("CREATE TABLE playlists(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT)")

        cursor.execute("DROP TABLE IF EXISTS playlist")
        cursor.execute("""CREATE TABLE playlist(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        playlist INT,
                        sort INT,
                        song INT,
                        collapsed INTEGER)""")

        cursor.execute("INSERT INTO playlists VALUES(?, ?)", (1, 'Default playlist'))

        for song in Song.getList():

            record = (song['id'], song['title'], song['artist'], song['album'], song['year'])
            cursor.execute("INSERT INTO songs VALUES(?, ?, ?, ?, ?)", record)

            sort = 0
            for page in Song.getPages(song['id']):
                cursor.execute("INSERT INTO pages VALUES(NULL, ?, ?, ?)", (song['id'], sort, page['page']))
                sort += 1

        connection.commit()
        connection.close()

    def reset_action(self):

        message = QMessageBox(self)
        message.setWindowTitle("Grail")
        message.setText("Restore settings")
        message.setInformativeText("Do you want to restore all setting and library to defaults?")
        message.setStandardButtons(QMessageBox.Cancel | QMessageBox.RestoreDefaults)
        message.setDefaultButton(QMessageBox.Cancel)

        if not PLATFORM_MAC:
            message.setWindowIcon(QIcon(':/icons/32.png'))

        if PLATFORM_UNIX:
            message.setWindowIcon(QIcon(':/icons/256.png'))

        result = message.exec_()

        if result == QMessageBox.RestoreDefaults:
            # close grail
            qApp.quit()
            ConnectionManager.close()

            # remove files
            remove_file(get_data_path() + '/settings.db')
            remove_file(get_data_path() + '/history.db')
            remove_file(get_data_path() + '/songs.db')

            copy_file(get_path() + '/default/songs.db', get_data_path() + '/songs.db')

            # run grail
            python = sys.executable
            os.execl(python, python, * sys.argv)


class OSCInputPanel(QWidget):

    changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super(OSCInputPanel, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):
        self.ui_label = QLabel("OSC Input not supported", self)
        self.ui_label.move(20, 20)


class OSCOutputPanel(OSCSourceWidget):

    def __init__(self):
        super(OSCOutputPanel, self).__init__()

        self.ui_itemsLabel.setText('0 destinations')
        self.ui_panel_label.setText('No destinations')

        self.changed.connect(self._items_changed)

        osc_out = Settings.getOSCOutputRules()

        for item in osc_out:
            self.addItem(item['host'], str(item['port']))

        self.updateLabel()

    def update(self):
        super(OSCOutputPanel, self).update()

        self.updateLabel()

    def updateLabel(self):

        self.ui_itemsLabel.setText("%d destinations" % (self.ui_list.rowCount(),))

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

    def _items_changed(self, items):
        self.updateLabel()


class BiblePanel(QWidget):

    def __init__(self):
        super(BiblePanel, self).__init__()

        self._init_ui()
        self.update_list()

    def _init_ui(self):

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setSpacing(0)
        self.ui_layout.setContentsMargins(0, 0, 0, 0)

        self.ui_list = SearchListWidget()
        self.ui_list.setObjectName("bible_list")
        self.ui_list.setAlternatingRowColors(True)

        self.ui_toolbar_label = QLabel("1 installed")
        self.ui_toolbar_label.setObjectName("bible_toolbat_label")
        self.ui_toolbar_label.setAlignment(Qt.AlignCenter)
        self.ui_toolbar_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        install_action = QAction(QIcon(':/icons/add.png'), 'Install', self)
        install_action.setIconVisibleInMenu(True)
        install_action.triggered.connect(self.install_action)

        primary_action = QAction(QIcon(':/icons/save.png'), 'Set as primary', self)
        primary_action.setIconVisibleInMenu(True)
        primary_action.triggered.connect(self.primary_action)

        self.ui_toolbar = QToolBar()
        self.ui_toolbar.setObjectName("bible_toolbar")
        self.ui_toolbar.setIconSize(QSize(16, 16))
        self.ui_toolbar.addAction(install_action)
        self.ui_toolbar.addWidget(self.ui_toolbar_label)
        self.ui_toolbar.addAction(primary_action)

        self.ui_layout.addWidget(self.ui_list)
        self.ui_layout.addWidget(self.ui_toolbar)

        self.setLayout(self.ui_layout)

    def install_action(self):

        location = QStandardPaths.locate(QStandardPaths.DocumentsLocation, "",
                                         QStandardPaths.LocateDirectory)
        path, ext = QFileDialog.getOpenFileName(self, "Open File...", location, "*.db")

        BibleManager.install(path)

        self.update_list()

    def primary_action(self):

        items = self.ui_list.selectedItems()

        if len(items) > 0:
            BibleManager.set(items[0].data['path'])

        self.update_list()

    def update_list(self):

        bibles = BibleManager.list()
        selected_path = Settings.get('bible.path')

        self.ui_list.clear()
        self.ui_toolbar_label.setText("%d installed" % len(bibles))

        for bible in bibles:

            item = SearchListItem()
            item.setItemData(bible)

            if bible['path'] == selected_path:
                item.setText("%s - selected" % (bible['name'],))
            else:
                item.setText(bible['name'])

            self.ui_list.addItem(item)
