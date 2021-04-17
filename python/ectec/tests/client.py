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
import os.path as osp
import sys
import unittest

if True:  # isort formatting
    PATH = sys.path
    sys.path.append(osp.abspath(osp.join(__file__, '../../')))

import src as ectec
from src import client


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
            self.assertEqual(p.recipient, ('testrecipient'))
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

            filtered = list(ps.filter(recipient=('testrecipient')))

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


if __name__ == '__main__':
    # unittest.main(buffer=True, verbosity=3)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite([])

    suite.addTest(loader.loadTestsFromTestCase(PackageTestCase))
    suite.addTest(loader.loadTestsFromTestCase(PackageStorageTestCase))

    runner = unittest.TextTestRunner(verbosity=3, buffer=False)

    runner.run(suite)
