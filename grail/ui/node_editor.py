# -*- coding: UTF-8 -*-
"""
    grail.ui.node_editor
    ~~~~~~~~~~~~~~~~~~~~

    Simple grail file node editor
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.ui import GWidget, GListWidget, GListItem

from grail.ui import Panel


class NodeEditor(Panel):

    def __init__(self, app):
        super(NodeEditor, self).__init__()

        self.connect('/property/changed', self._update)

        self.app = app

        self.__ui__()
        self._update()

    def __ui__(self):

        self._ui_list = GListWidget()
        self._ui_list.itemSelectionChanged.connect(self._node_selected_event)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add node', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_remove_action = QAction(QIcon(':/icons/remove-white.png'), 'Remove node', self)
        self._ui_remove_action.setIconVisibleInMenu(True)
        self._ui_remove_action.triggered.connect(self.remove_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("node_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_add_action)
        self._ui_toolbar.addWidget(spacer)
        self._ui_toolbar.addAction(self._ui_remove_action)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_layout.setSpacing(0)

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def _update(self):

        self._ui_list.clear()

        for entity in self.app.project.entities():
            item = GListItem("%d - %s" % (entity.id, entity.name))
            item.id = entity.id

            self._ui_list.addItem(item)

    def _node_selected_event(self):

        items = self._ui_list.selectedItems()

        if len(items) > 0:
            self.emit('/node/selected', items[0].id)

    def add_action(self):

        self.app.project.create("Untitled item")
        self.update_list()
        self._ui_list.setCurrentRow(self._ui_list.count() - 1)
        self.emit('/node/selected', self._ui_list.item(self._ui_list.count() - 1).id)

    def remove_action(self):

        item = self._ui_list.currentItem()

        if item:
            self.app.project.remove(item.id)

        self.update_list()
        self._ui_list.setCurrentRow(0)
        self.emit('/node/selected', self._ui_list.item(0).id)
