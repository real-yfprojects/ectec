#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A collection of helpers for the code of ectec-gui.

***********************************

Created on 2021/07/23 at 08:56:55

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
from typing import List

from PyQt5.QtCore import QDir, QLocale

from . import TRANSLATION_DIR


def get_languages(cls) -> List[QLocale]:
    """
    Return a list of languages that the server GUI can be translated to.

    This function queries the directory `TRANSLATION_DIR` for
    translation files that match the pattern `ectecgui.<locale>.qm`

    Returns
    -------
    list of QLocale
        The list of supported languages.
    """
    # check whether directory for translation files exists.
    tfile_dir = QDir(TRANSLATION_DIR)

    if not tfile_dir.exists():
        return []

    # get translation files in directory.
    tfiles = tfile_dir.entryList(['ectecgui.*.qm'])

    # query the files and make a list of locales that will be returned.
    locale_list = []
    for file in tfiles:
        # extract locale id from filename
        locale_id = file.split('.')[-2]

        # create locale and append to list
        locale = QLocale(locale_id)
        locale_list.append(locale)

    return locale_list


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
