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

from grailkit.qt import Label, Button, Spacer, VLayout

from grail.core import Viewer


class EmptyViewer(Viewer):

    id = 'empty'
    name = 'Empty'
    author = 'Grail Team'
    description = 'This viewer created after split or if viewer not found'
    private = True

    def __init__(self, parent=None):
        super(EmptyViewer, self).__init__(parent)

        self.setStyleSheet("""
            #EmptyViewer {
                background-color: #2f2f2f;
                }

            #EmptyViewer_title {
                qproperty-alignment: AlignCenter AlignCenter;
                text-align: center;
                font-size: 22px;
                margin: 0 0 6px 0;
                color: #f1f1f1;
                }

            #EmptyViewer_info {
                text-align: center;
                font-size: 13px;
                qproperty-alignment: AlignCenter AlignCenter;
                font-weight: 300;
                color: #929292;
                margin: 0 0 16px 0;
                }
            """)

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

        self._ui_layout.addWidget(Spacer())
        self._ui_layout.addWidget(self._ui_title_label)
        self._ui_layout.addWidget(self._ui_info_label)
        self._ui_layout.addWidget(self._ui_button, 0, Qt.AlignHCenter)
        self._ui_layout.addWidget(Spacer())

        self.setLayout(self._ui_layout)

    def menu_action(self):
        """Open menu with available viewers and other options"""

        menu = self.plugin_menu()
        menu.exec_(self.mapToGlobal(self._ui_button.pos()))
