# -*- coding: UTF-8 -*-
"""
    grail.plugins.empty_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Empty viewer

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy

from grail.qt import Label, Button, VLayout

from grail.core import Viewer


class EmptyViewer(Viewer):
    """Default viewer"""

    id = 'empty'
    name = 'Empty'
    author = 'Grail Team'
    description = 'This viewer created after split or if viewer not found'
    private = True

    def __init__(self, *args):
        super(EmptyViewer, self).__init__(*args)

        self.__ui__()

    def __ui__(self):
        """Setup UI components"""

        self.setObjectName("EmptyViewer")

        self._ui_title_label = Label("No view")
        self._ui_title_label.setObjectName('EmptyViewer_title')

        self._ui_info_label = Label("Viewer not loaded, click on button and pick one")
        self._ui_info_label.setObjectName('EmptyViewer_info')
        self._ui_info_label.setWordWrap(True)

        self._ui_button = Button('View')
        self._ui_button.clicked.connect(self.menu_action)
        self._ui_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._ui_button.setMaximumWidth(80)

        self._ui_layout = VLayout()
        self._ui_layout.setContentsMargins(12, 12, 12, 12)
        self._ui_layout.setAlignment(Qt.AlignHCenter)

        self._ui_layout.addStretch()
        self._ui_layout.addWidget(self._ui_title_label)
        self._ui_layout.addWidget(self._ui_info_label)
        self._ui_layout.addWidget(self._ui_button, 0, Qt.AlignHCenter)
        self._ui_layout.addStretch()

        self.setMinimumHeight(140)
        self.setLayout(self._ui_layout)

    def menu_action(self):
        """Open menu with available viewers and other options"""

        self.show_menu(self._ui_button.pos(), self)
