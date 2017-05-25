# -*- coding: UTF-8 -*-
"""
    grail.plugins.display_plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    2d graphics display

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import math

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.util import OS_MAC
from grailkit.qt import Frameless, Dialog, VLayout, Spacer

from grail.core import Plugin


class DisplayPlugin(Plugin):
    """Plugin for displaying cues"""

    id = 'display'
    name = 'Display'
    author = 'Grail Team'
    description = 'Display 2d graphics in window or in fullscreen mode'

    def __init__(self):
        super(DisplayPlugin, self).__init__()

        self.register_menu("Display->Disable", self.disable_action,
                           shortcut="Ctrl+D",
                           checkable=True,
                           checked=True)
        self.register_menu('Display->---')
        self.register_menu("Display->Show Test Card", self.testcard_action,
                           shortcut="Ctrl+Shift+T",
                           checkable=True)
        self.register_menu("Display->Advanced...", self.preferences_action,
                           shortcut="Ctrl+Shift+A")

        self.connect('/app/close', self.close)

        self.window = DisplayWindow()
        self.preferences_dialog = PreferencesDialog()

        desktop = QApplication.desktop()
        desktop.resized.connect(self._screens_changed)
        desktop.screenCountChanged.connect(self._screens_changed)
        desktop.workAreaResized.connect(self._screens_changed)

    def testcard_action(self, action):
        """Show or hide test card"""

        self.window.setTestCard(action.isChecked())

    def preferences_action(self, action):
        """Show display preferences dialog"""

        self.preferences_dialog.show()
        self.preferences_dialog.raise_()

    def disable_action(self, action):
        """Disable display output"""

        if action.isChecked():
            self.window.close()
        else:
            self.window.show()

    def close(self):
        """Close display on application exit"""

        self.window.close()

    def _screens_changed(self):
        """Display configuration changed"""

        self.window.close()


class DisplayWindow(Frameless):
    """Window that displays 2d graphics"""

    def __init__(self, parent=None):
        super(DisplayWindow, self).__init__(parent)

        self._position = QPoint(0, 0)
        self._display_test = False

        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)
        self.setWindowTitle("Display")
        self.setWindowFlags((Qt.Dialog if OS_MAC else Qt.Tool) |
                            Qt.FramelessWindowHint |
                            Qt.WindowSystemMenuHint |
                            Qt.WindowStaysOnTopHint)
        self.moveCenter()

    def paintEvent(self, event):
        """Draw image"""

        output = event.rect()

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        painter.fillRect(output, Qt.black)

        if self._display_test:
            painter.drawPixmap(output, self._generate_testcard(output.width(), output.height()))

        painter.end()

    def hideEvent(self, event):

        event.ignore()

    def mousePressEvent(self, event):

        self._position = event.globalPos()

    def mouseMoveEvent(self, event):

        delta = QPoint(event.globalPos() - self._position)

        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._position = event.globalPos()

    def setTestCard(self, flag):
        """Show test card or not"""

        self._display_test = flag
        self.update()

    @classmethod
    def _generate_testcard(cls, width, height):
        """Generate test card QPixmap"""

        comp = QRect(0, 0, width, height)
        image = QPixmap(comp.width(), comp.height())
        offset = 50

        painter = QPainter()
        painter.begin(image)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        painter.fillRect(comp, QColor("#7f7f7f"))

        pen = QPen(Qt.white)
        pen.setWidth(1)

        painter.setPen(pen)
        lines = math.ceil(max(comp.width(), comp.height()) / offset)

        for index in range(-lines, lines):
            o = index * offset

            painter.drawLine(0, comp.height() / 2 + o, comp.width(), comp.height() / 2 + o)
            painter.drawLine(comp.width() / 2 + o, 0, comp.width() / 2 + o, comp.height())

        pen = QPen(QColor("#222222"))
        pen.setWidth(3)
        painter.setPen(pen)

        painter.drawLine(0, comp.height() / 2, comp.width(), comp.height() / 2)
        painter.drawLine(comp.width() / 2, 0, comp.width() / 2, comp.height())

        pen.setWidth(5)
        painter.setPen(pen)

        radius = min(comp.height(), comp.width()) / 2
        circles = math.ceil((comp.width() / radius) / 2) + 1

        for index in range(-circles, circles + 1):
            ox = index * (radius * 1.25)

            painter.drawEllipse(QPoint(comp.width() / 2 + ox, comp.height() / 2), radius, radius)

        box = QRect(comp.topLeft(), comp.bottomRight())
        box.adjust(10, 10, -10, -10)

        painter.setPen(Qt.white)
        painter.setFont(QFont("decorative", 24))
        painter.drawText(box, Qt.AlignCenter | Qt.TextWordWrap,
                         "composition size %d x %d" % (comp.width(), comp.height()))

        painter.end()

        return image


class PreferencesDialog(Dialog):

    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)

        self.__ui__()

    def __ui__(self):
        """Build UI"""

        self._ui_toolbar = QToolBar()

        self._ui_layout = VLayout()
        self._ui_layout.addWidget(Spacer())
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)
        self.setWindowTitle("Display preferences")
        self.setGeometry(100, 100, 480, 360)
        self.setMinimumSize(300, 200)
        self.moveCenter()
