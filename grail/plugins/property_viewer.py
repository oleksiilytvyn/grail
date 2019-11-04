# -*- coding: UTF-8 -*-
"""
    grail.plugins.property_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Node properties viewer

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
from grail.qt import *
from grail.ui import PropertiesView
from grail.core import Viewer


class PropertyViewer(Viewer):
    """Simple property editor

    Connected:
        '!node/selected' id<int>
    Emits:

    Properties:
        follow (bool): If True viewer will show properties of selected node. Default value is True
        entity (int, None): Id of selected entity. Default value is None
        property (str, None): Key of selected property name. Default value is None
    """

    id = 'property'
    name = 'Properties'
    author = 'Alex Litvin'
    description = 'View properties of selected entities'
    single_instance = True

    def __init__(self, *args, **kwargs):
        super(PropertyViewer, self).__init__(*args, **kwargs)

        self.__ui__()

        self._updating = True
        self._entity_id = self.get('entity')
        self._property = self.get('property')
        self._follow = not self.get('follow', default=True)

        # connect signals
        self.connect('!node/selected', self._ui_properties.setEntityId)

        # update view
        self.follow_action()
        self._ui_properties.setEntityId(self._entity_id)

    def __ui__(self):
        """Create UI layout and widgets"""

        self.setObjectName("PropertyViewer")

        self._ui_properties = PropertiesView(self)
        self._ui_properties.setEntityFollow(True)

        # Action
        self._ui_follow_action = QtWidgets.QAction(Icon(':/rc/at.png'), 'Follow', self)
        self._ui_follow_action.setIconVisibleInMenu(True)
        self._ui_follow_action.triggered.connect(self.follow_action)

        self._ui_add_action = QtWidgets.QAction(Icon(':/rc/add.png'), 'Add property', self)
        self._ui_add_action.setIconVisibleInMenu(True)
        self._ui_add_action.triggered.connect(self._ui_properties.addProperty)

        self._ui_remove_action = QtWidgets.QAction(Icon(':/rc/remove-white.png'), 'Remove property', self)
        self._ui_remove_action.setIconVisibleInMenu(True)
        self._ui_remove_action.triggered.connect(self._ui_properties.removeSelected)

        self._ui_view_action = QtWidgets.QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon(':/rc/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        # Toolbar
        self._ui_toolbar = QtWidgets.QToolBar()
        self._ui_toolbar.setObjectName("PropertyViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addStretch()
        self._ui_toolbar.addAction(self._ui_follow_action)
        self._ui_toolbar.addAction(self._ui_remove_action)
        self._ui_toolbar.addAction(self._ui_add_action)

        # Layout
        self._ui_layout = QtWidgets.QVBoxLayout()

        self._ui_layout.addWidget(self._ui_properties)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def follow_action(self):
        """Toggle node follow"""

        self._follow = not self._follow

        # store property
        self.set('follow', self._follow)

        if self._follow:
            self._ui_follow_action.setIcon(Icon.colored(':/rc/at.png', QtGui.QColor('#aeca4b'), QtGui.QColor('#e3e3e3')))
        else:
            self._ui_follow_action.setIcon(Icon(':/rc/at.png'))

        self._ui_properties.setEntityFollow(self._follow)

    def view_action(self):
        """Replace current view with something else"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)
