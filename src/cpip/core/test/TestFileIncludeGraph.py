#!/usr/bin/env python
# CPIP is a C/C++ Preprocessor implemented in Python.
# Copyright (C) 2008-2011 Paul Ross
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
# Paul Ross: cpipdev@googlemail.com

"""Unit tests for FileIncludeGraph."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import os
import sys
import time
import logging

from cpip.core import FileIncludeGraph, PpToken, PpTokenCount

######################
# Section: Unit tests.
######################
import unittest

class TestFileIncludeGraph(unittest.TestCase):
    """Tests the class FileIncludeGraph."""

    def testCtor(self):
        """FileIncludeGraph - construction."""
        myObj = FileIncludeGraph.FileIncludeGraph('a.h', True, '', '')
        self.assertEqual('a.h', myObj.fileName)
        self.assertEqual(0, len(myObj._graph))

    def testCtorAddBranch_00(self):
        """FileIncludeGraph - construction and addBranch [00] a.h #includes b.h."""
        myObj = FileIncludeGraph.FileIncludeGraph('a.h', True, '', '')
        self.assertEqual('a.h', myObj.fileName)
        self.assertEqual(0, len(myObj._graph))
        myObj.addBranch(['a.h',], 1, 'b.h', True, '', '')
        self.assertEqual([['a.h',], ['a.h#1', 'b.h'],], myObj.retBranches())

    def testCtorAddBranch_01(self):
        """FileIncludeGraph - construction and addBranch [01] a.h #includes b.h that #includes c.h."""
        myObj = FileIncludeGraph.FileIncludeGraph('a.h', True, '', '')
        self.assertEqual('a.h', myObj.fileName)
        self.assertEqual(0, len(myObj._graph))
        myObj.addBranch(['a.h',], 1, 'b.h', True, '', '')
        self.assertEqual([['a.h',], ['a.h#1', 'b.h'],], myObj.retBranches())
        myObj.addBranch(['a.h', 'b.h'], 2, 'c.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
            ],
            myObj.retBranches())
        myObj.addBranch(['a.h', 'b.h', 'c.h'], 3, 'd3.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
            ],
            myObj.retBranches())
        myObj.addBranch(['a.h', 'b.h', 'c.h'], 4, 'd4.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
            ],
            myObj.retBranches())
        myObj.addBranch(['a.h', 'b.h'], 7, 't.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
                ['a.h#1', 'b.h#7', 't.h'],
            ],
            myObj.retBranches())
        myObj.addBranch(['a.h',], 5, 'x.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
                ['a.h#1', 'b.h#7', 't.h'],
                ['a.h#5', 'x.h'],
            ],
            myObj.retBranches())

    def testCtorAddBranchException(self):
        """FileIncludeGraph - construction and addBranch with exceptions."""
        myObj = FileIncludeGraph.FileIncludeGraph('a.h', True, '', '')
        self.assertEqual('a.h', myObj.fileName)
        self.assertEqual(0, len(myObj._graph))
        myObj.addBranch(['a.h',], 1, 'b.h', True, '', '')
        self.assertEqual([['a.h',], ['a.h#1', 'b.h'],], myObj.retBranches())
        # Empty branch
        self.assertRaises(FileIncludeGraph.ExceptionFileIncludeGraph,
                          myObj.addBranch,
                          [],
                          1,
                          'b.h',
                          True, 
                          '',
                          '')
        # Wrong root file
        self.assertRaises(FileIncludeGraph.ExceptionFileIncludeGraph,
                          myObj.addBranch,
                          ['b.h',],
                          1,
                          'b.h',
                          True, 
                          '',
                          '')
        # Right root but duplicate line
        self.assertRaises(FileIncludeGraph.ExceptionFileIncludeGraph,
                          myObj.addBranch,
                          ['a.h',],
                          1,
                          'b.h',
                          True, 
                          '',
                          '')
        # Right root, no duplicate line, but missing prior addBranch of 'c.h'
        self.assertRaises(FileIncludeGraph.ExceptionFileIncludeGraph,
                          myObj.addBranch,
                          ['a.h', 'b.h', 'c.h'],
                          2,
                          'd.h',
                          True, 
                          '',
                          '')

class TestFileIncludeGraphPlot(unittest.TestCase):
    """Tests the class FileIncludeGraph result."""

    def testStringRepresentation(self):
        """FileIncludeGraph - string representation."""
        myObj = FileIncludeGraph.FileIncludeGraph('a.h', True, 'a > 1', 'CP=a')
        self.assertEqual('a.h', myObj.fileName)
        self.assertEqual(0, len(myObj._graph))
        myObj.addBranch(['a.h',], 1, 'b.h', True, 'b > 0', 'CP=b')
        self.assertEqual([['a.h',], ['a.h#1', 'b.h'],], myObj.retBranches())
        myObj.addBranch(['a.h', 'b.h'], 2, 'c.h', True, 'c > 0', 'CP=c')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
            ],
            myObj.retBranches())
        myObj.addBranch(['a.h', 'b.h', 'c.h'], 3, 'd3.h', True, 'd > 3', 'CP=d')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
            ],
            myObj.retBranches())
        myObj.addBranch(['a.h', 'b.h', 'c.h'], 4, 'd4.h', True, 'd > 4', 'CP=d4')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
            ],
            myObj.retBranches())
        myObj.addBranch(['a.h', 'b.h'], 7, 't.h', True, 't > 0', 'CP=t')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
                ['a.h#1', 'b.h#7', 't.h'],
            ],
            myObj.retBranches())
        myObj.addBranch(['a.h',], 5, 'x.h', True, 'x > 0', 'CP=x')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
                ['a.h#1', 'b.h#7', 't.h'],
                ['a.h#5', 'x.h'],
            ],
            myObj.retBranches(),
            )
#        print()
#        print(myObj)
        self.assertEqual(
                         """a.h [None, None]:  True "a > 1" "CP=a"
000001: #include b.h
  b.h [None, None]:  True "b > 0" "CP=b"
  000002: #include c.h
    c.h [None, None]:  True "c > 0" "CP=c"
    000003: #include d3.h
      d3.h [None, None]:  True "d > 3" "CP=d"
    000004: #include d4.h
      d4.h [None, None]:  True "d > 4" "CP=d4"
  000007: #include t.h
    t.h [None, None]:  True "t > 0" "CP=t"
000005: #include x.h
  x.h [None, None]:  True "x > 0" "CP=x\"""",
                        str(myObj),
        )

class TestFileIncludeGetBranchLeaf(unittest.TestCase):
    """Tests the class FileIncludeGraph result."""

    def testGetBranchLeaf_00(self):
        """FileIncludeGraph - getting latest leaf and branches [00]."""
        # The ITU
        myObj = FileIncludeGraph.FileIncludeGraph('a.h', True, '', '')
        self.assertEqual('a.h', myObj.fileName)
        self.assertEqual(0, len(myObj._graph))
        self.assertEqual('a.h', myObj.retLatestLeaf().fileName)
        self.assertEqual(['a.h',], myObj.retLatestBranch())
        self.assertEqual(1, myObj.retLatestBranchDepth())
        #include "b.h"
        myObj.addBranch(['a.h',], 1, 'b.h', True, '', '')
        self.assertEqual([['a.h',], ['a.h#1', 'b.h'],], myObj.retBranches())
        self.assertEqual('b.h', myObj.retLatestLeaf().fileName)
        self.assertEqual(['a.h#1', 'b.h'], myObj.retLatestBranch())
        self.assertEqual([('a.h', 1), ('b.h', None)], myObj.retLatestBranchPairs())
        self.assertEqual(2, myObj.retLatestBranchDepth())
        #include "c.h"
        myObj.addBranch(['a.h', 'b.h'], 2, 'c.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
            ],
            myObj.retBranches())
        self.assertEqual('c.h', myObj.retLatestLeaf().fileName)
        self.assertEqual(['a.h#1', 'b.h#2', 'c.h',], myObj.retLatestBranch())
        self.assertEqual([('a.h', 1), ('b.h', 2), ('c.h', None),], myObj.retLatestBranchPairs())
        self.assertEqual(3, myObj.retLatestBranchDepth())
        #include "d3.h"
        myObj.addBranch(['a.h', 'b.h', 'c.h'], 3, 'd3.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
            ],
            myObj.retBranches())
        self.assertEqual('d3.h', myObj.retLatestLeaf().fileName)
        self.assertEqual(['a.h#1', 'b.h#2', 'c.h#3', 'd3.h',], myObj.retLatestBranch())
        self.assertEqual(4, myObj.retLatestBranchDepth())
        self.assertEqual(
                         [('a.h', 1), ('b.h', 2), ('c.h', 3), ('d3.h', None),],
                         myObj.retLatestBranchPairs()
                         )
        # End: #include "d3.h"
        #include "d4.h"
        myObj.addBranch(['a.h', 'b.h', 'c.h'], 4, 'd4.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
            ],
            myObj.retBranches())
        self.assertEqual('d4.h', myObj.retLatestLeaf().fileName)
        self.assertEqual(['a.h#1', 'b.h#2', 'c.h#4', 'd4.h',], myObj.retLatestBranch())
        self.assertEqual(4, myObj.retLatestBranchDepth())
        self.assertEqual(
                         [('a.h', 1), ('b.h', 2), ('c.h', 4), ('d4.h', None),],
                         myObj.retLatestBranchPairs()
                         )
        # End: #include "d4.h"
        # End: #include "c.h"
        #include "t.h"
        myObj.addBranch(['a.h', 'b.h'], 7, 't.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
                ['a.h#1', 'b.h#7', 't.h'],
            ],
            myObj.retBranches())
        self.assertEqual('t.h', myObj.retLatestLeaf().fileName)
        self.assertEqual(['a.h#1', 'b.h#7', 't.h',], myObj.retLatestBranch())
        self.assertEqual(3, myObj.retLatestBranchDepth())
        self.assertEqual(
                         [('a.h', 1), ('b.h', 7), ('t.h', None),],
                         myObj.retLatestBranchPairs()
                         )
        # End: #include "t.h"
        # End: #include "b.h"
        #include "x.h"
        myObj.addBranch(['a.h',], 5, 'x.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
                ['a.h#1', 'b.h#7', 't.h'],
                ['a.h#5', 'x.h'],
            ],
            myObj.retBranches(),
            )
        self.assertEqual('x.h', myObj.retLatestLeaf().fileName)
        self.assertEqual(['a.h#5', 'x.h',], myObj.retLatestBranch())
        self.assertEqual(2, myObj.retLatestBranchDepth())
        self.assertEqual(
                         [('a.h', 5), ('x.h', None),],
                         myObj.retLatestBranchPairs()
                         )
        # End: ITU "a.h"

    def test_retLatestNode_00(self):
        """FileIncludeGraph.retLatestNode() - getting latest node by branch."""
        # The ITU
        myObj = FileIncludeGraph.FileIncludeGraph('a.h', True, '', '')
        self.assertEqual('a.h',
                         myObj.retLatestNode(['a.h',]).fileName,
                         )
        #include "b.h"
        myObj.addBranch(['a.h',], 1, 'b.h', True, '', '')
        self.assertEqual('a.h',
                         myObj.retLatestNode(['a.h',]).fileName,
                         )
        self.assertEqual('b.h',
                         myObj.retLatestNode(['a.h', 'b.h',]).fileName,
                         )
        #include "c.h"
        myObj.addBranch(['a.h', 'b.h'], 2, 'c.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
            ],
            myObj.retBranches())
        self.assertEqual('a.h',
                         myObj.retLatestNode(['a.h',]).fileName,
                         )
        self.assertEqual('b.h',
                         myObj.retLatestNode(['a.h', 'b.h',]).fileName,
                         )
        self.assertEqual('c.h',
                         myObj.retLatestNode(['a.h', 'b.h', 'c.h']).fileName,
                         )
        #include "d3.h"
        myObj.addBranch(['a.h', 'b.h', 'c.h'], 3, 'd3.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
            ],
            myObj.retBranches())
        self.assertEqual('a.h',
                         myObj.retLatestNode(['a.h',]).fileName,
                         )
        self.assertEqual('b.h',
                         myObj.retLatestNode(['a.h', 'b.h',]).fileName,
                         )
        self.assertEqual('c.h',
                         myObj.retLatestNode(['a.h', 'b.h', 'c.h']).fileName,
                         )
        self.assertEqual('d3.h',
                         myObj.retLatestNode(['a.h', 'b.h', 'c.h', 'd3.h']).fileName,
                         )
        # End: #include "d3.h"
        #include "d4.h"
        myObj.addBranch(['a.h', 'b.h', 'c.h'], 4, 'd4.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
            ],
            myObj.retBranches())
        self.assertEqual('a.h',
                         myObj.retLatestNode(['a.h',]).fileName,
                         )
        self.assertEqual('b.h',
                         myObj.retLatestNode(['a.h', 'b.h',]).fileName,
                         )
        self.assertEqual('c.h',
                         myObj.retLatestNode(['a.h', 'b.h', 'c.h']).fileName,
                         )
        # Graph edge has changed
        self.assertRaises(FileIncludeGraph.ExceptionFileIncludeGraph,
                          myObj.retLatestNode,
                          ['a.h', 'b.h', 'c.h', 'd3.h'],
                          )
        # This graph edge is good...
        self.assertEqual('d4.h',
                         myObj.retLatestNode(['a.h', 'b.h', 'c.h', 'd4.h']).fileName,
                         )
        # End: #include "d4.h"
        # End: #include "c.h"
        #include "t.h"
        myObj.addBranch(['a.h', 'b.h'], 7, 't.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
                ['a.h#1', 'b.h#7', 't.h'],
            ],
            myObj.retBranches())
        self.assertEqual('a.h',
                         myObj.retLatestNode(['a.h',]).fileName,
                         )
        self.assertEqual('b.h',
                         myObj.retLatestNode(['a.h', 'b.h',]).fileName,
                         )
        # Graph edge has changed
        self.assertRaises(FileIncludeGraph.ExceptionFileIncludeGraph,
                          myObj.retLatestNode,
                          ['a.h', 'b.h', 'c.h',],
                          )
        # This graph edge is good...
        self.assertEqual('t.h',
                         myObj.retLatestNode(['a.h', 'b.h', 't.h']).fileName,
                         )
        # End: #include "t.h"
        # End: #include "b.h"
        #include "x.h"
        myObj.addBranch(['a.h',], 5, 'x.h', True, '', '')
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
                ['a.h#1', 'b.h#7', 't.h'],
                ['a.h#5', 'x.h'],
            ],
            myObj.retBranches(),
            )
        self.assertEqual('a.h',
                         myObj.retLatestNode(['a.h',]).fileName,
                         )
        # Graph edge has changed
        self.assertRaises(FileIncludeGraph.ExceptionFileIncludeGraph,
                          myObj.retLatestNode,
                          ['a.h', 'b.h',],
                          )
        self.assertRaises(FileIncludeGraph.ExceptionFileIncludeGraph,
                          myObj.retLatestNode,
                          ['a.h', 'b.h', 'c.h',],
                          )
        # This graph edge is good...
        self.assertEqual('x.h',
                         myObj.retLatestNode(['a.h', 'x.h']).fileName,
                         )
        # End: #include "x.h"
        self.assertEqual(
            [
                ['a.h',],
                ['a.h#1', 'b.h'],
                ['a.h#1', 'b.h#2', 'c.h'],
                ['a.h#1', 'b.h#2', 'c.h#3', 'd3.h'],
                ['a.h#1', 'b.h#2', 'c.h#4', 'd4.h'],
                ['a.h#1', 'b.h#7', 't.h'],
                ['a.h#5', 'x.h'],
            ],
            myObj.retBranches(),
            )
        self.assertEqual('a.h',
                         myObj.retLatestNode(['a.h',]).fileName,
                         )
        # Graph edge has changed
        self.assertRaises(FileIncludeGraph.ExceptionFileIncludeGraph,
                          myObj.retLatestNode,
                          ['a.h', 'b.h',],
                          )
        # This graph edge is good...
        self.assertEqual('x.h',
                         myObj.retLatestNode(['a.h', 'x.h']).fileName,
                         )
        # End: ITU "a.h"

    def test_retLatestNode_01(self):
        """FileIncludeGraph.retLatestNode() - bad call with zero length branch."""
        myObj = FileIncludeGraph.FileIncludeGraph('a.h', True, '', '')
        self.assertRaises(FileIncludeGraph.ExceptionFileIncludeGraph,
                          myObj.retLatestNode,
                          [],
                          )

class TestFileIncludeGraphAttributeSetGet(unittest.TestCase):
    """Tests the class FileIncludeGraph."""

    def testCtor_SetAttributes(self):
        """FileIncludeGraph - ctor, set attributes."""
        myObj = FileIncludeGraph.FileIncludeGraph('a.h', True, '', '')
        self.assertEqual('a.h', myObj.fileName)
        self.assertEqual(0, len(myObj._graph))
        myTcs = PpTokenCount.PpTokenCountStack()
        #myFs = []
        myTcs.push()
        #myFs.append('PreInclude_00')
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), True, 31)
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), False, 10)
        myObj.setTokenCounter(myTcs.pop())
        self.assertEqual(41, myObj.numTokens)
        self.assertEqual(31, myObj.numTokensSig)

    def testCtorAddBranch_SetAttributes_00(self):
        """FileIncludeGraph - ctor, addBranch [00] a.h #includes b.h. Set attributes."""
        myObj = FileIncludeGraph.FileIncludeGraph('a.h', True, '', '')
        self.assertEqual('a.h', myObj.fileName)
        self.assertEqual(0, len(myObj._graph))
        myObj.addBranch(['a.h',], 1, 'b.h', True, '', '')
        self.assertEqual([['a.h',], ['a.h#1', 'b.h'],], myObj.retBranches())

    def testCtor_SetAttributes_01(self):
        """FileIncludeGraph - ctor, set setTokenCounter()."""
        myObj = FileIncludeGraph.FileIncludeGraph('a.h', True, '', '')
        self.assertEqual('a.h', myObj.fileName)
        self.assertEqual(0, len(myObj._graph))
        myTcs = PpTokenCount.PpTokenCountStack()
        #myFs = []
        myTcs.push()
        #myFs.append('PreInclude_00')
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), True, 10)
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), False, 21)
        myObj.setTokenCounter(myTcs.pop())
        self.assertEqual(31, myObj.numTokens)
        self.assertEqual(10, myObj.numTokensSig)

class TestFileIncludeGraphDummyRoot(unittest.TestCase):
    """Tests the class FileIncludeGraph where None is the root of the branch."""

    def testCtor(self):
        """FileIncludeGraph - test ctor with dummy root."""
        myObj = FileIncludeGraph.FileIncludeGraph(None, True, '', '')
        self.assertEqual(None, myObj.fileName)
        self.assertEqual(0, len(myObj._graph))

    def testCtorAddBranch_00(self):
        """FileIncludeGraph - construction and addBranch [00] a.h #includes b.h."""
        myObj = FileIncludeGraph.FileIncludeGraph(None, True, '', '')
        self.assertEqual(None, myObj.fileName)
        self.assertEqual(0, len(myObj._graph))
        myObj.addBranch(
            [None,],
            FileIncludeGraph.DUMMY_FILE_LINENUM,
            'a.h',
            True,
            '',
            ''
            )
        self.assertEqual(
            [
                [None,],
                ['None#%d' % FileIncludeGraph.DUMMY_FILE_LINENUM, 'a.h'],
            ],
                myObj.retBranches())
        self.assertRaises(
            FileIncludeGraph.ExceptionFileIncludeGraph,
            myObj.addBranch,
            [None,],
            FileIncludeGraph.DUMMY_FILE_LINENUM,
            'b.h',
            True,
            '',
            ''
            )
    
class TestFileIncludeGraphRoot(unittest.TestCase):
    """Tests the class FileIncludeGraphRoot and simulates virtual roots."""
    
    def testCtor(self):
        """FileIncludeGraphRoot constructor."""
        myFigr = FileIncludeGraph.FileIncludeGraphRoot()
        self.assertEqual(0, myFigr.numTrees())
        #print
        #print myFigr
        self.assertEqual('', str(myFigr))
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('PreInclude_00', True, 'a >= b+2', 'Forced PreInclude_00'))
        self.assertEqual(1, myFigr.numTrees())
        #print myFigr
        self.assertEqual('PreInclude_00 [None, None]:  True "a >= b+2" "Forced PreInclude_00"', str(myFigr))
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('PreInclude_01', True, 'x > 1', 'Forced PreInclude_01'))
        self.assertEqual(2, myFigr.numTrees())
        #print myFigr
        self.assertEqual("""PreInclude_00 [None, None]:  True "a >= b+2" "Forced PreInclude_00"
PreInclude_01 [None, None]:  True "x > 1" "Forced PreInclude_01\"""", str(myFigr))

    def testGraphRaises(self):
        """FileIncludeGrphRoot graph raises on empty."""
        myFigr = FileIncludeGraph.FileIncludeGraphRoot()
        self.assertEqual(0, myFigr.numTrees())
        # Use try/except as this is a property
        try:
            myFigr.graph
            self.fail('FileIncludeGraph.ExceptionFileIncludeGraphRoot not raised.')
        except FileIncludeGraph.ExceptionFileIncludeGraphRoot:
            pass

    def testCtorAndIncTokens(self):
        """FileIncludeGraphRoot constructor with one graph and incrementing token count."""
        myFigr = FileIncludeGraph.FileIncludeGraphRoot()
        self.assertEqual(0, myFigr.numTrees())
        #print
        #print myFigr
        self.assertEqual('', str(myFigr))
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('PreInclude_00', True, 'a >= b+2', 'Forced PreInclude_00'))
        self.assertEqual(1, myFigr.numTrees())
        self.assertEqual('PreInclude_00 [None, None]:  True "a >= b+2" "Forced PreInclude_00"', str(myFigr))
        myTc = PpTokenCount.PpTokenCount()
        myTc.inc(PpToken.PpToken('PreInclude_00', 'identifier'), True, num=17)
        myTc.inc(PpToken.PpToken('PreInclude_00', 'identifier'), False, num=7)
        myFigr.graph.setTokenCounter(myTc)
        self.assertEqual('PreInclude_00 [24, 17]:  True "a >= b+2" "Forced PreInclude_00"', str(myFigr))

    def testCtorAddBranchIncTokens(self):
        """FileIncludeGraphRoot constructor with one graph, adding branch and incrementing token count."""
        myFigr = FileIncludeGraph.FileIncludeGraphRoot()
        self.assertEqual(0, myFigr.numTrees())
        self.assertEqual('', str(myFigr))
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('a.h', True, 'a >= b+2', 'CP=.'))
        self.assertEqual(1, myFigr.numTrees())
        self.assertEqual('a.h [None, None]:  True "a >= b+2" "CP=."', str(myFigr))
        myFigr.graph.addBranch(['a.h',], 1, 'b.h', True, '', 'CP=.')
        self.assertEqual([['a.h',], ['a.h#1', 'b.h'],], myFigr.graph.retBranches())
        myTc = PpTokenCount.PpTokenCount()
        #myTcs = PpTokenCount.PpTokenCountStack()
        #myFs = []
        #myTcs.push()
        #myFs.append('PreInclude_00')
        myTc.inc(PpToken.PpToken('a.h', 'identifier'), True, num=17)
        myTc.inc(PpToken.PpToken('a.h', 'identifier'), False, num=7)
        myFigr.graph.setTokenCounter(myTc)
        #print
        #print myFigr
        self.assertEqual(
            """a.h [24, 17]:  True "a >= b+2" "CP=."
000001: #include b.h
  b.h [None, None]:  True "" "CP=.\"""",
            str(myFigr),
        )

    def testCtorAddBranchesIncTokens(self):
        """FileIncludeGraphRoot constructor with multiple graphs, adding branch and incrementing token count."""
        myFigr = FileIncludeGraph.FileIncludeGraphRoot()
        self.assertEqual(0, myFigr.numTrees())
        self.assertEqual('', str(myFigr))
        # Simulate a pre-include
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('PreInc_00', True, '', 'Forced PreInc_00'))
        myTcs = PpTokenCount.PpTokenCountStack()
        myFs = []
        myTcs.push()
        myFs.append('PreInc_00')
        self.assertEqual(1, myFigr.numTrees())
        self.assertEqual('PreInc_00 [None, None]:  True "" "Forced PreInc_00"', str(myFigr))
        # push a.h
        myFigr.graph.addBranch(['PreInc_00',], 1, 'a.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('a.h')
        self.assertEqual([['PreInc_00',], ['PreInc_00#1', 'a.h'],], myFigr.graph.retBranches())
        # Set tokens for a.h
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), True, 91)
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), False, 26)
        # pop a.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        # Set tokens for PreInc_00
        myTcs.counter().inc(PpToken.PpToken('PreInc_00', 'identifier'), True, 17)
        myTcs.counter().inc(PpToken.PpToken('PreInc_00', 'identifier'), False, 7)
        # pop a.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 0)
        #print
        #print myFigr
        self.assertEqual(
            """PreInc_00 [24, 17]:  True "" "Forced PreInc_00"
000001: #include a.h
  a.h [117, 91]:  True "" "CP=.\"""",
            str(myFigr),
        )
        # Simulate a new pre-include
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('PreInc_01', True, '', 'Forced PreInc_01'))
        myTcs.push()
        myFs.append('PreInc_01')
        self.assertEqual(2, myFigr.numTrees())
        #print
        #print myFigr
        self.assertEqual("""PreInc_00 [24, 17]:  True "" "Forced PreInc_00"
000001: #include a.h
  a.h [117, 91]:  True "" "CP=."
PreInc_01 [None, None]:  True "" "Forced PreInc_01\"""", str(myFigr))
        # Add a new branch
        myFigr.graph.addBranch(['PreInc_01',], 15, 'b.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('b.h')
        self.assertEqual([['PreInc_01',], ['PreInc_01#15', 'b.h'],], myFigr.graph.retBranches())
        # Set tokens for b.h
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), True, 914)
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), False, 257)
        # pop b.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        # Set tokens for PreInc_01
        myTcs.counter().inc(PpToken.PpToken('PreInc_01', 'identifier'), True, 170)
        myTcs.counter().inc(PpToken.PpToken('PreInc_01', 'identifier'), False, 70)
        # pop PreInc_01
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        myTcs.close()
        self.assertEqual(len(myFs), 0)
        #print
        #print myFigr
        self.assertEqual(
            """PreInc_00 [24, 17]:  True "" "Forced PreInc_00"
000001: #include a.h
  a.h [117, 91]:  True "" "CP=."
PreInc_01 [240, 170]:  True "" "Forced PreInc_01"
000015: #include b.h
  b.h [1171, 914]:  True "" "CP=.\"""",
            str(myFigr),
        )

class MyVisitorTreeNode(FileIncludeGraph.FigVisitorTreeNodeBase):
    PAD = '  '
    def __init__(self, theFig, theLineNum):
        super(MyVisitorTreeNode, self).__init__(theLineNum)
        if theFig is None:
            self._name = None
            self._t = 0
        else:
            #print 'MyVisitorTreeNode.__init__(%s)' % theFig 
            self._name = theFig.fileName
            self._t = theFig.numTokens
            
    def finalise(self):
        for aChild in self._children:
            aChild.finalise()
            self._t += aChild._t
            
    def __str__(self):
        return self.retStr(0)
        
    def retStr(self, d):
        r = '%s%04d %s\n' % (self.PAD*d, self._lineNum, self._name)
        for aC in self._children:
            r += aC.retStr(d+1)
        return r
        

class TestFileIncludeGraphRootVisitorBase(unittest.TestCase):
    """Base class for testing visitors, setUp() loads self._figr (a FileIncludeGraphRoot)."""
    def setUpTwoPreIncludesAndAGraph(self):
        """setUp(): Two pre-includes and a graph."""
        self._figr = FileIncludeGraph.FileIncludeGraphRoot()
        myTcs = PpTokenCount.PpTokenCountStack()
        myFs = []
        # push PreInclude_00
        self._figr.addGraph(FileIncludeGraph.FileIncludeGraph('PreInclude_00', True, 'a >= b+2', 'Forced PreInclude_00'))
        myTcs.push()
        myFs.append('PreInclude_00')
        myTcs.counter().inc(PpToken.PpToken('PreInclude_00', 'identifier'), True, 50)
        myTcs.counter().inc(PpToken.PpToken('PreInclude_00', 'identifier'), False, 50)
        # pop PreInclude_00
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 0)
        # push PreInclude_01
        self._figr.addGraph(FileIncludeGraph.FileIncludeGraph('PreInclude_01', True, 'x > 1', 'Forced PreInclude_00'))
        myTcs.push()
        myFs.append('PreInclude_01')
        myTcs.counter().inc(PpToken.PpToken('PreInclude_01', 'identifier'), True, 60)
        myTcs.counter().inc(PpToken.PpToken('PreInclude_01', 'identifier'), False, 60)
        # pop PreInclude_01
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 0)
        # push ITU.h
        self._figr.addGraph(FileIncludeGraph.FileIncludeGraph('ITU.h', True, '', 'CP=.'))
        myTcs.push()
        myFs.append('ITU.h')
        self.assertEqual(3, self._figr.numTrees())
        # push ITU.h/a.h
        self._figr.graph.addBranch(['ITU.h',], 15, 'a.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('a.h')
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), True, 1)
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), False, 1)
        # push ITU.h/a.h/aa.h
        self._figr.graph.addBranch(['ITU.h', 'a.h'], 17, 'aa.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('aa.h')
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), True, 2)
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), False, 2)
        # pop ITU.h/a.h/aa.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # push ITU.h/a.h/ab.h
        self._figr.graph.addBranch(['ITU.h', 'a.h'], 19, 'ab.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('ab.h')
        myTcs.counter().inc(PpToken.PpToken('ab.h', 'identifier'), True, 4)
        myTcs.counter().inc(PpToken.PpToken('ab.h', 'identifier'), False, 4)
        # pop ITU.h/a.h/ab.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # pop ITU.h/a.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 1)
        # push ITU.h/b.h
        self._figr.graph.addBranch(['ITU.h',], 115, 'b.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('b.h')
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), True, 8)
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), False, 8)
        # push ITU.h/b.h/ba.h
        self._figr.graph.addBranch(['ITU.h', 'b.h'], 117, 'ba.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('ba.h')
        myTcs.counter().inc(PpToken.PpToken('ba.h', 'identifier'), True, 16)
        myTcs.counter().inc(PpToken.PpToken('ba.h', 'identifier'), False, 16)
        # pop ITU.h/b.h/ba.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # push ITU.h/b.h/bb.h
        self._figr.graph.addBranch(['ITU.h', 'b.h'], 119, 'bb.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('bb.h')
        myTcs.counter().inc(PpToken.PpToken('bb.h', 'identifier'), True, 32)
        myTcs.counter().inc(PpToken.PpToken('bb.h', 'identifier'), False, 32)
        # pop ITU.h/b.h/bb.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # pop ITU.h/b.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 1)
        # ITU.h
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), True, 70)
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), False, 70)
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 0)
        myTcs.close()
        expGraph = """PreInclude_00 [100, 50]:  True "a >= b+2" "Forced PreInclude_00"
PreInclude_01 [120, 60]:  True "x > 1" "Forced PreInclude_00"
ITU.h [140, 70]:  True "" "CP=."
000015: #include a.h
  a.h [2, 1]:  True "" "CP=."
  000017: #include aa.h
    aa.h [4, 2]:  True "" "CP=."
  000019: #include ab.h
    ab.h [8, 4]:  True "" "CP=."
000115: #include b.h
  b.h [16, 8]:  True "" "CP=."
  000117: #include ba.h
    ba.h [32, 16]:  True "" "CP=."
  000119: #include bb.h
    bb.h [64, 32]:  True "" "CP=.\""""
        #print
        #print expGraph
        #print
        #print str(self._figr)
        self.assertEqual(expGraph, str(self._figr))

    def setUpNoPreIncludesAndAGraph(self):
        """TestFileIncludeGraphRootVisitorBase: No pre-includes and a graph."""
        self._figr = FileIncludeGraph.FileIncludeGraphRoot()
        myTcs = PpTokenCount.PpTokenCountStack()
        myFs = []
        self._figr.addGraph(FileIncludeGraph.FileIncludeGraph('ITU.h', True, '', 'ITU'))
        self.assertEqual(1, self._figr.numTrees())
        myTcs.push()
        myFs.append('ITU.h')
        # push ITU.h/a.h
        self._figr.graph.addBranch(['ITU.h',], 15, 'a.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('a.h')
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), True, 1)
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), False, 1)
        # push ITU.h/a.h/aa.h
        self._figr.graph.addBranch(['ITU.h', 'a.h'], 17, 'aa.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('aa.h')
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), True, 2)
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), False, 2)
        # push ITU.h/a.h/aa.h/aaa.h
        self._figr.graph.addBranch(['ITU.h', 'a.h', 'aa.h'], 19, 'aaa.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('aaa.h')
        myTcs.counter().inc(PpToken.PpToken('aaa.h', 'identifier'), True, 4)
        myTcs.counter().inc(PpToken.PpToken('aaa.h', 'identifier'), False, 4)
        # push ITU.h/a.h/aa.h/aaa.h/aaaa.h
        self._figr.graph.addBranch(['ITU.h', 'a.h', 'aa.h', 'aaa.h'], 20, 'aaaa.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('aaaa.h')
        myTcs.counter().inc(PpToken.PpToken('aaaa.h', 'identifier'), True, 42)
        myTcs.counter().inc(PpToken.PpToken('aaaa.h', 'identifier'), False, 38)
        # pop ITU.h/a.h/aa.h/aaa.h/aaaa.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 4)
        # push ITU.h/a.h/aa.h/aaa.h/aaab.h
        self._figr.graph.addBranch(['ITU.h', 'a.h', 'aa.h', 'aaa.h'], 21, 'aaab.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('aaab.h')
        myTcs.counter().inc(PpToken.PpToken('aaab.h', 'identifier'), True, 43)
        myTcs.counter().inc(PpToken.PpToken('aaab.h', 'identifier'), False, 38)
        # pop ITU.h/a.h/aa.h/aaa.h/aaab.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 4)
        # pop ITU.h/a.h/aa.h/aaa.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 3)
        # push ITU.h/a.h/aa.h/aab.h
        self._figr.graph.addBranch(['ITU.h', 'a.h', 'aa.h'], 23, 'aab.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('aab.h')
        myTcs.counter().inc(PpToken.PpToken('aab.h', 'identifier'), True, 14)
        myTcs.counter().inc(PpToken.PpToken('aab.h', 'identifier'), False, 14)
        # push ITU.h/a.h/aa.h/aab.h/aaba.h
        self._figr.graph.addBranch(['ITU.h', 'a.h', 'aa.h', 'aab.h'], 117, 'aaba.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('aaba.h')
        myTcs.counter().inc(PpToken.PpToken('aaba.h', 'identifier'), True, 2)
        myTcs.counter().inc(PpToken.PpToken('aaba.h', 'identifier'), False, 5)
        # pop ITU.h/a.h/aa.h/aaa.h/aaba.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 4)
        # pop ITU.h/a.h/aa.h/aab.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 3)
        # pop ITU.h/a.h/aa.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # pop ITU.h/a.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 1)
        # push ITU.h/b.h
        self._figr.graph.addBranch(['ITU.h',], 115, 'b.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('b.h')
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), True, 8)
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), False, 8)
        # pop ITU.h/b.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 1)
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), True, 70)
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), False, 70)
        # pop ITU.h
        self._figr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 0)
        myTcs.close()
        expTree = """ITU.h [140, 70]:  True "" "ITU"
000015: #include a.h
  a.h [2, 1]:  True "" "CP=."
  000017: #include aa.h
    aa.h [4, 2]:  True "" "CP=."
    000019: #include aaa.h
      aaa.h [8, 4]:  True "" "CP=."
      000020: #include aaaa.h
        aaaa.h [80, 42]:  True "" "CP=."
      000021: #include aaab.h
        aaab.h [81, 43]:  True "" "CP=."
    000023: #include aab.h
      aab.h [28, 14]:  True "" "CP=."
      000117: #include aaba.h
        aaba.h [7, 2]:  True "" "CP=."
000115: #include b.h
  b.h [16, 8]:  True "" "CP=.\""""
        #print
        #print expTree
        #print
        #print self._figr
        self.assertEqual(expTree, str(self._figr))

class TestFileIncludeGraphRootVisitor(TestFileIncludeGraphRootVisitorBase):
    """Tests the class FileIncludeGraphRoot and simulates virtual roots."""
    def test_00(self):
        """TestFileIncludeGraphRootVisitor: Two pre-includes and a graph."""
        self.setUpTwoPreIncludesAndAGraph()
        myVis = FileIncludeGraph.FigVisitorTree(MyVisitorTreeNode)
        self._figr.acceptVisitor(myVis)
        myTree = myVis.tree()
        self.assertEquals(486, myTree._t)

    def test_01(self):
        """TestFileIncludeGraphRootVisitor: No pre-includes and a graph."""
        self.setUpNoPreIncludesAndAGraph()
        myVis = FileIncludeGraph.FigVisitorTree(MyVisitorTreeNode)
        self._figr.acceptVisitor(myVis)
        myTree = myVis.tree()
        self.assertEquals(366, myTree._t)

    def test_02(self):
        """TestFileIncludeGraphRootVisitor: Creates a tree of VisitorTreeNode(s) - simulates PpLexer."""
        myFigr = FileIncludeGraph.FileIncludeGraphRoot()
        myTcs = PpTokenCount.PpTokenCountStack()
        myFs = []
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('PreInclude_00', True, 'a >= b+2', 'Forced PreInclude_00'))
        # push PreInclude_00
        myTcs.push()
        myFs.append('PreInclude_00')
        myTcs.counter().inc(PpToken.PpToken('PreInclude_00', 'identifier'), True, 50)
        myTcs.counter().inc(PpToken.PpToken('PreInclude_00', 'identifier'), False, 50)
        # pop PreInclude_00
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('PreInclude_01', True, 'x > 1', 'Forced PreInclude_01'))
        # push PreInclude_01
        myTcs.push()
        myFs.append('PreInclude_01')
        myTcs.counter().inc(PpToken.PpToken('PreInclude_01', 'identifier'), True, 60)
        myTcs.counter().inc(PpToken.PpToken('PreInclude_01', 'identifier'), False, 60)
        # pop PreInclude_00
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('ITU.h', True, '', ''))
        # push ITU.h
        myTcs.push()
        myFs.append('ITU.h')
        self.assertEqual(3, myFigr.numTrees())
        myFigr.graph.addBranch(['ITU.h',], 15, 'a.h', True, '', 'CP=.')
        # push for ITU.h/a.h
        myTcs.push()
        myFs.append('a.h')
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), True, 1)
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), False, 1)
        myFigr.graph.addBranch(['ITU.h', 'a.h'], 17, 'aa.h', True, '', 'CP=.')
        # push for ITU.h/a.h/aa.h
        myTcs.push()
        myFs.append('aa.h')
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), True, 2)
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), False, 2)
        myFigr.graph.addBranch(['ITU.h', 'a.h', 'aa.h'], 19, 'aaa.h', True, '', 'CP=.')
        # push for ITU.h/a.h/aa.h/aaa.h
        myTcs.push()
        myFs.append('aaa.h')
        myTcs.counter().inc(PpToken.PpToken('aaa.h', 'identifier'), True, 4)
        myTcs.counter().inc(PpToken.PpToken('aaa.h', 'identifier'), False, 4)
        myFigr.graph.addBranch(['ITU.h', 'a.h', 'aa.h', 'aaa.h'], 20, 'aaaa.h', True, '', 'CP=.')
        # push for ITU.h/a.h/aa.h/aaa.h/aaaa.h
        myTcs.push()
        myFs.append('aaaa.h')
        myTcs.counter().inc(PpToken.PpToken('aaaa.h', 'identifier'), True, 42)
        myTcs.counter().inc(PpToken.PpToken('aaaa.h', 'identifier'), False, 38)
        # pop ITU.h/a.h/aa.h/aaa.h/aaaa.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        myFigr.graph.addBranch(['ITU.h', 'a.h', 'aa.h', 'aaa.h'], 21, 'aaab.h', True, '', 'CP=.')
        # push for ITU.h/a.h/aa.h/aaa.h/aaab.h
        myTcs.push()
        myFs.append('aaab.h')
        myTcs.counter().inc(PpToken.PpToken('aaab.h', 'identifier'), True, 43)
        myTcs.counter().inc(PpToken.PpToken('aaab.h', 'identifier'), False, 38)
        # pop ITU.h/a.h/aa.h/aaa.h/aaab.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        # pop ITU.h/a.h/aa.h/aaa.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        myFigr.graph.addBranch(['ITU.h', 'a.h', 'aa.h'], 23, 'aab.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('aab.h')
        myTcs.counter().inc(PpToken.PpToken('aab.h', 'identifier'), True, 14)
        myTcs.counter().inc(PpToken.PpToken('aab.h', 'identifier'), False, 14)
        myFigr.graph.addBranch(['ITU.h', 'a.h', 'aa.h', 'aab.h'], 117, 'aaba.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('aaba.h')
        myTcs.counter().inc(PpToken.PpToken('aaba.h', 'identifier'), True, 2)
        myTcs.counter().inc(PpToken.PpToken('aaba.h', 'identifier'), False, 5)
        # pop() aaba.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        # pop() aab.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        # pop() aa.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        # pop() a.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        myFigr.graph.addBranch(['ITU.h',], 115, 'b.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('b.h')
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), True, 8)
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), False, 8)
        # pop() b.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), True, 70)
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), False, 70)
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myTcs.close()
        myFs.pop()
        self.assertEqual(len(myFs), 0)
        myExpFigr = """PreInclude_00 [100, 50]:  True "a >= b+2" "Forced PreInclude_00"
PreInclude_01 [120, 60]:  True "x > 1" "Forced PreInclude_01"
ITU.h [140, 70]:  True "" ""
000015: #include a.h
  a.h [2, 1]:  True "" "CP=."
  000017: #include aa.h
    aa.h [4, 2]:  True "" "CP=."
    000019: #include aaa.h
      aaa.h [8, 4]:  True "" "CP=."
      000020: #include aaaa.h
        aaaa.h [80, 42]:  True "" "CP=."
      000021: #include aaab.h
        aaab.h [81, 43]:  True "" "CP=."
    000023: #include aab.h
      aab.h [28, 14]:  True "" "CP=."
      000117: #include aaba.h
        aaba.h [7, 2]:  True "" "CP=."
000115: #include b.h
  b.h [16, 8]:  True "" "CP=.\""""
        #print
        #print myFigr
        #print
        #print myExpFigr
        self.assertEqual(myExpFigr, str(myFigr))
        #print
        #myVis = FincgVisitorTree()
        myVis = FileIncludeGraph.FigVisitorTree(MyVisitorTreeNode)
        myFigr.acceptVisitor(myVis)
        #self.assertEquals(366, myVis._t)
        #self.assertEquals(186, myVis._ts)
        myExpTree = """-001 None
  -001 PreInclude_00
  -001 PreInclude_01
  -001 ITU.h
    0015 a.h
      0017 aa.h
        0019 aaa.h
          0020 aaaa.h
          0021 aaab.h
        0023 aab.h
          0117 aaba.h
    0115 b.h
"""
        #print 'myExpTree'
        #print myExpTree
        myActTree = myVis.tree()
        #print 'myActTree'
        #print myActTree
        self.assertEquals(myExpTree, str(myActTree))

    def test_03(self):
        """TestFileIncludeGraphRootVisitor: Creates a tree of VisitorTreeNode(s) - simulates PpLexer and checks token counters."""
        myFigr = FileIncludeGraph.FileIncludeGraphRoot()
        myTcs = PpTokenCount.PpTokenCountStack()
        myFs = []
        myFigr.addGraph(
            FileIncludeGraph.FileIncludeGraph(
                'PreInclude_00',
                True,
                'a >= b+2',
                'Forced PreInclude_00',
            )
        )
        # push PreInclude_00
        myTcs.push()
        myFs.append('PreInclude_00')
        myTcs.counter().inc(PpToken.PpToken('PreInclude_00', 'identifier'), True, 50)
        myTcs.counter().inc(PpToken.PpToken('PreInclude_00', 'identifier'), False, 50)
        # pop PreInclude_00
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        # Verify token counter
        self.assertEqual(100, myFigr.graph.retLatestNode(myFs).numTokens)
        self.assertEqual(50, myFigr.graph.retLatestNode(myFs).numTokensSig)
        self.assertEqual(100, myFigr.graph.retLatestNode(myFs).numTokensIncChildren)
        self.assertEqual(50, myFigr.graph.retLatestNode(myFs).numTokensSigIncChildren)
        #
        myFs.pop()
        myFigr.addGraph(
            FileIncludeGraph.FileIncludeGraph(
                'PreInclude_01',
                True,
                'x > 1',
                'Forced PreInclude_01',
            )
        )
        # push PreInclude_01
        myTcs.push()
        myFs.append('PreInclude_01')
        myTcs.counter().inc(PpToken.PpToken('PreInclude_01', 'identifier'), True, 60)
        myTcs.counter().inc(PpToken.PpToken('PreInclude_01', 'identifier'), False, 60)
        # pop PreInclude_00
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        # Verify token counter
        self.assertEqual(120, myFigr.graph.retLatestNode(myFs).numTokens)
        self.assertEqual(60, myFigr.graph.retLatestNode(myFs).numTokensSig)
        self.assertEqual(120, myFigr.graph.retLatestNode(myFs).numTokensIncChildren)
        self.assertEqual(60, myFigr.graph.retLatestNode(myFs).numTokensSigIncChildren)
        #
        myFs.pop()
        myFigr.addGraph(
            FileIncludeGraph.FileIncludeGraph(
                'ITU.h',
                True,
                '',
                'ITU',
            )
        )
        # push ITU.h
        myTcs.push()
        myFs.append('ITU.h')
        self.assertEqual(3, myFigr.numTrees())
        myFigr.graph.addBranch(['ITU.h',], 15, 'a.h', True, '', '"a.h", CP=')
        # push for ITU.h/a.h
        myTcs.push()
        myFs.append('a.h')
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), True, 1)
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), False, 1)
        myFigr.graph.addBranch(['ITU.h', 'a.h'], 17, 'aa.h', True, '', '"aa.h", CP=.')
        # push for ITU.h/a.h/aa.h
        myTcs.push()
        myFs.append('aa.h')
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), True, 2)
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), False, 2)
        myFigr.graph.addBranch(['ITU.h', 'a.h', 'aa.h'], 19, 'aaa.h', True, '', '"aaa.h", CP=.')
        # push for ITU.h/a.h/aa.h/aaa.h
        myTcs.push()
        myFs.append('aaa.h')
        myTcs.counter().inc(PpToken.PpToken('aaa.h', 'identifier'), True, 4)
        myTcs.counter().inc(PpToken.PpToken('aaa.h', 'identifier'), False, 4)
        myFigr.graph.addBranch(['ITU.h', 'a.h', 'aa.h', 'aaa.h'], 20, 'aaaa.h', True, '', '"aaaa.h", CP=.')
        # push for ITU.h/a.h/aa.h/aaa.h/aaaa.h
        myTcs.push()
        myFs.append('aaaa.h')
        myTcs.counter().inc(PpToken.PpToken('aaaa.h', 'identifier'), True, 42)
        myTcs.counter().inc(PpToken.PpToken('aaaa.h', 'identifier'), False, 38)
        # pop ITU.h/a.h/aa.h/aaa.h/aaaa.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        # Verify token counter
        self.assertEqual(80, myFigr.graph.retLatestNode(myFs).numTokens)
        self.assertEqual(42, myFigr.graph.retLatestNode(myFs).numTokensSig)
        self.assertEqual(80, myFigr.graph.retLatestNode(myFs).numTokensIncChildren)
        self.assertEqual(42, myFigr.graph.retLatestNode(myFs).numTokensSigIncChildren)
        #
        myFs.pop()
        myFigr.graph.addBranch(['ITU.h', 'a.h', 'aa.h', 'aaa.h'], 21, 'aaab.h', True, '', '"aaab.h", CP=.')
        # push for ITU.h/a.h/aa.h/aaa.h/aaab.h
        myTcs.push()
        myFs.append('aaab.h')
        myTcs.counter().inc(PpToken.PpToken('aaab.h', 'identifier'), True, 43)
        myTcs.counter().inc(PpToken.PpToken('aaab.h', 'identifier'), False, 38)
        # pop ITU.h/a.h/aa.h/aaa.h/aaab.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        # Verify token counter
        self.assertEqual(81, myFigr.graph.retLatestNode(myFs).numTokens)
        self.assertEqual(43, myFigr.graph.retLatestNode(myFs).numTokensSig)
        self.assertEqual(81, myFigr.graph.retLatestNode(myFs).numTokensIncChildren)
        self.assertEqual(43, myFigr.graph.retLatestNode(myFs).numTokensSigIncChildren)
        #
        myFs.pop()
        # pop ITU.h/a.h/aa.h/aaa.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        # Verify token counter
        self.assertEqual(8, myFigr.graph.retLatestNode(myFs).numTokens)
        self.assertEqual(4, myFigr.graph.retLatestNode(myFs).numTokensSig)
        self.assertEqual(169, myFigr.graph.retLatestNode(myFs).numTokensIncChildren)
        self.assertEqual(89, myFigr.graph.retLatestNode(myFs).numTokensSigIncChildren)
        #
        myFs.pop()
        myFigr.graph.addBranch(['ITU.h', 'a.h', 'aa.h'], 23, 'aab.h', True, '', '"aab.h", CP=.')
        myTcs.push()
        myFs.append('aab.h')
        myTcs.counter().inc(PpToken.PpToken('aab.h', 'identifier'), True, 14)
        myTcs.counter().inc(PpToken.PpToken('aab.h', 'identifier'), False, 14)
        myFigr.graph.addBranch(['ITU.h', 'a.h', 'aa.h', 'aab.h'], 117, 'aaba.h', True, '', '"aaba.h", CP=.')
        myTcs.push()
        myFs.append('aaba.h')
        myTcs.counter().inc(PpToken.PpToken('aaba.h', 'identifier'), True, 2)
        myTcs.counter().inc(PpToken.PpToken('aaba.h', 'identifier'), False, 5)
        # pop() aaba.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        # Verify token counter
        self.assertEqual(7, myFigr.graph.retLatestNode(myFs).numTokens)
        self.assertEqual(2, myFigr.graph.retLatestNode(myFs).numTokensSig)
        self.assertEqual(7, myFigr.graph.retLatestNode(myFs).numTokensIncChildren)
        self.assertEqual(2, myFigr.graph.retLatestNode(myFs).numTokensSigIncChildren)
        #
        myFs.pop()
        # pop() aab.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        # Verify token counter
        self.assertEqual(28, myFigr.graph.retLatestNode(myFs).numTokens)
        self.assertEqual(14, myFigr.graph.retLatestNode(myFs).numTokensSig)
        self.assertEqual(35, myFigr.graph.retLatestNode(myFs).numTokensIncChildren)
        self.assertEqual(16, myFigr.graph.retLatestNode(myFs).numTokensSigIncChildren)
        #
        myFs.pop()
        # pop() aa.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        # Verify token counter
        self.assertEqual(4, myFigr.graph.retLatestNode(myFs).numTokens)
        self.assertEqual(2, myFigr.graph.retLatestNode(myFs).numTokensSig)
        self.assertEqual(208, myFigr.graph.retLatestNode(myFs).numTokensIncChildren)
        self.assertEqual(107, myFigr.graph.retLatestNode(myFs).numTokensSigIncChildren)
        #
        myFs.pop()
        # pop() a.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        # Verify token counter
        self.assertEqual(2, myFigr.graph.retLatestNode(myFs).numTokens)
        self.assertEqual(1, myFigr.graph.retLatestNode(myFs).numTokensSig)
        self.assertEqual(210, myFigr.graph.retLatestNode(myFs).numTokensIncChildren)
        self.assertEqual(108, myFigr.graph.retLatestNode(myFs).numTokensSigIncChildren)
        #
        myFs.pop()
        myFigr.graph.addBranch(['ITU.h',], 115, 'b.h', True, '', '"b.h", CP=.')
        myTcs.push()
        myFs.append('b.h')
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), True, 8)
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), False, 8)
        # pop() b.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        # Verify token counter
        self.assertEqual(16, myFigr.graph.retLatestNode(myFs).numTokens)
        self.assertEqual(8, myFigr.graph.retLatestNode(myFs).numTokensSig)
        self.assertEqual(16, myFigr.graph.retLatestNode(myFs).numTokensIncChildren)
        self.assertEqual(8, myFigr.graph.retLatestNode(myFs).numTokensSigIncChildren)
        #
        myFs.pop()
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), True, 70)
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), False, 70)
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        # Verify token counter
        self.assertEqual(140, myFigr.graph.retLatestNode(myFs).numTokens)
        self.assertEqual(70, myFigr.graph.retLatestNode(myFs).numTokensSig)
        self.assertEqual(366, myFigr.graph.retLatestNode(myFs).numTokensIncChildren)
        self.assertEqual(186, myFigr.graph.retLatestNode(myFs).numTokensSigIncChildren)
        #
        myTcs.close()
        myFs.pop()
        self.assertEqual(len(myFs), 0)
        myExpFigr = """PreInclude_00 [100, 50]:  True "a >= b+2" "Forced PreInclude_00"
PreInclude_01 [120, 60]:  True "x > 1" "Forced PreInclude_01"
ITU.h [140, 70]:  True "" "ITU"
000015: #include a.h
  a.h [2, 1]:  True "" ""a.h", CP="
  000017: #include aa.h
    aa.h [4, 2]:  True "" ""aa.h", CP=."
    000019: #include aaa.h
      aaa.h [8, 4]:  True "" ""aaa.h", CP=."
      000020: #include aaaa.h
        aaaa.h [80, 42]:  True "" ""aaaa.h", CP=."
      000021: #include aaab.h
        aaab.h [81, 43]:  True "" ""aaab.h", CP=."
    000023: #include aab.h
      aab.h [28, 14]:  True "" ""aab.h", CP=."
      000117: #include aaba.h
        aaba.h [7, 2]:  True "" ""aaba.h", CP=."
000115: #include b.h
  b.h [16, 8]:  True "" ""b.h", CP=.\""""
        #print
        #print myFigr
        #print
        #print myExpFigr
        self.assertEqual(myExpFigr, str(myFigr))
        #print
        #myVis = FincgVisitorTree()
        myVis = FileIncludeGraph.FigVisitorTree(MyVisitorTreeNode)
        myFigr.acceptVisitor(myVis)
        myVisTree = myVis.tree()
        self.assertEquals(586, myVisTree._t)
        #self.assertEquals(186, myVis._ts)
        #print
        #print 'myVis.tree()'
        #print myVis.tree()
        myExpTree = """-001 None
  -001 PreInclude_00
  -001 PreInclude_01
  -001 ITU.h
    0015 a.h
      0017 aa.h
        0019 aaa.h
          0020 aaaa.h
          0021 aaab.h
        0023 aab.h
          0117 aaba.h
    0115 b.h
"""
        #print 'myExpTree'
        #print myExpTree
        #print 'myVisTree'
        #print myVisTree
        self.assertEquals(myExpTree, str(myVisTree))

class TestFileIncludeGraphRootVisitorFileSet(TestFileIncludeGraphRootVisitorBase):
    """Tests the visitor class that gathers file names."""
    def test_00(self):
        """Test FigVisitorFileSet: Two pre-includes and a graph."""
        self.setUpTwoPreIncludesAndAGraph()
        myVis = FileIncludeGraph.FigVisitorFileSet()
        self._figr.acceptVisitor(myVis)
        myList = list(myVis.fileNameSet)
        myList.sort()
        #print
        #print myList
        self.assertEqual(
            myList,
            ['ITU.h', 'PreInclude_00', 'PreInclude_01', 'a.h', 'aa.h', 'ab.h', 'b.h', 'ba.h', 'bb.h']
        )
        #print
        #print myVis.fileNameMap
        self.assertEqual(
                myVis.fileNameMap,
                {
                    'bb.h'          : 1,
                    'ab.h'          : 1,
                    'a.h'           : 1,
                    'b.h'           : 1,
                    'aa.h'          : 1,
                    'PreInclude_01' : 1,
                    'PreInclude_00' : 1,
                    'ba.h'          : 1,
                    'ITU.h'         : 1,
                },
        )

    def test_01(self):
        """Test FigVisitorFileSet: No pre-includes and a graph."""
        self.setUpNoPreIncludesAndAGraph()
        myVis = FileIncludeGraph.FigVisitorFileSet()
        self._figr.acceptVisitor(myVis)
        myList = list(myVis.fileNameSet)
        myList.sort()
        #print
        #print myList
        self.assertEqual(
            myList,
            ['ITU.h', 'a.h', 'aa.h', 'aaa.h', 'aaaa.h', 'aaab.h', 'aab.h', 'aaba.h', 'b.h'],
        )
        #print
        #print myVis.fileNameMap
        self.assertEqual(
                myVis.fileNameMap,
                {
                    'aab.h':    1,
                    'a.h':      1,
                    'aaab.h':   1,
                    'b.h':      1,
                    'aa.h':     1,
                    'aaba.h':   1,
                    'aaaa.h':   1,
                    'aaa.h':    1,
                    'ITU.h':    1,
                }
        )

#===============================================================================
# class TestFileIncludeGraphRootVisitorDot(TestFileIncludeGraphRootVisitorBase):
#    """Tests the visitor class that gathers file names."""
#    def test_00(self):
#        """Test TestFileIncludeGraphRootVisitorDot: Two pre-includes and a graph."""
#        self.setUpTwoPreIncludesAndAGraph()
#        myVis = FileIncludeGraph.FigVisitorDot()
#        self._figr.acceptVisitor(myVis)
#        #print
#        #print myVis
#        self.assertEqual(str(myVis), """digraph FigVisitorDot {
# "PreInclude_00" -> "PreInclude_01" -> "ITU.h";
# "PreInclude_00";
# "PreInclude_01";
# "ITU.h" -> "a.h";
# "ITU.h" -> "b.h";
# "a.h" -> "aa.h";
# "a.h" -> "ab.h";
# "aa.h";
# "ab.h";
# "b.h" -> "ba.h";
# "b.h" -> "bb.h";
# "ba.h";
# "bb.h";
# }
# """)
# 
#    def test_01(self):
#        """Test TestFileIncludeGraphRootVisitorDot: No pre-includes and a graph."""
#        self.setUpNoPreIncludesAndAGraph()
#        myVis = FileIncludeGraph.FigVisitorDot()
#        self._figr.acceptVisitor(myVis)
#        #print
#        #print myVis
#        self.assertEqual(str(myVis), """digraph FigVisitorDot {
# "ITU.h" -> "a.h";
# "ITU.h" -> "b.h";
# "a.h" -> "aa.h";
# "aa.h" -> "aaa.h";
# "aa.h" -> "aab.h";
# "aaa.h" -> "aaaa.h";
# "aaa.h" -> "aaab.h";
# "aaaa.h";
# "aaab.h";
# "aab.h" -> "aaba.h";
# "aaba.h";
# "b.h";
# }
# """)
#===============================================================================

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFileIncludeGraph)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileIncludeGraphPlot))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileIncludeGetBranchLeaf))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileIncludeGraphAttributeSetGet))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileIncludeGraphDummyRoot))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileIncludeGraphRoot))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileIncludeGraphRootVisitor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileIncludeGraphRootVisitorFileSet))
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileIncludeGraphRootVisitorDot))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestFileIncludeGraph.py - A module that tests FileIncludeGraph module.
Usage:
python TestFileIncludeGraph.py [-lh --help]

Options:
-h, --help  Help (this screen) and exit

Options (debug):
-l:         Set the logging level higher is quieter.
             Default is 20 (INFO) e.g.:
                CRITICAL    50
                ERROR       40
                WARNING     30
                INFO        20
                DEBUG       10
                NOTSET      0
""")

def main():
    """Invoke unit test code."""
    print('TestFileIncludeGraph.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
    print(__rights__)
    print()
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError:
        usage()
        print('ERROR: Invalid options!')
        sys.exit(1)
    logLevel = logging.INFO
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o == '-l':
            logLevel = int(a)
    if len(args) != 0:
        usage()
        print('ERROR: Wrong number of arguments!')
        sys.exit(1)
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    clkStart = time.clock()
    unitTest()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
