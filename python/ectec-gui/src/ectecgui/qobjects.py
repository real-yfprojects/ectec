#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QObject subclasses needed by other parts of the GUI.

***********************************

Created on 2022/05/28 at 21:29:38

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

from pathlib import Path
from typing import List, cast

from appdirs import user_log_dir
from PyQt5.QtCore import QEvent, QLocale, QTranslator, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QAction, QActionGroup, QApplication, QMenu

from . import APPAUTHOR, APPNAME, SOURCE_LANGUAGE, Settings, logger
from .helpers import get_current_language, get_languages

#: The function that provides internationalization by translation.
_tr = QApplication.translate

# ---- Log Action ------------------------------------------------------------


def open_logs():
    """Open the location of the default log file"""
    path = Settings.LOG_FILE.parent.resolve()
    QDesktopServices.openUrl(QUrl(path.as_uri()))


# ---- Language Menu ---------------------------------------------------------


class TranslatorAwareApp(QApplication):
    """A QApplication that gives access to the installed translators."""

    def __init__(self, argv: List[str]) -> None:
        """Init."""
        super().__init__(argv)

        self._translator_list: List[QTranslator] = []

    def translators(self) -> List[QTranslator]:
        """Get a list of the installed translators."""
        return self._translator_list.copy()

    def installTranslator(self, translationFile: QTranslator) -> bool:
        """
        Adds the translation file translationFile to the list of translation
        files to be used for translations.

        Multiple translation files can be installed.
        Translations are searched for in the reverse order in which
        they were installed, so the most recently installed translation file
        is searched first and the first translation file installed
        is searched last. The search stops as soon as a translation
        containing a matching string is found.

        Installing or removing a QTranslator, or changing an installed
        QTranslator generates a LanguageChange event for the QCoreApplication
        instance. A QApplication instance will propagate the event to all
        toplevel widgets, where a reimplementation of changeEvent can
        re-translate the user interface by passing user-visible strings
        via the tr() function to the respective property setters.
        User-interface classes generated by Qt Designer provide a
        retranslateUi() function that can be called.

        The function returns true on success and false on failure.
        """
        self._translator_list.append(translationFile)
        return super().installTranslator(translationFile)

    def removeTranslator(self, translationFile: QTranslator) -> bool:
        """
        Removes the translation file translationFile from the list of
        translation files used by this application.
        (It does not delete the translation file from the file system.)

        The function returns true on success and false on failure.
        """
        try:
            self._translator_list.remove(translationFile)
        except ValueError:
            # not in list
            pass

        return super().removeTranslator(translationFile)


class LanguageMenu(QMenu):
    """A menu for switching the app language."""

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent=parent, title=_tr("LanguageMenu", "Languages"))

        self.language_actiongroup = QActionGroup(self)

        current_locale = get_current_language()

        # add languages
        for locale in get_languages():
            name = QLocale.languageToString(locale.language())
            action = self.language_actiongroup.addAction(name)
            action.setCheckable(True)
            action.setData(locale)
            self.addAction(action)

            if locale.bcp47Name() == current_locale.bcp47Name():
                action.setChecked(True)

        self.language_actiongroup.triggered.connect(self.language_clicked)

    def language_clicked(self, action: QAction):
        """Change the translation of the app on trigger of a menu action."""
        app = QApplication.instance()

        if isinstance(app, TranslatorAwareApp):
            app = cast(TranslatorAwareApp, app)
            for translator in app.translators():
                success = QApplication.removeTranslator(translator)
            logger.debug("Removed old translator(s).")

        # install new translator
        locale = action.data()
        translator = QTranslator()
        success = translator.load('ectecgui.' + locale.bcp47Name(), ':/i18n',
                                  '.', '.qm')
        if not success and locale.bcp47Name() != SOURCE_LANGUAGE:
            logger.warning(
                f"Couldn't load translation file for {locale.bcp47Name()}.")

        QApplication.installTranslator(translator)

        logger.info(f"Installed translator for {locale.bcp47Name()}.")

        self.translator = translator

    def changeEvent(self, event: QEvent) -> None:
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
            # The checked language has to be updated.
            current_locale = get_current_language()
            for action in self.language_actiongroup.actions():
                if action.data().bcp47Name() == current_locale.bcp47Name():
                    action.setChecked(True)

            logger.debug(
                f"Language was changed to {current_locale.bcp47Name()}.")

        # Pass the event to the parent class for its handling.
        super().changeEvent(event)
