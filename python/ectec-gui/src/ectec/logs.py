#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Provide logging capablities for the ectec module.

***********************************

Created on Mon Mar 15 16:03:59 2021

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
from logging import (CRITICAL, DEBUG, ERROR, INFO, NOTSET, WARNING,
                     NullHandler, StreamHandler, getLogger)


def indent(text, by, space=" ", prefix="", suffix=""):
    """
    Indent a multiline string.

    Each line of `text` will be appended to prefix plus `by` times `space`
    plus the `suffix`.

    ::

        line = prefix + by * space + suffix + original_line


    Parameters
    ----------
    text : str
        the multiline string.
    by : int
        the amount of indent.
    space : str, optional
        The spacing character. The default is " ".
    prefix : str, optional
        The prefix of the spacing. The default is "".
    suffix : str, optional
        The suffix of the spacing. The default is "".

    Returns
    -------
    text : str
        The indented text.

    """
    t = ""  # Stores the indented lines and will be returned

    # Iterate of the lines of the text
    for l in text.splitlines(True):
        # The indented line is added to the result
        t += prefix + by*space + suffix + l

    return t


class EctecFormatter(logging.Formatter):
    """
    A formatter creates a string from a LogRecord.

    Exceptions are Incoperated into the log but indented.
    """

    def __init__(self,
                 fmt="{asctime}  {levelname:<8} [{name}]  {message}",
                 datefmt=None,
                 style='{'):

        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def formatException(self, exc_info):
        """
        Format an exception so that it prints on a single line.
        """
        result = super().formatException(exc_info)  # Super formats for us.
        return indent(result, 2, prefix="| >>>")  # Indent output
