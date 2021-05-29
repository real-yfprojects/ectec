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
import os.path as osp
import sys
import time
import unittest
import warnings
from unittest.signals import registerResult

try:
    import colorama
    from colorama import Back, Fore, Style
    colorama.init()
except Exception as error:
    print(error)
    colorama = None


def _import_ectec(*submodules):
    try:
        ectec = __import__('ectec')

        for sbm in submodules:
            __import__('ectec.'+sbm)
    except:
        PATH = sys.path
        sys.path.append(osp.abspath(osp.join(__file__, '../../')))

        ectec = __import__('src')

        for sbm in submodules:
            __import__('src.'+sbm)

    return ectec


class FunctionThread(threading.Thread):

    def run(self):
        self.return_value = None
        try:
            if self._target:
                self.return_value = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs


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


class EctecTestResult(unittest.TextTestResult):

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if colorama:
            # colored
            if doc_first_line:
                return doc_first_line + Style.DIM + Fore.MAGENTA + ' (' + \
                    unittest.case.strclass(test.__class__) + ')' + \
                    Style.RESET_ALL
            else:
                return str(test)
        else:
            # uncolored
            if doc_first_line:
                return doc_first_line + ' (' + \
                    unittest.case.strclass(test.__class__) + ')'
            else:
                return str(test)

    def addSuccess(self, test):
        if colorama:
            self.stream.write(Fore.GREEN)
            super().addSuccess(test)
            self.stream.write(Style.RESET_ALL)
        else:
            super().addSuccess(test)

    def addError(self, test, err):
        if colorama:
            self.stream.write(Fore.RED)
            super().addError(test, err)
            self.stream.write(Style.RESET_ALL)
        else:
            super().addError(test, err)

    def addFailure(self, test, err):
        if colorama:
            self.stream.write(Fore.RED)
            super().addFailure(test, err)
            self.stream.write(Style.RESET_ALL)
        else:
            super().addFailure(test, err)

    def addSkip(self, test, reason):
        if colorama:
            self.stream.write(Fore.LIGHTRED_EX)
            super().addSkip(test, reason)
            self.stream.write(Style.RESET_ALL)
        else:
            super().addSkip(test, reason)


class EctecTestRunner(unittest.TextTestRunner):
    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        result.tb_locals = self.tb_locals
        with warnings.catch_warnings():
            if self.warnings:
                # if self.warnings is set, use it to filter all the warnings
                warnings.simplefilter(self.warnings)
                # if the filter is 'default' or 'always', special-case the
                # warnings from the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd and -Wa flags can be used to bypass this
                # only when self.warnings is None.
                if self.warnings in ['default', 'always']:
                    warnings.filterwarnings('module',
                                            category=DeprecationWarning,
                                            message=r'Please use assert\w+ instead.')
            startTime = time.perf_counter()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()
            stopTime = time.perf_counter()
        timeTaken = stopTime - startTime
        result.printErrors()
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            if colorama:
                self.stream.write(Fore.RED + "FAILED" + Style.RESET_ALL)
            else:
                self.stream.write("FAILED")

            failed, errored = len(result.failures), len(result.errors)
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            if colorama:
                self.stream.write(Fore.GREEN + "OK" + Style.RESET_ALL)
            else:
                self.stream.write("OK")

        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        return result


if __name__ == '__main__':
    loader = unittest.TestLoader()
    runner = EctecTestRunner(verbosity=3, buffer=True,
                             resultclass=EctecTestResult)
    suite = suite = unittest.TestSuite([])

    # load
    suite.addTest(loader.discover(osp.dirname(osp.abspath(__file__)), "*.py"))

    # run
    runner.run(suite)
