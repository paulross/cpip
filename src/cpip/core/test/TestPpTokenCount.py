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

import unittest
import sys
import logging
import pprint

from cpip.core import PpToken, PpTokenCount
# Can use some test functionality
import TestPpDefine

#######################################
# Section: Unit tests
########################################
class TestPpTokenCount(TestPpDefine.TestPpDefine):
    """Test the PpTokenCount."""
    def setUp(self):
        self._ptc = PpTokenCount.PpTokenCount()

    def tearDown(self):
        pass
    
    def test_00(self):
        """TestPpTokenCount setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPpTokenCount increment."""
        myT = PpToken.PpToken('spam', 'identifier')
        self._ptc.inc(myT, True)
        self.assertEqual(1, self._ptc.totalAll)
        self.assertEqual(1, self._ptc.totalAllUnconditional)
        self.assertEqual(0, self._ptc.totalAllConditional)
        self.assertEqual(1, self._ptc.tokenCount('identifier', True))
        self.assertEqual(1, self._ptc.tokenCount('identifier', False))
        self.assertEqual(0, self._ptc.tokenCount('whitespace', True))
        self.assertEqual(1, self._ptc.tokenCountNonWs(True))
        self.assertEqual(1, self._ptc.tokenCountNonWs(False))

    def test_02(self):
        """TestPpTokenCount increment with more extensive code."""
        cntrAll = cntrUncond = 0
        for t in self.stringToTokens('#define SPAM 42\n'):
            self._ptc.inc(t, True)
            cntrAll += 1
            cntrUncond += 1
        for t in self.stringToTokens('#define EGGS SPAM\n'):
            self._ptc.inc(t, False)
            cntrAll += 1
        self.assertEqual(cntrAll, self._ptc.totalAll)
        self.assertEqual(cntrUncond, self._ptc.totalAllUnconditional)
        self.assertEqual(cntrAll-cntrUncond, self._ptc.totalAllConditional)
        self.assertEqual(5, self._ptc.tokenCount('identifier', True))
        self.assertEqual(2, self._ptc.tokenCount('identifier', False))
        self.assertEqual(6, self._ptc.tokenCount('whitespace', True))
        self.assertEqual(cntrAll-6, self._ptc.tokenCountNonWs(True))
        self.assertEqual(cntrUncond-3, self._ptc.tokenCountNonWs(False))

    def test_03(self):
        """TestPpTokenCount generator of results."""
        cntrAll = cntrUncond = 0
        for t in self.stringToTokens('#define SPAM 42\n'):
            self._ptc.inc(t, True)
            cntrAll += 1
            cntrUncond += 1
        for t in self.stringToTokens('#define EGGS SPAM\n'):
            self._ptc.inc(t, False)
            cntrAll += 1
        self.assertEqual(cntrAll, self._ptc.totalAll)
        self.assertEqual(cntrUncond, self._ptc.totalAllUnconditional)
        self.assertEqual(cntrAll-cntrUncond, self._ptc.totalAllConditional)
        myTypesCountsTrue = [x for x in self._ptc.tokenTypesAndCounts(True)]
        expTrue = [
            ('header-name',                 0),
            ('identifier',                  5),
            ('pp-number',                   1),
            ('character-literal',           0),
            ('string-literal',              0),
            ('preprocessing-op-or-punc',    2),
            ('non-whitespace',              0),
            ('whitespace',                  6),
            ('concat',                      0),
        ]
        #import pprint
        #print
        #pprint.pprint(myTypesCountsTrue)
        self.assertEqual(expTrue, myTypesCountsTrue)
        myTypesCountsFalse = [x for x in self._ptc.tokenTypesAndCounts(False)]
        #print
        #pprint.pprint(myTypesCountsFalse)
        expFalse = [
            ('header-name',                 0),
            ('identifier',                  2),
            ('pp-number',                   1),
            ('character-literal',           0),
            ('string-literal',              0),
            ('preprocessing-op-or-punc',    1),
            ('non-whitespace',              0),
            ('whitespace',                  3),
            ('concat',                      0),
        ]
        self.assertEqual(expFalse, myTypesCountsFalse)
        
class TestPpTokenCountMerge(TestPpDefine.TestPpDefine):
    """Test the PpTokenCount merging."""
    def setUp(self):
        self._ptc_1 = PpTokenCount.PpTokenCount()
        self._ptc_2 = PpTokenCount.PpTokenCount()

    def tearDown(self):
        pass
    
    def test_00(self):
        """TestPpTokenCount setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPpTokenCount __iadd__ simple"""
        #print
        self._ptc_1.inc(PpToken.PpToken('a', 'identifier'), True)
        self._ptc_2.inc(PpToken.PpToken('a', 'identifier'), True)
#===============================================================================
#        print '1 True:'
#        pprint.pprint([x for x in self._ptc_1.tokenTypesAndCounts(True, allPossibleTypes=False)])
#        print '1 False:'
#        pprint.pprint([x for x in self._ptc_1.tokenTypesAndCounts(False, allPossibleTypes=False)])
#        print
#        print '2 True:'
#        pprint.pprint([x for x in self._ptc_2.tokenTypesAndCounts(True, allPossibleTypes=False)])
#        print '2 False:'
#        pprint.pprint([x for x in self._ptc_2.tokenTypesAndCounts(False, allPossibleTypes=False)])
#===============================================================================
        #
        self._ptc_1 += self._ptc_2 
#===============================================================================
#        print
#        print 'Merged True:'
#        pprint.pprint([x for x in self._ptc_1.tokenTypesAndCounts(True, allPossibleTypes=False)])
#        print 'Merged False:'
#        pprint.pprint([x for x in self._ptc_1.tokenTypesAndCounts(False, allPossibleTypes=False)])
#===============================================================================
        self.assertEqual([x for x in self._ptc_1.tokenTypesAndCounts(True, allPossibleTypes=False)],
                         [('identifier', 2)])
        self.assertEqual([x for x in self._ptc_1.tokenTypesAndCounts(False, allPossibleTypes=False)],
                         [('identifier', 2)])
    
    def test_02(self):
        """TestPpTokenCount __iadd__ less simple."""
        #print
        cntrAll = cntrUncond = 0
        for t in self.stringToTokens('#define SPAM 42\n'):
            self._ptc_1.inc(t, True)
            self._ptc_2.inc(t, True)
            cntrAll += 1
            cntrUncond += 1
        for t in self.stringToTokens('#define EGGS SPAM\n'):
            self._ptc_1.inc(t, False)
            self._ptc_2.inc(t, False)
            cntrAll += 1
        self.assertEqual(cntrAll, self._ptc_1.totalAll)
        self.assertEqual(cntrUncond, self._ptc_1.totalAllUnconditional)
        self.assertEqual(cntrAll-cntrUncond, self._ptc_1.totalAllConditional)
        self.assertEqual(cntrAll, self._ptc_2.totalAll)
        self.assertEqual(cntrUncond, self._ptc_2.totalAllUnconditional)
        self.assertEqual(cntrAll-cntrUncond, self._ptc_2.totalAllConditional)
        myTypesCountsTrue_1 = [x for x in self._ptc_1.tokenTypesAndCounts(True)]
        expTrue = [
            ('header-name',                 0),
            ('identifier',                  5),
            ('pp-number',                   1),
            ('character-literal',           0),
            ('string-literal',              0),
            ('preprocessing-op-or-punc',    2),
            ('non-whitespace',              0),
            ('whitespace',                  6),
            ('concat',                      0),
        ]
        #pprint.pprint(myTypesCountsTrue_1)
        self.assertEqual(expTrue, myTypesCountsTrue_1)
        myTypesCountsFalse_1 = [x for x in self._ptc_1.tokenTypesAndCounts(False)]
        #print
        #pprint.pprint(myTypesCountsFalse)
        expFalse = [
            ('header-name',                 0),
            ('identifier',                  2),
            ('pp-number',                   1),
            ('character-literal',           0),
            ('string-literal',              0),
            ('preprocessing-op-or-punc',    1),
            ('non-whitespace',              0),
            ('whitespace',                  3),
            ('concat',                      0),
        ]
        self.assertEqual(expFalse, myTypesCountsFalse_1)
        # Now merge
        self._ptc_1 += self._ptc_2
        myTypesCountsTrue_1 = [x for x in self._ptc_1.tokenTypesAndCounts(True)]
        myTypesCountsFalse_1 = [x for x in self._ptc_1.tokenTypesAndCounts(False)]
        #print 'Merged:'
        #pprint.pprint(myTypesCountsTrue_1)
        expTrue= [
            ('header-name',                 0),
            ('identifier',                  10),
            ('pp-number',                   2),
            ('character-literal',           0),
            ('string-literal',              0),
            ('preprocessing-op-or-punc',    4),
            ('non-whitespace',              0),
            ('whitespace',                  12),
            ('concat',                      0),
            ]
        self.assertEqual(expTrue, myTypesCountsTrue_1)
        #print 'Merged:'
        #pprint.pprint(myTypesCountsFalse_1)
        expFalse = [
            ('header-name',                 0),
            ('identifier',                  4),
            ('pp-number',                   2),
            ('character-literal',           0),
            ('string-literal',              0),
            ('preprocessing-op-or-punc',    2),
            ('non-whitespace',              0),
            ('whitespace',                  6),
            ('concat',                      0),
        ]
        self.assertEqual(expFalse, myTypesCountsFalse_1)
        
class TestPpTokenCountStack(TestPpDefine.TestPpDefine):
    """Test the PpTokenCount."""
    def setUp(self):
        self._ptcs = PpTokenCount.PpTokenCountStack()

    def tearDown(self):
        self.assertEqual(0, len(self._ptcs))
    
    def test_00(self):
        """TestPpTokenCountStack setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestPpTokenCountStack push(), pop() and close()."""
        self._ptcs.push()
        self._ptcs.pop()
        self._ptcs.close()
    
    def test_02(self):
        """TestPpTokenCountStack push(), access counter, pop(), access counter and close()."""
        self._ptcs.push()
        self._ptcs.counter()
        cntrAll = cntrUncond = 0
        for t in self.stringToTokens('#define SPAM 42\n'):
            self._ptcs.counter().inc(t, True)
            cntrAll += 1
            cntrUncond += 1
        for t in self.stringToTokens('#define EGGS SPAM\n'):
            self._ptcs.counter().inc(t, False)
            cntrAll += 1
        self.assertEqual(cntrAll,               self._ptcs.counter().totalAll)
        self.assertEqual(cntrUncond,            self._ptcs.counter().totalAllUnconditional)
        self.assertEqual(cntrAll-cntrUncond,    self._ptcs.counter().totalAllConditional)
        self.assertEqual(5,                     self._ptcs.counter().tokenCount('identifier', True))
        self.assertEqual(2,                     self._ptcs.counter().tokenCount('identifier', False))
        self.assertEqual(6,                     self._ptcs.counter().tokenCount('whitespace', True))
        self.assertEqual(cntrAll-6,             self._ptcs.counter().tokenCountNonWs(True))
        self.assertEqual(cntrUncond-3,          self._ptcs.counter().tokenCountNonWs(False))
        myCntr = self._ptcs.pop()
        self.assertEqual(cntrAll,               myCntr.totalAll)
        self.assertEqual(cntrUncond,            myCntr.totalAllUnconditional)
        self.assertEqual(cntrAll-cntrUncond,    myCntr.totalAllConditional)
        self.assertEqual(5,                     myCntr.tokenCount('identifier', True))
        self.assertEqual(2,                     myCntr.tokenCount('identifier', False))
        self.assertEqual(6,                     myCntr.tokenCount('whitespace', True))
        self.assertEqual(cntrAll-6,             myCntr.tokenCountNonWs(True))
        self.assertEqual(cntrUncond-3,          myCntr.tokenCountNonWs(False))
        self._ptcs.close()
    
    def test_03(self):
        """TestPpTokenCountStack push(), access counter, pop(), access counter and close() - two counters."""
        self._ptcs.push()
        self._ptcs.push()
        cntrAll = cntrUncond = 0
        for t in self.stringToTokens('#define SPAM 42\n'):
            self._ptcs.counter().inc(t, True)
            cntrAll += 1
            cntrUncond += 1
        for t in self.stringToTokens('#define EGGS SPAM\n'):
            self._ptcs.counter().inc(t, False)
            cntrAll += 1
        self.assertEqual(cntrAll,               self._ptcs.counter().totalAll)
        self.assertEqual(cntrUncond,            self._ptcs.counter().totalAllUnconditional)
        self.assertEqual(cntrAll-cntrUncond,    self._ptcs.counter().totalAllConditional)
        self.assertEqual(5,                     self._ptcs.counter().tokenCount('identifier', True))
        self.assertEqual(2,                     self._ptcs.counter().tokenCount('identifier', False))
        self.assertEqual(6,                     self._ptcs.counter().tokenCount('whitespace', True))
        self.assertEqual(cntrAll-6,             self._ptcs.counter().tokenCountNonWs(True))
        self.assertEqual(cntrUncond-3,          self._ptcs.counter().tokenCountNonWs(False))
        myCntr = self._ptcs.pop()
        self.assertEqual(cntrAll,               myCntr.totalAll)
        self.assertEqual(cntrUncond,            myCntr.totalAllUnconditional)
        self.assertEqual(cntrAll-cntrUncond,    myCntr.totalAllConditional)
        self.assertEqual(5,                     myCntr.tokenCount('identifier', True))
        self.assertEqual(2,                     myCntr.tokenCount('identifier', False))
        self.assertEqual(6,                     myCntr.tokenCount('whitespace', True))
        self.assertEqual(cntrAll-6,             myCntr.tokenCountNonWs(True))
        self.assertEqual(cntrUncond-3,          myCntr.tokenCountNonWs(False))
        self._ptcs.pop()
        self._ptcs.close()
    
    def test_10(self):
        """TestPpTokenCountStack pop() raises on counter() on empty stack."""
        self.assertRaises(PpTokenCount.ExceptionPpTokenCountStack, self._ptcs.counter)

    def test_11(self):
        """TestPpTokenCountStack pop() raises on empty stack."""
        self.assertRaises(PpTokenCount.ExceptionPpTokenCountStack, self._ptcs.pop)

    def test_12(self):
        """TestPpTokenCountStack pop() raises on close() on non-empty stack."""
        self._ptcs.push()
        self.assertRaises(PpTokenCount.ExceptionPpTokenCountStack, self._ptcs.close)
        self._ptcs.pop()
        self._ptcs.close()

def unitTest(theVerbosity=2):
#    suite = unittest.TestLoader().loadTestsFromTestCase(TestPpTokenCount)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPpTokenCountMerge)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokenCountStack))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestPpTokenCount.py - A module that tests the PpTokenCOunt module.
Usage:
python TestPpTokenCount.py [-lh --help]

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
    print('TestPpTokenCount.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
    print(__rights__)
    print()
    import getopt
    import time
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


