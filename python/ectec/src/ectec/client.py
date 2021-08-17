#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The client api is implemented here.


***********************************

Created on Thu Mar  4 17:28:57 2021

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
import copy
import datetime
import re
import socket
import threading
import time
from typing import Callable, Iterator, List, Optional, Union

from . import (VERSION, AbstractPackage, AbstractPackageStorage,
               AbstractUserClient, Address, ConnectException, EctecException,
               Role, logs)

# ---- Logging

logger = logs.getLogger(__name__)


class ClientAdapter(logs.logging.LoggerAdapter):
    """
    Adapter to add client context information.

    A given message `msg` is added the ip address of the client and
    transformed to:
    ::
        |{ip_address}| {msg}

    Parameters
    ----------
    logger : logging.Logger or logging.LoggerAdapter
        The interface for logging.
    remote : (ip, port)
        The address tuple of the remote.
    extra : dict, optional
        More context. The default is None.

    """
    def __init__(self, logger, client_type: str, extra=None):
        """
        Adapter to add connection context information.

        Parameters
        ----------
        logger : logging.Logger or logging.LoggerAdapter
            The interface for logging.
        remote : (ip, port)
            The address tuple of the remote (client).
        extra : dict, optional
            More context. The default is {}.


        """
        super().__init__(logger,
                         (extra if extra else {}).update({'ct': client_type}))
        self.client_type = client_type

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
        msg = "[{}] {msg}".format(self.client_type, msg=msg)
        return super().process(msg, kwargs)


# ---- Package Managment


class Package(AbstractPackage):
    """
    A package being sent using ectec.

    This class is used by the PackageStorage. The content has to be assigned
    to the `content` attribute after initialization.

    Parameters
    ----------
    sender : str
        The user who sends the package.
    recipient : str or iterable of str
        The user(s) this package is sent to.
    type : str
        The content type.
    time : float or datetime.datetime, optional
        The time the package was received. The default is None.

    Attributes
    ----------
    sender : str
        The user who sends the package.
    recipient : tuple of str
        The users this package is sent to.
    type : str
        The content type.
    content : bytes
        The body of the package.
    time : datetime.datetime
        The time the package was received. Might be None.

    """

    __slots__ = ['__time']

    def __init__(self,
                 sender: str,
                 recipient: Union[str, List[str]],
                 typ: str,
                 time: Optional[Union[float, datetime.datetime]] = None):
        """
        Init.

        Parameters
        ----------
        sender : str
            The user who sends the package.
        recipient : str or list of str
            The user(s) this package is sent to.
        type : str
            The content type.
        time : float or datetime.datetime, optional
            The time the package was received. The default is None.

        """
        super().__init__(sender, recipient, typ)
        self.sender = sender
        self.type = typ
        self.content = b""
        self.time = time

        # handle `recipient` types
        if isinstance(recipient, str):
            self.recipient = (recipient, )
        else:
            self.recipient = tuple(recipient)

    @property
    def time(self):
        """
        Get the `time` property.

        Returns
        -------
        datetime.datetime or None
            The time the package was received.

        """
        return self.__time

    @time.setter
    def time(self, value):
        """
        Set the `time` property

        Parameters
        ----------
        value : None, number or datetime.datetime
            DESCRIPTION.

        Raises
        ------
        TypeError
            Tried to set to an unsupported type.

        """
        # handle `time` types
        if value is None:
            self.__time = None
        elif isinstance(value, (float, int)):
            self.__time = datetime.datetime.fromtimestamp(value)
        elif isinstance(value, datetime.datetime):
            self.__time = value
        else:
            raise TypeError(f"Unsupported type for `time`: {type(time)}")

    def __hash__(self):
        return hash(
            (self.sender, self.recipient, self.type, self.time, self.content))

    def __eq__(self, o):
        if not isinstance(o, AbstractPackage):
            return False

        return (self.sender == o.sender and self.recipient == o.recipient
                and self.type == o.type and self.content == o.content
                and self.time == o.time)

    def __str__(self):
        if not self.time:
            template = "<Package type={} sender={} recipients={}>"
            return template.format(self.type, self.sender, str(self.recipient))

        template = "<Package type={} sender={} recipients={} time={}>"
        return template.format(self.type, self.sender, str(self.recipient),
                               str(self.time.timestamp()))

    def __repr__(self):
        return str(self)


class PackageStorage(AbstractPackageStorage):
    """
    A storage and a manager for packages.

    The `PackageStorage` supports the in-statement to check wether the storage
    contains a package. It also supports the `len` function to get the number
    of packages stored. And the `PackageStorage` is an iterable.

    Examples
    --------
    >>> storage = PackageStorage()
    >>> storage.add(package1, package2)
    >>> storage.add(as_list=[package3, package4])
    >>> storage.all()
    [<Package 1>, <Package 2>, <Package 3>, <Package 4>]

    A PackageStorage is created. Two already instanciated `Package`s are
    added to the storage. Then a list of packages is added to the storage
    After that the `all` method is called. It returns a list
    of all packages in the storage.

    >>> storage.remove(package2)
    >>> for pkg in storage:
    ...     print(pkg)
    <Package 1>
    <Package 3>
    <Package 4>

    Now `package2` is removed from the storage in the first example. Then
    a for-loop iterates over all the packages in the storage and prints them.

    >>> len(storage)
    3

    The storage now only contains three packages.

    >>> for pkg in storage.filter(sender='somesender'):
            print(pkg)
    <Package 1>

    The for-loop iterates over all the packages yielded by the `filter` method.
    The method filters out all the Packages in the storage that have a sender
    called 'somesender'. In this case that's only `package1`.

    """
    def __init__(self):
        """
        Init.

        """
        self.package_list: List[Package] = []

    def __contains__(self, package: Package):
        """
        Test wether this PackageStorage contains the given package.

        This magic method is called when the `in` statement is used.

        Parameters
        ----------
        package : Package
            The package to search for.

        Returns
        -------
        bool
            Wether this PackageStorage contains the package.

        Examples
        --------
        >>> package = Package('sender', 'recipient', 'type')
        >>> mystorage = PackageStorage()
        >>> if package in mystorage:
        ...     print("Package was already added to the PackageStorage.")

        This example creates a PackageStorage and a Package. If the package is
        contained by the PackageStorage a statement is printed to the output.
        In this case the package isn't in the PackageStorage.

        """
        return package in self.package_list

    def __iter__(self):
        """
        Get an iterator for iterating over the PackageStorage.

        This magic method is called if your call `iter` on the instance or
        us it in an `for` statement.

        Examples
        --------
        >>> mystorage = PackageStorage()
        >>> for package in mystorage:
        ...     print(package)

        Print out every package in the Packagestorage. The `__iter__` method
        is called to get the packages in the for-loop.

        """
        return iter(self.package_list)

    def __len__(self):
        """
        Get the number of packages in this PackageStorage.

        This method is called if you call `len` on an instance.

        Returns
        -------
        Int.

        """
        return len(self.package_list)

    def remove(self,
               *packages: Package,
               func: Callable[[Package], bool] = None) -> None:
        """
        Remove packages from the storage.

        All packages that equal the packages directly specified are removed.
        The function acts as a filter. The `func` function gets passed
        an `Package` if the function returns `True` the package is removed.
        If you pass both packages and a function all packages matching
        one of them will be removed.

        Parameters
        ----------
        *packages : Package (optional)
            Packages to be removed.
        func : callable(Package) -> bool, optional
            A function acting as a filter.

        """
        packages = set(packages)
        new_list = []
        if func:
            for pkg in self.package_list:
                if pkg not in packages and not func(pkg):
                    new_list.append(pkg)

        else:
            for pkg in self.package_list:
                if pkg not in packages:
                    new_list.append(pkg)

        self.package_list = new_list

    def add(
        self,
        *packages: Union[Package, List[Package]],
        as_list: Optional[List[Package]] = None,
    ) -> None:
        """
        Add packages to the PackageStorage.

        Parameters
        ----------
        *packages : Package
            The packages.
        as_list : List[Package], optional
            The packages in a list. The default is None.

        Returns
        -------
        None.

        """
        if packages and isinstance(packages[0], list):
            raise ValueError("Expected Package not list for `*packages`.")

        self.package_list.extend(packages)
        if as_list:
            self.package_list.extend(as_list)

    def all(self) -> List[Package]:
        """
        Return a list of all packages in the PackageStorage.

        If not modified the packages are ordered in the order they were added
        to the PackageStorage.

        Returns
        -------
        List of Package.

        """

        return copy.copy(self.package_list)

    def filter(self,
               func: Optional[Callable[[Package], bool]] = None,
               **kwargs) -> Iterator[Package]:
        """
        Filter the packages in the PackageStorage.

        This functions returns an iterable yielding all packages that
        have a positive return value when passing to `func` AND
        match all the `kwargs`. The keywords are checked first.
        The PackageStorage isn't changed.

        Parameters
        ----------
        func : callable(Package) -> bool, optional
            A function acting as a filter.
        **kwargs : Any.
            Attributes of Package that should match.

        Yields
        ------
        Package
            The packages matching the filter.

        """
        # the list is iterated faster than the view
        kwargs_items = list(kwargs.items())

        for pkg in self.package_list:
            for keyword, value in kwargs_items:
                if not hasattr(pkg, keyword) or getattr(pkg, keyword) != value:
                    break
            else:
                if (not func) or (func and func(pkg)):
                    yield pkg

    def filter_recipient(self, *recipients: str):
        """
        Filter out the packages that have one of the given recipients.

        This method exists for greater performance.

        Parameters
        ----------
        *recipients : str
            The allowed recipients.

        Yields
        ------
        Package
            The packages.

        """
        for pkg in self.package_list:
            for recipient in recipients:
                if recipient in pkg.recipient:
                    yield pkg
                    break  # breaks inner loop


# ---- Client - General


class ConnectionClosed(EctecException):
    """
    The connection was closed.
    """


class CommandError(EctecException):
    """
    There was a problem handling a command.
    """


class CommandTimeout(CommandError):
    """
    The receiving of a command timed out.
    """


class Client:
    """
    The superclass of all clients.

    This class provides methods useful for all Ectec clients.
    """

    TIMEOUT = 1000  #: ms timeout for awaited commands

    TRANSMISSION_TIMEOUT = 0.200  #: seconds of timeout between parts
    COMMAND_TIMEOUT = 0.300  #: s timeout for a command to end
    SOCKET_BUFSIZE = 8192  #: bytes to read from socket at once
    COMMAND_SEPERATOR = b'\n'  #: seperates commands of the ectec protocol
    COMMAND_LENGTH = 4096  #: bytes - the maximum length of a command

    def __init__(self):
        self.socket: socket.SocketType = None
        self._buffer = b""

    def recv_bytes(self, length, start_timeout=None, timeout=None) -> bytes:
        """
        Receive a specified number of bytes.

        Parameters
        ----------
        length : int
            The number of bytes.
        start_timeout : int, optional
            The timeout in s for receiving first data. The default is None.
        timeout : int, optional
            The timeout in s for all data to be received. The default is None.

        Raises
        ------
        CommandTimeout
            The data timed out.
        ConnectionClosed
            The connection was closed unexpectedly.

        Returns
        -------
        bytes
            The received bytes.

        """
        if length < 1:
            return b''

        msg = self._buffer
        self._buffer = bytes(0)
        bufsize = self.SOCKET_BUFSIZE

        if len(msg) < 1:
            # buffer empty -> command not incoming yet
            self.socket.settimeout(start_timeout)

            try:
                msg = self.socket.recv(bufsize)  # msg was empty
            except socket.timeout as error:
                raise CommandTimeout(
                    "The receiving of the data timed out.") from error

            if not msg:
                # connection was closed
                raise ConnectionClosed("The connection was closed.")

        if len(msg) >= length:  # separator found
            data = msg[:length]
            self._buffer = msg[length:]

            return data

        # Data wasn't received completely yet.
        self.socket.settimeout(self.TRANSMISSION_TIMEOUT)

        # read out the most precice system clock for timeouting
        start_time = time.perf_counter_ns()

        # convert timeout to ns (nanoseconds)
        timeout = timeout * 0.000000001 if timeout is not None else None

        data_length = len(msg)
        needed = length - data_length
        while True:  # ends by an error or a return
            try:
                part = self.socket.recv(bufsize)
            except socket.timeout as error:
                raise CommandTimeout("Data parts timed out.") from error

            if not part:
                # connection was closed
                raise ConnectionClosed("The connection was closed.")

            time_elapsed = time.perf_counter_ns() - start_time

            part_length = len(part)

            if part_length >= needed:
                data = msg + part[:needed]
                self._buffer = part[needed:]
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

    def recv_command(self,
                     max_length,
                     start_timeout=None,
                     timeout=None) -> bytes:
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
        ConnectionClosed
            The connection was closed unexpectedly.

        Returns
        -------
        command : bytes
            The command.

        """
        msg = self._buffer
        self._buffer = bytes(0)
        seperator = self.COMMAND_SEPERATOR
        bufsize = self.SOCKET_BUFSIZE

        if len(msg) < 1:
            # buffer empty -> command not incoming yet
            self.socket.setblocking(True)
            self.socket.settimeout(start_timeout)

            try:
                msg = self.socket.recv(bufsize)  # msg was empty
            except socket.timeout as error:
                raise CommandTimeout(
                    "The receiving of the command timed out.") from error

            if not msg:
                # connection was closed
                raise ConnectionClosed("The connection was closed.")

        # check buffer or first data received
        i = msg.find(seperator)

        if i >= 0:  # separator found
            command = msg[:i]
            self._buffer = msg[i + len(seperator):]  # seperator is removed

            # for expected behavoir check length of command
            cmd_length = len(command)
            if cmd_length > max_length:
                raise CommandError(f"Command too long: {cmd_length} bytes" +
                                   f" from {max_length}")

            return command

        # Command wasn't received completely yet.
        self.socket.setblocking(True)
        self.socket.settimeout(self.TRANSMISSION_TIMEOUT)

        # read out the most precice system clock for timeouting
        start_time = time.perf_counter_ns()

        # convert timeout to ns (nanoseconds)
        timeout = timeout * 0.000000001 if timeout is not None else None

        length = len(msg)
        while True:  # ends by an error or a return
            try:
                part = self.socket.recv(bufsize)
            except socket.timeout as error:
                raise CommandTimeout("Command parts timed out.") from error

            if not part:
                # connection was closed
                raise ConnectionClosed("The connection was closed.")

            time_elapsed = time.perf_counter_ns() - start_time

            i = part.find(seperator)  # end of command?
            if i >= 0:  # separator found
                command = msg + part[:i]
                # seperator is removed
                self._buffer = part[i + len(seperator):]

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
    regex_info = re.compile(r"INFO (True|False) ([\w.\-+]+)")

    def parse_info(self, command):
        """
        Parse wether a command is an INFO command.

        If it is an INFO command it is also processed.

        ::

            INFO (True|False) ([\\w.\\-+]+)
                 ----------
                 version number


        Returns
        -------
        bool or str
            False or wether the version was accepted and
            the sent version number of the server.

        Examples
        --------
        >>> raw_cmd = self.recv_command(4096, 0.2, self.COMMAND_TIMEOUT)
        >>> cmd = raw_cmd.decode(encoding='utf-8', errors='backslashreplace')
        >>> res = client.parse_info(cmd)
        >>> if res:
        ...     if res[0]:
        ...         print("Accepted")
        ...     else:
        ...         print("Incompatible version", res[1])

        A command is received and decoded using UTF-8. Then the command is
        parsed. If it is an INFO command the `accepted` attribute is checked.
        If the version wasn't accepted the version of the server is printed.

        """
        # fullmatch regular expression
        match = self.regex_info.fullmatch(command)

        if not match:
            return False

        accepted = match.group(1).lower() == "True".lower()

        return accepted, match.group(2)

    # regular expression for the UPDATE USERS command
    regex_update = re.compile(r"UPDATE USERS (\d+)")

    def parse_update(self, command: str):
        """
        Parse and handle a update command.

        The command is only handled if it is an UPDATE USERS command. In that
        case the list of users is received and returned. If the command isn't
        a user command `False` is returned.

        .. warning:: The returned list might be empty.

        Parameters
        ----------
        command : str
            DESCRIPTION.

        Returns
        -------
        bool or List[str]
            False or list of names.

        Examples
        --------

        >>> raw_cmd = self.recv_command(4096, 0.2, self.COMMAND_TIMEOUT)
        >>> cmd = raw_cmd.decode(encoding='utf-8', errors='backslashreplace')
        >>> res = client.parse_update(cmd)
        >>> if res is not False:
        ...     print('\\n'.join(res))
        name1
        name2
        name3

        """
        # fullmatch regular expression
        match = self.regex_update.fullmatch(command)

        if not match:
            return False

        length = int(match.group(1))
        # Keep the timeout between 0.3 and 5
        timeout = min(max(length * 2e-07, 0.3), 5)

        data = self.recv_bytes(length, 0.2, timeout)
        if data:
            names = data.decode('utf-8', errors="backslashreplace").split(" ")
        else:
            names = []

        return names

    # regular expression for the PACKAGE command
    regex_package = re.compile(
        r"PACKAGE ([\w/.-]+) FROM ([\w]+) TO ([\w,]+) WITH (\d+)")

    def parse_package(self, command: str):
        """
        Parse and handle a PACKAGE command.

        The content of the command is received if it is a PACKAGE command.

        Parameters
        ----------
        command : str
            The received command.

        Returns
        -------
        bool or Package
            False or the package without timestamp.

        Examples
        --------

        >>> raw_cmd = self.recv_command(4096, 0.2, self.COMMAND_TIMEOUT)
        >>> cmd = raw_cmd.decode(encoding='utf-8', errors='backslashreplace')
        >>> res = client.parse_update(cmd)
        >>> if res:
        ...     # Package command received
        ...     print(res)
        <Package ...>

        """
        match = self.regex_package.fullmatch(command)

        if not match:
            return False

        content_type = match.group(1)
        sender = match.group(2)
        recipients = match.group(3).split(',')

        length = int(match.group(4))

        # Keep the timeout between 0.3 and 5
        timeout = min(max(length * 2e-07, 0.3), 5)

        data = self.recv_bytes(length, 0.2, timeout)

        package = Package(sender, recipients, content_type)
        package.content = data

        return package

    # regular expression for the ERROR command
    regex_error = re.compile(r"ERROR (.*)")

    def parse_error(self, command: str):
        """
        Parse a received command to now wether it is an ERROR command.

        If the `command` is not an ERROR command `False` is returned else
        the error message is returned.

        Parameters
        ----------
        command : str
            The decoded command.

        Returns
        -------
        bool or str
            False or the error message.

        """
        # match regular expression
        match = self.regex_error.fullmatch(command)

        if not match:
            return False
        return match.group(1)

    def send_command(self,
                     command: str,
                     data: bytes = b'',
                     errors='backslashreplace'):
        """
        Send a command containing the given string.

        Parameters
        ----------
        command : str
            The command.
        data : bytes, optional
            Bytes to be appended to the command. The default is `b''`.
        errors : str, optional
            The error handler for encoding of the string.
            The default is 'backslashreplace'.

        """

        command_bytes = command.encode('utf-8', errors=errors)

        self.socket.sendall(command_bytes + self.COMMAND_SEPERATOR + data)

    def send_info(self, version_str):
        """
        Send an INFO command.

        Parameters
        ----------
        version_str : str
            A string representing the version of the client.

        Raises
        ------
        ValueError
            Bad version string.

        """
        if not re.fullmatch(r'[\w.\-+]+', version_str):
            raise ValueError("Version string doesn't match `[\\w.-+]+`.")

        command = "INFO {version}".format(version=version_str)
        self.send_command(command)

    def send_register(self, name, role):
        """
        Send a REGISTER command with the given name and role.

        Parameters
        ----------
        name : str
            The name to register as.
        role : str
            The role to register as.

        Raises
        ------
        ValueError
            Bad name or role.

        """
        if not re.fullmatch(r'\w+', name):
            raise ValueError("Name doesn't match `\\w+`.")
        if not re.fullmatch(r'\w+', role):
            raise ValueError("Role doesn't match `\\w+`.")

        command = "REGISTER {name} AS {role}".format(name=name, role=role)
        self.send_command(command)

    def send_package(self, package):
        """
        Send a PACKAGE command containing the given package.

        Parameters
        ----------
        package : Package
            The package to send.

        Raises
        ------
        ValueError
            Some attribute of the package is not legal.


        """
        recipient = ",".join(package.recipient)
        length = len(package.content)

        # check characters of parameters using regexes
        if not re.fullmatch(r'[\w/.-]+', str(package.type)):
            raise ValueError("Type of package does't match `[\\w/.-]+`.")
        if not re.fullmatch(r'\w+', str(package.sender)):
            raise ValueError("Sender of package does't match `\\w+`.")
        if not re.fullmatch(r'[\w,]+', str(recipient)):
            raise ValueError("Recipient of package does't match `[\\w,]+`.")

        template = "PACKAGE {typ} FROM {sender} TO {recipient} WITH {length}"
        command = template.format(typ=package.type,
                                  sender=package.sender,
                                  recipient=recipient,
                                  length=length)

        self.send_command(command, package.content)


# ---- User Client


class UserClientThread(threading.Thread):
    """
    Thread to do the UserClient receiving work.
    """
    def __init__(self, userclient: 'UserClient'):
        super().__init__(name="Ectec-UserClientThread")
        self.client: 'UserClient' = userclient
        self.end = threading.Event()
        self.idle = threading.Event()

        self.log = ClientAdapter(logger, userclient.role.name)

    def run(self):
        try:
            while not self.end.is_set():
                try:
                    # Recv a command
                    raw_cmd = self.client.recv_command(
                        4096, 0.2, self.client.COMMAND_TIMEOUT)
                    cmd = raw_cmd.decode(encoding='utf-8',
                                         errors='backslashreplace')

                    self.idle.clear()

                    # Handle PACKAGE command
                    res = self.client.parse_package(cmd)
                    if res:
                        # Handle package
                        package: Package = res
                        package.time = time.time()

                        self.client._add_package(package)
                        continue

                    # Handle UPDATE USERS command
                    res = self.client.parse_update(cmd)
                    if res is not False:  # in case of empty list
                        # update users
                        self.client._update_users(res)
                        continue

                    # Handle ERROR command
                    res = self.client.parse_error(cmd)
                    if res:
                        self.log.error("Server error: " + res)
                        continue

                    # Unkown command
                    self.log.error("Server sent unkown command: " +
                                   cmd[:min(6, len(cmd))] + "...")

                except CommandTimeout:
                    self.idle.set()
                except (CommandError) as error:
                    self.log.error("CommandError: " + str(error))

        except (ConnectionClosed, OSError) as error:
            self.log.warning(str(error))
            self.client._handle_closed()
        except Exception as error:
            self.log.exception("Local Exception in UserClientThread.")

        self.idle.set()


class UserClient(Client, AbstractUserClient):
    """
    A Client for the normal user role.

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
    def __init__(self, username: str):
        """
        A Client for the normal user role.

        Parameters
        ----------
        username : str
            The name for this client which is used as an identifier.

        """
        super().__init__()
        self.username: str = username
        self.role: Role = Role.USER
        self.users: List[str] = None
        self.packages: PackageStorage = PackageStorage()

        #: A buffer for processing packages. This is used by `receive`.
        self.buffer = []

        #: The socket connected to the server. Or None.
        self.socket = None

        #: The LoggerAdapter for logging
        self.log = ClientAdapter(logger, self.__class__.__name__)

        #: Thread for background tasks
        self._thread: threading.Thread = None

    @property
    def connected(self):
        """
        Get the `connected` property.

        Returns wether the background thread is still running. This thead
        is started on connect and stopped when the connection is closed.

        Returns
        -------
        bool
            Wether the client is connected to a ectec server.

        """
        return self._thread and self._thread.is_alive()

    @property
    def server(self):
        """
        Get the `server` property.

        If the client isn't connected to a server this property is None.

        Returns
        -------
        None or Address
            The address of the server the client is connected to.
        """
        if not self.connected or not self.socket:
            return None

        return Address._make(self.socket.getpeername())

    def _add_package(self, package: Package):
        self.buffer.append(package)
        self.packages.add(package)

    def _update_users(self, user_list: List[str]):
        self.users = user_list

    def _handle_closed(self):
        """
        Handle the closing of the connection.

        Returns
        -------
        None.

        """
        self.users = []

    class ConnectionContextManager:
        """
        Context manager for the context of the client connected to a server.

        This manager closes the connection when the context is left.
        """
        def __init__(self, client):
            self.client: UserClient = client

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            self.client.disconnect()

            # wether to raise the Exception or suppress
            return False  # do not suppress

    def connect(self, server: str, port: int):
        """
        Connect to a server.

        Parameters
        ----------
        server : str
            The ip or hostname.
        port : int
            The port to connect to.

        Raises
        ------
        OSError
            Server not online. (Connection error on the socket layer.)
        ConnectException
            The connection couldn't be established.

        Returns
        -------
        None.

        """
        self.socket = socket.create_connection((server, port))

        try:
            # send version number
            self.send_info(str(VERSION))

            # receive answer of the server
            # wether the version is accepted and the version of the server.
            raw_cmd = self.recv_command(4096, 0.2, self.COMMAND_TIMEOUT)
            cmd = raw_cmd.decode(encoding='utf-8', errors='backslashreplace')

            parsed = self.parse_info(cmd)
            if parsed:
                # It is a INFO command
                if not parsed[0]:
                    # not accepted -> not compatible
                    raise ConnectException(
                        "Server ({}, {})[{}] refused.".format(
                            server, port, parsed[1]))
            else:
                parsed = self.parse_error(cmd)
                if parsed:
                    raise ConnectException(
                        "Server sent error '{}'.".format(parsed))

                # unnecessary else after raise
                raise ConnectException(
                    "Server didn't follow the ectec protocol.")

            # accepted -> compatible
            self.log.info("Server ({}, {})[{}] accepted.".format(
                server, port, parsed[1]))

            # send register
            self.send_register(self.username, self.role.value)

            # Receive user list update
            raw_cmd = self.recv_command(4096, 0.5, self.COMMAND_TIMEOUT)
            cmd = raw_cmd.decode(encoding='utf-8', errors='backslashreplace')

            parsed = self.parse_update(cmd)
            if parsed is not False:
                # It is a UPDATE USERS command
                self.users = parsed
            else:
                # It isn't a UPDATE USERS command
                parsed = self.parse_error(cmd)
                if parsed:
                    raise ConnectException(
                        "Server sent error '{}'.".format(parsed))

                # unnecessary else after raise
                raise ConnectException(
                    "Server didn't follow the ectec protocol.")

            # Start thread
            self._thread = UserClientThread(self)
            self._thread.start()

        except (CommandError, ConnectionClosed) as error:
            self.socket.close()
            raise ConnectException(str(error)) from None
        except OSError as error:
            self.socket.close()
            raise ConnectException("SocketError on connecting.") from error
        except Exception as error:
            self.socket.close()
            raise error

        return self.ConnectionContextManager(self)

    def disconnect(self):
        """
        Disconnect from the server the client currently is connected to.

        This then allows connecting to a different server.

        Returns
        -------
        None.

        """
        if self._thread:
            self._thread.end.set()
            self._thread.join()

        if self.socket:
            self.socket.close()

        self.users = []

    def send(self, package: Package):
        """
        Send a package.

        Parameters
        ----------
        package : Package
            The package.

        Raises
        ------
        Exceptions related to sending if the package couldn't be sent.

        Returns
        -------
        None.

        """
        self.send_package(package)

    def _update(self):
        """
        Block until background thread is idle.

        The background thread sets a threading.Event if it considers itself
        as idle. This is normally the case if a timeout is reached when waiting
        for a new command from the server. This command should be used with
        care. It can (nearly) dead-lock the calling thread. This can happen if
        the server doesn't really stop sending.

        Returns
        -------
        None.

        """
        if self._thread and self._thread.is_alive():
            self._thread.idle.wait()

    def receive(
            self,
            n: int = None) -> Union[AbstractPackage, List[AbstractPackage]]:
        """
        Read out the buffer of Packages.

        The buffer contains all Packages that were received since the last
        time the buffer was read. The optional `n` specified how many packages
        should be removed from the buffer and returned. If `n=1` a Package is
        returned. If `n>1` a list of Packages is returned. If `n=None` or
        `n<1` all packages in the buffer are returned.

        Parameters
        ----------
        n : positive int, optional
            Number of packages to read out. The default is None.

        Returns
        -------
        Package or list of Package.

        """
        if not n:
            packages = self.buffer
            self.buffer = []
            return packages

        if n > 1:
            packages = self.buffer[:n]
            self.buffer = self.buffer[n:]
            return packages

        if n == 1:
            package = self.buffer[0]
            self.buffer = self.buffer[1:]
            return package

        raise ValueError("Cannot receive less than one package from buffer.")
