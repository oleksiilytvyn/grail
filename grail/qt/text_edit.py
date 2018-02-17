# -*- coding: UTF-8 -*-
"""
    grail.qt.text_edit
    ~~~~~~~~~~~~~~~~~~

    Simple text edit widget

    :copyright: (c) 2018 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtWidgets import QTextEdit

from grail.qt import Component


class TextEdit(QTextEdit, Component):
    """Multi-line text editor"""

    def __init__(self, *args):
        super(TextEdit, self).__init__(*args)
