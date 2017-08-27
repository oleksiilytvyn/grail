# -*- coding: UTF-8 -*-
"""
    grail.plugins.display_plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    2d graphics display

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import math

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.util import OS_MAC
from grailkit.dna import DNA
from grailkit.qt import *

from grail.core import Plugin, Viewer, Configurator


class DisplayPlugin(Plugin):
    """Plugin for displaying cues

    Connected:
        '/app/close'

    Emits:
        -
    """

    id = 'display'
    name = 'Display'
    author = 'Grail Team'
    description = 'Display 2d graphics in window or in fullscreen mode'

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

        self.window = DisplayWindow(self)
        self.preferences_dialog = PreferencesDialog()

        # Connect signals
        self.connect('/app/close', self.close)
        self.connect('!cue/execute', self._execute)

        desktop = QApplication.desktop()
        desktop.resized.connect(self._screens_changed)
        desktop.screenCountChanged.connect(self._screens_changed)
        desktop.workAreaResized.connect(self._screens_changed)

        self._composition = CompositionTexture()

        # render update loop
        self._timer = QTimer()
        self._timer.timeout.connect(self._render)
        self._timer.start(1000 / 30)

        self._render()

    @property
    def composition(self):
        """Returns composition instance"""

        return self._composition

    def _render(self):
        """Update composition and windows"""

        # don't render if output disabled
        # if self.disabled:
        #    return False

        # render a composition
        self._composition.render()
        # notify others
        self.emit('!composition/update')

    def testcard_action(self, action=None):
        """Show or hide test card"""

        # called from Actions
        if not action:
            action = self.menu_testcard
            action.setChecked(not action.isChecked())

        self._composition.setTestCard(action.isChecked())

    def preferences_action(self, action=None):
        """Show display preferences dialog"""

        self.preferences_dialog.show()
        self.preferences_dialog.raise_()

    def disable_action(self, action=None):
        """Disable display output"""

        # called from Actions
        if not action:
            action = self.menu_disable
            action.setChecked(True)

        if action.isChecked():
            self.window.close()
        else:
            self.window.show()

    def close(self):
        """Close display and friends on application exit"""

        self.window.close()
        self.preferences_dialog.close()

    def _execute(self, cue):

        if cue.type == DNA.TYPE_SONG:
            text = cue.lyrics
        elif cue.type == DNA.TYPE_VERSE:
            text = "%s\n%s" % (cue.text, cue.reference)
        else:
            text = cue.name

        self._composition.setText(text)

    def _screens_changed(self):
        """Display configuration changed"""

        self.disable_action()

    @classmethod
    def instance(cls):
        """Get instance of DisplayPlugin"""

        return cls._instance


class DisplayWindow(Frameless):
    """Window that displays 2d graphics"""

    def __init__(self, parent):
        super(DisplayWindow, self).__init__(None)

        self._position = QPoint(0, 0)
        self._plugin = parent

        Application.instance().signals.connect('!composition/update', self.update)

        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)
        self.setWindowTitle("Display")
        self.setWindowFlags((Qt.Dialog if OS_MAC else Qt.Tool) |
                            Qt.FramelessWindowHint |
                            Qt.WindowSystemMenuHint |
                            Qt.WindowStaysOnTopHint)
        self.moveCenter()

    def paintEvent(self, event):
        """Draw image"""

        output = event.rect()
        composition = output

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        painter.fillRect(output, Qt.black)
        painter.drawImage(output, self._plugin.composition)

        painter.end()

    def hideEvent(self, event):

        event.ignore()

    def mousePressEvent(self, event):

        self._position = event.globalPos()

    def mouseMoveEvent(self, event):

        delta = QPoint(event.globalPos() - self._position)

        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._position = event.globalPos()


class CompositionTexture(QImage):

    def __init__(self):
        super(CompositionTexture, self).__init__(QSize(800, 600), QImage.Format_RGB32)

        self._display_test = False

        self._text = ""
        self._style_color = QColor('#fff')
        self._style_background = QColor('#222')
        self._style_case_transform = False
        self._style_font = QFont('decorative', 28)

        self._shadow_x = 0
        self._shadow_y = 5
        self._shadow_blur = 0
        self._shadow_color = QColor("#000000")

        self._padding = QMargins(10, 10, 10, 10)
        self._align_horizontal = Qt.AlignHCenter
        self._align_vertical = Qt.AlignVCenter

        self._transform = QTransform()
        self._composition = QRect(0, 0, 800, 600)
        self._fullscreen = False
        self._geometry = QRect(100, 100, 800, 600)

    def render(self):
        """Render composition"""

        p = QPainter()
        p.begin(self)

        p.fillRect(self.rect(), Qt.black)

        if self._display_test:
            p.drawPixmap(self.rect(), CompositionTexture.generate_testcard(self.width(), self.height()))
        else:
            self._draw_text(p)

        p.end()

    def setTestCard(self, flag):
        """Show test card or not"""

        self._display_test = flag
        self.render()

    def setText(self, text):

        self._text = text
        self.render()

    def _draw_text(self, painter):
        """Draw text"""

        painter.setFont(self._style_font)
        painter.setPen(self._shadow_color)

        padding = self._padding

        box = QRect(self._composition.topLeft(), self._composition.bottomRight())
        box.adjust(padding.left(), padding.top(), -padding.right(), -padding.bottom())
        box.setX(box.x() + self._shadow_x)
        box.setY(box.y() + self._shadow_y)

        painter.drawText(box, self._align_vertical | self._align_horizontal | Qt.TextWordWrap, self._text)

        painter.setPen(self._style_color)

        box = QRect(self._composition.topLeft(), self._composition.bottomRight())
        box.adjust(padding.left(), padding.top(), -padding.right(), -padding.bottom())

        painter.drawText(box, self._align_vertical | self._align_horizontal | Qt.TextWordWrap, self._text)

    @classmethod
    def generate_testcard(cls, width, height):
        """Generate test card QPixmap"""

        comp = QRect(0, 0, width, height)
        image = QPixmap(comp.width(), comp.height())
        offset = 50

        painter = QPainter()
        painter.begin(image)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        painter.fillRect(comp, QColor("#7f7f7f"))

        pen = QPen(Qt.white)
        pen.setWidth(1)

        painter.setPen(pen)
        lines = math.ceil(max(comp.width(), comp.height()) / offset)

        for index in range(-lines, lines):
            o = index * offset

            painter.drawLine(0, comp.height() / 2 + o, comp.width(), comp.height() / 2 + o)
            painter.drawLine(comp.width() / 2 + o, 0, comp.width() / 2 + o, comp.height())

        pen = QPen(QColor("#222222"))
        pen.setWidth(3)
        painter.setPen(pen)

        painter.drawLine(0, comp.height() / 2, comp.width(), comp.height() / 2)
        painter.drawLine(comp.width() / 2, 0, comp.width() / 2, comp.height())

        pen.setWidth(5)
        painter.setPen(pen)

        radius = min(comp.height(), comp.width()) / 2
        circles = math.ceil((comp.width() / radius) / 2) + 1

        for index in range(-circles, circles + 1):
            ox = index * (radius * 1.25)

            painter.drawEllipse(QPoint(comp.width() / 2 + ox, comp.height() / 2), radius, radius)

        box = QRect(comp.topLeft(), comp.bottomRight())
        box.adjust(10, 10, -10, -10)

        painter.setPen(Qt.white)
        painter.setFont(QFont("decorative", 24))
        painter.drawText(box, Qt.AlignCenter | Qt.TextWordWrap,
                         "composition size %d x %d" % (comp.width(), comp.height()))

        painter.end()

        return image


class DisplayWidget(QWidget):
    """Display composition texture in QWidget"""

    def __init__(self, parent=None):
        super(DisplayWidget, self).__init__(parent)

        self._plugin = None
        self._texture = None

        parent.connect('!composition/update', self.repaint)

    def paintEvent(self, event):

        p = QPainter()
        p.begin(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        p.fillRect(self.rect(), Qt.black)

        # Connect texture if available
        if not self._plugin:
            self._plugin = DisplayPlugin.instance()
            self._texture = self._plugin.composition if self._plugin else None

        # draw texture
        if self._texture:
            s = self.size()
            t = self._texture.size()

            scale = min(s.width() / t.width(), s.height() / t.height()) * 0.9

            w = t.width() * scale
            h = t.height() * scale

            x = s.width() / 2 - w / 2
            y = s.height() / 2 - h / 2

            p.fillRect(QRect(x - 1, y - 1, w + 2, h + 2), Qt.red)
            p.drawImage(QRect(x, y, w, h), self._texture)

        p.end()


class TransformWidget(QWidget):
    """Corner-pin transformation with composition display"""

    def __init__(self, parent=None):
        super(TransformWidget, self).__init__(parent)

    def paintEvent(self, event):

        p = QPainter()
        p.begin(self)
        p.end()


class PreferencesDialog(Dialog):
    """Display preferences window"""

    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)

        self.__ui__()

    def __ui__(self):
        """Build UI"""

        self._ui_toolbar = Toolbar()

        self._ui_layout = VLayout()
        self._ui_layout.addWidget(Spacer())
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)
        self.setWindowTitle("Display preferences")
        self.setGeometry(100, 100, 480, 360)
        self.setMinimumSize(300, 200)
        self.moveCenter()


class DisplayPreviewViewer(Viewer):
    """Preview display output in a Viewer"""

    id = "display-preview-viewer"
    name = "Preview"
    author = "Grail Team"
    description = "Preview items from library and cuelists"

    def __init__(self, *args, **kwargs):
        super(DisplayPreviewViewer, self).__init__(*args, **kwargs)

        self.connect('!cue/preview', self._preview)

        self.__ui__()
        self._label.setText(self.get('preview-text', default=""))

    def __ui__(self):

        self._label = Label()
        self._label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self._label.setObjectName("DisplayPreviewViewer_label")

        self._frame = QScrollArea()
        self._frame.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._frame.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._frame.setWidgetResizable(True)
        self._frame.setStyleSheet("border: none;")
        self._frame.setWidget(self._label)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon.colored(':/icons/menu.png', QColor('#555'), QColor('#e3e3e3')))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.setObjectName("DisplayPreviewViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(Spacer())

        self._layout = VLayout()
        self._layout.addWidget(self._frame)
        self._layout.addWidget(self._ui_toolbar)

        self.setLayout(self._layout)

    def _preview(self, cue):
        """Handle '!cue/preview' signal"""

        if cue.type == DNA.TYPE_SONG:
            text = cue.lyrics
        elif cue.type == DNA.TYPE_VERSE:
            text = "%s<br/><small>%s</small>" % (cue.text, cue.reference)
        else:
            text = cue.name

        self.set('preview-text', text)
        self._label.setText(text)

    def view_action(self):
        """Replace current view with something other"""

        self.plugin_menu().exec_(self._ui_toolbar.mapToGlobal(self._ui_view_action.pos()))


class DisplayViewer(Viewer):
    """View composition output as viewer"""

    id = "display-viewer"
    name = "Display Output"
    author = "Grail Team"
    description = "View composition output"

    def __init__(self, *args, **kwargs):
        super(DisplayViewer, self).__init__(*args, **kwargs)

        self.__ui__()

    def __ui__(self):

        self._widget = DisplayWidget(self)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon.colored(':/icons/menu.png', QColor('#555'), QColor('#e3e3e3')))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.setObjectName("DisplayPreviewViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(Spacer())

        self._layout = VLayout()
        self._layout.addWidget(self._widget)
        self._layout.addWidget(self._ui_toolbar)

        self.setLayout(self._layout)

    def view_action(self):
        """Replace current view with something other"""

        self.plugin_menu().exec_(self._ui_toolbar.mapToGlobal(self._ui_view_action.pos()))
