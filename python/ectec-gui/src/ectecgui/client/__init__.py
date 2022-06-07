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
import sys
from argparse import ArgumentParser

from .. import breeze_res, ectec_res
from ..setup import commmon_arguments, setup_logging, setup_qt
from .wConnect import ConnectWindow


def main():
    """Run the client gui."""
    # ---- Argparse --------------------------------------------------------------

    try:
        import argcomplete
    except ImportError:
        argcomplete = None

    # determine program name
    if sys.argv[0] == __file__:
        # use static value
        prog = 'ectecgui.client'
    else:
        prog = None

    # define arguments
    parser = ArgumentParser(
        description="The ectec client.",
        epilog="The ectec client program allows connecting to an ectec server "
        "and sending packages/messages to other clients connected to the "
        "same server.",
        prog=prog,
        allow_abbrev=True,
        add_help=True)

    commmon_arguments(parser)

    # parse arguments
    if argcomplete:
        argcomplete.autocomplete(parser)

    args = parser.parse_args()

    # handle common arguments
    setup_logging(args, 'Client', 'client.log')

    # ---- Qt App ----------------------------------------------------------------

    app = setup_qt()

    # open window
    dialog = ConnectWindow()

    dialog.show()

    # start qt event loop
    sys.exit(app.exec_())
