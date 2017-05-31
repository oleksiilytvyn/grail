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

from grailkit.qt import Dialog, Application, HLayout, Button, Spacer
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

        self._ui_title = QLineEdit()
        self._ui_title.setPlaceholderText("Song title")
        self._ui_title.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self._ui_artist = QLineEdit()
        self._ui_artist.setPlaceholderText("Artist name")
        self._ui_artist.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self._ui_album = QLineEdit()
        self._ui_album.setPlaceholderText("Album")
        self._ui_album.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self._ui_year = QLineEdit()
        self._ui_year.setPlaceholderText("Year")
        self._ui_year.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self._ui_lyrics = QTextEdit()
        self._ui_lyrics.setPlaceholderText("Lyrics")
        self._ui_lyrics.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self._ui_lyrics.setAcceptRichText(False)

        policy = self._ui_lyrics.sizePolicy()
        policy.setVerticalStretch(1)

        self._ui_lyrics.setSizePolicy(policy)

        self._ui_button_ok = Button("Ok")
        self._ui_button_ok.clicked.connect(self.accept_action)

        self._ui_button_cancel = Button("Cancel")
        self._ui_button_cancel.clicked.connect(self.reject_action)

        self._ui_buttons = HLayout()
        self._ui_buttons.setSpacing(10)
        self._ui_buttons.setContentsMargins(0, 0, 0, 0)
        self._ui_buttons.addWidget(Spacer())
        self._ui_buttons.addWidget(self._ui_button_cancel)
        self._ui_buttons.addWidget(self._ui_button_ok)

        self._ui_layout = QGridLayout()
        self._ui_layout.setSpacing(8)
        self._ui_layout.setContentsMargins(12, 12, 12, 10)
        self._ui_layout.setColumnMinimumWidth(0, 200)

        self._ui_layout.addWidget(self._ui_title, 1, 0, 1, 2)
        self._ui_layout.addWidget(self._ui_album, 3, 0, 1, 2)
        self._ui_layout.addWidget(self._ui_artist, 5, 0)
        self._ui_layout.addWidget(self._ui_year, 5, 1)
        self._ui_layout.addWidget(self._ui_lyrics, 7, 0, 1, 2)
        self._ui_layout.addLayout(self._ui_buttons, 8, 0, 1, 2)

        self.setLayout(self._ui_layout)
        self.setWindowIcon(QIcon(':/icons/32.png'))
        self.setWindowTitle('Add song')
        self.setGeometry(300, 300, 300, 400)
        self.setMinimumSize(300, 400)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

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
        year = int(''.join(x for x in self._ui_year.text() if x.isdigit()))

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
        """Set entity to edit"""

        self._entity = entity

        self.setWindowTitle("Edit song" if entity else "Add song")

        if entity:
            self._ui_title.setText(entity.name)
            self._ui_album.setText(entity.album)
            self._ui_artist.setText(entity.artist)
            self._ui_lyrics.setText(entity.lyrics)
            self._ui_year.setText(str(entity.year))

            self._mode = SongDialog.MODE_UPDATE
        else:
            self._ui_title.setText('')
            self._ui_album.setText('')
            self._ui_artist.setText('')
            self._ui_lyrics.setText('')
            self._ui_year.setText('')

            self._mode = SongDialog.MODE_CREATE
