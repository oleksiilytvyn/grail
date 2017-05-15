# -*- coding: UTF-8 -*-
"""
    grail.plugins.display_plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by Oleksii Lytvyn.
    :license: GNU, see LICENSE for more details.
"""
from grail.core import Plugin


class DisplayPlugin(Plugin):
    """Viewer that shows options to open another (more useful) view"""

    # Unique plugin name string
    name = 'Display'
    # Plugin author string
    author = 'Grail Team'
    # Plugin description string
    description = 'Display 2d graphics in window or or fullscreen'

    def __init__(self):
        super(DisplayPlugin, self).__init__()

    @classmethod
    def loaded(cls):
        print('Plugin %s loaded' % cls.name)

    @classmethod
    def unloaded(cls):
        print('Plugin %s unloaded' % cls.name)
