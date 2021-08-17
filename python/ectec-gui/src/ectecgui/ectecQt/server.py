#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modifications to `ectec.server` to integrate into the Qt Framework.

***********************************

Created on 2021/08/17 at 14:33:03

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
import threading

import ectec
import ectec.server as ectecserver
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from . import ThreadQ, pyqtClassSignal


class QClientHandler(ectecserver.ClientHandler, QObject):
    usersChanged = pyqtClassSignal(name='usersChanged')

    def handle_client(self, role):
        self.usersChanged.signal.emit()
        super().handle_client(role)

    def finish(self):
        disconnect = bool(self.client_data)
        super().finish()

        if disconnect:
            self.usersChanged.signal.emit()


class Server(QObject, ectecserver.Server):

    stopped = pyqtSignal()

    usersChanged = pyqtSignal()

    def __init__(self, requesthandler=QClientHandler):
        """
        Init the instance.

        Parameters
        ----------
        requesthandler : BaseRequestHandler, optional
            The request handler for the TCPServer.
            Needs a `get_client_list` static/class method and the same signals
            as `QClientHandler`.
            The default is QClientHandler.

        Returns
        -------
        None.

        """
        super().__init__(requesthandler=requesthandler)

        self.requesthandler_class.usersChanged.signal.connect(
            self.usersChanged)

    def start(self, port: int, address: str = ""):
        """
        Start the server at the given port and address.

        A new `TheadingTCPServer` is created every time start is called.
        It is important to call the `stop` method after this one so that
        the `EctecTCPServer` is teared down and cleaned up.

        Parameters
        ----------
        port : int
            the port.
        address : str
            The address. Defaults to an empty string.

        Raises
        ------
        EctecException
            The server is already running.

        Returns
        -------
        ServerRunningContextManager
            A context manager for closing the server.

        """
        if self.running:
            raise ectec.EctecException('Server is already running.')

        server = ectecserver.EctecTCPServer((address, port),
                                            self.requesthandler_class)
        self._server = server

        self._serve_thread = ThreadQ(target=server.serve_forever)
        self._serve_thread.finished.connect(self.stopped)
        self._serve_thread.start()

        return self.ServerRunningContextManager(self)

    @pyqtSlot(str)
    def kick(self, client_id):
        return super().kick(client_id)

    @pyqtSlot()
    def stop(self):
        super().stop()
        self.stopped.emit()
