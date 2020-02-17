# -*- coding: UTF-8 -*-
"""
    grail.qt.message_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~

    Replacement for default OS message dialog

    :copyright: (c) 2016-2020 by Oleksii Lytvyn (http://alexlitvin.name)
    :license: GNU, see LICENSE for more details.
"""
from grail.qt import QtWidgets, QtCore, QtGui, QtSignal
from grailkit.util import OS_MAC


# noinspection PyPep8Naming
class MessageDialog(QtWidgets.QDialog):
    """Message dialog, replacement of a default dialog"""

    # default icons
    NoIcon = 0
    Information = 1
    Warning = 2
    Critical = 3
    Question = 4

    # enum of all available standard icons
    Icon = (NoIcon, Information, Warning, Critical, Question)

    # button role
    InvalidRole = -1
    AcceptRole = 0
    RejectRole = 1
    DestructiveRole = 2
    ActionRole = 3
    HelpRole = 4
    YesRole = 5
    NoRole = 6
    ApplyRole = 7
    ResetRole = 8

    # enum of button roles
    Role = (InvalidRole, AcceptRole, RejectRole, DestructiveRole, ActionRole,
            HelpRole, YesRole, NoRole, ApplyRole, ResetRole)

    # standard buttons
    Ok = 1
    Open = 2
    Save = 3
    Cancel = 4
    Close = 5
    Discard = 6
    Apply = 7
    Reset = 8
    RestoreDefaults = 9
    Help = 10
    SaveAll = 11
    Yes = 12
    YesToAll = 13
    No = 14
    NoToAll = 15
    Abort = 16
    Retry = 17
    Ignore = 18
    NoButton = 19

    StandardButton = (Ok, Open, Save, Cancel, Close, Discard, Apply, Reset, RestoreDefaults, Help,
                      SaveAll, Yes, YesToAll, No, NoToAll, Abort, Retry, Ignore, NoButton)

    StandardButtonRoleName = {
        1: (AcceptRole, "Ok"),
        2: (AcceptRole, "Open"),
        3: (AcceptRole, "Save"),
        4: (RejectRole, "Cancel"),
        5: (RejectRole, "Close"),
        6: (DestructiveRole, "Discard"),
        7: (ApplyRole, "Apply"),
        8: (ResetRole, "Reset"),
        9: (ResetRole, "Restore Defaults"),
        10: (HelpRole, "Help"),
        11: (AcceptRole, "Save All"),
        12: (YesRole, "Yes"),
        13: (YesRole, "Yes to All"),
        14: (NoRole, "No"),
        15: (NoRole, "No to All"),
        16: (RejectRole, "Abort"),
        17: (AcceptRole, "Retry"),
        18: (AcceptRole, "Ignore"),
        19: (NoButton, "Button")
        }

    buttonClicked = QtSignal(object)

    def __init__(self, parent=None,
                 title="Primary text providing basic information and a suggestion",
                 text="Secondary text providing further details. Also includes information "
                      "that explains any unobvious consequences of actions.",
                 icon=None,
                 buttons=None):
        """Initialize a message dialog

        Args:
            title (str): title text
            text (str): message text
            icon (QIcon, QPixmap): dialog icon
            buttons (list): list of standard buttons
        """

        super(MessageDialog, self).__init__(parent)

        self._title = title
        self._text = text
        self._icon = None
        self._buttons = []

        self.__ui__()

        self.setIcon(icon)
        self.setStandardButtons(buttons if buttons else [])

    def __ui__(self):
        """Create UI components"""

        self._ui_icon = QtWidgets.QLabel(self)
        self._ui_icon.setAlignment(QtCore.Qt.AlignCenter)
        self._ui_icon.setGeometry(20, 18, 64, 64)

        self._ui_title = QtWidgets.QLabel(self._title)
        self._ui_title.setObjectName("g_message_title")
        self._ui_title.setWordWrap(True)
        self._ui_title.setIndent(88)

        self._ui_text = QtWidgets.QLabel(self._text)
        self._ui_text.setObjectName("g_message_text")
        self._ui_text.setWordWrap(True)
        self._ui_text.setIndent(88)

        self._ui_buttons_layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        self._ui_buttons_layout.setSpacing(6)
        self._ui_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_buttons_layout.addStretch(1)

        self._ui_buttons = QtWidgets.QWidget(self)
        self._ui_buttons.setMinimumHeight(30)
        self._ui_buttons.setLayout(self._ui_buttons_layout)

        self._ui_layout = QtWidgets.QVBoxLayout()
        self._ui_layout.setContentsMargins(12, 24, 12, 8)

        self._ui_layout.addWidget(self._ui_title, 0, QtCore.Qt.AlignTop)
        self._ui_layout.addWidget(self._ui_text, 1, QtCore.Qt.AlignTop)
        self._ui_layout.addWidget(self._ui_buttons, 0, QtCore.Qt.AlignBottom)

        self.setLayout(self._ui_layout)
        self._ui_icon.raise_()
        self.setWindowTitle(self._title if not OS_MAC else "")
        self.setMinimumSize(360, 60)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self._update_size()

    def title(self):
        """Get a dialog title"""

        return self._title

    def text(self):
        """Get a dialog text"""

        return self._text

    def icon(self):
        """Get a icon of dialog"""

        return QtGui.QIcon(self._icon)

    def setTitle(self, title):
        """Set dialog title

        Args:
            title (str): title
        """

        self._title = title
        self._ui_title.setText(self._title)

    def setText(self, text):
        """Text displayed in dialog

        Args:
            text (str): informative text
        """

        self._text = text
        self._ui_text.setText(self._text)

    def setIcon(self, icon):
        """Set dialog icon

        Args:
            icon (QIcon, QPixmap): icon of dialog
        """

        size = 56

        # pick a standard icon
        if icon in MessageDialog.Icon or icon is None:
            standard_icon = QtWidgets.QStyle.SP_MessageBoxInformation

            if icon == MessageDialog.Information:
                standard_icon = QtWidgets.QStyle.SP_MessageBoxInformation
            elif icon == MessageDialog.Question:
                standard_icon = QtWidgets.QStyle.SP_MessageBoxQuestion
            elif icon == MessageDialog.Warning:
                standard_icon = QtWidgets.QStyle.SP_MessageBoxWarning
            elif icon == MessageDialog.Critical:
                standard_icon = QtWidgets.QStyle.SP_MessageBoxCritical

            icon = QtWidgets.QApplication.style().standardIcon(standard_icon)

        if isinstance(icon, QtGui.QIcon):
            self._icon = icon.pixmap(size)

        if isinstance(icon, QtGui.QPixmap):
            self._icon = icon.scaledToWidth(size)

        self._ui_icon.setPixmap(self._icon)

    def buttons(self):
        """Returns a list of all the buttons that have been added to the message box."""

        return [item[3] for item in self._buttons]

    def button(self, button):
        """Returns a pointer corresponding to the standard button which,
        or 0 if the standard button doesn't exist in this message box.
        """
        for item in self._buttons:
            if item[2] == button:
                return item[3]

        return 0

    def buttonRole(self, button):
        """Returns the button role for the specified button. This function returns
        InvalidRole if button is 0 or has not been added to the message box.
        """

        for item in self._buttons:
            if item[3] == button:
                return item[2]

        return MessageDialog.InvalidRole

    def addButton(self, button, role=None):
        """Add button

        Args:
            button: button to add
            role: button role
        """

        if isinstance(button, str):
            name = button
            value = -1
        elif button in MessageDialog.StandardButton:
            name = MessageDialog.StandardButtonRoleName[button][1]
            role = button
            value = button
        elif isinstance(button, QtWidgets.QPushButton):
            name = button.text()
            value = -1
        else:
            raise Exception("Invalid argument passed, %s" % str(button))

        def triggered(_self, _btn):
            """Wrap button callback"""

            return lambda flag: _self.button_clicked(_btn)

        btn = button if isinstance(button, QtWidgets.QPushButton) else QtWidgets.QPushButton(name)
        btn.role = role
        btn.clicked.connect(triggered(self, btn))

        self._buttons.append((name, value, role, btn))
        self._ui_buttons_layout.addWidget(btn)
        self._update_size()

    def setStandardButtons(self, buttons):
        """Set a standard buttons

        Args:
            buttons (list): list of buttons with standard roles
        """

        if not buttons:
            return

        for button in buttons:
            if button not in MessageDialog.StandardButton:
                raise Exception("Button type is not standard")

            self.addButton(button)

    def button_clicked(self, button):
        """Button clicked proxy function"""

        self.buttonClicked.emit(button)
        self.done(button.role)

    def _update_size(self):
        """Update window size"""

        self.adjustSize()
        self.setFixedSize(self.size().width(), self.size().height())

    @staticmethod
    def warning(parent=None, title="Warning", text=""):
        """Warning dialog"""

        buttons = [MessageDialog.Ok]

        return MessageDialog(parent, title, text, MessageDialog.Warning, buttons)

    @staticmethod
    def critical(parent=None, title="Critical Problem", text=""):
        """Warning dialog"""

        buttons = [MessageDialog.Ok]

        return MessageDialog(parent, title, text, MessageDialog.Critical, buttons)

    @staticmethod
    def question(parent=None, title="Are you sure?", text=""):
        """Warning dialog"""

        buttons = [MessageDialog.Ok]

        return MessageDialog(parent, title, text, MessageDialog.Question, buttons)

    @staticmethod
    def information(parent=None, title="Information", text=""):
        """Warning dialog"""

        buttons = [MessageDialog.Ok]

        return MessageDialog(parent, title, text, MessageDialog.Information, buttons)
