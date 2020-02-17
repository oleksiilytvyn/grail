# -*- coding: UTF-8 -*-
"""
    grail.application
    ~~~~~~~~~~~~~~~~~

    Main Grail application instance class

    :copyright: (c) 2016-2020 by Oleksii Lytvyn (http://alexlitvin.name)
    :license: GNU, see LICENSE for more details.
"""
import io
import os
import re
import sys
import logging
import tempfile

from grailkit.dna import SettingsFile, Project, Library, ProjectError, DNAError
from grailkit.bible import BibleHost
from grailkit.core import Signalable, Signal

import grail
import grail.resources

from grail.qt import *
from grail.ui import MainWindow, WelcomeDialog
from grail.core import OSCHost, Viewer, Configurator, Plugin

# load internal plugins and viewers
from grail.plugins import *


class Grail(QtWidgets.QApplication):
    """Main application class"""

    def __init__(self, argv):
        super(Grail, self).__init__(argv)

        self._socket = QtNetwork.QLocalSocket()
        self._socket.connectToServer(grail.GUID, QtCore.QIODevice.ReadOnly)
        self._socket_connected = self._socket.waitForConnected()

        self._server = QtNetwork.QLocalServer()
        self._server.listen(grail.GUID)

        self._sys_exception_handler = sys.excepthook
        self.setQuitOnLastWindowClosed(True)
        self.lastWindowClosed.connect(self._closed)

        self.setApplicationName(grail.APPLICATION_NAME)
        self.setApplicationVersion(grail.__version__)
        self.setOrganizationName(grail.ORGANISATION_NAME)
        self.setOrganizationDomain(grail.ORGANISATION_DOMAIN)
        self.stylesheet = ""

        # set a exception handler
        sys.excepthook = self.unhandled_exception

        # fix for retina displays
        if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
            self.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

        # fix styles
        self.setStyle(_ProxyStyle())

        # use GTK style if available
        for style in QtWidgets.QStyleFactory.keys():
            if "gtk" in style.lower():
                self.setStyle(QtWidgets.QStyleFactory.create("gtk"))

        self._bind_stylesheet()

        # prevent from running more than one instance
        if not self.more_than_one_instance_allowed and self.is_already_running():
            self.another_instance_started()
            self.quit()

        BibleHost.setup()

        for plug in Plugin.plugins() + Viewer.plugins() + Configurator.plugins():
            plug.loaded()

        # Disable logging
        root_logger = logging.getLogger()
        root_logger.disabled = not grail.DEBUG

        self._plugins = []
        self._actions = []
        self._settings = SettingsFile(grail.SETTINGS_PATH, create=True)
        self._osc_host = OSCHost(self)
        self._midi_host = None
        self._project = None
        self._library = None
        self._bible = None
        self._signals = Signalable()
        self._launched = False

        self.change_bible(self.settings.get('bible/default', ""))

        self.main_window = None
        self.welcome_dialog = WelcomeDialog(self)

        # open last project instantly
        path = self.settings.get('project/last', default='')

        if self.settings.get('project/continue', default=False) and os.path.isfile(path):
            self.open(path, create=False)
        else:
            self.welcome_dialog.show()

        # console args
        create = '-c' in argv
        path = argv[1] if len(argv) >= 2 else None

        if path is not None:
            self.open(path, create=create)

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

    def _bind_stylesheet(self):
        """Get the application stylesheet

        Returns: stylesheet string
        """

        def read_stylesheet(file_path):
            """Read and return stylesheet file contents

            Args:
                file_path (str): path to stylesheet file
            """

            if not file_path:
                return ""

            data = ""
            stream = QtCore.QFile(file_path)

            if stream.open(QtCore.QFile.ReadOnly):
                data = str(stream.readAll())
                stream.close()

            return re.sub(r'(\\n)|(\\r)|(\\t)', '', data)[2:-1]

        self.stylesheet = read_stylesheet(":/qt/theme.css")

        self.setStyleSheet(self.stylesheet)

    def quit(self):
        """Quit application and close all connections"""

        QtWidgets.QApplication.quit()
        sys.exit(0)

    def unhandled_exception(self, exception_type, value, traceback_object):
        """Re-implement this method to catch exceptions"""

        self._sys_exception_handler(exception_type, value, traceback_object)

    def is_already_running(self):
        """Check for another instances of this application

        Returns: bool
        """

        return self._socket_connected

    @property
    def more_than_one_instance_allowed(self):
        """Do not allow multiple instances"""

        return False

    def another_instance_started(self):
        """Show a warning dialog when user try to
        launch multiple instances of Grail
        """

        message = MessageDialog(title="Grail already launched",
                                text="Close previously opened Grail and try again",
                                icon=MessageDialog.Critical)
        message.exec_()

    def open(self, path: str, create: bool = False):
        """Open a file"""

        project = False

        try:
            project = Project(path, create=create)
        except ProjectError:
            pass
        except DNAError:
            pass

        if project is False or not path or len(path) == 0:
            message = MessageDialog(title="Can't open file",
                                    text="File at location %s not exists." % path,
                                    icon=MessageDialog.Critical)
            message.exec_()

            return False

        if self.main_window:
            self.welcome_dialog.show()  # trick for keeping Qt alive
            self.main_window.close()

        self._project = project
        self._library = Library(grail.LIBRARY_PATH, create=True)

        self.settings.set('project/last', path)

        self.main_window = MainWindow(self)
        self.main_window.show()

        self.welcome_dialog.hide()

        if self._launched:
            for action in self._actions:
                del action

            for plug in self._plugins:
                plug.unloaded()
                del plug

        self._plugins = []
        self._actions = []

        # launch plugins and store them into list
        # this code prevents from GC on qt widgets
        for plug in Plugin.plugins():
            instance = plug()

            self._plugins.append(instance)

        self._launched = True

    def _closed(self):
        """Called when all windows closed"""

        for plug in Plugin.plugins() + Viewer.plugins() + Configurator.plugins():
            plug.unloaded()

        if self._library:
            self._library.close()

        if self._settings:
            self._settings.close()

        self.quit()

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
            _file_id, path = tempfile.mkstemp(prefix='bible-', suffix='.grail-bible')
            _file = os.fdopen(_file_id, 'w')
            _file.close()

            # remove empty file for qt to create a file at same place
            os.remove(path)

            # copy file from qt resource to local file system
            ref = QtCore.QFile(':default/bible-en-kjv.grail-bible')
            ref.copy(path)
            ref.close()

            BibleHost.install(path, replace=True)

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

    @classmethod
    def instance(cls):
        """Get instance of Application

        Returns: instance of QCoreApplication or Application
        """

        return QtCore.QCoreApplication.instance()


class _ProxyStyle(QtWidgets.QProxyStyle):
    """Fix stylesheet issues with custom style"""

    def styleHint(self, hint, option=None, widget=None, return_data=None):

        if QtWidgets.QStyle.SH_ComboBox_Popup == hint:
            return 0

        return QtWidgets.QProxyStyle.styleHint(self, hint, option, widget, return_data)


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

    def read(self, *args, **kwargs):
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
