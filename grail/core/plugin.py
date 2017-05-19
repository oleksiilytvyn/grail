# -*- coding: UTF-8 -*-
"""
    grail.core.plugin
    ~~~~~~~~~~~~~~~~~

    Plugin mechanism

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.qt import Component, Application, Splitter
from grailkit.plug import PluginRegistry


class _PluginMeta(object):
    """Plugin base class.
    All plugin types must have properties and methods defined by this class"""

    # unique plugin identifier
    id = 'dummy-plugin'
    # Plugin display name
    name = 'Default plugin'
    # Plugin author string
    author = 'Grail Team'
    # Plugin description string
    description = 'Dummy plugin that doesn\'t make anything useful'
    # Do not list this plugin if True
    private = False

    def __init__(self):
        """Initialize plugin"""

        super(_PluginMeta, self).__init__()

        # keep track of slot to delete them
        self.__slots = []
        self.__destroyed = False

    def emit(self, message, *args):
        """Emit a message with arguments

        Args:
            message (str): message name
            *args: any arguments
        """

        self.app.emit(message, *args)

    def connect(self, message, fn):
        """Connect a message listener

        Args:
            message (str): message name
            fn (callable): function to call
        """

        self.app.connect(message, fn)
        self.__slots.append([message, fn])

    def register_action(self, name, fn):
        """Register a global menu_action

        Actions added by this method can be accessed from menu_action list in application
        """

        pass

    def register_menu(self, location, fn=None, remove=False, index=-1, hotkey=None):
        """Register a menu item in global application menu

        Args:
            location (str): path to menu item and item name divided by '->'
            fn (callable): callback function

        Example:

            def callback():
                self._inspector_dialog.show()
                self._inspector_dialog.raise_()

            self.register_menu("View->Developer->Show inspector", callback)
        """

        main = self.app.main_window

        if main:
            main.register_menu(location, fn)

    def destroy(self):
        """Gracefully destroy widget and disconnect any signals
        Please call this method when you don't need instance anymore
        """

        # prevent from destructing several times
        if self.__destroyed:
            return None

        # clear slots as they keeping this object alive
        # and preventing from gc collection
        for slot in self.__slots:
            self.app.disconnect_signal(*slot)

        self.__slots = []

    @property
    def app(self):
        """Returns application instance"""

        return Application.instance()

    @classmethod
    def loaded(cls):
        """Called by plugin host when plugin is loaded"""

        pass

    @classmethod
    def unloaded(cls):
        """Called when plugin is unloaded"""

        pass

    @classmethod
    def plugins(cls):
        """Returns list of classes extended from Plugin in alphabetical order"""

        plugins = sorted(cls.__registry__, key=lambda x: str(x), reverse=True)

        return plugins


class Plugin(_PluginMeta, metaclass=PluginRegistry):
    """Abstract plugin"""

    def __init__(self):
        super(Plugin, self).__init__()


class _ComponentPluginRegistry(type(Component), PluginRegistry):
    """Meta class for visual plugins"""

    def __init__(cls, name, bases, attrs):
        type(Component).__init__(cls, name, bases, attrs)
        PluginRegistry.__init__(cls, name, bases, attrs)


class Viewer(Component, _PluginMeta, metaclass=_ComponentPluginRegistry):
    """Visual component plugin"""

    def __init__(self, parent=None):
        Component.__init__(self, parent)

        self.__properties = {}
        # destroy all signals
        self.destroyed.connect(lambda: _PluginMeta.destroy(self))

    def __ui__(self):
        """Please define UI code here and call from `__init__` method"""

        pass

    @property
    def arranger(self):
        """Access global arranger"""

        return self.app.main_window.view_arranger

    def paintEvent(self, event):
        """Fix issue with css component styles"""
        super(Viewer, self).paintEvent(event)

        option = QStyleOption()
        option.initFrom(self)

        painter = QPainter(self)

        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)

    def plugin_menu(self):
        """Returns qt menu that will replace this view with chosen from list"""

        menu = QMenu("Available views", self)

        def triggered(action):
            return lambda x, item=action: self.arranger.replace(self, item.plugin)

        for plug in self.plugins():

            if plug.private:
                continue

            action = QAction(plug.name, menu)
            action.plugin = plug.id
            action.triggered.connect(triggered(action))

            menu.addAction(action)

        remove_action = QAction('Remove', menu)
        remove_action.triggered.connect(lambda: self.arranger.remove(self))

        split_v_action = QAction('Split vertically', menu)
        split_v_action.triggered.connect(lambda: self.arranger.split(self, 'v'))

        split_h_action = QAction('Split horizontally', menu)
        split_h_action.triggered.connect(lambda: self.arranger.split(self, 'h'))

        menu.addSeparator()
        menu.addAction(split_h_action)
        menu.addAction(split_v_action)
        menu.addSeparator()
        menu.addAction(remove_action)

        return menu

    def set(self, key, value):
        """Store viewer state using key-value storage"""
        pass

    def get(self, key, default=None):
        pass


class Configurator(Component, _PluginMeta, metaclass=_ComponentPluginRegistry):
    """Visual plugin that will be shown in settings dialog as page"""

    def __init__(self, parent=None):
        Component.__init__(self, parent)

    def __ui__(self):
        """Please define UI code here and call from `__init__` method"""

        pass

    def clicked(self):
        """Called by host when configuration page is selected"""

        pass
