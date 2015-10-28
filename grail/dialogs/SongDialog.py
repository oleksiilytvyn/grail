#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Grail - Lyrics software. Simple.
# Copyright (C) 2014-2015 Oleksii Lytvyn
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

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.utils import *
from grail.data import Song


class SongDialog(QDialog):
    """Song window"""

    MODE_UPDATE = 0
    MODE_ADD = 1

    updateComplete = pyqtSignal()

    def __init__(self, parent=None, song=None):

        super(SongDialog, self).__init__(parent)

        self.setObjectName( "song_dialog" )
        self.setStyleSheet( get_stylesheet() )

        self.updateComplete.connect( self.updateCompleteEvent )
        self.initUI()
        self.mode = SongDialog.MODE_ADD

    def initUI( self ):

        title = QLabel('Title')
        artist = QLabel('Artist')
        album = QLabel('Album')
        year = QLabel('Year')
        pages = QLabel('Lyrics')

        self.titleEdit = QLineEdit()
        self.titleEdit.setAttribute( Qt.WA_MacShowFocusRect, 0 )
        self.artistEdit = QLineEdit()
        self.artistEdit.setAttribute( Qt.WA_MacShowFocusRect, 0 )
        self.albumEdit = QLineEdit()
        self.albumEdit.setAttribute( Qt.WA_MacShowFocusRect, 0 )
        self.yearEdit = QLineEdit()
        self.yearEdit.setAttribute( Qt.WA_MacShowFocusRect, 0 )
        self.pagesEdit = QTextEdit()
        self.pagesEdit.setAttribute( Qt.WA_MacShowFocusRect, 0 )
        self.pagesEdit.setAcceptRichText( False )

        buttonBox = QDialogButtonBox()
        buttonBox.setContentsMargins(0, 0, 0, 0)
        buttonBox.setStandardButtons( QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
        buttonBox.accepted.connect( self.acceptAction )
        buttonBox.rejected.connect( self.rejectAction )

        grid = QGridLayout()
        grid.setSpacing( 6 )
        grid.setContentsMargins( 8, 8, 8, 8 )
        grid.setColumnMinimumWidth( 0, 200 )

        grid.addWidget(title, 0, 0, 1, 2)
        grid.addWidget(self.titleEdit, 1, 0, 1, 2)

        grid.addWidget(album, 2, 0, 1, 2)
        grid.addWidget(self.albumEdit, 3, 0, 1, 2)

        grid.addWidget(artist, 4, 0)
        grid.addWidget(self.artistEdit, 5, 0)

        grid.addWidget(year, 4, 1)
        grid.addWidget(self.yearEdit, 5, 1)

        grid.addWidget(pages, 6, 0, 1, 2)
        grid.addWidget(self.pagesEdit, 7, 0, 1, 2)

        grid.addWidget(buttonBox, 8, 0, 1, 2)

        self.setLayout(grid)

        if not PLATFORM_MAC:
            self.setWindowIcon( QIcon(':/icons/32.png') )

        self.setWindowTitle('Add song')
        self.setGeometry( 300, 300, 300, 400 )
        self.setMinimumSize( 300, 400 )
        self.setWindowFlags( Qt.WindowCloseButtonHint )

    def rejectAction( self ):

        self.reject()

    def acceptAction( self ):

        title = str(self.titleEdit.text())
        album = str(self.albumEdit.text())
        artist = str(self.artistEdit.text())
        pages = str(self.pagesEdit.toPlainText()).strip()

        try:
            year = int(self.yearEdit.text())
        except:
            year = 2000

        if self.mode == SongDialog.MODE_UPDATE:
            id = self.song['id']

            Song.update( id, title, artist, album, year )
            Song.deletePages( id )
        else:
            id = Song.add( title, artist, album, year )

        for page in pages.split("\n\n"):
            Song.addPage( id, page )

        self.updateComplete.emit( )
        self.accept()

    def setMode( self, mode ):

        self.mode = mode

    def setSong( self, song ):

        self.setMode( SongDialog.MODE_UPDATE )
        self.song = song

        self.setWindowTitle( 'Editing - ' + song['title'] )

        self.titleEdit.setText( song['title'] )
        self.artistEdit.setText( song['artist'] )
        self.albumEdit.setText( song['album'] )
        self.yearEdit.setText( str(song['year']) )

        pages = Song.getPages( song['id'] )

        self.pagesEdit.setText( "\n\n".join( page['page'] for page in pages ) )

    def addSong( self ):

        self.setMode( SongDialog.MODE_ADD )
        self.setWindowTitle( 'Add new' )

        self.titleEdit.setText( "" )
        self.artistEdit.setText( "" )
        self.albumEdit.setText( "" )
        self.yearEdit.setText( "" )
        self.pagesEdit.setText( "" )

    def showOnTop( self ):

        self.setGeometry( 300, 300, 300, 400 )
        self.center()
        self.setWindowState( self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
        self.raise_()
        self.show()

    def center( self ):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter( cp )
        self.move( qr.topLeft() )

    def updateCompleteEvent( self ):
        pass
