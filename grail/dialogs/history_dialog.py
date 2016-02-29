#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Grail - Lyrics software. Simple.
# Copyright (C) 2014-2016 Oleksii Lytvyn
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
from grail.data import History, HistoryItem


class HistoryDialog(QDialog):

    itemSelected = pyqtSignal(object)

    def __init__( self, parent=None ):

        super(HistoryDialog, self).__init__(parent)

        History.changed.connect( self.update )

        self.initUI()

    def initUI( self ):

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setObjectName( "songsBar" )
        self.ui_layout.setSpacing( 0 )
        self.ui_layout.setContentsMargins( 0, 0, 0, 0 )

        self.ui_search = QSearchEdit()
        self.ui_search.setObjectName( "historySearch" )
        self.ui_search.setPlaceholderText( "Search History" )
        self.ui_search.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.ui_search.textChanged.connect( self.searchAction )
        self.ui_search.keyPressed.connect( self.searchKeyEvent )

        self.ui_list = SearchListWidget()
        self.ui_list.setObjectName( "historyList" )
        self.ui_list.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.ui_list.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.ui_list.setContextMenuPolicy( Qt.CustomContextMenu )

        self.ui_list.itemDoubleClicked.connect( self.itemDoubleClicked )
        self.ui_list.keyPressed.connect( self.listKeyEvent )

        clearAction = QAction( 'Clear', self )
        clearAction.triggered.connect( self.clear )

        self.ui_itemsLabel = QLabel("")
        self.ui_itemsLabel.setObjectName( "historyLabel" )
        self.ui_itemsLabel.setAlignment( Qt.AlignCenter )
        self.ui_itemsLabel.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )

        self.ui_panel_label = QLabel("Nothing in history yet.", self.ui_list )
        self.ui_panel_label.setAlignment( Qt.AlignCenter )
        self.ui_panel_label.setFont( QFont('Decorative', 12) )
        self.ui_panel_label.setObjectName( "historyPanelLabel" )

        self.ui_toolbar = QToolBar()
        self.ui_toolbar.setObjectName( "historyToolbar" )
        self.ui_toolbar.addAction( clearAction )
        self.ui_toolbar.addWidget( self.ui_itemsLabel )

        self.ui_layout.addWidget( self.ui_search )
        self.ui_layout.addWidget( self.ui_list )
        self.ui_layout.addWidget( self.ui_toolbar )

        self.setLayout( self.ui_layout )

        self.update()
        self.updateLabel()

        if not PLATFORM_MAC:
            self.setWindowIcon( QIcon(':/icons/32.png') )

        self.setWindowTitle('History')
        self.setGeometry( 300, 300, 240, 380 )
        self.setMinimumSize( 240, 380 )
        self.setWindowFlags( Qt.WindowCloseButtonHint )

    def searchAction( self, text ):
        keyword = str(self.ui_search.text())

        if keyword:
            self.updateSearch( History.search(keyword) )
        else:
            self.updateSearch()

    def searchKeyEvent( self, event ):

        if event.key() == Qt.Key_Escape:
            self.ui_search.setText("")
        else:
            QLineEdit.keyPressEvent( self.ui_search, event )

    def clear( self ):

        History.clear()

    def resizeEvent( self, event ):

        self.updateLabel()

    def updateLabel( self ):
        qr = self.ui_panel_label.geometry()
        cp = self.rect().center()
        self.ui_panel_label.resize( self.rect().width(), qr.height() )
        qr.moveCenter( cp )
        qr.setY( qr.y() - 47 )
        self.ui_panel_label.move( qr.topLeft() )

        if self.ui_list.count() > 0:
            self.ui_panel_label.hide()
        else:
            self.ui_panel_label.show()

    def updateSearch( self, items=None ):

        self.ui_list.clear()

        if not items:
            items = History.getAll()

        for item in items:
            self.ui_list.addItem( ListHistoryItem( HistoryItem( item['type'], item['title'], item['message'] ) ) )

        self.ui_itemsLabel.setText( "%d items" % len(items) )

        self.updateLabel()

    def update( self ):

        self.searchAction( "" )

    def itemDoubleClicked( self, item ):

        self.itemSelected.emit( item.getItem() )

    def listKeyEvent( self, event ):

        if event.key() == Qt.Key_Return:
            items = self.ui_list.selectedItems()

            if len(items) > 0:
                self.itemSelected.emit( items[0].getItem() )
        else:
            QListWidget.keyPressEvent( self.ui_list, event )


class ListHistoryItem(QListWidgetItem):

    def __init__( self, item ):
        super(ListHistoryItem, self).__init__()

        self.data = item

        self.setText( item.title )

    def getItem( self ):
        return self.data
