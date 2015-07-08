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


class PaddingDialog(BalloonDialog):

    updated = pyqtSignal("QMargins")

    def __init__( self, padding ):
        super(PaddingDialog, self).__init__( None )

        self.padding = padding

        self.initUI()

    def initUI( self ):

        self.setStyleSheet( get_stylesheet() )

        self.ui_left = QSpinBox()
        self.ui_left.setRange( 0, 1000 )
        self.ui_left.setValue( self.padding.left() )
        self.ui_left.valueChanged.connect( self.valueChanged )

        self.ui_right = QSpinBox()
        self.ui_right.setRange( 0, 1000 )
        self.ui_right.setValue( self.padding.right() )
        self.ui_right.valueChanged.connect( self.valueChanged )

        self.ui_top = QSpinBox()
        self.ui_top.setRange( 0, 1000 )
        self.ui_top.setValue( self.padding.top() )
        self.ui_top.valueChanged.connect( self.valueChanged )

        self.ui_bottom = QSpinBox()
        self.ui_bottom.setRange( 0, 1000 )
        self.ui_bottom.setValue( self.padding.bottom() )
        self.ui_bottom.valueChanged.connect( self.valueChanged )

        self.ui_layout = QGridLayout()
        self.ui_layout.setSpacing( 8 )
        self.ui_layout.setContentsMargins( 12, 12, 12, 12 )

        self.ui_layout.addWidget( QLabel('Left'), 0, 0 )
        self.ui_layout.addWidget( self.ui_left, 1, 0 )

        self.ui_layout.addWidget( QLabel('Right'), 0, 1 )
        self.ui_layout.addWidget( self.ui_right, 1, 1 )

        self.ui_layout.addWidget( QLabel('Top'), 2, 0 )
        self.ui_layout.addWidget( self.ui_top, 3, 0 )

        self.ui_layout.addWidget( QLabel('Bottom'), 2, 1 )
        self.ui_layout.addWidget( self.ui_bottom, 3, 1 )

        self.setLayout( self.ui_layout )

        self.setWindowTitle('Composition')
        self.setGeometry( 100, 300, 240, 128 )

    def valueChanged( self, i ):

        self.padding = QMargins( self.ui_left.value(),
                                 self.ui_top.value(),
                                 self.ui_right.value(),
                                 self.ui_bottom.value() )
        self.updated.emit( self.padding )

    def setPadding( self, padding ):

        self.padding = padding
