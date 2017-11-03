# -*- coding: UTF-8 -*-
"""
    grail.qt.label
    ~~~~~~~~~~~~~~

    Text label component

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtWidgets import QLabel
from grail.qt import Component


class Label(QLabel, Component):
    """Text label component"""

    def __init__(self, *args):
        super(Label, self).__init__(*args)
