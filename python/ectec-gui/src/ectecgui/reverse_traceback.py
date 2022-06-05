#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract information from a formatted traceback.

***********************************

Created on 2021/07/24 at 11:17:28

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
from typing import Dict

# ---- Define Regular Expressions --------------------------------------------

# One Frame
regex_posix_path = r"[\w/~.\-]+"
regex_windows_path = r"[\w\\.:\-]"
regex_path = regex_posix_path + r'|' + regex_windows_path

regex_in = r'[\w<>.-]+'

fheader_template = r'\s*File "(?P<path>{})", line (?P<line>\d+), ' + \
    r'in (?P<name>{}) ?'
regex_frame_header = fheader_template.format(regex_path, regex_in)

regex_code = r'\s{2,}(?P<code>.+)'

regex_frame = regex_frame_header + r'\n' + regex_code

# Traceback regex
regex_tb_header = r'Traceback \(most recent call last\):'

regex_error = r'(?P<exception>\w+)(?:\: (?P<msg>.*))?'

regex_traceback = regex_tb_header + r'\n' + \
    r'(?:(?P<lastframe>{})\n)+'.format(regex_frame) + \
    regex_error

cre_traceback = re.compile(regex_traceback)

# ---- Extraction ------------------------------------------------------------


class TracebackInfo:
    """
    A bundle of information extracted from a traceback string.

    The information is provided by the regular expression `regex_traceback`.
    All attributes can be `None` if the information wasn't found in the
    traceback string.

    Parameters
    ----------
    groupdict : Dict[str]
        The groupdict provided by the match object.

    Notes
    -----
    The traceback format expected is the one of `traceback.print_exception`.
    For Example:

    ::
        Traceback (most recent call last):
          File "/path/to/file.py", line 10, in someMethod
            raise Exception('Test')
        Exception: An error occurred.

    """
    def __init__(self, groupdict: Dict[str, str]):
        """
        Init the TracebackInfo

        An instance bundles the information extracted from a traceback string.

        Parameters
        ----------
        groupdict : Dict[str]
            The groupdict provided by the match object.
        """
        self.exception = groupdict['exception']
        self.lastframe = groupdict['lastframe']
        self.msg = groupdict['msg']
        self.code = groupdict['code']
        self.path = groupdict['path']
        self.name = groupdict['name']
        self.line = int(groupdict['line'])

        self.groupdict = dict(groupdict)

    def __str__(self):
        """
        Get a string representation of this object.

        """
        attributes_str = ' '.join([
            str(key) + '=' + repr(value)
            for key, value in self.groupdict.items()
            if value and key != 'lastframe'
        ])
        return 'TracebackInfo<{}>'.format(attributes_str)

    def __repr__(self) -> str:
        """
        Get a string representation of this object.

        """
        return str(self)

    @classmethod
    def extract(cls, tb: str):
        """
        Extract information from a given traceback.

        If the string provided isn't a traceback `None` is returned, otherwise
        a `TracebackInfo` object containing the fields defined in the regular
        expression `cre_traceback`. This class method can therefore be used in
        an if-statement.

        Parameters
        ----------
        tb : str
            The supposed traceback string.

        Returns
        -------
        TracebackInfo or None
            The information found or None if `tb` is not a traceback.
        """
        match = cre_traceback.fullmatch(tb)

        if not match:
            return None

        return cls(match.groupdict())
