# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chattool.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets, uic


class MainWindow(QWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = uic.loadUi("chattool.ui", self)


    def changeEvent(self, event):
        super().changeEvent(event)
        if isinstance(event, QtCore.QEvent):
            ui.retranslateUi(self)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())