# -*- coding: UTF-8 -*-
"""
    grail.plugins.property_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Node properties viewer

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import random

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QAction, QWidget, QStackedWidget, QToolButton

from grailkit.qt import Toolbar, Icon, Label, Spacer, VLayout, Popup, Table, TableItem

from grail.core import Viewer


class PropertyViewer(Viewer):
    """Simple property editor

    Connected:
        '!node/selected' id<int>
    Emits:

    Properties:
        follow (bool): If True viewer will show properties of selected node. Default value is True
        entity (int, None): Id of selected entity. Default value is None
        property (str, None): Key of selected property name. Default value is None
    """

    # todo: Add property editor that supports all types (True, False, None, int, float, string, JSON)

    id = 'property'
    name = 'Properties'
    author = 'Grail Team'
    description = 'View properties of selected entities'

    def __init__(self, *args, **kwargs):
        super(PropertyViewer, self).__init__(*args, **kwargs)

        self.__ui__()

        self._updating = True
        self._entity_id = self.get('entity', default=None)
        self._property = self.get('property', default=None)
        self._follow = not self.get('follow', default=True)

        # connect signals
        self.connect('!node/selected', self._update)

        # update view
        self.follow_action()
        self._update(self._entity_id)

    def __ui__(self):
        """Create UI layout and widgets"""

        self.setObjectName("PropertyViewer")

        self._ui_properties = Table(self)
        self._ui_properties.setShowGrid(False)
        self._ui_properties.setColumnCount(2)
        self._ui_properties.setAlternatingRowColors(True)
        self._ui_properties.verticalHeader().setVisible(False)
        self._ui_properties.setHorizontalHeaderLabels(["Key", "Value"])
        self._ui_properties.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._ui_properties.setSelectionMode(QAbstractItemView.SingleSelection)
        self._ui_properties.itemChanged.connect(self._item_changed)
        self._ui_properties.itemClicked.connect(self._item_clicked)
        self._ui_properties.itemSelectionChanged.connect(self._selection_changed)

        header = self._ui_properties.horizontalHeader()
        header.setVisible(True)
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(QHeaderView.Interactive)

        # Empty
        self._ui_empty_title = Label("No properties")
        self._ui_empty_title.setObjectName('PropertyViewer_empty_title')

        self._ui_empty_info = Label("Node not selected or node don't have properties.")
        self._ui_empty_info.setObjectName('PropertyViewer_empty_info')
        self._ui_empty_info.setWordWrap(True)

        self._ui_empty_layout = VLayout()
        self._ui_empty_layout.setContentsMargins(12, 12, 12, 12)
        self._ui_empty_layout.setAlignment(Qt.AlignHCenter)
        self._ui_empty_layout.addWidget(Spacer())
        self._ui_empty_layout.addWidget(self._ui_empty_title)
        self._ui_empty_layout.addWidget(self._ui_empty_info)
        self._ui_empty_layout.addWidget(Spacer())

        self._ui_empty = QWidget()
        self._ui_empty.setObjectName('PropertyViewer_empty')
        self._ui_empty.setLayout(self._ui_empty_layout)

        self._ui_stack = QStackedWidget()
        self._ui_stack.addWidget(self._ui_empty)
        self._ui_stack.addWidget(self._ui_properties)
        self._ui_stack.setCurrentIndex(0)

        # Action
        self._ui_follow_action = QAction(QIcon(':/icons/at.png'), 'Follow', self)
        self._ui_follow_action.setIconVisibleInMenu(True)
        self._ui_follow_action.triggered.connect(self.follow_action)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add property', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_remove_action = QAction(QIcon(':/icons/remove-white.png'), 'Remove property', self)
        self._ui_remove_action.setIconVisibleInMenu(True)
        self._ui_remove_action.triggered.connect(self.remove_action)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(QIcon(':/icons/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        # Toolbar
        self._ui_toolbar = Toolbar()
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addStretch()
        self._ui_toolbar.addAction(self._ui_follow_action)
        self._ui_toolbar.addAction(self._ui_remove_action)
        self._ui_toolbar.addAction(self._ui_add_action)

        # Layout
        self._ui_layout = VLayout()
        self._ui_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_layout.setSpacing(0)

        self._ui_layout.addWidget(self._ui_stack)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def _update(self, entity_id):
        """Show a node properties"""

        self._updating = True

        # update only if following node select
        if self._follow:
            self.set('entity', entity_id)
            self._entity_id = entity_id

        props = self.app.project.dna.properties(self._entity_id)
        entity = self.app.project.dna.entity(self._entity_id)

        self._ui_stack.setCurrentIndex(1 if entity else 0)

        if not entity:
            return False

        entity_props = [('@id', entity.id),
                        ('@name', entity.name),
                        ('@type', entity.type),
                        ('@parent', entity.parent_id),
                        ('@content', entity.content),
                        ('@created', entity.created),
                        ('@modified', entity.modified),
                        ('@search', entity.search),
                        ('@index', entity.index)
                        ]

        for key, value in sorted(props.items(), reverse=True):
            entity_props.append((key, value))

        self._ui_properties.clearContents()
        self._ui_properties.setRowCount(len(entity_props))

        index = 0

        for item in entity_props:
            key = item[0]
            value = item[1]

            item_key = TableItem(key)
            item_key.entity_id = self._entity_id
            item_key.entity_key = key

            item_value = TableItem(str(value))
            item_value.entity_id = self._entity_id
            item_value.entity_key = key

            if isinstance(value, int):
                color = QColor('#03A9F4')
            elif isinstance(value, str):
                color = QColor('#8BC34A')
            elif isinstance(value, bool):
                color = QColor('#673AB7')
            elif value is None:
                color = QColor('#EF6C00')
            else:
                color = QColor('#f1f1f1')

            item_value.setIcon(Icon.colored(':/icons/live.png', color, QColor('#e3e3e3')))

            self._ui_properties.setItem(index, 0, item_key)
            self._ui_properties.setItem(index, 1, item_value)

            if self._property == key:
                self._ui_properties.selectRow(index)

            index += 1

        self._updating = False

    def follow_action(self):
        """Toggle node follow"""

        self._follow = not self._follow

        # store property
        self.set('follow', self._follow)

        if self._follow:
            self._ui_follow_action.setIcon(Icon.colored(':/icons/at.png', QColor('#aeca4b'), QColor('#e3e3e3')))
        else:
            self._ui_follow_action.setIcon(QIcon(':/icons/at.png'))

    def view_action(self):
        """Replace current view with something else"""

        self.plugin_menu().exec_(self._ui_toolbar.mapToGlobal(self._ui_view_action.pos()))

    def add_action(self):
        """Add a new property"""

        property_key = 'Property-%d' % random.randint(1000, 9999)
        entity = self.app.project.dna.entity(self._entity_id)

        if not entity:
            return False

        self.app.project.dna.set(self._entity_id, property_key, None)

        # update view
        self._update(self._entity_id)

        # find and edit new property
        index = self._ui_properties.rowCount()-1

        for i in range(self._ui_properties.rowCount()-1):
            if self._ui_properties.item(i, 0).text() == property_key:
                index = i
                break

        self._ui_properties.editItem(self._ui_properties.item(index, 0))

    def remove_action(self):
        """Remove a selected property"""

        entity = self.app.project.dna.entity(self._entity_id)

        if not entity:
            return False

        indexes = self._ui_properties.selectionModel().selectedIndexes()
        count = self._ui_properties.rowCount()

        self.app.project.dna.unset(self._entity_id, self._property)
        self._update(self._entity_id)

        if len(indexes) > 0 and count > 0:
            next_index = self._ui_properties.model().index(max(0, indexes[0].row() - 1), 0)
            self._ui_properties.setCurrentIndex(next_index)

    def _selection_changed(self):
        """Selection changed"""

        items = self._ui_properties.selectedItems()

        if len(items) > 0:
            self._item_clicked(items[0])

    def _item_clicked(self, item):
        """Table item clicked"""

        self._property = item.entity_key
        self.set('property', item.entity_key)

    def _item_changed(self, item):
        """Table item changed"""

        if self._updating:
            return

        dna = self.app.project.dna

        std_props = ['@id',
                     '@name',
                     '@type',
                     '@parent',
                     '@content',
                     '@created',
                     '@modified',
                     '@search',
                     '@index']

        if item.column() == 0:
            if item.entity_key not in std_props:
                dna.rename(item.entity_id, item.entity_key, str(item.text()))

        if item.column() == 1:
            key = item.entity_key
            value = str(item.text())
            entity = dna.entity(item.entity_id)

            if key in std_props:
                if key == '@name':
                    entity.name = value
                if key == '@parent':
                    entity.parent_id = int(value)
                if key == '@index':
                    entity.index = int(value)
                if key == '@search':
                    entity.search = value
                if key == '@content':
                    entity.content = value

                entity.update()
            else:
                dna.set(item.entity_id, key, value)

        self._update(item.entity_id)


class PropertyPopup(Popup):
    """Popup dialog that allows users to edit DNA properties of all types."""

    def __init__(self, parent=None):
        super(PropertyPopup, self).__init__(parent)

    def __ui__(self):
        pass
