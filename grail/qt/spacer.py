# -*- coding: UTF-8 -*-
"""
    grail.qt.spacer
    ~~~~~~~~~~~~~~~

    Transparent widget that only task to stretch components and fill space

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""

from PyQt5.QtWidgets import QSizePolicy

from grail.qt import Component


class Spacer(Component):
    """Widget that simply allocate space and spread widgets"""

    def __init__(self, policy_horizontal=QSizePolicy.Expanding, policy_vertical=QSizePolicy.Expanding, parent=None):
        """Create spacer component that allocates space and stretches another components in layout

        Args:
            policy_horizontal (QSizePolicy.Policy): horizontal space allocation rule
            policy_vertical (QSizePolicy.Policy): vertical space allocation rule
            parent (object): parent qt widget
        """
        super(Spacer, self).__init__(parent)

        self.setSizePolicy(policy_horizontal, policy_vertical)
