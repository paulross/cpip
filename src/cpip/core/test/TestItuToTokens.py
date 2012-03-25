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
#import os
import unittest
import time
import logging
import pprint

try:
    import io as StringIO
except ImportError:
    import io

#try:
#    from xml.etree import cElementTree as etree
#except ImportError:
#    from xml.etree import ElementTree as etree

#sys.path.append(os.path.join(os.pardir + os.sep))
#===============================================================================
# import pprint
# pprint.pprint(sys.path)
#===============================================================================
from cpip.core import ItuToTokens

#######################################
# Section: Unit tests
########################################
class TestBase(unittest.TestCase):
    """Test the simple stuff."""
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_00(self):
        """TestBase.test_00(): setUp() and tearDown()."""
        pass

class TestItuToHtmlLowLevel(unittest.TestCase):
    """Test the ItuToHtml low level functionality."""
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_00(self):
        """TestItuToHtmlLowLevel.test_00(): setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestItuToHtmlLowLevel.test_01(): Empty string, no processing."""
        myIth = ItuToTokens.ItuToTokens(io.StringIO(''))
        myMps = myIth.multiPassString
        o = [c for c in myMps.genChars()]
        #print o
        self.assertEqual([], o)
        n = [c for c in myMps.genWords()]
        self.assertEqual([], n)
        self.assertEqual([], myMps.currentString)
        self.assertEqual(0, myMps.idxChar)
        self.assertEqual({}, myMps.idxTypeMap)
    
    def test_02(self):
        """TestItuToHtmlLowLevel.test_02(): _translatePhase_1() with empty string."""
        myIth = ItuToTokens.ItuToTokens(io.StringIO(''))
        myIth._translatePhase_1()
        myMps = myIth.multiPassString
        o = [c for c in myMps.genChars()]
        #print o
        self.assertEqual([], o)
        n = [c for c in myMps.genWords()]
        self.assertEqual([], n)
        self.assertEqual([], myMps.currentString)
        self.assertEqual(0, myMps.idxChar)
        self.assertEqual({}, myMps.idxTypeMap)
    
    def test_03(self):
        """TestItuToHtmlLowLevel.test_03(): _translatePhase_1() with trigraphs."""
        myTestData = [
            # Tuples of (input_string, [exp_tokens,], [exp_types,], [current_string])
            (
                '??=',
                ['#'],
                [
                    ('??=', 'trigraph'),
                ],
                ['#', '', ''],
            ),
            (
                '??=??(',
                ['#', '['],
                [
                    ('??=', 'trigraph'),
                    ('??(', 'trigraph'),
                ],
                ['#', '', '', '[', '', ''],
            ),
            (
                '??=??(??)',
                ['#', '[', ']'],
                [
                    ('??=', 'trigraph'),
                    ('??(', 'trigraph'),
                    ('??)', 'trigraph'),
                ],
                ['#', '', '', '[', '', '', ']', '', ''],
            ),
            (
                '??=??(??)??(??)',
                list('#[][]'),
                [
                    ('??=', 'trigraph'),
                    ('??(', 'trigraph'),
                    ('??)', 'trigraph'),
                    ('??(', 'trigraph'),
                    ('??)', 'trigraph'),
                ],
                ['#', '', '', '[', '', '', ']', '', '', '[', '', '', ']', '', '']
            ),
                      
        ]
        for s, eto, ety, cs in myTestData:
            #print 's:', s
            myIth = ItuToTokens.ItuToTokens(io.StringIO(s))
            myIth._translatePhase_1()
            myMps = myIth.multiPassString
            o = [c for c in myMps.genChars()]
            #print o
            self.assertEqual(eto, o)
            #print
            #print myMps.idxTypeMap
            n = [c for c in myMps.genWords()]
            #self.assertEqual({0: Word(wordLen=3, wordType='trigraph')}, myMps.idxTypeMap)
            self.assertEqual(len(s), myMps.idxChar)
            self.assertEqual(ety, n)
            self.assertEqual(cs, myMps.currentString)
    
class TestItuToHtmlPhase3(unittest.TestCase):
    """Test the ItuToHtml translation phase 3."""
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_00(self):
        """TestItuToHtmlPhase3.test_00(): setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestItuToHtmlPhase3.test_01(): Empty string."""
        myIth = ItuToTokens.ItuToTokens(io.StringIO(''))
        myIth.translatePhases123()
        myMps = myIth.multiPassString
        o = [c for c in myMps.genChars()]
        #print o
        self.assertEqual([], o)
        n = [c for c in myMps.genWords()]
        self.assertEqual([], n)
        self.assertEqual([], myMps.currentString)
        self.assertEqual(0, myMps.idxChar)
        self.assertEqual({}, myMps.idxTypeMap)
    
    def test_02(self):
        """TestItuToHtmlPhase3.test_02(): Macro."""
        myStr = '#define OBJ_LIKE /* white space */ (1-1) /* other */\n'
        myIth = ItuToTokens.ItuToTokens(io.StringIO(myStr))
        myIth.translatePhases123()
        myMps = myIth.multiPassString
        # Now test
        o = [c for c in myMps.genChars()]
        #print o
        #print ''.join(o)
        self.assertEqual(
            ['#', 'd', 'e', 'f', 'i', 'n', 'e', ' ', 'O', 'B', 'J', '_', 'L', 'I', 'K', 'E', ' ', ' ', ' ', '(', '1', '-', '1', ')', ' ', ' ', '\n'],
            o,
        )
        #self.assertEqual({}, myMps.idxTypeMap)        
        n = [c for c in myMps.genWords()]
        #pprint.pprint(n)
        self.assertEqual(
            n,
            [
                ('#',                   'preprocessing-op-or-punc'),
                 ('define',             'identifier'),
                 (' ',                  'whitespace'),
                 ('OBJ_LIKE',           'identifier'),
                 (' ',                  'whitespace'),
                 ('/* white space */',  'C comment'),
                 (' ',                  'whitespace'),
                 ('(',                  'preprocessing-op-or-punc'),
                 ('1',                  'pp-number'),
                 ('-',                  'preprocessing-op-or-punc'),
                 ('1',                  'pp-number'),
                 (')',                  'preprocessing-op-or-punc'),
                 (' ',                  'whitespace'),
                 ('/* other */',        'C comment'),
                 ('\n',                 'whitespace')
            ]
        )
        #self.assertEqual([], myMps.currentString)
        self.assertEqual(53, myMps.idxChar)
    
    def test_03(self):
        """TestItuToHtmlPhase3.test_03(): ISO/IEC 9899:1999 (E) 6.10.3.5-5 EXAMPLE 3"""
        myStr = """#define x 3
#define f(a) f(x * (a))
#undef x
#define x 2
#define g f
#define z z[0]
#define h g(~
#define m(a) a(w)
#define w 0,1
#define t(a) a
#define p() int
#define q(x) x
#define r(x,y) x ## y
#define str(x) # x
f(y+1) + f(f(z)) % t(t(g)(0) + t)(1);
g(x+(3,4)-w) | h 5) & m
(f)^m(m);
p() i[q()] = { q(1), r(2,3), r(4,), r(,5), r(,) };
char c[2][6] = { str(hello), str() };
"""
        myIth = ItuToTokens.ItuToTokens(io.StringIO(myStr))
        myIth.translatePhases123()
        myMps = myIth.multiPassString
        wordS = [w for w in myMps.genWords()]
        #print
        #pprint.pprint(wordS)
        self.assertEqual(
            wordS,
            [
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('x', 'identifier'),
                (' ', 'whitespace'),
                ('3', 'pp-number'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('f', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('a', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('f', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('x', 'identifier'),
                (' ', 'whitespace'),
                ('*', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('(', 'preprocessing-op-or-punc'),
                ('a', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (')', 'preprocessing-op-or-punc'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('undef', 'identifier'),
                (' ', 'whitespace'),
                ('x', 'identifier'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('x', 'identifier'),
                (' ', 'whitespace'),
                ('2', 'pp-number'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('g', 'identifier'),
                (' ', 'whitespace'),
                ('f', 'identifier'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('z', 'identifier'),
                (' ', 'whitespace'),
                ('z', 'identifier'),
                ('[', 'preprocessing-op-or-punc'),
                ('0', 'pp-number'),
                (']', 'preprocessing-op-or-punc'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('h', 'identifier'),
                (' ', 'whitespace'),
                ('g', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('~', 'preprocessing-op-or-punc'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('m', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('a', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('a', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('w', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('w', 'identifier'),
                (' ', 'whitespace'),
                ('0', 'pp-number'),
                (',', 'preprocessing-op-or-punc'),
                ('1', 'pp-number'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('t', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('a', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('a', 'identifier'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('p', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('int', 'identifier'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('q', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('x', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('x', 'identifier'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('r', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('x', 'identifier'),
                (',', 'preprocessing-op-or-punc'),
                ('y', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('x', 'identifier'),
                (' ', 'whitespace'),
                ('##', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('y', 'identifier'),
                ('\n', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                ('define', 'identifier'),
                (' ', 'whitespace'),
                ('str', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('x', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('#', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('x', 'identifier'),
                ('\n', 'whitespace'),
                ('f', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('y', 'identifier'),
                ('+', 'preprocessing-op-or-punc'),
                ('1', 'pp-number'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('+', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('f', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('f', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('z', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('%', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('t', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('t', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('g', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                ('(', 'preprocessing-op-or-punc'),
                ('0', 'pp-number'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('+', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('t', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                ('(', 'preprocessing-op-or-punc'),
                ('1', 'pp-number'),
                (')', 'preprocessing-op-or-punc'),
                (';', 'preprocessing-op-or-punc'),
                ('\n', 'whitespace'),
                ('g', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('x', 'identifier'),
                ('+', 'preprocessing-op-or-punc'),
                ('(', 'preprocessing-op-or-punc'),
                ('3', 'pp-number'),
                (',', 'preprocessing-op-or-punc'),
                ('4', 'pp-number'),
                (')', 'preprocessing-op-or-punc'),
                ('-', 'preprocessing-op-or-punc'),
                ('w', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('|', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('h', 'identifier'),
                (' ', 'whitespace'),
                ('5', 'pp-number'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('&', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('m', 'identifier'),
                ('\n', 'whitespace'),
                ('(', 'preprocessing-op-or-punc'),
                ('f', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                ('^', 'preprocessing-op-or-punc'),
                ('m', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('m', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (';', 'preprocessing-op-or-punc'),
                ('\n', 'whitespace'),
                ('p', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('i', 'identifier'),
                ('[', 'preprocessing-op-or-punc'),
                ('q', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                (')', 'preprocessing-op-or-punc'),
                (']', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('=', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('{', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('q', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('1', 'pp-number'),
                (')', 'preprocessing-op-or-punc'),
                (',', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('r', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('2', 'pp-number'),
                (',', 'preprocessing-op-or-punc'),
                ('3', 'pp-number'),
                (')', 'preprocessing-op-or-punc'),
                (',', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('r', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('4', 'pp-number'),
                (',', 'preprocessing-op-or-punc'),
                (')', 'preprocessing-op-or-punc'),
                (',', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('r', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                (',', 'preprocessing-op-or-punc'),
                ('5', 'pp-number'),
                (')', 'preprocessing-op-or-punc'),
                (',', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('r', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                (',', 'preprocessing-op-or-punc'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('}', 'preprocessing-op-or-punc'),
                (';', 'preprocessing-op-or-punc'),
                ('\n', 'whitespace'),
                ('char', 'identifier'),
                (' ', 'whitespace'),
                ('c', 'identifier'),
                ('[', 'preprocessing-op-or-punc'),
                ('2', 'pp-number'),
                (']', 'preprocessing-op-or-punc'),
                ('[', 'preprocessing-op-or-punc'),
                ('6', 'pp-number'),
                (']', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('=', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('{', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('str', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('hello', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (',', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('str', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('}', 'preprocessing-op-or-punc'),
                (';', 'preprocessing-op-or-punc'),
                ('\n', 'whitespace')
            ]
        )
        #self.assertEqual([], myMps.currentString)
        self.assertEqual(378, myMps.idxChar)

class TestItuToHtmlTokenGen(unittest.TestCase):
    """Test the ItuToHtml token genreator."""
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_00(self):
        """TestItuToHtmlTokenGen.test_00(): setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestItuToHtmlTokenGen.test_01(): Hello world."""
        myStr = """#include <iostream>

using namespace std;

void main()
{
    cout << "Hello World!" << endl;
    cout << "Welcome to C++ Programming" << endl;
}
"""
        myIth = ItuToTokens.ItuToTokens(io.StringIO(myStr))
        myTokS = [aTok for aTok in myIth.genTokensKeywordPpDirective()]
        #print
        #pprint.pprint(myTokS)
        expTokS = [
            ('#', 'preprocessing-op-or-punc'),
            ('include', 'preprocessing-directive'),
            (' ', 'whitespace'),
            ('<', 'preprocessing-op-or-punc'),
            ('iostream', 'identifier'),
            ('>', 'preprocessing-op-or-punc'),
            ('\n\n', 'whitespace'),
            ('using', 'keyword'),
            (' ', 'whitespace'),
            ('namespace', 'keyword'),
            (' ', 'whitespace'),
            ('std', 'identifier'),
            (';', 'preprocessing-op-or-punc'),
            ('\n\n', 'whitespace'),
            ('void', 'keyword'),
            (' ', 'whitespace'),
            ('main', 'identifier'),
            ('(', 'preprocessing-op-or-punc'),
            (')', 'preprocessing-op-or-punc'),
            ('\n', 'whitespace'),
            ('{', 'preprocessing-op-or-punc'),
            ('\n    ', 'whitespace'),
            ('cout', 'identifier'),
            (' ', 'whitespace'),
            ('<<', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('"Hello World!"', 'string-literal'),
            (' ', 'whitespace'),
            ('<<', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('endl', 'identifier'),
            (';', 'preprocessing-op-or-punc'),
            ('\n    ', 'whitespace'),
            ('cout', 'identifier'),
            (' ', 'whitespace'),
            ('<<', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('"Welcome to C++ Programming"', 'string-literal'),
            (' ', 'whitespace'),
            ('<<', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('endl', 'identifier'),
            (';', 'preprocessing-op-or-punc'),
            ('\n', 'whitespace'),
            ('}', 'preprocessing-op-or-punc'),
            ('\n', 'whitespace')
        ]
        self.assertEqual(expTokS, myTokS)

    def test_02(self):
        """TestItuToHtmlTokenGen.test_02(): Literals."""
        myStr = """char c = 'c';
long l = 42L;
int i = 42;
float f = 1.234E-27 ;
int o = 0123;
int h = 0xABC;
const char* s = "Hello world";
"""
        myIth = ItuToTokens.ItuToTokens(io.StringIO(myStr))
        myTokS = [aTok for aTok in myIth.genTokensKeywordPpDirective()]
        #print
        #pprint.pprint(myTokS)
        expTokS = [
            ('char', 'keyword'),
            (' ', 'whitespace'),
            ('c', 'identifier'),
            (' ', 'whitespace'),
            ('=', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ("'c'", 'character-literal'),
            (';', 'preprocessing-op-or-punc'),
            ('\n', 'whitespace'),
            ('long', 'keyword'),
            (' ', 'whitespace'),
            ('l', 'identifier'),
            (' ', 'whitespace'),
            ('=', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('42L', 'pp-number'),
            (';', 'preprocessing-op-or-punc'),
            ('\n', 'whitespace'),
            ('int', 'keyword'),
            (' ', 'whitespace'),
            ('i', 'identifier'),
            (' ', 'whitespace'),
            ('=', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('42', 'pp-number'),
            (';', 'preprocessing-op-or-punc'),
            ('\n', 'whitespace'),
            ('float', 'keyword'),
            (' ', 'whitespace'),
            ('f', 'identifier'),
            (' ', 'whitespace'),
            ('=', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('1.234E-27', 'pp-number'),
            (' ', 'whitespace'),
            (';', 'preprocessing-op-or-punc'),
            ('\n', 'whitespace'),
            ('int', 'keyword'),
            (' ', 'whitespace'),
            ('o', 'identifier'),
            (' ', 'whitespace'),
            ('=', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('0123', 'pp-number'),
            (';', 'preprocessing-op-or-punc'),
            ('\n', 'whitespace'),
            ('int', 'keyword'),
            (' ', 'whitespace'),
            ('h', 'identifier'),
            (' ', 'whitespace'),
            ('=', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('0xABC', 'pp-number'),
            (';', 'preprocessing-op-or-punc'),
            ('\n', 'whitespace'),
            ('const', 'keyword'),
            (' ', 'whitespace'),
            ('char', 'keyword'),
            ('*', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('s', 'identifier'),
            (' ', 'whitespace'),
            ('=', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('"Hello world"', 'string-literal'),
            (';', 'preprocessing-op-or-punc'),
            ('\n', 'whitespace')
        ]
        self.assertEqual(expTokS, myTokS)

class TestItuToHtmlTokenGenSpecial(unittest.TestCase):
    """Test the ItuToHtml token genreator for special cases."""
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_00(self):
        """TestItuToHtmlTokenGenSpecial.test_00(): setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestItuToHtmlTokenGenSpecial.test_01(): Use of $ in a file."""
        myStr = """# define _ASM_j(cond,dest) _asm jn##cond short $+11 _asm jmp dest
"""
        myIth = ItuToTokens.ItuToTokens(io.StringIO(myStr))
        myTokS = [aTok for aTok in myIth.genTokensKeywordPpDirective()]
        #print
        #pprint.pprint(myTokS)
        expTokS = [
            ('#', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('define', 'preprocessing-directive'),
            (' ', 'whitespace'),
            ('_ASM_j', 'identifier'),
            ('(', 'preprocessing-op-or-punc'),
            ('cond', 'identifier'),
            (',', 'preprocessing-op-or-punc'),
            ('dest', 'identifier'),
            (')', 'preprocessing-op-or-punc'),
            (' ', 'whitespace'),
            ('_asm', 'identifier'),
            (' ', 'whitespace'),
            ('jn', 'identifier'),
            ('##', 'preprocessing-op-or-punc'),
            ('cond', 'identifier'),
            (' ', 'whitespace'),
            ('short', 'keyword'),
            (' ', 'whitespace'),
            ('$', 'non-whitespace'),
            ('+', 'preprocessing-op-or-punc'),
            ('11', 'pp-number'),
            (' ', 'whitespace'),
            ('_asm', 'identifier'),
            (' ', 'whitespace'),
            ('jmp', 'identifier'),
            (' ', 'whitespace'),
            ('dest', 'identifier'),
            ('\n', 'whitespace')
        ]
        self.assertEqual(expTokS, myTokS)

    def test_02_00(self):
        """TestItuToHtmlTokenGenSpecial.test_02_00(): ISO/IEC 14882:1998(E) 2.12 Operators and punctuators [lex.operators] 'new' is a preprocessing-op-or-punc and keyword."""
        myStr = """(new);
"""
        myIth = ItuToTokens.ItuToTokens(io.StringIO(myStr))
        myTokS = [aTok for aTok in myIth.genTokensKeywordPpDirective()]
        #print
        #pprint.pprint(myTokS)
        expTokS = [
                ('(', 'preprocessing-op-or-punc'),
                ('new', 'keyword'),
                (')', 'preprocessing-op-or-punc'),
                (';', 'preprocessing-op-or-punc'),
                ('\n', 'whitespace'),
            ]
        self.assertEqual(expTokS, myTokS)

    def test_02_01(self):
        """TestItuToHtmlTokenGenSpecial.test_02_01(): ISO/IEC 14882:1998(E) 2.12 Operators and punctuators [lex.operators] 'new' is a preprocessing-op-or-punc and keyword."""
        myStr = """new;
"""
        myIth = ItuToTokens.ItuToTokens(io.StringIO(myStr))
        myTokS = [aTok for aTok in myIth.genTokensKeywordPpDirective()]
        #print
        #pprint.pprint(myTokS)
        expTokS = [
                ('new', 'keyword'),
                (';', 'preprocessing-op-or-punc'),
                ('\n', 'whitespace'),
            ]
        self.assertEqual(expTokS, myTokS)

    def test_02_10(self):
        """TestItuToHtmlTokenGenSpecial.test_02_10(): Use of new after parenthesis."""
        myStr = """return(new(ELeave) CBufFlat(anExpandSize));
"""
        myIth = ItuToTokens.ItuToTokens(io.StringIO(myStr))
        myTokS = [aTok for aTok in myIth.genTokensKeywordPpDirective()]
        #print
        #pprint.pprint(myTokS)
        expTokS = [
                ('return', 'keyword'),
                ('(', 'preprocessing-op-or-punc'),
                ('new', 'keyword'),
                ('(', 'preprocessing-op-or-punc'),
                ('ELeave', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (' ', 'whitespace'),
                ('CBufFlat', 'identifier'),
                ('(', 'preprocessing-op-or-punc'),
                ('anExpandSize', 'identifier'),
                (')', 'preprocessing-op-or-punc'),
                (')', 'preprocessing-op-or-punc'),
                (';', 'preprocessing-op-or-punc'),
                ('\n', 'whitespace'),
            ]
        self.assertEqual(expTokS, myTokS)

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    """Execute unit tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestItuToHtmlLowLevel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestItuToHtmlPhase3))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestItuToHtmlTokenGen))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestItuToHtmlTokenGenSpecial))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

#################
# End: Unit tests
#################

def usage():
    """Send the help to stdout."""
    print("""TestItuToHtml.py - A module that tests ItuToHtml module.
Usage:
python TestItuToHtml.py [-lh --help]

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
    print('TestItuToHtml.py script version "%s", dated %s' % (__version__, __date__))
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
