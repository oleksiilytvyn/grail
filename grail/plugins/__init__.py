# -*- coding: UTF-8 -*-
"""
    grail.plugins
    ~~~~~~~~~~~~~

    Internal plugins and configurators

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""

# configurators
from .configurators import *
from .osc_configurators import *

# viewers
from .empty_viewer import EmptyViewer

from .library_viewer import LibraryViewer
from .cuelist_viewer import CuelistViewer
from .time_viewer import TimeViewer
from .notes_viewer import NotesViewer
from .bible_viewer import BibleViewer

from .property_viewer import PropertyViewer
from .node_viewer import NodeViewer
from .console_viewer import ConsoleViewer

# plugins
from .display_plugin import DisplayPlugin
