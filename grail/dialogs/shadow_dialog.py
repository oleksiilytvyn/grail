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
from PyQt5.QtWidgets import *

from .balloon_dialog import BalloonDialog


class ShadowDialog(BalloonDialog):

    updated = pyqtSignal("QPoint", "int", "QColor")

    def __init__(self, offset, blur, color):
        super(ShadowDialog, self).__init__(None)

        self.offset = offset
        self.blur = blur
        self.color = color

        # initialize ui components
        self.ui_color_button = QPushButton("Set Color")
        self.ui_color_button.clicked.connect(self.colorAction)

        self.ui_top = QSpinBox()
        self.ui_top.setRange(0, 100)
        self.ui_top.setValue(self.offset.y())
        self.ui_top.valueChanged.connect(self.valueChanged)

        self.ui_left = QSpinBox()
        self.ui_left.setRange(0, 100)
        self.ui_left.setValue(self.offset.x())
        self.ui_left.valueChanged.connect(self.valueChanged)

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setSpacing(0)
        self.ui_layout.setContentsMargins(0, 0, 0, 0)

        self.ui_controls_layout = QGridLayout()
        self.ui_controls_layout.setSpacing(8)
        self.ui_controls_layout.setContentsMargins(12, 12, 12, 0)

        self.ui_controls_layout.addWidget(QLabel('Top'), 0, 0)
        self.ui_controls_layout.addWidget(self.ui_top, 1, 0)

        self.ui_controls_layout.addWidget(QLabel('Left'), 0, 1)
        self.ui_controls_layout.addWidget(self.ui_left, 1, 1)

        self.ui_button_layout = QVBoxLayout()
        self.ui_button_layout.setSpacing(8)
        self.ui_button_layout.setContentsMargins(12, 12, 12, 12)

        self.ui_button_layout.addWidget(self.ui_color_button)

        top = QWidget()
        top.setLayout(self.ui_controls_layout)

        line = QWidget()
        line.setObjectName("line-divider")

        self.ui_layout.addWidget(top)
        self.ui_layout.addWidget(line)

        bottom = QWidget()
        bottom.setLayout(self.ui_button_layout)

        self.ui_layout.addWidget(bottom)

        self.setLayout(self.ui_layout)

        self.setWindowTitle('Shadow')
        self.setGeometry(100, 300, 240, 140)

    def colorAction(self):
        self.color = QColorDialog.getColor(self.color)

        self.updated.emit(self.offset, self.blur, self.color)

    def valueChanged(self, i):
        self.offset = QPoint(self.ui_left.value(), self.ui_top.value())

        self.updated.emit(self.offset, self.blur, self.color)
