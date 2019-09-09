# -*- coding: UTF-8 -*-
"""
    grail.plugins.display.layer_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Composition scene layer Viewer

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
import os
import math

from grailkit.core import Signal

from grail.qt import *
from grail.qt import colors as qt_colors
from PyQt5.QtMultimedia import *

from grail.core import Viewer


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
