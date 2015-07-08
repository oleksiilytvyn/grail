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


class PlaylistsModel:
    '''
    Playlist managment
    '''

    def __init__( self ):

        path = get_data_path() + '/songs.db'
        first_run = False

        if not os.path.isfile( path ):
            first_run = True

        self.connection = ConnectionManager.get( path )

        if first_run:

            cur = self.connection.cursor()

            cur.execute("DROP TABLE IF EXISTS songs")
            cur.execute("""CREATE TABLE songs(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        artist TEXT,
                        album TEXT,
                        year INT)""")

            cur.execute("DROP TABLE IF EXISTS pages")
            cur.execute("CREATE TABLE pages(id INTEGER PRIMARY KEY AUTOINCREMENT, song INT, sort INT, page TEXT)")

            cur.execute("DROP TABLE IF EXISTS playlists")
            cur.execute("CREATE TABLE playlists(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT)")

            cur.execute("DROP TABLE IF EXISTS playlist")
            cur.execute("""CREATE TABLE playlist(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        playlist INT,
                        sort INT,
                        song INT,
                        collapsed INTEGER)""")

            cur.execute("INSERT INTO playlists VALUES(NULL, ?)", ("Default", ))

    def get( self, id ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM playlists WHERE id = ?", (id,))

        return cursor.fetchone()

    def update( self, id, title ):

        cur = self.connection.cursor()

        cur.execute("UPDATE playlists SET title=? WHERE id=?", (title, id))
        self.connection.commit()

    def add( self, title ):

        cur = self.connection.cursor()
        cur.execute("INSERT INTO playlists VALUES(NULL, ?)", (title, ))
        self.connection.commit()

        return cur.lastrowid

    def delete( self, id ):

        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM playlist WHERE playlist = ?", (id,))
        cursor.execute("DELETE FROM playlists WHERE id = ?", (id,))
        self.connection.commit()

    def getPlaylists( self ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM playlists")

        return cursor.fetchall()

    def getSongs( self, id ):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT
                playlist.id AS pid,
                songs.id,
                songs.title,
                songs.artist,
                songs.album,
                songs.year,
                playlist.collapsed
            FROM songs, playlist
            WHERE
                playlist.playlist = ?
                AND songs.id = playlist.song
                ORDER BY playlist.sort
            """, (id,))

        return cursor.fetchall()

    def getSongsLink( self, id ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM playlist WHERE playlist = ?", (id,))

        return cursor.fetchall()

    def addSong( self, playlist, song ):
        cur = self.connection.cursor()
        cur.execute("""INSERT INTO playlist
                    VALUES(NULL, ?, (SELECT max(sort) FROM playlist WHERE playlist = ?) + 1, ?, 0)""",
                    (playlist, playlist, song))
        self.connection.commit()

    def deleteSong( self, playlist, song ):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM playlist WHERE playlist = ? AND song = ?", (playlist, song))
        self.connection.commit()

    def collapseSong( self, playlist, song, collapsed ):
        cur = self.connection.cursor()
        cur.execute("UPDATE playlist SET collapsed=? WHERE playlist = ? AND song = ?", (int(collapsed), playlist, song))
        self.connection.commit()

    def sortSongs( self, playlist, item, index ):
        cur = self.connection.cursor()
        cur.execute("UPDATE playlist SET sort=? WHERE id = ?", (index, item))
        self.connection.commit()

    def close( self ):
        self.connection.commit()
        self.connection.close()

Playlist = PlaylistsModel()
