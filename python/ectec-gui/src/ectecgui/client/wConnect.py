#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The client window to connect to a server.

***********************************

Created on 2021/08/16 at 14:23:40

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

import ipaddress

import ectec
import ectec.client as eccl
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QEventLoop, QLocale, QTranslator, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMessageBox

from .. import DEFAULT_PORT
from ..about import AboutDialog
from ..ectecQt.client import QUserClient
from ..helpers import list_local_hosts, translate
from . import logger
from .qobjects import AddressValidator, UsernameValidator
from .ui_connect import Ui_dConnect
from .userclient.window import UserClientWindow

#: The function that provides internationalization by translation.
_tr = QApplication.translate

# ---- Add widgets to the main window form -----------------------------------


class Ui_ConnectWindow(Ui_dConnect):
    """
    The UI that are the Widgets of the ConnectWindow.

    This class inherits a automatically generated form class and makes changes
    that can't be done in Qt Designer.
    """

    def setupUi(self, dConnect: QtWidgets.QDialog):
        """
        Setup the form that is the GUI.

        This sets the window properties and adds the Widgets.

        Parameters
        ----------
        dStartServer : QtWidgets.QDialog
            The QDialog to add the widgets to.
        """
        super().setupUi(dConnect)

        # =================================================================
        #
        # Set up main menu.
        #
        # When clicking on the "burger" toolbutton the main menu pops up.
        # The menu is initiated. Then QtWidgets.QActions are created and
        # added to the menu. They represent the menu entries.
        #
        # =================================================================

        self.menu_main = QtWidgets.QMenu(dConnect)

        # Add 'About' action
        self.action_about = QtWidgets.QAction(_tr('dConnect', "About", "menu"),
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
        """
        super().retranslateUi(dStartServer)

        # =================================================================
        #
        # Retranslate main menu.
        #
        # =================================================================

        if hasattr(self, 'action_about'):
            self.action_about.setText(_tr('dConnect', "About", "menu"))


# ---- Implement GUI's logic -------------------------------------------------


class ConnectWindow(QtWidgets.QDialog):
    """
    The client window to connect to a server.

    This window allows the user to enter a server, a name and a role. Then it
    tries to connect to the server and start the window for the
    given user role.

    """

    def __init__(self, parent=None) -> None:
        """Init."""
        super().__init__(parent=parent)

        # load the GUI generated from an .ui file
        self.ui = Ui_ConnectWindow()
        self.ui.setupUi(self)

        # =================================================================
        #
        # Define attributes used later.
        #
        # =================================================================

        self.client = None
        self.windowRunning: QtWidgets.QDialog = None

        # =================================================================
        #
        # Setup entries and populate with default values.
        #
        # =================================================================

        self.ui.comboBoxRole.addItems([role.value for role in ectec.Role])
        self.ui.entryName.setMaxLength(20)
        self.ui.entryAddress.setMaxLength(20)
        self.ui.spinBoxPort.setValue(DEFAULT_PORT)

        # add validators
        self.ui.entryAddress.setValidator(AddressValidator(dn_allowed=True))
        self.ui.entryName.setValidator(UsernameValidator())

        # set initial address
        address = ipaddress.ip_address(list_local_hosts()[0])
        self.ui.entryAddress.setText(str(address))
        self.ui.entryAddress.setPlaceholderText(str(address))

        # =================================================================
        #
        # Connect signals.
        #
        # =================================================================

        self.ui.buttonConnect.clicked.connect(self.slotConnect)
        self.ui.buttonClose.clicked.connect(self.slotClose)

        # connect hamburger menu
        self.ui.action_about.triggered.connect(self.slotAbout)

        # =================================================================
        #
        # Init config phase.
        #
        # =================================================================

        self.init_pConfig()

    @pyqtSlot()
    def slotAbout(self):
        """Show the about dialog."""
        title = translate("AboutDialog", "Ectec - Client")
        description = translate("AboutDialog", "Description")

        dialog = AboutDialog(title, description, parent=self)
        self.finished.connect(dialog.done)
        dialog.show()
        logger.debug("Opened `About` window.")

    def init_pConfig(self):
        """Setup the interface for the phase in which the user enters info."""

        # clear status label
        self.ui.labelStatus.setText('')

        # =================================================================
        #
        # Enable widgets.
        #
        # =================================================================

        self.ui.entryAddress.setEnabled(True)
        self.ui.entryName.setEnabled(True)
        self.ui.comboBoxRole.setEnabled(True)
        self.ui.spinBoxPort.setEnabled(True)
        self.ui.buttonConnect.setEnabled(True)

    def init_pConnect(self):
        """Setup the interface for the connecting phase."""
        # =================================================================
        #
        # Disable widgets.
        #
        # =================================================================

        self.ui.entryAddress.setEnabled(False)
        self.ui.entryName.setEnabled(False)
        self.ui.comboBoxRole.setEnabled(False)
        self.ui.spinBoxPort.setEnabled(False)
        self.ui.buttonConnect.setEnabled(False)

    @pyqtSlot()
    def slotConnect(self):
        """
        Try to connect to a server.

        This method switches to the *connect* phase. After establishing the
        connection the client window matching to the user role is opened.
        """
        self.init_pConnect()

        address = self.ui.entryAddress.text()
        port = self.ui.spinBoxPort.value()
        role = ectec.Role(self.ui.comboBoxRole.currentText())  # not used yet
        name = self.ui.entryName.text()

        # check inputs
        if not name:
            # name empty
            logger.warning('User entered empty name.')

            # show error dialog
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle(_tr('dConnect', "Connecting failed."))
            msgBox.setText(_tr('dConnect', "The user name mustn't be empty."))
            msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
            msgBox.setIcon(QMessageBox.Icon.Critical)

            msgBox.exec()

            # give the user another chance
            self.init_pConfig()
            return

        # init Client
        if role == ectec.Role.USER:
            self.client = QUserClient(name)
        else:
            logger.error("Role {} not implemented.".format(str(role)))
            return

        # start connecting
        self.ui.labelStatus.setText(_tr('dConnect', 'Connecting...'))
        QApplication.processEvents(
            QEventLoop.ExcludeUserInputEvents)  # update label

        try:
            self.client.connect(address, port)
        except (OSError, eccl.ConnectException) as e:
            logger.warning("Connecting failed: " + str(e))

            self.ui.labelStatus.setText(_tr('dConnect', 'Connecting failed.'))

            # show error dialog
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle(_tr('dConnect', "Connecting failed."))
            msgBox.setText(
                _tr('dConnect', "Connection couldn't be established."))
            msgBox.setInformativeText(
                '<i><span style="color: firebrick">{}</span></i> {}'.format(
                    str(e.__class__.__name__), str(e)))
            msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
            msgBox.setIcon(QMessageBox.Icon.Critical)

            msgBox.exec()

            # give the user another chance
            self.init_pConfig()
            return

        logger.info("Connection established. Opening next dialog.")

        # select user role and open corresponding window
        if role == ectec.Role.USER:
            # user role

            # init window
            self.windowRunning = UserClientWindow(self.client)
            self.client = None

            self.windowRunning.ended.connect(self.slotDisconnected)

            # show on top
            self.windowRunning.show()
            self.windowRunning.raise_()
            self.windowRunning.activateWindow()

            # hide this window
            # when hiding the window it should be cleaned as in close
            # because close might not be called.
            self.hide()

            logger.debug('Started `UserClientWindow`.')

    @pyqtSlot()
    def slotDisconnected(self):
        """
        Handle the disconnecting by the client role specific window.

        This slot is connected to the `closed` signal of the window that
        is shown while the client is connected.

        Parameters
        ----------
        terminate : bool
            Whether to terminate the client app.
        """
        # window should be already closed.
        # removing reference -> will be garbage collected at some point.
        self.windowRunning = None

        self.init_pConfig()
        self.show()

    @pyqtSlot()
    def slotClose(self):
        """
        Close the window.

        This slot is usually connected to the 'cancel' button that closes
        the window.
        """
        self.close()

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
        if self.client:
            self.client.disconnect()

        if self.windowRunning:
            self.windowRunning.close()

        logger.debug('App closed.')

        return super().closeEvent(event)

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
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            # The language of the QApplication was changed.
            # The GUI has to be retranslated.
            self.ui.retranslateUi(self)

            logger.debug("Retranslated ui.")

        # Pass the event to the parent class for its handling.
        super().changeEvent(event)
