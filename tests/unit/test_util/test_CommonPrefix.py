#!/usr/bin/env python
# CPIP is a C/C++ Preprocessor implemented in Python.
# Copyright (C) 2008-2017 Paul Ross
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Paul Ross: apaulross@gmail.com

__author__  = 'Paul Ross'
__date__    = '2017-10-09'
__rights__  = 'Copyright (c) 2008-2017 Paul Ross'

import unittest

from cpip.util import CommonPrefix


class TestCommonPrefix(unittest.TestCase):

    def test_lenCommonPrefix_empty(self):
        result = CommonPrefix.lenCommonPrefix([])
        self.assertEqual(result, 0)

    def test_lenCommonPrefix_one(self):
        paths = ['path/to/file']
        result = CommonPrefix.lenCommonPrefix(paths)
        self.assertEqual(result, len('path/to/'))

    def test_lenCommonPrefix_many(self):
        paths = [
            'path/to/file_a',
            'path/to/another/file_a',
            'path/to/yetanother/file_a',
        ]
        result = CommonPrefix.lenCommonPrefix(paths)
        self.assertEqual(result, len('path/to/'))

    def test_lenCommonPrefix_many_nothing_in_common(self):
        paths = [
            'apath/to/file_a',
            'bpath/to/another/file_a',
            'cpath/to/yetanother/file_a',
        ]
        result = CommonPrefix.lenCommonPrefix(paths)
        self.assertEqual(result, 0)

if __name__ == '__main__':
    unittest.main()
