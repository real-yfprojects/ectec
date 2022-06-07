#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documentation string.

@version: 0.0

***********************************

Created on Mon Dec  7 17:53:16 2020

Copyright (C) 2020 yannick

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

import res
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import QLocale, QTranslator
from PyQt5.QtWidgets import QApplication


class MeinDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = uic.loadUi("hauptdialog.ui", self)

        self.ui.bOK.clicked.connect(self.onOK)
        self.ui.bCancel.clicked.connect(self.onCancel)

    def onOK(self):
        # Daten auslesen
        print(self.ui.eName.text())
        print(self.ui.ePrename.text())
        print(self.ui.eAddress.toPlainText())

        datum = self.ui.iBirthday.date()
        print(datum.toString("dd.MM.yyyy"))

        if self.ui.cbAGBs.checkState():
            print(QApplication.translate('MeinDialog', "AGBs akzeptiert"))
        if self.ui.cbCatalog.checkState():
            print(QApplication.translate("MeinDialog", "Katalog bestellt"))

        self.close()

    def onCancel(self):
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # app.setWindowIcon(QtGui.QIcon(':/res/icon.png'))

    locale = QLocale.system().name()
    locale = locale.split("_")[0]
    print(locale)

    qtTranslator = QTranslator()
    if qtTranslator.load("pyqt-example_" + locale, ""):
        app.installTranslator(qtTranslator)

    dialog = MeinDialog()
    dialog.show()

    sys.exit(app.exec_())
