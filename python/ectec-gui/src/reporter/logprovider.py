#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The abstract log provider provides the report dialog with logs from different sources

***********************************

Created on 2023/02/19 at 19:50:19

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
from typing import Any, Dict, List, NamedTuple, Optional, Union, overload

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt
from PyQt5.QtGui import QSyntaxHighlighter

#: String containing the log lines to display, default: ""
LogRole = Qt.ItemDataRole(Qt.ItemDataRole.UserRole + 1)

#: Boolean indicated whether the text is html (must be plain otherwise), default: False
IsHtmlRole = Qt.ItemDataRole(Qt.ItemDataRole.UserRole + 2)

#: The QSyntaxHighlighter to use for the given log lines, optional
HighlighterRole = Qt.ItemDataRole(Qt.ItemDataRole.UserRole + 3)


class AbstractLogProvider(QAbstractItemModel):
    """
    A model providing logs from different sources.

    The model is flat and only has a single column. Subclass must implement
    `data()`, `rowCount()` and `index()`.

    The Qt built-in data roles are used for a QComboBox that allows selecting
    a provider. The custom roles in this package are used for the log view
    itself. You will have to implement `LogRole`, `IsHtmlRole` and optionally
    `HighlighterRole`.


    See Also
    --------
    TODO

    """

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Returns the number of columns for the children of the given parent.

        Parameters
        ----------
        parent : QModelIndex, optional
            The parent to count for, by default QModelIndex()

        Returns
        -------
        int
            1 for the root index
        """
        return 1 if parent.isValid() else 0

    @overload
    def parent(self, index: QModelIndex) -> QModelIndex:
        ...

    @overload
    def parent(self) -> QObject:
        ...

    def parent(self, index=None):
        """
        Return the parent of a model index.

        Parameters
        ----------
        index : QModelIndex

        Returns
        -------
        QModelIndex
            The parent, always an invalid QModelIndex
        """
        if index is None:
            return super().parent()
        return QModelIndex()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Returns the item flags for the given index.

        The base class implementation returns a combination of flags
        that enables the item (`ItemIsEnabled`) and
        allows it to be selected (`ItemIsSelectable`)
        and `ItemNeverHasChildren`.

        Parameters
        ----------
        index : QModelIndex

        Returns
        -------
        Qt.ItemFlags
            The flags.
        """
        return super().flags(index) | Qt.ItemNeverHasChildren


class LogEntry(NamedTuple):
    """
    A log provider entry for use with `DictionaryLogProvider`.

    Attributes
    ----------
    name: str
        The log name/type
    logs: str
        the corresponding logs
    html: bool
        whether they are suppliedin html format
    highlighter: Optional[QSyntaxHighlighter]
        The highlighter to use with
    """
    name: str
    logs: str
    html: bool
    highlighter: Optional[QSyntaxHighlighter]


class DictionaryLogProvider(AbstractLogProvider):
    """
    A static LogProvider, you can pass a list/dict of entries to.

    If you set a dictionary as an entry list, it will be converted to a list
    of `LogEntry`. The dict key will be treated as a name. The value will be
    passed to the `logs` attribute of the `LogEntry`.
    `html` will be set to False. `highlighter` will be `None`.

    Parameters
    ----------
    entries : Union[Dict[str, str], List[LogEntry]]
        The logs to provide.
    parent : Optional[QObject], optional
        qt parent, by default None

    Atttributes
    -----------
    entries : List[LogEntry]
        a property for the served log entries. Also accepts Dict[str, str]
    """

    def __init__(self,
                 entries: Union[Dict[str, str], List[LogEntry]],
                 parent: Optional[QObject] = None) -> None:
        """
        Init.

        Parameters
        ----------
        entries : Union[Dict[str, str], List[LogEntry]]
            The logs to provide.
        parent : Optional[QObject], optional
            qt parent, by default None
        """
        super().__init__(parent)
        self.__entries: List[LogEntry] = []

        self.entries = entries    # type: ignore

    @property
    def entries(self) -> List[LogEntry]:
        """The entries"""
        return self.__entries.copy()

    @entries.setter
    def entries(self, entries: Union[Dict[str, str], List[LogEntry]]):
        """Update entries"""
        self.beginResetModel()
        if isinstance(entries, dict):
            self.__entries = [
                LogEntry(k, v, False, None) for k, v in entries.items()
            ]
        elif isinstance(entries, list):
            self.__entries = entries
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Get the number of rows in this model.

        Parameters
        ----------
        parent : QModelIndex, optional
            the index to count children for, by default QModelIndex()

        Returns
        -------
        int
            the number of different logs in this model
        """
        if parent == QModelIndex():
            return len(self.__entries)
        return 0

    def index(self, row: int, column: int,
              parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """
        Construct an index for a child.

        Parameters
        ----------
        row : int
            the row
        column : int
            the column, must be 0
        parent : QModelIndex, optional
            The parent, must be QModelIndex()

        Returns
        -------
        QModelIndex
            the new index
        """
        return self.createIndex(row, column, None)

    def data(self,
             index: QModelIndex,
             role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """
        Get the data for a given index.

        Implements `DisplayRole`, `LogRole`, `IsHtmlRole`
        and `HighlighterRole`.

        Returns str for `DisplayRole` and `LogRole`, bool for `IsHtmlRole` and
        Optional[QSyntaxHighlighter] for `HighlighterRole`.

        Parameters
        ----------
        index : QModelIndex
            the index to get the date for.
        role : int, optional
            the data role to retrieve, by default Qt.ItemDataRole.DisplayRole

        Returns
        -------
        Any
            the data
        """
        if not index.isValid():
            return None

        row = index.row()
        entry = self.__entries[row]

        if role == Qt.ItemDataRole.DisplayRole:
            return entry.name
        if role == LogRole:
            return entry.logs
        if role == IsHtmlRole and len(entry) > 2:
            return entry.html
        if role == IsHtmlRole and len(entry) > 2:
            return entry.highlighter

        return super().data(index, role)
