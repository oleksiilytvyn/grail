# -*- coding: UTF-8 -*-
"""
    grail.ui.song_dialog
    ~~~~~~~~~~~~~~~~~~~~

    Song edit dialog

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.qt import Dialog, Application
from grailkit.dna import DNA


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
        self.ui_title_edit.setPlaceholderText("Song title")
        self.ui_title_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self.ui_artist_edit = QLineEdit()
        self.ui_artist_edit.setPlaceholderText("Artist name")
        self.ui_artist_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self.ui_album_edit = QLineEdit()
        self.ui_album_edit.setPlaceholderText("Album")
        self.ui_album_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self.ui_year_edit = QLineEdit()
        self.ui_year_edit.setPlaceholderText("Year")
        self.ui_year_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self.ui_lyrics_edit = QTextEdit()
        self.ui_lyrics_edit.setPlaceholderText("Lyrics")
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
