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


class AlignDialog(BalloonDialog):

    updated = pyqtSignal(int, int)

    def __init__( self, horizontal, vertical ):
        super(AlignDialog, self).__init__( None )

        self.align_horizontal = horizontal
        self.align_vertical = vertical

        self.initUI()

    def initUI( self ):

        self.setStyleSheet( get_stylesheet() )

        self.ui_horizontal = QComboBox()
        self.ui_horizontal.activated.connect( self.valueChanged )

        hindex = [Qt.AlignLeft, Qt.AlignHCenter, Qt.AlignRight].index( self.align_horizontal )
        vindex = [Qt.AlignTop, Qt.AlignVCenter, Qt.AlignBottom].index( self.align_vertical )

        self.ui_horizontal.addItem( "Left", QVariant(Qt.AlignLeft) )
        self.ui_horizontal.addItem( "Center", QVariant(Qt.AlignHCenter) )
        self.ui_horizontal.addItem( "Right", QVariant(Qt.AlignRight) )
        self.ui_horizontal.setCurrentIndex( hindex )

        self.ui_vertical = QComboBox()
        self.ui_vertical.activated.connect( self.valueChanged )

        self.ui_vertical.addItem( "Top", QVariant(Qt.AlignTop) )
        self.ui_vertical.addItem( "Middle", QVariant(Qt.AlignVCenter) )
        self.ui_vertical.addItem( "Bottom", QVariant(Qt.AlignBottom) )
        self.ui_vertical.setCurrentIndex( vindex )

        self.ui_layout = QGridLayout()
        self.ui_layout.setSpacing( 8 )
        self.ui_layout.setContentsMargins( 12, 12, 12, 12 )

        self.ui_layout.addWidget( QLabel('Horiontal'), 0, 0 )
        self.ui_layout.addWidget( self.ui_horizontal, 1, 0 )

        self.ui_layout.addWidget( QLabel('Vertical'), 2, 0 )
        self.ui_layout.addWidget( self.ui_vertical, 3, 0 )

        self.setLayout( self.ui_layout )

        self.setWindowTitle('Align')
        self.setGeometry( 100, 300, 120, 128 )

    def valueChanged( self, i ):

        self.align_horizontal = self.ui_horizontal.currentData()
        self.align_vertical = self.ui_vertical.currentData()

        self.updated.emit( self.align_horizontal, self.align_vertical )

    def setAlign( self, horizontal, vertical ):

        self.align_horizontal = horizontal
        self.align_vertical = vertical
