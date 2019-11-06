# -*- coding: UTF-8 -*-
"""
    grail.qt.custom
    ~~~~~~~~~~~~~~~

    Replacement for some of Qt components as they not work as desired,
    plus some methods or new components in PyQt code style

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
from grail.qt import colors as qt_colors
from grailkit.util import OS_MAC, OS_LINUX

from PyQt5 import QtCore, QtNetwork, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets

QtSignal = QtCore.pyqtSignal
QtSlot = QtCore.pyqtSlot

# from PySide2 import QtCore, QtNetwork, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets

# QtSignal = QtCore.Signal
# QtSlot = QtCore.Slot


# References to original classes
QT_QTREEWIDGET = QtWidgets.QTreeWidget
QT_QLISTWIDGET = QtWidgets.QListWidget
QT_QTABLEWIDGET = QtWidgets.QTableWidget
QT_QTEXTEDIT = QtWidgets.QTextEdit
QT_QLINEEDIT = QtWidgets.QLineEdit


# noinspection PyPep8Naming,PyPep8Naming
class Icon(QtGui.QIcon):
    """Pixmap/vector icon"""

    def __init__(self, path=None):
        super(Icon, self).__init__(path)

    def coloredPixmap(self, width, height, color, original_color=QtGui.QColor('black')):
        """Create a pixmap from original icon, changing `original_color` color to given color

        Args:
            width (int): width of pixmap
            height (int): height of pixmap
            color (QColor): color of icon
            original_color (QColor): new color
        Returns:
            QPixmap of icon
        """

        pixmap = self.pixmap(width, height)
        mask = pixmap.createMaskFromColor(original_color, QtCore.Qt.MaskOutColor)
        pixmap.fill(color)
        pixmap.setMask(mask)

        return pixmap

    def addColoredPixmap(self, width=128, height=128, color=QtGui.QColor("#000"), mode=QtGui.QIcon.Normal,
                         state=QtGui.QIcon.On):
        """Add a pixmap with given color

        Args:
            width (int): width of added pixmap
            height (int): height of added pixmap
            color (QColor): color of icon
            mode: QIcon mode
            state: QIcon state
        """

        self.addPixmap(self.coloredPixmap(width, height, color), mode, state)

    @staticmethod
    def colored(path, color, original_color=QtGui.QColor('black')):
        """Colorize icon and return new instance

        Args:
            path (str): image location
            color (QColor): new color
            original_color (QColor): original color that will be used as mask to fill new color
        """

        icon = Icon(path)
        size = icon.availableSizes()[0] if len(icon.availableSizes()) > 0 else QtCore.QSize(16, 16)

        return Icon(icon.coloredPixmap(size.width(), size.height(), color, original_color))


# noinspection PyPep8Naming
class _QWidget(QtWidgets.QWidget):
    """Base widget"""

    def className(self):
        """
        Returns widget name that used in stylesheet.

        stylesheet example:
            Dialog {
                background: red;
            }
        """

        return type(self).__name__


class QSpacer(_QWidget):
    """Widget that simply allocate space and spread widgets"""

    def __init__(self, policy_horizontal=QtWidgets.QSizePolicy.Expanding,
                 policy_vertical=QtWidgets.QSizePolicy.Expanding, parent=None):
        """Create spacer component that allocates space and stretches another components in layout

        Args:
            policy_horizontal (QSizePolicy.Policy): horizontal space allocation rule
            policy_vertical (QSizePolicy.Policy): vertical space allocation rule
            parent (object): parent qt widget
        """
        super(QSpacer, self).__init__(parent)

        self.setSizePolicy(policy_horizontal, policy_vertical)


class _QListWidget(QtWidgets.QListWidget, _QWidget):
    """Simple list widget"""

    def __init__(self, parent=None):
        super(_QListWidget, self).__init__(parent)

        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # Fix items overlapping issue
        self.setStyleSheet("QListWidget::item {padding: 4px 12px;}")

        self._scrollbar_original = self.verticalScrollBar()
        self._scrollbar = QtWidgets.QScrollBar(QtCore.Qt.Vertical, self)
        self._scrollbar.valueChanged.connect(self._scrollbar_original.setValue)
        self._scrollbar_original.valueChanged.connect(self._scrollbar.setValue)

        self._update_scrollbar()

    def _update_scrollbar(self):
        """Update a custom scrollbar"""

        original = self._scrollbar_original

        if original.value() == original.maximum() and original.value() == 0:
            self._scrollbar.hide()
        else:
            self._scrollbar.show()

        self._scrollbar.setPageStep(original.pageStep())
        self._scrollbar.setRange(original.minimum(), original.maximum())
        self._scrollbar.resize(8, self.rect().height())
        self._scrollbar.move(self.rect().width() - 8, 0)

    def paintEvent(self, event):
        """Redraw a widget"""

        QT_QLISTWIDGET.paintEvent(self, event)

        self._update_scrollbar()


# noinspection PyPep8Naming
class _QListWidgetItem(QtWidgets.QListWidgetItem):
    """List item"""

    def __init__(self, parent=None):
        super(_QListWidgetItem, self).__init__(parent)

        self._data = None

    def setObject(self, data):
        """Set associated data object

        Args:
            data (object): any object
        """

        self._data = data

    def object(self):
        """Returns associated data object"""

        return self._data


# noinspection PyPep8Naming
class _QToolBar(QtWidgets.QToolBar, _QWidget):
    def __init__(self, parent=None):
        super(_QToolBar, self).__init__(parent)

        self.setFixedHeight(30)
        self.setIconSize(QtCore.QSize(16, 16))

    def addStretch(self, size=0):
        """Add space stretch"""

        if size > 0:
            spacer = QSpacer(QtWidgets.QSizePolicy.Minimum)
            spacer.setMinimumWidth(size)
            self.addWidget(spacer)
        else:
            self.addWidget(QSpacer())

    def paintEvent(self, event):
        """Paint component with CSS styles"""

        option = QtWidgets.QStyleOption()
        option.initFrom(self)

        painter = QtGui.QPainter(self)

        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, option, painter, self)

    """Toolbar component"""


class _QTreeWidget(QtWidgets.QTreeWidget, _QWidget):
    """Tree widget with predefined properties"""

    def __init__(self, parent=None):
        super(_QTreeWidget, self).__init__(parent)

        self.setAlternatingRowColors(True)
        self.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
        self.header().close()
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setWordWrap(True)
        self.setAnimated(False)
        self.setSortingEnabled(False)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self._scrollbar_original = self.verticalScrollBar()
        self._scrollbar = QtWidgets.QScrollBar(QtCore.Qt.Vertical, self)
        self._scrollbar.valueChanged.connect(self._scrollbar_original.setValue)
        self._scrollbar_original.valueChanged.connect(self._scrollbar.setValue)

        self._update_scrollbar()

    def _update_scrollbar(self):
        """Update a custom scrollbar"""

        original = self._scrollbar_original

        if original.value() == original.maximum() and original.value() == 0:
            self._scrollbar.hide()
        else:
            self._scrollbar.show()

        self._scrollbar.setPageStep(original.pageStep())
        self._scrollbar.setRange(original.minimum(), original.maximum())
        self._scrollbar.resize(8, self.rect().height())
        self._scrollbar.move(self.rect().width() - 8, 0)

    def paintEvent(self, event):
        """Redraw a widget"""

        QT_QTREEWIDGET.paintEvent(self, event)

        self._update_scrollbar()


# noinspection PyPep8Naming
class _QTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    """Representation of node as QTreeWidgetItem"""

    def __init__(self, data=None):
        super(_QTreeWidgetItem, self).__init__()

        self._data = data

    def object(self):
        """Returns associated object"""

        return self._data

    def setObject(self, data):
        """Set associated object"""

        self._data = data


class _QTableWidget(QtWidgets.QTableWidget):
    """Table widget"""

    def __init__(self, parent=None):
        super(_QTableWidget, self).__init__(parent)

        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self._scrollbar_original = self.verticalScrollBar()
        self._scrollbar = QtWidgets.QScrollBar(QtCore.Qt.Vertical, self)
        self._scrollbar.valueChanged.connect(self._scrollbar_original.setValue)
        self._scrollbar_original.valueChanged.connect(self._scrollbar.setValue)

        self._update_scrollbar()

    def _update_scrollbar(self):
        """Update a custom scrollbar"""

        original = self._scrollbar_original

        if original.value() == original.maximum() and original.value() == 0:
            self._scrollbar.hide()
        else:
            self._scrollbar.show()

        self._scrollbar.setPageStep(original.pageStep())
        self._scrollbar.setRange(original.minimum(), original.maximum())
        self._scrollbar.resize(8, self.rect().height())
        self._scrollbar.move(self.rect().width() - 8, 0)

    def paintEvent(self, event):
        """Redraw a widget"""

        QT_QTABLEWIDGET.paintEvent(self, event)

        self._update_scrollbar()


class _QHBoxLayout(QtWidgets.QHBoxLayout):
    """Horizontal layout"""

    def __init__(self, parent=None):
        super(_QHBoxLayout, self).__init__(parent)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)


class _QVBoxLayout(QtWidgets.QVBoxLayout):
    """Vertical layout"""

    def __init__(self, parent=None):
        super(_QVBoxLayout, self).__init__(parent)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)


class _QSplitter(QtWidgets.QSplitter, _QWidget):
    """Splitter component"""

    def __init__(self, *args):
        super(_QSplitter, self).__init__(*args)

        self.setHandleWidth(1)


class _QLineEdit(QT_QLINEEDIT, _QWidget):
    """Line edit widget"""

    def __init__(self, *args, **kwargs):
        super(_QLineEdit, self).__init__(*args, **kwargs)

        # fix: placeholder text color doesn't match theme color
        palette = self.palette()
        palette.setColor(QtGui.QPalette.PlaceholderText, QtGui.QColor(qt_colors.BASE_TEXT_ALT))

        self.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
        self.setPalette(palette)


class QSearchEdit(_QLineEdit):
    """Basic edit input for search with clear button"""

    keyPressed = QtSignal('QKeyEvent')
    focusOut = QtSignal('QFocusEvent')

    def __init__(self, parent=None):
        super(QSearchEdit, self).__init__(parent)

        self._placeholder = "Search"

        self.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
        self.textChanged.connect(self._text_changed)

        self._ui_clear = QtWidgets.QToolButton(self)
        self._ui_clear.setIconSize(QtCore.QSize(14, 14))
        self._ui_clear.setIcon(QtGui.QIcon(':/rc/search-clear.png'))
        self._ui_clear.setCursor(QtCore.Qt.ArrowCursor)
        self._ui_clear.hide()
        self._ui_clear.clicked.connect(self.clear)

        frame_width = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)

        size_hint = self.minimumSizeHint()
        btn_size_hint = self._ui_clear.sizeHint()

        self.setMinimumSize(
            max(size_hint.width(), btn_size_hint.height() + frame_width * 2 + 2),
            max(size_hint.height(), btn_size_hint.height() + frame_width * 2 + 2))

        self._adjust_button()

    def className(self):
        """Returns widget name that used in stylesheet."""

        return "QSearchEdit"

    def resizeEvent(self, event):
        """Redraw some elements"""

        self._adjust_button()

    def keyPressEvent(self, event):
        """Implements keyPressed signal"""

        super(QSearchEdit, self).keyPressEvent(event)

        self.keyPressed.emit(event)

    def focusOutEvent(self, event):
        """Focus is lost"""

        super(QSearchEdit, self).focusOutEvent(event)

        self.focusOut.emit(event)

    def _text_changed(self, text):
        """Process text changed event"""

        self._ui_clear.setVisible(len(text) > 0)
        self._adjust_button()

    def _adjust_button(self):

        size = self.rect()
        btn_size = self._ui_clear.sizeHint()
        frame_width = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)

        self._ui_clear.move(size.width() - btn_size.width() - (frame_width * 2),
                            (size.height() / 2) - (btn_size.height() / 2))


class _QTextEdit(QtWidgets.QTextEdit, _QWidget):
    """Multi-line text editor"""

    def __init__(self, *args):
        super(_QTextEdit, self).__init__(*args)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # Replace default scrollbar, as it causes many stylesheet issues
        self._scrollbar_original = self.verticalScrollBar()
        self._scrollbar = QtWidgets.QScrollBar(QtCore.Qt.Vertical, self)
        self._scrollbar.valueChanged.connect(self._scrollbar_original.setValue)
        self._scrollbar_original.valueChanged.connect(self._scrollbar.setValue)

        self._update_scrollbar()

    def _update_scrollbar(self):
        """Update a custom scrollbar"""

        original = self._scrollbar_original

        if original.value() == original.maximum() and original.value() == 0:
            self._scrollbar.hide()
        else:
            self._scrollbar.show()

        self._scrollbar.setPageStep(original.pageStep())
        self._scrollbar.setRange(original.minimum(), original.maximum())
        self._scrollbar.resize(8, self.rect().height())
        self._scrollbar.move(self.rect().width() - 8, 0)

    def paintEvent(self, event):
        """Redraw a widget"""

        QT_QTEXTEDIT.paintEvent(self, event)

        self._update_scrollbar()


# noinspection PyPep8Naming,PyPep8Naming
class _QDialog(QtWidgets.QDialog, _QWidget):
    """Abstract dialog window"""

    def __init__(self, parent=None):
        super(_QDialog, self).__init__(parent)

        # Set default window icon, used on Windows and some Linux distributions
        self.setWindowIcon(QtGui.QIcon(':/icon/32.png'))

    def moveCenter(self):
        """Move window to the center of current screen"""

        geometry = self.frameGeometry()
        geometry.moveCenter(QtWidgets.QDesktopWidget().availableGeometry().center())

        self.move(geometry.topLeft())

    def showWindow(self):
        """Raise dialog in any way"""

        self.show()
        self.raise_()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()


# noinspection PyPep8Naming,PyPep8Naming,PyPep8Naming
class QPopup(_QDialog):
    """Dialog without title bar and frame, but with rounded corners and pointing triangle"""

    def __init__(self, parent=None):
        super(QPopup, self).__init__(parent)

        self.__close_on_focus_lost = True
        self.__background_color = QtGui.QColor(qt_colors.CONTAINER)
        # Shadow padding
        self.__padding = 12
        # Caret size
        self.__caret_size = 5
        # Caret position relative to center of dialog
        self.__caret_position = 0
        # Corner roundness
        self.__roundness = 5

        self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.autoFillBackground = True

        self.installEventFilter(self)

        if not OS_MAC:
            effect = QtWidgets.QGraphicsDropShadowEffect()
            effect.setBlurRadius(12)
            effect.setColor(QtGui.QColor(0, 0, 0, 126))
            effect.setOffset(0)

            self.setGraphicsEffect(effect)

        self.setContentsMargins(self.__padding, self.__padding, self.__padding, self.__padding + self.__caret_size)

    def paintEvent(self, event):
        """Draw a dialog"""

        width = self.width()
        height = self.height()
        caret_offset = self.__caret_position

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Clear previous drawing
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), QtCore.Qt.transparent)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(255, 0, 0, 127))

        points = [QtCore.QPointF(width / 2 + caret_offset, height - self.__padding),
                  QtCore.QPointF(width / 2 - self.__caret_size + caret_offset,
                                 height - self.__caret_size - self.__padding),
                  QtCore.QPointF(width / 2 + self.__caret_size + caret_offset,
                                 height - self.__caret_size - self.__padding)]
        triangle = QtGui.QPolygonF(points)

        rounded_rect = QtGui.QPainterPath()
        rounded_rect.addRoundedRect(self.__padding, self.__padding,
                                    width - self.__padding * 2,
                                    height - self.__caret_size - self.__padding * 2,
                                    self.__roundness, self.__roundness)
        rounded_rect.addPolygon(triangle)

        painter.setOpacity(1)
        painter.fillPath(rounded_rect, QtGui.QBrush(self.__background_color))

        painter.restore()
        painter.end()

    def eventFilter(self, target, event):
        """Close dialog when focus is lost"""

        flag = self.__close_on_focus_lost
        type_ = event.type()

        if flag and type_ == QtCore.QEvent.WindowDeactivate:
            self.hide()

        # Workaround for linux
        if flag and type_ == QtCore.QEvent.Leave and OS_LINUX:
            self.hide()

        return _QDialog.eventFilter(self, target, event)

    def sizeHint(self):
        """Default minimum size"""

        return QtCore.QSize(300, 300)

    def closeOnFocusLost(self, value):
        """Close dialog when it looses focus

        Args:
            value (bool): close this dialog when it looses focus or not
        """

        self.__close_on_focus_lost = value

    def showAt(self, point):
        """Show dialog tip at given point

        Args:
            point (QPoint): point to show at
        """

        self.show()
        self.raise_()

        desktop = QtWidgets.QDesktopWidget()
        screen = desktop.screenGeometry(point)
        location = QtCore.QPoint(point.x() - self.width() / 2, point.y() - self.height() + 12)

        # calculate point location inside current screen
        if location.x() <= screen.x():
            location.setX(screen.x())
            self.__caret_position = -self.width() / 2 + self.__padding + self.__caret_size * 2
        elif location.x() + self.width() >= screen.x() + screen.width():
            location.setX(screen.x() + screen.width() - self.width())
            self.__caret_position = self.width() / 2 - self.__padding - self.__caret_size * 2
        else:
            self.__caret_position = 0

        self.move(location.x(), location.y())

    def setBackgroundColor(self, color):
        """Set a color of whole dialog

        Args:
            color (QColor): background color of widget
        """

        self.__background_color = color


# Replacing default widgets
Application = QtCore.QCoreApplication
QtWidgets.QWidget.className = _QWidget.className

QtWidgets.QHBoxLayout = _QHBoxLayout
QtWidgets.QVBoxLayout = _QVBoxLayout

QtWidgets.QSplitter = _QSplitter
QtWidgets.QLineEdit = _QLineEdit
QtWidgets.QTextEdit = _QTextEdit
QtWidgets.QToolBar = _QToolBar

QtWidgets.QTableWidget = _QTableWidget
QtWidgets.QTreeWidget = _QTreeWidget
QtWidgets.QTreeWidgetItem = _QTreeWidgetItem
QtWidgets.QListWidget = _QListWidget
QtWidgets.QListWidgetItem = _QListWidgetItem
QtWidgets.QDialog = _QDialog

QtDocumentsLocation = QtCore.QStandardPaths.locate(QtCore.QStandardPaths.DocumentsLocation, "",
                                                   QtCore.QStandardPaths.LocateDirectory)


def QtGetSaveFileName(parent=None, title="Save", location=QtDocumentsLocation, ext=""):

    path, _ = QtWidgets.QFileDialog.getSaveFileName(parent, title, location, ext)

    return path


def QtGetOpenFileName(parent=None, title="Save", location=QtDocumentsLocation, ext=""):

    path, _ = QtWidgets.QFileDialog.getOpenFileName(parent, title, location, ext)

    return path
