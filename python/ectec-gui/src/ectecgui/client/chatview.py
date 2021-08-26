#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of a View widget displaying a Chat consisting of ectec packages.

***********************************

Created on 2021/08/25 at 16:28:44

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

import textwrap
from typing import Callable, List, Optional, Tuple, Union

from ectec.client import Package, PackageStorage
from PyQt5.QtCore import (QAbstractListModel, QModelIndex, QObject, QRect,
                          QSize, Qt)
from PyQt5.QtGui import QFontMetrics, QPainter, QPen
from PyQt5.QtWidgets import (QListView, QStyledItemDelegate,
                             QStyleOptionViewItem)


class ModelPackageStorage(PackageStorage):
    """
    A PackageStorage that is connected to a EctecPackageStorage.

    Parameters
    ----------
    model : EctecPackageModel
        The connected model.
    """
    def __init__(self, model: 'EctecPackageModel'):
        """
        Init a PackageStorage that is connected to a Model.

        Parameters
        ----------
        model : EctecPackageModel
            The connected model.
        """
        super().__init__()
        self.model = model

    def remove(self,
               *packages: Package,
               func: Callable[[Package], bool] = None) -> None:
        """
        Remove packages from the storage.

        All packages that equal the packages directly specified are removed.
        The function acts as a filter. The `func` function gets passed
        an `Package` if the function returns `True` the package is removed.
        If you pass both packages and a function all packages matching
        one of them will be removed.

        Parameters
        ----------
        *packages : Package (optional)
            Packages to be removed.
        func : callable(Package) -> bool, optional
            A function acting as a filter.

        """
        self.model.beginResetModel()

        super().remove(*packages, func=func)

        self.model.endResetModel()

    def add(
        self,
        *packages: Union[Package, List[Package]],
        as_list: Optional[List[Package]] = None,
    ) -> None:
        """
        Add packages to the PackageStorage.

        Parameters
        ----------
        *packages : Package
            The packages.
        as_list : List[Package], optional
            The packages in a list. The default is None.

        Returns
        -------
        None.

        """
        count = len(packages) + (len(as_list) if as_list else 0)
        self.model.beginInsertRows(QModelIndex(), len(self),
                                   len(self) + count - 1)
        super().add(*packages, as_list=as_list)

        self.model.endInsertRows()


class EctecPackageModel(QAbstractListModel):
    """
    The model wrapping a PackageStorage of ectec packages.

    The storage connected to this model has to tell the model about changes
    made to the data. This is implemented in `ModelPackageStorage`.
    If no storage is specified a new one will be constructed.

    Parameters
    ----------
    parent : QObject, optional
        The parent of this model, by default None
    storage : ModelPackageStorage, optional
        The ModelPackageStorage used by this Model, by default None

    """
    def __init__(self,
                 parent=None,
                 storage: ModelPackageStorage = None) -> None:
        """
        Init.

        If no storage is specified a new one will be constructed.

        Parameters
        ----------
        parent : QObject, optional
            The parent of this model, by default None
        storage : ModelPackageStorage, optional
            The ModelPackageStorage used by this Model, by default None
        """
        super().__init__(parent=parent)
        self.storage = storage if storage else ModelPackageStorage(self)

    def rowCount(self, parent: QModelIndex) -> int:
        """Return the numbers of rows of this model."""
        return len(self.storage)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        """Get the data for the given role and index."""
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            return self.storage.all()[row]
        elif role == Qt.ItemDataRole.SizeHintRole:
            pass


class ChatViewDelegate(QStyledItemDelegate):
    def __init__(self, local_name: str, parent: Optional[QObject] = None):
        """
        Init the delegate.

        Parameters
        ----------
        local_name : str
            The name to treat as the local client's name.
        parent : QObject, optional
            The parent of this delegate, by default None.
        """
        super().__init__(parent=parent)
        self.local_name = local_name

        self.rel_size = 0.75
        self.margin = 6
        self.padding = 6

        self.header_padding = 3
        self.roundRadius = 3

        self.line_width = 1

    def sizeHint(self, option: QStyleOptionViewItem,
                 index: QModelIndex) -> QSize:
        """
        Get the minimum size for the representation of an item.

        The item's data can be obtained by calling `index.data()`.
        This is calculated so that the bubble is a little bit more than twice
        as long as 10 letters.

        Parameters
        ----------
        option : QStyleOptionViewItem
            The style options.
        index : QModelIndex
            The item's index with its data.

        Returns
        -------
        QSize
            The size needed.
        """
        # config
        LENGTH = 15

        # obtain paint data
        paint_frame = option.rect
        font = option.font
        alignment = option.displayAlignment
        layout_direction = option.direction
        bg_brush = option.backgroundBrush
        palette = option.palette

        # obtain package data
        package: Package = index.data()
        sender_text = textwrap.shorten(package.sender, width=10)

        if isinstance(package.content, bytes):
            text = package.content.decode('utf-8', errors='replace')
        else:
            text = str(package.content)

        # calculate width
        font.setBold(True)
        metrics = QFontMetrics(font)
        sender_width = metrics.boundingRect(
            0, 0,
            metrics.maxWidth() * len(sender_text),
            metrics.lineSpacing() * 2, 0, sender_text).width()
        sender_height = metrics.height()
        font.setBold(False)

        inner_width = sender_width * 2

        # frame for package content.
        metrics = QFontMetrics(font)
        content_frame = metrics.boundingRect(
            0, 0, inner_width,
            metrics.lineSpacing() * len(text),
            Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft, text)

        # bubble dimensions
        bubble_width = max(content_frame.width(), inner_width)
        bubble_width += self.padding * 2

        bubble_height = content_frame.height() + self.header_padding
        bubble_height += sender_height + self.padding * 2

        # combined dimenensions
        width = int(bubble_width /
                    self.rel_size) + self.line_width * 2 + self.margin * 2

        height = bubble_height + self.line_width * 2 + self.margin * 2

        return QSize(width, height)

    def calculate(
            self, option: QStyleOptionViewItem, index: QModelIndex
    ) -> Tuple[QRect, QRect, QRect, Optional[str], str]:
        """
        Make the calculations needed for painting the item.

        This method should simplify the `paint` method.
        It returns the rectangular frame for the message bubble,
        the (rectangular) frame for the header of the bubble, the frame for the
        content of the bubble, the text for the sender and the text for the
        receiver field.

        Parameters
        ----------
        option : QStyleOptionViewItem
            The stylistic options for drawing the item.
        index : QModelIndex
            The index of the item in the model.

        Returns
        -------
        Tuple[QRect, QRect, QRect, Optional[str], str]
            The calculated frames and texts.
        """
        # obtain paint data
        paint_frame: QRect = option.rect
        font = option.font
        alignment = option.displayAlignment
        layout_direction = option.direction
        bg_brush = option.backgroundBrush
        palette = option.palette

        # obtain package data
        package: Package = index.data()
        if isinstance(package.content, bytes):
            text = package.content.decode('utf-8', errors='replace')
        else:
            text = str(package.content)
        receiver_text = ', '.join(package.recipient)
        local = package.sender == self.local_name

        # helper frame's
        # bubble is on the right if send by local client otherwise on left
        bubble_frame = paint_frame.adjusted(self.margin, self.margin,
                                            -self.margin, -self.margin)
        indent = int(bubble_frame.width() * (1 - self.rel_size))
        if local:  # message by local client
            bubble_frame.adjust(indent, 0, 0, 0)
        else:
            bubble_frame.adjust(0, 0, -indent, 0)

        inner_frame = bubble_frame.adjusted(self.padding, self.padding,
                                            -self.padding, -self.padding)

        # title line
        font.setItalic(True)
        metrics = QFontMetrics(font)
        width = inner_frame.width() // 2
        receiver_text = metrics.elidedText(receiver_text,
                                           Qt.TextElideMode.ElideRight, width)
        receiver_rect = metrics.boundingRect(
            0, 0, width,
            metrics.lineSpacing() * 2,
            Qt.TextFlag.TextSingleLine | Qt.AlignmentFlag.AlignRight,
            receiver_text)
        font.setItalic(False)

        if local:  # message by local client
            title_rect = QRect(0, 0, inner_frame.width(),
                               receiver_rect.height())
            title_rect.translate(inner_frame.topLeft())
            sender_text = None
        else:
            font.setBold(True)
            metrics = QFontMetrics(font)
            sender_text = metrics.elidedText(package.sender,
                                             Qt.TextElideMode.ElideRight,
                                             width)
            sender_rect = metrics.boundingRect(
                0, 0, width,
                metrics.lineSpacing() * 2,
                Qt.TextFlag.TextSingleLine | Qt.AlignmentFlag.AlignLeft,
                sender_text)
            font.setBold(False)

            title_rect = QRect(
                0, 0, inner_frame.width(),
                max(sender_rect.height(), receiver_rect.height()))
            title_rect.translate(inner_frame.topLeft())

        # frame for package content.
        metrics = QFontMetrics(font)
        content_rect = metrics.boundingRect(
            0, 0, inner_frame.width(),
            metrics.lineSpacing() * len(text),
            Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft, text)
        content_rect.translate(title_rect.bottomLeft())
        content_rect.translate(0, self.header_padding)

        # return frames needed
        frames = bubble_frame, title_rect, content_rect

        return frames + (sender_text, receiver_text)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem,
              index: QModelIndex):
        """
        Paint the representation of an item.

        The item's data can be obtained by `index.data()`. Most calculations
        are moved to the `calculate` method.

        Parameters
        ----------
        painter : QtGui.QPainter
            The painter used to draw.
        option : QStyleOptionViewItem
            The style options.
        index : QModelIndex
            The index of the item with its data.

        """
        # push painter state (has to be restored at the end)
        painter.save()

        # enable anti-aliasing
        painter.setRenderHints(QPainter.RenderHint.Antialiasing
                               | QPainter.RenderHint.TextAntialiasing)

        # obtain paint data
        paint_frame = option.rect
        font = option.font
        alignment = option.displayAlignment
        layout_direction = option.direction
        bg_brush = option.backgroundBrush
        palette = option.palette

        # obtain package data
        package: Package = index.data()
        receiver_text = ', '.join(package.recipient)
        local = package.sender == self.local_name

        if isinstance(package.content, bytes):
            text = package.content.decode('utf-8', errors='replace')
        else:
            text = str(package.content)

        # calculate frames needed
        frames = self.calculate(option, index)
        bubble_frame, title_rect, content_rect, *texts = frames
        sender_text, receiver_text = texts

        # draw bg
        painter.setBrush(palette.base())
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(paint_frame)

        # draw bubble
        painter.setPen(QPen(palette.color(palette.ColorRole.Text)))
        painter.drawRoundedRect(bubble_frame, self.roundRadius,
                                self.roundRadius, Qt.SizeMode.AbsoluteSize)

        # draw header - receiver
        font.setItalic(True)
        painter.setFont(font)
        painter.drawText(
            title_rect,
            Qt.AlignmentFlag.AlignRight | Qt.TextFlag.TextSingleLine,
            receiver_text)
        font.setItalic(False)

        # draw header - sender
        if not local:
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(
                title_rect,
                Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextSingleLine,
                sender_text)
            font.setBold(False)

        # draw content
        painter.setFont(font)
        painter.drawText(content_rect,
                         Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap,
                         text)

        # pull painter state
        painter.restore()


class ChatView(QListView):
    """
    A View showing the packages of a chat as bubbles.

    The view is a subclass of `QListView` and can be treated as such.
    But it should be used with an `EctecPackageModel` and an ItemDelegate that
    can handle packages, e.g. `ChatViewDelegate`. The default item delegate is
    a `ChatViewDelegate` with the `local_name`.

    Parameters
    ----------
    local_name : str
        The id or name of the local client.
    parent : Optional[QObject], optional
        The parent of this widget, by default None.
    delegate : Optional[AbstractItemDelegate], optional
        The ItemDelegate for this view;
        it should be able to cope with data of type `Package`,
        by default ChatViewDelegate.
    """
    def __init__(self, local_name, parent=None, delegate=None):
        """
        Init.

        Sets the itemdelegate to `ChatViewDelegate` if no one is provided.

        Parameters
        ----------
        local_name : str
            The id or name of the local client.
        parent : Optional[QObject], optional
            The parent of this widget, by default None.
        delegate : Optional[AbstractItemDelegate], optional
            The ItemDelegate for this view;
            it should be able to cope with data of type `Package`,
            by default ChatViewDelegate.
        """
        super().__init__(parent)
        self.local_name = local_name

        self.setItemDelegate(ChatViewDelegate(local_name, self))
        self.setWordWrap(True)

    def setModel(self, model: EctecPackageModel):
        """
        Set the model used by the view.

        Parameters
        ----------
        model : EctecPackageModel
            The model.

        Raises
        ------
        TypeError
            The type of the model is not compatible.
        """
        if not isinstance(model, EctecPackageModel):
            raise TypeError("Model must be of type EctecPackageModel.")

        super().setModel(model)


if __name__ == '__main__':
    import sys

    from PyQt5 import QtGui
    from PyQt5.QtWidgets import QApplication

    # icon theme
    QtGui.QIcon.setFallbackThemeName('breeze')

    # start app
    app = QApplication(sys.argv)

    model = EctecPackageModel()
    storage = model.storage

    p1 = Package('Person A', 'Person B', 'text')
    p1.content = 'Hello!'
    p2 = Package('Person B', 'Person A', 'text')
    p2.content = 'This ChatView is currently only capable of displaying raw'
    p2.content += 'text but his might change in the future.'
    p3 = Package('Person B', ('Person A', 'Person C'), 'text')
    p3.content = 'Hello!\nHow are you?'

    storage.add(p1, p2, p3)

    chatview = ChatView('Person A')
    chatview.setModel(model)
    chatview.setVerticalScrollMode(ChatView.ScrollMode.ScrollPerPixel)

    chatview.show()

    sys.exit(app.exec_())
