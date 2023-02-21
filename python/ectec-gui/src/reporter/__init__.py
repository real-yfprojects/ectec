#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A customizable PyQt5 wizard for reporting bugs, errors, feature requests, etc.

***********************************

Created on 2023/02/19 at 15:50:23

Copyright (C) 2023 real-yfprojects (github.com user)

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
from typing import Any, Callable, NamedTuple, Optional, Union

from PyQt5.QtCore import QCoreApplication, QEvent, pyqtBoundSignal, pyqtSignal
from PyQt5.QtWidgets import QWidget

logger = logging.getLogger(__name__)

# Convenient type aliases.
PYQT_SLOT = Union[Callable[..., Any], pyqtBoundSignal]

# ---- Helpers --------------------------------------------------------------


class TranslatableString(NamedTuple):
    """
    Represents a string that can be translated with `QApplication.translate`.

    You can use this class to mark strings for translation without translating
    them yet. Just define an alias that matches the name of the
    `-translate-function` you configured for `lupdate5`:

    .. code:: python

        translate = TranslatableString

    """

    context: str
    sourceText: str
    disambiguation: Optional[str] = None
    n: int = -1

    def translated(self) -> str:
        """Translate this string using `QCoreApplication.translate`."""
        return QCoreApplication.translate(self.context, self.sourceText,
                                          self.disambiguation, self.n)

    def __str__(self) -> str:
        """Return translated string"""
        return self.translated()


# ---- Base Classes ----------------------------------------------------------


class TranslatableQWidget(QWidget):

    def retranslateUi(self):
        pass

    def changeEvent(self, event: QEvent):
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
        if event.type() == QEvent.LanguageChange:
            # The language of the QApplication was changed.
            # The GUI has to be retranslated.
            self.retranslateUi()

        # Pass the event to the parent class for its handling.
        super().changeEvent(event)


class View(TranslatableQWidget):
    closeRequested = pyqtSignal()
