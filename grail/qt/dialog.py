# -*- coding: UTF-8 -*-
"""
    grail.qt.dialog
    ~~~~~~~~~~~~~~~

    Base class for all Grail UI dialogs

    :copyright: (c) 2018 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QDesktopWidget

from grail.qt import Component


class Dialog(QDialog, Component):
    """Abstract dialog window"""

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        # Set default window icon, used on Windows and some Linux distributions
        self.setWindowIcon(QIcon(':/icon/32.png'))

    def moveCenter(self):
        """Move window to the center of current screen"""

        geometry = self.frameGeometry()
        geometry.moveCenter(QDesktopWidget().availableGeometry().center())

        self.move(geometry.topLeft())

    def showWindow(self):
        """Raise dialog in any way"""

        self.show()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
