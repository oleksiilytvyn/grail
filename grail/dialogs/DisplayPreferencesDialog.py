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

from grail.utils import *
from grail.data import Settings, DisplayPreferences, DisplayMode
from grail.widgets import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .CompositionDialog import CompositionDialog
from .PaddingDialog import PaddingDialog
from .ShadowDialog import ShadowDialog
from .AlignDialog import AlignDialog
from .OSCSourceDialog import OSCSourceDialog


class DisplayPreferencesDialog(QWidget):

    """Display Preferences Window"""

    updated = pyqtSignal()

    def __init__( self, parent, preferences=DisplayPreferences() ):

        super(DisplayPreferencesDialog, self).__init__( None )

        self.preferences = preferences
        self.display = parent

        self.updated.connect( self.updatedEvent )

        def composition_updated( rect ):

            self.preferences.composition = rect
            self.display.update()

        def padding_updated( margins ):

            self.preferences.padding = margins

            self.display.update()

        def shadow_updated( point, blur, color ):

            self.preferences.shadow_x = point.x()
            self.preferences.shadow_y = point.y()
            self.preferences.shadow_blur = blur
            self.preferences.shadow_color = color

            self.display.update()

        def align_updated( horizontal, vertical ):

            self.preferences.align_horizontal = horizontal
            self.preferences.align_vertical = vertical

            self.display.update()

        self.composition_dialog = CompositionDialog()
        self.composition_dialog.setCompositionGeometry( self.preferences.composition )
        self.composition_dialog.updated.connect( composition_updated )

        p = self.preferences

        self.padding_dialog = PaddingDialog( p.padding )
        self.padding_dialog.updated.connect( padding_updated )

        self.shadow_dialog = ShadowDialog( QPoint( p.shadow_x, p.shadow_y ), p.shadow_blur, p.shadow_color )
        self.shadow_dialog.updated.connect( shadow_updated )

        self.align_dialog = AlignDialog( p.align_horizontal, p.align_vertical )
        self.align_dialog.updated.connect( align_updated )

        self.initUI()

    def initUI( self ):

        self.setObjectName( "displayprefs_dialog" )
        self.setStyleSheet( get_stylesheet() )

        self.ui_transform = TransformWidget()
        self.ui_transform.setObjectName( "displayprefs_transform" )
        self.ui_transform.updated.connect( self.transformUpdated )

        # output

        self.ui_output_disabled_action = QAction('Disabled', self)
        self.ui_output_disabled_action.triggered.connect( self.disableOutput )
        self.ui_output_disabled_action.setCheckable( True )

        self.ui_output_action = QPushButton( "Output", self )

        self.ui_output_menu = QMenu( self )
        self.ui_output_action.setMenu( self.ui_output_menu )

        self.updateOutputMenu()

        # toolbar buttons

        self.ui_font_action = QToolButton( self )
        self.ui_font_action.setIcon( QIcon(':/icons/font.png') )
        self.ui_font_action.setObjectName( "displayprefs_action_font" )
        self.ui_font_action.setProperty( "left", True )
        self.ui_font_action.clicked.connect( self.fontAction )

        self.ui_shadow_action = QToolButton( self )
        self.ui_shadow_action.setIcon( QIcon(':/icons/shadow.png') )
        self.ui_shadow_action.setProperty( "middle", True )
        self.ui_shadow_action.clicked.connect( self.shadowAction )

        self.ui_align_action = QToolButton( self )
        self.ui_align_action.setIcon( QIcon(':/icons/align.png') )
        self.ui_align_action.setObjectName( "displayprefs_action_align" )
        self.ui_align_action.setProperty( "middle", True )
        self.ui_align_action.clicked.connect( self.alignAction )

        self.ui_color_action = QToolButton( self )
        self.ui_color_action.setIcon( QIcon(':/icons/color.png') )
        self.ui_color_action.setProperty( "right", True )
        self.ui_color_action.clicked.connect( self.colorAction )

        self.ui_background_action = QToolButton( self )
        self.ui_background_action.setIcon( QIcon(':/icons/color.png') )
        self.ui_background_action.setProperty( "single", True )
        self.ui_background_action.clicked.connect( self.backgroundAction )

        self.ui_composition_action = QToolButton( self )
        self.ui_composition_action.setIcon( QIcon(':/icons/zone-select.png') )
        self.ui_composition_action.setProperty( "left", True )
        self.ui_composition_action.clicked.connect( self.compositionAction )

        self.ui_padding_action = QToolButton( self )
        self.ui_padding_action.setIcon( QIcon(':/icons/selection-select.png') )
        self.ui_padding_action.setObjectName( "displayprefs_action_padding" )
        self.ui_padding_action.setProperty( "middle", True )
        self.ui_padding_action.clicked.connect( self.paddingAction )

        self.ui_testcard_action = QToolButton( self )
        self.ui_testcard_action.setIcon( QIcon(':/icons/testcard.png') )
        self.ui_testcard_action.setObjectName( "displayprefs_action_testcard" )
        self.ui_testcard_action.setProperty( "middle", True )
        self.ui_testcard_action.setCheckable( True )
        self.ui_testcard_action.clicked.connect( self.testcardAction )
        self.ui_testcard_action.setChecked( self.preferences.test )

        self.ui_paddingbox_action = QToolButton( self )
        self.ui_paddingbox_action.setIcon( QIcon(':/icons/text-padding-box.png') )
        self.ui_paddingbox_action.setObjectName( "displayprefs_action_box" )
        self.ui_paddingbox_action.setProperty( "right", True )
        self.ui_paddingbox_action.setCheckable( True )
        self.ui_paddingbox_action.clicked.connect( self.paddingboxAction )
        self.ui_paddingbox_action.setChecked( self.preferences.padding_box )

        self.ui_toolbar = QToolBar()
        self.ui_toolbar.setObjectName( "displayprefs_toolbar" )
        self.ui_toolbar.setIconSize( QSize(16, 16) )
        self.ui_toolbar.setStyle( QStyleFactory.create("windows") )

        self.ui_toolbar.addWidget( self.ui_font_action )
        self.ui_toolbar.addWidget( self.ui_shadow_action )
        self.ui_toolbar.addWidget( self.ui_align_action )
        self.ui_toolbar.addWidget( self.ui_color_action )

        self.ui_toolbar.addWidget( self.ui_background_action )

        self.ui_toolbar.addWidget( self.ui_composition_action )
        self.ui_toolbar.addWidget( self.ui_padding_action )
        self.ui_toolbar.addWidget( self.ui_testcard_action )
        self.ui_toolbar.addWidget( self.ui_paddingbox_action )

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ui_toolbar.addWidget( spacer )
        self.ui_toolbar.addWidget( self.ui_output_action )

        layout = QVBoxLayout()
        layout.setSpacing( 0 )
        layout.setContentsMargins( 0, 0, 0, 0 )

        layout.addWidget( self.ui_transform )
        layout.addWidget( self.ui_toolbar )

        self.setLayout( layout )

        self.setWindowIcon( QIcon(':/icons/32.png') )
        self.setWindowTitle( "Display Preferences" )
        self.setGeometry( 100, 100, 480, 360 )
        self.setMinimumSize( 300, 200 )

    def updatedEvent( self ):
        pass

    def actionMapToGlobal( self, action ):

        return action.mapToGlobal( action.rect().center() )

    def fontAction( self ):
        font, ok = QFontDialog.getFont( self.preferences.font )

        if ok:
            self.preferences.font = font

        self.updated.emit()

    def backgroundAction( self ):
        color = QColorDialog.getColor( self.preferences.background )

        self.preferences.background = color

        self.updated.emit()

    def paddingAction( self ):

        self.padding_dialog.showAt( self.actionMapToGlobal( self.ui_padding_action ) )

    def paddingboxAction( self ):

        self.preferences.padding_box = not self.preferences.padding_box
        self.ui_paddingbox_action.setChecked( self.preferences.padding_box )

        self.updated.emit()

    def testcardAction( self ):

        self.preferences.test = not self.preferences.test
        self.ui_testcard_action.setChecked( self.preferences.test )

        self.updated.emit()

    def shadowAction( self ):

        self.shadow_dialog.showAt( self.actionMapToGlobal( self.ui_shadow_action ) )

    def colorAction( self ):
        color = QColorDialog.getColor( self.preferences.color )

        self.preferences.color = color

        self.updated.emit()

    def compositionAction( self ):

        self.composition_dialog.showAt( self.actionMapToGlobal( self.ui_composition_action ) )

    def alignAction( self ):

        self.align_dialog.showAt( self.actionMapToGlobal( self.ui_align_action )  )

    def transformUpdated( self ):
        self.preferences.transform = self.ui_transform.getTransform()
        self.updated.emit()

    def updateTransform( self ):

        self.ui_transform.setScreen( self.preferences.geometry )
        self.ui_transform.update()

    def getPreferences( self ):
        return self.preferences

    def setPreferences( self, prefs ):
        self.preferences = prefs

    def updateOutputMenu( self ):

        self.ui_output_menu.clear()

        self.ui_output_menu.addAction( self.ui_output_disabled_action )
        self.ui_output_menu.addSeparator()

        def triggered( action ):
            return lambda item=action: self.updateOutput( action )

        current = self.display.getMode()
        flag = True

        self.ui_output_action.setText( current.name )

        for mode in self.display.getGeometryModes():

            if mode.disabled:
                continue

            if mode.name.find('Windowed') >= 0 and flag:
                self.ui_output_menu.addSeparator()
                flag = False

            action = QAction( mode.name, self )
            action.setProperty( "mode", QVariant( mode ) )
            action.triggered.connect( triggered( action ) )

            self.ui_output_menu.addAction( action )

    def disableOutput( self ):

        self.display.setDisabled( True )
        self.ui_output_disabled_action.setChecked( True )

    def updateOutput( self, action ):

        mode = action.property("mode")

        self.updateOutputMenu()
        self.display.setMode( mode )
        self.ui_output_disabled_action.setChecked( False )
        self.ui_output_action.setText( mode.name )

        self.ui_transform.setScreen( mode.geometry )
        self.ui_transform.update()

    def updateCurrentMode( self ):

        self.ui_output_action.setText( DisplayMode.getName(self.preferences) )
