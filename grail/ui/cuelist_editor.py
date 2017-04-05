# -*- coding: UTF-8 -*-
"""
    grail.ui.cuelist_editor
    ~~~~~~~~~~~~~~~~~~~~~~~

    Manage cuelist in this view
"""
import re

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.ui import CuelistDialog, Panel
from grailkit.dna import DNA

from grail.ui.node_editor import TreeWidget, TreeItemWidget


class CuelistEditor(Panel):

    def __init__(self, app):
        super(CuelistEditor, self).__init__()

        self.app = app
        self._locked = False
        self._cuelist_id = self.app.project.settings().get('cuelist/current', default=0)

        self.app.project.entity_changed.connect(self._update)
        self.app.project.entity_removed.connect(self._update)

        self.dialog = CuelistDialog()
        self.dialog.showAt(QPoint(500, 500))

        self.connect('/app/close', self._close)
        self.connect('/cuelist/selected', self.cuelist_selected)
        self.connect('/cuelist/add', self._add_entity)

        self.__ui__()
        self.cuelist_selected(self._cuelist_id)

    def __ui__(self):

        self.setObjectName("cuelist")

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setObjectName("cuelist_layout")
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_tree = TreeWidget()
        self._ui_tree.setObjectName('playlist_tree')
        self._ui_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_tree.customContextMenuRequested.connect(self._context_menu)
        self._ui_tree.itemSelectionChanged.connect(self._selection_changed)
        self._ui_tree.itemExpanded.connect(self._item_expanded)
        self._ui_tree.itemCollapsed.connect(self._item_collapsed)

        self._ui_label = QLabel("...")
        self._ui_label.setObjectName("cuelist_label")
        self._ui_label.setAlignment(Qt.AlignCenter)
        self._ui_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._ui_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_label.mousePressEvent = lambda event: self.menu_action()

        self._ui_lock_action = QAction(QIcon(':/icons/lock.png'), 'Lock', self)
        self._ui_lock_action.setIconVisibleInMenu(True)
        self._ui_lock_action.triggered.connect(self.lock_action)

        self._ui_menu_action = QAction(QIcon(':/icons/menu.png'), 'Cuelists', self)
        self._ui_menu_action.setIconVisibleInMenu(True)
        self._ui_menu_action.triggered.connect(self.menu_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("cuelist_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        # self._ui_toolbar.addAction(self._ui_lock_action)
        self._ui_toolbar.addWidget(self._ui_label)
        # self._ui_toolbar.addAction(self._ui_menu_action)

        self._ui_layout.addWidget(self._ui_tree)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def lock_action(self):

        self._locked = not self._locked
        self.app.emit("app/lock", self._locked)

    def menu_action(self):

        point = QPoint(self.rect().width() / 2, self.rect().height() - 16)

        self.dialog.update_list()
        self.dialog.showAt(self.mapToGlobal(point))

    def _update(self, *args):

        self.cuelist_selected(self._cuelist_id)

    def cuelist_selected(self, cuelist_id=0):

        self._cuelist_id = cuelist_id
        cuelist = self.app.project.cuelist(cuelist_id)
        dna = self.app.project.dna

        if cuelist is None:
            self._ui_label.setText("...")
            return False

        self.app.project.settings().set('cuelist/current', cuelist_id)

        self._ui_label.setText("%s <small>(%d cues)</small>" % (cuelist.name, len(cuelist)))

        self._ui_tree.clear()

        def add_childs(tree_item, parent_id):
            for child in dna.childs(parent_id):
                child_item = TreeItemWidget(child)
                child_item.setText(0, child.name)

                add_childs(child_item, child.id)

                tree_item.addChild(child_item)
                child_item.setExpanded(bool(child.get('expanded', default=False)))

        for entity in cuelist.cues():
            item = TreeItemWidget(entity)
            item.setText(0, entity.name)

            add_childs(item, entity.id)

            self._ui_tree.addTopLevelItem(item)
            item.setExpanded(bool(entity.get('expanded', default=False)))

    def _add_entity(self, entity_id):
        """Add entity to cuelist"""

        cuelist_id = self._cuelist_id
        entity = self.app.library.item(entity_id)
        cuelist = self.app.project.cuelist(cuelist_id)

        if entity and cuelist:
            new_entity = cuelist.append(entity)

            pages = re.sub(r'([\s]+?[\n]+)', '\n', new_entity.lyrics if new_entity.lyrics else '').split('\n\n')

            for page in pages:
                new_entity.create(name=page, entity_type=DNA.TYPE_CUE)

            self.cuelist_selected(cuelist_id)

    def _item_clicked(self):
        pass

    def _item_double_clicked(self):
        pass

    def _context_menu(self):
        pass

    def _key_event(self):
        pass

    def _list_reordered(self):
        pass

    def _selection_changed(self):
        pass

    def _item_expanded(self, item):
        """Tree item expanded

        Args:
            item (TreeItemWidget): tree item
        """

        item.object().set('expanded', True)

    def _item_collapsed(self, item):
        """Tree item collapsed

        Args:
            item (TreeItemWidget): tree item
        """

        item.object().set('expanded', False)

    def _close(self):
        """Close child dialogs"""

        self.dialog.close()

