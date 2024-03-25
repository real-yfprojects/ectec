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
from PyQt5.QtCore import pyqtSignal


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

        def connect(self,
                    slot,
                    type=QtCore.Qt.AutoConnection,
                    no_receiver_check=False):
            return self.signal.connect(slot, type, no_receiver_check)

        def emit(self, *args):
            return self.signal.emit(*args)

        def disconnect(self, slot=None):
            return self.signal.disconnect(slot)

    return ClassSignal()


def signal(*args, name=None):

    class Signal(QtCore.QObject):

        signal = pyqtSignal(*args, name=name) if name else pyqtSignal(*args)

        def connect(self,
                    slot,
                    type=QtCore.Qt.AutoConnection,
                    no_receiver_check=False):
            return self.signal.connect(slot, type, no_receiver_check)

        def emit(self, *args):
            return self.signal.emit(*args)

        def disconnect(self, slot=None):
            return self.signal.disconnect(slot)

    # descriptor class
    class SignalInstancer:

        def __init__(self, name=None) -> None:
            self.name = name if name else None

        @property
        def private_name(self):
            return '_' + self.name

        def __set_name__(self, owner, name):
            if not self.name:
                self.name = name

        def __get__(self, obj, objtype=None):
            if hasattr(obj, self.private_name):
                signal = getattr(obj, self.private_name)
            else:
                signal = Signal()
                setattr(obj, self.private_name, signal)

            return signal

    return SignalInstancer(name=name)
