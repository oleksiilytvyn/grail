# -*- coding: UTF-8 -*-
"""
    grail.ui.main_window
    ~~~~~~~~~~~~~~~~~~~~

    Main window of Grail application
"""

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QMainWindow, QMenuBar, QAction, QDesktopWidget

from grailkit.util import *
from grailkit.ui import GAboutDialog

import grail


class MainWindow(QMainWindow):
    """
    Grail application class
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.project = None

        self.__ui__()

    def __ui__(self):
        """
        Initialize UI
        """

        # about dialog
        self.about_dialog = GAboutDialog(None, "Grail %s" % (grail.__version__,),
                                         "Copyright © 2014-2016 Grail Team.\nAll rights reserved.",
                                         QIcon(':/icons/256.png'))
        self.about_dialog.url_report = "http://grailapp.com/"
        self.about_dialog.url_help = "http://grailapp.com/help"

        # setup window
        self._ui_menubar()

        self.setWindowIcon(QIcon(':/icons/256.png'))
        self.setGeometry(300, 300, 800, 480)
        self.setMinimumSize(320, 240)
        self.setWindowTitle("Grail")
        self.center()
        self.show()

    def _ui_menubar(self):
        """
        Setup menu
        """

        self.ui_menubar = QMenuBar(self)

        # File
        self.ui_import_action = QAction('Import...', self)
        self.ui_export_action = QAction('Export...', self)

        self.ui_new_action = QAction('New project', self)
        self.ui_open_action = QAction('Open project', self)
        self.ui_save_action = QAction('Save project', self)
        self.ui_save_as_action = QAction('Save project as', self)

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
        pass

    def open_project(self):
        pass

    def save_project(self):
        pass

    def save_project_as(self):
        pass

    def about_action(self):
        """About dialog action"""

        self.about_dialog.show()
        self.about_dialog.raise_()
        self.about_dialog.setWindowState(self.about_dialog.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.about_dialog.activateWindow()

    def update_action(self):
        """Check for updates action"""

        # to-do: add a dialog to check for updates
        pass

    def open_web_action(self):
        """Open a grailapp.com in a browser"""

        url = QUrl("http://grailapp.com/")
        QDesktopServices.openUrl(url)

    def open_manual_action(self):
        """Open a manual in new window"""

        url = QUrl("http://grailapp.com/help")
        QDesktopServices.openUrl(url)

    def closeEvent(self, event):
        pass
