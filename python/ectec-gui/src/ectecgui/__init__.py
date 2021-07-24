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

from . import logs

VERSION = SemanticVersion(1, 0, 0)

# ---- Constants -------------------------------------------------------------

TRANSLATION_DIR = ':/i18n'

# ---- Logging ---------------------------------------------------------------

logger = logs.getLogger(__name__)  # Parent logger for the module
logger.setLevel(logs.DEBUG)

# Disable default logging behaviour by creating bin for log events
nullhandler = logs.NullHandler()
logger.addHandler(nullhandler)
