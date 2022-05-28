#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The gui for ectec's standard user client.

***********************************

Created on 2021/08/16 at 12:17:22

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

from .. import breeze_res, ectec_res, logs

# ---- Logging ---------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logs.DEBUG)
