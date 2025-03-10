#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The qt subclasses for the user client GUI.

***********************************

Created on 2021/09/01 at 15:33:34

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
import re
from typing import Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QValidator
from PyQt5.QtWidgets import QCompleter, QLineEdit

from . import logger

# ---- Customize comboBox --------------------------------------------


class UserListLineEdit(QLineEdit):
    """
    A LineEdit to enter a user list into.

    This subclass overrides the backspace and delete key behaviour.

    """

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Converts the given key press event into a line edit action.

        This method overrides the backspace and delete key behaviour
        when it would normally delete a space or a semicolon so that it
        deletes the whole seperator in the user list.

        Parameters
        ----------
        event : QKeyEvent
            The key event to process

        """
        if not self.hasSelectedText():    # selections are not supported
            # switch key type
            key = event.key()
            if key == Qt.Key.Key_Backspace:
                # check whether seperator gets deleted
                pos = self.cursorPosition()
                text = self.text()

                delete = None    # will hold the index span to delete

                if pos > 1:    # check whether 0 < pos -1
                    # else it will be a normal delete
                    if pos > 2 and text[pos - 1] == ' ':
                        # double backspace
                        delete = (pos - 2, pos)
                    elif pos + 1 < len(text) and text[pos - 1] == ';':
                        # backspace and del
                        delete = (pos - 1, pos + 1)

                    if delete:    # whether a double deletion should take place
                        text = text[:delete[0]] + text[delete[1]:]
                        pos = delete[0]

                        self.setText(text)
                        self.setCursorPosition(pos)

                        logger.debug(
                            'UserListLineEdit: Backspace deletes {}'.format(
                                delete))
                        return    # no more processing of this event
            elif key == Qt.Key.Key_Delete:
                # check whether seperator gets deleted
                pos = self.cursorPosition()
                text = self.text()

                delete = None    # will hold the index span to delete

                if pos < len(text):    # check that pos isn't at the end
                    # else it will be a normal delete
                    if 1 < pos and text[pos] == ' ':
                        # del and backspace
                        delete = (pos - 1, pos + 1)
                    elif pos + 1 < len(text) and text[pos] == ';':
                        # double del
                        delete = (pos, pos + 2)

                    if delete:    # whether a double deletion should take place
                        text = text[:delete[0]] + text[delete[1]:]
                        pos = delete[0]

                        self.setText(text)
                        self.setCursorPosition(pos)

                        logger.debug(
                            'UserListLineEdit: Delete deletes {}'.format(
                                delete))
                        return    # no more processing of this event

        return super().keyPressEvent(event)


# ---- Validators ------------------------------------------------------------


class UsernameValidator(QValidator):
    """
    Validator for user names.

    Parameters
    ----------
    parent : QObject, optional
        The parent object, by default None
    max_length : int, optional
        The maximum length for the user name, by default None
    """

    def __init__(self, parent=None, max_length=None) -> None:
        """
        Init validator.


        Parameters
        ----------
        parent : QObject, optional
            The parent object, by default None
        max_length : int, optional
            The maximum length for the user name, by default None
        """
        super().__init__(parent=parent)
        self.max_length = max_length

        #: The regex defining the characters of a clients name
        self.regex_name = re.compile(r"\w{}".format(
            '{{1,{}}}'.format(max_length) if max_length else '+'))

    def validate(self, input: str,
                 pos: int) -> Tuple[QValidator.State, str, int]:
        """
        Validate the input string.

        This method checks whether the input is a valid user name of
        the maximum size `max_length`.

        Parameters
        ----------
        input : str
            The input of the user.
        pos : int
            The cursor position.

        Returns
        -------
        Tuple[QValidator.State, str, int]
            The validation state, the (changed) input and
            the (changed) cursor position.
        """
        # no spaces allowed but underscores are.
        input = input.lstrip().replace(' ', '_')

        if not input:
            return (self.State.Intermediate, input, pos)

        # enforce max length
        if self.max_length:
            input = input[:self.max_length]

        # check whether the characters are valid.
        if self.regex_name.fullmatch(input):
            return (self.State.Acceptable, input, pos)
        else:
            return (self.State.Invalid, input, pos)


class UserListValidator(QValidator):

    def __init__(self,
                 parent=None,
                 max_user_length: int = None,
                 max_users: int = None):
        """
        Init the validator

        Parameters
        ----------
        parent : QObject, optional
            The parent, by default None
        max_user_length : int, optional
            The maximum length of a user name, by default None
        max_users : int, optional
            The maximum number of users, by default None
        """
        super().__init__(parent=parent)
        self.max_user_length = max_user_length
        self.max_users = max_users

        # regex for validation
        regex_name = r'\w' + ('{{1,{}}}'.format(max_user_length)
                              if max_user_length else '+')
        regex = r'{0}(; {0}){1}(; )?'.format(regex_name,
                                             max_users if max_users else '*')
        self.regex = re.compile(regex)

        # regex to find the user 'all'
        regex_all = r'(^| |;)all(;| |$)'
        self.regex_all = re.compile(regex_all)

    def validate(self, input: str,
                 pos: int) -> Tuple[QValidator.State, str, int]:
        """
        Validate the input string.

        This method checks whether the input is a valid list of user names
        seperated by `; `. The user names must not exceed the size
        `max_user_length` if given. The list may only contain a number of
        `max_users` users if given. If a user exceed its maximum length it will
        be cut. If the list exceeds the maximum number of users the users at
        the end will be removed.

        Parameters
        ----------
        input : str
            The input of the user.
        pos : int
            The cursor position.

        Returns
        -------
        Tuple[QValidator.State, str, int]
            The validation state, the (changed) input and
            the (changed) cursor position.
        """
        # 'all' cannot be combined with other users
        if self.regex_all.search(input):
            return (self.State.Acceptable, 'all', 3)

        # check and fix regular list by iterating over the letters and
        # inserting or removing letters as needed.

        fixed = ''    # the fixed input string
        new_pos = pos    # the new cursor position

        pre: str = None    # previous char
        lname = 0    # the length of the currently processed word
        lusers = 0    # the number of already processed users

        for i, c in enumerate(input):

            # switch over the letter `c`
            if c.isspace():
                # space at the beginning or after another space will be removed
                if not pre or pre.isspace():
                    if i < pos: new_pos -= 1    # adjust cursor pos
                    continue

                if pre != ';':
                    # new word
                    lname = 0
                    lusers += 1
                    if self.max_users:
                        if lusers >= self.max_users:
                            break    # max length of input reached

                    # insert semicolon and space
                    pre = ' '
                    fixed += '; '
                    if i < pos: new_pos += 1    # adjust cursor pos
                else:
                    # regular space after semicolon - no change
                    pre = c
                    fixed += pre

            elif c == ';':

                # semicolon at start or after space or another semicolon
                # is removed.
                if not pre or pre.isspace() or pre == ';':
                    if i < pos: new_pos -= 1    # adjust cursor pos
                else:
                    # semicolon seperates the users -> new word
                    lname = 0
                    lusers += 1
                    if self.max_users:
                        if lusers >= self.max_users:
                            break    # max length of input reached

                    # add semicolon and space
                    pre = ' '
                    fixed += '; '
                    if i < pos: new_pos += 1

            elif re.fullmatch(r'\w', c):
                # word - new char
                if self.max_user_length:    # check length of the user name
                    lname += 1
                    if lname > self.max_user_length:
                        # no more chars for this user name
                        continue

                # there is always a valid seperator between words
                # nothing has to be done here

                pre = c
                fixed += pre

            else:
                # no valid char -> remove
                if i < pos: new_pos -= 1    # adjust cursor pos

        # complete check
        if self.regex.fullmatch(fixed):
            return (self.State.Acceptable, fixed, new_pos)
        else:
            # should never be the case
            return (self.State.Intermediate, fixed, new_pos)
