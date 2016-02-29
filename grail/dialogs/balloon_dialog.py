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
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from grail.utils import *


class BalloonDialog(QDialog):

    def __init__( self, parent=None ):

        super(BalloonDialog, self).__init__( parent )

        self.setWindowFlags( Qt.Widget | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint )
        self.setAttribute( Qt.WA_NoSystemBackground, True )
        self.setAttribute( Qt.WA_TranslucentBackground, True )

        self.installEventFilter( self )

        if not PLATFORM_MAC:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius( 12 )
            effect.setColor( QColor(0, 0, 0, 126) )
            effect.setOffset( 0 )

            self.setGraphicsEffect( effect )

        self.setContentsMargins( 12, 12, 12, 19 )

    def paintEvent( self, event ):

        roundness = 7
        side = 7

        painter = QPainter()
        painter.begin( self )
        painter.save()

        painter.setRenderHint( QPainter.Antialiasing )
        painter.setPen( Qt.NoPen )
        painter.setBrush( QColor(255, 0, 0, 127) )

        points = [QPointF( self.width() / 2, self.height() - 12 ),
                  QPointF( self.width() / 2 - side, self.height() - side - 12 ),
                  QPointF( self.width() / 2 + side, self.height() - side - 12 )]
        triangle = QPolygonF( points )

        rounded_rect = QPainterPath()
        rounded_rect.addRoundedRect( 12, 12, self.width() - 24, self.height() - side - 24, roundness, roundness )
        rounded_rect.addPolygon( triangle )

        painter.setOpacity( 1 )
        painter.fillPath( rounded_rect, QBrush( Qt.white) )

        painter.restore()
        painter.end()

    def eventFilter( self, target, event ):
        if event.type() == QEvent.WindowDeactivate:
            self.hide()

        return QObject.eventFilter( self, target, event )

    def sizeHint( self ):
        return QSize(300, 300)

    def showAt( self, point ):

        self.show()
        self.raise_()
        self.move( point.x() - self.width() / 2, point.y() - self.height() + 12 )
