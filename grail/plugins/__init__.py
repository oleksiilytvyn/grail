# -*- coding: UTF-8 -*-
"""
    grail.plugins
    ~~~~~~~~~~~~~

    Internal plugins and configurators

    :copyright: (c) 2016-2020 by Oleksii Lytvyn (http://alexlitvin.name)
    :license: GNU, see LICENSE for more details.
"""

# configurators
from .configurators import BibleConfigurator, GeneralConfigurator
from .osc_configurators import OSCInConfigurator, OSCOutConfigurator

# viewers
from .empty_viewer import EmptyViewer

from .library_viewer import LibraryViewer
from .cuelist_viewer import CuelistViewer
from .time_viewer import TimeViewer
from .notes_viewer import NotesViewer
from .bible_viewer import BibleViewer

from .property_viewer import PropertyViewer
from .node_viewer import NodeViewer

# plugins
from .display import *
