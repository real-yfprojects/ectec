#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The official GUI for the ectec chattool.

***********************************

Created on Sat Jun  5 14:23:48 2021

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
from typing import List

from ectec.version import SemanticVersion
from PyQt5.QtCore import QDir, QLocale, QTranslator

VERSION = SemanticVersion(1, 0, 0)

# ---- Constants

TRANSLATION_DIR = ':/i18n'

# ---- Helpers


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
