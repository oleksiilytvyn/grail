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

    def __init__(self):
        super(DisplayPlugin, self).__init__()

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

        self.window = DisplayWindow()
        self.preferences_dialog = PreferencesDialog()

        # Connect signals
        self.connect('/app/close', self.close)
        self.connect('!cue/execute', self._execute)

        desktop = QApplication.desktop()
        desktop.resized.connect(self._screens_changed)
        desktop.screenCountChanged.connect(self._screens_changed)
        desktop.workAreaResized.connect(self._screens_changed)

    def testcard_action(self, action=None):
        """Show or hide test card"""

        # called from Actions
        if not action:
            action = self.menu_testcard
            action.setChecked(not action.isChecked())

        self.window.setTestCard(action.isChecked())

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
            text = "%s<br/><small>%s</small>" % (cue.text, cue.reference)
        else:
            text = cue.name

        self.window.setText(text)

    def _screens_changed(self):
        """Display configuration changed"""

        self.disable_action()


class DisplayWindow(Frameless):
    """Window that displays 2d graphics"""

    def __init__(self, parent=None):
        super(DisplayWindow, self).__init__(parent)

        self._position = QPoint(0, 0)
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

        # corner-pin transform
        t = QTransform()
        q = QPolygonF([QPointF(0, 0),
                       QPointF(composition.width(), 0),
                       QPointF(composition.width(), composition.height()),
                       QPointF(0, composition.height())])
        p = QPolygonF([QPointF(0, 0),
                       QPointF(output.width(), 0),
                       QPointF(output.width(), output.height()),
                       QPointF(0, output.height())])

        QTransform.quadToQuad(QPolygonF(q), QPolygonF(p), t)
        world_transform = t * self._transform
        painter.setTransform(world_transform)

        if self._display_test:
            painter.drawPixmap(output, self._generate_testcard(output.width(), output.height()))
        else:
            self._draw_text(painter)

        painter.end()

    def hideEvent(self, event):

        event.ignore()

    def mousePressEvent(self, event):

        self._position = event.globalPos()

    def mouseMoveEvent(self, event):

        delta = QPoint(event.globalPos() - self._position)

        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._position = event.globalPos()

    def setTestCard(self, flag):
        """Show test card or not"""

        self._display_test = flag
        self.update()

    def setText(self, text):
        self._text = text
        self.update()

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
    def _generate_testcard(cls, width, height):
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


class PreferencesDialog(Dialog):
    """Display preferences window"""

    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)

        self.__ui__()

    def __ui__(self):
        """Build UI"""

        self._ui_toolbar = QToolBar()

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

    def __ui__(self):

        self._label = Label()
        self._label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self._label.setObjectName("DisplayPreviewViewer_label")

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon.colored(':/icons/menu.png', QColor('#555'), QColor('#e3e3e3')))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.setObjectName("DisplayPreviewViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(Spacer())

        self._layout = VLayout()
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._ui_toolbar)

        self.setLayout(self._layout)

    def _preview(self, cue):
        """Handle !cue/preview signal"""

        if cue.type == DNA.TYPE_SONG:
            text = cue.lyrics
        elif cue.type == DNA.TYPE_VERSE:
            text = "%s<br/><small>%s</small>" % (cue.text, cue.reference)
        else:
            text = cue.name

        self._label.setText(text)

    def view_action(self):
        """Replace current view with something other"""

        self.plugin_menu().exec_(self._ui_toolbar.mapToGlobal(self._ui_view_action.pos()))
