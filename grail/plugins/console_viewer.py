# -*- coding: UTF-8 -*-
"""
    grail.plugins.console_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    View python console output & execute commands

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.qt import *
from grail.core import Viewer


class ConsoleViewer(Viewer):
    """Python console"""

    id = 'console'
    name = 'Console'
    author = 'Grail Team'
    description = 'Python console'

    def __init__(self, *args):
        super(ConsoleViewer, self).__init__(*args)

        self.__ui__()

        self.app.console.output.changed.connect(self._changed)

    def __ui__(self):
        """Build UI"""

        self._ui_notes = TextEdit()
        self._ui_notes.setObjectName('ConsoleViewer_text')
        self._ui_notes.setPlainText(self.get('text', default=''))
        self._ui_notes.setAcceptRichText(False)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(QIcon(':/icons/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.setObjectName("ConsoleViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(Spacer())
        self._ui_toolbar.addWidget(Label("Console"))
        self._ui_toolbar.addWidget(Spacer())

        self._ui_layout = VLayout()
        self._ui_layout.addWidget(self._ui_notes)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def _changed(self):
        """Console output changed"""

        self._ui_notes.setPlainText(self.app.console.output.read())
