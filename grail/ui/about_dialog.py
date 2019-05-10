# -*- coding: UTF-8 -*-
"""
    grail.qt.about_dialog
    ~~~~~~~~~~~~~~~~~~~~~

    Generic about dialog window

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
from grail.qt import *


class AboutDialog(QDialog):
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

        self._ui_pixmap = QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation)

        self._ui_icon = QLabel(self)
        self._ui_icon.setPixmap(self._ui_pixmap.pixmap(64))
        self._ui_icon.setAlignment(Qt.AlignCenter)
        self._ui_icon.setGeometry(48, 52, 64, 64)

        if self._icon:
            self._ui_icon.setPixmap(self._icon.pixmap(64))

        self._ui_title = QLabel(self._title, self)
        self._ui_title.setObjectName("g_about_title")
        self._ui_title.setGeometry(160, 34, 311, 26)

        self._ui_description = QPlainTextEdit(self._description, self)
        self._ui_description.setObjectName("g_about_description")
        self._ui_description.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._ui_description.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._ui_description.setReadOnly(True)
        self._ui_description.setTextInteractionFlags(Qt.NoTextInteraction)
        self._ui_description.viewport().setCursor(Qt.ArrowCursor)
        self._ui_description.setGeometry(156, 74, 311, 100)

        self.setWindowTitle("About %s" % (self._title,))
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setGeometry(100, 100, 484, 224)
        self.setFixedSize(484, 190)
