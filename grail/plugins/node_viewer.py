# -*- coding: UTF-8 -*-
"""
    grail.plugins.node_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    This plugin for developers who want to see whats going on with nodes

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
from collections import defaultdict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QToolButton, QAbstractItemView, QTreeWidget

from grail.qt import Spacer, MessageDialog, Toolbar, Tree, TreeItem, VLayout
from grailkit.dna import DNA

from grail.core import Viewer


class NodeViewer(Viewer):
    """View DNA nodes of currently opened file

    Connected:

    Emits:
        '!node/selected', id:int
    """

    id = 'node'
    name = 'Nodes'
    author = 'Grail Team'
    description = 'View all nodes in grail file'

    def __init__(self, *args):
        super(NodeViewer, self).__init__(*args)

        self.__ui__()

        self._folded = defaultdict(bool)

        self.app.project.entity_changed.connect(self._update)
        self.app.project.entity_removed.connect(self._update)

        self._update()

    def __ui__(self):
        """Setup UI"""

        self.setObjectName("NodeViewer")

        self._ui_tree = _TreeWidget()
        self._ui_tree.setObjectName('playlist_tree')
        self._ui_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_tree.itemSelectionChanged.connect(self._selection_changed)
        self._ui_tree.itemExpanded.connect(self._item_expanded)
        self._ui_tree.itemCollapsed.connect(self._item_collapsed)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add node', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_remove_action = QAction(QIcon(':/icons/remove-white.png'), 'Remove node', self)
        self._ui_remove_action.setIconVisibleInMenu(True)
        self._ui_remove_action.triggered.connect(self.remove_action)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(QIcon(':/icons/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(Spacer())
        self._ui_toolbar.addAction(self._ui_remove_action)
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout = VLayout()
        self._ui_layout.addWidget(self._ui_tree)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def _update(self, *args):
        """Update nodes tree"""

        dna = self.app.project.dna

        self._ui_tree.clear()

        def add_childs(tree_item, parent_id):
            for child in dna.childs(parent_id):
                child_item = TreeItem(child)
                child_item.setText(0, child.name)

                add_childs(child_item, child.id)

                tree_item.addChild(child_item)

        for entity in dna.childs(0):
            item = TreeItem(entity)
            item.setText(0, entity.name)

            add_childs(item, entity.id)

            self._ui_tree.addTopLevelItem(item)

        # expand items
        for item in self._ui_tree.findItems('', Qt.MatchContains | Qt.MatchRecursive):
            item.setExpanded(self._folded[item.object().id])

    def _selection_changed(self, *args):
        """Tree selection changed"""

        current = self._ui_tree.currentItem()

        if current:
            self.emit('!node/selected', current.object().id)

    def _item_expanded(self, item):
        """Tree item expanded"""

        self._folded[item.object().id] = True

    def _item_collapsed(self, item):
        """Tree item collapsed"""

        self._folded[item.object().id] = False

    def view_action(self):
        """Replace current view with something other"""

        menu = self.plugin_menu()
        menu.exec_(self._ui_toolbar.mapToGlobal(self._ui_view_action.pos()))

    def add_action(self):
        """Add new node"""

        item = self._ui_tree.currentItem()
        parent_id = item.object().id if item else 0

        self.app.project.dna.create("Untitled item", parent=parent_id)

    def remove_action(self):
        """Remove selected entity"""

        item = self._ui_tree.currentItem()
        node = item.object()

        if item and node.type in (DNA.TYPE_VIEW, DNA.TYPE_PROJECT, DNA.TYPE_LAYOUT):
            message = MessageDialog(title="Item can't be removed",
                                    text="Item '%s' can't be removed" % node.name,
                                    icon=MessageDialog.Warning)
            message.exec_()

            return False

        self.app.project.dna.remove(node.id)

        # select first node
        self._ui_tree.setCurrentItem(self._ui_tree.itemAt(0, 0))
        item = self._ui_tree.currentItem()

        if item:
            self.emit('!node/selected', item.object().id)


class _TreeWidget(Tree):

    def __init__(self, *args):
        super(_TreeWidget, self).__init__(*args)

    def dropEvent(self, event):

        dropping = self.itemAt(event.pos())
        dragging = self.currentItem()
        dragging_object = dragging.object()
        drop_indicator = self.dropIndicatorPosition()

        # don't allow moving of project and project settings entities
        if (dragging_object.type == DNA.TYPE_PROJECT and dragging_object.parent_id == 0) or \
                (dragging_object.type == DNA.TYPE_SETTINGS and dragging_object.parent_id == 1):
            message = MessageDialog(title="Item can't be moved",
                                    text="Item '%s' can't be moved" % dragging_object.name,
                                    icon=MessageDialog.Warning)
            message.exec_()

            return

        # manage a boolean for the case when you are above an item
        if drop_indicator == QAbstractItemView.AboveItem:
            dragging.object().index = dropping.object().index - 1
        # something when being below an item
        elif drop_indicator == QAbstractItemView.BelowItem:
            dragging.object().index = dropping.object().index + 1
        # you're on an item, maybe add the current one as a child
        elif drop_indicator == QAbstractItemView.OnItem:
            dragging.object().parent_id = dropping.object().id
            # dragging.object().index = dropping.object().id
        # you are not on your tree
        elif drop_indicator == QAbstractItemView.OnViewport:
            pass

        QTreeWidget.dropEvent(self, event)
