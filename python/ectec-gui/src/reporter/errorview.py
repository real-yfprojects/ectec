#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A view showing an error with traceback and logs.

***********************************

Created on 2023/02/19 at 16:17:33

Copyright (C) 2023 real-yfprojects (github.com user)

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
import traceback as traceback_formatting
from types import TracebackType
from typing import Optional, Tuple, Type

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QDialogButtonBox, QWidget

from .ui_error import Ui_dErrorDialog

#: The function that provides internationalization by translation.
_tr = QApplication.translate

ExcInfo = Tuple[Type[BaseException], BaseException, TracebackType]


class Ui_ErrorDialog(Ui_dErrorDialog):

    def setupUi(self, dErrorDialog):
        """
        Setup the form that is the GUI.

        This sets the window properties and adds the Widgets.

        Parameters
        ----------
        dErrorDialog : QtWidgets.QWidget
            The parent to add the widgets to.
        """
        super().setupUi(dErrorDialog)

        # setup dialog button box
        self.buttonBox.setStandardButtons(QDialogButtonBox.NoButton)

        self.bIgnore = self.buttonBox.addButton(QDialogButtonBox.Discard)
        self.bReport = self.buttonBox.addButton("",
                                                QDialogButtonBox.ActionRole)
        self.bReport.setIcon(QIcon.fromTheme('tools-report-bug'))
        self.bReport.setIcon(QIcon.fromTheme('tools-report-bug'))

        # set strings
        self.retranslateUi(dErrorDialog)

    def retranslateUi(self, dErrorDialog):
        """
        Retranslate the UI.

        This should update the strings and other properties regarding
        internationalization.

        Parameters
        ----------
        dErrorDialog : QtWidgets.Widgets
            The widget that contains this form.
        """
        super().retranslateUi(dErrorDialog)

        if hasattr(self, 'bIgnore'):
            self.bIgnore.setText(_tr("ErrorDialog", "Ignore"))
            self.bReport.setText(_tr("ErrorDialog", "Report"))


class ErrorView(QWidget):
    closeRequested = pyqtSignal()
    reportRequested = pyqtSignal()

    def __init__(self,
                 error_message: str,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.ui = Ui_ErrorDialog()
        self.ui.setupUi(self)

        font = QFont('monospace')    # already does the job
        font.setStyleHint(QFont.Monospace)
        self.ui.tracebackView.setFont(font)
        self.ui.logView.setFont(font)

        self.ui.lError.setText(f"<h2>{error_message}</h2>")

        self._log_provider = None
        self.ui.fLogs.hide()

        self._traceback = ''
        self.ui.fTraceback.hide()

        # =================================================================
        #
        # Connect signals.
        #
        # =================================================================

        self.ui.bCopyLogs.clicked.connect(self.copy_logs)
        self.ui.bCopyTraceback.clicked.connect(self.copy_traceback)

        self.ui.bIgnore.clicked.connect(self.closeRequested)
        self.ui.bReport.clicked.connect(self.reportRequested)

    @pyqtSlot()
    def copy_traceback(self):
        QApplication.clipboard().setText(self._traceback)

    @pyqtSlot()
    def copy_logs(self):
        # TODO retrieve logs
        QApplication.clipboard().setText('')

    @property
    def error_message(self) -> str:
        return self.ui.lError.text()

    @error_message.setter    # type: ignore
    def error_mesage(self, msg: str):
        self.ui.lError.setText(msg)

    @property
    def log_provider(self):
        return self._log_provider

    @log_provider.setter    # type: ignore
    def log_provder(self, lp):
        self._log_provider = lp
        if lp:
            # TODO update logs
            self.ui.fLogs.show()
        else:
            self.ui.logView.clear()
            self.ui.fLogs.hide()

    @property
    def traceback(self) -> str:
        return self._traceback

    @traceback.setter
    def traceback(self, tb: str):
        self._traceback = tb
        if tb:
            self.ui.tracebackView.setPlainText(tb)
            self.ui.fTraceback.show()
        else:
            self.ui.tracebackView.clear()
            self.ui.fTraceback.hide()

    @classmethod
    def from_exception(cls,
                       exc_info: ExcInfo,
                       parent: Optional[QWidget] = None) -> 'ErrorView':
        etype, e, tb_ = exc_info
        msg = traceback_formatting.format_exception_only(etype, e)[-1]
        full_tb = ''.join(traceback_formatting.format_exception(etype, e, tb_))

        error_view = ErrorView(msg, parent=parent)
        error_view.traceback = full_tb + '\n'

        return error_view


if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        dummy = [1, 2, 3]
        dummy[6]
    except IndexError:
        exc_info = sys.exc_info()

    error_dialog = ErrorView.from_exception(exc_info)    # type: ignore
    error_dialog.show()

    sys.exit(app.exec_())
