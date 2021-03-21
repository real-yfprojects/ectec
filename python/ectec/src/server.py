#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The server api is implemented here.


***********************************

Created on Thu Mar  4 17:29:04 2021

Copyright (C) 2020 real-yfprojects (github.com user)

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
import socketserver
from collections import namedtuple

from . import VERSION, Address, Package, Role, logs, version

# ---- Logging

logger = logs.getLogger(__name__)


class ConnectionAdapter(logging.LoggerAdapter):
    """
    Adapter to add connection context information.

    Parameters
    ----------
    logger : logging.Logger or logging.LoggerAdapter
        The interface for logging.
    remote : (ip, port)
        The address tuple of the remote.
    extra : dict, optional
        More context. The default is {}.

    """

    def __init__(self, logger, remote, extra={}):
        """
        Adapter to add connection context information..

        Parameters
        ----------
        logger : logging.Logger or logging.LoggerAdapter
            The interface for logging.
        remote : (ip, port)
            The address tuple of the remote (client).
        extra : dict, optional
            More context. The default is {}.


        """
        super().__init__(logger, extra)
        self.remote = Address._make(remote)

    def process(self, msg, kwargs):
        """
        Process the log record, add ip info to msg.

        Overrides super's process.

        Parameters
        ----------
        msg : TYPE
            DESCRIPTION.
        kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        msg = "|{ip:>15}| {msg}".format(ip=self.remote.ip)
        kwargs['ip'] = self.remote.ip
        kwargs['port'] = self.remote.port
        return super().process(msg, kwargs)

# ---- Helpers


ClientData = namedtuple('ClientData', ['name', 'role', 'address', 'handler'])



# ---- Socketserver Implementation

class UserClientHandler(socketserver.BaseRequestHandler):

    # ---- Process (server) wide Data

    clients = {role.value: [] for role in Role}
    # Structure: { 'role': [ClientData, ClientData],
    #               }

    # ---- BaseRequestHandler API

    def setup(self):
        pass

    def handle(self):
        """
        Handle a client connection to a user.

        Overrides the superclasses handle method.

        """
        # Set up logging with context info of connection (ip)
        self.log = ConnectionAdapter(logger, self.client_address)

        # Handle all kinds of exceptions.
        # Log them and send a notice to the client
        try:
            self.run()
        except ConnectionRefusedError as error:
            self.log.exception("Connection refused: {msg}", msg=error.args[0])
            self.send_error(error)
        except Exception as error:
            self.log.exception("Critical Error while handling client.")
            self.send_error('Critical Error.')
        finally:
            pass

    # ---- Functionalities

    def run(self):

        # ---- Handel connect

        # Receive version number
        client_version = self.recv_info()

        # Check if version number is compatible
        # This raises an exception when there is a major problem
        # else returns a boolean value.
        if not self.check_version(client_version):
            # Version is incompatible
            self.send_info(False)  # Tell the client
            return  # The connection socket is closed automatically
        else:
            # Version is compatible - tell the client
            self.send_info(True)

        # Receive the role and name of the user
        name, role_str = self.recv_register()

        # Check role twice to prevent flaws
        try:
            role = Role(role_str)
        except AttributeError:
            raise ConnectionRefusedError(
                f"'{role_str}' is not a valid role") from None

        if role_str not in self.clients:  # Defined as class variable
            raise ConnectionRefusedError(f"'{role_str}' is not a valid role")

        # Check if name is already used
        for role_str, client_list in self.clients.items():
            for client in client_list:  # client : ClientData
                if client.name.lower() == name.lower():  # Design choice
                    # Name in use
                    raise ConnectionRefusedError(
                        f"'{name}' collides with an existing clients name")

        # Register
        self.client_data = ClientData(name, role,
                                      Address._make(
                                          self.request.getsockname()),
                                      self)
        self.clients[role.value].append(self.client_data)

        self.log.info("Registered as {name}, {role}".format(name, role.value))

        # Receive packages
        while True:
            break

        # TODO: Well the rest

    def recv_info(self):
        """
        Receive the info command from the client.

        Returns
        -------
        str
            the sent version number.

        """
        pass

    def recv_register(self):
        """
        Receive the register command of the client.

        Returns
        -------
        tuple (str, str)
            the name and the role received.

        """
        pass

    def recv_pkg(self):
        pass

    def send_info(self, ok: bool):
        pass

    def send_pkg(self, package):
        pass

    def send_error(self, error):
        """
        Send an error message to the client.

        Parameters
        ----------
        error : str or Exception
            The error to be sent.

        Returns
        -------
        None.

        """

    def finish(self):
        # Unregister client
        role = self.client_data.role
        try:
            self.clients[role.value].remove(self.client_data)
        except ValueError as error:
            self.log.debug("Client data wasn't found for removal." +
                           "(likely not registered)")

        self.log.info("Unregistered")

    @classmethod
    def check_version(cls, version_str: str) -> bool:
        try:
            v = version.SemanticVersion.parse(version_str)
        except:
            raise ConnectionRefusedError(
                f"Invalid version number {version_str}") from None

        if v.major != VERSION.major or v.minor != VERSION.minor:
            return False

        return True
