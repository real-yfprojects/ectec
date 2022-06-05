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

import logging
from pathlib import Path
from typing import Optional

from . import logs

VERSION = '1.0.1'

# ---- Constants -------------------------------------------------------------

APPNAME = 'Ectec'
APPAUTHOR = 'real-yfprojects'

SOURCE_LANGUAGE = 'en'

TRANSLATION_DIR = ':/i18n'

DEFAULT_PORT = 50234

# ---- Logging ---------------------------------------------------------------

logger = logging.getLogger(__name__)  # Parent logger for the module
logger.setLevel(logs.DEBUG)

# Disable default logging behaviour by creating bin for log events
nullhandler = logging.NullHandler()
logger.addHandler(nullhandler)

# ---- Dynamic settings ------------------------------------------------------


class Settings:
    """This namespace holds the settings of this app."""

    LOG_FILE: Optional[Path] = None
