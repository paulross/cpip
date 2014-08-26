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

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import sys
import os
import unittest
import time
import logging

from cpip.core import PpToken

#######################################
# Section: Unit tests
########################################
class TestGlobals(unittest.TestCase):
    """Test the globals."""

    def testGlobals(self):
        """Test globals NAME_ENUM, ENUM_NAME and LEX_PPTOKEN_TYPE_ENUM_RANGE."""
        self.assertEqual(len(PpToken.LEX_PPTOKEN_TYPE_ENUM_RANGE),
                         len(PpToken.NAME_ENUM))
        self.assertEqual(len(PpToken.LEX_PPTOKEN_TYPE_ENUM_RANGE),
                         len(PpToken.ENUM_NAME))
        for i in PpToken.LEX_PPTOKEN_TYPE_ENUM_RANGE:
            self.assertEqual(True, i in PpToken.ENUM_NAME)
            self.assertEqual(True,
                             PpToken.ENUM_NAME[i] in PpToken.NAME_ENUM
                             )
            self.assertEqual(i,
                             PpToken.NAME_ENUM[PpToken.ENUM_NAME[i]])

class TestPpTokenCtor(unittest.TestCase):
    """Tests PpToken construction."""

    def testInit_00(self):
        """PpToken() ctor good: PpToken('spam', 'identifier')"""
        myObj = PpToken.PpToken('spam', 'identifier')
        self.assertEqual('spam', myObj.t)
        self.assertEqual('identifier', myObj.tt)
        self.assertEqual(True, myObj.canReplace)
        self.assertEqual(False, myObj.prevWs)
        self.assertEqual('"spam"', '%r' % myObj)
        self.assertEqual(
            ('spam', PpToken.NAME_ENUM['identifier']),
            myObj.tokEnumToktype,
            )
        self.assertEqual(
            ('spam', 'identifier'),
            myObj.tokToktype,
            )

    def testInit_01(self):
        """PpToken() ctor good: PpToken('spam', 1)"""
        myObj = PpToken.PpToken('spam', 1)
        self.assertEqual('spam', myObj.t)
        self.assertEqual('identifier', myObj.tt)
        self.assertEqual(True, myObj.canReplace)
        self.assertEqual(False, myObj.prevWs)

    def testInit_02_00(self):
        """PpToken() ctor good: PpToken('"spam"', 0)"""
        myObj = PpToken.PpToken('"spam"', 0)
        self.assertEqual('"spam"', myObj.t)
        self.assertEqual('header-name', myObj.tt)
        self.assertEqual(False, myObj.canReplace)
        self.assertNotEqual(True, myObj.canReplace)
        self.assertEqual(False, myObj.prevWs)

    def testInit_02_01(self):
        """PpToken() ctor good: PpToken('<spam>', 0)"""
        myObj = PpToken.PpToken('<spam>', 0)
        self.assertEqual('<spam>', myObj.t)
        self.assertEqual('header-name', myObj.tt)
        self.assertEqual(False, myObj.canReplace)
        self.assertNotEqual(True, myObj.canReplace)
        self.assertEqual(False, myObj.prevWs)

    def testInit_03(self):
        """PpToken() ctor good: with non-identifier types (ints)."""
        for i in PpToken.LEX_PPTOKEN_TYPE_ENUM_RANGE:
            if PpToken.ENUM_NAME[i] != 'identifier':
                myObj = PpToken.PpToken('', i)
                self.assertEqual('', myObj.t)
                self.assertEqual(PpToken.ENUM_NAME[i], myObj.tt)
                self.assertEqual(False, myObj.canReplace)
                self.assertNotEqual(True, myObj.canReplace)
                self.assertEqual(False, myObj.prevWs)
                self.assertRaises(
                    PpToken.ExceptionCpipTokenIllegalOperation,
                    myObj.setReplace,
                    True
                    )

    def testInit_04(self):
        """PpToken() ctor good: with non-identifier types (strings)."""
        for i in PpToken.LEX_PPTOKEN_TYPE_ENUM_RANGE:
            if PpToken.ENUM_NAME[i] != 'identifier':
                myObj = PpToken.PpToken('', PpToken.ENUM_NAME[i])
                self.assertEqual('', myObj.t)
                self.assertEqual(PpToken.ENUM_NAME[i], myObj.tt)
                self.assertEqual(False, myObj.canReplace)
                self.assertNotEqual(True, myObj.canReplace)
                self.assertEqual(False, myObj.prevWs)
                self.assertRaises(
                    PpToken.ExceptionCpipTokenIllegalOperation,
                    myObj.setReplace,
                    True
                    )

    def testInit_10(self):
        """PpToken() ctor bad: PpToken('spam', -1)"""
        self.assertRaises(
            PpToken.ExceptionCpipTokenUnknownType,
            PpToken.PpToken,
            'spam',
            -1
            )

    def testInit_11(self):
        """PpToken() ctor bad: PpToken('spam', 'rubbish')"""
        self.assertRaises(
            PpToken.ExceptionCpipTokenUnknownType,
            PpToken.PpToken,
            'spam',
            'rubbish'
            )

class TestPpTokenFlags(unittest.TestCase):
    """Tests PpToken construction."""

    def testSetReplace_00(self):
        """PpToken() canReplace success: for ('spam', 'identifier')"""
        myObj = PpToken.PpToken('spam', 'identifier')
        self.assertEqual('spam', myObj.t)
        self.assertEqual('identifier', myObj.tt)
        self.assertEqual(True, myObj.canReplace)
        self.assertEqual(False, myObj.prevWs)
        myObj.canReplace = False
        self.assertEqual(False, myObj.canReplace)

    def testSetReplace_01(self):
        """PpToken() canReplace failure: for ('spam', 'identifier')"""
        myObj = PpToken.PpToken('spam', 'identifier')
        self.assertEqual('spam', myObj.t)
        self.assertEqual('identifier', myObj.tt)
        self.assertEqual(True, myObj.canReplace)
        self.assertEqual(False, myObj.prevWs)
        myObj.canReplace = False
        self.assertEqual(False, myObj.canReplace)
        self.assertRaises(
            PpToken.ExceptionCpipTokenReopenForExpansion,
            myObj.setReplace,
            True)
        try:
            myObj.canReplace = True
        except PpToken.ExceptionCpipTokenReopenForExpansion:
            pass
        else:
            self.assertEqual(0, 1)

    def testPrevWs_00(self):
        """PpToken() can set/clear prevWs for ('spam', 'identifier')"""
        myObj = PpToken.PpToken('spam', 'identifier')
        self.assertEqual('spam', myObj.t)
        self.assertEqual('identifier', myObj.tt)
        self.assertEqual(True, myObj.canReplace)
        self.assertEqual(False, myObj.prevWs)
        myObj.prevWs = True
        self.assertEqual(True, myObj.prevWs)
        myObj.prevWs = False
        self.assertEqual(False, myObj.prevWs)

class TestPpTokenCmp(unittest.TestCase):
    """Tests PpToken __cmp__()."""

    def testCmp_00(self):
        """PpToken() test __cmp__() equivelent."""
        myObj = PpToken.PpToken('spam', 'identifier')
        myOther = PpToken.PpToken('spam', 'identifier')
        self.assertEqual(myObj, myOther)

    def testCmp_01(self):
        """PpToken() test __cmp__() different tokens."""
        myObj = PpToken.PpToken('spam', 'identifier')
        myOther = PpToken.PpToken('eggs', 'identifier')
        self.assertNotEqual(myObj, myOther)

    def testCmp_02(self):
        """PpToken() test __cmp__() different token types."""
        myObj = PpToken.PpToken('spam', 'identifier')
        myOther = PpToken.PpToken('spam', 'pp-number')
        self.assertNotEqual(myObj, myOther)

    def testCmp_03(self):
        """PpToken() test __cmp__() zero after canReplace = False."""
        myObj = PpToken.PpToken('spam', 'identifier')
        myOther = PpToken.PpToken('spam', 'identifier')
        myObj.canReplace = False
        self.assertEqual(myObj, myOther)

class TestPpTokenWs(unittest.TestCase):
    """Tests PpToken whitespace."""

    def testWs_00(self):
        """PpToken() test not whitespace with isWs()"""
        myObj = PpToken.PpToken('spam', 'identifier')
        self.assertEqual('spam', myObj.t)
        self.assertEqual('identifier', myObj.tt)
        self.assertEqual(True, myObj.canReplace)
        self.assertEqual(False, myObj.prevWs)
        self.assertEqual(False, myObj.isWs())

    def testWs_01(self):
        """PpToken() test is whitespace with isWs()"""
        myObj = PpToken.PpToken(' ', 'whitespace')
        self.assertEqual(' ', myObj.t)
        self.assertEqual('whitespace', myObj.tt)
        self.assertEqual(False, myObj.canReplace)
        self.assertEqual(False, myObj.prevWs)
        self.assertEqual(True, myObj.isWs())

class TestPpTokenMerge(unittest.TestCase):
    """Tests PpToken whitespace."""

    def testMerge_00(self):
        """PpToken() test merge() succeeds with whitespace."""
        myObj_00 = PpToken.PpToken(' ', 'whitespace')
        self.assertEqual(' ', myObj_00.t)
        self.assertEqual('whitespace', myObj_00.tt)
        self.assertEqual(False, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(True, myObj_00.isWs())
        myObj_01 = PpToken.PpToken('   ', 'whitespace')
        self.assertEqual('   ', myObj_01.t)
        self.assertEqual('whitespace', myObj_01.tt)
        self.assertEqual(False, myObj_01.canReplace)
        self.assertEqual(False, myObj_01.prevWs)
        self.assertEqual(True, myObj_01.isWs())
        myObj_00.merge(myObj_01)
        self.assertEqual('    ', myObj_00.t)
        self.assertEqual('whitespace', myObj_00.tt)
        self.assertEqual(False, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(True, myObj_00.isWs())

    def testMerge_01(self):
        """PpToken() test merge() type='concat' with ws/identifier."""
        myObj_00 = PpToken.PpToken(' ', 'whitespace')
        self.assertEqual(' ', myObj_00.t)
        self.assertEqual('whitespace', myObj_00.tt)
        self.assertEqual(False, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(True, myObj_00.isWs())
        myObj_01 = PpToken.PpToken('f', 'identifier')
        self.assertEqual('f', myObj_01.t)
        self.assertEqual('identifier', myObj_01.tt)
        self.assertEqual(True, myObj_01.canReplace)
        self.assertEqual(False, myObj_01.prevWs)
        self.assertEqual(False, myObj_01.isWs())
        #self.assertRaises(
        #    PpToken.ExceptionCpipTokenIllegalMerge,
        #    myObj_00.merge,
        #    myObj_01)
        #self.assertRaises(
        #    PpToken.ExceptionCpipTokenIllegalMerge,
        #    myObj_01.merge,
        #    myObj_00)
        myObj_00.merge(myObj_01)
        self.assertEqual(' f', myObj_00.t)
        self.assertEqual('concat', myObj_00.tt)
        self.assertEqual(False, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(False, myObj_00.isWs())

    def testMerge_02(self):
        """PpToken() test merge() succeeds with identifier/identifier."""
        myObj_00 = PpToken.PpToken('f', 'identifier')
        self.assertEqual('f', myObj_00.t)
        self.assertEqual('identifier', myObj_00.tt)
        self.assertEqual(True, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(False, myObj_00.isWs())
        myObj_01 = PpToken.PpToken('g', 'identifier')
        self.assertEqual('g', myObj_01.t)
        self.assertEqual('identifier', myObj_01.tt)
        self.assertEqual(True, myObj_01.canReplace)
        self.assertEqual(False, myObj_01.prevWs)
        self.assertEqual(False, myObj_01.isWs())
        myObj_00.merge(myObj_01)
        self.assertEqual('fg', myObj_00.t)
        self.assertEqual('identifier', myObj_00.tt)
        self.assertEqual(True, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(False, myObj_00.isWs())

class TestPpTokenReplaceWhitespace(unittest.TestCase):
    """Tests PpToken whitespace."""

    def test_replaceNewLine_00(self):
        """PpToken() test replaceNewLine() succeeds."""
        myObj_00 = PpToken.PpToken('\n\n', 'whitespace')
        self.assertEqual('\n\n', myObj_00.t)
        self.assertEqual('whitespace', myObj_00.tt)
        self.assertEqual(False, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(True, myObj_00.isWs())
        myObj_00.replaceNewLine()
        self.assertEqual('  ', myObj_00.t)
        self.assertEqual('whitespace', myObj_00.tt)
        self.assertEqual(False, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(True, myObj_00.isWs())

    def test_replaceNewLine_01(self):
        """PpToken() test replaceNewLine() fails."""
        myObj_00 = PpToken.PpToken('f', 'identifier')
        self.assertEqual('f', myObj_00.t)
        self.assertEqual('identifier', myObj_00.tt)
        self.assertEqual(True, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(False, myObj_00.isWs())
        self.assertRaises(
            PpToken.ExceptionCpipTokenIllegalOperation,
            myObj_00.replaceNewLine
            )

    def test_shrinkWs_00(self):
        """PpToken() test shrinkWs() succeeds."""
        myObj_00 = PpToken.PpToken('    \n \n  ', 'whitespace')
        self.assertEqual('    \n \n  ', myObj_00.t)
        self.assertEqual('whitespace', myObj_00.tt)
        self.assertEqual(False, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(True, myObj_00.isWs())
        myObj_00.shrinkWs()
        self.assertEqual(myObj_00.SINGLE_SPACE, myObj_00.t)
        self.assertEqual('whitespace', myObj_00.tt)
        self.assertEqual(False, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(True, myObj_00.isWs())

    def test_shrinkWs_01(self):
        """PpToken() test shrinkWs() fails."""
        myObj_00 = PpToken.PpToken('f', 'identifier')
        self.assertEqual('f', myObj_00.t)
        self.assertEqual('identifier', myObj_00.tt)
        self.assertEqual(True, myObj_00.canReplace)
        self.assertEqual(False, myObj_00.prevWs)
        self.assertEqual(False, myObj_00.isWs())
        self.assertRaises(
            PpToken.ExceptionCpipTokenIllegalOperation,
            myObj_00.shrinkWs
            )

class TestPpTokenTokensStr(unittest.TestCase):
    """Tests tokensStr() function."""

    def test_tokensStr_00(self):
        """global function tokensStr() test single token."""
        myTokS = [PpToken.PpToken('f', 'identifier'),]
        self.assertEqual('f', PpToken.tokensStr(myTokS))

    def test_tokensStr_01(self):
        """global function tokensStr() test multiple tokens."""
        myTokS = [
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken('g', 'identifier'),
            ]
        self.assertEqual('fg', PpToken.tokensStr(myTokS))

    def test_tokensStr_02(self):
        """global function tokensStr() test single token, long form."""
        myTokS = [PpToken.PpToken('f', 'identifier'),]
        self.assertEqual(
            #'"f", identifier, True, False, False',
            'PpToken(t="f", tt=identifier, line=True, prev=False, ?=False)',
            PpToken.tokensStr(myTokS, shortForm=False)
            )

    def test_tokensStr_03(self):
        """global function tokensStr() test multiple tokens, long form."""
        myTokS = [
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken('g', 'identifier'),
            ]
        self.assertEqual(
            #'"f", identifier, True, False, False | "g", identifier, True, False, False',
            'PpToken(t="f", tt=identifier, line=True, prev=False, ?=False) | PpToken(t="g", tt=identifier, line=True, prev=False, ?=False)',
            PpToken.tokensStr(myTokS, shortForm=False)
            )

class TestPpTokenIsCond(unittest.TestCase):
    """Tests conditional compilation flag."""

    def test_isCond_00(self):
        """isCond is False on construction."""
        myTok = PpToken.PpToken('f', 'identifier')
        self.assertEqual(False, myTok.isCond)

    def test_isCond_01(self):
        """isCond can be set to True."""
        myTok = PpToken.PpToken('f', 'identifier')
        self.assertEqual(False, myTok.isCond)
        myTok.setIsCond()
        self.assertEqual(True, myTok.isCond)

    def test_isCond_02(self):
        """isCond can be not be set to False."""
        myTok = PpToken.PpToken('f', 'identifier')
        self.assertEqual(False, myTok.isCond)
        myTok.setIsCond()
        self.assertEqual(True, myTok.isCond)
        try:
            myTok.isCond = False
            self.fail('No AttributeError raised.')
        except AttributeError:
            pass

class TestPpTokenLineColumn(unittest.TestCase):
    """Tests line number and column number."""

    def test_00(self):
        """TestPpTokenLineColumn.test_00()"""
        myTok = PpToken.PpToken('f', 'identifier', 1, 2)
        self.assertEqual(1, myTok.lineNum)
        self.assertEqual(2, myTok.colNum)
        
class TestPpTokenEvalConstExpr(unittest.TestCase):
    """Tests line number and column number."""

    def test_00(self):
        """TestPpTokenEvalConstExpr.test_00(): Floating point literals."""
        myTok = PpToken.PpToken('1.23e4', 'pp-number')
        self.assertEqual('1.23e4', myTok.evalConstExpr())
        myTok = PpToken.PpToken('1.23e4f', 'pp-number')
        self.assertEqual('1.23e4', myTok.evalConstExpr())
        myTok = PpToken.PpToken('1.23e4F', 'pp-number')
        self.assertEqual('1.23e4', myTok.evalConstExpr())
        myTok = PpToken.PpToken('1.23e4l', 'pp-number')
        self.assertEqual('1.23e4', myTok.evalConstExpr())
        myTok = PpToken.PpToken('1.23e4L', 'pp-number')
        self.assertEqual('1.23e4', myTok.evalConstExpr())
        
    def test_01(self):
        """TestPpTokenEvalConstExpr.test_01(): Integer literals."""
        myTok = PpToken.PpToken('', 'pp-number')
        self.assertEqual('', myTok.evalConstExpr())
        myTok = PpToken.PpToken('1', 'pp-number')
        self.assertEqual('1', myTok.evalConstExpr())
        myTok = PpToken.PpToken('12', 'pp-number')
        self.assertEqual('12', myTok.evalConstExpr())
        myTok = PpToken.PpToken('123', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())

    def test_02(self):
        """TestPpTokenEvalConstExpr.test_02(): Integer literals, long."""
        myTok = PpToken.PpToken('123l', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())
        myTok = PpToken.PpToken('123L', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())
        
    def test_03(self):
        """TestPpTokenEvalConstExpr.test_03(): Integer literals, unsigned."""
        myTok = PpToken.PpToken('123u', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())
        myTok = PpToken.PpToken('123U', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())

    def test_04(self):
        """TestPpTokenEvalConstExpr.test_04(): Integer literals, unsigned/long."""
        myTok = PpToken.PpToken('123ul', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())
        myTok = PpToken.PpToken('123Ul', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())
        myTok = PpToken.PpToken('123uL', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())
        myTok = PpToken.PpToken('123UL', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())
        myTok = PpToken.PpToken('123lu', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())
        myTok = PpToken.PpToken('123lU', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())
        myTok = PpToken.PpToken('123Lu', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())
        myTok = PpToken.PpToken('123LU', 'pp-number')
        self.assertEqual('123', myTok.evalConstExpr())

    def test_05(self):
        """TestPpTokenEvalConstExpr.test_05(): Integer literals, unsigned/long, short strings."""
        myTok = PpToken.PpToken('1ul', 'pp-number')
        self.assertEqual('1', myTok.evalConstExpr())
        myTok = PpToken.PpToken('1U', 'pp-number')
        self.assertEqual('1', myTok.evalConstExpr())
        myTok = PpToken.PpToken('', 'pp-number')
        self.assertEqual('', myTok.evalConstExpr())

    def test_06(self):
        """TestPpTokenEvalConstExpr.test_06(): Integer literals, Hex and unsigned/long."""
        myTok = PpToken.PpToken('0xFF', 'pp-number')
        self.assertEqual('0xFF', myTok.evalConstExpr())
        myTok = PpToken.PpToken('0XAF', 'pp-number')
        self.assertEqual('0XAF', myTok.evalConstExpr())
        myTok = PpToken.PpToken('0xFFul', 'pp-number')
        self.assertEqual('0xFF', myTok.evalConstExpr())
        myTok = PpToken.PpToken('0XAFul', 'pp-number')
        self.assertEqual('0XAF', myTok.evalConstExpr())

    def test_07(self):
        """TestPpTokenEvalConstExpr.test_07(): Integer literals, Octal and unsigned/long."""
        myTok = PpToken.PpToken('012', 'pp-number')
        self.assertEqual('012', myTok.evalConstExpr())
        myTok = PpToken.PpToken('017', 'pp-number')
        self.assertEqual('017', myTok.evalConstExpr())
        myTok = PpToken.PpToken('017uL', 'pp-number')
        self.assertEqual('017', myTok.evalConstExpr())
        myTok = PpToken.PpToken('017l', 'pp-number')
        self.assertEqual('017', myTok.evalConstExpr())

    def test_10(self):
        """TestPpTokenEvalConstExpr.test_10(): Identifiers."""
        myTok = PpToken.PpToken('ABC', 'identifier')
        self.assertEqual('0', myTok.evalConstExpr())
        myTok = PpToken.PpToken('true', 'identifier')
        self.assertEqual('True', myTok.evalConstExpr())
        myTok = PpToken.PpToken('false', 'identifier')
        self.assertEqual('False', myTok.evalConstExpr())
        myTok = PpToken.PpToken('&&', 'preprocessing-op-or-punc')
        self.assertEqual('and', myTok.evalConstExpr())
        myTok = PpToken.PpToken('||', 'preprocessing-op-or-punc')
        self.assertEqual('or', myTok.evalConstExpr())
        
    def test_11(self):
        """TestPpTokenEvalConstExpr.test_11(): '/' gets converted to '//' for true division."""
        myTok = PpToken.PpToken('/', 'preprocessing-op-or-punc')
        self.assertEqual('//', myTok.evalConstExpr())
        
        
class TestPpTokenEscapeCodes(unittest.TestCase):
    """Tests escape codes."""
    def test_00(self):
        """Tests \\u escape."""
        p = PpToken.PpToken(r'object\u0092s', 'identifier')
#        print(p.t)
        self.assertEqual(p.t, r'object\u0092s')
        
    def test_01(self):
        """Tests \\x escape."""
        p = PpToken.PpToken(r'object\x92s', 'identifier')
#        print(p.t)
        self.assertEqual(p.t, r'object\x92s')


def unitTest(theVerbosity=2):
    """Execute unit tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGlobals)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenCtor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenFlags))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenCmp))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenWs))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenMerge))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenReplaceWhitespace))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenTokensStr))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenIsCond))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenLineColumn))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenEvalConstExpr))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenEscapeCodes))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

#################
# End: Unit tests
#################

def usage():
    """Send the help to stdout."""
    print("""TestPpToken.py - A module that tests PpToken module.
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
    print('TestPpToken.py script version "%s", dated %s' % (__version__, __date__))
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
