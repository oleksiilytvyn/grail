# -*- coding: UTF-8 -*-
"""
    grail.core.executor
    ~~~~~~~~~~~~~~~~~~~

    Execute cues and keep track of execution

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import grailkit.dna as dna


class Executor:
    """Execute cues"""

    def __init__(self):

        self._current = None

    @property
    def cue(self):
        """Returns current cue or last executed one"""

        return self._current

    @property
    def cuelist(self):
        """Returns cuelist of last executed cue"""

        return self._current

    def go(self, cue):
        """Execute given cue

        Args:
            cue (grailkit.dna.Cue): cue to execute
        """

        self._current = cue

        print('Executing cue:', cue.name)

        if cue.follow == dna.CueEntity.FOLLOW_CONTINUE:
            self.go(self.next())
        elif cue.follow == dna.CueEntity.FOLLOW_ON:
            self.select(self.next())

    def select(self, cue):
        """Select cue"""

        pass

    def next(self):
        """Execute next cue in current cuelist"""

        pass

    def previous(self):
        """Execute previous cue in current cuelist"""

        pass
