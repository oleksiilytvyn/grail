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

import math

from grail.utils import *
from grail.data import Settings, DisplayPreferences, DisplayMode
from grail.dialogs.DisplayPreferencesDialog import DisplayPreferencesDialog

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class DisplayDialog(QMainWindow):

    """
    Display Window
    """

    modeChanged = pyqtSignal()

    def __init__( self, parent=None, preferences=DisplayPreferences() ):

        super(DisplayDialog, self).__init__( parent )

        self.text = ""
        self.preferences = preferences
        self.oldcomposition = self.preferences.composition
        self.image = None
        self.testcard = None
        self.mousePosition = None

        self.preferences_dialog = DisplayPreferencesDialog( self, self.preferences )
        self.preferences_dialog.updated.connect( self.update )

        desktop = QApplication.desktop()
        desktop.resized.connect( self.screensChanged )
        desktop.screenCountChanged.connect( self.screensChanged )
        desktop.workAreaResized.connect( self.screensChanged )

        self.initUI()

    def initUI( self ):

        self.ui_preferences_action = QAction( "Preferences", self )
        self.ui_preferences_action.triggered.connect( self.preferencesAction )

        self.ui_test_card_action = QAction( "Show Test Card", self )
        self.ui_test_card_action.triggered.connect( self.showTestCardAction )
        self.ui_test_card_action.setCheckable( True )

        self.ui_menu = QMenu("Menu", self)
        self.ui_menu.addAction( self.ui_test_card_action )
        self.ui_menu.addSeparator()
        self.ui_menu.addAction( self.ui_preferences_action )

        self.setContextMenuPolicy( Qt.CustomContextMenu )
        self.customContextMenuRequested.connect( self.contextMenu )

        if not PLATFORM_MAC:
            self.setWindowIcon( QIcon(':/icons/32.png') )

        self.setWindowTitle( "Grail Display" )
        self.setMinimumSize( 400, 300 )
        self.setWindowFlags( (Qt.Dialog if PLATFORM_MAC else Qt.Tool) |
                             Qt.FramelessWindowHint |
                             Qt.WindowSystemMenuHint |
                             Qt.WindowStaysOnTopHint )

        self.updateGeometry()

    def initOSC():
        pass

    def recievedOSC( self, pattern, value ):
        pass

    def paintEvent(self, event):

        prefs = self.preferences
        comp = prefs.composition
        output = event.rect()

        if self.oldcomposition != comp:
            self.updateTestCard()
            self.oldcomposition = comp

        painter = QPainter()
        painter.begin( self )
        painter.setRenderHints( QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform )

        painter.fillRect( output, Qt.black )

        t = QTransform()
        q = QPolygonF( [QPointF(0, 0),
                        QPointF(comp.width(), 0),
                        QPointF(comp.width(), comp.height()),
                        QPointF(0, comp.height())] )
        p = QPolygonF( [QPointF(0, 0),
                        QPointF( output.width(), 0 ),
                        QPointF( output.width(), output.height() ),
                        QPointF( 0, output.height() )] )

        QTransform.quadToQuad( QPolygonF( q ), QPolygonF( p ), t )

        world_transform = t * prefs.transform

        painter.setTransform( world_transform )

        if not prefs.test:
            painter.fillRect( comp, prefs.background )

            if self.image:
                pixSize = self.image.size()
                pixSize.scale( comp.width(), comp.height(), Qt.KeepAspectRatio )

                painter.drawPixmap( comp.width() / 2 - pixSize.width() / 2,
                                    comp.height() / 2 - pixSize.height() / 2,
                                    pixSize.width(),
                                    pixSize.height(),
                                    self.image )

            painter.setFont( prefs.font )
            painter.setPen( prefs.shadow_color )

            box = QRect( comp.topLeft(), comp.bottomRight() )
            box.adjust( prefs.padding.left(), prefs.padding.top(), -prefs.padding.right(), -prefs.padding.bottom() )
            box.setX( box.x() + prefs.shadow_x )
            box.setY( box.y() + prefs.shadow_y )

            painter.drawText( box, prefs.align_vertical | prefs.align_horizontal | Qt.TextWordWrap, self.text )

            painter.setPen( prefs.color )

            box = QRect( comp.topLeft(), comp.bottomRight() )
            box.adjust( prefs.padding.left(), prefs.padding.top(), -prefs.padding.right(), -prefs.padding.bottom() )

            painter.drawText( box, prefs.align_vertical | prefs.align_horizontal | Qt.TextWordWrap, self.text )

        # debug screen
        if prefs.test and self.testcard:
            painter.drawPixmap( comp, self.testcard )

        # padding box
        if prefs.padding_box:
            pen = QPen( Qt.red )
            pen.setWidth( 1 )

            painter.setPen( pen )

            a = prefs.padding.left()
            b = prefs.padding.top()
            c = prefs.padding.right()
            d = prefs.padding.bottom()

            painter.drawLine( a, b, comp.width() - c, b )
            painter.drawLine( a, b, a, comp.height() - d )

            painter.drawLine( comp.width() - c, b, comp.width() - c, comp.height() - d )
            painter.drawLine( a, comp.height() - d, comp.width() - c, comp.height() - d )

        painter.end()

    def resizeEvent( self, event ):

        self.preferences.setGeometry( self.geometry() )
        self.preferences_dialog.updateCurrentMode()
        self.preferences_dialog.updateTransform()
        self.modeChanged.emit()

    def moveEvent( self, event ):

        self.preferences.setGeometry( self.geometry() )
        self.preferences_dialog.updateCurrentMode()
        self.modeChanged.emit()

    def mousePressEvent( self, event ):

        self.mousePosition = event.globalPos()

    def mouseMoveEvent( self, event ):

        delta = QPoint( event.globalPos() - self.mousePosition )

        self.move( self.x() + delta.x(), self.y() + delta.y() )

        self.mousePosition = event.globalPos()

    def closeEvent( self, event ):

        self.setDisabled( True )

    def hideEvent( self, event ):

        event.ignore()

    def close( self, force=False ):

        QMainWindow.close( self )

        if force:
            self.preferences_dialog.close()

    def updateTestCard( self ):

        comp = self.preferences.composition
        image = QPixmap( comp.width(), comp.height() )

        painter = QPainter()
        painter.begin( image )
        painter.setRenderHints( QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform )

        painter.fillRect( comp, QColor("#7f7f7f") )

        pen = QPen( Qt.white )
        pen.setWidth( 1 )

        painter.setPen( pen )
        offset = 50
        lines = math.ceil(max( comp.width(), comp.height() ) / offset)

        for index in range(-lines, lines):
            o = index * offset

            painter.drawLine( 0, comp.height() / 2 + o, comp.width(), comp.height() / 2 + o )
            painter.drawLine( comp.width() / 2 + o, 0, comp.width() / 2 + o, comp.height() )

        pen = QPen( QColor("#222222") )
        pen.setWidth( 3 )
        painter.setPen( pen )

        painter.drawLine( 0, comp.height() / 2, comp.width(), comp.height() / 2 )
        painter.drawLine( comp.width() / 2, 0, comp.width() / 2, comp.height() )

        pen.setWidth( 5 )
        painter.setPen( pen )

        radius = min( comp.height(), comp.width() ) / 2
        circles = math.ceil( (comp.width() / radius) / 2 )

        for index in range(-circles, circles):
            ox = index * (radius * 1.25)

            painter.drawEllipse( QPoint( comp.width() / 2 + ox, comp.height() / 2 ), radius, radius )

        box = QRect( comp.topLeft(), comp.bottomRight() )
        box.adjust( 10, 10, -10, -10 )

        painter.setPen( Qt.white )
        painter.setFont( QFont("decorative", 24) )
        painter.drawText( box, Qt.AlignCenter | Qt.TextWordWrap,
                          "composition size %d x %d" % (comp.width(), comp.height()) )

        painter.end()

        self.testcard = image

    def screensChanged( self, item=None ):
        self.setDisabled( True )
        self.preferences_dialog.updateOutputMenu()

    def contextMenu( self, event ):

        self.ui_menu.exec_( self.mapToGlobal( event ) )

    def preferencesAction( self ):

        self.preferences_dialog.show()

    def showTestCardAction( self ):

        self.setTestCard( self.ui_test_card_action.isChecked() )

    def updateGeometry( self ):

        if self.preferences.disabled:
            self.close()
        else:
            self.setGeometry( self.preferences.geometry )
            self.updateTestCard()
            self.show()

    def setMessage( self, message ):
        self.text = message

        self.update()

    def setOutput( self, name ):

        screen_available = False

        for screen in QGuiApplication.screens():
            if name == screen.name():
                geometry = screen.availableGeometry()
                screen_available = True

                self.preferences.fullscreen = True
                self.preferences.disabled = False

        if screen_available:
            self.preferences.geometry = geometry
        elif name == "none":
            self.preferences.disabled = True

        self.updateGeometry()
        self.preferences_dialog.update()

    def setGeometryOutput( self, geometry ):

        self.preferences.disabled = False
        self.preferences.fullscreen = False
        self.preferences.geometry = geometry
        self.updateGeometry()

    def setTestCard( self, enabled ):

        self.preferences.test = enabled
        self.updateTestCard()
        self.update()

    def isTestCard( self ):

        return self.preferences.test

    def isEnabled( self ):

        return self.preferences.disabled

    def setDisabled( self, flag ):

        self.preferences.disabled = bool(flag)
        self.updateGeometry()
        self.modeChanged.emit()
        self.preferences_dialog.updateOutputMenu()

    def getPreferences( self ):

        return self.preferences

    def setPreferences( self, prefs ):

        self.preferences = prefs
        self.preferencesUpdated.emit()

    def getPreferencesDialog( self ):

        return self.preferences_dialog

    def setMode( self, mode ):

        """ Set mode """

        if mode.fullscreen:
            self.setOutput( mode.display )
        else:
            self.setGeometryOutput( mode.geometry )

        self.preferences_dialog.updateOutputMenu()

    def getMode( self ):

        """ Returns current mode """

        return self.preferences.getMode()

    def getGeometryModes( self ):

        """ Returns list of available display modes """

        modes = []
        disabled = DisplayMode( "Disabled", QRect(0, 0, 800, 600), disabled=True )

        modes.append( disabled )

        for screen in QGuiApplication.screens():
            mode = DisplayMode( screen.name() + " (%dx%d)" %
                                (screen.size().width(), screen.size().height()),
                                screen.geometry(), True, screen.name() )

            modes.append( mode )

        display = QDesktopWidget().geometry()

        for rect in [QRect(0, 0, 800, 600), QRect(0, 0, 480, 320)]:

            w = rect.width()
            h = rect.height()

            rect = QRect( display.width() / 2 - w / 2, display.height() / 2 - h / 2, w, h )

            mode = DisplayMode( "Windowed (%dx%d)" % (rect.width(), rect.height()), rect, False )

            modes.append( mode )

        return modes

    def setImage( self, path ):

        if path:
            self.image = QPixmap( path )
        else:
            self.image = None

        self.update()
