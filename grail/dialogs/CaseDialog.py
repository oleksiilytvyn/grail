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


class CaseDialog(BalloonDialog):

    updated = pyqtSignal(int)

    def __init__( self, case = 0 ):
        super(CaseDialog, self).__init__( None )

        self.case = case

        self.initUI()

    def initUI( self ):

        self.ui_case = QComboBox()
        self.ui_case.activated.connect( self.valueChanged )

        hindex = [0, 1, 2, 3].index( self.case )

        self.ui_case.addItem( "Normal", QVariant( 0 ) )
        self.ui_case.addItem( "Title", QVariant( 1 ) )
        self.ui_case.addItem( "Upper", QVariant( 2 ) )
        self.ui_case.addItem( "Lower", QVariant( 3 ) )
        self.ui_case.addItem( "Capitalize", QVariant( 4 ) )
        self.ui_case.setCurrentIndex( hindex )

        self.ui_layout = QGridLayout()
        self.ui_layout.setSpacing( 8 )
        self.ui_layout.setContentsMargins( 12, 12, 12, 12 )

        self.ui_layout.addWidget( QLabel('Text Case'), 0, 0 )
        self.ui_layout.addWidget( self.ui_case, 1, 0 )

        self.setLayout( self.ui_layout )

        self.setWindowTitle('Align')
        self.setGeometry( 100, 300, 120, 80 )

    def valueChanged( self, i ):

        self.case = self.ui_case.currentData()

        self.updated.emit( self.case )

    def setCase( self, case ):

        self.case = case
