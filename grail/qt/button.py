# -*- coding: UTF-8 -*-
"""
    grail.qt.button
    ~~~~~~~~~~~~~~~

    Button component

    :copyright: (c) 2018 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""

from PyQt5.QtWidgets import QPushButton

from grail.qt import Component


class Button(QPushButton, Component):
    """Basic button widget"""

    def __init__(self, *args):
        super(Button, self).__init__(*args)
