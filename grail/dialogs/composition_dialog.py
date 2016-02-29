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
from grail.data import Playlist, Settings
from grail.widgets import *

from .balloon_dialog import BalloonDialog


class CompositionDialog(BalloonDialog):

    updated = pyqtSignal("QRect")

    def __init__( self, parent=None ):
        super(CompositionDialog, self).__init__( parent )

        self.composition = QRect(0, 0, 800, 600)

        self.initUI()
        self.updateUI()

    def initUI( self ):

        self.ui_width = QSpinBox()
        self.ui_width.setRange( 100, 32000 )
        self.ui_width.valueChanged.connect( self.valueChanged )

        self.ui_height = QSpinBox()
        self.ui_height.setRange( 100, 32000 )
        self.ui_height.valueChanged.connect( self.valueChanged )

        self.ui_preset = QComboBox()
        self.ui_preset.currentIndexChanged.connect( self.presetChanged )

        self.updateList()

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

        comp = self.composition

        self.ui_width.setValue( comp.width() )
        self.ui_height.setValue( comp.height() )

        self.ui_preset.setItemText( 0, "Current (%dx%d)" % (comp.width(), comp.height()) )

    def updateList( self ):

        comp = self.composition
        presets = [("Current (%dx%d)" % (comp.width(), comp.height()), comp),
                   ("Full HD (1920x1080)", QRect(0, 0, 1920, 1080)),
                   ("HD (1366x768)", QRect(0, 0, 1366, 768)),
                   ("XGA (1024x768)", QRect(0, 0, 1024, 768)),
                   ("WXGA (1280x800)", QRect(0, 0, 1280, 800)),
                   ("SXGA (1280x1024)", QRect(0, 0, 1280, 1024)),
                   ("UXGA (1600x1200)", QRect(0, 0, 1600, 1200)),
                   ("SVGA (800x600)", QRect(0, 0, 800, 600))]

        self.ui_preset.clear()

        for preset in presets:
            self.ui_preset.addItem( preset[0], preset[1] )

        self.ui_preset.insertSeparator( 1 )

    def valueChanged( self, i ):

        comp = QRect(0, 0, self.ui_width.value(), self.ui_height.value() )
        
        self.setCompositionGeometry( comp )

    def presetChanged( self, index ):

        rect = self.ui_preset.itemData( index )

        if rect is None or index == 0:
            return

        self.setCompositionGeometry( rect )

    def setCompositionGeometry( self, rect ):

        self.composition = rect
        self.updated.emit( rect )
        self.updateUI()
