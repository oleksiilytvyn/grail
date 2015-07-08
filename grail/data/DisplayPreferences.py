#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Grail - Lyrics software. Simple.
# Copyright (C) 2014-2015 Oleksii Lytvyn
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
from PyQt5.QtGui import *

from .DisplayMode import DisplayMode
from .Settings import Settings


class DisplayPreferences:

    color = QColor( "#ffffff" )
    font = QFont('decorative', 28)
    background = QColor( "#000000" )

    padding = QMargins( 10, 10, 10, 10 )
    padding_box = False

    align_horizontal = Qt.AlignHCenter
    align_vertical = Qt.AlignVCenter

    shadow_x = 0
    shadow_y = 5
    shadow_blur = 0
    shadow_color = QColor( "#000000" )

    geometry = QRect( 100, 100, 800, 600 )
    transform = QTransform()
    composition = QRect( 0, 0, 800, 600 )
    fullscreen = False
    display = "none"
    disabled = True
    test = False

    def __init__( self ):

        super(DisplayPreferences, self).__init__()

    def setGeometry( self, geometry ):

        self.geometry = geometry

    def getMode( self ):

        mode = DisplayMode()
        mode.setGeometry( self.geometry )
        mode.setDisabled( self.disabled )
        mode.setFullscreen( self.fullscreen )
        mode.setDisplay( self.display )
        mode.setName( "Disabled" if self.disabled else "%s (%dx%d)" %
                      ("Windowed" if not self.fullscreen else self.display,
                       self.geometry.width(), self.geometry.height()) )

        return mode

    def applyMode( self, mode ):

        self.display = mode.display
        self.disabled = mode.disabled
        self.geometry = mode.geometry
        self.fullscreen = mode.fullscreen

    def save( self ):

        comp = self.composition
        geo = self.geometry
        padd = self.padding

        Settings.set('color', self.color.name() )
        Settings.set('background', self.background.name() )
        Settings.set('font', "%s, %d" % (self.font.family(), self.font.pointSize()) )

        Settings.set('padding', "%d, %d, %d, %d" % (padd.left(), padd.top(), padd.right(), padd.bottom()) )
        Settings.set('padding_box', self.padding_box )

        Settings.set('align_horizontal', self.align_horizontal)
        Settings.set('align_vertical', self.align_vertical)

        Settings.set('shadow_x', self.shadow_x)
        Settings.set('shadow_y', self.shadow_y)
        Settings.set('shadow_blur', self.shadow_blur)
        Settings.set('shadow_color', self.shadow_color.name())

        t = self.transform
        mm = [t.m11(), t.m12(), t.m12(), t.m21(), t.m22(), t.m23(), t.m31(), t.m32(), t.m33()]

        Settings.set('geometry', "%d, %d, %d, %d" % (geo.x(), geo.y(), geo.width(), geo.height()) )
        Settings.set('transform', ', '.join(str(x) for x in mm ) )
        Settings.set('composition', "%d, %d, %d, %d" % (comp.x(), comp.y(), comp.width(), comp.height()) )
        Settings.set('fullscreen', self.fullscreen)
        Settings.set('display', self.display)
        Settings.set('disabled', self.disabled)
        Settings.set('test', self.test)

    def restore( self ):

        color = Settings.get('color')
        if color is not None:
            self.color = QColor( color )

        background = Settings.get('background')
        if background is not None:
            self.background = QColor( background )

        font = Settings.get('font')
        if font is not None:
            value = font.split(', ')
            self.font = QFont( value[0], int(value[1]) )

        padding = Settings.get('padding')
        if padding is not None:
            values = [ int(x) for x in padding.split(', ') ]
            self.padding = QMargins( values[0], values[1], values[2], values[3] )

        padding_box = Settings.get('padding_box')
        if padding_box is not None:
            self.padding_box = padding_box == "1"

        align_horizontal = Settings.get('align_horizontal')
        if align_horizontal is not None:
            self.align_horizontal = int(align_horizontal)

        align_vertical = Settings.get('align_vertical')
        if align_vertical is not None:
            self.align_vertical = int(align_vertical)

        shadow_x = Settings.get('shadow_x')
        if shadow_x is not None:
            self.shadow_x = int(shadow_x)

        shadow_y = Settings.get('shadow_y')
        if shadow_y is not None:
            self.shadow_y = int(shadow_y)

        shadow_blur = Settings.get('shadow_blur')
        if shadow_blur is not None:
            self.shadow_blur = int(shadow_blur)

        shadow_color = Settings.get('shadow_color')
        if shadow_color is not None:
            self.shadow_color = QColor( shadow_color )

        composition = Settings.get('composition')
        if composition is not None:
            values = [ int(x) for x in composition.split(', ') ]
            self.composition = QRect( 0, 0, values[2], values[3] )

        geometry = Settings.get('geometry')
        if geometry is not None:
            values = [ int(x) for x in geometry.split(', ') ]
            self.geometry = QRect( values[0], values[1], values[2], values[3] )

        display = Settings.get('display')
        if display is not None:
            self.display = display

        fullscreen = Settings.get('fullscreen')
        if fullscreen is not None:
            self.fullscreen = fullscreen == "1"

        disabled = Settings.get('disabled')
        if disabled is not None:
            self.disabled = disabled == "1"

        test = Settings.get('test')
        if test is not None:
            self.test = test == "1"
