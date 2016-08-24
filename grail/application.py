# -*- coding: UTF-8 -*-
"""
    grail.application
    ~~~~~~~~~~~~~~~~~

    Extended GApplication class and add some grail specific methods
"""

import os

from grailkit.project import Project, SettingsFile
from grailkit.library import Library
from grailkit.bible import BibleHost
from grailkit.ui import GApplication, GMessageDialog
from grailkit.util import path_appdata

import grail
import grail.resources

from grail.ui import MainWindow, WelcomeDialog

LIBRARY_PATH = os.path.join(path_appdata("grail"), "library.grail-library")
SETTINGS_PATH = os.path.join(path_appdata("grail"), "app.grail")


class Grail(GApplication):

    def __init__(self, argv):
        super(Grail, self).__init__(argv)

        BibleHost.setup()

        self.lastWindowClosed.connect(self._closed)

        self.setApplicationName(grail.APPLICATION_NAME)
        self.setApplicationVersion(grail.__version__)
        self.setOrganizationName(grail.ORGANISATION_NAME)
        self.setOrganizationDomain(grail.ORGANISATION_DOMAIN)
        self.setStyleSheetFile(":/stylesheet/grail.css")

        self.settings = SettingsFile(SETTINGS_PATH, create=True)
        self.project = None
        self.library = None

        self.main_window = None

        self.welcome_dialog = WelcomeDialog(self)
        self.welcome_dialog.show()

    def moreThanOneInstanceAllowed(self):
        """Do not allow multiple instances"""

        return False

    def anotherInstanceStarted(self):
        """Show a warning dialog when user try to
        launch multiple instances of Grail
        """

        message = GMessageDialog(title="Grail already launched",
                                 text="Close previously opened Grail and try again",
                                 icon=GMessageDialog.Critical)
        message.exec_()

    def open(self, path, create=False):
        """Open a file"""

        if self.main_window:
            self.main_window.close()

        self.project = Project(path, create=create)
        self.library = Library(LIBRARY_PATH, create=True)

        self.settings.set('last-project', path)

        self.main_window = MainWindow(self)
        self.main_window.show()

        self.welcome_dialog.close()

    def _closed(self):
        """Called when all windows closed"""

        self.library.close()
        self.settings.close()
