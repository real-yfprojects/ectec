#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The about window accessible from every window of the GUI.

***********************************

Created on 2022/05/26 at 13:19:01

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
from typing import Optional, Tuple, Union

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QFile, QIODevice, QLocale, QPoint, QRectF, QSize, Qt,
                          QTextStream, QTranslator, pyqtSignal, pyqtSlot)
from PyQt5.QtGui import QColor, QColorConstants, QImage, QPainter, QPixmap
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (QAction, QApplication, QMenu, QMessageBox,
                             QSizePolicy)

from .. import ectec_res, logs  # ectec_res will be imported in the ui module
from .ui_about import Ui_dAbout

#: The function that provides internationalization by translation.
_tr = QApplication.translate

# ---- Logging ---------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logs.DEBUG)

# ---- Implement AboutWindow -------------------------------------------------


class AboutDialog(QtWidgets.QDialog):
    """A dialog showing information about ectec and the current component."""

    def __init__(self,
                 component_title: Tuple[str, ...],
                 component_description: Tuple[str, ...],
                 parent=None) -> None:
        """Init."""
        super().__init__(parent)

        # set description of the component from which the about window was
        # opened
        self.component_description = component_description
        self.component_title = component_title

        # load the GUI generated from an .ui file
        self.ui = Ui_dAbout()
        self.ui.setupUi(self)

        # =================================================================
        #
        # Setup Labels and License view.
        #
        # =================================================================

        self.set_component_text()

        # set icon
        height = int(self.ui.scrollArea.height() * 0.3)
        self.ui.labelIcon.setFixedSize(height, height)

        # set license
        license_file = QFile(":/LICENSE")
        if (license_file.open(QIODevice.ReadOnly | QIODevice.Text)):
            license_text = QTextStream(license_file).readAll()
            self.ui.licenseView.setText(license_text)

        # =================================================================
        #
        # Connect signals and slots.
        #
        # =================================================================

        self.ui.buttonBox.rejected.connect(self.slotClose)

    def set_component_text(self):
        """Set the text describing the current component"""

        template = """
        <html><head/><body><p align=\"center\">
        <span style=\" font-size:18pt;\">{title}</span></p>
        <p align=\"justify\">{description}</p></body></html>
        """

        self.ui.labelComponent.setText(
            template.format(title=_tr(*self.component_title),
                            description=_tr(*self.component_description)))

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

            self.set_component_text()

            logger.debug("Retranslated ui.")

        # Pass the event to the parent class for its handling.
        super().changeEvent(event)

    @pyqtSlot()
    def slotClose(self):
        """
        Close the window.

        This slot is usually connected to the 'cancel' button that closes
        the window.
        """
        logger.debug('`About` closed.')
        self.accept()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Handle a QCloseEvent.

        This event handler is called with the given event when Qt receives
        a window close request for a top-level widget from the window system.
        By default, the event is accepted and the widget is closed. You can
        reimplement this function to change the way the widget responds to
        window close requests. For example, you can prevent the window from
        closing by calling `ignore()` on all events. When calling `accept()` on
        the event the window will be closed.

        Parameters
        ----------
        event : QtGui.QCloseEvent
            The close event.

        """
        logger.debug('`About` closed.')
        return super().closeEvent(event)
