# -*- coding: UTF-8 -*-
"""
    grail.qt.table
    ~~~~~~~~~~~~~~

    Table widget

    :copyright: (c) 2018 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


class Table(QTableWidget):
    """Table widget"""

    def __init__(self, parent=None):
        super(Table, self).__init__(parent)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._scrollbar_original = self.verticalScrollBar()
        self._scrollbar = QScrollBar(Qt.Vertical, self)
        self._scrollbar.valueChanged.connect(self._scrollbar_original.setValue)
        self._scrollbar_original.valueChanged.connect(self._scrollbar.setValue)

        self._update_scrollbar()

    def _update_scrollbar(self):
        """Update a custom scrollbar"""

        original = self._scrollbar_original

        if original.value() == original.maximum() and original.value() == 0:
            self._scrollbar.hide()
        else:
            self._scrollbar.show()

        self._scrollbar.setPageStep(original.pageStep())
        self._scrollbar.setRange(original.minimum(), original.maximum())
        self._scrollbar.resize(8, self.rect().height())
        self._scrollbar.move(self.rect().width() - 8, 0)

    def paintEvent(self, event):
        """Redraw a widget"""

        QTableWidget.paintEvent(self, event)

        self._update_scrollbar()


class TableItem(QTableWidgetItem):
    """Table item"""

    def __init__(self, *args):
        super(TableItem, self).__init__(*args)
