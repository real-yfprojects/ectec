#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modifications to the `ectec` module to integrate into the Qt Framework.

This is mostly done by subclassing. Main modifcation include the adding of
Qt Signals and Slots.

***********************************

Created on 2021/08/17 at 14:30:24

Copyright (C) 2021 real-yfprojects (github.com user)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
from typing import Callable

from PyQt5 import QtCore


class ThreadQ(QtCore.QThread):
    def __init__(self, parent=None, target: Callable = None):
        super().__init__(parent=parent)
        self._target = target
        self.result = None

    def run(self):
        if self._target:
            self.result = self._target()

    def is_alive(self):
        return self.isRunning()


def pyqtClassSignal(*types, name):
    class ClassSignal(QtCore.QObject):

        signal = QtCore.pyqtSignal(*types, name=name)

    return ClassSignal()
