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
import logging
import socket
import subprocess
import sys
from typing import List

from ectec import server as ecse
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QLocale, QPoint, Qt, QTranslator, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAction, QApplication, QMenu, QMessageBox

from .. import DEFAULT_PORT, ectec_res
from ..about import AboutDialog
from ..ectecQt.server import Server
from ..helpers import list_local_hosts, translate
from ..qobjects import LanguageMenu
from .modelview import ClientsTableModel
from .ui_main import Ui_dStartServer

#: The function that provides internationalization by translation.
_tr = QApplication.translate


# ---- Logging ---------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



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

        self.menu_main = QMenu(dStartServer)

        # language menu
        self.menu_main.addMenu(LanguageMenu(dStartServer))

        # Add 'About' action
        self.action_about = QAction(_tr('dStartServer', "About", "menu"),
                                    self.menu_main)
        self.menu_main.addAction(self.action_about)

        # Add menu to toolbutton
        self.toolButtonMenu.setMenu(self.menu_main)


    def retranslateUi(self, dStartServer: QtWidgets.QDialog):
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

        # =================================================================
        #
        # Retranslate main menu.
        #
        # =================================================================

        if hasattr(self, 'action_about'):
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

        self.server = Server()
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

        self.server.usersChanged.connect(self.model_clients.listChanged)
        self.ui.checkBoxBlocking.stateChanged.connect(
            self.slotBlockingStateChanged)

        # context menu for tableview.
        self.ui.tableClients.customContextMenuRequested.connect(
            self.slotTableContextMenu)

        # connect hamburger menu
        self.ui.action_about.triggered.connect(self.slotAbout)

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
        self.ui.checkBoxBlocking.setEnabled(False)
        self.ui.checkBoxBlocking.setChecked(False)

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

        self.ui.checkBoxBlocking.setEnabled(True)
        self.ui.checkBoxBlocking.setChecked(False)

    @pyqtSlot(bool)
    def slotStart(self, checked=False):
        # get input
        address = self.ui.comboBoxAddress.currentText()
        self.port = self.ui.spinBoxPort.value()

        # start server
        try:
            # the address '' will bind the socket to every interface
            # allowing it to be reachable by `localhost`.
            self.server.start(self.port, '')
        except ecse.EctecException as e:
            logger.debug("Server is already running.")
            return
        except OSError as e:
            logger.warning(
                "Starting the server on ({}, {}) failed: {}; {}".format(
                    address, self.port, e.__class__.__name__, str(e)))

            # show error dialog
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle(_tr('dStartServer',
                                      "Couldn't start server."))
            msgBox.setText(_tr('dStartServer', "Starting the server failed."))
            msgBox.setInformativeText(
                '<i><span style="color: firebrick">{}</span></i> {}'.format(
                    str(e.__class__.__name__), str(e)))
            msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
            msgBox.setIcon(QMessageBox.Icon.Critical)

            msgBox.exec()

            self.init_pStart()
            return

        logger.info("Start server on ({}, {}).".format(address, self.port))

        # update GUI
        self.init_pRunning()

        port = self.server.port

        # commented 'cause it won't be the real ip address on linux
        # address = self.server.address

        self.ui.comboBoxAddress.insertItem(0, address)
        self.ui.comboBoxAddress.setCurrentIndex(0)

        self.ui.spinBoxPort.setValue(port)

    @pyqtSlot(bool)
    def slotStop(self, checked=False):
        self.server.stop()

        logger.info("Stopped server.")

        self.init_pStart()

    @pyqtSlot(QPoint)
    def slotTableContextMenu(self, pos: QPoint):
        # construct context menu
        menu = QMenu(self)
        action_kick = QAction(_tr('dStartServer', 'Kick', 'client'), menu)
        action_kick.triggered.connect(self.slotKick)
        menu.addAction(action_kick)

        # show menu
        coords = self.ui.tableClients.viewport().mapToGlobal(pos)
        menu.popup(coords)

    @pyqtSlot()
    def slotKick(self):
        if not self.server.running:
            return

        # get selected items
        selected = self.ui.tableClients.selectionModel().selectedRows()
        model = self.ui.tableClients.model()

        names = []
        for index in selected:
            row = index.row()
            row_index = model.index(row, 0)
            name = model.data(row_index, Qt.ItemDataRole.DisplayRole)
            names.append(name)

        # This solution is not optimal. When the model changes while this is
        # running it won't work as expected. The model will most of the time
        # change when the clients are immediately kicked. That's why there are
        # two loops here.

        for name in names:
            self.server.kick(name)

    @pyqtSlot(int)
    def slotBlockingStateChanged(self, state: Qt.CheckState):
        if state == Qt.CheckState.Checked:
            # blocking
            self.server.reject = True
        else:
            # not blocked
            self.server.reject = False

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

            logger.debug("Retranslated ui.")

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

        logger.debug('App closed.')

        return super().closeEvent(event)

    @pyqtSlot()
    def slotAbout(self):
        """Show the about dialog."""
        title = translate("AboutDialog", "Ectec - Server")
        description = translate("AboutDialog", "Description")

        dialog = AboutDialog(title, description, parent=self)
        self.finished.connect(dialog.done)
        dialog.show()
        logger.debug("Opened `About` window.")
