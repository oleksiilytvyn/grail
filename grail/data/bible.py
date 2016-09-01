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

import os
import glob
import sqlite3 as lite

from grail.utils import *
from grail.data import Settings
from .connection_manager import ConnectionManager


def indexof(s, char):
    return s.find(char)


def string_rank(this, other):
    s = this.lower()
    h = other.lower()
    sl = len(s)
    hl = len(h)
    si = indexof(s, h)
    i = 0
    j = 0

    if s == h:
        return 9

    if si >= 0:
        return (sl - si) / sl + hl / sl + 2

    while i < min(sl, hl):
        if h[j] == s[i]:
            j += 1

        i += 1

    return j / sl + ((sl - indexof(s, h[0])) / sl if indexof(s, h[0]) >= 0 else 0)


class BibleModel:

    def __init__(self):

        self.connection = None

        bible_path = Settings.get('bible.path')
        default_bible_path = get_data_path() + '/bibles/default-ru-rst.db'

        # use bible that already selected as primary
        if bible_path is not None and os.path.isfile(bible_path) and os.path.getsize(bible_path) > 100:
            self.change_bible(bible_path)

            return

        # install default bible
        copy_file(get_path() + '/default/bible.db', default_bible_path)
        self.change_bible(default_bible_path)

    def change_bible(self, path):

        new_connection = ConnectionManager.get(path)
        cursor = new_connection.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS
               books(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, full TEXT, short TEXT )""")

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS
               verses(id INTEGER PRIMARY KEY AUTOINCREMENT, book INT, chapter INT, verse INT )""")

        if new_connection:
            self.connection = new_connection
            Settings.set('bible.path', path)

    def close(self):
        self.connection.commit()
        self.connection.close()

    def get(self, book, chapter, index):
        """Get single verse"""

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM verses WHERE book = ? AND chapter = ? AND verse = ?", (book, chapter, index))

        return cursor.fetchone()[3]

    def get_chapter(self, book, chapter):
        """Get all verses in chapter"""

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM verses WHERE book = ? AND chapter = ? ORDER BY verse ASC", (book, chapter))

        return cursor.fetchall()

    def get_book(self, book):
        """Get single book by id"""

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book,))

        return cursor.fetchone()

    def get_books(self):
        """Get all available books"""

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM books")

        return cursor.fetchall()

    def match_book(self, keyword):
        """Find book by name"""

        keyword = "%" + keyword + "%"

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM books
            WHERE
             lowercase(title) LIKE lowercase( ? )
             OR lowercase(short) LIKE lowercase( ? )
             OR lowercase(full) LIKE lowercase( ? )
            """, (keyword, keyword, keyword))

        return cursor.fetchall()

    def match_reference(self, keyword):
        """Find bible references by given string"""

        possible = []
        chapter = 1
        verse = 1

        match_c = re.search(r'([0-9]+)$', keyword)
        match_cv = re.search(r'([0-9]+)([\D]{1})([0-9]+)$', keyword)
        match_ce = re.search(r'([0-9]+)([\D]{1})([0-9]+)\-([0-9]+)$', keyword)

        if match_ce:
            chapter = match_ce.group(1)
            verse = match_ce.group(3)
            keyword = re.sub(r'([0-9]+)([\D]{1})([0-9]+)\-([0-9]+)$', '', keyword)
        elif match_cv:
            chapter = match_cv.group(1)
            verse = match_cv.group(3)
            keyword = re.sub(r'([0-9]+)([\D]{1})([0-9]+)$', '', keyword)
        elif match_c:
            chapter = match_c.group(1)
            keyword = re.sub(r'([0-9]+)$', '', keyword)

        books = self.get_books()

        keyword = keyword.lstrip().rstrip()

        for book in books:
            m1 = string_rank(book['title'], keyword)
            m2 = string_rank(book['full'], keyword)
            m3 = string_rank(book['short'], keyword)
            r = (m1 + m2 + m3) / 3

            if r >= 1.1:
                possible.append(["%s %s:%s" % (book['title'], chapter, verse), [book['id'], chapter, verse], r])

        def get_key(item):
            return -item[2]

        return sorted(possible, key=get_key)[0:3]

Bible = BibleModel()


class BibleManager:

    @staticmethod
    def getAll():

        files = glob.glob(get_data_path() + "/bibles/*.db")
        items = []

        for file in files:
            path = os.path.abspath(file)

            items.append({
                'name': os.path.basename(path)[:-3],
                'path': path
                 })

        return items

    @staticmethod
    def set(path):
        Bible.change_bible(path)

    @staticmethod
    def install(path):

        if BibleManager.verify(path):
            copy_file(os.path.normpath(path), os.path.normpath(get_data_path() + '/bibles/' + os.path.basename(path)))

    @staticmethod
    def verify(path):

        if not (os.path.exists(path) and os.path.isfile(path)):
            return False

        try:
            db = lite.connect(path)
            db.row_factory = lite.Row

            cursor = db.cursor()
            cursor.execute("SELECT book, chapter, verse FROM verses")
            cursor.execute("SELECT id, title, full, short FROM books")

            db.close()
        except:
            return False

        return True
