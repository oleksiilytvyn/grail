# -*- coding: UTF-8 -*-
"""
    grail.ui.welcome_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~

    Welcome dialog that provides options to choose from when Grail is launched

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
import os

import grail
from grail.qt import *


class Welcome(QtWidgets.QWidget):
    """Widget with title, icon and actions below"""

    def __init__(self, title="Welcome", description="Choose action bellow", icon=None, parent=None):
        super(Welcome, self).__init__(parent)

        self._icon = None
        self.__ui__()

        if icon:
            self.setIcon(icon)
            self.setIconVisible(True)
        else:
            self.setIconVisible(False)

        self.setTitle(title)
        self.setDescription(description)

    def __ui__(self):
        """Create ui"""

        self.setMinimumWidth(300)

        self._ui_icon = QtWidgets.QLabel(self)
        self._ui_icon.setAlignment(QtCore.Qt.AlignCenter)
        self._ui_icon.setGeometry(0, 0, 64, 64)

        self._ui_title = QtWidgets.QLabel("Welcome")
        self._ui_title.setObjectName("gk_welcome_title")
        self._ui_title.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self._ui_description = QtWidgets.QLabel("Choose some action below")
        self._ui_description.setObjectName("gk_welcome_description")
        self._ui_description.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self._ui_actions_layout = QtWidgets.QVBoxLayout()
        self._ui_actions_layout.setSpacing(14)
        self._ui_actions_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_actions = QtWidgets.QWidget()
        self._ui_actions.setContentsMargins(50, 0, 50, 0)
        self._ui_actions.setLayout(self._ui_actions_layout)

        self._ui_layout = QtWidgets.QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_layout.addStretch(1)
        self._ui_layout.addWidget(self._ui_icon)
        self._ui_layout.addSpacing(12)
        self._ui_layout.addWidget(self._ui_title)
        self._ui_layout.addWidget(self._ui_description)
        self._ui_layout.addWidget(self._ui_actions)
        self._ui_layout.addStretch(1)

        self.setLayout(self._ui_layout)

    def addWidget(self, widget):
        """Add action to list

        Args:
            widget (WelcomeAction): action to be added
        """

        self._ui_actions_layout.addWidget(widget)

    def setTitle(self, title):
        """Set widget title

        Args:
            title (str): title text
        """

        self._ui_title.setText(title)

    def setDescription(self, text):
        """Set widget description

        Args:
            text (str): description text
        """

        self._ui_description.setText(text)

    def setIcon(self, icon):
        """Set icon of widget

        Args:
            icon (QIcon, QPixmap): icon of widget
        """

        size = 128

        if isinstance(icon, QtGui.QIcon):
            self._icon = icon.pixmap(size)

        if isinstance(icon, QtGui.QPixmap):
            self._icon = icon.scaledToWidth(size)

        self._ui_icon.setPixmap(self._icon)

    def setIconVisible(self, flag):
        """Make icon visible or not

        Args:
            flag (bool): True if it visible
        """

        if flag:
            self._ui_icon.show()
        else:
            self._ui_icon.hide()

    def resizeEvent(self, event):
        """Align widgets"""

        super(Welcome, self).resizeEvent(event)

        width = self.size().width()

        if width <= 150:
            padding = 8
        elif width <= 300:
            padding = 50
        elif width >= 600:
            padding = (width - 350) * 0.5
        else:
            padding = width * 0.2

        self._ui_actions.setContentsMargins(padding, 0, padding, 0)

    def paintEvent(self, event):
        """Paint component with CSS styles"""

        option = QtWidgets.QStyleOption()
        option.initFrom(self)

        painter = QtGui.QPainter(self)

        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, option, painter, self)


class WelcomeAction(QtWidgets.QPushButton, QtWidgets.QWidget):
    """Action for Welcome"""

    def __init__(self, title="Action", text="Take some action", icon=None, parent=None):
        super(WelcomeAction, self).__init__(parent)

        self._icon = None
        self._title = title
        self._text = text
        self._icon_size = 48

        self._ui_title = QtWidgets.QLabel(self._title)
        self._ui_title.setObjectName("gk_welcome_action_title")

        self._ui_text = QtWidgets.QLabel(self._text)
        self._ui_text.setObjectName("gk_welcome_action_text")

        self._ui_layout = QtWidgets.QVBoxLayout()
        self._ui_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_layout.setSpacing(0)
        self._ui_layout.addStretch(1)
        self._ui_layout.addWidget(self._ui_title)
        self._ui_layout.addWidget(self._ui_text)
        self._ui_layout.addStretch(1)

        self.setIcon(icon)
        self.setText(self._text)

        self.setLayout(self._ui_layout)

    def sizeHint(self):
        """Default size of widget"""

        return QtCore.QSize(64, 64)

    def paintEvent(self, event):
        """Custom painting"""

        o = QtWidgets.QStyleOption()
        o.initFrom(self)

        p = QtGui.QPainter(self)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, o, p, self)

        if self._icon:
            p.drawPixmap(QtCore.QPoint(64 / 2 - self._icon_size / 2, self.height() / 2 - self._icon_size / 2),
                         self._icon)

        p.end()

    def setIcon(self, icon):
        """Set action icon

        Args:
            icon (QIcon, QPixmap): icon of action
        """

        if isinstance(icon, QtGui.QIcon):
            self._icon = icon.pixmap(self._icon_size)

        if isinstance(icon, QtGui.QPixmap):
            self._icon = icon.scaledToWidth(self._icon_size)

    def icon(self):
        """Get a icon of action

        Returns: QIcon
        """

        return QtGui.QIcon(self._icon)

    def setTitle(self, title):
        """Set a title of action

        Args:
            title (str): set a title of action
        """

        self._title = title
        self._ui_title.setText(self._title)

    def title(self):
        """Get title of action

        Returns: str
        """

        return self._title

    def setText(self, text):
        """Set a description text of this action

        Args:
            text (str): text of action
        """

        super(WelcomeAction, self).setText("")

        self._text = text
        self._ui_text.setText(self._text)

    def text(self):
        """Get a text of action

        Returns: str
        """

        return self._text


class WelcomeDialog(QtWidgets.QDialog):
    """Welcome dialog that shown on Grail startup"""

    def __init__(self, app):
        super(WelcomeDialog, self).__init__()

        self.app = app

        self.__ui__()

    def __ui__(self):
        """Build UI"""

        def std_icon(name):
            # scale standard icon to default size

            return QtGui.QIcon(QtGui.QPixmap(QtWidgets.QApplication.style()
                                             .standardIcon(name)
                                             .pixmap(32, 32)).scaled(48, 48))

        grail_icon = QtGui.QIcon(':/icon/256.png')

        create_action = WelcomeAction("Create", "New project", std_icon(QtWidgets.QStyle.SP_FileIcon))
        create_action.clicked.connect(self._create)

        open_action = WelcomeAction("Open", "Existing project", std_icon(QtWidgets.QStyle.SP_DirIcon))
        open_action.clicked.connect(self._open)

        last_project = self.app.settings.get('project/last', default="")
        last_project_continue = last_project and os.path.isfile(last_project)

        widget = Welcome()
        widget.setTitle("Grail %s" % grail.__version__)
        widget.setDescription("Choose action below")
        widget.setIcon(grail_icon)
        widget.setIconVisible(True)

        widget.addWidget(create_action)
        widget.addWidget(open_action)

        if last_project_continue:
            continue_action = WelcomeAction("Continue", os.path.split(last_project)[1], grail_icon)
            continue_action.clicked.connect(self._continue)

            widget.addWidget(continue_action)

        layout = QtWidgets.QHBoxLayout()
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

        path = QtGetOpenFileName(self, "Open File...", QtDocumentsLocation, "*.grail")

        if path:
            self.app.open(path)

    def _create(self):
        """Create a new project"""

        project_name = "untitled"
        location = os.path.join(QtDocumentsLocation, project_name)

        path = QtGetSaveFileName(self, "New project", location, "*.grail")

        if path:
            self.app.open(path, create=True)

    def _continue(self):
        """Open a last project"""

        path = self.app.settings.get('project/last')

        if os.path.isfile(path):
            self.app.open(path, create=False)
