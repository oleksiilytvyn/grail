# -*- coding: UTF-8 -*-
"""
    grail.plugins.display.preferences_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Display preferences dialog

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
import math

from grail.qt import *
from grail.qt import colors as qt_colors
from .scene import DisplaySceneView


class OutputConfiguration:

    def __init__(self, name: str, x: int, y: int, width: int, height: int,
                 disabled: bool = False, frameless: bool = True):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.disabled = disabled
        self.frameless = frameless


# noinspection PyPep8Naming
class TransformWidget(QtWidgets.QWidget):
    """Corner-pin transformation with composition display"""

    updated = QtSignal()

    def __init__(self, parent=None, width=800, height=600, enable_affine=True):
        super(TransformWidget, self).__init__(parent)

        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.setMouseTracking(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self._rect = QtCore.QRectF(0, 0, width, height)
        self._points = []
        self.fill()

        self._x = 0
        self._y = 0
        self._scale = 1.0
        self._index = -1
        self._last_index = -1
        self._font = QtGui.QFont("decorative", 14)
        self._text = ""
        self._mouse_x = 0
        self._mouse_y = 0
        self._mouse_hold = False
        self._mouse_hold_x = 0
        self._mouse_hold_y = 0
        self._allow_affine = True

        self._context_menu = QtWidgets.QMenu("Menu", self)

        whole_action = QtWidgets.QAction('Whole area', self._context_menu)
        whole_action.triggered.connect(self.fill)

        left_action = QtWidgets.QAction('Left side', self._context_menu)
        left_action.triggered.connect(self.left)

        right_action = QtWidgets.QAction('Right side', self._context_menu)
        right_action.triggered.connect(self.right)

        top_action = QtWidgets.QAction('Top half', self._context_menu)
        top_action.triggered.connect(self.top)

        bottom_action = QtWidgets.QAction('Bottom half', self._context_menu)
        bottom_action.triggered.connect(self.bottom)

        center_action = QtWidgets.QAction('Center', self._context_menu)
        center_action.triggered.connect(self.center)

        self._affine_action = QtWidgets.QAction("Affine transformation", self._context_menu)
        self._affine_action.setCheckable(True)
        self._affine_action.setChecked(True)
        self._affine_action.triggered.connect(self._toggle_affine_action)

        self._context_menu.addAction(left_action)
        self._context_menu.addAction(right_action)
        self._context_menu.addAction(top_action)
        self._context_menu.addAction(bottom_action)
        self._context_menu.addAction(whole_action)
        self._context_menu.addSeparator()
        self._context_menu.addAction(center_action)

        if enable_affine:
            self._context_menu.addAction(self._affine_action)

        self.customContextMenuRequested.connect(self._context_menu_action)

    def mousePressEvent(self, event):
        """Handle mouse press event"""

        self._mouse_hold = True
        index = 0
        x, y = event.x(), event.y()

        points = []

        for point in self._points:
            point = self._map_to_widget(point)
            px, py = point.x(), point.y()

            points.append((px, py))

            if math.sqrt(pow(px - x, 2) + pow(py - y, 2)) <= 5:
                self._index = index
                self._last_index = index
                self._mouse_hold_x, self._mouse_hold_y = x - px, y - py

            index = index + 1

        pairs = [
            [points[0], points[1]],
            [points[1], points[2]],
            [points[2], points[3]],
            [points[3], points[0]]
        ]

        for pair in pairs:
            px, py = (pair[0][0] + pair[1][0]) / 2, (pair[0][1] + pair[1][1]) / 2

            if math.sqrt(pow(px - x, 2) + pow(py - y, 2)) <= 5:
                self._index = index
                self._last_index = index
                self._mouse_hold_x, self._mouse_hold_y = x - px, y - py

            index = index + 1

        self.setFocus()

    def mouseReleaseEvent(self, event):
        """Handle mouse release event"""

        self._mouse_hold = False
        self._index = -1

    def mouseMoveEvent(self, event):
        """Handle mouse move event"""

        self._mouse_x = event.x()
        self._mouse_y = event.y()

        # Corner points
        if 0 <= self._index <= 3 and self._allow_affine:
            point = self._map_to_screen(QtCore.QPointF(event.x() - self._x, event.y() - self._y))

            self._text = "(%d, %d)" % (point.x(), point.y())
            self._points[self._index] = point

            self.updated.emit()
        elif 4 <= self._index <= 7:
            text_side = ""
            axis = 0  # 0 is horizontal, 1 is vertical
            index_a, index_b = 0, 1

            if self._index == 4:
                text_side = "Top"
                index_a, index_b, axis = 0, 1, 1
            elif self._index == 5:
                text_side = "Right"
                index_a, index_b, axis = 1, 2, 0
            elif self._index == 6:
                text_side = "Bottom"
                index_a, index_b, axis = 2, 3, 1
            elif self._index == 7:
                text_side = "Left"
                index_a, index_b, axis = 3, 0, 0

            point = self._map_to_screen(QtCore.QPointF(event.x() - self._x, event.y() - self._y))
            pa, pb = self._points[index_a], self._points[index_b]
            ix, iy = (pa.x() + pb.x()) / 2, (pa.y() + pb.y()) / 2
            dx, dy = point.x() - ix, point.y() - iy

            if not self._allow_affine:
                if axis == 0:
                    dy = 0
                else:
                    dx = 0

            self._points[index_a] = QtCore.QPointF(pa.x() + dx, pa.y() + dy)
            self._points[index_b] = QtCore.QPointF(pb.x() + dx, pb.y() + dy)

            self._text = "%s side" % text_side
            self.updated.emit()
        # No point
        else:
            self._text = ""

        self.update()

    def keyPressEvent(self, event):

        key = event.key()
        dx, dy = 0, 0

        if key == QtCore.Qt.Key_Up:
            dy = 1
        elif key == QtCore.Qt.Key_Down:
            dy = -1
        elif key == QtCore.Qt.Key_Left:
            dx = 1
        elif key == QtCore.Qt.Key_Right:
            dx = -1

        if 0 <= self._last_index <= 3:
            p = self._points[self._last_index]
            self._points[self._last_index] = QtCore.QPointF(p.x() - dx, p.y() - dy)

        self.update()

    def paintEvent(self, event):
        """Draw widget"""

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)

        painter.fillRect(event.rect(), QtGui.QColor(qt_colors.CONTAINER))

        rect = event.rect()
        scale = min(rect.width() / self._rect.width(), rect.height() / self._rect.height()) * 0.9

        w = self._rect.width() * scale
        h = self._rect.height() * scale

        x = (rect.width() - w) / 2
        y = (rect.height() - h) / 2

        self._x = x
        self._y = y
        self._scale = scale

        painter.fillRect(QtCore.QRect(x, y, w, h), QtGui.QColor(qt_colors.BASE))

        painter.setPen(QtGui.QColor(qt_colors.CONTAINER_ALT))
        painter.setBrush(QtGui.QColor(qt_colors.BASE_ALT))

        points = []
        index = 0

        for point in self._points:
            points.append(self._map_to_widget(point))

        painter.drawPolygon(QtGui.QPolygonF(points))

        painter.setPen(QtGui.QColor(qt_colors.WIDGET_ACTIVE))
        painter.setBrush(QtGui.QColor(qt_colors.WIDGET_ACTIVE))

        if self._allow_affine:
            for point in points:
                f = 1 if index == self._last_index else 0
                painter.drawEllipse(point, 4 + f, 4 + f)
                index = index + 1

        # Draw side handles
        pairs = [
            [points[0], points[1]],
            [points[1], points[2]],
            [points[2], points[3]],
            [points[3], points[0]]
        ]

        for pair in pairs:
            p = QtCore.QPointF((pair[0].x() + pair[1].x()) / 2, (pair[0].y() + pair[1].y()) / 2)
            painter.drawEllipse(p, 3, 3)
            index = index + 1

        painter.setPen(QtGui.QColor(qt_colors.WIDGET_TEXT))
        painter.setFont(self._font)
        painter.drawText(event.rect(), QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, self._text)

        painter.end()

    def center(self):
        """Center transformation"""

        w = self._rect.width()
        h = self._rect.height()
        min_x = w
        min_y = h
        max_x = 0
        max_y = 0

        for point in self._points:
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

        for point in self._points:
            point.setX(point.x() - min_x + x)
            point.setY(point.y() - min_y + y)

            self._points[index] = point
            index = index + 1

        self.updated.emit()
        self.update()

    def fill(self):
        """Transform to fill whole screen"""

        w, h = self._rect.width(), self._rect.height()

        self.setPoints(0, 0, w, 0, w, h, 0, h)

    def left(self):
        """Transform to fill left side of screen"""

        w, h = self._rect.width(), self._rect.height()

        self.setPoints(0, 0, w / 2, 0, w / 2, h, 0, h)

    def right(self):
        """Transform to fill right side of screen"""

        w, h = self._rect.width(), self._rect.height()

        self.setPoints(w / 2, 0, w, 0, w, h, w / 2, h)

    def top(self):
        """Transform to fill top half of screen"""

        w, h = self._rect.width(), self._rect.height()

        self.setPoints(0, 0, w, 0, w, h / 2, 0, h / 2)

    def bottom(self):
        """Transform to fill bottom half of screen"""

        w, h = self._rect.width(), self._rect.height()

        self.setPoints(0, h / 2, w, h / 2, w, h, 0, h)

    def setPoints(self, x1, y1, x2, y2, x3, y3, x4, y4):
        """Set transformation points"""

        self._points = [QtCore.QPointF(x1, y1), QtCore.QPointF(x2, y2), QtCore.QPointF(x3, y3), QtCore.QPointF(x4, y4)]

        self.updated.emit()
        self.update()

    def setRect(self, rect):
        """Set size of transformed area

        Args:
            rect (QtCore.QRectF, QtCore.QRect):
        """

        if not (isinstance(rect, QtCore.QRect) or isinstance(rect, QtCore.QRectF)):
            raise Exception("Given rect is not of type QtCore.QRect or QtCore.QRectF")

        self._rect = QtCore.QRectF(rect)
        self.fill()

    def rect(self):
        """Returns source rect"""

        return QtCore.QRectF(self._rect)

    def boundingRect(self):
        """Returns transformation quad bounding rect"""

        min_x = self._rect.width()
        min_y = self._rect.height()
        max_x = 0
        max_y = 0

        for point in self._points:
            if point.x() < min_x:
                min_x = point.x()

            if point.y() < min_y:
                min_y = point.y()

            if point.x() > max_x:
                max_x = point.x()

            if point.y() > max_y:
                max_y = point.y()

        return QtCore.QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

    def setAllowAffine(self, flag: bool):
        """Weather to allow affine transformation or only size and position can be changed"""

        self._allow_affine = bool(flag)

    def allowAffine(self):
        """Returns true if affine transformations is allowed"""

        return self._allow_affine

    def transformation(self):
        """Returns closes possible transformation (QTransform) object from points positions"""

        t = QtGui.QTransform()
        w, h = self._rect.width(), self._rect.height()

        # Source polygon, Destination Polygon, reference to QTransform
        QtGui.QTransform.quadToQuad(QtGui.QPolygonF([QtCore.QPointF(0, 0),
                                                     QtCore.QPointF(w, 0),
                                                     QtCore.QPointF(w, h),
                                                     QtCore.QPointF(0, h)]), QtGui.QPolygonF(self._points), t)

        return t

    def points(self, raw=False):
        """Returns points mapped to given rectangle"""

        if raw:
            values = []

            for p in self._points:
                values.append(p.x())
                values.append(p.y())

            return values
        else:
            return [QtCore.QPointF(p.x(), p.y()) for p in self._points]

    def _toggle_affine_action(self):

        flag = self._affine_action.isChecked()

        self._allow_affine = flag
        self._affine_action.setChecked(flag)

    def _context_menu_action(self, event):
        """Open context menu"""

        self._context_menu.exec_(self.mapToGlobal(event))

    def _map_to_widget(self, point):
        """Map point to widget coordinates"""

        return QtCore.QPointF(self._x + self._scale * point.x(), self._y + self._scale * point.y())

    def _map_to_screen(self, point):
        """Map point to screen coordinates"""

        return QtCore.QPointF(point.x() / self._scale, point.y() / self._scale)


class PaddingPopup(QPopup):
    """Padding popup dialog"""

    updated = QtSignal(int, int, int, int)

    def __init__(self, padding_left=0, padding_top=0, padding_right=0, padding_bottom=0, parent=None):
        super(PaddingPopup, self).__init__(parent)

        self._padding = [padding_left, padding_top, padding_right, padding_bottom]

        self.__ui__()

    def __ui__(self):
        self.ui_left = QtWidgets.QSpinBox()
        self.ui_left.setRange(0, 1000)
        self.ui_left.setValue(self._padding[0])
        self.ui_left.valueChanged.connect(self._value_changed)

        self.ui_right = QtWidgets.QSpinBox()
        self.ui_right.setRange(0, 1000)
        self.ui_right.setValue(self._padding[2])
        self.ui_right.valueChanged.connect(self._value_changed)

        self.ui_top = QtWidgets.QSpinBox()
        self.ui_top.setRange(0, 1000)
        self.ui_top.setValue(self._padding[1])
        self.ui_top.valueChanged.connect(self._value_changed)

        self.ui_bottom = QtWidgets.QSpinBox()
        self.ui_bottom.setRange(0, 1000)
        self.ui_bottom.setValue(self._padding[3])
        self.ui_bottom.valueChanged.connect(self._value_changed)

        self.ui_layout = QtWidgets.QGridLayout()
        self.ui_layout.setSpacing(8)
        self.ui_layout.setContentsMargins(12, 12, 12, 12)

        self.ui_layout.addWidget(QtWidgets.QLabel('Left'), 0, 0)
        self.ui_layout.addWidget(self.ui_left, 1, 0)

        self.ui_layout.addWidget(QtWidgets.QLabel('Right'), 0, 1)
        self.ui_layout.addWidget(self.ui_right, 1, 1)

        self.ui_layout.addWidget(QtWidgets.QLabel('Top'), 2, 0)
        self.ui_layout.addWidget(self.ui_top, 3, 0)

        self.ui_layout.addWidget(QtWidgets.QLabel('Bottom'), 2, 1)
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

    updated = QtSignal(str, str)

    def __init__(self, horizontal, vertical, parent=None):
        super(AlignPopup, self).__init__(parent)

        self.align_horizontal = horizontal
        self.align_vertical = vertical

        self.__ui__()

    def __ui__(self):

        self.ui_horizontal = QtWidgets.QComboBox()
        self.ui_horizontal.activated.connect(self._value_changed)

        try:
            h_index = [QtCore.Qt.AlignLeft, QtCore.Qt.AlignHCenter, QtCore.Qt.AlignRight].index(self.align_horizontal)
        except ValueError:
            h_index = QtCore.Qt.AlignHCenter

        try:
            v_index = [QtCore.Qt.AlignTop, QtCore.Qt.AlignVCenter, QtCore.Qt.AlignBottom].index(self.align_vertical)
        except ValueError:
            v_index = QtCore.Qt.AlignVCenter

        self.ui_horizontal.addItem("Left", "left")
        self.ui_horizontal.addItem("Center", "center")
        self.ui_horizontal.addItem("Right", "right")
        self.ui_horizontal.setCurrentIndex(h_index)

        self.ui_vertical = QtWidgets.QComboBox()
        self.ui_vertical.activated.connect(self._value_changed)

        self.ui_vertical.addItem("Top", "top")
        self.ui_vertical.addItem("Middle", "middle")
        self.ui_vertical.addItem("Bottom", "bottom")
        self.ui_vertical.setCurrentIndex(v_index)

        self.ui_layout = QtWidgets.QGridLayout()
        self.ui_layout.setSpacing(8)
        self.ui_layout.setContentsMargins(12, 12, 12, 12)

        self.ui_layout.addWidget(QtWidgets.QLabel('Horizontal'), 0, 0)
        self.ui_layout.addWidget(self.ui_horizontal, 1, 0)

        self.ui_layout.addWidget(QtWidgets.QLabel('Vertical'), 2, 0)
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

    updated = QtSignal("QPoint", "int", "QColor")

    def __init__(self, offset, blur, color):
        super(ShadowPopup, self).__init__(None)

        self.offset = offset
        self.blur = blur
        self.color = color

        # initialize ui components
        self.ui_color_button = QtWidgets.QPushButton("Set Color")
        self.ui_color_button.clicked.connect(self._color_action)

        self.ui_top = QtWidgets.QSpinBox()
        self.ui_top.setRange(0, 100)
        self.ui_top.setValue(self.offset.y())
        self.ui_top.valueChanged.connect(self._value_changed)

        self.ui_left = QtWidgets.QSpinBox()
        self.ui_left.setRange(0, 100)
        self.ui_left.setValue(self.offset.x())
        self.ui_left.valueChanged.connect(self._value_changed)

        self.ui_layout = QtWidgets.QVBoxLayout()

        self.ui_controls_layout = QtWidgets.QGridLayout()
        self.ui_controls_layout.setSpacing(8)
        self.ui_controls_layout.setContentsMargins(12, 12, 12, 0)
        self.ui_controls_layout.addWidget(QtWidgets.QLabel('Top'), 0, 0)
        self.ui_controls_layout.addWidget(self.ui_top, 1, 0)
        self.ui_controls_layout.addWidget(QtWidgets.QLabel('Left'), 0, 1)
        self.ui_controls_layout.addWidget(self.ui_left, 1, 1)

        self.ui_button_layout = QtWidgets.QVBoxLayout()
        self.ui_button_layout.setSpacing(8)
        self.ui_button_layout.setContentsMargins(12, 12, 12, 12)
        self.ui_button_layout.addWidget(self.ui_color_button)

        top = QtWidgets.QWidget()
        top.setLayout(self.ui_controls_layout)

        line = QtWidgets.QWidget()
        line.setObjectName("line-divider")

        self.ui_layout.addWidget(top)
        self.ui_layout.addWidget(line)

        bottom = QtWidgets.QWidget()
        bottom.setLayout(self.ui_button_layout)

        self.ui_layout.addWidget(bottom)

        self.setLayout(self.ui_layout)

        self.setWindowTitle('Shadow')
        self.setGeometry(100, 300, 240, 140)

    def _color_action(self):
        """Value of color picker changed"""

        self.color = QtWidgets.QColorDialog.getColor(self.color)
        self.updated.emit(self.offset, self.blur, self.color)

    def _value_changed(self, i):
        """Value of UI components changed"""

        self.offset = QtCore.QPoint(self.ui_left.value(), self.ui_top.value())
        self.updated.emit(self.offset, self.blur, self.color)


class CompositionPopup(QPopup):
    """Composition preferences popup"""

    updated = QtSignal("QSize")

    def __init__(self, size, parent=None):
        super(CompositionPopup, self).__init__(parent)

        self.composition = size
        self._ignore_update = False

        self.__ui__()
        self.update()

    def __ui__(self):

        self.ui_width = QtWidgets.QSpinBox()
        self.ui_width.setRange(self.composition.width(), 32000)
        self.ui_width.valueChanged.connect(self._value_changed)

        self.ui_height = QtWidgets.QSpinBox()
        self.ui_height.setRange(self.composition.height(), 32000)
        self.ui_height.valueChanged.connect(self._value_changed)

        self.ui_preset = QtWidgets.QComboBox()
        self.ui_preset.currentIndexChanged.connect(self._preset_changed)

        self._update_list()
        self.ui_preset.setItemText(0, "Current (%dx%d)" % (self.composition.width(), self.composition.height()))

        self.ui_layout = QtWidgets.QGridLayout()
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

        for screen in QtGui.QGuiApplication.screens():
            width = screen.size().width()
            height = screen.size().height()
            mode = (screen.name() + " (%dx%d)" % (width, height), QtCore.QSize(width, height))

            presets.append(mode)

        presets.extend([
            ("Full HD (1920x1080)", QtCore.QSize(1920, 1080)),
            ("HD (1280x720)", QtCore.QSize(1366, 768)),
            ("XGA (1024x768)", QtCore.QSize(1024, 768)),
            ("WXGA (1280x800)", QtCore.QSize(1280, 800)),
            ("SXGA (1280x1024)", QtCore.QSize(1280, 1024)),
            ("UXGA (1600x1200)", QtCore.QSize(1600, 1200)),
            ("SVGA (800x600)", QtCore.QSize(800, 600))])

        self.ui_preset.clear()

        for preset in presets:
            self.ui_preset.addItem(preset[0], preset[1])

        self.ui_preset.insertSeparator(1)

    def _value_changed(self, i):
        """Value of spinner is changed"""

        if self._ignore_update:
            return False

        self.set_composition(QtCore.QSize(self.ui_width.value(), self.ui_height.value()))

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

    updated = QtSignal(str)

    def __init__(self, case=0):
        super(CasePopup, self).__init__(None)

        self.case = case

        self.__ui__()

    def __ui__(self):
        self.ui_case = QtWidgets.QComboBox()
        self.ui_case.activated.connect(self.valueChanged)

        h_index = [0, 1, 2, 3].index(self.case)

        self.ui_case.addItem("Normal", "normal")
        self.ui_case.addItem("Title", "title")
        self.ui_case.addItem("Upper", "upper")
        self.ui_case.addItem("Lower", "lower")
        self.ui_case.addItem("Capitalize", "capitalize")
        self.ui_case.setCurrentIndex(h_index)

        self.ui_layout = QtWidgets.QGridLayout()
        self.ui_layout.setSpacing(8)
        self.ui_layout.setContentsMargins(12, 12, 12, 12)

        self.ui_layout.addWidget(QtWidgets.QLabel('Text Case'), 0, 0)
        self.ui_layout.addWidget(self.ui_case, 1, 0)

        self.setLayout(self.ui_layout)

        self.setWindowTitle('Text Transform')
        self.setGeometry(100, 300, 120, 80)

    def valueChanged(self, i):
        self.case = self.ui_case.currentData()

        self.updated.emit(self.case)

    def setCase(self, case):
        self.case = case


class DisplayPreferencesDialog(QtWidgets.QDialog):
    """Display preferences window"""

    updated = QtSignal()

    def __init__(self, parent):
        """Initialize PreferencesDialog

        Args:
            parent (DisplayPlugin): reference to DisplayPlugin instance
        """
        super(DisplayPreferencesDialog, self).__init__(None)

        self._plugin = parent

        self.padding_popup = PaddingPopup(0, 0, 0, 0)
        self.padding_popup.updated.connect(self.padding_updated)

        self.align_popup = AlignPopup(QtCore.Qt.AlignHCenter, QtCore.Qt.AlignVCenter)
        self.align_popup.updated.connect(self.align_updated)

        self.shadow_popup = ShadowPopup(QtCore.QPoint(0, 0), 0, QtGui.QColor("#000"))
        self.shadow_popup.updated.connect(self.shadow_updated)

        self.composition_popup = CompositionPopup(QtCore.QSize(800, 600))
        self.composition_popup.updated.connect(self.composition_updated)

        self.case_popup = CasePopup(0)
        self.case_popup.updated.connect(self.case_updated)

        desktop = QtWidgets.QApplication.desktop()
        desktop.resized.connect(self._screens_changed)
        desktop.screenCountChanged.connect(self._screens_changed)
        desktop.workAreaResized.connect(self._screens_changed)

        self.__ui__()

        self._plugin.connect_signal('/comp/testcard', self.testcard_cb)

        self._fit_view()
        self._update_output_list()
        self._update_outputs()

    def __ui__(self):
        """Build UI"""

        # Display output
        action = QtWidgets.QAction("Disabled", self)
        self._ui_display_menu = QtWidgets.QMenu(self)
        self._ui_display_menu.addAction(action)

        self._ui_display_dest_action = QtWidgets.QPushButton("Destination", self)
        self._ui_display_dest_action.setCheckable(True)
        self._ui_display_dest_action.setChecked(True)
        self._ui_display_dest_action.clicked.connect(self.dest_action)

        self._ui_display_output_action = QtWidgets.QPushButton("Disabled", self)
        self._ui_display_output_action.setMenu(self._ui_display_menu)

        self._ui_display_transform = TransformWidget()
        self._ui_display_transform.setRect(QtCore.QRect(0, 0, 800, 600))
        self._ui_display_transform.updated.connect(self.transform_updated)

        self._ui_display_toolbar = QtWidgets.QToolBar()
        self._ui_display_toolbar.addWidget(self._ui_display_dest_action)
        self._ui_display_toolbar.addStretch()
        self._ui_display_toolbar.addWidget(self._ui_display_output_action)

        self._ui_display_layout = QtWidgets.QVBoxLayout()
        self._ui_display_layout.addWidget(self._ui_display_transform)
        self._ui_display_layout.addWidget(self._ui_display_toolbar)

        self._ui_display = QtWidgets.QWidget(None)
        self._ui_display.setLayout(self._ui_display_layout)

        # Composition
        self._ui_view = DisplaySceneView()
        self._ui_view.setScene(self._plugin.scene)
        self._ui_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self._ui_font_action = QtWidgets.QToolButton(self)
        self._ui_font_action.setIcon(QtGui.QIcon(':/rc/font.png'))
        self._ui_font_action.clicked.connect(self.font_action)

        self._ui_shadow_action = QtWidgets.QToolButton(self)
        self._ui_shadow_action.setIcon(QtGui.QIcon(':/rc/shadow.png'))
        self._ui_shadow_action.clicked.connect(self.shadow_action)

        self._ui_align_action = QtWidgets.QToolButton(self)
        self._ui_align_action.setIcon(QtGui.QIcon(':/rc/align.png'))
        self._ui_align_action.clicked.connect(self.align_action)

        self._ui_case_action = QtWidgets.QToolButton(self)
        self._ui_case_action.setIcon(QtGui.QIcon(':/rc/case.png'))
        self._ui_case_action.clicked.connect(self.case_action)

        self._ui_color_action = QtWidgets.QToolButton(self)
        self._ui_color_action.setIcon(QtGui.QIcon(':/rc/color.png'))
        self._ui_color_action.clicked.connect(self.color_action)

        self._ui_composition_action = QtWidgets.QToolButton(self)
        self._ui_composition_action.setIcon(QtGui.QIcon(':/rc/zone-select.png'))
        self._ui_composition_action.clicked.connect(self.composition_action)

        self._ui_padding_action = QtWidgets.QToolButton(self)
        self._ui_padding_action.setIcon(QtGui.QIcon(':/rc/selection-select.png'))
        self._ui_padding_action.clicked.connect(self.padding_action)

        self._ui_testcard_action = QtWidgets.QToolButton(self)
        self._ui_testcard_action.setIcon(QtGui.QIcon(':/rc/testcard.png'))
        self._ui_testcard_action.setCheckable(True)
        self._ui_testcard_action.setChecked(True)
        self._ui_testcard_action.clicked.connect(self.testcard_action)

        self._ui_toolbar = QtWidgets.QToolBar()
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
        self._ui_comp_layout = QtWidgets.QVBoxLayout()
        self._ui_comp_layout.addWidget(self._ui_view)
        self._ui_comp_layout.addWidget(self._ui_toolbar)

        self._ui_comp = QtWidgets.QWidget()
        self._ui_comp.setLayout(self._ui_comp_layout)

        self._ui_stack = QtWidgets.QStackedWidget()
        self._ui_stack.addWidget(self._ui_comp)
        self._ui_stack.addWidget(self._ui_display)
        self._ui_stack.setCurrentIndex(0)

        # Outputs
        self._ui_list = QtWidgets.QListWidget()
        self._ui_list.itemClicked.connect(self.item_clicked)
        self._ui_list.itemChanged.connect(self._item_changed)

        self._ui_add_action = QtWidgets.QToolButton(self)
        self._ui_add_action.setIcon(QtGui.QIcon(':/rc/add.png'))
        self._ui_add_action.clicked.connect(self.add_action)

        self._ui_remove_action = QtWidgets.QToolButton(self)
        self._ui_remove_action.setIcon(QtGui.QIcon(':/rc/remove.png'))
        self._ui_remove_action.clicked.connect(self.remove_action)

        self._ui_list_toolbar = QtWidgets.QToolBar()
        self._ui_list_toolbar.addWidget(self._ui_add_action)
        self._ui_list_toolbar.addStretch()
        self._ui_list_toolbar.addWidget(self._ui_remove_action)

        self._ui_outputs_layout = QtWidgets.QVBoxLayout()
        self._ui_outputs_layout.addWidget(self._ui_list)
        self._ui_outputs_layout.addWidget(self._ui_list_toolbar)

        self._ui_outputs = QtWidgets.QWidget()
        self._ui_outputs.setMinimumWidth(120)
        self._ui_outputs.setMaximumWidth(240)
        self._ui_outputs.setLayout(self._ui_outputs_layout)

        # Global
        self._ui_splitter = QtWidgets.QSplitter()
        self._ui_splitter.addWidget(self._ui_outputs)
        self._ui_splitter.addWidget(self._ui_stack)
        self._ui_splitter.setCollapsible(0, False)
        self._ui_splitter.setCollapsible(1, False)
        self._ui_splitter.setHandleWidth(1)
        self._ui_splitter.setStretchFactor(0, 0)
        self._ui_splitter.setStretchFactor(1, 1)
        self._ui_splitter.setSizes([200, 600])

        self._ui_layout = QtWidgets.QVBoxLayout()
        self._ui_layout.addWidget(self._ui_splitter)

        # Set default view
        self._ui_list.addItem(QtWidgets.QListWidgetItem("Composition"))
        self._select_item(0)

        self.setLayout(self._ui_layout)
        self.setWindowTitle("Display Preferences")
        self.setGeometry(100, 100, 800, 360)
        self.setMinimumSize(800, 400)
        self.moveCenter()

    def resizeEvent(self, event):

        super(DisplayPreferencesDialog, self).resizeEvent(event)

        self._fit_view()

    def _fit_view(self):

        if self._ui_stack.currentIndex() != 0:
            return

        scene = self._plugin.scene
        factor = min(self._ui_view.width() / scene.width(), self._ui_view.height() / scene.height()) * 0.9

        self._ui_view.setScale(factor)

    def _update_outputs(self):

        modes = [OutputConfiguration("Disabled", 0, 0, 800, 600, disabled=True), None]

        for screen in QtGui.QGuiApplication.screens():
            rect = screen.geometry()
            name = screen.name()

            # Fix name on Windows
            if name.startswith("\\\\.\\"):
                name = name[4:]

            modes.append(OutputConfiguration(
                "%s (%dx%d)" % (name, screen.size().width(), screen.size().height()),
                rect.x(), rect.y(), rect.width(), rect.height(),
                frameless=True))

        modes.append(None)

        display = QtWidgets.QDesktopWidget().geometry()

        for (w, h) in [(1280, 720), (800, 600), (480, 320)]:
            modes.append(OutputConfiguration("Windowed (%dx%d)" % (w, h),
                                             (display.x() + display.width()) / 2 - w / 2,
                                             (display.y() + display.height()) / 2 - h / 2,
                                             w, h,
                                             frameless=False))

        self._ui_display_menu.clear()

        modes.reverse()

        def triggered(menu_action):
            return lambda item=menu_action: self._update_output_window(menu_action)

        for mode in modes:
            if mode is None:
                self._ui_display_menu.addSeparator()
                continue

            action = QtWidgets.QAction(mode.name, self)
            action.setProperty('mode', mode)
            action.triggered.connect(triggered(action))

            self._ui_display_menu.addAction(action)

    def _screens_changed(self):

        self._update_outputs()

    def _update_output_window(self, action):

        index = self._ui_list.currentRow()

        if index <= 0:
            return

        output = self._ui_list.item(index).output
        mode = action.property('mode')

        self._ui_display_output_action.setText(mode.name)

        if mode.disabled:
            output.close()

            return

        output.setFrameless(mode.frameless)
        output.setGeometry(mode.x, mode.y, mode.width, mode.height)
        output.show()

        self._ui_display_transform.setRect(QtCore.QRectF(0, 0, mode.width, mode.height))

    def emit_signal(self, message, *args, **kwargs):
        """Emit messages to plugin"""

        self._plugin.emit_signal(message, *args)

    def transform_updated(self):

        index = self._ui_list.currentRow()
        t = self._ui_display_transform

        if index > 0:
            output = self._ui_list.item(index).output
            output.setTransform(t.transformation())
            output.setTransformationPoints(t.points(True))

    def dest_action(self):

        self._ui_display_dest_action.setChecked(True)

    def add_action(self):
        """Add output action"""

        output = self._plugin.add_output()
        self._update_output_list()

        # select last item
        self._select_item(self._ui_list.count() - 1)

    def remove_action(self):
        """Remove output action"""

        index = self._ui_list.currentRow()

        if index > 0:
            self._ui_list.takeItem(index)

            output = self._plugin.outputs.pop(index - 1)

        # select previous item
        self._select_item(max(0, index - 1))

    def _update_output_list(self):
        """Update list of outputs"""

        self._ui_list.clear()

        # Add composition item
        self._ui_list.addItem(QtWidgets.QListWidgetItem("Composition"))

        # Add outputs items
        index = 1

        for output in self._plugin.outputs:
            item = QtWidgets.QListWidgetItem(f"Output {index}")
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            item.output = output

            self._ui_list.addItem(item)

            index += 1

        self._select_item(0)

    def _select_item(self, index: int):

        self._ui_list.setCurrentRow(index)
        self._ui_stack.setCurrentIndex(0 if index == 0 else 1)

        # restore output settings
        if index > 0:
            output = self._ui_list.item(index).output  # DisplayWindow
            points = output.points()

            self._ui_display_transform.setRect(output.rect())

            if points:
                self._ui_display_transform.setPoints(*points)

    def item_clicked(self, item=None):
        """Output list item clicked"""

        index = self._ui_list.currentRow()

        self._select_item(index)

    def _item_changed(self, item=None):
        """Output name changed"""

        if item:
            item.output.setName(item.text())

    def padding_updated(self, left_padding, top_padding, right_padding, bottom_padding):
        """Text padding updated"""

        self.emit_signal('/clip/text/padding', left_padding, top_padding, right_padding, bottom_padding)

    def shadow_updated(self, offset, blur, color):
        """Shadow properties changed"""

        self.emit_signal('/clip/text/shadow', offset.x(), offset.y(), blur, color.name())

    def align_updated(self, horizontal, vertical):
        """Align changed"""

        self.emit_signal('/clip/text/align', horizontal, vertical)

    def case_updated(self, index):
        """Text case changed"""

        self.emit_signal('/clip/text/transform', index)

    def composition_updated(self, size):
        """Composition size updated"""

        self._plugin.emit_signal('/comp/size', size.width(), size.height())
        self._fit_view()

    def font_action(self):
        """Font action clicked"""

        font, accept = QtWidgets.QFontDialog.getFont()

        if accept:
            # <size_pt:float> <family:str> <style:str>
            self.emit_signal('/clip/text/font', font.pointSize(), str(font.family()), str(font.styleName()))

        self.showWindow()

    def padding_action(self):
        """Padding action clicked"""

        self.padding_popup.showAt(self._map_action_position(self._ui_padding_action))

    def testcard_action(self):
        """Testcard action clicked"""

        self.emit_signal('/comp/testcard', not self._ui_testcard_action.isChecked())

    def testcard_cb(self, flag=False):
        """Receive test card update"""

        self._ui_testcard_action.setChecked(not flag)

    def shadow_action(self):
        """Handle text shadow action click"""

        self.shadow_popup.showAt(self._map_action_position(self._ui_shadow_action))

    def color_action(self):
        """Handle color action click"""

        color = QtWidgets.QColorDialog.getColor()

        if color:
            self.emit_signal('/clip/text/color', color.name())

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
