# -*- coding: UTF-8 -*-
"""
    grail.plugins.cuelist_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    View and edit cuelists

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import re

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.dna import DNA
from grailkit.qt import Popup, Application, Spacer, MessageDialog

from grail.core import Viewer


class CuelistDialog(Popup):

    def __init__(self):
        super(CuelistDialog, self).__init__()

        self._updating_list = False

        self.__ui__()
        self.update_list()

    def __ui__(self):

        self.setBackgroundColor(QColor("#222"))
        self.setObjectName('cuelist_dialog')

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_list = CuelistsListWidget()
        self._ui_list.setObjectName("cuelist_dialog_list")
        self._ui_list.cellChanged.connect(self._list_cell_changed)
        self._ui_list.itemSelectionChanged.connect(self._list_item_selected)

        self._ui_edit_action = QAction(QIcon(':/icons/edit.png'), 'Edit', self)
        self._ui_edit_action.triggered.connect(self.edit_action)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.setObjectName("cuelist_dialog_toolbar")
        self._ui_toolbar.addAction(self._ui_edit_action)
        self._ui_toolbar.addWidget(Spacer())
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)
        self.setWindowTitle('Cuelists')
        self.setGeometry(100, 300, 240, 300)
        self.setMinimumSize(240, 300)

    def update_list(self):

        self._updating_list = True

        app = Application.instance()
        cuelists = app.project.cuelists()
        x = 0

        self._ui_list.setRowCount(len(cuelists))

        for cuelist in cuelists:

            item = CuelistsListItem(cuelist.name)
            item.cuelist_id = cuelist.id

            button = CuelistsListButton(self)
            button.cuelist_id = cuelist.id
            button.clicked.connect(self._remove_clicked)

            self._ui_list.setItem(x, 0, item)
            self._ui_list.setCellWidget(x, 1, button)

            x += 1

        self._updating_list = False

    def _remove_clicked(self, item):

        Application.instance().project.remove(item.cuelist_id)

        self.update_list()

    def _list_item_selected(self):

        item = self._ui_list.item(self._ui_list.currentRow(), 0)

        if item:
            Application.instance().emit('/cuelist/selected', item.cuelist_id)

    def _list_cell_changed(self, row, column):

        # don't do anything if list refreshing
        if self._updating_list:
            return False

        item = self._ui_list.item(row, column)
        cuelist = Application.instance().project.cuelist(item.cuelist_id)
        cuelist.name = item.text()
        cuelist.update()

    def edit_action(self):
        """Edit button clicked"""

        items = self._ui_list.selectedItems()

        if len(items) < 1:
            return False

        self._ui_list.editItem(items[0])

    def add_action(self):
        """Add button clicked"""

        Application.instance().project.create(name="Untitled")

        self.update_list()
        self._ui_list.editItem(self._ui_list.item(self._ui_list.rowCount() - 1, 0))


class CuelistsListItem(QTableWidgetItem):
    """Playlist item inside playlist dialog"""

    def __init__(self, title):
        super(CuelistsListItem, self).__init__(title)

        self.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)


class CuelistsListButton(QWidget):

    clicked = pyqtSignal("QWidget")

    def __init__(self, parent):
        super(CuelistsListButton, self).__init__(parent)

        self._icon = QPixmap(':/icons/remove-white.png')

    def paintEvent(self, event):

        size = 18

        p = QPainter()
        p.begin(self)

        p.drawPixmap(self.width() / 2 - size / 2, self.height() / 2 - size / 2, size, size, self._icon)

        p.end()

    def mousePressEvent(self, event):

        self.clicked.emit(self)


class CuelistsListWidget(QTableWidget):

    def __init__(self, parent=None):
        """Initialize"""

        super(CuelistsListWidget, self).__init__(parent)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAutoScroll(False)

        self.setColumnCount(2)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(["Label", "Button"])
        self.setShowGrid(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)

        self.setColumnWidth(1, 42)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        original = self.verticalScrollBar()

        self._scrollbar = QScrollBar(Qt.Vertical, self)
        self._scrollbar.valueChanged.connect(original.setValue)
        self._scrollbar.rangeChanged.connect(self.scroll_to_selected)

        original.valueChanged.connect(self._scrollbar.setValue)

        self._update_scrollbar()

    def paintEvent(self, event):
        """Draw widget"""

        QTableWidget.paintEvent(self, event)

    def update(self, **kwargs):
        """Update ui components"""

        super(CuelistsListWidget, self).update()

        self._update_scrollbar()

    def _update_scrollbar(self):
        """Update scrollbar to draw properly"""

        original = self.verticalScrollBar()

        if not hasattr(self, '_scrollbar'):
            return

        if original.value() == original.maximum() and original.value() == 0:
            self._scrollbar.hide()
        else:
            self._scrollbar.show()

        self._scrollbar.setPageStep(original.pageStep())
        self._scrollbar.setRange(original.minimum(), original.maximum())
        self._scrollbar.resize(8, self.rect().height())
        self._scrollbar.move(self.rect().width() - 8, 0)

    def scroll_to_selected(self):
        """Scroll to selected item"""

        selected = self.selectedIndexes()

        if len(selected) == 0:
            x = 0
            self.setCurrentCell(x, 0)
        else:
            x = selected[0].row()

        self.scrollToItem(self.item(x, 0))


class CuelistViewer(Viewer):
    """Library viewer"""

    id = 'cuelist'
    # Unique plugin name string
    name = 'Cuelist'
    # Plugin author string
    author = 'Grail Team'
    # Plugin description string
    description = 'Manage cuelists'

    def __init__(self, *args):
        super(CuelistViewer, self).__init__(*args)

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
        self._ui_tree.itemClicked.connect(self._item_clicked)
        self._ui_tree.itemDoubleClicked.connect(self._item_double_clicked)

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

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(QIcon(':/icons/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("cuelist_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(self._ui_label)

        self._ui_layout.addWidget(self._ui_tree)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def view_action(self):
        """Replace current view with something other"""

        menu = self.plugin_menu()
        menu.exec_(self._ui_toolbar.mapToGlobal(self._ui_view_action.pos()))

    def lock_action(self):

        self._locked = not self._locked
        self.app.emit("app/lock", self._locked)

    def menu_action(self):

        point = QPoint(self.rect().width() / 2, self.rect().height() - 16)

        self.dialog.update_list()
        self.dialog.showAt(self.mapToGlobal(point))

    def item_delete(self, item):
        """Remove cue item menu_action"""

        item.object().delete()

    def item_edit(self, item):
        """Edit cue menu_action"""

        print('edit', item)

    def _update(self, *args):

        self.cuelist_selected(self._cuelist_id)

    def cuelist_selected(self, cuelist_id=0):

        self._cuelist_id = cuelist_id
        cuelist = self.app.project.cuelist(cuelist_id)
        dna = self.app.project.dna

        if cuelist is None:
            self._ui_label.setText("...")
            return False

        self._ui_tree.clear()

        self.app.project.settings().set('cuelist/current', cuelist_id)

        self._ui_label.setText("%s <small>(%d cues)</small>" % (cuelist.name, len(cuelist)))

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

    def _item_clicked(self, item):
        """Preview cue text"""

        self.app.emit('/message/preview', item.object().name)

    def _item_double_clicked(self, item):
        """Send cue text"""

        self.app.emit('/message/master', item.object().name)

    def _context_menu(self, pos):
        """Context menu on cue item"""

        item = self._ui_tree.itemAt(pos)

        if item:
            menu = QMenu("Context Menu", self)

            delete_action = QAction('Delete cue', menu)
            delete_action.triggered.connect(lambda: self.item_delete(item))

            edit_action = QAction('Edit cue', menu)
            edit_action.triggered.connect(lambda: self.item_edit(item))

            menu.addAction(edit_action)
            menu.addAction(delete_action)

            menu.exec_(self._ui_tree.mapToGlobal(pos))

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


class TreeWidget(QTreeWidget):

    def __init__(self, parent=None):
        super(TreeWidget, self).__init__(parent)

        self.setAlternatingRowColors(True)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.header().close()
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setWordWrap(True)
        self.setAnimated(False)
        self.setSortingEnabled(False)

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


class TreeItemWidget(QTreeWidgetItem):
    """Representation of node as QTreeWidgetItem"""

    def __init__(self, data=None):
        super(TreeItemWidget, self).__init__()

        self._data = data

    def object(self):

        return self._data

    def setObject(self, data):

        self._data = data
