# -*- coding: UTF-8 -*-
"""
    grail.application
    ~~~~~~~~~~~~~~~~~

    Extended GApplication class and add some grail specific methods
"""

from grailkit.ui import GApplication

from grail.ui import MainWindow


class Grail(GApplication):

    def __init__(self, argv):
        super(Grail, self).__init__(argv)

        self.main_window = MainWindow()
        self.main_window.show()

    def moreThanOneInstanceAllowed(self):
        """Do not allow multiple instances"""

        return False

    def anotherInstanceStarted(self):
        """Show a warning dialog"""

        # To-Do: replace with real dialog window
        print("Another instance of Grail launched")
