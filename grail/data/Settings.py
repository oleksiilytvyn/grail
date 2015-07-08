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

from grail.utils import *
from .ConnectionManager import ConnectionManager


class SettingsModel:

    def __init__( self ):

        path = get_data_path() + '/settings.db'
        first_run = False

        if not os.path.isfile( path ):
            first_run = True

        self.connection = ConnectionManager.get( path )

        if first_run:
            cur = self.connection.cursor()

            cur.execute("DROP TABLE IF EXISTS properties")
            cur.execute("CREATE TABLE properties(key TEXT PRIMARY KEY, value TEXT)")

            cur.execute("DROP TABLE IF EXISTS oscin")
            cur.execute("""CREATE TABLE oscin(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        host TEXT,
                        port INT,
                        message TEXT,
                        action INT )""")

            cur.execute("DROP TABLE IF EXISTS oscout")
            cur.execute("CREATE TABLE oscout(id INTEGER PRIMARY KEY AUTOINCREMENT, host TEXT, port INT )")

            self.set( 'playlist', 1 )

    def close( self ):
        self.connection.commit()
        self.connection.close()

    def get( self, property ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM properties WHERE key = ?", (property,))
        self.connection.commit()
        item = cursor.fetchone()

        if item:
            return item['value']
        else:
            return None

    def set( self, property, value ):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM properties WHERE key = ?", (property,))
        cur.execute("INSERT INTO properties VALUES(?, ?)", (property, value))
        self.connection.commit()

        return cur.lastrowid

    def addOSCInputRule( self, host, port, message, action ):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO oscin VALUES(NULL, ?, ?, ?, ?)", (host, port, message, action))
        self.connection.commit()

    def deleteOSCInputRules( self ):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM oscin")
        self.connection.commit()

    def getOSCInputRules( self ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM oscin")

        return cursor.fetchall()

    def addOSCOutputRule( self, host, port ):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO oscout VALUES(NULL, ?, ?)", (host, port))
        self.connection.commit()

    def deleteOSCOutputRules( self ):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM oscout")
        self.connection.commit()

    def getOSCOutputRules( self ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM oscout")

        return cursor.fetchall()

    def save( self ):
        self.connection.commit()

Settings = SettingsModel()
