# -*- coding: UTF-8 -*-
"""
    grail.plugins.node_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    This plugin for developers who want to see whats going on with nodes

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
from collections import defaultdict

from grailkit.dna import DNA

from grail.qt import *
from grail.core import Viewer


class NodeViewer(Viewer):
    """View DNA nodes of currently opened file

    Connected:

    Emits:
        '!node/selected', id:int
    """

    id = 'node'
    name = 'Nodes'
    author = 'Alex Litvin'
    description = 'View all nodes in grail file'
    single_instance = True

    def __init__(self, *args):
        super(NodeViewer, self).__init__(*args)

        self.__ui__()

        self._folded = defaultdict(bool)
        self._selected_id = None
        self._system_types = (DNA.TYPE_VIEW, DNA.TYPE_PROJECT, DNA.TYPE_LAYOUT, DNA.TYPE_SETTINGS)

        self.app.project.entity_changed.connect(self._update)
        self.app.project.entity_removed.connect(self._update)

        self._update()

    def __ui__(self):
        """Setup UI"""

        self.setObjectName("NodeViewer")

        self._ui_tree = _TreeWidget()
        self._ui_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_tree.itemSelectionChanged.connect(self._selection_changed)
        self._ui_tree.itemExpanded.connect(self._item_expanded)
        self._ui_tree.itemCollapsed.connect(self._item_collapsed)
        self._ui_tree.customContextMenuRequested.connect(self._context_menu)

        self._ui_add_action = QAction(QIcon(':/rc/add.png'), 'Add node', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_remove_action = QAction(QIcon(':/rc/remove-white.png'), 'Remove node', self)
        self._ui_remove_action.setIconVisibleInMenu(True)
        self._ui_remove_action.triggered.connect(self.remove_action)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(QIcon(':/rc/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("NodeViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addStretch()
        self._ui_toolbar.addAction(self._ui_remove_action)
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.addWidget(self._ui_tree)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def _update(self, *args):
        """Update nodes tree"""

        dna = self.app.project.dna
        selected_item = None
        system_icon = Icon.colored(':/rc/unlock.png', QColor('#aeca4b'), QColor('#e3e3e3'))

        self._ui_tree.clear()

        def add_childs(tree_item, parent_id):
            nonlocal self
            nonlocal selected_item
            nonlocal system_icon

            for child in dna.childs(parent_id):
                child_item = QTreeWidgetItem(child)
                child_item.setText(0, child.name)

                if child.type in self._system_types:
                    child_item.setIcon(0, system_icon)

                if child.id == self._selected_id:
                    selected_item = child_item

                add_childs(child_item, child.id)
                tree_item.addChild(child_item)

        for entity in dna.childs(0):
            item = QTreeWidgetItem(entity)
            item.setText(0, entity.name)

            add_childs(item, entity.id)

            if entity.type in self._system_types:
                item.setIcon(0, system_icon)

            if entity.id == self._selected_id:
                selected_item = item

            self._ui_tree.addTopLevelItem(item)

        # expand items
        for item in self._ui_tree.findItems('', Qt.MatchContains | Qt.MatchRecursive):
            item.setExpanded(self._folded[item.object().id])

        if selected_item:
            index = self._ui_tree.indexFromItem(selected_item)
            self._ui_tree.setCurrentIndex(index)

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

    def _context_menu(self, point):
        """Context menu callback

        Args:
            point (QPoint): point where context menu requested
        """

        if not self._ui_tree.itemAt(point):
            return False

        menu = QMenu("Context menu", self)

        remove_action = QAction('Remove', menu)
        remove_action.triggered.connect(lambda: self.remove_action())

        add_action = QAction('Add', menu)
        add_action.triggered.connect(lambda: self.add_action())

        menu.addAction(remove_action)
        menu.addAction(add_action)
        menu.exec_(self._ui_tree.mapToGlobal(point))

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def add_action(self):
        """Add new node"""

        item = self._ui_tree.currentItem()
        parent_id = item.object().id if item else 0

        self.app.project.dna.create("Untitled item", parent=parent_id)

    def remove_action(self):
        """Remove selected entity"""

        item = self._ui_tree.currentItem()
        above = self._ui_tree.itemAbove(item)
        node = item.object()

        if item and node.type in self._system_types:
            message = MessageDialog(title="Item can't be removed",
                                    text="Item '%s' can't be removed" % node.name,
                                    icon=MessageDialog.Warning)
            message.exec_()

            return False

        if above:
            self._selected_id = above.object().id

        self.app.project.dna.remove(node.id)
        self._update()

        # select first node
        item = self._ui_tree.currentItem()

        if item:
            self.emit('!node/selected', above)


class _TreeWidget(QTreeWidget):

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
