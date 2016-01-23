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
from grail.data import Playlist, Settings
from grail.widgets import *

from .BalloonDialog import BalloonDialog


class PlaylistDialog(BalloonDialog):

    selected = pyqtSignal(int)
    renamed = pyqtSignal(int)

    def __init__( self, parent=None ):
        super(PlaylistDialog, self).__init__( parent )

        self.selected.connect( self.selectedEvent )

        self.initUI()

    def initUI( self ):

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setSpacing( 0 )
        self.ui_layout.setContentsMargins( 0, 0, 0, 0 )

        self.ui_list = PlaylistTableWidget()
        self.ui_list.setObjectName("playlistList")
        self.ui_list.setColumnCount( 2 )
        self.ui_list.verticalHeader().setVisible( False )
        self.ui_list.horizontalHeader().setVisible( False )
        self.ui_list.setHorizontalHeaderLabels( ["Label", "Button"] )
        self.ui_list.setShowGrid( False )

        header = self.ui_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)

        self.ui_list.setColumnWidth( 1, 42 )
        self.ui_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui_list.cellChanged.connect( self.listCellChanged )
        self.ui_list.itemClicked.connect( self.listItemClicked )
        self.ui_list.itemClicked.connect( self.listItemClicked )
        self.ui_list.itemSelectionChanged.connect( self.listItemSelected )

        editAction = QAction( 'Edit', self )
        editAction.triggered.connect( self.editAction )

        addAction = QAction( 'Add', self )
        addAction.triggered.connect( self.addAction )

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ui_toolbar = QToolBar()
        self.ui_toolbar.setObjectName( "playlistDialogToolbar" )
        self.ui_toolbar.addAction( editAction )
        self.ui_toolbar.addWidget( spacer )
        self.ui_toolbar.addAction( addAction )

        self.ui_layout.addWidget( self.ui_list )
        self.ui_layout.addWidget( self.ui_toolbar )

        self.setLayout( self.ui_layout )

        self.setWindowTitle('Playlist')
        self.setGeometry( 100, 300, 240, 300 )
        self.setMinimumSize( 240, 300 )

        self.updateList()

    def addAction( self ):

        playlist = Playlist.get( Playlist.add("Untitled") )

        x = self.ui_list.rowCount()
        item = PlaylistDialogItem( playlist )

        self.ui_list.insertRow( x )

        self.ui_list.setItem( x, 0, item )

        button = PlaylistRemoveButton( self, playlist )
        button.triggered.connect( self.listRemoveClicked )
        self.ui_list.setCellWidget( x, 1, button)
        self.ui_list.setCurrentCell( x, 0 )

        self.ui_list.editItem( self.ui_list.item(x, 0) )

    def editAction( self ):

        x = self.ui_list.rowCount()
        id = Settings.get( 'playlist' )

        for i in range(0, x):
            item = self.ui_list.item( i, 0 )
            if int(item.getPlaylist()['id']) == int(id):
                self.listItemClicked( item )
                self.ui_list.editItem( item )

    def updateList( self ):

        playlists = Playlist.getPlaylists()

        self.ui_list.setRowCount( len(playlists) )

        x = 0
        id = int(Settings.get( 'playlist' ))

        for playlist in playlists:
            item = PlaylistDialogItem( playlist )
            self.ui_list.setItem(x, 0, item)

            if int(playlist['id']) == id:
                self.ui_list.setCurrentItem( item )
                self.listItemClicked( item )
                self.ui_list.scrollToItem( self.ui_list.item(x, 0) )

            button = PlaylistRemoveButton( self, playlist )
            button.triggered.connect( self.listRemoveClicked )

            self.ui_list.setCellWidget( x, 1, button)

            x = x + 1

    def listCellChanged( self, row, column ):

        item = self.ui_list.item( row, column )
        playlist = item.getPlaylist()
        Playlist.update( playlist['id'], item.text() )

        self.renamed.emit( playlist['id'] )

    def listRemoveClicked( self, action ):

        id = action.getPlaylist()['id']
        Playlist.delete( id )

        self.updateList()

    def listItemClicked( self, item ):

        x = self.ui_list.rowCount()
        y = self.ui_list.selectedIndexes()[0].row()

        for i in range(0, x):
            b = self.ui_list.cellWidget( i, 1 )

            if b and y == i:
                b.setIconState( False)
            elif b:
                b.setIconState( True )

        self.selected.emit( item.getPlaylist()['id'] )

    def listItemSelected( self ):

        item = self.ui_list.item( self.ui_list.currentRow(), 0 )

        self.listItemClicked( item )

    def selectedEvent( self, id ):
        pass

    def showAt( self, point ):
        
        super(PlaylistDialog, self).showAt( point )

        self.ui_list.update()


class PlaylistDialogItem(QTableWidgetItem):

    def __init__( self, item ):
        super(PlaylistDialogItem, self).__init__( item['title'] )

        self.playlist = item

        self.setFlags( self.flags() | Qt.ItemIsEditable )

    def getPlaylist( self ):
        return self.playlist


class PlaylistRemoveButton(QToolButton):

    triggered = pyqtSignal("QToolButton")

    def __init__( self, parent, item ):
        super(PlaylistRemoveButton, self).__init__( parent )

        self.playlist = item

        self.setIconState( True )
        self.setMinimumSize( 16, 16 )

        self.setStyleSheet("QToolButton {background: transparent;border: none;padding: 0;margin: 0;}")

        self.clicked.connect( self.clickedEvent )
        self.triggered.connect( self.triggeredEvent )

    def getPlaylist( self ):
        return self.playlist

    def clickedEvent( self, checked ):

        self.triggered.emit( self )

    def triggeredEvent( self, button ):
        pass

    def setIconState( self, b ):

        if b:
            self.setIcon( QIcon(':/icons/remove.png') )
        else:
            self.setIcon( QIcon(':/icons/remove-white.png') )


class PlaylistTableWidget(QTableWidget):

    def __init__( self, parent=None ):
        super(PlaylistTableWidget, self).__init__( parent )

        self.setVerticalScrollMode( QAbstractItemView.ScrollPerPixel )
        self.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.setAutoScroll( False )

        original = self.verticalScrollBar()

        self.scrollbar = QScrollBar( Qt.Vertical, self )
        self.scrollbar.valueChanged.connect( original.setValue )
        self.scrollbar.rangeChanged.connect( self.scrollToSelected )

        original.valueChanged.connect( self.scrollbar.setValue )

        self.updateScrollbar()

    def paintEvent( self, event ):

        QTableWidget.paintEvent( self, event )

        self.updateScrollbar()

        x = self.rowCount()
        y = self.selectedIndexes()[0].row()

        for i in range(0, x):
            b = self.cellWidget( i, 1 )

            if b and y == i:
                b.setIconState( False)
            elif b:
                b.setIconState( True )

    def update( self ):

        super(PlaylistTableWidget, self).update()
        self.updateScrollbar()

    def updateScrollbar( self ):

        original = self.verticalScrollBar()

        if not hasattr(self, 'scrollbar'):
            return

        if original.value() == original.maximum() and original.value() == 0:
            self.scrollbar.hide()
        else:
            self.scrollbar.show()

        self.scrollbar.setPageStep( original.pageStep() )
        self.scrollbar.setRange( original.minimum(), original.maximum() )
        self.scrollbar.resize( 8, self.rect().height() )
        self.scrollbar.move( self.rect().width() - 8, 0 )

    def scrollToSelected( self ):

        selected = self.selectedIndexes()

        if len(selected) == 0:
            x = 0
            self.setCurrentCell( x, 0 )
        else:
            x = selected[0].row()

        self.scrollToItem( self.item(x, 0) )
