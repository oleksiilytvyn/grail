# -*- coding: UTF-8 -*-
"""
    grail.qt.tree
    ~~~~~~~~~~~~~

    TreeWidget and TreeItem

    :copyright: (c) 2018 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView, QScrollBar


class Tree(QTreeWidget):
    """Tree widget with predefined properties"""

    def __init__(self, parent=None):
        super(Tree, self).__init__(parent)

        self.setAlternatingRowColors(True)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.header().close()
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setWordWrap(True)
        self.setAnimated(False)
        self.setSortingEnabled(False)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
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

        QTreeWidget.paintEvent(self, event)

        self._update_scrollbar()


class TreeItem(QTreeWidgetItem):
    """Representation of node as QTreeWidgetItem"""

    def __init__(self, data=None):
        super(TreeItem, self).__init__()

        self._data = data

    def object(self):
        """Returns associated object"""

        return self._data

    def setObject(self, data):
        """Set associated object"""

        self._data = data
