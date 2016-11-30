# -*- coding: UTF-8 -*-
"""
    grail.ui.cuelist_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~

    Bubble dialog with list of cuelists
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.ui import GBalloonDialog, GSpacer, GListWidget, GListItem
from grailkit.ui.gapplication import AppInstance


class CuelistDialog(GBalloonDialog):

    def __init__(self):
        super(CuelistDialog, self).__init__()

        self.__ui__()
        self.update_list()

    def __ui__(self):

        self.setBackgroundColor(QColor(75, 80, 86))
        self.setObjectName('cuelist_dialog')

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_list = CuelistsListWidget()

        self._ui_edit_action = QAction(QIcon(':/icons/edit.png'), 'Edit', self)
        self._ui_edit_action.triggered.connect(self.edit_action)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.setObjectName("cuelist_dialog_toolbar")
        self._ui_toolbar.addAction(self._ui_edit_action)
        self._ui_toolbar.addWidget(GSpacer())
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)
        self.setWindowTitle('Cuelists')
        self.setGeometry(100, 300, 240, 300)
        self.setMinimumSize(240, 300)

    def update_list(self):

        app = AppInstance()
        cuelists = app.project.cuelists()
        x = 0

        self._ui_list.setRowCount(len(cuelists))

        for cuelist in cuelists:
            item = CuelistsListItem(cuelist.name)
            self._ui_list.setItem(x, 0, item)

            #if int(playlist['id']) == id:
            #    self.ui_list.setCurrentItem(item)
            #    self._list_item_clicked(item)
            #    self.ui_list.scrollToItem(self.ui_list.item(x, 0))

            button = CuelistsListButton(self)
            #button.triggered.connect(self._list_remove_clicked)

            self._ui_list.setCellWidget(x, 1, button)

            x += 1

    def edit_action(self):
        pass

    def add_action(self):
        pass


class CuelistsListItem(QTableWidgetItem):
    """Playlist item inside playlist dialog"""

    def __init__(self, title):
        super(CuelistsListItem, self).__init__(title)

        self.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)


class CuelistsListButton(QToolButton):

    def __init__(self, parent):
        super(CuelistsListButton, self).__init__(parent)

        self.setMinimumSize(16, 16)
        self.setStyleSheet("QToolButton {background: transparent;border: none;padding: 0;margin: 0;}")


class CuelistsListWidget(QTableWidget):

    def __init__(self, parent=None):
        """Initialize PlaylistTableWidget"""

        super(CuelistsListWidget, self).__init__(parent)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAutoScroll(False)

        self.setColumnCount(2)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(["Label", "Button"])
        self.setShowGrid(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)

        self.setColumnWidth(1, 42)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        original = self.verticalScrollBar()

        self._scrollbar = QScrollBar(Qt.Vertical, self)
        self._scrollbar.valueChanged.connect(original.setValue)
        self._scrollbar.rangeChanged.connect(self.scroll_to_selected)

        original.valueChanged.connect(self._scrollbar.setValue)

        self._update_scrollbar()

    def paintEvent(self, event):
        """Draw widget"""

        QTableWidget.paintEvent(self, event)

        self._update_scrollbar()

    def update(self, **kwargs):
        """Update ui components
        :param **kwargs:
        """

        super(CuelistsListWidget, self).update()

        self._update_scrollbar()

    def _update_scrollbar(self):
        """Update scrollbar to draw properly"""

        original = self.verticalScrollBar()

        if not hasattr(self, 'scrollbar'):
            return

        if original.value() == original.maximum() and original.value() == 0:
            self._scrollbar.hide()
        else:
            self._scrollbar.show()

        self._scrollbar.setPageStep(original.pageStep())
        self._scrollbar.setRange(original.minimum(), original.maximum())
        self._scrollbar.resize(8, self.rect().height())
        self._scrollbar.move(self.rect().width() - 8, 0)

    def scroll_to_selected(self):
        """Scroll to selected item"""

        selected = self.selectedIndexes()

        if len(selected) == 0:
            x = 0
            self.setCurrentCell(x, 0)
        else:
            x = selected[0].row()

        self.scrollToItem(self.item(x, 0))
