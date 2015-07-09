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
from PyQt5.QtWidgets import *

from grail.utils import *


class AboutDialog(QDialog):

    """About Window"""

    def __init__( self, parent=None ):

        super(AboutDialog, self).__init__( parent )

        self.setObjectName( "about_dialog" )
        self.setStyleSheet( get_stylesheet() )

        picture = QLabel( self )
        picture.setGeometry( 0, 0, 450, 144 )
        picture.setPixmap( QPixmap(":/about.png") )

        copyright = QLabel( "Copyright © 2014-2015. The Grail Authors. All rights reserved.\n" +
                            "Grail application made possible by open source software and icons", self )
        copyright.move( 22, 154 )
        copyright.setObjectName( "about_copyright" )

        version = QLabel( "Version %s" % ( get_version(), ), self )
        version.move( 22, 56 )
        version.setObjectName( "about_version" )

        title = QLabel( "Grail", self )
        title.move( 22, 22 )
        title.setObjectName('about_title')

        color = QColor()
        color.setRgb( 237, 237, 237 )

        palette = QPalette()
        palette.setColor( QPalette.Background, color )
        self.setPalette( palette )

        self.setWindowFlags( Qt.WindowCloseButtonHint )

        self.setWindowIcon( QIcon(':/icons/32.png') )

        self.setWindowTitle('About Grail')
        self.setGeometry( 100, 100, 450, 200 )
        self.setFixedSize( 450, 200 )
