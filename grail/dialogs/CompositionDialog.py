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


class CompositionDialog(BalloonDialog):

    updated = pyqtSignal("QRect")

    def __init__( self, parent=None ):
        super(CompositionDialog, self).__init__( parent )

        self.composition = QRect(0, 0, 800, 600)

        self.initUI()
        self.updateUI()

    def initUI( self ):

        self.setStyleSheet( get_stylesheet() )

        self.ui_width = QSpinBox()
        self.ui_width.setRange( 100, 32000 )
        self.ui_width.valueChanged.connect( self.valueChanged )

        self.ui_height = QSpinBox()
        self.ui_height.setRange( 100, 32000 )
        self.ui_height.valueChanged.connect( self.valueChanged )

        self.ui_preset = QComboBox()
        self.ui_preset.currentIndexChanged.connect( self.presetChanged )

        presets = [("Full HD (1920x1080)", QRect(0, 0, 1920, 1080)),
                   ("HD (1280x720)", QRect(0, 0, 1280, 720)),
                   ("SD (800x600)", QRect(0, 0, 800, 600))]

        for preset in presets:
            self.ui_preset.addItem( preset[0], preset[1] )

        self.ui_layout = QGridLayout()
        self.ui_layout.setSpacing( 8 )
        self.ui_layout.setContentsMargins( 12, 12, 12, 12 )

        self.ui_layout.addWidget( self.ui_preset, 0, 0, 1, 2 )

        self.ui_layout.addWidget( self.ui_width, 1, 0 )
        self.ui_layout.addWidget( self.ui_height, 1, 1 )

        self.setLayout( self.ui_layout )

        self.setWindowTitle('Composition')
        self.setGeometry( 100, 300, 240, 108 )

    def updateUI( self ):

        self.ui_width.setValue( self.composition.width() )
        self.ui_height.setValue( self.composition.height() )

    def valueChanged( self, i ):

        self.updated.emit( QRect(0, 0, self.ui_width.value(), self.ui_height.value() ) )

    def presetChanged( self, index ):

        rect = self.ui_preset.itemData( index )

        self.setCompositionGeometry( rect )
        self.updateUI()
        self.updated.emit( rect )

    def setCompositionGeometry( self, rect ):

        self.composition = rect
