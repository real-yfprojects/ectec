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

ip_group = r"([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
full_ip = r"^({group}\.){{3}}{group}$".format(group=ip_group)
regex_ip = re.compile(full_ip)

dn_group = r"([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])"
full_dn = r"({group}\.)*{group}".format(group=dn_group)
regex_dn = re.compile(full_dn)


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
        input = input.strip().replace(' ', '')

        if regex_ip.match(input) or (self.dn_allowed
                                     and regex_dn.match(input)):
            # valid
            logger.debug('Address valid')
            return (self.State.Acceptable, input, pos)

        # must be an intermediate ip address
        fixed = ''
        new_pos = pos

        group_number = 0
        group = ''
        group_added = True
        for i, c in enumerate(input):
            if c == '.':
                # new group
                if not group:
                    fixed += '0'
                    if i < pos: new_pos += 1

                if group_number >= 3:
                    break  # ip address only consists of 4 groups

                # python's socket module doesn't work with leading zeros
                group = group.rstrip('0')
                if not group:  # group was only zero
                    group = '0'

                fixed += group + '.'
                group_added = True

                group = ''
                group_number += 1
            elif not group and re.fullmatch('[0-2]', c):
                # first digit may only be 1-2
                group += c
                group_added = False
            elif 0 < len(group) < 3 and re.fullmatch('[0-9]', c):
                # normal digit
                group += c
                group_added = False
            else:
                # invalid letter
                if i < pos: new_pos -= 1

        if not group_added:
            fixed += group

        return (self.State.Intermediate, fixed, new_pos)


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
