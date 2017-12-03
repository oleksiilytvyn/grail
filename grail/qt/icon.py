# -*- coding: UTF-8 -*-
"""
    grail.qt.icon
    ~~~~~~~~~~~~~

    QIcon with color changing capabilities

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor


class Icon(QIcon):
    """Pixmap/vector icon"""

    def __init__(self, path=None):
        super(Icon, self).__init__(path)

    def coloredPixmap(self, width, height, color, original_color=QColor('black')):
        """Create a pixmap from original icon, changing `original_color` color to given color

        Args:
            width (int): width of pixmap
            height (int): height of pixmap
            color (QColor): color of icon
            original_color (QColor): new color
        Returns:
            QPixmap of icon
        """

        pixmap = self.pixmap(width, height)
        mask = pixmap.createMaskFromColor(original_color, Qt.MaskOutColor)
        pixmap.fill(color)
        pixmap.setMask(mask)

        return pixmap

    def addColoredPixmap(self, width=128, height=128, color=QColor("#000"), mode=QIcon.Normal, state=QIcon.On):
        """Add a pixmap with given color

        Args:
            width (int): width of added pixmap
            height (int): height of added pixmap
            color (QColor): color of icon
            mode: QIcon mode
            state: QIcon state
        """

        self.addPixmap(self.coloredPixmap(width, height, color), mode, state)

    @staticmethod
    def colored(path, color, original_color=QColor('black')):

        icon = Icon(path)
        size = icon.availableSizes()[0]
        width = size.width()
        height = size.height()

        return QIcon(icon.coloredPixmap(width, height, color, original_color))
