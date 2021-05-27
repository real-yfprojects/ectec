#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test client and server working together.

***********************************

Created on Sat May 15 17:09:54 2021

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
import logging
import threading
import time
import unittest

from __init__ import ErrorDetectionHandler, ectec


class SimpleClientServerTests(unittest.TestCase):

    def setUp(self):
        self.handler = ErrorDetectionHandler(logging.WARNING)
        ectec.client.logger.addHandler(self.handler)
        ectec.client.logger.propagate = False

        # stream_handler = logging.StreamHandler()
        # stream_handler.setLevel(logging.DEBUG)
        # stream_handler.setFormatter(ectec.logs.EctecFormatter())
        # ectec.server.logger.addHandler(stream_handler)
        # ectec.client.logger.propagate = False

    def check_logs(self):
        for record in self.handler.records:
            if record.exc_info:
                raise record.exc_info[1]
            if record.levelno > - logging.WARNING:
                raise Exception(record.message)

    # @unittest.skip("")
    def test_one_server(self):
        """Test starting and stopping one server."""
        server = ectec.server.Server()

        self.assertFalse(server.running)

        with server.start(0):
            self.assertTrue(server.running)

            self.assertFalse(server.users)

            self.assertTrue(server.port)

            self.assertTrue(server.address)

        self.assertFalse(server.running)

        self.check_logs()

    # @unittest.skip("")
    def test_one_client(self):
        """Test one client connecting to a server."""
        server = ectec.server.Server()

        with server.start(0):
            client = ectec.client.UserClient('Testuser')

            self.assertFalse(client.connected)
            self.assertFalse(client.server)

            with client.connect("0.0.0.0", server.port):
                # some client attribute tests
                self.assertTrue(client.connected)
                self.assertTrue(client.server.ip)
                self.assertEqual(client.server.port, server.port)
                self.assertFalse(len(client.packages))
                self.assertEqual(client.users, ["Testuser"])

                # some server attribute tests
                self.assertEqual(len(server.users), 1)
                self.assertEqual(server.users[0].name, "Testuser")
                self.assertEqual(server.users[0].role, ectec.Role.USER)

                # send package
                package = ectec.client.Package(
                    'testsender', 'testrecipient', 'text/plain')

                client.send(package)

                # shouldn't receive anything
                self.assertFalse(len(client.packages))

            self.assertFalse(client.connected)
            self.assertFalse(client.server)

            time.sleep(0.1)
            self.assertEqual(len(server.users), 0)

            self.check_logs()

    # @unittest.skip("")
    def test_two_clients(self):
        """Test two clients using the server."""
        server = ectec.server.Server()

        with server.start(0):
            client1 = ectec.client.UserClient('user_1')
            client2 = ectec.client.UserClient('user_2')

            with client1.connect("0.0.0.0", server.port):
                with client2.connect("0.0.0.0", server.port):
                    # some client1 attribute tests
                    self.assertEqual(client1.users, ["user_1", "user_2"])

                    # some client2 attribute tests
                    self.assertEqual(client2.users, ["user_1", "user_2"])

                    # some server attributes tests
                    self.assertEqual(len(server.users), 2)
                    self.assertEqual(server.users[0].name, "user_1")
                    self.assertEqual(server.users[0].role, ectec.Role.USER)

                    # send package
                    package = ectec.client.Package(
                        'client1', 'client2', 'text/plain')
                    client1.send(package)

                    # client1 shouldn't receive anything
                    self.assertFalse(len(client1.packages))

                    # client2 should receive something
                    self.assertTrue(client2.receive(block=True))
                    self.assertEqual(len(client2.packages), 1)

            time.sleep(0.1)
            self.assertEqual(len(server.users), 0)

            self.check_logs()

    def test_many_clients(self):
        """Test multiple clients using the server."""
        N = 10

        server = ectec.server.Server()
        self.assertEqual(len(server.users), 0)

        clients = []

        with server.start(0):
            try:  # for disconnecting already connected clients

                # ---- connect clients
                for i in range(N):
                    client = ectec.client.UserClient(f'userclient_{i}')
                    client.connect('0.0.0.0', server.port)

                    clients.append(client)

                    # check user list
                    time.sleep(0.01)
                    self.assertEqual(len(client.users), i+1, f"Iteration {i}")

                # check user list for server
                self.assertEqual(len(server.users), N)

                # check user list for client
                for client in clients:
                    client._update()
                    self.assertEqual(len(client.users), N, client.username)

                # ---- send package
                package = ectec.client.Package(
                    'client1', 'client2', 'text/plain')
                clients[0].send(package)

                # ---- receive package
                # sender shouldn't receive anything
                self.assertFalse(clients[0].receive(block=True))
                self.assertEqual(len(clients[0].packages), 0)

                time.sleep(0.01)
                for client in clients[1:]:
                    self.assertTrue(client.receive(
                        block=True), client.username)
                    self.assertEqual(len(client.packages), 1, client.username)

                # ---- send multiple packages at once
                send_event = threading.Event()

                def send_pkg(i):
                    send_event.wait()
                    package = ectec.client.Package(
                        f'userclient_{i}', f'userclient_{i+1}', 'text/plain')
                    clients[i].send(package)

                threads = []
                for i in range(len(clients)):
                    thread = threading.Thread(target=send_pkg, args=(i,))
                    thread.start()
                    threads.append(thread)

                # launch threads
                send_event.set()

                for thread in threads:
                    thread.join()

                # ---- receive the many packages
                time.sleep(0.05)
                for client in clients:
                    self.assertEqual(
                        len(client.receive(block=True)), len(clients)-1)

                # ---- disconnect
                for i in range(len(clients)):
                    clients[i].disconnect()

                    if i < len(clients)-1:
                        # check user list
                        time.sleep(0.01)
                        clients[i+1]._update()
                        self.assertEqual(len(clients[i+1].users), N-i-1, i)

            finally:

                # disconnect already connected clients
                for client in clients:
                    try:
                        client.disconnect()
                    except Exception as e:
                        print(e)

        time.sleep(0.1)
        self.assertEqual(len(server.users), 0)

        self.check_logs()


def getModuleSuite():
    suite = unittest.TestSuite([])
    suite.addTest(loader.loadTestsFromTestCase(SimpleClientServerTests))

    return suite


if __name__ == '__main__':
    # unittest.main(buffer=True, verbosity=3)
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=3, buffer=False)

    # suite = unittest.TestSuite([])
    # suite.addTest(loader.loadTestsFromTestCase(UserClientThreadTestCase))
    # runner.run(suite)

    runner.run(getModuleSuite())
