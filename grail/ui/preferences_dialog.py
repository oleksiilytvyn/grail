# -*- coding: UTF-8 -*-
"""
    grail.ui.preferences_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Global preferences dialog window and all panels displayed inside
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.ui import GDialog, GWidget, GListWidget, GListItem
from grailkit.bible import BibleHost


class PreferencesDialog(GDialog):
    """Global preferences dialog"""

    def __init__(self):
        super(PreferencesDialog, self).__init__()

        self.__ui__()

    def __ui__(self):

        self._ui_sidebar_layout = QVBoxLayout()
        self._ui_sidebar_layout.setSpacing(0)
        self._ui_sidebar_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_sidebar_list = GListWidget()
        self._ui_sidebar_list.setObjectName("preferences_tabs")
        self._ui_sidebar_list.setAlternatingRowColors(True)
        self._ui_sidebar_list.itemClicked.connect(self.page_clicked)

        self._ui_sidebar = QWidget()
        self._ui_sidebar.setLayout(self._ui_sidebar_layout)
        self._ui_sidebar_layout.addWidget(self._ui_sidebar_list)

        self._ui_panel = QStackedWidget()

        pages = [
            GeneralPanel,
            OSCInPanel,
            OSCOutPanel,
            BiblePanel
        ]

        for index, page in enumerate(pages):
            panel = page(self)

            item = GListItem(panel.name())
            item.index = index

            self._ui_sidebar_list.addItem(item)
            self._ui_panel.addWidget(panel)

        # splitter
        self._ui_splitter = QSplitter()
        self._ui_splitter.setObjectName("preferences_splitter")

        self._ui_splitter.addWidget(self._ui_sidebar)
        self._ui_splitter.addWidget(self._ui_panel)

        self._ui_panel.setCurrentIndex(0)

        self._ui_splitter.setCollapsible(0, False)
        self._ui_splitter.setCollapsible(1, False)
        self._ui_splitter.setHandleWidth(1)
        self._ui_splitter.setSizes([200, 400])
        self._ui_splitter.setStretchFactor(0, 0)
        self._ui_splitter.setStretchFactor(1, 1)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_layout.addWidget(self._ui_splitter)

        self.setLayout(self._ui_layout)

        self.setWindowIcon(QIcon(':/icons/32.png'))
        self.setWindowTitle('Preferences')
        self.setGeometry(300, 300, 600, 400)
        self.setMinimumSize(600, 400)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def page_clicked(self, item):

        index = item.index
        panel = self._ui_panel.widget(index)

        self._ui_panel.setCurrentIndex(index)
        panel.clicked()
        panel.update()


class Panel(GWidget):

    def __init__(self, parent=None):
        super(Panel, self).__init__()

        self.__ui__()

    def __ui__(self):
        """Create all widgets"""

        pass

    def name(self):
        """Returns a panel name that will be displayed in sidebar"""

        return "panel"

    def clicked(self):
        """This method called when this panel is opened"""

        pass


class GeneralPanel(Panel):

    def __init__(self, parent=None):
        super(GeneralPanel, self).__init__(parent)

    def __ui__(self):
        pass

    def name(self):
        return "General"


class BiblePanel(Panel):

    def __init__(self, parent=None):
        super(BiblePanel, self).__init__(parent)

        self._update_list()

    def name(self):
        """Returns tab name"""

        return "Bible"

    def __ui__(self):
        """Build UI"""

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_list = GListWidget()
        self._ui_list.setAlternatingRowColors(True)

        self._ui_toolbar_label = QLabel("0 installed")
        self._ui_toolbar_label.setAlignment(Qt.AlignCenter)
        self._ui_toolbar_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_install_action = QAction(QIcon(':/icons/add.png'), 'Install', self)
        self._ui_install_action.setIconVisibleInMenu(True)
        self._ui_install_action.triggered.connect(self.install_action)

        self._ui_primary_action = QAction(QIcon(':/icons/save.png'), 'Set as primary', self)
        self._ui_primary_action.setIconVisibleInMenu(True)
        self._ui_primary_action.triggered.connect(self.primary_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_install_action)
        self._ui_toolbar.addWidget(self._ui_toolbar_label)
        self._ui_toolbar.addAction(self._ui_primary_action)

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def install_action(self):
        pass

    def primary_action(self):
        pass

    def _update_list(self):
        """Update list of installed bibles"""

        bibles = BibleHost.list()

        self._ui_list.clear()
        self._ui_toolbar_label.setText("%d installed" % len(bibles))

        for bible in bibles:

            item = GListItem()
            item.setText(bible['name'])

            self._ui_list.addItem(item)


class OSCInPanel(Panel):

    def __init__(self, parent=None):
        super(OSCInPanel, self).__init__(parent)

    def name(self):
        return "OSC in"

    def __ui__(self):

        self._ui_label = QLabel("OSC Input not supported", self)
        self._ui_label.move(20, 20)

    def update(self):

        size = self._ui_label.size()
        box = self.size()

        self._ui_label.move(box.width() / 2 - size.width() / 2, box.height() / 2 - size.height() / 2)


class OSCOutPanel(Panel):

    def __init__(self, parent=None):
        super(OSCOutPanel, self).__init__(parent)

    def name(self):
        return "OSC out"

    def __ui__(self):

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_list = GListWidget()
        self._ui_list.setAlternatingRowColors(True)

        self._ui_toolbar_label = QLabel("0 destinations")
        self._ui_toolbar_label.setAlignment(Qt.AlignCenter)
        self._ui_toolbar_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add destination', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addWidget(self._ui_toolbar_label)
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def add_action(self):
        pass
