# -*- coding: UTF-8 -*-
"""
    grail.ui.preferences_dialog
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Global preferences dialog window and all panels displayed inside
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.ui import GDialog, GWidget, GListWidget, GListItem, GSwitch
from grailkit.ui.gapplication import AppInstance
from grailkit.util import OS_MAC
from grailkit.bible import BibleHost, BibleHostError


class PreferencesDialog(GDialog):
    """Global preferences dialog"""

    def __init__(self):
        super(PreferencesDialog, self).__init__()

        self.__ui__()

    def __ui__(self):

        self._ui_sidebar_layout = QVBoxLayout()
        self._ui_sidebar_layout.setSpacing(0)
        self._ui_sidebar_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_sidebar_list = GListWidget()
        self._ui_sidebar_list.setObjectName("preferences_tabs")
        self._ui_sidebar_list.setAlternatingRowColors(True)
        self._ui_sidebar_list.itemClicked.connect(self.page_clicked)

        self._ui_sidebar = QWidget()
        self._ui_sidebar.setLayout(self._ui_sidebar_layout)
        self._ui_sidebar_layout.addWidget(self._ui_sidebar_list)

        self._ui_panel = QStackedWidget()

        pages = [
            GeneralPanel,
            OSCInPanel,
            OSCOutPanel,
            MIDIPanel,
            BiblePanel
        ]

        for index, page in enumerate(pages):
            panel = page(self)

            item = GListItem(panel.name())
            item.index = index

            self._ui_sidebar_list.addItem(item)
            self._ui_panel.addWidget(panel)

        # splitter
        self._ui_splitter = QSplitter()
        self._ui_splitter.setObjectName("preferences_splitter")

        self._ui_splitter.addWidget(self._ui_sidebar)
        self._ui_splitter.addWidget(self._ui_panel)

        self._ui_panel.setCurrentIndex(0)

        self._ui_splitter.setCollapsible(0, False)
        self._ui_splitter.setCollapsible(1, False)
        self._ui_splitter.setHandleWidth(1)
        self._ui_splitter.setSizes([200, 400])
        self._ui_splitter.setStretchFactor(0, 0)
        self._ui_splitter.setStretchFactor(1, 1)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)
        self._ui_layout.addWidget(self._ui_splitter)

        self.setLayout(self._ui_layout)

        self.setWindowIcon(QIcon(':/icons/32.png'))
        self.setWindowTitle('Preferences')
        self.setGeometry(300, 300, 600, 400)
        self.setMinimumSize(600, 400)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def page_clicked(self, item):

        index = item.index
        panel = self._ui_panel.widget(index)

        self._ui_panel.setCurrentIndex(index)
        panel.clicked()
        panel.update()


class Panel(GWidget):

    def __init__(self, parent=None):
        super(Panel, self).__init__()

        self.__ui__()

    def __ui__(self):
        """Create all widgets"""

        pass

    def name(self):
        """Returns a panel name that will be displayed in sidebar"""

        return "panel"

    def clicked(self):
        """This method called when this panel is opened"""

        pass


class GeneralPanel(Panel):

    def __init__(self, parent=None):
        super(GeneralPanel, self).__init__(parent)

    def __ui__(self):

        self.ui_reset_btn = QPushButton("Restore")
        self.ui_reset_btn.clicked.connect(self.restore_action)
        self.ui_reset_label = QLabel("Restore Grail to it's original state")

        self.ui_import_btn = QPushButton("Import library")
        self.ui_import_btn.clicked.connect(self.import_action)
        self.ui_import_label = QLabel("Add songs from a library file.")

        self.ui_export_btn = QPushButton("Export library")
        self.ui_export_btn.clicked.connect(self.export_action)
        self.ui_export_label = QLabel("Save my library of songs to file.")

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setContentsMargins(12, 12, 12, 12)

        self.ui_layout.setSpacing(8 if OS_MAC else 0)

        self.ui_layout.addWidget(self.ui_reset_btn, 0, Qt.AlignLeft)
        self.ui_layout.addWidget(self.ui_reset_label)
        self.ui_layout.addSpacing(12)

        self.ui_layout.addWidget(self.ui_import_btn, 0, Qt.AlignLeft)
        self.ui_layout.addWidget(self.ui_import_label)
        self.ui_layout.addSpacing(12)

        self.ui_layout.addWidget(self.ui_export_btn, 0, Qt.AlignLeft)
        self.ui_layout.addWidget(self.ui_export_label)
        self.ui_layout.addSpacing(12)

        self.ui_layout.addWidget(GSwitch())
        self.ui_layout.addWidget(QLabel("Continue last project on startup"))

        self.ui_layout.addStretch()

        self.setLayout(self.ui_layout)

    def name(self):
        return "General"

    def restore_action(self):
        """Restore Grail to it's factory settings.
        This action will remove all songs and clear all preferences
        """

        # To-do: implement this
        pass

    def import_action(self):
        """Import a library of songs to grail"""

        path, ext = QFileDialog.getOpenFileName(self, "Import...", "", "*.grail-library")

        # To-do: implement this
        pass

    def export_action(self):
        """Create a library file"""

        library_name = "untitled"
        path, ext = QFileDialog.getSaveFileName(self, "Export...", library_name, "*.grail-library")

        # To-do: implement this
        pass


class BiblePanel(Panel):

    def __init__(self, parent=None):
        super(BiblePanel, self).__init__(parent)

        self._update_list()

    def name(self):
        """Returns tab name"""

        return "Bible"

    def __ui__(self):
        """Build UI"""

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_list = GListWidget()
        self._ui_list.setObjectName("bible_list")
        self._ui_list.setAlternatingRowColors(True)

        self._ui_toolbar_label = QLabel("0 installed")
        self._ui_toolbar_label.setAlignment(Qt.AlignCenter)
        self._ui_toolbar_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_install_action = QAction(QIcon(':/icons/add.png'), 'Install', self)
        self._ui_install_action.setIconVisibleInMenu(True)
        self._ui_install_action.triggered.connect(self.install_action)

        self._ui_primary_action = QAction(QIcon(':/icons/save.png'), 'Set as primary', self)
        self._ui_primary_action.setIconVisibleInMenu(True)
        self._ui_primary_action.triggered.connect(self.primary_action)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("bible_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_install_action)
        self._ui_toolbar.addWidget(self._ui_toolbar_label)
        self._ui_toolbar.addAction(self._ui_primary_action)

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def install_action(self):
        """Install new bible"""

        path, ext = QFileDialog.getOpenFileName(self, "Open File...", "", "*.grail-bible")

        try:
            BibleHost.install(path)
        except BibleHostError as msg:
            print(msg)

        self._update_list()

    def primary_action(self):
        """Make installed bible primary in grail"""

        items = self._ui_list.selectedItems()

        if len(items) > 0:
            bible_id = items[0].bible_id

            AppInstance().settings.set('bible-default', bible_id)

        self._update_list()

    def _update_list(self):
        """Update list of installed bibles"""

        bibles = BibleHost.list()
        bible_selected_id = AppInstance().settings.get('bible-default', None)

        self._ui_list.clear()
        self._ui_toolbar_label.setText("%d installed" % len(bibles))

        for key in bibles:

            bible = bibles[key]

            item = GListItem()
            item.bible_id = bible.identifier
            item.setText("%s (%s)%s" % (bible.title, bible.identifier,
                                        " - selected" if bible_selected_id == bible.identifier else ""))

            self._ui_list.addItem(item)


class OSCInPanel(Panel):

    def __init__(self, parent=None):
        super(OSCInPanel, self).__init__(parent)

    def name(self):
        return "OSC in"

    def __ui__(self):

        self._ui_label = QLabel("OSC Input not supported", self)
        self._ui_label.move(20, 20)

    def resizeEvent(self, event):

        self.update()

    def update(self):

        size = self._ui_label.size()
        box = self.size()

        self._ui_label.move(box.width() / 2 - size.width() / 2, box.height() / 2 - size.height() / 2)


class OSCOutPanel(Panel):

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super(OSCOutPanel, self).__init__(parent)

        self._port_id = 0

    def name(self):
        return "OSC out"

    def __ui__(self):

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_list = OSCOutTableWidget()
        self._ui_list.changed.connect(self._updated)

        self._ui_toolbar_label = QLabel("0 destinations")
        self._ui_toolbar_label.setAlignment(Qt.AlignCenter)
        self._ui_toolbar_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_clear_action = QAction(QIcon(':/icons/remove-white.png'), 'Remove all', self)
        self._ui_clear_action.setIconVisibleInMenu(True)
        self._ui_clear_action.triggered.connect(self.clear_action)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add destination', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar = QToolBar()
        # to-do: rename object
        self._ui_toolbar.setObjectName("bible_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_clear_action)
        self._ui_toolbar.addWidget(self._ui_toolbar_label)
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def _updated(self, items):
        """Called when list of OSC destinations changed"""

        # to-do: save changes to settings and restart OSC server

        self._ui_toolbar_label.setText("%d destinations" % (len(items),))

    def add_action(self):
        """Add new OSC output destination"""

        self._port_id += 1
        self._ui_list.addItem("127.0.0.1", 9000 + self._port_id)

    def clear_action(self):
        """Clear all destinations"""

        self._ui_list.clearItems()


class OSCOutTableWidget(QTableWidget):
    """Widget that represents OSC out destinations in a table view"""

    changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super(OSCOutTableWidget, self).__init__(parent)

        self._id = 0
        self._list = []

        self.setShowGrid(False)
        self.setColumnCount(3)
        self.setObjectName("osc_out_list")
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(["Host", "Port", "Action"])
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.itemChanged.connect(self._item_changed)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)

        self.setColumnWidth(2, 42)
        self.setAlternatingRowColors(True)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        original = self.verticalScrollBar()

        self.scrollbar = QScrollBar(Qt.Vertical, self)
        self.scrollbar.valueChanged.connect(original.setValue)

        original.valueChanged.connect(self.scrollbar.setValue)

        self._update_scrollbar()

    def paintEvent(self, event):
        """Draw widget components"""

        QTableWidget.paintEvent(self, event)

        self._update_scrollbar()

    def _update_scrollbar(self):
        """Redraw a scrollbar"""

        original = self.verticalScrollBar()

        if original.value() == original.maximum() and original.value() == 0:
            self.scrollbar.hide()
        else:
            self.scrollbar.show()

        self.scrollbar.setPageStep(original.pageStep())
        self.scrollbar.setRange(original.minimum(), original.maximum())
        self.scrollbar.resize(8, self.rect().height())
        self.scrollbar.move(self.rect().width() - 8, 0)

    def _item_changed(self, item):
        """Process item changed event"""

        column = item.column()
        text = item.text()

        self._list[item.row()][column] = text if column == 0 else int(text)

        self.changed.emit(self._list)

    def addItem(self, host="128.0.0.1", port=8000):
        """Add a new item to table"""

        self._id += 1
        self._list.append([host, port])

        index = self.rowCount()
        self.insertRow(index)

        host_item = QTableWidgetItem(str(host))
        port_item = QTableWidgetItem(str(port))

        action = OSCTableRemoveButton(self)
        action.id = self._id
        action.triggered.connect(self._remove_clicked)

        self.setItem(index, 0, host_item)
        self.setItem(index, 1, port_item)
        self.setCellWidget(index, 2, action)
        self.setCurrentCell(index, 0)
        self.editItem(host_item)

    def clearItems(self):

        self._list = []
        self.setRowCount(0)
        self.changed.emit(self._list)

    def _remove_clicked(self, action):

        for index in range(self.rowCount()):
            item = self.cellWidget(index, 2)

            if item and action.id == item.id:
                self._list.pop(index)
                self.removeRow(index)

        self.changed.emit(self._list)


class OSCTableRemoveButton(QToolButton):

    triggered = pyqtSignal("QToolButton")

    def __init__(self, parent):
        super(OSCTableRemoveButton, self).__init__(parent)

        self.setIconState(True)
        self.setMinimumSize(16, 16)
        # to-do: move qss to resources
        self.setStyleSheet("QToolButton {background: transparent;border: none;padding: 0;margin: 0;}")
        self.clicked.connect(self._clicked_event)

    def _clicked_event(self):
        """Re-route clicked event with This Button as argument"""

        self.triggered.emit(self)

    def setIconState(self, flag):
        """Set a hovered icon state by passign True"""

        self.setIcon(QIcon(':/icons/remove-white.png'))


class MIDIPanel(Panel):

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super(MIDIPanel, self).__init__(parent)

    def name(self):
        return "MIDI in"

    def __ui__(self):

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setSpacing(0)
        self._ui_layout.setContentsMargins(0, 0, 0, 0)

        self._ui_list = OSCOutTableWidget()

        self._ui_toolbar_label = QLabel("0 destinations")
        self._ui_toolbar_label.setAlignment(Qt.AlignCenter)
        self._ui_toolbar_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_clear_action = QAction(QIcon(':/icons/remove-white.png'), 'Remove all', self)
        self._ui_clear_action.setIconVisibleInMenu(True)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add destination', self)
        self._ui_add_action.setIconVisibleInMenu(True)

        self._ui_toolbar = QToolBar()
        # to-do: rename object
        self._ui_toolbar.setObjectName("bible_toolbar")
        self._ui_toolbar.setIconSize(QSize(16, 16))
        self._ui_toolbar.addAction(self._ui_clear_action)
        self._ui_toolbar.addWidget(self._ui_toolbar_label)
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)
