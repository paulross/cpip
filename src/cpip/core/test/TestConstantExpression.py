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

"""Handles the Python interpretation of a constant-expression.
See ISO/IEC 14882:1998(E) TODO.

paulross@L071183 /cygdrive/d/wip/small_projects/Preprocess2.0/src/python
$ python c:/Python26/Lib/site-packages/coverage.py -x test/TestConstantExpression.py
TestConstantExpression.py script version "0.1.4", dated 2009-11-10


ConstantExpression - simple construction. ... ok
ConstantExpression - Conditional expression regular expression. ... ok
ConstantExpression - Conditional expression regular expression - no match. ... ok
ConstantExpression - Conditional expression evaluation: ((1)<(2)) ? (1) : (2)\n ... ok
ConstantExpression - Conditional expression evaluation: ((1)>(2)) ? (1) : (2)\n ... ok
ConstantExpression - Conditional expression evaluation: ((1)==(2-1)) ? (1) : (2)\n ... ok
ConstantExpression - Conditional expression evaluation: fails on ((1U)==(2L)) ? (1) : (2)\n ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.094s

OK
CPU time =    0.105 (S)
Bye, bye!

paulross@L071183 /cygdrive/d/wip/small_projects/Preprocess2.0/src/python
$ python c:/Python26/Lib/site-packages/coverage.py -r -m ConstantExpression.py
Name                 Stmts   Exec  Cover   Missing
--------------------------------------------------
ConstantExpression      51     41    80%   52, 63-72, 78, 85, 103

"""

import sys
import os
import time
import logging

from cpip.core import ConstantExpression, PpTokeniser

######################
# Section: Unit tests.
######################
import unittest

class TestConstantExpression(unittest.TestCase):
    """Tests the class ConstantExpression."""

    def testCtor_00(self):
        """ConstantExpression - simple construction."""
        ConstantExpression.ConstantExpression([])

    def testCtor_01(self):
        """ConstantExpression - construction with "1 < 2"."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('1 < 2')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual("1 < 2", str(myObj))

class TestConstantExpressionEvaluateSimple(unittest.TestCase):
    """Tests simple evaluation."""

    def testEval_00(self):
        """ConstantExpression - evaluation of "1 < 2"."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('1 < 2')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(1, myObj.evaluate())

    def testEval_01(self):
        """ISO/IEC 9899:1999 (E) 6.10.1-3 - evaluation of "A == B" is true when neither defined."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('A == B')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(1, myObj.evaluate())

    def testEval_02(self):
        """ISO/IEC 9899:1999 (E) 6.10.1-3 - evaluation of "A == 0" is true when A not defined."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('A == 0')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(1, myObj.evaluate())

    def testEval_03(self):
        """ISO/IEC 9899:1999 (E) 6.10.1-3 - evaluation of "A == 1" is false when A not defined."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('A == 1')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(0, myObj.evaluate())

    def testEval_Fail_00(self):
        """ConstantExpression - evaluation raises for '"x" < ==' as eval fails."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('"x" < ==')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        #self.assertEqual(1, myObj.evaluate())
        self.assertRaises(
            ConstantExpression.ExceptionEvaluateExpression,
            myObj.evaluate
            )

class TestConstantExpressionEvaluateWordReplace(unittest.TestCase):
    """Tests evaluation of things like &&, ||, true, False."""

    def testEval_Word_00(self):
        """ConstantExpression - evaluation of "1 && 1"."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('1 && 1')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(1, myObj.evaluate())

    def testEval_Word_01(self):
        """ConstantExpression - evaluation of "1 && 0"."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('1 && 0')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(0, myObj.evaluate())

    def testEval_Word_02(self):
        """ConstantExpression - evaluation of "1 || 0"."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('1 || 0')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(1, myObj.evaluate())

    def testEval_Word_03(self):
        """ConstantExpression - evaluation of "0 || 0"."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('0 || 0')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(0, myObj.evaluate())

    def testEval_Word_04(self):
        """ConstantExpression - evaluation of "true"."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('true')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(1, myObj.evaluate())

    def testEval_Word_05(self):
        """ConstantExpression - evaluation of "false"."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('false')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(0, myObj.evaluate())

    def testEval_Word_06(self):
        """ConstantExpression - evaluation of "(1 && 1) && ((0 > 0 ) || 1) && (true || false)"."""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('(1 && 1) && ((0 > 0 ) || 1) && (true || false)')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(1, myObj.evaluate())

class TestConstantExpressionRegex(unittest.TestCase):
    """Tests the regular expressions in class ConstantExpression."""

    def testConditionalExpressionRegex(self):
        """ConstantExpression - Conditional expression regular expression."""
        myObj = ConstantExpression.ConstantExpression([])
        m = myObj.RE_CONDITIONAL_EXPRESSION.match('(a) > (b) ? (a) : (b)')
        self.assertNotEqual(None, m)
        self.assertEqual(3, len(m.groups()))
        self.assertEqual('(a) > (b) ', m.group(1))
        self.assertEqual(' (a) ', m.group(2))
        self.assertEqual(' (b)', m.group(3))

    def testTerneryRegexNoMatch(self):
        """ConstantExpression - Conditional expression regular expression - no match."""
        myObj = ConstantExpression.ConstantExpression([])
        m = myObj.RE_CONDITIONAL_EXPRESSION.match('(a) > (b) ? (a)  (b)')
        self.assertEqual(None, m)

class TestConstantExpressionConditionalExpression(unittest.TestCase):
    """Tests the regular expressions in class ConstantExpression."""

    def testConditionalExpression_00(self):
        """ConstantExpression - Conditional expression evaluation: ((1)<(2)) ? (1) : (2)\\n"""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('((1)<(2)) ? (1) : (2)\n')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(1, myObj.evaluate())

    def testConditionalExpression_01(self):
        """ConstantExpression - Conditional expression evaluation: ((1)>(2)) ? (1) : (2)\\n"""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('((1)>(2)) ? (1) : (2)\n')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(2, myObj.evaluate())

    def testConditionalExpression_02(self):
        """ConstantExpression - Conditional expression evaluation: ((1)==(2-1)) ? (1) : (2)\\n"""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('((1)==(2-1)) ? (1) : (2)\n')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        self.assertEqual(1, myObj.evaluate())

    def testConditionalExpression_50(self):
        """ConstantExpression - Conditional expression evaluation: raises on ((1U)==(2L)) ? (1) : (2)\\n"""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('((1U)==(2L)) ? (1) : (2)\n')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        print()
        print(myToksTypes)
        print(myObj.evaluate())
        self.assertEqual(2, myObj.evaluate())
#        self.assertRaises(ConstantExpression.ExceptionConditionalExpression, myObj.evaluate)

class TestConstantExpressionLinux(unittest.TestCase):
    """Tests various issues discovered in building the Linux kernel."""
    def test_00(self):
        """TestConstantExpressionLinux.test_00(): 1000000UL * 1000"""
        myCpp = PpTokeniser.PpTokeniser()
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs('1000000UL * 1000\n')]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
#        print()
#        print(myObj.evaluate())
        self.assertEqual(1000000000, myObj.evaluate())

    def test_01(self):
        """TestConstantExpressionLinux.test_01(): jiffies.h expansion of ((((NSEC_PER_SEC << 2) / TICK_NSEC) << (SEC_JIFFIE_SC - 2)) & 0x80000000)"""
        myCpp = PpTokeniser.PpTokeniser()
        myStr = """(((0 + 100/2) / 100))
"""
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs(myStr)]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        print()
        print((myObj.evaluate()))
        self.assertEqual(0, myObj.evaluate())

    def test_02(self):
        """TestConstantExpressionLinux.test_02(): jiffies.h expansion of ((((NSEC_PER_SEC << 2) / TICK_NSEC) << (SEC_JIFFIE_SC - 2)) & 0x80000000)"""
        myCpp = PpTokeniser.PpTokeniser()
        myStr = """((0) / (((0 + 100/2) / 100)))
"""
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs(myStr)]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        print()
        print((myObj.evaluate()))
        self.assertEqual(1000000000, myObj.evaluate())

    def test_09(self):
        """TestConstantExpressionLinux.test_09(): jiffies.h expansion of ((((NSEC_PER_SEC << 2) / TICK_NSEC) << (SEC_JIFFIE_SC - 2)) & 0x80000000)"""
        myCpp = PpTokeniser.PpTokeniser()
        myStr = """(((0) / (((0 + 100/2) / 100))) << (8))
"""
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs(myStr)]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        print()
        print((myObj.evaluate()))
        self.assertEqual(1000000000, myObj.evaluate())

    def test_10(self):
        """TestConstantExpressionLinux.test_10(): jiffies.h expansion of ((((NSEC_PER_SEC << 2) / TICK_NSEC) << (SEC_JIFFIE_SC - 2)) & 0x80000000)"""
        myCpp = PpTokeniser.PpTokeniser()
        myStr = """((((1 << 2) / (( (((1000000UL * 1000) / ((( (((0) / (((0 + 100/2) / 100))) << (8)) + ((((0) % (((0 + 100/2) / 100))) << (8)) + (((0 + 100/2) / 100)) / 2) / (((0 + 100/2) / 100)))))) << (8)) + ((((1000000UL * 1000) % ((( (((0) / (((0 + 100/2) / 100))) << (8)) + ((((0) % (((0 + 100/2) / 100))) << (8)) + (((0 + 100/2) / 100)) / 2) / (((0 + 100/2) / 100)))))) << (8)) + ((( (((0) / (((0 + 100/2) / 100))) << (8)) + ((((0) % (((0 + 100/2) / 100))) << (8)) + (((0 + 100/2) / 100)) / 2) / (((0 + 100/2) / 100))))) / 2) / ((( (((0) / (((0 + 100/2) / 100))) << (8)) + ((((0) % (((0 + 100/2) / 100))) << (8)) + (((0 + 100/2) / 100)) / 2) / (((0 + 100/2) / 100)))))))) << ((31 - 7) - 2)) & 0x80000000)
"""
        myToksTypes = [t for t in myCpp.genLexPptokenAndSeqWs(myStr)]
        myObj = ConstantExpression.ConstantExpression(myToksTypes)
        print()
        print((myObj.evaluate()))
        self.assertEqual(1000000000, myObj.evaluate())

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConstantExpression)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConstantExpressionEvaluateSimple))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConstantExpressionEvaluateWordReplace))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConstantExpressionRegex))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConstantExpressionConditionalExpression))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConstantExpressionLinux))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print(\
"""TestConstantExpression.py - A module that tests PpToken module.
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
    print(('TestConstantExpression.py script version "%s", dated %s' % (__version__, __date__)))
    print(('Author: %s' % __author__))
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
    print(('CPU time = %8.3f (S)' % clkExec))
    print('Bye, bye!')

if __name__ == "__main__":
    main()
