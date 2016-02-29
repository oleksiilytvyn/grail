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
from PyQt5.QtWidgets import QTreeWidgetItem


class SongTreeWidgetItem(QTreeWidgetItem):

    def __init__( self, parent=None ):
        super(SongTreeWidgetItem, self).__init__(parent)

        self.setFlags( Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled )

        self.id = 0
        self.title = ''
        self.artist = ''
        self.album = ''
        self.year = 0

        self.song = None

    def setSong( self, song ):
        self.pid = song['pid']
        self.id = song['id']
        self.title = song['title']
        self.artist = song['artist']
        self.album = song['album']
        self.year = song['year']

        self.setText( 0, self.title )
        self.setExpanded( bool(song["collapsed"]) )

        self.song = song

    def getSong( self ):
        return self.song
