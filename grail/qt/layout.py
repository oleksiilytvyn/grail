# -*- coding: UTF-8 -*-
"""
    grailkit.qt.layout
    ~~~~~~~~~~~~~~~~~~

    Layouts

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout


class HLayout(QHBoxLayout):
    """Horizontal layout"""

    def __init__(self, parent=None):
        super(HLayout, self).__init__(parent)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)


class VLayout(QVBoxLayout):
    """Vertical layout"""

    def __init__(self, parent=None):
        super(VLayout, self).__init__(parent)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)


class GridLayout(QGridLayout):
    """Grid layout"""

    def __init__(self, parent=None):
        super(GridLayout, self).__init__(parent)
