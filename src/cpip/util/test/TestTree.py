#!/usr/bin/env python
# CPIP is a C/C++ Preprocessor implemented in Python.
# Copyright (C) 2008-2014 Paul Ross
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

"""Tests Tree.
"""

__author__  = 'Paul Ross'
__date__    = '2014-03-06'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import os
import sys
import time
import logging
import pprint

from cpip.util import Tree
from cpip.util import DictTree

######################
# Section: Unit tests.
######################
import unittest

class TestTreeCtor(unittest.TestCase):
    """Tests Tree consturctor."""
    def test_00(self):
        """TestTreeCtor: test_00(): constructor."""
        t = Tree.Tree('A')
        self.assertEquals('A', t.obj)
        self.assertEquals(0, len(t))
                
    def test_01(self):
        """TestTreeCtor: test_01(): constructor fails."""
        self.assertRaises(TypeError, Tree.Tree)
                    
    def test_02(self):
        """TestTreeCtor: test_00(): simple object has len == 0."""
        t = Tree.Tree('A')
        self.assertEquals(0, len(t))
                
class TestTreeAddChild(unittest.TestCase):
    """Tests Tree addChild() function."""
            
    def test_00(self):
        """TestTreeAdd: simple add."""
        t = Tree.Tree('A')
        t.addChild('B')
        self.assertEquals(1, len(t))
        t.addChild('B')
        self.assertEquals(2, len(t))
        t.addChild('C')
        self.assertEquals(3, len(t))

    def test_01(self):
        """TestTreeAdd: simple add and check .obj."""
        t = Tree.Tree('A')
        t.addChild('B')
        t.addChild('B')
        t.addChild('C')
        self.assertEqual(['B', 'B', 'C'], [v.obj for v in t.children])

    def test_02(self):
        """TestTreeCtor: test_02(): youngestChild raises when no children."""
        t = Tree.Tree('A')
        try:
            t.youngestChild
            self.fail('IndexError not raised.')
        except IndexError:
            pass
                    
class TestTreeBranches(unittest.TestCase):
    """Tests Tree branches() function."""
            
    def test_00(self):
        """TestTreeAdd: simple add."""
        t = Tree.Tree('A')
        t.addChild('AA')
        t.youngestChild.addChild('AAA')
        t.addChild('AB')
        t.youngestChild.addChild('ABA')
#         print(t.branches())
        self.assertEquals(
            [['A'], ['A', 'AA'], ['A', 'AA', 'AAA'], ['A', 'AB'], ['A', 'AB', 'ABA']],
            t.branches()
        )

    def test_01(self):
        """TestTreeAdd: simple add and convert to a Dict Tree."""
        t = Tree.Tree('A')
        t.addChild('AA')
        t.youngestChild.addChild('AAA')
        t.addChild('AB')
        t.youngestChild.addChild('ABA')
#         print(t.branches())
        self.assertEquals(
            [['A'], ['A', 'AA'], ['A', 'AA', 'AAA'], ['A', 'AB'], ['A', 'AB', 'ABA']],
            t.branches()
        )
        dt = DictTree.DictTree('list')
        for branch in t.branches():
            dt.add(branch, None)
#         print(dt.indentedStr())
        self.assertEqual("""A
  [None]
  AA
    [None]
    AAA
      [None]
  AB
    [None]
    ABA
      [None]""", dt.indentedStr())

class TestDuplexAdjacencyList(unittest.TestCase):
    """Tests DuplexAdjacencyList."""
            
    def test_00(self):
        """TestDuplexAdjacencyList: ctor, empty list."""
        t = Tree.DuplexAdjacencyList()
        self.assertRaises(KeyError, t.children, '')
        self.assertRaises(KeyError, t.parents, '')
        self.assertEqual([], list(t.allParents))
        self.assertEqual([], list(t.allChildren))

    def test_01(self):
        """TestDuplexAdjacencyList: single add."""
        t = Tree.DuplexAdjacencyList()
        t.add('parent', 'child')
        self.assertEqual(['child',], t.children('parent'))
        self.assertEqual(['parent',], t.parents('child'))
        self.assertEqual(['parent'], list(t.allParents))
        self.assertEqual(['child'], list(t.allChildren))

    def test_02(self):
        """TestDuplexAdjacencyList: single parent, two children."""
        t = Tree.DuplexAdjacencyList()
        t.add('parent', 'child_00')
        t.add('parent', 'child_01')
        self.assertEqual(['child_00', 'child_01',], t.children('parent'))
        self.assertEqual(['parent',], t.parents('child_00'))
        self.assertEqual(['parent',], t.parents('child_01'))
        self.assertEqual(['parent'], list(t.allParents))
        self.assertEqual(['child_00', 'child_01'], sorted(t.allChildren))
#         print(t.treeParentChild('parent').branches())
        self.assertEqual(
            [
                ['parent'],
                ['parent', 'child_00'],
                ['parent', 'child_01'],
            ],
            t.treeParentChild('parent').branches(),
        )

    def test_03(self):
        """TestDuplexAdjacencyList: simple cycle."""
        t = Tree.DuplexAdjacencyList()
        t.add('A', 'A')
        self.assertEqual(['A',], t.children('A'))
        self.assertEqual(['A',], t.parents('A'))
#         print(t.treeParentChild('A').branches())
        self.assertEqual(
            [
                ['A'],
            ],
            t.treeParentChild('A').branches(),
        )

    def test_04(self):
        """TestDuplexAdjacencyList: cycle A -> B -> A."""
        t = Tree.DuplexAdjacencyList()
        t.add('A', 'B')
        t.add('B', 'A')
        self.assertEqual(['B',], t.children('A'))
        self.assertEqual(['A',], t.parents('B'))
#         print(t.treeParentChild('A').branches())
        self.assertEqual(
            [
                ['A',],
                ['A', 'B',],
            ],
            t.treeParentChild('A').branches(),
        )
        self.assertEqual(
            [
                ['B',],
                ['B', 'A',],
            ],
            t.treeParentChild('B').branches(),
        )

    def test_05(self):
        """TestDuplexAdjacencyList: cycle A -> B -> C -> A."""
        t = Tree.DuplexAdjacencyList()
        t.add('A', 'B')
        t.add('B', 'C')
        t.add('C', 'A')
        self.assertEqual(['B',], t.children('A'))
        self.assertEqual(['C',], t.children('B'))
        self.assertEqual(['A',], t.children('C'))
        self.assertEqual(['C',], t.parents('A'))
        self.assertEqual(['A',], t.parents('B'))
        self.assertEqual(['B',], t.parents('C'))
#         print(t.treeParentChild('A').branches())
        self.assertEqual(
            [
                ['A',],
                ['A', 'B',],
                ['A', 'B', 'C',],
            ],
            t.treeParentChild('A').branches(),
        )
        self.assertEqual(
            [
                ['B',],
                ['B', 'C',],
                ['B', 'C', 'A',],
            ],
            t.treeParentChild('B').branches(),
        )
        self.assertEqual(
            [
                ['C',],
                ['C', 'A',],
                ['C', 'A', 'B',],
            ],
            t.treeParentChild('C').branches(),
        )

    def test_06(self):
        """TestDuplexAdjacencyList: test hasParent(), hasChildren()."""
        t = Tree.DuplexAdjacencyList()
        t.add('parent', 'child_00')
        t.add('parent', 'child_01')
        self.assertTrue(t.hasParent('parent'))
        self.assertTrue(t.hasChild('child_00'))
        self.assertTrue(t.hasChild('child_01'))
        self.assertFalse(t.hasParent('foo'))
        self.assertFalse(t.hasChild('bar'))
        
    def test_10(self):
        """TestDuplexAdjacencyList: Tree with no cycles."""
        t = Tree.DuplexAdjacencyList()
        t.add('A', 'AA')
        t.add('A', 'AB')
        t.add('AA', 'AAA')
        t.add('AA', 'AAB')
        t.add('AB', 'ABA')
        t.add('AB', 'ABB')
#         pprint.pprint(t.treeParentChild('A').branches())
        self.assertEqual(
            [
                ['A'],
                ['A', 'AA'],
                ['A', 'AA', 'AAA'],
                ['A', 'AA', 'AAB'],
                ['A', 'AB'],
                ['A', 'AB', 'ABA'],
                ['A', 'AB', 'ABB'],
            ],
            t.treeParentChild('A').branches(),
        )

    def test_20(self):
        """TestDuplexAdjacencyList: __str__ on a Tree."""
        t = Tree.DuplexAdjacencyList()
        t.add('A', 'AA')
        t.add('A', 'AB')
        t.add('AA', 'AAA')
        t.add('AA', 'AAB')
        t.add('AB', 'ABA')
        t.add('AB', 'ABB')
#         print(str(t))
#         self.assertEqual(
#             """"Parent -> Children:
# A -> ['AA', 'AB']
# AA -> ['AAA', 'AAB']
# AB -> ['ABA', 'ABB']""",
#             str(t),
#         )

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTreeCtor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTreeAddChild))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTreeBranches))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDuplexAdjacencyList))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestTree.py - A module that tests Tree module.
Usage:
python TestTree.py [-lh --help]

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
    print('TestTree.py script version "%s", dated %s' % (__version__, __date__))
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
