#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common setup operations.

***********************************

Created on 2022/06/01 at 16:50:14

Copyright (C) 2022 real-yfprojects (github.com user)

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
import signal
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from appdirs import user_log_dir
from PyQt5.QtCore import QLocale, Qt, QTranslator, qInstallMessageHandler
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QStyleFactory

from . import (APPAUTHOR, APPNAME, VERSION, Settings, helpers, logger, logs,
               qobjects)


def commmon_arguments(parser: ArgumentParser):
    """Add common cmd arguments to a parser."""
    parser.add_argument('--version',
                        action='version',
                        version="%(prog)s " + str(VERSION))

    # logging
    parser.add_argument(
        '--log-level',
        dest='log_level',
        choices=['critical', 'error', 'warning', 'info', 'debug', 'notset'],
        help="Set the minimum level for logged messages")
    log_file_group = parser.add_mutually_exclusive_group()
    log_file_group.add_argument(
        '--log-file',
        dest='log_file_path',
        metavar='PATH',
        type=Path,
        help="Set the file log messages are outputted to "
        "additionally to standard output.")
    log_file_group.add_argument('--no-logfile',
                                '--no-log-file',
                                action='store_false',
                                dest='log_file',
                                help="Log to standard output only.")


def setup_logging(args: Namespace, program: str, default_log_filename: str):
    """Setup the logging and handle the logging cmd arguments."""
    # standard output handler
    handler = logging.StreamHandler()
    handler.setFormatter(logs.EctecGuiFormatter(program))
    if args.log_level:
        handler.setLevel(args.log_level.upper())
    else:
        handler.setLevel(logs.WARNING)
    logger.addHandler(handler)

    # file handler
    if args.log_file:
        if args.log_file_path is None:
            log_dir = Path(user_log_dir(APPNAME, APPAUTHOR))
            log_dir.mkdir(parents=True, exist_ok=True)  # ensure dir exists
            log_file = log_dir / default_log_filename
        else:
            log_file = args.log_file_path

        max_size = 300 * 1024 * 1024  # 300 MiB
        file_handler = logs.SessionRotatingFileHandler(log_file,
                                                       sessionCount=5)
        file_handler.setFormatter(logs.EctecGuiFormatter(program))
        if args.log_level:
            file_handler.setLevel(args.log_level.upper())
        else:
            file_handler.setLevel(logs.DEBUG)
        logger.addHandler(file_handler)

        # set settings var
        Settings.LOG_FILE = log_file

    # convert Qt messages (from the qt logging system) to python LogRecords.
    qInstallMessageHandler(logs.QtMessageHander(logger))


def setup_qt() -> QApplication:
    """Setup qt and initialize an app."""

    # exit immediately on keyboard interrupt
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # some global settings
    QApplication.setDesktopSettingsAware(True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    # icon theme
    QIcon.setFallbackThemeName('breeze')
    if sys.platform == 'win32':
        QIcon.setThemeName('breeze')

    if sys.platform == 'win32' and 'Fusion' in QStyleFactory.keys():
        QApplication.setStyle(QStyleFactory.create('Fusion'))

    # start app
    app = qobjects.TranslatorAwareApp(sys.argv)

    # install default translator
    translator = QTranslator()
    success = translator.load(QLocale(), 'ectecgui', '.', ':/i18n', '.qm')
    app.installTranslator(translator)

    if success:
        locale = helpers.get_current_language()
        logger.debug(
            f"Loaded translation {locale.bcp47Name()} for {QLocale().uiLanguages()}."
        )
    else:
        logger.debug(
            f"Failed to load translation for {QLocale().uiLanguages()}.")

    return app
