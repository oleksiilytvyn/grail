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
from PyQt5.QtWidgets import QTreeWidgetItem


class PageTreeWidgetItem(QTreeWidgetItem):

    def __init__( self, parent=None ):
        super(PageTreeWidgetItem, self).__init__(parent)

        self.setFlags( Qt.ItemIsEnabled | Qt.ItemIsSelectable )

        self.id = 0
        self.page = ""
        self.song = 0
        self.data = None

    def setPage( self, page ):
        self.id = page['id']
        self.page = page['page']
        self.song = page['song']

        self.setText( 0, self.page )
        self.data = page

    def getPage( self ):
        return self.data
