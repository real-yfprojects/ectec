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

from PyQt5.QtCore import QMimeData, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QDialogButtonBox, QWidget
from reporter.logprovider import (AbstractLogProvider, DictionaryLogProvider,
                                  IsHtmlRole, LogRole)

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
    """
    A Widget that can be loaded into a dialog telling the user about an error.

    The widget features a QDialogButtonBox with two buttons: `Ignore` and
    `Report Bug`. When the former is clicked the widget should be hidden/the
    dialog should be closed. When the latter is clicked, the dialog should
    transition to a reporting the error.

    Parameters
    ----------
    error_message : str
        the title to display
    parent : Optional[QWidget], optional
        parent widget, by default None

    Attributes
    ----------
    closeRequested : pyqtSignal
        the user clicked the `Ignore` button.
    reportRequested : pyqtSignal
        the user clicked the `Report Bug` button.
    error_message : str
        The error title to display.
    log_provider : AbstractLogProvider
        The error message shown as a title of the dialog.
    modelRow : int
        The row of the log provide to use the logs from.

    Methods
    -------
    copy_traceback
        Copy the traceback set to the clipboard.
    copy_logs
        Copy the logs displayed to the clipboard.
    refreshLogs
        Refresh the logs displayed.

    Staticmethods
    -------------
    from_exception
        Init an errorview from an exception.
    """

    closeRequested = pyqtSignal()
    reportRequested = pyqtSignal()

    def __init__(self,
                 error_message: str,
                 parent: Optional[QWidget] = None) -> None:
        """
        Init.

        Parameters
        ----------
        error_message : str
            the title to display
        parent : Optional[QWidget], optional
            parent widget, by default None
        """
        super().__init__(parent)

        self.ui = Ui_ErrorDialog()
        self.ui.setupUi(self)

        font = QFont('monospace')    # already does the job
        font.setStyleHint(QFont.Monospace)
        self.ui.tracebackView.setFont(font)
        self.ui.logView.setFont(font)

        self.error_message = error_message    # does the formatting

        self._log_provider: Optional[AbstractLogProvider] = None
        self._row = 0
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
        """
        Copy the traceback set to the clipboard.
        """
        QApplication.clipboard().setText(self._traceback)

    @pyqtSlot()
    def copy_logs(self):
        """
        Copy the logs displayed to the clipboard.
        """
        data = QMimeData()
        data.setHtml(self.ui.logView.toHtml())
        data.setText(self.ui.logView.toPlainText())
        QApplication.clipboard().setMimeData(data)

    @property
    def error_message(self) -> str:
        """
        The error message shown as a title of the dialog.

        When set the message will automatically be surrounded by `<h2>` tags.
        """
        return self.ui.lError.text().lstrip("<h2>").rstrip("</h2>")

    @error_message.setter
    def error_message(self, msg: str):
        self.ui.lError.setText(f"<h2>{msg}</h2>")

    @property
    def log_provider(self) -> Optional[AbstractLogProvider]:
        """
        The log provider to retrieve the displayed logs from

        The row of the currently displayed log can be specified through
        `modelRow`.

        See Also
        --------
        modelRow : the row for the log provider used.
        """
        return self._log_provider

    @log_provider.setter
    def log_provider(self, lp: Optional[AbstractLogProvider]):
        if self._log_provider:
            self._log_provider.dataChanged.disconnect(self.refreshLogs)
        if lp:
            lp.dataChanged.connect(self.refreshLogs)
        self._log_provider = lp
        self.refreshLogs()

    @property
    def modelRow(self) -> int:
        """
        The row of the log provide to use the logs from.

        Setting this property will result in a call to `refreshLogs`.

        See Also
        --------
        log_provider : Set the log provider model.
        """
        return self._row

    @modelRow.setter
    def modelRow(self, row: int):
        """Set the row and refresh logs"""
        self._row = row
        self.refreshLogs()

    @pyqtSlot()
    def refreshLogs(self):
        """
        Refresh the logs displayed.

        This method retrieves the logs from the log provider set.
        If not possible, the corresponding widget is hidden.

        See Also
        --------
        log_provider : The log provider to use
        modelRow : The row to get the logs from
        """
        if self._log_provider and 0 <= self._row <= self._log_provider.rowCount(
        ):
            index = self._log_provider.index(self._row, 0)
            logs = self._log_provider.data(index, LogRole)
            if self._log_provider.data(index, IsHtmlRole):
                self.ui.logView.setHtml(logs)
            else:
                self.ui.logView.setPlainText(logs)
            self.ui.logView.show()
        else:
            self.ui.logView.clear()
            self.ui.logView.hide()

    @property
    def traceback(self) -> str:
        """The traceback to display."""
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

    @staticmethod
    def from_exception(exc_info: ExcInfo,
                       parent: Optional[QWidget] = None) -> 'ErrorView':
        """
        Init an errorview from an exception.

        Parameters
        ----------
        exc_info : ExcInfo
            A tuple as returned by `sys.exc_info()`
        parent : Optional[QWidget], optional
            Parent of the `ErrorView`, by default None

        Returns
        -------
        ErrorView
            The constructed ErrorView
        """
        etype, e, tb_ = exc_info
        msg = traceback_formatting.format_exception_only(etype, e)[-1]
        full_tb = ''.join(traceback_formatting.format_exception(etype, e, tb_))

        error_view = ErrorView(msg, parent=parent)
        error_view.traceback = full_tb

        return error_view


# ---- Testing ---------------------------------------------------------------

if __name__ == "__main__":

    app = QApplication(sys.argv)

    try:
        dummy = [1, 2, 3]
        dummy[6]
    except IndexError:
        exc_info = sys.exc_info()

    error_dialog = ErrorView.from_exception(exc_info)    # type: ignore
    error_dialog.log_provider = DictionaryLogProvider({"": "Some logs"})
    error_dialog.show()

    sys.exit(app.exec_())
