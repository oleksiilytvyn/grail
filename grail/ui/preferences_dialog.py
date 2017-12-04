# -*- coding: UTF-8 -*-
"""
    grail.ui.preferences_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Global preferences dialog window and all panels displayed inside

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStackedWidget

from grail.qt import Dialog, List, ListItem, Splitter, VLayout, Component, Icon

from grail.core import Configurator


class PreferencesDialog(Dialog):
    """Application preferences dialog"""

    def __init__(self):
        super(PreferencesDialog, self).__init__()

        self.__ui__()

    def __ui__(self):
        """Build UI"""

        self._ui_sidebar_layout = VLayout()

        self._ui_sidebar_list = List()
        self._ui_sidebar_list.itemClicked.connect(self.page_clicked)

        self._ui_sidebar = Component()
        self._ui_sidebar.setLayout(self._ui_sidebar_layout)
        self._ui_sidebar_layout.addWidget(self._ui_sidebar_list)

        self._ui_panel = QStackedWidget()

        plugins = Configurator.plugins(sort_key=lambda x: x.index, sort_reverse=False)

        for index, plug in enumerate(plugins):
            panel = plug()

            item = ListItem(plug.name)
            item.index = index

            self._ui_sidebar_list.addItem(item)
            self._ui_panel.addWidget(panel)

        # splitter
        self._ui_splitter = Splitter()

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

        self._ui_layout = VLayout()
        self._ui_layout.addWidget(self._ui_splitter)

        self.setLayout(self._ui_layout)

        self.setWindowIcon(Icon(':/icon/32.png'))
        self.setWindowTitle('Preferences')
        self.setGeometry(300, 300, 600, 400)
        self.setMinimumSize(600, 400)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def page_clicked(self, item):
        """Page clicked menu_action"""

        index = item.index
        panel = self._ui_panel.widget(index)

        self._ui_panel.setCurrentIndex(index)

        panel.clicked()
        panel.update()
