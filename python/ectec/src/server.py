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
import threading
import time
from collections import namedtuple

from . import VERSION, Address, EctecException, Package, Role, logs, version
from .util import ClassPropertyMetaClass, classproperty

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

    def __init__(self, logger, remote, extra=None):
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
        super().__init__(logger, extra if extra else {})
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
        msg = "|{ip:>15}| {msg}".format(ip=self.remote.ip, msg=msg)
        kwargs['ip'] = self.remote.ip
        kwargs['port'] = self.remote.port
        return super().process(msg, kwargs)

# ---- Exceptions for this implementation


class ConnectionClosed(EctecException):
    """
    The connection was closed.
    """


class RequestRefusedError(EctecException):
    """
    The the handler refuses the request.

    This can be raised if the versions aren't compatible or the client
    couldn't be registered.

    """


class CommandError(EctecException):
    """
    There was a problem handling a command.
    """


class CommandTimeout(CommandError):
    """
    The receiving of a command timed out.
    """


class UnexpectedData(CommandError):
    """
    The bytes sent by the client are unexpected.

    E.g. the client sent to many.
    """


class UnexpectedCommand(UnexpectedData):
    """
    The bytes sent by the client don't represent the expected command.
    """


# ---- Helpers


ClientData = namedtuple('ClientData', ['name', 'role', 'address', 'handler'])


# ---- Socketserver Implementation

class UserClientHandler(socketserver.BaseRequestHandler,
                        metaclass=ClassPropertyMetaClass):

    # ---- Process (server) wide constants
    TIMEOUT = 1000  # ms timeout for awaited commands

    TRANSMISSION_TIMEOUT = 0.200  # seconds of timeout between parts
    COMMAND_TIMOUT = 1.000  # s timeout for a command to be completely received
    SOCKET_BUFSIZE = 4096  # bytes to read from socket at once
    COMMAND_SEPERATOR = b'\n'  # seperates commands of the ectec protocol
    COMMAND_LENGTH = 4096  # bytes - the maximum length of a command

    # ---- Process (server) wide data

    class Locks:
        clients: threading.Lock = threading.Lock()

    clients = {role.value: [] for role in Role}
    # Structure: { 'role': [ClientData, ClientData],
    #               }
    # !!! the keys aren't thread safe

    # ---- BaseRequestHandler API

    def setup(self):
        # later stores the ClientData of this handler
        self.client_data: ClientData = None

        # stores received bytes that belong to the next command
        self.buffer: bytes = bytes(0)  # bytes object with zero bytes

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
        except RequestRefusedError as error:
            self.log.exception("Connection refused: {msg}", msg=error.args[0])
            self.send_error(error)
        except OSError as error:
            self.log.exception("OSError: {msg}", msg=error.args[0])
            self.send_error('Critical Error.')
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
            self.log.debug('Incompatible version. Refused')
            return  # The connection socket is closed automatically

        # Version is compatible - tell the client
        self.send_info(True)

        # Receive the role and name of the user
        name, role_str = self.recv_register()

        # Check role twice to prevent flaws
        try:
            role = Role(role_str)
        except AttributeError:
            raise RequestRefusedError(
                f"'{role_str}' is not a valid role") from None

        if role_str not in self.clients:  # Defined as class variable
            raise RequestRefusedError(f"'{role_str}' is not a valid role")

        # Check if name is already used
        with self.Locks.clients:
            for role_str, client_list in self.clients.items():
                for client in client_list:  # client : ClientData
                    if client.name.lower() == name.lower():  # Design choice
                        # Name in use
                        raise RequestRefusedError(
                            f"'{name}' collides with an existing clients name")

            # Register
            self.client_data = ClientData(name, role,
                                          Address._make(
                                              self.request.getsockname()),
                                          self)
            self.clients[role.value].append(self.client_data)

        self.log.info("Registered as {0}, {1}".format(name, role.value))

        # Receive packages
        while True:
            break

        # TODO: Well the rest

    def recv_command(self, max_length, start_timeout=None, timeout=None):
        """
        Receive a command and return it.

        Commands are seperatet by the a new line or the value of the
        class variable `COMMAND_SEPERATOR`. Commands also must not exceed a
        length of `max_length`. The timout for missing parts is defined in
        `TRANSMISSION_TIMEOUT`. The amount of bits received at once in
        `SOCKET_BUFSIZE`. This methods automatically exits about `timeout`
        miliseconds after the receiving of the command started.

        Parameters
        ----------
        max_length : int
            The maximum lenght of a command in bytes.
        start_timeout : int, optional
            The timeout in s for receiving first data. The default is None.
        timeout : int, optional
            The timeout in s for the end of the command. The default is None.

        Raises
        ------
        CommandError
            The command was too long.
        CommandTimeout
            The command timed out.

        Returns
        -------
        command : bytes
            the command.

        """
        msg = self.buffer
        seperator = self.COMMAND_SEPERATOR
        bufsize = self.SOCKET_BUFSIZE

        if len(msg) < 1:
            # buffer empty -> command not incoming yet
            self.request.setblocking(True)
            self.request.settimeout(start_timeout)

            try:
                msg = self.request.recv(bufsize)  # msg was empty
            except socket.timeout as error:
                raise CommandTimeout(
                    "The receiving of the command timed out.") from error

            if not msg:
                # connection was closed
                raise ConnectionClosed(
                    "The connection was closed by the client.")

        # check buffer or first data received
        i = msg.find(seperator)

        if i >= 0:  # separator found
            command = msg[:i]
            self.buffer = msg[i+len(seperator):]  # seperator is removed

            # for expected behavoir check length of command
            cmd_length = len(command)
            if cmd_length > max_length:
                raise CommandError(
                    f"Command too long: {cmd_length} bytes" +
                    f" from {max_length}")
            else:
                return command

        # Command wasn't received completely yet.
        self.request.setblocking(True)
        self.request.settimeout(self.TRANSMISSION_TIMEOUT)

        # read out the most precice system clock for timeouting
        start_time = time.perf_counter_ns()

        # convert timeout to ns (nanoseconds)
        timeout = timeout * 0.000000001 if timeout != None else None

        length = len(msg)
        while True:  # ends by an error or a return
            try:
                part = self.request.recv(bufsize)
            except socket.timeout as error:
                raise CommandTimeout("Command parts timed out.") from error

            if not part:
                # connection was closed
                raise ConnectionClosed(
                    "The connection was closed by the client.")

            time_elapsed = time.perf_counter_ns()-start_time

            i = part.find(seperator)  # end of command?

            if i >= 0:  # separator found
                command = msg + part[:i]
                self.buffer = part[i+len(seperator):]  # seperator is removed

                # for expected behavoir check length of command
                cmd_length = len(command)
                if cmd_length > max_length:
                    raise CommandError(
                        f"Command too long: {cmd_length} bytes" +
                        f" from {max_length}")
                else:
                    return command
            elif timeout is not None and time_elapsed > timeout:
                raise CommandTimeout("Receiving of a command took too long" +
                                     f". {time_elapsed} nanoseconds" +
                                     " have already past.")
            else:
                # end of command not yet received
                # check length
                length += len(part)

                if length > max_length:
                    # too long
                    raise CommandError(
                        f"Command too long: over {max_length} bytes")
                else:
                    # add part to local buffer
                    msg += part

    def recv_info(self):
        """
        Receive the info command from the client.

        The whole command must not exceed 4096 bit, that is 512 byte.
        The version number therefore must not exceed 507 letters.

        ::

            INFO <version number as str>


        Returns
        -------
        str
            the sent version number.

        """

        # TODO

    def recv_register(self):
        """
        Receive the register command of the client.

        Returns
        -------
        tuple (str, str)
            the name and the role received.

        """
        # TODO

    def recv_pkg(self):
        pass  # TODO

    def send_info(self, ok: bool):
        pass  # TODO

    def send_pkg(self, package):
        pass  # TODO

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
        # TODO

    def finish(self):
        # Unregister client
        if self.client_data:
            role = self.client_data.role
            try:
                with self.Locks.clients:
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
            raise RequestRefusedError(
                f"Invalid version number {version_str}") from None

        if v.major != VERSION.major or v.minor != VERSION.minor:
            return False

        return True
