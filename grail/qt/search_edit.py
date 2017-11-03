# -*- coding: UTF-8 -*-
"""
    grail.qt.search_edit
    ~~~~~~~~~~~~~~~~~~~~

    Line edit with clear button and more signals

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QPainter, QColor, QFont
from PyQt5.QtWidgets import QStyle, QToolButton, QLineEdit, QStyleOption

from grail.qt import LineEdit


class SearchEdit(LineEdit):
    """Basic edit input for search with clear button"""

    keyPressed = pyqtSignal('QKeyEvent')
    focusOut = pyqtSignal('QFocusEvent')

    def __init__(self, parent=None):
        super(SearchEdit, self).__init__(parent)

        self._placeholder = "Search"

        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.textChanged.connect(self._text_changed)

        self._ui_clear = QToolButton(self)
        self._ui_clear.setIconSize(QSize(14, 14))
        self._ui_clear.setIcon(QIcon(':/gk/icon/search-clear.png'))
        self._ui_clear.setCursor(Qt.ArrowCursor)
        self._ui_clear.setStyleSheet("QToolButton {background: none;}")
        self._ui_clear.hide()
        self._ui_clear.clicked.connect(self.clear)

        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)

        self.setStyleSheet("""
                QLineEdit {
                    background-color: #e9e9e9;
                    padding-right: %spx;
                    }
                """ % str(self._ui_clear.sizeHint().width() / 2 + frame_width + 1))

        size_hint = self.minimumSizeHint()
        btn_size_hint = self._ui_clear.sizeHint()

        self.setMinimumSize(
            max(size_hint.width(), btn_size_hint.height() + frame_width * 2 + 2),
            max(size_hint.height(), btn_size_hint.height() + frame_width * 2 + 2))

    def resizeEvent(self, event):
        """Redraw some elements"""

        size = self.rect()
        btn_size = self._ui_clear.sizeHint()
        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)

        self._ui_clear.move(size.width() - btn_size.width() - frame_width * 2,
                            size.height() / 2 - btn_size.height() / 2 + frame_width * 2)

    def keyPressEvent(self, event):
        """Implements keyPressed signal"""

        super(SearchEdit, self).keyPressEvent(event)

        self.keyPressed.emit(event)

    def focusOutEvent(self, event):
        """Focus is lost"""

        super(SearchEdit, self).focusOutEvent(event)

        self.focusOut.emit(event)

    def paintEvent(self, event):

        color = QColor('#777')
        p = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)

        # draw custom placeholder
        if not self.hasFocus() and not self.text() and self._placeholder:
            self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
            font = p.font()
            new_font = QFont().resolve(font)
            new_font.setPointSize(12)
            p.setFont(new_font)

            p.setPen(color)
            fm = self.fontMetrics()
            min_left = max(0, -fm.minLeftBearing())
            ph = self.rect().adjusted(min_left + 3, 0, 0, 0)
            elided_text = fm.elidedText(self._placeholder, Qt.ElideRight, ph.width())
            p.drawText(ph, Qt.AlignCenter, elided_text)

            p.setFont(font)
        else:
            QLineEdit.paintEvent(self, event)

    def setPlaceholderText(self, text):
        self._placeholder = text

    def placeholderText(self):
        return self._placeholder

    def _text_changed(self, text):
        """Process text changed event"""

        self._ui_clear.setVisible(len(text) > 0)
