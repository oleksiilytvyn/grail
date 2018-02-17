# -*- coding: UTF-8 -*-
"""
    grail.plugins.console_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    View python console output & execute commands

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import sys
import traceback

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.qt import *
from grail.core import Viewer


class ConsoleViewer(Viewer):
    """Python console"""

    id = 'console'
    name = 'Console'
    author = 'Grail Team'
    description = 'Python console'

    def __init__(self, *args):
        super(ConsoleViewer, self).__init__(*args)

        self._locals = {'self': self}
        self._follow = not self.get('follow', default=True)

        self.__ui__()
        self.follow_action()

        self.app.console.output.changed.connect(self._changed)

        print("Python %s" % sys.version)

    def __ui__(self):
        """Build UI"""

        self._ui_output = TextEdit()
        self._ui_output.setObjectName("ConsoleViewer_text")
        self._ui_output.setAcceptRichText(False)
        self._ui_output.setReadOnly(True)
        self._ui_output.setTextInteractionFlags(self._ui_output.textInteractionFlags() | Qt.TextSelectableByKeyboard)

        self._ui_input = TextEdit()
        self._ui_input.setPlaceholderText("Enter Python code")
        self._ui_input.setObjectName("ConsoleViewer_text")
        self._ui_input.setAcceptRichText(False)
        self._ui_input.keyPressEvent = self._key_pressed

        self._ui_splitter = Splitter(Qt.Vertical)
        self._ui_splitter.setHandleWidth(2)
        self._ui_splitter.addWidget(self._ui_output)
        self._ui_splitter.addWidget(self._ui_input)

        size = self._ui_splitter.height()
        self._ui_splitter.setSizes([size * 0.8, size * 0.2])
        self._ui_splitter.setCollapsible(0, False)

        self._ui_label = Label("Console")
        self._ui_label.setObjectName("ConsoleViewer_label")
        self._ui_label.setAlignment(Qt.AlignCenter)
        self._ui_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(QIcon(':/rc/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_follow_action = QToolButton()
        self._ui_follow_action.setText("Enter")
        self._ui_follow_action.setIcon(QIcon(':/rc/at.png'))
        self._ui_follow_action.clicked.connect(self.follow_action)

        self._ui_run_action = QToolButton()
        self._ui_run_action.setText("Run")
        self._ui_run_action.setIcon(QIcon(':/rc/play.png'))
        self._ui_run_action.clicked.connect(self.run_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.setObjectName("ConsoleViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(self._ui_label)
        self._ui_toolbar.addWidget(self._ui_follow_action)
        self._ui_toolbar.addWidget(self._ui_run_action)

        self._ui_layout = VLayout()
        self._ui_layout.addWidget(self._ui_splitter)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def run_action(self):
        """Execute text as python code"""

        try:
            code = str(self._ui_input.toPlainText())
            print('>>', code)

            try:
                value = eval(code, globals(), self._locals)

                print('->', value)
            except:
                exec(code, globals(), self._locals)

            self._ui_input.setPlainText("")
        except Exception as e:
            stack = traceback.extract_stack()[:-3] + traceback.extract_tb(e.__traceback__)
            pretty = traceback.format_list(stack)

            print(''.join(pretty) + '\n  {} {}'.format(e.__class__, e))

    def follow_action(self):
        """Execute on enter press"""

        self._follow = not self._follow

        # store property
        self.set('follow', self._follow)

        if self._follow:
            self._ui_follow_action.setIcon(Icon.colored(':/rc/at.png', QColor('#aeca4b'), QColor('#e3e3e3')))
        else:
            self._ui_follow_action.setIcon(QIcon(':/rc/at.png'))

    def _changed(self):
        """Console output changed"""

        self._ui_output.setPlainText(self.app.console.output.read())
        scrollbar = self._ui_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _key_pressed(self, event):
        """Process key event on  console input"""

        if (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return) and self._follow:
            self.run_action()
        else:
            QTextEdit.keyPressEvent(self._ui_input, event)
