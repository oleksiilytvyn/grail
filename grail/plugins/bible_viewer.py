# -*- coding: UTF-8 -*-
"""
    grail.plugins.bible_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    View and search bible

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
import re

from grail.qt import *
from grail.core import Viewer


class BibleViewer(Viewer):
    """Library viewer

    Connected:
        '/app/close'

    Emits:
        '/message/preview', message:str
        '/cuelist/add', entity:DNAEntity
    """

    id = 'bible'
    name = 'Bible'
    author = 'Alex Litvin'
    description = 'View and search bible'

    def __init__(self, *args):
        super().__init__(*args)

        self.book = self.get('book', default=1)
        self.chapter = self.get('chapter', default=1)

        self.__ui__()

    def __ui__(self):

        self.setObjectName("BibleViewer")

        self._ui_layout = QtWidgets.QVBoxLayout()

        self._ui_search = QSearchEdit()
        self._ui_search.setObjectName("BibleViewer_search")
        self._ui_search.setPlaceholderText("Search bible...")
        self._ui_search.textChanged.connect(self._search_event)
        self._ui_search.keyPressed.connect(self._search_key_event)
        self._ui_search.focusOut.connect(self._search_focus_out)

        self._ui_search_layout = QtWidgets.QVBoxLayout()
        self._ui_search_layout.setContentsMargins(4, 4, 4, 4)
        self._ui_search_layout.addWidget(self._ui_search)

        self._ui_search_widget = QtWidgets.QWidget()
        self._ui_search_widget.setObjectName("BibleViewer_search_widget")
        self._ui_search_widget.setLayout(self._ui_search_layout)

        self._ui_list = QtWidgets.QListWidget()
        self._ui_list.setWordWrap(True)
        self._ui_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._ui_list.currentItemChanged.connect(self._item_clicked)
        self._ui_list.itemDoubleClicked.connect(self._item_doubleclicked)
        self._ui_list.customContextMenuRequested.connect(self._context_menu)

        self._ui_view_action = QtWidgets.QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon(':/rc/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_label = QtWidgets.QLabel("")
        self._ui_label.setObjectName("BibleViewer_label")
        self._ui_label.setAlignment(QtCore.Qt.AlignCenter)
        self._ui_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self._ui_toolbar = QtWidgets.QToolBar()
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(self._ui_label)

        self._ui_layout.addWidget(self._ui_search_widget)
        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

        self.update_list(self.book, self.chapter)

    def update_list(self, book, chapter):
        """Update list"""

        self.set('book', book)
        self.set('chapter', chapter)

        self._ui_list.clear()

        flag = True

        for verse in self.bible.chapter(book, chapter):
            if flag:
                self._ui_label.setText("%s %d" % (verse.book, chapter))
                flag = False

            item = QtWidgets.QListWidgetItem()
            item.setText("%d. %s" % (verse.verse, verse.text))
            item.setObject(verse)

            self._ui_list.addItem(item)

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def add_item_action(self, entity):
        """Add item to cuelist"""

        # xxx: cue will be added to all opened cuelists
        self.emit_signal('/cuelist/add', entity)

    def _item_clicked(self, item):
        """List item clicked"""

        if not item:
            return

        self.emit_signal('!cue/preview', item.object())

    def _item_doubleclicked(self, item):
        """List item double-clicked"""

        if not item:
            return

        self.add_item_action(item.object())

    def _context_menu(self, pos):
        """Context menu menu_action"""

        item = self._ui_list.itemAt(pos)

        if not item:
            return

        entity = item.object()
        menu = QtWidgets.QMenu("Context Menu", self)

        def trigger(m, a):
            return lambda i: m(a)

        add_action = QtWidgets.QAction('Add to Cuelist', menu)
        add_action.triggered.connect(trigger(self.add_item_action, entity))

        menu.addAction(add_action)

        menu.exec_(self._ui_list.mapToGlobal(pos))

    def _search_event(self, keyword):
        """Triggered when user types something in search field"""

        self._ui_list.clear()
        self._ui_label.setText("")

        icon_bible = Icon.colored(':/rc/book.png', QtGui.QColor('#03A9F4'), QtGui.QColor('#e3e3e3'))

        if not keyword:
            self.update_list(self.book, self.chapter)

            return

        # Show bible full text search
        for verse in self.bible.match_text(keyword, limit=10):
            striped_keyword = keyword.lstrip().rstrip().lower()
            striped_text = verse.text.lower()
            start_index = striped_text.index(striped_keyword)

            item = QtWidgets.QListWidgetItem()
            item.setIcon(icon_bible)
            item.setText("...%s" % verse.text[start_index:])
            item.setObject(verse)

            self._ui_list.addItem(item)

        # show bible chapter by reference
        ref = self.bible.match_reference(keyword, limit=1)

        if ref and len(ref) > 0:
            ref = ref[0]

            self._ui_label.setText("%s %d" % (ref.book, ref.chapter))

            for verse in self.bible.chapter(ref.book_id, ref.chapter):
                item = QtWidgets.QListWidgetItem()
                item.setText("%d. %s" % (verse.verse, verse.text))
                item.setObject(verse)

                self._ui_list.addItem(item)

    def _search_key_event(self, event):
        """Process key evens before search menu_action begins"""

        event_key = event.key()

        if event_key == QtCore.Qt.Key_Return:
            item = self._ui_list.item(0)

            if item:
                self.emit_signal('!cue/execute', item.object())

        elif event_key == QtCore.Qt.Key_Down or event_key == QtCore.Qt.Key_Up:
            # if we have number at the end increment or decrement when Up or Down keys pressed
            keyword = str(self._ui_search.text())

            def down(match):
                return str(max(int(match.group(0)) - 1, 1))

            def up(match):
                return str(int(match.group(0)) + 1)

            keyword = re.sub(r'([0-9]+)$', down if event_key == QtCore.Qt.Key_Down else up, keyword)

            self._ui_search.setText(keyword)

        elif event_key == QtCore.Qt.Key_Escape:
            # clear field on Escape key
            self._ui_search.setText("")

    def _search_focus_out(self, event):
        """Focus on first item in list after Tab pressed"""

        if event.reason() == QtCore.Qt.TabFocusReason and event.lostFocus():
            self._ui_list.setCurrentRow(0)
            self._ui_list.setFocus()
