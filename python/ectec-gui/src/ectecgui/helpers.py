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
import socket
import subprocess
import sys
from typing import List

from PyQt5.QtCore import QDir, QLocale
from PyQt5.QtWidgets import QApplication

from . import SOURCE_LANGUAGE, TRANSLATION_DIR


def translate(context: str, sourceText: str, *args) -> tuple:
    """Mark a string for translation without translating it."""
    return (context, sourceText) + args


def get_current_language() -> QLocale:
    """Get the locale/language currently used for translation."""
    lid = QApplication.translate("METADATA", "LANGUAGE_ID")

    if lid == "LANGUAGE_ID":
        lid = SOURCE_LANGUAGE

    return QLocale(lid)


def get_languages() -> List[QLocale]:
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
    locale_list = [QLocale(SOURCE_LANGUAGE)]
    for file in tfiles:
        # extract locale id from filename
        locale_id = file.split('.')[-2]

        # create locale and append to list
        locale = QLocale(locale_id)
        locale_list.append(locale)

    return locale_list


def list_local_hosts() -> List[str]:
    """
    Get a list of host identifiers for this machine.

    Currently this returns the ip addresses of the local machine.

    Returns
    -------
    List[str]
        The list.
    """

    if sys.platform in ('linux'):
        try:
            process = subprocess.run(['hostname', '-I'], capture_output=True)
            process.check_returncode()

            output = process.stdout.decode('utf-8')

            addr_list = output.strip().split()
            return addr_list
        except (OSError, subprocess.CalledProcessError) as e:
            logger.warning("Linux - Couldn't run `hostname -I` because '" +
                           str(e) + "'")

    hostname = socket.gethostname()
    *dummy, ipaddr_list = socket.gethostbyname_ex(hostname)
    return ipaddr_list
