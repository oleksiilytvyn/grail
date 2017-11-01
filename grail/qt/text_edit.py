# -*- coding: UTF-8 -*-
"""
    grailkit.qt.text_edit
    ~~~~~~~~~~~~~~~~~~~~~

    
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextEdit

from grail.qt import Component


class TextEdit(QTextEdit, Component):

    def __init__(self, *args):
        super(TextEdit, self).__init__(*args)
