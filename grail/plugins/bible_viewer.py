# -*- coding: UTF-8 -*-
"""
    grail.plugins.bible_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    View and search bible

    :copyright: (c) 2018 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import re

from grailkit.bible import BibleHost, Verse, Book
from grailkit.dna import DNA

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
    author = 'Grail Team'
    description = 'View and search bible'

    def __init__(self, *args):
        super().__init__(*args)

        self.book = self.get('book', default=1)
        self.chapter = self.get('chapter', default=1)

        self.__ui__()

    def __ui__(self):

        self.setObjectName("BibleViewer")

        self._ui_layout = VLayout()

        self._ui_bar = Toolbar()

        self._ui_book = QComboBox()
        self._ui_book.currentIndexChanged.connect(self._book_changed)

        self._ui_chapter = QComboBox()
        self._ui_chapter.currentIndexChanged.connect(self._chapter_changed)

        self._ui_bar.addWidget(self._ui_book)
        self._ui_bar.addWidget(self._ui_chapter)
        self._ui_bar.addStretch()

        self._ui_list = List()
        self._ui_list.setWordWrap(True)
        self._ui_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_list.currentItemChanged.connect(self._item_clicked)
        self._ui_list.itemDoubleClicked.connect(self._item_doubleclicked)
        self._ui_list.customContextMenuRequested.connect(self._context_menu)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon(':/rc/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addStretch()

        self._ui_layout.addWidget(self._ui_bar)
        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

        self.update_list(self.book, self.chapter)
        self.update_bar()

    def update_bar(self):
        """Update book and chapter drop downs"""

        self._ui_book.clear()
        self._ui_chapter.clear()

        for book in self.bible.books():
            self._ui_book.addItem(book.name, book.id)

        for chapter in range(1, self.bible.count_chapters(book=self.book) + 1):
            self._ui_chapter.addItem(str(chapter), chapter)

    def update_list(self, book, chapter):
        """Update list"""

        self.set('book', book)
        self.set('chapter', chapter)

        self._ui_list.clear()

        for verse in self.bible.chapter(book, chapter):
            item = ListItem()
            item.setText("%d. %s" % (verse.verse, verse.text))
            item.setObject(verse)

            self._ui_list.addItem(item)

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def add_item_action(self, entity):
        """Add item to cuelist"""

        # xxx: cue will be added to all opened cuelists
        self.emit('/cuelist/add', entity)

    def _item_clicked(self, item):
        """List item clicked"""

        if not item:
            return

        self.emit('!cue/preview', item.object())

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
        menu = QMenu("Context Menu", self)

        def trigger(m, a):
            return lambda i: m(a)

        add_action = QAction('Add to Cuelist', menu)
        add_action.triggered.connect(trigger(self.add_item_action, entity))

        menu.addAction(add_action)

        menu.exec_(self._ui_list.mapToGlobal(pos))

    def _book_changed(self, index):

        book_id = self._ui_book.itemData(index)

        self.update_list(book_id, 1)
        self._ui_chapter.clear()

        for chapter in range(1, self.bible.count_chapters(book=book_id) + 1):
            self._ui_chapter.addItem(str(chapter), chapter)

    def _chapter_changed(self, index):

        chapter_id = self._ui_book.itemData(index)

        self.update_list(self.book, chapter_id)
