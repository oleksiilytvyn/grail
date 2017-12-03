# -*- coding: UTF-8 -*-
"""
    grail.plugins.display_plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    2d graphics display

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import math

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from grailkit.dna import DNA
from grailkit.util import OS_MAC

from grail.qt import *
from grail.core import Plugin, Viewer


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
        self.preferences_dialog = PreferencesDialog(self)

        # Connect signals
        self.connect('/app/close', self.close)
        self.connect('!cue/execute', self._execute)
        self.connect('/comp/testcard', self._testcard)
        self.connect('/comp/width', self._composition_changed)
        self.connect('/comp/height', self._composition_changed)

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

        self.emit('/comp/testcard', action.isChecked())

    def preferences_action(self, action=None):
        """Show display preferences dialog"""

        self.preferences_dialog.showWindow()

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

        self.emit('/display/disabled', action.isChecked())

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

        self.emit('/clip/text/source', text)

    def _screens_changed(self):
        """Display configuration changed"""

        self.disable_action()

    def _testcard(self, flag):
        """Update action according to"""

        action = self.menu_testcard
        action.setChecked(flag)

    def _composition_changed(self, size=0):
        """Swap composition texture as QImage can change size after initialization"""

        self._composition = CompositionTexture()
        self.emit('!composition/update')

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
        self._preferences = CompositionPreferences.instance()

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
        comp = self._plugin.composition

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        t = QTransform()
        q = QPolygonF([QPointF(0, 0),
                       QPointF(comp.width(), 0),
                       QPointF(comp.width(), comp.height()),
                       QPointF(0, comp.height())])
        p = QPolygonF([QPointF(0, 0),
                       QPointF(output.width(), 0),
                       QPointF(output.width(), output.height()),
                       QPointF(0, output.height())])

        QTransform.quadToQuad(q, p, t)

        painter.setTransform(t)  # * self._preferences.transformation)
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
    """Display output texture"""

    def __init__(self):

        self._p = CompositionPreferences.instance()

        # create composition
        super(CompositionTexture, self).__init__(self._p.composition, QImage.Format_RGB32)

        # connect signals
        signals = Application.instance().signals
        signals.connect('/comp/testcard', self._testcard_cb)
        signals.connect('/clip/text/source', self._text_cb)

    def _testcard_cb(self, flag=False):
        """Show test card or not"""

        self._p.display_test = flag
        self.render()

    def _text_cb(self, text):

        self._p.text = text
        self.render()

    def render(self):
        """Render composition"""

        p = QPainter()
        p.begin(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        p.fillRect(self.rect(), Qt.black)

        if self._p.display_test:
            p.drawPixmap(self.rect(), CompositionTexture.generate_testcard(self._p.composition.width(),
                                                                           self._p.composition.height()))
        else:
            self._draw_text(p)

        p.end()

    def _draw_text(self, painter):
        """Draw text"""

        painter.setFont(self._p.style_font)
        painter.setPen(self._p.shadow_color)

        padding = self._p.padding

        box = QRect(0, 0, self._p.composition.width(), self._p.composition.height())
        box.adjust(padding.left(), padding.top(), -padding.right(), -padding.bottom())
        box.setX(box.x() + self._p.shadow_x)
        box.setY(box.y() + self._p.shadow_y)

        painter.drawText(box, self._p.align_vertical | self._p.align_horizontal | Qt.TextWordWrap, self._p.text)

        painter.setPen(self._p.style_color)

        box = QRect(0, 0, self._p.composition.width(), self._p.composition.height())
        box.adjust(padding.left(), padding.top(), -padding.right(), -padding.bottom())

        painter.drawText(box, self._p.align_vertical | self._p.align_horizontal | Qt.TextWordWrap, self._p.text)

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
        lines = int(max(comp.width(), comp.height()) / offset)

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
        circles = int((comp.width() / radius) / 2) + 1

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


class CompositionPreferences(object):
    """This class holds attributes used to render composition as Qt objects"""

    __instance = None

    def __init__(self):

        # private
        self._app = Application.instance()
        self._signals = self._app.signals
        self._settings = self._app.project.settings()

        # public
        self.display_test = False

        self.text = ""
        self.style_color = QColor('#fff')
        self.style_background = QColor('#222')
        self.style_case_transform = 0
        self.style_font = QFont('decorative', 28)

        self.shadow_x = 0
        self.shadow_y = 5
        self.shadow_blur = 0
        self.shadow_color = QColor("#000000")

        self.padding = QMargins(10, 10, 10, 10)
        self.align_horizontal = Qt.AlignHCenter
        self.align_vertical = Qt.AlignVCenter

        self.transform = QTransform()
        self.composition = QSize(800, 600)
        self.fullscreen = False
        self.geometry = QRect(100, 100, 800, 600)

    def bind(self):
        """Bind signals"""

        pass

    def parse(self):
        """Get properties from project settings"""

        s = self._settings

        self.style_color = QColor(s.get('/clip/text/color', default='#ffffff'))
        self.style_background = QColor('#000')
        self.style_case_transform = s.get('/clip/text/transform', default=0)
        self.style_font = QFont('decorative', 28)

        self.shadow_x = s.get('/clip/text/shadow/x', default=0)
        self.shadow_y = s.get('/clip/text/shadow/y', default=0)
        self.shadow_blur = s.get('/clip/text/shadow/blur', default=0)
        self.shadow_color = QColor(s.get('/clip/text/shadow/color', default='#000000'))

        # self.padding = QMargins(*s.get('/clip/text/padding', default=[0, 0, 0, 0]))
        self.align_horizontal = s.get('/clip/text/align', default=Qt.AlignVCenter)
        self.align_vertical = s.get('/clip/text/valign', default=Qt.AlignHCenter)

        self.transform = QTransform()
        self.composition = QSize(s.get('/comp/width', default=800),
                                 s.get('/comp/height', default=600))
        self.fullscreen = s.get('/display/fullscreen', default=False)
        self.geometry = QRect(s.get('/display/x', default=0),
                              s.get('/display/y', default=0),
                              s.get('/display/width', default=800),
                              s.get('/display/height', default=600))

    @classmethod
    def instance(cls):
        """Returns instance"""

        if not cls.__instance:
            cls.__instance = CompositionPreferences()
            cls.__instance.parse()

        return cls.__instance


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

    updated = pyqtSignal()

    def __init__(self, parent=None):
        super(TransformWidget, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        screen = QGuiApplication.screens()[0].availableSize()
        self.screen = QRectF(0, 0, screen.width(), screen.height())
        self.points = [QPointF(0, 0), QPointF(0, 0), QPointF(0, 0), QPointF(0, 0)]
        self.wholeTransformation()

        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_hold = False
        self.mouse_hold_x = 0
        self.mouse_hold_y = 0
        self.x = 0
        self.y = 0
        self.scale = 1.0
        self.point_index = -1
        self.font = QFont("decorative", 14)
        self.text = ""

        self._menu = QMenu("Menu", self)

        whole_action = QAction('Whole area', self._menu)
        whole_action.triggered.connect(self.wholeTransformation)

        left_action = QAction('Left side', self._menu)
        left_action.triggered.connect(self.leftTransformation)

        right_action = QAction('Right side', self._menu)
        right_action.triggered.connect(self.rightTransformation)

        center_action = QAction('Center', self._menu)
        center_action.triggered.connect(self.centerTransformation)

        self._menu.addAction(left_action)
        self._menu.addAction(right_action)
        self._menu.addAction(whole_action)
        self._menu.addSeparator()
        self._menu.addAction(center_action)

        self.customContextMenuRequested.connect(self._context_menu)

    def _context_menu(self, event):
        """Open context menu"""

        self._menu.exec_(self.mapToGlobal(event))

    def _map_to_widget(self, point):
        """Map point to widget coordinates"""

        return QPointF(self.x + self.scale * point.x(), self.y + self.scale * point.y())

    def _map_to_screen(self, point):
        """Map point to screen coordinates"""

        return QPointF(point.x() * (1 / self.scale), point.y() * (1 / self.scale))

    def mousePressEvent(self, event):
        """Handle mouse press event"""

        self.mouse_hold = True
        index = 0

        for point in self.points:
            point = self._map_to_widget(point)

            if math.sqrt(pow(point.x() - event.x(), 2) + pow(point.y() - event.y(), 2)) <= 5:
                self.point_index = index
                self.mouse_hold_x = event.x() - point.x()
                self.mouse_hold_y = event.y() - point.y()

            index = index + 1

    def mouseReleaseEvent(self, event):
        """Handle mouse release event"""

        self.mouse_hold = False
        self.point_index = -1

    def mouseMoveEvent(self, event):
        """Handle mouse move event"""

        self.mouse_x = event.x()
        self.mouse_y = event.y()

        if self.point_index >= 0:
            point = self._map_to_screen(QPointF(event.x() - self.x, event.y() - self.y))

            self.text = "(%d, %d)" % (point.x(), point.y())
            self.points[self.point_index] = point

            self.updated.emit()
        else:
            self.text = ""

        self.update()

    def paintEvent(self, event):
        """Draw widget"""

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)

        painter.fillRect(event.rect(), QColor("#626364"))

        rect = event.rect()
        scale = min(rect.width() / self.screen.width(), rect.height() / self.screen.height()) * 0.9

        w = self.screen.width() * scale
        h = self.screen.height() * scale

        x = (rect.width() - w) / 2
        y = (rect.height() - h) / 2

        self.x = x
        self.y = y
        self.scale = scale

        painter.fillRect(QRect(x, y, w, h), QColor("#000000"))

        painter.setPen(QColor("#d6d6d6"))
        painter.setBrush(QColor("#111111"))

        points = []

        for point in self.points:
            points.append(self._map_to_widget(point))

        painter.drawPolygon(QPolygonF(points))

        painter.setPen(QColor("#8a9fbb"))
        painter.setBrush(QColor("#8a9fbb"))

        for point in points:
            painter.drawEllipse(point, 4, 4)

        painter.setPen(QColor("#e6e6e6"))
        painter.setFont(self.font)
        painter.drawText(event.rect(), Qt.AlignCenter | Qt.TextWordWrap, self.text)

        painter.end()

    def centerTransformation(self):
        """Center transformation"""

        w = self.screen.width()
        h = self.screen.height()
        min_x = w
        min_y = h
        max_x = 0
        max_y = 0

        for point in self.points:
            if point.x() < min_x:
                min_x = point.x()

            if point.y() < min_y:
                min_y = point.y()

            if point.x() > max_x:
                max_x = point.x()

            if point.y() > max_y:
                max_y = point.y()

        x = w / 2 - (max_x - min_x) / 2
        y = h / 2 - (max_y - min_y) / 2

        index = 0

        for point in self.points:
            point.setX(point.x() - min_x + x)
            point.setY(point.y() - min_y + y)

            self.points[index] = point
            index = index + 1

        self.updated.emit()
        self.update()

    def wholeTransformation(self):
        """Transform to fill whole screen"""

        w = self.screen.width()
        h = self.screen.height()

        self.points[0] = QPointF(0, 0)
        self.points[1] = QPointF(w, 0)
        self.points[2] = QPointF(w, h)
        self.points[3] = QPointF(0, h)

        self.updated.emit()
        self.update()

    def leftTransformation(self):
        """Transform to fill left side of screen"""

        w = self.screen.width()
        h = self.screen.height()

        self.points[0] = QPointF(0, 0)
        self.points[1] = QPointF(w / 2, 0)
        self.points[2] = QPointF(w / 2, h)
        self.points[3] = QPointF(0, h)

        self.updated.emit()
        self.update()

    def rightTransformation(self):
        """Transform to fill right side of screen"""

        w = self.screen.width()
        h = self.screen.height()

        self.points[0] = QPointF(w / 2, 0)
        self.points[1] = QPointF(w, 0)
        self.points[2] = QPointF(w, h)
        self.points[3] = QPointF(w / 2, h)

        self.updated.emit()
        self.update()

    def setRect(self, rect):
        """Set size of transformed area

        Args:
            rect (QRectF, QRect):
        """

        if not isinstance(rect, QRect) or not isinstance(rect, QRectF):
            raise Exception("Given rect is not of type QRect or QRectF")

        self.screen = QRectF(rect.x(), rect.y(), rect.width(), rect.height())

        # reset transformation
        self.wholeTransformation()

    def getTransform(self):
        """Returns QTransform object"""

        t = QTransform()
        p = [QPointF(o.x(), o.y()) for o in self.points]
        w = self.screen.width()
        h = self.screen.height()
        q = [QPointF(0, 0), QPointF(w, 0), QPointF(w, h), QPointF(0, h)]

        QTransform.quadToQuad(QPolygonF(q), QPolygonF(p), t)

        return t


class PaddingDialog(Popup):
    """Padding popup dialog"""

    updated = pyqtSignal(int, int, int, int)

    def __init__(self, padding_left=0, padding_top=0, padding_right=0, padding_bottom=0, parent=None):
        super(PaddingDialog, self).__init__(parent)

        self._padding = [padding_left, padding_top, padding_right, padding_bottom]

        self.__ui__()

    def __ui__(self):

        self.ui_left = QSpinBox()
        self.ui_left.setRange(0, 1000)
        self.ui_left.setValue(self._padding[0])
        self.ui_left.valueChanged.connect(self._value_changed)

        self.ui_right = QSpinBox()
        self.ui_right.setRange(0, 1000)
        self.ui_right.setValue(self._padding[2])
        self.ui_right.valueChanged.connect(self._value_changed)

        self.ui_top = QSpinBox()
        self.ui_top.setRange(0, 1000)
        self.ui_top.setValue(self._padding[1])
        self.ui_top.valueChanged.connect(self._value_changed)

        self.ui_bottom = QSpinBox()
        self.ui_bottom.setRange(0, 1000)
        self.ui_bottom.setValue(self._padding[3])
        self.ui_bottom.valueChanged.connect(self._value_changed)

        self.ui_layout = QGridLayout()
        self.ui_layout.setSpacing(8)
        self.ui_layout.setContentsMargins(12, 12, 12, 12)

        self.ui_layout.addWidget(QLabel('Left'), 0, 0)
        self.ui_layout.addWidget(self.ui_left, 1, 0)

        self.ui_layout.addWidget(QLabel('Right'), 0, 1)
        self.ui_layout.addWidget(self.ui_right, 1, 1)

        self.ui_layout.addWidget(QLabel('Top'), 2, 0)
        self.ui_layout.addWidget(self.ui_top, 3, 0)

        self.ui_layout.addWidget(QLabel('Bottom'), 2, 1)
        self.ui_layout.addWidget(self.ui_bottom, 3, 1)

        self.setLayout(self.ui_layout)
        self.setWindowTitle('Padding')
        self.setGeometry(100, 300, 240, 128)

    def _value_changed(self, i):
        """Value spinbox has changed"""

        self._padding = [int(self.ui_left.value()), int(self.ui_top.value()),
                         int(self.ui_right.value()), int(self.ui_bottom.value())]
        self.updated.emit(*self._padding)

    def setPadding(self, padding_left=0, padding_top=0, padding_right=0, padding_bottom=0):
        """Set padding values

        Args:
            padding_left (int): left padding
            padding_top (int): top padding
            padding_right (int): right padding
            padding_bottom (int): bottom padding
        """

        self._padding = [padding_left, padding_top, padding_right, padding_bottom]


class AlignDialog(Popup):
    """Text align popup dialog"""

    updated = pyqtSignal(int, int)

    def __init__(self, horizontal, vertical, parent=None):
        super(AlignDialog, self).__init__(parent)

        self.align_horizontal = horizontal
        self.align_vertical = vertical

        self.__ui__()

    def __ui__(self):

        self.ui_horizontal = QComboBox()
        self.ui_horizontal.activated.connect(self._value_changed)

        try:
            h_index = [Qt.AlignLeft, Qt.AlignHCenter, Qt.AlignRight].index(self.align_horizontal)
        except ValueError:
            h_index = Qt.AlignHCenter

        try:
            v_index = [Qt.AlignTop, Qt.AlignVCenter, Qt.AlignBottom].index(self.align_vertical)
        except ValueError:
            v_index = Qt.AlignVCenter

        self.ui_horizontal.addItem("Left", QVariant(Qt.AlignLeft))
        self.ui_horizontal.addItem("Center", QVariant(Qt.AlignHCenter))
        self.ui_horizontal.addItem("Right", QVariant(Qt.AlignRight))
        self.ui_horizontal.setCurrentIndex(h_index)

        self.ui_vertical = QComboBox()
        self.ui_vertical.activated.connect(self._value_changed)

        self.ui_vertical.addItem("Top", QVariant(Qt.AlignTop))
        self.ui_vertical.addItem("Middle", QVariant(Qt.AlignVCenter))
        self.ui_vertical.addItem("Bottom", QVariant(Qt.AlignBottom))
        self.ui_vertical.setCurrentIndex(v_index)

        self.ui_layout = QGridLayout()
        self.ui_layout.setSpacing(8)
        self.ui_layout.setContentsMargins(12, 12, 12, 12)

        self.ui_layout.addWidget(QLabel('Horizontal'), 0, 0)
        self.ui_layout.addWidget(self.ui_horizontal, 1, 0)

        self.ui_layout.addWidget(QLabel('Vertical'), 2, 0)
        self.ui_layout.addWidget(self.ui_vertical, 3, 0)

        self.setWindowTitle('Align')
        self.setLayout(self.ui_layout)
        self.setGeometry(100, 300, 120, 128)

    def _value_changed(self, i):
        """Value has been changed"""

        self.align_horizontal = self.ui_horizontal.currentData()
        self.align_vertical = self.ui_vertical.currentData()

        self.updated.emit(self.align_horizontal, self.align_vertical)

    def setAlign(self, horizontal, vertical):
        """Set align values

        Args:
            horizontal (int): align type id
            vertical (int): align type id
        """

        self.align_horizontal = horizontal
        self.align_vertical = vertical


class ShadowDialog(Popup):
    """Shadow popup"""

    updated = pyqtSignal("QPoint", "int", "QColor")

    def __init__(self, offset, blur, color):
        super(ShadowDialog, self).__init__(None)

        self.offset = offset
        self.blur = blur
        self.color = color

        # initialize ui components
        self.ui_color_button = QPushButton("Set Color")
        self.ui_color_button.clicked.connect(self._color_action)

        self.ui_top = QSpinBox()
        self.ui_top.setRange(0, 100)
        self.ui_top.setValue(self.offset.y())
        self.ui_top.valueChanged.connect(self._value_changed)

        self.ui_left = QSpinBox()
        self.ui_left.setRange(0, 100)
        self.ui_left.setValue(self.offset.x())
        self.ui_left.valueChanged.connect(self._value_changed)

        self.ui_layout = VLayout()

        self.ui_controls_layout = GridLayout()
        self.ui_controls_layout.setSpacing(8)
        self.ui_controls_layout.setContentsMargins(12, 12, 12, 0)
        self.ui_controls_layout.addWidget(QLabel('Top'), 0, 0)
        self.ui_controls_layout.addWidget(self.ui_top, 1, 0)
        self.ui_controls_layout.addWidget(QLabel('Left'), 0, 1)
        self.ui_controls_layout.addWidget(self.ui_left, 1, 1)

        self.ui_button_layout = VLayout()
        self.ui_button_layout.setSpacing(8)
        self.ui_button_layout.setContentsMargins(12, 12, 12, 12)
        self.ui_button_layout.addWidget(self.ui_color_button)

        top = QWidget()
        top.setLayout(self.ui_controls_layout)

        line = QWidget()
        line.setObjectName("line-divider")

        self.ui_layout.addWidget(top)
        self.ui_layout.addWidget(line)

        bottom = QWidget()
        bottom.setLayout(self.ui_button_layout)

        self.ui_layout.addWidget(bottom)

        self.setLayout(self.ui_layout)

        self.setWindowTitle('Shadow')
        self.setGeometry(100, 300, 240, 140)

    def _color_action(self):
        """Value of color picker changed"""

        self.color = QColorDialog.getColor(self.color)
        self.updated.emit(self.offset, self.blur, self.color)

    def _value_changed(self, i):
        """Value of UI components changed"""

        self.offset = QPoint(self.ui_left.value(), self.ui_top.value())
        self.updated.emit(self.offset, self.blur, self.color)


class CompositionDialog(Popup):
    """Composition preferences popup"""

    updated = pyqtSignal("QSize")

    def __init__(self, size, parent=None):
        super(CompositionDialog, self).__init__(parent)

        self.composition = size
        self._ignore_update = False

        self.__ui__()
        self.update()

    def __ui__(self):

        self.ui_width = QSpinBox()
        self.ui_width.setRange(100, 32000)
        self.ui_width.valueChanged.connect(self._value_changed)

        self.ui_height = QSpinBox()
        self.ui_height.setRange(100, 32000)
        self.ui_height.valueChanged.connect(self._value_changed)

        self.ui_preset = QComboBox()
        self.ui_preset.currentIndexChanged.connect(self._preset_changed)

        self._update_list()

        self.ui_layout = QGridLayout()
        self.ui_layout.setSpacing(8)
        self.ui_layout.setContentsMargins(12, 12, 12, 12)

        self.ui_layout.addWidget(self.ui_preset, 0, 0, 1, 2)

        self.ui_layout.addWidget(self.ui_width, 1, 0)
        self.ui_layout.addWidget(self.ui_height, 1, 1)

        self.setLayout(self.ui_layout)

        self.setWindowTitle('Composition')
        self.setGeometry(100, 300, 240, 108)

    def update(self):
        """Update UI"""
        super(CompositionDialog, self).update()

        width = self.composition.width()
        height = self.composition.height()

        self.ui_width.setValue(width)
        self.ui_height.setValue(height)
        self.ui_preset.setItemText(0, "Current (%dx%d)" % (width, height))

    def _update_list(self):

        comp = self.composition
        presets = [("Current (%dx%d)" % (comp.width(), comp.height()), comp)]

        for screen in QGuiApplication.screens():
            width = screen.size().width()
            height = screen.size().height()
            mode = (screen.name() + " (%dx%d)" % (width, height), QSize(width, height))

            presets.append(mode)

        presets.extend([
            ("Full HD (1920x1080)", QSize(1920, 1080)),
            ("HD (1366x768)", QSize(1366, 768)),
            ("XGA (1024x768)", QSize(1024, 768)),
            ("WXGA (1280x800)", QSize(1280, 800)),
            ("SXGA (1280x1024)", QSize(1280, 1024)),
            ("UXGA (1600x1200)", QSize(1600, 1200)),
            ("SVGA (800x600)", QSize(800, 600))])

        self.ui_preset.clear()

        for preset in presets:
            self.ui_preset.addItem(preset[0], preset[1])

        self.ui_preset.insertSeparator(1)

    def _value_changed(self, i):
        """Value of spinner is changed"""

        if self._ignore_update:
            return False

        self.set_composition(QSize(self.ui_width.value(), self.ui_height.value()))

    def _preset_changed(self, index):

        rect = self.ui_preset.itemData(index)

        if rect is None or index == 0:
            return

        self.set_composition(rect)

    def set_composition(self, size):

        self._ignore_update = True
        self.composition = size
        self.updated.emit(size)
        self.update()
        self._ignore_update = False


class CaseDialog(Popup):

    updated = pyqtSignal(int)

    def __init__(self, case=0):
        super(CaseDialog, self).__init__(None)

        self.case = case

        self.__ui__()

    def __ui__(self):

        self.ui_case = QComboBox()
        self.ui_case.activated.connect(self.valueChanged)

        h_index = [0, 1, 2, 3].index(self.case)

        self.ui_case.addItem("Normal", QVariant(0))
        self.ui_case.addItem("Title", QVariant(1))
        self.ui_case.addItem("Upper", QVariant(2))
        self.ui_case.addItem("Lower", QVariant(3))
        self.ui_case.addItem("Capitalize", QVariant(4))
        self.ui_case.setCurrentIndex(h_index)

        self.ui_layout = QGridLayout()
        self.ui_layout.setSpacing(8)
        self.ui_layout.setContentsMargins(12, 12, 12, 12)

        self.ui_layout.addWidget(QLabel('Text Case'), 0, 0)
        self.ui_layout.addWidget(self.ui_case, 1, 0)

        self.setLayout(self.ui_layout)

        self.setWindowTitle('Align')
        self.setGeometry(100, 300, 120, 80)

    def valueChanged(self, i):

        self.case = self.ui_case.currentData()

        self.updated.emit(self.case)

    def setCase(self, case):

        self.case = case


class PreferencesDialog(Dialog):
    """Display preferences window"""

    updated = pyqtSignal()

    def __init__(self, parent):
        """Initialize PreferencesDialog

        Args:
            parent (DisplayPlugin): reference to DisplayPlugin instance
        """
        super(PreferencesDialog, self).__init__(None)

        self._parent = parent
        self._settings = self._parent.project.settings()
        self._preferences = CompositionPreferences.instance()
        p = self._preferences

        self.padding_popup = PaddingDialog(p.padding.left(), p.padding.top(), p.padding.right(), p.padding.bottom())
        self.padding_popup.updated.connect(self.padding_updated)

        self.align_popup = AlignDialog(p.align_horizontal, p.align_vertical)
        self.align_popup.updated.connect(self.align_updated)

        self.shadow_popup = ShadowDialog(QPoint(p.shadow_x, p.shadow_y), p.shadow_blur, p.shadow_color)
        self.shadow_popup.updated.connect(self.shadow_updated)

        self.composition_popup = CompositionDialog(p.composition)
        self.composition_popup.updated.connect(self.composition_updated)

        self.case_popup = CaseDialog(p.style_case_transform)
        self.case_popup.updated.connect(self.case_updated)

        self.__ui__()

    def __ui__(self):
        """Build UI"""

        self._ui_transform = TransformWidget()
        self._ui_transform.updated.connect(self._transform_event)

        # toolbar actions
        self._ui_output_menu = QMenu(self)

        self._ui_output_action = Button("Output", self)
        self._ui_output_action.setMenu(self._ui_output_menu)

        self._ui_font_action = QToolButton(self)
        self._ui_font_action.setIcon(QIcon(':/rc/font.png'))
        self._ui_font_action.clicked.connect(self.font_action)

        self._ui_shadow_action = QToolButton(self)
        self._ui_shadow_action.setIcon(QIcon(':/rc/shadow.png'))
        self._ui_shadow_action.clicked.connect(self.shadow_action)

        self._ui_align_action = QToolButton(self)
        self._ui_align_action.setIcon(QIcon(':/rc/align.png'))
        self._ui_align_action.clicked.connect(self.align_action)

        self._ui_case_action = QToolButton(self)
        self._ui_case_action.setIcon(QIcon(':/rc/case.png'))
        self._ui_case_action.clicked.connect(self.case_action)

        self._ui_color_action = QToolButton(self)
        self._ui_color_action.setIcon(QIcon(':/rc/color.png'))
        self._ui_color_action.clicked.connect(self.color_action)

        self._ui_composition_action = QToolButton(self)
        self._ui_composition_action.setIcon(QIcon(':/rc/zone-select.png'))
        self._ui_composition_action.clicked.connect(self.composition_action)

        self._ui_padding_action = QToolButton(self)
        self._ui_padding_action.setIcon(QIcon(':/rc/selection-select.png'))
        self._ui_padding_action.clicked.connect(self.padding_action)

        self._ui_testcard_action = QToolButton(self)
        self._ui_testcard_action.setIcon(QIcon(':/rc/testcard.png'))
        self._ui_testcard_action.setCheckable(True)
        self._ui_testcard_action.setChecked(self._preferences.display_test)
        self._ui_testcard_action.clicked.connect(self.testcard_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.addWidget(self._ui_font_action)
        self._ui_toolbar.addWidget(self._ui_shadow_action)
        self._ui_toolbar.addWidget(self._ui_align_action)
        self._ui_toolbar.addWidget(self._ui_case_action)
        self._ui_toolbar.addWidget(self._ui_color_action)
        self._ui_toolbar.addWidget(self._ui_composition_action)
        self._ui_toolbar.addWidget(self._ui_padding_action)
        self._ui_toolbar.addWidget(self._ui_testcard_action)
        self._ui_toolbar.addWidget(Spacer())
        self._ui_toolbar.addWidget(self._ui_output_action)

        self._ui_layout = VLayout()
        self._ui_layout.addWidget(self._ui_transform)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)
        self.setWindowTitle("Display preferences")
        self.setGeometry(100, 100, 480, 360)
        self.setMinimumSize(300, 200)
        self.moveCenter()

    def _transform_event(self):
        """Called when transformation is changed"""

        pass

    @staticmethod
    def _map_action_position(action):
        """Returns point in middle of action"""

        return action.mapToGlobal(action.rect().center())

    def emit(self, message, *args):
        """Emit message to all"""

        self._settings.set(message, args[0] if len(args) == 1 else args)
        self._parent.emit(message, *args)
        self._preferences.parse()

    def padding_updated(self, left_padding, top_padding, right_padding, bottom_padding):
        """Text padding updated"""

        self.emit('/clip/text/padding', left_padding, top_padding, right_padding, bottom_padding)

    def shadow_updated(self, offset, blur, color):
        """Shadow properties changed"""

        self.emit('/clip/text/shadow/x', offset.x())
        self.emit('/clip/text/shadow/y', offset.y())
        self.emit('/clip/text/shadow/color', color.name())
        self.emit('/clip/text/shadow/blur', blur)

    def align_updated(self, horizontal, vertical):
        """Align changed"""

        self.emit('/clip/text/align', horizontal)
        self.emit('/clip/text/valign', vertical)

    def case_updated(self, index):
        """Text case changed"""

        self.emit('/clip/text/transform', index)

    def composition_updated(self, size):
        """Composition size updated"""

        self.emit('/comp/width', size.width())
        self.emit('/comp/height', size.height())

    def font_action(self):
        """Font action clicked"""

        font, accept = QFontDialog.getFont(self._preferences.style_font)

        if accept:
            print('font', font)

        self.showWindow()

    def padding_action(self):
        """Padding action clicked"""

        self.padding_popup.showAt(self._map_action_position(self._ui_padding_action))

    def testcard_action(self):
        """Testcard action clicked"""

        self.emit('/comp/testcard', not self._preferences.display_test)

    def shadow_action(self):
        """Handle text shadow action click"""

        self.shadow_popup.showAt(self._map_action_position(self._ui_shadow_action))

    def color_action(self):
        """Handle color action click"""

        color = QColorDialog.getColor(self._preferences.style_color)

        if color:
            self.emit('/clip/text/color', color.name())

        self.showWindow()

    def composition_action(self):
        """Handle composition action click"""

        self.composition_popup.showAt(self._map_action_position(self._ui_composition_action))

    def align_action(self):
        """Handle text align action click"""

        self.align_popup.showAt(self._map_action_position(self._ui_align_action))

    def case_action(self):
        """Handle case action click"""

        self.case_popup.showAt(self._map_action_position(self._ui_case_action))


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
        self._ui_view_action.setIcon(Icon.colored(':/rc/menu.png', QColor('#555'), QColor('#e3e3e3')))
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

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)


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
        self._ui_view_action.setIcon(Icon.colored(':/rc/menu.png', QColor('#555'), QColor('#e3e3e3')))
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

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)
