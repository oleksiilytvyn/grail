# -*- coding: UTF-8 -*-
"""
    grail.plugins.time_plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    View current time

    :copyright: (c) 2016-2020 by Oleksii Lytvyn (http://alexlitvin.name)
    :license: GNU, see LICENSE for more details.
"""
import os
import datetime

from grail.qt import *
from grail.core import Viewer


class TimeViewer(Viewer):
    """View current time"""

    id = 'time'
    name = 'Time'
    author = 'Oleksii Lytvyn'
    description = 'Display current time'

    def __init__(self, *args):
        super(TimeViewer, self).__init__(*args)

        self.__ui__()

        self._background_image = None
        self.style_background = self.get('background', default="#222")
        self.style_color = self.get('color', default="#f1f1f1")
        self.style_size = self.get('size', default=48)
        self.style_font = self.get('font', default='sans-serif')
        self.style_image = self.get('image')

        self._popup = _PropertiesPopup(self)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)

        self._update_time()
        self.update_style()

    def __ui__(self):
        """Build UI"""

        self._label = QtWidgets.QLabel('00:00:00')
        self._label.setObjectName("TimeViewer_label")

        self._ui_view_action = QtWidgets.QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_settings_action = QtWidgets.QToolButton()
        self._ui_settings_action.setText("Settings")
        self._ui_settings_action.clicked.connect(self.settings_action)

        self._ui_toolbar = QtWidgets.QToolBar()
        self._ui_toolbar.setObjectName("TimeViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addStretch()
        self._ui_toolbar.addWidget(self._ui_settings_action)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._ui_toolbar)

        self.setLayout(self._layout)

    def paintEvent(self, event):
        """Draw background image"""

        painter = QtGui.QPainter(self)

        if self._background_image:
            scaled = self._background_image.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatioByExpanding)
            painter.drawPixmap(self.width() / 2 - scaled.width() / 2,
                               self.height() / 2 - scaled.height() / 2,
                               scaled)

        QtWidgets.QWidget.paintEvent(self, event)

    def update_style(self):
        """Update styles"""

        reference_color = QtGui.QColor(self.style_background)

        if self.style_image and os.path.isfile(self.style_image):
            background = 'transparent'
            self._background_image = QtGui.QPixmap(self.style_image)

            img = self._background_image.scaled(3, 3).toImage()
            avg = [0, 0, 0]
            pixels = 9

            for x in range(0, img.width()):
                for y in range(0, img.height()):
                    colors = QtGui.QColor(img.pixel(x, y)).getRgb()
                    avg[0] += colors[0]
                    avg[1] += colors[1]
                    avg[2] += colors[2]

            avg = [round(x/pixels) for x in avg]

            reference_color = QtGui.QColor.fromRgb(*avg)
        else:
            background = self.style_background
            self._background_image = None
            self.style_image = ''

        self.setStyleSheet("TimeViewer {background: %s;}" % self.style_background)

        self._label.setStyleSheet("""
            color: %s;
            background: %s;
            font-size: %dpx;
            font-family: %s;
            """ % (self.style_color,
                   background,
                   self.style_size,
                   self.style_font))

        self._ui_toolbar.setStyleSheet("""
            QToolBar {
                background: %s;
                border-top: none;
                }
            """ % background)

        if reference_color.lightness() > 120:
            color = QtGui.QColor("#222")
            original = QtGui.QColor("#e3e3e3")

            self._ui_view_action.setIcon(Icon.colored(':/rc/menu.png', color, original))
            self._ui_settings_action.setIcon(Icon.colored(':/rc/edit.png', color, original))
        else:
            self._ui_view_action.setIcon(Icon(':/rc/menu.png'))
            self._ui_settings_action.setIcon(Icon(':/rc/edit.png'))

        self.set('background', self.style_background)
        self.set('color', self.style_color)
        self.set('size', self.style_size)
        self.set('font', self.style_font)
        self.set('image', self.style_image)

    def _update_time(self):
        """Update time"""

        _time = datetime.datetime.now()

        self._label.setText("%s:%s:%s" % (str(_time.hour).zfill(2),
                                          str(_time.minute).zfill(2),
                                          str(_time.second).zfill(2)))

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def settings_action(self):
        """Open settings preferences"""

        p = self._ui_toolbar.mapToGlobal(self._ui_settings_action.pos())

        self._popup.showAt(QtCore.QPoint(p.x() + 12, p.y()))


class _Button(QtWidgets.QPushButton):

    def __init__(self, *args):
        super(_Button, self).__init__(*args)

        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.setFixedWidth(90)


class _PropertiesPopup(QPopup):

    def __init__(self, parent=None):
        super(_PropertiesPopup, self).__init__()

        self._viewer = parent
        self._viewer.app.signals.connect('/app/close', self.close)

        self.__ui__()

    def __ui__(self):
        """Build UI"""

        self.setBackgroundColor(QtGui.QColor("#626364"))

        self._ui_layout = QtWidgets.QGridLayout()
        self._ui_layout.setContentsMargins(4, 4, 4, 4)
        self._ui_layout.setSpacing(8)
        self._ui_layout.setColumnStretch(1, 1)

        # size
        self._ui_size = QtWidgets.QSpinBox()
        self._ui_size.setMinimum(12)
        self._ui_size.setMaximum(180)
        self._ui_size.setValue(self._viewer.style_size)
        self._ui_size.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self._ui_size.setMaximumWidth(90)
        self._ui_size.valueChanged.connect(self.size_changed)

        self._ui_size_label = QtWidgets.QLabel("Text size")
        self._ui_layout.addWidget(self._ui_size, 0, 0)
        self._ui_layout.addWidget(self._ui_size_label, 0, 1)

        # color
        self._ui_color = _Button()
        self._ui_color.setStyleSheet("background: %s;" % self._viewer.style_color)
        self._ui_color.clicked.connect(self.color_action)

        self._ui_color_label = QtWidgets.QLabel("Text color")

        self._ui_layout.addWidget(self._ui_color, 1, 0)
        self._ui_layout.addWidget(self._ui_color_label, 1, 1)

        # background
        self._ui_background = _Button()
        self._ui_background.setStyleSheet("background: %s;" % self._viewer.style_background)
        self._ui_background.clicked.connect(self.background_action)

        self._ui_background_label = QtWidgets.QLabel("Background color")

        self._ui_layout.addWidget(self._ui_background, 2, 0)
        self._ui_layout.addWidget(self._ui_background_label, 2, 1)

        # background image
        self._ui_background_image = _Button("Pick")
        self._ui_background_image.clicked.connect(self.background_image_action)

        self._ui_background_image_label = QtWidgets.QLabel("Background image")

        self._ui_layout.addWidget(self._ui_background_image, 3, 0)
        self._ui_layout.addWidget(self._ui_background_image_label, 3, 1)

        # background clear
        self._ui_background_clear = _Button("Clear")
        self._ui_background_clear.clicked.connect(self.background_clear_action)

        self._ui_background_clear_label = QtWidgets.QLabel("Clear background")

        self._ui_layout.addWidget(self._ui_background_clear, 4, 0)
        self._ui_layout.addWidget(self._ui_background_clear_label, 4, 1)

        # font
        self._ui_font = _Button("Choose")
        self._ui_font.clicked.connect(self.font_action)

        self._ui_font_label = QtWidgets.QLabel("Font")

        self._ui_layout.addWidget(self._ui_font, 5, 0)
        self._ui_layout.addWidget(self._ui_font_label, 5, 1)

        self.setLayout(self._ui_layout)
        self.setGeometry(0, 0, 120, 170)

    def color_action(self):
        """Update text color"""

        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self._viewer.style_color), self, "Background color")

        self._ui_color.setStyleSheet("background: %s;" % color.name())
        self._viewer.style_color = color.name()
        self._viewer.update_style()

    def background_action(self):
        """Update background"""

        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self._viewer.style_background), self, "Background color")

        self._ui_background.setStyleSheet("background: %s;" % color.name())
        self._viewer.style_background = color.name()
        self._viewer.update_style()

    def size_changed(self):
        """Update size"""

        self._viewer.style_size = int(self._ui_size.value())
        self._viewer.update_style()

    def background_image_action(self):
        """Update background image"""

        path = QtGetOpenFileName(self, "Open File...", QtDocumentsLocation, "Images (*.png *.jpg *.jpeg)")

        if path:
            self._viewer.style_image = str(path)
            self._viewer.update_style()

    def background_clear_action(self):
        """Clear background image"""

        self._viewer.style_image = None
        self._viewer.update_style()

    def font_action(self):
        """Update font"""

        font, accept = QtWidgets.QFontDialog.getFont(QtGui.QFont(self._viewer.style_font))

        if accept:
            self._viewer.style_font = str(font.family())
            self._viewer.update_style()
