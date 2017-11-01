# -*- coding: UTF-8 -*-
"""
    grailkit.qt.progress_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dialog for displaying any progress

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.qt import Dialog


class ProgressDialog(Dialog):
    """Progress dialog with cancel button, title and description text"""

    def __init__(self, parent=None,
                 title="Processing something...",
                 text="Item 1 of 10",
                 icon=None,
                 minimum=0,
                 maximum=100):
        super(ProgressDialog, self).__init__(parent)

        self._title = title
        self._text = text
        self._icon = None
        self._auto_close = False
        self._icon_visible = True

        self.__ui__()

        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setIconVisible(self._icon_visible)
        self.setIcon(icon)

    def __ui__(self):

        self._ui_icon = QLabel(self)
        self._ui_icon.setAlignment(Qt.AlignCenter)
        self._ui_icon.setGeometry(12, 12, 56, 56)

        self._ui_cancel_btn = QToolButton(self)
        self._ui_cancel_btn.setIconSize(QSize(14, 14))
        self._ui_cancel_btn.setIcon(QIcon(':/gk/icon/search-clear.png'))
        self._ui_cancel_btn.setCursor(Qt.ArrowCursor)
        self._ui_cancel_btn.setGeometry(0, 0, 14, 14)
        self._ui_cancel_btn.clicked.connect(self.cancel)

        self._ui_title = QLabel(self._title)
        self._ui_title.setObjectName("g_progress_title")

        self._ui_text = QLabel(self._text)
        self._ui_text.setObjectName("g_progress_text")

        self._ui_progress = QProgressBar()
        self._ui_progress.setMinimum(0)
        self._ui_progress.setMaximum(100)
        self._ui_progress.setValue(50)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setContentsMargins(82, 0, 36, 0)
        self._ui_layout.setSpacing(0)

        self._ui_layout.addWidget(self._ui_title, 1, Qt.AlignBottom)
        self._ui_layout.addWidget(self._ui_progress, 0, Qt.AlignVCenter)
        self._ui_layout.addWidget(self._ui_text, 1, Qt.AlignTop)

        self.setLayout(self._ui_layout)
        self.setWindowTitle(self._title)
        self.setMinimumSize(420, 82)
        self.setGeometry(100, 100, 420, 82)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(self.size().width(), self.size().height())

    def resizeEvent(self, event):
        """Update widgets positions"""

        rect = self.rect()
        btn_rect = self._ui_cancel_btn.rect()
        icon_rect = self._ui_icon.rect()

        self._ui_icon.move(12, rect.height() / 2 - icon_rect.height() / 2 - 2)

        self._ui_cancel_btn.move(rect.width() - btn_rect.width() - 12,
                                 rect.height() / 2 - btn_rect.height() / 2)

    def icon(self):
        """Get a icon of dialog"""

        return QIcon(self._icon)

    def setIcon(self, icon):
        """Set dialog icon

        Args:
            icon (QIcon, QPixmap): icon of dialog
        """

        size = 56

        if isinstance(icon, QIcon):
            self._icon = icon.pixmap(size)
        elif isinstance(icon, QPixmap):
            self._icon = icon.scaledToWidth(size)
        else:
            self._icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation).pixmap(size)

        self._ui_icon.setPixmap(self._icon)

    def setIconVisible(self, flag):
        """Show icon or not"""

        self._icon_visible = flag

        if flag:
            self._ui_icon.show()
            self._ui_layout.setContentsMargins(82, 0, 36, 0)
        else:
            self._ui_icon.hide()
            self._ui_layout.setContentsMargins(12, 0, 36, 0)

    def title(self):
        """Get a dialog title"""

        return self._title

    def setTitle(self, title):
        """Set dialog title

        Args:
            title (str): title
        """

        self._title = title
        self._ui_title.setText(self._title)

    def text(self):
        """Get a dialog text"""

        return self._text

    def setText(self, text):
        """Text displayed in dialog

        Args:
            text (str): informative text
        """

        self._text = text
        self._ui_text.setText(self._text)

    def setValue(self, value):
        """Set value of progress bar

        Args:
            value (int): value of progress
        """

        if value >= self._ui_progress.value() and self._auto_close:
            self.close()

        self._ui_progress.setValue(value)

    def value(self):
        """Returns value of progressbar"""

        return self._ui_progress.value()

    def setMaximum(self, value):
        """Set maximum value of progress bar

        Args:
            value (int): maximum value
        """

        self._ui_progress.setMaximum(value)

    def setMinimum(self, value):
        """Set minimum value of progress bar

        Args:
            value (int): minimum value
        """

        self._ui_progress.setMinimum(value)

    def setRange(self, min, max):
        """Set a minimum and maximum values of progress bar

        Args:
            min (int): minimum value
            max (int): maximum value
        """

        self._ui_progress.setRange(min, max)

    def setAutoClose(self, flag):
        """Close dialog when progress reaches maximum value

        Args:
            flag (bool): close dialog or not
        """

        self._auto_close = flag

    def cancel(self):
        """Cancel a progress and close dialog"""

        self.close()
