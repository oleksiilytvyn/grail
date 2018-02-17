# -*- coding: UTF-8 -*-
"""
    grail.qt.toolbar
    ~~~~~~~~~~~~~~~~

    Toolbar component

    :copyright: (c) 2018 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QStyleOption, QStyle, QToolBar

from grail.qt import Spacer, Component


class Toolbar(QToolBar, Component):
    """Toolbar component"""

    def __init__(self, parent=None):
        super(Toolbar, self).__init__(parent)

        self.setMaximumHeight(36)
        self.setMinimumHeight(36)
        self.setIconSize(QSize(16, 16))

    def addStretch(self):
        """Add space stretch"""

        self.addWidget(Spacer())

    def paintEvent(self, event):
        """Paint component with CSS styles"""

        option = QStyleOption()
        option.initFrom(self)

        painter = QPainter(self)

        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)
