# -*- coding: UTF-8 -*-
"""
    grail.plugins.display_plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    2D Graphics scene

    :copyright: (c) 2016-2020 by Oleksii Lytvyn (http://alexlitvin.name)
    :license: GNU, see LICENSE for more details.
"""
from grail.qt import *
from grail.qt import colors as qt_colors


class TestCardTexture(QtGui.QPixmap):

    def __init__(self, width: int, height: int):
        """Generate test card QPixmap

        Args:
            width (int): image width
            height (int): image height
        Returns:
            QPixmap with test card pattern
        """
        super(TestCardTexture, self).__init__(width, height)

        comp = QtCore.QRect(0, 0, width, height)
        offset = 50

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)

        painter.fillRect(comp, QtGui.QColor(qt_colors.CONTAINER_ALT))

        pen = QtGui.QPen(QtCore.Qt.white)
        pen.setWidth(1)

        painter.setPen(pen)
        lines = int(max(comp.width(), comp.height()) / offset)

        for index in range(-lines, lines):
            o = index * offset

            painter.drawLine(0, comp.height() / 2 + o, comp.width(), comp.height() / 2 + o)
            painter.drawLine(comp.width() / 2 + o, 0, comp.width() / 2 + o, comp.height())

        pen = QtGui.QPen(QtGui.QColor(qt_colors.BASE))
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

            painter.drawEllipse(QtCore.QPoint(comp.width() / 2 + ox, comp.height() / 2), radius, radius)

        box = QtCore.QRect(comp.topLeft(), comp.bottomRight())
        box.adjust(10, 10, -10, -10)

        painter.setPen(QtCore.Qt.white)
        painter.setFont(QtGui.QFont("decorative", 24))
        painter.drawText(box, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap,
                         "Composition %d x %d" % (comp.width(), comp.height()))

        painter.end()


class DisplaySceneLayer:

    def __init__(self, scene, layer=1):

        self._scene = scene
        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 0
        self._scale = 1.0
        self._angle = 0
        self._layer_id = layer

        self._video_item = QtMultimediaWidgets.QGraphicsVideoItem()
        self._video_item.setSize(QtCore.QSizeF(640, 480))
        self._video_item.setAspectRatioMode(QtCore.Qt.IgnoreAspectRatio)

        self._video_player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
        self._video_player.setVideoOutput(self._video_item)
        self._video_player.positionChanged.connect(self._position_cb)
        self._video_player.durationChanged.connect(self._duration_cb)
        self._video_player.stateChanged.connect(self._state_cb)

        self.connect(f"/clip/{self._layer_id}/playback/play", self._video_player.play)
        self.connect(f"/clip/{self._layer_id}/playback/pause", self._video_player.pause)
        self.connect(f"/clip/{self._layer_id}/playback/stop", self._video_player.stop)
        self.connect(f"/clip/{self._layer_id}/playback/position", self._video_player.setPosition)

        self._scene.addItem(self._video_item)

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

        self._resize()

    @property
    def size(self):

        return self._width, self._height

    def set_position(self, x: float, y: float):

        self._x = x
        self._y = y

        self._resize()

    @property
    def position(self):
        return self._x, self._y

    def set_rotate(self, angle: float):

        self._angle = angle

        self._resize()

    @property
    def angle(self):

        return self._angle

    def set_scale(self, scale: float):

        self._scale = scale

        self._resize()

    @property
    def scale(self):
        return self._scale

    def set_source(self, path: str):

        self._video_player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path)))
        self._video_item.show()

    def play(self):

        self._video_player.play()

    def pause(self):

        self._video_player.pause()

    def stop(self):

        self._video_player.stop()

    def set_playback_position(self, position: float): pass

    def set_transport(self, value: str): pass

    def _resize(self):

        sw, sh = self._scene.width(), self._scene.height()
        w, h = self._width, self._height
        tx, ty = w / 2, h / 2

        self._video_item.setPos(sw / 2 - w / 2 + self._x, sh / 2 - h / 2 + self._y)
        self._video_item.setSize(QtCore.QSizeF(w, h))

        t = QtGui.QTransform()
        t.translate(tx, ty)
        t.rotate(self._angle)
        t.scale(self._scale, self._scale)
        t.translate(-tx, -ty)
        self._video_item.setTransform(t)

    def _position_cb(self, position):

        self.emit(f"!clip/{self._layer_id}/playback/position", position)

    def _duration_cb(self, length):

        self.emit(f"!clip/{self._layer_id}/playback/duration", length)

    def _state_cb(self, state):

        self.emit(f"!clip/{self._layer_id}/playback/state", state)

    def emit(self, message, *args):
        """Emit message"""

        Application.instance().signals.emit(message, *args)

    def connect(self, message, fn):
        """Connect event handler"""

        Application.instance().signals.connect(message, fn)


class DisplaySceneTextItem(QtWidgets.QGraphicsItem):

    def __init__(self, text=""):
        super(DisplaySceneTextItem, self).__init__()

        self._text = text
        self._rect = QtCore.QRectF(0, 0, 100, 100)
        self._alignment = QtCore.Qt.AlignCenter
        self._padding = QtCore.QMarginsF(0, 0, 0, 0)
        self._font = QtGui.QFont("decorative", 12)
        self._color = QtGui.QColor("#fff")
        self._transform = None
        self._shadow_blur = 0
        self._shadow_color = QtGui.QColor("#000")
        self._shadow_position = QtCore.QPointF(0, 0)

    def set_text(self, text):

        self._text = text

    def text(self):

        return self._text

    def set_font(self, font):

        self._font = font

    def font(self):

        return self._font

    def set_color(self, color):

        self._color = color

    def color(self):

        return self._color

    def set_alignment(self, alignment):

        self._alignment = alignment

    def alignment(self):

        return self._alignment

    def set_padding(self, l, t, r, b):

        self._padding = QtCore.QMarginsF(l, t, r, b)

    def set_size(self, size_pt):

        self._font.setPointSizeF(size_pt)

    def size(self):

        return self._font.pointSizeF()

    def set_transform(self, transform: str):

        self._transform = transform

    def boundingRect(self):

        return self._rect

    def set_rect(self, rect: QtCore.QRectF):

        self._rect = QtCore.QRectF(rect.x(), rect.y(), rect.width(), rect.height())

        self.update()

    def set_shadow(self, x: int, y: int, blur: int, color: str):

        self._shadow_blur = blur
        self._shadow_position = QtCore.QPointF(x, y)
        self._shadow_color = QtGui.QColor(color)

    def shadow_blur(self):

        return self._shadow_blur

    def shadow_color(self):

        return self._shadow_color.name()

    def shadow_pos(self):

        return self._shadow_position.x(), self._shadow_position.y()

    def paint(self, painter, option, widget=None):

        painter.setFont(self._font)

        p = self._padding
        rect = self.boundingRect()
        text = self._text

        # Title
        if self._transform == "title":
            text = text.title()
        # Upper
        elif self._transform == "upper":
            text = text.upper()
        # Lower
        elif self._transform == "lower":
            text = text.lower()
        # Capitalize
        elif self._transform == "capitalize":
            text = text.capitalize()

        box = QtCore.QRect(0, 0, rect.width(), rect.height())
        box.adjust(p.left(), p.top(), -p.right(), -p.bottom())

        box_shadow = QtCore.QRect(self._shadow_position.x(), self._shadow_position.y(), rect.width(), rect.height())
        box_shadow.adjust(p.left(), p.top(), -p.right(), -p.bottom())

        painter.setPen(self._shadow_color)
        painter.drawText(box_shadow, self._alignment | QtCore.Qt.TextWordWrap, text)

        painter.setPen(self._color)
        painter.drawText(box, self._alignment | QtCore.Qt.TextWordWrap, text)


class DisplayScene(QtWidgets.QGraphicsScene):

    def __init__(self):
        super(DisplayScene, self).__init__()

        # Global parameters
        self._volume = 1.0
        self._opacity = 1.0
        self._width = 800
        self._height = 600
        self._testcard = False
        self._transition = 0

        # Internal
        self._text_item = DisplaySceneTextItem("")
        self._testcard_pixmap = TestCardTexture(self._width, self._height)
        self._testcard_item = QtWidgets.QGraphicsPixmapItem(self._testcard_pixmap)
        self._background_item = QtWidgets.QGraphicsRectItem()
        self._background_item.setBrush(QtGui.QBrush(QtGui.QColor("#000")))
        self._background_item.setRect(QtCore.QRectF(0, 0, self.width(), self.height()))

        self.addItem(self._background_item)
        self._layers = [DisplaySceneLayer(self, layer=1), DisplaySceneLayer(self, layer=2)]
        self.addItem(self._text_item)
        self.addItem(self._testcard_item)

        self.set_testcard(False)

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

    def set_opacity(self, opacity: float):

        self._opacity = opacity

    @property
    def opacity(self):

        return self._opacity

    def set_size(self, width: int, height: int):
        """Change scene size"""

        self._width = max(1, width)
        self._height = max(1, height)

        size_rect = QtCore.QRectF(0, 0, self._width, self._height)

        self.setSceneRect(size_rect)
        self._background_item.setRect(size_rect)
        self._text_item.set_rect(size_rect)
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

        if 0 <= layer < len(self._layers):
            return self._layers[layer]

        return None

    # Text Controls

    def set_text(self, text: str):

        self._text_item.set_text(text)
        self.update()

    def set_text_color(self, color: str):

        self._text_item.set_color(QtGui.QColor(color))

    def set_text_padding(self, l: float, t: float, r: float, b: float):

        self._text_item.set_padding(l, t, r, b)

    def set_text_align(self, horizontal: str, vertical: str):
        # "left", "center", "right", "top", "middle", "bottom"

        alignment = QtCore.Qt.AlignCenter

        if horizontal == "left":
            alignment = QtCore.Qt.AlignLeft
        elif horizontal == "center":
            alignment = QtCore.Qt.AlignHCenter
        elif horizontal == "right":
            alignment = QtCore.Qt.AlignRight

        if vertical == "top":
            alignment |= QtCore.Qt.AlignTop
        elif vertical == "middle":
            alignment |= QtCore.Qt.AlignVCenter
        elif vertical == "bottom":
            alignment |= QtCore.Qt.AlignBottom

        self._text_item.set_alignment(alignment)

    def set_text_shadow_pos(self, x: int, y: int):

        self._text_item.set_shadow(x, y, self._text_item.shadow_blur(), self._text_item.shadow_color())

    def set_text_shadow_color(self, color: str):

        x, y = self._text_item.shadow_pos()

        self._text_item.set_shadow(x, y, self._text_item.shadow_blur(), color)

    def set_text_shadow_blur(self, blur: int):

        x, y = self._text_item.shadow_pos()

        self._text_item.set_shadow(x, y, blur, self._text_item.shadow_color())

    def set_text_shadow(self, x, y, blur, color):

        self._text_item.set_shadow(x, y, blur, color)

    def set_text_transform(self, mode: str):
        # values("normal", "title", "upper", "lower", "capitalize")

        self._text_item.set_transform(mode)

    def set_text_font_name(self, family: str):

        style = self._text_item.font().styleName()
        size = self._text_item.font().pointSize()

        self.set_text_font(size, family, style)

    def set_text_font_size(self, pt: float):

        font = self._text_item.font()
        font.setPointSizeF(pt)

        self._text_item.set_font(font)

    def set_text_font_style(self, style: str):

        font = self._text_item.font()
        font.setStyleName(style)

        self._text_item.set_font(font)

    def set_text_font(self, size_pt: float, name: str, style: str):

        font = QtGui.QFont(name, size_pt)
        font.setStyleName(style)

        self._text_item.set_font(font)

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

        if value in ("loop", "stop", "pause"):
            item.set_transport(value)


class DisplayWindow(QtWidgets.QDialog):
    """Display full scene or portion of it"""

    def __init__(self, plugin=None):
        super(DisplayWindow, self).__init__(None)

        self._plugin = plugin
        self._scene = self._plugin.scene
        self._position = QtCore.QPoint(0, 0)
        self._transformation = QtGui.QTransform()
        self._transformation_points = None

        self._scene.changed.connect(lambda _: self.repaint())
        self._scene.sceneRectChanged.connect(lambda rect: self.repaint())

        self.setGeometry(0, 0, 800, 600)
        self.setWindowTitle("Display Output")
        self.setFrameless(False)

    def paintEvent(self, event):

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)

        # draw background
        painter.fillRect(event.rect(), QtCore.Qt.black)

        target = QtCore.QRectF(0, 0, self.width(), self.height())
        source = QtCore.QRectF(0, 0, self._scene.width(), self._scene.height())

        painter.setTransform(self._transformation)

        # draw scene items
        self._scene.render(painter, target, source, QtCore.Qt.IgnoreAspectRatio)

        painter.end()

    def setGeometry(self, x, y, width, height):

        super(DisplayWindow, self).setGeometry(x, y, width, height)
        self.setFixedSize(width, height)

    def resizeEvent(self, event):

        self.setTransform(self._transformation)

    def hideEvent(self, event):

        event.ignore()

    def setTransform(self, transform: QtGui.QTransform):

        self._transformation = transform

        self.repaint()

    def setFrameless(self, flag: bool = True):

        if flag:
            self.setWindowFlags(QtCore.Qt.Window |
                                QtCore.Qt.FramelessWindowHint |
                                QtCore.Qt.WindowSystemMenuHint |
                                QtCore.Qt.WindowStaysOnTopHint |
                                QtCore.Qt.NoDropShadowWindowHint)
        else:
            self.setWindowFlags(QtCore.Qt.Window |
                                QtCore.Qt.WindowSystemMenuHint |
                                QtCore.Qt.WindowStaysOnTopHint |
                                QtCore.Qt.NoDropShadowWindowHint |
                                QtCore.Qt.WindowTitleHint |
                                QtCore.Qt.WindowCloseButtonHint)

    def setName(self, name: str):

        self.setWindowTitle("Output: %s" % name)

    def setTransformationPoints(self, points):

        self._transformation_points = points

    def points(self):

        return self._transformation_points


class DisplaySceneView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(DisplaySceneView, self).__init__(parent)

        self._scale = 1.0
        self._position = QtCore.QPoint(0, 0)
        self._press_point = QtCore.QPoint(0, 0)
        self._background_color = QtGui.QColor(qt_colors.WIDGET)

        self._scene = None

    def scene(self):

        return self._scene

    def setScene(self, scene: QtWidgets.QGraphicsScene):

        if scene is None:
            return False

        if self._scene is not None:
            self._scene.changed.disconnect(self._scene_changed)
            self._scene.sceneRectChanged.disconnect(self._scene_rect_changed)

        self._scene = scene
        self._scene.changed.connect(self._scene_changed)
        self._scene.sceneRectChanged.connect(self._scene_rect_changed)

    def setScale(self, factor: float):

        self._scale = factor
        self._position = QtCore.QPoint(0, 0)
        self.repaint()

    def paintEvent(self, event):

        scene_width, scene_height = self._scene.width() * self._scale, self._scene.height() * self._scale
        width, height = self.width(), self.height()

        painter = QtGui.QPainter()
        painter.begin(self)
        # draw background
        painter.fillRect(event.rect(), self._background_color)

        target = QtCore.QRectF(self._position.x() + width / 2 - scene_width / 2,
                               self._position.y() + height / 2 - scene_height / 2, scene_width, scene_height)
        source = QtCore.QRectF(0, 0, self._scene.width(), self._scene.height())

        # draw scene items
        self._scene.render(painter, target, source, QtCore.Qt.IgnoreAspectRatio)

        painter.end()

    def mouseMoveEvent(self, event):

        sw = self._scene.width() * self._scale
        sh = self._scene.height() * self._scale

        # DO nothing if scene fits in view
        if sw < self.width() and sh < self.height():
            self._position = QtCore.QPoint(0, 0)

            return

        dx = event.x() - self._press_point.x()
        dy = event.y() - self._press_point.y()

        f = 30  # space from edge of widget to scene image
        x = dx + self.width() / 2 - sw / 2
        y = dy + self.height() / 2 - sh / 2

        if f >= x >= self.width() - sw - f:
            self._position.setX(dx)

        if f >= y >= self.height() - sh - f:
            self._position.setY(dy)

        self.repaint()

    def mousePressEvent(self, event):

        dx = event.x() - self._position.x()
        dy = event.y() - self._position.y()

        self._press_point = QtCore.QPoint(dx, dy)

    def mouseReleaseEvent(self, event):

        pass

    def _scene_changed(self, scene):

        self.repaint()

    def _scene_rect_changed(self, rect):

        self.repaint()
