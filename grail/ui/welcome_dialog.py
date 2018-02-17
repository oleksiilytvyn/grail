# -*- coding: UTF-8 -*-
"""
    grail.ui.welcome_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~

    Welcome dialog that provides options to choose from when Grail is launched

    :copyright: (c) 2018 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""

import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from grail.qt import Dialog, Welcome, WelcomeAction


class WelcomeDialog(Dialog):
    """Welcome dialog that shown on Grail startup"""

    def __init__(self, app):
        super(WelcomeDialog, self).__init__()

        self.app = app

        self.__ui__()

    def __ui__(self):
        """Build UI"""

        std_icon = QApplication.style().standardIcon
        grail_icon = QIcon(':/icon/256.png')

        create_action = WelcomeAction("Create", "New project", std_icon(QStyle.SP_FileIcon))
        create_action.clicked.connect(self._create)

        open_action = WelcomeAction("Open", "Open project", std_icon(QStyle.SP_DirIcon))
        open_action.clicked.connect(self._open)

        last_project = self.app.settings.get('project/last', default="")
        last_project_continue = last_project and os.path.isfile(last_project)

        widget = Welcome()
        widget.setTitle("Welcome to Grail")
        widget.setDescription("Choose menu_action below")
        widget.setIcon(grail_icon)
        widget.setIconVisible(True)

        widget.addWidget(create_action)
        widget.addWidget(open_action)

        if last_project_continue:
            continue_action = WelcomeAction("Continue", os.path.split(last_project)[1], grail_icon)
            continue_action.clicked.connect(self._continue)

            widget.addWidget(continue_action)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)

        self.setLayout(layout)
        self.setWindowTitle("Welcome to Grail")
        self.setWindowIcon(grail_icon)
        self.setGeometry(100, 100, 380, 460)
        self.setFixedSize(380, 460)
        self.moveCenter()

    def _open(self):
        """Open a existing project"""

        location = QStandardPaths.locate(QStandardPaths.DocumentsLocation, "",
                                         QStandardPaths.LocateDirectory)
        path, ext = QFileDialog.getOpenFileName(self, "Open File...", location, "*.grail")

        if path:
            self.app.open(path)

    def _create(self):
        """Create a new project"""

        project_name = "untitled"
        location = QStandardPaths.locate(QStandardPaths.DocumentsLocation, "",
                                         QStandardPaths.LocateDirectory)
        location = os.path.join(location, project_name)

        path, ext = QFileDialog.getSaveFileName(self, "New project", location, "*.grail")

        if path:
            self.app.open(path, create=True)

    def _continue(self):
        """Open a last project"""

        path = self.app.settings.get('project/last')

        if os.path.isfile(path):
            self.app.open(path, create=False)
