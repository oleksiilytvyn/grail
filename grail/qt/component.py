# -*- coding: UTF-8 -*-
"""
    grail.qt.component
    ~~~~~~~~~~~~~~~~~~

    Base widget for all Grail Qt components

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtWidgets import QWidget


class Component(QWidget):
    """Base widget"""

    def className(self):
        """
        Returns widget name that used in stylesheet.

        stylesheet example:
            Dialog {
                background: red;
            }
        """

        return type(self).__name__
