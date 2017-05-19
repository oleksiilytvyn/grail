# -*- coding: UTF-8 -*-
"""
    grail.ui.view_arranger
    ~~~~~~~~~~~~~~~~~~~~~~

    Arrange views in any order you want

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import sip

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.qt import Component, HLayout, Button, Splitter
from grail.core import Viewer
from grail.plugins import EmptyViewer


class ViewArranger(Component):

    def __init__(self, parent=None):
        super(ViewArranger, self).__init__(parent)

        self._viewers = []
        self._layout = HLayout()
        self.setLayout(self._layout)

        # create test widgets
        widget = self.build(['h', 'library', 'cuelist', ['v', 'node', 'property'], 'empty'])
        self._layout.addWidget(widget)

    def build(self, data):

        views = data[1:]
        splitter = Splitter(Qt.Horizontal if data[0] == 'h' else Qt.Vertical)

        for view in views:
            if isinstance(view, str):
                splitter.addWidget(self._create(view, splitter))
            elif isinstance(view, list):
                splitter.addWidget(self.build(view))

        return splitter

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

    def _destroy(self, viewer):
        """Destroy viewer and remove from list"""

        # remove current viewer
        viewer.setParent(None)
        viewer.deleteLater()

        if viewer in self._viewers:
            self._viewers.remove(viewer)

    def _create(self, name, parent):
        """Returns viewer by id or empty viewer"""

        viewer = EmptyViewer

        for plug in Viewer.plugins():
            if plug.id == name:
                viewer = plug

        ref = viewer(parent)
        self._viewers.append(ref)

        return ref
