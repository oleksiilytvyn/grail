# -*- coding: UTF-8 -*-
"""
    grail.ui.panel
    ~~~~~~~~~~~~~~

    Panels and panel manager
"""

from grailkit.qt import Component, Application


class Panel(Component):

    def __init__(self):
        super(Panel, self).__init__()

        self.__app = Application.instance()

    def __ui__(self):
        pass

    def emit(self, message, *args):
        """Emit signal globally"""

        self.__app.emit(message, *args)

    def connect(self, message, fn):

        self.__app.connect(message, fn)
