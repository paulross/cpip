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

"""Tests DictTree.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import os
import sys
import time
import logging
import pprint

from cpip.util import DictTree

######################
# Section: Unit tests.
######################
import unittest

class TestDictTreeCtor(unittest.TestCase):
    """Tests DictTree consturctor."""
    def test_00(self):
        """TestDictTreeCtor: test_00(): constructor."""
        DictTree.DictTree()
        self.assertTrue(True)
                
    def test_01(self):
        """TestDictTreeCtor: test_01(): constructor fails."""
        try:
            DictTree.DictTree(valIterable='int')
            self.fail('DictTree.ExceptionDictTree not raised.')
        except DictTree.ExceptionDictTree:
            pass
                
    def test_02(self):
        """TestDictTreeCtor: test_02(): constructor OK, change valIterable and fail."""
        myDt = DictTree.DictTree()
        myDt._vI = 'int'
        try:
            myDt.add(list(range(1)), 'one')
            self.fail('DictTree.ExceptionDictTree not raised.')
        except DictTree.ExceptionDictTree as err:
            pass
                
class TestDictTreeAdd(unittest.TestCase):
    """Tests DictTree add() function."""
    def setUp(self):
        self._dt = DictTree.DictTree()
        self.assertEqual([], list(self._dt.keys()))
        self.assertEqual([], list(self._dt.values()))
        self.assertEqual(0, len(self._dt))
        self.assertNotEqual(True, 'spam' in self._dt)
        self.assertEqual(0, self._dt.depth())
        
    def tearDown(self):
        pass
    
    def test_00(self):
        """TestDictTreeAdd: test setUp() and tearDown()."""
        self.assertTrue(True)

    def test_01(self):
        """TestDictTreeAdd: test_00(): simple add."""
        self._dt.add(list(range(4)), 'four')
        self.assertEqual([list(range(4)),], list(self._dt.keys()))
        self.assertEqual(['four',], list(self._dt.values()))
        self.assertEqual(1, len(self._dt))
        self.assertNotEqual(True, 'spam' in self._dt)
        self.assertEqual(True, list(range(4)) in self._dt)
        self.assertEqual('four', self._dt.value(list(range(4))))
        self.assertEqual(4, self._dt.depth())
                
    def test_02(self):
        """TestDictTreeAdd: test_02(): add and stringise."""
        self._dt.add(list(range(2)), 'one')
        self.assertEqual(2, self._dt.depth())
        self._dt.add(list(range(4)), 'three')
        self.assertEqual(4, self._dt.depth())
        self._dt.add(list(range(6)), 'five')
        self.assertEqual(6, self._dt.depth())
        self.assertEqual([list(range(2)),list(range(4)),list(range(6)),], list(self._dt.keys()))
        self.assertEqual(['one','three','five',], list(self._dt.values()))
        self.assertEqual(3, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""0
  1
    one
    2
      3
        three
        4
          5
            five""", self._dt.indentedStr())

    def test_03(self):
        """TestDictTreeAdd: test_00(): add, remove and stringise."""
        self._dt.add(list(range(2)), 'one')
        self._dt.add(list(range(4)), 'three')
        self._dt.add(list(range(6)), 'five')
        self.assertEqual([list(range(2)),list(range(4)),list(range(6)),], list(self._dt.keys()))
        self.assertEqual(['one','three','five',], list(self._dt.values()))
        self.assertEqual(3, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""0
  1
    one
    2
      3
        three
        4
          5
            five""", self._dt.indentedStr())
        self._dt.remove(list(range(4)))
        self.assertEqual([list(range(2)),list(range(6)),], list(self._dt.keys()))
        self.assertEqual(['one','five',], list(self._dt.values()))
        self.assertEqual(2, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""0
  1
    one
    2
      3
        4
          5
            five""", self._dt.indentedStr())

class TestDictTreeAddList(unittest.TestCase):
    """Tests DictTree [list] add() function."""
    def setUp(self):
        self._dt = DictTree.DictTree(valIterable='list')
        self.assertEqual([], list(self._dt.keys()))
        self.assertEqual([], list(self._dt.values()))
        self.assertEqual(0, len(self._dt))
        self.assertNotEqual(True, 'spam' in self._dt)
        self.assertEqual(0, self._dt.depth())
        
    def tearDown(self):
        pass
    
    def test_00(self):
        """TestDictTreeAddList: test_00(): add value as list and stringise."""
        self._dt.add(list(range(2)), 'one')
        self._dt.add(list(range(2)), 'One')
        self._dt.add(list(range(2)), 'ONE')
        self.assertEqual(2, self._dt.depth())
        self._dt.add(list(range(4)), 'three')
        self._dt.add(list(range(4)), 'Three')
        self._dt.add(list(range(4)), 'THREE')
        self.assertEqual(4, self._dt.depth())
        self._dt.add(list(range(6)), 'five')
        self._dt.add(list(range(6)), 'Five')
        self._dt.add(list(range(6)), 'FIVE')
        self.assertEqual(6, self._dt.depth())
        self.assertEqual([list(range(2)),list(range(4)),list(range(6)),], list(self._dt.keys()))
        self.assertEqual(
            [
                ['one', 'One', 'ONE'],
                ['three', 'Three', 'THREE'],
                ['five', 'Five', 'FIVE']
            ],
            list(self._dt.values()),
            )
        self.assertEqual(3, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""0
  1
    ['one', 'One', 'ONE']
    2
      3
        ['three', 'Three', 'THREE']
        4
          5
            ['five', 'Five', 'FIVE']""",
            self._dt.indentedStr())

    def test_01(self):
        """TestDictTreeAddList: test_01(): add value as list then remove it."""
        self._dt.add(list(range(2)), 'one')
        self.assertEqual(True, list(range(2)) in self._dt)
        # Try removing something not there
        try:
            self._dt.remove(list(range(2)), 'two')
            self.fail('DictTree.ExceptionDictTree not raised')
        except DictTree.ExceptionDictTree:
            pass
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""0
  1
    ['one']""",
            self._dt.indentedStr()
        )
        self._dt.remove(list(range(2)), 'one')
        self.assertEqual(True, list(range(2)) in self._dt)
        self.assertEqual([], self._dt.value(list(range(2))))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""0
  1
    []""",
            self._dt.indentedStr()
        )
        # Remove the key completely
        self._dt.remove(list(range(2)), None)
        self.assertNotEqual(True, list(range(2)) in self._dt)
        self.assertEqual(None, self._dt.value(list(range(2))))

    def test_02(self):
        """TestDictTreeAddList: test_02(): add value as list then try to remove something else."""
        self._dt.add(list(range(3)), 'three')
        self.assertEqual(True, list(range(3)) in self._dt)
        # Try removing something with a key overrun
        try:
            self._dt.remove(list(range(4)), 'four')
            self.fail('DictTree.ExceptionDictTree not raised')
        except DictTree.ExceptionDictTree:
            pass
        # Try removing something with a key mismatch
        try:
            self._dt.remove([1, 2, 3, 4], 'one to four')
            self.fail('DictTree.ExceptionDictTree not raised')
        except DictTree.ExceptionDictTree:
            pass
        # Try removing something with a key underrun
        try:
            self._dt.remove(list(range(2)), 'two')
            self.fail('DictTree.ExceptionDictTree not raised')
        except DictTree.ExceptionDictTree:
            pass

class TestDictTreeAddSet(unittest.TestCase):
    """Tests DictTree [set] add() function."""
    def setUp(self):
        self._dt = DictTree.DictTree(valIterable='set')
        self.assertEqual([], list(self._dt.keys()))
        self.assertEqual([], list(self._dt.values()))
        self.assertEqual(0, len(self._dt))
        self.assertNotEqual(True, 'spam' in self._dt)
        self.assertEqual(0, self._dt.depth())
        
    def tearDown(self):
        pass
    
    def test_00(self):
        """TestDictTreeAddSet: test_00(): add value as set and stringise."""
        self._dt.add(list(range(2)), 'one')
        self._dt.add(list(range(2)), 'One')
        self._dt.add(list(range(2)), 'ONE')
        self.assertEqual(2, self._dt.depth())
        self._dt.add(list(range(4)), 'three')
        self._dt.add(list(range(4)), 'Three')
        self._dt.add(list(range(4)), 'THREE')
        self.assertEqual(4, self._dt.depth())
        self._dt.add(list(range(6)), 'five')
        self._dt.add(list(range(6)), 'Five')
        self._dt.add(list(range(6)), 'FIVE')
        self.assertEqual(6, self._dt.depth())
        self.assertEqual([list(range(2)),list(range(4)),list(range(6)),], list(self._dt.keys()))
        self.assertEqual(
            [
                set(['one', 'One', 'ONE']),
                set(['three', 'Three', 'THREE']),
                set(['five', 'Five', 'FIVE']),
            ],
            list(self._dt.values()),
            )
        self.assertEqual(3, len(self._dt))
        self.assertEqual(6, self._dt.depth())
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""0
  1
    {'One', 'ONE', 'one'}
    2
      3
        {'THREE', 'three', 'Three'}
        4
          5
            {'Five', 'FIVE', 'five'}""",
            self._dt.indentedStr())
        # Try removal
        self._dt.remove(list(range(4)), 'THREE')
        # Try removal of something that is not there
        try:
            self._dt.remove(list(range(4)), 'TWENTY_TWO')
            self.fail('DictTree.ExceptionDictTree not raised')
        except DictTree.ExceptionDictTree:
            pass

    def test_01(self):
        """TestDictTreeAddSet: test_01(): add value as set then remove it."""
        self._dt.add(list(range(2)), 'one')
        self.assertEqual(True, list(range(2)) in self._dt)
        # Try removing something not there
        try:
            self._dt.remove(list(range(2)), 'two')
            self.fail('DictTree.ExceptionDictTree not raised')
        except DictTree.ExceptionDictTree:
            pass
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""0
  1
    {'one'}""",
            self._dt.indentedStr()
        )
        self._dt.remove(list(range(2)), 'one')
        self.assertEqual(True, list(range(2)) in self._dt)
        self.assertEqual(set([]), self._dt.value(list(range(2))))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""0
  1
    set()""",
            self._dt.indentedStr()
        )
        # Remove the key completely
        self._dt.remove(list(range(2)), None)
        self.assertNotEqual(True, list(range(2)) in self._dt)
        self.assertEqual(None, self._dt.value(list(range(2))))

    def test_02(self):
        """TestDictTreeAddList: test_02(): add value as set then try to remove something else."""
        self._dt.add(list(range(3)), 'three')
        self.assertEqual(True, list(range(3)) in self._dt)
        # Try removing something with a key overrun
        try:
            self._dt.remove(list(range(4)), 'four')
            self.fail('DictTree.ExceptionDictTree not raised')
        except DictTree.ExceptionDictTree:
            pass
        # Try removing something with a key mismatch
        try:
            self._dt.remove([1, 2, 3, 4], 'one to four')
            self.fail('DictTree.ExceptionDictTree not raised')
        except DictTree.ExceptionDictTree:
            pass
        # Try removing something with a key underrun
        try:
            self._dt.remove(list(range(2)), 'two')
            self.fail('DictTree.ExceptionDictTree not raised')
        except DictTree.ExceptionDictTree:
            pass

class TestDictTreeAddBespokeList(unittest.TestCase):
    """Tests DictTree add() function."""
    def setUp(self):
        self._dt = DictTree.DictTree()
        self.assertEqual([], list(self._dt.keys()))
        self.assertEqual([], list(self._dt.values()))
        self.assertEqual(0, len(self._dt))
        self.assertNotEqual(True, 'spam' in self._dt)
        
    def tearDown(self):
        pass
    
    def test_00(self):
        """TestDictTreeAdd: test_00(): add value with bespoke list and stringise."""
        def addKv(dt, k, v):
            if dt.value(k) is None:
                dt.add(k, [v,])
            else:
                dt.value(k).append(v)
        addKv(self._dt, list(range(2)), 'one')
        addKv(self._dt, list(range(2)), 'One')
        addKv(self._dt, list(range(2)), 'ONE')
        addKv(self._dt, list(range(4)), 'three')
        addKv(self._dt, list(range(4)), 'Three')
        addKv(self._dt, list(range(4)), 'THREE')
        addKv(self._dt, list(range(6)), 'five')
        addKv(self._dt, list(range(6)), 'Five')
        addKv(self._dt, list(range(6)), 'FIVE')
        self.assertEqual([list(range(2)),list(range(4)),list(range(6)),], list(self._dt.keys()))
        self.assertEqual(
            [
                ['one', 'One', 'ONE'],
                ['three', 'Three', 'THREE'],
                ['five', 'Five', 'FIVE']
            ],
            list(self._dt.values()),
            )
        self.assertEqual(3, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""0
  1
    ['one', 'One', 'ONE']
    2
      3
        ['three', 'Three', 'THREE']
        4
          5
            ['five', 'Five', 'FIVE']""",
            self._dt.indentedStr())
        
class TestDictTreeHtmlTableBase(unittest.TestCase):
    """Tests TestDictTreeHtmlTable row and col span functions."""
    def setUp(self):
        self._dt = DictTree.DictTreeHtmlTable()
        self.assertEqual([], list(self._dt.keys()))
        self.assertEqual([], list(self._dt.values()))
        self.assertEqual(0, len(self._dt))
        self.assertNotEqual(True, 'spam' in self._dt)
        
    def tearDown(self):
        pass
    
    def _retHtmlTableString(self, cellContentsIsValue=False):
        """If cellContentsIsValue then the value will be put in the cell if not
        None otherwise the tip of the key list."""
        htmlLineS = []
        # Write: <table border="2" width="100%">
        htmlLineS.append('<table border="2" width="100%">')
        for anEvent in self._dt.genColRowEvents():
            if anEvent == self._dt.ROW_OPEN:
                # Write out the '<tr>' element
                htmlLineS.append('<tr>')
            elif anEvent == self._dt.ROW_CLOSE:
                # Write out the '</tr>' element
                htmlLineS.append('</tr>')
            else:
                k, v, r, c = anEvent
                # Write '<td rowspan="%d" colspan="%d">%s</td>' % (r, c, txt[-1])
                myL = ['    <td']
                if r > 1:
                    myL.append(' rowspan="%d"' % r)
                if c > 1:
                    myL.append(' colspan="%d"' % c)
                if cellContentsIsValue and v is not None:
                    myL.append('>%s</td>' % v)
                else:
                    myL.append('>%s</td>' % k[-1])
                htmlLineS.append(''.join(myL))
        # Write: </table>
        htmlLineS.append('</table>')
        return '\n'.join(htmlLineS)

class TestDictTreeHtmlTable(TestDictTreeHtmlTableBase):    
    def test_00(self):
        """TestDictTreeHtmlTable: test_00(): row and col span."""
        self._dt.add(('X', 'XX', 'XXX'),    'Value XXX')
        self.assertEqual(3, self._dt.depth())
        self._dt.add(('X', 'XX', 'XXY'),    'Value XXY')
        self.assertEqual(3, self._dt.depth())
        self._dt.add(('X', 'XX', 'XXZ'),    'Value XXZ')
        self._dt.add(('X', 'XY',),          'Value XY')
        self._dt.add(('X', 'XZ', 'XZX'),    'Value XZX')
        self._dt.add(('Y',),                'Value Y')
        self._dt.add(('Z', 'ZX', 'ZXX'),    'Value ZXX')
        self.assertEqual(3, self._dt.depth())
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""X
  XX
    XXX
      Value XXX
    XXY
      Value XXY
    XXZ
      Value XXZ
  XY
    Value XY
  XZ
    XZX
      Value XZX
Y
  Value Y
Z
  ZX
    ZXX
      Value ZXX""",
            self._dt.indentedStr()
        )
        #print 'walkRowColSpan():'
        #print self._dt.walkColRowSpan()
        self.assertEqual("""X r=1, c=1
  XX r=1, c=1
    XXX r=1, c=1
    XXY r=1, c=1
    XXZ r=1, c=1
  XY r=1, c=1
  XZ r=1, c=1
    XZX r=1, c=1
Y r=1, c=1
Z r=1, c=1
  ZX r=1, c=1
    ZXX r=1, c=1
""", self._dt.walkColRowSpan())
        #print 'genRowColEvents()'
        #for anEvent in self._dt.genColRowEvents():
        #    print anEvent
        eventResult = '\n'.join([str(e) for e in self._dt.genColRowEvents()])
        #print
        #print eventResult
        self.assertEqual("""(None, 0, 0)
(['X'], None, 5, 1)
(['X', 'XX'], None, 3, 1)
(['X', 'XX', 'XXX'], 'Value XXX', 1, 1)
(None, -1, -1)
(None, 0, 0)
(['X', 'XX', 'XXY'], 'Value XXY', 1, 1)
(None, -1, -1)
(None, 0, 0)
(['X', 'XX', 'XXZ'], 'Value XXZ', 1, 1)
(None, -1, -1)
(None, 0, 0)
(['X', 'XY'], 'Value XY', 1, 2)
(None, -1, -1)
(None, 0, 0)
(['X', 'XZ'], None, 1, 1)
(['X', 'XZ', 'XZX'], 'Value XZX', 1, 1)
(None, -1, -1)
(None, 0, 0)
(['Y'], 'Value Y', 1, 3)
(None, -1, -1)
(None, 0, 0)
(['Z'], None, 1, 1)
(['Z', 'ZX'], None, 1, 1)
(['Z', 'ZX', 'ZXX'], 'Value ZXX', 1, 1)
(None, -1, -1)""",
            eventResult,
        )

    def test_01(self):
        """TestDictTreeHtmlTable: test_01(): row and col span."""
        self._dt.add(('X', 'XX',),    'Value XXX')
        self.assertEqual(2, self._dt.depth())
        self._dt.add(('X', 'XX',),    'Value XXY')
        self.assertEqual(2, self._dt.depth())
        self._dt.add(('X', 'XX',),    'Value XXZ')
        self._dt.add(('X',),          'Value XY')
        self._dt.add(('X', 'XZ',),    'Value XZX')
        self._dt.add(tuple(),             'Value Y')
        self._dt.add(('Z', 'ZX',),    'Value ZXX')
        self.assertEqual(2, self._dt.depth())
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""Value Y
X
  Value XY
  XX
    Value XXZ
  XZ
    Value XZX
Z
  ZX
    Value ZXX""",
        self._dt.indentedStr())
        #print 'walkRowColSpan():'
        #print self._dt.walkColRowSpan()
        #print 'genRowColEvents()'
        #for anEvent in self._dt.genColRowEvents():
        #    print anEvent
        eventResult = '\n'.join([str(e) for e in self._dt.genColRowEvents()])
        #print
        #print eventResult
        self.assertEqual("""(None, 0, 0)
(['X'], 'Value XY', 2, 1)
(['X', 'XX'], 'Value XXZ', 1, 1)
(None, -1, -1)
(None, 0, 0)
(['X', 'XZ'], 'Value XZX', 1, 1)
(None, -1, -1)
(None, 0, 0)
(['Z'], None, 1, 1)
(['Z', 'ZX'], 'Value ZXX', 1, 1)
(None, -1, -1)""",
            eventResult,
        )
        #print
        #print self._retHtmlTableString()

    def test_02(self):
        """TestDictTreeHtmlTable: test_02(): row and col span in an HTML table."""
        self._dt.add(('A', 'AA', 'AAA'), None)
        self._dt.add(('A', 'AA', 'AAB'), None)
        self._dt.add(('A', 'AA', 'AAC'), None)
        self._dt.add(('A', 'AB',), None)
        self._dt.add(('A', 'AC', 'ACA'), None)
        self._dt.add(('B',), None)
        self._dt.add(('C', 'CA', 'CAA'), None)
        eventResult = '\n'.join([str(e) for e in self._dt.genColRowEvents()])
        #print
        #print 'self._dt.indentedStr()'
        #print self._dt.indentedStr()
        #print 'self._dt.walkColRowSpan()'
        #print self._dt.walkColRowSpan()
        #print 'eventResult'
        #print eventResult
        #print 'self._retHtmlTableString()'
        #print self._retHtmlTableString()
        self.assertEqual("""<table border="2" width="100%">
<tr>
    <td rowspan="5">A</td>
    <td rowspan="3">AA</td>
    <td>AAA</td>
</tr>
<tr>
    <td>AAB</td>
</tr>
<tr>
    <td>AAC</td>
</tr>
<tr>
    <td colspan="2">AB</td>
</tr>
<tr>
    <td>AC</td>
    <td>ACA</td>
</tr>
<tr>
    <td colspan="3">B</td>
</tr>
<tr>
    <td>C</td>
    <td>CA</td>
    <td>CAA</td>
</tr>
</table>""",
            self._retHtmlTableString())
    
class TestDictTreeHtmlTableFile(TestDictTreeHtmlTableBase):
    """Tests TestDictTreeHtmlTable simulating a file/line/column table."""
    def fnSplit(self, f, l=None):
        retVal = ['%s/' % d for d in f.split('/')[:-1]]
        retVal.append(f.split('/')[-1])
        if l is not None:
            retVal.append(l)
        return retVal
        #return f.split('/') + [l,]

class TestDictTreeHtmlTableFileLineCol(TestDictTreeHtmlTableFile):
    """Tests TestDictTreeHtmlTable simulating a file/line/column table."""

    def setUp(self):
        self._dt = DictTree.DictTreeHtmlTable('list')
        self.assertEqual([], list(self._dt.keys()))
        self.assertEqual([], list(self._dt.values()))
        self.assertEqual(0, len(self._dt))
        self.assertNotEqual(True, 'spam' in self._dt)
        
    def tearDown(self):
        pass
    
    def test_00(self):
        """TestDictTreeHtmlTableFileLineCol: test_00(): Single file/line/column."""
        self._dt.add(('file_one', 12), 24)
        self._dt.add(('file_one', 12), 80)
        self.assertEqual(2, self._dt.depth())
        self.assertEqual([['file_one', 12]], list(self._dt.keys()))
        self.assertEqual(
            [
                [24, 80],
            ],
            list(self._dt.values()),
            )
        self.assertEqual(1, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""file_one
  12
    [24, 80]""",
            self._dt.indentedStr())
        
    def test_01(self):
        """TestDictTreeHtmlTableFileLineCol: test_01(): Multiple file/line/column."""
        # Same line, different column
        self._dt.add(('file_one', 12), 24)
        self._dt.add(('file_one', 12), 80)
        # Different line, different column
        self._dt.add(('file_two', 1), 1)
        self._dt.add(('file_two', 14), 75)
        # Same line, same column
        self._dt.add(('file_three', 15), 10)
        self._dt.add(('file_three', 15), 10)
        # Different line, same column
        self._dt.add(('file_four', 1), 19)
        self._dt.add(('file_four', 14), 19)
        self.assertEqual(2, self._dt.depth())
        self.assertEqual([
                          ['file_two', 1],
                          ['file_two', 14],
                          ['file_one', 12],
                          ['file_four', 1],
                          ['file_four', 14],
                          ['file_three', 15]
                        ],
                        list(self._dt.keys()))
        self.assertEqual(
            [
                [1],
                [75],
                [24, 80],
                [19], [19],
                [10, 10],
            ],
            list(self._dt.values()),
            )
        self.assertEqual(6, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""file_four
  1
    [19]
  14
    [19]
file_one
  12
    [24, 80]
file_three
  15
    [10, 10]
file_two
  1
    [1]
  14
    [75]""",
            self._dt.indentedStr())
        
    def test_02(self):
        """TestDictTreeHtmlTableFileLineCol: test_02(): Single file/line/column with split on path."""
        # Same line, different column
        self._dt.add(self.fnSplit('spam/eggs/chips.h', 12), 24)
        self._dt.add(self.fnSplit('spam/eggs/chips.h', 12), 80)
        self.assertEqual(4, self._dt.depth())
        self.assertEqual([
                          ['spam/', 'eggs/', 'chips.h', 12],
                        ],
                        list(self._dt.keys()))
        self.assertEqual(
            [
                [24, 80],
            ],
            list(self._dt.values()),
            )
        self.assertEqual(1, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""spam/
  eggs/
    chips.h
      12
        [24, 80]""",
            self._dt.indentedStr())
        
    def test_03(self):
        """TestDictTreeHtmlTableFileLineCol: test_03(): Multiple file/line/column with split on path."""
        self._dt.add(self.fnSplit('spam.h', 12), 24)
        self._dt.add(self.fnSplit('spam/eggs.h', 12), 24)
        self._dt.add(self.fnSplit('spam/cheese.h', 12), 24)
        self._dt.add(self.fnSplit('spam/cheese.h', 14), 28)
        self._dt.add(self.fnSplit('spam/eggs/chips.h', 12), 24)
        self._dt.add(self.fnSplit('spam/eggs/chips/beans.h', 12), 24)
        self._dt.add(self.fnSplit('spam/eggs/chips/beans.h', 12), 80)
        #print
        #print self._retHtmlTableString()
        self.assertEqual(5, self._dt.depth())
        #print
        #pprint.pprint(self._dt.keys())
        self.assertEqual(
                    [
                        ['spam/', 'eggs/', 'chips.h', 12],
                        ['spam/', 'eggs/', 'chips/', 'beans.h', 12],
                        ['spam/', 'cheese.h', 12],
                        ['spam/', 'cheese.h', 14],
                        ['spam/', 'eggs.h', 12],
                        ['spam.h', 12],
                    ],
                    list(self._dt.keys()))
        self.assertEqual(
            [
                [24], [24, 80], [24], [28], [24], [24],
            ],
            list(self._dt.values()),
            )
        self.assertEqual(6, len(self._dt))
        #print
        #print self._dt.indentedStr()
        self.assertEqual("""spam.h
  12
    [24]
spam/
  cheese.h
    12
      [24]
    14
      [28]
  eggs.h
    12
      [24]
  eggs/
    chips.h
      12
        [24]
    chips/
      beans.h
        12
          [24, 80]""",
            self._dt.indentedStr())
        #print
        #print self._retHtmlTableString()
        self.assertEqual("""<table border="2" width="100%">
<tr>
    <td>spam.h</td>
    <td colspan="4">12</td>
</tr>
<tr>
    <td rowspan="5">spam/</td>
    <td rowspan="2">cheese.h</td>
    <td colspan="3">12</td>
</tr>
<tr>
    <td colspan="3">14</td>
</tr>
<tr>
    <td>eggs.h</td>
    <td colspan="3">12</td>
</tr>
<tr>
    <td rowspan="2">eggs/</td>
    <td>chips.h</td>
    <td colspan="2">12</td>
</tr>
<tr>
    <td>chips/</td>
    <td>beans.h</td>
    <td>12</td>
</tr>
</table>""",
            self._retHtmlTableString())
        
    def test_04(self):
        """TestDictTreeHtmlTableFileLineCol: test_04(): Multiple file/line/column with split on path."""
        for aLine in """epoc32/include/bldcodeline.hrh 
epoc32/include/bldprivate.hrh 
epoc32/include/bldpublic.hrh 
epoc32/include/bldregional.hrh 
epoc32/include/bldvariant.hrh 
epoc32/include/defaultcaps.hrh 
epoc32/include/e32base.h 
epoc32/include/e32base.inl 
epoc32/include/e32capability.h 
epoc32/include/e32cmn.h 
epoc32/include/e32cmn.inl 
epoc32/include/e32const.h 
epoc32/include/e32def.h 
epoc32/include/e32des16.h 
epoc32/include/e32des8.h 
epoc32/include/e32err.h 
epoc32/include/e32lang.h 
epoc32/include/e32reg.h 
epoc32/include/e32std.h 
epoc32/include/e32std.inl 
epoc32/include/platform/cflog.h 
epoc32/include/privateruntimeids.hrh 
epoc32/include/productvariant.hrh 
epoc32/include/publicruntimeids.hrh 
epoc32/include/variant/Symbian_OS.hrh 
epoc32/include/variant/platform_paths.hrh 
sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.cpp 
sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.h""".split('\n'):
            self._dt.add(self.fnSplit(aLine), None)
        #print
        #print self._retHtmlTableString()
        self.assertEqual("""<table border="2" width="100%">
<tr>
    <td rowspan="26">epoc32/</td>
    <td rowspan="26">include/</td>
    <td colspan="5">bldcodeline.hrh </td>
</tr>
<tr>
    <td colspan="5">bldprivate.hrh </td>
</tr>
<tr>
    <td colspan="5">bldpublic.hrh </td>
</tr>
<tr>
    <td colspan="5">bldregional.hrh </td>
</tr>
<tr>
    <td colspan="5">bldvariant.hrh </td>
</tr>
<tr>
    <td colspan="5">defaultcaps.hrh </td>
</tr>
<tr>
    <td colspan="5">e32base.h </td>
</tr>
<tr>
    <td colspan="5">e32base.inl </td>
</tr>
<tr>
    <td colspan="5">e32capability.h </td>
</tr>
<tr>
    <td colspan="5">e32cmn.h </td>
</tr>
<tr>
    <td colspan="5">e32cmn.inl </td>
</tr>
<tr>
    <td colspan="5">e32const.h </td>
</tr>
<tr>
    <td colspan="5">e32def.h </td>
</tr>
<tr>
    <td colspan="5">e32des16.h </td>
</tr>
<tr>
    <td colspan="5">e32des8.h </td>
</tr>
<tr>
    <td colspan="5">e32err.h </td>
</tr>
<tr>
    <td colspan="5">e32lang.h </td>
</tr>
<tr>
    <td colspan="5">e32reg.h </td>
</tr>
<tr>
    <td colspan="5">e32std.h </td>
</tr>
<tr>
    <td colspan="5">e32std.inl </td>
</tr>
<tr>
    <td>platform/</td>
    <td colspan="4">cflog.h </td>
</tr>
<tr>
    <td colspan="5">privateruntimeids.hrh </td>
</tr>
<tr>
    <td colspan="5">productvariant.hrh </td>
</tr>
<tr>
    <td colspan="5">publicruntimeids.hrh </td>
</tr>
<tr>
    <td rowspan="2">variant/</td>
    <td colspan="4">Symbian_OS.hrh </td>
</tr>
<tr>
    <td colspan="4">platform_paths.hrh </td>
</tr>
<tr>
    <td rowspan="2">sf/</td>
    <td rowspan="2">os/</td>
    <td rowspan="2">networkingsrv/</td>
    <td rowspan="2">networkcontrol/</td>
    <td rowspan="2">iptransportlayer/</td>
    <td rowspan="2">src/</td>
    <td>ipscprlog.cpp </td>
</tr>
<tr>
    <td>ipscprlog.h</td>
</tr>
</table>""",
            self._retHtmlTableString())

class TestDictTreeHtmlTableFileTree(TestDictTreeHtmlTableFile):
    """Tests TestDictTreeHtmlTableFileTree simulating a directory structure."""

    def setUp(self):
        self._dt = DictTree.DictTreeHtmlTable(None)
        self.assertEqual([], list(self._dt.keys()))
        self.assertEqual([], list(self._dt.values()))
        self.assertEqual(0, len(self._dt))
        self.assertNotEqual(True, 'spam' in self._dt)
        
    def tearDown(self):
        pass
    
    def test_01(self):
        """TestDictTreeHtmlTableFileTree: test_01(): Multiple file/line/column with split on path and links."""
        for aLine in """epoc32/include/bldcodeline.hrh 
epoc32/include/bldprivate.hrh 
epoc32/include/bldpublic.hrh 
epoc32/include/bldregional.hrh 
epoc32/include/bldvariant.hrh 
epoc32/include/defaultcaps.hrh 
epoc32/include/e32base.h 
epoc32/include/e32base.inl 
epoc32/include/e32capability.h 
epoc32/include/e32cmn.h 
epoc32/include/e32cmn.inl 
epoc32/include/e32const.h 
epoc32/include/e32def.h 
epoc32/include/e32des16.h 
epoc32/include/e32des8.h 
epoc32/include/e32err.h 
epoc32/include/e32lang.h 
epoc32/include/e32reg.h 
epoc32/include/e32std.h 
epoc32/include/e32std.inl 
epoc32/include/platform/cflog.h 
epoc32/include/privateruntimeids.hrh 
epoc32/include/productvariant.hrh 
epoc32/include/publicruntimeids.hrh 
epoc32/include/variant/Symbian_OS.hrh 
epoc32/include/variant/platform_paths.hrh 
sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.cpp 
sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.h""".split('\n'):
            aLine = aLine.strip()
            self._dt.add(self.fnSplit(aLine), '<a href="%s">%s</a>' % (aLine, os.path.basename(aLine)))
        eventResult = '\n'.join([str(e) for e in self._dt.genColRowEvents()])
#        print()
#        print(self._dt.indentedStr())
#        self.maxDiff = None
        self.assertEqual("""epoc32/
  include/
    bldcodeline.hrh
      <a href="epoc32/include/bldcodeline.hrh">bldcodeline.hrh</a>
    bldprivate.hrh
      <a href="epoc32/include/bldprivate.hrh">bldprivate.hrh</a>
    bldpublic.hrh
      <a href="epoc32/include/bldpublic.hrh">bldpublic.hrh</a>
    bldregional.hrh
      <a href="epoc32/include/bldregional.hrh">bldregional.hrh</a>
    bldvariant.hrh
      <a href="epoc32/include/bldvariant.hrh">bldvariant.hrh</a>
    defaultcaps.hrh
      <a href="epoc32/include/defaultcaps.hrh">defaultcaps.hrh</a>
    e32base.h
      <a href="epoc32/include/e32base.h">e32base.h</a>
    e32base.inl
      <a href="epoc32/include/e32base.inl">e32base.inl</a>
    e32capability.h
      <a href="epoc32/include/e32capability.h">e32capability.h</a>
    e32cmn.h
      <a href="epoc32/include/e32cmn.h">e32cmn.h</a>
    e32cmn.inl
      <a href="epoc32/include/e32cmn.inl">e32cmn.inl</a>
    e32const.h
      <a href="epoc32/include/e32const.h">e32const.h</a>
    e32def.h
      <a href="epoc32/include/e32def.h">e32def.h</a>
    e32des16.h
      <a href="epoc32/include/e32des16.h">e32des16.h</a>
    e32des8.h
      <a href="epoc32/include/e32des8.h">e32des8.h</a>
    e32err.h
      <a href="epoc32/include/e32err.h">e32err.h</a>
    e32lang.h
      <a href="epoc32/include/e32lang.h">e32lang.h</a>
    e32reg.h
      <a href="epoc32/include/e32reg.h">e32reg.h</a>
    e32std.h
      <a href="epoc32/include/e32std.h">e32std.h</a>
    e32std.inl
      <a href="epoc32/include/e32std.inl">e32std.inl</a>
    platform/
      cflog.h
        <a href="epoc32/include/platform/cflog.h">cflog.h</a>
    privateruntimeids.hrh
      <a href="epoc32/include/privateruntimeids.hrh">privateruntimeids.hrh</a>
    productvariant.hrh
      <a href="epoc32/include/productvariant.hrh">productvariant.hrh</a>
    publicruntimeids.hrh
      <a href="epoc32/include/publicruntimeids.hrh">publicruntimeids.hrh</a>
    variant/
      Symbian_OS.hrh
        <a href="epoc32/include/variant/Symbian_OS.hrh">Symbian_OS.hrh</a>
      platform_paths.hrh
        <a href="epoc32/include/variant/platform_paths.hrh">platform_paths.hrh</a>
sf/
  os/
    networkingsrv/
      networkcontrol/
        iptransportlayer/
          src/
            ipscprlog.cpp
              <a href="sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.cpp">ipscprlog.cpp</a>
            ipscprlog.h
              <a href="sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.h">ipscprlog.h</a>""",
              self._dt.indentedStr())
        #print
        #print eventResult
        #print
        #print self._retHtmlTableString()
        #print
        #print self._retHtmlTableString(cellContentsIsValue=True)
        self.assertEqual("""<table border="2" width="100%">
<tr>
    <td rowspan="26">epoc32/</td>
    <td rowspan="26">include/</td>
    <td colspan="5"><a href="epoc32/include/bldcodeline.hrh">bldcodeline.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/bldprivate.hrh">bldprivate.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/bldpublic.hrh">bldpublic.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/bldregional.hrh">bldregional.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/bldvariant.hrh">bldvariant.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/defaultcaps.hrh">defaultcaps.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32base.h">e32base.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32base.inl">e32base.inl</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32capability.h">e32capability.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32cmn.h">e32cmn.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32cmn.inl">e32cmn.inl</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32const.h">e32const.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32def.h">e32def.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32des16.h">e32des16.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32des8.h">e32des8.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32err.h">e32err.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32lang.h">e32lang.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32reg.h">e32reg.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32std.h">e32std.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/e32std.inl">e32std.inl</a></td>
</tr>
<tr>
    <td>platform/</td>
    <td colspan="4"><a href="epoc32/include/platform/cflog.h">cflog.h</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/privateruntimeids.hrh">privateruntimeids.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/productvariant.hrh">productvariant.hrh</a></td>
</tr>
<tr>
    <td colspan="5"><a href="epoc32/include/publicruntimeids.hrh">publicruntimeids.hrh</a></td>
</tr>
<tr>
    <td rowspan="2">variant/</td>
    <td colspan="4"><a href="epoc32/include/variant/Symbian_OS.hrh">Symbian_OS.hrh</a></td>
</tr>
<tr>
    <td colspan="4"><a href="epoc32/include/variant/platform_paths.hrh">platform_paths.hrh</a></td>
</tr>
<tr>
    <td rowspan="2">sf/</td>
    <td rowspan="2">os/</td>
    <td rowspan="2">networkingsrv/</td>
    <td rowspan="2">networkcontrol/</td>
    <td rowspan="2">iptransportlayer/</td>
    <td rowspan="2">src/</td>
    <td><a href="sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.cpp">ipscprlog.cpp</a></td>
</tr>
<tr>
    <td><a href="sf/os/networkingsrv/networkcontrol/iptransportlayer/src/ipscprlog.h">ipscprlog.h</a></td>
</tr>
</table>""",
            self._retHtmlTableString(cellContentsIsValue=True))


class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDictTreeCtor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDictTreeAdd))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDictTreeAddList))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDictTreeAddSet))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDictTreeAddBespokeList))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDictTreeHtmlTable))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDictTreeHtmlTableFileLineCol))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDictTreeHtmlTableFileTree))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestDictTree.py - A module that tests DictTree module.
Usage:
python TestDictTree.py [-lh --help]

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
    print('TestDictTree.py script version "%s", dated %s' % (__version__, __date__))
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
