# -*- coding: UTF-8 -*-
"""
    grail.ui.library_editor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Simple library editor
"""

import re

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.ui import GWidget, GSearchEdit, GListWidget, GListItem
from grailkit.ui.gapplication import AppInstance


class LibraryEditor(GWidget):
    """Simple library browser"""

    def __init__(self, app):
        super(LibraryEditor, self).__init__()

        self.app = app

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
        self._ui_list.itemClicked.connect(self._item_clicked)
        self._ui_list.currentItemChanged.connect(self._item_clicked)
        self._ui_list.itemDoubleClicked.connect(self._item_doubleclicked)
        self._ui_list.customContextMenuRequested.connect(self._context_menu)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("library_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_add_action)
        self._ui_toolbar.addWidget(spacer)

        self._ui_layout.addWidget(self._ui_search_widget)
        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def _search_event(self, keyword):
        """Triggered when user types something in search field"""

        self._ui_list.clear()

        if not keyword:
            return

        # show bible references (limit to 3)
        for verse in AppInstance().bible.match_reference(keyword):
            item = GListItem()
            item.setText(verse.reference)

            self._ui_list.addItem(item)

        # show songs from library (limit to 9)
        # show media items from library (limit to 6)

    def _search_key_event(self, event):
        """Process key evens before search action begins"""

        event_key = event.key()

        if event_key == Qt.Key_Return:
            # self.showQuickAction()
            pass
        elif event_key == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            # self.blackoutAction()
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
        elif event.key == Qt.Key_Escape:
            # clear field on Escape key
            self._ui_search.setText("")

    def _context_menu(self, event):
        """Context menu action"""

        pass

    def _item_clicked(self, item):
        """List item clicked"""

        pass

    def _item_doubleclicked(self, item):
        """List item double-clicked"""

        pass

    def add_action(self):
        """Add action"""

        pass
