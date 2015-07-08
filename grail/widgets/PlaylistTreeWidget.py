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

from .SongTreeWidgetItem import SongTreeWidgetItem
from .PageTreeWidgetItem import PageTreeWidgetItem


class PlaylistTreeWidget(QTreeWidget):

    keyPressed = pyqtSignal('QKeyEvent')
    orderChanged = pyqtSignal()

    def __init__( self, parent=None ):
        super(PlaylistTreeWidget, self).__init__(parent)

        self.setObjectName( "playlistTree" )
        self.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.header().close()

        self.setSelectionMode( QAbstractItemView.SingleSelection )
        self.setDragEnabled( True )
        self.viewport().setAcceptDrops( True )
        self.setDropIndicatorShown( True )
        self.setDragDropMode( QAbstractItemView.InternalMove )
        self.setWordWrap( True )

        self.setAnimated( True )
        self.setSortingEnabled( False )
        self.setDropIndicatorShown( True )

        self.keyPressed.connect( self.keyPressedEvent )
        self.setVerticalScrollMode( QAbstractItemView.ScrollPerPixel )
        self.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )

        original = self.verticalScrollBar()

        self.scrollbar = QScrollBar( Qt.Vertical, self )
        self.scrollbar.valueChanged.connect( original.setValue )

        original.valueChanged.connect( self.scrollbar.setValue )

        self.updateScrollbar()

    def keyPressEvent( self, event ):
        self.keyPressed.emit( event )

    def keyPressedEvent( self, event ):
        pass

    def dropEvent( self, event ):

        dropingOn = self.itemAt( event.pos() )
        dropingIndex = self.indexOfTopLevelItem( dropingOn )
        draggingItem = self.currentItem()

        # count items in list
        iterator = QTreeWidgetItemIterator(self)
        items_count = 0

        while iterator.value():
            if type( iterator.value() ) == SongTreeWidgetItem:
                items_count += 1

            iterator += 1

        if type( dropingOn ) == SongTreeWidgetItem:
            expanded = draggingItem.isExpanded()
            self.takeTopLevelItem( self.indexOfTopLevelItem( draggingItem ) )

            index = self.indexOfTopLevelItem( dropingOn )

            dp = self.dropIndicatorPosition()

            if dp == QAbstractItemView.BelowItem:
                index = index + 1

            if index == items_count:
                index = index - 1

            self.insertTopLevelItem(index, draggingItem)
            self.setCurrentItem( draggingItem )
            draggingItem.setExpanded( expanded )

        self.orderChanged.emit()

    def updateScrollbar( self ):

        original = self.verticalScrollBar()

        if original.value() == original.maximum() and original.value() == 0:
            self.scrollbar.hide()
        else:
            self.scrollbar.show()

        self.scrollbar.setPageStep( original.pageStep() )
        self.scrollbar.setRange( original.minimum(), original.maximum() )
        self.scrollbar.resize( 8, self.rect().height() )
        self.scrollbar.move( self.rect().width() - 8, 0 )

    def paintEvent( self, event ):

        QTreeWidget.paintEvent( self, event )
        self.updateScrollbar()
