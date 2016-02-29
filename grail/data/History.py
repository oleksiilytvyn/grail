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
from datetime import date, datetime

from .connection_manager import ConnectionManager


class HistoryModel(QObject):

    changed = pyqtSignal()

    def __init__( self ):

        super(HistoryModel, self).__init__()

        self.changed.connect( self.changedEvent )

        path = get_data_path() + '/history.db'
        first_run = False

        if not os.path.isfile( path ):
            first_run = True

        self.connection = ConnectionManager.get( path )

        if first_run:
            cur = self.connection.cursor()
            cur.execute("DROP TABLE IF EXISTS history")
            cur.execute("""CREATE TABLE history(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type INT,
                        title TEXT,
                        message TEXT,
                        added timestamp )""")

    def get( self, id ):

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM history WHERE id = ?", (id,))

        return cursor.fetchone()

    def getAll( self ):

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM history ORDER BY added DESC")

        return cursor.fetchall()

    def getLast( self, size = 10 ):

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM history ORDER BY added DESC LIMIT ?", (size,))

        return cursor.fetchall()

    def search( self, keyword ):

        keyword = "%" + keyword + "%"

        cur = self.connection.cursor()
        cur.execute("""
            SELECT * FROM history
            WHERE
             searchprep(title) LIKE searchprep( ? )
             OR lowercase(message) LIKE lowercase( ? )
             ORDER BY added DESC
            """, (keyword, keyword))

        return cur.fetchall()

    def clear( self ):

        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM history")
        self.connection.commit()

        self.changed.emit()

    def add( self, item_type, title, message ):

        cur = self.connection.cursor()
        cur.execute("INSERT INTO history VALUES(NULL, ?, ?, ?, ?)", ( item_type, title, message, datetime.now() ))
        self.connection.commit()

        self.changed.emit()

        return cur.lastrowid

    def changedEvent( self ):
        pass

    def close( self ):
        self.connection.commit()
        self.connection.close()

History = HistoryModel()
