# -*- coding: UTF-8 -*-
"""
    grailkit.qt.switch
    ~~~~~~~~~~~~~~~~~~

    Simple two state switch component

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.qt import Component


class Switch(QAbstractButton, Component):
    """Simple two state switch widget"""

    changed = pyqtSignal(bool)

    def __init__(self, parent=None, state=True):

        super(Switch, self).__init__(parent)

        self._state = state
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

    def paintEvent(self, event):
        """Draw a widget"""

        width = self.size().width()
        height = self.size().height()

        on_color = QColor("#4bda64")
        off_color = QColor("#fe3a2e")
        switch_color = QColor('#fff')
        roundness = 10

        p = QPainter()
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(QRectF(1, 1, width - 2, height - 2), roundness, roundness)

        flag_path = QPainterPath()

        pen_color = QColor()
        pen_color.setNamedColor("#444444")

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(pen_color)
        p.setPen(pen)

        switch_size = height - 6
        switch_roundness = switch_size / 2

        if self._state:
            p.fillPath(path, on_color)
            flag_path.addRoundedRect(QRectF(width - switch_size - 3, 3, switch_size, switch_size),
                                     switch_roundness, switch_roundness)
        else:
            p.fillPath(path, off_color)
            flag_path.addRoundedRect(QRectF(3, 3, switch_size, switch_size),
                                     switch_roundness, switch_roundness)

        p.drawPath(path)

        color = QColor('#000')
        color.setAlphaF(0.2)

        pen.setColor(color)
        p.setPen(pen)

        p.fillPath(flag_path, switch_color)
        p.drawPath(flag_path)

        p.end()

    def mousePressEvent(self, event):
        """React to mouse click"""

        self._state = not self._state
        self.changed.emit(self._state)

    def sizeHint(self):
        """Resize rule"""

        return QSize(52, 24)

    def setValue(self, flag):
        """Set state of switch"""

        self._state = bool(flag)

    def value(self):
        """Get state of switch"""

        return self._state
