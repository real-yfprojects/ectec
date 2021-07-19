#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of the window that runs the server.

***********************************

Created on 2021/06/25 at 16:52:15

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

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QLocale, QTranslator, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication

from .. import ectec_res
from .ui_main import Ui_dStartServer

#: The function that provides internationalization by translation.
_tr = QApplication.translate


class Ui_mainWindow(Ui_dStartServer):
    """
    The UI that are the Widgets of the MainWindow.

    This class inherits a automatically generated form class and makes changes
    that can't be done in Qt Designer.
    """

    #: This GUI's name in the `server` namespace of the translation files.
    TRANSLATION_UI_NAME = 'mainwindow'

    def setupUi(self, dStartServer: QtWidgets.QDialog):
        """
        Setup the form that is the GUI.

        This sets the window properties and adds the Widgets.

        Parameters
        ----------
        dStartServer : QtWidgets.QDialog
            The QDialog to add the widgets to.
        """
        super().setupUi(dStartServer)

        # =================================================================
        #
        # Set up main menu.
        #
        # When clicking on the "burger" toolbutton the main menu pops up.
        # The menu is initiated. Then QtWidgets.QActions are created and
        # added to the menu. They represent the menu entries.
        #
        # =================================================================

        self.menu_main = QtWidgets.QMenu(dStartServer)

        # Add 'About' action
        self.action_about = QtWidgets.QAction(
            _tr('dStartServer', "About", "menu"), self.menu_main)
        self.menu_main.addAction(self.action_about)

        # Add menu to toolbutton
        self.toolButtonMenu.setMenu(self.menu_main)

    def retranslateUi(self, dStartServer: QtWidgets.QDialog, init=True):
        """
        Retranslate the UI.

        This should update the strings and other properties regarding
        internationalization.

        Parameters
        ----------
        dStartServer : QtWidgets.QDialog
            The QDialog window that contains this form.
        init : bool
            Whether the UI is completely initialized.
        """
        super().retranslateUi(dStartServer)

        if init:
            return

        # =================================================================
        #
        # Retranslate main menu.
        #
        # =================================================================

        self.action_about.setText(_tr('dStartServer', "About", "menu"))


class MainWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # load the GUI generated from an .ui file
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

    def changeEvent(self, event: QtCore.QEvent):
        """
        This event handler can be implemented to handle state changes.

        The state being changed in this event can be retrieved through
        the event supplied. Change events include:
        `QEvent.ToolBarChange`, `QEvent.ActivationChange`,
        `QEvent.EnabledChange`, `QEvent.FontChange`, `QEvent.StyleChange`,
        `QEvent.PaletteChange`, `QEvent.WindowTitleChange`,
        `QEvent.IconTextChange`, `QEvent.ModifiedChange`,
        `QEvent.MouseTrackingChange`, `QEvent.ParentChange`,
        `QEvent.WindowStateChange`, `QEvent.LanguageChange`,
        `QEvent.LocaleChange`, `QEvent.LayoutDirectionChange`,
        `QEvent.ReadOnlyChange`.

        Parameters
        ----------
        event : QtCore.QEvent
            The event that occurred.
        """
        if event.type() == QtCore.QEvent.LanguageChange:
            # The language of the QApplication was changed.
            # The GUI has to be retranslated.
            self.ui.retranslateUi(self)

        # Pass the event to the parent class for its handling.
        super().changeEvent(event)
