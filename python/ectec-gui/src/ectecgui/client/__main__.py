#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run the client gui.

***********************************

Created on 2021/08/16 at 14:39:21

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
from PyQt5.QtCore import (QFile, QLocale, Qt, QTextStream, QTranslator,
                          qInstallMessageHandler)
from PyQt5.QtWidgets import QApplication, QStyleFactory

from .. import logs
from .wConnect import ConnectWindow

# ---- Logging ---------------------------------------------------------------

logger = logs.getLogger()  # root logger

handler = logs.StreamHandler()
handler.setFormatter(logs.EctecGuiFormatter('UserClient'))
handler.setLevel(logs.DEBUG)
logger.addHandler(handler)

# convert Qt messages (from the qt logging system) to python LogRecords.
qInstallMessageHandler(logs.QtMessageHander(logger))

# ---- Qt App ----------------------------------------------------------------

# some global settings
QApplication.setDesktopSettingsAware(True)
QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

# icon theme
QtGui.QIcon.setFallbackThemeName('breeze')

# start app
app = QtWidgets.QApplication(sys.argv)

dialog = ConnectWindow()

dialog.show()

sys.exit(app.exec_())
