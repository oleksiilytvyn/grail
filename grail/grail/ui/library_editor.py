# -*- coding: UTF-8 -*-
"""
    grail.ui.library_editor
    ~~~~~~~~~~~~~~~~~~~~~~~

    Simple library editor
"""

import re

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.bible import Verse
from grailkit.dna import DNA, SongEntity
from grailkit.ui import GSearchEdit, GListWidget, GListItem, GSpacer
from grailkit.ui.gapplication import AppInstance

from grail.ui import SongDialog, Panel


class LibraryEditor(Panel):
    """Simple library browser"""

    def __init__(self, app):
        super(LibraryEditor, self).__init__()

        self.app = app
        self.song_dialog = SongDialog()

        self.connect('/app/close', self._close)

        self.__ui__()

    def __ui__(self):

        self.setObjectName("library")

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setObjectName("library_layout")
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_search = GSearchEdit()
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

        self._ui_list = GListWidget()
        self._ui_list.setObjectName("library_list")
        self._ui_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_list.currentItemChanged.connect(self._item_clicked)
        self._ui_list.itemDoubleClicked.connect(self._item_doubleclicked)
        self._ui_list.customContextMenuRequested.connect(self._context_menu)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("library_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_add_action)
        self._ui_toolbar.addWidget(GSpacer())

        self._ui_layout.addWidget(self._ui_search_widget)
        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

        # simulate search event
        self._search_event("")

    def _search_event(self, keyword):
        """Triggered when user types something in search field"""

        self._ui_list.clear()

        if not keyword:

            # show songs from library
            for song in AppInstance().library.items(filter_type=DNA.TYPE_SONG):
                item = GListItem()
                item.setText("[S] %s" % (song.name,))
                item.setObject(song)

                self._ui_list.addItem(item)

            return

        # show bible references (limit to 3)
        for verse in AppInstance().bible.match_reference(keyword):
            item = GListItem()
            item.setText("[V] %s" % (verse.reference,))
            item.setObject(verse)

            self._ui_list.addItem(item)

        # show songs from library (limit to 9)
        for song in AppInstance().library.items(filter_keyword=keyword, filter_type=DNA.TYPE_SONG,
                                                sort="name", reverse=True, limit=9):
            item = GListItem()
            item.setText("[S] %s" % (song.name,))
            item.setObject(song)

            self._ui_list.addItem(item)

        # To-do: show media items from library (limit to 6)

    def _search_key_event(self, event):
        """Process key evens before search action begins"""

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
        """Context menu action"""

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

        # to-do add item to cuelist
        pass

    def add_action(self):
        """Add action"""

        self.song_dialog.show()

    def add_item_action(self, item):

        pass

    def delete_item_action(self, item):
        """Delete item from library"""

        AppInstance().library.remove(item.id)

    def edit_item_action(self, item):
        """Edit library item"""

        self.song_dialog.set_entity(item)
        self.song_dialog.show()

    def _close(self):

        self.song_dialog.close()
