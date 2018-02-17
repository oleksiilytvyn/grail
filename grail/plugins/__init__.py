# -*- coding: UTF-8 -*-
"""
    grail.plugins
    ~~~~~~~~~~~~~

    Internal plugins and configurators

    :copyright: (c) 2018 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""

# configurators
from .configurators import *
from .osc_configurators import *

# viewers
from .empty_viewer import EmptyViewer
from .library_viewer import LibraryViewer
from .cuelist_viewer import CuelistViewer
from .property_viewer import PropertyViewer
from .node_viewer import NodeViewer
from .time_viewer import TimeViewer
from .notes_viewer import NotesViewer
from .console_viewer import ConsoleViewer

# plugins
from .display_plugin import DisplayPlugin
