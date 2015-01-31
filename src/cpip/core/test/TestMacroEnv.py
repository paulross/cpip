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

"""Test the MacroEnv module.

Using cpp.exe to help with test cases:

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

Using the regex to the source file:
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

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import logging
import sys
import time

from cpip.core import PpToken, PpTokeniser, PpDefine, MacroEnv, FileLocation
from TestPpDefine import TestPpDefine

######################
# Section: Unit tests.
######################
import unittest
import io
# Define unit test classes


class TestMacroEnv(TestPpDefine):
    """Sub-class of test class that has some convenience functions."""

    def _checkMacroEnv(self, theGen, theEnv, expectedIdentifiers, testNOTHING=True):
        """Checks constructed environment is correct."""
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, theGen)
        self.assertEqual(len(expectedIdentifiers), len(theEnv))
        for anName in expectedIdentifiers:
            self.assertEqual(
                True,
                theEnv.mightReplace(
                    PpToken.PpToken(anName, 'identifier')
                )
            )
            # Check using isDefined()
            self.assertEqual(
                True,
                theEnv.isDefined(
                    PpToken.PpToken(anName, 'identifier')
                )
            )
        if testNOTHING:
            self.assertEqual(
                False,
                theEnv.mightReplace(
                    PpToken.PpToken('NOTHING', 'identifier')
                )
            )
            # Check using isDefined()
            self.assertEqual(
                False,
                theEnv.isDefined(
                    PpToken.PpToken('NOTHING', 'identifier')
                )
            )

class MacroEnvInit(TestMacroEnv):
    """Tests the MacroEnv.MacroEnv initialisation."""

    def testDefineMapInit_00(self):
        """MacroEnv.MacroEnv - simple creation."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, 'f.h', 1)
        myMap.define(myGen, 'f.h', 2)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS',])
        self.assertEqual("""#define EGGS 2 /* f.h#2 Ref: 1 True */
#define SPAM 1 /* f.h#1 Ref: 1 True */""", str(myMap))
        self.assertEqual(
            self.stringToTokens(u'1'),
            myMap.replace(
                PpToken.PpToken('SPAM', 'identifier'), None)
            )
        self.assertEqual(
            self.stringToTokens(u'2'),
            myMap.replace(
                PpToken.PpToken('EGGS', 'identifier'), None)
            )
        self.assertEqual("""#define EGGS 2 /* f.h#2 Ref: 2 True */
#define SPAM 1 /* f.h#1 Ref: 2 True */""", str(myMap))

    def testDefineMapInit_00_00(self):
        """MacroEnv.MacroEnv - simple creation and then using clear()."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, 'f.h', 1)
        myMap.define(myGen, 'f.h', 2)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS',])
        myMap.clear()
        self._checkMacroEnv(myGen, myMap, [])

    def testDefineMapInit_01(self):
        """MacroEnv.MacroEnv - simple creation and execution of debug/trace."""
        # Really just for test coverage reasons
        myMap = MacroEnv.MacroEnv(enableTrace=True)
        myMap.debugMarker = 'MacroEnvInit.testDefineMapInit_01()'
        myMap._debugTokenStream('Prefix', 'String')
        myMap._debugTokenStream(
            'Prefix',
            [
                PpToken.PpToken('1',   'pp-number'),
                PpToken.PpToken(' ',   'whitespace'),
                PpToken.PpToken('and', 'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',   'whitespace'),
                PpToken.PpToken('2',   'pp-number'),
            ],
            )
        myMap._debugTokenStream('Prefix', None)
        self.assertRaises(
            MacroEnv.ExceptionMacroEnv,
            myMap._debugTokenStream,
            'Prefix',
            {},
            )

    def testDefineMapInit_fails_00(self):
        """MacroEnv.MacroEnv - creation failure with only newline."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        self.assertRaises(
            MacroEnv.ExceptionMacroReplacementInit,
            myMap.define,
            myGen,
            '',
            1,
            )

    def testDefineMapInit_fails_01(self):
        """MacroEnv.MacroEnv - creation failure with empty string."""
        myMap = MacroEnv.MacroEnv()
        myStr = u""""""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        self.assertRaises(
            MacroEnv.ExceptionMacroReplacementInit,
            myMap.define,
            myGen,
            '',
            1,
            )

class MacroEnvDefined(TestMacroEnv):
    """Tests the MacroEnv.MacroEnv with defined()."""

    def test_00(self):
        """MacroEnvDefined.test_00 - check defined()."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, 'f.h', 1)
        myMap.define(myGen, 'f.h', 2)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS',])
        self.assertEqual("""#define EGGS 2 /* f.h#2 Ref: 1 True */
#define SPAM 1 /* f.h#1 Ref: 1 True */""", str(myMap))
        myCodeResult = (
            (PpToken.PpToken('SPAM', 'identifier'), False, PpToken.PpToken('1', 'pp-number')),
            (PpToken.PpToken('EGGS', 'identifier'), False, PpToken.PpToken('1', 'pp-number')),
            (PpToken.PpToken('NOWT', 'identifier'), False, PpToken.PpToken('0', 'pp-number')),
            (PpToken.PpToken('SPAM', 'identifier'), True, PpToken.PpToken('0', 'pp-number')),
            (PpToken.PpToken('EGGS', 'identifier'), True, PpToken.PpToken('0', 'pp-number')),
            (PpToken.PpToken('NOWT', 'identifier'), True, PpToken.PpToken('1', 'pp-number')),
            )
        for aTok, aFlag, aResult in myCodeResult:
            self.assertEqual(
                myMap.defined(aTok, aFlag),
                aResult
                )

    def test_01(self):
        """MacroEnvDefined.test_01 - check defined() raises on non-identifier."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, 'f.h', 1)
        myMap.define(myGen, 'f.h', 2)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS',])
        self.assertEqual("""#define EGGS 2 /* f.h#2 Ref: 1 True */
#define SPAM 1 /* f.h#1 Ref: 1 True */""", str(myMap))
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""
1
"something"
'c'
#
""")
            )
        for aTok in myCpp.next():
            self.assertRaises(
                MacroEnv.ExceptionMacroEnv,
                myMap.defined,
                aTok,
                True,
                )

class MacroEnvSimpleReplaceObject(TestMacroEnv):
    """Tests the MacroEnv.MacroEnv simple replacement of Object only style macros."""

    def testDefineMapSimpleReplaceObject_00(self):
        """MacroEnv.MacroEnv - simple replacement of object style macros, no change on rescanning: "SPAM and EGGS" """
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS',])
        self.assertEqual(
            [
                PpToken.PpToken('1',   'pp-number'),
            ],
            myMap.replace(
                PpToken.PpToken('SPAM', 'identifier'),
                myGen)
            )
        self.assertEqual(
            [
                PpToken.PpToken('2',   'pp-number'),
            ],
            myMap.replace(
                PpToken.PpToken('EGGS', 'identifier'),
                myGen)
            )
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'SPAM and EGGS')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        self.assertEqual(
            [
                PpToken.PpToken('1',   'pp-number'),
                PpToken.PpToken(' ',   'whitespace'),
                PpToken.PpToken('and', 'identifier'),
                PpToken.PpToken(' ',   'whitespace'),
                PpToken.PpToken('2',   'pp-number'),
            ],
            repList,
            )

    def testDefineMapSimpleReplaceObject_01(self):
        """MacroEnv.MacroEnv - simple replacement of object style macros, no change on rescanning: "SPAM==EGGS" """
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS',])
        self.assertEqual(
            [
                PpToken.PpToken('1',   'pp-number'),
            ],
            myMap.replace(
                PpToken.PpToken('SPAM', 'identifier'),
                myGen)
            )
        self.assertEqual(
            [
                PpToken.PpToken('2',   'pp-number'),
            ],
            myMap.replace(
                PpToken.PpToken('EGGS', 'identifier'),
                myGen)
            )
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'SPAM==EGGS')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        self.assertEqual(
            [
                PpToken.PpToken('1',   'pp-number'),
                PpToken.PpToken('==',  'preprocessing-op-or-punc'),
                PpToken.PpToken('2',   'pp-number'),
            ],
            repList,
            )

class MacroEnvReplaceObject(TestMacroEnv):
    """Tests the MacroEnv.MacroEnv more complex replacement of Object only style macros."""

    def testDefineMapReplaceObject_00(self):
        """MacroEnv.MacroEnv - more complex replacement of object style macros, changes once on rescanning: "SPAM and EGGS" """
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM EGGS and eggs and EGGS
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS',])
        myReplacement = myMap.replace(
            PpToken.PpToken('SPAM', 'identifier'),
            None)
        myExpected = [
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('and',     'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('eggs',    'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('and',     'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('2',       'pp-number'),
            ]
        self._printDiff(myReplacement, myExpected)
        self.assertEqual(
            myExpected,
            myReplacement,
            )
        self.assertEqual(
            [
                PpToken.PpToken('2',   'pp-number'),
            ],
            myMap.replace(
                PpToken.PpToken('EGGS', 'identifier'),
                myGen
                )
            )
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'SPAM hold the EGGS')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        self.assertEqual(
            [
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('and',     'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('eggs',    'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('and',     'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('hold',    'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('the',     'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('2',       'pp-number'),
            ],
            repList,
            )

    def testDefineMapReplaceObject_00_00(self):
        """testDefineMapReplaceObject_00_00 - more complex replacement of object style macros, changes once on rescanning: "SPAM and EGGS" """
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM EGGS EGGS
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS',])
        myTok = PpToken.PpToken('SPAM', 'identifier')
        myReplacement = myMap.replace(myTok, None)
        myExpected = [
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('2',       'pp-number'),
            ]
        self._printDiff(myReplacement, myExpected)
        self.assertEqual(myExpected, myReplacement)

    def testDefineMapReplaceObject_01(self):
        """MacroEnv.MacroEnv - more complex replacement of object style macros, changes twice on rescanning: "Anyone for SPAM?" """
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM EGGS+EGGS
EGGS CHIPS or SALT?
CHIPS frites
SALT sel
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS', 'CHIPS', 'SALT',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'Anyone for SPAM?')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        self.assertEqual(
            [
                PpToken.PpToken('Anyone',  'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('for',     'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('frites',  'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('or',      'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('sel',     'identifier'),
                PpToken.PpToken('?',       'preprocessing-op-or-punc'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('frites',  'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('or',      'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('sel',     'identifier'),
                PpToken.PpToken('?',       'preprocessing-op-or-punc'),
                PpToken.PpToken('?',       'preprocessing-op-or-punc'),
            ],
            repList,
            )
        # This is another way of doing things
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'Anyone for frites or sel?+frites or sel??')
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

class MacroEnvSimpleReplaceFunction(TestMacroEnv):
    """Tests replacement with function style macros."""

    def testDefineMapSimpleReplaceFunction_00(self):
        """MacroEnv.MacroEnv - simple replacement of function style macros #define FUNC(a) a\\n, no replacement"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""FUNC(a) a
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['FUNC',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'FUNC(12);')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        self.assertEqual(
            [
                PpToken.PpToken('12',  'pp-number'),
                PpToken.PpToken(';', 'preprocessing-op-or-punc'),
            ],
            repList,
            )

    def testDefineMapSimpleReplaceFunction_01_00(self):
        """MacroEnv.MacroEnv - simple replacement of function style macros #define FUNC(a) a\\n where "FUNC" is called."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""FUNC(a) a
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['FUNC',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'FUNC')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        expectedList = [
                PpToken.PpToken('FUNC',    'identifier'),
            ]
        self._printDiff(repList, expectedList)
        self.assertEqual(expectedList, repList)

    def testDefineMapSimpleReplaceFunction_01_01(self):
        """MacroEnv.MacroEnv - simple replacement of function style macros #define FUNC(a) a\\n where "FUNC ;" is called."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""FUNC(a) a
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['FUNC',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'FUNC ;')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        expectedList = [
                PpToken.PpToken('FUNC',    'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken(';',       'preprocessing-op-or-punc'),
            ]
        self._printDiff(repList, expectedList)
        self.assertEqual(expectedList, repList)

    def testDefineMapSimpleReplaceFunction_01_02(self):
        """MacroEnv.MacroEnv - simple replacement of function style macros #define FUNC(a) a\\n where "FUNC FUNC(7)" is called."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""FUNC(a) a
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['FUNC',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'FUNC FUNC(7);')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        expectedList =             [
                PpToken.PpToken('FUNC',    'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('7',       'pp-number'),
                PpToken.PpToken(';',       'preprocessing-op-or-punc'),
            ]
        self._printDiff(repList, expectedList)
        self.assertEqual(expectedList, repList)

    def testDefineMapSimpleReplaceFunction_01_03(self):
        """MacroEnv.MacroEnv - simple replacement of function style macros #define FUNC(a) a\\n where "FUNC(12) plus FUNC minus FUNC(1);" is called."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""FUNC(a) a
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['FUNC',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'FUNC(12) plus FUNC minus FUNC(1);')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        expectedList =             [
                PpToken.PpToken('12',      'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('plus',    'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('FUNC',    'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('minus',   'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken(';',       'preprocessing-op-or-punc'),
            ]
        self._printDiff(repList, expectedList)
        self.assertEqual(expectedList, repList)

    def testDefineMapSimpleReplaceFunction_01_04(self):
        """MacroEnv.MacroEnv - simple replacement of function style macros #define INC(f) <f>\\n."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""INC(f) <f>
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['INC',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'INC(spam.h);')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        myExp = [
                PpToken.PpToken('<',        'preprocessing-op-or-punc'),
                PpToken.PpToken('spam',     'identifier'),
                PpToken.PpToken('.',        'preprocessing-op-or-punc'),
                PpToken.PpToken('h',        'identifier'),
                PpToken.PpToken('>',        'preprocessing-op-or-punc'),
                PpToken.PpToken(';',        'preprocessing-op-or-punc'),
            ]
        self._printDiff(repList, myExp)
        self.assertEqual(repList, myExp)
        # Now convert to header-name
        myObj = PpTokeniser.PpTokeniser()
        myHdrToks = myObj.reduceToksToHeaderName(repList)
        myExp = [
                PpToken.PpToken('<spam.h>',     'header-name'),
                PpToken.PpToken(';',            'preprocessing-op-or-punc'),
            ]
        self._printDiff(myHdrToks, myExp)
        self.assertEqual(myHdrToks, myExp)

    def testDefineMapSimpleReplaceFunction_01_05(self):
        """MacroEnv.MacroEnv - simple replacement of function style macros #define INC(f) # f\\n."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""INC(f) # f
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['INC',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'INC(spam.h);')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        myExp = [
                PpToken.PpToken(' ',            'whitespace'),
                PpToken.PpToken('"spam.h"',     'string-literal'),
                PpToken.PpToken(';',            'preprocessing-op-or-punc'),
            ]
        self._printDiff(repList, myExp)
        self.assertEqual(repList, myExp)
        # Now convert to header-name
        myObj = PpTokeniser.PpTokeniser()
        myHdrToks = myObj.reduceToksToHeaderName(repList)
        myExp = [
                PpToken.PpToken(' ',            'whitespace'),
                PpToken.PpToken('"spam.h"',     'header-name'),
                PpToken.PpToken(';',            'preprocessing-op-or-punc'),
            ]
        self._printDiff(myHdrToks, myExp)
        self.assertEqual(myHdrToks, myExp)

    def testDefineMapSimpleReplaceFunction_02(self):
        """MacroEnv.MacroEnv - simple replacement of function style macros by another function macro - no replacement."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""f(a) a+a
g(a) a(2)
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['f', 'g',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'g(x);\nf(y)')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'x(2);\ny+y')
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

    def testDefineMapSimpleReplaceFunction_03(self):
        """MacroEnv.MacroEnv - simple replacement of function style macros with rescanning replacement."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""f(a) a+a
g(a) a(2)
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['f', 'g',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'g(f);')
            )
        myMap.debugMarker = 'MacroEnvSimpleReplaceFunction.testDefineMapSimpleReplaceFunction_03()'
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'2+2;')
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

class MacroEnvCycles(TestMacroEnv):
    """Tests the MacroEnv.MacroEnv.
    cpp.exe produces the following output:

Cyclic References
=================
File - self reference:
----------------------
#define SPAM SPAM
SPAM

Result:
SPAM

File - a two reference cycle:
-----------------------------
#define SPAM EGGS
#define EGGS SPAM
SPAM
EGGS

File - a three reference cycle:
-------------------------------
#define SPAM EGGS
#define EGGS CHIPS
#define CHIPS SPAM
SPAM
EGGS
CHIPS

Result:
SPAM
EGGS
CHIPS

File - a self reference with a reference to it:
-----------------------------------------------
#define SPAM SPAM
#define EGGS SPAM
SPAM
EGGS

Result:
SPAM
SPAM

File - a two reference cycle with a reference to it:
----------------------------------------------------
#define SPAM EGGS
#define EGGS SPAM
#define CHIPS SPAM
SPAM
EGGS
CHIPS

Result:
SPAM
EGGS
SPAM

"""
    def testDefineMap_01(self):
        """MacroEnv.MacroEnv - recursive expansion to self."""
        # cpp.exe, given:
        # #define SPAM SPAM
        # SPAM
        #
        #Result:
        # SPAM
        #
        # cpp.exe, given:
        # #define SPAM SPAM+1
        # SPAM
        #
        #Result:
        # SPAM+1
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM SPAM\n"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['SPAM',])
        expTokS = [
                PpToken.PpToken('SPAM', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('SPAM', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)

    def testDefineMap_02(self):
        """MacroEnv.MacroEnv - recursive alias expansion to self. i.e. #define SPAM EGGS\\n#define EGGS SPAM\\n"""
        # cpp.exe, given:
        # #define SPAM EGGS
        # #define EGGS SPAM
        # SPAM
        # EGGS
        #
        # Result:
        # SPAM
        # EGGS
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM EGGS
EGGS SPAM
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS',])
        expTokS = [
                PpToken.PpToken('SPAM', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('SPAM', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)
        expTokS = [
                PpToken.PpToken('EGGS', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('EGGS', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)

    def testDefineMap_03(self):
        """MacroEnv.MacroEnv - recursive (2) expansion to self. SPAM->EGGS->CHIPS->SPAM"""
        # cpp.exe, given:
        # #define SPAM EGGS
        # #define EGGS CHIPS
        # #define CHIPS SPAM
        # SPAM
        # EGGS
        # CHIPS
        #
        #Result:
        # SPAM
        # EGGS
        # CHIPS
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM EGGS
EGGS CHIPS
CHIPS SPAM
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS', 'CHIPS',])
        # SPAM
        expTokS = [
                PpToken.PpToken('SPAM', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('SPAM', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)
        # EGGS
        expTokS = [
                PpToken.PpToken('EGGS', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('EGGS', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)
        # CHIPS
        expTokS = [
                PpToken.PpToken('CHIPS', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('CHIPS', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)

    def testDefineMap_04(self):
        """MacroEnv.MacroEnv - recursive (3) expansion to self. SPAM->EGGS->CHIPS->BEANS->SPAM"""
        # cpp.exe, given:
        # #define SPAM EGGS
        # #define EGGS CHIPS
        # #define CHIPS BEANS
        # #define BEANS SPAM
        # SPAM
        # EGGS
        # CHIPS
        # BEANS
        #
        #Result:
        # SPAM
        # EGGS
        # CHIPS
        # BEANS
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM EGGS
EGGS CHIPS
CHIPS BEANS
BEANS SPAM
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS', 'CHIPS', 'BEANS',])
        # SPAM
        expTokS = [
                PpToken.PpToken('SPAM', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('SPAM', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)
        # EGGS
        expTokS = [
                PpToken.PpToken('EGGS', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('EGGS', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)
        # CHIPS
        expTokS = [
                PpToken.PpToken('CHIPS', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('CHIPS', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)
        # BEANS
        expTokS = [
                PpToken.PpToken('BEANS', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('BEANS', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)

    def testDefineMap_05(self):
        """MacroEnv.MacroEnv - recursive expansion to self. SPAM->EGGS->SPAM, CHIPS-SPAM"""
        # cpp.exe, given:
        # #define SPAM EGGS
        # #define EGGS SPAM
        # #define CHIPS SPAM
        # SPAM
        # EGGS
        # CHIPS
        #
        #Result:
        # SPAM
        # EGGS
        # SPAM
        myMap = MacroEnv.MacroEnv()
        myStr = u"""SPAM EGGS
EGGS SPAM
CHIPS SPAM
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['SPAM', 'EGGS', 'CHIPS',])
        # SPAM
        expTokS = [
                PpToken.PpToken('SPAM', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('SPAM', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)
        # EGGS
        expTokS = [
                PpToken.PpToken('EGGS', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('EGGS', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)
        # CHIPS
        expTokS = [
                PpToken.PpToken('SPAM', 'identifier'),
            ]
        actTokS = myMap.replace(PpToken.PpToken('CHIPS', 'identifier'), myGen)
        self._printDiff(actTokS, expTokS)
        self.assertEqual(actTokS, expTokS)

class MacroEnvReplaceMixed(TestMacroEnv):
    """Tests replacement with mixed object and function style macros with complex declarations."""

    def testDefineMapReplace_00(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.3-4"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""hash_hash # ## #
mkstr(a) # a
in_between(a) mkstr(a)
join(c, d) in_between(c hash_hash d)
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        # Load the four macro definitions
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['hash_hash', 'mkstr', 'in_between', 'join',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'join(x,y)')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        self.assertEqual(
            [
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"x ## y"',    'string-literal'),
            ],
            repList,
            )

    def testDefineMapReplace_01(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-3 EXAMPLE 1"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""TABSIZE 100
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        # Load the one macro definition
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['TABSIZE',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'int table[TABSIZE];')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        #print '\nTRACE: repList:\n', '\n'.join([str(x) for x in repList])
        self.assertEqual(
            self.stringToTokens(u'int table[100];'),
            repList,
            )
        #print 'str(myMap):'
        #pprint.pprint(myMap._defineMap)
        #print myMap._defineMap
        #print str(myMap)
        self.assertEqual(
            """#define TABSIZE 100 /* #1 Ref: 2 True */""",
            str(myMap)
            )

    def testDefineMapReplace_02(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-4 EXAMPLE 2"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""max(a, b) ((a) > (b) ? (a) : (b))
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['max',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'max(x,y)')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        #print '\nTRACE: repList:\n', '\n'.join([str(x) for x in repList])
        #self.pprintReplacementList(repList)
        self.assertEqual(
            self.stringToTokens(u'((x) > (y) ? (x) : (y))'),
            repList,
            )
        #print 'str(myMap):'
        #pprint.pprint(myMap._defineMap)
        #print myMap._defineMap
        #print str(myMap)
        self.assertEqual(
            """#define max(a,b) ((a) > (b) ? (a) : (b)) /* #1 Ref: 2 True */""",
            str(myMap)
            )

    def testDefineMapReplace_03xxx(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3: h 5) -> f(2 * (~ 5))"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""f(a) f(x * (a))
x 2
g f
h g(~
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 4:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'g', 'h',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""h 5)""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        expectedTokens = self.stringToTokens(u'f(2 * (~ 5))')
        #expectedTokens = [
        #        PpToken.PpToken('f',       'identifier'),
        #        PpToken.PpToken('(',       'preprocessing-op-or-punc'),
        #        PpToken.PpToken('2',       'pp-number'),
        #        PpToken.PpToken(' ',       'whitespace'),
        #        PpToken.PpToken('*',       'preprocessing-op-or-punc'),
        #        PpToken.PpToken(' ',       'whitespace'),
        #        PpToken.PpToken('(',       'preprocessing-op-or-punc'),
        #        PpToken.PpToken('~',       'preprocessing-op-or-punc'),
        #        PpToken.PpToken(' ',       'whitespace'),
        #        PpToken.PpToken('5',       'pp-number'),
        #        PpToken.PpToken(')',       'preprocessing-op-or-punc'),
        #        PpToken.PpToken(')',       'preprocessing-op-or-punc'),
        #    ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(
            expectedTokens,
            repList,
            )
        # Or, from cpp:
        myResultString = u"""f(2 * (~ 5))"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myResultString)
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

    def testDefineMapReplace_03a(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3 f(f(z)) -> f(2 * (f(2 * (z[0]))))"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 2
f(a) f(x * (a))
z z[0]
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 3:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'z',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""f(f(z))""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'MacroEnvReplaceMixed.testDefineMapReplace_03a()'
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            #print '\nTRACE: testDefineMapReplace_03a [%d]' % r
            #self.pprintReplacementList(myReplacements)
            repList += myReplacements
        expectedTokens = [
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('z',       'identifier'),
                PpToken.PpToken('[',       'preprocessing-op-or-punc'),
                PpToken.PpToken('0',       'pp-number'),
                PpToken.PpToken(']',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
            ]
        #self.pprintReplacementList(repList)
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        # Or, from cpp:
        myResultString = u"""f(2 * (f(2 * (z[0]))))"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myResultString)
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

    def testDefineMapReplace_03b(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3 f(z) -> f(2 * (f(2 * (z[0]))))"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 2
f(a) f(x * (a))
z z[0]
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 3:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'z',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""f(z)""")
            )
        repList = []
        myGen = myCpp.next()
        for t in myGen:
            myReplacements = myMap.replace(t, myGen)
            repList += myReplacements
        expectedTokens = [
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('z',       'identifier'),
                PpToken.PpToken('[',       'preprocessing-op-or-punc'),
                PpToken.PpToken('0',       'pp-number'),
                PpToken.PpToken(']',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
            ]
        #self.pprintReplacementList(repList)
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        # Or, from cpp:
        myResultString = u"""f(2 * (z[0]))"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myResultString)
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

class TestMacroReplacementFuncRecursive(TestMacroEnv):
    """Tests replacement with mixed object and function style macros with complex declarations."""

    def testDefineMapFuncRecurseReplace_00(self):
        """MacroEnv.MacroEnv - function calling function - multiple depthes"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 2
f(a) f(x * (a))
z z[0]
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 3:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'z',])
        ##define x 2
        ##define f(a) f(x * (a))
        ##define z z[0]
        #f(z)            // f(2 * (z[0]))
        #f(f(z))         // f(2 * (f(2 * (z[0]))))
        #f(f(f(z)))      // f(2 * (f(2 * (f(2 * (z[0]))))))
        #f(f(f(f(z))))   // f(2 * (f(2 * (f(2 * (f(2 * (z[0]))))))))
        myCppResult = (
            (u'f(z)',            'f(2 * (z[0]))'),
            (u'f(f(z))',         'f(2 * (f(2 * (z[0]))))'),
            (u'f(f(f(z)))',      'f(2 * (f(2 * (f(2 * (z[0]))))))'),
            (u'f(f(f(f(z))))',   'f(2 * (f(2 * (f(2 * (f(2 * (z[0]))))))))'),
        )
        #print
        #print '%-20s  %-32s  %s' % ('Source', 'Got', 'Should have got')
        for c, r in myCppResult:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(c)
                )
            repList = []
            myGen = myCpp.next()
            for t in myGen:
                myReplacements = myMap.replace(t, myGen)
                repList += myReplacements
            myResult = PpToken.tokensStr(repList)
            #print '%-20s  %-32s  %s' % (c, myResult, r)
            self.assertEqual(myResult, r)

class TestMacroReplacementFuncRecursive_01(TestMacroEnv):
    """Tests replacement with mixed object and function style macros with complex declarations."""

    def testDefineMapFuncRecurseReplace_01(self):
        """MacroEnv.MacroEnv - function calling function - multiple depthes[1]"""
        #return
        #assert(0)
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 2
f(a) f(x * (a))
z z[0]
g f
t(a) a
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 5:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'z', 'g', 't'])
        myCppResult = (
            (u'z',                       'z[0]'),
            (u'f(z)',                    'f(2 * (z[0]))'),
            (u'f(f(z))',                 'f(2 * (f(2 * (z[0]))))'),
            (u'f(f(f(z)))',              'f(2 * (f(2 * (f(2 * (z[0]))))))'),
            (u'f(f(f(f(z))))',           'f(2 * (f(2 * (f(2 * (f(2 * (z[0]))))))))'),
            (u't(g)',                    'f'),
            (u't(g)(0)',                 'f(2 * (0))'),
            (u't(g)(0) + t',             'f(2 * (0)) + t'),
            (u't(g(0) + t);',            'f(2 * (0)) + t;'),
            (u't(t(g))',                 'f'),
            (u't(t(g)(0) + t)(1);',      'f(2 * (0)) + t(1);'),
            (u't(t)',                    't'),
            (u't(t);',                   't;'),
            (u't(t)();',                 't();'),
            (u't(t)(1)',                 't(1)'),
        )
        myMap.debugMarker = 'TestMacroReplacementFuncRecursive_01.testDefineMapFuncRecurseReplace_01()'
        #print
        #print '%-20s  %-40s  %s' % ('Source', 'Got', 'Should have got')
        for c, r in myCppResult:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(c)
                )
            #print '\n'.join([str(x) for x in myCpp.next()])
            #myCpp = PpTokeniser.PpTokeniser(
            #    theFileObj=StringIO.StringIO(c)
            #    )
            repList = []
            myGen = myCpp.next()
            for t in myGen:
                myReplacements = myMap.replace(t, myGen)
                repList += myReplacements
            myResult = PpToken.tokensStr(repList)
            #print '%-20s  %-40s  %-40s  %s' % (c, myResult, r, myResult==r)
            self.assertEqual(myResult, r)

    def testDefineMapFuncRecurseReplace_02(self):
        """MacroEnv.MacroEnv - function calling function - multiple depthes[2]"""
        #return
        #assert(0)
        myMap = MacroEnv.MacroEnv()
        myCpp = """#define t(a) a
#define u(a) a
t(t)();     // t();
t(u)();     // ;
t(t)(1);    // t(1);
t(u)(1);    // 1;
t(t(t))();  // t();
t(u(t))();  // t();
#define f(x) b x
f(f)(2)     // b f(2)

"""
        myStr = u"""t(a) a
u(a) a
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['t', 'u',])
        myCppResult = (
            (u't(t)();',                 't();'),
            (u't(u)();',                 ';'),
            (u't(t)(1);',                't(1);'),
            (u't(u)(1);',                '1;'),
            (u't(t(t))();',              't();'),
            (u't(u(t))();',              't();'),
        )
        myMap.debugMarker = 'TestMacroReplacementFuncRecursive_01.testDefineMapFuncRecurseReplace_02()'
        #print
        #print '%-20s  %-40s  %s' % ('Source', 'Got', 'Should have got')
        for c, r in myCppResult:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(c)
                )
            #print '\n'.join([str(x) for x in myCpp.next()])
            #myCpp = PpTokeniser.PpTokeniser(
            #    theFileObj=StringIO.StringIO(c)
            #    )
            repList = []
            myGen = myCpp.next()
            for t in myGen:
                myReplacements = myMap.replace(t, myGen)
                repList += myReplacements
            myResult = PpToken.tokensStr(repList)
            #print '%-20s  %-40s  %-40s  %s' % (c, myResult, r, myResult==r)
            self.assertEqual(myResult, r)

    def testDefineMapFuncRecurseReplace_03(self):
        """MacroEnv.MacroEnv - function calling function - multiple depthes[3]"""
        #return
        #assert(0)
        myMap = MacroEnv.MacroEnv()
        myCpp = """#define f(x) b x
f(f)(2)     // b f(2)
"""
        myStr = u"""f(x) b x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 1:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f',])
        myCppResult = (
            (u'f(f)(2)',     'b f(2)'),
            (u'f f(2)',      'f b 2'),
        )
        myMap.debugMarker = 'TestMacroReplacementFuncRecursive_01.testDefineMapFuncRecurseReplace_03()'
        #print
        #print '%-20s  %-40s  %s' % ('Source', 'Got', 'Should have got')
        for c, r in myCppResult:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(c)
                )
            #print '\n'.join([str(x) for x in myCpp.next()])
            #myCpp = PpTokeniser.PpTokeniser(
            #    theFileObj=StringIO.StringIO(c)
            #    )
            repList = []
            myGen = myCpp.next()
            for t in myGen:
                myReplacements = myMap.replace(t, myGen)
                #self.pprintReplacementList(myReplacements)
                repList += myReplacements
            myResult = PpToken.tokensStr(repList)
            #print '%-20s  %-40s  %-40s  %s' % (c, myResult, r, myResult==r)
            self.assertEqual(myResult, r)

class TestPpDefineReplace_Special_00(TestMacroEnv):
    """Tests special functionality ."""

    def test_00(self):
        """TestPpDefineReplace_Special_00.test_00() - a thorny problems with mixed object and function style macros.
#define x y (
#define y(a) a+1
x 2  )
"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x y(
y(a) a+1
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        # Load the macro definitions
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['x', 'y',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'x 2  )')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #[(' ', 7), ('2', 2), ('  ', 7), ('+', 5), ('1', 2)]
        self.assertEqual(
            [
                #PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('2',       'pp-number'),
                #PpToken.PpToken('  ',      'whitespace'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('1',       'pp-number'),
            ],
            repList,
            )
        # Or:
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'2+1')
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

    def test_01(self):
        """TestPpDefineReplace_Special_00.test_01(): example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3: h 5) -> f(2 * (~ 5))"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""f(a) f(2 * (a))
g f
h g(~
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 3:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'g', 'h',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""h 5)""")
            )
        repList = []
        myGen = myCpp.next()
        i = 0
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            #print '\nTRACE: test_01 [%d]' % i
            #self.pprintReplacementList(myReplacements)
            repList += myReplacements
            i += 1
        expectedTokens = [
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('~',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('5',       'pp-number'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
            ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(repList, expectedTokens)
        # Or, from cpp:
        myResultString = u"""f(2 * (~ 5))"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myResultString)
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

    def test_02(self):
        """TestPpDefineReplace_Special_00.test_02(): example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3: h 5) with x 2 -> f(2 * (~ 5))"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""f(a) f(x * (a))
x 2
g f
h g(~
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 4:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'g', 'h',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""h 5)""")
            )
        repList = []
        myGen = myCpp.next()
        for t in myGen:
            myReplacements = myMap.replace(t, myGen)
            repList += myReplacements
        expectedTokens = [
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('~',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('5',       'pp-number'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
            ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(repList, expectedTokens)
        # Or, from cpp:
        myResultString = u"""f(2 * (~ 5))"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myResultString)
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )


class SpecialClass(TestMacroEnv):
    pass

    def testDefineMapReplace_03_00(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3 f(z) -> f(2 * (z[0]))"""
        #assert(0)
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 2
f(a) f(x * (a))
z z[0]
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 3:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'z',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""f(z)""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        expectedTokens = [
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('z',       'identifier'),
                PpToken.PpToken('[',       'preprocessing-op-or-punc'),
                PpToken.PpToken('0',       'pp-number'),
                PpToken.PpToken(']',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
            ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        ## Or, from cpp:
        #myResultString = u"""f(2 * (f(2 * (z[0]))))"""
        #myCpp = PpTokeniser.PpTokeniser(
        #    theFileObj=StringIO.StringIO(myResultString)
        #    )
        #self.assertEqual(
        #    [t_tt for t_tt in myCpp.next()],
        #    repList,
        #    )

    def testDefineMapReplace_03_01(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3 f(f(z)) -> f(2 * (f(2 * (z[0]))))"""
        #assert(0)
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 2
f(a) f(x * (a))
z z[0]
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 3:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'z',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""f(f(z))""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        expectedTokens = [
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('z',       'identifier'),
                PpToken.PpToken('[',       'preprocessing-op-or-punc'),
                PpToken.PpToken('0',       'pp-number'),
                PpToken.PpToken(']',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
            ]
        #self.pprintReplacementList(repList)
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        # Or, from cpp:
        myResultString = u"""f(2 * (f(2 * (z[0]))))"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myResultString)
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

    def testDefineMapReplace_03_02(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3. f(y+1) + f(f(z))"""
        #assert(0)
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 3
f(a) f(x * (a))
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x',])
        myMap.undef(
            PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(u'x\n')
            ).next(),
            '',
            1,
        )
        self._checkMacroEnv(myGen, myMap, ['f',])
        myStr = u"""x 2
g f
z z[0]
h g(~
m(a) a(w)
w 0,1
t(a) a
p() int
q(x) x
r(x,y) x ## y
str(x) # x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        for i in range(11):
            myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'g', 'z', 'h', 'm', 'w', 't', 'p', 'q', 'r', 'str',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""f(y+1) + f(f(z))""")# % t(t(g)(0) + t)(1);""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            #self.pprintReplacementList(myReplacements)
            #print
            repList += myReplacements
        expectedTokens = [
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('y',       'identifier'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('z',       'identifier'),
                PpToken.PpToken('[',       'preprocessing-op-or-punc'),
                PpToken.PpToken('0',       'pp-number'),
                PpToken.PpToken(']',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
            ]
        #self.pprintReplacementList(repList)
        # TODO:
        #print '\ntestDefineMapReplace_03_02'
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        # Or:
        myResultString = u"""f(2 * (y+1)) + f(2 * (f(2 * (z[0]))))"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myResultString)
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

    def testDefineMapReplace_03_03_00(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3. t(g)(0)"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 2
f(a) f(x * (a))
g f
t(a) a
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 4:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'g', 't'])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""t(g(0))""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            #print 'Replacment of "%s" with:' % ttt
            #self.pprintReplacementList(myReplacements)
            #print
            repList += myReplacements
        expectedTokens = [
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('2',       'pp-number'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('*',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('0',       'pp-number'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
            ]
        #self.pprintReplacementList(repList)
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        # Or:
        myResultString = u"""f(2 * (0))"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myResultString)
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

    def testDefineMapReplace_03_04(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3. t(t(g)(0) + t)(1);"""
        """#define x 2
#define f(a) f(x * (a))
#define g f
#define t(a) a
t(g)                // f
t(g)(0)             // f(2 * (0))
t(g)(0) + t         // f(2 * (0)) + t
t(t(g)(0) + t)(1);  // f(2 * (0)) + t(1);
"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 2
f(a) f(x * (a))
g f
t(a) a
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 4:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'g', 't',])
        myResultPairs = (
            (u't(g)',                     'f'),
            (u't(g)(0)',                  'f(2 * (0))'),
            (u't(g)(0) + t',              'f(2 * (0)) + t'),
            (u't(g(0) + t);',             'f(2 * (0)) + t;'),
            (u't(t(g))',                  'f'),
            (u't(t(g)(0) + t)(1);',       'f(2 * (0)) + t(1);'),
            (u't(t)',                     't'),
            (u't(t);',                    't;'),
            (u't(t)();',                  't();'),
            (u't(t)(1)',                  't(1)'),
        )
        #print
        myMap.debugMarker = 'SpecialClass.testDefineMapReplace_03_04()'
        for tIn, tExp in myResultPairs:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(tIn)
                )
            repList = []
            myGen = myCpp.next()
            for ttt in myGen:
                myReplacements = myMap.replace(ttt, myGen)
                #print 'Replacment of "%s" with:' % ttt
                #self.pprintReplacementList(myReplacements)
                #print
                repList += myReplacements
            tRes = PpToken.tokensStr(repList)
            #print 'In: %-20s Got: %-20s Expected: %-20s  %s' \
            #    % (tIn, tRes, tExp, tRes==tExp)
            self.assertEqual(tRes, tExp)

    def testDefineMapReplace_03_05(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 3
f(a) f(x * (a))
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myMap.define(myGen, 'a.h', i+1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x',])
        myMap.undef(
            PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(u'x\n')
            ).next(),
            'a.h',
            i+1,
        )
        self._checkMacroEnv(myGen, myMap, ['f',])
        myStr = u"""x 2
g f
z z[0]
h g(~
m(a) a(w)
w 0,1
t(a) a
p() int
q(x) x
r(x,y) x ## y
str(x) # x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        for i in range(11):
            myMap.define(myGen, 'b.h', i+1)
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'g', 'z', 'h', 'm', 'w', 't', 'p', 'q', 'r', 'str',])
        strOriginal = u"""f(y+1) + f(f(z)) % t(t(g)(0) + t)(1);
g(x+(3,4)-w) | h 5) & m
(f)^m(m);
p() i[q()] = { q(1), r(2,3), r(4,), r(,5), r(,) };
char c[2][6] = { str(hello), str() };
"""
        strExpected = u"""f(2 * (y+1)) + f(2 * (f(2 * (z[0])))) % f(2 * (0)) + t(1);
f(2 * (2+(3,4)-0,1)) | f(2 * (~ 5)) & f(2 * (0,1))^m(0,1);
int i[] = { 1, 23, 4, 5,  };
char c[2][6] = { "hello", "" };
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(strOriginal)
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            #self.pprintReplacementList(myReplacements)
            #print
            repList += myReplacements
#         expectedTokens = self.stringToTokens(strExpected)
        #print 'TRACE:'
        #self.pprintTokensAsCtors(repList)
        #print 'TRACE:'
        #self.pprintTokensAsCtors(expectedTokens)
        expectedTokens = [
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('2', 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('*', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('y', 'identifier'),
            PpToken.PpToken('+', 'preprocessing-op-or-punc'),
            PpToken.PpToken('1', 'pp-number'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('+', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('2', 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('*', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('2', 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('*', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('z', 'identifier'),
            PpToken.PpToken('[', 'preprocessing-op-or-punc'),
            PpToken.PpToken('0', 'pp-number'),
            PpToken.PpToken(']', 'preprocessing-op-or-punc'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('%', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('2', 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('*', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('0', 'pp-number'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('+', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('t', 'identifier'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('1', 'pp-number'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(';', 'preprocessing-op-or-punc'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('2', 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('*', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('2', 'pp-number'),
            PpToken.PpToken('+', 'preprocessing-op-or-punc'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('3', 'pp-number'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken('4', 'pp-number'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken('-', 'preprocessing-op-or-punc'),
            PpToken.PpToken('0', 'pp-number'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken('1', 'pp-number'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('|', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('2', 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('*', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('~', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('5', 'pp-number'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('&', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('2', 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('*', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('0', 'pp-number'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken('1', 'pp-number'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken('^', 'preprocessing-op-or-punc'),
            PpToken.PpToken('m', 'identifier'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken('0', 'pp-number'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken('1', 'pp-number'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(';', 'preprocessing-op-or-punc'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('int', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('i', 'identifier'),
            PpToken.PpToken('[', 'preprocessing-op-or-punc'),
            PpToken.PpToken(']', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('=', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('{', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('1', 'pp-number'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('23', 'pp-number'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('4', 'pp-number'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('5', 'pp-number'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('}', 'preprocessing-op-or-punc'),
            PpToken.PpToken(';', 'preprocessing-op-or-punc'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('char', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('c', 'identifier'),
            PpToken.PpToken('[', 'preprocessing-op-or-punc'),
            PpToken.PpToken('2', 'pp-number'),
            PpToken.PpToken(']', 'preprocessing-op-or-punc'),
            PpToken.PpToken('[', 'preprocessing-op-or-punc'),
            PpToken.PpToken('6', 'pp-number'),
            PpToken.PpToken(']', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('=', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('{', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('"hello"', 'string-literal'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('""', 'string-literal'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('}', 'preprocessing-op-or-punc'),
            PpToken.PpToken(';', 'preprocessing-op-or-punc'),
            PpToken.PpToken('\n', 'whitespace'),

            ]
        #self.pprintReplacementList(repList)
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)

    def testDefineMapReplace_03_06(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3 with str(MacroEnv)"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 3
f(a) f(x * (a))
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myMap.define(myGen, 'a.h', i+1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x',])
        myMap.undef(
            PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(u'x\n')
            ).next(),
            'a.h',
            i+1,
        )
        self._checkMacroEnv(myGen, myMap, ['f',])
        myStr = u"""x 2
g f
z z[0]
h g(~
m(a) a(w)
w 0,1
t(a) a
p() int
q(x) x
r(x,y) x ## y
str(x) # x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        for i in range(11):
            myMap.define(myGen, 'b.h', i+1)
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'g', 'z', 'h', 'm', 'w', 't', 'p', 'q', 'r', 'str',])
        strOriginal = u"""f(y+1) + f(f(z)) % t(t(g)(0) + t)(1);
g(x+(3,4)-w) | h 5) & m
(f)^m(m);
p() i[q()] = { q(1), r(2,3), r(4,), r(,5), r(,) };
char c[2][6] = { str(hello), str() };
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(strOriginal)
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            #self.pprintReplacementList(myReplacements)
            #print
            repList += myReplacements
        #print 'str(myMap):'
        #pprint.pprint(myMap._defineMap)
        #print myMap._defineMap
        #print str(myMap)
        self.assertEqual(
            """#define f(a) f(x * (a)) /* a.h#2 Ref: 10 True */
#define g f /* b.h#2 Ref: 4 True */
#define h g(~ /* b.h#4 Ref: 2 True */
#define m(a) a(w) /* b.h#5 Ref: 3 True */
#define p() int /* b.h#8 Ref: 2 True */
#define q(x) x /* b.h#9 Ref: 3 True */
#define r(x,y) x ## y /* b.h#10 Ref: 5 True */
#define str(x) # x /* b.h#11 Ref: 3 True */
#define t(a) a /* b.h#7 Ref: 3 True */
#define w 0,1 /* b.h#6 Ref: 4 True */
#define x 2 /* b.h#1 Ref: 9 True */
#define z z[0] /* b.h#3 Ref: 2 True */""",
            str(myMap)
            )

    def testDefineMapReplace_03_07(self):
        """MacroEnv.MacroEnv - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3 with str(MacroEnv.genMacros())"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 3
f(a) f(x * (a))
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myMap.define(myGen, 'a.h', i+1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x',])
        myMap.undef(
            PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(u'x\n')
            ).next(),
            'a.h',
            i+1,
        )
        self._checkMacroEnv(myGen, myMap, ['f',])
        myStr = u"""x 2
g f
z z[0]
h g(~
m(a) a(w)
w 0,1
t(a) a
p() int
q(x) x
r(x,y) x ## y
str(x) # x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        for i in range(11):
            myMap.define(myGen, 'b.h', i+1)
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'g', 'z', 'h', 'm', 'w', 't', 'p', 'q', 'r', 'str',])
        strOriginal = u"""f(y+1) + f(f(z)) % t(t(g)(0) + t)(1);
g(x+(3,4)-w) | h 5) & m
(f)^m(m);
p() i[q()] = { q(1), r(2,3), r(4,), r(,5), r(,) };
char c[2][6] = { str(hello), str() };
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(strOriginal)
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        # Now examine the MacroEnvironment history
        myMacroStrS = [str(m) for m in myMap.genMacros()]
        myMacroStr = '\n'.join(myMacroStrS)
        #print 'myMacroStr:'
        #print myMacroStr
        self.assertEqual(
            """#define x 3 /* a.h#1 Ref: 1 False a.h#3 */
#define f(a) f(x * (a)) /* a.h#2 Ref: 10 True */
#define g f /* b.h#2 Ref: 4 True */
#define h g(~ /* b.h#4 Ref: 2 True */
#define m(a) a(w) /* b.h#5 Ref: 3 True */
#define p() int /* b.h#8 Ref: 2 True */
#define q(x) x /* b.h#9 Ref: 3 True */
#define r(x,y) x ## y /* b.h#10 Ref: 5 True */
#define str(x) # x /* b.h#11 Ref: 3 True */
#define t(a) a /* b.h#7 Ref: 3 True */
#define w 0,1 /* b.h#6 Ref: 4 True */
#define x 2 /* b.h#1 Ref: 9 True */
#define z z[0] /* b.h#3 Ref: 2 True */""",
            myMacroStr,
            )
        # Now examine the MacroEnvironment history for 'x'
        myMacroStrS = [str(m) for m in myMap.genMacros('x')]
        myMacroStr = '\n'.join(myMacroStrS)
        #print 'myMacroStr:'
        #print myMacroStr
        self.assertEqual(
            """#define x 3 /* a.h#1 Ref: 1 False a.h#3 */
#define x 2 /* b.h#1 Ref: 9 True */""",
            myMacroStr,
            )

class TestExample4(TestMacroEnv):
    """Tests ISO/IEC 9899:1999(E) 6.10.3.5-6 EXAMPLE 4"""
    def setUp(self):
        """#define str(s) # s
#define xstr(s) str(s)
#define debug(s, t) printf("x" # s "= %d, x" # t "= %s", \
x ## s, x ## t)
#define INCFILE(n) vers ## n // from previous #include example
#define glue(a, b) a ## b
#define xglue(a, b) glue(a, b)
#define HIGHLOW "hello"
#define LOW LOW ", world"
debug(1, 2);
fputs(str(strncmp("abc\0d", "abc", '\4') // this goes away
== 0) str(: @\n), s);
#include xstr(INCFILE(2).h)
glue(HIGH, LOW);
xglue(HIGH, LOW)

Becomes:
printf("x" "1" "= %d, x" "2" "= %s", x1, x2);
fputs("strncmp(\"abc\\0d\", \"abc\", '\\4') == 0" ": @\n",s);
#include "vers2.h"
"hello";
"hello" ", world"
"""
        self._macroEnv = MacroEnv.MacroEnv()
        myStr = u"""str(s) # s
xstr(s) str(s)
debug(s, t) printf("x" # s "= %d, x" # t "= %s", x ## s, x ## t)
INCFILE(n) vers ## n
glue(a, b) a ## b
xglue(a, b) glue(a, b)
HIGHLOW "hello"
LOW LOW ", world"
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 8:
            self._macroEnv.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(
            myGen,
            self._macroEnv,
            ['str', 'xstr', 'debug', 'INCFILE', 'glue', 'xglue', 'HIGHLOW', 'LOW'])

    def testSetUp(self):
        """TestExample4.testSetUp() - ISO/IEC 9899:1999(E) 6.10.3.5-6 EXAMPLE 4 test setUp()"""
        pass

    def test_00(self):
        """TestExample4.test_00() - ISO/IEC 9899:1999(E) 6.10.3.5-6 EXAMPLE 4 [0]"""

        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""debug(1, 2);
""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = self._macroEnv.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #print
        #self.pprintTokensAsCtors(repList)
        # printf("x" "1" "= %d, x" "2" "= %s", x1, x2);
        #expectedTokens = self.stringToTokens(u'printf("x"  "1" "= %d, x" "2" "= %s", x1, x2);')
        expectedTokens = [
            PpToken.PpToken('printf',       'identifier'),
            PpToken.PpToken('(',            'preprocessing-op-or-punc'),
            PpToken.PpToken('"x"',          'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"1"',          'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"= %d, x"',    'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"2"',          'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"= %s"',       'string-literal'),
            PpToken.PpToken(',',            'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('x1',           'concat'),
            PpToken.PpToken(',',            'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('x2',           'concat'),
            PpToken.PpToken(')',            'preprocessing-op-or-punc'),
            PpToken.PpToken(';',            'preprocessing-op-or-punc'),
            PpToken.PpToken('\n',           'whitespace'),
        ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)

    def test_01(self):
        """TestExample4.test_01() - ISO/IEC 9899:1999(E) 6.10.3.5-6 EXAMPLE 4 [1]"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""fputs(str(strncmp("abc\\0d", "abc", '\\4') == 0) str(: @\\n), s);
""")
            )
        # Should convert to:
        # fputs("strncmp(\"abc\\0d\", \"abc\", '\\4') == 0" ": @\\n",s);
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = self._macroEnv.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #print
        #self.pprintTokensAsCtors(repList)
        # printf("x" "1" "= %d, x" "2" "= %s", x1, x2);
        #expectedTokens = self.stringToTokens(u"""fputs("strncmp(\"abc\\0d\", \"abc\", '\\4') == 0" ": @\n",s);""")
        #print 'Expected:'
        #self.pprintTokensAsCtors(expectedTokens)
        expectedTokens = [
            PpToken.PpToken('fputs', 'identifier'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('"strncmp(\\"abc\\0d\\", \\"abc\\", \'\\4\') == 0"', 'string-literal'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('": @\\n"', 'string-literal'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('s', 'identifier'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(';', 'preprocessing-op-or-punc'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)

    def test_02(self):
        """TestExample4.test_02() - ISO/IEC 9899:1999(E) 6.10.3.5-6 EXAMPLE 4 [2]"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""#include xstr(INCFILE(2).h)
""")
            )
        # Should convert to:
        # #include "vers2.h"
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = self._macroEnv.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #print
        #self.pprintTokensAsCtors(repList)
        # printf("x" "1" "= %d, x" "2" "= %s", x1, x2);
        #expectedTokens = self.stringToTokens(u"""#include "vers2.h"\n""")
        #print 'Expected:'
        #self.pprintTokensAsCtors(expectedTokens)
        expectedTokens = [
            PpToken.PpToken('#',            'preprocessing-op-or-punc'),
            PpToken.PpToken('include',      'identifier'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"vers2.h"',    'string-literal'),
            PpToken.PpToken('\n',           'whitespace'),
        ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)

    def test_03(self):
        """TestExample4.test_03() - ISO/IEC 9899:1999(E) 6.10.3.5-6 EXAMPLE 4 [3]"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""glue(HIGH, LOW);
""")
            )
        # Should convert to:
        # "hello";
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = self._macroEnv.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #print
        #self.pprintTokensAsCtors(repList)
        # printf("x" "1" "= %d, x" "2" "= %s", x1, x2);
        #expectedTokens = self.stringToTokens(u"""#include "vers2.h"\n""")
        #print 'Expected:'
        #self.pprintTokensAsCtors(expectedTokens)
        expectedTokens = [
            PpToken.PpToken('"hello"',  'string-literal'),
            PpToken.PpToken(';',        'preprocessing-op-or-punc'),
            PpToken.PpToken('\n',       'whitespace'),
        ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)

    def test_04(self):
        """TestExample4.test_04() - ISO/IEC 9899:1999(E) 6.10.3.5-6 EXAMPLE 4 [4]"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""xglue(HIGH, LOW)
""")
            )
        # Should convert to:
        # "hello" ", world"
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = self._macroEnv.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #print
        #self.pprintTokensAsCtors(repList)
        # printf("x" "1" "= %d, x" "2" "= %s", x1, x2);
        #expectedTokens = self.stringToTokens(u"""#include "vers2.h"\n""")
        #print 'Expected:'
        #self.pprintTokensAsCtors(expectedTokens)
        expectedTokens = [
            PpToken.PpToken('"hello"',      'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('", world"',    'string-literal'),
            PpToken.PpToken('\n',           'whitespace'),
        ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)

    def test_10(self):
        """TestExample4.test_10() - ISO/IEC 9899:1999(E) 6.10.3.5-6 EXAMPLE 4"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""debug(1, 2);
fputs(str(strncmp("abc\\0d", "abc", '\\4') == 0) str(: @\\n), s);
#include xstr(INCFILE(2).h)
glue(HIGH, LOW);
xglue(HIGH, LOW)
""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = self._macroEnv.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #print
        #self.pprintTokensAsCtors(repList)
        # printf("x" "1" "= %d, x" "2" "= %s", x1, x2);
        #expectedTokens = self.stringToTokens(u"""#include "vers2.h"\n""")
        #print 'Expected:'
        #self.pprintTokensAsCtors(expectedTokens)
        expectedTokens = [
            PpToken.PpToken('printf',       'identifier'),
            PpToken.PpToken('(',            'preprocessing-op-or-punc'),
            PpToken.PpToken('"x"',          'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"1"',          'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"= %d, x"',    'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"2"',          'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"= %s"',       'string-literal'),
            PpToken.PpToken(',',            'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('x1',           'concat'),
            PpToken.PpToken(',',            'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('x2',           'concat'),
            PpToken.PpToken(')',            'preprocessing-op-or-punc'),
            PpToken.PpToken(';',            'preprocessing-op-or-punc'),
            PpToken.PpToken('\n',           'whitespace'),
            #
            PpToken.PpToken('fputs',        'identifier'),
            PpToken.PpToken('(',            'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"strncmp(\\"abc\\0d\\", \\"abc\\", \'\\4\') == 0"', 'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('": @\\n"',        'string-literal'),
            PpToken.PpToken(',',            'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('s',            'identifier'),
            PpToken.PpToken(')',            'preprocessing-op-or-punc'),
            PpToken.PpToken(';',            'preprocessing-op-or-punc'),
            PpToken.PpToken('\n',           'whitespace'),
            #
            PpToken.PpToken('#',            'preprocessing-op-or-punc'),
            PpToken.PpToken('include',      'identifier'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"vers2.h"',    'string-literal'),
            PpToken.PpToken('\n',           'whitespace'),
            #
            PpToken.PpToken('"hello"',      'string-literal'),
            PpToken.PpToken(';',            'preprocessing-op-or-punc'),
            PpToken.PpToken('\n',           'whitespace'),
            #
            PpToken.PpToken('"hello"',      'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('", world"',    'string-literal'),
            PpToken.PpToken('\n',           'whitespace'),
        ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)

    def test_11(self):
        """TestExample4.test_10() - ISO/IEC 9899:1999(E) 6.10.3.5-6 EXAMPLE 4 with str(MacroEnv)"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""debug(1, 2);
fputs(str(strncmp("abc\\0d", "abc", '\\4') == 0) str(: @\\n), s);
#include xstr(INCFILE(2).h)
glue(HIGH, LOW);
xglue(HIGH, LOW)
""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = self._macroEnv.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        #print 'str(self._macroEnv):'
        #print str(self._macroEnv)
        self.assertEqual(
            """#define HIGHLOW "hello" /* #1 Ref: 3 True */
#define INCFILE(n) vers ## n /* #1 Ref: 2 True */
#define LOW LOW ", world" /* #1 Ref: 2 True */
#define debug(s,t) printf("x" # s "= %d, x" # t "= %s", x ## s, x ## t) /* #1 Ref: 2 True */
#define glue(a,b) a ## b /* #1 Ref: 3 True */
#define str(s) # s /* #1 Ref: 4 True */
#define xglue(a,b) glue(a, b) /* #1 Ref: 2 True */
#define xstr(s) str(s) /* #1 Ref: 2 True */""",
            str(self._macroEnv)
            )

    def test_12(self):
        """TestExample4.test_10() - ISO/IEC 9899:1999(E) 6.10.3.5-6 EXAMPLE 4 with str(genMacros)"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""debug(1, 2);
fputs(str(strncmp("abc\\0d", "abc", '\\4') == 0) str(: @\\n), s);
#include xstr(INCFILE(2).h)
glue(HIGH, LOW);
xglue(HIGH, LOW)
""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = self._macroEnv.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        myMacroStrS = [str(m) for m in self._macroEnv.genMacros()]
        myMacroStr = '\n'.join(myMacroStrS)
        #print 'myMacroStr:'
        #print myMacroStr
        self.assertEqual(
            """#define HIGHLOW "hello" /* #1 Ref: 3 True */
#define INCFILE(n) vers ## n /* #1 Ref: 2 True */
#define LOW LOW ", world" /* #1 Ref: 2 True */
#define debug(s,t) printf("x" # s "= %d, x" # t "= %s", x ## s, x ## t) /* #1 Ref: 2 True */
#define glue(a,b) a ## b /* #1 Ref: 3 True */
#define str(s) # s /* #1 Ref: 4 True */
#define xglue(a,b) glue(a, b) /* #1 Ref: 2 True */
#define xstr(s) str(s) /* #1 Ref: 2 True */""",
            myMacroStr,
            )

class TestExample5(TestMacroEnv):
    """Tests ISO/IEC 9899:1999 (E) 6.10.3.5-7 EXAMPLE 5
7 EXAMPLE 5 To illustrate the rules for placemarker preprocessing tokens, the sequence"""

    """ISO/IEC 9899:1999 (E) 6.10.3.5-7 EXAMPLE 5
7 EXAMPLE 5 To illustrate the rules for placemarker preprocessing tokens, the sequence
#define t(x,y,z) x ## y ## z
int j[] = { t(1,2,3), t(,4,5), t(6,,7), t(8,9,),
t(10,,), t(,11,), t(,,12), t(,,) };
results in
int j[] = { 123, 45, 67, 89,
10, 11, 12, };"""

    def setUp(self):
        """"""
        self._macroEnv = MacroEnv.MacroEnv()
        myStr = u"""t(x,y,z) x ## y ## z
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 1:
            self._macroEnv.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(
            myGen,
            self._macroEnv,
            ['t',])

    def testSetUp(self):
        """TestExample5.testSetUp() - ISO/IEC 9899:1999 (E) 6.10.3.5-7 EXAMPLE 5 test setUp()"""
        pass

    def test_00(self):
        """TestExample5.test_00() - ISO/IEC 9899:1999 (E) 6.10.3.5-7 EXAMPLE 5 [0]"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""int j[] = { t(1,2,3), t(,4,5), t(6,,7), t(8,9,),
t(10,,), t(,11,), t(,,12), t(,,) };
""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = self._macroEnv.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #print
        #self.pprintTokensAsCtors(repList)
        # printf("x" "1" "= %d, x" "2" "= %s", x1, x2);
#         expectedTokens = self.stringToTokens(u"""int j[] = { 123, 45, 67, 89,
#10, 11, 12,  };""")
        expectedTokens = [
            PpToken.PpToken('int',      'identifier'),
            PpToken.PpToken(' ',        'whitespace'),
            PpToken.PpToken('j',        'identifier'),
            PpToken.PpToken('[',        'preprocessing-op-or-punc'),
            PpToken.PpToken(']',        'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',        'whitespace'),
            PpToken.PpToken('=',        'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',        'whitespace'),
            PpToken.PpToken('{',        'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',        'whitespace'),
            PpToken.PpToken('123',      'pp-number'),
            PpToken.PpToken(',',        'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',        'whitespace'),
            PpToken.PpToken('45',       'pp-number'),
            PpToken.PpToken(',',        'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',        'whitespace'),
            PpToken.PpToken('67',       'pp-number'),
            PpToken.PpToken(',',        'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',        'whitespace'),
            PpToken.PpToken('89',       'pp-number'),
            PpToken.PpToken(',',        'preprocessing-op-or-punc'),
            PpToken.PpToken('\n',       'whitespace'),
            PpToken.PpToken('10',       'pp-number'),
            PpToken.PpToken(',',        'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',        'whitespace'),
            PpToken.PpToken('11',       'pp-number'),
            PpToken.PpToken(',',        'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',        'whitespace'),
            PpToken.PpToken('12',       'pp-number'),
            PpToken.PpToken(',',        'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',        'whitespace'),
            PpToken.PpToken(' ',        'whitespace'),
            PpToken.PpToken('}',        'preprocessing-op-or-punc'),
            PpToken.PpToken(';',        'preprocessing-op-or-punc'),
            PpToken.PpToken('\n',       'whitespace'),
        ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)

    def test_01(self):
        """TestExample5.test_00() - ISO/IEC 9899:1999 (E) 6.10.3.5-7 EXAMPLE 5 [0] with str(MacroEnv)"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""int j[] = { t(1,2,3), t(,4,5), t(6,,7), t(8,9,),
t(10,,), t(,11,), t(,,12), t(,,) };
""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = self._macroEnv.replace(ttt, myGen)
            repList += myReplacements
        #print 'str(self._macroEnv):'
        #print str(self._macroEnv)
        self.assertEqual(
            """#define t(x,y,z) x ## y ## z /* #1 Ref: 9 True */""",
            str(self._macroEnv)
            )

class MacroEnvReplaceFunctionLowLevel(TestMacroEnv):
    """Tests low level operation on a MacroEnv.MacroEnv for function like macros."""
    def _genMap_00(self):
        """Return a map of four defines."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 2
f(a) f(x * (a))
g f
t(a) a
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 4:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['x', 'f', 'g', 't',])
        return myMap

    def _genMap_01(self):
        """Return a map of three defines."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""z z[0]
x 4
f(a) f(x+a)
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 3:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['z', 'x', 'f',])
        return myMap

    def test_replaceFunctionStyleMacro_00(self):
        """MacroEnv.MacroEnv._replaceFunctionStyleMacro() - low level 'f(7)'"""
        myMap = self._genMap_01()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"f(7)")
            )
        myGen = myCpp.next()
        myArgTokType = next(myGen)
        #print 'Argument t_tt:', myArgTokType
        #mySeenSet = set()
        myReplacements = myMap.replace(myArgTokType, myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        #self.pprintReplacementList(myReplacements)
        expectedTokens = [
            PpToken.PpToken('f',       'identifier'),
            PpToken.PpToken('(',       'preprocessing-op-or-punc'),
            PpToken.PpToken('4',       'pp-number'),
            PpToken.PpToken('+',       'preprocessing-op-or-punc'),
            PpToken.PpToken('7',       'pp-number'),
            PpToken.PpToken(')',       'preprocessing-op-or-punc'),
        ]
        self._printDiff(myReplacements, expectedTokens)
        self.assertEqual(myReplacements, expectedTokens)

    def test_replaceFunctionStyleMacro_01(self):
        """MacroEnv.MacroEnv._replaceFunctionStyleMacro() - low level 'f(z)'"""
        myMap = self._genMap_01()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"f(z)")
            )
        myGen = myCpp.next()
        myArgTokType = next(myGen)
        #print 'Argument t_tt:', myArgTokType
        myReplacements = myMap.replace(myArgTokType, myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        #self.pprintReplacementList(myReplacements)
        expectedTokens = [
            PpToken.PpToken('f',       'identifier'),
            PpToken.PpToken('(',       'preprocessing-op-or-punc'),
            PpToken.PpToken('4',       'pp-number'),
            PpToken.PpToken('+',       'preprocessing-op-or-punc'),
            PpToken.PpToken('z',       'identifier'),
            PpToken.PpToken('[',       'preprocessing-op-or-punc'),
            PpToken.PpToken('0',       'pp-number'),
            PpToken.PpToken(']',       'preprocessing-op-or-punc'),
            PpToken.PpToken(')',       'preprocessing-op-or-punc'),
        ]
        self._printDiff(myReplacements, expectedTokens)
        self.assertEqual(myReplacements, expectedTokens)

    def test_replaceFunctionStyleMacro_02(self):
        """MacroEnv.MacroEnv._replaceFunctionStyleMacro() - low level '#define foo(y) bar y\\nfoo(foo) (2)'"""
        #/* From http://gcc.gnu.org/onlinedocs/cppinternals/Macro-Expansion.html
        #*/
        ##define foo(y) bar y
        #foo(foo) (2)
        #// Result: bar foo (2)
        #/* Expalanation:
        #
        #
        #*/
        myMap = MacroEnv.MacroEnv()
        myStr = u"""foo(x) bar x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 1:
            myMap.define(myGen, '', 1)
            i += 1
        # Check that all tokens have been consumed
        self._checkMacroEnv(myGen, myMap, ['foo',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"foo(foo) (2)")
            )
        myGen = myCpp.next()
        myReplacements = []
        for myArgTokType in myGen:
            myReplacements += myMap.replace(myArgTokType, myGen)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        #self.pprintReplacementList(myReplacements)
        expectedTokens = [
            PpToken.PpToken('bar',     'identifier'),
            PpToken.PpToken(' ',       'whitespace'),
            PpToken.PpToken('foo',     'identifier'),
            PpToken.PpToken(' ',       'whitespace'),
            PpToken.PpToken('(',       'preprocessing-op-or-punc'),
            PpToken.PpToken('2',       'pp-number'),
            PpToken.PpToken(')',       'preprocessing-op-or-punc'),
        ]
        self._printDiff(myReplacements, expectedTokens)
        self.assertEqual(myReplacements, expectedTokens)

class RecursiveFunctionLike(TestMacroEnv):
    pass

    def _genMap_00(self):
        """Return a map of three defines."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 4
f(a) f(x+a)
z z[0]
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 3:
            myMap.define(myGen, '', 1)
            i += 1
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        self.assertEqual(3, len(myMap))
        return myMap

    def testRecursiveFunctionLike_00(self):
        """testRecursiveFunctionLike_00: f(z) -> f(4+z[0])"""
        myMap = self._genMap_00()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""f(z)""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'RecursiveFunctionLike.testRecursiveFunctionLike_00()'
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        expectedTokens = [
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('4',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('z',       'identifier'),
                PpToken.PpToken('[',       'preprocessing-op-or-punc'),
                PpToken.PpToken('0',       'pp-number'),
                PpToken.PpToken(']',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
            ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        # Or, from cpp:
        myResultString = u"""f(4+z[0])"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myResultString)
            )
        self.assertEqual(
            [t_tt for t_tt in myCpp.next()],
            repList,
            )

    def testRecursiveFunctionLike_01(self):
        """testRecursiveFunctionLike_01: f(f(z)) -> f(4 +f(4 +z[0]))"""
        myMap = self._genMap_00()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""f(f(z))""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'RecursiveFunctionLike.testRecursiveFunctionLike_01()'
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            #print '%s -> %s' % (t, myReplacements)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        expectedTokens = [
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('4',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('f',       'identifier'),
                PpToken.PpToken('(',       'preprocessing-op-or-punc'),
                PpToken.PpToken('4',       'pp-number'),
                PpToken.PpToken('+',       'preprocessing-op-or-punc'),
                PpToken.PpToken('z',       'identifier'),
                PpToken.PpToken('[',       'preprocessing-op-or-punc'),
                PpToken.PpToken('0',       'pp-number'),
                PpToken.PpToken(']',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
                PpToken.PpToken(')',       'preprocessing-op-or-punc'),
            ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        # Or, from cpp:
        myResultString = u"""f(4+f(4+z[0]))"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myResultString)
            )
        aS, bS = self._extendPair([t_tt for t_tt in myCpp.next()], repList)
        for a, b in zip(aS, bS):
            self.assertEqual(a, b)
        #self.assertEqual(
        #    [t_tt for t_tt in myCpp.next()],
        #    repList,
        #    )


class MacroEnvFuncReexamine(TestMacroEnv):
    """Tests reexamination with function style macros."""

    def testDefineFunction_00(self):
        """MacroEnvFuncReexamine.testDefineFunction_00 - function like macros with rescanning replacement [00]."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""f(a) a+a
g(a) a(2)
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['f', 'g',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'g(f);')
            )
        myMap.debugMarker = 'MacroEnvFuncReexamine.testDefineFunction_00()'
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        #print '\nTRACE: repList:\n', '\n'.join([str(x) for x in repList])
        #myCpp = PpTokeniser.PpTokeniser(
        #    theFileObj=StringIO.StringIO('2+2;')
        #    )
        self.assertEqual(self.stringToTokens(u'2+2;'), repList)

    def testDefineFunction_01(self):
        """MacroEnvFuncReexamine.testDefineFunction_01 - function like macros with rescanning replacement [01]."""
        """#define x 2
#define f(a) f(x * (a))
#define g f
#define t(a) a
t(g)                // f
t(g)(0)             // f(2 * (0))
t(g)(0) + t         // f(2 * (0)) + t
t(t(g)(0) + t)(1);  // f(2 * (0)) + t(1);
"""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 2
f(a) f(x * (a))
g f
t(a) a
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 4:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['x', 'f', 'g', 't',])
        myResultPairs = (
            (u't(g)',                     'f'),
            (u't(g)(0)',                  'f(2 * (0))'),
            (u't(g)(0) + t',              'f(2 * (0)) + t'),
            (u't(g(0) + t);',             'f(2 * (0)) + t;'),
            (u't(t(g))',                  'f'),
            (u't(t(g)(0) + t)(1);',       'f(2 * (0)) + t(1);'),
            (u't(t)',                     't'),
            (u't(t);',                    't;'),
            (u't(t)();',                  't();'),
            (u't(t)(1)',                  't(1)'),
        )
        #print
        myMap.debugMarker = 'MacroEnvFuncReexamine.testDefineFunction_00()'
        for tIn, tExp in myResultPairs:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(tIn)
                )
            repList = []
            myGen = myCpp.next()
            for ttt in myGen:
                myReplacements = myMap.replace(ttt, myGen)
                #print 'Replacment of "%s" with:' % ttt
                #self.pprintReplacementList(myReplacements)
                #print
                repList += myReplacements
            tRes = PpToken.tokensStr(repList)
            #print 'In: %-20s Got: %-20s Expected: %-20s  %s' \
            #    % (tIn, tRes, tExp, tRes==tExp)
            self.assertEqual(tRes, tExp)


class TestExample3(TestMacroEnv):
    """Tests example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3"""
    def _createEnv(self):
        """Creates a MacroEnv for the #defines in this example."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""x 3
f(a) f(x * (a))
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['f', 'x',])
        myMap.undef(
            PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(u'x\n')
            ).next(),
            '',
            1,
        )
        self._checkMacroEnv(myGen, myMap, ['f',])
        myStr = u"""x 2
g f
z z[0]
h g(~
m(a) a(w)
w 0,1
t(a) a
p() int
q(x) x
r(x,y) x ## y
str(x) # x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        for i in range(11):
            myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['f', 'x', 'g', 'z', 'h', 'm', 'w', 't', 'p', 'q', 'r', 'str',])
        return myMap

    def testTestExample3_line_01(self):
        """TestExample3.testTestExample3_line_01() - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3 line 1"""
        myMap = self._createEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""f(y+1) + f(f(z)) % t(t(g)(0) + t)(1);
""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestExample3.testTestExample3_line_01()'
        for ttt in myGen:
            #if ttt.t == 'r':
            #    print ttt
            myReplacements = myMap.replace(ttt, myGen)
            #self.pprintReplacementList(myReplacements)
            #print
            repList += myReplacements
        expectedString = u"""f(2 * (y+1)) + f(2 * (f(2 * (z[0])))) % f(2 * (0)) + t(1);
"""
        repString = self.tokensToString(repList)
        expectedTokens = self.stringToTokens(expectedString)
        #self.pprintReplacementList(repList)
        self._printDiff(repList, expectedTokens)
        #print 'Got:'
        #print repString
        #print 'Expected:'
        #print expectedString
        self.assertEqual(repString, expectedString)

    def testTestExample3_line_02(self):
        """TestExample3.testTestExample3_line_02() - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3 line 2"""
        myMap = self._createEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""g(x+(3,4)-w) | h 5) & m(f)^m(m);
""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestExample3.testTestExample3_line_02()'
        for ttt in myGen:
            #if ttt.t == 'r':
            #    print ttt
            myReplacements = myMap.replace(ttt, myGen)
            #self.pprintReplacementList(myReplacements)
            #print
            repList += myReplacements
        expectedString = u"""f(2 * (2+(3,4)-0,1)) | f(2 * (~ 5)) & f(2 * (0,1))^m(0,1);
"""
        repString = self.tokensToString(repList)
        expectedTokens = self.stringToTokens(expectedString)
        #self.pprintReplacementList(repList)
        self._printDiff(repList, expectedTokens)
        #print 'Got:'
        #print repString
        #print 'Expected:'
        #print expectedString
        self.assertEqual(repString, expectedString)

    def testTestExample3_line_03(self):
        """TestExample3.testTestExample3_line_03() - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3 line 3"""
        myMap = self._createEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""p() i[q()] = { q(1), r(2,3), r(4,), r(,5), r(,) };
""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestExample3.testTestExample3_line_03()'
        for ttt in myGen:
            #if ttt.t == 'r':
            #    print ttt
            myReplacements = myMap.replace(ttt, myGen)
            #self.pprintReplacementList(myReplacements)
            #print
            repList += myReplacements
        expectedString = """int i[] = { 1, 23, 4, 5,  };
"""
        repString = self.tokensToString(repList)
        #expectedTokens = self.stringToTokens(expectedString)
        #self.pprintReplacementList(repList)
        #self._printDiff(repList, expectedTokens)
        #print 'Got:'
        #print repString
        #print 'Expected:'
        #print expectedString
        self.assertEqual(repString, expectedString)

    def testTestExample3_line_04(self):
        """TestExample3.testTestExample3_line_04() - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3 line 4"""
        myMap = self._createEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""char c[2][6] = { str(hello), str() };""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestExample3.testTestExample3_line_04()'
        for ttt in myGen:
            #if ttt.t == 'r':
            #    print ttt
            myReplacements = myMap.replace(ttt, myGen)
            #self.pprintReplacementList(myReplacements)
            #print
            repList += myReplacements
        expectedString = """char c[2][6] = {  "hello",  "" };"""
        repString = self.tokensToString(repList)
        #expectedTokens = self.stringToTokens(expectedString)
        #self.pprintReplacementList(repList)
        #self._printDiff(repList, expectedTokens)
        #print 'Got:'
        #print repString
        #print 'Expected:'
        #print expectedString
        self.assertEqual(repString, expectedString)

    def testTestExample3_str_x(self):
        """TestExample3.testTestExample3_str_x() - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3 str(x)"""
        myMap = self._createEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""str()""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestExample3.testTestExample3_str_x()'
        for ttt in myGen:
            #if ttt.t == 'r':
            #    print ttt
            myReplacements = myMap.replace(ttt, myGen)
            #self.pprintReplacementList(myReplacements)
            #print
            repList += myReplacements
        expectedString = ' ""'
        repString = self.tokensToString(repList)
        #expectedTokens = self.stringToTokens(expectedString)
        #self.pprintReplacementList(repList)
        #self._printDiff(repList, expectedTokens)
        #print 'Got:'
        #print repString
        #print 'Expected:'
        #print expectedString
        self.assertEqual(repString, expectedString)

    def testTestExample3(self):
        """TestExample3.testTestExample3() - mixed replacement - example in ISO/IEC 9899:1999(E) 6.10.3.5-5 EXAMPLE 3"""
        myMap = self._createEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""f(y+1) + f(f(z)) % t(t(g)(0) + t)(1);
g(x+(3,4)-w) | h 5) & m(f)^m(m);
p() i[q()] = { q(1), r(2,3), r(4,), r(,5), r(,) };
char c[2][6] = { str(hello), str() };""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestExample3.testTestExample3()'
        for ttt in myGen:
            #if ttt.t == 'r':
            #    print ttt
            myReplacements = myMap.replace(ttt, myGen)
            #self.pprintReplacementList(myReplacements)
            #print
            repList += myReplacements
        expectedString = """f(2 * (y+1)) + f(2 * (f(2 * (z[0])))) % f(2 * (0)) + t(1);
f(2 * (2+(3,4)-0,1)) | f(2 * (~ 5)) & f(2 * (0,1))^m(0,1);
int i[] = { 1, 23, 4, 5,  };
char c[2][6] = {  "hello",  "" };"""
        repString = self.tokensToString(repList)
        #expectedTokens = self.stringToTokens(expectedString)
        #self.pprintReplacementList(repList)
        #self._printDiff(repList, expectedTokens)
        #print 'Got:'
        #print repString
        #print 'Expected:'
        #print expectedString
        self.assertEqual(repString, expectedString)

class TestMacroRedefinition(TestMacroEnv):
    """Tests macro redefinition"""
    def testObjectLikeRedefinition_00(self):
        """TestMacroRedefinition.testObjectLikeRedefinition_00(): #defines then redefines an object like macro correctly."""
        myMap = MacroEnv.MacroEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'OBJ 1 + 2\n')
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['OBJ',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'OBJ    1    +    2    \n')
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['OBJ',])

    def testObjectLikeRedefinition_01(self):
        """TestMacroRedefinition.testObjectLikeRedefinition_01(): #defines then redefines an object like macro incorrectly."""
        myMap = MacroEnv.MacroEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'OBJ 1 + 2\n')
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['OBJ',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'OBJ 1+2\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            MacroEnv.ExceptionMacroEnvInvalidRedefinition,
            myMap.define,
            myGen,
            '',
            1,
            )
        self._checkMacroEnv(myGen, myMap, ['OBJ',])

    def testFunctionLikeRedefinition_00(self):
        """TestMacroRedefinition.testFunctionLikeRedefinition_00(): #defines then redefines an function like macro correctly."""
        myMap = MacroEnv.MacroEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'FUNC_LIKE(a) ( a )\n')
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['FUNC_LIKE',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'FUNC_LIKE( a )( /* note the white space */ a /* other stuff on this line */ )\n')
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['FUNC_LIKE',])

    def testFunctionLikeRedefinition_01(self):
        """TestMacroRedefinition.testFunctionLikeRedefinition_01(): #defines then redefines an function like macro incorrectly."""
        myMap = MacroEnv.MacroEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'FUNC_LIKE(a) ( a )\n')
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['FUNC_LIKE',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'FUNC_LIKE(b) ( b )\n')
            )
        myGen = myCpp.next()
        self.assertRaises(
            MacroEnv.ExceptionMacroEnvInvalidRedefinition,
            myMap.define,
            myGen,
            '',
            1,
            )
        self._checkMacroEnv(myGen, myMap, ['FUNC_LIKE',])

class TestMacroUndef(TestMacroEnv):
    """Tests macro #undef command"""
    def testObjectLikeUndef_00(self):
        """TestMacroUndef.testObjectLikeUndef_00(): #defines then undefs an object like macro correctly."""
        myMap = MacroEnv.MacroEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'OBJ 1 + 2\n')
            )
        myGen = myCpp.next()
        myMap.define(myGen, 'obj.h', 1)
        self._checkMacroEnv(myGen, myMap, ['OBJ',])
        # undef something that is not there
        self.assertEquals(
            None,
            myMap.undef(
                PpTokeniser.PpTokeniser(
                    theFileObj=io.StringIO(u'NOTHING\n')
                ).next(),
                '',
                1,
            )
        )
        # Check undef has not removed anything
        self._checkMacroEnv(myGen, myMap, ['OBJ',])
        # undef something that is there
        myMap.undef(
                PpTokeniser.PpTokeniser(
                    theFileObj=io.StringIO(u'OBJ\n')
                ).next(),
                'obj.h',
                1
            )
#===============================================================================
#        myGen = myCpp.next()
#        myMacro = PpDefine.PpDefine(myGen, '', 1)
#        self.assertEquals(
#            myMacro,
#            myMap.undef(
#                PpTokeniser.PpTokeniser(
#                    theFileObj=StringIO.StringIO('OBJ\n')
#                ).next()
#            )
#        )
#===============================================================================
        self._checkMacroEnv(myGen, myMap, [])

    def testObjectLikeUndef_01(self):
        """TestMacroUndef.testObjectLikeUndef_01(): #defines then undefs an object like macro and invokes genMacros()."""
        myEnv = MacroEnv.MacroEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'OBJ 1 + 2\n')
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'obj.h', 1)
        self._checkMacroEnv(myGen, myEnv, ['OBJ',])
        # undef something that is not there
        myEnv.undef(
            PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(u'NOTHING\n')
            ).next(),
            '',
            1,
        )
        # Check undef has not removed anything
        self._checkMacroEnv(myGen, myEnv, ['OBJ',])
        # undef something that is there
        myEnv.undef(
                PpTokeniser.PpTokeniser(
                    theFileObj=io.StringIO(u'OBJ\n')
                ).next(),
                'obj.h',
                2,
            )
        self._checkMacroEnv(myGen, myEnv, [])
        # Redefine it
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'OBJ 3 + 4\n')
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'obj.h', 3)
        self._checkMacroEnv(myGen, myEnv, ['OBJ',])
        #for aMacro in myEnv.genMacros():
        #    print aMacro
        #print
        myExpList = [
                     '#define OBJ 1 + 2 /* obj.h#1 Ref: 2 False obj.h#2 */',
                     '#define OBJ 3 + 4 /* obj.h#3 Ref: 1 True */',
                     ]
        myList = [str(m) for m in myEnv.genMacros()]
        #print myList
        self.assertEquals(myExpList, myList)
        myList = [str(m) for m in myEnv.genMacros('OBJ')]
        self.assertEquals(myExpList, myList)
        myList = [str(m) for m in myEnv.genMacros('NOTHING')]
        self.assertEquals([], myList)

    def testFunctionLikeUndef_00(self):
        """TestMacroUndef.testFunctionLikeUndef_00(): #defines then undefs an function like macro correctly."""
        myMap = MacroEnv.MacroEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'FUNC_LIKE(a) ( a )\n')
            )
        myGen = myCpp.next()
        myMap.define(myGen, 'F.h', 1)
        self._checkMacroEnv(myGen, myMap, ['FUNC_LIKE',])
        # undef something that is not there
        self.assertEquals(
            None,
            myMap.undef(
                PpTokeniser.PpTokeniser(
                    theFileObj=io.StringIO(u'NOTHING\n')
                ).next(),
                '',
                1,
            )
        )
        self._checkMacroEnv(myGen, myMap, ['FUNC_LIKE',])
        # undef it
        myMap.undef(
            PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(u'FUNC_LIKE\n')
            ).next(),
            'F.h',
            2,
        )
#===============================================================================
#        myGen = myCpp.next()
#        myMacro = PpDefine.PpDefine(myGen, '', 1)
#        self.assertEquals(
#            myMacro,
#            myMap.undef(
#                PpTokeniser.PpTokeniser(
#                    theFileObj=StringIO.StringIO('FUNC_LIKE\n')
#                ).next()
#            )
#        )
#===============================================================================
        self._checkMacroEnv(myGen, myMap, [])

class TestFromCppInternals(TestMacroEnv):
    """Misc. tests"""
    def test_00(self):
        """TestFromCppInternals.test_00 - #define foo(x) bar x\\n then: foo(foo) (2)."""
        ##define foo(x) bar x
        #foo(foo) (2)
        #which fully expands to "bar foo (2)".
        myMap = MacroEnv.MacroEnv()
        myStr = u"""foo(x) bar x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 1:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['foo',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""foo(foo) (2)""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestFromCppInternals.test_00()'
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        expectedString = """bar foo (2)"""
        repString = self.tokensToString(repList)
        #expectedTokens = self.stringToTokens(expectedString)
        #self.pprintReplacementList(repList)
        #self._printDiff(repList, expectedTokens)
        #print 'Got:'
        #print repString
        #print 'Expected:'
        #print expectedString
        self.assertEqual(repString, expectedString)

class TestFromCppInternalsTokenspacing(TestMacroEnv):
    """Misc. tests on token spacing."""
    def test_01(self):
        """TestFromCppInternalsTokenspacing.test_01 - Token spacing torture test #define PLUS +"""
        ##define PLUS +
        ##define EMPTY
        ##define f(x) =x=
        #+PLUS -EMPTY- PLUS+ f(=)
        #-> + + - - + + = = =
        #not
        #-> ++ -- ++ ===
        myMap = MacroEnv.MacroEnv()
        myStr = u"""PLUS +
EMPTY
f(x) =x=
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 3:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['PLUS', 'EMPTY', 'f'])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""+PLUS -EMPTY- PLUS+ f(=)""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestFromCppInternals.test_01()'
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        expectedString = """+ + - - + + = = ="""
        repString = self.tokensToString(repList)
        #expectedTokens = self.stringToTokens(expectedString)
        #self.pprintReplacementList(repList)
        #self._printDiff(repList, expectedTokens)
        #print 'Got:'
        #print repString
        #print 'Expected:'
        #print expectedString
        self.assertEqual(repString, expectedString)

    def test_02(self):
        """TestFromCppInternalsTokenspacing.test_02 - Token spacing torture test #define add(x, y, z) x + y +z;"""
        ##define add(x, y, z) x + y +z;
        #sum = add (1,2, 3);
        #-> sum = 1 + 2 +3;
        myMap = MacroEnv.MacroEnv()
        # NOTE: Had to take spurious ';' out
        myStr = u"""add(x, y, z) x + y +z
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 1:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['add',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""sum = add (1,2, 3);""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestFromCppInternals.test_02()'
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        expectedString = """sum = 1 + 2 +3;"""
        repString = self.tokensToString(repList)
        #expectedTokens = self.stringToTokens(expectedString)
        #self.pprintReplacementList(repList)
        #self._printDiff(repList, expectedTokens)
        #print 'Got:'
        #print repString
        #print 'Expected:'
        #print expectedString
        self.assertEqual(repString, expectedString)

    def test_03(self):
        """TestFromCppInternalsTokenspacing.test_03 - Token spacing torture test [foo]"""
        ##define foo bar
        ##define bar baz
        #[foo]
        #-> [baz]
        myMap = MacroEnv.MacroEnv()
        # NOTE: Had to take spurious ';' out
        myStr = u"""foo bar
bar baz
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['foo', 'bar',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""[foo]""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestFromCppInternals.test_03()'
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        expectedString = """[baz]"""
        repString = self.tokensToString(repList)
        #expectedTokens = self.stringToTokens(expectedString)
        #self.pprintReplacementList(repList)
        #self._printDiff(repList, expectedTokens)
        #print 'Got:'
        #print repString
        #print 'Expected:'
        #print expectedString
        self.assertEqual(repString, expectedString)

    def test_04(self):
        """TestFromCppInternalsTokenspacing.test_04 - Token spacing torture test [foo] EMPTY"""
        ##define foo bar
        ##define bar EMPTY baz
        ##define EMPTY
        #[foo] EMPTY;
        #-> [ baz] ;

        myMap = MacroEnv.MacroEnv()
        # NOTE: Had to take spurious ';' out
        myStr = u"""foo bar
bar EMPTY baz
EMPTY
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 3:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(myGen, myMap, ['foo', 'bar', 'EMPTY'])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""[foo] EMPTY;""")
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestFromCppInternals.test_04()'
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        expectedString = """[ baz] ;"""
        repString = self.tokensToString(repList)
        #expectedTokens = self.stringToTokens(expectedString)
        #self.pprintReplacementList(repList)
        #self._printDiff(repList, expectedTokens)
        #print 'Got:'
        #print repString
        #print 'Expected:'
        #print expectedString
        self.assertEqual(repString, expectedString)

class TestFromStandardMisc(TestMacroEnv):
    """Misc. tests from the standard."""
    def test_00(self):
        """TestFromStandardMisc.test_00 - #define glue(a, b) a ## b etc."""
        """#define glue(a, b) a ## b
#define xglue(a, b) glue(a, b)
#define HIGHLOW "hello"
#define LOW LOW ", world"
#define LO " earth"
#define f(a) f(a)
glue(HIGH, LOW) // "hello"
glue(HIGH, LO) // HIGHLO
"""
        myMap = MacroEnv.MacroEnv(enableTrace=True)
        myStr = u"""glue(a, b) a ## b
xglue(a, b) glue(a, b)
HIGHLOW "hello"
LOW LOW ", world"
LO " earth"
f(a) f(a)
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 6:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(
            myGen,
            myMap,
            ['glue', 'xglue', 'HIGHLOW', 'LOW', 'LO', 'f']
            )
        myInOut = (
            (u'glue(HIGH,LOW)', '"hello"',),
            (u'glue(HIGH, LOW)', '"hello"',),
            (u'glue(HIGH,LOW )', '"hello"',),
            (u'glue(HIGH, LOW )', '"hello"',),
            (u'glue( HIGH,LOW)', '"hello"',),
            (u'glue( HIGH, LOW)', '"hello"',),
            (u'glue( HIGH,LOW )', '"hello"',),
            (u'glue( HIGH, LOW )', '"hello"',),
            (u'glue(HIGH ,LOW)', '"hello"',),
            (u'glue(HIGH , LOW)', '"hello"',),
            (u'glue(HIGH ,LOW )', '"hello"',),
            (u'glue(HIGH , LOW )', '"hello"',),
            (u'glue( HIGH ,LOW)', '"hello"',),
            (u'glue( HIGH , LOW)', '"hello"',),
            (u'glue( HIGH ,LOW )', '"hello"',),
            (u'glue( HIGH , LOW )', '"hello"',),
            #
            (u'glue(HIGH,LO)',  'HIGHLO',),
            (u'glue(HIGH, LO)',  'HIGHLO',),
            (u'glue(HIGH,LO )',  'HIGHLO',),
            (u'glue(HIGH, LO )',  'HIGHLO',),
            (u'glue( HIGH,LO)',  'HIGHLO',),
            (u'glue( HIGH, LO)',  'HIGHLO',),
            (u'glue( HIGH,LO )',  'HIGHLO',),
            (u'glue( HIGH, LO )',  'HIGHLO',),
            (u'glue(HIGH ,LO)',  'HIGHLO',),
            (u'glue(HIGH , LO)',  'HIGHLO',),
            (u'glue(HIGH ,LO )',  'HIGHLO',),
            (u'glue(HIGH , LO )',  'HIGHLO',),
            )
        #print
        for myIn, myOut in myInOut:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(myIn)
                )
            repList = []
            myGen = myCpp.next()
            myMap.debugMarker = 'TestFromStandardMisc.test_00()'
            for ttt in myGen:
                myReplacements = myMap.replace(ttt, myGen)
                repList += myReplacements
            repString = self.tokensToString(repList)
            #expectedTokens = self.stringToTokens(myOut)
            #self.pprintReplacementList(repList)
            #self._printDiff(repList, expectedTokens)
            #print 'Got:'
            #print repString
            #print 'Expected:'
            #print expectedString
            #print 'In: %-20s Got: %-20s Expected: %-20s  %s' \
            #    % (myIn, repString, myOut, repString==myOut)
            self.assertEqual(repString, myOut)

    def test_01(self):
        """TestFromStandardMisc.test_00 - #define glue(a, b) a ## b etc and use xglue."""
        """#define glue(a, b) a ## b
#define xglue(a, b) glue(a, b)
#define HIGHLOW "hello"
#define LOW LOW ", world"
#define LO " earth"
#define f(a) f(a)
xglue(HIGH, LOW) // "hello" ", world"
"""
        myMap = MacroEnv.MacroEnv(enableTrace=True)
        myStr = u"""glue(a, b) a ## b
xglue(a, b) glue(a, b)
HIGHLOW "hello"
LOW LOW ", world"
LO " earth"
f(a) f(a)
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 6:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(
            myGen,
            myMap,
            ['glue', 'xglue', 'HIGHLOW', 'LOW', 'LO', 'f']
            )
        myInOut = (
            #('glue(HIGH,LOW)',  '"hello"',),
            (u'xglue(HIGH,LOW)', '"hello" ", world"'),
            (u'xglue(HIGH,LO)', 'HIGH" earth"'),

            )
        #print
        for myIn, myOut in myInOut:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(myIn)
                )
            repList = []
            myGen = myCpp.next()
            myMap.debugMarker = 'TestFromStandardMisc.test_01()'
            for ttt in myGen:
                myReplacements = myMap.replace(ttt, myGen)
                repList += myReplacements
            repString = self.tokensToString(repList)
            #expectedTokens = self.stringToTokens(myOut)
            #self.pprintReplacementList(repList)
            #self._printDiff(repList, expectedTokens)
            #print 'Got:'
            #print repString
            #print 'Expected:'
            #print expectedString
            #print 'In: %-20s Got: %-20s Expected: %-20s  %s' \
            #    % (myIn, repString, myOut, repString==myOut)
            self.assertEqual(repString, myOut)

    def test_ambiguos_00(self):
        """TestFromStandardMisc.test_ambiguos_00 - not ambiguos."""
        """#define f(a) a*g
#define g f
"""
        myMap = MacroEnv.MacroEnv(enableTrace=True)
        myStr = u"""f(a) a*g
g f
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(
            myGen,
            myMap,
            ['f', 'g',]
            )
        myInOut = (
            (u'f(2)(9)', '2*f(9)',),
            )
        #print
        for myIn, myOut in myInOut:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(myIn)
                )
            repList = []
            myGen = myCpp.next()
            myMap.debugMarker = 'TestFromStandardMisc.test_ambiguos_00()'
            for ttt in myGen:
                myReplacements = myMap.replace(ttt, myGen)
                repList += myReplacements
            repString = self.tokensToString(repList)
            #expectedTokens = self.stringToTokens(myOut)
            #self.pprintReplacementList(repList)
            #self._printDiff(repList, expectedTokens)
            #print 'Got:'
            #print repString
            #print 'Expected:'
            #print expectedString
            #print 'In: %-20s Got: %-20s Expected: %-20s  %s' \
            #    % (myIn, repString, myOut, repString==myOut)
            self.assertEqual(repString, myOut)

    def test_ambiguos_01(self):
        """TestFromStandardMisc.test_ambiguos_01 - ambiguos."""
        """#define f(a) a*g
#define g(a) f(a)
f(2)(9)
"""
        myMap = MacroEnv.MacroEnv(enableTrace=True)
        myStr = u"""f(a) a*g
g f
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(
            myGen,
            myMap,
            ['f', 'g',]
            )
        myInOut = (
            (u'f(2)(9)', '2*f(9)',),
            #(u'f(2)(9)', '2*9*g',),
            )
        #print
        for myIn, myOut in myInOut:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(myIn)
                )
            repList = []
            myGen = myCpp.next()
            myMap.debugMarker = 'TestFromStandardMisc.test_ambiguos_01()'
            for ttt in myGen:
                myReplacements = myMap.replace(ttt, myGen)
                repList += myReplacements
            repString = self.tokensToString(repList)
            #expectedTokens = self.stringToTokens(myOut)
            #self.pprintReplacementList(repList)
            #self._printDiff(repList, expectedTokens)
            #print 'Got:'
            #print repString
            #print 'Expected:'
            #print expectedString
            #print 'In: %-20s Got: %-20s Expected: %-20s  %s' \
            #    % (myIn, repString, myOut, repString==myOut)
            self.assertEqual(repString, myOut)

class TestStringise(TestMacroEnv):
    """Test the '#' operator."""
    """$ cpp -E
#define s(x) # x
s(foo)
s("foo")
s(s(foo))
# 1 "<stdin>"
# 1 "<built-in>"
# 1 "<command line>"
# 1 "<stdin>"

"foo"
"\"foo\""
"s(foo)"
"""
    def test_00(self):
        """TestStringise.test_00() - #define s(x) # x [0]."""
        """#define s(x) # x
s(foo)
s("foo")
s(s(foo))
Becomes:
"foo"
"\"foo\""
"s(foo)"
"""
        myMap = MacroEnv.MacroEnv(enableTrace=True)
        myStr = u"""s(x) # x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 1:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(
            myGen,
            myMap,
            ['s',]
            )
        myInOut = (
            (u's(spam)', ' "spam"',),
            (u's("spam")', ' "\\"spam\\""',),
            (u's(s(spam))', ' "s(spam)"',),
            )
        #print
        for myIn, myOut in myInOut:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(myIn)
                )
            repList = []
            myGen = myCpp.next()
            myMap.debugMarker = 'TestStringise.test_00'
            for ttt in myGen:
                myReplacements = myMap.replace(ttt, myGen)
                repList += myReplacements
            repString = self.tokensToString(repList)
            #expectedTokens = self.stringToTokens(myOut)
            #self.pprintReplacementList(repList)
            #self._printDiff(repList, expectedTokens)
            #print 'Got:'
            #print repString
            #print 'Expected:'
            #print expectedString
            #print 'In: %-20s Got: %-20s Expected: %-20s  %s' \
            #    % (myIn, repString, myOut, repString==myOut)
            self.assertEqual(repString, myOut)

    def test_01(self):
        """TestStringise.test_01() - #define s(x) # x [1]."""
        """#define s(x) # x
s(foo)
s("foo")
s(s(foo))
Becomes:
"foo"
"\"foo\""
"s(foo)"
"""
        myMap = MacroEnv.MacroEnv(enableTrace=True)
        myStr = u"""s(x) # x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 1:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(
            myGen,
            myMap,
            ['s',]
            )
        myInOut = (
            # cpp:
            # "\"abc\\0d\""
            (u's("abc\\0d")', u' "\\"abc\\0d\\""'),
            )
        #print
        for myIn, myOut in myInOut:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(myIn)
                )
            repList = []
            myGen = myCpp.next()
            myMap.debugMarker = 'TestStringise.test_01'
            for ttt in myGen:
                myReplacements = myMap.replace(ttt, myGen)
                repList += myReplacements
            repString = self.tokensToString(repList)
            expectedTokens = self.stringToTokens(myOut)
            #self.pprintReplacementList(repList)
            self._printDiff(repList, expectedTokens)
            #print 'Got:'
            #print repString
            #print 'Expected:'
            #print expectedString
            #print 'In: %-20s Got: %-20s Expected: %-20s  %s' \
            #    % (myIn, repString, myOut, repString==myOut)
            self.assertEqual(repString, myOut)

    def test_02(self):
        """TestStringise.test_02() - #define s(x) # x [2]."""
        """#define s(x) # x
s(@)
"""
        myMap = MacroEnv.MacroEnv(enableTrace=True)
        myStr = u"""s(x) # x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 1:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(
            myGen,
            myMap,
            ['s',]
            )
        myInOut = (
            # cpp:
            (u's(@)', ' "@"'),
            )
        for myIn, myOut in myInOut:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(myIn)
                )
            repList = []
            myGen = myCpp.next()
            myMap.debugMarker = 'TestStringise.test_02()'
            for ttt in myGen:
                myReplacements = myMap.replace(ttt, myGen)
                repList += myReplacements
            repString = self.tokensToString(repList)
            self.assertEqual(repString, myOut)

class TestPredefinedRedefinition(TestMacroEnv):
    """Tests redefining predefined macros."""
    def test_00(self):
        """TestPredefinedInCtor.test_00 - Define an arbitrary macro as a stdPredefMacros then trying to redefine it fails."""
        myEnv = MacroEnv.MacroEnv(
                    enableTrace=True,
            stdPredefMacros = {
                    '__DATE__'      : 'Apr 02 2009\n',
                    '__TIME__'      : '14:21:32\n',
                }
            )
        self.assertRaises(
            MacroEnv.ExceptionMacroReplacementPredefinedRedefintion,
            myEnv.define,
            PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(u'__DATE__ Apr 02 2009\n')
            ).next(),
            'mt.h',
            1
        )
        self.assertRaises(
            MacroEnv.ExceptionMacroReplacementPredefinedRedefintion,
            myEnv.define,
            PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(u'__TIME__ 14:21:32\n')
            ).next(),
            'mt.h',
            1
        )

    def test_01(self):
        """TestPredefinedInCtor.test_01 - Define an arbitrary macro as a stdPredefMacros then trying to redefine it fails."""
        myEnv = MacroEnv.MacroEnv(
                    enableTrace=True,
            stdPredefMacros = {
                'SPAM' : '\n',
                }
            )
        self.assertRaises(
            MacroEnv.ExceptionMacroReplacementPredefinedRedefintion,
            myEnv.define,
            PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(u'SPAM\n')
            ).next(),
            'mt.h',
            1
        )

    def test_02(self):
        """TestPredefinedInCtor.test_02 - Define a macro in the ctor with a token stream that is to short."""
        myPredef = {
            '__LINE__'      : '1',
        }
        self.assertRaises(
            PpDefine.ExceptionCpipDefineInit,
            MacroEnv.MacroEnv,
            True,           # enableTrace
            myPredef,       # stdPredefMacros
        )

    def test_03(self):
        """TestPredefinedInCtor.test_03 - attempt to define 'defined' in ctor."""
        myPredef = {
            'defined'      : '\n',
        }
        self.assertRaises(
            MacroEnv.ExceptionMacroReplacementInit,
            MacroEnv.MacroEnv,
            True,           # enableTrace
            myPredef,       # stdPredefMacros
        )

    def test_04(self):
        """TestPredefinedInCtor.test_04 - attempt to redefine 'defined'."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""defined
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        self.assertRaises(
            MacroEnv.ExceptionMacroReplacementPredefinedRedefintion,
            myMap.define,
            myGen,
            '',
            1,
            )

    def test_11(self):
        """TestPredefinedInCtor.test_11 - Define a macro in the ctor that is a predefined one."""
        myPredef = {
            '__LINE__'      : '1\n',
            '__FILE__'      : 'afile\n',
            '__DATE__'      : 'Apr 02 2009\n',
            '__TIME__'      : '14:21:32\n',
            '__STDC__'      : '1\n',
            '__cplusplus'   : '1\n',
        }
        myMap = MacroEnv.MacroEnv(enableTrace=True, stdPredefMacros=myPredef)
        for aName in list(myPredef.keys()):
            self.assertEqual(
                True,
                myMap.mightReplace(
                    PpToken.PpToken(aName, 'identifier')
                )
            )

    def test_12(self):
        """TestPredefinedInCtor.test_12 - Attempt to redefine a macro that is a predefined one."""
        myMap = MacroEnv.MacroEnv(
            stdPredefMacros = {
                '__STDC__'     : '1\n',
                '__cplusplus'  : '201103L\n',
            }
        )
        for aMacro in (
            u'__LINE__ \n',
            u'__FILE__ \n',
            u'__DATE__ \n',
            u'__TIME__ \n',
            u'__STDC__ \n',
            u'__cplusplus \n',
            ):
#             print(aMacro)
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(aMacro)
                )
            myGen = myCpp.next()
            self.assertRaises(
                MacroEnv.ExceptionMacroReplacementPredefinedRedefintion,
                myMap.define,
            myGen,
            '',
            1,
            )

class TestPredefined__FILE__(TestMacroEnv):
    """Tests __FILE__ setting."""
    def setUp(self):
        self._macroName = '__FILE__'

    def test_00(self):
        """TestPredefined__FILE__.test_00 - redefining __FILE__ fails when using define()."""
        myMap = MacroEnv.MacroEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'%s\n' % self._macroName)
            )
        myGen = myCpp.next()
        self.assertRaises(
            MacroEnv.ExceptionMacroReplacementPredefinedRedefintion,
            myMap.define,
            myGen,
            '',
            1,
            )

    def test_01(self):
        """TestPredefined__FILE__.test_01 - redefining __FILE__ succeeds when using set__FILE__()."""
        myMap = MacroEnv.MacroEnv()
        myMap.set__FILE__(u'42\n')
        self.assertEqual(
            True,
            myMap.mightReplace(
                PpToken.PpToken(self._macroName, 'identifier')
            )
        )
        self.assertEqual(
            self.stringToTokens(u'42'),
            myMap.replace(
                PpToken.PpToken(self._macroName, 'identifier'), None)
            )

class TestPredefined__LINE__(TestMacroEnv):
    """Tests __LINE__ setting."""
    def setUp(self):
        self._macroName = '__LINE__'

    def test_00(self):
        """TestPredefined__LINE__.test_00 - redefining __LINE__ fails when using define()."""
        myMap = MacroEnv.MacroEnv()
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'%s\n' % self._macroName)
            )
        myGen = myCpp.next()
        self.assertRaises(
            MacroEnv.ExceptionMacroReplacementPredefinedRedefintion,
            myMap.define,
            myGen,
            '',
            1,
            )

    def test_01(self):
        """TestPredefined__LINE__.test_01 - redefining __LINE__ succeeds when using set__LINE__()."""
        myMap = MacroEnv.MacroEnv()
        myMap.set__LINE__(u'42\n')
        self.assertEqual(
            True,
            myMap.mightReplace(
                PpToken.PpToken(self._macroName, 'identifier')
            )
        )
        self.assertEqual(
            self.stringToTokens(u'42'),
            myMap.replace(
                PpToken.PpToken(self._macroName, 'identifier'), None)
            )

class MacroEnvIncRefCount(TestMacroEnv):
    """Tests that the reference count of a macro is appropriatly incremented."""

    def test_00(self):
        """MacroEnvIncRefCount.test_00() refcount zero on definition.""" 
        myMap = MacroEnv.MacroEnv()
        myStr = u"""REFCOUNT 1
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self.assertTrue(myMap.hasMacro('REFCOUNT'))
        self.assertEqual(0, myMap.macro('REFCOUNT').refCount)
        # Checking existance increments refcount
        self._checkMacroEnv(myGen, myMap, ['REFCOUNT', ])
        self.assertEqual(1, myMap.macro('REFCOUNT').refCount)

    def test_00_00(self):
        """MacroEnvIncRefCount.test_00_00() refcount raises on macro() if name not defined.""" 
        myMap = MacroEnv.MacroEnv()
        myStr = u"""REFCOUNT 1
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self.assertTrue(myMap.hasMacro('REFCOUNT'))
        self.assertEqual(0, myMap.macro('REFCOUNT').refCount)
        # Checking existance increments refcount
        self._checkMacroEnv(myGen, myMap, ['REFCOUNT', ])
        self.assertEqual(1, myMap.macro('REFCOUNT').refCount)
        self.assertRaises(
            MacroEnv.ExceptionMacroEnvNoMacroDefined,
            myMap.macro,
            'NOTHING'
            )

    def test_01(self):
        """MacroEnvIncRefCount.test_01() refcount increments on isDefined().""" 
        myMap = MacroEnv.MacroEnv()
        myStr = u"""REFCOUNT 1
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self.assertTrue(myMap.hasMacro('REFCOUNT'))
        self.assertEqual(0, myMap.macro('REFCOUNT').refCount)
        # Checking existance increments refcount
        self._checkMacroEnv(myGen, myMap, ['REFCOUNT', ])
        self.assertEqual(1, myMap.macro('REFCOUNT').refCount)
        myMap.isDefined(PpToken.PpToken('REFCOUNT', 'identifier'))
        self.assertEqual(2, myMap.macro('REFCOUNT').refCount)

    def test_02(self):
        """MacroEnvIncRefCount.test_02() refcount increments on defined().""" 
        myMap = MacroEnv.MacroEnv()
        myStr = u"""REFCOUNT 1
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self.assertTrue(myMap.hasMacro('REFCOUNT'))
        self.assertEqual(0, myMap.macro('REFCOUNT').refCount)
        # Checking existance increments refcount
        self._checkMacroEnv(myGen, myMap, ['REFCOUNT', ])
        self.assertEqual(1, myMap.macro('REFCOUNT').refCount)
        myMap.defined(PpToken.PpToken('REFCOUNT', 'identifier'), False)
        self.assertEqual(2, myMap.macro('REFCOUNT').refCount)
        myMap.defined(PpToken.PpToken('REFCOUNT', 'identifier'), True)
        self.assertEqual(3, myMap.macro('REFCOUNT').refCount)

    def test_03(self):
        """MacroEnvIncRefCount.test_03() refcount increments on isDefined().""" 
        myMap = MacroEnv.MacroEnv()
        myStr = u"""REFCOUNT 1
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self.assertTrue(myMap.hasMacro('REFCOUNT'))
        self.assertEqual(0, myMap.macro('REFCOUNT').refCount)
        # Checking existance increments refcount
        self._checkMacroEnv(myGen, myMap, ['REFCOUNT', ])
        self.assertEqual(1, myMap.macro('REFCOUNT').refCount)
        myMap.isDefined(PpToken.PpToken('REFCOUNT', 'identifier'))
        self.assertEqual(2, myMap.macro('REFCOUNT').refCount)

    def test_04(self):
        """MacroEnvIncRefCount.test_04() refcount does not increment on undef.""" 
        myMap = MacroEnv.MacroEnv()
        myStr = u"""REFCOUNT 1
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self.assertTrue(myMap.hasMacro('REFCOUNT'))
        self.assertEqual(0, myMap.macro('REFCOUNT').refCount)
        # Checking existance increments refcount
        self._checkMacroEnv(myGen, myMap, ['REFCOUNT', ])
        self.assertEqual(1, myMap.macro('REFCOUNT').refCount)
        myMap.isDefined(PpToken.PpToken('REFCOUNT', 'identifier'))
        self.assertEqual(2, myMap.macro('REFCOUNT').refCount)
        # Now undef it
        myMap.undef(
            PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(u'REFCOUNT\n')
            ).next(),
            '',
            1,
        )
        self._checkMacroEnv(myGen, myMap, [])
        for aMacro in myMap.genMacros('REFCOUNT'):
            self.assertEqual(2, aMacro.refCount)

    def test_05(self):
        """MacroEnvIncRefCount.test_05() refcount increments on simple replacement.""" 
        myMap = MacroEnv.MacroEnv()
        myStr = u"""REFCOUNT 1
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self.assertTrue(myMap.hasMacro('REFCOUNT'))
        self.assertEqual(0, myMap.macro('REFCOUNT').refCount)
        # Checking existance increments refcount
        self._checkMacroEnv(myGen, myMap, ['REFCOUNT', ])
        self.assertEqual(1, myMap.macro('REFCOUNT').refCount)
        self.assertEqual(
            self.stringToTokens(u'1'),
            myMap.replace(
                PpToken.PpToken('REFCOUNT', 'identifier'), None)
            )
        self.assertEqual(2, myMap.macro('REFCOUNT').refCount)

    def test_06(self):
        """MacroEnvIncRefCount.test_05() refcount increments on replacement with re-examination.""" 
        myEnv = MacroEnv.MacroEnv()
        myStr = u"""glue(a, b) a ## b
xglue(a, b) glue(a, b)
HIGHLOW "hello"
LOW LOW ", world"
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 4:
            myEnv.define(myGen, '', 1)
            i += 1
        myMacroNameS = ['glue', 'xglue', 'HIGHLOW', 'LOW']
        # Check before _checkMacroEnv()
        for aMacroName in myMacroNameS:
            self.assertEqual(0, myEnv.macro(aMacroName).refCount)
        #print
        #print str(myEnv)
        self.assertEqual("""#define HIGHLOW "hello" /* #1 Ref: 0 True */
#define LOW LOW ", world" /* #1 Ref: 0 True */
#define glue(a,b) a ## b /* #1 Ref: 0 True */
#define xglue(a,b) glue(a, b) /* #1 Ref: 0 True */""", str(myEnv))
        self._checkMacroEnv(myGen, myEnv, myMacroNameS)
        # Check after _checkMacroEnv()
        for aMacroName in myMacroNameS:
            self.assertEqual(1, myEnv.macro(aMacroName).refCount)
        #print
        #print str(myEnv)
        self.assertEqual("""#define HIGHLOW "hello" /* #1 Ref: 1 True */
#define LOW LOW ", world" /* #1 Ref: 1 True */
#define glue(a,b) a ## b /* #1 Ref: 1 True */
#define xglue(a,b) glue(a, b) /* #1 Ref: 1 True */""", str(myEnv))
        # Now replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""glue(HIGH, LOW);
xglue(HIGH, LOW)
""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myEnv.replace(ttt, myGen)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #print
        #self.pprintTokensAsCtors(repList)
        expectedTokens = [
            #
            PpToken.PpToken('"hello"',      'string-literal'),
            PpToken.PpToken(';',            'preprocessing-op-or-punc'),
            PpToken.PpToken('\n',           'whitespace'),
            #
            PpToken.PpToken('"hello"',      'string-literal'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('", world"',    'string-literal'),
            PpToken.PpToken('\n',           'whitespace'),
        ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        #print
        #print str(myEnv)
        # Note was:
        #define HIGHLOW "hello" /* #1 Ref: 1 True */
        #define LOW LOW ", world" /* #1 Ref: 1 True */
        #define glue(a,b) a ## b /* #1 Ref: 1 True */
        #define xglue(a,b) glue(a, b) /* #1 Ref: 1 True */
        self.assertEqual("""#define HIGHLOW "hello" /* #1 Ref: 3 True */
#define LOW LOW ", world" /* #1 Ref: 2 True */
#define glue(a,b) a ## b /* #1 Ref: 3 True */
#define xglue(a,b) glue(a, b) /* #1 Ref: 2 True */""", str(myEnv))
        self.assertEqual(3, myEnv.macro('HIGHLOW').refCount)
        self.assertEqual(2, myEnv.macro('LOW').refCount)
        self.assertEqual(3, myEnv.macro('glue').refCount)
        self.assertEqual(2, myEnv.macro('xglue').refCount)

class MacroEnvAccess(TestMacroEnv):
    """Tests that the macro can be accessed."""
    def test_00(self):
        """MacroEnvAccess.test_00() accessing the macro environment after processing.""" 
        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM -1
EGGS -2+SPAM
CHIPS 3+EGGS
BEANS 4+CHIPS
PEAS Not on the menu
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 5:
            myEnv.define(myGen, '', i+1)
            i += 1
        # Do some undef'ing
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""SPAM
EGGS
PEAS
""")
            )
        myGen = myCpp.next()
        i = 0
        while i < 3:
            myEnv.undef(myGen, '', i+10)
            i += 1
        # Do some defining
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""SPAM 1
EGGS 2+SPAM
""")
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myEnv.define(myGen, '', i+100)
            i += 1
        # Now test
        myMacroNameS = ['SPAM', 'EGGS', 'CHIPS', 'BEANS']
        # Check before _checkMacroEnv()
        for aMacroName in myMacroNameS:
            self.assertEqual(0, myEnv.macro(aMacroName).refCount)
        #print
        #print str(myEnv)
        self.assertEqual("""#define BEANS 4+CHIPS /* #4 Ref: 0 True */
#define CHIPS 3+EGGS /* #3 Ref: 0 True */
#define EGGS 2+SPAM /* #101 Ref: 0 True */
#define SPAM 1 /* #100 Ref: 0 True */""", str(myEnv))
        self._checkMacroEnv(myGen, myEnv, myMacroNameS)
        # Check after _checkMacroEnv()
        for aMacroName in myMacroNameS:
            self.assertEqual(1, myEnv.macro(aMacroName).refCount)
        self.assertEqual("""#define BEANS 4+CHIPS /* #4 Ref: 1 True */
#define CHIPS 3+EGGS /* #3 Ref: 1 True */
#define EGGS 2+SPAM /* #101 Ref: 1 True */
#define SPAM 1 /* #100 Ref: 1 True */""", str(myEnv))
        # Now replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""SPAM
EGGS
CHIPS
BEANS
""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myEnv.replace(ttt, myGen)
            repList += myReplacements
        expectedTokens = self.stringToTokens(u"""1
2+1
3+2+1
4+3+2+1
""")
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        #print
        #print str(myEnv)
        self.assertEqual("""#define BEANS 4+CHIPS /* #4 Ref: 2 True */
#define CHIPS 3+EGGS /* #3 Ref: 3 True */
#define EGGS 2+SPAM /* #101 Ref: 4 True */
#define SPAM 1 /* #100 Ref: 5 True */""", str(myEnv))
        self.assertEqual(5, myEnv.macro('SPAM').refCount)
        self.assertEqual(4, myEnv.macro('EGGS').refCount)
        self.assertEqual(3, myEnv.macro('CHIPS').refCount)
        self.assertEqual(2, myEnv.macro('BEANS').refCount)
        for mId in myEnv.macros():
            self.assertTrue(myEnv.hasMacro(mId))
            try:
                myEnv.macro(mId)
            except MacroEnv.ExceptionMacroEnvNoMacroDefined:
                self.fail('MacroEnv.macro() raises when macro %s is there' % mId)
        self.assertRaises(MacroEnv.ExceptionMacroEnvNoMacroDefined, myEnv.macro, 'WRONG')
        # Now access macro history
        myMacroHistory = '\n'.join([str(m) for m in myEnv.genMacros()])
        #print
        #print myMacroHistory
        self.assertEqual("""#define SPAM -1 /* #1 Ref: 0 False #10 */
#define EGGS -2+SPAM /* #2 Ref: 0 False #11 */
#define PEAS Not on the menu /* #5 Ref: 0 False #12 */
#define BEANS 4+CHIPS /* #4 Ref: 2 True */
#define CHIPS 3+EGGS /* #3 Ref: 3 True */
#define EGGS 2+SPAM /* #101 Ref: 4 True */
#define SPAM 1 /* #100 Ref: 5 True */""", myMacroHistory)
        #print
        #print myEnv.referencedMacroIdentifiers(sortedByRefcount=False)
        # NOTE: no guarentee of sort order when sortedByRefcount=False
        self.assertEqual(
                set(['BEANS', 'EGGS', 'CHIPS', 'SPAM']),
                set(myEnv.referencedMacroIdentifiers(sortedByRefcount=False))
                         )
        #print
        #print myEnv.referencedMacroIdentifiers(sortedByRefcount=True)
        self.assertEqual(
                ['BEANS', 'CHIPS', 'EGGS', 'SPAM'],
                myEnv.referencedMacroIdentifiers(sortedByRefcount=True)
                         )
        

class MacroEnvPreserveStateOnRedefinition(TestMacroEnv):
    """Test state (refcount etc.) is preserved on redefinition."""
    def test_00(self):
        """MacroEnvPreserveStateOnRedefinition.test_00(): Test state (refcount etc.) is preserved on redefinition.""" 
        myMap = MacroEnv.MacroEnv()
        myStr = u"""DEF 1 + 2
 """
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, 'a.h', 11)
        self.assertTrue(myMap.hasMacro('DEF'))
        self.assertEqual(0, myMap.macro('DEF').refCount)
        # Checking existance increments refcount
        self._checkMacroEnv(myGen, myMap, ['DEF', ])
        # Test macro state
        self.assertEqual('a.h', myMap.macro('DEF').fileId)
        self.assertEqual(11, myMap.macro('DEF').line)
        self.assertEqual(1, myMap.macro('DEF').refCount)
        # Now try a bad redefinition
        myStr = u'DEF 1+2\n'
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        self.assertRaises(
            MacroEnv.ExceptionMacroEnvInvalidRedefinition,
            myMap.define,
            myGen,
            'b.h',
            17,
            )
        # Now try a good redefinition from different file and line
        myStr = u'DEF   1   /*   Some  comment   */    +     2    \n'
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, 'c.h', 112)
        self.assertTrue(myMap.hasMacro('DEF'))
        # Test state, it should be the same as the original definition
        self.assertEqual('a.h', myMap.macro('DEF').fileId)
        self.assertEqual(11, myMap.macro('DEF').line)
        self.assertEqual(1, myMap.macro('DEF').refCount)
        # Test that the state is not the same as the redefined macro
        self.assertNotEqual('c.h', myMap.macro('DEF').fileId)
        self.assertNotEqual(112, myMap.macro('DEF').line)
        self.assertNotEqual(0, myMap.macro('DEF').refCount)
        
class SpecialParsingOverRun(TestMacroEnv):
    """Special tests."""

    def test_00(self):
        """Special.test_00() - #if INC == 1 parsing without overrun."""
        """NOTE: The rationale for this was a problem with the list generator
        which yielded the following tokens:
        Special.test_00() - #if INC == 1 parsing. ...
          Token: "INC", identifier, True, False, False
        Replace: ["1", " "]
          Token: "==", preprocessing-op-or-punc, False, False, False
        Replace: ["=="]
          Token: " ", whitespace, False, False, False
        Replace: [" "]
          Token: "1", pp-number, False, False, False
        Replace: ["1"]
          Token: "
        ", whitespace, False, False, False
        Replace: ["
        "]
        result: [["1", " "], ["=="], [" "], ["1"], ["\n"]]
        Note that the last line should be:
        result: [["1",], [" "], ["=="], [" "], ["1"], ["\n"]]
        The problem was the test to stop re-examination was off by one.
        This test makes sure that the fix works. See the ListGen for more
        information.
        """
        myMap = MacroEnv.MacroEnv()#enableTrace=True)
        myStr = u"""INC 1
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['INC',])
        myTuPp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'INC == 1\n')
            )
        myGen = myTuPp.next()
        result = []
        #print
        for aTt in myGen:
            #print '  Token:', aTt
            myRep = myMap.replace(aTt, myGen)
            #print 'Replace:', myRep
            result.append(myRep)
        #print 'result:', result
        self.assertEqual(
                result,
                [
                    [
                     PpToken.PpToken('1',   'pp-number'),
                     ],
                    [
                     PpToken.PpToken(' ',   'whitespace'),
                     ],
                    [
                     PpToken.PpToken('==',  'preprocessing-op-or-punc')
                     ],
                    [
                     PpToken.PpToken(' ',   'whitespace')
                     ],
                    [
                     PpToken.PpToken('1',   'pp-number')
                     ],
                    [
                     PpToken.PpToken('\n',   'whitespace')
                     ],
                ]
        )


class MacroEnvCppInternals(TestMacroEnv):
    """Test from cpp.pdf.
    TODO: Identify source of this doc."""
    def test_3_9_00(self):
        """MacroEnvCppInternals.test_3_9_00(): 3.9 [0]. TODO: Raise an exception.""" 
        myEnv = MacroEnv.MacroEnv()
        myStr = u"""f(x) x x
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'a.h', 1)
        self._checkMacroEnv(myGen, myEnv, ['f',])
        # Now replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""f (1
#undef f
#define f 2
f)
""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myEnv.replace(ttt, myGen)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #print
        #self.pprintTokensAsCtors(repList)
        # Some versions of cpp expand this to '1 2 1 2'
        expectedTokens = [
            PpToken.PpToken('1', 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('#', 'preprocessing-op-or-punc'),
            PpToken.PpToken('undef', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('#', 'preprocessing-op-or-punc'),
            PpToken.PpToken('define', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('2', 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('1', 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('#', 'preprocessing-op-or-punc'),
            PpToken.PpToken('undef', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('#', 'preprocessing-op-or-punc'),
            PpToken.PpToken('define', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('2', 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('f', 'identifier'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        
    
    """3.9 Directives Within Macro Arguments
    Occasionally it is convenient to use preprocessor directives within the arguments of a macro.
    The C and C++ standards declare that behavior in these cases is undefined.
    Versions of CPP prior to 3.2 would reject such constructs with an error message. This
    was the only syntactic difference between normal functions and function-like macros, so
    it seemed attractive to remove this limitation, and people would often be surprised that
    they could not use macros in this way. Moreover, sometimes people would use conditional
    compilation in the argument list to a normal library function like 'printf', only to find
    that after a library upgrade 'printf' had changed to be a function-like macro, and their
    code would no longer compile. So from version 3.2 we changed CPP to successfully process
    arbitrary directives within macro arguments in exactly the same way as it would have
    processed the directive were the function-like macro invocation not present.
    If, within a macro invocation, that macro is redefined, then the new definition takes effect
    in time for argument pre-expansion, but the original definition is still used for argument
    replacement. Here is a pathological example:
    #define f(x) x x
    f (1
    #undef f
    #define f 2
    f)
    which expands to
    1 2 1 2
    with the semantics described above.    
    """
    
    
    def test_3_10_1_00(self):
        """MacroEnvCppInternals.test_00(): 3.10.1 [0].""" 
        # #define twice(x) (2*(x))
        # #define call_with_1(x) x(1)
        # call_with_1 (twice)
        # -> twice(1)
        # -> (2*(1))
        myEnv = MacroEnv.MacroEnv()
        myStr = u"""twice(x) (2*(x))
call_with_1(x) x(1)
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'a.h', 1)
        myEnv.define(myGen, 'a.h', 2)
        self._checkMacroEnv(myGen, myEnv, ['twice', 'call_with_1',])
        # Now replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""call_with_1 (twice)
""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myEnv.replace(ttt, myGen)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #print
        #self.pprintTokensAsCtors(repList)
        expectedTokens = [
            PpToken.PpToken('(',            'preprocessing-op-or-punc'),
            PpToken.PpToken('2',            'pp-number'),
            PpToken.PpToken('*',            'preprocessing-op-or-punc'),
            PpToken.PpToken('(',            'preprocessing-op-or-punc'),
            PpToken.PpToken('1',            'pp-number'),
            PpToken.PpToken(')',            'preprocessing-op-or-punc'),
            PpToken.PpToken(')',            'preprocessing-op-or-punc'),
            PpToken.PpToken('\n',           'whitespace'),
        ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)
        
    def test_3_10_1_01(self):
        """MacroEnvCppInternals.test_01(): 3.10.1 [1].""" 
        # Macro definitions do not have to have balanced parentheses.
        # By writing an unbalanced open parenthesis in a macro body,
        # it is possible to create a macro call that begins inside
        # the macro body but ends outside of it. For example,
        # #define strange(file) fprintf (file, "%s %d",
        # ...
        # strange(stderr) p, 35)
        # -> fprintf (stderr, "%s %d", p, 35)
        myEnv = MacroEnv.MacroEnv()
        myStr = u"""strange(file) fprintf (file, "%s %d",
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'a.h', 1)
        self._checkMacroEnv(myGen, myEnv, ['strange',])
        # Now replacement
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u"""strange(stderr) p, 35)
""")
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myEnv.replace(ttt, myGen)
            repList += myReplacements
        #self.pprintReplacementList(repList)
        #print
        #self.pprintTokensAsCtors(repList)
        # fprintf (stderr, "%s %d", p, 35)
        expectedTokens = [
            PpToken.PpToken('fprintf',      'identifier'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('(',            'preprocessing-op-or-punc'),
            PpToken.PpToken('stderr',       'identifier'),
            PpToken.PpToken(',',            'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('"%s %d"',      'string-literal'),
            PpToken.PpToken(',',            'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('p',            'identifier'),
            PpToken.PpToken(',',            'preprocessing-op-or-punc'),
            PpToken.PpToken(' ',            'whitespace'),
            PpToken.PpToken('35',           'pp-number'),
            PpToken.PpToken(')',            'preprocessing-op-or-punc'),
            PpToken.PpToken('\n',           'whitespace'),                          
        ]
        self._printDiff(repList, expectedTokens)
        self.assertEqual(expectedTokens, repList)

class VariableArgumentMacros(TestMacroEnv):
    """Test of adding a variable argument function like macro to the environment."""
    def test_00(self):
        """VariableArgumentMacros.test_00(): - Function like macro with variable arguments."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""showlist(...) puts(#__VA_ARGS__)
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, '', 1)
        self._checkMacroEnv(myGen, myMap, ['showlist',])
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'showlist(The first, second, and third items.);')
            )
        repList = []
        myGen = myCpp.next()
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
        #print
        #print 'TRACE: repList:\n', '\n'.join([str(x) for x in repList])
        #print 'TRACE:', self.tokensToString(repList)
        self.assertEqual(
            self.stringToTokens(u'puts("The first,second,and third items.");'),
            repList,
            )

class MacroHistory(TestMacroEnv):
    """Test of macro history."""
    def test_00(self):
        """MacroHistory.test_00(): - Basic macro history."""

        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'f.h', 1)
        myEnv.define(myGen, 'f.h', 2)
        #print
        #print myEnv.macroHistory()
        self.assertEqual(
            myEnv.macroHistory(),
            """Macro Environment:
#define EGGS 2 /* f.h#2 Ref: 0 True */
#define SPAM 1 /* f.h#1 Ref: 0 True */

Macro History (referenced macros only):
In scope:""")
        #print
        #print myEnv.macroHistoryMap()
        self.assertEqual(
            myEnv.macroHistoryMap(),
            {
                'EGGS': ([], True),
                'SPAM': ([], True),
            }
        )

    def test_01(self):
        """MacroHistory.test_01(): - define, undef and define again."""

        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
SPAM
SPAM 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'f.h', 1)
        myEnv.undef(myGen, 'f.h', 2)
        myEnv.define(myGen, 'f.h', 3)
        #print
        #print myEnv.macroHistory(onlyRef=False)
        self.assertEqual(
            myEnv.macroHistory(onlyRef=False),
            """Macro Environment:
#define SPAM 2 /* f.h#3 Ref: 0 True */

Macro History (all macros):
Out-of-scope:
#define SPAM 1 /* f.h#1 Ref: 0 False f.h#2 */
In scope:
#define SPAM 2 /* f.h#3 Ref: 0 True */""")
        #print
        #print myEnv.macroHistoryMap()
        self.assertEqual(
            myEnv.macroHistoryMap(),
            {
                'SPAM': ([0, ], True),
            }
        )

    def test_02(self):
        """MacroHistory.test_02(): - Multiple definition and undefinition."""

        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
SPAM
SPAM 2
SPAM
SPAM 3
SPAM
SPAM 4
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'f.h', 1)
        myEnv.undef(myGen, 'f.h', 2)
        myEnv.define(myGen, 'f.h', 3)
        myEnv.undef(myGen, 'f.h', 4)
        myEnv.define(myGen, 'f.h', 5)
        myEnv.undef(myGen, 'f.h', 6)
        myEnv.define(myGen, 'f.h', 7)
        #print
        #print myEnv.macroHistory(onlyRef=False)
        self.assertEqual(
            myEnv.macroHistory(onlyRef=False),
            """Macro Environment:
#define SPAM 4 /* f.h#7 Ref: 0 True */

Macro History (all macros):
Out-of-scope:
#define SPAM 1 /* f.h#1 Ref: 0 False f.h#2 */
#define SPAM 2 /* f.h#3 Ref: 0 False f.h#4 */
#define SPAM 3 /* f.h#5 Ref: 0 False f.h#6 */
In scope:
#define SPAM 4 /* f.h#7 Ref: 0 True */""")
        #print
        #print myEnv.macroHistoryMap()
        self.assertEqual(
            myEnv.macroHistoryMap(),
            {
                'SPAM': ([0, 1, 2, ], True),
            }
        )

    def test_03(self):
        """MacroHistory.test_01(): - define, undef and get the undef macro."""

        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
SPAM
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'f.h', 1)
        myEnv.undef(myGen, 'f.h', 2)
        #print
        #print myEnv.macroHistory(onlyRef=False)
        self.assertEqual(
            myEnv.macroHistory(onlyRef=False),
            """Macro Environment:


Macro History (all macros):
Out-of-scope:
#define SPAM 1 /* f.h#1 Ref: 0 False f.h#2 */""")
        #print
        #print myEnv.macroHistoryMap()
        self.assertEqual(
            myEnv.macroHistoryMap(),
            {
                'SPAM': ([0, ], False),
            }
        )
        myMacro = myEnv.getUndefMacro(0)
        self.assertEqual(
            '#define SPAM 1 /* f.h#1 Ref: 0 False f.h#2 */',
            str(myMacro)
        )
        try:
            myMacro = myEnv.getUndefMacro(1)
            self.fail('MacroEnv.ExceptionMacroIndexError not raised')
        except MacroEnv.ExceptionMacroIndexError:
            pass
        try:
            myMacro = myEnv.getUndefMacro(-2)
            self.fail('MacroEnv.ExceptionMacroIndexError not raised')
        except MacroEnv.ExceptionMacroIndexError:
            pass

    def test_04(self):
        """MacroHistory.test_04(): - define, undef and define again with references."""

        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
SPAM
SPAM 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'f.h', 1)
        self.assertEqual(
                True,
                myEnv.isDefined(
                    PpToken.PpToken('SPAM', 'identifier'),
                    theFileLineCol=FileLocation.FileLineCol(
                            'spam.h',
                            12,
                            17),
                )
            )
        myEnv.undef(myGen, 'f.h', 2)
        self.assertEqual(
                False,
                myEnv.isDefined(
                    PpToken.PpToken('SPAM', 'identifier'),
                    theFileLineCol=None,
                )
            )
        myEnv.define(myGen, 'f.h', 3)
        self.assertEqual(
                True,
                myEnv.isDefined(
                    PpToken.PpToken('SPAM', 'identifier'),
                    theFileLineCol=FileLocation.FileLineCol(
                            'spam.h',
                            21,
                            71),
                )
            )
        #print
        #print myEnv.macroHistory(onlyRef=False)
        self.assertEqual(
            myEnv.macroHistory(onlyRef=False),
            """Macro Environment:
#define SPAM 2 /* f.h#3 Ref: 1 True */

Macro History (all macros):
Out-of-scope:
#define SPAM 1 /* f.h#1 Ref: 1 False f.h#2 */
    spam.h 12 17
In scope:
#define SPAM 2 /* f.h#3 Ref: 1 True */
    spam.h 21 71""")
        #print
        #print myEnv.macroHistoryMap()
        self.assertEqual(
            myEnv.macroHistoryMap(),
            {
                'SPAM': ([0, ], True),
            }
        )

    def test_05(self):
        """MacroHistory.test_05(): - references to ifdef'd macros that are not defined."""

        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'f.h', 1)
        self.assertEqual(
                True,
                myEnv.isDefined(
                    PpToken.PpToken('SPAM', 'identifier'),
                    theFileLineCol=FileLocation.FileLineCol(
                            'spam.h',
                            12,
                            17),
                )
            )
        self._checkMacroEnv(myGen, myEnv, ['SPAM', ], testNOTHING=False)
        #print
        #print myEnv.macroHistory(onlyRef=False)
        self.assertEqual(
            myEnv.macroHistory(onlyRef=False),
            """Macro Environment:
#define SPAM 1 /* f.h#1 Ref: 2 True */

Macro History (all macros):
In scope:
#define SPAM 1 /* f.h#1 Ref: 2 True */
    spam.h 12 17""")
        #print
        #print myEnv.macroHistoryMap()
        self.assertEqual(
            myEnv.macroHistoryMap(),
            {
                'SPAM': ([], True),
            }
        )
        # Now do some isDefined() and defined()
        # Check using isDefined()
        self.assertEqual(
            False,
            myEnv.isDefined(
                PpToken.PpToken('NOTDEF', 'identifier'),
                theFileLineCol=FileLocation.FileLineCol('notdef.h', 12, 17)
            )
        )
        # Check using defined()
        self.assertEqual(
            PpToken.PpToken('1', 'pp-number'),
            myEnv.defined(
                PpToken.PpToken('NOTDEF', 'identifier'),
                flagInvert=True,
                theFileLineCol=FileLocation.FileLineCol('notdef.h', 120, 19)   
            )
        )
        #print
        #print myEnv.macroNotDefinedDependencies()
        self.assertEqual(
            myEnv.macroNotDefinedDependencies(),
            {
                'NOTDEF': [
                               FileLocation.FileLineCol('notdef.h', 12, 17),
                               FileLocation.FileLineCol('notdef.h', 120, 19),
                           ],
            }
        )
        self.assertEqual(myEnv.macroNotDefinedDependencyNames(), ['NOTDEF',])
        self.assertEqual(
            myEnv.macroNotDefinedDependencyReferences('NOTDEF'),
            [
               FileLocation.FileLineCol('notdef.h', 12, 17),
               FileLocation.FileLineCol('notdef.h', 120, 19),
             ]
        )
        self.assertRaises(
                MacroEnv.ExceptionMacroEnvNoMacroDefined,
                myEnv.macroNotDefinedDependencyReferences,
                'WRONG'
            )

class TestLinux(TestMacroEnv):
    """Tests that resulted in processing Linux."""
    def test_00(self):
        """TestLinux.test_00() - From include/linux/stringify.h."""
        """#define __stringify_1(x...)    #x
#define __stringify(x...)    __stringify_1(x)
"""
        myMap = MacroEnv.MacroEnv(enableTrace=True)
        myStr = u"""__stringify_1(x...)    #x
__stringify(x...)    __stringify_1(x)
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myMap.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(
            myGen,
            myMap,
            ['__stringify_1', '__stringify',]
            )
        myInOut = (
            # cpp:
            (u'__stringify(X)', '"X"'),
            (u'__stringify(X,Y)', '"X"'),
            )
        for myIn, myOut in myInOut:
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(myIn)
                )
            repList = []
            myGen = myCpp.next()
            myMap.debugMarker = 'TestLinux.test_00()'
            for ttt in myGen:
                myReplacements = myMap.replace(ttt, myGen)
                repList += myReplacements
            repString = self.tokensToString(repList)
            self.assertEqual(repString, myOut)

    def test_01(self):
        """Test where we get errors such as missing arguments.
        macro "__ASM_SEL" passed 3 arguments, but takes just 2 at line=203, col=25 of file "/Users/paulross/dev/linux/linux-3.13/arch/x86/include/asm/rwsem.h"
        macro "__ASM_SEL" requires 2 arguments, but only 1 given at line=213, col=23 of file "/Users/paulross/dev/linux/linux-3.13/arch/x86/include/asm/rwsem.h"
        """
        src = """#define __ASM_SEL(a,b) a,b
#define __ASM_SIZE(inst, ...)    __ASM_SEL(inst##l##__VA_ARGS__, inst##q##__VA_ARGS__)
/* rwsem.h */
f(__ASM_SIZE(add))
"""
        def_src = u"""__ASM_SEL(a,b) a,b
__ASM_SIZE(inst, ...)    __ASM_SEL(inst##l##__VA_ARGS__, inst##q##__VA_ARGS__)
"""
        myMacEnv = MacroEnv.MacroEnv(enableTrace=True)
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(def_src)
            )
        myGen = myCpp.next()
        i = 0
        while i < 2:
            myMacEnv.define(myGen, '', 1)
            i += 1
        self._checkMacroEnv(
            myGen,
            myMacEnv,
            ['__ASM_SEL', '__ASM_SIZE',]
            )
        srcIn = u"f(__ASM_SIZE(add))\n"
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(srcIn)
            )
        repList = []
        myGen = myCpp.next()
        myMacEnv.debugMarker = 'TestLinux.test_01()'
        for ttt in myGen:
            myReplacements = myMacEnv.replace(ttt, myGen)
            repList += myReplacements
        repString = self.tokensToString(repList)
        self.assertEqual(repString, 'f(addl,addq)\n')

    def test_02(self):
        """Test where we get errors such as missing arguments.
        macro "__ASM_SEL" passed 3 arguments, but takes just 2 at line=203, col=25 of file "/Users/paulross/dev/linux/linux-3.13/arch/x86/include/asm/rwsem.h"
        macro "__ASM_SEL" requires 2 arguments, but only 1 given at line=213, col=23 of file "/Users/paulross/dev/linux/linux-3.13/arch/x86/include/asm/rwsem.h"
        """
        src = """/* asm.h */
# define __ASM_FORM(x)    " " #x " "
/* ndef CONFIG_X86_32 */
# define __ASM_SEL(a,b) __ASM_FORM(b)
#define __ASM_SIZE(inst, ...)    __ASM_SEL(inst##l##__VA_ARGS__, \
                      inst##q##__VA_ARGS__)
#define _ASM_ADD    __ASM_SIZE(add)
/* rwsem.h */
f(_ASM_ADD)
"""
        def_src = u"""__ASM_FORM(x)    " " #x " "
__ASM_SEL(a,b) __ASM_FORM(b)
__ASM_SIZE(inst, ...)    __ASM_SEL(inst##l##__VA_ARGS__, inst##q##__VA_ARGS__)
_ASM_ADD    __ASM_SIZE(add)
"""
        myMacEnv = MacroEnv.MacroEnv(enableTrace=True)
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(def_src)
            )
        myGen = myCpp.next()
        i = 0
        while i < 4:
            myMacEnv.define(myGen, '', 1)
            i += 1
#         print('WTF')
#         print(myMacEnv)
        self._checkMacroEnv(
            myGen,
            myMacEnv,
            ['__ASM_FORM', '__ASM_SEL', '__ASM_SIZE', '_ASM_ADD',]
            )
        srcIn = u"f(_ASM_ADD)\n"
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(srcIn)
            )
        repList = []
        myGen = myCpp.next()
        myMacEnv.debugMarker = 'TestLinux.test_01()'
        for ttt in myGen:
            myReplacements = myMacEnv.replace(ttt, myGen)
            repList += myReplacements
        repString = self.tokensToString(repList)
#         print(repString)
        self.assertEqual(repString, 'f(" " "addq" " ")\n')

class MacroDependencies(TestMacroEnv):
    """Test of macro dependencies."""
    def test_00(self):
        """MacroDependencies.test_00(): - No macro dependencies."""
        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'f.h', 1)
        myEnv.define(myGen, 'f.h', 2)
#         print()
#         print(myEnv._staticMacroDependencies('EGGS').branches())
        self.assertEquals([], myEnv._staticMacroDependencies('SPAM'))
        self.assertEquals([], myEnv._staticMacroDependencies('EGGS'))

    def test_01(self):
        """MacroDependencies.test_01(): - Simple macro dependency."""
        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM EGGS
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'f.h', 1)
        myEnv.define(myGen, 'f.h', 2)
        self.assertEquals(['EGGS',], myEnv._staticMacroDependencies('SPAM'))
        self.assertEquals([], myEnv._staticMacroDependencies('EGGS'))
        myAdjList = myEnv.allStaticMacroDependencies()
        self.assertEquals(['EGGS',], myAdjList.children('SPAM'))
        self.assertRaises(KeyError, myAdjList.children, 'EGGS')
        self.assertEquals(['SPAM',], myAdjList.parents('EGGS'))
        self.assertRaises(KeyError, myAdjList.parents, 'SPAM')
        
    def test_02(self):
        """MacroDependencies.test_02(): - Macro dependency on self."""
        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM SPAM\n"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'f.h', 1)
        self.assertEquals(['SPAM',], myEnv._staticMacroDependencies('SPAM'))
        myAdjList = myEnv.allStaticMacroDependencies()
        self.assertEquals(['SPAM',], myAdjList.children('SPAM'))
        self.assertEquals(['SPAM',], myAdjList.parents('SPAM'))

    def test_03(self):
        """MacroDependencies.test_03(): - Macro cyclic dependency."""
        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM EGGS
EGGS SPAM
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'f.h', 1)
        myEnv.define(myGen, 'f.h', 2)
#         print()
#         print(myEnv._staticMacroDependencies('EGGS').branches())
#         print(myEnv.allStaticMacroDependencies())
#         for k, v in myEnv.allStaticMacroDependencies().items():
#             print(k, ':', v)
        self.assertEquals(['EGGS',], myEnv._staticMacroDependencies('SPAM'))
        self.assertEquals(['SPAM',], myEnv._staticMacroDependencies('EGGS'))
        myAdjList = myEnv.allStaticMacroDependencies()
        self.assertEquals(['EGGS',], myAdjList.children('SPAM'))
        self.assertEquals(['SPAM',], myAdjList.children('EGGS'))
        self.assertEquals(['SPAM',], myAdjList.parents('EGGS'))
        self.assertEquals(['EGGS',], myAdjList.parents('SPAM'))

    def test_04(self):
        """MacroDependencies.test_04(): - Non-existent macro."""
        myEnv = MacroEnv.MacroEnv()
        myStr = u"""SPAM 1
EGGS 2
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myEnv.define(myGen, 'f.h', 1)
        myEnv.define(myGen, 'f.h', 2)
        try:
            myEnv._staticMacroDependencies('CHIPS').branches()
            self.fail('MacroEnv.ExceptionMacroEnvNoMacroDefined not raised')
        except MacroEnv.ExceptionMacroEnvNoMacroDefined:
            pass


class TestLibCello(TestMacroEnv):
    """Tests that resulted in processing libCello."""
    def test_00(self):
        """MacroEnvDefined.test_00 - check defined()."""
        myMap = MacroEnv.MacroEnv()
        myStr = u"""X (    (  (defined (SPAM))))
"""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myGen = myCpp.next()
        myMap.define(myGen, 'libCello.h', 1)
        self._checkMacroEnv(myGen, myMap, ['X',])
        self.assertEqual("""#define X ( ( (defined (SPAM)))) /* libCello.h#1 Ref: 1 True */""", str(myMap))
        myCodeResult = (
            (PpToken.PpToken('X', 'identifier'), False, PpToken.PpToken('1', 'pp-number')),
            )
        for aTok, aFlag, aResult in myCodeResult:
            self.assertEqual(
                myMap.defined(aTok, aFlag),
                aResult
                )
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO('X')
            )
        repList = []
        myGen = myCpp.next()
        myMap.debugMarker = 'TestLibCello.test_00()'
        for ttt in myGen:
            myReplacements = myMap.replace(ttt, myGen)
            repList += myReplacements
#         self.pprintTokensAsCtors(repList)
        repString = self.tokensToString(repList)
        self.assertEqual(repString, '(    (  (defined (SPAM))))')
    
class NullClass(TestMacroEnv):
    pass

def unitTest(theVerbosity=2):
    # - OK
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvInit))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvDefined))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvSimpleReplaceObject))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvReplaceObject))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvSimpleReplaceFunction))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvReplaceFunctionLowLevel))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvCycles))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvReplaceMixed))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExample3))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpDefineReplace_Special_00))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(SpecialClass))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExample4))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExample5))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(RecursiveFunctionLike))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMacroReplacementFuncRecursive))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMacroReplacementFuncRecursive_01))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvFuncReexamine))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMacroRedefinition))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMacroUndef))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFromCppInternals))
    ## - OK - needs work?
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFromCppInternalsTokenspacing))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFromStandardMisc))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStringise))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPredefinedRedefinition))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPredefined__FILE__))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPredefined__LINE__))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvIncRefCount))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvAccess))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvPreserveStateOnRedefinition))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroEnvCppInternals))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(SpecialParsingOverRun))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(VariableArgumentMacros))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroHistory))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLinux))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MacroDependencies))
    # - OK
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLibCello))
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
