#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementations of Qt's model/view architecture.

***********************************

Created on 2021/07/19 at 17:59:03

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

import ectec.server as ecse
from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication

#: The function that provides internationalization by translation.
_tr = QApplication.translate


class ClientsTableModel(QtCore.QAbstractTableModel):

    listChanged = pyqtSignal()

    def __init__(self, server: ecse.Server, parent=None):
        super().__init__(parent)
        self.server = server

        self.headings = ["Client Name (ID)", "Role", "IP address"]

        self.listChanged.connect(self.allDataChange)

    @pyqtSlot()
    def allDataChange(self):
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        Return the number of rows.

        Parameters
        ----------
        parent : [type], optional
            [description], by default QtCore.QModelIndex()

        Returns
        -------
        int
           The number of rows.
        """
        return len(self.server.users)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        Return the number of columns.

        Parameters
        ----------
        parent : [type], optional
            [description], by default QtCore.QModelIndex()

        Returns
        -------
        int
            The number of columns.
        """
        return len(self.headings)

    def data(self,
             index: QtCore.QModelIndex,
             role=Qt.ItemDataRole.DisplayRole):
        """
        Returns the data for the table cells.

        Parameters
        ----------
        index : QModelIndex
            The Index describes the row and the column of the cell.
        role : int, optional
            The role of the requested data, by default Qt.DisplayRole.

        Returns
        -------
        QVariant
            Depends on the role.
        """
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        users = self.server.users

        if index.row() >= len(users):
            return 'UnDeFinEd'

        if index.column() == 1:
            return str(users[index.row()][1].value.capitalize())
        elif index.column() == 2:
            return str(users[index.row()][2].ip)
        else:
            return str(users[index.row()][index.column()])

    def headerData(self,
                   section: int,
                   orientation: Qt.Orientation,
                   role=Qt.ItemDataRole.DisplayRole):
        """
        Returns the data of the header with the specified orientation.

        Parameters
        ----------
        section : int
            The column or row of the header.
        orientation : Qt.Orientation
            The orientation of the header.
        role : int
            The role of the data requested.
            The text to display has the DisplayRole.
        """
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        return self.headings[section]
