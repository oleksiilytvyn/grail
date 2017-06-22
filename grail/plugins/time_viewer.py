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

from grailkit.qt import VLayout, Label, Spacer, Toolbar
from grail.core import Viewer


class TimeViewer(Viewer):
    """View current time"""

    id = 'time'
    name = 'Time'
    author = 'Grail Team'
    description = 'Display current time'

    # todo: Add options like color, size and background

    def __init__(self, *args):
        super(TimeViewer, self).__init__(*args)

        self.__ui__()

        self.timer = QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(1000)

        self._update()

    def __ui__(self):

        self._label = Label('00:00:00')
        self._label.setObjectName("TimeViewer_label")

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(QIcon(':/icons/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.setObjectName("TimeViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(Spacer())

        self._layout = VLayout()
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._ui_toolbar)

        self.setLayout(self._layout)

    def _update(self):
        """Update time"""

        _time = datetime.datetime.now()

        self._label.setText("%s:%s:%s" % (str(_time.hour).zfill(2),
                                          str(_time.minute).zfill(2),
                                          str(_time.second).zfill(2)))

    def view_action(self):
        """Replace current view with something other"""

        self.plugin_menu().exec_(self._ui_toolbar.mapToGlobal(self._ui_view_action.pos()))
