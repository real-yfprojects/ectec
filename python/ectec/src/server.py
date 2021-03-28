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
import re
import socket
import socketserver
import threading
import time
from collections import namedtuple

from . import (VERSION, AbstractServer, Address, EctecException, Role, logs,
               version)

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

Package = namedtuple('Package', ['sender', 'recipient',
                                 'type', 'content'])


# ---- Socketserver Implementation

class ClientHandler(socketserver.BaseRequestHandler):
    """
    Handles one client connecting to the server.

    Multiple instaces can handle all clients to the server.
    Clients are identified by their name and stored in `clients`. The names
    aren't case sensitiv.

    Attributes
    ----------
    run
        Run the protocoll until the client is registered.
    handle_XXX
        Handle client with a specific role.
    recv_bytes
        Receive a specified number of bytes.
    recv_command
        Receive unspecified command. This should be called in methods that
        receive a specific command.
    recv_XXX
        Receive a specific command and interpret it.
    send_XXX
        Send a specific command. Don't harcode the seperator!

    Notes
    -----
    Each client has to perform a version check.
    After that it is able to register itself with a name and a role.
    The name must be unique among all roles. The names are case sensitiv.
    But when checking uniquness the case is ignored.

    There is one handle method for each type of role. The method will be
    called after registering.
    """

    # ---- Process (server) wide constants
    TIMEOUT = 1000  # ms timeout for awaited commands

    TRANSMISSION_TIMEOUT = 0.200  # seconds of timeout between parts
    COMMAND_TIMEOUT = 0.300  # s timeout for a command to be completely received
    SOCKET_BUFSIZE = 4096  # bytes to read from socket at once
    COMMAND_SEPERATOR = b'\n'  # seperates commands of the ectec protocol
    COMMAND_LENGTH = 4096  # bytes - the maximum length of a command

    # Users with the listed roles are shared with all clients:
    PUBLIC_ROLES = [Role.USER]

    # ---- Process (server) wide data

    class Locks:
        """
        This is a data class holding locks for class variables.

        Its puprose is making the code cleaner.
        """
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
        """
        Run the initial register sequence of the ectec protocoll.

        The `handle_XXX` methods are called depending on the role.

        Raises
        ------
        RequestRefusedError
            The connection and register attempt was refused.
        NotImplementedError
            The role is not yet implemented.

        Returns
        -------
        None.

        """
        # ---- Version check

        # Receive version number
        try:
            client_version = self.recv_info()
        except (OSError, CommandError, CommandTimeout) as error:
            self.log.debug("Error while receiving client info: " +
                           str(error.args[0]))

        # Check if version number is compatible
        # This raises an exception when there is a major problem
        # else returns a boolean value.
        if not self.check_version(client_version):
            # Version is incompatible
            self.send_info(False)  # Tell the client
            self.log.debug('Incompatible version. Refused')
            return  # The connection socket is closed automatically

        self.log.debug("Version check passed. Sending answer.")

        # Version is compatible - tell the client
        self.send_info(True)

        # ---- Register

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
            for dummy, client_list in self.clients.items():
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

        # ---- Send user update
        # Update user lists of all clients
        with self.Locks.clients:
            for dummy, client_list in self.clients.items():
                for client in client_list:
                    try:
                        client.handler.send_update()
                    except OSError:
                        # client disconnected
                        pass
                    except Exception as error:
                        self.log.debug(f"Couldn't update because {str(error)}")

        if role == Role.USER:
            self.handle_user()
        else:
            raise NotImplementedError("The role {str(role)} is not supported.")

    def handle_user(self):
        """
        Handle a client (after registering) with the role `USER`.

        Raises
        ------
        OSError
            The connection was closed by the client.

        """
        # Receive packages
        while True:
            try:
                package = self.recv_pkg()
            except (OSError, ConnectionClosed) as error:  # Connection closed
                raise error
            except CommandTimeout as error:
                # wait for next command
                self.send_error(error)
            except CommandError as error:
                # wait for next command
                self.send_error(error)

            command = "PACKAGE {} FROM {} TO {} WITH {}"
            self.log.info(command.format(package.type,
                                         package.sender,
                                         package.recipient,
                                         len(package.content)
                                         ))

            # forward package
            with self.Locks.clients:
                for client in self.clients[Role.USER]:
                    try:
                        client.handler.send_pkg(package)
                    except OSError:
                        # client already disconnected
                        self.log.debug("Couldn't forward package to " +
                                       f"{client.address.ip}")

    def recv_bytes(self, length, start_timeout=None, timeout=None) -> bytes:
        """
        Receive a specified amount of bytes.

        Parameters
        ----------
        length : int
            the amount of bytes.
        start_timeout : int, optional
            The timeout in s for receiving first data. The default is None.
        timeout : int, optional
            The timeout in s for the end of the command. The default is None.

        Raises
        ------
        CommandTimeout
            The command timed out.

        Returns
        -------
        bytes
            the received data.

        """
        msg = self.buffer
        self.buffer = bytes(0)
        bufsize = self.SOCKET_BUFSIZE

        if len(msg) < 1:
            # buffer empty -> command not incoming yet
            self.request.setblocking(True)
            self.request.settimeout(start_timeout)

            try:
                msg = self.request.recv(bufsize)  # msg was empty
            except socket.timeout as error:
                raise CommandTimeout(
                    "The receiving of the data timed out.") from error

            if not msg:
                # connection was closed
                raise ConnectionClosed(
                    "The connection was closed by the client.")

        if len(msg) >= length:  # separator found
            data = msg[:length]
            self.buffer = msg[length:]

            return data

        # Data wasn't received completely yet.
        self.request.setblocking(True)
        self.request.settimeout(self.TRANSMISSION_TIMEOUT)

        # read out the most precice system clock for timeouting
        start_time = time.perf_counter_ns()

        # convert timeout to ns (nanoseconds)
        timeout = timeout * 0.000000001 if timeout is not None else None

        data_length = len(msg)
        needed = length - data_length
        while True:  # ends by an error or a return
            try:
                part = self.request.recv(bufsize)
            except socket.timeout as error:
                raise CommandTimeout("Data parts timed out.") from error

            if not part:
                # connection was closed
                raise ConnectionClosed(
                    "The connection was closed by the client.")

            time_elapsed = time.perf_counter_ns()-start_time

            part_length = len(part)

            if part_length >= needed:
                data = msg + part[:needed]
                self.buffer = part[needed:]
                return data

            # check time
            if timeout is not None and time_elapsed > timeout:
                raise CommandTimeout("Receiving of a data took too long" +
                                     f". {time_elapsed} nanoseconds" +
                                     " have already past.")

            # end of command not yet received
            # check length
            data_length += part_length
            needed = length - data_length

            # add part to local buffer
            msg += part

    def recv_command(self, max_length,
                     start_timeout=None, timeout=None) -> bytes:
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
        start_timeout : float, optional
            The timeout in s for receiving first data. The default is None.
        timeout : float, optional
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
        self.buffer = bytes(0)
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

            return command

        # Command wasn't received completely yet.
        self.request.setblocking(True)
        self.request.settimeout(self.TRANSMISSION_TIMEOUT)

        # read out the most precice system clock for timeouting
        start_time = time.perf_counter_ns()

        # convert timeout to ns (nanoseconds)
        timeout = timeout * 0.000000001 if timeout is not None else None

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

                return command

            # check time
            if timeout is not None and time_elapsed > timeout:
                raise CommandTimeout("Receiving of a command took too long" +
                                     f". {time_elapsed} nanoseconds" +
                                     " have already past.")

            # end of command not yet received
            # check length
            length += len(part)

            if length > max_length:
                # too long
                raise CommandError(
                    f"Command too long: over {max_length} bytes")

            # add part to local buffer
            msg += part

    # regular expression for the INFO command
    regex_info = re.compile(r"INFO ([\w+.-]+)")

    def recv_info(self):
        """
        Receive the info command from the client.

        The whole command must not exceed 4096 byte.
        The version number therefore must not exceed 4091 letters.
        The regex in `regex_info` is used. You should only change it when
        subclassing.

        ::

            INFO ([\\w+.-]+)
                 ----------
                 version number


        Returns
        -------
        str
            the sent version number.

        """

        raw_cmd = self.recv_command(4096, 0.2, self.COMMAND_TIMEOUT)
        cmd = raw_cmd.decode(encoding='utf-8', errors='surrogateescape')

        # match regular expression
        match = self.regex_info.fullmatch(cmd)  # should match the whole text

        if not match:
            raise CommandError("Received data doesn't match INFO command.")

        return match.group(1)

    # regular expression for the REGISTER command
    regex_register = re.compile(r"REGISTER (\w+) AS (/w+)")

    def recv_register(self):
        """
        Receive the register command of the client.

        ::

            REGISTER (\\w+) AS (\\w+)
                     ----     -----
                     name     role

        Returns
        -------
        tuple (str, str)
            the name and the role received.

        """
        raw_cmd = self.recv_command(4096, 0.2, self.COMMAND_TIMEOUT)
        cmd = raw_cmd.decode(encoding='utf-8', errors='surrogateescape')

        # match regular expression on the whole text
        match = self.regex_register.fullmatch(cmd)

        if not match:
            raise CommandError("Received data doesn't match REGISTER command.")

        return match.group(1), match.group(2)

    # regular expression for the PACKAGE command
    regex_package = re.compile(
        r"PACKAGE ([\w/.-]+) FROM ([\w/.-]+) TO ([\w/.-]+) WITH .{2}")

    def recv_pkg(self, timeout=None):
        """
        Receive a package command from the client.

        A package command is a normal command followed by a specified
        stream of bytes. There are two bytes which representing a integer in
        the big endian format. The integer sprecifies the length of the
        content in bytes. The content therefore must not exceed 65,535 bytes.

        ::

            PACKAGE ([\\w/.-]+) FROM ([\\w/.-]+) TO ([\\w/.-]+) WITH .{2}
                    ----------      ----------    ----------      ----
                    content-type    sender        recipient      content-length

        Parameters
        ----------
        timeout : float
            The timeout for when the package should arrive.
            The default is None.

        Raises
        ------
        CommandError
            Wrong command.

        Returns
        -------
        package : Package
            the packages fields in a namedtuple.

        """
        raw_cmd = self.recv_command(4096, timeout, self.COMMAND_TIMEOUT)
        cmd = raw_cmd.decode(encoding='utf-8', errors='surrogateescape')

        # match regular expression on the whole text
        match = self.regex_package.fullmatch(cmd)

        if not match:
            raise CommandError("Received data doesn't match PACKAGE command.")

        type_code = match.group(1)
        sender = match.group(2)
        recipient = match.group(3)

        # decode length
        length_bytes = match.group(4).encode(
            encoding='utf-8', errors='surrogateescape')
        length = int.from_bytes(length_bytes, 'big', signed=False)

        # receive package content
        if length:
            content = self.recv_bytes(length)
        else:
            content = b''

        # create package
        package = Package(sender, recipient, type_code, content)

        return package

    def send_info(self, accepted: bool):
        """
        Send a INFO command to the remote.

        The INFO command contains the version number of the module. That is
        `str(VERSION)`.

        Parameters
        ----------
        accepted : bool
            Wether the client's version was accepted.

        """
        template = b'INFO {ok} {version}{sep}'

        command = template.format(ok=accepted,
                                  version=str(VERSION).encode('utf-8'),
                                  sep=self.COMMAND_SEPERATOR)
        self.request.sendall(command)

    def send_pkg(self, package: Package):
        """
        Send a package command with the packages content.

        ::

            PACKAGE {typ} FROM {sender} TO {recipient} WITH {length}

        Parameters
        ----------
        package : Package
            The namedtuple containing the package data.

        """
        template = b'PACKAGE {typ} FROM {sender} TO {recipient} WITH {l}{sep}'

        length = len(package.content).to_bytes(2, 'big', signed=False)

        command = template.format(typ=package.type,
                                  sender=package.sender,
                                  recipient=package.recipient,
                                  l=length,
                                  sep=self.COMMAND_SEPERATOR)
        data = command + package.content

        self.request.sendall(data)

    def send_update(self):
        """
        Send an update to the user list of the remote.

        The user list is automatically created from the users in `clients`.
        But users with roles that aren't specified in `PUBLIC_ROLES`
        are ignored. The users are sent after the command and seperated by
        spaces.

        ::

            UPDATE USERS {length}

        """
        template = b'UPDATE USERS {length}{sep}'

        user_names = []
        with self.Locks.clients:
            for role in self.PUBLIC_ROLES:
                # role is type `Role`
                for user in self.clients[role.value]:
                    # user is type `ClientData`
                    user_names.append(user.name)

        user_list = b' '.join(user_names)
        length = len(user_list).to_bytes(2, 'big', signed=False)

        command = template.format(length=length,
                                  sep=self.COMMAND_SEPERATOR)
        data = command + user_list

        self.request.sendall(data)

    def send_error(self, error):
        """
        Send an error message to the client.

        The message may contain every character besides the command seperator

        ::

            ERROR {message}{sep}


        Parameters
        ----------
        error : str or Exception
            The error to be sent.

        Returns
        -------
        None.

        """
        template = b'ERROR {typ} {message}{sep}'

        if isinstance(error, Exception):
            name = type(error).__name__
            text = '; '.join(error.args).replace(self.COMMAND_SEPERATOR, '')

            message = name + ': ' + text
        else:
            message = str(error)

        command = template.format(message=message.encode('utf-8'),
                                  sep=self.COMMAND_SEPERATOR)

        try:
            self.request.sendall(command)
        except OSError:
            self.log.debug("Error couldn't be sent.")

    def finish(self):
        # Unregister client
        if self.client_data:
            role = self.client_data.role
            try:
                with self.Locks.clients:
                    self.clients[role.value].remove(self.client_data)
            except ValueError:
                self.log.debug("Client data wasn't found for removal." +
                               "(likely not registered)")

            self.log.info("Unregistered")

            # ---- Send user update
            # Update user lists of all clients
            with self.Locks.clients:
                for dummy, client_list in self.clients.items():
                    for client in client_list:
                        try:
                            client.handler.send_update()
                        except OSError:
                            # client disconnected
                            pass
                        except Exception as error:
                            self.log.debug(
                                f"Couldn't update because {str(error)}")

    @classmethod
    def check_version(cls, version_str: str) -> bool:
        """
        Check wether a version string represents a compatible version number.

        Parameters
        ----------
        version_str : str
            the received version string.

        Raises
        ------
        RequestRefusedError
            The version number is invalid.

        Returns
        -------
        bool
            Wether the version is compatible.

        """
        try:
            vers = version.SemanticVersion.parse(version_str)
        except:
            raise RequestRefusedError(
                f"Invalid version number {version_str}") from None

        if vers.major != VERSION.major or vers.minor != VERSION.minor:
            return False

        return True

    @classmethod
    def get_client_list(cls):
        """
        Get a list of the connected clients.

        Returns
        -------
        client_list : list of ClientData
            a list of the clients.

        """
        clientl = []
        for role in cls.clients:
            clientl += cls.clients[role]

        return clientl


class Server(AbstractServer):
    """
    A Server ectec clients can connect to.

    Parameters
    ----------
    requesthandler : BaseRequestHandler, optional
        The request handler for the TCPServer.
        Needs a `get_client_list` static/class method.
        The default is ClientHandler.

    Attributes
    ----------
    users : list of (str, Role, *)
        list of users as name, role pairs
    hostname : str
        hostname of the server.
    address : str
        ip address of the server.
    port : int
        the port of the server.

    Notes
    -----
    The `bind` method is a synonym for the `start` method.
    """
    version = VERSION

    def __init__(self, requesthandler=ClientHandler):
        """
        Init the instance.

        Parameters
        ----------
        requesthandler : BaseRequestHandler, optional
            The request handler for the TCPServer.
            Needs a `get_client_list` static/class method.
            The default is ClientHandler.

        Returns
        -------
        None.

        """
        super().__init__()

        self.requesthandler_class = requesthandler

        self.__ip = None
        self.__port = None
        self.__users = None

        # Holds the thread running TCPServer.serve_forever
        self._serve_thread = None

        # Holds the ThreadingTCPServer
        self._server = None

    @property
    def hostname(self):
        """
        Get the contents of the hostname property.

        Returns
        -------
        str
            The hostname of the maschine.

        """
        return socket.gethostname()

    @property
    def address(self):
        """
        Get the contents of the ip property.

        Returns
        -------
        str
            The (ip) address of the server/maschine.

        """
        if not self._server:
            return socket.gethostbyname(self.hostname)

        return self._server.server_address[0]

    @property
    def port(self):
        if not self._server:
            raise AttributeError(
                "Server not runnning.")
        return self._server.server_address[1]

    @property
    def users(self):
        """
        Get the list of users

        Returns
        -------
        list of ClientData
            namedtuple for each client.

        """
        return self.requesthandler_class.get_client_list()

    @property
    def running(self):
        """
        Get the contents of the running property.

        Returns
        -------
        bool

        """
        return self._serve_thread and self._serve_thread.is_alive()

    def start(self, port: str, address: str = ""):
        """
        Start the server at the given port and address.

        Parameters
        ----------
        port : str
            the port.
        address : str
            The address. Defaults to an empty string.

        Returns
        -------
        ServerRunningContext
            A context object for closing the server.

        """
        server = socketserver.ThreadingTCPServer((address, port),
                                                 self.requesthandler_class)
        self._server = server

        self._serve_thread = threading.Thread(target=server.serve_forever)
        self._serve_thread.start()

        return type('ServerRunningContext', (),
                    {'__enter__': (lambda x: x),
                     '__exit__': (lambda *args: self.stop())
                     })()

    def stop(self):
        """
        Stops the server.

        Returns
        -------
        None.

        """
        if self._server:
            self._server.shutdown()
            self._server.server_close()
