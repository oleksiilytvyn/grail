# -*- coding: UTF-8 -*-
"""
    grailkit.qt.list
    ~~~~~~~~~~~~~~~~

    Simple list widget

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollBar, QListWidget, QListWidgetItem, QAbstractItemView

from grail.qt import Component


class List(QListWidget, Component):
    """Simple list widget"""

    def __init__(self, parent=None):
        super(List, self).__init__(parent)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        # Fix items overlapping issue
        self.setStyleSheet("QListWidget::item {padding: 4px 12px;}")

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

        QListWidget.paintEvent(self, event)

        self._update_scrollbar()


class ListItem(QListWidgetItem):
    """List item"""

    def __init__(self, parent=None):
        super(ListItem, self).__init__(parent)

        self._data = None

    def setObject(self, data):
        """Set associated data object

        Args:
            data (object): any object
        """

        self._data = data

    def object(self):
        """Returns associated data object"""

        return self._data
