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
import sqlite3 as lite

from .ConnectionManager import ConnectionManager


class SongModel:

    '''
    Songs data model
    '''

    def __init__( self ):

        path = get_data_path() + '/songs.db'
        first_run = False

        if not os.path.isfile( path ):
            first_run = True

        self.connection = ConnectionManager.get( path, get_path() + '/default/songs.db' )

        if first_run:

            cur = self.connection.cursor()

            cur.execute("""CREATE TABLE IF NOT EXISTS songs(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        artist TEXT,
                        album TEXT,
                        year INT)""")

            cur.execute("CREATE TABLE IF NOT EXISTS pages(id INTEGER PRIMARY KEY AUTOINCREMENT, song INT, sort INT, page TEXT)")

            cur.execute("CREATE TABLE IF NOT EXISTS playlists(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT)")

            cur.execute("""CREATE TABLE IF NOT EXISTS playlist(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        playlist INT,
                        sort INT,
                        song INT,
                        collapsed INTEGER)""")

            cur.execute("INSERT INTO playlists VALUES(NULL, ?)", ("Default", ))

    def close( self ):
        self.connection.commit()
        self.connection.close()

    def getConnection( self ):
        return self.connection

    def get( self, id ):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM songs WHERE id = ?", (id,))

        return cur.fetchone()

    def search( self, keyword ):
        keyword = "%" + keyword + "%"

        cur = self.connection.cursor()
        cur.execute("""
            SELECT * FROM songs
            WHERE
             id IN ( SELECT song FROM pages WHERE lowercase(page) LIKE lowercase(?) )
             OR searchprep(title) LIKE searchprep( ? )
             OR lowercase(album) LIKE lowercase( ? )
             OR lowercase(artist) LIKE lowercase( ? )
             OR year LIKE ?
             ORDER BY title
            """, (keyword, keyword, keyword, keyword, keyword))

        return cur.fetchall()

    def add( self, title, artist="unknown", album="unknown", year=0 ):
        record = (title, artist, album, year)

        cur = self.connection.cursor()
        cur.execute("INSERT INTO songs VALUES(NULL, ?, ?, ?, ?)", record)
        self.connection.commit()

        return cur.lastrowid

    def update( self, id, title, artist, album, year ):
        cur = self.connection.cursor()

        cur.execute("UPDATE songs SET title=?, artist=?, album=?, year=? WHERE id=?", (title, artist, album, year, id))
        self.connection.commit()

    def delete( self, id ):
        # if song in any playlist dont delete it
        cursor = self.connection.cursor()

        cursor.execute("SELECT * FROM playlist WHERE song = ?", (id,))

        if not cursor.fetchall():
            cursor.execute("DELETE FROM songs WHERE id = ?", (id,))
            cursor.execute("DELETE FROM pages WHERE song = ?", (id,))

    def getList( self ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM songs ORDER BY title")

        return cursor.fetchall()

    def getPage( self, id, index ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM pages WHERE song = ? AND sort = ?", (id, index))

        return cursor.fetchone()

    def getPages( self, id ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM pages WHERE song = ? ORDER BY sort ASC", (id,))

        return cursor.fetchall()

    def addPage( self, id, text ):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO pages VALUES(NULL, ?, (SELECT max(sort) FROM pages WHERE song = ?) + 1, ?)",
                    (id, id, text))

    def deletePage( self, id, index ):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM pages WHERE song = ? AND sort = ?", (id, index))

    def deletePages( self, id ):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM pages WHERE song = ?", (id, ))

    def updatePage( self, id, index, page ):
        cur = self.connection.cursor()

        cur.execute("UPDATE pages SET page=? WHERE song=? AND id=?", (page, id, index))
        self.connection.commit()

Song = SongModel()
