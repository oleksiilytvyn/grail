# -*- coding: UTF-8 -*-
"""
    grail.ui.view_arranger
    ~~~~~~~~~~~~~~~~~~~~~~

    Arrange viewers in any order you want

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import json

from PyQt5.QtCore import *

from grailkit.core import Signal
from grail.qt import Component, HLayout, Splitter

from grail.core import Viewer
from grail.plugins import EmptyViewer


class ViewArranger(Component):

    def __init__(self, parent=None):
        super(ViewArranger, self).__init__(parent)

        self._viewers = []
        self._layout = HLayout()
        self._root = None
        self._timer = QTimer()
        self._timer.timeout.connect(self._timeout)
        self._timer.setInterval(1000)

        self.updated = Signal()

        self.setLayout(self._layout)

    def _build(self, structure):
        """Create widgets and splitter corresponding to given structure"""

        views = structure[1:]
        layout = structure[0]
        horizontal = layout['layout/orientation'] == 'horizontal'
        splitter = Splitter(Qt.Horizontal if horizontal else Qt.Vertical)
        splitter.splitterMoved.connect(self._splitter_moved)
        sizes = []

        for view in views:
            if not view:
                continue

            if isinstance(view, dict):
                viewer = self._create(view['view/id'], splitter, view)

                splitter.addWidget(viewer)
                sizes.append(view['width'] if horizontal else view['height'])
            elif isinstance(view, list):
                splitter.addWidget(self._build(view))
                sizes.append(view[0]['width'] if horizontal else view[0]['height'])

        splitter.setSizes(sizes)

        return splitter

    def compose(self, structure):
        """Build layouts and load viewers corresponding to given structure

        Args:
            structure: list that represents layout
        """
        self._root = self._build(structure)
        self._layout.addWidget(self._root)

    def decompose(self, _root=None):
        """Return structure containing information about views & layouts"""

        splitter = _root if _root else self._root
        structure = []
        vertical = splitter.orientation() == Qt.Vertical

        if not splitter:
            return []

        structure.append({
            'layout/type': 'layout',
            'layout/orientation': "vertical" if vertical else "horizontal",
            'x': 0,
            'y': 0,
            'width': splitter.width(),
            'height': splitter.height(),
            })

        sizes = splitter.sizes()

        for index in range(len(sizes)):
            widget = splitter.widget(index)

            if isinstance(widget, Splitter):

                structure.append(self.decompose(widget))

            elif isinstance(widget, Viewer):

                viewer = widget.properties()
                viewer['view/id'] = widget.id
                viewer['x'] = 0
                viewer['y'] = 0
                viewer['width'] = sizes[index] if not vertical else splitter.width()
                viewer['height'] = sizes[index] if vertical else splitter.height()

                structure.append(viewer)

        return structure

    def replace(self, viewer, other):
        """Replace one viewer with another

        Args:
            viewer (grail.core.Viewer): viewer to replace
            other (string): new viewer
        """

        splitter = viewer.parentWidget()
        index = splitter.indexOf(viewer)
        sizes = splitter.sizes()

        self._destroy(viewer)

        splitter.insertWidget(index, self._create(other, splitter))
        splitter.setSizes(sizes)

        self._update()

    def remove(self, viewer):
        """Remove viewer from arranger

        Args:
            viewer (grail.core.Viewer): viewer to be removed
        """

        splitter = viewer.parentWidget()

        # Removing last viewer in root splitter
        if splitter.parentWidget().__class__.__name__ == 'ViewArranger' and splitter.count() == 1:
            # add empty viewer
            splitter.addWidget(self._create('empty', splitter))

        # Removing one of two viewers in splitter
        elif splitter.count() == 2:
            other = splitter.widget(1 if splitter.widget(0) == viewer else 0)
            parent = splitter.parentWidget()

            # don't replace splitter if this is root one
            if parent.__class__.__name__ != 'ViewArranger':
                index = parent.indexOf(splitter)
                parent.insertWidget(index, other)

                splitter.setParent(None)
                splitter.deleteLater()

        self._destroy(viewer)
        self._update()

    def split(self, viewer, direction=None):
        """Add new viewer to splitter

        Args:
            viewer (grail.core.Viewer): viewer to split
            direction: split orientation
        """

        splitter = viewer.parentWidget()
        index = splitter.indexOf(viewer)
        view = self._create('empty', splitter)
        orientation = Qt.Horizontal if direction == 'h' else Qt.Vertical

        if splitter.orientation() == orientation:
            splitter.addWidget(view)
        else:
            viewer.setParent(None)

            sub = Splitter(orientation)
            sub.addWidget(viewer)
            sub.addWidget(view)

            splitter.insertWidget(index, sub)

        self._update()

    def _destroy(self, viewer):
        """Destroy viewer and remove from list"""

        viewer.setParent(None)
        viewer.deleteLater()

        if viewer in self._viewers:
            self._viewers.remove(viewer)

    def _create(self, name, parent, properties=None):
        """Returns viewer by id or empty viewer"""

        viewer = EmptyViewer

        for plug in Viewer.plugins():
            if plug.id == name:
                viewer = plug
                break

        ref = viewer(parent, properties)
        self._viewers.append(ref)

        return ref

    def _update(self):
        """Called when layout changed or view replaced, also on splitter resize"""

        self.updated.emit()

    def _splitter_moved(self, position, index):
        """Catch splitter moved event"""

        self._timer.stop()
        self._timer.start()

    def _timeout(self):
        """This timeout makes delay to prevent from frequent update of layout"""

        self._timer.stop()
        self._update()
