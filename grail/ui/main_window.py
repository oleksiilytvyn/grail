# -*- coding: UTF-8 -*-
"""
    grail.ui.main_window
    ~~~~~~~~~~~~~~~~~~~~

    Main window of Grail application
"""

import os
import json

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.dna import DNA
from grailkit.util import *
from grailkit.ui import GAboutDialog, GMessageDialog
from grailkit.ui.gapplication import AppInstance

import grail
from grail.ui import PreviewEditor, LibraryEditor, PreferencesDialog, CuelistEditor


class MainWindow(QMainWindow):
    """
    Grail application class
    """

    def __init__(self, app=None):
        super(MainWindow, self).__init__()

        self.app = app
        self.project = self.app.project

        self.__ui__()

    def __ui__(self):
        """
        Initialize UI
        """

        # about dialog
        self.about_dialog = GAboutDialog(None, "Grail %s" % (grail.__version__,),
                                         "Copyright © 2014-2016 Grail Team.\nAll rights reserved.",
                                         QIcon(':/icon/256.png'))
        self.about_dialog.url_report = "http://grailapp.com/"
        self.about_dialog.url_help = "http://grailapp.com/help"

        self.preferences_dialog = PreferencesDialog()

        self._ui_menubar()

        self.ui_library = LibraryEditor(self.app)
        self.ui_cuelist = CuelistEditor(self.app)
        self.ui_preview = PreviewEditor(self.app)

        # splitter
        self._ui_splitter = QSplitter()
        self._ui_splitter.setObjectName("main_splitter")
        self._ui_splitter.addWidget(self.ui_library)
        self._ui_splitter.addWidget(self.ui_cuelist)
        self._ui_splitter.addWidget(self.ui_preview)

        self._ui_splitter.setCollapsible(0, False)
        self._ui_splitter.setCollapsible(2, False)
        self._ui_splitter.setHandleWidth(1)
        self._ui_splitter.setSizes([self._ui_splitter.rect().width() / 3] * 3)

        self.setCentralWidget(self._ui_splitter)
        self.setWindowIcon(QIcon(':/icon/256.png'))
        self.setGeometry(300, 300, 800, 480)
        self.setMinimumSize(320, 240)
        self.setWindowTitle("%s - Grail" % (self.app.project.name,))
        self.center()
        self.show()

    def _ui_menubar(self):
        """
        Setup menu
        """

        self.ui_menubar = QMenuBar(self)

        # File
        self.ui_import_action = QAction('Import...', self)
        self.ui_import_action.triggered.connect(self.import_action)
        self.ui_export_action = QAction('Export...', self)
        self.ui_export_action.triggered.connect(self.export_action)

        self.ui_new_action = QAction('New project', self)
        self.ui_new_action.triggered.connect(self.new_project)
        self.ui_open_action = QAction('Open project', self)
        self.ui_open_action.triggered.connect(self.open_project)
        self.ui_save_action = QAction('Save project', self)
        self.ui_save_action.triggered.connect(self.save_project)
        self.ui_save_as_action = QAction('Save project as', self)
        self.ui_save_as_action.triggered.connect(self.save_project_as)

        self.ui_quit_action = QAction('Quit', self)
        self.ui_quit_action.triggered.connect(self.close)

        # Edit
        self.ui_cut_action = QAction('Cut', self)
        self.ui_copy_action = QAction('Copy', self)
        self.ui_paste_action = QAction('Paste', self)
        self.ui_duplicate_action = QAction('Duplicate', self)
        self.ui_delete_action = QAction('Delete', self)

        self.ui_add_song_action = QAction('Add new Song', self)

        # Controls
        self.ui_go_action = QAction('Go', self)
        self.ui_go_to_action = QAction('Go to Cue', self)
        self.ui_blackout_action = QAction('Blackout', self)
        self.ui_next_cue_action = QAction('Next cue', self)
        self.ui_previous_cue_action = QAction('Previous cue', self)
        self.ui_last_cue_action = QAction('Go to last cue', self)
        self.ui_first_cue_action = QAction('Go to first cue', self)

        # Options
        self.ui_edit_osc_action = QAction('Edit OSC map', self)
        self.ui_edit_key_action = QAction('Edit Key map', self)
        self.ui_lock_action = QAction('Lock', self)
        self.ui_preferences_action = QAction('Preferences', self)
        self.ui_preferences_action.triggered.connect(self.preferences_action)

        # Help
        self.ui_about_action = QAction('About Grail', self)
        self.ui_about_action.triggered.connect(self.about_action)

        self.ui_updates_action = QAction('Check for updates', self)
        self.ui_updates_action.triggered.connect(self.update_action)

        self.ui_open_web_action = QAction('Visit grailapp.com', self)
        self.ui_open_web_action.triggered.connect(self.open_web_action)

        self.ui_open_manual_action = QAction('View manual', self)
        self.ui_open_manual_action.triggered.connect(self.open_manual_action)

        # Output
        self.ui_disable_output_action = QAction('Disabled', self)
        self.ui_show_test_card_action = QAction('Show Test Card', self)
        self.ui_output_preferences_action = QAction('Advanced Preferences', self)

        # File menu
        self.ui_menu_file = self.ui_menubar.addMenu('&File')
        self.ui_menu_file.addAction(self.ui_new_action)
        self.ui_menu_file.addAction(self.ui_open_action)
        self.ui_menu_file.addSeparator()
        self.ui_menu_file.addAction(self.ui_save_action)
        self.ui_menu_file.addAction(self.ui_save_as_action)
        self.ui_menu_file.addSeparator()
        self.ui_menu_file.addAction(self.ui_import_action)
        self.ui_menu_file.addAction(self.ui_export_action)
        self.ui_menu_file.addSeparator()
        self.ui_menu_file.addAction(self.ui_quit_action)

        # Edit menu
        self.ui_menu_edit = self.ui_menubar.addMenu('&Edit')
        self.ui_menu_edit.addAction(self.ui_cut_action)
        self.ui_menu_edit.addAction(self.ui_copy_action)
        self.ui_menu_edit.addAction(self.ui_paste_action)
        self.ui_menu_edit.addAction(self.ui_duplicate_action)
        self.ui_menu_edit.addAction(self.ui_delete_action)
        self.ui_menu_edit.addSeparator()
        self.ui_menu_edit.addAction(self.ui_add_song_action)

        # Controls menu
        self.ui_menu_controls = self.ui_menubar.addMenu('&Controls')
        self.ui_menu_controls.addAction(self.ui_go_action)
        self.ui_menu_controls.addAction(self.ui_go_to_action)
        self.ui_menu_controls.addAction(self.ui_blackout_action)
        self.ui_menu_controls.addSeparator()
        self.ui_menu_controls.addAction(self.ui_previous_cue_action)
        self.ui_menu_controls.addAction(self.ui_next_cue_action)
        self.ui_menu_controls.addAction(self.ui_first_cue_action)
        self.ui_menu_controls.addAction(self.ui_last_cue_action)

        # View menu
        self.ui_menu_view = self.ui_menubar.addMenu('&View')

        # Options menu
        self.ui_menu_options = self.ui_menubar.addMenu('&Options')
        self.ui_menu_options.addAction(self.ui_edit_osc_action)
        self.ui_menu_options.addAction(self.ui_edit_key_action)
        self.ui_menu_options.addSeparator()
        self.ui_menu_options.addAction(self.ui_lock_action)

        if not OS_MAC:
            self.ui_menu_options.addSeparator()

        self.ui_menu_options.addAction(self.ui_preferences_action)

        # Output menu
        self.ui_menu_output = self.ui_menubar.addMenu('&Output')
        self.ui_menu_output.addAction(self.ui_disable_output_action)
        self.ui_menu_output.addSeparator()
        self.ui_menu_output.addAction(self.ui_show_test_card_action)
        self.ui_menu_output.addAction(self.ui_output_preferences_action)

        # Help menu
        self.ui_menu_help = self.ui_menubar.addMenu('&Help')
        self.ui_menu_help.addAction(self.ui_open_manual_action)
        self.ui_menu_help.addAction(self.ui_open_web_action)
        self.ui_menu_help.addSeparator()
        self.ui_menu_help.addAction(self.ui_updates_action)

        if not OS_MAC:
            self.ui_menu_help.addSeparator()

        self.ui_menu_help.addAction(self.ui_about_action)

        if not OS_MAC:
            self.setMenuBar(self.ui_menubar)

    def center(self):
        """Move window to the center of current screen"""

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

        self.move(qr.topLeft())

    def new_project(self):
        """Create a new project"""

        project_name = "untitled"
        path, ext = QFileDialog.getSaveFileName(self, "New project", project_name, "*.grail")

        if path:
            self.app.open(path, create=True)

    def open_project(self):
        """Open an existing file"""

        path, ext = QFileDialog.getOpenFileName(self, "Open File...", "", "*.grail")

        if path:
            self.app.open(path, create=False)

    def save_project(self):
        """Save current project"""

        self.project.save()

    def save_project_as(self):
        """Save current project as another project"""

        project_name = "%s copy" % (self.project.name, )
        path, ext = QFileDialog.getSaveFileName(self, "Save project as", project_name, "*.grail")

        self.project.save_copy(path)

    def import_action(self):
        """Import data into Grail library or current project"""

        path, ext = QFileDialog.getOpenFileName(self, "Import...", "", "*")
        ext = path.split('.')[-1]

        if ext == 'grail':
            print("Import of grail files not supported")
        elif ext == 'grail-library':
            print("Import of grail library files not supported")
        elif ext == 'grail-bible':
            print("Import of grail bible files not supported")
        else:
            self._import_json(path)

    def _import_json(self, path):
        """Import json file"""

        lib = self.app.library

        def json_key(obj, key, default=""):
            if obj:
                return obj[key] if key in obj else default
            else:
                return default

        try:
            with open(path) as data_file:
                data = json.load(data_file)

                for item in data:
                    if 'name' not in item:
                        continue

                    song = lib.create(json_key(item, 'name', 'Untitled'), entity_type=DNA.TYPE_SONG)
                    song.year = json_key(item, 'year', 2000)
                    song.album = json_key(item, 'album', 'Unknown')
                    song.artist = json_key(item, 'artist', 'Unknown')
                    song.lyrics = json_key(item, 'lyrics', '')
                    song.update()

            return True
        except ValueError:
            pass

        return False

    def export_action(self):
        """Export library or project"""

        project_name = "untitled"
        path, ext = QFileDialog.getSaveFileName(self, "Export...", project_name, "*.grail")

        # to-do: implement this

    def about_action(self):
        """About dialog action"""

        self.about_dialog.show()
        self.about_dialog.raise_()
        self.about_dialog.setWindowState(self.about_dialog.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.about_dialog.activateWindow()

    def update_action(self):
        """Check for updates action"""

        # to-do: add a dialog to check for updates
        message = GMessageDialog(title="No updates",
                                 text="Updates not available.",
                                 icon=GMessageDialog.Warning)
        message.exec_()

    def open_web_action(self):
        """Open a grailapp.com in a browser"""

        QDesktopServices.openUrl(QUrl("http://grailapp.com/"))

    def open_manual_action(self):
        """Open a manual in browser"""

        QDesktopServices.openUrl(QUrl("http://grailapp.com/help"))

    def preferences_action(self):
        """Open a preferences dialog"""

        self.preferences_dialog.show()
        self.preferences_dialog.raise_()
        self.preferences_dialog.setWindowState(self.preferences_dialog.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.preferences_dialog.activateWindow()

    def closeEvent(self, event):
        """Save project"""

        AppInstance().emit('/app/close')
        self.app.project.close()