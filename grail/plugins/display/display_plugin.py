# -*- coding: UTF-8 -*-
"""
    grail.plugins.display.display_plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    2d graphics display

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
from grail.qt import *
from grail.core import Plugin, debug

from .preferences_dialog import DisplayPreferencesDialog
from .scene import DisplayWindow, DisplayScene


class DisplayPlugin(Plugin):
    """Plugin for displaying cues

    Connected:
        '/app/close'

    Emits:
        -
    """

    id = 'display'
    name = 'Display'
    author = 'Alex Litvin'
    description = 'Display 2d graphics in window or in full screen mode'

    _instance = None

    def __init__(self):
        super(DisplayPlugin, self).__init__()

        # Register instance
        if not DisplayPlugin._instance:
            DisplayPlugin._instance = self

        # Register menu items
        self.menu_disable = self.register_menu("Display->Disable", self.disable_action,
                                               shortcut="Ctrl+D",
                                               checkable=True,
                                               checked=True)
        self.register_menu("Display->Clear Text", self.clear_text_action,
                           shortcut="Ctrl+Z")
        self.register_menu("Display->Clear Output", self.clear_output_action,
                           shortcut="Ctrl+Shift+Z")
        self.register_menu('Display->---')
        self.menu_testcard = self.register_menu("Display->Show Test Card", self.testcard_action,
                                                shortcut="Ctrl+Shift+T",
                                                checkable=True)
        self.register_menu("Display->Advanced...", self.preferences_action,
                           shortcut="Ctrl+Shift+A")

        # Register actions
        self.register_action("Disable output", self.disable_action)
        self.register_action("Toggle test card", self.testcard_action)
        self.register_action("Advanced preferences...", self.preferences_action)

        self.register_action("Clear Text", self.clear_output_action)
        self.register_action("Clear Output", self.clear_text_action)

        # Connect signals
        self.connect('/app/close', self.close)
        self.connect('/clip/text', lambda text: self.scene.set_text(text))
        self.connect('!cue/execute', self.cue_cb)
        self.connect('/clip/1/playback/source', lambda path: self.scene.clip_playback_source(1, path))

        # Composition signals
        self.connect('/comp/size', self._comp_size_cb)
        self.connect('/comp/testcard', self._comp_testcard_cb)
        self.connect('/comp/opacity', self._comp_opacity_cb)
        self.connect('/comp/transition', self._comp_transition_cb)
        self.connect('/comp/volume', self._comp_volume_cb)

        self.connect('/clip/text', self._text_cb)
        self.connect('/clip/text/font', self._text_font_cb)

        self.connect('/clip/text/color', self._text_color_cb)
        self.connect('/clip/text/padding', self._text_padding_cb)
        self.connect('/clip/text/align', self._text_align_cb)
        self.connect('/clip/text/shadow', self._text_shadow_cb)
        self.connect('/clip/text/transform', self._text_transform_cb)

        desktop = QApplication.desktop()
        desktop.resized.connect(self._screens_changed)
        desktop.screenCountChanged.connect(self._screens_changed)
        desktop.workAreaResized.connect(self._screens_changed)

        self._outputs = []

        self._scene = DisplayScene()
        self._scene.set_size(1920, 1080)
        # todo: restore from settings

        self._preferences_dialog = DisplayPreferencesDialog(self)

        # Notify other plugins and viewers that DisplayPlugin is loaded
        self.emit("!display/instance")

    def cue_cb(self, cue):

        self.scene.set_text(cue.name)

    @debug
    def _comp_size_cb(self, width: int, height: int):

        self._scene.set_size(width, height)

    @debug
    def _comp_opacity_cb(self, opacity: float):

        self._scene.set_opacity(opacity)

    @debug
    def _comp_transition_cb(self, seconds: float):

        self._scene.set_transition(seconds)

    @debug
    def _comp_volume_cb(self, volume: float):

        self._scene.set_volume(volume)

    @debug
    def _text_cb(self, text):

        self._scene.set_text(text)

    @debug
    def _text_font_cb(self, size, name, style):

        self._scene.set_text_font(size, name, style)

    @debug
    def _text_color_cb(self, color):

        self._scene.set_text_color(color)

    @debug
    def _text_padding_cb(self, l, t, r, b):

        self._scene.set_text_padding(l, t, r, b)

    @debug
    def _text_align_cb(self, h, v):

        self._scene.set_text_align(h, v)

    @debug
    def _text_shadow_cb(self, x, y, blur, color):

        self._scene.set_text_shadow(x, y, blur, color)

    @debug
    def _text_transform_cb(self, transform):

        self._scene.set_text_transform(transform)

    def testcard_action(self, action=None):
        """Show or hide test card"""

        # called from Actions
        if not action:
            action = self.menu_testcard
            action.setChecked(not action.isChecked())

        self._scene.set_testcard(action.isChecked())

    def _comp_testcard_cb(self, flag=False):

        self.menu_testcard.setChecked(flag)
        self._scene.set_testcard(flag)

    def preferences_action(self, action=None):
        """Show display preferences dialog"""

        self._preferences_dialog.showWindow()

    def disable_action(self, action=None):
        """Disable display output"""

        # called from Actions
        if not action:
            action = self.menu_disable
            action.setChecked(True)

        for output in self._outputs:
            output.hide()

    def clear_output_action(self, action=None):
        """Clear display output"""

        # todo: implement this

    def clear_text_action(self, action=None):
        """Clear display text"""

        pass
        # todo: implement this

    def close(self):
        """Close display and friends on application exit"""

        self._preferences_dialog.close()

        for output in self._outputs:
            output.close()

    def _screens_changed(self):
        """Display configuration changed"""

        self.disable_action()

    def add_output(self):
        """Add new output"""

        output = DisplayWindow(self)
        output.show()

        self._outputs.append(output)

        return output

    @property
    def scene(self):
        """Returns scene"""

        return self._scene

    @property
    def outputs(self):
        """List of DisplayWindow"""

        return self._outputs

    @classmethod
    def instance(cls):
        """Get instance of DisplayPlugin"""

        return cls._instance
