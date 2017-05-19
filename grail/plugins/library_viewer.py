# -*- coding: UTF-8 -*-
"""
    grail.plugins.library_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Manage built-in library

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import re

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.bible import Verse
from grailkit.dna import DNA, SongEntity
from grailkit.qt import SearchEdit, List, ListItem, Spacer, Dialog, Application

from grail.core import Viewer


class SongDialog(Dialog):
    """Song edit dialog"""

    MODE_CREATE = 0
    MODE_UPDATE = 1

    changed = pyqtSignal()

    def __init__(self, parent=None, song=None):
        super(SongDialog, self).__init__(parent)

        self._mode = SongDialog.MODE_CREATE
        self._entity = song

        self.__ui__()

    def __ui__(self):
        """Create UI of this dialog"""

        self.ui_title_label = QLabel('Title')
        self.ui_artist_label = QLabel('Artist')
        self.ui_album_label = QLabel('Album')
        self.ui_year_label = QLabel('Year')
        self.ui_lyrics_label = QLabel('Lyrics')

        self.ui_title_edit = QLineEdit()
        self.ui_title_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.ui_artist_edit = QLineEdit()
        self.ui_artist_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.ui_album_edit = QLineEdit()
        self.ui_album_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.ui_year_edit = QLineEdit()
        self.ui_year_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.ui_lyrics_edit = QTextEdit()
        self.ui_lyrics_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.ui_lyrics_edit.setAcceptRichText(False)

        self.ui_buttons = QDialogButtonBox()
        self.ui_buttons.setContentsMargins(0, 12, 0, 0)
        self.ui_buttons.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.ui_buttons.accepted.connect(self.accept_action)
        self.ui_buttons.rejected.connect(self.reject_action)

        self.ui_grid = QGridLayout()
        self.ui_grid.setSpacing(10)
        self.ui_grid.setContentsMargins(12, 12, 12, 12)
        self.ui_grid.setColumnMinimumWidth(0, 200)

        self.ui_grid.addWidget(self.ui_title_label, 0, 0, 1, 2)
        self.ui_grid.addWidget(self.ui_title_edit, 1, 0, 1, 2)

        self.ui_grid.addWidget(self.ui_album_label, 2, 0, 1, 2)
        self.ui_grid.addWidget(self.ui_album_edit, 3, 0, 1, 2)

        self.ui_grid.addWidget(self.ui_artist_label, 4, 0)
        self.ui_grid.addWidget(self.ui_artist_edit, 5, 0)

        self.ui_grid.addWidget(self.ui_year_label, 4, 1)
        self.ui_grid.addWidget(self.ui_year_edit, 5, 1)

        self.ui_grid.addWidget(self.ui_lyrics_label, 6, 0, 1, 2)
        self.ui_grid.addWidget(self.ui_lyrics_edit, 7, 0, 1, 2)

        self.ui_grid.addWidget(self.ui_buttons, 8, 0, 1, 2)

        self.setLayout(self.ui_grid)
        self.setWindowIcon(QIcon(':/icons/32.png'))
        self.setWindowTitle('Add song')
        self.setGeometry(300, 300, 300, 400)
        self.setMinimumSize(300, 400)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def reject_action(self):
        """Close window"""

        self.changed.emit()
        self.reject()

    def accept_action(self):
        """Save or create a song"""

        title = str(self.ui_title_edit.text())
        album = str(self.ui_album_edit.text())
        artist = str(self.ui_artist_edit.text())
        lyrics = str(self.ui_lyrics_edit.toPlainText()).strip()
        year = int(''.join(x for x in self.ui_year_edit.text() if x.isdigit()))

        if self._mode == SongDialog.MODE_CREATE:
            entity = Application.instance().library.create(name=title, entity_type=DNA.TYPE_SONG)
        else:
            entity = self._entity

        entity.name = title
        entity.album = album
        entity.artist = artist
        entity.lyrics = lyrics
        entity.year = year
        entity.update()

        self.changed.emit()
        self.accept()

    def set_entity(self, entity):

        self._entity = entity

        if entity:
            self.ui_title_edit.setText(entity.name)
            self.ui_album_edit.setText(entity.album)
            self.ui_artist_edit.setText(entity.artist)
            self.ui_lyrics_edit.setText(entity.lyrics)
            self.ui_year_edit.setText(str(entity.year))

            self._mode = SongDialog.MODE_UPDATE
        else:
            self.ui_title_edit.setText('Untitled')
            self.ui_album_edit.setText('')
            self.ui_artist_edit.setText('Unknown')
            self.ui_lyrics_edit.setText('')
            self.ui_year_edit.setText('2000')

            self._mode = SongDialog.MODE_CREATE


class LibraryViewer(Viewer):
    """Library viewer"""

    id = 'library'
    # Unique plugin name string
    name = 'Library'
    # Plugin author string
    author = 'Grail Team'
    # Plugin description string
    description = 'Manage grail library'

    def __init__(self, *args):
        super(LibraryViewer, self).__init__(*args)

        self.song_dialog = SongDialog()
        self.song_dialog.changed.connect(self._update)

        self.connect('/app/close', self._close)
        self.app.library.entity_changed.connect(self._update)
        self.app.library.entity_removed.connect(self._update)

        self.__ui__()

    def __ui__(self):

        self.setObjectName("library")

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setObjectName("library_layout")
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_search = SearchEdit()
        self._ui_search.setObjectName("library_search")
        self._ui_search.setPlaceholderText("Search library...")
        self._ui_search.textChanged.connect(self._search_event)
        self._ui_search.keyPressed.connect(self._search_key_event)
        self._ui_search.focusOut.connect(self._search_focus_out)

        self._ui_search_layout = QVBoxLayout()
        self._ui_search_layout.setSpacing(0)
        self._ui_search_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_search_layout.addWidget(self._ui_search)

        self._ui_search_widget = QWidget()
        self._ui_search_widget.setObjectName("library_search_widget")
        self._ui_search_widget.setLayout(self._ui_search_layout)

        self._ui_list = List()
        self._ui_list.setObjectName("library_list")
        self._ui_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_list.currentItemChanged.connect(self._item_clicked)
        self._ui_list.itemDoubleClicked.connect(self._item_doubleclicked)
        self._ui_list.customContextMenuRequested.connect(self._context_menu)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(QIcon(':/icons/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("library_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(Spacer())
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout.addWidget(self._ui_search_widget)
        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

        # simulate search event
        self._search_event("")

    def _update(self, entity_id=None):
        """Update panel"""

        self._search_event(str(self._ui_search.text()))

    def _search_event(self, keyword):
        """Triggered when user types something in search field"""

        self._ui_list.clear()

        if not keyword:

            # show songs from library
            for song in self.app.library.items(filter_type=DNA.TYPE_SONG):
                item = ListItem()
                item.setText("%s" % (song.name,))
                item.setObject(song)

                self._ui_list.addItem(item)

            return

        # show bible references (limit to 3)
        for verse in self.app.bible.match_reference(keyword):
            item = ListItem()
            item.setText("%s" % (verse.reference,))
            item.setObject(verse)

            self._ui_list.addItem(item)

        # show songs from library (limit to 9)
        for song in self.app.library.items(filter_keyword=keyword, filter_type=DNA.TYPE_SONG,
                                      sort="name", reverse=True, limit=9):
            item = ListItem()
            item.setText("%s" % (song.name,))
            item.setObject(song)

            self._ui_list.addItem(item)

        # todo: show media items from library (limit to 6)

    def _search_key_event(self, event):
        """Process key evens before search menu_action begins"""

        event_key = event.key()

        if event_key == Qt.Key_Return:
            # to-do: self.showQuickAction()
            pass

        elif event_key == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            # to-do: self.blackoutAction()
            pass

        elif event_key == Qt.Key_Down or event_key == Qt.Key_Up:
            # if we have number at the end increment or decrement when Up or Down keys pressed
            keyword = str(self._ui_search.text())

            def down(match):
                return str(max(int(match.group(0)) - 1, 1))

            def up(match):
                return str(int(match.group(0)) + 1)

            keyword = re.sub(r'([0-9]+)$', down if event_key == Qt.Key_Down else up, keyword)

            self._ui_search.setText(keyword)

        elif event_key == Qt.Key_Escape:
            # clear field on Escape key
            self._ui_search.setText("")

    def _search_focus_out(self, event):
        """Focus on first item in list after Tab pressed"""

        if event.reason() == Qt.TabFocusReason and event.lostFocus():
            self._ui_list.setCurrentRow(0)
            self._ui_list.setFocus()

    def _context_menu(self, pos):
        """Context menu menu_action"""

        item = self._ui_list.itemAt(pos)

        if not item:
            return

        entity = item.object()
        menu = QMenu("Context Menu", self)

        def trigger(m, a):
            return lambda i: m(a)

        if isinstance(entity, Verse):
            pass
        else:
            if isinstance(entity, SongEntity):
                edit_action = QAction('Edit', menu)
                edit_action.triggered.connect(trigger(self.edit_item_action, entity))
                menu.addAction(edit_action)

            delete_action = QAction('Delete', menu)
            delete_action.triggered.connect(trigger(self.delete_item_action, entity))
            menu.addAction(delete_action)

        add_action = QAction('Add to Cuelist', menu)
        add_action.triggered.connect(trigger(self.add_item_action, entity))
        menu.addAction(add_action)

        menu.exec_(self._ui_list.mapToGlobal(pos))

    def _item_clicked(self, item):
        """List item clicked"""

        if not item:
            return

        entity = item.object()

        if isinstance(entity, Verse):
            self.emit('/message/preview', "%s\n%s" % (entity.text, entity.reference))
        elif isinstance(entity, SongEntity):
            self.emit('/message/preview', entity.lyrics)

    def _item_doubleclicked(self, item):
        """List item double-clicked"""

        if not item:
            return

        self.add_item_action(item.object())

    def view_action(self):
        """Replace current view with something other"""

        menu = self.plugin_menu()
        menu.exec_(self._ui_toolbar.mapToGlobal(self._ui_view_action.pos()))

    def add_action(self):
        """Add menu_action"""

        self.song_dialog.set_entity(None)
        self.song_dialog.show()

    def add_item_action(self, entity):
        """Add item to cuelist"""

        self.emit('/cuelist/add', entity.id)

    def delete_item_action(self, entity):
        """Delete item from library"""

        self.app.library.remove(entity.id)

    def edit_item_action(self, entity):
        """Edit library item"""

        self.song_dialog.set_entity(entity)
        self.song_dialog.show()

    def _close(self):
        """Close this panel and child components"""

        self.song_dialog.close()
