# -*- coding: UTF-8 -*-
"""
    grail.ui.welcome_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~

    Welcome dialog that provides option to choose action when Grail is launched
"""

import os

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.ui import GDialog, GWelcomeWidget, GWelcomeAction


class WelcomeDialog(GDialog):

    def __init__(self, app):
        super(WelcomeDialog, self).__init__()

        self.app = app

        self.__ui__()

    def __ui__(self):

        std_icon = QApplication.style().standardIcon

        create_action = GWelcomeAction("Create", "New project", std_icon(QStyle.SP_FileIcon))
        create_action.clicked.connect(self._create)

        open_action = GWelcomeAction("Open", "Open project", std_icon(QStyle.SP_DirIcon))
        open_action.clicked.connect(self._open)

        last_project = self.app.settings.get('project-last', default="")
        last_project_continue = last_project and os.path.isfile(last_project)

        if last_project_continue:
            continue_action = GWelcomeAction("Continue", os.path.split(last_project)[1], QIcon(':/icon/256.png'))
            continue_action.clicked.connect(self._continue)

        widget = GWelcomeWidget()
        widget.setTitle("Welcome to Grail")
        widget.setDescription("Choose action below")
        widget.setIcon(QIcon(':/icon/256.png'))
        widget.setIconVisible(True)

        widget.addWidget(create_action)
        widget.addWidget(open_action)

        if last_project_continue:
            widget.addWidget(continue_action)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)

        self.setLayout(layout)

        self.setGeometry(100, 100, 380, 460)
        self.setFixedSize(380, 460)
        self.setWindowTitle("Welcome to Grail")
        self.moveToCenter()

    def _open(self):
        """Open a existing project"""

        path, ext = QFileDialog.getOpenFileName(self, "Open File...", "", "*.grail")

        if path:
            self.app.open(path)

    def _create(self):
        """Create a new project"""

        project_name = "untitled"
        path, ext = QFileDialog.getSaveFileName(self, "New project", project_name, "*.grail")

        if path:
            self.app.open(path, create=True)

    def _continue(self):
        """Open a last project"""

        path = self.app.settings.get('last-project')

        if os.path.isfile(path):
            self.app.open(path, create=False)
