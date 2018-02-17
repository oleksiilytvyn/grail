# -*- coding: UTF-8 -*-
"""
    grail.ui.project_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~

    Change project information

    :copyright: (c) 2018 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.qt import Dialog, VLayout, HLayout, Application, LineEdit


class ProjectDialog(Dialog):
    """Project information"""

    def __init__(self, parent=None):
        super(ProjectDialog, self).__init__(parent)

        self.__ui__()
        self._update()

        Application.instance().signals.connect('/app/close', self.close)

    def __ui__(self):

        self._ui_title = LineEdit()
        self._ui_title.setPlaceholderText("Project title")
        self._ui_title.textChanged.connect(self.title_changed)

        self._ui_author = LineEdit()
        self._ui_author.setPlaceholderText("Project author")
        self._ui_author.setMaximumWidth(160)
        self._ui_author.textChanged.connect(self.author_changed)

        self._ui_description = QTextEdit()
        self._ui_description.setPlaceholderText("Description")
        self._ui_description.textChanged.connect(self.description_changed)

        self._ui_title_layout = HLayout()
        self._ui_title_layout.setSpacing(8)
        self._ui_title_layout.setContentsMargins(8, 8, 8, 8)

        self._ui_title_layout.addWidget(self._ui_title)
        self._ui_title_layout.addWidget(self._ui_author)

        self._ui_layout = VLayout()
        self._ui_layout.addLayout(self._ui_title_layout)
        self._ui_layout.addWidget(self._ui_description)

        self.setLayout(self._ui_layout)
        self.setWindowTitle("Project details")
        self.setGeometry(0, 0, 400, 200)

    def _update(self):

        project = Application.instance().project

        self._ui_title.setText(project.name)
        self._ui_author.setText(project.author)
        self._ui_description.setPlainText(project.description)

    def title_changed(self):

        project = Application.instance().project
        project.name = str(self._ui_title.text())

    def author_changed(self):

        project = Application.instance().project
        project.author = str(self._ui_author.text())

    def description_changed(self):

        project = Application.instance().project
        project.description = str(self._ui_description.toPlainText())
