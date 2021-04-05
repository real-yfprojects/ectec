#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TestCases for the `ectec.server` module.

***********************************

Created on Mon Mar 29 13:03:21 2021

Copyright (C) 2020 real-yfprojects (github.com user)

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
import cProfile
import importlib
import logging
import os.path as osp
import secrets
import socket
import socketserver
import sys
import threading
import time
import unittest
from unittest import mock
import copy

if True:  # isort formatting
    PATH = sys.path
    sys.path.append(osp.abspath(osp.join(__file__, '../../')))

import src as ectec
import src.server as ectecserver
import src.version as ectecversion


# ---- Helper


class FunctionThread(threading.Thread):

    def run(self):
        self.return_value = None
        try:
            if self._target:
                self.return_value = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs


# ---- TestCases

CLIENTS = copy.deepcopy(ectecserver.ClientHandler.clients)


class ClientHandlerTestCase(unittest.TestCase):
    """A TestCase to test (almost) all the functions of the `Clienthandler`."""

    def setUp(self):
        # add a cleanup method that is always called
        self.addCleanup(self.do_cleanup)

        # set up server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", 0))
        self.server_socket.listen(1)

        dummy, port = self.server_socket.getsockname()

        # connect client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connect_thread = FunctionThread(
            target=self.server_socket.accept, daemon=True)
        self.connect_thread.start()

        self.client_socket.connect(("127.0.0.1", port))
        self.connect_thread.join()

        if not self.connect_thread.return_value:
            self.fail("Connection couldn't be established.")
        self.handler_socket, self.address = self.connect_thread.return_value

        # set up ClientHandler
        server = mock.MagicMock(spec=socketserver.TCPServer)

        class TestHandler(ectecserver.ClientHandler):

            def __init__(self, request, address, server):
                self.request = request
                self.client_address = address
                self.server = server

        TestHandler.clients = copy.deepcopy(CLIENTS)

        self.handler = TestHandler(self.handler_socket,
                                   self.address,
                                   server)
        self.handler.log = mock.MagicMock(spec=logging.LoggerAdapter)
        self.handler.setup()

    def test_get_clientlist(self):
        """Test the client list method with no client registered."""
        client_list = self.handler.get_client_list()
        self.assertEqual(client_list, [])

    def test_check_version(self):
        """Test the version check with the handler's version."""
        version_str = str(ectecserver.VERSION)
        self.assertTrue(self.handler.check_version(version_str))

    def test_recv_bytes(self):
        """Test the `receiving of x random bytes."""

        numbers = [1, 2, 3, 4, 5, 6, 10, 11, 14, 4096,
                   6500,  30000, 500 * 1000]

        # no buffer required
        self.handler_socket.settimeout(0)  # wrong timout - should be handled
        for length in numbers:
            with self.subTest("Same length", length=length):
                data = secrets.token_bytes(length)

                thread = FunctionThread(
                    target=self.handler.recv_bytes, args=[length])
                thread.start()

                t1 = time.perf_counter()
                self.client_socket.sendall(data)
                t2 = time.perf_counter()

                thread.join()

                result = thread.return_value

                self.assertEqual(data, result)

        # buffer needed
        self.handler_socket.settimeout(0)
        buffer = b'test'
        self.client_socket.sendall(buffer)
        for length in numbers[5:-2]:
            with self.subTest("Buffer needed", length=length):
                data = secrets.token_bytes(length)

                thread = FunctionThread(
                    target=self.handler.recv_bytes, args=[length])
                thread.start()

                self.client_socket.sendall(data)

                thread.join()

                result = thread.return_value

                res_data = buffer + data[:-4]
                buffer = data[-4:]

                self.assertEqual(res_data, result)

        # test start timeout
        self.handler_socket.settimeout(0)
        timeout = 0.500
        self.handler.buffer = b''
        with self.subTest("Wait timeout", timeout=timeout):
            with self.assertRaises(ectecserver.CommandTimeout):
                t1 = time.perf_counter()
                self.handler.recv_bytes(100, start_timeout=timeout)
            t2 = time.perf_counter()
            if t2-t1 > timeout+0.100:
                self.fail(f"Timout too late by: {t2-t1-timeout}")

        # test end timeout
        self.handler_socket.settimeout(0)
        timeout = 0.500
        length = 1000
        with self.subTest("Part timout", timeout=timeout):

            def run(self, timeout, length):
                times = timeout * 2 // (self.handler.COMMAND_TIMEOUT*0.5)
                for i in range(int(times)):
                    data = secrets.token_bytes(length//10)

                    self.client_socket.sendall(data)
                    time.sleep(self.handler.COMMAND_TIMEOUT*0.5)

            thread = FunctionThread(target=run, args=[self, timeout, length])
            thread.start()
            with self.assertRaises(ectecserver.CommandTimeout):
                t1 = time.perf_counter()
                self.handler.recv_bytes(length, timeout=timeout)  # in seconds
            t2 = time.perf_counter()
            thread.join()

            if t2-t1 > timeout+self.handler.COMMAND_TIMEOUT:
                self.fail(f"Timout too late by: {t2-t1-timeout}")

    def test_recv_command(self):
        """Test the receiving of a random command."""
        numbers = [1, 2, 3, 4, 5, 6, 10, 11, 14, 4096,
                   6500,  30000, 500 * 1000]

        # no buffer required
        self.handler_socket.settimeout(0)  # wrong timout - should be handled
        for length in numbers:
            with self.subTest("Same length", length=length):
                data = secrets.token_bytes(length).replace(
                    self.handler.COMMAND_SEPERATOR, b'a')

                thread = FunctionThread(
                    target=self.handler.recv_command,
                    args=[length*2 + len(self.handler.COMMAND_SEPERATOR)])
                thread.start()

                self.client_socket.sendall(
                    data + self.handler.COMMAND_SEPERATOR)

                thread.join()

                result = thread.return_value

                self.assertEqual(data, result)

        # buffer needed
        self.handler_socket.settimeout(0)
        buffer = b'test'
        self.client_socket.sendall(buffer)
        for length in numbers[5:]:
            with self.subTest("Buffer needed", length=length):
                data = secrets.token_bytes(length).replace(
                    self.handler.COMMAND_SEPERATOR, b'a')

                thread = FunctionThread(
                    target=self.handler.recv_command, args=[length*2])
                thread.start()

                self.client_socket.sendall(
                    data[:-4] + self.handler.COMMAND_SEPERATOR + data[-4:])

                thread.join()

                result = thread.return_value

                res_data = buffer + data[:-4]
                buffer = data[-4:]

                self.assertEqual(res_data, result)

        # test start timeout
        self.handler_socket.settimeout(0)
        timeout = 0.500
        self.handler.buffer = b''
        with self.subTest("Wait timeout", timeout=timeout):
            with self.assertRaises(ectecserver.CommandTimeout):
                t1 = time.perf_counter()
                self.handler.recv_command(100, start_timeout=timeout)
            t2 = time.perf_counter()
            if t2-t1 > timeout+0.100:
                self.fail(f"Timout too late by: {t2-t1-timeout}")

        # test end timeout
        self.handler_socket.settimeout(0)
        timeout = 0.500
        length = 1000
        with self.subTest("Part timout", timeout=timeout):

            def run(self, timeout, length):
                times = timeout * 2 // (self.handler.COMMAND_TIMEOUT*0.5)
                for i in range(int(times)):
                    data = secrets.token_bytes(length//10).replace(
                        self.handler.COMMAND_SEPERATOR, b'a')

                    self.client_socket.sendall(data)
                    time.sleep(self.handler.COMMAND_TIMEOUT*0.5)

            thread = FunctionThread(target=run, args=[self, timeout, length])
            thread.start()
            with self.assertRaises(ectecserver.CommandTimeout):
                t1 = time.perf_counter()
                self.handler.recv_command(
                    length*2, timeout=timeout)  # in seconds
            t2 = time.perf_counter()
            thread.join()

            if t2-t1 > timeout+self.handler.COMMAND_TIMEOUT:
                self.fail(f"Timout too late by: {t2-t1-timeout}")

    def test_recv_info(self):
        """Test receiving of the INFO command."""
        versions = ['1.1.1', '1.1.1-label',
                    '7.2.6+meta', '3.5.2-labe+meta']

        version = ''
        with self.subTest(version=version):
            command = 'INFO {}'.format(
                version).encode(encoding='utf-8') + \
                self.handler.COMMAND_SEPERATOR
            self.client_socket.sendall(command)

            with self.assertRaises(ectecserver.CommandError):
                result = self.handler.recv_info()

        version = ' '
        with self.subTest(version=version):
            command = 'INFO {}'.format(
                version).encode(encoding='utf-8') + \
                self.handler.COMMAND_SEPERATOR
            self.client_socket.sendall(command)

            with self.assertRaises(ectecserver.CommandError):
                result = self.handler.recv_info()

        for version in versions:
            with self.subTest(version=version):
                command = 'INFO {}'.format(
                    version).encode(encoding='utf-8') + \
                    self.handler.COMMAND_SEPERATOR
                self.client_socket.sendall(command)

                result = self.handler.recv_info()

                self.assertEqual(version, result)

    def test_recv_register(self):
        """Test the receiving the REGISTER command."""
        names = ['plain', '_underscore_', 'long_name', 'Numbers1234']
        roles = list(ectec.Role)

        for role in roles:
            for name in names:
                with self.subTest(name=name, role=role.value):
                    command = 'REGISTER {} AS {}'.format(name,
                                                         role.value)
                    command = command.encode(encoding='utf-8')
                    command += self.handler.COMMAND_SEPERATOR

                    self.client_socket.sendall(command)

                    res_name, res_role = self.handler.recv_register()

                    self.assertEqual(name, res_name)
                    self.assertEqual(role.value, res_role)

    def test_recv_pkg(self):
        """Test the receiving of a package using the PACKAGE command."""
        numbers = [1, 2, 3, 4, 5, 6, 10, 11, 14, 4096,
                   6500, 30000]

        names = ['plain', '_underscore_', 'long_name', 'Numbers1234']
        types = ['plain', 'meme/type', '_undescore_',
                 'long-type', 'numbered133type']

        self.client_socket.settimeout(1)

        for length in numbers:
            for typ in types:
                for sender in names:
                    recipient = 'plain'
                    with self.subTest(sender=sender,
                                      recipient=recipient,
                                      content_length=length,
                                      type=typ):

                        template = 'PACKAGE {} FROM {} TO {} WITH {}'

                        command = template.format(typ,
                                                  sender,
                                                  recipient,
                                                  str(length))

                        command = command.encode(encoding='utf-8')
                        command += self.handler.COMMAND_SEPERATOR

                        content = secrets.token_bytes(length)

                        package = (sender, recipient, typ, content)

                        thread = FunctionThread(
                            target=self.handler.recv_pkg)
                        thread.start()

                        self.client_socket.sendall(command)
                        self.client_socket.sendall(content)

                        thread.join()
                        result = thread.return_value

                        self.assertEqual(package, result)

                for recipient in names:
                    sender = 'plain'
                    with self.subTest(sender=sender,
                                      recipient=recipient,
                                      content_length=length,
                                      type=typ):

                        template = 'PACKAGE {} FROM {} TO {} WITH {}'

                        command = template.format(typ,
                                                  sender,
                                                  recipient,
                                                  str(length))

                        command = command.encode(encoding='utf-8')
                        command += self.handler.COMMAND_SEPERATOR

                        content = secrets.token_bytes(length)

                        package = (sender, recipient, typ, content)

                        thread = FunctionThread(
                            target=self.handler.recv_pkg)
                        thread.start()

                        self.client_socket.sendall(command)
                        self.client_socket.sendall(content)

                        thread.join()
                        result = thread.return_value

                        self.assertEqual(package, result)

    def test_send_pkg(self):
        """Test the sending of a package."""
        numbers = [1, 2, 3, 4, 5, 6, 10, 11, 14, 4096,
                   6500,  30000, 500 * 1000]

        for length in numbers:
            with self.subTest(length=length):
                content = secrets.token_bytes(length)
                package = ectecserver.Package(
                    'plain', 'plain', 'some_type', content)

                thread = FunctionThread(
                    target=self.handler.send_pkg, args=[package])
                thread.start()

                command = 'PACKAGE some_type FROM plain TO plain WITH ' + \
                    str(length)

                expected = command.encode('utf-8') + \
                    self.handler.COMMAND_SEPERATOR + content

                i = 0
                result = b''
                while i < length*0.5 and len(result) < len(expected):
                    result += self.client_socket.recv(8192)
                    i += 1

                thread.join()

                self.assertEqual(result, expected)

    def test_send_update(self):
        """Test the sending of an update"""
        # empty
        with self.subTest("No registered clients"):
            self.handler.send_update()

            command = b'UPDATE USERS 0' + self.handler.COMMAND_SEPERATOR

            result = self.client_socket.recv(4096)

            self.assertEqual(command, result)

        # users
        with self.subTest("3 registered users"):
            cl = [ectecserver.ClientData('one', 'user', None, None),
                  ectecserver.ClientData('two', 'user', None, None),
                  ectecserver.ClientData('three', 'user', None, None)]
            self.handler.clients[ectec.Role.USER.value] = cl

            self.handler.send_update()

            data = ' '.join([c.name for c in cl]).encode('utf-8')
            command = b'UPDATE USERS ' + bytes(str(len(data)), 'utf-8') + \
                self.handler.COMMAND_SEPERATOR

            result = self.client_socket.recv(4096)

            self.assertEqual(command+data, result)

    def test_send_error(self):
        """Test the `send_error` method."""
        # send exception
        with self.subTest('Send Exception'):
            exc = Exception('TestError')
            self.handler.send_error(exc)

            expected = b'ERROR Exception: TestError' + \
                self.handler.COMMAND_SEPERATOR

            result = self.client_socket.recv(4096)

            self.assertEqual(result, expected)

        # send text
        with self.subTest('Send error string'):
            self.handler.send_error('TestError')

            expected = b'ERROR TestError' + \
                self.handler.COMMAND_SEPERATOR

            result = self.client_socket.recv(4096)

            self.assertEqual(result, expected)

        # connection closed
        # this test is not reliable because the socket
        # doesn't realise the closed connection reliable
        with self.subTest('Close connection during sending'):
            self.client_socket.close()
            try:
                self.handler.send_error('TestError')
            except OSError as e:
                raise AssertionError(f'{e.__class__.__name__} raised.')

    # ---- Cleanup

    def do_cleanup(self):
        if hasattr(self, 'server_socket'):
            self.server_socket.close()

        if hasattr(self, 'client_socket'):
            self.client_socket.close()

        if hasattr(self, 'handler_socket'):
            self.handler_socket.close()


class ClientHandlerAdvancedTestCase(unittest.TestCase):
    """Advanced and more complex tests for the `ClientHandler`."""

    setUp = ClientHandlerTestCase.setUp

    do_cleanup = ClientHandlerTestCase.do_cleanup

    # client_socket: socket.SocketType

    def test_handling_user(self):
        """Tests the handling of one user client."""
        sep = self.handler.COMMAND_SEPERATOR
        self.client_socket.settimeout(1)  # test shouldn't hang on fail

        thread = FunctionThread(target=self.handler.handle)
        thread.start()

        # ---- version check
        version_bytes = str(ectecserver.VERSION).encode('utf-8')
        command = b'INFO ' + version_bytes + sep

        self.client_socket.sendall(command)

        # should be send as one by socket API
        info_answer = self.client_socket.recv(4096)
        expected = b'INFO True ' + version_bytes + sep

        self.assertEqual(info_answer, expected)

        # ---- register
        name, role = 'name1', ectec.Role.USER
        command = b'REGISTER ' + name.encode('utf-8') + \
            b' AS ' + role.value.encode('utf-8') + sep
        self.client_socket.sendall(command)

        # ---- user update
        users_list = name.encode('utf-8')
        command = b'UPDATE USERS ' + str(len(users_list)).encode('utf-8') + sep

        expected = command + users_list

        user_list_answer = self.client_socket.recv(4096)

        self.assertEqual(user_list_answer, expected)

        # ---- Check `get_client_list`

        client_list = self.handler.get_client_list()
        address = ectec.Address._make(self.client_socket.getsockname())
        expected_list = [ectecserver.ClientData(
            name, role, address, self.handler)]

        self.assertEqual(client_list, expected_list)

        # ---- send package
        command = b'PACKAGE text/plain FROM name1 TO unknown WITH 10' + \
            sep + secrets.token_bytes(10)

        self.client_socket.sendall(command)

        # ---- disconnect
        self.client_socket.close()
        thread.join()

        self.handler.finish()

        client_list = self.handler.get_client_list()
        self.assertEqual(client_list, [])

    # @unittest.skip("Blocks port")
    def test_handling_bad_client(self):
        """Test the handling of a bad client."""
        with self.subTest("No Info"):
            thread = FunctionThread(target=self.handler.handle)
            thread.start()
            time.sleep(1)
            self.assertFalse(thread.is_alive())


    def test_handling_two_clients(self):
        """Test the handling of two clients."""
        # TODO


if __name__ == '__main__':
    # unittest.main(buffer=True, verbosity=3)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite([])

    suite.addTest(loader.loadTestsFromTestCase(ClientHandlerTestCase))
    suite.addTest(loader.loadTestsFromTestCase(ClientHandlerAdvancedTestCase))

    unittest.TextTestRunner(verbosity=3, buffer=False).run(suite)
