# -*- coding: UTF-8 -*-
"""
    grail.application
    ~~~~~~~~~~~~~~~~~

    Extended GApplication class and add some grail specific methods

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import io
import os
import sys
import tempfile

from PyQt5.QtCore import QFile

from grailkit.dna import SettingsFile, Project, Library
from grailkit.bible import BibleHost
from grailkit.core import Signalable, Signal

import grail
import grail.resources

from grail.qt import Application, MessageDialog
from grail.ui import MainWindow, WelcomeDialog
from grail.core import OSCHost
# load internal plugins and viewers
from grail.plugins import *


class Grail(Application):
    """Main application class"""

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
        self.setStyleSheetFile(":/qt/grail.css")

        self._plugins = []
        self._actions = []
        self._relaunch = False
        self._relaunch_args = []
        self._settings = SettingsFile(grail.SETTINGS_PATH, create=True)
        self._osc_host = OSCHost()
        self._midi_host = None
        self._project = None
        self._library = None
        self._bible = None
        self._signals = Signalable()

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

    @property
    def settings(self):
        """Returns global grail settings"""

        return self._settings

    @property
    def project(self):
        """Returns DNAProject instance"""

        return self._project

    @property
    def bible(self):
        """Returns Bible instance"""

        return self._bible

    @property
    def library(self):
        """Returns Grail library"""

        return self._library

    @property
    def signals(self):
        """Returns signals"""

        return self._signals

    @property
    def osc(self):
        """Returns OSC in/out host"""

        return self._osc_host

    @property
    def midi(self):
        """Returns midi in/out host"""

        return self._midi_host

    @property
    def console(self):
        """Returns console object"""

        return Console.instance()

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

        self._project = Project(path, create=create)
        self._library = Library(grail.LIBRARY_PATH, create=True)

        self.settings.set('project/last', path)

        self.main_window = MainWindow(self)
        self.main_window.show()

        self.welcome_dialog.close()

        self._plugins = []
        self._actions = []

        # launch plugins and store them into list
        # this code prevents from GC on qt widgets
        for plug in Plugin.plugins():
            instance = plug()

            self._plugins.append(instance)

    def _closed(self):
        """Called when all windows closed"""

        for plug in Plugin.plugins() + Viewer.plugins() + Configurator.plugins():
            plug.unloaded()

        if self._library:
            self._library.close()

        if self._settings:
            self._settings.close()

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
            self._bible = BibleHost.get(bible_id)
        # if bible not selected but available
        # pick first bible
        elif len(bibles) > 0:
            for bible_id, bible in bibles.items():
                self._bible = BibleHost.get(bible_id)
                self.settings.set('bible/default', bible_id)
                break
        # if there is no bibles available
        # install default bible from resources
        else:
            _file, path = tempfile.mkstemp(prefix='bible-', suffix='.grail-bible')
            # remove empty file for qt to create a file at same place
            os.remove(path)

            # copy file from qt resource to local file system
            ref = QFile(':default/bible-en-kjv.grail-bible')
            ref.copy(path)
            ref.close()

            BibleHost.install(path, replace=True)
            # remove temporary file
            os.remove(path)

            bibles = BibleHost.list()

            for bible_id, bible in bibles.items():
                self._bible = BibleHost.get(bible_id)
                self.settings.set('bible/default', bible_id)

                break

    def register_action(self, plugin, name, fn):
        """Register global action

        Args:
            plugin (grail.core.Plugin): plugin instance
            name (str): name of action
            fn (callable): callback
        Raises:
            ValueError if one of arguments type isn't supported
        """

        if not callable(fn):
            raise ValueError("Given argument `fn` is not callable")

        if not isinstance(name, str):
            raise ValueError("Given argument `name` is not of type str")

        ref = CallableAction(fn)
        ref.name = name
        ref.plugin = plugin

        self._actions.append(ref)
        self.signals.emit('/app/actions')

    def actions(self):
        """Get list of actions"""

        return self._actions


class _ConsoleOutput(io.StringIO):
    """Wrapper for console output"""

    def __init__(self):
        super(_ConsoleOutput, self).__init__("")

        self.changed = Signal()

        self._stdout = sys.stdout
        self._output = ""

    def write(self, msg):
        """Write message to std output

        Args:
            msg (str, object): Message to add to console output
        """

        self._output += msg

        self.changed.emit()

    def read(self):
        """Read output of console"""

        return self._output

    def flush(self):
        """Clear console output"""

        self._stdout.flush()
        self._output = ""

        self.changed.emit()


class Console(object):
    """Take control over console input/output"""

    __instance = None

    def __init__(self):
        self._stdout = sys.stdout
        self._stdin = sys.stdin

        self._in = None
        self._out = _ConsoleOutput()

        sys.stdout = self._out
        sys.stdin = self._in

    @property
    def output(self):
        """Console output"""

        return self._out

    @property
    def input(self):
        """Console input"""

        return self._stdin

    @classmethod
    def instance(cls):
        """Return console instance"""

        if not cls.__instance:
            cls.__instance = cls()

        return cls.__instance


class CallableAction(object):
    """Wrapper for callable object"""

    def __init__(self, fn):
        self._fn = fn

    def __call__(self, *args, **kwargs):
        self._fn(*args, **kwargs)
