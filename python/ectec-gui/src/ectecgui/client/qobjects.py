#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implement QObjects needed for the client module.

That includes model, views or validators for the `wConnect.ConnectWindow`.

***********************************

Created on 2021/09/07 at 17:13:54

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
import re
from typing import Tuple

from PyQt5.QtGui import QValidator

from . import logger

# ---- Validators ------------------------------------------------------------

# host name re as specified in https://www.rfc-editor.org/rfc/rfc952 as hname
name = r"(?!-)[a-zA-Z0-9-]+(?<!-)"  # may not start or end with a hyphen
hname = r"({name}.?)+".format(name=name)
regex_hname = re.compile(hname)


class AddressValidator(QValidator):
    """
    Validate a address a socket can connect to.

    That can be an IP address or a domain-/hostname.
    """
    def __init__(self, parent=None, dn_allowed=True) -> None:
        """
        Init.

        Parameters
        ----------
        parent : QObject, optional
            The parent, by default None
        dn_allowed : bool, optional
            Whether domain names are allowed, by default True
        """
        super().__init__(parent=parent)
        self.dn_allowed = dn_allowed

    def validate(self, input: str,
                 pos: int) -> Tuple[QValidator.State, str, int]:
        """Validate the address"""
        if not input:
            return QValidator.Intermediate, input, pos

        if not (len(input) < 255 and regex_hname.fullmatch(input)):
            return QValidator.Invalid, input, pos

        return QValidator.Acceptable, input, pos


class UsernameValidator(QValidator):
    """
    Validator for user names.

    Parameters
    ----------
    parent : QObject, optional
        The parent object, by default None
    max_length : int, optional
        The maximum length for the user name, by default None
    """
    def __init__(self, parent=None, max_length=None) -> None:
        """
        Init validator.


        Parameters
        ----------
        parent : QObject, optional
            The parent object, by default None
        max_length : int, optional
            The maximum length for the user name, by default None
        """
        super().__init__(parent=parent)
        self.max_length = max_length

        #: The regex defining the characters of a clients name
        self.regex_name = re.compile(r"\w{}".format(
            '{{1,{}}}'.format(max_length) if max_length else '+'))

    def validate(self, input: str,
                 pos: int) -> Tuple[QValidator.State, str, int]:
        """
        Validate the input string.

        This method checks whether the input is a valid user name of
        the maximum size `max_length`.

        Parameters
        ----------
        input : str
            The input of the user.
        pos : int
            The cursor position.

        Returns
        -------
        Tuple[QValidator.State, str, int]
            The validation state, the (changed) input and
            the (changed) cursor position.
        """
        # no spaces allowed but underscores are.
        input = input.lstrip().replace(' ', '_')

        if not input:
            return (self.State.Intermediate, input, pos)

        # enforce max length
        if self.max_length:
            input = input[:self.max_length]

        # check whether the characters are valid.
        if self.regex_name.fullmatch(input):
            return (self.State.Acceptable, input, pos)
        else:
            return (self.State.Invalid, input, pos)
