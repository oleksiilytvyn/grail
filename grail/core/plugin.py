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

from grailkit.util import default_key
from grailkit.qt import Component, Application
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

        # keep track of slots to delete them
        self.__slots = []
        self.__destroyed = False
        self.__app = Application.instance()

    def emit(self, message, *args):
        """Emit a message with arguments

        Args:
            message (str): message name
            *args: any arguments
        """

        self.__app.emit(message, *args)

    def connect(self, message, fn):
        """Connect a message listener

        Args:
            message (str): message name
            fn (callable): function to call
        """

        self.__app.connect(message, fn)
        self.__slots.append([message, fn])

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
            self.__app.disconnect_signal(*slot)

        self.__slots = []

    @property
    def app(self):
        """Returns application instance"""

        return self.__app

    @property
    def library(self):
        return self.__app.library

    @property
    def project(self):
        return self.__app.project

    @property
    def bible(self):
        return self.__app.bible

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

        return sorted(cls.__registry__, key=lambda x: str(x), reverse=True)


class Plugin(_PluginMeta, metaclass=PluginRegistry):
    """Non-visual plugin.
    Subclasses of `Plugin` created when project opened and
    closed when user closes application or another project opened

    Plugins can:
     - register actions
     - register items in global menu
    """

    def __init__(self):
        super(Plugin, self).__init__()

    def register_action(self, name, fn):
        """Register a global menu_action
        Actions added by this method can be accessed from menu_action list in application

        Args:
            name (str): name of action
            fn (callable): callback function
        """

        self.app.register_action(self, name, fn)

    def register_menu(self, location, fn=None, shortcut=None, checkable=False, checked=False, before='Help'):
        """Register a menu item in global application menu

        Args:
            location (str): path to menu item and item name divided by '->'
            fn (callable): callback function
            shortcut (str): Qt shortcut string
            checkable (bool): weather this is action with checkbox
            checked (bool): action checked or not if `checkable`
            before (str): where to place item

        Example:

            def callback():
                self._inspector_dialog.show()
                self._inspector_dialog.raise_()

            self.register_menu("View->Developer->Show inspector", callback)
        """

        main = self.app.main_window
        menubar = main.ui_menubar
        tokens = location.split('->')
        before = before.split('->')
        items = tokens[0:len(tokens) - 1]
        name = tokens[-1]

        def create_action(menu, location_tokens, new_action, before_tokens):
            action_name = location_tokens[0]
            action_target = None
            before_name = before_tokens[0] if len(before_tokens) else None
            before_action = None

            # search for existing items
            for action in menu.actions():
                if action.text() == action_name:
                    action_target = action

                if action.text() == before_name:
                    before_action = action

            if action_target:
                action_target = action_target.menu()
            elif not action_target and before_action:
                action_target = menu.insertMenu(before_action, QMenu(action_name, menu)).menu()
            else:
                action_target = menu.addMenu(action_name)

            before_action = None
            before_name = before_tokens[1] if len(before_tokens) > 1 else None

            for item in action_target.actions():
                if item.text() == before_name:
                    before_action = item
                    break

            if len(location_tokens) == 1 and before_action:
                if new_action:
                    action_target.insertAction(before_action, new_action)
                else:
                    action_target.insertSeparator(before_action)
            elif len(location_tokens) == 1:
                if new_action:
                    action_target.addAction(new_action)
                else:
                    action_target.addSeparator()
            else:
                create_action(action_target, location_tokens[1:], new_action, before_tokens[1:])

        # add separator
        if name == '---':
            create_action(menubar, items, None, before)
        # add action
        else:
            def trigger(_fn, _action):
                return lambda: _fn(_action)

            action = QAction(name, menubar)
            action.triggered.connect(trigger(fn, action))

            if checkable:
                action.setCheckable(True)
                action.setChecked(checked)

            if shortcut:
                action.setShortcut(shortcut)
                action.setShortcutContext(Qt.ApplicationShortcut)

            create_action(menubar, items, action, before)


class _ComponentPluginRegistry(type(Component), PluginRegistry):
    """Meta class for visual plugins
    Combines properties of grailkit.qt.Component and grailkit.plug.PluginRegistry"""

    def __init__(cls, name, bases, attrs):
        type(Component).__init__(cls, name, bases, attrs)
        PluginRegistry.__init__(cls, name, bases, attrs)


class Viewer(Component, _PluginMeta, metaclass=_ComponentPluginRegistry):
    """Visual component plugin that will be available in view arranger

    Viewer class can only create self and listen/emit global events
    """

    def __init__(self, parent=None):
        Component.__init__(self, parent)

        # viewer properties
        self.__properties = {}
        # destroy all signals when qt object destroyed
        self.destroyed.connect(lambda: _PluginMeta.destroy(self))

    def __ui__(self):
        """Please define UI code here and call from `__init__` method"""

        pass

    @property
    def __arranger(self):
        return Application.instance().main_window.view_arranger

    def paintEvent(self, event):
        """Fix issue with css component styles"""

        super(Viewer, self).paintEvent(event)

        option = QStyleOption()
        option.initFrom(self)

        painter = QPainter(self)

        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)

    def plugin_menu(self):
        """Returns QMenu with list of viewers, split options and action to remove current viewer"""

        menu = QMenu("Viewers", self)

        def triggered(plugin_id):
            return lambda item: self.__arranger.replace(self, plugin_id)

        for plug in self.plugins():

            if plug.private:
                continue

            action = QAction(plug.name, menu)
            action.triggered.connect(triggered(plug.id))

            menu.addAction(action)

        remove_action = QAction('Remove', menu)
        remove_action.triggered.connect(lambda: self.__arranger.remove(self))

        split_v_action = QAction('Split vertically', menu)
        split_v_action.triggered.connect(lambda: self.__arranger.split(self, 'v'))

        split_h_action = QAction('Split horizontally', menu)
        split_h_action.triggered.connect(lambda: self.__arranger.split(self, 'h'))

        menu.addSeparator()
        menu.addAction(split_h_action)
        menu.addAction(split_v_action)
        menu.addSeparator()
        menu.addAction(remove_action)

        return menu

    def set(self, key, value):
        """Store viewer state using key-value storage"""

        if not isinstance(key, str):
            raise ValueError('Unable to set property %s of object %s' % (str(key), str(self)))

        self.__properties[key] = value

    def get(self, key, default=None):
        """Returns stored property"""

        return default_key(self.__properties, key, default)


class Configurator(Component, _PluginMeta, metaclass=_ComponentPluginRegistry):
    """Visual plugin that will be shown in settings dialog as page"""

    def __init__(self, parent=None):
        Component.__init__(self, parent)

    def __ui__(self):
        """Please define UI code here and call from `__init__` method"""

        pass

    def clicked(self):
        """Called by host when configuration page is selected.
        You can refresh data at this moment.
        """

        pass
