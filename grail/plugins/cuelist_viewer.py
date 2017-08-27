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
        self.__ui__()

    def __ui__(self):
        """Build UI"""

        self._ui_title = LineEdit()
        self._ui_title.setPlaceholderText("Cue name")
        self._ui_title.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self._ui_artist = LineEdit()
        self._ui_artist.setPlaceholderText("Artist name")
        self._ui_artist.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self._ui_album = LineEdit()
        self._ui_album.setPlaceholderText("Album")
        self._ui_album.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self._ui_year = LineEdit()
        self._ui_year.setPlaceholderText("Year")
        self._ui_year.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self._ui_lyrics = TextEdit()
        self._ui_lyrics.setPlaceholderText("Lyrics")
        self._ui_lyrics.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self._ui_lyrics.setAcceptRichText(False)

        policy = self._ui_lyrics.sizePolicy()
        policy.setVerticalStretch(1)

        self._ui_lyrics.setSizePolicy(policy)

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

        self._ui_layout = QGridLayout()
        self._ui_layout.setSpacing(8)
        self._ui_layout.setContentsMargins(12, 12, 12, 10)
        self._ui_layout.setColumnMinimumWidth(0, 200)

        self._ui_layout.addWidget(self._ui_title, 1, 0, 1, 2)
        self._ui_layout.addWidget(self._ui_album, 3, 0, 1, 2)
        self._ui_layout.addWidget(self._ui_artist, 5, 0)
        self._ui_layout.addWidget(self._ui_year, 5, 1)
        self._ui_layout.addWidget(self._ui_lyrics, 7, 0, 1, 2)
        self._ui_layout.addLayout(self._ui_buttons, 8, 0, 1, 2)

        self.setLayout(self._ui_layout)
        self.setWindowIcon(QIcon(':/icons/32.png'))
        self.setWindowTitle('Edit Cue')
        self.setGeometry(300, 300, 300, 400)
        self.setMinimumSize(300, 400)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def accept_action(self):
        pass

    def reject_action(self):
        pass

    def set_entity(self, entity):
        """Update edited entity information"""

        pass


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

    # todo: add edit action to context menu
    # todo: add colors to context menu
    # todo: add cue edit dialog
    # todo: context menu layout - edit, duplicate, delete | colors

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
        self._ui_tree.itemSelectionChanged.connect(self._selection_changed)
        self._ui_tree.itemExpanded.connect(self._item_expanded)
        self._ui_tree.itemCollapsed.connect(self._item_collapsed)
        self._ui_tree.itemClicked.connect(self._item_clicked)
        self._ui_tree.itemDoubleClicked.connect(self._item_double_clicked)
        self._ui_tree.currentItemChanged.connect(self._item_clicked)

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

        point = QPoint(self.rect().width() / 2, self.rect().height() - 16)

        self._dialog.update_list()
        self._dialog.showAt(self.mapToGlobal(point))

    def add_action(self):
        """Add new entity"""

        self.project.cuelist(self._cuelist_id).create("Untitled item")

    def item_delete(self, item):
        """Remove cue item menu_action"""

        if not item:
            return False

        above = self._ui_tree.itemAbove(item)

        if above:
            self._selected_id = above.object().id

        # remove selected item
        item.object().delete()

    def item_edit(self, item):
        """Edit cue menu_action"""

        return False

        # entity = item.object()

        # if entity:
        #     self._cuedialog.set_entity(entity)
        #     self._cuedialog.show()
        #     self._cuedialog.raise_()

    def _update(self, *args):

        self.cuelist_selected(self._cuelist_id)

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

        def add_childs(tree_item, parent_id):
            nonlocal selected_item
            # nonlocal self

            for child in dna.childs(parent_id):
                child_item = TreeItem(child)
                child_item.setText(0, child.name)

                add_childs(child_item, child.id)

                tree_item.addChild(child_item)
                child_item.setExpanded(bool(child.get('expanded', default=False)))

                if child.id == self._selected_id:
                    selected_item = item

        for entity in cuelist.cues():
            item = TreeItem(entity)
            item.setText(0, entity.name)

            add_childs(item, entity.id)

            self._ui_tree.addTopLevelItem(item)
            item.setExpanded(bool(entity.get('expanded', default=False)))

            if entity.id == self._selected_id:
                selected_item = item

        if selected_item:
            index = self._ui_tree.indexFromItem(selected_item)
            self._ui_tree.setCurrentIndex(index)

    def _add_entity(self, entity):
        """Add entity to cuelist"""

        cuelist_id = self._cuelist_id
        cuelist = self.project.cuelist(cuelist_id)

        if not entity and not cuelist:
            return False

        if entity.type == DNA.TYPE_SONG:
            new_entity = cuelist.append(entity)
            lyrics = new_entity.lyrics or ''

            pages = [re.sub(r'([\s]+?[\n]+)', '\n', page) for page in lyrics.split('\n\n')]

            for page in pages:
                new_entity.create(name=page, entity_type=DNA.TYPE_CUE)

            self.cuelist_selected(cuelist_id)
        elif entity.type == DNA.TYPE_VERSE:
            cuelist.create(name="%s\n%s" % (entity.text, entity.reference),
                           entity_type=DNA.TYPE_CUE)

            self.cuelist_selected(cuelist_id)

    def _item_clicked(self, item):
        """Preview cue text"""

        if not item:
            return False

        self._selected_id = item.object().id

        self.emit('!node/selected', item.object().id)
        self.emit('!cue/preview', item.object())

    def _item_double_clicked(self, item):
        """Send cue text"""

        if not item:
            return False

        self._selected_id = item.object().id

        self.emit('!cue/execute', item.object())

    def _context_menu(self, pos):
        """Context menu on cue item"""

        item = self._ui_tree.itemAt(pos)

        if item:
            menu = QMenu("Context Menu", self)

            delete_action = QAction('Delete cue', menu)
            delete_action.triggered.connect(lambda: self.item_delete(item))

            edit_action = QAction('Edit cue', menu)
            edit_action.triggered.connect(lambda: self.item_edit(item))

            # menu.addAction(edit_action)
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
            item (TreeItem): tree item
        """

        item.object().set('expanded', True)

    def _item_collapsed(self, item):
        """Tree item collapsed

        Args:
            item (TreeItem): tree item
        """

        item.object().set('expanded', False)

    def _close(self):
        """Close child dialogs"""

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
