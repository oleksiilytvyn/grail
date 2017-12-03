# -*- coding: UTF-8 -*-
"""
    grail.plugins.notes_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Create text notes

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.qt import *
from grail.core import Viewer


class NotesViewer(Viewer):
    """View text notes"""

    id = 'notes'
    name = 'Notes'
    author = 'Grail Team'
    description = 'Create text notes'

    def __init__(self, *args):
        super(NotesViewer, self).__init__(*args)

        self.__ui__()

    def __ui__(self):
        """Build UI"""

        text = self.get('text', default='')

        self.setObjectName('NotesViewer')

        self._ui_notes = TextEdit()
        self._ui_notes.setObjectName('NotesViewer_text')
        self._ui_notes.setPlainText(text)
        self._ui_notes.setAcceptRichText(False)
        self._ui_notes.textChanged.connect(self._text_changed)

        self._ui_label = Label("Notes")
        self._ui_label.setObjectName('NotesViewer_label')
        self._ui_label.setAlignment(Qt.AlignCenter)
        self._ui_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon.colored(':/rc/menu.png', QColor('#2d2d32'), QColor('#e3e3e3')))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.setObjectName("NotesViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(self._ui_label)

        self._ui_layout = VLayout()
        self._ui_layout.addWidget(self._ui_notes)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def _text_changed(self):
        """Save text when changed"""

        self.set('text', str(self._ui_notes.toPlainText()))
