# -*- coding: UTF-8 -*-
"""
    grail.ui.node_editor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Simple grail file node editor
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.ui import GWidget, GListWidget, GListItem


class NodeEditor(GWidget):

    nodeSelected = pyqtSignal(int)

    def __init__(self, app):
        super(NodeEditor, self).__init__()

        self.app = app

        self.__ui__()
        self._update()

    def __ui__(self):

        self._ui_list = GListWidget()
        self._ui_list.itemClicked.connect(self._node_selected_event)

        self._ui_add_action = QAction(QIcon(':/icon/32.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("node_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_add_action)
        self._ui_toolbar.addWidget(spacer)

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

    def _node_selected_event(self, item):

        self.nodeSelected.emit(item.id)

    def add_action(self):
        pass
