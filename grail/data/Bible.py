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


def indexof(s, char):
    return s.find(char)


def string_rank( S, H ):
    s = S.lower()
    h = H.lower()
    sl = len(s)
    hl = len(h)
    si = indexof(s, h)
    a = 0
    i = 0
    j = 0

    if s == h:
        return 9

    if si >= 0:
        return (sl - si) / sl + hl / sl + 2

    while i < min(sl, hl):
        if h[j] == s[i]:
            j = j + 1

        i = i + 1

    return j / sl + ((sl - indexof(s, h[0])) / sl if indexof(s, h[0]) >= 0 else 0)


class BibleModel():

    def __init__( self ):

        path = get_data_path() + '/bible.db'
        first_run = False

        if not os.path.isfile( path ):
            first_run = True

        self.connection = ConnectionManager.get( path )

        if first_run:
            cur = self.connection.cursor()

            cur.execute("DROP TABLE IF EXISTS books")
            cur.execute("CREATE TABLE books(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, full TEXT, short TEXT )")

            cur.execute("DROP TABLE IF EXISTS verses")
            cur.execute("CREATE TABLE verses(id INTEGER PRIMARY KEY AUTOINCREMENT, book INT, chapter INT, verse INT )")

    def close( self ):
        self.connection.commit()
        self.connection.close()

    def get( self, book, chapter, index ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM verses WHERE book = ? AND chapter = ? AND verse = ?", (book, chapter, index))

        return cursor.fetchone()[ 3 ]

    def getChapter( self, book, chapter ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM verses WHERE book = ? AND chapter = ? ORDER BY verse ASC", (book, chapter))

        return cursor.fetchall()

    def getBook( self, book ):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book, ))

        return cursor.fetchone()

    def getBooks( self ):

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM books")

        return cursor.fetchall()

    def matchBook( self, keyword ):
        keyword = "%" + keyword + "%"

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM books
            WHERE
             lowercase(title) LIKE lowercase( ? )
             OR lowercase(short) LIKE lowercase( ? )
             OR lowercase(full) LIKE lowercase( ? )
            """, (keyword, keyword, keyword ))

        return cursor.fetchall()

    def matchReference( self, keyword ):
        possible = []
        chapter = 1
        verse = 1

        match_c = re.search( r'([0-9]+)$', keyword)
        match_cv = re.search( r'([0-9]+)([\D]{1})([0-9]+)$', keyword )
        match_ce = re.search( r'([0-9]+)([\D]{1})([0-9]+)\-([0-9]+)$', keyword )

        if match_ce:
            chapter = match_ce.group(1)
            verse = match_ce.group(3)
            keyword = re.sub( r'([0-9]+)([\D]{1})([0-9]+)\-([0-9]+)$', '', keyword )
        elif match_cv:
            chapter = match_cv.group(1)
            verse = match_cv.group(3)
            keyword = re.sub( r'([0-9]+)([\D]{1})([0-9]+)$', '', keyword )
        elif match_c:
            chapter = match_c.group(1)
            keyword = re.sub( r'([0-9]+)$', '', keyword )

        books = self.getBooks()

        keyword = keyword.lstrip().rstrip()

        for book in books:
            m1 = string_rank( book['title'], keyword )
            m2 = string_rank( book['full'], keyword )
            m3 = string_rank( book['short'], keyword )
            r = (m1 + m2 + m3) / 3

            if r >= 1.1:
                possible.append([ "%s %s:%s" % (book['title'], chapter, verse), [book['id'], chapter, verse], r ])

        def getKey(item):
            return -item[2]

        return sorted(possible, key=getKey)[0:3]

Bible = BibleModel()
