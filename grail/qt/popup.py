# -*- coding: UTF-8 -*-
"""
    grail.qt.balloon_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~

    Floating dialog with pointer and without title bar

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""

from PyQt5.QtCore import Qt, QPoint, QPointF, QSize, QEvent, QObject
from PyQt5.QtGui import QPolygonF, QColor, QPainter, QPainterPath, QBrush
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QDesktopWidget

from grail.qt import Dialog
from grailkit.util import OS_MAC


class Popup(Dialog):
    """Dialog without title bar and frame, but with rounded corners and pointing triangle"""

    def __init__(self, parent=None):
        super(Popup, self).__init__(parent)

        self._close_on_focus_lost = True
        self._background_color = QColor(255, 255, 255)
        # Shadow padding
        self._padding = 12
        # Caret size
        self._caret_size = 5
        # Caret position relative to center of dialog
        self._caret_position = 0
        # Corner roundness
        self._roundness = 5

        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.autoFillBackground = True

        self.installEventFilter(self)

        if not OS_MAC:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(12)
            effect.setColor(QColor(0, 0, 0, 126))
            effect.setOffset(0)

            self.setGraphicsEffect(effect)

        self.setContentsMargins(self._padding, self._padding, self._padding, self._padding + self._caret_size)

    def paintEvent(self, event):
        """Draw a dialog"""

        painter = QPainter()
        painter.begin(self)
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # Clear previous drawing
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 0, 0, 127))

        points = [QPointF(self.width() / 2 + self._caret_position,
                          self.height() - self._padding),
                  QPointF(self.width() / 2 - self._caret_size + self._caret_position,
                          self.height() - self._caret_size - self._padding),
                  QPointF(self.width() / 2 + self._caret_size + self._caret_position,
                          self.height() - self._caret_size - self._padding)]
        triangle = QPolygonF(points)

        rounded_rect = QPainterPath()
        rounded_rect.addRoundedRect(self._padding, self._padding,
                                    self.width() - self._padding * 2,
                                    self.height() - self._caret_size - self._padding * 2,
                                    self._roundness, self._roundness)
        rounded_rect.addPolygon(triangle)

        painter.setOpacity(1)
        painter.fillPath(rounded_rect, QBrush(self._background_color))

        painter.restore()
        painter.end()

    def eventFilter(self, target, event):
        """Close dialog when focus is lost"""

        if self._close_on_focus_lost and event.type() == QEvent.WindowDeactivate:
            self.hide()

        return QObject.eventFilter(self, target, event)

    def sizeHint(self):
        """Default minimum size"""

        return QSize(300, 300)

    def closeOnFocusLost(self, value):
        """Close dialog when it looses focus

        Args:
            value (bool): close this dialog when it looses focus or not
        """

        self._close_on_focus_lost = value

    def showAt(self, point):
        """Show dialog tip at given point

        Args:
            point (QPoint): point to show at
        """

        self.show()
        self.raise_()

        desktop = QDesktopWidget()
        screen = desktop.screenGeometry(point)
        location = QPoint(point.x() - self.width() / 2, point.y() - self.height() + 12)

        # calculate point location inside current screen
        if location.x() <= screen.x():
            location.setX(screen.x())
            self._caret_position = -self.width() / 2 + self._padding + self._caret_size * 2
        elif location.x() + self.width() >= screen.x() + screen.width():
            location.setX(screen.x() + screen.width() - self.width())
            self._caret_position = self.width() / 2 - self._padding - self._caret_size * 2
        else:
            self._caret_position = 0

        self.move(location.x(), location.y())

    def setBackgroundColor(self, color):
        """Set a color of whole dialog

        Args:
            color (QColor): background color of widget
        """

        self._background_color = color
