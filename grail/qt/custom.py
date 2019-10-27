# -*- coding: UTF-8 -*-
"""
    grail.qt.custom
    ~~~~~~~~~~~~~~~

    Replacement for some of Qt components as they not work as desired,
    plus some methods or new components in PyQt code style

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.qt import colors as qt_colors
from grailkit.util import OS_MAC, OS_LINUX

# References to original classes
QT_QTREEWIDGET = QTreeWidget
QT_QLISTWIDGET = QListWidget
QT_QTABLEWIDGET = QTableWidget
QT_QTEXTEDIT = QTextEdit
QT_QLINEEDIT = QLineEdit


class Icon(QIcon):
    """Pixmap/vector icon"""

    def __init__(self, path=None):
        super(Icon, self).__init__(path)

    def coloredPixmap(self, width, height, color, original_color=QColor('black')):
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
        mask = pixmap.createMaskFromColor(original_color, Qt.MaskOutColor)
        pixmap.fill(color)
        pixmap.setMask(mask)

        return pixmap

    def addColoredPixmap(self, width=128, height=128, color=QColor("#000"), mode=QIcon.Normal, state=QIcon.On):
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
    def colored(path, color, original_color=QColor('black')):
        """Colorize icon and return new instance

        Args:
            path (str): image location
            color (QColor): new color
            original_color (QColor): original color that will be used as mask to fill new color
        """

        icon = Icon(path)
        size = icon.availableSizes()[0]

        return Icon(icon.coloredPixmap(size.width(), size.height(), color, original_color))


class _QWidget(QWidget):
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

    def __init__(self, policy_horizontal=QSizePolicy.Expanding, policy_vertical=QSizePolicy.Expanding, parent=None):
        """Create spacer component that allocates space and stretches another components in layout

        Args:
            policy_horizontal (QSizePolicy.Policy): horizontal space allocation rule
            policy_vertical (QSizePolicy.Policy): vertical space allocation rule
            parent (object): parent qt widget
        """
        super(QSpacer, self).__init__(parent)

        self.setSizePolicy(policy_horizontal, policy_vertical)


class _QListWidget(QListWidget, _QWidget):
    """Simple list widget"""

    def __init__(self, parent=None):
        super(_QListWidget, self).__init__(parent)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        # Fix items overlapping issue
        self.setStyleSheet("QListWidget::item {padding: 4px 12px;}")

        self._scrollbar_original = self.verticalScrollBar()
        self._scrollbar = QScrollBar(Qt.Vertical, self)
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


class _QListWidgetItem(QListWidgetItem):
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


class _QToolBar(QToolBar, _QWidget):
    def __init__(self, parent=None):
        super(_QToolBar, self).__init__(parent)

        self.setFixedHeight(30)
        self.setIconSize(QSize(16, 16))

    def addStretch(self):
        """Add space stretch"""

        self.addWidget(QSpacer())

    def paintEvent(self, event):
        """Paint component with CSS styles"""

        option = QStyleOption()
        option.initFrom(self)

        painter = QPainter(self)

        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)

    """Toolbar component"""


class _QTreeWidget(QTreeWidget, _QWidget):
    """Tree widget with predefined properties"""

    def __init__(self, parent=None):
        super(_QTreeWidget, self).__init__(parent)

        self.setAlternatingRowColors(True)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.header().close()
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setWordWrap(True)
        self.setAnimated(False)
        self.setSortingEnabled(False)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._scrollbar_original = self.verticalScrollBar()
        self._scrollbar = QScrollBar(Qt.Vertical, self)
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


class _QTreeWidgetItem(QTreeWidgetItem):
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


class _QTableWidget(QTableWidget):
    """Table widget"""

    def __init__(self, parent=None):
        super(_QTableWidget, self).__init__(parent)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._scrollbar_original = self.verticalScrollBar()
        self._scrollbar = QScrollBar(Qt.Vertical, self)
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


class _QHBoxLayout(QHBoxLayout):
    """Horizontal layout"""

    def __init__(self, parent=None):
        super(_QHBoxLayout, self).__init__(parent)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)


class _QVBoxLayout(QVBoxLayout):
    """Vertical layout"""

    def __init__(self, parent=None):
        super(_QVBoxLayout, self).__init__(parent)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)


class _QSplitter(QSplitter, _QWidget):
    """Splitter component"""

    def __init__(self, *args):
        super(_QSplitter, self).__init__(*args)

        self.setHandleWidth(1)


class _QLineEdit(QT_QLINEEDIT, _QWidget):
    """Line edit widget"""

    def __init__(self, *args, **kwargs):
        super(_QLineEdit, self).__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_MacShowFocusRect, False)


class QSearchEdit(QT_QLINEEDIT):
    """Basic edit input for search with clear button"""

    keyPressed = pyqtSignal('QKeyEvent')
    focusOut = pyqtSignal('QFocusEvent')

    def __init__(self, parent=None):
        super(QSearchEdit, self).__init__(parent)

        self._placeholder = "Search"

        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.textChanged.connect(self._text_changed)

        self._ui_clear = QToolButton(self)
        self._ui_clear.setIconSize(QSize(14, 14))
        self._ui_clear.setIcon(QIcon(':/rc/search-clear.png'))
        self._ui_clear.setCursor(Qt.ArrowCursor)
        self._ui_clear.hide()
        self._ui_clear.clicked.connect(self.clear)

        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)

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
        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)

        self._ui_clear.move(size.width() - btn_size.width() - (frame_width * 2),
                            (size.height() / 2) - (btn_size.height() / 2))


class _QTextEdit(QTextEdit, _QWidget):
    """Multi-line text editor"""

    def __init__(self, *args):
        super(_QTextEdit, self).__init__(*args)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Replace default scrollbar, as it causes many stylesheet issues
        self._scrollbar_original = self.verticalScrollBar()
        self._scrollbar = QScrollBar(Qt.Vertical, self)
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


class _QDialog(QDialog, _QWidget):
    """Abstract dialog window"""

    def __init__(self, parent=None):
        super(_QDialog, self).__init__(parent)

        # Set default window icon, used on Windows and some Linux distributions
        self.setWindowIcon(QIcon(':/icon/32.png'))

    def moveCenter(self):
        """Move window to the center of current screen"""

        geometry = self.frameGeometry()
        geometry.moveCenter(QDesktopWidget().availableGeometry().center())

        self.move(geometry.topLeft())

    def showWindow(self):
        """Raise dialog in any way"""

        self.show()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()


class QPopup(_QDialog):
    """Dialog without title bar and frame, but with rounded corners and pointing triangle"""

    def __init__(self, parent=None):
        super(QPopup, self).__init__(parent)

        self.__close_on_focus_lost = True
        self.__background_color = QColor(qt_colors.CONTAINER)
        # Shadow padding
        self.__padding = 12
        # Caret size
        self.__caret_size = 5
        # Caret position relative to center of dialog
        self.__caret_position = 0
        # Corner roundness
        self.__roundness = 5

        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.autoFillBackground = True

        self.installEventFilter(self)

        if not OS_MAC:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(12)
            effect.setColor(QColor(0, 0, 0, 126))
            effect.setOffset(0)

            self.setGraphicsEffect(effect)

        self.setContentsMargins(self.__padding, self.__padding, self.__padding, self.__padding + self.__caret_size)

    def paintEvent(self, event):
        """Draw a dialog"""

        width = self.width()
        height = self.height()
        caret_offset = self.__caret_position

        painter = QPainter()
        painter.begin(self)
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # Clear previous drawing
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 0, 0, 127))

        points = [QPointF(width / 2 + caret_offset, height - self.__padding),
                  QPointF(width / 2 - self.__caret_size + caret_offset, height - self.__caret_size - self.__padding),
                  QPointF(width / 2 + self.__caret_size + caret_offset, height - self.__caret_size - self.__padding)]
        triangle = QPolygonF(points)

        rounded_rect = QPainterPath()
        rounded_rect.addRoundedRect(self.__padding, self.__padding,
                                    width - self.__padding * 2,
                                    height - self.__caret_size - self.__padding * 2,
                                    self.__roundness, self.__roundness)
        rounded_rect.addPolygon(triangle)

        painter.setOpacity(1)
        painter.fillPath(rounded_rect, QBrush(self.__background_color))

        painter.restore()
        painter.end()

    def eventFilter(self, target, event):
        """Close dialog when focus is lost"""

        flag = self.__close_on_focus_lost
        type_ = event.type()

        if flag and type_ == QEvent.WindowDeactivate:
            self.hide()

        # Workaround for linux
        if flag and type_ == QEvent.Leave and OS_LINUX:
            self.hide()

        return _QDialog.eventFilter(self, target, event)

    def sizeHint(self):
        """Default minimum size"""

        return QSize(300, 300)

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

        desktop = QDesktopWidget()
        screen = desktop.screenGeometry(point)
        location = QPoint(point.x() - self.width() / 2, point.y() - self.height() + 12)

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
Application = QCoreApplication
QWidget.className = _QWidget.className

QHBoxLayout = _QHBoxLayout
QVBoxLayout = _QVBoxLayout

QSplitter = _QSplitter
QLineEdit = _QLineEdit
QTextEdit = _QTextEdit
QToolBar = _QToolBar

QTableWidget = _QTableWidget
QTreeWidget = _QTreeWidget
QTreeWidgetItem = _QTreeWidgetItem
QListWidget = _QListWidget
QListWidgetItem = _QListWidgetItem
QDialog = _QDialog
