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

#import os
import sys
import time
import logging
import io

from cpip.core import PpToken
from cpip.core import PpTokeniser
from cpip.core import PpDefine
from cpip.core import FileLocation

from cpip.core.test import TestBase
######################
# Section: Unit tests.
######################
import unittest
# Define unit test classes

"""Using cpp.exe to help with test cases:

Suppose you have a file with the expected expansion in a comment thus:
#define x 2
#define f(a) f(x * (a))
#define g f
#define t(a) a
t(g)                    // f
t(g)(0)                 // f(2 * (0))
t(g)(0) + t             // f(2 * (0)) + t
t(g(0) + t);            // f(2 * (0)) + t;
t(t(g)(0) + t)(1);      // f(2 * (0)) + t(1);
t(t)                    // t
t(t);                   // t;
t(t)();                 // t();

Invoke cpp.exe thus:
$ cpp.exe -E -C -P example_3.h
f // f
f(2 * (0)) // f(2 * (0))
f(2 * (0)) + t // f(2 * (0)) + t
f(2 * (0)) + t; // f(2 * (0)) + t;
f(2 * (0)) + t(1); // f(2 * (0)) + t(1);
t // t
t; // t;
t(); // t();

You can check that the left and right sides of the comment are the same.

Could use -dD option as well to get the macro definitions out.

Using the regex to teh source file:
^(.+?)(\s+)//\s+(.+)\s*$
Replacing with:
('\1',\2 '\3'),
Gives:
('t(g)',                     'f'),
('t(g)(0)',                  'f(2 * (0))'),
('t(g)(0) + t',              'f(2 * (0)) + t'),
('t(g(0) + t);',             'f(2 * (0)) + t;'),
('t(t(g)(0) + t)(1);',       'f(2 * (0)) + t(1);'),
('t(t)',                     't'),
('t(t);',                    't;'),
('t(t)();',                  't();'),

"""

class TestPpDefine(TestBase.TestCpipBase):
    """Base class for tests on PpDefine and PpDefine.MacroReplacementEnv."""

    def _retCheckedMacro(self, theStr, isObj, numToks, name, idS, rS):
        """Creates and checks a macro and returns it."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(theStr)
            )
        myGen = myCpp.next()
        MY_SPOOF_FILE = 'Some kind of thing that might not be a file on the file system'
        MY_LINE = 12
        retDef = PpDefine.PpDefine(myGen,
                                   MY_SPOOF_FILE,
                                   MY_LINE)
        self.assertEqual(isObj, retDef.isObjectTypeMacro)
        self.assertEqual(numToks, retDef.tokensConsumed)
        self.assertEqual(name, retDef.identifier)
        self.assertEqual(idS, retDef.parameters)
        self.assertEqual(rS, retDef.replacements)
        self.assertEqual(retDef.fileId, MY_SPOOF_FILE)
        self.assertEqual(retDef.line, MY_LINE)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        return retDef
    
class TestPpDefineInit(TestPpDefine):
    """Tests the creation of PpDefine from a token stream."""

    #====================
    # Object type macros.
    #====================
    def testInitObject_00(self):
        """PpDefine.__init__(): OK from object type macro: <#define> 'FOO\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(2, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertFalse(myCppDef.expandArguments)

    def testInitObject_00_00(self):
        """PpDefine.__init__(): OK from object type macro: <#define> 'FOO  \\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO  \n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(2, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_00_01(self):
        """PpDefine.__init__(): OK from object type macro: <#define> 'FOO\\n  abc'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO  \n  abc')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(2, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        #print 'TRACE_MACRO:\n"%s"' % myCppDef
        self.assertEqual(PpToken.PpToken('abc', 'identifier'), next(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_01(self):
        """PpDefine.__init__(): OK from object type macro: <#define> 'FOO\\n#define BAR\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO\n#define BAR\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(2, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check remainder
        self.assertEqual(
            [
                PpToken.PpToken('#',        'preprocessing-op-or-punc'),
                PpToken.PpToken('define',   'identifier'),
                PpToken.PpToken(' ',        'whitespace'),
                PpToken.PpToken('BAR',      'identifier'),
                PpToken.PpToken('\n',       'whitespace')
            ],
            [x for x in myGen],
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_02(self):
        """PpDefine.__init__(): OK from object type macro: <#define> 'FOO 42\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO 42\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(4, myCppDef.tokensConsumed)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['42',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_03(self):
        """PpDefine.__init__(): OK from object type macro: <#define> '   FOO\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('   FOO\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(3, myCppDef.tokensConsumed)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_04(self):
        """PpDefine.__init__(): OK from object type macro: <#define> '   FOO    \\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('   FOO    \n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(3, myCppDef.tokensConsumed)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_05(self):
        """PpDefine.__init__(): OK from object type macro: <#define> 'FOO a b c\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO a b c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(8, myCppDef.tokensConsumed)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['a', ' ', 'b', ' ', 'c',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_06(self):
        """PpDefine.__init__(): OK from object type macro: <#define> 'FOO a b c   \\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO a b c   \n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(8, myCppDef.tokensConsumed)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['a', ' ', 'b', ' ', 'c',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_07(self):
        """PpDefine.__init__(): OK from object type macro: <#define> 'FOO a b c \\nName'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO a b c \nName')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(8, myCppDef.tokensConsumed)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['a', ' ', 'b', ' ', 'c',], myCppDef.replacements)
        self.assertEqual(
            [
                PpToken.PpToken('Name', 'identifier'),
            ],
            [x for x in myGen],
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_08(self):
        """PpDefine.__init__(): OK from object type macro: <#define> 'DOUBLE_SHARP spam ## eggs\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('DOUBLE_SHARP spam ## eggs\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(8, myCppDef.tokensConsumed)
        self.assertEqual('DOUBLE_SHARP', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['spam', ' ', '##', ' ', 'eggs'], myCppDef.replacements)
        # Check remainder
        self.assertEqual(
            [
                PpToken.PpToken('spam',    'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('##',      'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('eggs',    'identifier'),
            ],
            myCppDef.replacementTokens,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    # Failures
    def testInitObject_Fail_00(self):
        """PpDefine.__init__(): Bad from object type macro: <#define> '\\n' (non-directive)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_Fail_01(self):
        """PpDefine.__init__(): Bad from object type macro: <#define> '' (no newline and empty)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_Fail_02(self):
        """PpDefine.__init__(): Bad from object type macro: <#define> 'EGGS' (no newline)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('EGGS')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_Fail_03(self):
        """PpDefine.__init__(): Bad from object type macro: <#define> 'PLUS+\\n'.
        cpp says for "#define PLUS+":
        src.h:1:13: warning: ISO C requires whitespace after the macro name"""
        logging.debug('testInitObject_Fail_03()')
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('PLUS+\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineMissingWs,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitObject_Fail_04(self):
        """PpDefine.__init__(): ISO/IEC 14882:1998(E) 16-2 bad whitespace in object type macro: <#define> 'SPAM\\v\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM\v\n')
            )
        myGen = myCpp.next()
        #myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertRaises(
            PpDefine.ExceptionCpipDefineBadWs,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitObject_Fail_05(self):
        """PpDefine.__init__(): ISO/IEC 14882:1998(E) 16-2 bad whitespace in object type macro: <#define> 'SPAM\\f\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM\f\n')
            )
        myGen = myCpp.next()
        #myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertRaises(
            PpDefine.ExceptionCpipDefineBadWs,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM\f EGGS\n')
            )
        myGen = myCpp.next()
        #myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertRaises(
            PpDefine.ExceptionCpipDefineBadWs,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitObject_Fail_06(self):
        """PpDefine.__init__(): ISO/IEC 14882:1998(E) 16.3.3-1 bad '##' in object type macro: <#define> 'DOUBLE_SHARP ##\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('DOUBLE_SHARP ##\n')
            )
        myGen = myCpp.next()
        #myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitObject_Fail_07(self):
        """PpDefine.__init__(): ISO/IEC 14882:1998(E) 16.3.3-1 bad leading '##' in object type macro: <#define> 'DOUBLE_SHARP ## spam\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('DOUBLE_SHARP ## spam\n')
            )
        myGen = myCpp.next()
        #myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitObject_Fail_08(self):
        """PpDefine.__init__(): ISO/IEC 14882:1998(E) 16.3.3-1 bad trailing '##' in object type macro: <#define> 'DOUBLE_SHARP spam ##\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('DOUBLE_SHARP spam ##\n')
            )
        myGen = myCpp.next()
        #myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitObject_Fail_09(self):
        """PpDefine.__init__(): Bad from object type macro: <#define> '123' (no identifier, pp-number)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('123')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_Fail_10(self):
        """PpDefine.__init__(): Bad from object type macro: <#define> '123 456\\n' (no identifier, pp-number)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('123 456\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_Fail_11(self):
        """PpDefine.__init__(): Bad from object type macro: <#define> '?\\n' (no identifier, preprocessing-op-or-punc)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('?\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_Fail_12(self):
        """PpDefine.__init__(): Bad from object type macro: <#define> '"string"\\n' (no identifier, string-literal)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('"string"\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_Fail_13(self):
        """PpDefine.__init__(): Bad from object type macro: <#define> "'c'\\n" (no identifier, character-literal)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO("'c'\n")
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitObject_Fail_14(self):
        """PpDefine.__init__(): Bad from object type macro: <#define> '<string>\\n' (no identifier, header-name)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('<string>\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testObject_String_00(self):
        """PpDefine.__str__(): OK from object type macro: <#define> 'FOO 42\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO    a +b  \n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'foo.h', 17)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual(7, myCppDef.tokensConsumed)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['a', ' ', '+', 'b'], myCppDef.replacements)
        self.assertEqual('#define FOO a +b /* foo.h#17 Ref: 0 True */', str(myCppDef))

    def testObject_String_01(self):
        """PpDefine.__str__(): OK from object type macro: <#define> 'FOO 42\\n' when #undef'd."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO    a +b  \n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'foo.h', 17)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual(7, myCppDef.tokensConsumed)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['a', ' ', '+', 'b'], myCppDef.replacements)
        self.assertEqual('#define FOO a +b /* foo.h#17 Ref: 0 True */', str(myCppDef))
        myCppDef.undef('foo.h', 127)
        self.assertEqual('#define FOO a +b /* foo.h#17 Ref: 0 False foo.h#127 */', str(myCppDef))

    #=========================
    # End: Object like macros.
    #=========================

    #======================
    # Function like macros.
    #======================
    def testInitFunction_00(self):
        """PpDefine.__init__(): OK from function type macro: <#define> 'FOO(a,b,c)\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c)\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(9, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertTrue(myCppDef.expandArguments)

    def testInitFunction_03(self):
        """PpDefine.__init__(): OK from function type macro: <#define> 'FOO(  a  ,  b ,c)\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(  a  ,  b ,c)\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(13, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitFunction_05(self):
        """PpDefine.__init__(): OK from function type macro: <#define> 'FOO(a,b,c) a+b+c\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c) a+b+c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(15, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual(['a', '+', 'b', '+', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitFunction_06(self):
        """PpDefine.__init__(): OK from function type macro: <#define> 'SPAM()\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM()\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(4, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual([], myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitFunction_07(self):
        """PpDefine.__init__(): OK from function type macro: <#define> 'SPAM()1+2\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM()1+2\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(7, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual([], myCppDef.parameters)
        self.assertEqual(['1', '+', '2'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitFunction_08(self):
        """PpDefine.__init__(): OK from function type macro: <#define> 'SPAM(a,b,c) a + b - c\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM(a,b,c) a + b - c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(19, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c'], myCppDef.parameters)
        self.assertEqual(['a', ' ', '+', ' ', 'b', ' ', '-', ' ', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitFunction_09(self):
        """PpDefine.__init__(): OK from function type macro: <#define> 'SPAM(a,b,c) a ## b ## c\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM(a,b,c) a ## b ## c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(19, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c'], myCppDef.parameters)
        self.assertEqual(['a', ' ', '##', ' ', 'b', ' ', '##', ' ', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertFalse(myCppDef.expandArguments)

    def testInitFunction_10(self):
        """PpDefine.__init__(): OK from function type macro: <#define> 'SPAM(a,b,c) # a # b # c\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM(a,b,c) # a # b # c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(21, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c'], myCppDef.parameters)
        self.assertEqual(['#', ' ', 'a', ' ', '#', ' ', 'b', ' ', '#', ' ', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertFalse(myCppDef.expandArguments)

    def testInitFunction_11(self):
        """PpDefine.__init__(): OK from function type macro: <#define> 'SPAM(a,b) ab a b\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM(a,b) ab a b\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(13, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(['a', 'b',], myCppDef.parameters)
        self.assertEqual(['ab', ' ', 'a', ' ', 'b',], myCppDef.replacements)
        self.assertEqual(
            [
                PpToken.PpToken('ab',  'identifier'),
                PpToken.PpToken(' ',   'whitespace'),
                PpToken.PpToken('a',   'identifier'),
                PpToken.PpToken(' ',   'whitespace'),
                PpToken.PpToken('b',   'identifier'),
            ],
            myCppDef.replacementTokens,
            )

    def testInitFunction_12(self):
        """PpDefine.__init__(): OK from function type macro: <#define> 'INC(a) <a>\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('INC(a) <a>\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(9, myCppDef.tokensConsumed)
        self.assertEqual('INC', myCppDef.identifier)
        self.assertEqual(['a',], myCppDef.parameters)
        self.assertEqual(['<', 'a', '>',], myCppDef.replacements)
        myExp = [
                PpToken.PpToken('<',    'preprocessing-op-or-punc'),
                PpToken.PpToken('a',    'identifier'),
                PpToken.PpToken('>',    'preprocessing-op-or-punc'),
            ]
        self._printDiff(myCppDef.replacementTokens, myExp)
        self.assertEqual(
            myCppDef.replacementTokens,
            myExp,
            )

    def testInitFunction_13(self):
        """PpDefine.__init__(): OK from function type macro: <#define> 'INC(a) # a\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('INC(a) # a\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(9, myCppDef.tokensConsumed)
        self.assertEqual('INC', myCppDef.identifier)
        self.assertEqual(['a',], myCppDef.parameters)
        self.assertEqual(['#', ' ', 'a',], myCppDef.replacements)
        myExp = [
                PpToken.PpToken('#',    'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',    'whitespace'),
                PpToken.PpToken('a',    'identifier'),
            ]
        self._printDiff(myCppDef.replacementTokens, myExp)
        self.assertEqual(
            myCppDef.replacementTokens,
            myExp,
            )

    # Testing failure
    def testInitFunction_50(self):
        """PpDefine.__init__(): Bad from function type macro: <#define> 'FOO(a,b,c\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitFunction_51(self):
        """PpDefine.__init__(): Bad from function type macro: <#define> 'FOO(a,(b,c)\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,(b,c)\n')
            )
        myGen = myCpp.next()
        #PpDefine.PpDefine(myGen, '', 1)
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitFunction_52(self):
        """PpDefine.__init__(): OK from attempted function type macro: <#define> 'FOO (a,b,c)\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO (a,b,c)\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(10, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['(', 'a', ',', 'b', ',', 'c', ')'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testInitFunction_53(self):
        """PpDefine.__init__(): Bad from function type macro: <#define> 'FOO(a,a)\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,a)\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineDupeId,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitFunction_54(self):
        """PpDefine.__init__(): Bad from function type macro: <#define> 'SPAM(a,b,c) # x # b # c\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM(a,b,c) # x # b # c\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitFunction_55(self):
        """PpDefine.__init__(): Bad from function type macro: <#define> 'SPAM(a,b,c) # a # y # c\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM(a,b,c) # a # y # c\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitFunction_56(self):
        """PpDefine.__init__(): Bad from function type macro: <#define> 'SPAM(a,b,c) # a # b # z\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM(a,b,c) # a # b # z\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitFunction_70(self):
        """PpDefine.__init__(): Bad from function type macro: <#define> 'FOO((a,b,c))\\n'.
        See note on PpDefine._ctorFunctionMacro() about the standard vs cpp.exe"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO((a,b,c))\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitFunction_71(self):
        """PpDefine.__init__(): Bad from function type macro: <#define> 'FOO((a),(b),(c))\\n'.
        See note on PpDefine._ctorFunctionMacro() about the standard vs cpp.exe"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO((a),(b),(c))\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testInitFunction_72(self):
        """PpDefine.__init__(): Bad from function type macro: <#define> 'FOO(a,(,)b)\\n'.
        See note on PpDefine._ctorFunctionMacro() about the standard vs cpp.exe"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,(,)b)\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            PpDefine.PpDefine,
            myGen,
            '',
            1,
            )

    def testFunction_String_00(self):
        """PpDefine.__str__(): OK from function type macro: <#define> 'SPAM(a,b,c) # a # b # c\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM(a  ,  b  ,  c  )    # a  #  b # c   \n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'spam.h', 11)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(26, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c'], myCppDef.parameters)
        self.assertEqual(['#', ' ', 'a', '  ', '#', '  ', 'b', ' ', '#', ' ', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual('#define SPAM(a,b,c) # a # b # c /* spam.h#11 Ref: 0 True */', str(myCppDef))

    def testFunction_String_01(self):
        """PpDefine.__str__(): OK from function type macro: <#define> 'SPAM(a,b,c) # a # b # c\\n' when #undef'd."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM(a  ,  b  ,  c  )    # a  #  b # c   \n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'spam.h', 11)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(26, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c'], myCppDef.parameters)
        self.assertEqual(['#', ' ', 'a', '  ', '#', '  ', 'b', ' ', '#', ' ', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual('#define SPAM(a,b,c) # a # b # c /* spam.h#11 Ref: 0 True */', str(myCppDef))
        myCppDef.undef('spam.h', 27)
        self.assertEqual('#define SPAM(a,b,c) # a # b # c /* spam.h#11 Ref: 0 False spam.h#27 */', str(myCppDef))

    #===========================
    # End: Function type macros.
    #===========================

class TestPpDefineRedefineAndCmp(TestPpDefine):
    """Tests the redefinition and comparison rules for PpDefine."""

    def testDefine_00(self):
        """PpDefine: Redefine OK from object type macro: <#define> 'FOO\\n'."""
        myDefA = self._retCheckedMacro('FOO\n', True, 2, 'FOO', None, [])
        myDefB = self._retCheckedMacro('FOO\n', True, 2, 'FOO', None, [])
        self.assertEqual(True, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(True, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(0, myDefA.isSame(myDefB))
        self.assertEqual(0, myDefB.isSame(myDefA))
        self.assertEqual(myDefA, myDefB)

    def testDefine_01(self):
        """PpDefine: Redefine OK from object type macro: <#define> 'FOO 1\\n'."""
        myDefA = self._retCheckedMacro('FOO 1\n', True, 4, 'FOO', None, ['1'])
        myDefB = self._retCheckedMacro('FOO   1  \n', True, 4, 'FOO', None, ['1'])
        self.assertEqual(True, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(True, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(0, myDefA.isSame(myDefB))
        self.assertEqual(0, myDefB.isSame(myDefA))
        self.assertEqual(myDefA, myDefB)

    def testDefine_02(self):
        """PpDefine: Redefine OK from object type macro: <#define> 'FOO 1+2\\n'."""
        myDefA = self._retCheckedMacro('FOO 1+2\n', True, 6, 'FOO', None, ['1', '+', '2'])
        myDefB = self._retCheckedMacro('FOO   1+2  \n', True, 6, 'FOO', None, ['1', '+', '2'])
        self.assertEqual(True, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(True, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(0, myDefA.isSame(myDefB))
        self.assertEqual(0, myDefB.isSame(myDefA))
        self.assertEqual(myDefA, myDefB)

    def testDefine_03(self):
        """PpDefine: Redefine OK from object type macro: <#define> 'FOO 1  +  2  \\n' (whitespace equivelent)."""
        myDefA = self._retCheckedMacro(
            'FOO 1 + 2\n',
            True,
            8,
            'FOO',
            None,
            ['1', ' ', '+', ' ', '2'],
            )
        myDefB = self._retCheckedMacro(
            'FOO 1  +   2  \n',
            True,
            8,
            'FOO',
            None,
            ['1', '  ', '+', '   ', '2'],
            )
        self.assertEqual(True, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(True, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(0, myDefA.isSame(myDefB))
        self.assertEqual(0, myDefB.isSame(myDefA))
        self.assertEqual(myDefA, myDefB)

    def testRedefine_10(self):
        """PpDefine: Redefine OK from object type macro: ISO/IEC 14882:1998(E) 16.3.5-7 [cpp.replace] <#define> 'OBJ_LIKE (1-1)\\n'."""
        myDefA = self._retCheckedMacro('OBJ_LIKE (1-1)\n',
                                       True,
                                       8,
                                       'OBJ_LIKE',
                                       None,
                                       ['(', '1', '-', '1', ')'],
                                       )
        myDefB = self._retCheckedMacro('OBJ_LIKE /* white space */ (1-1) /* other */\n',
                                       True,
                                       12,
                                       'OBJ_LIKE',
                                       None,
                                       ['(', '1', '-', '1', ')'],
                                       )
        self.assertEqual(True, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(True, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(0, myDefA.isSame(myDefB))
        self.assertEqual(0, myDefB.isSame(myDefA))
        self.assertEqual(myDefA, myDefB)

    def testRedefine_11(self):
        """PpDefine: Redefine not OK from object type macro: ISO/IEC 14882:1998(E) 16.3.5-7 [cpp.replace] <#define> 'OBJ_LIKE (1-1)\\n'."""
        myDefA = self._retCheckedMacro('OBJ_LIKE (1-1)\n',
                                       True,
                                       8,
                                       'OBJ_LIKE',
                                       None,
                                       ['(', '1', '-', '1', ')'],
                                       )
        myDefB = self._retCheckedMacro('OBJ_LIKE (1 - 1)\n',
                                       True,
                                       10,
                                       'OBJ_LIKE',
                                       None,
                                       ['(', '1', ' ', '-', ' ', '1', ')'],
                                       )
        self.assertEqual(False, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(False, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(1, myDefA.isSame(myDefB))
        self.assertEqual(1, myDefB.isSame(myDefA))
        self.assertNotEqual(myDefA, myDefB)

    def testRedefine_12(self):
        """PpDefine: Redefine OK from function like macro: ISO/IEC 14882:1998(E) 16.3.5-7 [cpp.replace] <#define> 'FUNC_LIKE(a) ( a )\\n' (whitespace equivelent)."""
        myDefA = self._retCheckedMacro(
            'FUNC_LIKE(a) ( a )\n',
            False,
            11,
            'FUNC_LIKE',
            ['a',],
            ['(', ' ', 'a', ' ', ')'],
            )
        myDefB = self._retCheckedMacro(
            'FUNC_LIKE( a )( /* note the white space */ a /* other stuff on this line */ )\n',
            False,
            16,
            'FUNC_LIKE',
            ['a',],
            ['(', '   ', 'a', '   ', ')'],
            )
        self.assertEqual(True, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(True, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(0, myDefA.isSame(myDefB))
        self.assertEqual(0, myDefB.isSame(myDefA))
        self.assertEqual(myDefA, myDefB)

    def testRedefine_13(self):
        """PpDefine: Redefine not OK from function like macro: ISO/IEC 14882:1998(E) 16.3.5-7 [cpp.replace] <#define> 'FUNC_LIKE(a) ( a )\\n' (id and replacement)."""
        myDefA = self._retCheckedMacro(
            'FUNC_LIKE(a) ( a )\n',
            False,
            11,
            'FUNC_LIKE',
            ['a',],
            ['(', ' ', 'a', ' ', ')'],
            )
        myDefB = self._retCheckedMacro(
            'FUNC_LIKE(b) ( b )\n',
            False,
            11,
            'FUNC_LIKE',
            ['b',],
            ['(', ' ', 'b', ' ', ')'],
            )
        self.assertEqual(False, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(False, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(1, myDefA.isSame(myDefB))
        self.assertEqual(1, myDefB.isSame(myDefA))
        self.assertNotEqual(myDefA, myDefB)

    def testRedefine_14(self):
        """PpDefine: Redefine not OK from function like macro: ISO/IEC 14882:1998(E) 16.3.5-7 [cpp.replace] <#define> 'FUNC_LIKE(a) ( a )\\n' (replacement)."""
        myDefA = self._retCheckedMacro(
            'FUNC_LIKE(a) ( a )\n',
            False,
            11,
            'FUNC_LIKE',
            ['a',],
            ['(', ' ', 'a', ' ', ')'],
            )
        myDefB = self._retCheckedMacro(
            'FUNC_LIKE(a) ( b )\n',
            False,
            11,
            'FUNC_LIKE',
            ['a',],
            ['(', ' ', 'b', ' ', ')'],
            )
        self.assertEqual(False, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(False, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(1, myDefA.isSame(myDefB))
        self.assertEqual(1, myDefB.isSame(myDefA))
        self.assertNotEqual(myDefA, myDefB)

    def testRedefine_15(self):
        """PpDefine: Redefine not OK from function like macro: ISO/IEC 14882:1998(E) 16.3.5-7 [cpp.replace] <#define> 'FUNC_LIKE(a) ( a )\\n' (id)."""
        myDefA = self._retCheckedMacro(
            'FUNC_LIKE(a) ( a )\n',
            False,
            11,
            'FUNC_LIKE',
            ['a',],
            ['(', ' ', 'a', ' ', ')'],
            )
        myDefB = self._retCheckedMacro(
            'FUNC_LIKE(b) ( a )\n',
            False,
            11,
            'FUNC_LIKE',
            ['b',],
            ['(', ' ', 'a', ' ', ')'],
            )
        self.assertEqual(False, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(False, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(1, myDefA.isSame(myDefB))
        self.assertEqual(1, myDefB.isSame(myDefA))
        self.assertNotEqual(myDefA, myDefB)

    def testRedefine_16(self):
        """PpDefine: Redefine not OK from function/object like macro: ISO/IEC 14882:1998(E) 16.3.5-7 [cpp.replace].
        Also: ISO/IEC 9899:1999 (E) 6.10.3.5-8"""
        myDefA = self._retCheckedMacro(
            'SPAM(a) a\n',
            False,
            7,
            'SPAM',
            ['a',],
            ['a',],
            )
        myDefB = self._retCheckedMacro(
            'SPAM a\n',
            True,
            4,
            'SPAM',
            None,
            ['a',],
            )
        self.assertEqual(False, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(False, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(1, myDefA.isSame(myDefB))
        self.assertEqual(1, myDefB.isSame(myDefA))
        self.assertNotEqual(myDefA, myDefB)

    def testRedefine_17(self):
        """PpDefine: Redefine not OK from object like macro: ISO/IEC 14882:1998(E) 16.3.5-7 [cpp.replace] whitespace missmatch.
        Also: ISO/IEC 9899:1999 (E) 6.10.3.5-8"""
        myDefA = self._retCheckedMacro(
            'SPAM a b c\n',
            True,
            8,
            'SPAM',
            None,
            ['a', ' ', 'b', ' ', 'c'],
            )
        myDefB = self._retCheckedMacro(
            'SPAM a   c d\n',
            True,
            8,
            'SPAM',
            None,
            ['a', '   ', 'c', ' ', 'd'],
            )
        self.assertEqual(False, myDefA.isValidRefefinition(myDefB))
        self.assertEqual(False, myDefB.isValidRefefinition(myDefA))
        self.assertEqual(1, myDefA.isSame(myDefB))
        self.assertEqual(1, myDefB.isSame(myDefA))
        self.assertNotEqual(myDefA, myDefB)

    def testDefine_18(self):
        """PpDefine: Redefine fails from object type macro [A] that has been #undef'd."""
        myDefA = self._retCheckedMacro('FOO\n', True, 2, 'FOO', None, [])
        myDefA.undef('', 1)
        myDefB = self._retCheckedMacro('FOO\n', True, 2, 'FOO', None, [])
        self.assertRaises(PpDefine.ExceptionCpipDefine, myDefA.isValidRefefinition, myDefB)
        self.assertRaises(PpDefine.ExceptionCpipDefine, myDefB.isValidRefefinition, myDefA)
        self.assertRaises(PpDefine.ExceptionCpipDefine, myDefA.isSame, myDefB)
        self.assertRaises(PpDefine.ExceptionCpipDefine, myDefB.isSame, myDefA)
        try:
            self.assertEqual(myDefA, myDefB)
            self.fail('PpDefine.ExceptionCpipDefine not raised on equality.')
        except PpDefine.ExceptionCpipDefine:
            pass

    def testDefine_19(self):
        """PpDefine: Redefine fails from object type macro [B] that has been #undef'd."""
        myDefA = self._retCheckedMacro('FOO\n', True, 2, 'FOO', None, [])
        myDefB = self._retCheckedMacro('FOO\n', True, 2, 'FOO', None, [])
        myDefB.undef('', 1)
        self.assertRaises(PpDefine.ExceptionCpipDefine, myDefA.isValidRefefinition, myDefB)
        self.assertRaises(PpDefine.ExceptionCpipDefine, myDefB.isValidRefefinition, myDefA)
        self.assertRaises(PpDefine.ExceptionCpipDefine, myDefA.isSame, myDefB)
        self.assertRaises(PpDefine.ExceptionCpipDefine, myDefB.isSame, myDefA)
        try:
            self.assertEqual(myDefA, myDefB)
            self.fail('PpDefine.ExceptionCpipDefine not raised on equality.')
        except PpDefine.ExceptionCpipDefine:
            pass
    
    def testDefine_cmp_00(self):
        """PpDefine: __cmp__() of differently named object type macros."""
        myDefA = self._retCheckedMacro('SPAM\n', True, 2, 'SPAM', None, [])
        myDefB = self._retCheckedMacro('EGGS\n', True, 2, 'EGGS', None, [])
        self.assertRaises(PpDefine.ExceptionCpipDefineInvalidCmp, myDefA.isValidRefefinition, myDefB)
        self.assertEqual(-1, myDefA.isSame(myDefB))
        self.assertEqual(-1, myDefB.isSame(myDefA))
        self.assertNotEqual(myDefA, myDefB)

    def testDefine_cmp_01(self):
        """PpDefine: __cmp__() of differently named object type macros with replacment."""
        myDefA = self._retCheckedMacro('SPAM 1\n', True, 4, 'SPAM', None, ['1',])
        myDefB = self._retCheckedMacro('EGGS 1\n', True, 4, 'EGGS', None, ['1',])
        self.assertRaises(PpDefine.ExceptionCpipDefineInvalidCmp, myDefA.isValidRefefinition, myDefB)
        self.assertEqual(-1, myDefA.isSame(myDefB))
        self.assertEqual(-1, myDefB.isSame(myDefA))
        self.assertNotEqual(myDefA, myDefB)

    def testDefine_cmp_10(self):
        """PpDefine: __cmp__() of differently named function type macros."""
        myDefA = self._retCheckedMacro('SPAM(a)\n', False, 5, 'SPAM', ['a',], [])
        myDefB = self._retCheckedMacro('EGGS(a)\n', False, 5, 'EGGS', ['a',], [])
        self.assertRaises(PpDefine.ExceptionCpipDefineInvalidCmp, myDefA.isValidRefefinition, myDefB)
        self.assertEqual(-1, myDefA.isSame(myDefB))
        self.assertEqual(-1, myDefB.isSame(myDefA))
        self.assertNotEqual(myDefA, myDefB)

    def testDefine_cmp_11(self):
        """PpDefine: __cmp__() of differently named function type macros with replacment."""
        myDefA = self._retCheckedMacro('SPAM(a) (a)\n', False, 9, 'SPAM', ['a',], ['(', 'a', ')'])
        myDefB = self._retCheckedMacro('EGGS(a) (a)\n', False, 9, 'EGGS', ['a',], ['(', 'a', ')'])
        self.assertRaises(PpDefine.ExceptionCpipDefineInvalidCmp, myDefA.isValidRefefinition, myDefB)
        self.assertEqual(-1, myDefA.isSame(myDefB))
        self.assertEqual(-1, myDefB.isSame(myDefA))
        self.assertNotEqual(myDefA, myDefB)

class TestPpDefineFunctionLikeLowLevel(TestPpDefine):
    """Tests PpDefine low level functionality. Function style macros only."""

    def testConsumeFunctionPreamble_00(self):
        """PpDefine.consumeFunctionPreamble() when well formed."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c)\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(9, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Now try various preambles
        # Good ones first
        for aStr in ['(', ' (', '  (', '   (', '\t(', '\n(', ' \t\n (']:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(aStr)
                )
            myGen = myCpp.next()
            myResult = myCppDef.consumeFunctionPreamble(myGen)
            # Check that all tokens have been consumed
            self.assertRaises(StopIteration, myGen.__next__)
            # Check the result
            self.assertEqual(None, myResult)

    def testConsumeFunctionPreamble_01(self):
        """PpDefine.consumeFunctionPreamble() when ill-formed."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c)\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(9, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # No tokens
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('')
            )
        myGen = myCpp.next()
        myResult = myCppDef.consumeFunctionPreamble(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the result
        self.assertEqual(
                [
                ],
                myResult
            )
        # Single whitespace
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(' ')
            )
        myGen = myCpp.next()
        myResult = myCppDef.consumeFunctionPreamble(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the result
        self.assertEqual(
                [
                    PpToken.PpToken(' ',       'whitespace'),
                ],
                myResult
            )
        # RPAREN, this should return an empty list
        # but leave the RPAREN on the generator
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(')')
            )
        myGen = myCpp.next()
        myResult = myCppDef.consumeFunctionPreamble(myGen)
        # Check the result
        self.assertEqual([], myResult)
        # Get the token and check
        self.assertEqual(
                PpToken.PpToken(')', 'preprocessing-op-or-punc'),
                next(myGen),
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testCppretArgumentListTokens_00(self):
        """PpDefine.retArgumentListTokens() - All arguments."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testCppretArgumentListTokens_01(self):
        """PpDefine.retArgumentListTokens() - Missing leading argument."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(',2,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                myCppDef.PLACEMARKER,
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testCppretArgumentListTokens_02(self):
        """PpDefine.retArgumentListTokens() - Missing trailing argument."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2,)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                myCppDef.PLACEMARKER,
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testCppretArgumentListTokens_03(self):
        """PpDefine.retArgumentListTokens() - Missing middle argument."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                myCppDef.PLACEMARKER,
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testCppretArgumentListTokens_04(self):
        """PpDefine.retArgumentListTokens() - Missing all arguments."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(',,)')
            )
        myGen = myCpp.next()
        myArgTokens = [
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testCppretArgumentListTokens_05(self):
        """PpDefine.retArgumentListTokens() - #define f(a) a \\n and invoke f(t(g)(0) + t)."""
        myCppDef = self._retCheckedMacro(
                            'f(a) a\n',
                            False,
                            7,
                            'f',
                            ['a',],
                            ['a',],
                        )
        self.assertEqual(
            [
                PpToken.PpToken('a',     'identifier'),
            ],
            myCppDef.replacementTokens
        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('t(g)(0) + t)')
            )
        myGen = myCpp.next()
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('t',      'identifier'),
                    PpToken.PpToken('(',      'preprocessing-op-or-punc'),
                    PpToken.PpToken('g',      'identifier'),
                    PpToken.PpToken(')',      'preprocessing-op-or-punc'),
                    PpToken.PpToken('(',      'preprocessing-op-or-punc'),
                    PpToken.PpToken('0',      'pp-number'),
                    PpToken.PpToken(')',      'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',      'whitespace'),
                    PpToken.PpToken('+',      'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',      'whitespace'),
                    PpToken.PpToken('t',      'identifier'),
                ],
            ]
        myActualArgTokens = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual(myExpectedArgTokens, myActualArgTokens)

    def testCppretArgumentListTokens_06(self):
        """PpDefine.retArgumentListTokens() - #define f(a,b) a+b \\n and invoke f(1(,)2,3)."""
        myCppDef = self._retCheckedMacro(
                            'f(a,b) a+b\n',
                            False,
                            11,
                            'f',
                            ['a', 'b'],
                            ['a', '+', 'b'],
                        )
        self.assertEqual(
            [
                PpToken.PpToken('a',     'identifier'),
                PpToken.PpToken('+',     'preprocessing-op-or-punc'),
                PpToken.PpToken('b',     'identifier'),
            ],
            myCppDef.replacementTokens
        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1(,)2,3)')
            )
        myGen = myCpp.next()
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('1',      'pp-number'),
                    PpToken.PpToken('(',      'preprocessing-op-or-punc'),
                    PpToken.PpToken(',',      'preprocessing-op-or-punc'),
                    PpToken.PpToken(')',      'preprocessing-op-or-punc'),
                    PpToken.PpToken('2',      'pp-number'),
                ],
                [
                    PpToken.PpToken('3',      'pp-number'),
                ],
            ]
        myActualArgTokens = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual(myExpectedArgTokens, myActualArgTokens)

    def testCppretArgumentListTokens_07(self):
        """PpDefine.retArgumentListTokens() - #define t(a) a\\n and invoke t()."""
        myCppDef = self._retCheckedMacro(
                            't(a) a\n',
                            False,
                            7,
                            't',
                            ['a',],
                            ['a',],
                        )
        self.assertEqual(
            [
                PpToken.PpToken('a',     'identifier'),
            ],
            myCppDef.replacementTokens
        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(')')
            )
        myGen = myCpp.next()
        myExpectedArgTokens = [None,]
        myActualArgTokens = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual(myExpectedArgTokens, myActualArgTokens)

    def testCppretArgumentListTokens_08(self):
        """PpDefine.retArgumentListTokens() - Whitespace removal."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(' 1,2 ,3 )')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testCpp_retReplacementMap_00(self):
        """PpDefine._retReplacementMap() - All arguments."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        self.assertEqual(
                    {
                    'a' : [
                            PpToken.PpToken('1', 'pp-number'),
                        ],
                    'b' : [
                            PpToken.PpToken('2', 'pp-number'),
                        ],
                    'c' : [
                            PpToken.PpToken('3', 'pp-number'),
                            #('+', 'preprocessing-op-or-punc'),
                            #('7', 'pp-number')
                        ],
                    },
                    myReplaceMap)

    def testCpp_retReplacementMap_01(self):
        """PpDefine._retReplacementMap() - Missing leading argument."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(',2,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                myCppDef.PLACEMARKER,
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        self.assertEqual(
                    {
                    'a' : myCppDef.PLACEMARKER,
                    'b' : [
                            PpToken.PpToken('2', 'pp-number'),
                        ],
                    'c' : [
                            PpToken.PpToken('3', 'pp-number'),
                            #('+', 'preprocessing-op-or-punc'),
                            #('7', 'pp-number')
                        ],
                    },
                    myReplaceMap)

    def testCpp_retReplacementMap_02(self):
        """PpDefine._retReplacementMap() - Missing trailing argument."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2,)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                myCppDef.PLACEMARKER,
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        self.assertEqual(
                    {
                    'a' : [
                            PpToken.PpToken('1', 'pp-number'),
                          ],
                    'b' : [
                            PpToken.PpToken('2', 'pp-number'),
                        ],
                    'c' : myCppDef.PLACEMARKER,
                    },
                    myReplaceMap)

    def testCpp_retReplacementMap_03(self):
        """PpDefine._retReplacementMap() - Missing middle argument."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                myCppDef.PLACEMARKER,
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        self.assertEqual(
                    {
                    'a' : [
                            PpToken.PpToken('1', 'pp-number'),
                          ],
                    'b' : myCppDef.PLACEMARKER,
                    'c' : [
                            PpToken.PpToken('3', 'pp-number'),
                        ],
                    },
                    myReplaceMap)

    def testCpp_retReplacementMap_04(self):
        """PpDefine._retReplacementMap() - Missing all arguments."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(',,)')
            )
        myGen = myCpp.next()
        myArgTokens = [
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        self.assertEqual(
                    {
                    'a' : myCppDef.PLACEMARKER,
                    'b' : myCppDef.PLACEMARKER,
                    'c' : myCppDef.PLACEMARKER,
                    },
                    myReplaceMap)

    def testCpp_functionLikeReplacement_00(self):
        """PpDefine._functionLikeReplacement() - cpp.concat: #define q(x,y) x ## y\\n with: q(A,B) -> AB"""
        # #define q(x,y) x ## y
        # q(A,B);
        myCppDef = self._retCheckedMacro(
                            'q(x,y) x ## y\n',
                            False,
                            13,
                            'q',
                            ['x', 'y',],
                            ['x', ' ', '##', ' ', 'y'],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('A,B)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('A',       'identifier'),
                ],
                [
                    PpToken.PpToken('B',       'identifier'),
                ],
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        self.assertEqual(
                    {
                    'x' : [
                            PpToken.PpToken('A',       'identifier'),
                        ],
                    'y' : [
                            PpToken.PpToken('B',       'identifier'),
                        ],
                    },
                    myReplaceMap)
        myReplacementS = myCppDef._functionLikeReplacement(myReplaceMap)
        #self.pprintReplacementList(myReplacementS)
        myExpectedReplTokens = [
                PpToken.PpToken('AB',       'identifier'),
            ]
        self._printDiff(myReplacementS, myExpectedReplTokens)
        self.assertEqual(myExpectedReplTokens, myReplacementS)

    def testCpp_functionLikeReplacement_01(self):
        """PpDefine._functionLikeReplacement() - cpp.concat: #define qq(x,y,z) x ## y ## z\\n with: qq(A,B,C) -> ABC"""
        # #define q(x,y,z) x ## y ## z
        # q(A,B);
        myCppDef = self._retCheckedMacro(
                            'qq(x,y,z) x ## y ## z\n',
                            False,
                            19,
                            'qq',
                            ['x', 'y', 'z'],
                            ['x', ' ', '##', ' ', 'y', ' ', '##', ' ', 'z'],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('A,B,C)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('A',       'identifier'),
                ],
                [
                    PpToken.PpToken('B',       'identifier'),
                ],
                [
                    PpToken.PpToken('C',       'identifier'),
                ],
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        self.assertEqual(
                    {
                    'x' : [
                            PpToken.PpToken('A',       'identifier'),
                        ],
                    'y' : [
                            PpToken.PpToken('B',       'identifier'),
                        ],
                    'z' : [
                            PpToken.PpToken('C',       'identifier'),
                        ],
                    },
                    myReplaceMap)
        myReplacementS = myCppDef._functionLikeReplacement(myReplaceMap)
        #self.pprintReplacementList(myReplacementS)
        myExpectedReplTokens = [
                PpToken.PpToken('ABC',       'identifier'),
            ]
        self.assertEqual(myExpectedReplTokens, myReplacementS)

    def testCpp_functionLikeReplacement_02(self):
        """PpDefine._functionLikeReplacement() - cpp.concat: #define qq(x,y,z) x ## y ## z\\n with: qq(A,,C) -> AC"""
        # #define q(x,y,z) x ## y ## z
        # q(A,B);
        myCppDef = self._retCheckedMacro(
                            'qq(x,y,z) x ## y ## z\n',
                            False,
                            19,
                            'qq',
                            ['x', 'y', 'z'],
                            ['x', ' ', '##', ' ', 'y', ' ', '##', ' ', 'z'],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('A,,C)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('A',       'identifier'),
                ],
                myCppDef.PLACEMARKER,
                [
                    PpToken.PpToken('C',       'identifier'),
                ],
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        #print '\n  TRACE: myArgList:', myArgList
        #print 'TRACE: myArgTokens:', myArgTokens
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        self.assertEqual(
                    {
                    'x' : [
                            PpToken.PpToken('A',       'identifier'),
                        ],
                    'y' : myCppDef.PLACEMARKER,
                    'z' : [
                            PpToken.PpToken('C',       'identifier'),
                        ],
                    },
                    myReplaceMap)
        myReplacementS = myCppDef._functionLikeReplacement(myReplaceMap)
        #self.pprintReplacementList(myReplacementS)
        myExpectedReplTokens = [
                PpToken.PpToken('AC',       'identifier'),
            ]
        self._printDiff(myReplacementS, myExpectedReplTokens)
        self.assertEqual(myExpectedReplTokens, myReplacementS)

    def testCpp_functionLikeReplacement_03(self):
        """PpDefine._functionLikeReplacement() - cpp.concat: #define qq(x,y,z) x ## y ## z\\n with: qq(,,C) -> C"""
        # #define q(x,y,z) x ## y ## z
        # q(A,B);
        myCppDef = self._retCheckedMacro(
                            'qq(x,y,z) x ## y ## z\n',
                            False,
                            19,
                            'qq',
                            ['x', 'y', 'z'],
                            ['x', ' ', '##', ' ', 'y', ' ', '##', ' ', 'z'],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(',,C)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                myCppDef.PLACEMARKER,
                myCppDef.PLACEMARKER,
                [
                    PpToken.PpToken('C',       'identifier'),
                ],
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        self.assertEqual(
                    {
                    'x' : myCppDef.PLACEMARKER,
                    'y' : myCppDef.PLACEMARKER,
                    'z' : [
                            PpToken.PpToken('C',       'identifier'),
                        ],
                    },
                    myReplaceMap)
        myReplacementS = myCppDef._functionLikeReplacement(myReplaceMap)
        #self.pprintReplacementList(myReplacementS)
        myExpectedReplTokens = [
                PpToken.PpToken('C',       'identifier'),
            ]
        self.assertEqual(myExpectedReplTokens, myReplacementS)

    def testCpp_functionLikeReplacement_04(self):
        """PpDefine._functionLikeReplacement() - cpp.concat: #define qq(x,y,z) x ## y ## z\\n with: qq(,,) -> """
        # #define q(x,y,z) x ## y ## z
        # q(A,B);
        myCppDef = self._retCheckedMacro(
                            'qq(x,y,z) x ## y ## z\n',
                            False,
                            19,
                            'qq',
                            ['x', 'y', 'z'],
                            ['x', ' ', '##', ' ', 'y', ' ', '##', ' ', 'z'],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(',,)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                myCppDef.PLACEMARKER,
                myCppDef.PLACEMARKER,
                myCppDef.PLACEMARKER,
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        self.assertEqual(
                    {
                    'x' : myCppDef.PLACEMARKER,
                    'y' : myCppDef.PLACEMARKER,
                    'z' : myCppDef.PLACEMARKER,
                    },
                    myReplaceMap)
        myReplacementS = myCppDef._functionLikeReplacement(myReplaceMap)
        #self.pprintReplacementList(myReplacementS)
        myExpectedReplTokens = [
            ]
        self.assertEqual(myExpectedReplTokens, myReplacementS)

    def testCpp_functionLikeReplacement_05(self):
        """PpDefine._functionLikeReplacement() - cpp.concat: #define qq(x,y,z) x ## y ## z\\n with: qq(A,,) -> A"""
        # #define q(x,y,z) x ## y ## z
        # q(A,B);
        myCppDef = self._retCheckedMacro(
                            'qq(x,y,z) x ## y ## z\n',
                            False,
                            19,
                            'qq',
                            ['x', 'y', 'z'],
                            ['x', ' ', '##', ' ', 'y', ' ', '##', ' ', 'z'],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('A,,)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('A',       'identifier'),
                ],
                myCppDef.PLACEMARKER,
                myCppDef.PLACEMARKER,
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        self.assertEqual(
                    {
                    'x' : [
                            PpToken.PpToken('A',       'identifier'),
                        ],
                    'y' : myCppDef.PLACEMARKER,
                    'z' : myCppDef.PLACEMARKER,
                    },
                    myReplaceMap)
        myReplacementS = myCppDef._functionLikeReplacement(myReplaceMap)
        #self.pprintReplacementList(myReplacementS)
        myExpectedReplTokens = [
                PpToken.PpToken('A',       'identifier'),
            ]
        self.assertEqual(myExpectedReplTokens, myReplacementS)

class TestPpDefineFunctionLikeBadArguments(TestPpDefine):
    """Tests PpDefine low level functionality. Function style macros only."""

    def test_00(self):
        """TestPpDefineFunctionLikeBadArguments.test_00() - FUNCTION_STYLE(a,b,c) fails with no arguments."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(')')
            )
        myGen = myCpp.next()
        myArgTokens = [
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            ]
        self.assertRaises(
                PpDefine.ExceptionCpipDefineBadArguments,
                myCppDef.retArgumentListTokens,
                myGen,
                )

    def test_01(self):
        """TestPpDefineFunctionLikeBadArguments.test_01() - FUNCTION_STYLE(a,b,c) fails with one argument."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1)')
            )
        myGen = myCpp.next()
        myArgTokens = [
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            ]
        self.assertRaises(
                PpDefine.ExceptionCpipDefineBadArguments,
                myCppDef.retArgumentListTokens,
                myGen,
                )

    def test_02(self):
        """TestPpDefineFunctionLikeBadArguments.test_02() - FUNCTION_STYLE(a,b,c) fails with two arguments."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2)')
            )
        myGen = myCpp.next()
        myArgTokens = [
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            ]
        self.assertRaises(
                PpDefine.ExceptionCpipDefineBadArguments,
                myCppDef.retArgumentListTokens,
                myGen,
                )

    def test_04(self):
        """TestPpDefineFunctionLikeBadArguments.test_04() - FUNCTION_STYLE(a,b,c) fails with four arguments."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_STYLE(a,b,c) \n',
                            False,
                            9,
                            'FUNCTION_STYLE',
                            ['a', 'b', 'c',],
                            [],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2,3,4)')
            )
        myGen = myCpp.next()
        myArgTokens = [
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            myCppDef.PLACEMARKER,
            ]
        self.assertRaises(
                PpDefine.ExceptionCpipDefineBadArguments,
                myCppDef.retArgumentListTokens,
                myGen,
                )

class TestPpDefineFunctionLikeAcceptableArguments(TestPpDefine):
    """Tests PpDefine low level functionality for function style macros.

Test code with cpp.exe:
START_F_0
#define F_0() |-| EOL
F_0()        // |-| EOL
F_0(1)        // F_0 func_args.h:4:6: macro "F_0" passed 1 arguments, but takes just 0
END_F_0

START_F_1
#define F_1(a) |a| EOL
F_1()        // | | EOL
F_1(1)        // |1| EOL
F_1(1,2)    // F_1 func_args.h:11:8: macro "F_1" passed 2 arguments, but takes just 1
F_1(,)        // F_1 func_args.h:12:6: macro "F_1" passed 2 arguments, but takes just 1
END_F_1

START_F_2
#define F_2(a,b) |a|b| EOL
F_2()        // error
F_2(1)        // error
F_2(1,2)    // |a|b| EOL
F_2(1,2,3)    // error
F_2(,)        // | | | EOL
F_2(,,)        // error
END_F_2

    """

    def test_00(self):
        """TestPpDefineFunctionLikeAcceptableArguments.test_00() - FUNCTION_LIKE() succeeds with no arguments."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_LIKE() |-|\n',
                            False,
                            8,
                            'FUNCTION_LIKE',
                            [],
                            ['|', '-', '|'],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(')')
            )
        myGen = myCpp.next()
        myExpArgTokens = []
        myArgTokens = myCppDef.retArgumentListTokens(myGen)
        # print
        # print 'TRACE:', myArgTokens
        self.assertEquals(myExpArgTokens, myArgTokens)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        #myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
        myReplaceToks = myCppDef.replaceArgumentList(myArgTokens)
        #self.pprintReplacementList(myReplaceToks)
        myExpectedTokens = [
                PpToken.PpToken('|',       'preprocessing-op-or-punc'),
                PpToken.PpToken('-',       'preprocessing-op-or-punc'),
                PpToken.PpToken('|',       'preprocessing-op-or-punc'),
            ]
        self._printDiff(myReplaceToks, myExpectedTokens)
        self.assertEqual(myExpectedTokens, myReplaceToks)
        
    def test_01(self):
        """TestPpDefineFunctionLikeAcceptableArguments.test_01() - FUNCTION_LIKE() fails with one argument."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_LIKE() |-|\n',
                            False,
                            8,
                            'FUNCTION_LIKE',
                            [],
                            ['|', '-', '|'],
                        )
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1)')
            )
        myGen = myCpp.next()
        myExpArgTokens = [
                [
                 PpToken.PpToken('1',       'pp-number'),
                 ],
            ]
        self.assertRaises(
                PpDefine.ExceptionCpipDefineBadArguments,
                myCppDef.retArgumentListTokens,
                myGen,
                )
        
    def test_02(self):
        """TestPpDefineFunctionLikeAcceptableArguments.test_02() - FUNCTION_LIKE() fails with two arguments."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_LIKE() |-|\n',
                            False,
                            8,
                            'FUNCTION_LIKE',
                            [],
                            ['|', '-', '|'],
                        )
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2)')
            )
        myGen = myCpp.next()
        myExpArgTokens = [
                [
                 PpToken.PpToken('1',       'pp-number'),
                 ],
                [
                 PpToken.PpToken('2',       'pp-number'),
                 ],
            ]
        self.assertRaises(
                PpDefine.ExceptionCpipDefineBadArguments,
                myCppDef.retArgumentListTokens,
                myGen,
                )

    def test_10(self):
        """TestPpDefineFunctionLikeAcceptableArguments.test_10() - FUNCTION_LIKE(a) succeeds with no arguments."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_LIKE(a) |a|\n',
                            False,
                            9,
                            'FUNCTION_LIKE',
                            ['a',],
                            ['|', 'a', '|'],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(')')
            )
        myGen = myCpp.next()
        myExpArgTokens = [
            myCppDef.PLACEMARKER,
            ]
        myArgTokens = myCppDef.retArgumentListTokens(myGen)
        #print
        #print 'TRACE:', myArgTokens
        self.assertEquals(myExpArgTokens, myArgTokens)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
        #print 'TRACE: ', myReplaceMap 
        myReplaceToks = myCppDef.replaceArgumentList(myArgTokens)
        #self.pprintReplacementList(myReplaceToks)
        myExpectedArgTokens = [
                PpToken.PpToken('|',       'preprocessing-op-or-punc'),
                PpToken.PpToken('|',       'preprocessing-op-or-punc'),
            ]
        #print
        #print 'TRACE:       myReplaceToks', [str(x) for x in myReplaceToks]
        #print 'TRACE: myExpectedArgTokens', [str(x) for x in myExpectedArgTokens]
        self._printDiff(myReplaceToks, myExpectedArgTokens)
        self.assertEqual(myExpectedArgTokens, myReplaceToks)
        
    def test_11(self):
        """TestPpDefineFunctionLikeAcceptableArguments.test_11() - FUNCTION_LIKE(a) succeeds with one argument."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_LIKE(a) |a|\n',
                            False,
                            9,
                            'FUNCTION_LIKE',
                            ['a',],
                            ['|', 'a', '|'],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1)')
            )
        myGen = myCpp.next()
        myExpArgTokens = [
                [
                 PpToken.PpToken('1',       'pp-number'),
                 ],
            ]
        myArgTokens = myCppDef.retArgumentListTokens(myGen)
        # print
        # print 'TRACE:', myArgTokens
        self.assertEquals(myExpArgTokens, myArgTokens)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        #myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
        myReplaceToks = myCppDef.replaceArgumentList(myArgTokens)
        #self.pprintReplacementList(myReplaceToks)
        myExpectedArgTokens = [
                PpToken.PpToken('|',       'preprocessing-op-or-punc'),
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken('|',       'preprocessing-op-or-punc'),
            ]
        #print
        #print 'TRACE:       myReplaceToks', [str(x) for x in myReplaceToks]
        #print 'TRACE: myExpectedArgTokens', [str(x) for x in myExpectedArgTokens]
        self._printDiff(myReplaceToks, myExpectedArgTokens)
        self.assertEqual(myExpectedArgTokens, myReplaceToks)
        
    def test_12(self):
        """TestPpDefineFunctionLikeAcceptableArguments.test_12() - FUNCTION_LIKE(a) fails with two argument."""
        myCppDef = self._retCheckedMacro(
                            'FUNCTION_LIKE(a) |a|\n',
                            False,
                            9,
                            'FUNCTION_LIKE',
                            ['a',],
                            ['|', 'a', '|'],
                        )
        # Missing leading argument
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2)')
            )
        myGen = myCpp.next()
        myExpArgTokens = [
                [
                 PpToken.PpToken('1',       'pp-number'),
                 ],
                [
                 PpToken.PpToken('2',       'pp-number'),
                 ],
            ]
        self.assertRaises(
                PpDefine.ExceptionCpipDefineBadArguments,
                myCppDef.retArgumentListTokens,
                myGen,
                )

    """Test code with cpp.exe:
START_F_0
#define F_0() |-| EOL
F_0()        // |-| EOL
F_0(1)        // F_0 func_args.h:4:6: macro "F_0" passed 1 arguments, but takes just 0
END_F_0

START_F_1
#define F_1(a) |a| EOL
F_1()        // | | EOL
F_1(1)        // |1| EOL
F_1(1,2)    // F_1 func_args.h:11:8: macro "F_1" passed 2 arguments, but takes just 1
F_1(,)        // F_1 func_args.h:12:6: macro "F_1" passed 2 arguments, but takes just 1
END_F_1

START_F_2
#define F_2(a,b) |a|b| EOL
F_2()            // func_args.h:17:5: macro "F_2" requires 2 arguments, but only 1 given
F_2(1)           // func_args.h:18:6: macro "F_2" requires 2 arguments, but only 1 given
F_2(1,2)         // |1|2| EOL
F_2(1,2,3)       // func_args.h:20:10: macro "F_2" passed 3 arguments, but takes just 2
F_2(,)           // | | | EOL
F_2(,,)          // func_args.h:22:7: macro "F_2" passed 3 arguments, but takes just 2
END_F_2"""

    def test_F_0(self):
        """TestPpDefineFunctionLikeAcceptableArguments.test_F_0() - F_0()."""
        # #define F_0() |-| EOL
        # F_0()        // |-| EOL
        # F_0(1)        // F_0 func_args.h:4:6: macro "F_0" passed 1 arguments, but takes just 0
        myCppDef = self._retCheckedMacro(
                            'F_0() |-| EOL\n',
                            False,
                            10,
                            'F_0',
                            [],
                            ['|', '-', '|', ' ', 'EOL'],
                        )
        myArgsExpToksAndReplMap = (
                # F_0()
                (
                    ')',
                    [],
                    {},
                    self.stringToTokens('|-| EOL'),
                  ),
                # F_0(1)
                (
                    '1)',
                    None,
                    None,
                    None,
                  ),
                # F_0(1,2)
                (
                    '1,2)',
                    None,
                    None,
                    None,
                  ),
              )
        #print
        #print 'TRACE:  parameters:', myCppDef.parameters
        for inToks, expArgToks, expRepMap, expReprToks in myArgsExpToksAndReplMap:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(inToks)
                )
            myGen = myCpp.next()
            if expArgToks is None:
                self.assertRaises(
                    PpDefine.ExceptionCpipDefineBadArguments,
                    myCppDef.retArgumentListTokens,
                    myGen,
                    )
            else:
                myArgTokens = myCppDef.retArgumentListTokens(myGen)
                #print 'TRACE: myArgTokens:', myArgTokens
                self.assertEquals(expArgToks, myArgTokens)
                # Check that all tokens have been consumed
                self.assertRaises(StopIteration, myGen.__next__)
                myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
                #print 'TRACE:  map:', myReplaceMap
                self.assertEquals(expRepMap, myReplaceMap)
                myReplacements = myCppDef._functionLikeReplacement(myReplaceMap)
                #print 'TRACE:  out:', myReplacements
                self.assertEquals(expReprToks, myReplacements)

    def test_F_1(self):
        """TestPpDefineFunctionLikeAcceptableArguments.test_F_1() - F_1(a)."""
        # #define F_1(a) |a| EOL
        # F_1()        // | | EOL
        # F_1(1)        // |1| EOL
        # F_1(1,2)    // F_1 func_args.h:11:8: macro "F_1" passed 2 arguments, but takes just 1
        # F_1(,)        // F_1 func_args.h:12:6: macro "F_1" passed 2 arguments, but takes just 1
        myCppDef = self._retCheckedMacro(
                            'F_1(a) |a| EOL\n',
                            False,
                            11,
                            'F_1',
                            ['a',],
                            ['|', 'a', '|', ' ', 'EOL'],
                        )
        myArgsExpToksAndReplMap = (
                # F_1()
                (
                    ')',
                    [myCppDef.PLACEMARKER, ],
                    {'a' : myCppDef.PLACEMARKER},
                    self.stringToTokens('|')+self.stringToTokens('| EOL'),
                  ),
                # F_1(1)
                (
                    '1)',
                    [
                        self.stringToTokens('1'),
                        ],
                    {'a' : self.stringToTokens('1')},
                    self.stringToTokens('|1| EOL'),
                  ),
                # F_1(1,2)
                (
                    '1,2)',
                    None,
                    None,
                    None,
                  ),
                # F_1(,)
                (
                    ',)',
                    None,
                    None,
                    None,
                  ),
              )
        #print
        #print 'TRACE:  parameters:', myCppDef.parameters
        for inToks, expArgToks, expRepMap, expReprToks in myArgsExpToksAndReplMap:
            #print 'TRACE:  inToks:', inToks
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(inToks)
                )
            myGen = myCpp.next()
            if expArgToks is None:
                self.assertRaises(
                    PpDefine.ExceptionCpipDefineBadArguments,
                    myCppDef.retArgumentListTokens,
                    myGen,
                    )
            else:
                myArgTokens = myCppDef.retArgumentListTokens(myGen)
                #print 'TRACE: myArgTokens:', myArgTokens
                self.assertEquals(expArgToks, myArgTokens)
                # Check that all tokens have been consumed
                self.assertRaises(StopIteration, myGen.__next__)
                myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
                #print 'TRACE:  map:', myReplaceMap
                self.assertEquals(expRepMap, myReplaceMap)
                myReplacements = myCppDef._functionLikeReplacement(myReplaceMap)
                #print 'TRACE:  out:', myReplacements
                self.assertEquals(expReprToks, myReplacements)

    def test_F_2(self):
        """TestPpDefineFunctionLikeAcceptableArguments.test_F_2() - F_2(a,b)."""
        #START_F_2
        ##define F_2(a,b) |a|b| EOL
        #F_2()            // func_args.h:17:5: macro "F_2" requires 2 arguments, but only 1 given
        #F_2(1)           // func_args.h:18:6: macro "F_2" requires 2 arguments, but only 1 given
        #F_2(1,2)         // |1|2| EOL
        #F_2(1,2,3)       // func_args.h:20:10: macro "F_2" passed 3 arguments, but takes just 2
        #F_2(,)           // | | | EOL
        #F_2(,,)          // func_args.h:22:7: macro "F_2" passed 3 arguments, but takes just 2
        myCppDef = self._retCheckedMacro(
                            'F_2(a,b) |a|b| EOL\n',
                            False,
                            15,
                            'F_2',
                            ['a', 'b', ],
                            ['|', 'a', '|', 'b', '|', ' ', 'EOL'],
                        )
        myArgsExpToksAndReplMap = (
                # F_2()
                (
                    ')',
                    None,
                    None,
                    None,
                  ),
                # F_2(1)
                (
                    '1)',
                    None,
                    None,
                    None,
                  ),
                # F_2(1,2)
                (
                    '1,2)',
                    [
                        self.stringToTokens('1'),
                        self.stringToTokens('2'),
                        ],
                    {
                        'a' : self.stringToTokens('1'),
                        'b' : self.stringToTokens('2'),
                    },
                    self.stringToTokens('|1|2| EOL'),
                  ),
                # F_2(1,2,3)
                (
                    '1,2,3)',
                    None,
                    None,
                    None,
                  ),
                # F_2(,)
                (
                    ',)',
                    [myCppDef.PLACEMARKER, myCppDef.PLACEMARKER],
                    {
                        'a' : myCppDef.PLACEMARKER,
                        'b' : myCppDef.PLACEMARKER,
                    },
                    self.stringToTokens('|')+ self.stringToTokens('|')+self.stringToTokens('| EOL'),
                  ),
                # F_2(,,)
                (
                    ',,)',
                    None,
                    None,
                    None,
                  ),
              )
        #print
        #print 'TRACE:  parameters:', myCppDef.parameters
        for inToks, expArgToks, expRepMap, expReprToks in myArgsExpToksAndReplMap:
            #print 'TRACE:  inToks:', inToks
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(inToks)
                )
            myGen = myCpp.next()
            if expArgToks is None:
                self.assertRaises(
                    PpDefine.ExceptionCpipDefineBadArguments,
                    myCppDef.retArgumentListTokens,
                    myGen,
                    )
            else:
                myArgTokens = myCppDef.retArgumentListTokens(myGen)
                #print 'TRACE: myArgTokens:', myArgTokens
                self.assertEquals(expArgToks, myArgTokens)
                # Check that all tokens have been consumed
                self.assertRaises(StopIteration, myGen.__next__)
                myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
                #print 'TRACE:  map:', myReplaceMap
                self.assertEquals(expRepMap, myReplaceMap)
                myReplacements = myCppDef._functionLikeReplacement(myReplaceMap)
                #print 'TRACE:  out:', myReplacements
                self.assertEquals(expReprToks, myReplacements)

    def test_F_2_errors(self):
        """TestPpDefineFunctionLikeAcceptableArguments.test_F_2() - F_2(a,b) error messages."""
        #START_F_2
        ##define F_2(a,b) |a|b| EOL
        #F_2()            // func_args.h:17:5: macro "F_2" requires 2 arguments, but only 1 given
        #F_2(1)           // func_args.h:18:6: macro "F_2" requires 2 arguments, but only 1 given
        #F_2(1,2)         // |1|2| EOL
        #F_2(1,2,3)       // func_args.h:20:10: macro "F_2" passed 3 arguments, but takes just 2
        #F_2(,)           // | | | EOL
        #F_2(,,)          // func_args.h:22:7: macro "F_2" passed 3 arguments, but takes just 2
        myCppDef = self._retCheckedMacro(
                            'F_2(a,b) |a|b| EOL\n',
                            False,
                            15,
                            'F_2',
                            ['a', 'b', ],
                            ['|', 'a', '|', 'b', '|', ' ', 'EOL'],
                        )
        myToksList = (
                # F_2()
                (
                    ')',
                    'macro "F_2" requires 2 arguments, but only 1 given',
                ),
                # F_2(1)
                (
                    '1)',
                    'macro "F_2" requires 2 arguments, but only 1 given',
                ),
                # F_2(1,2,3)
                (
                    '1,2,3)',
                    'macro "F_2" passed 3 arguments, but takes just 2',
                ),
                # F_2(,,)
                (
                    ',,)',
                    'macro "F_2" passed 3 arguments, but takes just 2',
                ),
                # F_2(,2,3)
                (
                    ',2,3)',
                    'macro "F_2" passed 3 arguments, but takes just 2',
                ),
                # F_2(1,,3)
                (
                    '1,,3)',
                    'macro "F_2" passed 3 arguments, but takes just 2',
                ),
                # F_2(1,2,)
                (
                    '1,2,)',
                    'macro "F_2" passed 3 arguments, but takes just 2',
                ),
              )
        #print
        #print 'TRACE:  parameters:', myCppDef.parameters
        for inToks, errMsg in myToksList:
            #print 'TRACE:  inToks:', inToks
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(inToks)
                )
            myGen = myCpp.next()
            try:
                myCppDef.retArgumentListTokens(myGen)
                self.fail('PpDefine.ExceptionCpipDefineBadArguments not raised')
            except PpDefine.ExceptionCpipDefineBadArguments as err:
                self.assertEquals(errMsg, str(err))
                

class TestConcatFunctionLikeMacro(TestPpDefine):
    """Tests #define r(x,y) x ## y with various combinations of arguments."""
    def testCppConcat_Function_00(self):
        """PpDefine: ISO/IEC ISO/IEC 14882:1998(E) 16.3.3 The ## operator [cpp.concat]: #define r(x,y) x ## y called with r(4,) etc.."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('r(x,y) x ## y\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(13, myCppDef.tokensConsumed)
        self.assertEqual('r', myCppDef.identifier)
        self.assertEqual(['x', 'y'], myCppDef.parameters)
        self.assertEqual(['x', ' ', '##', ' ', 'y'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Go through r(2,3), r(4,), r(,5), r(,)
        #
        myInOut = (
            ('2,3)',    '23'),
            ('4,)',     '4'),
            (',5)',     '5'),
            (',)',      ''),
            )
        for strIn, strOut in myInOut:
            #print
            #print 'strIn', strIn
            #print 'strOut', strOut
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(strIn)
                )
            myGen = myCpp.next()
            myArgList = myCppDef.retArgumentListTokens(myGen)
            # Check that all tokens have been consumed
            self.assertRaises(StopIteration, myGen.__next__)
            #myReplaceMap = myCppDef._retReplacementMap(myArgList)
            myReplaceToks = myCppDef.replaceArgumentList(myArgList)
            #self.pprintReplacementList(myReplacementS)
            myExpectedReplTokens = self.stringToTokens(strOut)
            self._printDiff(myReplaceToks, myExpectedReplTokens)
            self.assertEqual(myExpectedReplTokens, myReplaceToks)

class TestPpDefineCppStringize(TestPpDefine):
    """Tests PpDefine handling of '#'. Function style macros only."""

    def testCppStringizeFunction_00(self):
        """PpDefine: ISO/IEC ISO/IEC 14882:1998(E) 16.3.2 The # operator [cpp.stringize]: checking PpDefine._cppStringize()."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a) # a\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(9, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a',], myCppDef.parameters)
        self.assertEqual(['#', ' ', 'a'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check internal functions
        #
        # Empty token list
        myArgTokens = []
        self.assertEqual(
            myCppDef._cppStringize(myArgTokens),
            PpToken.PpToken('""',      'string-literal'),
            )
        # Various tokens
        myArgTokens = [
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('3',       'pp-number'),
            ]
        self.assertEqual(
            PpToken.PpToken('"1 +2+3"',      'string-literal'),
            myCppDef._cppStringize(myArgTokens)
            )
        # Empty string literal
        myArgTokens = [
                PpToken.PpToken('""',      'string-literal'),
            ]
        self.assertEqual(
            PpToken.PpToken('"\\"\\""',      'string-literal'),
            myCppDef._cppStringize(myArgTokens)
            )
        # String literal
        myArgTokens = [
                PpToken.PpToken('"xYz"',      'string-literal'),
            ]
        self.assertEqual(
            PpToken.PpToken('"\\"xYz\\""',      'string-literal'),
            myCppDef._cppStringize(myArgTokens)
            )
        # String literal
        myArgTokens = [
                PpToken.PpToken('"',       'string-literal'),
                PpToken.PpToken('xYz',     'identifier'),
                PpToken.PpToken('"',       'string-literal'),
            ]
        self.assertEqual(
            PpToken.PpToken('"\\"xYz\\""',      'string-literal'),
            myCppDef._cppStringize(myArgTokens)
            )
        # Leading whitespace
        myArgTokens = [
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('pQ',       'preprocessing-op-or-punc'),
            ]
        self.assertEqual(
            PpToken.PpToken('"pQ"',      'string-literal'),
            myCppDef._cppStringize(myArgTokens)
            )
        # Leading whitespace
        myArgTokens = [
                PpToken.PpToken('   ',       'whitespace'),
                PpToken.PpToken('pQ',       'preprocessing-op-or-punc'),
            ]
        self.assertEqual(
            PpToken.PpToken('"pQ"',      'string-literal'),
            myCppDef._cppStringize(myArgTokens)
            )
        # Leading whitespace
        myArgTokens = [
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('pQ',      'preprocessing-op-or-punc'),
            ]
        self.assertEqual(
            PpToken.PpToken('"pQ"',      'string-literal'),
            myCppDef._cppStringize(myArgTokens)
            )
        # Trailing whitespace
        myArgTokens = [
                PpToken.PpToken('pQ',      'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
            ]
        self.assertEqual(
            PpToken.PpToken('"pQ"',      'string-literal'),
            myCppDef._cppStringize(myArgTokens)
            )
        # Trailing whitespace
        myArgTokens = [
                PpToken.PpToken('pQ',       'preprocessing-op-or-punc'),
                PpToken.PpToken('   ',      'whitespace'),
            ]
        self.assertEqual(
            PpToken.PpToken('"pQ"',      'string-literal'),
            myCppDef._cppStringize(myArgTokens)
            )
        # Trailing whitespace
        myArgTokens = [
                PpToken.PpToken('pQ',      'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken(' ',       'whitespace'),
            ]
        self.assertEqual(
            PpToken.PpToken('"pQ"',      'string-literal'),
            myCppDef._cppStringize(myArgTokens)
            )

    def testCppStringizeFunction_01(self):
        """PpDefine: ISO/IEC ISO/IEC 14882:1998(E) 16.3.2 The # operator [cpp.stringize]: <#define> 'FOO(a) # a\\n' called with (123)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a) # a\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(9, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a',], myCppDef.parameters)
        self.assertEqual(['#', ' ', 'a'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(123)')
            )
        myGen = myCpp.next()
        # We simulate here what PpDefine.MacroReplacementEnv must do for function style
        # macros but without the rescanning and further replacement.
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('123',       'pp-number'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        myExpectedArgTokens = [
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('"123"',   'string-literal'),
            ]
        #print
        #print 'TRACE:       myReplaceToks', [str(x) for x in myReplaceToks]
        #print 'TRACE: myExpectedArgTokens', [str(x) for x in myExpectedArgTokens]
        self._printDiff(myReplaceToks, myExpectedArgTokens)
        self.assertEqual(myExpectedArgTokens, myReplaceToks)

    def testCppStringizeFunction_02(self):
        """PpDefine: ISO/IEC ISO/IEC 14882:1998(E) 16.3.2 The # operator [cpp.stringize]: <#define> 'FOO(a) # a\\n' called with (1(,)23)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a) # a\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(9, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a',], myCppDef.parameters)
        self.assertEqual(['#', ' ', 'a'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(1(,)23)')
            )
        myGen = myCpp.next()
        # We simulate here what PpDefine.MacroReplacementEnv must do for function style
        # macros but without the rescanning and further replacement.
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                    PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                    PpToken.PpToken(',',       'preprocessing-op-or-punc'),
                    PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                    PpToken.PpToken('23',      'pp-number'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        self.assertEqual(
            [
                PpToken.PpToken(' ',          'whitespace'),
                PpToken.PpToken('"1(,)23"',   'string-literal'),
            ],
            myReplaceToks,
            )

    def testCppStringizeFunction_03(self):
        """PpDefine: ISO/IEC ISO/IEC 14882:1998(E) 16.3.2 The # operator [cpp.stringize]: <#define> 'FOO(a) # a\\n' called with (c d e)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a) # a\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(9, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a',], myCppDef.parameters)
        self.assertEqual(['#', ' ', 'a'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(c d e)')
            )
        myGen = myCpp.next()
        # We simulate here what PpDefine.MacroReplacementEnv must do for function style
        # macros but without the rescanning and further replacement.
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('c',       'identifier'),
                    PpToken.PpToken(' ',       'whitespace'),
                    PpToken.PpToken('d',       'identifier'),
                    PpToken.PpToken(' ',       'whitespace'),
                    PpToken.PpToken('e',       'identifier'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        self.assertEqual(
            [
                PpToken.PpToken(' ',         'whitespace'),
                PpToken.PpToken('"c d e"',   'string-literal'),
            ],
            myReplaceToks,
            )

class TestPpDefineCppConcat(TestPpDefine):
    """Tests PpDefine handling of '##'. Object and function style macros."""

    def testCppConcat_Object_00(self):
        """PpDefine: ISO/IEC ISO/IEC 14882:1998(E) 16.3.3 The ## operator [cpp.concat]: PpDefine._objectLikeReplacement() 00."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('CONCAT a ## b\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(8, myCppDef.tokensConsumed)
        self.assertEqual('CONCAT', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['a', ' ', '##', ' ', 'b'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check internal functions
        #
        # Resulting tokens
        myArgTokens = [
                PpToken.PpToken('ab',      'identifier'),
            ]
        self.assertEqual(myArgTokens, myCppDef._objectLikeReplacement())

    def testCppConcat_Object_01(self):
        """PpDefine: ISO/IEC ISO/IEC 14882:1998(E) 16.3.3 The ## operator [cpp.concat]: PpDefine._objectLikeReplacement() 01."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('CONCAT a ## b ## c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(12, myCppDef.tokensConsumed)
        self.assertEqual('CONCAT', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['a', ' ', '##', ' ', 'b', ' ', '##', ' ', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check internal functions
        #
        # Resulting tokens
        myArgTokens = [
                PpToken.PpToken('abc',      'identifier'),
            ]
        self.assertEqual(myArgTokens, myCppDef._objectLikeReplacement())

    def testCppConcat_Object_02(self):
        """PpDefine: ISO/IEC ISO/IEC 14882:1998(E) 16.3.3 The ## operator [cpp.concat]: PpDefine._objectLikeReplacement() 02."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('hash_hash # ## #\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(8, myCppDef.tokensConsumed)
        self.assertEqual('hash_hash', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['#', ' ', '##', ' ', '#',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check internal functions
        #
        # Resulting tokens
        myArgTokens = [
                PpToken.PpToken('##', 'preprocessing-op-or-punc'),
            ]
        myReplaceTokens = myCppDef._objectLikeReplacement()
        self._printDiff(myArgTokens, myReplaceTokens)
        self.assertEqual(myArgTokens, myReplaceTokens)

    def testCppConcat_Object_03(self):
        """PpDefine: ISO/IEC ISO/IEC 14882:1998(E) 16.3.3 The ## operator [cpp.concat]: PpDefine._objectLikeReplacement() 03."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('CONCAT 1 ## A\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(8, myCppDef.tokensConsumed)
        self.assertEqual('CONCAT', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['1', ' ', '##', ' ', 'A',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check internal functions
        #
        # Resulting tokens
        myArgTokens = [
                PpToken.PpToken('1A',      'concat'),
            ]
        myReplaceTokens = myCppDef._objectLikeReplacement()
        self._printDiff(myArgTokens, myReplaceTokens)
        self.assertEqual(myArgTokens, myReplaceTokens)

class TestPpDefineReplaceObjectStyle(TestPpDefine):
    """Tests the replace functionality of PpDefine of an object style macro
    i.e. single replacement."""

    def testReplaceObject_00(self):
        """PpDefine: Replacement OK from object type macro: <#define> 'FOO 1+2+3\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO 1+2+3\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(8, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['1', '+', '2', '+', '3'], myCppDef.replacements)
        self.assertEqual(
            [
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('3',       'pp-number'),
            ],
            myCppDef.replacementTokens,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myReplacements = myCppDef.replaceObjectStyleMacro()
        self.assertEqual(
            [
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('3',       'pp-number'),
            ],
            myReplacements,
            )

    def testReplaceObject_01(self):
        """PpDefine: Replacement OK from object type macro: <#define> 'FOO FOO\\n'."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO FOO\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(4, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['FOO'], myCppDef.replacements)
        self.assertEqual(
            [
                PpToken.PpToken('FOO',     'identifier'),
            ],
            myCppDef.replacementTokens,
            )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myReplacements = myCppDef.replaceObjectStyleMacro()
        self.assertEqual(
            [
                PpToken.PpToken('FOO',     'identifier'),
            ],
            myReplacements,
            )

    # Failures: None for object macros as it is so simple?

class TestPpDefineReplaceFunctionStyle(TestPpDefine):
    """Tests the replace functionality of PpDefine of an function style macro
    We simulate part of what PpDefine.MacroReplacementEnv must do to replace a function style
    macro."""

    def testReplaceFunction_00(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'FOO(a,b,c)\\n' called with FOO(1,2,3)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c)\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(9, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(1,2,3)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        self.assertEqual([], myReplaceToks)

    def testReplaceFunction_01(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'FOO(a,b,c) a+b+c\\n' called with FOO(1,2,3)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c) a+b+c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(15, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual(['a', '+', 'b', '+', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(1,2,3)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        self.assertEqual(
            [
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('3',       'pp-number'),
            ],
            myReplaceToks
            )

    def testReplaceFunction_02(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'FOO(a,b,c) a+b+c\\n' called with FOO(,2,3)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c) a+b+c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(15, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual(['a', '+', 'b', '+', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(,2,3)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                myCppDef.PLACEMARKER,
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        self.assertEqual(
            [
                #PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('3',       'pp-number'),
            ],
            myReplaceToks,
            )

    def testReplaceFunction_03(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'FOO(a,b,c) a+b+c\\n' called with FOO(1,,3)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c) a+b+c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(15, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual(['a', '+', 'b', '+', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(1,,3)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                myCppDef.PLACEMARKER,
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        self.assertEqual(
            [
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('3',       'pp-number'),
            ],
            myReplaceToks,
            )

    def testReplaceFunction_04(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'FOO(a,b,c) a+b+c\\n' called with FOO(1,2,)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c) a+b+c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(15, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual(['a', '+', 'b', '+', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(1,2,)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                myCppDef.PLACEMARKER,
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        self.assertEqual(
            [
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
            ],
            myReplaceToks,
            )

    def testReplaceFunction_05(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'FOO(a,b,c) a++b++c\\n' called with FOO(+,+,+)."""
        # cpp.exe behaviour:
        # #define FOO(a,b,c) a++b++c
        # FOO(+,+,+)
        # Gives
        # + +++ +++
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c) a++b++c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(15, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual(['a', '++', 'b', '++', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(+,+,+)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                ],
                [
                    PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                ],
                [
                    PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        self.assertEqual(
            [
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('++',      'preprocessing-op-or-punc'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('++',      'preprocessing-op-or-punc'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
            ],
            myReplaceToks,
            )

    def testReplaceFunction_06(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'p() int\\n' called with p()."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('p() int\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(6, myCppDef.tokensConsumed)
        self.assertEqual('p', myCppDef.identifier)
        #self.assertEqual([myCppDef.PLACEMARKER,], myCppDef.parameters)
        self.assertEqual([], myCppDef.parameters)
        self.assertEqual(['int'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('()')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = []
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        self.assertEqual(
            [
                PpToken.PpToken('int',     'identifier'),
            ],
            myReplaceToks,
            )

    def testReplaceFunction_07(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'q(x) x\\n' called with q()."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('q(x) x\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(7, myCppDef.tokensConsumed)
        self.assertEqual('q', myCppDef.identifier)
        self.assertEqual(['x'], myCppDef.parameters)
        self.assertEqual(['x'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('()')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [myCppDef.PLACEMARKER,]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        self.assertEqual(
            [],
            myReplaceToks,
            )

    def testReplaceFunction_08(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'r(x,y) x ## y\\n' called with r(2,3)"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('r(x,y) x ## y\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(13, myCppDef.tokensConsumed)
        self.assertEqual('r', myCppDef.identifier)
        self.assertEqual(['x', 'y'], myCppDef.parameters)
        self.assertEqual(['x', ' ', '##', ' ', 'y'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(2,3)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        #self.pprintReplacementList(myReplaceToks)
        self.assertEqual(
            [
                PpToken.PpToken('23',       'pp-number'),
            ],
            myReplaceToks,
            )

    def testReplaceFunction_09(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'f(a) a+a\\n' called with f(\\n1\\n) C: 6.10.3-10, C++: 16.3-9."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('f(a) a+a\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(9, myCppDef.tokensConsumed)
        self.assertEqual('f', myCppDef.identifier)
        self.assertEqual(['a',], myCppDef.parameters)
        self.assertEqual(['a', '+', 'a'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(\n1\n)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    #PpToken.PpToken('\n',         'whitespace'),
                    PpToken.PpToken('1',          'pp-number'),
                    #PpToken.PpToken('\n',         'whitespace'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        #self.pprintReplacementList(myReplaceToks)
        self.assertEqual(
            [
                #PpToken.PpToken(' ',         'whitespace'),
                PpToken.PpToken('1',          'pp-number'),
                #PpToken.PpToken(' ',         'whitespace'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                #PpToken.PpToken(' ',         'whitespace'),
                PpToken.PpToken('1',          'pp-number'),
                #PpToken.PpToken(' ',         'whitespace'),
            ],
            myReplaceToks,
            )

    def testReplaceFunction_10(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'f(a,b) a+b\\n' called with f(\\n1\\n,\\n2) C: 6.10.3-10, C++: 16.3-9."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('f(a,b) a+b\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(11, myCppDef.tokensConsumed)
        self.assertEqual('f', myCppDef.identifier)
        self.assertEqual(['a', 'b',], myCppDef.parameters)
        self.assertEqual(['a', '+', 'b'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(\n1\n,\n2\n)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('1',          'pp-number'),
                ],
                [
                    PpToken.PpToken('2',          'pp-number'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        #self.pprintReplacementList(myReplaceToks)
        self.assertEqual(
            [
                PpToken.PpToken('1',          'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',          'pp-number'),
            ],
            myReplaceToks,
            )

    def testReplaceFunction_20(self):
        """PpDefine: Replacement OK from function type macro: <#define> 'r(x,y) x ## y, y ## x\\n' called with r(2,3)"""
        # NOTE: This problem was discovered when processing Linux.
        # See the __ASM_SEL issue.
        # Essentially _functionLikeReplacement() was corrupting the map created
        # by _retReplacementMap() when doing concatenation.
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('r(x,y) x ## y, y ## x\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(20, myCppDef.tokensConsumed)
        self.assertEqual('r', myCppDef.identifier)
        self.assertEqual(['x', 'y'], myCppDef.parameters)
        self.assertEqual(
            ['x', ' ', '##', ' ', 'y', ',', ' ', 'y', ' ', '##', ' ', 'x'],
            myCppDef.replacements,
        )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(2,3)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        #self.pprintReplacementList(myReplaceToks)
        self.assertEqual(
            [
                PpToken.PpToken('23',       'pp-number'),
                PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',        'whitespace'),
                PpToken.PpToken('32',       'pp-number'),
            ],
            myReplaceToks,
            )


    # Testing failure
    def testReplaceFunction_50(self):
        """PpDefine: Replace bad from function type macro: <#define> 'FOO(a,b,c) a+b+c\\n' with FOO(1,2)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c) a+b+c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(15, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual(['a', '+', 'b', '+', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(1,2)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        self.assertRaises(PpDefine.ExceptionCpipDefineBadArguments, myCppDef.retArgumentListTokens, myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testReplaceFunction_51(self):
        """PpDefine: Replace bad from function type macro: <#define> 'FOO(a,b,c) a+b+c\\n' with FOO(1,2,3,4)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO(a,b,c) a+b+c\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(15, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(['a', 'b', 'c',], myCppDef.parameters)
        self.assertEqual(['a', '+', 'b', '+', 'c'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(1,2,3,4)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        self.assertRaises(PpDefine.ExceptionCpipDefineBadArguments, myCppDef.retArgumentListTokens, myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

class TestPpDefineExample5(TestPpDefine):
    """ISO/IEC 9899:1999 (E) 6.10.3.5-7 EXAMPLE 5
t(x,y,z) x ## y ## z
int j[] = { t(1,2,3), t(,4,5), t(6,,7), t(8,9,),
t(10,,), t(,11,), t(,,12), t(,,) };
"""

    def testExample5_00(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.5-7 EXAMPLE 5."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('t(x,y,z) x ## y ## z\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(19, myCppDef.tokensConsumed)
        self.assertEqual('t', myCppDef.identifier)
        self.assertEqual(['x', 'y', 'z',], myCppDef.parameters)
        self.assertEqual(
            ['x', ' ', '##', ' ', 'y', ' ', '##', ' ', 'z'],
            myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myInOut = (
            ('(1,2,3)',     '123'),
            ('(,4,5)',      '45'),
            ('(6,,7)',      '67'),
            ('(8,9,)',      '89'),
            ('(10,,)',      '10'),
            ('(,11,)',      '11'),
            ('(,,12)',      '12'),
            ('(,,)',        ''),
        )
        #print myInOut
        for aIn, aOut in myInOut:
            # Replacement
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(aIn)
                )
            myGen = myCpp.next()
            # First consume the preamble i.e. LPAREN
            self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
            # Now consume the arguments
            myArgS = myCppDef.retArgumentListTokens(myGen)
            # Check that all tokens have been consumed
            self.assertRaises(StopIteration, myGen.__next__)
            myReplaceToks = myCppDef.replaceArgumentList(myArgS)
            myExpectedReplTokens = self.stringToTokens(aOut)
            self._printDiff(myReplaceToks, myExpectedReplTokens)
            self.assertEqual(myReplaceToks, myExpectedReplTokens)

class TestPpDefineFileLine(TestPpDefine):
    """Tests the creation of PpDefine and accessing file and line number."""

    def testInitObject_00(self):
        """PpDefine.__init__(): OK from object type macro: <#define> 'FOO\\n' and accessing file and line number."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FOO\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'foo.h', 21)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(2, myCppDef.tokensConsumed)
        self.assertEqual('FOO', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual('foo.h', myCppDef.fileId)
        self.assertEqual(21, myCppDef.line)

    def testInitFail_00(self):
        """PpDefine.__init__(): Bad from object macro on line 0."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInitBadLine,
            PpDefine.PpDefine,
            myGen,
            '',
            0,
            )

class TestPpDefineRefCount(TestPpDefine):
    """Tests the creation of PpDefine and incrementing the reference count."""

    def testInitObject_00(self):
        """PpDefine.incRefCount(): OK from object type macro: <#define> 'SPAM\\n' incrementing and accessing the reference count."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM 1\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'spam.h', 7)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(4, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['1',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual('spam.h', myCppDef.fileId)
        self.assertEqual(7, myCppDef.line)
        self.assertEqual(0, myCppDef.refCount)
        self.assertFalse(myCppDef.isReferenced)
        myCppDef.incRefCount()
        self.assertEqual(1, myCppDef.refCount)
        self.assertTrue(myCppDef.isReferenced)
        myCppDef.incRefCount()
        self.assertEqual(2, myCppDef.refCount)
        self.assertTrue(myCppDef.isReferenced)

    def testInitObject_01(self):
        """PpDefine.incRefCount(): fails for #undef'd object like macro."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM 1\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'spam.h', 7)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(4, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['1',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual('spam.h', myCppDef.fileId)
        self.assertEqual(7, myCppDef.line)
        self.assertEqual(0, myCppDef.refCount)
        myCppDef.incRefCount()
        self.assertEqual(1, myCppDef.refCount)
        myCppDef.incRefCount()
        self.assertEqual(2, myCppDef.refCount)
        # #undef it and then try to increment the reference count
        myCppDef.undef('spam.h', 193)
        self.assertRaises(PpDefine.ExceptionCpipDefine, myCppDef.incRefCount)

    def testInitObject_02(self):
        """PpDefine.incRefCount(): Using FileLineCol update."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM 1\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'spam.h', 7)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(4, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['1',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual('spam.h', myCppDef.fileId)
        self.assertEqual(7, myCppDef.line)
        self.assertEqual(0, myCppDef.refCount)
        self.assertFalse(myCppDef.isReferenced)
        myCppDef.incRefCount(FileLocation.FileLineCol('spam.h', 173, 45))
        self.assertEqual(1, myCppDef.refCount)
        self.assertTrue(myCppDef.isReferenced)
        myCppDef.incRefCount(FileLocation.FileLineCol('eggs.h', 78, 98))
        self.assertEqual(2, myCppDef.refCount)
        self.assertTrue(myCppDef.isReferenced)
        #print
        #print [str(x) for x in myCppDef.refFileLineColS]
        self.assertEqual(
            [
             "FileLineCol(fileId='spam.h', lineNum=173, colNum=45)",
             "FileLineCol(fileId='eggs.h', lineNum=78, colNum=98)",
             ],
            [str(x) for x in myCppDef.refFileLineColS],
            )

class TestPpDefineUndef(TestPpDefine):
    """Tests the creation of PpDefine and incrementing the reference count."""

    def testUndef_00(self):
        """TestPpDefineUndef.testUndef_00(): Simple #undef."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM 1\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'spam.h', 7)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(4, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['1',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual('spam.h', myCppDef.fileId)
        self.assertEqual(7, myCppDef.line)
        self.assertEqual(0, myCppDef.refCount)
        self.assertTrue(myCppDef.isCurrentlyDefined)
        self.assertEqual('#define SPAM 1 /* spam.h#7 Ref: 0 True */', str(myCppDef))
        myCppDef.undef('spam.h', 73)
        self.assertFalse(myCppDef.isCurrentlyDefined)
        self.assertEqual('#define SPAM 1 /* spam.h#7 Ref: 0 False spam.h#73 */', str(myCppDef))
        
    def testUndef_01(self):
        """TestPpDefineUndef.testUndef_01(): double #undef fails."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM 1\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'spam.h', 7)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(4, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['1',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual('spam.h', myCppDef.fileId)
        self.assertEqual(7, myCppDef.line)
        self.assertEqual(0, myCppDef.refCount)
        self.assertTrue(myCppDef.isCurrentlyDefined)
        self.assertEqual('#define SPAM 1 /* spam.h#7 Ref: 0 True */', str(myCppDef))
        myCppDef.undef('spam.h', 73)
        self.assertFalse(myCppDef.isCurrentlyDefined)
        self.assertEqual('#define SPAM 1 /* spam.h#7 Ref: 0 False spam.h#73 */', str(myCppDef))
        self.assertRaises(PpDefine.ExceptionCpipDefine, myCppDef.undef, 'spam.h', 74)
        
    def testUndef_02(self):
        """TestPpDefineUndef.testUndef_02(): #undef on bad line fails."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('SPAM 1\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'spam.h', 7)
        self.assertEqual(True, myCppDef.isObjectTypeMacro)
        self.assertEqual(4, myCppDef.tokensConsumed)
        self.assertEqual('SPAM', myCppDef.identifier)
        self.assertEqual(None, myCppDef.parameters)
        self.assertEqual(['1',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual('spam.h', myCppDef.fileId)
        self.assertEqual(7, myCppDef.line)
        self.assertEqual(0, myCppDef.refCount)
        self.assertTrue(myCppDef.isCurrentlyDefined)
        self.assertEqual('#define SPAM 1 /* spam.h#7 Ref: 0 True */', str(myCppDef))
        self.assertRaises(PpDefine.ExceptionCpipDefine, myCppDef.undef, 'spam.h', 0)
        self.assertTrue(myCppDef.isCurrentlyDefined)
        
#===============================================================================
#        myCppDef.incRefCount()
#        self.assertEqual(1, myCppDef.refCount)
#        myCppDef.incRefCount()
#        self.assertEqual(2, myCppDef.refCount)
#===============================================================================

class TestPpDefineVariadic(TestPpDefine):
    """Tests variadic macros."""

    def testVariadicCtor_00(self):
        """TestPpDefineVariadic.testVariadicCtor_00(): Simple ctor."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FV(...) __VA_ARGS__\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'spam.h', 7)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(7, myCppDef.tokensConsumed)
        self.assertEqual('FV', myCppDef.identifier)
        self.assertEqual(['...',], myCppDef.parameters)
        self.assertEqual(['__VA_ARGS__',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual('spam.h', myCppDef.fileId)
        self.assertEqual(7, myCppDef.line)
        self.assertEqual(0, myCppDef.refCount)
        self.assertTrue(myCppDef.isCurrentlyDefined)
        self.assertEqual('#define FV(...) __VA_ARGS__ /* spam.h#7 Ref: 0 True */', str(myCppDef))
        myCppDef.undef('spam.h', 73)
        self.assertFalse(myCppDef.isCurrentlyDefined)
        self.assertEqual('#define FV(...) __VA_ARGS__ /* spam.h#7 Ref: 0 False spam.h#73 */', str(myCppDef))
        
    def testVariadicCtor_01(self):
        """TestPpDefineVariadic.testVariadicCtor_01(): Failure with ctor with spurious trailing arguments."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FV(...,a,b) __VA_ARGS__\n')
            )
        myGen = myCpp.next()
        self.assertRaises(PpDefine.ExceptionCpipDefineInit, PpDefine.PpDefine, myGen, 'spam.h', 7)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
    
    def testVariadicCtor_02(self):
        """TestPpDefineVariadic.testVariadicCtor_02(): Failure with function like ctor with __VA_ARGS__ but no ..."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FV(a,b) __VA_ARGS__\n')
            )
        myGen = myCpp.next()
        self.assertRaises(PpDefine.ExceptionCpipDefineInit, PpDefine.PpDefine, myGen, 'spam.h', 7)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
    
    def testVariadicCtor_03(self):
        """TestPpDefineVariadic.testVariadicCtor_02(): #define showlist(...) puts(#__VA_ARGS__)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('showlist(...) puts(#__VA_ARGS__)\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, 'spam.h', 7)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(11, myCppDef.tokensConsumed)
        self.assertEqual('showlist', myCppDef.identifier)
        self.assertEqual(['...',], myCppDef.parameters)
        self.assertEqual(['puts', '(', '#', '__VA_ARGS__', ')',], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        self.assertEqual('spam.h', myCppDef.fileId)
        self.assertEqual(7, myCppDef.line)
        self.assertEqual(0, myCppDef.refCount)
        self.assertTrue(myCppDef.isCurrentlyDefined)
        self.assertEqual('#define showlist(...) puts(#__VA_ARGS__) /* spam.h#7 Ref: 0 True */', str(myCppDef))
        myCppDef.undef('spam.h', 73)
        self.assertFalse(myCppDef.isCurrentlyDefined)
        self.assertEqual('#define showlist(...) puts(#__VA_ARGS__) /* spam.h#7 Ref: 0 False spam.h#73 */', str(myCppDef))
        
        
#===============================================================================
#        myCppDef = self._retCheckedMacro(
#                            '#define showlist(...) puts(#__VA_ARGS__)\n',
#                            False,
#                            7,
#                            'FV',
#                            ['...',],
#                            ['__VA_ARGS__',],
#                        )
#        # Replacement
#        myCpp = PpTokeniser.PpTokeniser(
#            theFileObj=StringIO.StringIO('(1,2,3)')
#            )
#        myGen = myCpp.next()
#        # First consume the preamble i.e. LPAREN
#        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
#        # Now consume the arguments
#        myArgS = myCppDef.retArgumentListTokens(myGen)
#        # Check that all tokens have been consumed
#        self.assertRaises(StopIteration, myGen.next)
#        # Check the arguments
#        myExpectedArgTokens = [
#                [
#                    PpToken.PpToken('1',       'pp-number'),
#                ],
#                [
#                    PpToken.PpToken('2',       'pp-number'),
#                ],
#                [
#                    PpToken.PpToken('3',       'pp-number'),
#                ],
#            ]
#        self.assertEqual(myExpectedArgTokens, myArgS)
#        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
#        myExpTokens = [
#                PpToken.PpToken('1',    'pp-number'),
#                PpToken.PpToken(',',    'preprocessing-op-or-punc'),
#                PpToken.PpToken('2',    'pp-number'),
#                PpToken.PpToken(',',    'preprocessing-op-or-punc'),
#                PpToken.PpToken('3',    'pp-number'),
#            ]
#        self.assertEqual(myExpTokens, myReplaceToks)
#===============================================================================

    def testVariadicCtor_Obj_00(self):
        """TestPpDefineVariadic.testVariadicCtor_Obj_00(): Failure with object like macro that has __VA_ARGS__."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('OBJ __VA_ARGS__\n')
            )
        myGen = myCpp.next()
        self.assertRaises(PpDefine.ExceptionCpipDefineInit, PpDefine.PpDefine, myGen, 'spam.h', 7)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testVariadicArgumentListTokens_00(self):
        """TestPpDefineVariadic.testVariadicArgumentListTokens_00() - All arguments."""
        myCppDef = self._retCheckedMacro(
                            'FV(...) __VA_ARGS__\n',
                            False,
                            7,
                            'FV',
                            ['...',],
                            ['__VA_ARGS__',],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

    def testVariadicArgumentListTokens_01(self):
        """TestPpDefineVariadic.testVariadicArgumentListTokens_01() - No arguments."""
        myCppDef = self._retCheckedMacro(
                            'FV(...) __VA_ARGS__\n',
                            False,
                            7,
                            'FV',
                            ['...',],
                            ['__VA_ARGS__',],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(')')
            )
        myGen = myCpp.next()
        myArgTokens = [
                myCppDef.PLACEMARKER,
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
    
    def testVariadicArgumentListTokens_02(self):
        """TestPpDefineVariadic.testVariadicArgumentListTokens_02() - #define F1(a,...) A a B __VA_ARGS__ C\\n - missing arguments."""
        myCppDef = self._retCheckedMacro(
                            'F1(a,...) A a B __VA_ARGS__ C\n',
                            False,
                            17,
                            'F1',
                            ['a', '...',],
                            ['A', ' ', 'a', ' ', 'B', ' ', '__VA_ARGS__', ' ', 'C'],
                        )
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(')')
            )
        myGen = myCpp.next()
        myArgTokens = [
                myCppDef.PLACEMARKER,
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(',)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                myCppDef.PLACEMARKER,
                myCppDef.PLACEMARKER,
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(',,)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                myCppDef.PLACEMARKER,
                myCppDef.PLACEMARKER,
                myCppDef.PLACEMARKER,
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
    
    def testVariadicArgumentListTokens_03(self):
        """TestPpDefineVariadic.testVariadicArgumentListTokens_03() - #define F1(a,...) A a B __VA_ARGS__ C\\n - has arguments."""
        myCppDef = self._retCheckedMacro(
                            'F1(a,...) A a B __VA_ARGS__ C\n',
                            False,
                            17,
                            'F1',
                            ['a', '...',],
                            ['A', ' ', 'a', ' ', 'B', ' ', '__VA_ARGS__', ' ', 'C'],
                        )
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
    
    def testVariadic_retReplacementMap_00(self):
        """TestPpDefineVariadic.testVariadic_retReplacementMap_00() - FV(...) __VA_ARGS__\\n."""
        myCppDef = self._retCheckedMacro(
                            'FV(...) __VA_ARGS__\n',
                            False,
                            7,
                            'FV',
                            ['...',],
                            ['__VA_ARGS__',],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        #print
        #print myReplaceMap
        self.assertEqual(
                    {
                    '...' : [
                            PpToken.PpToken('1', 'pp-number'),
                            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                            PpToken.PpToken('2', 'pp-number'),
                            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                            PpToken.PpToken('3', 'pp-number'),
                        ],
                    },
                    myReplaceMap)

    def testVariadic_retReplacementMap_01(self):
        """TestPpDefineVariadic.testVariadic_retReplacementMap_01() - FV(a,...) a - __VA_ARGS__\\n."""
        myCppDef = self._retCheckedMacro(
                            'FV(a,...) a - __VA_ARGS__\n',
                            False,
                            13,
                            'FV',
                            ['a', '...',],
                            ['a', ' ', '-', ' ', '__VA_ARGS__',],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        #print
        #print myReplaceMap
        self.assertEqual(
                    {
                    'a' : [
                            PpToken.PpToken('1', 'pp-number'),
                        ],
                    '...' : [
                            PpToken.PpToken('2', 'pp-number'),
                            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                            PpToken.PpToken('3', 'pp-number'),
                        ],
                    },
                    myReplaceMap)

    def testVariadic_retReplacementMap_02(self):
        """TestPpDefineVariadic.testVariadic_retReplacementMap_02() - FV(a,b,...) a - b - __VA_ARGS__\\n."""
        myCppDef = self._retCheckedMacro(
                            'FV(a,b,...) a - b - __VA_ARGS__\n',
                            False,
                            19,
                            'FV',
                            ['a', 'b', '...',],
                            ['a', ' ', '-', ' ', 'b', ' ', '-', ' ', '__VA_ARGS__',],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        #print
        #print myReplaceMap
        self.assertEqual(
                    {
                    'a' : [
                            PpToken.PpToken('1', 'pp-number'),
                        ],
                    'b' : [
                            PpToken.PpToken('2', 'pp-number'),
                        ],
                    '...' : [
                            PpToken.PpToken('3', 'pp-number'),
                        ],
                    },
                    myReplaceMap)

    def testVariadic_retReplacementMap_03(self):
        """TestPpDefineVariadic.testVariadic_retReplacementMap_03() - FV(a,b,c,...) a - b - c - __VA_ARGS__\\n."""
        myCppDef = self._retCheckedMacro(
                            'FV(a,b,c,...) a - b - c - __VA_ARGS__\n',
                            False,
                            25,
                            'FV',
                            ['a', 'b', 'c', '...',],
                            ['a', ' ', '-', ' ', 'b', ' ', '-', ' ', 'c', ' ', '-', ' ', '__VA_ARGS__',],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2,3)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        myArgList = myCppDef.retArgumentListTokens(myGen)
        self.assertEqual(myArgTokens, myArgList)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgList)
        #print
        #print myReplaceMap
        self.assertEqual(
                    {
                    'a' : [
                            PpToken.PpToken('1', 'pp-number'),
                        ],
                    'b' : [
                            PpToken.PpToken('2', 'pp-number'),
                        ],
                    'c' : [
                            PpToken.PpToken('3', 'pp-number'),
                        ],
                    },
                    myReplaceMap)

    def testVariadic_retReplacementMap_04(self):
        """TestPpDefineVariadic.testVariadic_retReplacementMap_04() - FV(a,b,...) a * b * __VA_ARGS__\\n witn no arguments."""
        myCppDef = self._retCheckedMacro(
                            'FV(a,b,...) a * b * __VA_ARGS__\n',
                            False,
                            19,
                            'FV',
                            ['a', 'b', '...',],
                            ['a', ' ', '*', ' ', 'b', ' ', '*', ' ', '__VA_ARGS__'],
                        )
        # Check internal functions
        #
        # Note that for function style macros the LPAREN is consumed
        # before retArgumentListTokens() is called.
        #
        # Simple argument list
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('1,2)')
            )
        myGen = myCpp.next()
        myArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
            ]
        self.assertEqual(myArgTokens, myCppDef.retArgumentListTokens(myGen))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
        #print
        #print myReplaceMap
        self.assertEqual(
                    {
                    'a' : [
                            PpToken.PpToken('1', 'pp-number'),
                        ],
                    'b' : [
                            PpToken.PpToken('2', 'pp-number'),
                        ],
                    },
                    myReplaceMap)
        
    def testReplaceVariadic_00(self):
        """TestPpDefineVariadic.testReplaceVariadic_00(): 'FV(...)\\n' called with FV(1,2,3)."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('FV(...)\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(5, myCppDef.tokensConsumed)
        self.assertEqual('FV', myCppDef.identifier)
        self.assertEqual(['...',], myCppDef.parameters)
        self.assertEqual([], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(1,2,3)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        self.assertEqual([], myReplaceToks)
 
    def testReplaceVariadic_01(self):
        """TestPpDefineVariadic.testReplaceVariadic_01(): 'FV(...) __VA_ARGS__\\n' called with FV(1,2,3)."""
        myCppDef = self._retCheckedMacro(
                            'FV(...) __VA_ARGS__\n',
                            False,
                            7,
                            'FV',
                            ['...',],
                            ['__VA_ARGS__',],
                        )
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(1,2,3)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('1',       'pp-number'),
                ],
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        myExpTokens = [
                PpToken.PpToken('1',    'pp-number'),
                PpToken.PpToken(',',    'preprocessing-op-or-punc'),
                PpToken.PpToken('2',    'pp-number'),
                PpToken.PpToken(',',    'preprocessing-op-or-punc'),
                PpToken.PpToken('3',    'pp-number'),
            ]
        self.assertEqual(myExpTokens, myReplaceToks)

    def testReplaceVariadic_02(self):
        """TestPpDefineVariadic.testReplaceVariadic_02(): '#define showlist(...) puts(#__VA_ARGS__)\\n' ISO/IEC 9899:1999 (E) 6.10.3.5 EXAMPLE 7."""
        myCppDef = self._retCheckedMacro(
                            'showlist(...) puts(#__VA_ARGS__)\n',
                            False,
                            11,
                            'showlist',
                            ['...',],
                            ['puts', '(', '#', '__VA_ARGS__', ')'],
                        )
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(The first, second, and third items.)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('The',      'identifier'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('first',    'identifier'),
                ],
                [
                    PpToken.PpToken('second',   'identifier'),
                ],
                [
                    PpToken.PpToken('and',      'identifier'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('third',    'identifier'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('items',    'identifier'),
                    PpToken.PpToken('.',        'preprocessing-op-or-punc'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceMap = myCppDef._retReplacementMap(myArgS)
        #print
        #print myReplaceMap
        self.assertEqual(
                    {
                    '...' : [
                        PpToken.PpToken('The',      'identifier'),
                        PpToken.PpToken(' ',        'whitespace'),
                        PpToken.PpToken('first',    'identifier'),

                        PpToken.PpToken(',',        'preprocessing-op-or-punc'),

                        PpToken.PpToken('second',   'identifier'),

                        PpToken.PpToken(',',        'preprocessing-op-or-punc'),

                        PpToken.PpToken('and',      'identifier'),
                        PpToken.PpToken(' ',        'whitespace'),
                        PpToken.PpToken('third',    'identifier'),
                        PpToken.PpToken(' ',        'whitespace'),
                        PpToken.PpToken('items',    'identifier'),
                        PpToken.PpToken('.',        'preprocessing-op-or-punc'),
                        ],
                    },
                    myReplaceMap)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        myExpTokens = self.stringToTokens('puts("The first,second,and third items.")')
        self._printDiff(myReplaceToks, myExpTokens)
        self.assertEqual(myExpTokens, myReplaceToks)

class TestPpDefineFunctionLikeAcceptableVariadicArguments(TestPpDefine):
    """Tests PpDefine low level functionality for variadic function style macros.
    ISO/IEC 9899:1999 (E) 6.10.3 Macro replacement
        Constraints
    6.10.3-4:
    If the identifier-list in the macro definition does not end with an ellipsis, the number of
arguments (including those arguments consisting of no preprocessing tokens) in an
invocation of a function-like macro shall equal the number of parameters in the macro
definition. Otherwise, there shall be more arguments in the invocation than there are
parameters in the macro definition (excluding the ...). There shall exist a )
preprocessing token that terminates the invocation.

Test code with cpp.exe:
#define F0(...) |-| __VA_ARGS__ EOL
F0()            // |-| EOL
F0(1)           // |-| 1 EOL
F0(1,2)         // |-| 1,2 EOL
F0(1,2,3)       // |-| 1,2,3 EOL
F0(,)           // |-| EOL
F0(,,)          // |-| ,EOL
F0(,,,)         // |-| ,, EOL
#define F1(a,...) |a| __VA_ARGS__ EOL
F1()            // | | EOL
F1(1)           // |1| EOL
F1(1,2)         // |1| 2 EOL
F1(1,2,3)       // |1| 2,3 EOL
F1(,)           // | | EOL
F1(,,)          // | | ,EOL
F1(,,,)         // | | ,, EOL
#define F2(a,b,...) |a|b| __VA_ARGS__ EOL
F2()            // variadic.h:10:4: macro "F2" requires 3 arguments, but only 1 given
F2(1)           // variadic.h:11:5: macro "F2" requires 3 arguments, but only 1 given
F2(1,)          // |1| | EOL
F2(1,2)         // |1|2| EOL
F2(1,2,3)       // |1|2| 3 EOL
F2(1,2,3,4)     // |1|2| 3,4 EOL
F2(,)           // | | | EOL
F2(,,)          // | | | EOL
F2(,,,)         // | | | , EOL
F2(,,,,)        // | | | ,, EOL
#define F3(a,b,c,...) |a|b|c| __VA_ARGS__ EOL
F3()            // variadic.h:19:4: macro "F3" requires 4 arguments, but only 1 given
F3(1)           // variadic.h:20:5: macro "F3" requires 4 arguments, but only 1 given
F3(1,2)         // variadic.h:21:7: macro "F3" requires 4 arguments, but only 2 given
F3(1,2,3)       // |1|2|3| EOL
F3(1,2,3,4)     // |1|2|3| 4 EOL
F3(1,2,3,4,5)   // |1|2|3| 4,5 EOL
F3(,)           // variadic.h:24:5: macro "F3" requires 4 arguments, but only 2 given
F3(,,)          // | | | | EOL
F3(,,,)         // | | | | EOL
F3(,,,,)        // | | | | , EOL
F3(,,,,,)       // | | | | ,, EOL
EOF
    """

    def test_00(self):
        """TestPpDefineFunctionLikeAcceptableVariadicArguments.test_00() - F0(...)."""
        # TODO: Make these tests exercise the code example above
        """cpp.exe:
        #define F0(...) |-| __VA_ARGS__ EOL
F0()            // |-| EOL
F0(1)           // |-| 1 EOL
F0(1,2)         // |-| 1,2 EOL
F0(1,2,3)       // |-| 1,2,3 EOL
F0(,)           // |-| , EOL
F0(,,)          // |-| ,, EOL
F0(,,,)         // |-| ,,, EOL
"""
        myCppDef = self._retCheckedMacro(
                            'F0(...) |-| __VA_ARGS__ EOL\n',
                            False,
                            13,
                            'F0',
                            ['...',],
                            ['|', '-', '|', ' ', '__VA_ARGS__', ' ', 'EOL',],
                        )
        myExpArgTokens = [
            myCppDef.PLACEMARKER,
            ]
        myArgsExpToksAndReplMap = (
            # F0()
            (
                ')',
                [
                 myCppDef.PLACEMARKER,
                ],
                {'...': []},
                self.stringToTokens('|-| ')+self.stringToTokens(' EOL'),
              ),
            # F0(1)
            (
                '1)',
                [
                    self.stringToTokens('1'),
                ],
                {'...': self.stringToTokens('1')},
                self.stringToTokens('|-| 1 EOL'),
              ),
            # F0(1,2)
            (
                '1,2)',
                [
                    self.stringToTokens('1'),
                    self.stringToTokens('2'),
                ],
                {'...': self.stringToTokens('1,2')},
                self.stringToTokens('|-| 1,2 EOL'),
              ),
            # F0(1,2,3)
            (
                '1,2,3)',
                [
                    self.stringToTokens('1'),
                    self.stringToTokens('2'),
                    self.stringToTokens('3'),
                ],
                {'...': self.stringToTokens('1,2,3')},
                self.stringToTokens('|-| 1,2,3 EOL'),
              ),
            # F0(,)
            (
                ',)',
                [
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                ],
                {'...': self.stringToTokens(',')},
                self.stringToTokens('|-| , EOL'),
              ),
            # F0(,,)
            (
                ',,)',
                [
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                ],
                {'...' : [
                          PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                          PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                          ],
                 },
                self.stringToTokens('|-| ,, EOL'),
              ),
            )
        for args, expArgToks, expMap, expRepl in myArgsExpToksAndReplMap:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(args)
                )
            myGen = myCpp.next()
            myArgTokens = myCppDef.retArgumentListTokens(myGen)
            # Check that all tokens have been consumed
            self.assertRaises(StopIteration, myGen.__next__)
            #print
            #print 'TRACE: args:', args
            #print 'TRACE: toks:', myArgTokens
            self._printDiff(myArgTokens, expArgToks)
            self.assertEquals(expArgToks, myArgTokens)
            myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
            #print 'TRACE:  map:', myReplaceMap
            self.assertEquals(expMap, myReplaceMap)
            myReplacements = myCppDef._functionLikeReplacement(myReplaceMap)
            #print 'TRACE:  out:', myReplacements
            self.assertEquals(expRepl, myReplacements)

    def test_00_00(self):
        """TestPpDefineFunctionLikeAcceptableVariadicArguments.test_00_00() - F0(...) - special test."""
        """cpp.exe:
        #define F0(...) |-| __VA_ARGS__ EOL
F0()            // |-| EOL
F0(,)           // |-| , EOL
F0(,,)          // |-| ,, EOL
F0(,,,)         // |-| ,,, EOL
"""
        myCppDef = self._retCheckedMacro(
                            'F0(...) |-| __VA_ARGS__ EOL\n',
                            False,
                            13,
                            'F0',
                            ['...',],
                            ['|', '-', '|', ' ', '__VA_ARGS__', ' ', 'EOL',],
                        )
        myExpArgTokens = [
            myCppDef.PLACEMARKER,
            ]
        myArgsExpToksAndReplMap = (
            # F0()
            (
                ')',
                [
                 myCppDef.PLACEMARKER,
                ],
                {'...': []},
                self.stringToTokens('|-| ')+self.stringToTokens(' EOL'),
              ),
            # F0(,)
            (
                ',)',
                [
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                ],
                {'...': self.stringToTokens(',')},
                self.stringToTokens('|-| , EOL'),
              ),
            # F0(,,)
            (
                ',,)',
                [
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                ],
                {'...' : self.stringToTokens(',,')},
                self.stringToTokens('|-| ,, EOL'),
              ),
            )
        for args, expArgToks, expMap, expRepl in myArgsExpToksAndReplMap:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(args)
                )
            myGen = myCpp.next()
            myArgTokens = myCppDef.retArgumentListTokens(myGen)
            # Check that all tokens have been consumed
            self.assertRaises(StopIteration, myGen.__next__)
            #print
            #print 'TRACE: args:', args
            #print 'TRACE: toks:', myArgTokens
            self._printDiff(myArgTokens, expArgToks)
            self.assertEquals(expArgToks, myArgTokens)
            myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
            #print 'TRACE:  map:', myReplaceMap
            self.assertEquals(expMap, myReplaceMap)
            myReplacements = myCppDef._functionLikeReplacement(myReplaceMap)
            #print 'TRACE:  out:', myReplacements
            self.assertEquals(expRepl, myReplacements)

    def test_01(self):
        """TestPpDefineFunctionLikeAcceptableVariadicArguments.test_01() - F1(a,...)."""
        """cpp.exe:
#define F1(a,...) |a| __VA_ARGS__ EOL
F1()            // | | EOL
F1(1)           // |1| EOL
F1(1,2)         // |1| 2 EOL
F1(1,2,3)       // |1| 2,3 EOL
F1(,)           // | | EOL
F1(,,)          // | | ,EOL
F1(,,,)         // | | ,, EOL
"""
        myCppDef = self._retCheckedMacro(
                            'F1(a,...) |a| __VA_ARGS__ EOL\n',
                            False,
                            15,
                            'F1',
                            ['a', '...',],
                            ['|', 'a', '|', ' ', '__VA_ARGS__', ' ', 'EOL',],
                        )
        myExpArgTokens = [
            myCppDef.PLACEMARKER,
            ]
        myArgsExpToksAndReplMap = (
            # F1()
            (
                ')',
                [
                 myCppDef.PLACEMARKER,
                ],
                {'a': myCppDef.PLACEMARKER},
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F1(1)
            (
                '1)',
                [
                    self.stringToTokens('1'),
                ],
                {'a': self.stringToTokens('1')},
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('1',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F1(1,2)
            (
                '1,2)',
                [
                    self.stringToTokens('1'),
                    self.stringToTokens('2'),
                ],
                {
                    'a'     : self.stringToTokens('1'),
                    '...'   : self.stringToTokens('2'),
                },
                self.stringToTokens('|1| 2 EOL'),
              ),
            # F1(1,2,3)
            (
                '1,2,3)',
                [
                    self.stringToTokens('1'),
                    self.stringToTokens('2'),
                    self.stringToTokens('3'),
                ],
                {
                    'a'     : self.stringToTokens('1'),
                    '...'   : self.stringToTokens('2,3'),
                },
                self.stringToTokens('|1| 2,3 EOL'),
              ),
            # F1(,)
            (
                ',)',
                [
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    '...'   : [],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F1(,,)
            (
                ',,)',
                [
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    '...'   : [
                               PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                               ],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F1(,,,)
            (
                ',,,)',
                [
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                 myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    '...'   : [
                               PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                               PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                               ],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F1(,2,,4)
            (
                ',2,,4)',
                [
                    myCppDef.PLACEMARKER,
                    [PpToken.PpToken('2',        'pp-number'),],
                    myCppDef.PLACEMARKER,
                    [PpToken.PpToken('4',        'pp-number'),],
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    '...'   : [
                               PpToken.PpToken('2',        'pp-number'),
                               PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                               PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                               PpToken.PpToken('4',        'pp-number'),
                               ],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('2',        'pp-number'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('4',        'pp-number'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F1(,,3,)
            (
                ',,3,)',
                [
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    [PpToken.PpToken('3',        'pp-number'),],
                    myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    '...'   : [
                               PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                               PpToken.PpToken('3',        'pp-number'),
                               PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                               ],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('3',        'pp-number'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            )
        for args, expArgToks, expMap, expRepl in myArgsExpToksAndReplMap:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(args)
                )
            myGen = myCpp.next()
            myArgTokens = myCppDef.retArgumentListTokens(myGen)
            # Check that all tokens have been consumed
            self.assertRaises(StopIteration, myGen.__next__)
            #print
            #print 'TRACE: args:', args
            #print 'TRACE: toks:', myArgTokens
            #print 'TRACE:  exp:', expArgToks
            self._printDiff(myArgTokens, expArgToks)
            self.assertEquals(expArgToks, myArgTokens)
            myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
            #print 'TRACE:  map:', myReplaceMap
            self.assertEquals(expMap, myReplaceMap)
            myReplacements = myCppDef._functionLikeReplacement(myReplaceMap)
            #print 'TRACE:  out:', myReplacements
            #print 'TRACE:  out:', self.tokensToString(myReplacements)
            self.assertEquals(expRepl, myReplacements)

    def test_02(self):
        """TestPpDefineFunctionLikeAcceptableVariadicArguments.test_02() - F2(a,b,...)."""
        """cpp.exe:
F_2_START
#define F2(a,b,...) |a|b| __VA_ARGS__ EOL
F2()            // variadic.h:10:4: macro "F2" requires 3 arguments, but only 1 given
F2(1)           // variadic.h:11:5: macro "F2" requires 3 arguments, but only 1 given
F2(1,)          // |1| | EOL
F2(1,2)         // |1|2| EOL
F2(1,2,3)       // |1|2| 3 EOL
F2(1,2,3,4)     // |1|2| 3,4 EOL
F2(,)           // | | | EOL
F2(,,)          // | | | EOL
F2(,,,)         // | | | , EOL
F2(,,,,)        // | | | ,, EOL
F_2_END
"""
        myCppDef = self._retCheckedMacro(
                            'F2(a,b,...) |a|b| __VA_ARGS__ EOL\n',
                            False,
                            19,
                            'F2',
                            ['a', 'b', '...',],
                            ['|', 'a', '|', 'b', '|', ' ', '__VA_ARGS__', ' ', 'EOL',],
                        )
        myExpArgTokens = [
            myCppDef.PLACEMARKER,
            ]
        myArgsExpToksAndReplMap = (
            # F2()
            (
                ')',
                None,
                None,
                None,
              ),
            # F2(1)
            (
                '1)',
                None,
                None,
                None,
              ),
            # F2(1,)
            (
                '1,)',
                [
                    [PpToken.PpToken('1',        'pp-number'),],
                    myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : [PpToken.PpToken('1',        'pp-number'),],
                    'b'     : myCppDef.PLACEMARKER,
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('1',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F2(1,2)
            (
                '1,2)',
                [
                    [PpToken.PpToken('1',        'pp-number'),],
                    [PpToken.PpToken('2',        'pp-number'),],
                ],
                {
                    'a'     : [PpToken.PpToken('1',        'pp-number'),],
                    'b'     : [PpToken.PpToken('2',        'pp-number'),],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('1',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('2',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F2(1,2,3)
            (
                '1,2,3)',
                [
                    [PpToken.PpToken('1',        'pp-number'),],
                    [PpToken.PpToken('2',        'pp-number'),],
                    [PpToken.PpToken('3',        'pp-number'),],
                ],
                {
                    'a'     : [PpToken.PpToken('1',        'pp-number'),],
                    'b'     : [PpToken.PpToken('2',        'pp-number'),],
                    '...'   : [PpToken.PpToken('3',        'pp-number'),],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('1',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('2',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('3',        'pp-number'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F2(1,2,3,4)
            (
                '1,2,3,4)',
                [
                    [PpToken.PpToken('1',        'pp-number'),],
                    [PpToken.PpToken('2',        'pp-number'),],
                    [PpToken.PpToken('3',        'pp-number'),],
                    [PpToken.PpToken('4',        'pp-number'),],
                ],
                {
                    'a'     : [PpToken.PpToken('1',        'pp-number'),],
                    'b'     : [PpToken.PpToken('2',        'pp-number'),],
                    '...'   : [
                               PpToken.PpToken('3',        'pp-number'),
                               PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                               PpToken.PpToken('4',        'pp-number'),
                               ],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('1',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('2',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('3',        'pp-number'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('4',        'pp-number'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F2(,)
            (
                ',)',
                [
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    'b'     : myCppDef.PLACEMARKER,
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F2(,,)
            (
                ',,)',
                [
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    'b'     : myCppDef.PLACEMARKER,
                    '...'   : [],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F2(,,,)
            (
                ',,,)',
                [
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    'b'     : myCppDef.PLACEMARKER,
                    '...'   : [
                               PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                               ],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F2(,,,,)
            (
                ',,,,)',
                [
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    'b'     : myCppDef.PLACEMARKER,
                    '...'   : [
                               PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                               PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                               ],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            )
        for inToks, expArgToks, expRepMap, expReprToks in myArgsExpToksAndReplMap:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(inToks)
                )
            myGen = myCpp.next()
            if expArgToks is None:
                self.assertRaises(
                    PpDefine.ExceptionCpipDefineBadArguments,
                    myCppDef.retArgumentListTokens,
                    myGen,
                    )
            else:
                myArgTokens = myCppDef.retArgumentListTokens(myGen)
                #print
                #print 'TRACE: myArgTokens:', myArgTokens
                #print 'TRACE:         exp:', expArgToks
                self.assertEquals(expArgToks, myArgTokens)
                # Check that all tokens have been consumed
                self.assertRaises(StopIteration, myGen.__next__)
                myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
                #print 'TRACE:  map:', myReplaceMap
                self.assertEquals(expRepMap, myReplaceMap)
                myReplacements = myCppDef._functionLikeReplacement(myReplaceMap)
                #print 'TRACE:  out:', myReplacements
                #print 'TRACE:  out:', self.tokensToString(myReplacements)
                self.assertEquals(expReprToks, myReplacements)

    def test_03(self):
        """TestPpDefineFunctionLikeAcceptableVariadicArguments.test_03() F3(a,b,c,...)."""
        """cpp.exe:
F_3_START
#define F3(a,b,c,...) |a|b|c| __VA_ARGS__ EOL
F3()            // variadic.h:19:4: macro "F3" requires 4 arguments, but only 1 given
F3(1)           // variadic.h:20:5: macro "F3" requires 4 arguments, but only 1 given
F3(1,2)         // variadic.h:21:7: macro "F3" requires 4 arguments, but only 2 given
F3(1,2,3)       // |1|2|3| EOL
F3(1,2,3,4)     // |1|2|3| 4 EOL
F3(1,2,3,4,5)   // |1|2|3| 4,5 EOL
F3(,)           // variadic.h:24:5: macro "F3" requires 4 arguments, but only 2 given
F3(,,)          // | | | | EOL
F3(,,,)         // | | | | EOL
F3(,,,,)        // | | | | , EOL
F3(,,,,,)       // | | | | ,, EOL
F_3_END
"""
        myCppDef = self._retCheckedMacro(
                            'F3(a,b,c,...) |a|b|c| __VA_ARGS__ EOL\n',
                            False,
                            23,
                            'F3',
                            ['a', 'b', 'c', '...',],
                            ['|', 'a', '|', 'b', '|', 'c', '|', ' ', '__VA_ARGS__', ' ', 'EOL',],
                        )
        myExpArgTokens = [
            myCppDef.PLACEMARKER,
            ]
        myArgsExpToksAndReplMap = (
            # F3()
            (
                ')',
                None,
                None,
                None,
              ),
            # F3(1)
            (
                '1)',
                None,
                None,
                None,
              ),
            # F3(1)
            (
                '1,2)',
                None,
                None,
                None,
              ),
            # F3(1,2,3)
            (
                '1,2,3)',
                [
                    [PpToken.PpToken('1',        'pp-number'),],
                    [PpToken.PpToken('2',        'pp-number'),],
                    [PpToken.PpToken('3',        'pp-number'),],
                ],
                {
                    'a'     : [PpToken.PpToken('1',        'pp-number'),],
                    'b'     : [PpToken.PpToken('2',        'pp-number'),],
                    'c'     : [PpToken.PpToken('3',        'pp-number'),],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('1',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('2',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('3',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F3(1,2,3,4)
            (
                '1,2,3,4)',
                [
                    [PpToken.PpToken('1',        'pp-number'),],
                    [PpToken.PpToken('2',        'pp-number'),],
                    [PpToken.PpToken('3',        'pp-number'),],
                    [PpToken.PpToken('4',        'pp-number'),],
                ],
                {
                    'a'     : [PpToken.PpToken('1',        'pp-number'),],
                    'b'     : [PpToken.PpToken('2',        'pp-number'),],
                    'c'     : [PpToken.PpToken('3',        'pp-number'),],
                    '...'   : [PpToken.PpToken('4',        'pp-number'),],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('1',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('2',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('3',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('4',        'pp-number'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F3(1,2,3,4,5)
            (
                '1,2,3,4,5)',
                [
                    [PpToken.PpToken('1',        'pp-number'),],
                    [PpToken.PpToken('2',        'pp-number'),],
                    [PpToken.PpToken('3',        'pp-number'),],
                    [PpToken.PpToken('4',        'pp-number'),],
                    [PpToken.PpToken('5',        'pp-number'),],
                ],
                {
                    'a'     : [PpToken.PpToken('1',        'pp-number'),],
                    'b'     : [PpToken.PpToken('2',        'pp-number'),],
                    'c'     : [PpToken.PpToken('3',        'pp-number'),],
                    '...'   : [
                               PpToken.PpToken('4',        'pp-number'),
                               PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                               PpToken.PpToken('5',        'pp-number'),
                               ],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('1',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('2',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('3',        'pp-number'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('4',        'pp-number'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('5',        'pp-number'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F3()
            (
                ',)',
                None,
                None,
                None,
              ),
            # F3(,,)
            (
                ',,)',
                [
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    'b'     : myCppDef.PLACEMARKER,
                    'c'     : myCppDef.PLACEMARKER,
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F3(,,,)
            (
                ',,,)',
                [
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    'b'     : myCppDef.PLACEMARKER,
                    'c'     : myCppDef.PLACEMARKER,
                    '...'   : [],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F3(,,,,)
            (
                ',,,,)',
                [
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    'b'     : myCppDef.PLACEMARKER,
                    'c'     : myCppDef.PLACEMARKER,
                    '...'   : [
                               PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                               ],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            # F3(,,,,,)
            (
                ',,,,,)',
                [
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                    myCppDef.PLACEMARKER,
                ],
                {
                    'a'     : myCppDef.PLACEMARKER,
                    'b'     : myCppDef.PLACEMARKER,
                    'c'     : myCppDef.PLACEMARKER,
                    '...'   : [
                               PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                               PpToken.PpToken(',', 'preprocessing-op-or-punc'),
                               ],
                },
                [
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken('|',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(',',        'preprocessing-op-or-punc'),
                    PpToken.PpToken(' ',        'whitespace'),
                    PpToken.PpToken('EOL',      'identifier'),
                 ],
              ),
            )
        for inToks, expArgToks, expRepMap, expReprToks in myArgsExpToksAndReplMap:
            #print
            #print 'TRACE:      inToks:', inToks
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(inToks)
                )
            myGen = myCpp.next()
            if expArgToks is None:
                self.assertRaises(
                    PpDefine.ExceptionCpipDefineBadArguments,
                    myCppDef.retArgumentListTokens,
                    myGen,
                    )
            else:
                myArgTokens = myCppDef.retArgumentListTokens(myGen)
                #print 'TRACE: myArgTokens:', myArgTokens
                #print 'TRACE:         exp:', expArgToks
                self.assertEquals(expArgToks, myArgTokens)
                # Check that all tokens have been consumed
                self.assertRaises(StopIteration, myGen.__next__)
                myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
                #print 'TRACE:  map:', myReplaceMap
                self.assertEquals(expRepMap, myReplaceMap)
                myReplacements = myCppDef._functionLikeReplacement(myReplaceMap)
                #print 'TRACE:  out:', myReplacements
                #print 'TRACE:  out:', self.tokensToString(myReplacements)
                self.assertEquals(expReprToks, myReplacements)
        
#===============================================================================
#        for args, expArgToks, expMap, expRepl in myArgsExpToksAndReplMap:
#            myCpp = PpTokeniser.PpTokeniser(
#                theFileObj=StringIO.StringIO(args)
#                )
#            myGen = myCpp.next()
#            myArgTokens = myCppDef.retArgumentListTokens(myGen)
#            # Check that all tokens have been consumed
#            self.assertRaises(StopIteration, myGen.next)
#            print
#            print 'TRACE: args:', args
#            print 'TRACE: toks:', myArgTokens
#            print 'TRACE:  exp:', expArgToks
#            self._printDiff(myArgTokens, expArgToks)
#            self.assertEquals(expArgToks, myArgTokens)
#            myReplaceMap = myCppDef._retReplacementMap(myArgTokens)
#            print 'TRACE:  map:', myReplaceMap
#            self.assertEquals(expMap, myReplaceMap)
#            myReplacements = myCppDef._functionLikeReplacement(myReplaceMap)
#            print 'TRACE:  out:', myReplacements
#            print 'TRACE:  out:', self.tokensToString(myReplacements)
#            self.assertEquals(expRepl, myReplacements)
#===============================================================================

class TestPpDefineLinux(TestPpDefine):
    """Tests exposed by preprocessing the Linus Kernel"""

    def test_00(self):
        """PpDefine: Linux issue with: #define __ASM_SIZE(inst) inst##l, inst##q"""
        src = """#define __ASM_SIZE(inst)    inst##l, inst##q
/* rwsem.h */
__ASM_SIZE(a)
/* Expects:
al, aq
*/
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('__ASM_SIZE(inst)    inst##l, inst##q\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(14, myCppDef.tokensConsumed)
        self.assertEqual('__ASM_SIZE', myCppDef.identifier)
        self.assertEqual(['inst'], myCppDef.parameters)
        self.assertEqual(['inst', '##', 'l', ',', ' ', 'inst', '##', 'q'], myCppDef.replacements)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(a)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('a',       'identifier'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
        #self.pprintReplacementList(myReplaceToks)
        self.assertEqual(
            [
                PpToken.PpToken(t="al", tt='identifier'),
                PpToken.PpToken(t=",", tt='preprocessing-op-or-punc'),
                PpToken.PpToken(t=" ", tt='whitespace'),
                PpToken.PpToken(t="aq", tt='identifier'),
            ],
            myReplaceToks,
            )

    def test_01(self):
        """PpDefine: Linux issue with: #define __ASM_SIZE(inst, ...) inst##l##__VA_ARGS__, inst##q##__VA_ARGS__"""
        src = """#define __ASM_SIZE(inst, ...) inst##l##__VA_ARGS__, inst##q##__VA_ARGS__
/* rwsem.h */
__ASM_SIZE(a)
/* Expects:
al, aq
*/
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('__ASM_SIZE(inst, ...) inst##l##__VA_ARGS__, inst##q##__VA_ARGS__\n')
            )
        myGen = myCpp.next()
        myCppDef = PpDefine.PpDefine(myGen, '', 1)
        self.assertEqual(False, myCppDef.isObjectTypeMacro)
        self.assertEqual(21, myCppDef.tokensConsumed)
        self.assertEqual('__ASM_SIZE', myCppDef.identifier)
        self.assertEqual(['inst', '...'], myCppDef.parameters)
        self.assertEqual(
            [
                'inst', '##', 'l', '##', '__VA_ARGS__', ',',
                ' ', 'inst', '##', 'q', '##', '__VA_ARGS__'
            ],
            myCppDef.replacements,
        )
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('(a)')
            )
        myGen = myCpp.next()
        # First consume the preamble i.e. LPAREN
        self.assertEqual(None, myCppDef.consumeFunctionPreamble(myGen))
        # Now consume the arguments
        myArgS = myCppDef.retArgumentListTokens(myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
        # Check the arguments
        myExpectedArgTokens = [
                [
                    PpToken.PpToken('a',       'identifier'),
                ],
            ]
        self.assertEqual(myExpectedArgTokens, myArgS)
        myReplaceToks = myCppDef.replaceArgumentList(myArgS)
#         self.pprintReplacementList(myReplaceToks)
        # TODO: This test was created whilst fixing the Linux __ASM_SEL bug
        # however why is the token type of 'al' concat and not 'aq'?
        self.assertEqual(
            [
                PpToken.PpToken(t="al", tt='identifier'),
                PpToken.PpToken(t=",", tt='preprocessing-op-or-punc'),
                PpToken.PpToken(t=" ", tt='whitespace'),
                PpToken.PpToken(t="aq", tt='identifier'),
            ],
            myReplaceToks,
            )

class NullClass(TestPpDefine):
    pass

def unitTest(theVerbosity=2):
    # - OK
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineInit))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineFunctionLikeLowLevel))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineFunctionLikeBadArguments))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineFunctionLikeAcceptableArguments))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineRedefineAndCmp))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineReplaceObjectStyle))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineReplaceFunctionStyle))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineCppStringize))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineCppConcat))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConcatFunctionLikeMacro))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineExample5))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineFileLine))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineRefCount))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineUndef))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineVariadic))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineFunctionLikeAcceptableVariadicArguments))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineLinux))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################


def usage():
    print("""TestPpDefine.py - Tests the PpDefine module.
Usage:
python TestPpDefine.py [-hl: --help]

Options:
-h, --help ~ Help (this screen) and exit.
-l:        ~ set the logging level higher is quieter.
             Default is 30 (WARNING) e.g.:
                CRITICAL    50
                ERROR       40
                WARNING     30
                INFO        20
                DEBUG       10
                NOTSET      0
""")

def main():
    print('TestPpDefine.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
    print(__rights__)
    print()
    import getopt
    print('Command line:')
    print(' '.join(sys.argv))
    print()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError as myErr:
        usage()
        print('ERROR: Invalid option: %s' % str(myErr))
        sys.exit(1)
    logLevel = logging.WARNING
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o == '-l':
            logLevel = int(a)
    if len(args) != 0:
        usage()
        print('ERROR: Wrong number of arguments[%d]!' % len(args))
        sys.exit(1)
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    unitTest()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
