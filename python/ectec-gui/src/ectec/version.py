#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versioning in Python.

@version: 0.0


***********************************

Created on Fri Feb 26 16:49:40 2021

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

from functools import total_ordering


class VersionException(Exception):
    """
    Superclass of all Exceptions related to versions
    """

class Version:
    """
    The superclass of all Versions.

    This class is intended for type annotations
    """


class SemanticVersionException(VersionException):
    """
    Exception related to semantic version numbers
    """


class SubVersionException(SemanticVersionException):
    """
    Raise if there are too many subversions in a semantic version.
    """

@total_ordering
class SemanticVersion(Version):
    """
    Implementation of a Semantic Version Number.

    Notes
    -----

    Given a version number MAJOR.MINOR.PATCH, increment the:

    MAJOR version when you make incompatible API changes,
    MINOR version when you add functionality in a backwards compatible manner,
    PATCH version when you make backwards compatible bug fixes.

    Additional labels for pre-release and build metadata are available as
    extension to the MAJOR.MINOR.PATCH format.

    Labels for pre-release versions may be appended using a hyphen `-`.
    Build metadata may be denoted by appending it after a plussign `+`.

    """

    def __init__(self, major, minor, patch, label=''):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.label = label
        self.metadata = ''

    def add_metadata(self, metadata):
        self.metadata = metadata

    def __repr__(self):
        return '<SemanticVersion \'{}\' >'.format(str(self))

    def __str__(self):
        main = str(self.major) + '.' + str(self.minor) + '.' + str(self.patch)
        label = '-' + str(self.label) if self.label else ''
        metadata = '+' + str(self.metadata) if self.metadata else ''
        return main + label + metadata

    def __gt__(self, other):
        a = self.major == other.major
        b = self.minor == other.minor
        c = self.major > other.major
        d = self.minor > other.minor
        e = self.patch > other.patch
        l = not (self.label or other.label)
        return c or (a and (d or (b and e and l)))

    def __eq__(self, other):
        a = self.major == other.major
        b = self.minor == other.minor
        c = self.patch == other.patch
        d = self.label == other.label
        return a and b and c and d

    def equals(self, other):
        """
        Test wether two SemanticVersion are identical.

        Parameters
        ----------
        other : SemanticVersion
            the other version number.

        Returns
        -------
        boolean
            the return value.

        """
        a = self.major == other.major
        b = self.minor == other.minor
        c = self.patch == other.patch
        d = self.label == other.label
        e = self.metadata == other.metadata
        return a and b and c and d and e

    @classmethod
    def parse(cls, string: str) -> 'SemanticVersion':
        """
        Parses a string describing a semantic version number.

        It creates a SemanticVersion objekt representing
        the same version number as the string.

        Parameters
        ----------
        string : str
            the string representing the version number.

        Raises
        ------
        SubVersionException
            In case of too many subversion numbers.

        Returns
        -------
        SemanticVersion
            The objekt.

        """

        string = string.strip()
        major = ''
        minor = ''
        patch = ''
        label = ''
        metadata = ''

        seq = 0
        for s in string:
            if seq == 0:
                # major
                if s == '.':
                    seq += 1
                elif s == '-':
                    seq = 3
                elif s == '+':
                    seq = 4
                elif s.isdigit():
                    major += s

            elif seq == 1:
                # minor
                if s == '.':
                    seq += 1
                elif s == '-':
                    seq = 3
                elif s == '+':
                    seq = 4
                elif s.isdigit():
                    minor += s

            elif seq == 2:
                # patch
                if s == '.':
                    raise SubVersionException('More than 3 subversions')

                if s == '-':
                    seq = 3
                elif s == '+':
                    seq = 4
                elif s.isdigit():
                    patch += s

            elif seq == 3:
                # label
                if s == '+':
                    seq = 4
                elif not s.isspace():
                    label += s

            else:
                if not s.isspace():
                    metadata += s

        major = int(major) if major else 0
        minor = int(minor) if minor else 0
        patch = int(patch) if patch else 0

        objekt = cls(major, minor, patch, label)
        objekt.add_metadata(metadata)

        return objekt
