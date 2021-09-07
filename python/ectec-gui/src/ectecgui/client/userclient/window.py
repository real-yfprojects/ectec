#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The main window of the ectec user client.

***********************************

Created on 2021/08/30 at 14:57:02

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
import ectec
import ectec.client as eccl
from PyQt5 import QtWidgets
from PyQt5.QtCore import QEvent, QLocale, QTranslator, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCloseEvent, QPalette
from PyQt5.QtWidgets import QApplication, QComboBox, QMessageBox

from ...ectecQt.client import QUserClient
from ...helpers import list_local_hosts
from ..chatview import ChatView, EctecPackageModel
from . import logger
from .qobjects import UserListLineEdit, UserListValidator, UsernameValidator
from .ui_main import Ui_dUserClient

#: The function that provides internationalization by translation.
_tr = QApplication.translate

# ---- Add widgets to the main window form -----------------------------------


class Ui_UserClientWindow(Ui_dUserClient):
    """
    The UI that are the Widgets of the ConnectWindow.

    This class inherits a automatically generated form class and makes changes
    that can't be done in Qt Designer.
    """
    def setupUi(self, dUserClient: QtWidgets.QDialog):
        """
        Setup the form that is the GUI.

        This sets the window properties and adds the Widgets.

        Parameters
        ----------
        dStartServer : QtWidgets.QDialog
            The QDialog to add the widgets to.
        """
        self.init = True
        super().setupUi(dUserClient)

        # =================================================================
        #
        # Replace ListView with ChatView in the form.
        #
        # The widget showing the chat was set to be a listview in qt
        # designer but it should be a ChatView.
        #
        # =================================================================

        splitter_index = self.splitterMain.indexOf(self.chatView)

        # remove placeholder QListView
        self.chatView.hide()
        self.chatView.setParent(None)
        self.chatView.destroy()

        # define real ChatView
        self.chatView = ChatView()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.chatView.sizePolicy().hasHeightForWidth())
        self.chatView.setSizePolicy(sizePolicy)
        self.chatView.setVerticalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.chatView.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.chatView.setObjectName("chatView")

        # self.chatView.setBackgroundRole(QPalette.ColorRole.Base)

        # add ChatView to splitter
        self.splitterMain.insertWidget(splitter_index, self.chatView)

        # =================================================================
        #
        # Set up main menu.
        #
        # When clicking on the "burger" toolbutton the main menu pops up.
        # The menu is initiated. Then QtWidgets.QActions are created and
        # added to the menu. They represent the menu entries.
        #
        # =================================================================

        self.menu_main = QtWidgets.QMenu(dUserClient)

        # Add 'About' action
        self.action_about = QtWidgets.QAction(
            _tr('dUserClient', "About", "menu"), self.menu_main)
        self.menu_main.addAction(self.action_about)

        # Add menu to toolbutton
        self.toolButtonMenu.setMenu(self.menu_main)

        # end init
        self.init = False

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

        if self.init:
            return

        # =================================================================
        #
        # Retranslate main menu.
        #
        # =================================================================

        self.action_about.setText(_tr('dUserClient', "About", "menu"))


class UserClientWindow(QtWidgets.QDialog):
    """
    The window for using a ectec server as a USER client.
    """

    #: Return to the calling window. This window is already closed.
    ended = pyqtSignal()

    def __init__(self, client: eccl.UserClient, parent=None) -> None:
        """Init."""
        super().__init__(parent=parent)
        # type checks
        if not isinstance(client, QUserClient):
            raise TypeError('The parameter `client` ' +
                            'has to be of type `ectec.client.UserClient`.')

        if not client.connected:
            raise TypeError('The client past as `client` has to be running.')

        # load the GUI generated from an .ui file
        self.ui = Ui_UserClientWindow()
        self.ui.setupUi(self)

        # =================================================================
        #
        # Define or init attributes.
        #
        # =================================================================

        self.client = client

        # =================================================================
        #
        # Setup entries and populate with default values.
        #
        # =================================================================

        # init values for info labels
        local_address = list_local_hosts()[0]
        server_address = self.client.server

        self.ui.labelClientAddress.setText(local_address)
        self.ui.labelClientName.setText(self.client.username)
        self.ui.labelServerAddress.setText(str(server_address.ip))
        self.ui.labelServerPort.setText(str(server_address.port))

        # init comboboxes
        self.ui.comboBoxFrom.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.ui.comboBoxTo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.slotUsersUpdated()  # add items

        # Override deletion of the user list seperator in `comboBoxTo`
        self.ui.comboBoxTo.setLineEdit(UserListLineEdit())

        #  add validators to comboBoxes
        self.ui.comboBoxFrom.setValidator(UsernameValidator(max_length=20))
        self.ui.comboBoxTo.setValidator(
            UserListValidator(max_user_length=20, max_users=5))

        # init chatview

        # change packagestorage of client
        self.packagemodel = EctecPackageModel()
        self.client.packages = self.packagemodel.storage

        self.ui.chatView.setModel(self.packagemodel)
        self.ui.chatView.setLocalName(self.client.username)

        # =================================================================
        #
        # Connect signals.
        #
        # =================================================================

        self.ui.buttonDisconnect.clicked.connect(self.slotDisconnect)
        self.client.usersUpdated.connect(self.slotUsersUpdated)
        self.ui.buttonSend.clicked.connect(self.slotSend)

        # TODO comboBoxes

        # TODO About menu

    @pyqtSlot()
    def slotSend(self):
        # get package meta
        sender = self.ui.comboBoxFrom.currentText()
        raw_receiver = self.ui.comboBoxTo.currentText()

        receiver = raw_receiver.split('; ')
        if not receiver:
            logger.debug('Send: No receiver specified.')
            return  # receiver needed
        if not receiver[-1]:
            receiver = receiver[:-1]
        if not receiver:
            logger.debug('Send: No receiver specified.')
            return  # receiver needed

        # content
        content = self.ui.textEditContent.toPlainText()

        # construct package
        # the package type is irrelevant at the moment
        package = eccl.Package(sender, receiver, 'text/plain')
        package.content = content.encode('utf-8', errors='backslashreplace')

        # send package
        logger.debug('Sending package {}.'.format(hash(package)))
        try:
            self.client.send(package)
        except (OSError, ectec.EctecException) as e:
            logger.warning('Sending package failed: ' + str(e))

            # show error dialog
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle(_tr('dUserClient', "Sending failed."))
            msgBox.setText(_tr('dUserClient', "The following error occured."))
            msgBox.setInformativeText(
                '<i><span style="color: firebrick">{}</span></i> {}'.format(
                    str(e.__class__.__name__), str(e)))
            msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
            msgBox.setIcon(QMessageBox.Icon.Critical)

            msgBox.exec()
            return

    @pyqtSlot()
    def slotUsersUpdated(self):
        """
        Handle an update of the user list.

        This method updates the items in the comboboxes for sending a package.
        """
        # Add special users to list of users
        users = [''] + self.client.users
        users.append('all')

        # Update comboBoxes
        self.ui.comboBoxFrom.clear()
        self.ui.comboBoxTo.clear()

        self.ui.comboBoxFrom.insertItems(0, users)
        self.ui.comboBoxTo.insertItems(0, users)

    @pyqtSlot()
    def slotDisconnect(self):
        """
        Disconnect and return to previous window.

        Disconnect the client from the server and emit the `ended` signal
        telling that the gui flow should return to the previous window.
        Usually that should be the client's `ConnectWindow`.
        """
        logger.debug("Disconnecting.")

        self.close()  # Does the disconnecting in `closeEvent`

        self.ended.emit()  # tells other's to return to previous window.

    def closeEvent(self, event: QCloseEvent) -> None:
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

        logger.debug('UserClientWindow closed.')

        return super().closeEvent(event)

    def changeEvent(self, event: QEvent):
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
        if event.type() == QEvent.Type.LanguageChange:
            # The language of the QApplication was changed.
            # The GUI has to be retranslated.
            self.ui.retranslateUi(self)

            logger.debug("Retranslated ui.")

        # Pass the event to the parent class for its handling.
        super().changeEvent(event)
