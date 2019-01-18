# -*- coding: UTF-8 -*-
"""
    grail.core.osc_host
    ~~~~~~~~~~~~~~~~~~~

    Host in/out OSC connections

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
import socketserver

from PyQt5.QtCore import QThread, pyqtSignal

from grailkit.osc import *


class OSCHost:
    """Wrapper for OSC client and server"""

    def __init__(self):
        """Take care of OSC in/out"""

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


class _OSCServer:
    """Handle incoming messages"""

    def __init__(self):
        self._clients = []
        self._ports = {}

    @property
    def clients(self):
        """Returns list of clients"""

        return self._clients

    def clear(self):
        """Clear list of clients"""

        self._clients = []
        self._ports = {}

    def add(self, address, port):
        """Add client to listen from

        Args:
            address (str): ip address
            port (int): port
        """

        self._clients.append((address, port))

        if port not in self._ports:
            thread = _ListenerThread(port, self)
            thread.received.connect(self.handle)
            thread.start()

            self._ports[port] = thread

    def remove(self, address, port):
        """Remove client from list"""

        port_used = 0

        for client in self._clients:
            if client[1] == port:
                port_used += 1

        for client in self._clients:
            if client[0] == address and client[1] == port:
                self._clients.remove(client)

                if port_used == 1:
                    self._ports[port].terminate()
                    del self._ports[port]

                break

    def handle(self, address, message, date):
        """Handle incoming osc messages"""

        # todo: pipe it to application
        print("OSC received from %s:%d by %s" % (address[0], address[1], self), date, message.address, *message.args)


class _OSCListener(OSCServer, socketserver.ThreadingMixIn):
    """Listen for incoming OSC messages on certain port"""

    def __init__(self, port, parent):
        super(_OSCListener, self).__init__('0.0.0.0', port)

        self._parent = parent

    def handle(self, address, message, date):
        """Handle incoming message"""

        self._parent.handle(address, message, date)


class _ListenerThread(QThread):
    """Qt thread with OSCServer"""

    received = pyqtSignal(object, object, object)

    def __init__(self, port, parent):
        super(_ListenerThread, self).__init__()

        self.listener = None
        self.parent = parent

        try:
            self.listener = _OSCListener(port, self)
        except OSError:
            self.terminate()

    def handle(self, address, message, date):
        """Pass message to parent thread"""

        self.received.emit(address, message, date)

    def run(self):
        """Run listener"""

        if self.listener:
            self.listener.serve_forever()


class _OSCClient(OSCClient):
    """Send OSC messages to multiple hosts"""

    def __init__(self):
        super(_OSCClient, self).__init__()
