# -*- coding: UTF-8 -*-
"""
    grail.plugins.configurators
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Core configurators

    :copyright: (c) 2016-2020 by Oleksii Lytvyn (http://alexlitvin.name)
    :license: GNU, see LICENSE for more details.
"""

from grailkit import dna
from grailkit.bible import BibleHost, BibleHostError

from grail.qt import *
from grail.core import Configurator


class GeneralConfigurator(Configurator):
    """Configure general preferences"""

    id = 'general-configurator'
    name = 'General'
    index = -100
    author = 'Oleksii Lytvyn'
    description = 'General configuration page'

    def __init__(self, parent=None):
        super(GeneralConfigurator, self).__init__(parent)

        self.__ui__()

    def __ui__(self):

        self.ui_layout = QtWidgets.QGridLayout()

        # Reset
        self.ui_reset_btn = QtWidgets.QPushButton("Restore")
        self.ui_reset_btn.clicked.connect(self.restore_action)
        self.ui_reset_label = QtWidgets.QLabel("Restore Grail to it's original state")

        self.ui_layout.addWidget(self.ui_reset_btn, 0, 1, QtCore.Qt.AlignRight)
        self.ui_layout.addWidget(self.ui_reset_label, 0, 0, QtCore.Qt.AlignLeft)

        # Import
        self.ui_import_btn = QtWidgets.QPushButton("Import library")
        self.ui_import_btn.clicked.connect(self.import_action)
        self.ui_import_label = QtWidgets.QLabel("Add songs from a library file.")

        self.ui_layout.addWidget(self.ui_import_btn, 1, 1, QtCore.Qt.AlignRight)
        self.ui_layout.addWidget(self.ui_import_label, 1, 0, QtCore.Qt.AlignLeft)

        # Export
        self.ui_export_btn = QtWidgets.QPushButton("Export library")
        self.ui_export_btn.clicked.connect(self.export_action)
        self.ui_export_label = QtWidgets.QLabel("Save my library of songs to file.")

        self.ui_layout.addWidget(self.ui_export_btn, 2, 1, QtCore.Qt.AlignRight)
        self.ui_layout.addWidget(self.ui_export_label, 2, 0, QtCore.Qt.AlignLeft)

        # Continue last project
        cont_flag = self.app.settings.get('project/continue', default=False)
        self.ui_continue = QtWidgets.QPushButton("On" if cont_flag else "Off")
        self.ui_continue.clicked.connect(self.continue_action)
        self.ui_continue_label = QtWidgets.QLabel("Continue last project on startup")

        self.ui_layout.addWidget(self.ui_continue, 3, 1, QtCore.Qt.AlignRight)
        self.ui_layout.addWidget(self.ui_continue_label, 3, 0, QtCore.Qt.AlignLeft)

        self.ui_layout.addWidget(QSpacer(), 4, 0)
        self.ui_layout.setColumnStretch(0, 1)
        self.ui_layout.setVerticalSpacing(24)

        self.setLayout(self.ui_layout)

    def restore_action(self):
        """Restore Grail to it's factory settings.
        This menu_action will remove all songs and clear all preferences
        """

        message = MessageDialog(title="Restore settings",
                                text="Do you want to restore all setting and library to defaults?",
                                buttons=[MessageDialog.Cancel, MessageDialog.RestoreDefaults],
                                icon=MessageDialog.Warning)

        if message.exec_() != MessageDialog.RestoreDefaults:
            return False

        # clear library
        self.app.library.clear()

    def import_action(self):
        """Import a library of songs to grail"""

        path = QtGetOpenFileName(self, "Import...", QtDocumentsLocation, "*.grail-library")

        if not path:
            return False

        try:
            library = dna.Library(path, create=False)
            items = library.items()
            progress = ProgressDialog(title="Importing...", text="Importing items to library")
            progress.setAutoClose(True)
            progress.setMaximum(len(items))
            progress.show()

            for index, entity in enumerate(items):
                self.app.library.copy(entity)
                progress.setValue(index)

            MessageDialog.information(title="Import",
                                      text="Items from <b>%s</b> imported successfully." % path).exec_()
        except dna.DNAError:
            MessageDialog.warning(title="Import",
                                  text="Unable to import Grail Library...").exec_()

            return False

    def export_action(self):
        """Create a library file"""

        path = QtGetSaveFileName(self, "Export library...", QtDocumentsLocation, "*.grail-library")

        if not path:
            return False

        self.app.library.save_copy(path, create=True)

    def continue_action(self):
        """Continue last project"""
        flag = not self.app.settings.get('project/continue', default=False)

        self.ui_continue.setText("On" if flag else "Off")
        self.app.settings.set('project/continue', flag)


class BibleConfigurator(Configurator):
    """Configure bible preferences"""

    id = 'bible-configurator'
    name = 'Bible'
    index = -98
    author = 'Oleksii Lytvyn'
    description = 'Configuration page for bibles'

    def __init__(self, parent=None):
        super(BibleConfigurator, self).__init__(parent)

        self.__ui__()
        self._update_list()

    def __ui__(self):
        """Build UI"""

        self.setObjectName("BibleConfigurator")

        self._ui_layout = QtWidgets.QVBoxLayout()
        self._ui_list = QtWidgets.QListWidget()
        self._ui_list.setObjectName("BibleConfigurator_list")

        self._ui_toolbar_label = QtWidgets.QLabel("0 installed")
        self._ui_toolbar_label.setAlignment(QtCore.Qt.AlignCenter)
        self._ui_toolbar_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self._ui_install_action = QtWidgets.QAction(Icon(':/rc/add.png'), 'Install', self)
        self._ui_install_action.setIconVisibleInMenu(True)
        self._ui_install_action.triggered.connect(self.install_action)

        self._ui_uninstall_action = QtWidgets.QAction(Icon(':/rc/remove.png'), 'Uninstall', self)
        self._ui_uninstall_action.setIconVisibleInMenu(True)
        self._ui_uninstall_action.triggered.connect(self.uninstall_action)

        self._ui_primary_action = QtWidgets.QAction(Icon(':/rc/save.png'), 'Set as primary', self)
        self._ui_primary_action.setIconVisibleInMenu(True)
        self._ui_primary_action.triggered.connect(self.primary_action)

        self._ui_toolbar = QtWidgets.QToolBar()
        self._ui_toolbar.addAction(self._ui_install_action)
        self._ui_toolbar.addAction(self._ui_uninstall_action)
        self._ui_toolbar.addWidget(self._ui_toolbar_label)
        self._ui_toolbar.addAction(self._ui_primary_action)

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def install_action(self):
        """Install new bible"""

        path = QtGetOpenFileName(self, "Open File...", QtDocumentsLocation, "*.grail-bible")

        try:
            BibleHost.install(path)
        except BibleHostError as error:
            message = MessageDialog(title="Unable to install",
                                    text=str(error),
                                    icon=MessageDialog.Critical)
            message.exec_()

        self._update_list()

    def uninstall_action(self):
        """Remove previously added bible"""

        items = self._ui_list.selectedItems()

        if len(items) > 0:
            bible_id = items[0].bible_id
            current_id = self.app.settings.set('bible/default', bible_id)

            BibleHost.uninstall(bible_id)

            if bible_id == current_id:
                new_id = BibleHost.list()[0]
                self.app.settings.set('bible/default', new_id.identifier)

        self._update_list()

    def primary_action(self):
        """Make installed bible primary in grail"""

        items = self._ui_list.selectedItems()

        if len(items) > 0:
            bible_id = items[0].bible_id

            # change settings
            self.app.settings.set('bible/default', bible_id)
            # update bible object
            self.app.change_bible(bible_id)

        self._update_list()

    def _update_list(self):
        """Update list of installed bibles"""

        bibles = BibleHost.list()
        bible_selected_id = self.app.settings.get('bible/default', None)

        self._ui_list.clear()
        self._ui_toolbar_label.setText("%d installed" % len(bibles))

        for key in bibles:

            bible = bibles[key]

            item = QtWidgets.QListWidgetItem()
            item.bible_id = bible.identifier
            item.setText("%s (%s)%s" % (bible.title, bible.identifier,
                                        " - selected" if bible_selected_id == bible.identifier else ""))

            self._ui_list.addItem(item)
