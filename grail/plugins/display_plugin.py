# -*- coding: UTF-8 -*-
"""
    grail.plugins.display_plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    2d display

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.qt import Dialog, Button

from grail.core import Plugin


class DisplayPlugin(Plugin):
    """Plugin for displaying cues"""

    id = 'display'
    # Unique plugin name string
    name = 'Display'
    # Plugin author string
    author = 'Grail Team'
    # Plugin description string
    description = 'Display 2d graphics in window or in fullscreen mode'

    def __init__(self):
        super(DisplayPlugin, self).__init__()

        self.register_menu("Display->Disable", self.disable_action)
        self.register_menu('Display->---', None)
        self.register_menu("Display->Show Test Card", self.testcard_action)
        self.register_menu("Display->Preferences", self.preferences_action)

        # self.window = DisplayWindow()
        # self.window.show()

    def testcard_action(self):
        pass

    def preferences_action(self):
        pass

    def disable_action(self):
        pass


class DisplayWindow(Dialog):

    def __init__(self, parent=None):
        super(DisplayWindow, self).__init__(parent)

        widget = Button('Hello world')

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)

        self.setLayout(layout)

        self.setGeometry(100, 100, 380, 460)
        self.setFixedSize(380, 460)
        self.setWindowTitle("Welcome to Grail")
        self.moveCenter()
