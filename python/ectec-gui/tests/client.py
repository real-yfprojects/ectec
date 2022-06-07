#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documentation string.

***********************************

Created on Tue Apr  6 10:50:54 2021

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
import datetime
import logging
import secrets
import socket
import time
import unittest

from . import ErrorDetectionHandler, FunctionThread, _import_ectec

ectec = _import_ectec('client', 'logs')
client = ectec.client

# ---- Asset Test


class PackageTestCase(unittest.TestCase):
    """TestCase for the `Package` class."""

    def test_init(self):
        """Test the creation of an instance."""
        with self.subTest('No time, one recipient'):
            p = client.Package('testsender', 'testrecipient', 'testtype')
            self.assertEqual(p.sender, 'testsender')
            self.assertEqual(p.recipient, ('testrecipient',))
            self.assertEqual(p.content, b'')
            self.assertEqual(p.type, 'testtype')
            self.assertEqual(p.time, None)

        with self.subTest('No time, more recipients'):
            p = client.Package(
                'testsender', ['testrecipient', 'reci'], 'testtype')
            self.assertEqual(p.sender, 'testsender')
            self.assertEqual(p.recipient, ('testrecipient', 'reci'))
            self.assertEqual(p.content, b'')
            self.assertEqual(p.type, 'testtype')
            self.assertEqual(p.time, None)

        with self.subTest('Time'):
            time = datetime.datetime.now()
            p = client.Package('testsender', 'testrecipient', 'testtype',
                               time.timestamp())
            self.assertEqual(p.sender, 'testsender')
            self.assertEqual(p.recipient, ('testrecipient',))
            self.assertEqual(p.content, b'')
            self.assertEqual(p.type, 'testtype')
            self.assertEqual(p.time, time)

    def test_eq(self):
        """Tests the comparing of two instances for equality regarding `==`."""
        with self.subTest('No time'):
            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            p2 = client.Package('testsender', 'testrecipient', 'testtype')

            self.assertFalse(p1 is p2)
            self.assertEqual(p1, p2)

        with self.subTest('With time'):
            p1 = client.Package('testsender', 'testrecipient', 'testtype', 1)
            p2 = client.Package('testsender', 'testrecipient', 'testtype', 1)

            self.assertFalse(p1 is p2)
            self.assertEqual(p1, p2)

    def test_hash(self):
        """Test the hashing of instances."""
        with self.subTest('Equal'):
            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            p2 = client.Package('testsender', 'testrecipient', 'testtype')

            self.assertEqual(p1, p2)
            self.assertEqual(hash(p1), hash(p2))

        with self.subTest('Time and no time'):
            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            p2 = client.Package('testsender', 'testrecipient', 'testtype', 1)

            self.assertNotEqual(p1, p2)
            self.assertNotEqual(hash(p1), hash(p2))

        with self.subTest('Different sender'):
            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            p2 = client.Package('testman', 'testrecipient', 'testtype')

            self.assertNotEqual(p1, p2)
            self.assertNotEqual(hash(p1), hash(p2))

        with self.subTest('Different recipient'):
            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            p2 = client.Package('testsender', 'testman', 'testtype')

            self.assertNotEqual(p1, p2)
            self.assertNotEqual(hash(p1), hash(p2))

        with self.subTest('Different recipients'):
            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            p2 = client.Package(
                'testsender', ['testrecipient', 'testman'], 'testtype')

            self.assertNotEqual(p1, p2)
            self.assertNotEqual(hash(p1), hash(p2))

        with self.subTest('Different type'):
            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            p2 = client.Package('testsender', 'testrecipient', 'realtype')

            self.assertNotEqual(p1, p2)
            self.assertNotEqual(hash(p1), hash(p2))

        with self.subTest('Different time'):
            p1 = client.Package('testsender', 'testrecipient', 'testtype', 1)
            p2 = client.Package('testsender', 'testrecipient', 'testtype', 2)

            self.assertNotEqual(p1, p2)
            self.assertNotEqual(hash(p1), hash(p2))

        with self.subTest('Different content'):
            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            p2 = client.Package('testsender', 'testrecipient', 'testtype')

            p2.content = b'some different content'

            self.assertNotEqual(p1, p2)
            self.assertNotEqual(hash(p1), hash(p2))


class PackageStorageTestCase(unittest.TestCase):
    """Tests for the `PackageStorage`."""

    def test_add_all(self):
        """Test the adding of packages and the `all` method."""
        with self.subTest("Empty."):
            ps = client.PackageStorage()

            self.assertEqual(list(ps.all()), [])

        with self.subTest("Add one."):
            ps = client.PackageStorage()

            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            ps.add(p1)

            self.assertEqual(ps.all(), [p1])

        with self.subTest("Add two seperately."):
            ps = client.PackageStorage()

            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            p2 = client.Package('testsender', 'testrecipient', 'testtype', 2)
            ps.add(p1)
            ps.add(p2)

            self.assertEqual(ps.all(), [p1, p2])

        with self.subTest("Add two at once."):
            ps = client.PackageStorage()

            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            p2 = client.Package('testsender', 'testrecipient', 'testtype', 2)
            ps.add(p1, p2)

            self.assertEqual(ps.all(), [p1, p2])

        with self.subTest("Add list of two."):
            ps = client.PackageStorage()

            p1 = client.Package('testsender', 'testrecipient', 'testtype')
            p2 = client.Package('testsender', 'testrecipient', 'testtype', 2)
            ps.add(as_list=[p1, p2])

            self.assertEqual(ps.all(), [p1, p2])

    def test_remove(self):
        """Test the removing of packages."""
        # self.maxDiff = None
        p1 = client.Package('testsender', 'testrecipient', 'testtype')
        p2 = client.Package('testsender', 'testrecipient', 'testtype', 2)
        p3 = client.Package('testsender', 'testrecipient', 'testtype', 2)
        p4 = client.Package('testsender', 'testrecipient', 'sometype')
        p5 = client.Package('testman', 'testrecipient', 'testtype')
        p6 = client.Package('testman', 'testrecipient', 'testtype', 2)

        packages = [p1, p2, p3, p4, p5, p6]

        with self.subTest('Remove two equal ones. Specify one.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            ps.remove(p2)

            self.assertEqual(ps.all(), [p1, p4, p5, p6])

        with self.subTest('Remove two different ones.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            ps.remove(p1, p5)

            self.assertEqual(ps.all(), [p2, p3, p4, p6])

        with self.subTest('Remove with function filter.'):
            def filter_function(pkg):
                return bool(pkg.time)  # removed if there is a time

            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            ps.remove(func=filter_function)

            self.assertEqual(ps.all(), [p1, p4, p5])

        with self.subTest('remove one and remove with function filter.'):
            def filter_function(pkg):
                return bool(pkg.time)  # removed if there is a time

            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            ps.remove(p1, func=filter_function)

            self.assertEqual(ps.all(), [p4, p5])

        with self.subTest('Remove missing.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            pack = client.Package('unique', 'unique', 'unique')

            ps.remove(pack)

            self.assertEqual(ps.all(), packages)

        with self.subTest('Remove none with filter.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            ps.remove(func=lambda p: False)

            self.assertEqual(ps.all(), packages)

    def test_filter(self):
        """Test the filtering of packages."""
        p1 = client.Package('testsender', 'testrecipient', 'testtype')
        p2 = client.Package('testsender', 'testrecipient', 'testtype', 2)
        p3 = client.Package('testsender', 'testrecipient', 'testtype', 2)
        p4 = client.Package('testsender', 'testrecipient', 'sometype')
        p5 = client.Package('testman', 'testrecipient', 'testtype')
        p6 = client.Package('testman', 'testrecipient', 'testtype', 2)
        p7 = client.Package(
            'testman', ['testrecipient', 'someman'], 'testtype', 2)

        packages = [p1, p2, p3, p4, p5, p6, p7]

        p4.content = b'some content'

        with self.subTest('Filter sender.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter(sender='testman'))

            self.assertEqual(filtered, [p5, p6, p7])

        with self.subTest('Filter recipient.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter(recipient=('testrecipient',)))

            self.assertEqual(filtered, [p1, p2, p3, p4, p5, p6])

            filtered = list(ps.filter(recipient=('testrecipient', 'someman')))

            self.assertEqual(filtered, [p7])

        with self.subTest('Filter Type.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter(type='sometype'))

            self.assertEqual(filtered, [p4])

        with self.subTest('Filter content.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter(type='sometype'))

            self.assertEqual(filtered, [p4])

        with self.subTest('Filter time.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter(time=None))

            self.assertEqual(filtered, [p1, p4, p5])

            dt = datetime.datetime.fromtimestamp(2)
            filtered = list(ps.filter(time=dt))

            self.assertEqual(filtered, [p2, p3, p6, p7])

        with self.subTest('Filter with function.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            def filfunc(pkg):
                return 'someman' in pkg.recipient

            filtered = list(ps.filter(func=filfunc))

            self.assertEqual(filtered, [p7])

        with self.subTest('Filter none.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter(func=lambda p: False))

            self.assertEqual(filtered, [])

        with self.subTest('Filter all.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter())

            self.assertEqual(filtered, packages)

        with self.subTest('Function and kwarg.'):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            def filfunc(pkg):
                return bool(pkg.time)

            filtered = list(ps.filter(func=filfunc, sender='testsender'))

            self.assertEqual(filtered, [p2, p3])

    def test_filter_recipient(self):
        p1 = client.Package('testsender', 'testrecipient', 'testtype')
        p2 = client.Package('testsender', 'name1', 'testtype', 2)
        p3 = client.Package('testsender', 'name1', 'testtype', 2)
        p4 = client.Package('testsender', 'name2', 'sometype')
        p5 = client.Package('testman', 'name2', 'testtype')
        p6 = client.Package('testman', 'name3', 'testtype', 2)
        p7 = client.Package(
            'testman', ['name2', 'someman'], 'testtype', 2)

        packages = [p1, p2, p3, p4, p5, p6, p7]

        with self.subTest("One recipient"):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter_recipient("testrecipient"))

            self.assertEqual(filtered, [p1])

        with self.subTest("One recipient, muliple packages"):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter_recipient("name1"))

            self.assertEqual(filtered, [p2, p3])

        with self.subTest("Inexistent recipient"):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter_recipient("name3", "name4"))

            self.assertEqual(filtered, [p6])

        with self.subTest("Nothing"):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter_recipient())

            self.assertEqual(filtered, [])

        with self.subTest("Multiple recipients, multiple packages"):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter_recipient("name3", "name1"))

            self.assertEqual(filtered, [p2, p3, p6])

        with self.subTest("Package with multiple recipients"):
            ps = client.PackageStorage()
            ps.add(as_list=packages)
            self.assertEqual(ps.all(), packages)

            filtered = list(ps.filter_recipient("name2"))

            self.assertEqual(filtered, [p4, p5, p7])


# ---- Client Tests


class ClientTestCase(unittest.TestCase):
    """
    Test the methods and functionalities provided by the `Client` class.

    These functionalities are inherited by every Client.
    """

    def setUp(self):
        self.client = client.Client()

        self.client.socket, self.server_socket = socket.socketpair()

    def test_recv_bytes(self):
        """Test the receiving of x random bytes."""

        numbers = [1, 2, 3, 4, 5, 6, 10, 11, 14, 4096,
                   6500,  30000, 500 * 1000]

        # no buffer required
        self.client.socket.settimeout(0)  # wrong timout - should be handled
        for length in numbers:
            with self.subTest("Same length", length=length):
                data = secrets.token_bytes(length)

                thread = FunctionThread(
                    target=self.client.recv_bytes, args=[length])
                thread.start()

                t1 = time.perf_counter()
                self.server_socket.sendall(data)
                t2 = time.perf_counter()

                thread.join()

                result = thread.return_value

                self.assertEqual(data, result)

        # buffer needed
        self.client.socket.settimeout(0)
        buffer = b'test'
        self.server_socket.sendall(buffer)
        for length in numbers[5:-2]:
            with self.subTest("Buffer needed", length=length):
                data = secrets.token_bytes(length)

                thread = FunctionThread(
                    target=self.client.recv_bytes, args=[length])
                thread.start()

                self.server_socket.sendall(data)

                thread.join()

                result = thread.return_value

                res_data = buffer + data[:-4]
                buffer = data[-4:]

                self.assertEqual(res_data, result)

        # test start timeout
        self.client.socket.settimeout(0)
        timeout = 0.500
        self.client.buffer = b''
        with self.subTest("Wait timeout", timeout=timeout):
            with self.assertRaises(client.CommandTimeout):
                t1 = time.perf_counter()
                self.client.recv_bytes(100, start_timeout=timeout)
            t2 = time.perf_counter()
            if t2-t1 > timeout+0.100:
                self.fail(f"Timout too late by: {t2-t1-timeout}")

        # test end timeout
        self.client.socket.settimeout(0)
        timeout = 0.500
        length = 1000
        with self.subTest("Part timout", timeout=timeout):

            def run(self, timeout, length):
                times = timeout * 2 // (self.client.COMMAND_TIMEOUT*0.5)
                for i in range(int(times)):
                    data = secrets.token_bytes(length//10)

                    self.server_socket.sendall(data)
                    time.sleep(self.client.COMMAND_TIMEOUT*0.5)

            thread = FunctionThread(target=run, args=[self, timeout, length])
            thread.start()
            with self.assertRaises(client.CommandTimeout):
                t1 = time.perf_counter()
                self.client.recv_bytes(length, timeout=timeout)  # in seconds
            t2 = time.perf_counter()
            thread.join()

            if t2-t1 > timeout+self.client.COMMAND_TIMEOUT:
                self.fail(f"Timout too late by: {t2-t1-timeout}")

    def test_recv_command(self):
        """Test the receiving of a random command."""
        numbers = [1, 2, 3, 4, 5, 6, 10, 11, 14, 4096,
                   6500,  30000, 500 * 1000]

        # no buffer required
        self.client.socket.settimeout(0)  # wrong timout - should be handled
        for length in numbers:
            with self.subTest("Same length", length=length):
                data = secrets.token_bytes(length).replace(
                    self.client.COMMAND_SEPERATOR, b'a')

                thread = FunctionThread(
                    target=self.client.recv_command,
                    args=[length*2 + len(self.client.COMMAND_SEPERATOR)])
                thread.start()

                self.server_socket.sendall(
                    data + self.client.COMMAND_SEPERATOR)

                thread.join()

                result = thread.return_value

                self.assertEqual(data, result)

        # buffer needed
        self.client.socket.settimeout(0)
        buffer = b'test'
        self.server_socket.sendall(buffer)
        for length in numbers[5:]:
            with self.subTest("Buffer needed", length=length):
                data = secrets.token_bytes(length).replace(
                    self.client.COMMAND_SEPERATOR, b'a')

                thread = FunctionThread(
                    target=self.client.recv_command, args=[length*2])
                thread.start()

                self.server_socket.sendall(
                    data[:-4] + self.client.COMMAND_SEPERATOR + data[-4:])

                thread.join()

                result = thread.return_value

                res_data = buffer + data[:-4]
                buffer = data[-4:]

                self.assertEqual(res_data, result)

        # test start timeout
        self.client.socket.settimeout(0)
        timeout = 0.500
        self.client.buffer = b''
        with self.subTest("Wait timeout", timeout=timeout):
            with self.assertRaises(client.CommandTimeout):
                t1 = time.perf_counter()
                self.client.recv_command(100, start_timeout=timeout)
            t2 = time.perf_counter()
            if t2-t1 > timeout+0.100:
                self.fail(f"Timout too late by: {t2-t1-timeout}")

        # test end timeout
        self.client.socket.settimeout(0)
        timeout = 0.500
        length = 1000
        with self.subTest("Part timout", timeout=timeout):

            def run(self, timeout, length):
                times = timeout * 2 // (self.client.COMMAND_TIMEOUT*0.5)
                for i in range(int(times)):
                    data = secrets.token_bytes(length//10).replace(
                        self.client.COMMAND_SEPERATOR, b'a')

                    self.server_socket.sendall(data)
                    time.sleep(self.client.COMMAND_TIMEOUT*0.5)

            thread = FunctionThread(target=run, args=[self, timeout, length])
            thread.start()
            with self.assertRaises(client.CommandTimeout):
                t1 = time.perf_counter()
                self.client.recv_command(
                    length*2, timeout=timeout)  # in seconds
            t2 = time.perf_counter()
            thread.join()

            if t2-t1 > timeout+self.client.COMMAND_TIMEOUT:
                self.fail(f"Timout too late by: {t2-t1-timeout}")

    def test_parse_info(self):
        """Test the parsing of an INFO command."""
        with self.subTest("Other command"):
            command = 'ERROR Some Exception was raised'

            res = self.client.parse_info(command)
            self.assertFalse(res)

        with self.subTest("Bad argument"):
            command = 'INFO bool version'

            res = self.client.parse_info(command)
            self.assertFalse(res)

        with self.subTest("Accepted"):
            command = 'INFO True 1.9.0-testlabel+meta'

            res = self.client.parse_info(command)

            self.assertNotEqual(res, False)
            self.assertTrue(len(res) >= 2)

            self.assertTrue(res[0])
            self.assertEqual(res[1], '1.9.0-testlabel+meta')

        with self.subTest("Refused"):
            command = 'INFO False 1.9.0-testlabel+meta'

            res = self.client.parse_info(command)

            self.assertNotEqual(res, False)
            self.assertTrue(len(res) >= 2)

            self.assertFalse(res[0])
            self.assertEqual(res[1], '1.9.0-testlabel+meta')

    def test_parse_update(self):
        """Test parsing an UPDATE USERS command."""
        with self.subTest("Other command"):
            command = 'INFO'

            res = self.client.parse_update(command)
            self.assertFalse(res)

        with self.subTest("Valid, one client"):
            command = 'UPDATE USERS 10'
            data = b'testclient'

            if self.server_socket.send(data) < len(data):
                raise Exception("Data wasn't sent at once.")

            res = self.client.parse_update(command)

            self.assertEqual(res, ['testclient'])

        with self.subTest("Valid, three client"):
            command = 'UPDATE USERS 21'
            data = b'testclient hello test'

            if self.server_socket.send(data) < len(data):
                raise Exception("Data wasn't sent at once.")

            res = self.client.parse_update(command)

            self.assertEqual(res, ['testclient', 'hello', 'test'])

        with self.subTest("Valid, complex client"):
            command = 'UPDATE USERS 7'
            data = b'hell_2g'

            if self.server_socket.send(data) < len(data):
                raise Exception("Data wasn't sent at once.")

            res = self.client.parse_update(command)

            self.assertEqual(res, ['hell_2g'])

        with self.subTest("Valid, no client"):
            command = 'UPDATE USERS 0'
            data = b''

            if self.server_socket.send(data) < len(data):
                raise Exception("Data wasn't sent at once.")

            res = self.client.parse_update(command)

            self.assertEqual(res, [])

        with self.subTest("Valid, small client"):
            command = 'UPDATE USERS 1'
            data = b'3'

            if self.server_socket.send(data) < len(data):
                raise Exception("Data wasn't sent at once.")

            res = self.client.parse_update(command)

            self.assertEqual(res, ['3'])

    def test_parse_package(self):
        with self.subTest("Other command"):
            command = 'INFO'

            res = self.client.parse_package(command)
            self.assertFalse(res)

        with self.subTest("Valid"):
            command = 'PACKAGE testtype FROM ben TO anna WITH 20'
            data = b'a\xd9\xf7\xafa-\xd3#\xea\xf3$\xedj\xa2\x1f[\xe6i\x85\xbe'

            package = client.Package('ben', 'anna', 'testtype')
            package.content = data

            if self.server_socket.send(data) < len(data):
                raise Exception("Data wasn't sent at once.")

            res = self.client.parse_package(command)

            self.assertEqual(res, package)

        with self.subTest("Empty"):
            command = 'PACKAGE testtype FROM ben TO anna WITH 0'
            data = b''

            package = client.Package('ben', 'anna', 'testtype')
            package.content = data

            if self.server_socket.send(data) < len(data):
                raise Exception("Data wasn't sent at once.")

            res = self.client.parse_package(command)

            self.assertEqual(res, package)

        with self.subTest("Small"):
            command = 'PACKAGE testtype FROM ben TO anna WITH 1'
            data = b'a'

            package = client.Package('ben', 'anna', 'testtype')
            package.content = data

            if self.server_socket.send(data) < len(data):
                raise Exception("Data wasn't sent at once.")

            res = self.client.parse_package(command)

            self.assertEqual(res, package)

    def test_parse_error(self):
        """Test parsing an ERROR command."""
        with self.subTest("Other command"):
            command = 'INFO'

            res = self.client.parse_error(command)
            self.assertFalse(res)

        with self.subTest("One word"):
            command = 'ERROR baderr'

            res = self.client.parse_error(command)
            self.assertEqual(res, 'baderr')

        with self.subTest("Three words"):
            command = 'ERROR Exception is bad'

            res = self.client.parse_error(command)
            self.assertEqual(res, 'Exception is bad')

    def test_send_command(self):
        with self.subTest("Empty"):
            self.client.send_command('')

            ans = self.server_socket.recv(4096)

            self.assertEqual(ans, self.client.COMMAND_SEPERATOR)

        with self.subTest("Normal"):
            self.client.send_command('HELLO test g3')

            ans = self.server_socket.recv(4096)

            self.assertEqual(ans, b'HELLO test g3' +
                             self.client.COMMAND_SEPERATOR)

        with self.subTest("With data"):
            self.client.send_command('HELLO test g3', b'gjkl')

            ans = self.server_socket.recv(4096)

            self.assertEqual(ans, b'HELLO test g3' +
                             self.client.COMMAND_SEPERATOR + b'gjkl')

    def test_send_info(self):
        self.client.send_info('testversion')
        ans = self.server_socket.recv(4096)

        self.assertEqual(ans, b'INFO testversion' +
                         self.client.COMMAND_SEPERATOR)

    def test_send_register(self):
        self.client.send_register('testname', 'testrole')
        ans = self.server_socket.recv(4096)

        self.assertEqual(ans, b'REGISTER testname AS testrole' +
                         self.client.COMMAND_SEPERATOR)

    def test_send_package(self):
        sep = self.client.COMMAND_SEPERATOR

        with self.subTest("Empty package"):
            package = client.Package("ben", "anna", "typ4")

            self.client.send_package(package)

            ans = self.server_socket.recv(4096)

            expected = b"PACKAGE typ4 FROM ben TO anna WITH 0" + sep
            self.assertEqual(ans, expected)

        with self.subTest("Normal package"):
            package = client.Package("ben", "anna", "typ4")
            package.content = b'Test'

            self.client.send_package(package)

            ans = self.server_socket.recv(4096)

            expected = b"PACKAGE typ4 FROM ben TO anna WITH 4" + sep + b'Test'
            self.assertEqual(ans, expected)

        with self.subTest("Small package"):
            package = client.Package("ben", "anna", "typ4")
            package.content = b'T'

            self.client.send_package(package)

            ans = self.server_socket.recv(4096)

            expected = b"PACKAGE typ4 FROM ben TO anna WITH 1" + sep + b'T'
            self.assertEqual(ans, expected)


class UserClientThreadTestCase(unittest.TestCase):

    def setUp(self):
        self.client: client.UserClient = client.UserClient('somename')

        self.client.socket, self.server_socket = socket.socketpair()

        self.thread = client.UserClientThread(self.client)
        self.client._thread = self.thread

        self.handler = ErrorDetectionHandler(logging.WARNING)
        client.logger.addHandler(self.handler)
        client.logger.propagate = False

    def test_server_closes(self):
        """Test closing the server socket during `run`."""
        self.thread.start()
        self.server_socket.close()

        time.sleep(0.3)

        self.assertFalse(self.thread.is_alive())
        self.assertTrue(self.handler.has_record(levelno=logging.WARNING))

        self.thread.join()

        for record in self.handler.records:
            if record.exc_info:
                raise record.exc_info[1]
            if record.levelno != logging.WARNING:
                raise Exception(record.message)

    def test_client_closes(self):
        """Test calling `client.disconnect` during `run`."""
        self.thread.start()
        self.client.disconnect()

        time.sleep(0.3)

        self.assertFalse(self.thread.is_alive())

        self.thread.join()

        for record in self.handler.records:
            if record.exc_info:
                raise record.exc_info[1]
            raise Exception(record.message)

    @unittest.skip("Not implemented yet.")
    def test_bad_command(self):
        pass  # TODO test_bad_command

    @unittest.skip("Not implemented yet.")
    def test_package(self):
        pass  # TODO test_package

    @unittest.skip("Not implemented yet.")
    def test_update(self):
        pass  # TODO test_update

    @unittest.skip("Not implemented yet.")
    def test_error(self):
        pass  # TODO test_error

    @unittest.skip("Not implemented yet.")
    def test_all_commands(self):
        pass  # TODO test_all_commands


class UserClientTestCase(unittest.TestCase):
    # TODO implement `UserClientTestCase`
    pass


def getModuleSuite():
    suite = unittest.TestSuite([])
    suite.addTest(loader.loadTestsFromTestCase(PackageTestCase))
    suite.addTest(loader.loadTestsFromTestCase(PackageStorageTestCase))
    suite.addTest(loader.loadTestsFromTestCase(ClientTestCase))
    suite.addTest(loader.loadTestsFromTestCase(UserClientTestCase))
    suite.addTest(loader.loadTestsFromTestCase(UserClientThreadTestCase))

    return suite


if __name__ == '__main__':
    # unittest.main(buffer=True, verbosity=3)
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=3, buffer=False)

    # suite = unittest.TestSuite([])
    # suite.addTest(loader.loadTestsFromTestCase(UserClientThreadTestCase))
    # runner.run(suite)

    runner.run(getModuleSuite())
