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

        self.MAX_LAYERS = 2

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

        # Text layer signals
        self.connect('/clip/text', self._text_cb)
        self.connect('/clip/text/font', self._text_font_cb)
        self.connect('/clip/text/color', self._text_color_cb)
        self.connect('/clip/text/padding', self._text_padding_cb)
        self.connect('/clip/text/align', self._text_align_cb)
        self.connect('/clip/text/shadow', self._text_shadow_cb)
        self.connect('/clip/text/transform', self._text_transform_cb)

        def connect_layer(layer):
            self.connect(f"/clip/{layer}/size", lambda w, h: self._clip_size_cb(layer, w, h))
            self.connect(f"/clip/{layer}/pos", lambda x, y: self._clip_pos_cb(layer, x, y))
            self.connect(f"/clip/{layer}/rotate", lambda angle: self._clip_angle_cb(layer, angle))
            self.connect(f"/clip/{layer}/opacity", lambda opacity: self._clip_opacity_cb(layer, opacity))
            self.connect(f"/clip/{layer}/volume", lambda volume: self._clip_volume_cb(layer, volume))
            self.connect(f"/clip/{layer}/scale", lambda scale: self._clip_scale_cb(layer, scale))
            self.connect(f"/clip/{layer}/playback/source", lambda source: self._clip_source_cb(layer, source))
            self.connect(f"/clip/{layer}/playback/position", lambda pos: self._clip_position_cb(layer, pos))
            self.connect(f"/clip/{layer}/playback/transport", lambda tr: self._clip_transport_cb(layer, tr))
            self.connect(f"/clip/{layer}/playback/play", lambda: self._clip_play_cb(layer))

        # Media clip signals
        for layer_id in range(1, self.MAX_LAYERS + 1):
            connect_layer(layer_id)

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

    def _clip_angle_cb(self, layer, angle):

        self._scene.clip_rotate(layer, angle)

    def _clip_opacity_cb(self, layer, opacity):

        self._scene.clip_opacity(layer, opacity)

    def _clip_volume_cb(self, layer, volume):

        self._scene.clip_volume(layer, volume)

    def _clip_scale_cb(self, layer, scale):

        self._scene.clip_scale(layer, scale)

    def _clip_source_cb(self, layer, source):

        print("Clip Source", layer, source)
        self._scene.clip_playback_source(layer, source)

    def _clip_position_cb(self, layer, pos):

        self._scene.clip_playback_position(layer, pos)

    def _clip_transport_cb(self, layer, tr):

        self._scene.clip_playback_transport(layer, tr)

    def _clip_play_cb(self, layer):

        self._scene.clip_playback_play(layer)

    def _clip_size_cb(self, layer, width, height):

        self._scene.clip_size(layer, width, height)

    def _clip_pos_cb(self, layer, x, y):

        self._scene.clip_position(layer, x, y)

    def _comp_size_cb(self, width: int, height: int):

        self._scene.set_size(width, height)

    def _comp_opacity_cb(self, opacity: float):

        self._scene.set_opacity(opacity)

    def _comp_transition_cb(self, seconds: float):

        self._scene.set_transition(seconds)

    def _comp_volume_cb(self, volume: float):

        self._scene.set_volume(volume)

    def _text_cb(self, text):

        self._scene.set_text(text)

    def _text_font_cb(self, size, name, style):

        self._scene.set_text_font(size, name, style)

    def _text_color_cb(self, color):

        self._scene.set_text_color(color)

    def _text_padding_cb(self, l, t, r, b):

        self._scene.set_text_padding(l, t, r, b)

    def _text_align_cb(self, h, v):

        self._scene.set_text_align(h, v)

    def _text_shadow_cb(self, x, y, blur, color):

        self._scene.set_text_shadow(x, y, blur, color)

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

        for layer in range(1, self.MAX_LAYERS):
            self.emit(f"/clip/{layer}/playback/stop")

    def clear_text_action(self, action=None):
        """Clear display text"""

        self.emit('/clip/text', "")

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
