# -*- coding: UTF-8 -*-
"""
    grail.ui.panel
    ~~~~~~~~~~~~~~

    Panels and panel manager
"""

from grailkit.ui import GWidget
from grailkit.ui.gapplication import AppInstance


class Panel(GWidget):

    def __init__(self):
        super(Panel, self).__init__()

        self.__app = AppInstance()

    def __ui__(self):
        pass

    def emit(self, message, *args):
        """Emit signal globally"""

        print(self, message, *args)

        self.__app.emit(message, *args)

    def connect(self, message, fn):

        self.__app.connect(message, fn)