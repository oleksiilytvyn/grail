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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QListWidgetItem


class SearchListItem(QListWidgetItem):

    TYPE_DEFAULT = 0
    TYPE_SONG = 1
    TYPE_BIBLE = 2
    TYPE_REFERENCE = 3
    TYPE_HISTORY = 4

    def __init__( self, parent=None ):
        super(SearchListItem, self).__init__(parent)

        self.data = None
        self.type = None
        self.message = ""

    def setType( self, item_type ):
        self.type = item_type

    def setSong( self, song ):
        self.data = song

        self.setType( SearchListItem.TYPE_SONG )
        self.setText( '%s - %s' % (song["title"], song["artist"]) )

    def setMessage( self, text ):
        self.message = text

    def getMessage( self ):
        return self.message

    def setItemData( self, data ):
        self.data = data

    def getData( self ):
        return self.data
