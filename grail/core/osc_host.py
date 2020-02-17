# -*- coding: UTF-8 -*-
"""
    grail.core.osc_host
    ~~~~~~~~~~~~~~~~~~~

    Host in/out OSC connections

    :copyright: (c) 2016-2020 by Oleksii Lytvyn (http://alexlitvin.name)
    :license: GNU, see LICENSE for more details.
"""
import logging
import socketserver

from grail.qt import QtCore, QtSignal

from grailkit.osc import *


class OSCHost:
    """Wrapper for OSC client and server"""

    def __init__(self, application):
        """Take care of OSC in/out"""

        self._app = application
        self._client = _OSCClient(self._app)
        self._server = _OSCServer(self._app)

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

    def __init__(self, application):

        self._clients = []
        self._ports = {}
        self._app = application

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
            thread = _ListenerThread(address, port, self)
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

        logging.info("OSC received from %s:%d by %s" % (address[0], address[1], self))

        signals = self._app.signals

        # forward messages to application
        if isinstance(message, OSCBundle):
            for item in message:
                signals.emit(item.address, *item.args)
        else:
            # pass single message signal
            signals.emit(message.address, *message.args)

            # fix: accept old style messages
            if message.address == "/grail/message":
                signals.emit("/clip/text/source", str(message.args[0], "utf-8"))


class _OSCListener(OSCServer, socketserver.ThreadingMixIn):
    """Listen for incoming OSC messages on certain port"""

    def __init__(self, host, port, parent):
        super(_OSCListener, self).__init__(host, port)

        self._parent = parent

    def handle(self, address, message, date):
        """Handle incoming message"""

        self._parent.handle(address, message, date)


class _ListenerThread(QtCore.QThread):
    """Qt thread with OSCServer"""

    received = QtSignal(object, object, object)

    def __init__(self, host, port, parent: object):
        super(_ListenerThread, self).__init__()

        self.listener = None
        self.parent = parent

        try:
            self.listener = _OSCListener(host, port, self)
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

    def __init__(self, application):
        super(_OSCClient, self).__init__()

        self._app = application
