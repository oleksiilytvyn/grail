# -*- coding: UTF-8 -*-
"""
    grail.ui.cuelist_editor
    ~~~~~~~~~~~~~~~~~~~~~~~

    Manage cuelist in this view
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.ui import GSpacer, GListWidget

from grail.ui import CuelistDialog, Panel


class CuelistEditor(Panel):

    def __init__(self, app):
        super(CuelistEditor, self).__init__()

        self.app = app
        self._locked = False

        self.dialog = CuelistDialog()
        self.dialog.showAt(QPoint(500, 500))

        self.connect('/app/close', self._close)

        self.__ui__()

    def __ui__(self):

        self.setObjectName("cuelist")

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setObjectName("cuelist_layout")
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_list = GListWidget()
        self._ui_list.setObjectName("cuelist_list")
        self._ui_list.setContextMenuPolicy(Qt.CustomContextMenu)

        self._ui_lock_action = QAction(QIcon(':/icons/lock.png'), 'Lock', self)
        self._ui_lock_action.setIconVisibleInMenu(True)
        self._ui_lock_action.triggered.connect(self.lock_action)

        self._ui_menu_action = QAction(QIcon(':/icons/menu.png'), 'Cuelists', self)
        self._ui_menu_action.setIconVisibleInMenu(True)
        self._ui_menu_action.triggered.connect(self.menu_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("cuelist_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_lock_action)
        self._ui_toolbar.addWidget(GSpacer())
        self._ui_toolbar.addAction(self._ui_menu_action)

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def lock_action(self):

        self._locked = not self._locked
        self.app.emit("app/lock", self._locked)

    def menu_action(self):

        point = QPoint(self.rect().width() - 20, self.rect().height() - 16)

        self.dialog.update_list()
        self.dialog.showAt(self.mapToGlobal(point))

    def _close(self):
        """Close child dialogs"""

        self.dialog.close()
