# -*- coding: UTF-8 -*-
"""
    grail.plugins.configurators
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Core configurators

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.core import Configurator
from grailkit.qt import List, ListItem, Switch, Application, Button, VLayout, Label, Spacer
from grailkit.bible import BibleHost, BibleHostError


class GeneralConfigurator(Configurator):
    """Configure general preferences"""

    id = 'general-configurator'
    name = 'General'
    author = 'Grail Team'
    description = 'General configuration page'

    def __init__(self, parent=None):
        super(GeneralConfigurator, self).__init__(parent)

        self.__ui__()

    def __ui__(self):

        self.ui_reset_btn = Button("Restore")
        self.ui_reset_btn.clicked.connect(self.restore_action)
        self.ui_reset_label = QLabel("Restore Grail to it's original state")

        self.ui_import_btn = Button("Import library")
        self.ui_import_btn.clicked.connect(self.import_action)
        self.ui_import_label = QLabel("Add songs from a library file.")

        self.ui_export_btn = Button("Export library")
        self.ui_export_btn.clicked.connect(self.export_action)
        self.ui_export_label = QLabel("Save my library of songs to file.")

        self.ui_layout = QGridLayout()

        self.ui_layout.addWidget(self.ui_reset_btn, 0, 1, Qt.AlignRight)
        self.ui_layout.addWidget(self.ui_reset_label, 0, 0, Qt.AlignLeft)

        self.ui_layout.addWidget(self.ui_import_btn, 1, 1, Qt.AlignRight)
        self.ui_layout.addWidget(self.ui_import_label, 1, 0, Qt.AlignLeft)

        self.ui_layout.addWidget(self.ui_export_btn, 2, 1, Qt.AlignRight)
        self.ui_layout.addWidget(self.ui_export_label, 2, 0, Qt.AlignLeft)

        self.ui_layout.addWidget(Switch(), 3, 1, Qt.AlignRight)
        self.ui_layout.addWidget(Label("Continue last project on startup"), 3, 0, Qt.AlignLeft)

        self.ui_layout.addWidget(Spacer(), 4, 0)
        self.ui_layout.setColumnStretch(0, 1)
        self.ui_layout.setVerticalSpacing(24)

        self.setLayout(self.ui_layout)

    def restore_action(self):
        """Restore Grail to it's factory settings.
        This menu_action will remove all songs and clear all preferences
        """

        # Todo: implement this
        pass

    def import_action(self):
        """Import a library of songs to grail"""

        path, ext = QFileDialog.getOpenFileName(self, "Import...", "", "*.grail-library")

        # Todo: implement this
        pass

    def export_action(self):
        """Create a library file"""

        library_name = "untitled"
        path, ext = QFileDialog.getSaveFileName(self, "Export...", library_name, "*.grail-library")

        # Todo: implement this
        pass


class BibleConfigurator(Configurator):
    """Configure bible preferences"""

    id = 'bible-configurator'
    name = 'Bible'
    author = 'Grail Team'
    description = 'Configuration page for bibles'

    def __init__(self, parent=None):
        super(BibleConfigurator, self).__init__(parent)

        self.__ui__()
        self._update_list()

    def __ui__(self):
        """Build UI"""

        self._ui_layout = VLayout()
        self._ui_list = List()
        self._ui_list.setObjectName('bible_list')

        self._ui_toolbar_label = Label("0 installed")
        self._ui_toolbar_label.setAlignment(Qt.AlignCenter)
        self._ui_toolbar_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_install_action = QAction(QIcon(':/icons/add.png'), 'Install', self)
        self._ui_install_action.setIconVisibleInMenu(True)
        self._ui_install_action.triggered.connect(self.install_action)

        self._ui_primary_action = QAction(QIcon(':/icons/save.png'), 'Set as primary', self)
        self._ui_primary_action.setIconVisibleInMenu(True)
        self._ui_primary_action.triggered.connect(self.primary_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("bible_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_install_action)
        self._ui_toolbar.addWidget(self._ui_toolbar_label)
        self._ui_toolbar.addAction(self._ui_primary_action)

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def install_action(self):
        """Install new bible"""

        path, ext = QFileDialog.getOpenFileName(self, "Open File...", "", "*.grail-bible")

        try:
            BibleHost.install(path)
        except BibleHostError as msg:
            print(msg)

        self._update_list()

    def primary_action(self):
        """Make installed bible primary in grail"""

        items = self._ui_list.selectedItems()

        if len(items) > 0:
            bible_id = items[0].bible_id

            Application.instance().settings.set('bible/default', bible_id)

        self._update_list()

    def _update_list(self):
        """Update list of installed bibles"""

        bibles = BibleHost.list()
        bible_selected_id = Application.instance().settings.get('bible/default', None)

        self._ui_list.clear()
        self._ui_toolbar_label.setText("%d installed" % len(bibles))

        for key in bibles:

            bible = bibles[key]

            item = ListItem()
            item.bible_id = bible.identifier
            item.setText("%s (%s)%s" % (bible.title, bible.identifier,
                                        " - selected" if bible_selected_id == bible.identifier else ""))

            self._ui_list.addItem(item)
