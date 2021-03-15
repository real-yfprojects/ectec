#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The core package of the ectec chattool.

The package provides all the lower level functionalities that can be used
by a GUI or other applications.


***********************************

Created on Wed Feb 17 12:13:03 2021

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

import enum
from typing import Callable, List, Union

from . import logs
from .version import SemanticVersion, Version

VERSION: Version = SemanticVersion(0, 0, 1)


# ---- Logging

logger = logs.getLogger(__name__)  # Parent logger for the module

nullhandler = logs.NullHandler()  # Bin for logs

handler = logs.StreamHandler()  # Output to console
handler.setLevel(logs.WARNING)  # Log everything with equal or greater level
formatter = logs.EctecFormatter()  # Control format of output
handler.setFormatter(formatter)  # Add formatter to handler

# Add Handlers to logger
logger.addHandler(nullhandler)
logger.addHandler(handler)

# ---- Exceptions


class EctecException(Exception):
    """
    Superclass of all Exceptions defined in the ectec API.
    """


class ConnectException(EctecException):
    """
    Raised if there is an error on the process of connecting to a server.
    """


class IncompatibleServer(ConnectException):
    """
    The server is not understandable using the used ectec protocoll.
    """


class IncompatibleVersion(ConnectException):
    """
    The client and the server have incompatible version numbers.
    """


# ---- Assets

class Package():
    """
    A package being sent using ectec.

    This class can be used before and after sending.

    Parameters
    ----------
    sender : str
        the user who sends the package.
    recipient : str
        the user this package is sent to.
    type : str
        the content type.
    time : float, optional
        the time the package was received. The default is None.

    Attributes
    ----------
    sender : TYPE
        the user who sends the package.
    recipient : TYPE
        the user this package is sent to.
    type : TYPE
        the content type.
    content : bytes or TYPE
        the body of the package.
    time : TYPE
        the time the package was received. Might be None.

    """

    def __init__(self, sender: str, recipient: str, type: str,
                 time: float = None):
        """

        A package being sent using ectec.

        This class can be used before and after sending.

        Parameters
        ----------
        sender : str
            the user who sends the package.
        recipient : str
            the user this package is sent to.
        type : str
            the content type.
        time : float, optional
            the time the package was received. The default is None.

        Attributes
        ----------
        sender : TYPE
            the user who sends the package.
        recipient : TYPE
            the user this package is sent to.
        type : TYPE
            the content type.
        content : bytes or TYPE
            the body of the package.
        time : float
            the time the package was received. Might be None.


        """

    @property
    def content(self):
        """Property content"""

        raise NotImplementedError("Must be implemented by subclasses")


class Role(enum.Enum):
    USER = "user"


# ---- Client API / Standard User

class PackageStorage:
    """
    Stores and manages packages.


    """

    def __init__(self):
        pass

    def remove(self, *packages: List[Package],
               func: Callable[[Package], bool] = None) -> int:
        """
        Remove packages from the storage.

        If `packages` is specified this method returns the number of
        packages in `packages` that could not be removed.

        Parameters
        ----------
        *packages : Package (optional)
            Packages to be removed.
        func : callable(Package) -> bool, optional
            A function acting as a filter.

        Returns
        -------
        Int.

        """
        return 0

    def add(self, *packages: List[Package]):
        """
        Add packages to the PackageStorage.

        Parameters
        ----------
        *packages : Package
            The packages.

        Returns
        -------
        None.

        """

    def all(self) -> List[Package]:
        """
        Return a list of all packages in the PackageStorage.

        If not modified the packages are ordered in the order they were added
        to the PackageStorage.

        Returns
        -------
        List of Package.

        """

        return []

    def filter(self, func: Callable[[Package], bool] = None,
               **kwargs) -> List[Package]:
        """
        Return a filtered list of the packages in the PackageStorage.

        Parameters
        ----------
        func : callable(Package) -> bool, optional
            A function acting as a filter.
        **kwargs : Any.
            Attributes of Package that should match.

        Returns
        -------
        list of Package.

        """
        return []


class UserClient:
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
    users : list of str
        list of users connected to the server.
    packages : PackageStorage
        The PackageStorage managing the received packages.

    """

    version = VERSION

    def __init__(self, username: str):
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
        users : list of str
            list of users connected to the server.
        packages : PackageStorage
            The PackageStorage managing the received packages.

        """
        self.username: str = username
        self.users: List[str]
        self.packages: PackageStorage

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
        ConnectException
            The connection couldn't be established.

        Returns
        -------
        None.

        """
        raise NotImplementedError("Must be implemented by subclasses")

    def disconnect(self):
        """
        Disconnect from the server the client currently is connected to.

        This then allows connecting to a different server.

        Returns
        -------
        None.

        """

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
        raise NotImplementedError("Must be implemented by subclasses")

    def receive(self, n: int = None) -> Union[Package, List[Package]]:
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
        raise NotImplementedError("Must be implemented by subclasses")

    @property
    def server(self):
        """
        Property `server`. Read only.

        """
        raise NotImplementedError("Must be implemented by subclasses")


# ---- Server API

class Server():
    """
    A Server ectec clients can connect to.

    Attributes
    ----------
    users : list of (str, Role)
        list of users as name, role pairs
    hostname : str
        hostname of the server
    ip : str
        ip address of the server

    Notes
    -----
    The `bind` method is a synonym for the `start` method.
    """
    version = VERSION

    def __init__(self):
        pass

    def start(self, port: str, address: str = None):
        """
        Start the server at the given port and address.

        Parameters
        ----------
        address : str
            the address.
        port : str
            the port.

        Returns
        -------
        None.

        """

    bind = start

    def stop(self):
        """
        Stops the server.

        Returns
        -------
        None.

        """
