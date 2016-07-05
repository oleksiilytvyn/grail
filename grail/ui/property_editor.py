# -*- coding: UTF-8 -*-
"""
    grail.ui.property_editor
    ~~~~~~~~~~~~~~~~~~~~~~~~

    
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.ui import GWidget, GListWidget, GListItem


class PropertyEditor(GWidget):
    """Simple property editor"""

    def __init__(self, app):
        super(PropertyEditor, self).__init__()

        self.app = app

        self.__ui__()

    def __ui__(self):
        """Create UI layout and widgets"""

        self._ui_properties = QTableWidget()
        self._ui_properties.setShowGrid(False)
        self._ui_properties.setColumnCount(2)
        self._ui_properties.horizontalHeader().setVisible(False)
        self._ui_properties.horizontalHeader().setStretchLastSection(True)
        self._ui_properties.setAlternatingRowColors(True)
        self._ui_properties.verticalHeader().setVisible(False)
        self._ui_properties.setHorizontalHeaderLabels(["Key", "Value"])
        self._ui_properties.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._ui_properties.setSelectionMode(QAbstractItemView.SingleSelection)
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

        self._ui_add_action = QAction(QIcon(':/icon/32.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("library_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_layout.setSpacing(0)

        self._ui_layout.addWidget(self._ui_properties)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def node(self, entity_id):
        """Show a node properties"""

        props = self.app.project.properties(entity_id)

        entity = self.app.project.entity(entity_id)
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

        self._ui_properties.clearContents()
        self._ui_properties.setRowCount(len(props) + len(entity_props))

        index = 0

        for key in entity_props:
            self._ui_properties.setItem(index, 0, QTableWidgetItem(key))
            self._ui_properties.setItem(index, 1, QTableWidgetItem(str(entity_props[key])))
            index += 1

        for key in props:
            self._ui_properties.setItem(index, 0, QTableWidgetItem(key))
            self._ui_properties.setItem(index, 1, QTableWidgetItem(str(props[key])))
            index += 1

    def add_action(self):
        pass
