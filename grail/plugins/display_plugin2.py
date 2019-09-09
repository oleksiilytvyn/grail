# -*- coding: UTF-8 -*-
"""
    grail.plugins.display_plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    2d graphics display

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
import os
import math

from grailkit.core import Signal

from grail.qt import *
from grail.qt import colors as qt_colors

from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from grail.core import Plugin, Viewer


class TestCardTexture(QPixmap):

    def __init__(self, width: int, height: int):
        """Generate test card QPixmap

        Args:
            width (int): image width
            height (int): image height
        Returns:
            QPixmap with test card pattern
        """
        super(TestCardTexture, self).__init__(width, height)

        comp = QRect(0, 0, width, height)
        offset = 50

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        painter.fillRect(comp, QColor(qt_colors.CONTAINER_ALT))

        pen = QPen(Qt.white)
        pen.setWidth(1)

        painter.setPen(pen)
        lines = int(max(comp.width(), comp.height()) / offset)

        for index in range(-lines, lines):
            o = index * offset

            painter.drawLine(0, comp.height() / 2 + o, comp.width(), comp.height() / 2 + o)
            painter.drawLine(comp.width() / 2 + o, 0, comp.width() / 2 + o, comp.height())

        pen = QPen(QColor(qt_colors.BASE))
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
        painter.drawText(box, Qt.AlignCenter | Qt.TextWordWrap, "Composition %d x %d" % (comp.width(), comp.height()))

        painter.end()


class DisplaySceneLayer:

    def __init__(self, scene):

        self._scene = scene
        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 0
        self._scale = 1.0
        self._angle = 0

        self._image_item = QGraphicsPixmapItem()

        self._video_item = QGraphicsVideoItem()
        self._video_item.setSize(QSizeF(640, 480))

        self._video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self._video_player.setVideoOutput(self._video_item)

        self._scene.addItem(self._video_item)
        self._scene.addItem(self._image_item)

    def set_volume(self, value: float):

        if value >= 1:
            value = 1
        elif value <= 0:
            value = 0

        self._video_player.setVolume(value * 100)

    @property
    def volume(self):
        return self._video_player.volume() / 100

    def set_opacity(self, value):
        self._video_item.setOpacity(value)

    @property
    def opacity(self):
        return self._video_item.opacity()

    def set_size(self, width: int, height: int):

        self._width = width
        self._height = height

        self._video_item.setSize(QSizeF(width, height))
        self._image_item.setSize(QSizeF(width, height))

    @property
    def size(self):

        return self._width, self._height

    def set_position(self, x: float, y: float):

        self._x = x
        self._y = y

    @property
    def position(self):
        return self._x, self._y

    def set_rotate(self, angle: float):

        self._angle = angle

    @property
    def angle(self):

        return self._angle

    def set_scale(self, scale: float):

        self._scale = scale

    @property
    def scale(self):
        return self._scale

    def set_source(self, path: str):

        self._video_player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))

    def play(self):

        self._video_player.play()

    def pause(self):

        self._video_player.pause()

    def stop(self):

        self._video_player.stop()

    def set_playback_position(self, position: float): pass

    def set_transport(self, value: str): pass


class DisplaySceneTextItem(QGraphicsItem):

    def __init__(self, text=""):
        super(DisplaySceneTextItem, self).__init__()

        self._text = ""
        self._rect = QRectF(0, 0, 100, 100)
        self._alignment = Qt.AlignCenter
        self._padding = QMarginsF(0, 0, 0, 0)
        self._font = QFont("decorative", 12)
        self._color = QColor("#fff")
        self._transform = None

        self.setText(text)

    def setText(self, text):

        self._text = text

    def text(self):

        return self._text

    def setFont(self, font):

        self._font = font

    def font(self):

        return self._font

    def setColor(self, color):

        self._color = color

    def color(self):

        return self._color

    def setAlignment(self, alignment):

        self._alignment = alignment

    def alignment(self):

        return self._alignment

    def setSize(self, size):

        self._font.setPointSizeF(size)

    def size(self):

        return self._font.pointSizeF()

    def setTextTransform(self, transform: str):
        pass

    def boundingRect(self):

        return self._rect

    def setRect(self, rect: QRectF):

        self._rect = QRectF(rect.x(), rect.y(), rect.width(), rect.height())

        self.update()

    def paint(self, painter, option, widget=None):

        painter.setFont(self._font)
        painter.setPen(self._color)

        p = self._padding
        rect = self.boundingRect()
        text = self._text

        # Title
        if self._transform == 1:
            text = text.title()
        # Upper
        elif self._transform == 2:
            text = text.upper()
        # Lower
        elif self._transform == 3:
            text = text.lower()
        # Capitalize
        elif self._transform == 4:
            text = text.capitalize()

        box = QRect(0, 0, rect.width(), rect.height())
        box.adjust(p.left(), p.top(), -p.right(), -p.bottom())

        painter.drawText(box, self._alignment | Qt.TextWordWrap, text)


class DisplayScene(QGraphicsScene):

    def __init__(self):
        super(DisplayScene, self).__init__()

        # Global parameters
        self._volume = 0
        self._width = 800
        self._height = 600
        self._testcard = False
        self._transition = 0

        # Internal
        self._layers = [DisplaySceneLayer(self), DisplaySceneLayer(self)]
        self._text_item = DisplaySceneTextItem("Hello World!")
        self._testcard_pixmap = TestCardTexture(self._width, self._height)
        self._testcard_item = QGraphicsPixmapItem(self._testcard_pixmap)
        self._background_item = QGraphicsRectItem()
        self._background_item.setBrush(QBrush(QColor("#000")))
        self._background_item.setRect(QRectF(0, 0, self.width(), self.height()))

        self.addItem(self._background_item)
        self.addItem(self._text_item)
        self.addItem(self._testcard_item)

    # Global Controls

    def set_volume(self, value: float):
        """Adjust global volume"""

        if value >= 1.0:
            self._volume = 1.0
        elif value <= 0:
            self._volume = 0.0
        else:
            self._volume = value

    @property
    def volume(self):
        """Returns global volume"""

        return self._volume

    def set_size(self, width: int, height: int):
        """Change scene size"""

        self._width = max(1, width)
        self._height = max(1, height)

        size_rect = QRectF(0, 0, self._width, self._height)

        self.setSceneRect(size_rect)
        self._background_item.setRect(size_rect)
        self._text_item.setRect(size_rect)
        self._testcard_pixmap = TestCardTexture(self._width, self._height)
        self._testcard_item.setPixmap(self._testcard_pixmap)

    @property
    def size(self):
        """Returns size of composition"""

        return [self._width, self._height]

    def set_testcard(self, flag: bool):
        """Weather to show or hide test card"""

        self._testcard = flag

        if flag:
            # todo: ensure correct test card size
            self._testcard_item.show()
        else:
            self._testcard_item.hide()

    @property
    def testcard(self):

        return self._testcard

    def set_transition(self, value: float):
        """Transition time in seconds"""

        if value >= 10:
            self._transition = 10
        elif value <= 0:
            self._transition = 0
        else:
            self._transition = value

    @property
    def transition(self):

        return self._transition

    def layer(self, layer: int):

        layer = layer - 1

        if layer in self._layers:
            return self._layers[layer]

        return None

    # Text Controls

    def set_text(self, text: str):

        self._text_item.setText(text)

    def set_text_color(self, color: str):

        self._text_item.setColor(QColor(color))

    def set_text_padding(self, l: float, t: float, r: float, b: float): pass

    def set_text_align(self, position: str): pass  # values("left", "center", "right")

    def set_text_valign(self, position: str): pass  # values("top", "middle", "bottom")

    def set_text_shadow_pos(self, x: int, y: int): pass

    def set_text_shadow_color(self, color: str): pass

    def set_text_shadow_blur(self, value: int): pass

    def set_text_transform(self, mode: str): pass  # values("normal", "title", "upper", "lower", "capitalize")

    def set_text_font_name(self, family: str): pass

    def set_text_font_size(self, pt: float): pass

    def set_text_font_style(self, style: str): pass

    # Layers Controls

    def clip_volume(self, layer: int, value: float):
        item = self.layer(layer)

        if item is None:
            return False

        item.set_volume(value)

    def clip_size(self, layer: int, width: int, height: int):

        item = self.layer(layer)

        if item is None:
            return False

        item.set_size(width, height)

    def clip_position(self, layer: int, x: float, y: float):

        item = self.layer(layer)

        if item is None:
            return False

        item.set_position(x, y)

    def clip_rotate(self, layer: int, angle: float):

        item = self.layer(layer)

        if item is None:
            return False

        item.set_rotate(angle)

    def clip_opacity(self, layer: int, opacity: float):

        item = self.layer(layer)

        if item is None:
            return False

        item.set_opacity(opacity)

    def clip_scale(self, layer: int, scale: float):

        item = self.layer(layer)

        if item is None:
            return False

        item.set_scale(scale)

    def clip_playback_source(self, layer: int, path: str):

        item = self.layer(layer)

        if item is None:
            return False

        item.set_source(path)

    def clip_playback_play(self, layer: int):

        item = self.layer(layer)

        if item is None:
            return False

        item.play()

    def clip_playback_pause(self, layer: int):

        item = self.layer(layer)

        if item is None:
            return False

        item.pause()

    def clip_playback_stop(self, layer: int):

        item = self.layer(layer)

        if item is None:
            return False

        item.stop()

    def clip_playback_position(self, layer: int, position: float):

        item = self.layer(layer)

        if item is None:
            return False

        item.set_playback_position(position)

    def clip_playback_transport(self, layer: int, value: str):

        item = self.layer(layer)

        if item is None:
            return False

        if value in ("Loop", "stop", "pause"):
            item.set_transport(value)


class DisplayWindow(QDialog):
    """Display full scene or portion of it"""

    def __init__(self, plugin=None):
        super(DisplayWindow, self).__init__(None)

        self._plugin = plugin
        self._scene = self._plugin.scene

        self._position = QPoint(0, 0)
        self._view = QGraphicsView(self._scene)
        self._view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._view.setContentsMargins(0, 0, 0, 0)
        self._view.setViewportMargins(0, 0, 0, 0)
        self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._layout = QHBoxLayout()
        self._layout.addWidget(self._view)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

        self.setGeometry(100, 100, 800, 600)
        # self.setFixedSize(800, 600)
        self.setWindowTitle("Display")
        self.setWindowFlags(Qt.Window |
                            Qt.FramelessWindowHint |
                            Qt.WindowSystemMenuHint |
                            Qt.WindowStaysOnTopHint |
                            Qt.NoDropShadowWindowHint |
                            Qt.X11BypassWindowManagerHint)

        self.moveCenter()

    def hideEvent(self, event):

        event.ignore()

    def mousePressEvent(self, event):

        self._position = event.globalPos()

    def mouseMoveEvent(self, event):

        delta = QPoint(event.globalPos() - self._position)

        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._position = event.globalPos()


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

        painter.fillRect(event.rect(), QColor(qt_colors.CONTAINER))

        rect = event.rect()
        scale = min(rect.width() / self.screen.width(), rect.height() / self.screen.height()) * 0.9

        w = self.screen.width() * scale
        h = self.screen.height() * scale

        x = (rect.width() - w) / 2
        y = (rect.height() - h) / 2

        self.x = x
        self.y = y
        self.scale = scale

        painter.fillRect(QRect(x, y, w, h), QColor(qt_colors.BASE))

        painter.setPen(QColor(qt_colors.CONTAINER_ALT))
        painter.setBrush(QColor(qt_colors.BASE_ALT))

        points = []

        for point in self.points:
            points.append(self._map_to_widget(point))

        painter.drawPolygon(QPolygonF(points))

        painter.setPen(QColor(qt_colors.WIDGET_ACTIVE))
        painter.setBrush(QColor(qt_colors.WIDGET_ACTIVE))

        for point in points:
            painter.drawEllipse(point, 4, 4)

        painter.setPen(QColor(qt_colors.WIDGET_TEXT))
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

        if not (isinstance(rect, QRect) or isinstance(rect, QRectF)):
            raise Exception("Given rect is not of type QRect or QRectF")

        self.screen = QRectF(rect.x(), rect.y(), rect.width(), rect.height())

        # reset transformation
        self.wholeTransformation()

    def getTransform(self):
        """Returns QTransform object"""

        t = QTransform()
        w, h = self.screen.width(), self.screen.height()
        q = [QPointF(0, 0), QPointF(w, 0), QPointF(w, h), QPointF(0, h)]
        p = [QPointF(o.x(), o.y()) for o in self.points]

        QTransform.quadToQuad(QPolygonF(q), QPolygonF(p), t)

        return t


class PaddingPopup(QPopup):
    """Padding popup dialog"""

    updated = pyqtSignal(int, int, int, int)

    def __init__(self, padding_left=0, padding_top=0, padding_right=0, padding_bottom=0, parent=None):
        super(PaddingPopup, self).__init__(parent)

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


class AlignPopup(QPopup):
    """Text align popup dialog"""

    updated = pyqtSignal(int, int)

    def __init__(self, horizontal, vertical, parent=None):
        super(AlignPopup, self).__init__(parent)

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


class ShadowPopup(QPopup):
    """Shadow popup"""

    updated = pyqtSignal("QPoint", "int", "QColor")

    def __init__(self, offset, blur, color):
        super(ShadowPopup, self).__init__(None)

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

        self.ui_layout = QVBoxLayout()

        self.ui_controls_layout = QGridLayout()
        self.ui_controls_layout.setSpacing(8)
        self.ui_controls_layout.setContentsMargins(12, 12, 12, 0)
        self.ui_controls_layout.addWidget(QLabel('Top'), 0, 0)
        self.ui_controls_layout.addWidget(self.ui_top, 1, 0)
        self.ui_controls_layout.addWidget(QLabel('Left'), 0, 1)
        self.ui_controls_layout.addWidget(self.ui_left, 1, 1)

        self.ui_button_layout = QVBoxLayout()
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


class CompositionPopup(QPopup):
    """Composition preferences popup"""

    updated = pyqtSignal("QSize")

    def __init__(self, size, parent=None):
        super(CompositionPopup, self).__init__(parent)

        self.composition = size
        self._ignore_update = False

        self.__ui__()
        self.update()

    def __ui__(self):

        self.ui_width = QSpinBox()
        self.ui_width.setRange(self.composition.width(), 32000)
        self.ui_width.valueChanged.connect(self._value_changed)

        self.ui_height = QSpinBox()
        self.ui_height.setRange(self.composition.height(), 32000)
        self.ui_height.valueChanged.connect(self._value_changed)

        self.ui_preset = QComboBox()
        self.ui_preset.currentIndexChanged.connect(self._preset_changed)

        self._update_list()
        self.ui_preset.setItemText(0, "Current (%dx%d)" % (self.composition.width(), self.composition.height()))

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
        super(CompositionPopup, self).update()

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
            ("HD (1280x720)", QSize(1366, 768)),
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


class CasePopup(QPopup):
    """Popup for selecting text transformation"""

    updated = pyqtSignal(int)

    def __init__(self, case=0):
        super(CasePopup, self).__init__(None)

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


class DisplayPreferencesDialog(QDialog):
    """Display preferences window"""

    updated = pyqtSignal()

    def __init__(self, parent):
        """Initialize PreferencesDialog

        Args:
            parent (DisplayPlugin): reference to DisplayPlugin instance
        """
        super(DisplayPreferencesDialog, self).__init__(None)

        self._plugin = parent
        self._settings = self._plugin.project.settings()

        self.padding_popup = PaddingPopup(0, 0, 0, 0)
        self.padding_popup.updated.connect(self.padding_updated)

        self.align_popup = AlignPopup(Qt.AlignHCenter, Qt.AlignVCenter)
        self.align_popup.updated.connect(self.align_updated)

        self.shadow_popup = ShadowPopup(QPoint(0, 0), 0, QColor("#000"))
        self.shadow_popup.updated.connect(self.shadow_updated)

        self.composition_popup = CompositionPopup(QSize(800, 600))
        self.composition_popup.updated.connect(self.composition_updated)

        self.case_popup = CasePopup(0)
        self.case_popup.updated.connect(self.case_updated)

        desktop = QApplication.desktop()
        desktop.resized.connect(self._screens_changed)
        desktop.screenCountChanged.connect(self._screens_changed)
        desktop.workAreaResized.connect(self._screens_changed)

        self.__ui__()

        self._fit_view()
        self._update_output_list()

    def __ui__(self):
        """Build UI"""

        # Display output
        self._ui_display_menu = QMenu(self)

        self._ui_display_source_action = QPushButton("Source", self)
        self._ui_display_source_action.setCheckable(True)
        self._ui_display_source_action.setChecked(True)
        self._ui_display_source_action.clicked.connect(self.source_action)

        self._ui_display_dest_action = QPushButton("Destination", self)
        self._ui_display_dest_action.setCheckable(True)
        self._ui_display_dest_action.setChecked(False)
        self._ui_display_dest_action.clicked.connect(self.dest_action)

        self._ui_display_output_action = QPushButton("Disabled", self)
        self._ui_display_output_action.setMenu(self._ui_display_menu)

        self._ui_display_transform = TransformWidget()
        self._ui_display_transform.setRect(QRect(0, 0, 420, 280))

        self._ui_display_toolbar = QToolBar()
        self._ui_display_toolbar.addWidget(self._ui_display_source_action)
        self._ui_display_toolbar.addWidget(self._ui_display_dest_action)
        self._ui_display_toolbar.addStretch()
        self._ui_display_toolbar.addWidget(self._ui_display_output_action)

        self._ui_display_layout = QVBoxLayout()
        self._ui_display_layout.addWidget(self._ui_display_transform)
        self._ui_display_layout.addWidget(self._ui_display_toolbar)

        self._ui_display = QWidget(None)
        self._ui_display.setLayout(self._ui_display_layout)

        # Composition
        self._ui_view = QGraphicsView(self._plugin.scene)
        self._ui_view.setAlignment(Qt.AlignCenter)
        self._ui_view.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing)
        self._ui_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self._ui_view.setBackgroundBrush(QBrush(QColor(qt_colors.WIDGET)))
        self._ui_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._ui_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._ui_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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
        self._ui_testcard_action.setChecked(True)
        self._ui_testcard_action.clicked.connect(self.testcard_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.addWidget(self._ui_font_action)
        self._ui_toolbar.addWidget(self._ui_shadow_action)
        self._ui_toolbar.addWidget(self._ui_align_action)
        self._ui_toolbar.addWidget(self._ui_case_action)
        self._ui_toolbar.addWidget(self._ui_color_action)
        self._ui_toolbar.addStretch()
        self._ui_toolbar.addWidget(self._ui_composition_action)
        self._ui_toolbar.addWidget(self._ui_padding_action)
        self._ui_toolbar.addWidget(self._ui_testcard_action)

        # Composition
        self._ui_comp_layout = QVBoxLayout()
        self._ui_comp_layout.addWidget(self._ui_view)
        self._ui_comp_layout.addWidget(self._ui_toolbar)

        self._ui_comp = QWidget()
        self._ui_comp.setLayout(self._ui_comp_layout)

        self._ui_stack = QStackedWidget()
        self._ui_stack.addWidget(self._ui_comp)
        self._ui_stack.addWidget(self._ui_display)
        self._ui_stack.setCurrentIndex(0)

        # Outputs
        self._ui_list = QListWidget()
        self._ui_list.itemClicked.connect(self.item_clicked)

        self._ui_add_action = QToolButton(self)
        self._ui_add_action.setIcon(QIcon(':/rc/add.png'))
        self._ui_add_action.clicked.connect(self.add_action)

        self._ui_remove_action = QToolButton(self)
        self._ui_remove_action.setIcon(QIcon(':/rc/remove.png'))
        self._ui_remove_action.clicked.connect(self.remove_action)

        self._ui_list_toolbar = QToolBar()
        self._ui_list_toolbar.addWidget(self._ui_add_action)
        self._ui_list_toolbar.addStretch()
        self._ui_list_toolbar.addWidget(self._ui_remove_action)

        self._ui_outputs_layout = QVBoxLayout()
        self._ui_outputs_layout.addWidget(self._ui_list)
        self._ui_outputs_layout.addWidget(self._ui_list_toolbar)

        self._ui_outputs = QWidget()
        self._ui_outputs.setMinimumWidth(120)
        self._ui_outputs.setMaximumWidth(240)
        self._ui_outputs.setLayout(self._ui_outputs_layout)

        # Global
        self._ui_splitter = QSplitter()
        self._ui_splitter.addWidget(self._ui_outputs)
        self._ui_splitter.addWidget(self._ui_stack)
        self._ui_splitter.setCollapsible(0, False)
        self._ui_splitter.setCollapsible(1, False)
        self._ui_splitter.setHandleWidth(1)
        self._ui_splitter.setStretchFactor(0, 0)
        self._ui_splitter.setStretchFactor(1, 1)
        self._ui_splitter.setSizes([200, 600])

        self._ui_layout = QVBoxLayout()
        self._ui_layout.addWidget(self._ui_splitter)

        # Set default view
        self._ui_list.addItem(QListWidgetItem("Composition"))
        self._ui_list.setCurrentRow(0)

        self.setLayout(self._ui_layout)
        self.setWindowTitle("Display Preferences")
        self.setGeometry(100, 100, 800, 360)
        self.setMinimumSize(800, 400)
        self.moveCenter()

    def resizeEvent(self, event):

        super(DisplayPreferencesDialog, self).resizeEvent(event)

        self._fit_view()
        # todo: don't fit if view is not active

    def _fit_view(self):

        scene = self._plugin.scene
        factor = min(self._ui_view.width()/scene.width(), self._ui_view.height()/scene.height()) * 0.9

        t = self._ui_view.transform()
        t.reset()
        t.scale(factor, factor)

        self._ui_view.setTransform(t)

    def _screens_changed(self):
        pass

    def emit(self, message, *args, **kwargs):
        """Emit messages to plugin"""

        self._plugin.emit(message, *args)

    def source_action(self):

        self._ui_display_source_action.setChecked(True)
        self._ui_display_dest_action.setChecked(False)

    def dest_action(self):

        self._ui_display_source_action.setChecked(False)
        self._ui_display_dest_action.setChecked(True)

    def add_action(self):
        """Add output action"""

        self._plugin.add_output()
        self._update_output_list()

    def remove_action(self):
        """Remove output action"""

        index = self._ui_list.currentRow()

        if index > 0:
            self._ui_list.takeItem(index)

            output = self._plugin.outputs.pop(index - 1)

    def _update_output_list(self):
        """Update list of outputs"""

        self._ui_list.clear()

        # Add composition item
        item = QListWidgetItem("Composition")

        self._ui_list.addItem(item)

        # Add outputs items
        index = 1

        for output in self._plugin.outputs:
            item = QListWidgetItem(f"Output {index}")
            item.output = output

            self._ui_list.addItem(item)

            index += 1

    def item_clicked(self, item=None):
        """Output list item clicked"""

        index = self._ui_list.currentRow()

        self._ui_stack.setCurrentIndex(0 if index == 0 else 1)
        # todo: load selected window settings

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

        self._settings.set('/comp/width', size.width())
        self._settings.set('/comp/height', size.height())

        self._plugin.emit('/comp/width', size.width())
        self._plugin.emit('/comp/height', size.height())

        # todo: update transform widget
        # self._ui_transform.setRect(QRect(0, 0, size.width(), size.height()))

    def font_action(self):
        """Font action clicked"""

        font, accept = QFontDialog.getFont()

        if accept:
            self.emit('/clip/text/font/name', str(font.family()))
            self.emit('/clip/text/font/size', font.pointSize())
            self.emit('/clip/text/font/style', str(font.styleName()))

        self.showWindow()

    def padding_action(self):
        """Padding action clicked"""

        self.padding_popup.showAt(self._map_action_position(self._ui_padding_action))

    def testcard_action(self):
        """Testcard action clicked"""

        self.emit('/comp/testcard', True)

    def shadow_action(self):
        """Handle text shadow action click"""

        self.shadow_popup.showAt(self._map_action_position(self._ui_shadow_action))

    def color_action(self):
        """Handle color action click"""

        color = QColorDialog.getColor()

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

    @staticmethod
    def _map_action_position(action):
        """Returns point in middle of action"""

        return action.mapToGlobal(action.rect().center())


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

        desktop = QApplication.desktop()
        desktop.resized.connect(self._screens_changed)
        desktop.screenCountChanged.connect(self._screens_changed)
        desktop.workAreaResized.connect(self._screens_changed)

        self._outputs = []

        self._scene = DisplayScene()
        self._scene.set_size(1920, 1080)
        s = self._scene
        s.set_testcard(False)
        s.set_text("Lorem ipsum dolore sit amet")
        s.set_text_align("middle")

        self._preferences_dialog = DisplayPreferencesDialog(self)
        self._preferences_dialog.show()

        # Notify other plugins and viewers that DisplayPlugin is loaded
        self.emit("!display/instance")

    def cue_cb(self, cue):

        self.scene.set_text(cue.name)

    def testcard_action(self, action=None):
        """Show or hide test card"""

        # called from Actions
        if not action:
            action = self.menu_testcard
            action.setChecked(not action.isChecked())

        self._scene.set_testcard(action.isChecked())

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


class DisplayViewer(Viewer):
    """View composition output as viewer"""

    id = "display-viewer"
    name = "Display Output"
    author = "Grail Team"
    description = "View composition output"

    def __init__(self, *args, **kwargs):
        super(DisplayViewer, self).__init__(*args, **kwargs)

        self.connect("!display/instance", self._display_instance)

        self.__ui__()

    def resizeEvent(self, event):

        super(DisplayViewer, self).resizeEvent(event)

        self._fit_clicked()

    def __ui__(self):

        self._ui_view = QGraphicsView()
        self._ui_view.setAlignment(Qt.AlignCenter)
        self._ui_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self._ui_view.setBackgroundBrush(QBrush(QColor(qt_colors.WIDGET)))
        self._ui_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._ui_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._ui_fit = QPushButton("fit")
        self._ui_fit.clicked.connect(self._fit_clicked)

        self._ui_scale_factor = QDoubleSpinBox()
        self._ui_scale_factor.setMinimum(10)
        self._ui_scale_factor.setMaximum(200)
        self._ui_scale_factor.setValue(100)
        self._ui_scale_factor.setMaximumWidth(70)
        self._ui_scale_factor.valueChanged.connect(self._scale_changed)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon(':/rc/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("DisplayPreviewViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addStretch()
        self._ui_toolbar.addWidget(self._ui_fit)
        self._ui_toolbar.addWidget(self._ui_scale_factor)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.addWidget(self._ui_view)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def _fit_clicked(self):
        """Fit button clicked"""

        scene = self._ui_view.scene()

        if scene is None:
            return False

        factor = min(self.width()/scene.width(), self.height()/scene.height()) * 0.9

        self._scale_scene(factor)

    def _scale_changed(self, value):
        """Scale factor changed"""

        self._scale_scene(float(value) / 100)

    def _scale_scene(self, factor):
        """Scale scene by factor, 1.0 is actual size"""

        t = self._ui_view.transform()
        t.reset()
        t.scale(factor, factor)

        self._ui_view.setTransform(t)
        self._ui_scale_factor.setValue(factor * 100)

    def _display_instance(self):
        """Display plugin si available"""

        self._ui_view.setScene(DisplayPlugin.instance().scene)
        self._fit_clicked()

#
# Display Layer Viewer
# ~~~~~~~~~~~~~~~~~~~~
#


class GrabberVideoSurface(QAbstractVideoSurface):
    """Video surface for grabbing frames from video"""

    def __init__(self, parent):
        super(GrabberVideoSurface, self).__init__()

        self._size = QSize(0, 0)
        self._format = QImage.Format_Invalid
        self._count = 0
        self._parent = parent

        self.image = None

    def start(self, _format):

        image_format = QVideoFrame.imageFormatFromPixelFormat(_format.pixelFormat())
        size = _format.frameSize()

        if image_format != QImage.Format_Invalid and not size.isEmpty():
            self._format = image_format
            self._size = size

            QAbstractVideoSurface.start(self, _format)

            return True
        else:
            return False

    def present(self, frame):

        self._count += 1

        if frame.map(QAbstractVideoBuffer.ReadOnly):
            self.image = QImage(frame.bits(), frame.width(), frame.height(), frame.bytesPerLine(), self._format)

            self._parent.updated.emit()

            frame.unmap()

        return True

    def supportedPixelFormats(self, handle_type):

        if handle_type == QAbstractVideoBuffer.NoHandle:
            return [QVideoFrame.Format_RGB32,
                    QVideoFrame.Format_ARGB32,
                    QVideoFrame.Format_ARGB32_Premultiplied,
                    QVideoFrame.Format_RGB565,
                    QVideoFrame.Format_RGB555]
        else:
            return []


class FrameGrabber:
    """Helper class for generating preview images for video files"""

    _instance = None

    def __init__(self):

        self.video_surface = GrabberVideoSurface(self)

        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.video_surface)
        self.player.setPlaybackRate(0.33)
        self.player.setMuted(True)

        self.updated = Signal()

    def load(self, path):

        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.player.play()
        self.player.setPosition(500)
        self.player.pause()

    def grab(self):
        """Returns QImage, a random frame from video"""

        return self.video_surface.image

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()

        return cls._instance


class ClipItem:

    def __init__(self, path, pixmap):

        self.path = path
        self.pixmap = pixmap

        self.original_width = pixmap.width()
        self.original_height = pixmap.height()
        self.width = pixmap.width()
        self.height = pixmap.height()
        self.x = 0
        self.y = 0
        self.angle = 0
        self.scale = 1.0
        self.opacity = 1.0
        self.volume = 1.0
        self.transport = "stop"


class ClipWidget(QWidget):

    def __init__(self, parent=None):
        super(ClipWidget, self).__init__(parent)

        self._items = []
        self._selected = -1
        self._rows = 0
        self._columns = 0
        self._size = 180
        self.size = 180

        self.COLOR_NORMAL = QColor(qt_colors.BASE_ALT)
        self.COLOR_ACTIVE = QColor(qt_colors.WIDGET_ACTIVE)
        self.COLOR_TEXT = QColor(qt_colors.WIDGET_TEXT)
        self.COLOR_TEXT_ACTIVE = QColor(qt_colors.BASE)

        # self.setMouseTracking(True)

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setBrush(self.COLOR_NORMAL)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # todo: make it more scalable/flexible
        batch_size = self._size
        width = self.width()
        height = self.height()

        length = len(self._items)
        columns = self._columns
        rows = self._rows
        row = 0
        column = -1
        text_height = 20

        for index, item in enumerate(self._items):
            column += 1
            selected = self._selected == index

            if column >= columns:
                column = 0
                row += 1

            bo = 3
            bx, by, bw, bh = column * batch_size, row * batch_size, batch_size, batch_size
            size = item.pixmap.size().scaled(QSize(bw, bh - text_height), Qt.KeepAspectRatio)
            ox = bw / 2 - size.width() / 2
            oy = (bh - text_height) / 2 - size.height() / 2
            text_box = QRect(bx + bo, by + bo + bh - text_height, bw - bo * 2, text_height - bo * 2)
            label = item.path.split("/")[-1]

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(self.COLOR_TEXT_ACTIVE if not selected else self.COLOR_ACTIVE, Qt.SolidPattern))

            # Frame
            painter.drawRect(bx, by, bw, bh)

            # Image
            painter.setBrush(QBrush(self.COLOR_NORMAL, Qt.SolidPattern))
            painter.drawRect(bx + bo, by + bo, bw - bo * 2, bh - bo * 2)
            painter.drawPixmap(bx + bo + ox, by + bo + oy, size.width() - bo * 2, size.height() - bo * 2, item.pixmap)

            # Text label
            painter.setBrush(QBrush(self.COLOR_ACTIVE if selected else self.COLOR_TEXT_ACTIVE, Qt.SolidPattern))
            painter.drawRect(text_box)
            painter.setPen(QPen(self.COLOR_TEXT_ACTIVE if selected else self.COLOR_TEXT, 0, Qt.SolidLine, Qt.SquareCap))
            painter.drawText(text_box, Qt.AlignLeft | Qt.AlignVCenter, label)

    def update(self):
        super(ClipWidget, self).update()

        self._size = self.size
        width = max(self.width(), 1)

        if self._size > width:
            self._size = width

        length = len(self._items)

        self._columns = max(math.floor(width / self._size), 1)
        self._rows = math.ceil(length / self._columns)

        if self._columns * self._size < width:
            self._size = math.floor(width / self._columns)

        self.setMinimumHeight(self._rows * self._size)
        self.repaint()

    def resizeEvent(self, event):
        super(ClipWidget, self).resizeEvent(event)

        self.update()

    def mousePressEvent(self, event):

        self._selected = self.itemIndexAt(event.pos())
        self.repaint()

        QWidget.mousePressEvent(self, event)

    def addItem(self, item):
        """Add item to list"""

        self._items.append(item)
        self.update()

    def removeItem(self, item):

        self._items.remove(item)
        self.update()

    def item(self, index):
        """Returns item at index, items distributed from top to bottom, left to right"""

        return self._items[index] if index < len(self._items) else None

    def itemIndexAt(self, pos):

        x, y = pos.x(), pos.y()
        s = self._size
        ax, ay = x % s, y % s
        c, r = math.floor((x - ax) / s), math.floor((y - ay) / s)
        index = c + r * self._columns

        return index if index < len(self._items) else None

    def itemAt(self, pos):
        """Returns item at given position"""

        x, y = pos.x(), pos.y()
        s = self._size
        ax, ay = x % s, y % s
        c, r = math.floor((x - ax) / s), math.floor((y - ay) / s)
        index = c + r * self._columns

        return self.item(index) if index < len(self._items) else None

    def setBatchSize(self, size: int):
        """Resize items batch size"""

        self.size = size


class ClipList(QScrollArea):

    itemDoubleClicked = pyqtSignal(object)
    itemClicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super(ClipList, self).__init__(parent)

        self._widget = ClipWidget()
        self._items = {}
        self._files = []
        self._files_stack = []

        self.setAcceptDrops(True)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFrameShape(QFrame.NoFrame)

        # fix inside padding
        self.setStyleSheet("QScrollArea { margin: 0; padding: 0; }")

        original = self.verticalScrollBar()
        self.scrollbar = QScrollBar(Qt.Vertical, self)
        self.scrollbar.valueChanged.connect(original.setValue)
        original.valueChanged.connect(self.scrollbar.setValue)

        self.grabber = FrameGrabber.instance()
        self.grabber.updated.connect(lambda: self._frame_received())

        self.update_scrollbar()

        self.setWidget(self._widget)
        self.setWidgetResizable(True)

    def update_scrollbar(self):

        original = self.verticalScrollBar()

        if original.value() == original.maximum() and original.value() == 0:
            self.scrollbar.hide()
        else:
            self.scrollbar.show()

        self.scrollbar.setPageStep(original.pageStep())
        self.scrollbar.setRange(original.minimum(), original.maximum())
        self.scrollbar.resize(8, self.rect().height())
        self.scrollbar.move(self.rect().width() - 8, 0)

    def paintEvent(self, event):

        QScrollArea.paintEvent(self, event)
        self.update_scrollbar()

    def dragEnterEvent(self, event):

        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):

        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):

        if event.mimeData().hasUrls():

            for url in event.mimeData().urls():
                path = self._normalize_path(url)

                # skip already added files
                if self.hasItem(path):
                    continue

                # add files for later processing
                self._files_stack.append(path)

            event.acceptProposedAction()

        self._process_files()

    def mouseDoubleClickEvent(self, event):

        position = self._widget.mapFromParent(event.pos())
        item = self._widget.itemAt(position)

        if item:
            self.itemDoubleClicked.emit(item)

    def mousePressEvent(self, event):

        position = self._widget.mapFromParent(event.pos())
        item = self._widget.itemAt(position)

        if item:
            self.itemClicked.emit(item)

    def itemAt(self, position):

        return self._widget.itemAt(position)

    def addItem(self, path):

        path = self._normalize_path(path)

        # skip already added files
        if self.hasItem(path):
            return False

        # add files for later processing
        self._files_stack.append(path)

        self._process_files()

    def removeItem(self, path):

        if self.hasItem(path):
            path = self._normalize_path(path)

            self._files.remove(path)
            item = self._items[path]
            self._widget.removeItem(item)

            del self._items[path]

    def hasItem(self, path):

        return self._normalize_path(path) in self._files

    def _normalize_path(self, path):

        if type(path) == QUrl:
            result = os.path.abspath(str(QUrl(path).toLocalFile()))
        elif type(path) == str:
            result = os.path.abspath(path)
        else:
            result = None

        return result

    def _add(self, path, pixmap):

        # if size is 0x0 don't load image it can broke view
        if pixmap.size().isEmpty():
            return False

        item = ClipItem(path, pixmap)

        self._files.append(path)
        self._items[path] = item
        self._widget.addItem(item)

    def _process_files(self):

        if len(self._files_stack) == 0:
            return False

        path = self._files_stack[0]
        ext = str(path.split('.')[-1]).lower()

        if ext in ['jpg', 'jpeg', 'png', 'gif']:
            pixmap = QPixmap(path)
            path = self._files_stack.pop(0)

            self._add(path, pixmap)
            self._process_files()
        elif ext in ['mp4', 'm4v', 'avi']:
            self.grabber.load(path)

    def _frame_received(self):

        # Prevent from processing non-existent files
        if len(self._files_stack) <= 0:
            return False

        pixmap = QPixmap(self.grabber.grab())
        path = self._files_stack.pop(0)

        self._add(path, pixmap)
        self._process_files()


class DisplayLayerInspector(QDialog):

    def __init__(self, parent=None):
        super(DisplayLayerInspector, self).__init__(parent)

        self.__ui__()

    def __ui__(self):

        self._ui_label = QLabel("No item")
        self._ui_label.setWordWrap(True)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.addWidget(self._ui_label)

        self.setLayout(self._ui_layout)

    def setItem(self, item):

        if item is None:
            self._ui_label.setText("No item")

        self._ui_label.setText(item.path)


class DisplayLayerTransportWidget(QWidget):

    def __init__(self, parent=None):
        super(DisplayLayerTransportWidget, self).__init__(parent)

        self.__ui__()

    def __ui__(self):

        self._ui_label = QLabel("Item name")
        self._ui_label.setWordWrap(True)
        self._ui_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self._ui_pixmap = QLabel()

        self._ui_layout = QHBoxLayout()
        self._ui_layout.setSpacing(6)
        self._ui_layout.addWidget(self._ui_pixmap)
        self._ui_layout.addWidget(self._ui_label)

        self.setLayout(self._ui_layout)

    def setItem(self, item):

        if item is None:
            self._ui_label.setText("Item not selected")
            self._ui_pixmap.setPixmap(None)
        else:
            self._ui_label.setText(item.path)
            self._ui_pixmap.setPixmap(item.pixmap.scaled(100, 100, Qt.KeepAspectRatio))


class DisplayLayerViewer(Viewer):

    id = "display-layer"
    name = "Display Layer"
    author = "Grail Team"
    description = "Manage Layers"

    def __init__(self, *args, **kwargs):
        super(DisplayLayerViewer, self).__init__(*args, **kwargs)

        self._layer_id = 1

        self.connect('/app/close', self._close)

        self.__ui__()

    def __ui__(self):

        self._ui_list = ClipList()
        self._ui_list.itemClicked.connect(self.item_clicked)
        self._ui_list.itemDoubleClicked.connect(self.item_doubleclicked)
        self.customContextMenuRequested.connect(self.context_menu)

        self._inspector = DisplayLayerInspector()

        self._ui_transport = DisplayLayerTransportWidget()

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon(':/rc/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_play_action = QToolButton()
        self._ui_play_action.setText("Play/pause")
        self._ui_play_action.setIcon(Icon(':/rc/play.png'))
        self._ui_play_action.clicked.connect(self.play_action)

        self._ui_stop_action = QToolButton()
        self._ui_stop_action.setText("Stop")
        self._ui_stop_action.setIcon(Icon(':/rc/stop.png'))
        self._ui_stop_action.clicked.connect(self.stop_action)

        self._ui_label = QLabel("Layer 1")

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("DisplayMediaBinViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addStretch()
        self._ui_toolbar.addWidget(self._ui_label)
        self._ui_toolbar.addWidget(self._ui_play_action)
        self._ui_toolbar.addWidget(self._ui_stop_action)

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._ui_list)
        self._layout.addWidget(self._ui_transport)
        self._layout.addWidget(self._ui_toolbar)

        self.setLayout(self._layout)

        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def play_action(self):

        playing = True

        if playing:
            self.emit(f"/clip/{self._layer_id}/playback/pause")
        else:
            self.emit(f"/clip/{self._layer_id}/playback/play")

    def stop_action(self):

        self.emit(f"/clip/{self._layer_id}/playback/stop")

    def context_menu(self, pos):

        item = self._ui_list.itemAt(pos)

        add_action = QAction("Add")
        add_action.triggered.connect(lambda: self.item_add(item))

        edit_action = QAction("Edit")
        edit_action.triggered.connect(lambda: self.item_inspector(item))

        remove_action = QAction("Remove")
        remove_action.triggered.connect(lambda: self.item_remove(item))

        inspector_action = QAction("Inspector")
        inspector_action.triggered.connect(lambda: self.item_inspector(item))

        menu = QMenu("Clip", self)

        if item:
            menu.addAction(add_action)
            menu.addAction(edit_action)
            menu.addAction(remove_action)
            menu.addSeparator()
            menu.addAction(inspector_action)
        else:
            menu.addAction(add_action)
            menu.addSeparator()
            menu.addAction(inspector_action)

        return menu.exec_(self.mapToGlobal(pos))

    def item_clicked(self, item):

        self._ui_transport.setItem(item)

    def item_doubleclicked(self, item):

        layer = self._layer_id

        self.emit(f"/clip/{layer}/size", item.width, item.height)
        self.emit(f"/clip/{layer}/pos", item.x, item.y)
        self.emit(f"/clip/{layer}/rotate", item.angle)
        self.emit(f"/clip/{layer}/opacity", item.opacity)
        self.emit(f"/clip/{layer}/volume", item.volume)
        self.emit(f"/clip/{layer}/scale", item.scale)
        self.emit(f"/clip/{layer}/playback/source", item.path)

        self.emit(f"/clip/{layer}/playback/position", 0)
        self.emit(f"/clip/{layer}/playback/transport", item.transport)
        self.emit(f"/clip/{layer}/playback/play")

    def item_add(self, item=None):

        location = QStandardPaths.locate(QStandardPaths.DocumentsLocation, "",
                                         QStandardPaths.LocateDirectory)
        path, ext = QFileDialog.getOpenFileName(self, "Add File...", location, "*")

        if path:
            self._ui_list.addItem(path)

    def item_inspector(self, item=None):

        if item is None:
            return False

        self._inspector.setItem(item)
        self._inspector.showWindow()

    def item_remove(self, item=None):

        if item:
            self._ui_list.removeItem(item.path)

    def _close(self):

        self._inspector.close()
