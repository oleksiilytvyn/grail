# -*- coding: UTF-8 -*-
"""
    grail.core.plugin
    ~~~~~~~~~~~~~~~~~

    Plugin mechanism
"""
from grailkit.qt import Component, Application, Button
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

    def __init__(self):
        """Initialize plugin"""

        super(_PluginMeta, self).__init__()

    def emit(self, message, *args):
        """Emit a message with arguments

        Args:
            message (str): message name
            *args (list): any arguments
        """

        self.app.emit(message, *args)

    def connect(self, message, fn):
        """Connect a message listener

        Args:
            message (str): message name
            fn (callable): function to call
        """

        self.app.connect(message, fn)

    def register_action(self, name, fn):
        """Register a global action"""

        pass

    @property
    def app(self):
        """Returns application instance"""

        return Application.instance()

    @classmethod
    def loaded(cls):
        """Called by plugin host when plugin loaded"""

        pass

    @classmethod
    def unloaded(cls):
        """Called when plugin is unloaded"""

        pass

    @classmethod
    def plugins(cls):
        """Returns list of classes extended from Plugin"""

        plugins = sorted(cls.__registry__, key=lambda x: str(x), reverse=True)

        return plugins


class Plugin(_PluginMeta, metaclass=PluginRegistry):
    """Abstract plugin"""

    pass


class _ComponentPluginRegistry(type(Component), PluginRegistry):
    """Meta class for visual plugins"""

    def __init__(cls, name, bases, attrs):
        type(Component).__init__(cls, name, bases, attrs)
        PluginRegistry.__init__(cls, name, bases, attrs)


class Viewer(Component, _PluginMeta, metaclass=_ComponentPluginRegistry):
    """Visual component plugin"""

    def __init__(self, parent=None):
        Component.__init__(self, parent)

    def plugin_menu(self):
        """Returns qt menu that will replace this view with chosen from list"""

        menu = None

        return menu

    def __ui__(self):
        """Please define UI code here and call from `__init__` method"""

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
