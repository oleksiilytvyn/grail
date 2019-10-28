# -*- coding: UTF-8 -*-
"""
    grail.plugins.osc_configurators
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Configurators for OSC I/O

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
from grail.qt import *
from grail.core import Configurator


class OSCInConfigurator(Configurator):
    """Configure OSC input"""

    id = 'osc-in-configurator'
    name = 'OSC Input'
    index = 10
    author = 'Alex Litvin'
    description = 'Manage OSC input'

    def __init__(self, parent=None):
        super(OSCInConfigurator, self).__init__(parent)

        self._osc_host = Application.instance().osc
        self._last_port = 9000
        self._do_not_update = False
        self._project = self.app.project.dna
        self._settings = self.app.project.settings()
        self._osc_entity = self._project.entities(filter_parent=self.app.project.settings().id,
                                                  filter_keyword="OSC")

        # create osc settings entity
        if len(self._osc_entity) == 0:
            self._osc_entity = self._project.create('OSC', parent=self.app.project.settings().id)
            # send outgoing traffic
            self._osc_entity.set('osc/input', True)
            # Accept incoming traffic
            self._osc_entity.set('osc/output', True)
        else:
            self._osc_entity = self._osc_entity[0]

        # Add clients from project settings
        for entity in self._osc_entity.childs():
            if entity.get('mode', default=None) == 'in':
                self._osc_host.input.add(entity.get('host', default='127.0.0.1'),
                                         entity.get('port', default=9000))

        self.__ui__()
        self.clicked()

    def __ui__(self):

        self.setObjectName("OSCInConfigurator")

        self._ui_list = QTableWidget()
        self._ui_list.setObjectName("OSCInConfigurator_list")
        self._ui_list.setShowGrid(False)
        self._ui_list.setColumnCount(2)
        self._ui_list.horizontalHeader().setVisible(False)
        self._ui_list.verticalHeader().setVisible(False)
        self._ui_list.setHorizontalHeaderLabels(["Host", "Port"])
        self._ui_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._ui_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._ui_list.itemChanged.connect(self._updated)
        self._ui_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_list.customContextMenuRequested.connect(self._context_menu)

        header = self._ui_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self._ui_clear_action = QAction(Icon(':/rc/remove-white.png'), 'Clear', self)
        self._ui_clear_action.triggered.connect(self.clear_action)

        self._ui_add_action = QAction(Icon(':/rc/add.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar_label = QLabel("0 Inputs")
        self._ui_toolbar_label.setObjectName("OSCInConfigurator_label")
        self._ui_toolbar_label.setAlignment(Qt.AlignCenter)
        self._ui_toolbar_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("OSCInConfigurator_toolbar")
        self._ui_toolbar.addAction(self._ui_clear_action)
        self._ui_toolbar.addWidget(self._ui_toolbar_label)
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setObjectName("OSCInConfigurator_layout")
        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def _update(self):
        """Update list of clients"""

        clients = []

        for entity in self._osc_entity.childs():
            if entity.get('mode', default=None) == 'in':
                clients.append((entity.get('host', default='127.0.0.1'), entity.get('port', default=9000)))

        self._do_not_update = True
        self._ui_list.setRowCount(len(clients))

        for index, client in enumerate(clients):
            host, port = client

            host_item = QTableWidgetItem(host)
            port_item = QTableWidgetItem()
            port_item.setData(Qt.EditRole, int(port))

            self._ui_list.setItem(index, 0, host_item)
            self._ui_list.setItem(index, 1, port_item)

        self._ui_toolbar_label.setText("%d Inputs" % len(clients))
        self._do_not_update = False

    def _updated(self):
        """Update list after editing"""

        # don't update when items just added to ui table
        if self._do_not_update:
            return False

        # Remove OSC clients
        self._osc_host.input.clear()

        # Remove OSC output settings
        for entity in self._osc_entity.childs():
            if entity.get('mode', default=None) == 'in':
                self._osc_entity.remove(entity)

        for index in range(self._ui_list.rowCount()):
            host = self._ui_list.item(index, 0)
            port = self._ui_list.item(index, 1)

            if host and port:
                host = str(self._ui_list.item(index, 0).text())
                port = int(self._ui_list.item(index, 1).text())

                self._osc_host.input.add(host, port)

                entity = self._osc_entity.create('Input from %s:%d' % (host, port))
                entity.set('host', host)
                entity.set('port', port)
                entity.set('mode', 'in')
                entity.update()

    def _context_menu(self, point):
        """Create context menu"""

        position = self._ui_list.mapToGlobal(point)
        item = self._ui_list.itemAt(point)

        delete_action = QAction('Delete', self)
        delete_action.triggered.connect(lambda action: self.delete_action(item))

        add_action = QAction('Add', self)
        add_action.triggered.connect(lambda action: self.add_action())

        menu = QMenu()
        menu.addAction(delete_action)
        menu.addAction(add_action)

        menu.exec(position)

    def clicked(self):
        """Configurator page was clicked"""

        self._update()

    def add_action(self):
        """Add new OSC client"""

        self._last_port += 1
        host = '127.0.0.1'
        port = self._last_port

        # Add to OSC clients
        self._osc_host.input.add(host, port)

        # Save in settings
        entity = self._osc_entity.create('Input from %s:%d' % (host, port))
        entity.set('host', host)
        entity.set('port', port)
        entity.set('mode', 'in')
        entity.update()

        self._update()

    def delete_action(self, item):
        """Delete item"""

        self._ui_list.removeRow(item.row())
        self._updated()

    def clear_action(self):
        """Remove all clients from list"""

        # Remove all clients
        self._osc_host.input.clear()

        # Remove OSC output settings
        for entity in self._osc_entity.childs():
            if entity.get('mode', default=None) == 'in':
                self._osc_entity.remove(entity)

        self._update()


class OSCOutConfigurator(Configurator):
    """Configure OSC input"""

    id = 'osc-out-configurator'
    name = 'OSC Output'
    index = 11
    author = 'Alex Litvin'
    description = 'Manage OSC output'

    def __init__(self, parent=None):
        super(OSCOutConfigurator, self).__init__(parent)

        self._osc_host = Application.instance().osc
        self._last_port = 8000
        self._do_not_update = False
        self._project = self.app.project.dna
        self._settings = self.app.project.settings()
        self._osc_entity = self._project.entities(filter_parent=self.app.project.settings().id,
                                                  filter_keyword="OSC")

        # create osc settings entity
        if len(self._osc_entity) == 0:
            self._osc_entity = self._project.create('OSC', parent=self.app.project.settings().id)
            # send outgoing traffic
            self._osc_entity.set('osc/input', True)
            # Accept incoming traffic
            self._osc_entity.set('osc/output', True)
        else:
            self._osc_entity = self._osc_entity[0]

        # Add clients from project settings
        for entity in self._osc_entity.childs():
            if entity.get('mode', default=None) == 'out':
                self._osc_host.output.add(entity.get('host', default='127.0.0.1'),
                                          entity.get('port', default=8000))

        self.__ui__()
        self.clicked()

    def __ui__(self):

        self.setObjectName("OSCOutConfigurator")

        self._ui_list = QTableWidget()
        self._ui_list.setObjectName("OSCOutConfigurator_list")
        self._ui_list.setShowGrid(False)
        self._ui_list.setColumnCount(2)
        self._ui_list.horizontalHeader().setVisible(False)
        self._ui_list.verticalHeader().setVisible(False)
        self._ui_list.setHorizontalHeaderLabels(["Host", "Port"])
        self._ui_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._ui_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._ui_list.itemChanged.connect(self._updated)
        self._ui_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui_list.customContextMenuRequested.connect(self._context_menu)

        header = self._ui_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self._ui_clear_action = QAction(Icon(':/rc/remove-white.png'), 'Clear', self)
        self._ui_clear_action.triggered.connect(self.clear_action)

        self._ui_add_action = QAction(Icon(':/rc/add.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar_label = QLabel("0 sources")
        self._ui_toolbar_label.setObjectName("OSCOutConfigurator_label")
        self._ui_toolbar_label.setAlignment(Qt.AlignCenter)
        self._ui_toolbar_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_toolbar = QToolBar()
        self._ui_toolbar.setObjectName("OSCOutConfigurator_toolbar")
        self._ui_toolbar.addAction(self._ui_clear_action)
        self._ui_toolbar.addWidget(self._ui_toolbar_label)
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout = QVBoxLayout()
        self._ui_layout.setObjectName("OSCOutConfigurator_layout")
        self._ui_layout.addWidget(self._ui_list)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def _update(self):
        """Update list of clients"""

        clients = self._osc_host.output.clients

        self._do_not_update = True
        self._ui_list.setRowCount(len(clients))

        for index, client in enumerate(clients):
            host, port = client

            host_item = QTableWidgetItem(host)
            port_item = QTableWidgetItem()
            port_item.setData(Qt.EditRole, port)

            self._ui_list.setItem(index, 0, host_item)
            self._ui_list.setItem(index, 1, port_item)

        self._ui_toolbar_label.setText("%d Outputs" % len(clients))
        self._do_not_update = False

    def _updated(self):
        """Update list after editing"""

        # don't update when items just added to ui table
        if self._do_not_update:
            return False

        # Remove OSC clients
        self._osc_host.output.clear()

        # Remove OSC output settings
        for entity in self._osc_entity.childs():
            if entity.get('mode', default=None) == 'out':
                self._osc_entity.remove(entity)

        for index in range(self._ui_list.rowCount()):
            host = self._ui_list.item(index, 0)
            port = self._ui_list.item(index, 1)

            if host and port:
                host = str(self._ui_list.item(index, 0).text())
                port = int(self._ui_list.item(index, 1).text())

                self._osc_host.output.add(host, port)

                entity = self._osc_entity.create('Output to %s:%d' % (host, port))
                entity.set('host', host)
                entity.set('port', port)
                entity.set('mode', 'out')
                entity.update()

    def _context_menu(self, point):
        """Create context menu"""

        position = self._ui_list.mapToGlobal(point)
        item = self._ui_list.itemAt(point)

        delete_action = QAction('Delete', self)
        delete_action.triggered.connect(lambda action: self.delete_action(item))

        add_action = QAction('Add', self)
        add_action.triggered.connect(lambda action: self.add_action())

        menu = QMenu()
        menu.addAction(delete_action)
        menu.addAction(add_action)

        menu.exec(position)

    def clicked(self):
        """Configurator page was clicked"""

        self._update()

    def add_action(self):
        """Add new OSC client"""

        self._last_port += 1
        host = '127.0.0.1'
        port = self._last_port

        # Add to OSC clients
        self._osc_host.output.add(host, port)

        # Save in settings
        entity = self._osc_entity.create('Output to %s:%d' % (host, port))
        entity.set('host', host)
        entity.set('port', port)
        entity.set('mode', 'out')
        entity.update()

        self._update()

    def delete_action(self, item):
        """Delete item"""

        self._ui_list.removeRow(item.row())
        self._updated()

    def clear_action(self):
        """Remove all clients from list"""

        # Remove all clients
        self._osc_host.output.clear()

        # Remove OSC output settings
        for entity in self._osc_entity.childs():
            if entity.get('mode', default=None) == 'out':
                self._osc_entity.remove(entity)

        self._update()
