# -*- coding: UTF-8 -*-
"""
    grail.qt.welcome
    ~~~~~~~~~~~~~~~~

    Welcome component

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""

from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QPushButton, QLabel, QStyleOption, QStyle, QWidget, QVBoxLayout, QSizePolicy

from grail.qt import Component, Application


class Welcome(Component):
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

        # fix stylesheet issues
        self.setStyleSheet(Application.instance().stylesheet())
        self.setMinimumWidth(300)

        self._ui_icon = QLabel(self)
        self._ui_icon.setAlignment(Qt.AlignCenter)
        self._ui_icon.setGeometry(0, 0, 64, 64)

        self._ui_title = QLabel("Welcome")
        self._ui_title.setObjectName("gk_welcome_title")
        self._ui_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_description = QLabel("Choose some action below")
        self._ui_description.setObjectName("gk_welcome_description")
        self._ui_description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_actions_layout = QVBoxLayout()
        self._ui_actions_layout.setSpacing(14)
        self._ui_actions_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_actions = QWidget()
        self._ui_actions.setContentsMargins(50, 0, 50, 0)
        self._ui_actions.setLayout(self._ui_actions_layout)

        self._ui_layout = QVBoxLayout()
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

        if isinstance(icon, QIcon):
            self._icon = icon.pixmap(size)

        if isinstance(icon, QPixmap):
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

        option = QStyleOption()
        option.initFrom(self)

        painter = QPainter(self)

        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)


class WelcomeAction(QPushButton, Component):
    """Action for Welcome"""

    def __init__(self, title="Action", text="Take some action", icon=None, parent=None):
        super(WelcomeAction, self).__init__(parent)

        self._icon = None
        self._title = title
        self._text = text
        self._icon_size = 48

        self._ui_title = QLabel(self._title)
        self._ui_title.setObjectName("gk_welcome_action_title")

        self._ui_text = QLabel(self._text)
        self._ui_text.setObjectName("gk_welcome_action_text")

        self._ui_layout = QVBoxLayout()
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

        return QSize(64, 64)

    def paintEvent(self, event):
        """Custom painting"""

        o = QStyleOption()
        o.initFrom(self)

        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)

        if self._icon:
            p.drawPixmap(QPoint(64 / 2 - self._icon_size / 2, self.height() / 2 - self._icon_size / 2), self._icon)

        p.end()

    def setIcon(self, icon):
        """Set action icon

        Args:
            icon (QIcon, QPixmap): icon of action
        """

        if isinstance(icon, QIcon):
            self._icon = icon.pixmap(self._icon_size)

        if isinstance(icon, QPixmap):
            self._icon = icon.scaledToWidth(self._icon_size)

    def icon(self):
        """Get a icon of action

        Returns: QIcon
        """

        return QIcon(self._icon)

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
