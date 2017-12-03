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

        self.__close_on_focus_lost = True
        self.__background_color = QColor(255, 255, 255)
        # Shadow padding
        self.__padding = 12
        # Caret size
        self.__caret_size = 5
        # Caret position relative to center of dialog
        self.__caret_position = 0
        # Corner roundness
        self.__roundness = 5

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

        self.setContentsMargins(self.__padding, self.__padding, self.__padding, self.__padding + self.__caret_size)

    def paintEvent(self, event):
        """Draw a dialog"""

        width = self.width()
        height = self.height()
        caret_offset = self.__caret_position

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

        points = [QPointF(width / 2 + caret_offset, height - self.__padding),
                  QPointF(width / 2 - self.__caret_size + caret_offset, height - self.__caret_size - self.__padding),
                  QPointF(width / 2 + self.__caret_size + caret_offset, height - self.__caret_size - self.__padding)]
        triangle = QPolygonF(points)

        rounded_rect = QPainterPath()
        rounded_rect.addRoundedRect(self.__padding, self.__padding,
                                    width - self.__padding * 2,
                                    height - self.__caret_size - self.__padding * 2,
                                    self.__roundness, self.__roundness)
        rounded_rect.addPolygon(triangle)

        painter.setOpacity(1)
        painter.fillPath(rounded_rect, QBrush(self.__background_color))

        painter.restore()
        painter.end()

    def eventFilter(self, target, event):
        """Close dialog when focus is lost"""

        if self.__close_on_focus_lost and event.type() == QEvent.WindowDeactivate:
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

        self.__close_on_focus_lost = value

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
            self.__caret_position = -self.width() / 2 + self.__padding + self.__caret_size * 2
        elif location.x() + self.width() >= screen.x() + screen.width():
            location.setX(screen.x() + screen.width() - self.width())
            self.__caret_position = self.width() / 2 - self.__padding - self.__caret_size * 2
        else:
            self.__caret_position = 0

        self.move(location.x(), location.y())

    def setBackgroundColor(self, color):
        """Set a color of whole dialog

        Args:
            color (QColor): background color of widget
        """

        self.__background_color = color
