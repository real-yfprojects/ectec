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
from typing import Callable, Iterable, List, Optional, Union

from . import (VERSION, AbstractPackage, AbstractPackageStorage,
               AbstractUserClient, Role)


class Package(AbstractPackage):
    """
    A package being sent using ectec.

    This class is used by the PackageStorage.

    Parameters
    ----------
    sender : str
        The user who sends the package.
    recipient : str or list of str
        The user(s) this package is sent to.
    type : str
        The content type.
    time : float, optional
        The time the package was received. The default is None.

    Attributes
    ----------
    sender : str
        The user who sends the package.
    recipient : list of str
        The users this package is sent to.
    type : str
        The content type.
    content : bytes
        The body of the package.
    time : TYPE
        The time the package was received. Might be None.

    """

    __slots__ = []

    def __init__(self, sender: str, recipient: Union[str, List[str]],
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
        self.sender = sender
        self.type = typ
        self.content = b''

        # handle `recipient` types
        if isinstance(recipient, str):
            self.recipient = [recipient]
        else:
            self.recipient = list(recipient)

        # handle `time` types
        if time is None:
            self.time = None
        elif isinstance(time, (float, int)):
            self.time = datetime.datetime.fromtimestamp(time)
        elif isinstance(time, datetime.datetime):
            self.time = time
        else:
            raise TypeError(f"Unsupported type for `time`: {type(time)}")

    def __hash__(self):
        return hash(
            (self.sender, self.recipient, self.type, self.time, self.content))

    def __eq__(self, o):
        if not isinstance(o, AbstractPackage):
            return False

        return self.sender == o.sender and self.recipient == o.recipient and \
            self.type == o.type and self.content == o.content and \
            self.time == o.time


class PackageStorage(AbstractPackageStorage):
    """
    A storage and a manager for packages.
    """

    def __init__(self):
        self.package_list: List[Package] = []

    def remove(self, *packages: Package,
               func: Callable[[Package], bool] = None) -> int:
        """
        Remove packages from the storage.

        If `packages` is specified this method returns the number of
        packages in `packages` that could not be removed. The `func` function
        gets passed an `Package` if the function returns `True` the package is
        removed. If you pass both packages and a function all packages matching
        one of them will be removed.

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

    def add(self, *packages: AbstractPackage):
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
        self.package_list.extend(packages)

    def all(self) -> Iterable[AbstractPackage]:
        """
        Return a list of all packages in the PackageStorage.

        If not modified the packages are ordered in the order they were added
        to the PackageStorage.

        Returns
        -------
        List of Package.

        """

        return copy.copy(self.package_list)

    def filter(self, func: Callable[[AbstractPackage], bool] = None,
               **kwargs) -> Iterable[AbstractPackage]:
        """
        Return a filtered list of the packages in the PackageStorage.

        This functions returns an iterable yielding all packages that
        have a positive return value when passing or that match all the
        `kwargs`. The keywords are checked first.

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
        # the list is iterated faster than the view
        kwargs_items = list(kwargs.items())

        for pkg in self.package_list:
            for keyword, value in kwargs_items:
                if not hasattr(pkg, keyword) or getattr(pkg, keyword) != value:
                    break
            else:
                yield pkg
                continue

            if func(pkg):
                yield pkg
