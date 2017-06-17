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
from cpip.core.IncludeHandler import CppIncludeStringIO, CppIncludeStdOs

import TestPpDefine

import unittest

class TestPpLexerPerfBase(TestPpDefine.TestPpDefine):
    """Helper class for the performance tests."""

    def runLex(self, theLex, incWs=True, repeatNum=5):
        """causes theLex to preprocess and returns:
        (tokens, time_in_seconds_as_a_float).
        if repeatNum is non-zero the test is run that number of times and the
        median is returned."""
        assert(repeatNum > 0)
        if (repeatNum % 2) != 1:
            # Even, reduce so as odd for the median
            repeatNum -= 1
        myTimS = []
        for i in range(repeatNum):
            myTimStart = time.clock()
            if incWs:
                myToks = [t for t in theLex.ppTokens()]
            else:
                myToks = [t for t in theLex.ppTokens() if not t.isWs()]
            theLex.finalise()
            myTime = time.clock() - myTimStart
            if repeatNum > 1:
                myTimS.append(myTime)
        if repeatNum > 1:
            myTimS.sort()
            myTime = myTimS[(len(myTimS)-1)/2] 
        sys.stderr.write('Rate (median of %3d: %6.1f tokens/second ... ' \
                         % (repeatNum, len(myToks) / myTime)
                         )
        return myToks, myTime

    def simpleLexWithContent(self, theContent):
        return PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([],[],theContent,{}),
                 preIncFiles=[],
                 diagnostic=None,
                 )
    
    def retObjectMacros(self, theNum):
        """Returns a string that #defines a set of macros that expand to
        each other. This returns a tuple of (#define_string, start, end)
        where start is the token to start with and end is the token that
        should result. 
        For example:
        #define D0001 PASS
        #define D0002 D0001
        #define D0003 D0002
        And this will return that string followed by 'D0003', 'PASS'
        """
        assert(theNum > 0)
        replaceResult = 'PASS'
        fmtDec = 'D%04d'
        fmtStr = '#define %s %%s\n' % fmtDec
        myList = []
        myList.append(fmtStr % (0, replaceResult))
        i = 1
        while i < theNum:
            myList.append(fmtStr % (i, fmtDec%(i-1)))
            i += 1
        return ''.join(myList), fmtDec%(i-1), replaceResult
            


class TestBase(TestPpLexerPerfBase):
    def test00(self):
        """Generation of macro graph."""
        #print
        #print self.retObjectMacros(4)
        self.assertEqual(
            (
                """#define D0000 PASS
#define D0001 D0000
#define D0002 D0001
#define D0003 D0002
""",
                'D0003', 
                'PASS'
            ),
            self.retObjectMacros(4),
            )
        
class TestPpLexerSimpleText(TestPpLexerPerfBase):

    def test_00(self):
        """TestPpLexerSimpleText: Test with "spam\\n" * 1."""
        myText = 'spam\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_00_01(self):
        """TestPpLexerSimpleText: Test with "spam\\n" * 2."""
        myText = 'spam\n' * 2
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_00_02(self):
        """TestPpLexerSimpleText: Test with "spam\\n" * 4."""
        myText = 'spam\n' * 4
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_01(self):
        """TestPpLexerSimpleText: Test with "spam\\n" * 10."""
        myText = 'spam\n' * 10
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_02(self):
        """TestPpLexerSimpleText: Test with "spam\\n" * 100."""
        myText = 'spam\n' * 100
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_03(self):
        """TestPpLexerSimpleText: Test with "spam\\n" * 1000."""
        myText = 'spam\n' * 1000
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_04(self):
        """TestPpLexerSimpleText: Test with "spam\\n" * 10000."""
        myText = 'spam\n' * 10000
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

class TestPpLexerSimpleNumber(TestPpLexerPerfBase):

    def test_00(self):
        """TestPpLexerSimpleNumber: "1 " * 1."""
        myText = ('1 ' * 1) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_00_01(self):
        """TestPpLexerSimpleNumber: "1 " * 2."""
        myText = ('1 ' * 1000) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_00_02(self):
        """TestPpLexerSimpleNumber: "1 " * 4."""
        myText = ('1 ' * 1000) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_01(self):
        """TestPpLexerSimpleNumber: "1 " * 10."""
        myText = ('1 ' * 10) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_02(self):
        """TestPpLexerSimpleNumber: "1 " * 100."""
        myText = ('1 ' * 100) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_03(self):
        """TestPpLexerSimpleNumber: "1 " * 1000."""
        myText = ('1 ' * 1000) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_04(self):
        """TestPpLexerSimpleNumber: "1 " * 10000."""
        myText = ('1 ' * 10000) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_10(self):
        """TestPpLexerSimpleNumber: "-1.23456789e+21 " * 1."""
        myText = ('-1.23456789e+21 ' * 1) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_11(self):
        """TestPpLexerSimpleNumber: "-1.23456789e+21 " * 10."""
        myText = ('-1.23456789e+21 ' * 10) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_12(self):
        """TestPpLexerSimpleNumber: "-1.23456789e+21 " * 100."""
        myText = ('-1.23456789e+21 ' * 100) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_13(self):
        """TestPpLexerSimpleNumber: "-1.23456789e+21 " * 1000."""
        myText = ('-1.23456789e+21 ' * 1000) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

    def test_14(self):
        """TestPpLexerSimpleNumber: "-1.23456789e+21 " * 10000."""
        myText = ('-1.23456789e+21 ' * 10000) + '\n'
        myL = self.simpleLexWithContent(myText)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myText), myToks)

class TestPpLexerReplaceGraph(TestPpLexerPerfBase):
    NUM_TESTS = 10
    
    def _reexamineLevel(self, theLevel):
        myCont, myStart, myEnd = self.retObjectMacros(theLevel)
        myCont += ('%s\n' % myStart) * self.NUM_TESTS
        myL = self.simpleLexWithContent(myCont)
        myToks, myTime = self.runLex(myL)
        myExp = []
        for i in range(theLevel):
            myExp.append(PpToken.PpToken('\n',   'whitespace'))
        myExp += self.stringToTokens(('%s\n' % myEnd) * self.NUM_TESTS)
        self.assertEqual(myExp, myToks)
    
    def test_0001(self):
        """TestPpLexerReplaceGraph: Test with "spam\\n" * 1000, reexamine level =    1."""
        self._reexamineLevel(1)
        
    def test_0002(self):
        """TestPpLexerReplaceGraph: Test with "spam\\n" * 1000, reexamine level =    2."""
        self._reexamineLevel(2)
        
    def test_0004(self):
        """TestPpLexerReplaceGraph: Test with "spam\\n" * 1000, reexamine level =    4."""
        self._reexamineLevel(4)

    def test_0008(self):
        """TestPpLexerReplaceGraph: Test with "spam\\n" * 1000, reexamine level =    8."""
        self._reexamineLevel(8)

    def test_0016(self):
        """TestPpLexerReplaceGraph: Test with "spam\\n" * 1000, reexamine level =   16."""
        self._reexamineLevel(16)
        
    def test_0032(self):
        """TestPpLexerReplaceGraph: Test with "spam\\n" * 1000, reexamine level =   32."""
        self._reexamineLevel(32)
        
    def test_0064(self):
        """TestPpLexerReplaceGraph: Test with "spam\\n" * 1000, reexamine level =   64."""
        self._reexamineLevel(64)
        
    def test_0128(self):
        """TestPpLexerReplaceGraph: Test with "spam\\n" * 1000, reexamine level =  128."""
        self._reexamineLevel(128)
        
    def test_0256(self):
        """TestPpLexerReplaceGraph: Test with "spam\\n" * 1000, reexamine level =  256."""
        self._reexamineLevel(256)
        
    def test_0512(self):
        """TestPpLexerReplaceGraph: Test with "spam\\n" * 1000, reexamine level =  512."""
        self._reexamineLevel(512)
        
#===============================================================================
#    def test_1024(self):
#        """TestPpLexerReplaceGraph: Test with "spam\\n" * 1000, reexamine level = 1024."""
#        self._reexamineLevel(1024)
#===============================================================================
        


class TestPpLexerSimpleReplace(TestPpLexerPerfBase):
    NUM_TESTS = 1000
    def test_00(self):
        """TestPpLexerSimpleReplace: Test with "spam\\n" * 1000."""
        myCont = 'spam\n' * self.NUM_TESTS
        myL = self.simpleLexWithContent(myCont)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(self.stringToTokens(myCont), myToks)

    def test_01(self):
        """TestPpLexerSimpleReplace: Test with "spam\\n" * 1000 and #define spam eggs."""
        myCont = '#define spam eggs\n'
        myCont += 'spam\n' * self.NUM_TESTS
        myL = self.simpleLexWithContent(myCont)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(
            self.stringToTokens('\n' + ('eggs\n' * self.NUM_TESTS)),
            myToks
            )

    def test_02(self):
        """TestPpLexerSimpleReplace: Test with "spam\\n" * 1000, #define spam eggs and #define eggs chips."""
        myCont = '#define spam eggs\n'
        myCont += '#define eggs chips\n'
        myCont += 'spam\n' * self.NUM_TESTS
        myL = self.simpleLexWithContent(myCont)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(
            [
            PpToken.PpToken('\n',   'whitespace'),
            PpToken.PpToken('\n',   'whitespace'),
            ] + self.stringToTokens('chips\n' * self.NUM_TESTS),
            myToks,
            )

    def test_03(self):
        """TestPpLexerSimpleReplace: Test with "spam\\n" * 1000, #define spam eggs, #define eggs chips and #define chips beans."""
        myCont = '#define spam eggs\n'
        myCont += '#define eggs chips\n'
        myCont += '#define chips beans\n'
        myCont += 'spam\n' * self.NUM_TESTS
        myL = self.simpleLexWithContent(myCont)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(
            [
            PpToken.PpToken('\n',   'whitespace'),
            PpToken.PpToken('\n',   'whitespace'),
            PpToken.PpToken('\n',   'whitespace'),
            ] + self.stringToTokens('beans\n' * self.NUM_TESTS),
            myToks,
            )

    def test_04(self):
        """TestPpLexerSimpleReplace: Test with "spam\\n" * 1000, #define spam eggs, #define eggs chips, #define chips beans and #define beans peas."""
        myCont = '#define spam eggs\n'
        myCont += '#define eggs chips\n'
        myCont += '#define chips beans\n'
        myCont += '#define beans peas\n'
        myCont += 'spam\n' * self.NUM_TESTS
        myL = self.simpleLexWithContent(myCont)
        myToks, myTime = self.runLex(myL)
        #logging.info('Rate: %6.1f tokens/second.' % (len(myToks) / myTime))
        self.assertEqual(
            [
            PpToken.PpToken('\n',   'whitespace'),
            PpToken.PpToken('\n',   'whitespace'),
            PpToken.PpToken('\n',   'whitespace'),
            PpToken.PpToken('\n',   'whitespace'),
            ] + self.stringToTokens('peas\n' * self.NUM_TESTS),
            myToks,
            )

class TestPpLexerRealCode(TestPpLexerPerfBase):
    """Test the time taken to process a 'real' code in test/PerfRealCode."""
    REAL_PATH = os.path.join('test', 'PerfRealCode')
    def test_00(self):
        """Test the time taken to process a 'real' code in test/PerfRealCode."""
        for aName in os.listdir(self.REAL_PATH):
            sys.stderr.write('\n')
            sys.stderr.write("Testing '%s' " % aName)
            myPath = os.path.join(self.REAL_PATH, aName)
            mySize = os.path.getsize(myPath)
            myLexer = PpLexer.PpLexer(
                     myPath,
                     CppIncludeStdOs([],[]),
                     preIncFiles=[],
                     diagnostic=None,
                     )
            myToks, myTime = self.runLex(myLexer)
            sys.stderr.write(' %0.1f kB/S ' % (mySize/(1024*myTime)))
            #pprint.pprint(self.retTokHistogram(tS))


class Special(TestPpLexerPerfBase):
    pass
    
class NullClass(TestPpLexerPerfBase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerSimpleText))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerSimpleNumber))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerSimpleReplace))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerReplaceGraph))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerRealCode))
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
