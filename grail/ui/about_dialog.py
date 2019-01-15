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
        self._icon = None

        self.url_report = ""
        self.url_help = ""

        self.__ui__()
        self.setIcon(icon)

    def __ui__(self):

        self._ui_pixmap = QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation)

        self._ui_icon = QLabel(self)
        self._ui_icon.setPixmap(self._ui_pixmap.pixmap(64))
        self._ui_icon.setAlignment(Qt.AlignCenter)
        self._ui_icon.setGeometry(48, 52, 64, 64)

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
        self._ui_description.setGeometry(156, 74, 311, 88)

        self._ui_btn_help = QPushButton("Help")
        self._ui_btn_help.clicked.connect(self.help)

        self._ui_btn_report = QPushButton("Report a problem")
        self._ui_btn_report.clicked.connect(self.report)

        self.ui_btn_close = QPushButton("Close")
        self.ui_btn_close.setDefault(True)
        self.ui_btn_close.clicked.connect(self.close)

        self._ui_buttons_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self._ui_buttons_layout.addWidget(self._ui_btn_help)
        self._ui_buttons_layout.addStretch()
        self._ui_buttons_layout.addWidget(self._ui_btn_report)
        self._ui_buttons_layout.addWidget(self.ui_btn_close)

        self._ui_buttons = QWidget(self)
        self._ui_buttons.setLayout(self._ui_buttons_layout)
        self._ui_buttons.setGeometry(8, 172, 484 - 16, 50)

        self.setWindowTitle("About %s" % (self._title,))
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setGeometry(100, 100, 484, 224)
        self.setFixedSize(484, 224)

    def setIcon(self, icon):
        """Set icon"""

        size = 64

        if isinstance(icon, QIcon):
            self._icon = icon.pixmap(size)

        if isinstance(icon, QPixmap):
            self._icon = icon.scaledToWidth(size)

        if self._icon:
            self._ui_icon.setPixmap(self._icon)

    def setTitle(self, title):
        """Set a title text"""

        self._ui_title.setText(title)

    def setDescription(self, text):
        """Set a description text"""

        self._ui_description.setPlainText(text)

    def help(self):
        """Open a web page"""

        QDesktopServices.openUrl(QUrl(self.url_help))

    def report(self):
        """Open a web page"""

        QDesktopServices.openUrl(QUrl(self.url_report))
