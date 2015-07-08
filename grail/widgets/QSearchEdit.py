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


class QSearchEdit(QLineEdit):

    keyPressed = pyqtSignal('QKeyEvent')

    def __init__( self, parent=None ):
        super(QSearchEdit, self).__init__(parent)

        self.keyPressed.connect( self.keyPressedEvent )

        self.setPlaceholderText( "Search Library" )

        self.clearButton = QToolButton( self )
        self.clearButton.setIconSize( QSize(14, 14) )
        self.clearButton.setIcon( QIcon(':/icons/search-clear.png') )
        self.clearButton.setCursor( Qt.ArrowCursor )
        self.clearButton.setStyleSheet("QToolButton { border: none; padding: 0px; }")
        self.clearButton.hide()

        self.clearButton.clicked.connect( self.clear )
        self.textChanged.connect( self.updateClearButton )

        frameWidth = self.style().pixelMetric( QStyle.PM_DefaultFrameWidth )
        self.setStyleSheet( "QLineEdit { padding-right: %spx; height: 21px;} " %
                            str(self.clearButton.sizeHint().width() + frameWidth + 1) )
        msz = self.minimumSizeHint()
        self.setMinimumSize(
            max(msz.width(), self.clearButton.sizeHint().height() + frameWidth * 2 + 2),
            max(msz.height(), self.clearButton.sizeHint().height() + frameWidth * 2 + 2))

    def resizeEvent( self, event ):
        sz = self.clearButton.sizeHint()
        self.clearButton.move( self.rect().right() - sz.width(), (self.rect().bottom() + 5 - sz.height()) / 2 )

    def updateClearButton( self, text ):
        self.clearButton.setVisible( len(text) > 0 )

    def keyPressEvent( self, event ):
        self.keyPressed.emit( event )

    def keyPressedEvent( self, event ):
        pass
