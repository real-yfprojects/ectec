#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute all tests for ectec.

***********************************

Created on Sat May 29 14:54:26 2021

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
import os.path as osp
import unittest

from . import EctecTestResult, EctecTestRunner

if __name__ == '__main__':
    loader = unittest.TestLoader()
    runner = EctecTestRunner(verbosity=3, buffer=True,
                             resultclass=EctecTestResult)
    suite = suite = unittest.TestSuite([])

    # load
    start_dir = osp.dirname(osp.abspath(__file__))
    top_level = osp.abspath(osp.join(osp.dirname(osp.abspath(__file__)), '..'))
    suite.addTest(loader.discover(start_dir, "*.py", top_level))

    # run
    runner.run(suite)
