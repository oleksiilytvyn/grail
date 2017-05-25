# -*- coding: UTF-8 -*-
"""
    grail.plugins.time_plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    View current time

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.qt import VLayout, Label, Spacer
from grail.core import Viewer


class TimeViewer(Viewer):
    """View current time"""

    id = 'time'
    name = 'Time'
    author = 'Grail Team'
    description = 'Display current time'

    def __init__(self, parent=None):
        super(TimeViewer, self).__init__(parent)

        self.__ui__()

        self.timer = QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(1000)

        self._update()

    def __ui__(self):

        self._label = Label('Hello World!')
        self._label.setStyleSheet("""
            Label {
                color: #f1f1f1;
                background: #222;
                text-align: center;
                font-size: 48px;
                qproperty-alignment: AlignCenter AlignCenter;
            }
            """)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(QIcon(':/icons/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setStyleSheet("""
            QToolBar {
                color: #f1f1f1;
                background: #222;
                border-top: 1px solid #666;
            }
            """)

        self._ui_toolbar.setObjectName("library_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(Spacer())

        self._layout = VLayout()
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._ui_toolbar)

        self.setLayout(self._layout)

    def _update(self):

        _time = datetime.datetime.now()

        self._label.setText("%d:%d:%d" % (_time.hour, _time.minute, _time.second))

    def view_action(self):
        """Replace current view with something other"""

        menu = self.plugin_menu()
        menu.exec_(self._ui_toolbar.mapToGlobal(self._ui_view_action.pos()))
