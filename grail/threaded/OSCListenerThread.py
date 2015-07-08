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

from pythonosc import osc_message_builder, udp_client, dispatcher, osc_server
from PyQt5.QtCore import *


class OSCListenerThread(QThread):
    """
    Listen for incoming OSC messages
    """

    recieved = pyqtSignal( object, object)

    def __init__( self, host, port ):
        super(OSCListenerThread, self).__init__()

        self.host = host
        self.port = port

        self.mapper = dispatcher.Dispatcher()
        self.mapper.set_default_handler( self.messageRecieved )

    def run( self ):
        server = osc_server.ThreadingOSCUDPServer((self.host, self.port), self.mapper)
        server.serve_forever()

    def messageRecieved( self, pattern, value ):
        self.recieved.emit( pattern, value )
