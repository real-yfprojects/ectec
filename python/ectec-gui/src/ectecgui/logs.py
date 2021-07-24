#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The logging capabilities of ectec-gui.

How to set up logging in ectec-gui:

::
    logger: logging.Logger

    streamhandler = logs.StreamHandler()
    streamhandler.setLevel(logs.WARNING)
    streamhandler.setFormatter(logs.EctecGuiFormatter('proc'))
    logger.addHandler(streamhandler)

    filehandler = logs.SessionRotatingFileHandler(filename,
                                                sessionCount=3)
    filehandler.setLevel(logs.DEBUG)
    filehandler.setFormatter(logs.EctecGuiFormatter('proc'))
    logger.addHandler(filehandler)


***********************************

Created on 2021/07/23 at 09:06:26

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
import logging
import os
from logging import (CRITICAL, DEBUG, ERROR, INFO, NOTSET, WARNING,
                     NullHandler, StreamHandler, getLogger, handlers)
from pathlib import Path, PurePath
from posixpath import basename


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
        t += prefix + by * space + suffix + l

    return t


class EctecGuiFormatter(logging.Formatter):
    """
    A formatter creates a string from a LogRecord.

    Exceptions are incoperated into the log but indented.

    Parameters
        ----------
        program : str, optional
            The name of the subprogram run (e.g. Client), by default None
        fmt : str, optional
            A format string specifying the log message format, by default None
        datefmt : as super defines.
        style : str, optional
            The format variable style used, by default '{'

    """
    def __init__(self, program=None, fmt=None, datefmt=None, style='{'):
        """
        Init the Formatter.

        Parameters
        ----------
        program : str, optional
            The name of the subprogram run (e.g. Client), by default None
        fmt : str, optional
            A format string specifying the log message format, by default None
        datefmt : as super defines.
        style : str, optional
            The format variable style used, by default '{'
        """
        if not fmt:
            prg = str(program) if program else ''
            fmt = "{asctime} {levelname:<8} " + prg + "[{name}]  {message}"

        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def formatException(self, exc_info):
        """
        Format an exception so that it prints on a single line.
        """
        result = super().formatException(exc_info)  # Super formats for us.
        return indent(result, 2, prefix="| >>>")  # Indent output


class SessionRotatingFileHandler(handlers.BaseRotatingHandler):
    def __init__(self,
                 filename,
                 sessionCount: int,
                 mode: str = 'a',
                 encoding: str = 'utf-8') -> None:
        """
        Init a Rotating FileHandler that rotates on session start.

        This Rotating FileHandler rotates only on session start. that is
        when this handler is initialized.

        Parameters
        ----------
        filename : str or Path
            The path of the file to log to.
        sessionCount : int
            The number of sessions to store.
        mode : str
            The mode to open the file in, by default 'a'.
        encoding : str, optional
            The encoding of the characters to use, by default 'utf-8'.
        """
        super().__init__(filename, mode=mode, encoding=encoding, delay=False)
        self.sessionCount = sessionCount

        # Each session gets an own file.
        self.doRollover()

    def doRollover(self):
        """
        Do a rollover, as described in RotatingFileHandler.__init__().

        The file is closed and renamed. A new log file is opened.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.sessionCount > 0:
            for i in range(self.sessionCount - 1, 0, -1):
                sfn = self.rotation_filename("%s.%d" % (self.baseFilename, i))
                dfn = self.rotation_filename("%s.%d" %
                                             (self.baseFilename, i + 1))
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + ".1")
            if os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()

    def shouldRollover(self, record: logging.LogRecord) -> bool:
        """
        Decide whether to do a rollover.

        This is always false in the current implementation.
        Rollover only occurs on session start.

        Parameters
        ----------
        record : logging.LogRecord
            The current log record.

        Returns
        -------
        bool
            False.
        """
        return False  # Only rollover when session changes
