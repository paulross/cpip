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

"""A module that tests the implementation limits of the PpLexer module.

Limitations identified in ISO/IEC ISO/IEC 9899:1999 (E):
5.2.4.1 Translation limits
1 The implementation shall be able to translate and execute at least one program that
contains at least one instance of every one of the following limits:13)
- 127 nesting levels of blocks
- 63 nesting levels of conditional inclusion
- 12 pointer, array, and function declarators (in any combinations) modifying an
arithmetic, structure, union, or incomplete type in a declaration
- 63 nesting levels of parenthesized declarators within a full declarator
- 63 nesting levels of parenthesized expressions within a full expression
- 63 significant initial characters in an internal identifier or a macro name (each
universal character name or extended source character is considered a single
character)
- 31 significant initial characters in an external identifier (each universal character name
specifying a short identifier of 0000FFFF or less is considered 6 characters, each
universal character name specifying a short identifier of 00010000 or more is
considered 10 characters, and each extended source character is considered the same
13) Implementations should avoid imposing fixed translation limits whenever possible.
20 Environment 5.2.4.1
ISO/IEC ISO/IEC 9899:1999 (E)

number of characters as the corresponding universal character name, if any)14)
- 4095 external identifiers in one translation unit
- 511 identifiers with block scope declared in one block
- 4095 macro identifiers simultaneously defined in one preprocessing translation unit
- 127 parameters in one function definition
- 127 arguments in one function call
- 127 parameters in one macro definition
- 127 arguments in one macro invocation
- 4095 characters in a logical source line
- 4095 characters in a character string literal or wide string literal (after concatenation)
- 65535 bytes in an object (in a hosted environment only)
- 15 nesting levels for #included files
- 1023 case labels for a switch statement (excluding those for any nested switch
statements)
- 1023 members in a single structure or union
- 1023 enumeration constants in a single enumeration
- 63 levels of nested structure or union definitions in a single struct-declaration-list


TODO: Do 64 levels, non-exhaustive with only two #includes
TODO: 64 levels with random set of macro values set and limited (not 2^64!) tests.
TODO: Other relevant tests (above).
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import time
import logging
import sys
import os
try:
    import io as StringIO
except ImportError:
    import io
import pprint

from cpip.core import PpLexer, PpTokeniser, PpToken
# File location test classes
from cpip.core.IncludeHandler import CppIncludeStringIO

import TestPpDefine

import unittest

class TestPpLexerLimits(TestPpDefine.TestPpDefine):
    """Helper class for the unit tests."""
    pass

class TestPpLexerCondIncBase(TestPpLexerLimits):
    """Tests 5.2.4.1 Translation limits - nesting levels of conditional inclusion."""
    # NOTE: 2 means 0, 1, 2 will be generated
    MAX_DEPTH_INDEX = 2
    #FIELD_WIDTH = MAX_DEPTH_INDEX+1
    # Are all possible combinations of conditional include generated
    IS_ITU_EXHAUSTIVE = True#False 
    def setUp(self):
        self._itu = io.StringIO()
        #myInt = long(1)
        myInt = self.retIntRep()
        #print myInt
        self._retIntRepAct = self._writeCondInclude(
                                self._itu,
                                myInt,
                                0,
                                )
        
    def tearDown(self):
        #print 'self._itu:\n', self._itu.getvalue()
        #print 'self.retIncludeMapAndContents()'
        #pprint.pprint(self.retIncludeMapAndContents())
        self._itu.close()
        
    def retIntRep(self):
        return (int(1)<<self.MAX_DEPTH_INDEX+1)-1
        
    def _padStr(self, theD):
        return ''
        #return ' ' * (self.MAX_DEPTH_INDEX-theD)
    
    def _retMacroName(self, theIntId):
        """Returns a macro name."""
        return 'C' + format(theIntId, '0%db' % (self.MAX_DEPTH_INDEX+1))
    
    def _writeCppIf(self, theFile, theD):
        theFile.write(self._padStr(theD))
        theFile.write('#if ')
        theFile.write(self._retMacroName(theD))
        theFile.write('\n')
    
    def retCppDefine(self, theIntId, theIntRepr):
        # NOTE: Inversion of logic here
        if ((int(1) << theIntId) & theIntRepr):
            mName = self._retMacroName(theIntId) + ' 1'
        else:
            mName = self._retMacroName(theIntId) + ' 0'
        #print 'theIntId=%d, theIntRepr=%d, mName=%s' % (theIntId, theIntRepr, mName)
        return '#define ' + mName
    
    def _includeId(self, theIntRep):
        return format(theIntRep, '0%db' % (self.MAX_DEPTH_INDEX+1))
        
    def _includeContents(self, theIntRep):
        return self._includeId(theIntRep) + '\n'
    
    def _includeName(self, theIntRep):
        return 'H%s.h' % self._includeId(theIntRep)
    
    def retExpTokensNoWs(self, theIntRep):
        return [
                PpToken.PpToken(self._includeId(theIntRep), 'pp-number'),
                ]
        
    def _writeCppInclude(self, theFile, theD, theIntRep):
        theFile.write('%s#include "%s"\n' \
                      % (
                         self._padStr(theD),
                         self._includeName(theIntRep)))
    
    def _writeCondInclude(self, theFile, theIntRep, theDepth):
        """Recursive #if...#include writer."""
        assert(theDepth <= self.MAX_DEPTH_INDEX)
        myIntRep = theIntRep
        self._writeCppIf(theFile, self.MAX_DEPTH_INDEX-theDepth)
        if theDepth == self.MAX_DEPTH_INDEX:
            # Base case
            self._writeCppInclude(theFile, 1+theDepth, myIntRep)
            #theFile.write('%s#include "H%s.h"\n' % (' ' * (1+theDepth), format(myIntRep, '04b')))
            myIntRep -= 1
        else:
            # Recursive case
            myIntRep = self._writeCondInclude(theFile, myIntRep, theDepth+1)
        theFile.write('%s#else\n' % self._padStr(theDepth))
        if theDepth == self.MAX_DEPTH_INDEX:
            # Base case
            self._writeCppInclude(theFile, 1+theDepth, myIntRep)
            #theFile.write('%s#include "H%s.h"\n' % (' ' * (1+theDepth), format(myIntRep, '04b')))
            myIntRep -= 1
        elif self.IS_ITU_EXHAUSTIVE:
            # Recursive case
            myIntRep = self._writeCondInclude(theFile, myIntRep, theDepth+1)
        theFile.write('%s#endif\n' % self._padStr(theDepth))
        return myIntRep
    
    def retIncludeMapAndContents(self):
        retMap = {}
        myIntRep = self.retIntRep()
        cntr = 0
        while myIntRep > -1:
            retMap[self._includeName(myIntRep)] = self._includeContents(myIntRep) 
            cntr += 1
            if cntr == 2 and not self.IS_ITU_EXHAUSTIVE:
                break
            myIntRep -= 1
        return retMap

    def testSetupTearDown(self):
        """TestPpLexerCondIncBase.testSetupTearDown():"""
        pass
    
    def retIncHandler(self):
        """Returns a populated StringIO handler."""
        return CppIncludeStringIO(
                [],
                [], 
                self._itu.getvalue(),
                self.retIncludeMapAndContents()
                )
    
    def retPreIncludeMacros(self, theIntRepr=None):
        if theIntRepr is None: 
            theIntRepr = self.retIntRep()
        #print
        #print 'retPreIncludeMacros(theIntRepr):', format(theIntRepr, 'b')
        myInt = 0
        myDefS = []
        while myInt < self.MAX_DEPTH_INDEX+1:
            myDefS.append(self.retCppDefine(myInt, theIntRepr))
            myInt += 1
        return '\n'.join(myDefS) + '\n'
        
class TestPpLexerCondIncFour(TestPpLexerCondIncBase):
    """Tests 5.2.4.1 Translation limits - 4 nesting levels of conditional inclusion, exhaustive."""
    # NOTE: 2 means 0, 1, 2 will be generated
    MAX_DEPTH_INDEX = 3
    # Are all possible combinations of conditional include generated
    IS_ITU_EXHAUSTIVE = True 

    def test_00(self):
        """Tests 5.2.4.1 Translation limits - 4 nesting levels of conditional inclusion, no predefines."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 self.retIncHandler(),
                 preIncFiles=[
                              io.StringIO('#define SPAM(x,y) x+y\n#define EGGS SPAM\n'),
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens() if not t.isWs()]
        self.assertEqual(self.retExpTokensNoWs(0), myToks)
        myLexer.finalise()

    def test_01_00(self):
        """TestPpLexerCondIncFour.test_01_00(): dummy test."""
        return
        myIntRepr = self.retIntRep()
        while 1:
            print()
            print('myIntRepr:', myIntRepr)
            print('With\n', self.retPreIncludeMacros(myIntRepr))
            print('self._itu:\n', self._itu.getvalue())
            print('Expects: ', self._includeId(myIntRepr))
            print('     Or: ', self.retExpTokensNoWs(myIntRepr))
            if myIntRepr == 0:
                break
            myIntRepr -= 1

    def test_01(self):
        """Tests 5.2.4.1 Translation limits - 4 nesting levels of conditional inclusion, exhaustive."""
        myIntRepr = self.retIntRep()
        myIncHandler = self.retIncHandler()
        #print 'self._itu:\n', self._itu.getvalue()
        while 1:
            #print
            #print 'myIntRepr:', myIntRepr
            myLexer = PpLexer.PpLexer(
                     'mt.h',
                     myIncHandler,
                     preIncFiles=[
                        io.StringIO(self.retPreIncludeMacros(myIntRepr)),
                                  ],
                     diagnostic=None,
                     )
            myToks = [t for t in myLexer.ppTokens() if not t.isWs()]
            #print '      Got:', myToks
            expToks = self.retExpTokensNoWs(myIntRepr)
            #print ' Expected:', expToks
            # TODO: Fix this test
            self.assertEqual(expToks, myToks)
            myLexer.finalise()
            if myIntRepr == 0:
                break
            myIntRepr -= 1

class TestPpLexerCondIncEight(TestPpLexerCondIncBase):
    """Tests 5.2.4.1 Translation limits - 8 nesting levels of conditional inclusion, exhaustive."""
    # NOTE: 2 means 0, 1, 2 will be generated
    MAX_DEPTH_INDEX = 8
    # Are all possible combinations of conditional include generated
    IS_ITU_EXHAUSTIVE = True 

    def test_00(self):
        """Tests 5.2.4.1 Translation limits - 8 nesting levels of conditional inclusion, no predefines."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 self.retIncHandler(),
                 preIncFiles=[
                              io.StringIO('#define SPAM(x,y) x+y\n#define EGGS SPAM\n'),
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens() if not t.isWs()]
        self.assertEqual(self.retExpTokensNoWs(0), myToks)
        myLexer.finalise()

    def test_01(self):
        """Tests 5.2.4.1 Translation limits - 8 nesting levels of conditional inclusion, exhaustive."""
        myIntRepr = self.retIntRep()
        myIncHandler = self.retIncHandler()
        #print 'self._itu:\n', self._itu.getvalue()
        print('self._itu size: %d' % len(self._itu.getvalue()))
        while 1:
            #print 'myIntRepr:', myIntRepr
            #print
            #print 'myIntRepr:', myIntRepr
            myLexer = PpLexer.PpLexer(
                     'mt.h',
                     myIncHandler,
                     preIncFiles=[
                        io.StringIO(self.retPreIncludeMacros(myIntRepr)),
                                  ],
                     diagnostic=None,
                     )
            myToks = [t for t in myLexer.ppTokens() if not t.isWs()]
            #print '      Got:', myToks
            expToks = self.retExpTokensNoWs(myIntRepr)
            #print ' Expected:', expToks
            # TODO: Fix this test
            self.assertEqual(expToks, myToks)
            myLexer.finalise()
            if myIntRepr == 0:
                break
            myIntRepr -= 1

class TestPpLexerCondInc64NonExhaustive(TestPpLexerCondIncBase):
    """Tests 5.2.4.1 Translation limits - 64 nesting levels of conditional inclusion, non-exhaustive."""
    # NOTE: 2 means 0, 1, 2 will be generated
    MAX_DEPTH_INDEX = 8
    # Are all possible combinations of conditional include generated
    IS_ITU_EXHAUSTIVE = False 

    def test_00(self):
        """Tests 5.2.4.1 Translation limits - 64 nesting levels of conditional inclusion, no predefines."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 self.retIncHandler(),
                 preIncFiles=[
                              io.StringIO('#define SPAM(x,y) x+y\n#define EGGS SPAM\n'),
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens() if not t.isWs()]
        #self.assertEqual(self.retExpTokensNoWs(0), myToks)
        self.assertEqual([], myToks)
        myLexer.finalise()

    def test_01(self):
        """Tests 5.2.4.1 Translation limits - 64 nesting levels of conditional inclusion, non-exhaustive."""
        myIntRepr = self.retIntRep()
        myIncHandler = self.retIncHandler()
        print('self._itu size: %d' % len(self._itu.getvalue()))
        print('self._itu:\n', self._itu.getvalue())
        while 1:
            #print 'myIntRepr:', myIntRepr
            #print
            #print 'myIntRepr:', myIntRepr
            myLexer = PpLexer.PpLexer(
                     'mt.h',
                     myIncHandler,
                     preIncFiles=[
                        io.StringIO(self.retPreIncludeMacros(myIntRepr)),
                                  ],
                     diagnostic=None,
                     )
            myToks = [t for t in myLexer.ppTokens() if not t.isWs()]
            #print '      Got:', myToks
            expToks = self.retExpTokensNoWs(myIntRepr)
            #print ' Expected:', expToks
            # TODO: Fix this test
            self.assertEqual(expToks, myToks)
            myLexer.finalise()
            if myIntRepr == 0:
                break
            myIntRepr -= 1

class Special(TestPpLexerLimits):
    pass
    
class NullClass(TestPpLexerLimits):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerCondIncBase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerCondIncFour))
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerCondIncEight))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerCondInc64NonExhaustive))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Special))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestPpLexerLimits.py - A module that tests the implementation limits of
the PpLexer module.
Usage:
python TestPpLexerLimits.py [-lh --help]

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
    print('TestPpLexer.py script version "%s", dated %s' % (__version__, __date__))
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
