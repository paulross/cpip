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
import string

from cpip import ExceptionCpip
from cpip.util import MaxMunchGen
import TestBufGen

#######################################
# Section: Unit tests
########################################
class TestMaxMunchGen(unittest.TestCase):
    def setUp(self):
        pass
    
    def testNull(self):
        """TestMaxMunchGen: Test setUp() and tearDown()."""
        pass

    def tearDown(self):
        pass

class TestMaximalMunchText(unittest.TestCase):
    """Tests text parsing."""
    def vowels(self, theGen):
        i = 0
        for aVal in theGen:
            if not aVal in 'aeiou':
                break
            i +=1
        return i, 'vowels', None
    def numbers(self, theGen):
        i = 0
        for aVal in theGen:
            if not aVal in string.digits:
                break
            i +=1
        return i, 'numbers', None
    def consonants(self, theGen):
        i = 0
        for aVal in theGen:
            if not (aVal.lower() in 'bcdfghjklmnpqrstvwxyz'):
                break
            i +=1
        return i, 'consonants', None
    def consonants_2(self, theGen):
        i = 0
        try:
            while theGen.next().lower() in 'bcdfghjklmnpqrstvwxyz':
                i +=1
        except StopIteration:
            pass
        return i, 'consonants', None    
    def whitespace(self, theGen):
        i = 0
        try:
            while theGen.next().lower() in ' \t\n':
                i +=1
        except StopIteration:
            pass
        return i, 'whitespace', None 
    
    def setUp(self):
        pass
    
    def testNull(self):
        """TestMaximalMunchText: Test setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestMaximalMunchText: Test parsing vowels, consonants and digits: ''."""
        myStrGen = TestBufGen.StrGen('')
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.vowels,
                        self.numbers,
                        self.consonants,
                    ]
                    )
        myResult = [aVal for aVal in myBg.gen()]
        myExpResult = []
        self.assertEquals(myResult, myExpResult)

    def test_01(self):
        """TestMaximalMunchText: Test parsing vowels, consonants and digits: 'a'."""
        myStrGen = TestBufGen.StrGen('a')
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.vowels,
                        self.numbers,
                        self.consonants,
                    ]
                    )
        myResult = [aVal for aVal in myBg.gen()]
        myExpResult = [
            (['a', ],     'vowels'),
                       ]
        self.assertEquals(myResult, myExpResult)

    def test_02(self):
        """TestMaximalMunchText: Test parsing vowels, consonants and digits: 'aeioubc123daaavfr'."""
        myStrGen = TestBufGen.StrGen('aeioubc123daaavfr')
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.vowels,
                        self.numbers,
                        self.consonants,
                    ]
                    )
        myResult = [aVal for aVal in myBg.gen()]
        myExpResult = [
            (['a', 'e', 'i', 'o', 'u'],     'vowels'),
            (['b', 'c'],                    'consonants'),
            (['1', '2', '3'],               'numbers'),
            (['d'],                         'consonants'),
            (['a', 'a', 'a'],               'vowels'),
            (['v', 'f', 'r'],               'consonants'),
                       ]
        self.assertEquals(myResult, myExpResult)

    def test_03_00(self):
        """TestMaximalMunchText: Test parsing vowels, consonants and digits: 'wraexyz'."""
        myStrGen = TestBufGen.StrGen('wraexyz')
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.vowels,
                        self.numbers,
                        self.consonants,
                    ]
                    )
#===============================================================================
#        print
#        for aVal in myBg.gen():
#            print aVal
#        return
#===============================================================================
        myResult = [aVal for aVal in myBg.gen()]
        myExpResult = [
            (['w', 'r'], 'consonants'),
            (['a', 'e'], 'vowels'),
            (['x', 'y', 'z'], 'consonants'),
                       ]
        self.assertEquals(myResult, myExpResult)

    def test_03_01(self):
        """TestMaximalMunchText: Test parsing vowels, consonants and digits: 'wraexyz' with alternate function."""
        myStrGen = TestBufGen.StrGen('wraexyz')
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.vowels,
                        self.numbers,
                        self.consonants_2,
                    ]
                    )
#===============================================================================
#        print
#        for aVal in myBg.gen():
#            print aVal
#        return
#===============================================================================
        myResult = [aVal for aVal in myBg.gen()]
        myExpResult = [
            (['w', 'r'], 'consonants'),
            (['a', 'e'], 'vowels'),
            (['x', 'y', 'z'], 'consonants'),
                       ]
        self.assertEquals(myResult, myExpResult)

    def test_04_00(self):
        """TestMaximalMunchText: Test parsing vowels, consonants, no whitespace: 'wrae xyz'."""
        myStrGen = TestBufGen.StrGen('wrae xyz')
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.vowels,
                        self.consonants,
                    ]
                    )
        myResult = [aVal for aVal in myBg.gen()]
        myExpResult = [
            (['w', 'r'], 'consonants'),
            (['a', 'e'], 'vowels'),
            #(['x', 'y', 'z'], 'consonants'),
                       ]
        self.assertEquals(myResult, myExpResult)

    def test_04_01(self):
        """TestMaximalMunchText: Test parsing vowels, consonants and whitespace: 'wrae xyz'."""
        myStrGen = TestBufGen.StrGen('wrae xyz')
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.vowels,
                        self.consonants,
                        self.whitespace,
                    ]
                    )
        myResult = [aVal for aVal in myBg.gen()]
        myExpResult = [
            (['w', 'r'],        'consonants'),
            (['a', 'e'],        'vowels'),
            ([' ', ],           'whitespace'),
            (['x', 'y', 'z'],   'consonants'),
                       ]
        self.assertEquals(myResult, myExpResult)

    def test_04_02(self):
        """TestMaximalMunchText: Test parsing vowels, consonants, whitespace as anyToken(): 'wrae xyz'."""
        myStrGen = TestBufGen.StrGen('wrae xyz')
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.vowels,
                        self.consonants,
                        MaxMunchGen.anyToken,
                    ]
                    )
#===============================================================================
#        print
#        for aVal in myBg.gen():
#            print aVal
#        return
#===============================================================================
        myResult = [aVal for aVal in myBg.gen()]
        myExpResult = [
            (['w', 'r'],        'consonants'),
            (['a', 'e'],        'vowels'),
            ([' ', ],           None),
            (['x', 'y', 'z'],   'consonants'),
                       ]
        self.assertEquals(myResult, myExpResult)

    def test_11(self):
        """TestMaximalMunchText: ambiguos result."""
        myStrGen = TestBufGen.StrGen('aeiou')
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.vowels,
                        self.vowels,
                    ]
                    )
        try:
            myResult = [aVal for aVal in myBg.gen()]
            self.fail('ExceptionMaxMunchGen not raised')
        except MaxMunchGen.ExceptionMaxMunchGen:
            pass
    
    def tearDown(self):
        pass

class TestMaximalMunchReplace(unittest.TestCase):
    """Tests text parsing and replacement."""
    def nonwhitespace(self, theGen):
        i = 0
        for aVal in theGen:
            if aVal in ' \t\n':
                break
            i +=1
        return i, 'nonwhitespace', None
    def whitespace(self, theGen):
        i = 0
        try:
            while theGen.next().lower() in ' \t\n':
                i +=1
        except StopIteration:
            pass
        return i, 'whitespace', [' ']
    
    def setUp(self):
        pass
    
    def testNull(self):
        """TestMaximalMunchReplace: Test setUp() and tearDown()."""
        pass

    def tearDown(self):
        pass
    
    def test_00(self):
        """TestMaximalMunchReplace: Space runs to single space."""
        myStrGen = TestBufGen.StrGen(' abc    def  ghi d ')
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.whitespace,
                        self.nonwhitespace,
                    ]
                    )
#        print
#        for aVal in myBg.gen():
#            print aVal
#        return
        myResult = [aVal for aVal in myBg.gen()]
        myExpResult = [
            ([' '],             'whitespace'),
            (['a', 'b', 'c'],   'nonwhitespace'),
            ([' '],             'whitespace'),
            (['d', 'e', 'f'],   'nonwhitespace'),
            ([' '],             'whitespace'),
            (['g', 'h', 'i'],   'nonwhitespace'),
            ([' '],             'whitespace'),
            (['d'],             'nonwhitespace'),
            ([' '],             'whitespace'),
                       ]
        self.assertEquals(myResult, myExpResult)

class TestMaximalMunchTrigraph(unittest.TestCase):
    """Simulates Trigraph replacement."""
    SOURCE_CHARACTER_SET = set("""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_{}[]#()<>%:;.?*+-/^&|~!=,\\"'\t\v\f\n """)
    UCN_ORDINALS =  set((0x24, 0x40, 0x60))
    # NOTE: Constant prefix of '??' is absent from keys.
    TRIGRAPH_TABLE = {
        '='       : '#',
        '('       :  '[',
        '<'       : '{',
        '/'       : '\\',
        ')'       : ']',
        '>'       : '}',
        "'"       : '^',
        '!'       : '|',
        '-'       : '~',
    }
    TRIGRAPH_SIZE = 3
    def universalCharacterName(self, theGen):
        i = 0
        r = None
        try:
            myChr = theGen.next()
            if myChr not in self.SOURCE_CHARACTER_SET:
                i = 1
                myOrd = ord(myChr)
                # Expand to a universal-character-name
                if myOrd <= 0xFFFF:
                    if myOrd not in self.UCN_ORDINALS:
                        # This is not 0024 ($), 0040 (@), or 0060 (back tick)
                        r = '\\u%04X' % myOrd
                else:
                    self._fileLocator.substString(1, 8)
                    r = '\\U%08X' % myOrd
        except StopIteration:
            pass
        return i, 'ucn', r
    def trigraph(self, theGen):
        i = 0
        r = None
        try:
            if theGen.next() == '?' \
            and theGen.next() == '?':
                try:
                    r = self.TRIGRAPH_TABLE[theGen.next()]
                    i = self.TRIGRAPH_SIZE
                except KeyError:
                    pass
        except StopIteration:
            pass
        return i, 'trigraph', r
    
    def setUp(self):
        pass
    
    def testNull(self):
        """TestMaximalMunchTrigraph: Test setUp() and tearDown()."""
        pass

    def tearDown(self):
        pass
    
    def test_00(self):
        """TestMaximalMunchTrigraph: Trigraph replacemnt."""
        myPStr = '??=define arraycheck(a,b) a??(b??) ??!??! b??(a??)'
        myLStr = '#define arraycheck(a,b) a[b] || b[a]'
        myStrGen = TestBufGen.StrGen(myPStr)
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.universalCharacterName,
                        self.trigraph,
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=True
                    )
#        print
#        for aVal in myBg.gen():
#            print aVal
#        return
        myResult = [aVal for aVal in myBg.gen()]
        myResultStr = ''.join([''.join(v[0]) for v in myResult])
        #print
        #print myResultStr
        self.assertEquals(myResultStr, myLStr)

    def test_01(self):
        """TestMaximalMunchTrigraph: universal-character-name replacemnt."""
        myPStr = 'ab\xa9$@xyz'
        myLStr = 'ab\\u00A9$@xyz'
        myStrGen = TestBufGen.StrGen(myPStr)
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.trigraph,
                        self.universalCharacterName,
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=True
                    )
#        print
#        for aVal in myBg.gen():
#            print aVal
#        return
        myResult = [aVal for aVal in myBg.gen()]
        myResultStr = ''.join([''.join(v[0]) for v in myResult])
        #print
        #print myResultStr
        self.assertEquals(myResultStr, myLStr)

class TestMaximalMunchLineContinuation(unittest.TestCase):
    """Simulates line continuation replacement."""
    def __init__(self, *args):
        super(TestMaximalMunchLineContinuation, self).__init__(*args)
        self._cntrAddNewLinesAfterCont = 0
        
    def lineContinuation(self, theGen):
        i = 0
        r = None
        try:
            aChar = theGen.next()
            if aChar == '\\' \
            and theGen.next() == '\n':
                r = ''
                i = 2
                self._cntrAddNewLinesAfterCont += 1
            elif aChar == '\n' and self._cntrAddNewLinesAfterCont > 0:
                r = '\n' * (1+self._cntrAddNewLinesAfterCont)
                i = 1
                self._cntrAddNewLinesAfterCont = 0
        except StopIteration:
            pass
        return i, 'lineContinuation', r
    
    def setUp(self):
        pass
    
    def testNull(self):
        """TestMaximalMunchLineContinuation: Test setUp() and tearDown()."""
        pass

    def tearDown(self):
        pass
    
    def test_00(self):
        """TestMaximalMunchLineContinuation: Line continuation replacement [00]."""
        myStrIn  = 'abc\\\ndef\n'
        myStrOut = 'abcdef\n\n'
        myStrGen = TestBufGen.StrGen(myStrIn)
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.lineContinuation,
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=True
                    )
#        print
#        for aVal in myBg.gen():
#            print aVal
#        return
        myResult = [aVal for aVal in myBg.gen()]
        #print myResult
        myResultStr = ''.join([''.join(v[0]) for v in myResult])
        #print
        #print myResultStr
        self.assertEquals(myResultStr, myStrOut)
        self.assertEquals(0, self._cntrAddNewLinesAfterCont)

    def test_01(self):
        """TestMaximalMunchLineContinuation: Line continuation replacement [01]."""
        myStrIn  = 'a\\\nb\\\nc\n'
        myStrOut = 'abc\n\n\n'
        myStrGen = TestBufGen.StrGen(myStrIn)
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.lineContinuation,
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=True
                    )
#        print
#        for aVal in myBg.gen():
#            print aVal
#        return
        myResult = [aVal for aVal in myBg.gen()]
        #print myResult
        myResultStr = ''.join([''.join(v[0]) for v in myResult])
        #print
        #print myResultStr
        self.assertEquals(myResultStr, myStrOut)
        self.assertEquals(0, self._cntrAddNewLinesAfterCont)

    def test_02(self):
        """TestMaximalMunchLineContinuation: Line continuation replacement - detection of one at EOF [02]."""
        myStrIn  = 'a\\\n'
        myStrOut = 'a\n'
        myStrGen = TestBufGen.StrGen(myStrIn)
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.lineContinuation,
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=True
                    )
#        print
#        for aVal in myBg.gen():
#            print aVal
#        return
        myResult = [aVal for aVal in myBg.gen()]
        #print myResult
        self.assertEquals(myResult, [(['a'], None), ([], 'lineContinuation')])
        self.assertEquals(1, self._cntrAddNewLinesAfterCont)

class ExceptionTestMaximalMunchComment(ExceptionCpip):
    pass
    
class TestMaximalMunchComment(unittest.TestCase):
    """Simulates comment replacement."""
#    def __init__(self, *args):
#        super(TestMaximalMunchLineContinuation, self).__init__(*args)
#        self._cntrAddNewLinesAfterCont = 0
        
    def cComment(self, theGen):
        i = 0
        r = None
        try:
            aChar = theGen.next()
            if aChar == '/' \
            and theGen.next() == '*':
                r = ' '
                i = 2
                while 1:
                    if theGen.next() == '*':
                        i += 1
                        if theGen.next() == '/':
                            i += 1
                            break
                    else:
                        i += 1                        
        except StopIteration:
            # Raise here if i > 0 as unclosed comment
            if i > 0:
                raise ExceptionTestMaximalMunchComment()
            pass
        return i, 'cComment', r
    def cxxComment(self, theGen):
        i = 0
        r = None
        try:
            aChar = theGen.next()
            if aChar == '/' \
            and theGen.next() == '/':
                r = ' '
                i = 2
                while 1:
                    if theGen.next() == '\n':
                        #i += 1
                        break
                    i += 1                        
        except StopIteration:
            # Raise here if i > 0 as unclosed comment
            if i > 0:
                raise ExceptionTestMaximalMunchComment()
        return i, 'cxxComment', r
    
    
    def setUp(self):
        pass
    
    def testNull(self):
        """TestMaximalMunchComment: Test setUp() and tearDown()."""
        pass

    def tearDown(self):
        pass
    
    def test_00(self):
        """TestMaximalMunchComment: Comment [00]."""
        myStrIn  = """// CXX Comment

/ // More comment

// /* C inside CXX */

/* C comment */

/* // CXX in C */
"""
        myStrOut = ' \n\n/  \n\n \n\n \n\n \n'
        myStrGen = TestBufGen.StrGen(myStrIn)
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.cComment,
                        self.cxxComment,
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=False
                    )
#        print
#        for aVal in self._bg.gen():
#            print aVal
#        return
        myResult = [aVal for aVal in myBg.gen()]
        #print myResult
        myResultStr = ''.join([''.join(v[0]) for v in myResult])
        #print
        #print myResultStr
        self.assertEquals(myResultStr, myStrOut)

    def test_01(self):
        """TestMaximalMunchComment: Unclosed C Comment."""
        myStrIn  = """/* 
"""
        myStrOut = ''
        myStrGen = TestBufGen.StrGen(myStrIn)
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.cComment,
                        self.cxxComment,
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=False
                    )
#        print
#        for aVal in self._bg.gen():
#            print aVal
#        return
        try:
            myResult = [aVal for aVal in myBg.gen()]
            self.fail('ExceptionTestMaximalMunchComment not raised')
        except ExceptionTestMaximalMunchComment:
            pass

    def test_02(self):
        """TestMaximalMunchComment: Unclosed CXX Comment."""
        myStrIn  = '//'
        myStrOut = ''
        myStrGen = TestBufGen.StrGen(myStrIn)
        myBg = MaxMunchGen.MaxMunchGen(
                    myStrGen.next(),
                    [
                        self.cComment,
                        self.cxxComment,
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=False
                    )
#        print
#        for aVal in self._bg.gen():
#            print aVal
#        return
        try:
            myResult = [aVal for aVal in myBg.gen()]
            self.fail('ExceptionTestMaximalMunchComment not raised')
        except ExceptionTestMaximalMunchComment:
            pass

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    """Execute unit tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMaxMunchGen))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMaximalMunchText))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMaximalMunchReplace))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMaximalMunchTrigraph))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMaximalMunchLineContinuation))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMaximalMunchComment))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

#################
# End: Unit tests
#################

def usage():
    """Send the help to stdout."""
    print \
"""TestMaxMunchGen.py - A module that tests PpToken module.
Usage:
python TestMaxMunchGen.py [-lh --help]

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
"""

def main():
    """Invoke unit test code."""
    print 'TestMaxMunchGen.py script version "%s", dated %s' % (__version__, __date__)
    print 'Author: %s' % __author__
    print __rights__
    print
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError:
        usage()
        print 'ERROR: Invalid options!'
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
        print 'ERROR: Wrong number of arguments!'
        sys.exit(1)
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    clkStart = time.clock()
    unitTest()
    clkExec = time.clock() - clkStart
    print 'CPU time = %8.3f (S)' % clkExec
    print 'Bye, bye!'

if __name__ == "__main__":
    main()
