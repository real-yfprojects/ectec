#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modifications to `ectec.server` to integrate into the Qt Framework.

***********************************

Created on 2021/09/01 at 14:59:02

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
from typing import List

import ectec
from ectec import client
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from . import signal


class QUserClient(client.UserClient):
    """
    A Client for the normal user role.

    This subclass adds the pyqtSignals `disconnected` and `usersUpdated`.

    Parameters
    ----------
    username : str
        The name for this client which is used as an identifier.

    Attributes
    ----------
    version : Version
        Equals `VERSION` of this python module.
    username : str
        The name for this client which is used as an identifier.
        None if the client is not connected to a server.
    users : list of str
        list of users connected to the server.
    packages : PackageStorage
        The PackageStorage managing the received packages.
    role : Role
        The role of this client. Equals Role.USER.
    server : Address or None
        The address the client is connected to.
    usersUpdated: qt Signal
        The client list (attribute `users`) was updated.
    disconnected: qt Signal
        The connection was closed by the server.

    Methods
    -------
    connect(server, port)
        Connect to a server.
    disconnect()
        Disconnect from the server the client currently is connected to.
    send(package)
        Send a package.
    receive(n)
        Read out the buffer of Packages.

    """

    #: The client list was updated (attribute `users`)
    usersUpdated = signal(name='usersUpdated')

    #: The connection was closed by the server.
    disconnected = signal(name='disconnected')

    def __init__(self, username: str):
        """Init."""
        super().__init__(username=username)

    def _handle_closed(self):
        """
        Handle the closing of the connection.

        Also emits the `disconnected` signal.

        """
        super()._handle_closed()
        self.disconnected.emit()

    def _update_users(self, user_list: List[str]):
        """
        Update the user list.

        This method is usually called by the UserClientThread.

        Parameters
        ----------
        user_list : List[str]
            The list of the user's names.
        """
        super()._update_users(user_list)
        self.usersUpdated.emit()
