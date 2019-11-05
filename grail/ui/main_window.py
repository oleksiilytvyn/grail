# -*- coding: UTF-8 -*-
"""
    grail.ui.main_window
    ~~~~~~~~~~~~~~~~~~~~

    Main window of Grail application

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
import json

from grailkit.dna import DNA, DNAError, Library
from grailkit.util import *
from grailkit.bible import BibleHost, BibleHostError

import grail
from grail.qt import *
from grail.ui import ActionsDialog, PreferencesDialog, ViewArranger, ProjectDialog, AboutDialog


class MainWindow(QtWidgets.QMainWindow):
    """Grail application class"""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()

        self.app = Application.instance()
        self.project = self.app.project

        self.__ui__()

    def __ui__(self):
        """Initialize UI"""

        # about dialog
        self.preferences_dialog = PreferencesDialog()
        self.actions_dialog = ActionsDialog()
        self.project_dialog = ProjectDialog()
        self.about_dialog = AboutDialog(None, "Grail %s" % (grail.__version__,),
                                        "Copyright © 2016-2019 Alex Litvin.\nAll rights reserved.\n\n"
                                        "http://grailapp.com/",
                                        QtGui.QIcon(':/icon/256.png'))

        self._ui_menubar()

        struct = self._compose()

        self.view_arranger = ViewArranger()
        self.view_arranger.compose(struct)
        self.view_arranger.updated.connect(self._arranger_updated)

        self.setCentralWidget(self.view_arranger)
        self.setWindowIcon(QtGui.QIcon(':/icon/256.png'))
        self.setGeometry(0, 0, 800, 600)
        self.setMinimumSize(320, 240)
        self.setWindowTitle("%s - Grail" % (self.app.project.location,))
        self.center()
        self.show()

        window = struct[0]

        if window:
            if default_key(window, 'maximized', False):
                self.setWindowState(QtCore.Qt.WindowMaximized)
            else:
                self.setGeometry(default_key(window, 'x', 0),
                                 default_key(window, 'y', 0),
                                 default_key(window, 'width', 0),
                                 default_key(window, 'height', 0))

    def _ui_menubar(self):
        """Setup menu"""

        self.ui_menubar = QtWidgets.QMenuBar(None)

        # File
        self.ui_import_action = QtWidgets.QAction('Import...', self)
        self.ui_import_action.triggered.connect(self.import_action)
        self.ui_export_action = QtWidgets.QAction('Export...', self)
        self.ui_export_action.triggered.connect(self.export_action)

        self.ui_new_action = QtWidgets.QAction('New project', self)
        self.ui_new_action.setShortcut("Ctrl+N")
        self.ui_new_action.triggered.connect(self.new_project)
        self.ui_open_action = QtWidgets.QAction('Open project', self)
        self.ui_open_action.setShortcut("Ctrl+O")
        self.ui_open_action.triggered.connect(self.open_project)
        self.ui_save_action = QtWidgets.QAction('Save project', self)
        self.ui_save_action.setShortcut("Ctrl+S")
        self.ui_save_action.triggered.connect(self.save_project)
        self.ui_save_as_action = QtWidgets.QAction('Save project as', self)
        self.ui_save_as_action.setShortcut("Ctrl+Shift+S")
        self.ui_save_as_action.triggered.connect(self.save_project_as)

        self.ui_quit_action = QtWidgets.QAction('Quit', self)
        self.ui_quit_action.triggered.connect(self.close)

        self.ui_preferences_action = QtWidgets.QAction('Preferences', self)
        self.ui_preferences_action.setShortcut("Ctrl+P")
        self.ui_preferences_action.triggered.connect(self.preferences_action)

        self.ui_project_action = QtWidgets.QAction('Project info', self)
        self.ui_project_action.triggered.connect(self.project_action)

        self.ui_actions_action = QtWidgets.QAction('Show actions...', self)
        self.ui_actions_action.setShortcut("Ctrl+Alt+A")
        self.ui_actions_action.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.ui_actions_action.triggered.connect(self.open_actions_action)

        # Help
        self.ui_about_action = QtWidgets.QAction('About Grail', self)
        self.ui_about_action.triggered.connect(self.about_action)

        self.ui_open_web_action = QtWidgets.QAction('Visit grailapp.com', self)
        self.ui_open_web_action.triggered.connect(
            lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://grailapp.com/")))

        self.ui_open_manual_action = QtWidgets.QAction('View manual', self)
        self.ui_open_manual_action.triggered.connect(
            lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://grailapp.com/help")))

        # File menu
        self.ui_menu_file = self.ui_menubar.addMenu('File')
        self.ui_menu_file.addAction(self.ui_new_action)
        self.ui_menu_file.addAction(self.ui_open_action)
        self.ui_menu_file.addSeparator()
        self.ui_menu_file.addAction(self.ui_save_action)
        self.ui_menu_file.addAction(self.ui_save_as_action)
        self.ui_menu_file.addSeparator()
        self.ui_menu_file.addAction(self.ui_import_action)
        self.ui_menu_file.addAction(self.ui_export_action)
        self.ui_menu_file.addSeparator()
        self.ui_menu_file.addAction(self.ui_preferences_action)
        self.ui_menu_file.addAction(self.ui_project_action)
        self.ui_menu_file.addAction(self.ui_quit_action)

        # Action menu
        self.ui_menu_action = self.ui_menubar.addMenu('Action')
        self.ui_menu_action.addAction(self.ui_actions_action)

        # Help menu
        self.ui_menu_help = self.ui_menubar.addMenu('Help')
        self.ui_menu_help.addAction(self.ui_open_manual_action)
        self.ui_menu_help.addAction(self.ui_open_web_action)

        if not OS_MAC:
            self.ui_menu_help.addSeparator()

        self.ui_menu_help.addAction(self.ui_about_action)

        if not OS_MAC:
            self.setMenuBar(self.ui_menubar)

    def _compose(self, _root=None, _depth=1):
        """Create structure from project nodes"""

        # default structure
        default = [
                {
                    "layout/orientation": "horizontal",
                    "layout/type": "layout",
                    "width": 1280,
                    "height": 751,
                    "x": 0,
                    "y": 0
                },
                {
                    "view/id": "library",
                    "width": 311,
                    "height": 751,
                    "x": 0,
                    "y": 0
                },
                {
                    "view/id": "cuelist",
                    "width": 370,
                    "height": 751,
                    "x": 0,
                    "y": 0
                },
                {
                    "view/id": "time",
                    "width": 278,
                    "height": 751,
                    "x": 0,
                    "y": 0
                }
            ]
        structure = []

        if _root is None:
            entities = self.project.dna.entities(filter_type=DNA.TYPE_LAYOUT, filter_parent=0, filter_keyword="Layout")

            if len(entities) == 0:
                return default
            else:
                layout = entities[0]
        else:
            layout = _root

        structure.append({
                "layout/orientation": layout.get("layout/orientation", default="horizontal"),
                "layout/type": layout.get("layout/type", default="layout"),
                "width": layout.get("width", default=100),
                "height": layout.get("height", default=100),
                "x": layout.get("x", default=0),
                "y": layout.get("y", default=0),
                "maximized": layout.get("maximized", default=False)
            })

        for entity in layout.childs():
            if entity.type == DNA.TYPE_LAYOUT:
                structure.append(self._compose(entity, _depth + 1))
            elif entity.type == DNA.TYPE_VIEW:
                structure.append(entity.properties())

        return default if _root is None and len(structure) == 0 else structure

    def _arranger_updated(self, _structure=None, _root=None, _depth=1):
        """Layout of arranger is changed"""

        root = self.project.dna if not _root else _root
        structure = _structure if _structure is not None else self.view_arranger.decompose()
        layout = structure[0] if len(structure) > 0 else {}
        views = structure[1:] if len(structure) > 0 else []

        if not _root:
            # remove old layout entity
            entities = root.entities(filter_type=DNA.TYPE_LAYOUT,
                                     filter_parent=0,
                                     filter_keyword="Layout")

            for entity in entities:
                root.remove(entity.id)

            # create new layout entity
            entity = root.create(name="Layout",
                                 entity_type=DNA.TYPE_LAYOUT,
                                 parent=0,
                                 properties=layout)
            geometry = self.geometry()
            entity.set("x", geometry.x())
            entity.set("y", geometry.y())
            entity.set("width", geometry.width())
            entity.set("height", geometry.height())
            entity.set("maximized", self.isMaximized())
        else:
            # create child entity
            entity = root.create(name="Layout",
                                 entity_type=DNA.TYPE_LAYOUT,
                                 properties=layout)

        for view in views:
            if isinstance(view, list):
                self._arranger_updated(view, entity, _depth + 1)
            elif isinstance(view, dict):
                entity.create(name="View",
                              entity_type=DNA.TYPE_VIEW,
                              properties=view)

    def _geometry_changed(self):

        # Get window entity
        entities = self.project.dna.entities(filter_type=DNA.TYPE_LAYOUT, filter_parent=0, filter_keyword="Layout")

        if len(entities) > 0:
            window = entities[0]
            geometry = self.geometry()
            window.set("x", geometry.x())
            window.set("y", geometry.y())
            window.set("width", geometry.width())
            window.set("height", geometry.height())

    def resizeEvent(self, event):

        self._geometry_changed()

    def moveEvent(self, event):

        self._geometry_changed()

    def changeEvent(self, e):
        """Save window state"""

        entities = self.project.dna.entities(filter_type=DNA.TYPE_LAYOUT, filter_parent=0, filter_keyword="Layout")

        if len(entities) > 0:
            # Main window entity
            entities[0].set("maximized", self.isMaximized())

        QtWidgets.QMainWindow.changeEvent(self, e)

    def center(self):
        """Move window to the center of current screen"""

        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

        self.move(qr.topLeft())

    def new_project(self):
        """Create a new project"""

        project_name = "untitled"
        location = os.path.join(QtDocumentsLocation, project_name)

        path, ext = QtWidgets.QFileDialog.getSaveFileName(self, "New project", location, "*.grail")

        if path and len(path) != 0:
            self.app.open(path, create=True)

    def open_project(self):
        """Open an existing file"""

        path, ext = QtWidgets.QFileDialog.getOpenFileName(self, "Open File...", QtDocumentsLocation, "*.grail")

        if path and len(path) != 0:
            self.app.open(path, create=False)

    def save_project(self):
        """Save current project"""

        self._arranger_updated()
        self.project.save()

    def save_project_as(self):
        """Save current project as another project"""

        project_name = "%s copy" % (self.project.name, )
        location = os.path.join(QtDocumentsLocation, project_name)

        path, ext = QtWidgets.QFileDialog.getSaveFileName(self, "Save project as", location, "*.grail")

        self.project.save_copy(path)

    def open_actions_action(self):
        """Open actions dialog"""

        self.actions_dialog.showWindow()

    def import_action(self):
        """Import data into Grail library or current project"""

        path, ext = QtWidgets.QFileDialog.getOpenFileName(self, "Import...", QtDocumentsLocation,
                                                          "*.json, *.grail, *.grail-library")
        ext = path.split('.')[-1]
        message = ""

        if ext == 'grail':
            message = "Import of grail files not supported. Try to open as Grail Project."
        elif ext == 'grail-library':
            self._import_library(path)
        elif ext == 'grail-bible':
            self._import_bible(path)
        elif ext == 'json':
            self._import_json(path)
        else:
            message = "File format not supported."

        if message:
            dialog = MessageDialog(title="Import",
                                   text=message,
                                   icon=MessageDialog.Warning)
            dialog.exec_()

    def _import_json(self, path):
        """Import json file"""

        lib = self.app.library

        try:
            with open(path) as data_file:
                data = json.load(data_file)

                for item in data:
                    if 'name' not in item:
                        continue

                    song = lib.create(default_key(item, 'name', 'Untitled'), entity_type=DNA.TYPE_SONG)
                    song.year = default_key(item, 'year', 2000)
                    song.album = default_key(item, 'album', 'Unknown')
                    song.artist = default_key(item, 'artist', 'Unknown')
                    song.lyrics = default_key(item, 'lyrics', '')
                    song.update()

            return True
        except ValueError:
            return False

    def _import_library(self, path):
        """Import *.grail-library file"""

        if not path:
            return False

        try:
            library = Library(path, create=False)
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
        except DNAError:
            MessageDialog.warning(title="Import",
                                  text="Unable to import Grail Library...").exec_()

            return False

    def _import_bible(self, path):
        """Import and install new grail bible"""

        if not path:
            return False

        try:
            BibleHost.install(path)
        except BibleHostError as error:
            message = MessageDialog(title="Import",
                                    text=str(error),
                                    icon=MessageDialog.Warning)
            message.exec_()

        self._update_list()

    def export_action(self):
        """Export grail library as single file"""

        path, ext = QtWidgets.QFileDialog.getSaveFileName(self, "Export library...", QtDocumentsLocation, "*.grail-library")

        if not path:
            return False

        try:
            self.app.library.save_copy(path, create=True)
        except DNAError:
            message = MessageDialog(title="Export",
                                    text="Unable to export Grail Library to location %s.",
                                    icon=MessageDialog.Warning)
            message.exec_()

    def about_action(self):
        """About dialog menu_action"""

        self.about_dialog.showWindow()
        self.about_dialog.moveCenter()

    def preferences_action(self):
        """Open a preferences dialog"""

        self.preferences_dialog.showWindow()

    def project_action(self):
        """Open project information dialog"""

        self.project_dialog.showWindow()
        self.project_dialog.moveCenter()

    def closeEvent(self, event):
        """Save project"""

        self.app.signals.emit('/app/close')
        self.app.project.close()
