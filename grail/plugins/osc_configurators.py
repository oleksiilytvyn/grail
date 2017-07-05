# -*- coding: UTF-8 -*-
"""
    grail.plugins.osc_configurators
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Configurators for OSC I/O
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grailkit.qt import *

from grail.core import Configurator


class OSCInConfigurator(Configurator):
    """Configure OSC input"""

    id = 'osc-in-configurator'
    name = 'OSC Input'
    index = 10
    author = 'Grail Team'
    description = 'View and configure plugins'

    # todo: implement OSC input configuration

    def __init__(self, parent=None):
        super(OSCInConfigurator, self).__init__(parent)

        self.__ui__()
        self.clicked()

    def __ui__(self):

        self._ui_label = Label("OSC Input not supported.")
        self._ui_label.setObjectName('OSCInConfigurator_title')

        self._ui_layout = VLayout()
        self._ui_layout.setContentsMargins(12, 12, 12, 12)
        self._ui_layout.setAlignment(Qt.AlignHCenter)
        self._ui_layout.addWidget(Spacer())
        self._ui_layout.addWidget(self._ui_label)
        self._ui_layout.addWidget(Spacer())

        self.setLayout(self._ui_layout)

    def clicked(self):
        pass


class OSCOutConfigurator(Configurator):
    """Configure OSC input"""

    id = 'osc-out-configurator'
    name = 'OSC Output'
    index = 11
    author = 'Grail Team'
    description = 'View and configure plugins'

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

        self._ui_list = Table()
        self._ui_list.setObjectName("OSCOutConfigurator_list")
        self._ui_list.setShowGrid(False)
        self._ui_list.setColumnCount(2)
        self._ui_list.horizontalHeader().setVisible(False)
        self._ui_list.verticalHeader().setVisible(False)
        self._ui_list.setHorizontalHeaderLabels(["Host", "Port", "Action"])
        self._ui_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._ui_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._ui_list.itemChanged.connect(self._updated)

        header = self._ui_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self._ui_clear_action = QAction(QIcon(':/icons/remove-white.png'), 'Clear', self)
        self._ui_clear_action.triggered.connect(self.clear_action)

        self._ui_add_action = QAction(QIcon(':/icons/add.png'), 'Add', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self.add_action)

        self._ui_toolbar_label = Label("0 sources")
        self._ui_toolbar_label.setObjectName("OSCOutConfigurator_label")
        self._ui_toolbar_label.setAlignment(Qt.AlignCenter)
        self._ui_toolbar_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.setObjectName("OSCOutConfigurator_toolbar")
        self._ui_toolbar.addAction(self._ui_clear_action)
        self._ui_toolbar.addWidget(self._ui_toolbar_label)
        self._ui_toolbar.addAction(self._ui_add_action)

        self._ui_layout = VLayout()
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

            host_item = TableItem(host)
            port_item = TableItem(str(port))

            self._ui_list.setItem(index, 0, host_item)
            self._ui_list.setItem(index, 1, port_item)

        self._ui_toolbar_label.setText("%d Outputs" % len(clients))
        self._do_not_update = False

    def _updated(self):

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

    def clear_action(self):
        """Remove all clients from list"""

        # Remove all clients
        self._osc_host.output.clear()

        # Remove OSC output settings
        for entity in self._osc_entity.childs():
            if entity.get('mode', default=None) == 'out':
                self._osc_entity.remove(entity)

        self._update()
