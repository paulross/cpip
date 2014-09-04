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

import sys
import os
import unittest
import time
import logging
import random
#import pprint

from cpip.util import OaS

#######################################
# Section: Unit tests
########################################
class TestIndexMatch(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """OaS.indexMatch() - setUp() and tearDown()."""
        pass

    def test_01(self):
        """OaS.indexMatch() - empty list returns -1"""
        self.assertEqual(-1, OaS.indexMatch([], 23))

    def test_02(self):
        """OaS.indexMatch() - missing returns -1"""
        self.assertEqual(-1, OaS.indexMatch(list(range(4)), 23))
        self.assertEqual(-1, OaS.indexMatch(list(range(4)), -1))
        self.assertEqual(-1, OaS.indexMatch(list(range(4)), 4))

    def test_03_01(self):
        """OaS.indexMatch() - correct match on range(1)"""
        self.assertEqual(-1, OaS.indexMatch(list(range(1)), -1))
        self.assertEqual(0, OaS.indexMatch(list(range(1)), 0))
        self.assertEqual(-1, OaS.indexMatch(list(range(1)), 1))

    def test_03_02(self):
        """OaS.indexMatch() - correct match on range(2)"""
        self.assertEqual(-1, OaS.indexMatch(list(range(2)), -1))
        self.assertEqual(0, OaS.indexMatch(list(range(2)), 0))
        self.assertEqual(1, OaS.indexMatch(list(range(2)), 1))
        self.assertEqual(-1, OaS.indexMatch(list(range(2)), 2))

    def test_03_03(self):
        """OaS.indexMatch() - correct match on range(3)"""
        self.assertEqual(-1, OaS.indexMatch(list(range(3)), -1))
        self.assertEqual(0, OaS.indexMatch(list(range(3)), 0))
        self.assertEqual(1, OaS.indexMatch(list(range(3)), 1))
        self.assertEqual(2, OaS.indexMatch(list(range(3)), 2))
        self.assertEqual(-1, OaS.indexMatch(list(range(3)), 3))

    def test_03_04(self):
        """OaS.indexMatch() - correct match on range(4)"""
        self.assertEqual(0, OaS.indexMatch(list(range(4)), 0))
        self.assertEqual(1, OaS.indexMatch(list(range(4)), 1))
        self.assertEqual(2, OaS.indexMatch(list(range(4)), 2))
        self.assertEqual(3, OaS.indexMatch(list(range(4)), 3))

    def test_04(self):
        """OaS.indexMatch() - 100 random ranges -10,000 to 10,000"""
        random.seed()
        for i in range(1):
            start = random.randint(-10000, 10000)
            end = random.randint(-10000, 10000)
            if start > end:
                start, end = end, start
            myR = list(range(start, end))
            self.assertEqual(-1, OaS.indexMatch(myR, start-1))
            for j, aVal in enumerate(myR):
                self.assertEqual(j, OaS.indexMatch(myR, aVal))
            self.assertEqual(-1, OaS.indexMatch(myR, end))
            
class TestLowerBound(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """OaS.indexLB() - setUp() and tearDown()."""
        pass

    def test_00_01(self):
        """OaS.indexLB() - under range returns -1"""
        self.assertEqual(-1, OaS.indexLB([], 23))
        self.assertEqual(-1, OaS.indexLB([23,], 22))

    def test_01(self):
        """OaS.indexLB() - within list range(1)."""
        self.assertEqual(-1, OaS.indexLB(list(range(1)), -10))
        self.assertEqual(0, OaS.indexLB(list(range(1)), 0))
        self.assertEqual(0, OaS.indexLB(list(range(1)), 1))
        self.assertEqual(0, OaS.indexLB(list(range(1)), 2))
        self.assertEqual(0, OaS.indexLB(list(range(1)), 3))

    def test_02(self):
        """OaS.indexLB() - within list range(2)."""
        self.assertEqual(-1, OaS.indexLB(list(range(2)), -10))
        self.assertEqual(0, OaS.indexLB(list(range(2)), 0))
        self.assertEqual(1, OaS.indexLB(list(range(2)), 1))
        self.assertEqual(1, OaS.indexLB(list(range(2)), 2))
        self.assertEqual(1, OaS.indexLB(list(range(2)), 3))

    def test_03(self):
        """OaS.indexLB() - within list range(3)."""
        self.assertEqual(-1, OaS.indexLB(list(range(3)), -10))
        self.assertEqual(0, OaS.indexLB(list(range(3)), 0))
        self.assertEqual(1, OaS.indexLB(list(range(3)), 1))
        self.assertEqual(2, OaS.indexLB(list(range(3)), 2))
        self.assertEqual(2, OaS.indexLB(list(range(3)), 3))

    def test_04(self):
        """OaS.indexLB() - within list range(4)."""
        self.assertEqual(0, OaS.indexLB(list(range(4)), 0))
        self.assertEqual(1, OaS.indexLB(list(range(4)), 1))
        self.assertEqual(2, OaS.indexLB(list(range(4)), 2))
        self.assertEqual(3, OaS.indexLB(list(range(4)), 3))
        self.assertEqual(0, OaS.indexLB([0], 23))

    def test_08_02(self):
        """OaS.indexLB() - within list range(8, 2)."""
        self.assertEqual(0, OaS.indexLB(list(range(0, 8, 2)), 0))
        self.assertEqual(0, OaS.indexLB(list(range(0, 8, 2)), 1))
        self.assertEqual(1, OaS.indexLB(list(range(0, 8, 2)), 2))
        self.assertEqual(1, OaS.indexLB(list(range(0, 8, 2)), 3))

    def test_random(self):
        """OaS.indexLB() - random sets of integers."""
        CYCLES = 8
        SIZE = 1024
        LB = -1 * 2 << 16
        UB = 2 << 16
        TESTS = 1024
        random.seed()
        for cyc in range(CYCLES):
            s = set()
            for r in range(SIZE):
                s.add(random.randint(LB, UB))
            l = list(s)
            l.sort()
            # Test exact membership
            for i, v in enumerate(l):
                self.assertEqual(i, OaS.indexLB(l, v))
            # Test lower bound
            for t in range(TESTS):
                v = random.randint(LB, UB)
                result = OaS.indexLB(l, v)
                if result != -1:
                    self.assertTrue(l[result] <= v)
                    
class TestUpperBound(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00(self):
        """OaS.indexUB() - setUp() and tearDown()."""
        pass

    def test_00_01(self):
        """OaS.indexUB() - under range returns -1"""
        self.assertEqual(-1, OaS.indexUB([], 23))
        self.assertEqual(-1, OaS.indexUB([23,], 24))

    def test_01(self):
        """OaS.indexUB() - within list range(1)."""
        self.assertEqual(0, OaS.indexUB(list(range(1)), -10))
        self.assertEqual(0, OaS.indexUB(list(range(1)), 0))
        self.assertEqual(-1, OaS.indexUB(list(range(1)), 1))
        self.assertEqual(-1, OaS.indexUB(list(range(1)), 2))
        self.assertEqual(-1, OaS.indexUB(list(range(1)), 3))

    def test_02(self):
        """OaS.indexUB() - within list range(2)."""
        self.assertEqual(0, OaS.indexUB(list(range(2)), -10))
        self.assertEqual(0, OaS.indexUB(list(range(2)), 0))
        self.assertEqual(1, OaS.indexUB(list(range(2)), 1))
        self.assertEqual(-1, OaS.indexUB(list(range(2)), 2))
        self.assertEqual(-1, OaS.indexUB(list(range(2)), 3))

    def test_03(self):
        """OaS.indexUB() - within list range(3)."""
        self.assertEqual(0, OaS.indexUB(list(range(3)), -10))
        self.assertEqual(0, OaS.indexUB(list(range(3)), 0))
        self.assertEqual(1, OaS.indexUB(list(range(3)), 1))
        self.assertEqual(2, OaS.indexUB(list(range(3)), 2))
        self.assertEqual(-1, OaS.indexUB(list(range(3)), 3))

    def test_04(self):
        """OaS.indexUB() - within list range(4)."""
        self.assertEqual(0, OaS.indexUB(list(range(4)), 0))
        self.assertEqual(1, OaS.indexUB(list(range(4)), 1))
        self.assertEqual(2, OaS.indexUB(list(range(4)), 2))
        self.assertEqual(3, OaS.indexUB(list(range(4)), 3))

    def test_08_02(self):
        """OaS.indexUB() - within list range(8, 2)."""
        self.assertEqual(0, OaS.indexUB(list(range(0, 8, 2)), 0))
        self.assertEqual(1, OaS.indexUB(list(range(0, 8, 2)), 1))
        
    def test_10(self):
        """OaS.indexUB() - Special tests (1)."""
        myL = [62, 99, 291, 452, 621, 726, 739, 850, 859, 959]
        self.assertEqual(8, OaS.indexLB(myL, 936))
        self.assertEqual(9, OaS.indexUB(myL, 936))
        self.assertEqual(2, OaS.indexLB(myL, 380))
        self.assertEqual(3, OaS.indexUB(myL, 380))
        self.assertEqual(2, OaS.indexLB(myL, 373))
        self.assertEqual(3, OaS.indexUB(myL, 373))
        self.assertEqual(2, OaS.indexLB(myL, 450))
        self.assertEqual(3, OaS.indexUB(myL, 450))

    def test_11(self):
        """OaS.indexUB() - Special tests (2)."""
        myL = [1618, 2203, 12713, 15130, 47532, 48695, 68099, 79859, 82937, 92404, 110497, 125270]
        self.assertEqual(10, OaS.indexLB(myL, 116860))
        self.assertEqual(11, OaS.indexUB(myL, 116860))
        self.assertEqual(8, OaS.indexLB(myL, 90531))
        self.assertEqual(9, OaS.indexUB(myL, 90531))
#88156
#88275
#84194
#84204
#115377
#83339
#91406
#86696
#123891
#84575
#114382

    def test_random(self):
        """OaS.indexUB() - random sets of integers."""
        CYCLES = 8
        SIZE = 1024
        LB = -1 * 2 << 16
        UB = 2 << 16
        TESTS = 1024
        random.seed()
        for cyc in range(CYCLES):
            s = set()
            for r in range(SIZE):
                s.add(random.randint(LB, UB))
            l = list(s)
            l.sort()
            # Test exact membership
            for i, v in enumerate(l):
                self.assertEqual(i, OaS.indexUB(l, v))
            # Test lower bound
            for t in range(TESTS):
                #print t
                v = random.randint(LB, UB)
                result = OaS.indexUB(l, v)
                if result != -1:
                    #if l[result] < v:
                    #    print 'result: %d l[result]: %d < v: %d l: %s' % (result, l[result], v, l)
                    #assert(type(l[result]) == type(1))
                    #assert(type(v) == type(1))
                    #assert(l[result] >= v), 'l[result]: %d >= v: %d' % (l[result], v)
                    self.assertTrue(l[result] >= v)

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    """Execute unit tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIndexMatch))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLowerBound))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUpperBound))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

#################
# End: Unit tests
#################

def usage():
    """Send the help to stdout."""
    print("""TestBufGen.py - A module that tests PpToken module.
Usage:
python TestBufGen.py [-lh --help]

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
    print('TestBufGen.py script version "%s", dated %s' % (__version__, __date__))
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
