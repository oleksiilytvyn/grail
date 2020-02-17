# -*- coding: UTF-8 -*-
"""
    grail.qt.about_dialog
    ~~~~~~~~~~~~~~~~~~~~~

    Generic about dialog window

    :copyright: (c) 2016-2020 by Oleksii Lytvyn (http://alexlitvin.name)
    :license: GNU, see LICENSE for more details.
"""
from grail.qt import *


class AboutDialog(QtWidgets.QDialog):
    """Default about dialog"""

    def __init__(self, parent=None, title="Application", description="version 1.0", icon=None):
        """A basic about dialog"""

        super(AboutDialog, self).__init__(parent)

        self._title = title
        self._description = description
        self._icon = icon

        self.app = Application.instance()
        self.app.signals.connect('/app/close', self.close)

        self.__ui__()

        self._ui_description.setPlainText(description)
        self._ui_title.setText(title)

    def __ui__(self):

        self._ui_icon = QtWidgets.QLabel(self)
        self._ui_icon.setAlignment(QtCore.Qt.AlignCenter)
        self._ui_icon.setGeometry(48, 52, 64, 64)

        if self._icon:
            self._ui_icon.setPixmap(self._icon.pixmap(64))

        self._ui_title = QtWidgets.QLabel(self._title, self)
        self._ui_title.setObjectName("g_about_title")
        self._ui_title.setGeometry(160, 34, 311, 26)

        self._ui_description = QtWidgets.QPlainTextEdit(self._description, self)
        self._ui_description.setObjectName("g_about_description")
        self._ui_description.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._ui_description.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._ui_description.setReadOnly(True)
        self._ui_description.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self._ui_description.viewport().setCursor(QtCore.Qt.ArrowCursor)
        self._ui_description.setGeometry(156, 74, 311, 100)

        self.setWindowTitle("About %s" % (self._title,))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setGeometry(100, 100, 484, 224)
        self.setFixedSize(484, 190)
