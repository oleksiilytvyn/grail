# -*- coding: UTF-8 -*-
"""
    grail.application
    ~~~~~~~~~~~~~~~~~

    Extended GApplication class and add some grail specific methods

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""

import os
import sys
import weakref
import tempfile

from PyQt5.QtCore import QFile, pyqtSignal

from grailkit.dna import SettingsFile, Project, Library
from grailkit.bible import BibleHost
from grailkit.qt import Application, MessageDialog

import grail
import grail.resources
from grail.ui import MainWindow, WelcomeDialog
from grail.core import Plugin, Viewer
from grail.core.executor import Executor

# load internal plugins and viewers
from grail.plugins import *


class Grail(Application):

    def __init__(self, argv):
        super(Grail, self).__init__(argv)

        BibleHost.setup()

        for plug in Plugin.plugins() + Viewer.plugins() + Configurator.plugins():
            plug.loaded()

        self.setQuitOnLastWindowClosed(True)
        self.lastWindowClosed.connect(self._closed)

        self.setApplicationName(grail.APPLICATION_NAME)
        self.setApplicationVersion(grail.__version__)
        self.setOrganizationName(grail.ORGANISATION_NAME)
        self.setOrganizationDomain(grail.ORGANISATION_DOMAIN)
        self.setStyleSheetFile(":/stylesheet/grail.css")

        self._slots = {}
        self._plugins = []
        self._relaunch = False
        self._relaunch_args = []

        self.settings = SettingsFile(grail.SETTINGS_PATH, create=True)
        self.osc_host = None
        self.project = None
        self.library = None
        self.bible = None
        self.executor = Executor()
        self.change_bible(self.settings.get('bible/default', ""))

        self.main_window = None

        self.welcome_dialog = WelcomeDialog(self)
        self.welcome_dialog.show()

        # open last project instantly
        if self.settings.get('project/continue', default=False):
            path = self.settings.get('project/last', default='')

            if os.path.isfile(path):
                self.open(path, create=False)

        # console args
        create = '-c' in argv
        path = argv[1] if len(argv) >= 2 else False

        if path:
            self.open(path, create)

    def moreThanOneInstanceAllowed(self):
        """Do not allow multiple instances"""

        return False

    def anotherInstanceStarted(self):
        """Show a warning dialog when user try to
        launch multiple instances of Grail
        """

        message = MessageDialog(title="Grail already launched",
                                text="Close previously opened Grail and try again",
                                icon=MessageDialog.Critical)
        message.exec_()

    def open(self, path, create=False):
        """Open a file"""

        if self.main_window:
            self._relaunch = True
            self._relaunch_args = [path, '-c']
            self.main_window.close()

        self.project = Project(path, create=create)
        self.library = Library(grail.LIBRARY_PATH, create=True)

        self.settings.set('project/last', path)

        self.main_window = MainWindow(self)
        self.main_window.show()

        self.welcome_dialog.close()

        self._plugins = []

        # launch plugins and store them in list
        # this code prevents from GC on qt widgets
        for plug in Plugin.plugins():
            instance = plug()

            self._plugins.append(instance)

    def _closed(self):
        """Called when all windows closed"""

        for plug in Plugin.plugins() + Viewer.plugins() + Configurator.plugins():
            plug.unloaded()

        if self.library:
            self.library.close()

        if self.settings:
            self.settings.close()

        if self._relaunch:
            python = sys.executable
            os.execl(python, python, sys.argv[0], *self._relaunch_args)

    def change_bible(self, bible_id):
        """Change bible on the fly

        Args:
            bible_id: bible identifier
        """

        bibles = BibleHost.list()

        # if bible already selected
        if bible_id in bibles:
            self.bible = BibleHost.get(bible_id)
        # if bible not selected but available
        # pick first bible
        elif len(bibles) > 0:
            for bible_id, bible in bibles.items():
                self.bible = BibleHost.get(bible_id)
                self.settings.set('bible/default', bible_id)
                break
        # if there is no bibles available
        # install default bible from resources
        else:
            _file, path = tempfile.mkstemp(prefix='bible-', suffix='.grail-bible')
            # remove empty file for qt to create a file at same place
            os.remove(path)

            ref = QFile(':default/bible-en-kjv.grail-bible')
            ref.copy(path)
            ref.close()

            BibleHost.install(path, replace=True)
            # remove temporary file
            os.remove(path)

            bibles = BibleHost.list()

            for bible_id, bible in bibles.items():
                self.bible = BibleHost.get(bible_id)
                self.settings.set('bible/default', bible_id)

                break

    def connect(self, message, fn):
        """Connect a message listener

        Args:
            message (str): message name
            fn (callable): function to call
        Raises:
            Exception when message or fn arguments is incorrect
        """

        if not message or not isinstance(message, str):
            raise Exception("Message argument is wrong")

        if not callable(fn):
            raise Exception("Given function is not callable.")

        if message not in self._slots:
            self._slots[message] = []

        self._slots[message].append(fn)

    def disconnect_signal(self, message, fn):
        """Disconnect given function from signal"""

        if message in self._slots:
            self._slots[message].remove(fn)

    def emit(self, message, *args):
        """Emit a message with arguments

        Args:
            message (str): message name
            *args: any arguments
        """

        if message in self._slots:
            for fn in self._slots[message]:
                fn(*args)
