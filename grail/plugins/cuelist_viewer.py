# -*- coding: UTF-8 -*-
"""
    grail.plugins.cuelist_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    View and edit cuelists

    :copyright: (c) 2016-2020 by Oleksii Lytvyn (http://alexlitvin.name)
    :license: GNU, see LICENSE for more details.
"""
import re
from functools import wraps

from grailkit.dna import DNA, CueEntity
from grailkit.osc import OSCMessage, OSCBundle

from grail.core import Viewer
from grail.ui import PropertiesView
from grail.qt import *


def guard_lock(func):
    """Prevent cuelist from editing"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """Replace original method"""

        if self._locked:
            return False
        else:
            return func(self, *args, **kwargs)

    return wrapper


class CuelistDialog(QPopup):
    """Displays list of Cuelist's"""

    selected = QtSignal(int)

    def __init__(self):
        super(CuelistDialog, self).__init__()

        self._updating_list = False
        self._app = Application.instance()

        self.__ui__()
        self.update_list()

    def __ui__(self):

        self.setBackgroundColor(QtGui.QColor("#222"))
        self.setObjectName('cuelist_dialog')

        self._ui_layout = QtWidgets.QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_list = CuelistsListWidget()
        self._ui_list.setObjectName("cuelist_dialog_list")
        self._ui_list.cellChanged.connect(self._list_cell_changed)
        self._ui_list.itemSelectionChanged.connect(self._list_item_selected)

        self._ui_edit_action = QtWidgets.QAction(Icon(':/rc/edit.png'), 'Edit', self)
        self._ui_edit_action.triggered.connect(self.edit_action)

        self._ui_add_action = QtWidgets.QAction(Icon(':/rc/add.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar = QtWidgets.QToolBar()
        self._ui_toolbar.setObjectName("cuelist_dialog_toolbar")
        self._ui_toolbar.addAction(self._ui_edit_action)
        self._ui_toolbar.addStretch()
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

            item_button = CuelistsListButton(self)
            item_button.cuelist_id = cuelist.id
            item_button.clicked.connect(self._remove_clicked)

            self._ui_list.setItem(x, 0, item)
            self._ui_list.setCellWidget(x, 1, item_button)

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


class CuelistsListItem(QtWidgets.QTableWidgetItem):
    """Playlist item inside playlist dialog"""

    def __init__(self, title):
        super(CuelistsListItem, self).__init__(title)

        self.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)


class CuelistsListButton(QtWidgets.QWidget):
    """Button widget used in list of Cuelist's"""

    clicked = QtSignal("QWidget")

    def __init__(self, parent):
        super(CuelistsListButton, self).__init__(parent)

        self._icon = QtGui.QPixmap(':/rc/remove-white.png')

    def paintEvent(self, event):
        """Draw button widget"""

        size = 18

        p = QtGui.QPainter()
        p.begin(self)

        p.drawPixmap(self.width() / 2 - size / 2, self.height() / 2 - size / 2, size, size, self._icon)

        p.end()

    def mousePressEvent(self, event):
        """Emit click event"""

        self.clicked.emit(self)


class CuelistsListWidget(QtWidgets.QTableWidget):
    """Cuelist list widget used in CuelistDialog"""

    def __init__(self, parent=None):
        """Initialize"""

        super(CuelistsListWidget, self).__init__(parent)

        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setAutoScroll(False)

        self.setColumnCount(2)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(["Label", "Button"])
        self.setShowGrid(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)

        self.setColumnWidth(1, 42)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        original = self.verticalScrollBar()

        self._scrollbar = QtWidgets.QScrollBar(QtCore.Qt.Vertical, self)
        self._scrollbar.valueChanged.connect(original.setValue)
        self._scrollbar.rangeChanged.connect(self.scroll_to_selected)

        original.valueChanged.connect(self._scrollbar.setValue)

        self._update_scrollbar()

    def paintEvent(self, event):
        """Draw widget"""

        QtWidgets.QTableWidget.paintEvent(self, event)

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


class CueDialog(QtWidgets.QDialog):
    """Cue editor dialog"""

    def __init__(self, viewer):
        super(CueDialog, self).__init__()

        self._viewer = viewer
        self._entity = None
        self._color = None
        self._follow = None

        self.follow_options = {
            "Follow": CueEntity.FOLLOW_ON,
            "Continue": CueEntity.FOLLOW_CONTINUE,
            "Don't follow": CueEntity.FOLLOW_OFF
            }

        self.__ui__()

    def __ui__(self):
        """Build UI"""

        def color_triggered(menu_action):
            """Trigger menu action"""

            return lambda: self._color_changed(menu_action.data())

        def follow_triggered(menu_action):
            """Trigger menu action"""

            return lambda: self._follow_changed(menu_action.data())

        # General section
        self._ui_text = QtWidgets.QTextEdit()
        self._ui_text.setPlaceholderText("Name")
        self._ui_text.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)
        self._ui_text.setAcceptRichText(False)
        self._ui_text.sizePolicy().setVerticalStretch(1)
        self._ui_text.setMinimumHeight(120)

        self._ui_number = QtWidgets.QLineEdit()
        self._ui_number.setPlaceholderText("Number")
        self._ui_number.setValidator(QtGui.QDoubleValidator(0, 1000, 2, self))
        self._ui_number.setMaximumWidth(80)

        self._ui_color_menu = QtWidgets.QMenu(self)

        for color, name in zip(CueEntity.COLORS, CueEntity.COLOR_NAMES):
            action = QtWidgets.QAction(name, self._ui_color_menu)
            action.setData(color)
            action.triggered.connect(color_triggered(action))

            self._ui_color_menu.addAction(action)

        self._ui_color = QtWidgets.QPushButton("")
        self._ui_color.setObjectName("CueDialog_color_btn")
        self._ui_color.setIcon(Icon(":/rc/live.png"))
        self._ui_color.setMenu(self._ui_color_menu)

        self._ui_follow_menu = QtWidgets.QMenu(self)

        for name, value in self.follow_options.items():
            action = QtWidgets.QAction(name, self._ui_follow_menu)
            action.setData(value)
            action.triggered.connect(follow_triggered(action))

            self._ui_follow_menu.addAction(action)

        self._ui_follow = QtWidgets.QPushButton("Follow")
        self._ui_follow.setObjectName("CueDialog_follow_btn")
        self._ui_follow.setMenu(self._ui_follow_menu)

        self._ui_pre_wait = QtWidgets.QLineEdit()
        self._ui_pre_wait.setValidator(QtGui.QDoubleValidator(0, 1000, 2, self))
        self._ui_pre_wait.setPlaceholderText("Pre wait")
        self._ui_pre_wait.setMaximumWidth(80)

        self._ui_post_wait = QtWidgets.QLineEdit()
        self._ui_post_wait.setValidator(QtGui.QDoubleValidator(0, 1000, 2, self))
        self._ui_post_wait.setPlaceholderText("Post wait")
        self._ui_post_wait.setMaximumWidth(80)

        self._ui_opt_layout = QtWidgets.QGridLayout()
        self._ui_opt_layout.setSpacing(6)
        self._ui_opt_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_opt_layout.addWidget(self._ui_number, 1, 0)
        self._ui_opt_layout.addWidget(QtWidgets.QLabel("Number"), 0, 0, QtCore.Qt.AlignHCenter)
        self._ui_opt_layout.addWidget(self._ui_pre_wait, 1, 1)
        self._ui_opt_layout.addWidget(QtWidgets.QLabel("Pre"), 0, 1, QtCore.Qt.AlignHCenter)
        self._ui_opt_layout.addWidget(self._ui_post_wait, 1, 2)
        self._ui_opt_layout.addWidget(QtWidgets.QLabel("Post"), 0, 2, QtCore.Qt.AlignHCenter)
        self._ui_opt_layout.setColumnStretch(3, 1)
        self._ui_opt_layout.addWidget(self._ui_color, 1, 4)
        self._ui_opt_layout.addWidget(QtWidgets.QLabel("Color"), 0, 4, QtCore.Qt.AlignHCenter)
        self._ui_opt_layout.addWidget(self._ui_follow, 1, 5)
        self._ui_opt_layout.addWidget(QtWidgets.QLabel("Execution"), 0, 5, QtCore.Qt.AlignHCenter)

        self._ui_opt_widget = QtWidgets.QWidget()
        self._ui_opt_widget.setObjectName("CueDialog_options")
        self._ui_opt_widget.setLayout(self._ui_opt_layout)

        # Properties
        self._ui_properties = PropertiesView(self)
        self._ui_properties.setEntityFollow(True)

        # Toolbar
        self._ui_add_action = QtWidgets.QAction(Icon(':/rc/add.png'), 'Add property', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self._ui_properties.addProperty)

        self._ui_remove_action = QtWidgets.QAction(Icon(':/rc/remove-white.png'), 'Remove property', self)
        self._ui_remove_action.setIconVisibleInMenu(True)
        self._ui_remove_action.triggered.connect(self._ui_properties.removeSelected)

        self._ui_done_action = QtWidgets.QPushButton('Done', self)
        self._ui_done_action.clicked.connect(self.accept_action)

        self._ui_toolbar = QtWidgets.QToolBar()
        self._ui_toolbar.setObjectName("CueDialog_toolbar")
        self._ui_toolbar.setMinimumHeight(40)
        self._ui_toolbar.addAction(self._ui_remove_action)
        self._ui_toolbar.addAction(self._ui_add_action)
        self._ui_toolbar.addStretch()
        self._ui_toolbar.addWidget(self._ui_done_action)

        # Layout
        self._ui_layout = QtWidgets.QVBoxLayout()

        self._ui_general_layout = QtWidgets.QVBoxLayout()
        self._ui_general_layout.setSpacing(8)
        self._ui_general_layout.setContentsMargins(12, 12, 12, 10)
        self._ui_general_layout.addWidget(self._ui_text)
        self._ui_general_layout.addWidget(self._ui_opt_widget)

        self._ui_general = QtWidgets.QWidget()
        self._ui_general.setObjectName("CueDialog_layout")
        self._ui_general.setLayout(self._ui_general_layout)

        self._ui_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self._ui_splitter.setHandleWidth(2)
        self._ui_splitter.addWidget(self._ui_general)
        self._ui_splitter.addWidget(self._ui_properties)
        size = self._ui_splitter.height()
        self._ui_splitter.setSizes([size * 0.2, size * 0.8])
        self._ui_splitter.setCollapsible(0, False)

        self._ui_layout.addWidget(self._ui_splitter)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)
        self.setWindowTitle('Cue Inspector')
        self.setMinimumSize(300, 400)
        self.setGeometry(200, 200, 300, 400)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

    def _follow_changed(self, value):

        self._follow = value

        self._ui_follow.setText("None")

        for key, _value in self.follow_options.items():
            if _value == value:
                self._ui_follow.setText(key)
                break

    def _color_changed(self, value):

        self._color = value

        if value:
            self._ui_color.setIcon(Icon.colored(':/rc/live.png', QtGui.QColor(value), QtGui.QColor('#e3e3e3')))
        else:
            self._ui_color.setIcon(Icon(':/rc/live.png'))

    def accept_action(self):
        """Accept entity changes"""

        self._entity.name = str(self._ui_text.toPlainText())
        self._entity.number = str(self._ui_number.text())
        self._entity.pre_wait = float(self._ui_pre_wait.text())
        self._entity.post_wait = float(self._ui_post_wait.text())

        if self._color:
            self._entity.color = self._color

        if self._follow in CueEntity.FOLLOW_TYPE:
            self._entity.follow = self._follow

        self.accept()

    def reject_action(self):
        """Cancel editing of entity"""

        self.reject()

    def set_entity(self, entity):
        """Update edited entity information"""

        self._entity = entity
        self._ui_properties.setEntity(entity)

        # Update UI
        self.setWindowTitle("Cue Inspector - %s" % entity.name.split('\n')[0])
        self._ui_text.setText(entity.name)
        self._ui_number.setText(str(entity.number))
        self._ui_pre_wait.setText(str(entity.pre_wait))
        self._ui_post_wait.setText(str(entity.post_wait))

        self._color_changed(entity.color)
        self._follow_changed(entity.follow)


class CuelistViewer(Viewer):
    """Library viewer

    Connected:
        '/app/close'
        '/cuelist/add'

    Emits:
        !cue/preview <message:DNAEntity>
    """

    id = 'cuelist'
    name = 'Cuelist'
    author = 'Oleksii Lytvyn'
    description = 'Manage cuelists'
    single_instance = True

    def __init__(self, *args):
        super(CuelistViewer, self).__init__(*args)

        self._locked = False
        self._cuelist_id = self.project.settings().get('cuelist/current', default=0)
        self._dialog = CuelistDialog()
        self._dialog.selected.connect(self.cuelist_selected)
        self._cuedialog = CueDialog(self)
        self._selected_id = None
        self._update_lock = False

        self._cue_timer = QtCore.QTimer()
        self._cue_timer.setSingleShot(True)
        self._cue_timer.timeout.connect(self._cue_timer_execute)

        # Track project changes
        self.project.entity_changed.connect(self._update_changed)
        self.project.entity_removed.connect(self._update_removed)
        self.project.property_changed.connect(self._update_property)

        # Application signals
        self.app.signals.connect('/app/close', self._close)
        self.app.signals.connect('/cuelist/add', self._add_entity)

        self.__ui__()
        self.cuelist_selected(self._cuelist_id)

    def __ui__(self):

        self.setObjectName("CuelistViewer")

        self._ui_layout = QtWidgets.QVBoxLayout()
        self._ui_layout.setObjectName("CuelistViewer_layout")
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_tree = TreeWidget()
        self._ui_tree.setObjectName('CuelistViewer_tree')
        self._ui_tree.setHeaderHidden(True)
        self._ui_tree.setHeaderLabels(['Number', 'Name'])

        self._ui_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._ui_tree.customContextMenuRequested.connect(self._context_menu)
        self._ui_tree.itemExpanded.connect(self.item_expanded)
        self._ui_tree.itemCollapsed.connect(self.item_collapsed)
        self._ui_tree.itemClicked.connect(self.item_clicked)
        self._ui_tree.itemDoubleClicked.connect(self.item_double_clicked)
        self._ui_tree.currentItemChanged.connect(self.item_clicked)
        self._ui_tree.keyPressEvent = self._key_event

        # Empty
        self._ui_empty_title = QtWidgets.QLabel("No Cuelist")
        self._ui_empty_title.setObjectName('CuelistViewer_empty_title')

        self._ui_empty_info = QtWidgets.QLabel("Cuelist not selected or there are no cuelist.")
        self._ui_empty_info.setObjectName('CuelistViewer_empty_info')
        self._ui_empty_info.setWordWrap(True)

        self._ui_empty_layout = QtWidgets.QVBoxLayout()
        self._ui_empty_layout.setContentsMargins(12, 12, 12, 12)
        self._ui_empty_layout.setAlignment(QtCore.Qt.AlignHCenter)
        self._ui_empty_layout.addStretch()
        self._ui_empty_layout.addWidget(self._ui_empty_title)
        self._ui_empty_layout.addWidget(self._ui_empty_info)
        self._ui_empty_layout.addStretch()

        self._ui_empty = QtWidgets.QWidget()
        self._ui_empty.setObjectName('CuelistViewer_empty')
        self._ui_empty.setLayout(self._ui_empty_layout)

        self._ui_stack = QtWidgets.QStackedWidget()
        self._ui_stack.addWidget(self._ui_empty)
        self._ui_stack.addWidget(self._ui_tree)
        self._ui_stack.setCurrentIndex(0)

        self._ui_label = QtWidgets.QLabel("...")
        self._ui_label.setObjectName("CuelistViewer_label")
        self._ui_label.setAlignment(QtCore.Qt.AlignCenter)
        self._ui_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self._ui_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._ui_label.mousePressEvent = lambda event: self.menu_action()

        self._ui_view_action = QtWidgets.QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon(':/rc/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_lock_action = QtWidgets.QAction(Icon(':/rc/unlock.png'), 'Lock cuelist', self)
        self._ui_lock_action.setIconVisibleInMenu(True)
        self._ui_lock_action.triggered.connect(self.lock_action)

        self._ui_add_action = QtWidgets.QAction(Icon(':/rc/add.png'), 'Add new Cue', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar = QtWidgets.QToolBar()
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(self._ui_label)
        self._ui_toolbar.addAction(self._ui_lock_action)
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout.addWidget(self._ui_stack)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def menu_action(self):
        """Open a list of all cuelists"""

        point = QtCore.QPoint(self.rect().width() / 2, self.rect().height() - 16)

        self._dialog.update_list()
        self._dialog.showAt(self.mapToGlobal(point))

    def lock_action(self):
        """Lock & unlock cuelist edit"""

        self._locked = not self._locked

        if self._locked:
            self._ui_lock_action.setIcon(
                Icon.colored(':/rc/lock.png', QtGui.QColor('#aeca4b'), QtGui.QColor('#e3e3e3')))
        else:
            self._ui_lock_action.setIcon(QtGui.QIcon(':/rc/unlock.png'))

        self._ui_tree.setDragEnabled(not self._locked)

    @guard_lock
    def add_action(self, *_):
        """Add new entity to current cuelist"""

        cuelist = self.project.cuelist(self._cuelist_id)

        if cuelist:
            cuelist.create("Untitled item", entity_type=DNA.TYPE_CUE)

    @guard_lock
    def item_delete(self, item):
        """Remove cue item menu_action

        Args:
            item (QTreeWidgetItem): tree item
        """

        if not item:
            return False

        above = self._ui_tree.itemAbove(item)

        if above:
            self._selected_id = above.object().id

        self._update_lock = True

        # remove selected item
        item.object().delete()

        self._update_lock = False
        self._update()

    @guard_lock
    def item_edit(self, item):
        """Edit cue menu_action

        Args:
            item (QTreeWidgetItem): tree item
        """

        if not item:
            return False

        entity = item.object()

        if entity:
            self._cuedialog.set_entity(entity)
            self._cuedialog.showWindow()

    @guard_lock
    def item_duplicate(self, item):
        """Duplicate cue menu_action

        Args:
            item (QTreeWidgetItem): tree item
        """

        if not item:
            return False

        entity = item.object()
        new_entity = entity.parent.insert(entity.index + 1, entity)

        match = re.match('^([sw]+)copy( ([d]+))?$', new_entity.name, re.MULTILINE | re.IGNORECASE)

        if match:
            name = match.group(1)

            if not match.group(3):
                name += 'copy 2'
            else:
                name += 'copy %d' % (int(match.group(3)) + 1)

            new_entity.name = name
        else:
            new_entity.name = entity.name + " copy"

        self._selected_id = new_entity.id

    @guard_lock
    def item_color(self, item, color):
        """Change cue color menu_action

        Args:
            item (QTreeWidgetItem): tree item
            color (int): cue color constant
        """

        entity = item.object()
        self._selected_id = entity.id

        if isinstance(entity, CueEntity) and color in CueEntity.COLORS:
            entity.color = color

    def item_clicked(self, item):
        """Preview cue text

        Args:
            item (QTreeWidgetItem): tree item
        """

        if not item:
            return False

        self._selected_id = item.object().id

        self.emit_signal('!node/selected', item.object().id)
        self.emit_signal('!cue/preview', item.object())

    def item_double_clicked(self, item):
        """Send cue text

        Args:
            item (QTreeWidgetItem): tree item
        """

        if not item:
            return False

        self._selected_id = item.object().id

        self._cue_execute(item.object())

    def item_expanded(self, item):
        """Tree item expanded

        Args:
            item (QTreeWidgetItem): tree item
        """

        self.item_toggle(item, True)

    def item_collapsed(self, item):
        """Tree item collapsed

        Args:
            item (QTreeWidgetItem): tree item
        """

        self.item_toggle(item, False)

    def item_toggle(self, item, flag=False):
        """Change item collapsed/expanded state

        Args:
            item (QTreeWidgetItem): tree item
            flag (bool): True if expanded
        """

        if not item:
            return

        item.object().set('expanded', flag)

    def cuelist_selected(self, cuelist_id=0):
        """Open cuelist in viewer

        Args:
            cuelist_id (int): cuelist id
        """

        if self.is_destroyed or self._update_lock:
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

        def create_item(_entity):
            """Create tree item from entity"""

            name = _entity.name

            _item = QtWidgets.QTreeWidgetItem(_entity)
            # todo: Add number to song entity or add CueEntity instead
            _item.setText(0, str(_entity.number) if hasattr(_entity, 'number') else "")
            _item.setText(1, name if len(name) < 50 else "%s..." % name[:50])

            if isinstance(_entity, CueEntity):
                if _entity.color != CueEntity.COLOR_DEFAULT:
                    bg = QtGui.QBrush(QtGui.QColor(_entity.color))
                    fg = QtGui.QBrush(QtGui.QColor("#222" if _entity.color == CueEntity.COLOR_YELLOW else "#fff"))

                    _item.setBackground(0, bg)
                    _item.setForeground(0, fg)
                    _item.setBackground(1, bg)
                    _item.setForeground(1, fg)

                if _entity.follow == CueEntity.FOLLOW_OFF:
                    _item.setIcon(0, Icon(':/rc/follow-off.png'))
                elif _entity.follow == CueEntity.FOLLOW_ON:
                    _item.setIcon(0, Icon(':/rc/follow-on.png'))
                elif _entity.follow == CueEntity.FOLLOW_CONTINUE:
                    _item.setIcon(0, Icon(':/rc/follow-cont.png'))

            return _item

        def add_childs(tree_item, parent_id):
            """Add childs to tree item"""

            nonlocal selected_item
            nonlocal self

            for child in dna.childs(parent_id):
                child_item = create_item(child)
                add_childs(child_item, child.id)

                tree_item.addChild(child_item)
                child_item.setExpanded(bool(child.get('expanded', default=False)))

                if child.id == self._selected_id:
                    selected_item = child_item

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

    def _update(self, *_):
        """Internal update"""

        if not self._update_lock:
            self.cuelist_selected(self._cuelist_id)

    def _cue_contains(self, entity_id):

        if entity_id == self._cuelist_id:
            return True

        return self.project.dna.contains(self._cuelist_id, entity_id)

    def _update_changed(self, entity_id):

        if self._cue_contains(entity_id):
            self._update()

    def _update_removed(self, entity_id):

        if self._cue_contains(entity_id):
            self._update()

    def _update_property(self, entity_id, key, value):
        """Update list when cue's properties changed"""

        if key == 'color' or key == 'follow':
            self._update()

    @guard_lock
    def _add_entity(self, entity):
        """Add entity to cuelist"""

        self._update_lock = True

        cuelist_id = self._cuelist_id
        cuelist = self.project.cuelist(cuelist_id)

        if not entity or not cuelist:
            return False

        if entity.type == DNA.TYPE_SONG:
            new_entity = cuelist.append(entity)
            new_entity.type = DNA.TYPE_CUE

            lyrics = new_entity.lyrics or ''
            pages = [re.sub(r'([\s]+?[\n\r]+)', '\n', page) for page in lyrics.replace('\r', '').split('\n\n')]

            for page in pages:
                new_entity.create(name=page, entity_type=DNA.TYPE_CUE)
        elif entity.type == DNA.TYPE_VERSE:
            cuelist.create(name="%s\n%s" % (entity.text, entity.reference),
                           entity_type=DNA.TYPE_CUE)

        self._update_lock = False
        self._update()

    def _context_menu(self, pos):
        """Context menu on cue item"""

        item = self._ui_tree.itemAt(pos)

        if not item:
            return False

        def create_color_action(this, action_index, name, menu_ref):
            """Create, connect and return QAction."""

            action = QtWidgets.QAction(name, menu_ref)
            action.triggered.connect(lambda: this.item_color(item, CueEntity.COLORS[action_index]))

            return action

        menu = QtWidgets.QMenu("Context Menu", self)

        delete_action = QtWidgets.QAction('Delete Cue', menu)
        delete_action.triggered.connect(lambda: self.item_delete(item))

        edit_action = QtWidgets.QAction('Edit Cue', menu)
        edit_action.triggered.connect(lambda: self.item_edit(item))

        duplicate_action = QtWidgets.QAction('Duplicate Cue', menu)
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
            if key == QtCore.Qt.Key_Return:
                self.item_double_clicked(item)
                return
            elif key == QtCore.Qt.Key_Delete or key == QtCore.Qt.Key_Backspace:
                self.item_delete(item)
                return
            elif key == QtCore.Qt.Key_Up:
                self.item_clicked(item)
            elif key == QtCore.Qt.Key_Down:
                self.item_clicked(item)

        # call default event handler
        QtWidgets.QTreeWidget.keyPressEvent(self._ui_tree, event)

    def _cue_timer_execute(self):

        cue = self._cue_timer.cue

        self.emit_signal('!cue/execute', cue)
        self._osc_execute(cue)

        # Do not execute next cue
        if hasattr(cue, 'follow') and cue.follow == CueEntity.FOLLOW_OFF:
            return False

        next_cue = None

        # go inside cue
        if cue.has_childs():
            next_cue = cue.childs()[0]
        # find cue beside or in parents
        else:
            traverse_cond = True
            traverse_cue = cue

            while traverse_cond:
                parent_cues = self.project.dna.childs(traverse_cue.parent_id)
                index = 0

                # find next cue in parent list
                for item in parent_cues:
                    index += 1

                    if item.id == traverse_cue.id and index < len(parent_cues):
                        next_cue = parent_cues[index]
                        traverse_cond = False

                        break

                # find in parent list
                if index == len(parent_cues):
                    traverse_cue = traverse_cue.parent

        # Execute next cue
        if next_cue and cue.follow == CueEntity.FOLLOW_CONTINUE:
            # post wait
            self._cue_execute(next_cue, cue.post_wait)

    def _cue_execute(self, cue=None, wait=0):
        """Execute cue"""

        if not cue:
            return False

        self._selected_id = cue.id

        pause = 0

        if hasattr(cue, "pre_wait"):
            pause = (cue.pre_wait + wait) * 1000

        # pre wait
        self._cue_timer.cue = cue
        self._cue_timer.stop()
        self._cue_timer.start(pause)

        # update list show what is currently running
        self._update()

    def _osc_execute(self, cue):
        """Execute cue and send OSC bundle

        Send bundle with all valid OSC properties + entity info
        """

        bundle = OSCBundle()
        bundle.add(OSCMessage(address='/cue/id', args=[cue.id]))
        bundle.add(OSCMessage(address='/cue/type', args=[cue.type]))
        bundle.add(OSCMessage(address='/cue/parent', args=[cue.parent]))

        name = OSCMessage(address='/cue/name')
        # Blob value cannot be empty, so we replace it with one space
        name.add(bytes(cue.name if len(cue.name) > 0 else " ", 'utf-8'))
        bundle.add(name)

        for key, value in cue.properties().items():
            # check if property name is valid OSC address pattern
            if not OSCMessage.is_valid_address(key):
                continue

            bundle.add(OSCMessage(address=key, args=[value]))

        osc_out = self.app.osc.output
        osc_out.send(bundle)

    def _close(self):
        """Close child dialogs"""

        self._cuedialog.close()
        self._dialog.close()


class TreeWidget(QtWidgets.QTreeWidget):
    """Tree widget used in CuelistViewer"""

    def __init__(self, *args):
        super(TreeWidget, self).__init__(*args)

    def dropEvent(self, event):
        """Validate item while dropping"""

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
        if drop_indicator == QtWidgets.QAbstractItemView.AboveItem:
            dragging.object().index = dropping.object().index - 1
        # something when being below an item
        elif drop_indicator == QtWidgets.QAbstractItemView.BelowItem:
            dragging.object().index = dropping.object().index + 1
        # you're on an item, maybe add the current one as a child
        elif drop_indicator == QtWidgets.QAbstractItemView.OnItem:
            dragging.object().parent_id = dropping.object().id
        # you are not on your tree
        elif drop_indicator == QtWidgets.QAbstractItemView.OnViewport:
            pass

        QtWidgets.QTreeWidget.dropEvent(self, event)
