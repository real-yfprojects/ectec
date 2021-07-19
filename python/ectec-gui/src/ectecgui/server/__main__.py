#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run the server gui.

***********************************

Created on 2021/06/25 at 19:32:41

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

import sys

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QLocale, QTranslator
from PyQt5.QtWidgets import QApplication, QStyleFactory

from .window import MainWindow

if __name__ == "__main__":
    QApplication.setDesktopSettingsAware(True)
    app = QtWidgets.QApplication(sys.argv)

    dialog = MainWindow()
    QApplication.setStyle(QStyleFactory.create("Breeze"))

    dialog.show()

    sys.exit(app.exec_())
