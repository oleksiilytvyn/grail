# -*- coding: UTF-8 -*-
"""
    grail.application
    ~~~~~~~~~~~~~~~~~

    Extended GApplication class and add some grail specific methods
"""

from grailkit.project import Project
from grailkit.library import Library
from grailkit.bible import BibleHost
from grailkit.ui import GApplication, GMessageDialog

import grail
import grail.resources

from grail.ui import MainWindow, WelcomeDialog


class Grail(GApplication):

    def __init__(self, argv):
        super(Grail, self).__init__(argv)

        self._library_path = "library-path"

        self.setApplicationName("Grail")
        self.setApplicationVersion(grail.__version__)
        self.setOrganizationName("Grail")
        self.setOrganizationDomain("grailapp.com")
        self.setStyleSheetFile(":/stylesheet/grail.css")

        self.project = None
        self.library = None
        self.bible_host = None

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
        self.library = Library(self._library_path, create=True)
        self.bible_host = BibleHost()

        self.main_window = MainWindow(self)
        self.main_window.show()

        self.welcome_dialog.close()
