# -*- coding: UTF-8 -*-
"""
    grail.ui.preview_editor
    ~~~~~~~~~~~~~~~~~~~~~~~

    Simple preview panel
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.qt import GSpacer

from grail.ui import Panel


class PreviewEditor(Panel):

    def __init__(self, app):
        super(PreviewEditor, self).__init__()

        self.app = app
        self.connect('/message/preview', self._on_message)

        self.__ui__()

    def __ui__(self):

        self._ui_label = QLabel("")
        self._ui_label.setObjectName("preview_label")
        self._ui_label.setWordWrap(True)
        self._ui_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        self._ui_edit = QTextEdit()
        self._ui_edit.setObjectName("preview_edit")
        self._ui_edit.textChanged.connect(self._edit_changed)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("preview_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))

        self._ui_blackout_action = QAction(QIcon(':/icons/stop.png'), 'Blackout', self)
        self._ui_blackout_action.triggered.connect(self._blackout_action)

        self._ui_show_quick_action = QAction(QIcon(':/icons/play.png'), 'Show', self)
        self._ui_show_quick_action.triggered.connect(self._show_action)
        self._ui_show_quick_action.setIconVisibleInMenu(True)

        self._ui_live_action = QAction(QIcon(':/icons/live.png'), 'Live', self)
        self._ui_live_action.triggered.connect(self._live_action)
        self._ui_live_action.setCheckable(True)
        self._ui_live_action.setChecked(False)
        self._ui_live_action.setIconVisibleInMenu(True)

        self._ui_toolbar.addAction(self._ui_show_quick_action)
        self._ui_toolbar.addAction(self._ui_blackout_action)
        self._ui_toolbar.addWidget(GSpacer())
        self._ui_toolbar.addAction(self._ui_live_action)

        self._ui_edit_layout = QVBoxLayout()
        self._ui_edit_layout.setSpacing(0)
        self._ui_edit_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_edit_layout.addWidget(self._ui_edit)
        self._ui_edit_layout.addWidget(self._ui_toolbar)

        self._ui_edit_widget = QWidget()
        self._ui_edit_widget.setMinimumSize(200, 100)
        self._ui_edit_widget.setLayout(self._ui_edit_layout)

        self._ui_splitter = QSplitter(Qt.Vertical)
        self._ui_splitter.setObjectName("preview_splitter")
        self._ui_splitter.addWidget(self._ui_label)
        self._ui_splitter.addWidget(self._ui_edit_widget)
        self._ui_splitter.setCollapsible(1, False)
        self._ui_splitter.setSizes([400, 120])
        self._ui_splitter.setHandleWidth(1)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_layout.addWidget(self._ui_splitter)

        self.setLayout(self._ui_layout)

    def _on_message(self, message):
        """Display message"""

        self._ui_label.setText(message)
        self._ui_edit.setPlainText(message)

    def _edit_changed(self):
        pass

    def _blackout_action(self):
        pass

    def _show_action(self):
        pass

    def _live_action(self):
        pass
