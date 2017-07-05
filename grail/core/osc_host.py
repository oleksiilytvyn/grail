# -*- coding: UTF-8 -*-
"""
    grail.core.osc_host
    ~~~~~~~~~~~~~~~~~~~

    Host in/out OSC connections
"""
import socketserver

from grailkit.osc import *


class OSCHost:

    def __init__(self):
        """"""

        self._client = _OSCClient()
        self._server = _OSCServer()

    @property
    def input(self):
        """Returns OSC input"""

        return self._server

    @property
    def output(self):
        """Returns OSC output"""

        return self._client


class _OSCServer(OSCServer, socketserver.ThreadingMixIn):
    """Handle incoming messages"""

    def __init__(self):
        super(_OSCServer, self).__init__()

    def handle(self, address, message, date):
        pass


class _OSCClient(OSCClient):

    def __init__(self):
        super(_OSCClient, self).__init__()
