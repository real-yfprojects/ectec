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
from typing import Callable, Iterator, Iterable, List, Optional, Union

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
            self.recipient = (recipient)
        else:
            self.recipient = tuple(recipient)

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

    def remove(self, *packages: Package,
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

    def add(self, *packages: Union[Package, List[Package]],
            as_list: Optional[List[Package]] = None) -> None:
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
            raise ValueError('Expected Package not list for `*packages`.')

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

    def filter(self, func: Optional[Callable[[Package], bool]] = None,
               **kwargs) -> Iterator[Package]:
        """
        Return a filtered list of the packages in the PackageStorage.

        This functions returns an iterable yielding all packages that
        have a positive return value when passing to `func` OR
        that match all the `kwargs`. The keywords are checked first.

        Parameters
        ----------
        func : callable(Package) -> bool, optional
            A function acting as a filter.
        **kwargs : Any.
            Attributes of Package that should match.

        Returns
        -------
        Iterator over the packages.

        """
        # the list is iterated faster than the view
        kwargs_items = list(kwargs.items())

        for pkg in self.package_list:
            if kwargs:
                for keyword, value in kwargs_items:
                    if not hasattr(pkg, keyword) or \
                            getattr(pkg, keyword) != value:
                        break
                else:
                    yield pkg
                    continue

            if func and func(pkg):
                yield pkg
