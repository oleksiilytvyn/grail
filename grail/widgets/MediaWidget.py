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
from grail.widgets import *

import os

class MediaWidget(QWidget):

    itemSelected = pyqtSignal(object)
    switchMode = pyqtSignal()

    def __init__( self, parent=None ):

        super(MediaWidget, self).__init__(parent)

        self.files_list = []

        self.initUI()

    def initUI( self ):

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setObjectName( "media_dialog" )
        self.ui_layout.setSpacing( 0 )
        self.ui_layout.setContentsMargins( 0, 0, 0, 0 )

        addAction = QAction( 'Add', self )
        addAction.triggered.connect( self.addFilesAction )

        toggleAction = QAction( 'Library', self )
        toggleAction.triggered.connect( self.toggleAction )

        self.ui_expander = QWidget()
        self.ui_expander.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )

        self.ui_toolbar = QToolBar()
        self.ui_toolbar.setObjectName( "mediaToolbar" )
        self.ui_toolbar.addAction( addAction )
        self.ui_toolbar.addWidget( self.ui_expander )
        self.ui_toolbar.addAction( toggleAction )

        size = 128

        self.ui_list = ImageListWidget()
        self.ui_list.setObjectName( "mediaList" )
        self.ui_list.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.ui_list.itemDoubleClicked.connect( self.itemDoubleClicked )
        self.ui_list.keyPressed.connect( self.itemKeypress )
        self.ui_list.fileDropped.connect( self.fileDropped )

        self.ui_list.setDragEnabled( False )
        self.ui_list.setViewMode( QListView.IconMode )
        self.ui_list.setIconSize( QSize( size, size ) )
        self.ui_list.setSpacing( 1 )
        self.ui_list.setAcceptDrops( True )
        self.ui_list.setDropIndicatorShown( False )
        self.ui_list.setWrapping( True )
        self.ui_list.setLayoutMode( QListView.Batched )
        self.ui_list.setMovement( QListView.Snap )
        self.ui_list.setResizeMode( QListView.Adjust )
        self.ui_list.setBatchSize( size )
        self.ui_list.setGridSize( QSize( size, size ) )
        self.ui_list.setUniformItemSizes( True )

        self.ui_layout.addWidget( self.ui_list )
        self.ui_layout.addWidget( self.ui_toolbar )

        self.setLayout( self.ui_layout )

        self.setContextMenuPolicy( Qt.CustomContextMenu )
        self.customContextMenuRequested.connect( self.contextMenu )

    def contextMenu( self, pos ):

        menu = QMenu("Context Menu", self)

        clearAction = QAction('Clear list', menu)
        clearAction.triggered.connect( self.clear )

        addAction = QAction('Add', menu)
        addAction.triggered.connect( self.addFilesAction )

        menu.addAction( addAction )
        menu.addSeparator()
        menu.addAction( clearAction )

        ret = menu.exec_( self.mapToGlobal(pos) )

    def addFilesAction( self ):

        dialog = QFileDialog()
        dialog.setFileMode( QFileDialog.ExistingFiles )
        dialog.setNameFilter( "Images (*.png *.jpeg *.jpg *.gif)" )

        if dialog.exec():
            for path in dialog.selectedFiles():
                self.addListItem( path )

    def fileDropped( self, url ):

        path, ext = os.path.splitext(url.toLocalFile())

        if ext in [".png", ".jpeg", ".jpg", ".gif"]:
            self.addListItem( url.toLocalFile() )

    def clear( self ):

        self.files_list = []
        self.ui_list.clear()

    def toggleAction( self ):
        
        self.switchMode.emit()

    def blackoutAction( self ):

        self.itemSelected.emit( None )

    def addListItem( self, path ):

        if path not in self.files_list:
            pieceItem = QListWidgetItem()
            pieceItem.setIcon( QIcon( path ) )
            pieceItem.setData( Qt.UserRole, path )
            pieceItem.setFlags( Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

            self.files_list.append( path )
            self.ui_list.addItem( pieceItem )

    def itemDoubleClicked( self, item ):

        self.itemSelected.emit( item.data( Qt.UserRole ) )

    def itemKeypress( self, event ):

        if event.key() == Qt.Key_Return:
            item = self.ui_list.currentItem()
            self.itemSelected.emit( item.data( Qt.UserRole ) )
        else:
            QListWidget.keyPressEvent( self.ui_list, event )

class ImageListWidget(QListWidget):

    keyPressed = pyqtSignal('QKeyEvent')
    fileDropped = pyqtSignal('QUrl')

    def __init__( self, parent=None ):
        super(ImageListWidget, self).__init__(parent)

        self.keyPressed.connect( self.keyPressedEvent )
        self.setVerticalScrollMode( QAbstractItemView.ScrollPerPixel )
        self.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.setAttribute( Qt.WA_MacShowFocusRect, False )

        original = self.verticalScrollBar()

        self.scrollbar = QScrollBar( Qt.Vertical, self )
        self.scrollbar.valueChanged.connect( original.setValue )

        original.valueChanged.connect( self.scrollbar.setValue )

        self.updateScrollbar()

    def keyPressEvent( self, event ):
        self.keyPressed.emit( event )

    def keyPressedEvent( self, event ):
        pass

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

        QListWidget.paintEvent( self, event )
        self.updateScrollbar()

    def dragEnterEvent( self, event ):

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            QListWidget.dragEnterEvent( self, event )

    def dragMoveEvent( self, event ):
        
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            QListWidget.dragMoveEvent( self, event )

    def dropEvent( self, event ):

        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            
            if urls:
                for url in urls:
                    self.fileDropped.emit( url )

            event.acceptProposedAction()

        QListWidget.dropEvent( self, event )
