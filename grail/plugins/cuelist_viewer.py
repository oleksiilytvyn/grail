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

from grailkit.dna import DNA, CueEntity
from grailkit.qt import *

from grail.core import Viewer


class CuelistDialog(Popup):

    selected = pyqtSignal(int)

    def __init__(self):
        super(CuelistDialog, self).__init__()

        self._updating_list = False
        self._app = Application.instance()

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

        self._app.project.remove(item.cuelist_id)

        self.update_list()

    def _list_item_selected(self):

        item = self._ui_list.item(self._ui_list.currentRow(), 0)

        if item:
            self._app.signals.emit('/cuelist/selected', item.cuelist_id)
            self.selected.emit(item.cuelist_id)

    def _list_cell_changed(self, row, column):

        # don't do anything if list refreshing
        if self._updating_list:
            return False

        item = self._ui_list.item(row, column)
        cuelist = self._app.project.cuelist(item.cuelist_id)
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

        self._app.project.create(name="Untitled")

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


class CueDialog(Dialog):

    def __init__(self, viewer):
        super(CueDialog, self).__init__()

        self._viewer = viewer
        self._entity = None
        self.__ui__()

    def __ui__(self):
        """Build UI"""

        self._ui_text = TextEdit()
        self._ui_text.setPlaceholderText("Lyrics")
        self._ui_text.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self._ui_text.setAcceptRichText(False)

        policy = self._ui_text.sizePolicy()
        policy.setVerticalStretch(1)

        self._ui_text.setSizePolicy(policy)

        self._ui_button_ok = Button("Ok")
        self._ui_button_ok.clicked.connect(self.accept_action)

        self._ui_button_cancel = Button("Cancel")
        self._ui_button_cancel.clicked.connect(self.reject_action)

        self._ui_buttons = HLayout()
        self._ui_buttons.setSpacing(10)
        self._ui_buttons.setContentsMargins(0, 0, 0, 0)
        self._ui_buttons.addWidget(Spacer())
        self._ui_buttons.addWidget(self._ui_button_cancel)
        self._ui_buttons.addWidget(self._ui_button_ok)

        self._ui_layout = VLayout()
        self._ui_layout.setSpacing(8)
        self._ui_layout.setContentsMargins(12, 12, 12, 10)

        self._ui_layout.addWidget(self._ui_text)
        self._ui_layout.addLayout(self._ui_buttons)

        self.setLayout(self._ui_layout)
        self.setWindowIcon(QIcon(':/icons/32.png'))
        self.setWindowTitle('Edit Cue')
        self.setMinimumSize(100, 100)
        self.setGeometry(200, 200, 250, 200)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def accept_action(self):
        """Accept entity changes"""

        self._entity.name = str(self._ui_text.toPlainText())

        self.accept()

    def reject_action(self):

        self.reject()

    def set_entity(self, entity):
        """Update edited entity information"""

        self._entity = entity

        self.setWindowTitle("Edit Cue - %s" % entity.name.split('\n')[0])
        self._ui_text.setText(entity.name)


class CuelistViewer(Viewer):
    """Library viewer

    Connected:
        '/app/close'
        '/cuelist/add'

    Emits:
        !cue/execute <message:DNAEntity>
        !cue/preview <message:DNAEntity>
    """

    id = 'cuelist'
    name = 'Cuelist'
    author = 'Grail Team'
    description = 'Manage cuelists'

    def __init__(self, *args):
        super(CuelistViewer, self).__init__(*args)

        self._locked = False
        self._cuelist_id = self.project.settings().get('cuelist/current', default=0)
        self._dialog = CuelistDialog()
        self._dialog.selected.connect(self.cuelist_selected)
        self._cuedialog = CueDialog(self)
        self._selected_id = None

        # Track project changes
        self.project.entity_changed.connect(self._update)
        self.project.entity_removed.connect(self._update)

        # Application signals
        self.connect('/app/close', self._close)
        self.connect('/cuelist/add', self._add_entity)

        self.__ui__()
        self.cuelist_selected(self._cuelist_id)

    def __ui__(self):

        self.setObjectName("CuelistViewer")

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setObjectName("CuelistViewer_layout")
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_tree = TreeWidget()
        self._ui_tree.setObjectName('CuelistViewer_tree')
        self._ui_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_tree.customContextMenuRequested.connect(self._context_menu)
        self._ui_tree.itemExpanded.connect(self.item_expanded)
        self._ui_tree.itemCollapsed.connect(self.item_collapsed)
        self._ui_tree.itemClicked.connect(self.item_clicked)
        self._ui_tree.itemDoubleClicked.connect(self.item_double_clicked)
        self._ui_tree.currentItemChanged.connect(self.item_clicked)
        self._ui_tree.keyPressEvent = self._key_event

        # Empty
        self._ui_empty_title = Label("No Cuelist")
        self._ui_empty_title.setObjectName('CuelistViewer_empty_title')

        self._ui_empty_info = Label("Cuelist not selected or there are no cuelist.")
        self._ui_empty_info.setObjectName('CuelistViewer_empty_info')
        self._ui_empty_info.setWordWrap(True)

        self._ui_empty_layout = VLayout()
        self._ui_empty_layout.setContentsMargins(12, 12, 12, 12)
        self._ui_empty_layout.setAlignment(Qt.AlignHCenter)
        self._ui_empty_layout.addWidget(Spacer())
        self._ui_empty_layout.addWidget(self._ui_empty_title)
        self._ui_empty_layout.addWidget(self._ui_empty_info)
        self._ui_empty_layout.addWidget(Spacer())

        self._ui_empty = QWidget()
        self._ui_empty.setObjectName('CuelistViewer_empty')
        self._ui_empty.setLayout(self._ui_empty_layout)

        self._ui_stack = QStackedWidget()
        self._ui_stack.addWidget(self._ui_empty)
        self._ui_stack.addWidget(self._ui_tree)
        self._ui_stack.setCurrentIndex(0)

        self._ui_label = QLabel("...")
        self._ui_label.setObjectName("CuelistViewer_label")
        self._ui_label.setAlignment(Qt.AlignCenter)
        self._ui_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._ui_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_label.mousePressEvent = lambda event: self.menu_action()

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(QIcon(':/icons/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add node', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(self._ui_label)
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout.addWidget(self._ui_stack)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def view_action(self):
        """Replace current view with something other"""

        menu = self.plugin_menu()
        menu.exec_(self._ui_toolbar.mapToGlobal(self._ui_view_action.pos()))

    def menu_action(self):
        """Open a list of all cuelists"""

        point = QPoint(self.rect().width() / 2, self.rect().height() - 16)

        self._dialog.update_list()
        self._dialog.showAt(self.mapToGlobal(point))

    def add_action(self):
        """Add new entity to current cuelist"""

        cuelist = self.project.cuelist(self._cuelist_id)

        if cuelist:
            cuelist.create("Untitled item", entity_type=DNA.TYPE_CUE)

    def item_delete(self, item):
        """Remove cue item menu_action

        Args:
            item (TreeItem): tree item
        """

        if not item:
            return False

        above = self._ui_tree.itemAbove(item)

        if above:
            self._selected_id = above.object().id

        # remove selected item
        item.object().delete()

    def item_edit(self, item):
        """Edit cue menu_action

        Args:
            item (TreeItem): tree item
        """

        if not item:
            return False

        entity = item.object()

        if entity:
            self._cuedialog.set_entity(entity)
            self._cuedialog.showWindow()

    def item_duplicate(self, item):
        """Duplicate cue menu_action

        Args:
            item (TreeItem): tree item
        """

        if not item:
            return False

        entity = item.object()
        new_entity = entity.parent.insert(entity.index + 1, entity)
        new_entity.name = entity.name + " copy"

        self._selected_id = new_entity.id
        self._update()

    def item_color(self, item, color):
        """Change cue color menu_action

        Args:
            item (TreeItem): tree item
        """

        entity = item.object()

        if isinstance(entity, CueEntity) and color in CueEntity.COLORS:
            entity.color = color

        self._update()

    def item_clicked(self, item):
        """Preview cue text

        Args:
            item (TreeItem): tree item
        """

        if not item:
            return False

        self._selected_id = item.object().id

        self.emit('!node/selected', item.object().id)
        self.emit('!cue/preview', item.object())

    def item_double_clicked(self, item):
        """Send cue text

        Args:
            item (TreeItem): tree item
        """

        if not item:
            return False

        self._selected_id = item.object().id

        self.emit('!cue/execute', item.object())

    def item_expanded(self, item):
        """Tree item expanded

        Args:
            item (TreeItem): tree item
        """

        self.item_toggle(item, True)

    def item_collapsed(self, item):
        """Tree item collapsed

        Args:
            item (TreeItem): tree item
        """

        self.item_toggle(item, False)

    def item_toggle(self, item, flag=False):
        """Change item collapsed/expanded state

        Args:
            item (TreeItem): tree item
            flag (bool): True if expanded
        """

        if not item:
            return

        item.object().set('expanded', flag)

    def cuelist_selected(self, cuelist_id=0):

        if self.is_destroyed:
            return False

        self._cuelist_id = cuelist_id
        cuelist = self.project.cuelist(cuelist_id)
        dna = self.project.dna
        selected_item = None

        if cuelist is None:
            self._ui_label.setText("...")
            self._ui_stack.setCurrentIndex(0)

            return False

        self._ui_stack.setCurrentIndex(1)
        self._ui_tree.clear()

        self.project.settings().set('cuelist/current', cuelist_id)
        self._ui_label.setText("%s <small>(%d cues)</small>" % (cuelist.name, len(cuelist)))

        def create_item(entity):
            item = TreeItem(entity)
            item.setText(0, entity.name)

            if isinstance(entity, CueEntity) and entity.color != CueEntity.COLOR_DEFAULT:
                item.setIcon(0, Icon.colored(':/icons/live.png', QColor(entity.color), QColor('#e3e3e3')))

            return item

        def add_childs(tree_item, parent_id):
            nonlocal selected_item

            for child in dna.childs(parent_id):
                child_item = create_item(child)
                add_childs(child_item, child.id)

                tree_item.addChild(child_item)
                child_item.setExpanded(bool(child.get('expanded', default=False)))

                if child.id == self._selected_id:
                    selected_item = item

        for entity in cuelist.cues():
            item = create_item(entity)

            add_childs(item, entity.id)

            self._ui_tree.addTopLevelItem(item)
            item.setExpanded(bool(entity.get('expanded', default=False)))

            if entity.id == self._selected_id:
                selected_item = item

        if selected_item:
            index = self._ui_tree.indexFromItem(selected_item)
            self._ui_tree.setCurrentIndex(index)

    def _update(self, *args):
        """Internal update"""

        self.cuelist_selected(self._cuelist_id)

    def _add_entity(self, entity):
        """Add entity to cuelist"""

        cuelist_id = self._cuelist_id
        cuelist = self.project.cuelist(cuelist_id)

        if not entity and not cuelist:
            return False

        if entity.type == DNA.TYPE_SONG:
            new_entity = cuelist.append(entity)
            new_entity.type = DNA.TYPE_CUE

            lyrics = new_entity.lyrics or ''
            pages = [re.sub(r'([\s]+?[\n\r]+)', '\n', page) for page in lyrics.replace('\r', '').split('\n\n')]

            for page in pages:
                new_entity.create(name=page, entity_type=DNA.TYPE_CUE)

            self.cuelist_selected(cuelist_id)
        elif entity.type == DNA.TYPE_VERSE:
            cuelist.create(name="%s\n%s" % (entity.text, entity.reference),
                           entity_type=DNA.TYPE_CUE)

            self.cuelist_selected(cuelist_id)

    def _context_menu(self, pos):
        """Context menu on cue item"""

        item = self._ui_tree.itemAt(pos)

        if not item:
            return False

        def create_color_action(self, index, name, menu):
            action = QAction(name, menu)
            action.triggered.connect(lambda: self.item_color(item, CueEntity.COLORS[index]))

            return action

        menu = QMenu("Context Menu", self)

        delete_action = QAction('Delete Cue', menu)
        delete_action.triggered.connect(lambda: self.item_delete(item))

        edit_action = QAction('Edit Cue', menu)
        edit_action.triggered.connect(lambda: self.item_edit(item))

        duplicate_action = QAction('Duplicate Cue', menu)
        duplicate_action.triggered.connect(lambda: self.item_duplicate(item))

        menu.addAction(edit_action)
        menu.addAction(duplicate_action)
        menu.addSeparator()

        for index, color_name in enumerate(CueEntity.COLOR_NAMES):
            menu.addAction(create_color_action(self, index, color_name, menu))

        menu.addSeparator()
        menu.addAction(delete_action)

        menu.exec_(self._ui_tree.mapToGlobal(pos))

    def _key_event(self, event):
        """Process keyboard events of Tree widget"""

        item = self._ui_tree.currentItem()
        key = event.key()

        if item:
            if key == Qt.Key_Return:
                self.item_double_clicked(item)
                return
            elif key == Qt.Key_Delete or key == Qt.Key_Backspace:
                self.item_delete(item)
                return
            elif key == Qt.Key_Up:
                self.item_clicked(item)
            elif key == Qt.Key_Down:
                self.item_clicked(item)

        # call default event handler
        QTreeWidget.keyPressEvent(self._ui_tree, event)

    def _close(self):
        """Close child dialogs"""

        self._cuedialog.close()
        self._dialog.close()


class TreeWidget(Tree):

    def __init__(self, *args):
        super(TreeWidget, self).__init__(*args)

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
