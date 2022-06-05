#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The implementation of the ectec server GUI.

***********************************

Created on Sat Jun  5 14:53:21 2021

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

import sys
from argparse import ArgumentParser

from .. import breeze_res, ectec_res
from ..setup import commmon_arguments, setup_logging, setup_qt
from .window import MainWindow

# ---- Main ------------------------------------------------------------------


def main():
    """Run the server gui."""
    # ---- Argparse --------------------------------------------------------------

    try:
        import argcomplete
    except ImportError:
        argcomplete = None

    # determine program name
    if sys.argv[0] == __file__:
        # use static value
        prog = 'ectecgui.server'
    else:
        prog = None

    # define arguments
    parser = ArgumentParser(
        description=
        "The ectec server allows multiple clients to exchange packages.",
        epilog=
        "Ectec clients need a server they can connect to. The server will "
        "relay packages he receives to the other clients. "
        "Here therefore can be seen as the coordinator/moderator of a chat.",
        prog=prog,
        allow_abbrev=True,
        add_help=True)

    commmon_arguments(parser)

    # parse arguments
    if argcomplete:
        argcomplete.autocomplete(parser)

    args = parser.parse_args()

    # handle common command line arguments
    setup_logging(args, 'Server', 'server.log')

    # ---- Qt App ----------------------------------------------------------------

    app = setup_qt()

    # open window
    dialog = MainWindow()

    dialog.show()

    sys.exit(app.exec_())
