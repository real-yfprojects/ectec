#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A view showing different ways of feedback to choose from.

These include other wizards, links or arbitrary actions.

***********************************

Created on 2023/02/20 at 11:44:00

Copyright (C) 2023 real-yfprojects (github.com user)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public Licenseframe
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

import logging
from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

from PyQt5.QtCore import QEvent, QUrl, pyqtBoundSignal, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
                             QPushButton, QVBoxLayout, QWidget)

from . import TranslatableString

#: The function that provides internationalization by translation.
_tr = QApplication.translate

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FeedbackOptionConfig:
    """
    Base class of all feedback option configurations.

    Attributes
    ----------
    name: TranslatableString
        The name/title of this option
    about: TranslatableString
        The description of this option
    action_label: TranslatableString
        The button label describing the action of this option
    icon: QIcon
        The button icon of this option

    See Also
    --------
    FeedbackOption
    """
    name: TranslatableString
    about: TranslatableString
    action_label: TranslatableString
    icon: QIcon


class FeedbackOption(QFrame):
    """
    Base class for all feedback option widgets.

    Subclasses must implement the `action` method.

    Parameters
    ----------
    config : FeedbackOptionConfig
        The attributes/configs of this option.
    parent : Optional[QWidget], optional
        The parent of this widget, by default None
    flags :
        Inherited from `QWidget`.

    Attributes
    ----------
    clicked: pyqtSignal
        The user clicked the action button of this option.

    Methods
    -------
    action()
        Run action corresponding to this option

    See Also
    --------
    FeedbackOptionConfig
    """

    clicked = pyqtSignal()

    def __init__(self,
                 config: FeedbackOptionConfig,
                 parent: Optional[QWidget] = None,
                 flags=None) -> None:
        """
        Init.

        Parameters
        ----------
        config : FeedbackOptionConfig
            The attributes/configs of this option.
        parent : Optional[QWidget], optional
            The parent of this widget, by default None
        flags :
            Inherited from `QWidget`.
        """
        super().__init__(parent, flags)

        # =================================================================
        #
        # Setup ui.
        #
        # =================================================================

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        hlay = QHBoxLayout(self)
        hlay.setSpacing(8)
        hlay.setContentsMargins(8, 8, 8, 8)
        vlay = QVBoxLayout()
        vlay.setSpacing(4)

        self.lName = QLabel(self)
        self.lName.setWordWrap(True)

        self.lDescription = QLabel(self)
        self.lDescription.setWordWrap(True)

        self.bAction = QPushButton(self)

        vlay.addWidget(self.lName)
        vlay.addWidget(self.lDescription)
        hlay.addLayout(vlay)

        # =================================================================
        #
        # Set values from config.
        #
        # =================================================================

        self._config = config
        self.bAction.setIcon(config.icon)
        self.retranslateUi()

        # =================================================================
        #
        # Connect signals.
        #
        # =================================================================

        self.bAction.clicked.connect(self.clicked)
        self.bAction.clicked.connect(self.action)

    def retranslateUi(self):
        """
        Set and retranslate the strings displayed.
        """
        self.lName.setText(self._config.name.translated())
        self.lDescription.setText(self._config.about.translated())
        self.bAction.setText(self._config.action_label.translated())

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
            logger.debug("Retranslated ui.")

        # Pass the event to the parent class for its handling.
        super().changeEvent(event)

    def action(self):
        """
        Execute the action for clicking this feedback option.
        """
        raise NotImplementedError(
            "Subclasses of `FeedbackOption` must implement `action`.")


@dataclass(frozen=True)
class ContactLinkConfig(FeedbackOptionConfig):
    """
    Configuration for a contact link option.

    Attributes
    ----------
    name: TranslatableString
        The name/title of this option
    about: TranslatableString
        The description of this option
    action_label: TranslatableString
        The button label describing the action of this option
    icon: QIcon
        The button icon of this option
    url: QUrl
        The url that should be opened when clicking the button

    See Also
    --------
    ContactLinkOption
    """
    url: QUrl


class ContactLinkOption(FeedbackOption):
    """
    FeedbackOption that opens a link when clicked.

    The configured link is opened in the users default browser.

    Parameters
    ----------
    config : ContactLinkConfig
        The attributes/configs of this option.
    parent : Optional[QWidget], optional
        The parent of this widget, by default None
    flags :
        Inherited from `QWidget`.

    Attributes
    ----------
    clicked: pyqtSignal
        The user clicked the action button of this option.

    Methods
    -------
    action()
        Open the link configured

    See Also
    --------
    ContactLinkConfig
    """

    def __init__(self,
                 config: ContactLinkConfig,
                 parent: Optional[QWidget] = None,
                 flags=None) -> None:
        """Init."""
        super().__init__(config, parent, flags)
        self._config: ContactLinkConfig = config

    @pyqtSlot()
    def action(self):
        """
        Execute the action for clicking this feedback option.

        This opens the configured url in the users default browser.
        """
        return QDesktopServices.openUrl(self._config.url)


@dataclass(frozen=True)
class SlotConfig(FeedbackOptionConfig):
    """
    Configuration for an option that runs any slot when it is clicked.

    Attributes
    ----------
    name: TranslatableString
        The name/title of this option
    about: TranslatableString
        The description of this option
    action_label: TranslatableString
        The button label describing the action of this option
    icon: QIcon
        The button icon of this option
    slot: pyqtSlot/Signal
        The slot/signal to be called.

    See Also
    --------
    SlotOption
    """
    slot: Union[Callable[[], Any], pyqtBoundSignal]


class SlotOption(FeedbackOption):
    """
    FeedbackOption that calls an abitrary qt slot.

    Parameters
    ----------
    config : SlotConfig
        The attributes/configs of this option.
    parent : Optional[QWidget], optional
        The parent of this widget, by default None
    flags :
        Inherited from `QWidget`.

    Attributes
    ----------
    clicked: pyqtSignal
        The user clicked the action button of this option.

    Methods
    -------
    action()
        Trigger/run the slot configured.

    See Also
    --------
    SlotConfig
    """

    def __init__(self,
                 config: SlotConfig,
                 parent: Optional[QWidget] = None,
                 flags=None) -> None:
        """Init."""
        super().__init__(config, parent, flags)
        self._config: SlotConfig = config

    @pyqtSlot()
    def action(self):
        """
        Execute the action for clicking this feedback option.

        This opens the configured url in the users default browser.
        """
        if isinstance(self._config.slot, pyqtBoundSignal):
            self._config.slot.emit()
        else:
            self._config.slot()
