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
import os


class ConnectionManager:
    """
    Manage SQlite connections
    """

    __list__ = {}

    def __init__( self ):
        pass

    def get( self, path ):

        if path in self.__list__:
            connection = self.__list__[ path ]
        else:
            directory = os.path.dirname(os.path.realpath( path ))

            if not os.path.exists(directory):
                os.makedirs(directory)

            if not os.path.isfile( path ):
                open( path, 'w+' )

            connection = lite.connect( path )
            connection.row_factory = lite.Row

            def lowercase( char ):
                return char.lower()

            def searchprep( char ):
                char = re.sub(r'[\[\_\]\.\-\,\!\(\)\"\'\:\;]', '', char)

                return char.lower()

            connection.create_function("lowercase", 1, lowercase)
            connection.create_function("searchprep", 1, searchprep)

            self.__list__[ path ] = connection

        return connection

    def closeAll( self ):

        for key in self.__list__:
            connection = self.__list__[ key ]

            connection.commit()
            connection.close()

ConnectionManager = ConnectionManager()
