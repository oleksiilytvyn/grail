# -*- coding: UTF-8 -*-
"""
    grail.core.plugin
    ~~~~~~~~~~~~~~~~~

    Plugin mechanism

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
from grailkit.util import default_key
from grailkit.plug import PluginRegistry

from grail.qt import *


class _PluginMeta(object):
    """
    Plugin base class.
    All plugin types must have properties and methods defined by this class.
    """

    # Unique plugin identifier
    id = 'dummy-plugin'

    # Plugin display name
    name = 'Default plugin'

    # Plugin author string
    author = 'Unnamed Developer'

    # Plugin description string
    description = 'Dummy plugin that doesn\'t do anything useful'

    # Do not list this plugin if True
    private = False

    # Do not allow multiple instances
    single_instance = False

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

        self.__app.signals.emit(message, *args)

    def connect(self, message, fn):
        """Connect a message listener

        Args:
            message (str): message name
            fn (callable): function to call
        """

        self.__app.signals.connect(message, fn)
        self.__slots.append([message, fn])

    def destroy(self):
        """Gracefully destroy widget and disconnect any signals
        Please call this method when you don't need instance anymore
        """
        # prevent from destructing several times
        if self.__destroyed:
            return None

        # clear slots as they keeping this object alive
        # and preventing from garbage collection
        for slot in self.__slots:
            self.__app.signals.disconnect(*slot)

        self.__slots = []
        self.__destroyed = True

    @property
    def app(self):
        """Returns application instance"""

        return self.__app

    @property
    def library(self):
        """Library instance"""

        return self.__app.library

    @property
    def project(self):
        """Current project instance"""

        return self.__app.project

    @property
    def bible(self):
        """Bible instance"""

        return self.__app.bible

    @property
    def is_destroyed(self):
        """Returns True if plugin is destroyed by host"""

        return self.__destroyed

    @classmethod
    def loaded(cls):
        """Called by plugin host when plugin is loaded"""

        pass

    @classmethod
    def unloaded(cls):
        """Called when plugin is unloaded"""

        pass

    @classmethod
    def plugins(cls, sort_reverse=True, sort_key=lambda x: str(x)):
        """Returns list of classes extended from Plugin in alphabetical order"""

        if hasattr(cls, '__registry__'):
            return sorted(cls.__registry__, key=sort_key, reverse=sort_reverse)
        else:
            return set()


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

        Returns:
            QAction menu item created

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

        # add separator
        if name == '---':
            self.__create_action(menubar, items, None, before)
        # add action
        else:
            def trigger(_fn, _action):
                """Callback wrapper"""

                return lambda: _fn(_action)

            action = QAction(name, menubar)
            action.triggered.connect(trigger(fn, action))

            if checkable:
                action.setCheckable(True)
                action.setChecked(checked)

            if shortcut:
                action.setShortcut(shortcut)
                action.setShortcutContext(Qt.ApplicationShortcut)

            self.__create_action(menubar, items, action, before)

            return action

    def __create_action(self, menu, location_tokens, new_action, before_tokens):
        """Create menu item

        Args:
            menu: menu reference
            location_tokens: path string that represents location of new action in menu
            new_action: action reference
            before_tokens: path string, it used to determinate where to place item above or below others
        """

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
            self.__create_action(action_target, location_tokens[1:], new_action, before_tokens[1:])


class _ComponentPluginRegistry(type(QWidget), PluginRegistry):
    """Meta class for visual plugins
    Combines properties of grailkit.qt.Component and grailkit.plug.PluginRegistry"""

    def __init__(cls, name, bases, attrs):
        """This class makes bridge between Regular plugin and Qt Widget component

        Args:
            name (str): class name
            bases (tuple): class parents
            attrs (dict): attributes
        """
        type(QWidget).__init__(cls, name, bases, attrs)
        PluginRegistry.__init__(cls, name, bases, attrs)


class Viewer(QWidget, _PluginMeta, metaclass=_ComponentPluginRegistry):
    """Visual component plugin that will be available in view arranger

    Viewer class can only create self and listen/emit global events
    """

    def __init__(self, parent=None, properties=None):
        QWidget.__init__(self, parent)

        # viewer properties
        if properties and isinstance(properties, dict):
            self.__properties = properties
        else:
            self.__properties = {}

        # destroy all signals when qt object destroyed
        self.destroyed.connect(lambda: _PluginMeta.destroy(self))

    def __ui__(self):
        """Please define UI code here and call from `__init__` method"""

        pass

    @property
    def __arranger(self):
        """Returns ViewArranger instance"""

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
        active_viewers = [v.name for v in self.app.main_window.view_arranger._viewers]

        def triggered(plugin_id):
            """Action callback closure"""

            return lambda item: self.__arranger.replace(self, plugin_id)

        for plug in self.plugins():

            if plug.private:
                continue

            action = QAction(plug.name, menu)
            action.triggered.connect(triggered(plug.id))

            # don't show plugin if single_instance is True and viewer already exists
            action.setDisabled((plug.name in active_viewers) and plug.single_instance)

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

    def show_menu(self, position, widget=None):
        """Show viewer menu

        Args:
            position (QPoint): location where to show menu
            widget (QWidget): Qt widget, if given location will be calculated relative to this widget
        """

        if widget:
            self.plugin_menu().exec_(widget.mapToGlobal(position))
        else:
            self.plugin_menu().exec_(position)

    def set(self, key, value):
        """Store viewer state using key-value storage"""

        if not isinstance(key, str):
            raise ValueError('Unable to set property %s of object %s' % (str(key), str(self)))

        self.__properties[key] = value

    def get(self, key, default=None):
        """Returns stored property"""

        return default_key(self.__properties, key, default)

    def properties(self):
        """Returns all properties of viewer"""

        return self.__properties


class Configurator(QWidget, _PluginMeta, metaclass=_ComponentPluginRegistry):
    """Visual plugin that will be shown in settings dialog as page"""

    index = 0

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

    def __ui__(self):
        """Please define UI code here and call from `__init__` method"""

        pass

    def clicked(self):
        """Called by host when configuration page is selected.
        You can refresh data at this moment.
        """

        pass
