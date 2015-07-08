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


class SearchListWidget(QListWidget):

    keyPressed = pyqtSignal('QKeyEvent')

    def __init__( self, parent=None ):
        super(SearchListWidget, self).__init__(parent)

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
