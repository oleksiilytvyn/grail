#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Grail - Lyrics software. Simple.
# Copyright (C) 2014-2016 Oleksii Lytvyn
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from PyQt5.QtCore import *


class DisplayMode:

    def __init__(self, name="Untitled", geometry=QRect(0, 0, 800, 600),
                 fullscreen=True, display="none", disabled=False):
        self.name = name
        self.geometry = geometry
        self.fullscreen = fullscreen
        self.display = display
        self.disabled = disabled

    def isEqual(self, mode):
        return self.geometry == mode.geometry and self.fullscreen == mode.fullscreen

    def setName(self, name):
        self.name = name

    def setDisabled(self, flag):
        self.disabled = bool(flag)

    def setGeometry(self, geometry):
        self.geometry = geometry

    def setFullscreen(self, flag):
        self.fullscreen = bool(flag)

    def setDisplay(self, name):
        self.display = name

    def getName(self):
        data = ("Windowed" if not self.fullscreen else self.display, self.geometry.width(), self.geometry.height())

        return "Disabled" if self.disabled else "%s (%dx%d)" % data
