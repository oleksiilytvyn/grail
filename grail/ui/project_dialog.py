# -*- coding: UTF-8 -*-
"""
    grail.ui.project_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~

    Change project information

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
from grail.qt import *


class ProjectDialog(QtWidgets.QDialog):
    """Project information"""

    def __init__(self, parent=None):
        super(ProjectDialog, self).__init__(parent)

        self.__ui__()
        self._update()

        Application.instance().signals.connect('/app/close', self.close)

    def __ui__(self):

        self._ui_title = QtWidgets.QLineEdit()
        self._ui_title.setPlaceholderText("Project title")
        self._ui_title.textChanged.connect(self.title_changed)

        self._ui_author = QtWidgets.QLineEdit()
        self._ui_author.setPlaceholderText("Project author")
        self._ui_author.setMaximumWidth(160)
        self._ui_author.textChanged.connect(self.author_changed)

        self._ui_description = QtWidgets.QTextEdit()
        self._ui_description.setPlaceholderText("Description")
        self._ui_description.textChanged.connect(self.description_changed)

        self._ui_title_layout = QtWidgets.QHBoxLayout()
        self._ui_title_layout.setSpacing(8)
        self._ui_title_layout.setContentsMargins(8, 8, 8, 8)

        self._ui_title_layout.addWidget(self._ui_title)
        self._ui_title_layout.addWidget(self._ui_author)

        self._ui_layout = QtWidgets.QVBoxLayout()
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
        """Project title changed"""

        project = Application.instance().project
        project.name = str(self._ui_title.text())

    def author_changed(self):
        """Project author changed"""

        project = Application.instance().project
        project.author = str(self._ui_author.text())

    def description_changed(self):
        """Project description changed"""

        project = Application.instance().project
        project.description = str(self._ui_description.toPlainText())
