#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testing equipment.

***********************************

Created on Sat May 15 17:41:34 2021

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
import sys
import os.path as osp

global ectec

def _import_ectec():
    global ectec

    PATH = sys.path
    sys.path.append(osp.abspath(osp.join(__file__, '../../')))

    ectec = __import__('src')
    __import__('src.client')
    __import__('src.server')

_import_ectec()


class ErrorDetectionHandler(logging.Handler):

    def __init__(self, level):
        super().__init__(level)
        self.records = []

    def emit(self, record):
        self.records.append(record)
        return True

    def has_record(self, **kwargs):
        for rec in self.records:
            for kw, value in kwargs.items():
                if getattr(rec, kw) is not value:
                    break
            else:
                return True

        return False

    def check_exception(self):
        for rec in self.records:
            if rec.exc_info:
                return rec

        return False

    def clear(self):
        self.acquire()
        self.records = []
        self.release()
