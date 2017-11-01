# -*- coding: UTF-8 -*-
"""
    grailkit.qt.frameless
    ~~~~~~~~~~~~~~~~~~~~~

    Frameless dialog implementation

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import Qt

from grail.qt import Dialog
from grailkit.util import OS_MAC


class Frameless(Dialog):
    """Frameless dialog that stays on top and doesn't shown in menu bar"""

    def __init__(self, parent=None):
        super(Frameless, self).__init__(parent)

        # set window flags
        self.setWindowFlags((Qt.Dialog if OS_MAC else Qt.Tool) |
                            Qt.FramelessWindowHint |
                            Qt.WindowSystemMenuHint |
                            Qt.WindowStaysOnTopHint)
