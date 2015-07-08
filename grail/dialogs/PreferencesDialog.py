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

from grail.data import Settings, RemoteAction
from grail.utils import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .OSCSourceDialog import OSCSourceDialog


class PreferencesDialog(OSCSourceDialog):

    osc_out_changed = pyqtSignal(object)

    def __init__(self, parent=None, song=None):
        super(PreferencesDialog, self).__init__(parent)

        self.ui_itemsLabel.setText( '0 destinations' )
        self.ui_panel_label.setText( 'No destinations' )
        self.setWindowTitle('Preferences')

        self.changed.connect( self.listChanged )

        oscout = Settings.getOSCOutputRules()

        for item in oscout:
            self.addItem( item['host'], str(item['port']) )

    def updateLabel( self ):

        self.ui_itemsLabel.setText( "%d destinations" % (self.ui_list.rowCount(), ) )

        qr = self.ui_panel_label.geometry()
        cp = self.rect().center()
        self.ui_panel_label.resize( self.rect().width(), qr.height() )
        qr.moveCenter( cp )
        qr.setY( qr.y() - 47 )
        self.ui_panel_label.move( qr.topLeft() )

        if self.ui_list.rowCount() > 0:
            self.ui_panel_label.hide()
        else:
            self.ui_panel_label.show()

    def listChanged( self, items ):

        Settings.deleteOSCOutputRules()

        for item in items:
            if item[0] and item[1]:
                Settings.addOSCOutputRule( item[0], int(item[1]) )

        self.osc_out_changed.emit( items )
