# -*- coding: UTF-8 -*-
"""
    grail.ui.actions_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~

    Actions dialog

    :copyright: (c) 2018 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.qt import Dialog, VLayout, List, ListItem, Label, Application, Toolbar, SearchEdit


class ActionsDialog(Dialog):
    """Display actions registered by plugins"""

    def __init__(self, parent=None):
        super(ActionsDialog, self).__init__(parent)

        self._keyword = ""

        self.app = Application.instance()
        self.app.signals.connect('/app/close', self.close)
        self.app.signals.connect('/app/actions', self._update)

        self.__ui__()
        self._update()

    def __ui__(self):

        self._ui_list = List()
        self._ui_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_list.itemDoubleClicked.connect(self.run_action)
        self._ui_list.customContextMenuRequested.connect(self._context_menu)

        self._ui_label = Label("0 Actions")
        self._ui_label.setAlignment(Qt.AlignCenter)
        self._ui_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_go_action = QAction(QIcon(':/rc/play.png'), "Run selected", self)
        self._ui_go_action.setIconVisibleInMenu(True)
        self._ui_go_action.triggered.connect(self.run_action)

        self._ui_search = SearchEdit()
        self._ui_search.setPlaceholderText("Search actions...")
        self._ui_search.textChanged.connect(self._search_event)

        self._ui_search_layout = VLayout()
        self._ui_search_layout.setContentsMargins(8, 8, 8, 8)
        self._ui_search_layout.addWidget(self._ui_search)

        self._ui_search_widget = QWidget()
        self._ui_search_widget.setObjectName("ActionsDialog_search_widget")
        self._ui_search_widget.setLayout(self._ui_search_layout)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.addWidget(self._ui_label)
        self._ui_toolbar.addAction(self._ui_go_action)

        self._ui_layout = VLayout()
        self._ui_layout.addWidget(self._ui_search_widget)
        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)
        self.setWindowTitle("Actions")
        self.setGeometry(0, 0, 300, 400)
        self.setMinimumSize(200, 200)
        self.moveCenter()

    def _update(self):
        """Update list of actions"""

        self._ui_list.clear()

        actions = self.app.actions()

        for action in actions:

            if len(self._keyword) > 0 and (self._keyword not in action.plugin.name + " " + action.name):
                continue

            item = ListItem("%s → %s" % (action.plugin.name, action.name))
            item.action = action

            self._ui_list.addItem(item)

        self._ui_label.setText("%d Actions" % len(actions))

    def _context_menu(self, pos):
        """Open context menu"""

        item = self._ui_list.itemAt(pos)

        if not item:
            return

        menu = QMenu("Context Menu", self)

        run_action = QAction('Run action', menu)
        run_action.triggered.connect(self.run_action)
        menu.addAction(run_action)

        menu.exec_(self._ui_list.mapToGlobal(pos))

    def _search_event(self, keyword):
        """Update list when search keyword available"""

        self._keyword = keyword
        self._update()

    def run_action(self):
        """Execute selected action"""

        items = self._ui_list.selectedItems()

        if len(items) > 0:
            items[0].action()
