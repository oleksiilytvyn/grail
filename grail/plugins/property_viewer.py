# -*- coding: UTF-8 -*-
"""
    grail.plugins.property_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.qt import Spacer

from grail.core import Viewer


class PropertyViewer(Viewer):
    """Simple property editor"""

    # Unique plugin name string
    name = 'Properties'
    # Plugin author string
    author = 'Grail Team'
    # Plugin description string
    description = 'View all properties of selected entities'

    def __init__(self, app):
        super(PropertyViewer, self).__init__()

        self.current_entity = None
        self.current_property = None
        self._updating_list = True

        # connect signals
        self.connect('/node/selected', self.node)

        self.__ui__()

    def __ui__(self):
        """Create UI layout and widgets"""

        self._ui_properties = QTableWidget()
        self._ui_properties.setShowGrid(False)
        self._ui_properties.setColumnCount(2)
        self._ui_properties.horizontalHeader().setVisible(True)
        self._ui_properties.horizontalHeader().setStretchLastSection(True)
        self._ui_properties.setAlternatingRowColors(True)
        self._ui_properties.verticalHeader().setVisible(False)
        self._ui_properties.setHorizontalHeaderLabels(["Key", "Value"])
        self._ui_properties.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._ui_properties.setSelectionMode(QAbstractItemView.SingleSelection)
        self._ui_properties.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._ui_properties.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._ui_properties.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: #2f2f2f;
                alternate-background-color: #393939;
                show-decoration-selected: 1;
                outline: 0;
                }

                QTableWidget QScrollBar::handle:vertical {
                    background: #ddd;
                    min-height: 20px;
                    border-radius: 3px;
                    }

                QTableWidget::item {
                    color: #e6e6e6;
                    padding: 4px 12px;
                    margin: 0;
                    border-bottom: 1px solid transparent;
                    qproperty-wordWrap: true;
                    }

                QTableWidget::item:selected {
                    background: #8a9fbb;
                    border-bottom: 1px solid #8a9fbb;
                    color: #e6e6e6;
                    }""")
        self._ui_properties.itemChanged.connect(self._item_changed)
        self._ui_properties.itemClicked.connect(self._item_clicked)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add property', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_remove_action = QAction(QIcon(':/icons/remove-white.png'), 'Remove property', self)
        self._ui_remove_action.setIconVisibleInMenu(True)
        self._ui_remove_action.triggered.connect(self.remove_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("library_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_add_action)
        self._ui_toolbar.addWidget(Spacer())
        self._ui_toolbar.addAction(self._ui_remove_action)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_layout.setSpacing(0)

        self._ui_layout.addWidget(self._ui_properties)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def node(self, entity_id):
        """Show a node properties"""

        self._updating_list = True
        self.current_entity = entity_id

        props = self.app.project.dna.properties(entity_id)
        entity = self.app.project.dna.entity(entity_id)

        if not entity:
            return False

        entity_props = {'@id': entity.id,
                        '@name': entity.name,
                        '@type': entity.type,
                        '@parent': entity.parent_id,
                        '@content': entity.content,
                        '@created': entity.created,
                        '@modified': entity.modified,
                        '@search': entity.search,
                        '@index': entity.index
                        }

        for key in props:
            entity_props[key] = props[key]

        self._ui_properties.clearContents()
        self._ui_properties.setRowCount(len(entity_props))

        index = 0

        for key in entity_props:
            item_key = QTableWidgetItem(key)
            item_key.entity_id = entity_id
            item_key.entity_key = key

            item_value = QTableWidgetItem(str(entity_props[key]))
            item_value.entity_id = entity_id
            item_value.entity_key = key

            self._ui_properties.setItem(index, 0, item_key)
            self._ui_properties.setItem(index, 1, item_value)

            index += 1

        self._updating_list = False

    def add_action(self):
        """Add a new property"""

        self.app.project.dna.set(self.current_entity, str(self.current_property) + '%', "")

    def remove_action(self):
        """Remove a selected property"""

        self.app.project.dna.unset(self.current_entity, self.current_property)
        self.node(self.current_entity)

    def _item_clicked(self, item):

        self.current_property = item.entity_key

    def _item_changed(self, item):

        if self._updating_list:
            return

        project = self.app.project
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
                project.dna.rename(item.entity_id, item.entity_key, str(item.text()))

        if item.column() == 1:
            key = item.entity_key
            value = str(item.text())
            entity = project.dna.entity(item.entity_id)

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
                project.dna.set(item.entity_id, key, value)

        self.node(item.entity_id)
        self.emit('/property/changed')
