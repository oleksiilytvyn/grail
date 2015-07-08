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

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class TransformWidget(QWidget):

    updated = pyqtSignal()

    def __init__(self, parent=None):

        super(TransformWidget, self).__init__( parent )

        self.updated.connect( self.updatedEvent )
        self.setSizePolicy( QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding )
        self.setMouseTracking( True )
        self.setContextMenuPolicy( Qt.CustomContextMenu )

        self.menu = QMenu("Coverage", self)

        wholeAction = QAction('Whole area', self.menu)
        wholeAction.triggered.connect( self.wholeTransformation )

        leftAction = QAction('Left side', self.menu)
        leftAction.triggered.connect( self.leftTransformation )

        rightAction = QAction('Right side', self.menu)
        rightAction.triggered.connect( self.rightTransformation )

        centerAction = QAction('Center', self.menu)
        centerAction.triggered.connect( self.centerTransformation )

        self.menu.addAction( leftAction )
        self.menu.addAction( rightAction )
        self.menu.addAction( wholeAction )
        self.menu.addSeparator()
        self.menu.addAction( centerAction )

        self.customContextMenuRequested.connect( self.contextMenu )

        screen = QGuiApplication.screens()[0]
        self.screen = QRect(0, 0, screen.availableSize().width(), screen.availableSize().height() )
        self.points = [
            QPointF(0, 0),
            QPointF(0, 0),
            QPointF(0, 0),
            QPointF(0, 0)]
        self.wholeTransformation()

        self.mouseX = 0
        self.mouseY = 0
        self.mouseHold = False
        self.mouseHoldX = 0
        self.mouseHoldY = 0

        self.x = 0
        self.y = 0
        self.scale = 1
        self.pointIndex = -1

        self.font = QFont( "decorative", 14 )
        self.text = ""

    def contextMenu( self, event ):

        self.menu.exec_( self.mapToGlobal(event) )

    def paintEvent( self, event ):

        painter = QPainter()
        painter.begin( self )
        painter.setRenderHints( QPainter.Antialiasing | QPainter.TextAntialiasing )

        painter.fillRect( event.rect(), QColor( "#383838" ) )

        rect = event.rect()
        scale = min( rect.width() / self.screen.width(), rect.height() / self.screen.height() ) * 0.9

        w = self.screen.width() * scale
        h = self.screen.height() * scale

        x = (rect.width() - w) / 2
        y = (rect.height() - h) / 2

        self.x = x
        self.y = y
        self.scale = scale

        painter.fillRect( QRect(x, y, w, h), QColor( "#000000" ) )

        painter.setPen( QColor("#d6d6d6") )
        painter.setBrush( QColor("#111111") )

        points = []

        for point in self.points:
            points.append( self.mapToWidget( point ) )

        painter.drawPolygon( QPolygonF(points) )

        painter.setPen( QColor("#0069d9") )
        painter.setBrush( QColor("#0069d9") )

        for point in points:
            painter.drawEllipse( point, 4, 4 )

        painter.setPen( QColor("#ffffff") )
        painter.setFont( self.font )
        painter.drawText( event.rect(), Qt.AlignCenter | Qt.TextWordWrap, self.text )

        painter.end()

    def mousePressEvent( self, event ):
        self.mouseHold = True
        index = 0

        for point in self.points:
            point = self.mapToWidget( point )

            if math.sqrt( pow(point.x() - event.x(), 2) + pow(point.y() - event.y(), 2) ) <= 5:
                self.pointIndex = index
                self.mouseHoldX = event.x() - point.x()
                self.mouseHoldY = event.y() - point.y()

            index = index + 1

    def mouseReleaseEvent( self, event ):
        self.mouseHold = False
        self.pointIndex = -1

    def mouseMoveEvent( self, event ):
        self.mouseX = event.x()
        self.mouseY = event.y()

        if self.pointIndex >= 0:
            point = self.mapToScreen(QPointF( event.x() - self.x, event.y() - self.y ))

            self.text = "(%d, %d)" % ( point.x(), point.y() )
            self.points[ self.pointIndex ] = point

            self.updated.emit()
        else:
            self.text = ""

        self.update()

    def mapToWidget( self, point ):

        return QPointF( self.x + self.scale * point.x(), self.y + self.scale * point.y() )

    def mapToScreen( self, point ):

        return QPointF( point.x() * (1 / self.scale), point.y() * (1 / self.scale) )

    def centerTransformation( self ):

        w = self.screen.width()
        h = self.screen.height()
        x = 0
        y = 0

        minx = w
        miny = h
        maxx = 0
        maxy = 0

        for point in self.points:
            if point.x() < minx:
                minx = point.x()

            if point.y() < miny:
                miny = point.y()

            if point.x() > maxx:
                maxx = point.x()

            if point.y() > maxy:
                maxy = point.y()

        x = w / 2 - (maxx - minx) / 2
        y = h / 2 - (maxy - miny) / 2

        index = 0

        for point in self.points:
            point.setX( point.x() - minx + x )
            point.setY( point.y() - miny + y )

            self.points[ index ] = point
            index = index + 1

        self.updated.emit()
        self.update()

    def wholeTransformation( self ):
        """
        Fill whole screen
        """

        w = self.screen.width()
        h = self.screen.height()

        self.points[ 0 ] = QPointF( 0, 0 )
        self.points[ 1 ] = QPointF( w, 0 )
        self.points[ 2 ] = QPointF( w, h )
        self.points[ 3 ] = QPointF( 0, h )

        self.updated.emit()
        self.update()

    def leftTransformation( self ):
        """
        Fill left side of the screen
        """

        w = self.screen.width()
        h = self.screen.height()

        self.points[ 0 ] = QPointF( 0, 0 )
        self.points[ 1 ] = QPointF( w / 2, 0 )
        self.points[ 2 ] = QPointF( w / 2, h )
        self.points[ 3 ] = QPointF( 0, h )

        self.updated.emit()
        self.update()

    def rightTransformation( self ):
        """
        Fill right side
        """

        w = self.screen.width()
        h = self.screen.height()

        self.points[ 0 ] = QPointF( w / 2, 0 )
        self.points[ 1 ] = QPointF( w, 0 )
        self.points[ 2 ] = QPointF( w, h )
        self.points[ 3 ] = QPointF( w / 2, h )

        self.updated.emit()
        self.update()

    def setScreen( self, screen ):

        self.screen = screen
        self.wholeTransformation()

    def getTransform( self ):
        t = QTransform()
        p = []
        q = [
            QPointF(0, 0),
            QPointF(self.screen.width(), 0),
            QPointF(self.screen.width(), self.screen.height()),
            QPointF(0, self.screen.height())]

        for o in self.points:
            a = QPointF( o.x(), o.y() )
            p.append( a )

        QTransform.quadToQuad( QPolygonF( q ), QPolygonF( p ), t )

        return t

    def updatedEvent( self ):
        pass
