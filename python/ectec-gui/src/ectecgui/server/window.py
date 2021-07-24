#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of the window that runs the server.

***********************************

Created on 2021/06/25 at 16:52:15

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
import socket
import subprocess
import sys
from typing import List

from ectec import server as ecse
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QLocale, QTranslator, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget

from .. import DEFAULT_PORT, ectec_res
from .modelview import ClientsTableModel
from .ui_main import Ui_dStartServer

#: The function that provides internationalization by translation.
_tr = QApplication.translate

# ---- Helpers ---------------------------------------------------------------


def list_local_hosts() -> List[str]:
    """
    Get a list of host identifiers for this machine.

    Currently this returns the ip addresses of the local machine.

    Returns
    -------
    List[str]
        The list.
    """

    if sys.platform in ('linux'):
        try:
            process = subprocess.run(['hostname', '-I'], capture_output=True)
            process.check_returncode()

            output = process.stdout.decode('utf-8')

            addr_list = output.strip().split()
            return addr_list
        except (OSError, subprocess.CalledProcessError):
            pass

    hostname = socket.gethostname()
    *dummy, ipaddr_list = socket.gethostbyname_ex(hostname)
    return ipaddr_list


# ---- Add widgets to the main window form -----------------------------------
class Ui_mainWindow(Ui_dStartServer):
    """
    The UI that are the Widgets of the MainWindow.

    This class inherits a automatically generated form class and makes changes
    that can't be done in Qt Designer.
    """
    def setupUi(self, dStartServer: QtWidgets.QDialog):
        """
        Setup the form that is the GUI.

        This sets the window properties and adds the Widgets.

        Parameters
        ----------
        dStartServer : QtWidgets.QDialog
            The QDialog to add the widgets to.
        """
        super().setupUi(dStartServer)

        # =================================================================
        #
        # Set up main menu.
        #
        # When clicking on the "burger" toolbutton the main menu pops up.
        # The menu is initiated. Then QtWidgets.QActions are created and
        # added to the menu. They represent the menu entries.
        #
        # =================================================================

        self.menu_main = QtWidgets.QMenu(dStartServer)

        # Add 'About' action
        self.action_about = QtWidgets.QAction(
            _tr('dStartServer', "About", "menu"), self.menu_main)
        self.menu_main.addAction(self.action_about)

        # Add menu to toolbutton
        self.toolButtonMenu.setMenu(self.menu_main)

    def retranslateUi(self, dStartServer: QtWidgets.QDialog, init=True):
        """
        Retranslate the UI.

        This should update the strings and other properties regarding
        internationalization.

        Parameters
        ----------
        dStartServer : QtWidgets.QDialog
            The QDialog window that contains this form.
        init : bool
            Whether the UI is completely initialized.
        """
        super().retranslateUi(dStartServer)

        if init:
            return

        # =================================================================
        #
        # Retranslate main menu.
        #
        # =================================================================

        self.action_about.setText(_tr('dStartServer', "About", "menu"))


class MainWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # load the GUI generated from an .ui file
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        # =================================================================
        #
        # Define attributes used later.
        #
        # =================================================================

        self.server = ecse.Server()
        self.port = DEFAULT_PORT

        # =================================================================
        #
        # Setup table view of clients.
        #
        # =================================================================

        self.model_clients = ClientsTableModel(self.server,
                                               self.ui.tableClients)
        self.ui.tableClients.setModel(self.model_clients)
        self.ui.tableClients.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)

        # =================================================================
        #
        # Connect signals.
        #
        # =================================================================

        # TODO About menu

        # =================================================================
        #
        # Init start phase.
        #
        # =================================================================

        self.init_pStart()

    def init_pStart(self):
        """
        Setup the interface for the phase in which the server is started.

        """

        # =================================================================
        #
        # Populate address combobox.
        #
        # =================================================================

        combobox = self.ui.comboBoxAddress
        model: QtGui.QStandardItemModel = combobox.model()
        model.clear()
        model.appendColumn([])

        machines_addresses = list_local_hosts()
        combobox.addItems(machines_addresses)

        # =================================================================
        #
        # Setup buttonStart.
        #
        # =================================================================

        self.ui.buttonStart.setText(_tr('dStartServer', "Start", "server"))
        self.ui.buttonStart.disconnect()
        self.ui.buttonStart.clicked.connect(self.slotStart)

        # =================================================================
        #
        # Reset spinBox to default value or value before start.
        #
        # =================================================================

        self.ui.spinBoxPort.setValue(self.port)

        # =================================================================
        #
        # Enable or disable the widgets.
        #
        # =================================================================

        self.ui.tableClients.setEnabled(False)
        self.ui.comboBoxAddress.setEnabled(True)
        self.ui.spinBoxPort.setEnabled(True)

    def init_pRunning(self):
        """
        Setup the interface for the phase in which the server is running.

        """
        # =================================================================
        #
        # Change buttonStart to buttonStop.
        #
        # =================================================================

        self.ui.buttonStart.setText(_tr('dStartServer', "Stop", "server"))
        self.ui.buttonStart.disconnect()
        self.ui.buttonStart.clicked.connect(self.slotStop)

        # =================================================================
        #
        # Enable or disable the widgets.
        #
        # =================================================================

        self.ui.tableClients.setEnabled(True)
        self.ui.comboBoxAddress.setEnabled(False)
        self.ui.spinBoxPort.setEnabled(False)

    @pyqtSlot(bool)
    def slotStart(self, checked=False):
        # get input
        address = self.ui.comboBoxAddress.currentText()
        self.port = self.ui.spinBoxPort.value()

        # start server
        self.server.start(self.port, address)

        # update GUI
        self.init_pRunning()

        port = self.server.port
        address = self.server.address

        self.ui.comboBoxAddress.insertItem(0, address)
        self.ui.comboBoxAddress.setCurrentIndex(0)

        self.ui.spinBoxPort.setValue(port)

    @pyqtSlot(bool)
    def slotStop(self, checked=False):
        self.server.stop()
        self.init_pStart()

    def changeEvent(self, event: QtCore.QEvent):
        """
        This event handler can be implemented to handle state changes.

        The state being changed in this event can be retrieved through
        the event supplied. Change events include:
        `QEvent.ToolBarChange`, `QEvent.ActivationChange`,
        `QEvent.EnabledChange`, `QEvent.FontChange`, `QEvent.StyleChange`,
        `QEvent.PaletteChange`, `QEvent.WindowTitleChange`,
        `QEvent.IconTextChange`, `QEvent.ModifiedChange`,
        `QEvent.MouseTrackingChange`, `QEvent.ParentChange`,
        `QEvent.WindowStateChange`, `QEvent.LanguageChange`,
        `QEvent.LocaleChange`, `QEvent.LayoutDirectionChange`,
        `QEvent.ReadOnlyChange`.

        Parameters
        ----------
        event : QtCore.QEvent
            The event that occurred.
        """
        if event.type() == QtCore.QEvent.LanguageChange:
            # The language of the QApplication was changed.
            # The GUI has to be retranslated.
            self.ui.retranslateUi(self)

        # Pass the event to the parent class for its handling.
        super().changeEvent(event)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Handle a QCloseEvent.

        This event handler is called with the given event when Qt receives
        a window close request for a top-level widget from the window system.
        By default, the event is accepted and the widget is closed. You can
        reimplement this function to change the way the widget responds to
        window close requests. For example, you can prevent the window from
        closing by calling `ignore()` on all events. When calling `accept()` on
        the event the window will be closed.

        Parameters
        ----------
        event : QtGui.QCloseEvent
            The close event.

        """
        self.server.stop()
        return super().closeEvent(event)
