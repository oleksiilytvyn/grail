# -*- coding: UTF-8 -*-
"""
    grail.application
    ~~~~~~~~~~~~~~~~~

    Extended GApplication class and add some grail specific methods
"""

from grailkit.ui import GApplication, GMessageDialog

import grail
from grail.ui import MainWindow


class Grail(GApplication):

    def __init__(self, argv):
        super(Grail, self).__init__(argv)

        self.setApplicationName("Grail")
        self.setApplicationVersion(grail.__version__)
        self.setOrganizationName("Grail")
        self.setOrganizationDomain("grailapp.com")

        self.project = None
        self.library = None
        self.bible_manager = None

        self.main_window = MainWindow(self)
        self.main_window.show()

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
