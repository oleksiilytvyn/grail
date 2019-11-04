# -*- coding: UTF-8 -*-
"""
    grail.ui.preferences_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Global preferences dialog window and all panels displayed inside

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
from grail.qt import *
from grail.core import Configurator


class PreferencesDialog(QtWidgets.QDialog):
    """Application preferences dialog"""

    def __init__(self):
        super(PreferencesDialog, self).__init__()

        self.app = Application.instance()
        self.app.signals.connect('/app/close', self.close)

        self.__ui__()

    def __ui__(self):
        """Build UI"""

        self._ui_sidebar_layout = QtWidgets.QVBoxLayout()

        self._ui_sidebar_list = QtWidgets.QListWidget()
        self._ui_sidebar_list.itemClicked.connect(self.page_clicked)

        self._ui_sidebar = QtWidgets.QWidget()
        self._ui_sidebar.setLayout(self._ui_sidebar_layout)
        self._ui_sidebar_layout.addWidget(self._ui_sidebar_list)

        self._ui_panel = QtWidgets.QStackedWidget()

        plugins = Configurator.plugins(sort_key=lambda x: x.index, sort_reverse=False)

        for index, plug in enumerate(plugins):
            panel = plug()

            item = QtWidgets.QListWidgetItem(plug.name)
            item.index = index

            self._ui_sidebar_list.addItem(item)
            self._ui_panel.addWidget(panel)

        # splitter
        self._ui_splitter = QtWidgets.QSplitter()

        self._ui_splitter.addWidget(self._ui_sidebar)
        self._ui_splitter.addWidget(self._ui_panel)

        self._ui_panel.setCurrentIndex(0)
        self._ui_sidebar_list.setCurrentItem(self._ui_sidebar_list.item(0))

        self._ui_splitter.setCollapsible(0, False)
        self._ui_splitter.setCollapsible(1, False)
        self._ui_splitter.setHandleWidth(1)
        self._ui_splitter.setSizes([200, 400])
        self._ui_splitter.setStretchFactor(0, 0)
        self._ui_splitter.setStretchFactor(1, 1)

        self._ui_layout = QtWidgets.QVBoxLayout()
        self._ui_layout.addWidget(self._ui_splitter)

        self.setLayout(self._ui_layout)

        self.setWindowTitle('Preferences')
        self.setGeometry(300, 300, 600, 400)
        self.setMinimumSize(600, 400)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

    def page_clicked(self, item):
        """Page clicked menu_action"""

        index = item.index
        panel = self._ui_panel.widget(index)

        self._ui_panel.setCurrentIndex(index)

        panel.clicked()
        panel.update()
