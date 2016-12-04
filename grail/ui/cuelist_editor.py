# -*- coding: UTF-8 -*-
"""
    grail.ui.cuelist_editor
    ~~~~~~~~~~~~~~~~~~~~~~~

    Manage cuelist in this view
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.ui import GSpacer, GListWidget, GListItem

from grail.ui import CuelistDialog, Panel


class CuelistEditor(Panel):

    def __init__(self, app):
        super(CuelistEditor, self).__init__()

        self.app = app
        self._locked = False

        self.dialog = CuelistDialog()
        self.dialog.showAt(QPoint(500, 500))

        self.connect('/app/close', self._close)
        self.connect('/cuelist/selected', self.cuelist_selected)

        self.__ui__()

    def __ui__(self):

        self.setObjectName("cuelist")

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setObjectName("cuelist_layout")
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_list = CuelistWidget()
        self._ui_list.setObjectName("cuelist_list")
        self._ui_list.setContextMenuPolicy(Qt.CustomContextMenu)

        # self._ui_list.itemClicked.connect(self.page_clicked)
        # self._ui_list.itemDoubleClicked.connect(self.page_double_clicked)
        # self._ui_list.customContextMenuRequested.connect(self.playlist_context_menu)
        # self._ui_list.keyPressed.connect(self.playlist_key_event)
        # self._ui_list.orderChanged.connect(self.playlist_reordered)
        # self._ui_list.itemCollapsed.connect(self.playlist_item_collapsed)
        # self._ui_list.itemExpanded.connect(self.playlist_item_collapsed)

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

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def lock_action(self):

        self._locked = not self._locked
        self.app.emit("app/lock", self._locked)

    def menu_action(self):

        point = QPoint(self.rect().width() / 2, self.rect().height() - 16)

        self.dialog.update_list()
        self.dialog.showAt(self.mapToGlobal(point))

    def cuelist_selected(self, cuelist_id):

        cuelist = self.app.project.cuelist(cuelist_id)

        self._ui_label.setText("%s <small>(%d cues)</small>" % (cuelist.name, len(cuelist)))
        self._ui_list.clear()

        for cue in cuelist.cues():
            item = QTreeWidgetItem(self._ui_list, ["%s" % (cue.name, ), '2s', 'E'])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            self._ui_list.addTopLevelItem(item)

    def _close(self):
        """Close child dialogs"""

        self.dialog.close()


class CuelistWidget(QTreeWidget):

    keyPressed = pyqtSignal('QKeyEvent')
    orderChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(CuelistWidget, self).__init__(parent)

        self.header().close()
        self.setWordWrap(True)
        self.setAnimated(True)
        self.setDragEnabled(True)
        self.setSortingEnabled(False)
        self.setDropIndicatorShown(True)
        self.setAlternatingRowColors(True)
        self.viewport().setAcceptDrops(True)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        original = self.verticalScrollBar()

        self._scrollbar = QScrollBar(Qt.Vertical, self)
        self._scrollbar.valueChanged.connect(original.setValue)

        original.valueChanged.connect(self._scrollbar.setValue)

        self._update_scrollbar()

    def keyPressEvent(self, event):

        self.keyPressed.emit(event)

    def dropEvent(self, event):

        dropping_on = self.itemAt(event.pos())
        dropping_index = self.indexOfTopLevelItem(dropping_on)
        dragging_item = self.currentItem()

        # count items in list
        iterator = QTreeWidgetItemIterator(self)
        items_count = 0

        while iterator.value():
            if True: # type(iterator.value()) == SongTreeWidgetItem:
                items_count += 1

            iterator += 1

        if True: # type(dropping_on) == SongTreeWidgetItem:
            expanded = dragging_item.isExpanded()
            self.takeTopLevelItem(self.indexOfTopLevelItem(dragging_item))

            index = self.indexOfTopLevelItem(dropping_on)
            dp = self.dropIndicatorPosition()

            if dp == QAbstractItemView.BelowItem:
                index += 1

            if index == items_count:
                index -= 1

            self.insertTopLevelItem(index, dragging_item)
            self.setCurrentItem(dragging_item)

            dragging_item.setExpanded(expanded)

        self.orderChanged.emit()

    def _update_scrollbar(self):

        original = self.verticalScrollBar()

        if original.value() == original.maximum() and original.value() == 0:
            self._scrollbar.hide()
        else:
            self._scrollbar.show()

        self._scrollbar.setPageStep(original.pageStep())
        self._scrollbar.setRange(original.minimum(), original.maximum())
        self._scrollbar.resize(8, self.rect().height())
        self._scrollbar.move(self.rect().width() - 8, 0)
