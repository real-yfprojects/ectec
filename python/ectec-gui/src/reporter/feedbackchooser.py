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
from typing import (Any, Callable, Dict, Iterable, List, Optional, Type,
                    TypeVar, Union)

from PyQt5.QtCore import Qt, QUrl, pyqtBoundSignal, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import (QApplication, QDialogButtonBox, QFrame,
                             QHBoxLayout, QLabel, QPushButton, QScrollArea,
                             QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from . import TranslatableQWidget, TranslatableString, View

logger = logging.getLogger(__name__)

# ---- FeedbackOptions -------------------------------------------------------


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


class FeedbackOption(QFrame, TranslatableQWidget):
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

    def __init__(
            self,
            config: FeedbackOptionConfig,
            *,
            parent: Optional[QWidget] = None,
            flags=Qt.WindowFlags(),
    ) -> None:
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
        hlay.addLayout(vlay, 1)
        hlay.addWidget(self.bAction)

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

    # type var for class method
    Instance = TypeVar("Instance", bound="FeedbackOption")

    @classmethod
    def from_config(cls: Type[Instance],
                    config: FeedbackOptionConfig) -> Instance:
        """Construct FeedbackOption from corresponding config."""
        return cls(config)

    def retranslateUi(self):
        """
        Set and retranslate the strings displayed.
        """
        self.lName.setText(f"<h3>{self._config.name.translated()}</h3>")
        self.lDescription.setText(self._config.about.translated())
        self.bAction.setText(self._config.action_label.translated())

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

    def __init__(
            self,
            config: ContactLinkConfig,
            *,
            parent: Optional[QWidget] = None,
            flags=Qt.WindowFlags(),
    ) -> None:
        """Init."""
        super().__init__(config, parent=parent, flags=flags)
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

    def __init__(
            self,
            config: SlotConfig,
            *,
            parent: Optional[QWidget] = None,
            flags=Qt.WindowFlags(),
    ) -> None:
        """Init."""
        super().__init__(config, parent=parent, flags=flags)
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


# ---- FeedbackView ----------------------------------------------------------


class UnknownFeedbackOptionConfig(Exception):
    pass


def options_from_config(
    configs: List[FeedbackOptionConfig],
    *,
    class_mapping: Dict[Type[FeedbackOptionConfig], Type[FeedbackOption]] = {},
) -> List[FeedbackOption]:
    build_in_configs = {
        FeedbackOptionConfig: FeedbackOption,
        ContactLinkConfig: ContactLinkOption,
        SlotConfig: SlotOption,
    }
    for c, o in build_in_configs.items():
        class_mapping.setdefault(c, o)

    options = []
    for fc in configs:
        try:
            cls = class_mapping[type(fc)]
            option_instance = cls.from_config(fc)
            options.append(option_instance)
        except KeyError:
            raise UnknownFeedbackOptionConfig(
                f"Can't match {type(fc)} to any feedback option.") from None
    return options


class FeedbackView(View):

    def __init__(
            self,
            options: Iterable[FeedbackOption] = [],
            *,
            parent: Optional[QWidget] = None,
            flags=Qt.WindowFlags(),
    ) -> None:
        super().__init__(parent, flags)

        # =================================================================
        #
        # Setup ui.
        #
        # =================================================================

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, -1)
        root_layout.setSpacing(8)

        # ScrollArea with feedback options
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Plain)
        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()
        self.fo_layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.fo_layout.setContentsMargins(8, 8, 8, 8)
        self.fo_layout.setSpacing(12)

        self.fo_spacer = QSpacerItem(10, 0, QSizePolicy.Minimum,
                                     QSizePolicy.Expanding)
        self.fo_layout.addItem(self.fo_spacer)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        root_layout.addWidget(self.scrollArea)

        # dialog button box
        pad_layout = QVBoxLayout()
        pad_layout.setContentsMargins(8, -1, 8, -1)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        pad_layout.addWidget(self.buttonBox)

        root_layout.addLayout(pad_layout)

        # =================================================================
        #
        # Add config options.
        #
        # =================================================================

        for fo in options:
            self.addOption(fo)

        # =================================================================
        #
        # Connect slots.
        #
        # =================================================================

        self.buttonBox.clicked.connect(self.closeRequested)

    def addOption(self, option: FeedbackOption):
        self.fo_layout.insertWidget(self.fo_layout.count() - 1, option)

    def removeOption(self, option: FeedbackOption):
        self.fo_layout.removeWidget(option)


if __name__ == "__main__":
    import sys

    _tr = TranslatableString

    app = QApplication(sys.argv)

    ctx = "test"
    go_string = _tr(ctx, "Go")
    icon = QIcon.fromTheme("go-jump")
    configs = [
        ContactLinkConfig(
            _tr(ctx, "Documentation"),
            _tr(ctx, "Open the the docs in browser"),
            go_string,
            icon,
            QUrl("https://github.com"),
        ),
        ContactLinkConfig(
            _tr(ctx, "Discussions"),
            _tr(ctx, "Open discussions"),
            go_string,
            icon,
            QUrl("https://example.com"),
        ),
    ]
    options = options_from_config(configs)
    feedback_dialog = FeedbackView(options)
    feedback_dialog.show()

    sys.exit(app.exec_())
