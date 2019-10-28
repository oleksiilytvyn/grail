# -*- coding: UTF-8 -*-
"""
    grail.plugins.display.display_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Display output composition Viewer

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
from grail.qt import *
from grail.qt import colors as qt_colors

from grail.core import Viewer

from .display_plugin import DisplayPlugin


class DisplayViewer(Viewer):
    """View composition output as viewer"""

    id = "display-viewer"
    name = "Display Output"
    author = "Grail Team"
    description = "View composition output"
    single_instance = True

    def __init__(self, *args, **kwargs):
        super(DisplayViewer, self).__init__(*args, **kwargs)

        self.connect("!display/instance", self._display_instance)
        self.connect('/comp/size', self._comp_size_cb)

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

    def _comp_size_cb(self, width=1, height=1):
        """Composition scene size changed"""

        # Wait composition to refresh and then fit
        QTimer.singleShot(50, lambda: self._fit_clicked())