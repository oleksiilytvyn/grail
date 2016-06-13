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

# generic imports
import sqlite3 as lite

# OSC library
from osc import OSCMessage, OSCClient

# PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# grail library
from grail import resources
from grail.data import *
from grail.widgets import *
from grail.dialogs import *
from grail.utils import *


class Grail(QMainWindow):
    """
    Grail application class
    """

    def __init__(self, parent=None):
        super(Grail, self).__init__(parent)

        self.subscribers = []

        self._init_ui()
        self._init_osc()

    def _init_ui(self):
        """
        Initialize UI
        """

        self._init_menubar()

        # dialogs
        self.dialog_about = AboutDialog()
        self.dialog_preferences = PreferencesDialog()
        self.dialog_preferences.osc_out_changed.connect(self.update_osc)

        self.dialog_song = SongDialog()
        self.dialog_song.updateComplete.connect(self.updateSearch)
        self.dialog_song.updateComplete.connect(self.updatePlaylist)

        self.dialog_playlist = PlaylistDialog()
        self.dialog_playlist.selected.connect(self.playlistSelectedAction)
        self.dialog_playlist.renamed.connect(self.playlistSelectedAction)

        self.prefs = DisplayPreferences()
        self.prefs.restore()

        self.display = DisplayDialog(None, self.prefs)
        self.display.modeChanged.connect(self.updateOutputMenu)
        self.display.testCardChanged.connect(self.updateOutputMenu)

        # left
        self._init_ui_library()

        # center
        self._init_ui_playlist()

        # right
        self._init_ui_preview()

        # vertical spliter
        self.ui_vertical_spliter = QSplitter(Qt.Vertical)
        self.ui_vertical_spliter.setObjectName("verticalSpliter")
        self.ui_vertical_spliter.addWidget(self.ui_preview_label)
        self.ui_vertical_spliter.addWidget(self.ui_preview_panel)
        self.ui_vertical_spliter.setCollapsible(1, False)
        self.ui_vertical_spliter.setSizes([400, 120])
        self.ui_vertical_spliter.setHandleWidth(1)

        # stacked widget
        self.ui_left_sidebar = QStackedWidget()
        self.ui_left_sidebar.addWidget(self.ui_songs_panel)
        self.ui_left_sidebar.addWidget(self.ui_media_panel)

        # spliter
        self.ui_spliter = QSplitter()
        self.ui_spliter.setObjectName("spliter")

        self.ui_spliter.addWidget(self.ui_left_sidebar)
        self.ui_spliter.addWidget(self.ui_playlist_panel)
        self.ui_spliter.addWidget(self.ui_vertical_spliter)

        self.ui_left_sidebar.setCurrentIndex(0)

        self.ui_spliter.setCollapsible(0, False)
        self.ui_spliter.setCollapsible(2, False)
        self.ui_spliter.setHandleWidth(1)
        self.ui_spliter.splitterMoved.connect(self.splitterMoved)

        self.setCentralWidget(self.ui_spliter)

        playlist_id = Settings.get('playlist')

        if playlist_id is not None:
            self.playlist = Playlist.get(playlist_id)
        else:
            self.playlist = Playlist.getPlaylists()[0]

        self.updateSearch()
        self.updatePlaylist()

        if not PLATFORM_MAC:
            self.setWindowIcon(QIcon(':/icons/32.png'))

        if PLATFORM_UNIX:
            self.setWindowIcon(QIcon(':/icons/256.png'))

        self.setGeometry(300, 300, 800, 480)
        self.setMinimumSize(320, 240)
        self.setWindowTitle("Grail")
        self.center()
        self.show()
        self.updateLabels()
        self.updateOutputMenu()

        History.changed.connect(self.updateSearch)

    def _init_menubar(self):

        # menubar
        self.ui_menubar = QMenuBar(self)

        # Help
        self.ui_aboutAction = QAction('About Grail', self)
        self.ui_aboutAction.triggered.connect(self.aboutAction)

        # Import Playlist
        self.ui_importPlaylistAction = QAction('Import playlist', self)
        self.ui_importPlaylistAction.triggered.connect(self.importPlaylistAction)

        # Export Playlist
        self.ui_exportPlaylistAction = QAction('Export playlist', self)
        self.ui_exportPlaylistAction.triggered.connect(self.exportPlaylistAction)

        # Clear history
        self.ui_clearHistoryAction = QAction('Clear history', self)
        self.ui_clearHistoryAction.triggered.connect(self.clearHistoryAction)

        # Display
        self.ui_showAction = QAction('Show', self)
        self.ui_showAction.triggered.connect(self.showAction)

        self.ui_blackoutAction = QAction('Blackout', self)
        self.ui_blackoutAction.setShortcut('Ctrl+Z')
        self.ui_blackoutAction.setShortcutContext(Qt.ApplicationShortcut)
        self.ui_blackoutAction.triggered.connect(self.blackoutAction)

        self.ui_blackoutMediaAction = QAction('Blackout Media', self)
        self.ui_blackoutMediaAction.setShortcut('Ctrl+Shift+Z')
        self.ui_blackoutMediaAction.setShortcutContext(Qt.ApplicationShortcut)
        self.ui_blackoutMediaAction.triggered.connect(self.blackoutMediaAction)

        self.ui_blackoutTextAction = QAction('Blackout Text', self)
        self.ui_blackoutTextAction.setShortcut('Ctrl+Alt+Z')
        self.ui_blackoutTextAction.setShortcutContext(Qt.ApplicationShortcut)
        self.ui_blackoutTextAction.triggered.connect(self.blackoutTextAction)

        self.ui_nextPageAction = QAction('Next page', self)
        self.ui_nextPageAction.setShortcut('Ctrl+N')
        self.ui_nextPageAction.setShortcutContext(Qt.ApplicationShortcut)
        self.ui_nextPageAction.triggered.connect(self.nextPageAction)

        self.ui_previousPageAction = QAction('Previous page', self)
        self.ui_previousPageAction.setShortcut('Ctrl+Shift+N')
        self.ui_previousPageAction.setShortcutContext(Qt.ApplicationShortcut)
        self.ui_previousPageAction.triggered.connect(self.previousPageAction)

        self.ui_newDisplayAction = QAction('Open new display', self)
        self.ui_newDisplayAction.setShortcut('Ctrl+D')
        self.ui_newDisplayAction.setShortcutContext(Qt.ApplicationShortcut)
        self.ui_newDisplayAction.triggered.connect(self.newDisplayAction)

        self.ui_preferencesAction = QAction('Preferences', self)
        self.ui_preferencesAction.setShortcut('Ctrl+P')
        self.ui_preferencesAction.setShortcutContext(Qt.ApplicationShortcut)
        self.ui_preferencesAction.triggered.connect(self.preferencesAction)

        self.ui_showLibraryAction = QAction('Show Library', self)
        self.ui_showLibraryAction.setShortcut('Ctrl+L')
        self.ui_showLibraryAction.triggered.connect(self.showLibraryPanel)

        self.ui_showMediaAction = QAction('Show Media', self)
        self.ui_showMediaAction.setShortcut('Ctrl+M')
        self.ui_showMediaAction.triggered.connect(self.showMediaPanel)

        self.ui_toggleLibraryAction = QAction('Toggle Library sidebar', self)
        self.ui_toggleLibraryAction.triggered.connect(self.toggleLibrary)

        self.ui_togglePreviewAction = QAction('Toggle Preview sidebar', self)
        self.ui_togglePreviewAction.triggered.connect(self.togglePreview)

        self.ui_navigateToSearchAction = QAction('Search library', self)
        self.ui_navigateToSearchAction.setShortcut('Ctrl+`')
        self.ui_navigateToSearchAction.triggered.connect(self.searchNavigateAction)

        self.ui_navigateToPlaylistAction = QAction('Navigate to playlist', self)
        self.ui_navigateToPlaylistAction.setShortcut('Ctrl+1')
        self.ui_navigateToPlaylistAction.triggered.connect(self.playlistNavigateAction)

        # Songs and playlists
        self.ui_addSongAction = QAction('Add new Song', self)
        self.ui_addSongAction.triggered.connect(self.addSongAction)

        self.ui_outputDisabledAction = QAction('Disabled', self)
        self.ui_outputDisabledAction.setShortcut('Ctrl+Shift+D')
        self.ui_outputDisabledAction.setShortcutContext(Qt.ApplicationShortcut)
        self.ui_outputDisabledAction.triggered.connect(self.displayOutputDisabledAction)
        self.ui_outputDisabledAction.setCheckable(True)

        self.ui_showTestCardAction = QAction('Show Test Card', self)
        self.ui_showTestCardAction.setShortcut('Ctrl+T')
        self.ui_showTestCardAction.setShortcutContext(Qt.ApplicationShortcut)
        self.ui_showTestCardAction.triggered.connect(self.displayShowTestCardAction)
        self.ui_showTestCardAction.setCheckable(True)

        self.ui_outputPreferencesAction = QAction('Advanced Preferences', self)
        self.ui_outputPreferencesAction.setShortcut('Ctrl+Shift+P')
        self.ui_outputPreferencesAction.setShortcutContext(Qt.ApplicationShortcut)
        self.ui_outputPreferencesAction.triggered.connect(self.displayOutputPreferencesAction)

        # edit menu
        self.ui_menu_edit = self.ui_menubar.addMenu('&Edit')
        self.ui_menu_edit.addAction(self.ui_addSongAction)
        self.ui_menu_edit.addSeparator()
        self.ui_menu_edit.addAction(self.ui_importPlaylistAction)
        self.ui_menu_edit.addAction(self.ui_exportPlaylistAction)

        self.ui_menu_edit.addSeparator()
        self.ui_menu_edit.addAction(self.ui_clearHistoryAction)

        if not PLATFORM_MAC:
            self.ui_menu_edit.addSeparator()

        self.ui_menu_edit.addAction(self.ui_preferencesAction)

        # display menu
        self.ui_menu_display = self.ui_menubar.addMenu('&Display')
        self.ui_menu_display.addAction(self.ui_newDisplayAction)
        self.ui_menu_display.addSeparator()
        self.ui_menu_display.addAction(self.ui_showAction)
        self.ui_menu_display.addAction(self.ui_blackoutAction)
        self.ui_menu_display.addAction(self.ui_blackoutTextAction)
        self.ui_menu_display.addAction(self.ui_blackoutMediaAction)
        self.ui_menu_display.addSeparator()
        self.ui_menu_display.addAction(self.ui_previousPageAction)
        self.ui_menu_display.addAction(self.ui_nextPageAction)

        # view menu
        self.ui_menu_view = self.ui_menubar.addMenu('&View')
        self.ui_menu_view.addAction(self.ui_showLibraryAction)
        self.ui_menu_view.addAction(self.ui_showMediaAction)
        self.ui_menu_view.addSeparator()
        self.ui_menu_view.addAction(self.ui_toggleLibraryAction)
        self.ui_menu_view.addAction(self.ui_togglePreviewAction)
        self.ui_menu_view.addSeparator()
        self.ui_menu_view.addAction(self.ui_navigateToSearchAction)
        self.ui_menu_view.addAction(self.ui_navigateToPlaylistAction)

        # output menu
        self.ui_menu_output = self.ui_menubar.addMenu('&Output')

        # help menu
        self.ui_menu_help = self.ui_menubar.addMenu('&Help')
        self.ui_menu_help.addAction(self.ui_aboutAction)

        if not PLATFORM_MAC:
            self.setMenuBar(self.ui_menubar)

    def _init_ui_library(self):
        """Initialize UI of Library/Media panel"""

        self.ui_media_panel = MediaWidget()
        self.ui_media_panel.itemSelected.connect(self.imageSelected)
        self.ui_media_panel.switchMode.connect(self.showLibraryPanel)
        self.ui_media_panel.blackoutImage.connect(self.setBlackoutImage)
        self.ui_media_panel.textImage.connect(self.setTextImage)

        self.ui_songs_bar = QVBoxLayout()
        self.ui_songs_bar.setObjectName("library_bar")
        self.ui_songs_bar.setSpacing(0)
        self.ui_songs_bar.setContentsMargins(0, 0, 0, 0)

        self.ui_songs_search = QSearchEdit()
        self.ui_songs_search.setObjectName("library_search")
        self.ui_songs_search.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.ui_songs_search.textChanged.connect(self.searchAction)
        self.ui_songs_search.keyPressed.connect(self.searchKeyEvent)

        self.ui_songs_list = SearchListWidget()
        self.ui_songs_list.setObjectName("library_list")
        self.ui_songs_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui_songs_list.setAlternatingRowColors(True)

        self.ui_songs_list.itemClicked.connect(self.songClicked)
        self.ui_songs_list.itemDoubleClicked.connect(self.songDoubleClicked)
        self.ui_songs_list.currentItemChanged.connect(self.songClicked)
        self.ui_songs_list.keyPressed.connect(self.songKeyEvent)
        self.ui_songs_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui_songs_list.customContextMenuRequested.connect(self.songContextMenu)

        addSongAction = QAction(QIcon(':/icons/add.png'), 'Add', self)
        addSongAction.setIconVisibleInMenu(True)
        addSongAction.triggered.connect(self.addSongAction)

        switchViewAction = QAction(QIcon(':/icons/media.png'), 'Media', self)
        switchViewAction.setIconVisibleInMenu(True)
        switchViewAction.triggered.connect(self.toggleLeftView)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ui_songs_toolbar = QToolBar()
        self.ui_songs_toolbar.setObjectName("library_toolbar")
        self.ui_songs_toolbar.setIconSize(QSize(16, 16))
        self.ui_songs_toolbar.addAction(addSongAction)
        self.ui_songs_toolbar.addWidget(spacer)
        self.ui_songs_toolbar.addAction(switchViewAction)

        self.ui_songs_bar.addWidget(self.ui_songs_search)
        self.ui_songs_bar.addWidget(self.ui_songs_list)
        self.ui_songs_bar.addWidget(self.ui_songs_toolbar)

        self.ui_songs_panel = QWidget()
        self.ui_songs_panel.setObjectName("library_panel")
        self.ui_songs_panel.setLayout(self.ui_songs_bar)
        self.ui_songs_panel.setMinimumSize(100, 100)

        self.ui_songs_bar_label = QLabel("There are no results", self.ui_songs_list)
        self.ui_songs_bar_label.setAlignment(Qt.AlignCenter)
        self.ui_songs_bar_label.setFont(QFont('Decorative', 12))

    def _init_ui_playlist(self):
        """Initialize UI of playlist panel"""

        self.ui_playlist_bar = QVBoxLayout()
        self.ui_playlist_bar.setSpacing(0)
        self.ui_playlist_bar.setContentsMargins(0, 0, 0, 0)

        self.ui_playlist_toolbar = QToolBar()
        self.ui_playlist_toolbar.setObjectName("playlist_toolbar")

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ui_playlist_label = PlaylistLabel()
        self.ui_playlist_label.setObjectName("playlist_label")
        self.ui_playlist_label.setText("Playlist (0 Songs)")
        self.ui_playlist_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui_playlist_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui_playlist_label.clicked.connect(self.playlistLabelClicked)

        self.ui_playlist_toolbar.addWidget(self.ui_playlist_label)

        self.ui_playlist_tree = PlaylistTreeWidget()
        self.ui_playlist_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui_playlist_tree.itemClicked.connect(self.pageClicked)
        self.ui_playlist_tree.itemDoubleClicked.connect(self.pageDoubleClicked)
        self.ui_playlist_tree.customContextMenuRequested.connect(self.playlistContextMenu)
        self.ui_playlist_tree.keyPressed.connect(self.playlistKeyEvent)
        self.ui_playlist_tree.orderChanged.connect(self.playlistReordered)
        self.ui_playlist_tree.itemCollapsed.connect(self.playlistItemCollapsed)
        self.ui_playlist_tree.itemExpanded.connect(self.playlistItemCollapsed)

        self.ui_playlist_bar.addWidget(self.ui_playlist_tree)
        self.ui_playlist_bar.addWidget(self.ui_playlist_toolbar)

        self.ui_playlist_panel = QWidget()
        self.ui_playlist_panel.setObjectName("playlist_panel")
        self.ui_playlist_panel.setLayout(self.ui_playlist_bar)
        self.ui_playlist_panel.setMinimumSize(100, 100)

        self.ui_playlist_panel_label = QLabel("Nothing in playlist", self.ui_playlist_panel)
        self.ui_playlist_panel_label.setAlignment(Qt.AlignCenter)
        self.ui_playlist_panel_label.setFont(QFont('Decorative', 12))

    def _init_ui_preview(self):
        """Initialize preview panel"""

        self.ui_preview_bar = QVBoxLayout()
        self.ui_preview_bar.setSpacing(0)
        self.ui_preview_bar.setContentsMargins(0, 0, 0, 0)

        self.ui_preview_label = QLabel()
        self.ui_preview_label.setObjectName("preview_label")
        self.ui_preview_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        self.ui_preview_edit = QuickTextEdit()
        self.ui_preview_edit.setObjectName("preview_edit")
        self.ui_preview_edit.textChanged.connect(self.quickEditChanged)

        self.ui_preview_toolbar = QToolBar()
        self.ui_preview_toolbar.setObjectName("preview_toolbar")
        self.ui_preview_toolbar.setIconSize(QSize(16, 16))

        blackoutAction = QAction(QIcon(':/icons/stop.png'), 'Blackout', self)
        blackoutAction.triggered.connect(self.blackoutAction)

        showQuickAction = QAction(QIcon(':/icons/play.png'), 'Show', self)
        showQuickAction.triggered.connect(self.showQuickAction)
        showQuickAction.setIconVisibleInMenu(True)

        saveQuickAction = QAction(QIcon(':/icons/save.png'), 'Save', self)
        saveQuickAction.triggered.connect(self.saveAction)
        saveQuickAction.setIconVisibleInMenu(True)

        self.ui_preview_liveAction = QAction(QIcon(':/icons/live.png'), 'Live', self)
        self.ui_preview_liveAction.setCheckable(True)
        self.ui_preview_liveAction.setChecked(False)
        self.ui_preview_liveAction.setIconVisibleInMenu(True)

        self.ui_preview_toolbar.addAction(showQuickAction)
        self.ui_preview_toolbar.addAction(saveQuickAction)
        self.ui_preview_toolbar.addAction(blackoutAction)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ui_preview_toolbar.addWidget(spacer)
        self.ui_preview_toolbar.addAction(self.ui_preview_liveAction)

        self.ui_preview_bar.addWidget(self.ui_preview_edit)
        self.ui_preview_bar.addWidget(self.ui_preview_toolbar)

        self.ui_preview_panel = QWidget()
        self.ui_preview_panel.setLayout(self.ui_preview_bar)
        self.ui_preview_panel.setMinimumSize(200, 100)

    def _init_osc(self):

        self.subscribers = []
        self.listeners = []
        self.displays = []

        for rule in Settings.getOSCOutputRules():
            self.subscribers.append(OSCClient(rule["host"], rule["port"]))

        ports = []

        for rule in Settings.getOSCInputRules():
            if not rule['port'] in ports:
                ports.append(rule['port'])

    def update_osc(self, items):

        self.subscribers = []

        for rule in Settings.getOSCOutputRules():
            self.subscribers.append(OSCClient(rule["host"], rule["port"]))

    def send(self, item):

        text = item.message

        if text == "":
            text = " "

        self.display.setMessage(text)

        for display in self.displays:
            display.setMessage(text)

        msg = OSCMessage(address="/grail/message")
        msg.add(bytes(text, "utf-8"))
        msg.add(item.type)

        for client in self.subscribers:
            client.send(msg)

        if item.type != HistoryItem.TYPE_QUICK and item.type != HistoryItem.TYPE_BLACKOUT:
            History.add(item.type, item.title, text)

    # UI

    def resizeEvent(self, event):

        self.updateLabels()

    def closeEvent(self, event):

        self.prefs.save()
        self.dialog_about.close()
        self.dialog_preferences.close()
        self.dialog_song.close()
        self.display.setAttribute(Qt.WA_DeleteOnClose, True)
        self.display.close(True)

        self.dialog_playlist.close()

        for display in self.displays:
            display.setAttribute(Qt.WA_DeleteOnClose, True)
            display.close(True)

        ConnectionManager.close()

    def center(self):
        """Center a main window"""

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

        self.move(qr.topLeft())

    def toggleLeftView(self):

        index = self.ui_left_sidebar.currentIndex()
        self.ui_left_sidebar.setCurrentIndex(0 if index == 1 else 1)

    def showLibraryPanel(self):

        self.ui_left_sidebar.setCurrentIndex(0)

    def showMediaPanel(self):

        self.ui_left_sidebar.setCurrentIndex(1)

    def searchNavigateAction(self):

        self.ui_songs_search.setText("")
        self.ui_songs_search.setFocus(Qt.OtherFocusReason)

    def playlistNavigateAction(self):

        self.ui_playlist_tree.setFocus(Qt.OtherFocusReason)

    def splitterMoved(self, pos, index):

        self.updateLabels()

    def updateLabels(self):
        qr = self.ui_songs_bar_label.geometry()
        sr = self.ui_songs_panel.rect()
        cp = sr.center()
        self.ui_songs_bar_label.resize(sr.width(), qr.height())

        qr.moveTo(cp.x() - sr.width() / 2, sr.height() / 2 - qr.height() / 2 - 47)

        self.ui_songs_bar_label.move(qr.topLeft())

        qr = self.ui_playlist_panel_label.geometry()
        sr = self.ui_playlist_panel.rect()
        cp = sr.center()
        self.ui_playlist_panel_label.resize(self.ui_playlist_panel.rect().width(), qr.height())

        qr.moveTo(cp.x() - sr.width() / 2, sr.height() / 2 - qr.height() / 2)

        self.ui_playlist_panel_label.move(qr.topLeft())

        if self.ui_songs_list.count() > 0:
            self.ui_songs_bar_label.hide()
        else:
            self.ui_songs_bar_label.show()

        if self.ui_playlist_tree.topLevelItem(0):
            self.ui_playlist_panel_label.hide()
        else:
            self.ui_playlist_panel_label.show()

    def updateOutputMenu(self):

        current = self.display.getMode()
        flag = True

        self.ui_menu_output.clear()

        self.ui_showTestCardAction.setChecked(self.display.isTestCard())
        self.ui_outputDisabledAction.setChecked(self.display.isEnabled())

        self.ui_menu_output.addAction(self.ui_outputDisabledAction)
        self.ui_menu_output.addSeparator()

        def triggered(action):

            def fn(item=action):
                a = self.updateOutputMenu()
                b = self.display.setMode(action.property("mode"))
                c = self.ui_outputDisabledAction.setChecked(False)

                return a or b or c

            return fn

        for mode in self.display.getGeometryModes():

            if mode.disabled:
                continue

            if mode.name.find('Windowed') >= 0 and flag:
                self.ui_menu_output.addSeparator()
                flag = False

            action = QAction(mode.name, self)
            action.setProperty("mode", QVariant(mode))
            action.triggered.connect(triggered(action))

            self.ui_menu_output.addAction(action)

        self.ui_menu_output.addSeparator()
        self.ui_menu_output.addAction(self.ui_showTestCardAction)
        self.ui_menu_output.addAction(self.ui_outputPreferencesAction)

    def updateSearch(self, items=None):

        self.ui_songs_list.clear()

        if not items:
            items = History.getLast(35)

            for item in items:
                listitem = SearchListItem()
                listitem.setType(SearchListItem.TYPE_HISTORY)
                listitem.setText(item['title'])
                listitem.setMessage(item['message'])
                listitem.setItemData(item)

                self.ui_songs_list.addItem(listitem)
        else:
            for item in items:
                self.ui_songs_list.addItem(item)

        self.updateLabels()

    def updatePlaylist(self):

        self.ui_playlist_tree.clear()

        if self.playlist:
            songs = Playlist.getSongs(self.playlist['id'])

            self.ui_playlist_label.setText("%s (%d songs)" % (self.playlist['title'], len(songs)))

            for song in songs:
                songItem = SongTreeWidgetItem(self.ui_playlist_tree)
                songItem.setSong(song)

                for page in Song.getPages(song['id']):
                    pageItem = PageTreeWidgetItem()
                    pageItem.setPage(page)
                    pageItem.setSong(song)

                    songItem.addChild(pageItem)

                self.ui_playlist_tree.addTopLevelItem(songItem)

        self.updateLabels()

    # Actions

    def importPlaylistAction(self):

        path, ext = QFileDialog.getOpenFileName(self, "Open File...", "", "*.grail1")

        if not os.path.isfile(path):
            return

        connection = lite.connect(path)
        connection.row_factory = lite.Row

        cursor = connection.cursor()

        # create new playlist

        cursor.execute("SELECT * FROM playlists WHERE id = 1")
        pid = Playlist.add(cursor.fetchone()['title'])

        # add songs to playlist
        cursor.execute(
            """
            SELECT
                playlist.id AS pid,
                songs.id,
                songs.title,
                songs.artist,
                songs.album,
                songs.year,
                playlist.collapsed
            FROM songs, playlist
            WHERE
                playlist.playlist = 1
                AND songs.id = playlist.song
                ORDER BY playlist.sort
            """)
        songs = cursor.fetchall()

        for song in songs:

            available = False
            for search_item in Song.search(song['title']):
                if (search_item['title'] == song['title'] and search_item['artist'] == song['artist']
                    and search_item['album'] == song['album'] and search_item['year'] == song['year']):
                    available = True
                    sid = search_item['id']

            if not available:
                sid = Song.add(song['title'], song['artist'], song['album'], song['year'])

                cursor.execute("SELECT * FROM pages WHERE song = ? ORDER BY sort ASC", (song['id'],))
                for page in cursor.fetchall():
                    Song.addPage(sid, page['page'])

            Playlist.addSong(pid, sid)
            Playlist.collapseSong(pid, sid, song['collapsed'])

        self.playlist = Playlist.get(pid)
        self.updateSearch()
        self.updatePlaylist()

        connection.close()

    def exportPlaylistAction(self):

        if not self.playlist:
            return

        def rchop(thestring, ending):
            if thestring.endswith(ending):
                return thestring[:-len(ending)]
            return thestring

        path, ext = QFileDialog.getSaveFileName(self, "Save file", self.playlist['title'], "*.grail1")
        filepath = rchop(path, '.grail1') + '.grail1'

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

        cursor.execute("INSERT INTO playlists VALUES(?, ?)", (1, self.playlist['title']))

        songs = Playlist.getSongs(self.playlist['id'])
        songids = []
        playlistsort = 0

        for song in songs:

            if not song['id'] in songids:
                record = (song['id'], song['title'], song['artist'], song['album'], song['year'])
                cursor.execute("INSERT INTO songs VALUES(?, ?, ?, ?, ?)", record)

                songids.append(song['id'])

                sort = 0
                for page in Song.getPages(song['id']):
                    cursor.execute("INSERT INTO pages VALUES(NULL, ?, ?, ?)", (song['id'], sort, page['page']))
                    sort = sort + 1

            cursor.execute("INSERT INTO playlist VALUES(NULL, ?, ?, ?, ?)",
                           (1, playlistsort, song['id'], song['collapsed']))
            playlistsort = playlistsort + 1

        connection.commit()
        connection.close()

    def clearHistoryAction(self):

        History.clear()

    def displayShowTestCardAction(self):

        self.display.setTestCard(self.ui_showTestCardAction.isChecked())

    def displayOutputDisabledAction(self):

        self.display.setDisabled(True)
        self.ui_outputDisabledAction.setChecked(True)

    def displayOutputPreferencesAction(self):

        dialog = self.display.getPreferencesDialog()
        dialog.show()

    def addSongAction(self):

        self.dialog_song.addSong()
        self.dialog_song.showOnTop()

    def togglePreview(self):

        sizes = self.ui_spliter.sizes()

        if sizes[2] != 0:
            self.ui_spliter.size_preview = sizes[2]
            sizes[2] = 0

            self.ui_spliter.setCollapsible(2, True)
            self.ui_spliter.setSizes(sizes)
        else:
            sizes[2] = self.ui_spliter.size_preview

            self.ui_spliter.setCollapsible(2, False)
            self.ui_spliter.setSizes(sizes)

    def toggleLibrary(self):

        sizes = self.ui_spliter.sizes()

        if sizes[0] != 0:
            self.ui_spliter.size_library = sizes[0]
            sizes[0] = 0

            self.ui_spliter.setCollapsible(0, True)
            self.ui_spliter.setSizes(sizes)
        else:
            sizes[0] = self.ui_spliter.size_library

            self.ui_spliter.setCollapsible(0, False)
            self.ui_spliter.setSizes(sizes)

    def newDisplayAction(self):

        prefs = DisplayPreferences()
        prefs.disabled = False

        display = DisplayDialog(None, prefs)

        def updateDisplay():
            mode = display.getMode()

            if mode.disabled:
                display.setAttribute(Qt.WA_DeleteOnClose, True)
                display.close(True)
                self.displays.remove(display)

        display.modeChanged.connect(updateDisplay)
        display.show()

        self.displays.append(display)

    def aboutAction(self):

        self.dialog_about.show()
        self.dialog_about.raise_()
        self.dialog_about.setWindowState(self.dialog_about.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.dialog_about.activateWindow()

    def preferencesAction(self):

        self.dialog_preferences.show()
        self.dialog_preferences.raise_()
        self.dialog_preferences.setWindowState(self.dialog_about.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.dialog_preferences.activateWindow()

    def searchAction(self, text):

        keyword = str(self.ui_songs_search.text())

        if keyword:
            items = []
            songs = Song.search(keyword)
            references = Bible.match_reference(keyword)

            for item in references:
                listitem = SearchListItem()
                listitem.setType(SearchListItem.TYPE_REFERENCE)
                listitem.setText(item[0])
                listitem.setItemData(item)
                items.append(listitem)

            for item in songs:
                listitem = SearchListItem()
                listitem.setSong(item)
                items.append(listitem)

            if len(references) > 0:
                try:
                    text = Bible.get(references[0][1][0], references[0][1][1], references[0][1][2])

                    text = re.sub(r'[\[\_\]]', '', text)
                    text = re.sub(r'\_', '', text)
                    text = re.sub(r'\-\-', '-', text)

                    text_verse = text + "\n" + references[0][0]

                    self.ui_preview_label.setText(text_verse)
                    self.ui_preview_edit.setPlainText(text_verse)
                except:
                    pass

            self.updateSearch(items)
        else:
            self.updateSearch()

    def showAction(self):
        """
        Show selected song page or first page of first song in selected playlist
        """

        items = self.ui_playlist_tree.selectedItems()

        if len(items) > 0:
            item = items[0]

            text = ''

            if type(item) == SongTreeWidgetItem:
                pages = Song.getPages(item.id)

                if len(pages) > 0:
                    text = pages[0]['page']

            elif type(item) == PageTreeWidgetItem:
                text = item.page

            self.ui_preview_label.setText(text)

            item = HistoryItem(HistoryItem.TYPE_SONG, text.split('\n')[0], text)

            self.send(item)

    def showQuickAction(self):

        text = str(self.ui_preview_edit.toPlainText())

        if text.split('\n')[-1].find(':') > -1:
            item = HistoryItem(HistoryItem.TYPE_BIBLE, text.split('\n')[-1], text)
        else:
            item = HistoryItem(HistoryItem.TYPE_SONG, text.split('\n')[0], text)

        self.send(item)

    def quickEditChanged(self):

        if self.ui_preview_liveAction.isChecked():
            text = str(self.ui_preview_edit.toPlainText())
            item = HistoryItem(HistoryItem.TYPE_QUICK, text, text)

            self.send(item)

    def saveAction(self):
        items = self.ui_playlist_tree.selectedItems()

        if len(items) > 0:
            item = items[0]
            song = -1
            page = -1

            if type(item) == SongTreeWidgetItem:
                pages = Song.getPages(item.id)

                if len(pages) > 0:
                    song = item.id
                    page = pages[0]['id']

            elif type(item) == PageTreeWidgetItem:
                song = item.song
                page = item.id

            if song > -1 and page > -1:
                text = str(self.ui_preview_edit.toPlainText()).strip()
                Song.updatePage(song, page, text)
                self.updatePlaylist()

    def blackoutAction(self):
        self.blackoutTextAction()
        self.blackoutMediaAction()

    def blackoutTextAction(self):

        text = " "
        item = HistoryItem(HistoryItem.TYPE_BLACKOUT, text, text)
        self.send(item)

    def blackoutMediaAction(self):

        self.imageSelected(None)

    def songClicked(self, item):

        if not item:
            return

        if item.type == SearchListItem.TYPE_SONG:
            text = '\n\n'.join(page['page'] for page in Song.getPages(item.data["id"]))

            self.ui_preview_label.setText(text)

        if item.type == SearchListItem.TYPE_HISTORY:
            text = item.data["message"]

            self.ui_preview_label.setText(text)

        if item.type == SearchListItem.TYPE_REFERENCE:
            data = item.getData()

            try:
                text = Bible.get(data[1][0], data[1][1], data[1][2])

                text = re.sub(r'[\[\_\]]', '', text)
                text = re.sub(r'\_', '', text)
                text = re.sub(r'\-\-', '-', text)

                text_verse = text + "\n" + data[0]

                self.ui_preview_label.setText(text_verse)
                self.ui_preview_edit.setPlainText(text_verse)
            except:
                pass

    def songDoubleClicked(self, item):

        if item.type == SearchListItem.TYPE_SONG:
            id = item.data["id"]

            Playlist.addSong(self.playlist['id'], id)
            self.updatePlaylist()

        if item.type == SearchListItem.TYPE_REFERENCE:
            data = item.getData()

            try:
                text = Bible.get(data[1][0], data[1][1], data[1][2])

                text = re.sub(r'[\[\_\]]', '', text)
                text = re.sub(r'\_', '', text)
                text = re.sub(r'\-\-', '-', text)

                text_verse = text + "\n" + data[0]

                self.ui_preview_label.setText(text_verse)
                self.ui_preview_edit.setPlainText(text_verse)

                hitem = HistoryItem(HistoryItem.TYPE_BIBLE, data[0], text_verse)

                self.send(hitem)
            except:
                pass

        if item.type == SearchListItem.TYPE_HISTORY:
            data = item.getData()

            hitem = HistoryItem(HistoryItem.TYPE_QUICK, data["title"], data["message"])
            self.send(hitem)

    def songKeyEvent(self, event):

        if event.key() == Qt.Key_Return:
            self.songAddToPlaylist()
        else:
            QListWidget.keyPressEvent(self.ui_songs_list, event)

    def songAddToPlaylist(self):

        items = self.ui_songs_list.selectedItems()

        if len(items) > 0:
            self.songDoubleClicked(items[0])

    def songContextMenu(self, pos):

        item = self.ui_songs_list.itemAt(pos)

        if item is not None:
            if item.type == SearchListItem.TYPE_SONG:
                menu = QMenu("Context Menu", self)

                editAction = QAction('Edit song', menu)
                editAction.triggered.connect(self.updateSongAction)

                deleteAction = QAction('Delete song', menu)
                deleteAction.triggered.connect(self.deleteSongAction)

                addAction = QAction('Add to playlist', menu)
                addAction.triggered.connect(self.songAddToPlaylist)

                menu.addAction(editAction)
                menu.addAction(deleteAction)
                menu.addAction(addAction)

                menu.exec_(self.ui_songs_list.mapToGlobal(pos))

    def deleteSongAction(self):

        items = self.ui_songs_list.selectedItems()

        if len(items) > 0:
            item = items[0]

            if item.type == SearchListItem.TYPE_SONG:
                Song.delete(item.data["id"])

                self.updateSearch()

    def updateSongAction(self):
        items = self.ui_songs_list.selectedItems()

        if len(items) > 0:
            item = items[0]

            if item.type == SearchListItem.TYPE_SONG:
                self.dialog_song.setSong(item.getData())

                self.dialog_song.showOnTop()

                self.updateSearch()
                self.updatePlaylist()

    def pageClicked(self, item):

        text = ''

        if type(item) == SongTreeWidgetItem:
            pages = Song.getPages(item.id)

            if len(pages) > 0:
                text = pages[0]['page']

        elif type(item) == PageTreeWidgetItem:
            text = item.page

        self.ui_preview_label.setText(text)
        self.ui_preview_edit.setPlainText(text)

    def pageDoubleClicked(self, item):

        text = ''

        if type(item) == SongTreeWidgetItem:
            pages = Song.getPages(item.id)

            if len(pages) > 0:
                text = pages[0]['page']

        elif type(item) == PageTreeWidgetItem:
            text = item.page

        self.ui_preview_label.setText(text)
        self.ui_preview_edit.setPlainText(text)

        item = HistoryItem(HistoryItem.TYPE_SONG, text.split('\n')[0], text)

        self.send(item)

    def playlistContextMenu(self, pos):
        item = self.ui_playlist_tree.itemAt(pos)

        if item is not None:
            menu = QMenu("Context Menu", self)

            deleteAction = QAction('Delete from playlist', menu)
            deleteAction.triggered.connect(self.deletePlaylistSongAction)

            editAction = QAction('Edit', menu)
            editAction.triggered.connect(self.editPlaylistSongAction)

            menu.addAction(editAction)
            menu.addSeparator()
            menu.addAction(deleteAction)

            ret = menu.exec_(self.ui_playlist_tree.mapToGlobal(pos))

    def playlistReordered(self):

        for index in range(self.ui_playlist_tree.topLevelItemCount()):
            item = self.ui_playlist_tree.topLevelItem(index)
            Playlist.sortSongs(int(self.playlist['id']), item.pid, index)

    def playlistItemCollapsed(self, item):

        if item.song is not None:
            Playlist.collapseSong(self.playlist["id"], item.pid, item.isExpanded())

    def deletePlaylistSongAction(self):

        item = self.ui_playlist_tree.currentItem()

        if type(item) == SongTreeWidgetItem:
            id = item.id
            pid = item.pid
            index = self.ui_playlist_tree.indexOfTopLevelItem(item)
            self.ui_playlist_tree.takeTopLevelItem(index)

        if type(item) == PageTreeWidgetItem:
            id = item.song
            pid = item.pid
            index = self.ui_playlist_tree.indexOfTopLevelItem(item.parent())
            self.ui_playlist_tree.takeTopLevelItem(index)

        Playlist.deleteSong(self.playlist['id'], id, pid)
        self.updatePlaylist()

    def editPlaylistSongAction(self):

        item = self.ui_playlist_tree.currentItem()

        if type(item) == SongTreeWidgetItem:
            id = item.id

        if type(item) == PageTreeWidgetItem:
            id = item.song

        self.dialog_song.setSong(Song.get(id))
        self.dialog_song.showOnTop()

    def playlistLabelClicked(self, event):

        self.dialog_playlist.showAt(self.ui_playlist_label.mapToGlobal(self.ui_playlist_label.rect().center()))

    def playlistSelectedAction(self, id):

        self.playlist = Playlist.get(id)
        self.updatePlaylist()

        Settings.set('playlist', id)

        self.updateLabels()

    def previousPageAction(self):

        item = self.ui_playlist_tree.itemAbove(self.ui_playlist_tree.currentItem())

        if not item:
            item = self.ui_playlist_tree.itemAt(0, 0)

        if item:
            self.ui_playlist_tree.setCurrentItem(item)
            self.showAction()

    def nextPageAction(self):

        item = self.ui_playlist_tree.itemBelow(self.ui_playlist_tree.currentItem())

        if not item and not self.ui_playlist_tree.currentItem():
            item = self.ui_playlist_tree.itemAt(0, 0)

        if item:
            self.ui_playlist_tree.setCurrentItem(item)
            self.showAction()

    def playlistKeyEvent(self, event):
        item = self.ui_playlist_tree.currentItem()

        if event.key() == Qt.Key_Return and item:
            self.pageDoubleClicked(item)
        elif event.key() == Qt.Key_Delete and item:
            self.deletePlaylistSongAction()
        elif event.key() == Qt.Key_Up and item:
            QTreeWidget.keyPressEvent(self.ui_playlist_tree, event)
            self.pageClicked(self.ui_playlist_tree.currentItem())
        elif event.key() == Qt.Key_Down and item:
            QTreeWidget.keyPressEvent(self.ui_playlist_tree, event)
            self.pageClicked(self.ui_playlist_tree.currentItem())
        else:
            QTreeWidget.keyPressEvent(self.ui_playlist_tree, event)

    def searchKeyEvent(self, event):

        if event.key() == Qt.Key_Return:
            self.showQuickAction()
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self.blackoutAction()
        elif event.key() == Qt.Key_Up:
            keyword = str(self.ui_songs_search.text())

            def up(match):
                return str(int(match.group(0)) + 1)

            keyword = re.sub(r'([0-9]+)$', up, keyword)

            self.ui_songs_search.setText(keyword)
            self.searchAction("")
        elif event.key() == Qt.Key_Down:
            keyword = str(self.ui_songs_search.text())

            def down(match):
                return str(max(int(match.group(0)) - 1, 1))

            keyword = re.sub(r'([0-9]+)$', down, keyword)

            self.ui_songs_search.setText(keyword)
            self.searchAction("")
        elif event.key() == Qt.Key_Escape:
            self.ui_songs_search.setText("")
        else:
            QLineEdit.keyPressEvent(self.ui_songs_search, event)

    def historyItemSelected(self, item):

        self.send(item)

    def imageSelected(self, path):

        self.display.setImage(path)

        for display in self.displays:
            display.setImage(path)

    def setBlackoutImage(self, path):

        self.display.setBlackoutImage(path)

        for display in self.displays:
            display.setBlackoutImage(path)

    def setTextImage(self, path):

        self.display.setTextImage(path)

        for display in self.displays:
            display.setTextImage(path)
