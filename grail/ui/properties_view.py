# -*- coding: UTF-8 -*-
"""
    grail.ui.properties_view
    ~~~~~~~~~~~~~~~~~~~~~~~~

    View and edit properties of DNA entity, this widget used in Cue Inspector and Properties Viewer

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
import json
import random

from grail.qt import *


class PropertiesView(QtWidgets.QWidget):
    """View for editing entity properties"""

    def __init__(self, parent=None):
        super(PropertiesView, self).__init__(parent)

        self._dna = Application.instance().project.dna
        self._updating = True
        self._entity_id = None
        self._property = None
        self._follow = False

        # Properties
        self._ui_properties = QtWidgets.QTableWidget(self)
        self._ui_properties.setShowGrid(False)
        self._ui_properties.setColumnCount(2)
        self._ui_properties.setAlternatingRowColors(True)
        self._ui_properties.verticalHeader().setVisible(False)
        self._ui_properties.setHorizontalHeaderLabels(["Key", "Value"])
        self._ui_properties.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._ui_properties.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._ui_properties.itemChanged.connect(self._item_changed)
        self._ui_properties.itemClicked.connect(self._item_clicked)
        self._ui_properties.itemSelectionChanged.connect(self._selection_changed)
        self._ui_properties.setItemDelegateForColumn(1, _PropertyDelegate(self))
        self._ui_properties.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._ui_properties.customContextMenuRequested.connect(self._context_menu)

        header = self._ui_properties.horizontalHeader()
        header.setVisible(True)
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

        # Empty
        self._ui_empty_title = QtWidgets.QLabel("No properties")
        self._ui_empty_title.setObjectName('PropertiesView_empty_title')

        self._ui_empty_info = QtWidgets.QLabel("Node not selected or don't have properties.")
        self._ui_empty_info.setObjectName('PropertiesView_empty_info')
        self._ui_empty_info.setWordWrap(True)

        self._ui_empty_layout = QtWidgets.QVBoxLayout()
        self._ui_empty_layout.setContentsMargins(12, 12, 12, 12)
        self._ui_empty_layout.setAlignment(QtCore.Qt.AlignHCenter)
        self._ui_empty_layout.addStretch()
        self._ui_empty_layout.addWidget(self._ui_empty_title)
        self._ui_empty_layout.addWidget(self._ui_empty_info)
        self._ui_empty_layout.addStretch()

        self._ui_empty = QtWidgets.QWidget()
        self._ui_empty.setObjectName('PropertiesView_empty')
        self._ui_empty.setLayout(self._ui_empty_layout)

        self._ui_stack = QtWidgets.QStackedWidget()
        self._ui_stack.addWidget(self._ui_empty)
        self._ui_stack.addWidget(self._ui_properties)
        self._ui_stack.setCurrentIndex(0)

        self._ui_layout = QtWidgets.QVBoxLayout()
        self._ui_layout.addWidget(self._ui_stack)

        self.setLayout(self._ui_layout)

        # Track project changes
        project = Application.instance().project
        project.entity_changed.connect(self._update)
        project.entity_removed.connect(self._update)
        project.property_changed.connect(lambda entity_id, key, value: self._update())

    def _context_menu(self, point):
        """Context menu callback

        Args:
            point (QPoint): point where context menu requested
        """

        if not self._ui_properties.itemAt(point):
            return False

        menu = QtWidgets.QMenu("Context menu", self)

        remove_action = QtWidgets.QAction('Remove property', menu)
        remove_action.triggered.connect(lambda: self.removeSelected())

        add_action = QtWidgets.QAction('Add property', menu)
        add_action.triggered.connect(lambda: self.addProperty())

        menu.addAction(add_action)
        menu.addAction(remove_action)

        menu.exec_(self._ui_properties.mapToGlobal(point))

    def addProperty(self):
        """Add a new property"""

        property_key = 'Property-%d' % random.randint(1000, 9999)
        entity = self._dna.entity(self._entity_id)

        if not entity:
            return False

        self._dna.set(self._entity_id, property_key, None)

        # update view
        self._update()

        # find and edit new property
        index = self._ui_properties.rowCount()-1

        for i in range(self._ui_properties.rowCount()-1):
            if self._ui_properties.item(i, 0).text() == property_key:
                index = i
                break

        self._ui_properties.editItem(self._ui_properties.item(index, 0))

    def removeSelected(self):
        """Remove a selected property"""

        entity = self._dna.entity(self._entity_id)

        if not entity:
            return False

        indexes = self._ui_properties.selectionModel().selectedIndexes()
        count = self._ui_properties.rowCount()

        self._dna.unset(self._entity_id, self._property)
        self._update()

        if len(indexes) > 0 and count > 0:
            next_index = self._ui_properties.model().index(max(0, indexes[0].row() - 1), 0)
            self._ui_properties.setCurrentIndex(next_index)

    def setEntity(self, entity):
        """Set entity to edit properties

        Args:
            entity (DNAEntity): entity of which properties to show
        """

        if not self._follow:
            return False

        self._entity_id = entity.id
        self._property = None
        self._update(self._entity_id)

    def setEntityId(self, entity_id):
        """Set entity to edit properties

        Args:
            entity_id (int): entity id of which properties to show
        """

        if not self._follow:
            return False

        self._entity_id = entity_id
        self._property = None
        self._update(self._entity_id)

    def setEntityFollow(self, follow):
        """Set to True and setEntity will not take effect,
        and properties of current entity will not disappear

        Args:
            follow (bool): Flag
        """

        self._follow = bool(follow)

    def _update(self, entity_id=None):
        """Show a node properties

        Args:
            entity_id (int): DNAEntity id, not used by method, but given by callbacks
        """

        self._updating = True

        # update only if following node select
        if self._follow and entity_id:
            self._entity_id = entity_id

        props = self._dna.properties(self._entity_id)
        entity = self._dna.entity(self._entity_id)

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

            item_key = QtWidgets.QTableWidgetItem(key)
            item_key.entity_id = self._entity_id
            item_key.entity_key = key

            item_value = QtWidgets.QTableWidgetItem(str(value))
            item_value.setData(QtCore.Qt.UserRole, value)
            item_value.entity_id = self._entity_id
            item_value.entity_key = key

            # True and False
            if isinstance(value, bool) and value is True:
                color = QtGui.QColor('#8BC34A')
            elif isinstance(value, bool) and value is False:
                color = QtGui.QColor('#B71C1C')
            # Number
            elif isinstance(value, int):
                color = QtGui.QColor('#EF6C00')
            elif isinstance(value, float):
                color = QtGui.QColor('#FFEB3B')
            # String
            elif isinstance(value, str):
                color = QtGui.QColor('#03A9F4')
            # JSON
            elif isinstance(value, dict) or isinstance(value, list):
                color = QtGui.QColor('#673AB7')
            # None
            else:
                color = QtGui.QColor('#BDBDBD')

            item_value.setIcon(Icon.colored(':/rc/live.png', color, QtGui.QColor('#e3e3e3')))

            self._ui_properties.setItem(index, 0, item_key)
            self._ui_properties.setItem(index, 1, item_value)

            if self._property == key:
                self._ui_properties.selectRow(index)

            index += 1

        self._updating = False

    def _selection_changed(self):
        """Selection changed"""

        items = self._ui_properties.selectedItems()

        if len(items) > 0:
            self._item_clicked(items[0])

    def _item_clicked(self, item):
        """Table item clicked"""

        self._property = item.entity_key

    def _item_changed(self, item):
        """Table item changed"""

        if self._updating:
            return

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
                self._dna.rename(item.entity_id, item.entity_key, str(item.text()))

        if item.column() == 1:
            key = item.entity_key
            value = item.data(QtCore.Qt.UserRole)
            entity = self._dna.entity(item.entity_id)

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
                self._dna.set(item.entity_id, key, value)

        self._update()


class _PropertyEdit(QtWidgets.QLineEdit):
    """Editor for PropertiesView"""

    TYPES = {
        "None": 'type_none',
        "True": 'type_true',
        "False": 'type_false',
        "Float": 'type_float',
        "Integer": 'type_int',
        "String": 'type_str',
        "JSON": 'type_json'
        }

    TYPES_ORDER = ['None', 'True', 'False', 'Float', 'Integer', 'String', 'JSON']

    def __init__(self, *args):
        super(_PropertyEdit, self).__init__(*args)

        self._type = 'type_none'
        self._data = None

        self.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
        self.textChanged.connect(self._text_changed)

        self._ui_clear = QtWidgets.QToolButton(self)
        self._ui_clear.setIconSize(QtCore.QSize(14, 14))
        self._ui_clear.setIcon(QtGui.QIcon(':/rc/branch-open.png'))
        self._ui_clear.setCursor(QtCore.Qt.ArrowCursor)
        self._ui_clear.setStyleSheet("""
            QToolButton {
                background: none;
                border: none;
                }
            """)
        self._ui_clear.clicked.connect(self._context_menu)

        frame_width = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)

        self.setStyleSheet("""
                QLineEdit {
                    background-color: #e9e9e9;
                    padding-right: %spx;
                    border: 1px solid #888;
                    border-radius: 2px;
                    }
                """ % str(self._ui_clear.sizeHint().width() / 2 + frame_width + 1))

    def setData(self, value):
        """Store something"""

        if isinstance(value, int):
            _type = 'type_int'
        elif isinstance(value, float):
            _type = 'type_float'
        elif isinstance(value, str):
            _type = 'type_str'
        elif value is True:
            _type = 'type_true'
        elif value is False:
            _type = 'type_false'
        elif isinstance(value, dict) or isinstance(value, list):
            _type = 'type_json'
        else:
            _type = 'type_none'

        self._type = _type
        self._data = value

    def data(self):
        """Returns stored data"""

        return self._data

    def resizeEvent(self, event):
        """Redraw some elements"""

        size = self.rect()
        btn_size = self._ui_clear.sizeHint()
        frame_width = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)

        self._ui_clear.move(size.width() - btn_size.width() - frame_width * 2,
                            size.height() / 2 - btn_size.height() / 2)

    def _context_menu(self):
        """Open context menu"""

        menu = QtWidgets.QMenu("Select Type", self)

        def wrap(_type, _name):
            """Action context closure"""

            return lambda: self._menu_item(_type, _name)

        for name in self.TYPES_ORDER:
            _type = self.TYPES[name]
            action = QtWidgets.QAction(name, menu)
            action.triggered.connect(wrap(name, _type))

            menu.addAction(action)

        menu.exec_(self.mapToGlobal(self._ui_clear.pos()))

    def _menu_item(self, name, _type):
        """Context menu item clicked"""

        self._type = _type
        self._data = self.type(self._type, str(self.text()))

        self.setText(str(self._data))

    def _text_changed(self):
        """Update user data"""

        self._data = self.type(self._type, str(self.text()))

    @classmethod
    def type(cls, _type, value):
        """Convert `type`"""

        return getattr(cls, _type)(value)

    @classmethod
    def type_none(cls, value):
        """Convert anything to None"""

        return None

    @classmethod
    def type_true(cls, value):
        """Convert anything to True"""

        return True

    @classmethod
    def type_false(cls, value):
        """Convert anything to False"""

        return False

    @classmethod
    def type_str(cls, value):
        """Convert anything to string"""

        try:
            return str(value)
        except (UnicodeError, ValueError):
            return ""

    @classmethod
    def type_float(cls, value):
        """Convert anything to float"""

        try:
            return float(value)
        except ValueError:
            return 0

    @classmethod
    def type_int(cls, value):
        """Convert anything to int"""
        try:
            return int(value)
        except ValueError:
            return 0

    @classmethod
    def type_json(cls, value):
        """Convert anything to json object (dict, list)"""

        try:
            return json.loads(str(value))
        except ValueError:
            return {}


class _PropertyDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, *args):
        super(_PropertyDelegate, self).__init__(*args)

    def createEditor(self, parent, option, index):
        """Create editor widget"""

        editor = _PropertyEdit(parent)

        return editor

    def setEditorData(self, editor, index):
        """Set"""
        super(_PropertyDelegate, self).setEditorData(editor, index)

        editor.setData(index.data(QtCore.Qt.UserRole))

    def setModelData(self, editor, model, index):
        """Store data"""

        index.model().setData(index, editor.data(), QtCore.Qt.UserRole)
