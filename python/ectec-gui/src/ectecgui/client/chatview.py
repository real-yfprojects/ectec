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
from typing import Callable, List, Optional, Tuple, Union, cast

from ectec.client import Package, PackageStorage
from PyQt5.QtCore import (QAbstractListModel, QEvent, QModelIndex, QObject,
                          QRect, QSize, Qt, pyqtSlot)
from PyQt5.QtGui import (QFontMetrics, QHelpEvent, QPainter, QPalette, QPen,
                         QResizeEvent)
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QListView,
                             QStyle, QStyledItemDelegate, QStyleOptionViewItem,
                             QToolTip)

#: The function that provides internationalization by translation.
_tr = QApplication.translate


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


class ChatViewDelegate(QStyledItemDelegate):
    """
    A Item Delegate for ectec Chat packages.

    This delegate should only be used with instances of `ChatView` and one
    view per instance of this delegate. The delegate draws a bubble with
    sender, receiver and content but it currently only supports raw
    text content.

    Parameters
    ----------
    local_name : str
        The name to treat as the local client's name.
    parent : QObject, optional
        The parent of this delegate, by default None.

    Attributes
    ----------
    rel_size
        The width of the bubble relative to the viewport.
    margin
        The margin around the bubble.
    padding
        The padding inside the bubble.
    header_padding
        The padding between the bubble's header and the bubble's content.
    corner_radius
        The radius of the bubble's corners.
    border_width
        The width of the bubble's border.
    dimm
        The dimm factor of the hsv color value of the border.
    bg_role
        The color role for the bubble's background/
    border_role
        The color role for the bubble's border.

    """
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

        # drawing options

        #: the width of the bubble relative to the viewport
        self.rel_size = 0.75

        #: the margin around the bubble
        self.margin = 6

        #: the padding inside the bubble
        self.padding = 6

        #: the padding between the bubble's header and the bubble's content
        self.header_padding = 3

        #: the radius of the bubble's corners
        self.corner_radius = 3

        #: the width of the bubble's border
        self.border_width: int = 1

        #: the dimm factor of the hsv color value of the border
        self.dimm = 1

        #: the color role for the bubble's background
        self.bg_role = QPalette.ColorRole.Base

        #: the color role for the bubble's border
        self.border_role = self.bg_role

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
        # obtain paint data
        paint_frame = option.rect
        state = option.state
        font = option.font
        alignment = option.displayAlignment
        layout_direction = option.direction
        bg_brush = option.backgroundBrush
        palette = option.palette

        # obtain package data
        package_data = self.process_package(index)
        dummy, local, sender_text, receiver_text, text = package_data

        sender_text = textwrap.shorten(sender_text, width=10)

        # calculate minimum width for sender field
        font.setBold(True)
        metrics = QFontMetrics(font)
        sender_width = metrics.boundingRect(
            0, 0,
            metrics.maxWidth() * len(sender_text),
            metrics.lineSpacing() * 2, 0, sender_text).width()
        sender_height = metrics.height()
        font.setBold(False)

        # calculate minimum width of item when two sender fields should fit in
        # the bubble
        min_width = int((sender_width * 2 + self.padding * 2) / self.rel_size)
        min_width += self.padding * 2 + self.border_width * 2 + self.margin * 2

        # adjust width for calling `calculate`
        option.rect.setWidth(
            max(min_width,
                option.styleObject.viewport().width()))

        # do some more calculations
        dummy1, title_rects, content_rect, *dummy2 = self.calculate(
            option, index)
        title_rect, *dummy3 = title_rects

        # calculate size of the elements combined
        bubble = QRect(
            0, 0,
            max(title_rect.width(), content_rect.width()) + self.padding * 2,
            title_rect.height() + self.header_padding + content_rect.height() +
            self.padding * 2)

        frame = QRect(
            0, 0,
            int(bubble.width() / self.rel_size) + self.border_width * 2 +
            self.margin * 2,
            bubble.height() + self.border_width * 2 + self.margin * 2)

        # return combined size
        return QSize(frame.width(), frame.height())

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
        state = option.state
        font = option.font
        alignment = option.displayAlignment
        layout_direction = option.direction
        bg_brush = option.backgroundBrush
        palette = option.palette

        # obtain package data
        package_data = self.process_package(index)
        dummy, local, sender_text, receiver_text, text = package_data

        # calculate frames needed
        frames = self.calculate(option, index)
        bubble_frame, title_rects, content_rect, *texts = frames
        title_rect, *dummy = title_rects
        sender_text, receiver_text = texts

        # determine bubble pen
        # the pen width may only be an integer but lighter lines look thinner
        # therefore the color is dimmable
        if state & QStyle.StateFlag.State_Selected:
            color = palette.color(palette.ColorRole.Highlight)
        else:
            color = palette.color(self.border_role)
            color = color.lighter(int(100 * self.dimm))

        pen_bubble = QPen(color)
        pen_bubble.setWidth(self.border_width)
        painter.setPen(pen_bubble)

        # draw bubble
        painter.setBrush(palette.brush(self.bg_role))
        painter.drawRoundedRect(bubble_frame, self.corner_radius,
                                self.corner_radius, Qt.SizeMode.AbsoluteSize)

        # text pen
        pen_text = QPen(palette.color(palette.ColorRole.Text))
        painter.setPen(pen_text)

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

    def helpEvent(self, event: QHelpEvent, view: QAbstractItemView,
                  option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        """
        Handle a help event.

        Whenever a help event occurs, this function is called with the event
        view option and the index that corresponds to the item where the event
        occurs. Returns true if the delegate can handle the event; otherwise
        returns false. A return value of true indicates that the data obtained
        using the index had the required role.
        For `QEvent::ToolTip` and `QEvent::WhatsThis` events that were handled
        successfully, the relevant popup may be shown depending
        on the user's system configuration.

        `QHelpEvent` can only be of type `ToolTip` or `WhatsThis`. Currently
        tooltips for the fields in the item's bubble are shown in case of type
        `ToolTip`. The event is passed to the superclass.

        Parameters
        ----------
        event : QHelpEvent
            The help event to handler.
        view : QAbstractItemView
            The view the event occurred in.
        option : QStyleOptionViewItem
            The style options for this item.
        index : QModelIndex
            The index of this item in the model.

        Returns
        -------
        bool
            Whether the event could be handled.
        """
        # only handle tooltip request's
        if event.type() != QEvent.Type.ToolTip:
            return super().helpEvent(event, view, option, index)

        # check index
        # (mouse cursor could be in blank space
        # when list widget is larger than the items)
        if not index.isValid():
            return False

        # obtain package data
        package_data = self.process_package(index)
        dummy, local, sender_text, receiver_text, text = package_data

        # calculate frames needed
        frames = self.calculate(option, index)
        bubble_frame, title_rects, content_rect, *texts = frames
        title_rect, sender_rect, receiver_rect = title_rects

        # switch item the cursor is in
        pos = event.pos()
        if content_rect.contains(pos):
            tooltipText = text
            tooltipRect = content_rect
        elif sender_rect and sender_rect.contains(pos):
            tooltipText = _tr('ChatView', 'From: ', 'letter') + sender_text
            tooltipRect = sender_rect
        elif receiver_rect.contains(pos):
            tooltipText = _tr('ChatView', 'To: ', 'letter') + receiver_text
            tooltipRect = receiver_rect
        else:
            # no tooltip available
            QToolTip.hideText()  # hiding the tooltip isn't done automatically
            event.ignore()  # necessary after hiding the tooltip
            return False

        # pos to global
        tooltipPos = event.globalPos()  # cursor position on screen\

        # Show tooltip
        QToolTip.showText(tooltipPos, tooltipText, view, tooltipRect)
        return True

    def calculate(
        self, option: QStyleOptionViewItem, index: QModelIndex
    ) -> Tuple[QRect, Tuple[QRect, Optional[QRect], QRect], QRect,
               Optional[str], str]:
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
        state = option.state
        font = option.font
        alignment = option.displayAlignment
        layout_direction = option.direction
        bg_brush = option.backgroundBrush
        palette = option.palette

        # obtain package data
        package_data = self.process_package(index)
        dummy, local, sender_text, receiver_text, text = package_data

        # helper frame's
        # bubble is on the right if send by local client otherwise on left
        bubble_frame = paint_frame.adjusted(self.margin + self.border_width,
                                            self.margin + self.border_width,
                                            -self.margin - self.border_width,
                                            -self.margin - self.border_width)
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
            sender_rect = None
        else:
            font.setBold(True)
            metrics = QFontMetrics(font)
            sender_text = metrics.elidedText(sender_text,
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

            # set location of sender rect
            sender_rect.translate(title_rect.topLeft())

        # set location of receiver rect
        receiver_rect.moveTopRight(title_rect.topRight())

        # frame for package content.
        metrics = QFontMetrics(font)
        content_rect = metrics.boundingRect(
            0, 0, inner_frame.width(),
            metrics.lineSpacing() * len(text),
            Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft, text)
        content_rect.translate(title_rect.bottomLeft())
        content_rect.translate(0, self.header_padding)

        # return frames needed
        frames = bubble_frame, (title_rect, sender_rect,
                                receiver_rect), content_rect

        return frames + (sender_text, receiver_text)

    def process_package(
            self, index: QModelIndex) -> Tuple[Package, bool, str, str, str]:
        """
        Process and clean the package data of a given index.

        This method sorts the receiver's.

        Parameters
        ----------
        index : QModelIndex
            The index in the model for the package.

        Returns
        -------
        Tuple[Package, bool, str, str, str]
            The data: package, local, sender_text, receiver_text, content_text
        """
        # obtain package data
        package: Package = index.data()

        # handle package content
        if isinstance(package.content, bytes):
            text = package.content.decode('utf-8', errors='replace')
        else:
            text = str(package.content)

        # handle sender
        sender_text = package.sender

        # handle receiver
        def rw(rec: str):
            if rec == self.local_name:
                return 0

            return len(rec)

        recipients = list(package.recipient)
        recipients.sort(key=rw)
        receiver_text = ', '.join(recipients)

        # msg by local client?
        local = package.sender == self.local_name

        # return data
        return package, local, sender_text, receiver_text, text


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
    def __init__(self, parent=None, local_name='', delegate=None):
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
        self.local_name = str(local_name)

        self.setItemDelegate(ChatViewDelegate(local_name, self))

        # set background color role
        self.setBackgroundRole(QPalette.ColorRole.AlternateBase)

        # range tracking for autoScrollToBottom
        self.autoScrollToBottom = True
        self._min = None
        self._max = None
        self.verticalScrollBar().rangeChanged.connect(
            self.slotHorizontalRangeChanged)

    def setLocalName(self, local_name: str):
        """Set `local_name` in qt fashion."""
        self.local_name = str(local_name)
        if isinstance(self.itemDelegate(), ChatViewDelegate):
            delegate = cast(ChatViewDelegate, self.itemDelegate())  # type hint
            delegate.local_name = local_name

    def localName(self) -> str:
        """Get `local_name` in qt fashion."""
        return self.local_name

    def setAutoScrollToBottom(self, value: bool):
        """Set the `autoScrollToBottom` attribute."""
        self.autoScrollToBottom = value

    @pyqtSlot(int, int)
    def slotHorizontalRangeChanged(self, min: int, max: int):
        """
        Handle the horizontal range of the list view beeing changed.

        This slot can be connected to a scrollbar's `rangeChanged` signal.
        """
        if self.autoScrollToBottom:
            if self._max is not None and self._min is not None:
                # react to size change
                value_offset = abs(self._max -
                                   self.verticalScrollBar().value())
                if value_offset < self._max:
                    # was at the end before -> scroll to end
                    self.scrollToBottom()

        self._min = min
        self._max = max

    def setBackgroundRole(self, role: QPalette.ColorRole) -> None:
        """
        Set the background color role of the widget to role.

        The background role defines the brush from the widget's
        palette that is used to render the background.
        If role is `QPalette::NoRole`, then the widget inherits its parent's
        background role.

        Parameters
        ----------
        role : QPalette.ColorRole
            The role from the widget's palette.
        """
        super().setBackgroundRole(role)
        self.viewport().setBackgroundRole(role)

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

    def resizeEvent(self, e: QResizeEvent) -> None:
        """
        React to a resize event.

        the widget already has its new geometry.
        The old size is accessible through QResizeEvent::oldSize().
        The widget will be erased and receive a paint event immediately after
        processing the resize event. No drawing need be (or should be)
        done inside this handler.

        Parameters
        ----------
        e : QtGui.QResizeEvent
            The resize event.

        """
        r = super().resizeEvent(e)

        # this tells the view's using the delegate that it's size changed.
        # I think the `index` parameter is not used by the `QAbstractItemView`
        # at the moment.
        self.itemDelegate().sizeHintChanged.emit(QModelIndex())

        return r


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
    p3 = Package('Person B', ('short', 'Person A', 'Person C'), 'text')
    p3.content = 'Hello!\nHow are you?'

    storage.add(p1, p2, p3)

    chatview = ChatView('Person A')
    chatview.setModel(model)
    chatview.setVerticalScrollMode(ChatView.ScrollMode.ScrollPerPixel)

    chatview.show()

    sys.exit(app.exec_())
