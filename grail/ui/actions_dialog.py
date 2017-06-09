# -*- coding: UTF-8 -*-
"""
    grail.ui.actions_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~

    Actions dialog

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.qt import Dialog, VLayout, List, ListItem, Label, Application, Toolbar


class ActionsDialog(Dialog):

    def __init__(self, parent=None):
        super(ActionsDialog, self).__init__(parent)

        self.app = Application.instance()
        self.app.signals.connect('/app/close', self.close)
        self.app.signals.connect('/app/actions', self._update)

        self.__ui__()
        self._update()

    def __ui__(self):

        self._ui_list = List()
        self._ui_list.itemDoubleClicked.connect(self.go_action)

        self._ui_label = Label("0 Actions")
        self._ui_label.setAlignment(Qt.AlignCenter)
        self._ui_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_go_action = QAction(QIcon(':/icons/play.png'), "Execute", self)
        self._ui_go_action.setIconVisibleInMenu(True)
        self._ui_go_action.triggered.connect(self.go_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.addWidget(self._ui_label)
        self._ui_toolbar.addAction(self._ui_go_action)

        self._ui_layout = VLayout()
        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)
        self.setWindowTitle("Actions")
        self.setGeometry(0, 0, 300, 400)
        self.setMinimumSize(200, 200)
        self.moveCenter()

    def _update(self):

        self._ui_list.clear()

        actions = Application.instance().actions()

        for action in actions:
            item = ListItem("%s → %s" % (action.plugin.name, action.name))
            item.action = action

            self._ui_list.addItem(item)

        self._ui_label.setText("%d Actions" % len(actions))

    def go_action(self):
        """Execute selected action"""

        items = self._ui_list.selectedItems()

        if len(items) > 0:
            action = items[0].action
            action()
