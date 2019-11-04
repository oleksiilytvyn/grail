# -*- coding: UTF-8 -*-
"""
    grail.plugins.library_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Manage built-in library

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
import re

from grailkit.bible import Verse
from grailkit.dna import DNA, SongEntity

from grail.qt import *
from grail.core import Viewer


class SongDialog(QtWidgets.QDialog):
    """Song edit dialog"""

    MODE_CREATE = 0
    MODE_UPDATE = 1

    changed = QtSignal()

    def __init__(self, parent=None, song=None):
        super(SongDialog, self).__init__(parent)

        self._mode = SongDialog.MODE_CREATE
        self._entity = song

        self.__ui__()

    def __ui__(self):
        """Create UI of this dialog"""

        # header
        self._ui_head_title = QtWidgets.QLabel("Song title")
        self._ui_head_title.setObjectName("SongDialog_head_title")

        self._ui_head_subtitle = QtWidgets.QLabel("Artist - Album - year")
        self._ui_head_subtitle.setObjectName("SongDialog_head_subtitle")

        self._ui_head_layout = QtWidgets.QVBoxLayout()
        self._ui_head_layout.setSpacing(2)
        self._ui_head_layout.setContentsMargins(8, 4, 8, 8)
        self._ui_head_layout.addWidget(self._ui_head_title)
        self._ui_head_layout.addWidget(self._ui_head_subtitle)

        self._ui_head = QtWidgets.QWidget()
        self._ui_head.setObjectName("SongDialog_head")
        self._ui_head.setLayout(self._ui_head_layout)

        # body
        self._ui_title = QtWidgets.QLineEdit()
        self._ui_title.textChanged.connect(self._text_changed)
        self._ui_title.setPlaceholderText("Song title")

        self._ui_artist = QtWidgets.QLineEdit()
        self._ui_artist.textChanged.connect(self._text_changed)
        self._ui_artist.setPlaceholderText("Artist name")

        self._ui_album = QtWidgets.QLineEdit()
        self._ui_album.textChanged.connect(self._text_changed)
        self._ui_album.setPlaceholderText("Album")

        self._ui_year = QtWidgets.QLineEdit()
        self._ui_year.textChanged.connect(self._text_changed)
        self._ui_year.setPlaceholderText("Year")

        self._ui_genre = QtWidgets.QLineEdit()
        self._ui_genre.setPlaceholderText("Genre")

        self._ui_track = QtWidgets.QLineEdit()
        self._ui_track.setPlaceholderText("Track")

        self._ui_language = QtWidgets.QLineEdit()
        self._ui_language.setPlaceholderText("Language")

        self._ui_lyrics = QtWidgets.QTextEdit()
        self._ui_lyrics.setPlaceholderText("Lyrics")
        self._ui_lyrics.setAcceptRichText(False)

        policy = self._ui_lyrics.sizePolicy()
        policy.setVerticalStretch(1)

        self._ui_lyrics.setSizePolicy(policy)

        self._ui_button_ok = QtWidgets.QPushButton("Ok")
        self._ui_button_ok.clicked.connect(self.accept_action)

        self._ui_button_cancel = QtWidgets.QPushButton("Cancel")
        self._ui_button_cancel.clicked.connect(self.reject_action)

        self._ui_buttons_layout = QtWidgets.QHBoxLayout()
        self._ui_buttons_layout.setSpacing(10)
        self._ui_buttons_layout.setContentsMargins(14, 0, 14, 14)
        self._ui_buttons_layout.addStretch()
        self._ui_buttons_layout.addWidget(self._ui_button_cancel)
        self._ui_buttons_layout.addWidget(self._ui_button_ok)

        self._ui_buttons = QtWidgets.QWidget()
        self._ui_buttons.setLayout(self._ui_buttons_layout)

        self._ui_body_layout = QtWidgets.QGridLayout()
        self._ui_body_layout.setSpacing(8)
        self._ui_body_layout.setContentsMargins(12, 12, 12, 10)

        self._ui_body_layout.addWidget(self._ui_title, 0, 0, 1, 3)
        self._ui_body_layout.addWidget(self._ui_album, 1, 0, 1, 3)
        self._ui_body_layout.addWidget(self._ui_artist, 2, 0, 1, 2)
        self._ui_body_layout.addWidget(self._ui_year, 2, 2)
        self._ui_body_layout.addWidget(self._ui_genre, 3, 0)
        self._ui_body_layout.addWidget(self._ui_language, 3, 1)
        self._ui_body_layout.addWidget(self._ui_track, 3, 2)
        self._ui_body_layout.addWidget(self._ui_lyrics, 4, 0, 1, 3)

        self._ui_body = QtWidgets.QWidget()
        self._ui_body.setLayout(self._ui_body_layout)

        # main layout
        self._ui_layout = QtWidgets.QVBoxLayout()
        self._ui_layout.addWidget(self._ui_head)
        self._ui_layout.addWidget(self._ui_body)
        self._ui_layout.addWidget(self._ui_buttons)

        self.setLayout(self._ui_layout)

        self.setWindowTitle('Add song')
        self.setGeometry(300, 300, 300, 400)
        self.setMinimumSize(300, 400)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

    def closeEvent(self, event):
        """Reject on close"""
        super(SongDialog, self).closeEvent(event)

        self.reject_action()

    def reject_action(self):
        """Close window"""

        self.changed.emit()
        self.reject()

    def accept_action(self):
        """Save or create a song"""

        title = str(self._ui_title.text())
        album = str(self._ui_album.text())
        artist = str(self._ui_artist.text())
        lyrics = str(self._ui_lyrics.toPlainText()).strip()
        genre = str(self._ui_genre.text())
        language = str(self._ui_language.text())

        year = self.__parse_int(self._ui_year.text())
        track = self.__parse_int(self._ui_track.text())

        if self._mode == SongDialog.MODE_CREATE:
            entity = Application.instance().library.create(name=title, entity_type=DNA.TYPE_SONG)
        else:
            entity = self._entity

        entity.name = title
        entity.album = album
        entity.artist = artist
        entity.lyrics = lyrics
        entity.year = year
        entity.genre = genre
        entity.track = track
        entity.language = language
        entity.update()

        self.changed.emit()
        self.accept()

    def set_entity(self, entity):
        """Set entity to edit"""

        self._entity = entity

        self.setWindowTitle("Edit song" if entity else "Add song")

        if entity:
            self._ui_head_title.setText(entity.name)
            self._ui_head_subtitle.setText("%s - %s - %d" % (entity.artist, entity.album, entity.year))

            self._ui_title.setText(entity.name)
            self._ui_album.setText(entity.album)
            self._ui_artist.setText(entity.artist)
            self._ui_lyrics.setText(entity.lyrics)
            self._ui_year.setText(str(entity.year))
            self._ui_track.setText(str(entity.track))
            self._ui_language.setText(entity.language)
            self._ui_genre.setText(entity.genre)

            self._mode = SongDialog.MODE_UPDATE
        else:
            self._ui_head_title.setText("Untitled")
            self._ui_head_subtitle.setText("Unknown")

            self._ui_title.setText('')
            self._ui_album.setText('')
            self._ui_artist.setText('')
            self._ui_lyrics.setText('')
            self._ui_year.setText('')
            self._ui_track.setText('')
            self._ui_language.setText('')
            self._ui_genre.setText('')

            self._mode = SongDialog.MODE_CREATE

    def _text_changed(self, *args):
        """This method called when title, year, artist or album is changed
            So we can update window title and header bar"""

        self._ui_head_title.setText(self.__strip_default(self._ui_title.text(), "No Title"))
        self._ui_head_subtitle.setText("%s - %s - %s" %
                                       (self.__strip_default(self._ui_artist.text(), "Unknown"),
                                        self.__strip_default(self._ui_album.text(), "Unknown"),
                                        self.__strip_default(self._ui_year.text(), "-")))

    def __strip_default(self, value, default=""):

        title = str(value).lstrip().rstrip()

        if len(title) == 0:
            return default

        return value

    def __parse_int(self, value, default=0):

        try:
            return int(re.sub(r'[^0-9]', '', str(value)))
        except:
            return default


class LibraryViewer(Viewer):
    """Library viewer

    Connected:
        '/app/close'

    Emits:
        '/message/preview', message:str
        '/cuelist/add', entity:DNAEntity
    """

    id = 'library'
    name = 'Library'
    author = 'Alex Litvin'
    description = 'Manage grail library'

    def __init__(self, *args):
        super(LibraryViewer, self).__init__(*args)

        self.song_dialog = SongDialog()
        self.song_dialog.changed.connect(self._update)

        self.app.signals.connect('/app/close', self._close)

        self.library.entity_added.connect(self._update)
        self.library.entity_changed.connect(self._update)
        self.library.entity_removed.connect(self._update)

        self.__ui__()

    def __ui__(self):

        self.setObjectName("LibraryViewer")

        self._ui_layout = QtWidgets.QVBoxLayout()

        self._ui_search = QSearchEdit()
        self._ui_search.setObjectName("LibraryViewer_search")
        self._ui_search.setPlaceholderText("Search library...")
        self._ui_search.textChanged.connect(self._search_event)
        self._ui_search.keyPressed.connect(self._search_key_event)
        self._ui_search.focusOut.connect(self._search_focus_out)

        self._ui_search_layout = QtWidgets.QVBoxLayout()
        self._ui_search_layout.setContentsMargins(4, 4, 4, 4)
        self._ui_search_layout.addWidget(self._ui_search)

        self._ui_search_widget = QtWidgets.QWidget()
        self._ui_search_widget.setObjectName("LibraryViewer_search_widget")
        self._ui_search_widget.setLayout(self._ui_search_layout)

        self._ui_list = QtWidgets.QListWidget()
        self._ui_list.setWordWrap(True)
        self._ui_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._ui_list.currentItemChanged.connect(self._item_clicked)
        self._ui_list.itemDoubleClicked.connect(self._item_doubleclicked)
        self._ui_list.customContextMenuRequested.connect(self._context_menu)

        self._ui_add_action = QtWidgets.QAction(Icon(':/rc/add.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_view_action = QtWidgets.QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon(':/rc/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = QtWidgets.QToolBar()
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addStretch()
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

        icon_song = Icon.colored(':/rc/txt.png', QtGui.QColor('#ffffff'), QtGui.QColor('#e3e3e3'))
        icon_bible = Icon.colored(':/rc/book.png', QtGui.QColor('#03A9F4'), QtGui.QColor('#e3e3e3'))

        if not keyword:

            # show songs from library
            for song in self.library.items(filter_type=DNA.TYPE_SONG):
                item = QtWidgets.QListWidgetItem()
                item.setText("%s" % (song.name,))
                item.setObject(song)

                self._ui_list.addItem(item)

            return

        # show bible references (limit to 3)
        for verse in self.bible.match_reference(keyword):
            item = QtWidgets.QListWidgetItem()
            item.setIcon(icon_bible)
            item.setText("%s" % (verse.reference,))
            item.setObject(verse)

            self._ui_list.addItem(item)

        # Show bible full text search
        for verse in self.bible.match_text(keyword, limit=3):
            item = QtWidgets.QListWidgetItem()
            item.setIcon(icon_bible)
            item.setText(verse.text)
            item.setObject(verse)

            self._ui_list.addItem(item)

        # show songs from library (limit to 9)
        for song in self.library.items(filter_keyword=keyword, filter_type=DNA.TYPE_SONG,
                                       sort="name", reverse=True, limit=9):
            item = QtWidgets.QListWidgetItem()
            item.setIcon(icon_song)
            item.setText("%s" % (song.name,))
            item.setObject(song)

            self._ui_list.addItem(item)

        # xxx: show media items from library (limit to 6)

    def _search_key_event(self, event):
        """Process key evens before search menu_action begins"""

        event_key = event.key()

        if event_key == QtCore.Qt.Key_Return:
            item = self._ui_list.item(0)
            self.emit('!cue/execute', item.object())

        elif event_key == QtCore.Qt.Key_Z and event.modifiers() & QtCore.Qt.ControlModifier:
            # todo: self.blackoutAction()
            pass

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

    def _context_menu(self, pos):
        """Context menu menu_action"""

        item = self._ui_list.itemAt(pos)

        if not item:
            return

        entity = item.object()
        menu = QtWidgets.QMenu("Context Menu", self)

        def trigger(m, a):
            """Wrap action callback"""

            return lambda i: m(a)

        if isinstance(entity, Verse):
            pass
        else:
            if isinstance(entity, SongEntity):
                edit_action = QtWidgets.QAction('Song info', menu)
                edit_action.triggered.connect(trigger(self.edit_item_action, entity))
                menu.addAction(edit_action)

            delete_action = QtWidgets.QAction('Delete', menu)
            delete_action.triggered.connect(trigger(self.delete_item_action, entity))
            menu.addAction(delete_action)

        add_action = QtWidgets.QAction('Add to Cuelist', menu)
        add_action.triggered.connect(trigger(self.add_item_action, entity))
        menu.addAction(add_action)

        menu.exec_(self._ui_list.mapToGlobal(pos))

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

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def add_action(self):
        """Add menu_action"""

        self.song_dialog.set_entity(None)
        self.song_dialog.showWindow()

    def add_item_action(self, entity):
        """Add item to cuelist"""

        # xxx: cue will be added to all opened cuelists
        self.emit('/cuelist/add', entity)

    def delete_item_action(self, entity):
        """Delete item from library"""

        self.library.remove(entity.id)

    def edit_item_action(self, entity):
        """Edit library item"""

        self.song_dialog.set_entity(entity)
        self.song_dialog.showWindow()

    def _close(self):
        """Close this panel and child components"""

        self.song_dialog.close()
