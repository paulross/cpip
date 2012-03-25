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

"""Tests CppCond.py
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import sys
import time
import logging

from cpip.core import CppCond
from cpip.core import FileLocation

######################
# Section: Unit tests.
######################
import unittest

class TestConditionalState(unittest.TestCase):
    """Tests the ConditionalState class."""
    def testCtor(self):
        """ConditionalState: Test basic construction."""
        myCs = CppCond.ConditionalState(True, 'me')
        self.assertEqual(True, myCs.state)
        self.assertEqual('me', myCs.constExprStr())

    def testFlip_00(self):
        """ConditionalState: Test flip() False->True->False == False->True->False."""
        myCs = CppCond.ConditionalState(False, 'me')
        self.assertEqual(False, myCs.state)
        self.assertEqual('me', myCs.constExprStr())
        myCs.flip()
        self.assertEqual(True, myCs.state)
        self.assertEqual('%s(me)' % CppCond.TOKEN_NEGATION, myCs.constExprStr())
        myCs.flip()
        self.assertEqual(False, myCs.state)
        self.assertEqual('%s(%s(me))' \
                         % (CppCond.TOKEN_NEGATION, CppCond.TOKEN_NEGATION), myCs.constExprStr())

    def testFlip_01(self):
        """ConditionalState: Test flip() True->False->True == True->False->False."""
        myCs = CppCond.ConditionalState(True, 'me')
        self.assertEqual(True, myCs.state)
        self.assertEqual('me', myCs.constExprStr())
        myCs.flip()
        self.assertEqual(False, myCs.state)
        self.assertEqual('%s(me)' % CppCond.TOKEN_NEGATION, myCs.constExprStr())
        myCs.flip()
        self.assertEqual(False, myCs.state)
        self.assertEqual('%s(%s(me))' \
                         % (CppCond.TOKEN_NEGATION, CppCond.TOKEN_NEGATION), myCs.constExprStr())

    def testFlipAndAdd_00(self):
        """ConditionalState: Test flipAndAdd() False->True->True == False->True->False."""
        #if a
        myCs = CppCond.ConditionalState(False, 'a')
        self.assertEqual(False, myCs.state)
        self.assertEqual('a', myCs.constExprStr())
        self.assertEqual('!(a)', myCs.constExprStr(invert=True))
        #elif b
        myCs.flipAndAdd(True, 'b')
        self.assertEqual(True, myCs.state)
        self.assertEqual('(%s)' % CppCond.TOKEN_JOIN_AND.join(['!(a)', 'b']),
                         myCs.constExprStr())
        self.assertEqual('%s(%s)' % (
                                     CppCond.TOKEN_NEGATION,
                                     CppCond.TOKEN_JOIN_OR.join(['!(a)', 'b'])
                                     ),
                         myCs.constExprStr(invert=True))
        #elif c
        myCs.flipAndAdd(True, 'c')
        self.assertEqual(False, myCs.state)
        self.assertEqual('(%s)' % CppCond.TOKEN_JOIN_AND.join(['!(a)', '!(b)', 'c',]),
                         myCs.constExprStr())
        self.assertEqual('%s(%s)' % (
                                     CppCond.TOKEN_NEGATION,
                                     CppCond.TOKEN_JOIN_OR.join(['!(a)', '!(b)', 'c',])
                                     ),
                         myCs.constExprStr(invert=True))

    def testFlipAndAdd_01(self):
        """ConditionalState: Test flipAndAdd() True->False->True == True->False->False."""
        #if a
        myCs = CppCond.ConditionalState(True, 'a')
        self.assertEqual(True, myCs.state)
        self.assertEqual('a', myCs.constExprStr())
        self.assertEqual('!(a)', myCs.constExprStr(invert=True))
        #elif b
        myCs.flipAndAdd(False, 'b')
        self.assertEqual(False, myCs.state)
        self.assertEqual('(%s)' % CppCond.TOKEN_JOIN_AND.join(['!(a)', 'b']),
                         myCs.constExprStr())
        self.assertEqual('%s(%s)' % (
                                     CppCond.TOKEN_NEGATION,
                                     CppCond.TOKEN_JOIN_OR.join(['!(a)', 'b'])
                                     ),
                         myCs.constExprStr(invert=True))
        #elif c
        myCs.flipAndAdd(True, 'c')
        self.assertEqual(False, myCs.state)
        self.assertEqual('(%s)' % CppCond.TOKEN_JOIN_AND.join(['!(a)', '!(b)', 'c',]),
                         myCs.constExprStr())
        self.assertEqual('%s(%s)' % (
                                     CppCond.TOKEN_NEGATION,
                                     CppCond.TOKEN_JOIN_OR.join(['!(a)', '!(b)', 'c',])
                                     ),
                         myCs.constExprStr(invert=True))

    def testFlipAndAdd_02(self):
        """ConditionalState: Test flipAndAdd() False->False->True == False->False->False."""
        #if a
        myCs = CppCond.ConditionalState(False, 'a')
        self.assertEqual(False, myCs.state)
        self.assertEqual('a', myCs.constExprStr())
        self.assertEqual('!(a)', myCs.constExprStr(invert=True))
        #elif b
        myCs.flipAndAdd(False, 'b')
        self.assertEqual(False, myCs.state)
        self.assertEqual('(%s)' % CppCond.TOKEN_JOIN_AND.join(['!(a)', 'b']),
                         myCs.constExprStr())
        self.assertEqual('%s(%s)' % (
                                     CppCond.TOKEN_NEGATION,
                                     CppCond.TOKEN_JOIN_OR.join(['!(a)', 'b'])
                                     ),
                         myCs.constExprStr(invert=True))
        #elif c
        myCs.flipAndAdd(True, 'c')
        self.assertEqual(True, myCs.state)
        self.assertEqual('(%s)' % CppCond.TOKEN_JOIN_AND.join(['!(a)', '!(b)', 'c',]),
                         myCs.constExprStr())
        self.assertEqual('%s(%s)' % (
                                     CppCond.TOKEN_NEGATION,
                                     CppCond.TOKEN_JOIN_OR.join(['!(a)', '!(b)', 'c',])
                                     ),
                         myCs.constExprStr(invert=True))

class TestCppCondLowLevel(unittest.TestCase):
    """Tests the CppCond class."""
    def testEmptyCtor(self):
        """Construct an empty CppCond and test."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.close()

    def testSingleInsertTrue(self):
        """Construct an empty CppCond, push True and test."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj._push(True, '')
        self.assertEqual(1, myObj.stackDepth)
        # Test __nonzero__
        self.assertEqual(True, myObj!=False)
        # This is odd
        self.assertEqual(False, myObj==False)
        # self.assertEqual(True, myObj) evaluates to:
        # AssertionError: True != <__main__.CppCond object at 0x00989F10>
        # So we fall back on this test:
        if myObj:
            self.assertEqual(True, True)
        else:
            self.assertEqual(True, False)
        self.assertRaises(CppCond.ExceptionCppCond, myObj.close)
        myObj._pop()
        myObj.close()

    def testSingleInsertFalse(self):
        """Construct an empty CppCond, push False and test."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        self.assertEqual(True, myObj.isTrue())
        myObj._push(False, '')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual(False, myObj.isTrue())
        # self.assertEqual(True, myObj) evaluates to:
        # AssertionError: True != <__main__.CppCond object at 0x00989F10>
        # So we fall back on this test:
        if myObj:
            self.fail('CppCond object is True!')

    def testExceptionRaising(self):
        """Construct an empty CppCond, test exception conditions."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        # Everything outside an empty stack is True
        self.assertEqual(True, myObj.isTrue())
        self.assertRaises(CppCond.ExceptionCppCond, myObj._pop)
        self.assertRaises(CppCond.ExceptionCppCond, myObj._flip)
        myObj.close()

    def testSimplePushAndTestLeafFlip_00(self):
        """Construct an empty CppCond, test flip() with True->False->True == True->False->False."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj._push(True, '')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual(True, myObj.isTrue())
        myObj._flip()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual(False, myObj.isTrue())
        myObj._flip()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual(False, myObj.isTrue())
        myObj._pop()
        myObj.close()

    def testSimplePushAndTestLeafFlip_01(self):
        """Construct an empty CppCond, test flip() with False->True->False == False->True->False."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj._push(False, '')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual(False, myObj.isTrue())
        myObj._flip()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual(True, myObj.isTrue())
        myObj._flip()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual(False, myObj.isTrue())
        myObj._pop()
        myObj.close()

class TestCppCondConstExpr(unittest.TestCase):
    """Tests the CppCond class constants expression."""
    def testSinglePush(self):
        """CppCond with a single constant-expression."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj._push(True, '1 > 0')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1 > 0', str(myObj))
        myObj._flip()
        self.assertEqual('!(1 > 0)', str(myObj))
        myObj._flip()
        self.assertEqual('!(!(1 > 0))', str(myObj))
        myObj._pop()
        myObj.close()

    def testMultiplePush(self):
        """CppCond with multiple constant-expressions."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj._push(True, '1 > 0')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1 > 0', str(myObj))
        myObj._push(True, '2 > 1')
        self.assertEqual('1 > 0 && 2 > 1', str(myObj))
        myObj._flip()
        self.assertEqual('1 > 0 && !(2 > 1)', str(myObj))
        myObj._pop()
        self.assertEqual('1 > 0', str(myObj))
        myObj._flip()
        self.assertEqual('!(1 > 0)', str(myObj))
        myObj._pop()
        myObj.close()

    def testElifLevel_1(self):
        """CppCond with #if/#elif constant-expressions for a stack depth of one."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        #if True
        myObj.oIf(True, '1 > 0')
        self.assertEqual(1, myObj.stackDepth)
        self.assertTrue(myObj.isTrue())
        self.assertEqual('1 > 0', str(myObj))
        #elif True is False because of previous True
        myObj.oElif(True, '2 > 1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertFalse(myObj.isTrue())
        self.assertEqual('(!(1 > 0) && 2 > 1)', str(myObj))
        myObj.oEndif()
        myObj.close()

    def testElifLevel_0(self):
        """CppCond with #elif, #endif constant-expressions for a stack depth of zero."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        self.assertRaises(CppCond.ExceptionCppCond, myObj.oElif, True, 'EGGS')
        self.assertRaises(CppCond.ExceptionCppCond, myObj.oEndif)
        myObj.close()

    def testIfdefElifLevel_1(self):
        """CppCond with #ifdef/#elif constant-expressions for a stack depth of one."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        #if True
        myObj.oIfdef(True, 'SPAM')
        self.assertEqual(1, myObj.stackDepth)
        self.assertTrue(myObj.isTrue())
        self.assertEqual('SPAM', str(myObj))
        #elif True is False because of previous True
        myObj.oElif(True, '2 > 1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertFalse(myObj.isTrue())
        self.assertEqual('(!(SPAM) && 2 > 1)', str(myObj))
        myObj.oEndif()
        myObj.close()

    def testIfndefElifLevel_1(self):
        """CppCond with #ifndef/#elif constant-expressions for a stack depth of one."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        #define SPAM
        #ifndef SPAM
        myObj.oIfndef(True, 'SPAM')
        self.assertEqual(1, myObj.stackDepth)
        self.assertFalse(myObj.isTrue())
        self.assertEqual('SPAM', str(myObj))
        #elif True is True because of previous False
        myObj.oElif(True, '2 > 1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertTrue(myObj.isTrue())
        self.assertEqual('(!(SPAM) && 2 > 1)', str(myObj))
        myObj.oEndif()
        myObj.close()

class TestCppCondIfElifElse(unittest.TestCase):
    """Tests the CppCond with #if/#elif/#else variants."""
    def testElifElse_0(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 1; #if block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(True, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oElif(False, '0')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && 0)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && !(0))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        myObj.close()

    def testElifElse_1(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 1; #elif block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(False, '0')
        self.assertEqual(1, myObj.stackDepth)
        self.assertFalse(myObj.isTrue())
        self.assertEqual('0', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(True, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertTrue(myObj.isTrue())
        self.assertEqual('(!(0) && 1)', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(0) && !(1))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        myObj.close()

    def testElifElse_2(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 1; #else block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(False, '0')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('0', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(False, '0')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(0) && 0)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertTrue(myObj.isTrue())
        self.assertEqual('(!(0) && !(0))', str(myObj))
        myObj.oEndif()
        myObj.close()

    def testElifElse_3(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 1; #if block prevails but #elif is True."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(True, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oElif(True, '2')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && 2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        myObj.close()

class TestCppCondIfElifElseMultipleDepth(unittest.TestCase):
    """Tests the CppCond with #if/#elif/#else variants."""
    def testElifElse_00(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 2; #if/#if block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(True, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1', str(myObj))
        self.assertTrue(myObj.isTrue())
        # Second block
        myObj.oIf(True, '1.1')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('1 && 1.1', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oElif(False, '1.2')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('1 && (!(1.1) && 1.2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('1 && (!(1.1) && !(1.2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        self.assertEqual(1, myObj.stackDepth)
        # Back to first block
        myObj.oElif(False, '2')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && 2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        myObj.close()

    def testElifElse_01(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 2; #if/#elif block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(True, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1', str(myObj))
        self.assertTrue(myObj.isTrue())
        # Second block
        myObj.oIf(False, '1.1')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('1 && 1.1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(True, '1.2')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('1 && (!(1.1) && 1.2)', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('1 && (!(1.1) && !(1.2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        self.assertEqual(1, myObj.stackDepth)
        # Back to first block
        myObj.oElif(False, '2')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && 2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        myObj.close()

    def testElifElse_02(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 2; #if/#else block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(True, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1', str(myObj))
        self.assertTrue(myObj.isTrue())
        # Second block
        myObj.oIf(False, '1.1')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('1 && 1.1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(False, '1.2')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('1 && (!(1.1) && 1.2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('1 && (!(1.1) && !(1.2))', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oEndif()
        self.assertEqual(1, myObj.stackDepth)
        # Back to first block
        myObj.oElif(False, '2')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && 2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        myObj.close()

    def testElifElse_03(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 2; #elif/#if block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(False, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(True, '2')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && 2)', str(myObj))
        self.assertTrue(myObj.isTrue())
        # Second block
        myObj.oIf(True, '1.1')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && 2) && 1.1', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oElif(False, '1.2')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && 2) && (!(1.1) && 1.2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && 2) && (!(1.1) && !(1.2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        self.assertEqual(1, myObj.stackDepth)
        # Back to first block
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        myObj.close()

    def testElifElse_04(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 2; #elif/#elif block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(False, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(True, '2')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && 2)', str(myObj))
        self.assertTrue(myObj.isTrue())
        # Second block
        myObj.oIf(False, '1.1')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && 2) && 1.1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(True, '1.2')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && 2) && (!(1.1) && 1.2)', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && 2) && (!(1.1) && !(1.2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        self.assertEqual(1, myObj.stackDepth)
        # Back to first block
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        myObj.close()

    def testElifElse_05(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 2; #elif/#else block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(False, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(True, '2')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && 2)', str(myObj))
        self.assertTrue(myObj.isTrue())
        # Second block
        myObj.oIf(False, '1.1')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && 2) && 1.1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(False, '1.2')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && 2) && (!(1.1) && 1.2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && 2) && (!(1.1) && !(1.2))', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oEndif()
        self.assertEqual(1, myObj.stackDepth)
        # Back to first block
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        myObj.close()

    def testElifElse_06(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 2; #else/#if block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(False, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(False, '2')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && 2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2))', str(myObj))
        self.assertTrue(myObj.isTrue())
        # Second block
        myObj.oIf(True, '1.1')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2)) && 1.1', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oElif(False, '1.2')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2)) && (!(1.1) && 1.2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2)) && (!(1.1) && !(1.2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        self.assertEqual(1, myObj.stackDepth)
        # Back to first block        
        myObj.oEndif()
        myObj.close()

    def testElifElse_07(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 2; #else/#elif block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(False, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(False, '2')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && 2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2))', str(myObj))
        self.assertTrue(myObj.isTrue())
        # Second block
        myObj.oIf(False, '1.1')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2)) && 1.1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(True, '1.2')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2)) && (!(1.1) && 1.2)', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2)) && (!(1.1) && !(1.2))', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oEndif()
        self.assertEqual(1, myObj.stackDepth)
        # Back to first block        
        myObj.oEndif()
        myObj.close()

    def testElifElse_08(self):
        """CppCond with #if/#elif/#else constant-expressions, depth 2; #else/#else block prevails."""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(False, '1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(False, '2')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && 2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2))', str(myObj))
        self.assertTrue(myObj.isTrue())
        # Second block
        myObj.oIf(False, '1.1')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2)) && 1.1', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElif(False, '1.2')
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2)) && (!(1.1) && 1.2)', str(myObj))
        self.assertFalse(myObj.isTrue())
        myObj.oElse()
        self.assertEqual(2, myObj.stackDepth)
        self.assertEqual('(!(1) && !(2)) && (!(1.1) && !(1.2))', str(myObj))
        self.assertTrue(myObj.isTrue())
        myObj.oEndif()
        self.assertEqual(1, myObj.stackDepth)
        # Back to first block        
        myObj.oEndif()
        myObj.close()

class TestCppCond(unittest.TestCase):
    """Tests the CppCond as a caller might use it."""
    def testSequentialBool(self):
        """CppCond simulating an example of sequential #if, #elif #else from ISO/IEC 9899:1999(E) section 6.10.2-8
#if VERSION == 1
#define INCFILE "vers1.h"
#elif VERSION == 2
#define INCFILE "vers2.h" // and so on
#else
#define INCFILE "versN.h"
#endif
#include INCFILE
Forward references: macro replacement (6.10"""
        myObj = CppCond.CppCond()
        self.assertEqual(0, myObj.stackDepth)
        myObj.oIf(False, 'VERSION == 1')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual('VERSION == 1', str(myObj))
        myObj.oElif(False, 'VERSION == 2')
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual(
            '(!(VERSION == 1) && VERSION == 2)',
            str(myObj)
            )
        myObj.oElse()
        self.assertEqual(1, myObj.stackDepth)
        self.assertEqual(
            '(!(VERSION == 1) && !(VERSION == 2))',
            str(myObj)
            )
        myObj.oEndif()
        myObj.close()

class TestCppCondGraph(unittest.TestCase):
    """Tests the CppCondGraph."""
    def test_00(self):
        """CppCondGraph.test_00() - Simple construction."""
        myObj = CppCond.CppCondGraph()
        self.assertTrue(myObj.isComplete)
        #print
        #print myObj
        self.assertEqual("""""", str(myObj))
    
    def test_00_00(self):
        """CppCondGraph.test_00_00() - ifSection raises on empty graph."""
        myObj = CppCond.CppCondGraph()
        self.assertTrue(myObj.isComplete)
        #print
        #print myObj
        self.assertEqual("""""", str(myObj))
        
    def test_00_01(self):
        """CppCondGraph.test_00_01() - __str__()."""
        myObj = CppCond.CppCondGraph()
        self.assertTrue(myObj.isComplete)
        #print
        #print myObj
        self.assertEqual("""""", str(myObj))
    
    def test_00_02(self):
        """CppCondGraph.test_00_02() - Fails when no #if but #elif."""
        myObj = CppCond.CppCondGraph()
        self.assertTrue(myObj.isComplete)
        try:
            myObj.oElif(False, 'elif Condition 1', FileLocation.FileLineCol('file', 11, 1), 0)
            self.fail('ifSection fails to raise ExceptionCppCondGraph when #elif but no #if.')
        except CppCond.ExceptionCppCondGraph:
            pass
    
    def test_00_03(self):
        """CppCondGraph.test_00_03() - Fails when no #if but #else."""
        myObj = CppCond.CppCondGraph()
        self.assertTrue(myObj.isComplete)
        try:
            myObj.oElse(FileLocation.FileLineCol('file', 11, 1), 0, False)
            self.fail('ifSection fails to raise ExceptionCppCondGraph when #else but no #if.')
        except CppCond.ExceptionCppCondGraph:
            pass
    
    def test_00_04(self):
        """CppCondGraph.test_00_04() - Fails when no #if but #endif."""
        myObj = CppCond.CppCondGraph()
        self.assertTrue(myObj.isComplete)
        try:
            myObj.oEndif(FileLocation.FileLineCol('file', 11, 1), 0, True)
            self.fail('ifSection fails to raise ExceptionCppCondGraph when #endif but no #if.')
        except CppCond.ExceptionCppCondGraph:
            pass
    
    def test_01(self):
        """CppCondGraph.test_01() - Single #if, no #endif."""
        myObj = CppCond.CppCondGraph()
        myObj.oIf(FileLocation.FileLineCol('file', 1, 2), 0, True, 'Condition')
        self.assertFalse(myObj.isComplete)
        #print
        #print myObj
        self.assertEqual(
            """#if Condition /* True "file" 1 0 */""",
            str(myObj),
        )
    
    def test_02(self):
        """CppCondGraph.test_02() - Single #if/#endif."""
        myObj = CppCond.CppCondGraph()
        myObj.oIf(FileLocation.FileLineCol('file', 1, 1), 0,True, 'Condition')
        myObj.oEndif(FileLocation.FileLineCol('file', 2, 1), 0, True)
        self.assertTrue(myObj.isComplete)
        #print
        #print myObj
        self.assertEqual(
            """#if Condition /* True "file" 1 0 */
#endif /* True "file" 2 0 */""",
            str(myObj),
        )
    
    def test_03(self):
        """CppCondGraph.test_03() - Single #if/#else/#endif."""
        myObj = CppCond.CppCondGraph()
        myObj.oIf(FileLocation.FileLineCol('file', 1, 1), 0, True, 'Condition')
        myObj.oElse(FileLocation.FileLineCol('file', 2, 1), 0, True)
        myObj.oEndif(FileLocation.FileLineCol('file', 3, 1), 0, True)
        self.assertTrue(myObj.isComplete)
        #print
        #print myObj
        self.assertEqual(
            """#if Condition /* True "file" 1 0 */
#else /* True "file" 2 0 */
#endif /* True "file" 3 0 */""",
            str(myObj),
        )
    
    def test_04(self):
        """CppCondGraph.test_04() - Single #if/#elif/#else/#endif."""
        myObj = CppCond.CppCondGraph()
        myObj.oIf(FileLocation.FileLineCol('file', 1, 1), 0, True, 'if Condition')
        #print
        #print myObj
        myObj.oElif(FileLocation.FileLineCol('file', 11, 1), 0, False, 'elif Condition 1')
        #print
        #print myObj
        myObj.oElse(FileLocation.FileLineCol('file', 20, 1), 0, True)
        #print
        #print myObj
        myObj.oEndif(FileLocation.FileLineCol('file', 30, 1), 0, True)
        self.assertTrue(myObj.isComplete)
        #print
        #print myObj
        self.assertEqual(
            """#if if Condition /* True "file" 1 0 */
#elif elif Condition 1 /* False "file" 11 0 */
#else /* True "file" 20 0 */
#endif /* True "file" 30 0 */""",
            str(myObj),
        )
    
    def test_05(self):
        """CppCondGraph.test_05() - #if/#if/#endif/#endif."""
        myObj = CppCond.CppCondGraph()
        myObj.oIf(FileLocation.FileLineCol('file', 1, 1), 0, True, 'if Condition 0')
        myObj.oIf(FileLocation.FileLineCol('file', 11, 1), 0, False, 'if Condition 1')
        myObj.oEndif(FileLocation.FileLineCol('file', 20, 1), 0, True)
        myObj.oEndif(FileLocation.FileLineCol('file', 30, 1), 0, True)
        #print
        #print myObj
        self.assertTrue(myObj.isComplete)
        self.assertEqual(
            """#if if Condition 0 /* True "file" 1 0 */
    #if if Condition 1 /* False "file" 11 0 */
    #endif /* True "file" 20 0 */
#endif /* True "file" 30 0 */""",
            str(myObj),
        )
    
    def test_06(self):
        """CppCondGraph.test_06() - #if/#ifdef/#ifndef/#endif/#endif/#endif."""
        myObj = CppCond.CppCondGraph()
        myObj.oIf(FileLocation.FileLineCol('file', 1, 1), 0, True, 'if Condition 0')
        self.assertFalse(myObj.isComplete)
        myObj.oIfdef(FileLocation.FileLineCol('file', 11, 1), 0, False, 'ifdef Condition 1')
        self.assertFalse(myObj.isComplete)
        myObj.oIfndef(FileLocation.FileLineCol('file', 111, 1), 0, False, 'ifndef Condition 2')
        self.assertFalse(myObj.isComplete)
        myObj.oEndif(FileLocation.FileLineCol('file', 200, 1), 0, True)
        self.assertFalse(myObj.isComplete)
        myObj.oEndif(FileLocation.FileLineCol('file', 201, 1), 0, True)
        self.assertFalse(myObj.isComplete)
        myObj.oEndif(FileLocation.FileLineCol('file', 201, 1), 0, True)
        #print
        #print myObj
        self.assertTrue(myObj.isComplete)
        self.assertEqual(
            """#if if Condition 0 /* True "file" 1 0 */
    #ifdef ifdef Condition 1 /* False "file" 11 0 */
        #ifndef ifndef Condition 2 /* False "file" 111 0 */
        #endif /* True "file" 200 0 */
    #endif /* True "file" 201 0 */
#endif /* True "file" 201 0 */""",
            str(myObj),
        )
    
    def test_10(self):
        """CppCondGraph.test_10() - #if/#else/#if/#endif/#endif."""
        #print
        myObj = CppCond.CppCondGraph()
        myObj.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'if Condition 0')
        self.assertFalse(myObj.isComplete)
        myObj.oElse(FileLocation.FileLineCol('file', 2, 1), 20, True)
        self.assertFalse(myObj.isComplete)
        #print
        #print myObj
        myObj.oIf(FileLocation.FileLineCol('file', 3, 1), 30, True, 'if Condition 0.0')
        self.assertFalse(myObj.isComplete)
        myObj.oEndif(FileLocation.FileLineCol('file', 4, 1), 40, True)
        #print
        #print myObj
        self.assertFalse(myObj.isComplete)
        myObj.oEndif(FileLocation.FileLineCol('file', 5, 1), 50, True)
        #print
        #print myObj
        self.assertTrue(myObj.isComplete)
        self.assertEqual(
            """#if if Condition 0 /* True "file" 1 10 */
#else /* True "file" 2 20 */
    #if if Condition 0.0 /* True "file" 3 30 */
    #endif /* True "file" 4 40 */
#endif /* True "file" 5 50 */""",
            str(myObj),
        )

    def test_11(self):
        """CppCondGraph.test_11() - #if/#else/#if/#if/#endif/#endif/#endif."""
        #print
        myObj = CppCond.CppCondGraph()
        myObj.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'if Condition 0')
        self.assertFalse(myObj.isComplete)
        myObj.oElse(FileLocation.FileLineCol('file', 2, 1), 20, True)
        self.assertFalse(myObj.isComplete)
        #print
        #print myObj
        myObj.oIf(FileLocation.FileLineCol('file', 3, 1), 30, True, 'if Condition 0.0')
        self.assertFalse(myObj.isComplete)
        myObj.oIf(FileLocation.FileLineCol('file', 3, 1), 30, True, 'if Condition 0.0.0')
        self.assertFalse(myObj.isComplete)
        myObj.oEndif(FileLocation.FileLineCol('file', 4, 1), 40, True)
        self.assertFalse(myObj.isComplete)
        myObj.oEndif(FileLocation.FileLineCol('file', 5, 1), 50, True)
        #print
        #print myObj
        self.assertFalse(myObj.isComplete)
        myObj.oEndif(FileLocation.FileLineCol('file', 6, 1), 60, True)
        #print
        #print myObj
        self.assertTrue(myObj.isComplete)
        self.assertEqual(
            """#if if Condition 0 /* True "file" 1 10 */
#else /* True "file" 2 20 */
    #if if Condition 0.0 /* True "file" 3 30 */
        #if if Condition 0.0.0 /* True "file" 3 30 */
        #endif /* True "file" 4 40 */
    #endif /* True "file" 5 50 */
#endif /* True "file" 6 60 */""",
            str(myObj),
        )

    def test_12(self):
        """CppCondGraph.test_12() - #if/#if/#elif/#endif/#endif."""
        myObj = CppCond.CppCondGraph()
        myObj.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'if Condition 0')
        myObj.oIf(FileLocation.FileLineCol('file', 11, 1), 110, False, 'if Condition 1')
        myObj.oElif(FileLocation.FileLineCol('file', 12, 1), 120, False, 'elif Condition 1')
        myObj.oEndif(FileLocation.FileLineCol('file', 20, 1), 200, True)
        myObj.oEndif(FileLocation.FileLineCol('file', 30, 1), 3000, True)
        #print
        #print myObj
        self.assertTrue(myObj.isComplete)
        self.assertEqual(
            """#if if Condition 0 /* True "file" 1 10 */
    #if if Condition 1 /* False "file" 11 110 */
    #elif elif Condition 1 /* False "file" 12 120 */
    #endif /* True "file" 20 200 */
#endif /* True "file" 30 3000 */""",
            str(myObj),
        )
    
    def test_12_00(self):
        """CppCondGraph.test_12_00() - #if/#endif."""
        myCcg = CppCond.CppCondGraph()
        myCcg.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'Condition 0')
        myCcg.oEndif(FileLocation.FileLineCol('file', 40, 1), 4000, True)
        #print
        #print myCcg
        self.assertTrue(myCcg.isComplete)
        self.assertEqual(
            """#if Condition 0 /* True "file" 1 10 */
#endif /* True "file" 40 4000 */""",
            str(myCcg),
        )

    def test_12_01(self):
        """CppCondGraph.test_12_01() - #if/#else/#endif."""
        myCcg = CppCond.CppCondGraph()
        myCcg.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'Condition 0')
        myCcg.oElse(FileLocation.FileLineCol('file', 20, 1), 2000, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 40, 1), 4000, True)
        #print
        #print myCcg
        self.assertTrue(myCcg.isComplete)
        self.assertEqual(
            """#if Condition 0 /* True "file" 1 10 */
#else /* True "file" 20 2000 */
#endif /* True "file" 40 4000 */""",
            str(myCcg),
        )

    def test_12_02(self):
        """CppCondGraph.test_12_02() - #if/#elif/#else/#endif."""
        myCcg = CppCond.CppCondGraph()
        myCcg.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'Condition 0')
        myCcg.oElif(FileLocation.FileLineCol('file', 10, 1), 1000, False, 'Condition 1')
        myCcg.oElse(FileLocation.FileLineCol('file', 20, 1), 2000, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 40, 1), 4000, True)
        #print
        #print myCcg
        self.assertTrue(myCcg.isComplete)
        self.assertEqual(
            """#if Condition 0 /* True "file" 1 10 */
#elif Condition 1 /* False "file" 10 1000 */
#else /* True "file" 20 2000 */
#endif /* True "file" 40 4000 */""",
            str(myCcg),
        )

    def test_12_03(self):
        """CppCondGraph.test_12_03() - #if/#if/#endif/#endif."""
        myCcg = CppCond.CppCondGraph()
        myCcg.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'Condition 0')
        myCcg.oIf(FileLocation.FileLineCol('file', 2, 1), 20, True, 'Condition 1')
        myCcg.oEndif(FileLocation.FileLineCol('file', 30, 1), 3000, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 40, 1), 4000, True)
        #print
        #print myCcg
        self.assertTrue(myCcg.isComplete)
        self.assertEqual(
            """#if Condition 0 /* True "file" 1 10 */
    #if Condition 1 /* True "file" 2 20 */
    #endif /* True "file" 30 3000 */
#endif /* True "file" 40 4000 */""",
            str(myCcg),
        )

    def test_12_04(self):
        """CppCondGraph.test_12_04() - #if/#elif/#endif."""
        myCcg = CppCond.CppCondGraph()
        myCcg.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'Condition 0')
        myCcg.oElif(FileLocation.FileLineCol('file', 2, 1), 20, True, 'Condition 1')
        myCcg.oEndif(FileLocation.FileLineCol('file', 30, 1), 3000, True)
        #print
        #print myCcg
        self.assertTrue(myCcg.isComplete)
        self.assertEqual(
            """#if Condition 0 /* True "file" 1 10 */
#elif Condition 1 /* True "file" 2 20 */
#endif /* True "file" 30 3000 */""",
            str(myCcg),
        )

    def test_12_05(self):
        """CppCondGraph.test_12_05() - #if/#if/#if/#endif/#endif/#endif."""
        myCcg = CppCond.CppCondGraph()
        myCcg.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'Condition 0')
        myCcg.oIf(FileLocation.FileLineCol('file', 2, 1), 20, True, 'Condition 1')
        myCcg.oIf(FileLocation.FileLineCol('file', 3, 1), 30, True, 'Condition 2')
        myCcg.oEndif(FileLocation.FileLineCol('file', 30, 1), 3000, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 200, 1), 20000, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 1000, 1), 100000, True)
        #print
        #print myCcg
        self.assertTrue(myCcg.isComplete)
        self.assertEqual(
            """#if Condition 0 /* True "file" 1 10 */
    #if Condition 1 /* True "file" 2 20 */
        #if Condition 2 /* True "file" 3 30 */
        #endif /* True "file" 30 3000 */
    #endif /* True "file" 200 20000 */
#endif /* True "file" 1000 100000 */""",
            str(myCcg),
        )

    def test_13(self):
        """CppCondGraph.test_13() - #if/#if/#elif/#elif/#endif/#endif."""
        myObj = CppCond.CppCondGraph()
        myObj.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'if Condition 0')
        myObj.oIf(FileLocation.FileLineCol('file', 11, 1), 110, False, 'if Condition 0.0')
        myObj.oElif(FileLocation.FileLineCol('file', 12, 1), 120, False, 'elif Condition 0.1')
        myObj.oIf(FileLocation.FileLineCol('file', 12, 1), 130, False, 'if Condition 0.1.0')
        myObj.oElif(FileLocation.FileLineCol('file', 14, 1), 140, False, 'elif Condition 0.1.1')
        myObj.oEndif(FileLocation.FileLineCol('file', 20, 1), 200, True)
        myObj.oEndif(FileLocation.FileLineCol('file', 30, 1), 3000, True)
        myObj.oEndif(FileLocation.FileLineCol('file', 40, 1), 4000, True)
        #print
        #print myObj
        self.assertTrue(myObj.isComplete)
        self.assertEqual(
            """#if if Condition 0 /* True "file" 1 10 */
    #if if Condition 0.0 /* False "file" 11 110 */
    #elif elif Condition 0.1 /* False "file" 12 120 */
        #if if Condition 0.1.0 /* False "file" 12 130 */
        #elif elif Condition 0.1.1 /* False "file" 14 140 */
        #endif /* True "file" 20 200 */
    #endif /* True "file" 30 3000 */
#endif /* True "file" 40 4000 */""",
            str(myObj),
        )

    def test_13_00(self):
        """CppCondGraph.test_13_00() - #if/#elif/#if/#elif/#endif/#endif."""
        myCcg = CppCond.CppCondGraph()
        myCcg.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'Condition 0')
        myCcg.oElif(FileLocation.FileLineCol('file', 12, 1), 120, False, 'Condition 0.1')
        myCcg.oIf(FileLocation.FileLineCol('file', 12, 1), 130, False, 'Condition 0.1.0')
        myCcg.oElif(FileLocation.FileLineCol('file', 14, 1), 140, False, 'Condition 0.1.1')
        myCcg.oEndif(FileLocation.FileLineCol('file', 20, 1), 200, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 30, 1), 300, True)
        self.assertTrue(myCcg.isComplete)
        #print
        #print myCcg
        self.assertEqual(
            """#if Condition 0 /* True "file" 1 10 */
#elif Condition 0.1 /* False "file" 12 120 */
    #if Condition 0.1.0 /* False "file" 12 130 */
    #elif Condition 0.1.1 /* False "file" 14 140 */
    #endif /* True "file" 20 200 */
#endif /* True "file" 30 300 */""",
            str(myCcg),
        )

    def test_14(self):
        """CppCondGraph.test_14() - #if/#if/#elif/#if/#elif/#endif/#endif/#endif."""
        myCcg = CppCond.CppCondGraph()
        myCcg.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'Condition 0')
        myCcg.oIf(FileLocation.FileLineCol('file', 11, 1), 110, False, 'Condition 0.0')
        myCcg.oElif(FileLocation.FileLineCol('file', 12, 1), 120, False, 'Condition 0.1')
        myCcg.oIf(FileLocation.FileLineCol('file', 12, 1), 130, False, 'Condition 0.1.0')
        myCcg.oElif(FileLocation.FileLineCol('file', 14, 1), 140, False, 'Condition 0.1.1')
        myCcg.oEndif(FileLocation.FileLineCol('file', 20, 1), 200, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 30, 1), 3000, True)
        #print
        #print myCcg
        myCcg.oEndif(FileLocation.FileLineCol('file', 40, 1), 4000, True)
        #print
        #print myCcg
        self.assertTrue(myCcg.isComplete)
        self.assertEqual(
            """#if Condition 0 /* True "file" 1 10 */
    #if Condition 0.0 /* False "file" 11 110 */
    #elif Condition 0.1 /* False "file" 12 120 */
        #if Condition 0.1.0 /* False "file" 12 130 */
        #elif Condition 0.1.1 /* False "file" 14 140 */
        #endif /* True "file" 20 200 */
    #endif /* True "file" 30 3000 */
#endif /* True "file" 40 4000 */""",
            str(myCcg),
        )

    def test_14_00(self):
        """CppCondGraph.test_14_00() - #if/#if/#if/#endif/#endif/#endif."""
        myCcg = CppCond.CppCondGraph()
        myCcg.oIf(FileLocation.FileLineCol('file', 1, 1), 10, True, 'Condition 0')
        myCcg.oIf(FileLocation.FileLineCol('file', 11, 1), 110, False, 'Condition 0.0')
        myCcg.oIf(FileLocation.FileLineCol('file', 12, 1), 120, False, 'Condition 0.1')
        myCcg.oEndif(FileLocation.FileLineCol('file', 20, 1), 200, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 30, 1), 3000, True)
        #print
        #print myCcg
        myCcg.oEndif(FileLocation.FileLineCol('file', 40, 1), 4000, True)
        #print
        #print myCcg
        self.assertTrue(myCcg.isComplete)
        self.assertEqual(
            """#if Condition 0 /* True "file" 1 10 */
    #if Condition 0.0 /* False "file" 11 110 */
        #if Condition 0.1 /* False "file" 12 120 */
        #endif /* True "file" 20 200 */
    #endif /* True "file" 30 3000 */
#endif /* True "file" 40 4000 */""",
            str(myCcg),
        )

    def test_50(self):
        """CppCondGraph.test_50() - Large combination of preprocessing directives."""
        myObj = CppCond.CppCondGraph()
        # 0
        myObj.oIf(FileLocation.FileLineCol('file', 10, 1), 0, True, '0')
        # 1
        myObj.oIfdef(FileLocation.FileLineCol('file', 20, 1), 0, False, '0.0')
        # 2
        myObj.oIfndef(FileLocation.FileLineCol('file', 30, 1), 0, False, '0.0.0')
        myObj.oElif(FileLocation.FileLineCol('file', 40, 1), 0, False, '0.0.1')
        myObj.oElif(FileLocation.FileLineCol('file', 50, 1), 0, False, '0.0.2')
        myObj.oElse(FileLocation.FileLineCol('file', 60, 1), 0, True)
        # 3
        myObj.oIf(FileLocation.FileLineCol('file', 70, 1), 0, True, '0.0.3')
        myObj.oElif(FileLocation.FileLineCol('file', 80, 1), 0, False, '0.0.4')
        myObj.oElse(FileLocation.FileLineCol('file', 90, 1), 0, True)
        myObj.oEndif(FileLocation.FileLineCol('file', 100, 1), 0, True)
        # 2
        myObj.oEndif(FileLocation.FileLineCol('file', 201, 1), 0, True)
        # 1
        myObj.oEndif(FileLocation.FileLineCol('file', 301, 1), 0, True)
        # 0
        myObj.oEndif(FileLocation.FileLineCol('file', 401, 1), 0, True)
        #print
        #print myObj
        self.assertTrue(myObj.isComplete)
        self.assertEqual(
            """#if 0 /* True "file" 10 0 */
    #ifdef 0.0 /* False "file" 20 0 */
        #ifndef 0.0.0 /* False "file" 30 0 */
        #elif 0.0.1 /* False "file" 40 0 */
        #elif 0.0.2 /* False "file" 50 0 */
        #else /* True "file" 60 0 */
            #if 0.0.3 /* True "file" 70 0 */
            #elif 0.0.4 /* False "file" 80 0 */
            #else /* True "file" 90 0 */
            #endif /* True "file" 100 0 */
        #endif /* True "file" 201 0 */
    #endif /* True "file" 301 0 */
#endif /* True "file" 401 0 */""",
            str(myObj),
        )
    
    def test_51(self):
        """CppCondGraph.test_51() - Large combination of preprocessing directives."""
        #assert(0)
        myCcg = CppCond.CppCondGraph()
        # 0
        myCcg.oIf(FileLocation.FileLineCol('file', 10, 1), 0, True, '0')
        # 1
        myCcg.oIf(FileLocation.FileLineCol('file', 20, 1), 0, False, '0.0')
        # 2
        myCcg.oIf(FileLocation.FileLineCol('file', 30, 1), 0, False, '0.0.0')
        myCcg.oElif(FileLocation.FileLineCol('file', 40, 1), 0, False, '0.0.1')
        myCcg.oElif(FileLocation.FileLineCol('file', 50, 1), 0, False, '0.0.2')
        myCcg.oElse(FileLocation.FileLineCol('file', 90, 1), 0, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 100, 1), 0, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 200, 1), 0, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 300, 1), 0, True)
        #print
        #print myCcg
        self.assertTrue(myCcg.isComplete)
        self.assertEqual("""#if 0 /* True "file" 10 0 */
    #if 0.0 /* False "file" 20 0 */
        #if 0.0.0 /* False "file" 30 0 */
        #elif 0.0.1 /* False "file" 40 0 */
        #elif 0.0.2 /* False "file" 50 0 */
        #else /* True "file" 90 0 */
        #endif /* True "file" 100 0 */
    #endif /* True "file" 200 0 */
#endif /* True "file" 300 0 */""", str(myCcg))
    
    def test_52(self):
        """CppCondGraph.test_52() - Large combination of preprocessing directives."""
        myCcg = CppCond.CppCondGraph()
        # 0
        myCcg.oIf(FileLocation.FileLineCol('file', 10, 1), 0, True, '0')
        myCcg.oElif(FileLocation.FileLineCol('file', 40, 1), 0, False, '0.0.1')
        myCcg.oElif(FileLocation.FileLineCol('file', 50, 1), 0, False, '0.0.2')
        myCcg.oElse(FileLocation.FileLineCol('file', 90, 1), 0, True)
        myCcg.oEndif(FileLocation.FileLineCol('file', 300, 1), 0, True)
        #print
        #print myCcg
        self.assertTrue(myCcg.isComplete)
        self.assertEqual("""#if 0 /* True "file" 10 0 */
#elif 0.0.1 /* False "file" 40 0 */
#elif 0.0.2 /* False "file" 50 0 */
#else /* True "file" 90 0 */
#endif /* True "file" 300 0 */""", str(myCcg))

class TestCppCondGraphFail(unittest.TestCase):
    """Tests the CppCondGraph failure conditions."""
    def test_00(self):
        """TestCppCondGraphFail.test_00() - Simple construction."""
        myCcg = CppCond.CppCondGraph()
        self.assertTrue(myCcg.isComplete)
        #print
        #print myCcg
        self.assertEqual("""""", str(myCcg))
    
    def test_01(self):
        """TestCppCondGraphFail.test_01() - Fails when no #if but #elif."""
        myCcg = CppCond.CppCondGraph()
        self.assertTrue(myCcg.isComplete)
        try:
            myCcg.oElif(False, 'elif Condition 1', FileLocation.FileLineCol('file', 11, 1), 0)
            self.fail('ifSection fails to raise ExceptionCppCondGraph when #elif but no #if.')
        except CppCond.ExceptionCppCondGraph:
            pass
    
    def test_02(self):
        """TestCppCondGraphFail.test_02() - Fails when no #if but #else."""
        myCcg = CppCond.CppCondGraph()
        self.assertTrue(myCcg.isComplete)
        try:
            myCcg.oElse(FileLocation.FileLineCol('file', 11, 1), 0, True)
            self.fail('ifSection fails to raise ExceptionCppCondGraph when #else but no #if.')
        except CppCond.ExceptionCppCondGraph:
            pass
    
    def test_03(self):
        """TestCppCondGraphFail.test_03() - Fails when no #if but #endif."""
        myCcg = CppCond.CppCondGraph()
        self.assertTrue(myCcg.isComplete)
        try:
            myCcg.oEndif(FileLocation.FileLineCol('file', 11, 1), 0, True)
            self.fail('ifSection fails to raise ExceptionCppCondGraph when #endif but no #if.')
        except CppCond.ExceptionCppCondGraph:
            pass
    
    def test_04(self):
        """TestCppCondGraphFail.test_04() - Fails on #if/#endif/#endif."""
        myCcg = CppCond.CppCondGraph()
        self.assertTrue(myCcg.isComplete)
        myCcg.oIf(FileLocation.FileLineCol('file', 11, 1), 0, True, '0')
        myCcg.oEndif(FileLocation.FileLineCol('file', 12, 1), 0, True)
        try:
            myCcg.oEndif(FileLocation.FileLineCol('file', 13, 1), 0, True)
            self.fail('ifSection fails to raise ExceptionCppCondGraph when #endif but no #if.')
        except CppCond.ExceptionCppCondGraph:
            pass
    
    def test_05(self):
        """TestCppCondGraphFail.test_05() - Fails on #if/#else/#elif."""
        myCcg = CppCond.CppCondGraph()
        self.assertTrue(myCcg.isComplete)
        myCcg.oIf(FileLocation.FileLineCol('file', 11, 1), 0, True, '0')
        myCcg.oElse(FileLocation.FileLineCol('file', 12, 1), 0, True)
        try:
            myCcg.oElif(FileLocation.FileLineCol('file', 13, 1), 0, True, '1')
            self.fail('ifSection fails to raise ExceptionCppCondGraph.')
        except CppCond.ExceptionCppCondGraph:
            pass
    
    def test_06(self):
        """TestCppCondGraphFail.test_06() - Fails on #if/#else/#else."""
        myCcg = CppCond.CppCondGraph()
        self.assertTrue(myCcg.isComplete)
        myCcg.oIf(FileLocation.FileLineCol('file', 11, 1), 0, True, '0')
        myCcg.oElse(FileLocation.FileLineCol('file', 12, 1), 0, True)
        try:
            myCcg.oElse(FileLocation.FileLineCol('file', 13, 1), 0, True)
            self.fail('ifSection fails to raise ExceptionCppCondGraph.')
        except CppCond.ExceptionCppCondGraph:
            pass
    
class TestCcgVisitor(CppCond.CppCondGraphVisitorBase):
    """Test class for a CppCondGraph visitor object."""
    def __init__(self):
        super(TestCcgVisitor, self).__init__()
        self._lineS = []
        
    def __str__(self):
        return '\n'.join(self._lineS)
    
    def visitPre(self, theCcgNode, theDepth):
        """Pre-traversal call with a CppCondGraphNode and the integer depth in
        the tree."""
        if theCcgNode.constExpr is not None:
            self._lineS.append('%s->#%s %s' \
                    % (
                        ' '*theDepth,
                        theCcgNode.cppDirective,
                        theCcgNode.constExpr,
                    )
                )
        else:
            self._lineS.append('%s->#%s' \
                            % (' '*theDepth, theCcgNode.cppDirective))
        
    def visitPost(self, theCcgNode, theDepth):
        """Post-traversal call with a CppCondGraphNode and the integer depth in
        the tree."""
        self._lineS.append('%s<-#%s' % (' '*theDepth, theCcgNode.cppDirective))

class TestCppCondGraphVisitor(unittest.TestCase):
    """Tests the CppCondGraph visitor."""
    def test_00(self):
        """TestCppCondGraphVisitor.test_00() - Test a visitor object."""
        myCcg = CppCond.CppCondGraph()
        # 0
        myCcg.oIf(FileLocation.FileLineCol('file', 10, 1), 0, True, '0')
        # 1
        myCcg.oIfdef(FileLocation.FileLineCol('file', 20, 1), 0, False, '0.0')
        # 2
        myCcg.oIfndef(FileLocation.FileLineCol('file', 30, 1), 0, False, '0.0.0')
        myCcg.oElif(FileLocation.FileLineCol('file', 40, 1), 0, False, '0.0.1')
        myCcg.oElif(FileLocation.FileLineCol('file', 50, 1), 0, False, '0.0.2')
        myCcg.oElse(FileLocation.FileLineCol('file', 60, 1), 0, True)
        # 3
        myCcg.oIf(FileLocation.FileLineCol('file', 70, 1), 0, True, '0.0.3')
        myCcg.oElif(FileLocation.FileLineCol('file', 80, 1), 0, False, '0.0.4')
        myCcg.oElse(FileLocation.FileLineCol('file', 90, 1), 0, False)
        myCcg.oEndif(FileLocation.FileLineCol('file', 100, 1), 0, True)
        # 2
        myCcg.oEndif(FileLocation.FileLineCol('file', 201, 1), 0, False)
        # 1
        myCcg.oEndif(FileLocation.FileLineCol('file', 301, 1), 0, True)
        # 0
        myCcg.oEndif(FileLocation.FileLineCol('file', 401, 1), 0, False)
        #print
        #print myCcg
        self.assertTrue(myCcg.isComplete)
        self.assertEqual(
            """#if 0 /* True "file" 10 0 */
    #ifdef 0.0 /* False "file" 20 0 */
        #ifndef 0.0.0 /* False "file" 30 0 */
        #elif 0.0.1 /* False "file" 40 0 */
        #elif 0.0.2 /* False "file" 50 0 */
        #else /* True "file" 60 0 */
            #if 0.0.3 /* True "file" 70 0 */
            #elif 0.0.4 /* False "file" 80 0 */
            #else /* False "file" 90 0 */
            #endif /* True "file" 100 0 */
        #endif /* False "file" 201 0 */
    #endif /* True "file" 301 0 */
#endif /* False "file" 401 0 */""",
            str(myCcg),
        )
        myV = TestCcgVisitor()
        myCcg.visit(myV)
        #print
        #print myV
        self.assertEqual("""->#if 0
 ->#ifdef 0.0
  ->#ifndef 0.0.0
  <-#ifndef
  ->#elif 0.0.1
  <-#elif
  ->#elif 0.0.2
  <-#elif
  ->#else
   ->#if 0.0.3
   <-#if
   ->#elif 0.0.4
   <-#elif
   ->#else
   <-#else
   ->#endif
   <-#endif
  <-#else
  ->#endif
  <-#endif
 <-#ifdef
 ->#endif
 <-#endif
<-#if
->#endif
<-#endif""", str(myV))
        
class Special(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConditionalState))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppCondLowLevel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppCondConstExpr))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppCondIfElifElse))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppCondIfElifElseMultipleDepth))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppCond))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppCondGraph))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppCondGraphFail))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppCondGraphVisitor))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestCppCond.py - A module that tests PpToken module.
Usage:
python PpToken.py [-lh --help]

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
    print('TestCppCond.py script version "%s", dated %s' % (__version__, __date__))
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
