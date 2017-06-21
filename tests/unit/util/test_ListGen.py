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
import time
import logging

from cpip.util import ListGen
# Used to test Pre-processing token behaviour
from cpip.core import PpToken

######################
# Section: Unit tests.
######################
import unittest

class TestListGen(unittest.TestCase):
    """Tests the generator."""
    def testSimple(self):
        """ListAsGenerator: simple test of a list of integers."""
        myList = list(range(5))
        myG = next(ListGen.ListAsGenerator(myList))
        self.assertEqual(myList, [x for x in myG])
        self.assertRaises(StopIteration, next, myG)

    def testPassingGenerator(self):
        """ListAsGenerator: Passing a generator around yielding list of ints."""
        myList = list(range(6))
        myG = next(ListGen.ListAsGenerator(myList))
        result = []
        try:
            while 1:
                result.append(self._takeGenAndConsume(myG))
        except StopIteration:
            pass
        self.assertRaises(StopIteration, next, myG)
        self.assertEqual(myList, result)

    def _takeGenAndConsume(self, theGen):
        return next(theGen)

    def testTokenGenerator(self):
        """ListAsGenerator: list of PpToken(token, token_type)."""
        myList = [
                PpToken.PpToken('#',       'preprocessing-op-or-punc'),
                PpToken.PpToken('define',  'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('BAR',     'identifier'),
                PpToken.PpToken('\n',      'whitespace'),
            ]
        myG = next(ListGen.ListAsGenerator(myList))
        self.assertEqual(
                PpToken.PpToken('#',   'preprocessing-op-or-punc'),
                next(myG)
            )
        self.assertEqual(
                PpToken.PpToken('define',  'identifier'),
                next(myG)
            )
        self.assertEqual(
                PpToken.PpToken(' ',       'whitespace'),
                next(myG)
            )
        self.assertEqual(
                PpToken.PpToken('BAR',     'identifier'),
                next(myG)
            )
        self.assertEqual(
                PpToken.PpToken('\n',      'whitespace'),
                next(myG)
            )
        self.assertRaises(StopIteration, next, myG)

    def testContinuation(self):
        """ListAsGenerator: test of using a extra generator on a list of ints."""
        myList = list(range(5))
        myLetterList = [chr(x+ord('A')) for x in range(6)]
        myContGen = next(ListGen.ListAsGenerator(myLetterList))
        myG = next(ListGen.ListAsGenerator(myList, myContGen))
        self.assertEqual(
            [0, 1, 2, 3, 4, 'A', 'B', 'C', 'D', 'E', 'F'],
            [x for x in myG])
        self.assertRaises(StopIteration, next, myG)

class TestListGenUnget(unittest.TestCase):
    """Tests getting and ungetting a token."""

    def testAsimpleInit(self):
        """ListAsGenerator: simple list with list comprehension."""
        myObj = ListGen.ListAsGenerator(list(range(8)))
        myGen = next(myObj)
        myResult = [x for x in myGen]
        self.assertRaises(StopIteration, next, myGen)
        self.assertEqual(myResult, list(range(8)))

    def testIncGen(self):
        """ListAsGenerator: with incremental generation (inc. gen.)."""
        myObj = ListGen.ListAsGenerator(list(range(2)))
        myGen = next(myObj)
        # Iterate
        myVal = next(myGen)
        self.assertEqual(myVal, 0)
        myVal = next(myGen)
        self.assertEqual(myVal, 1)
        self.assertRaises(StopIteration, next, myGen)

    def testIncGenUnget(self):
        """ListAsGenerator: inc. gen. and single send()."""
        myObj = ListGen.ListAsGenerator(list(range(2)))
        myGen = next(myObj)
        # Iterate 0
        myVal = next(myGen)
        self.assertEqual(myVal, 0)
        # send() after next
        myGen.send(myVal)
        myVal = next(myGen)
        self.assertEqual(myVal, 0)
        myVal = next(myGen)
        self.assertEqual(myVal, 1)
        self.assertRaises(StopIteration, next, myGen)

    def testIncGenUngetAtStart(self):
        """ListAsGenerator: inc. gen. and single send() before next()."""
        myObj = ListGen.ListAsGenerator(list(range(2)))
        myGen = next(myObj)
        # Try sending before iterating
        self.assertRaises(TypeError, myGen.send, 42)
        myVal = next(myGen)
        self.assertEqual(myVal, 0)
        myVal = next(myGen)
        self.assertEqual(myVal, 1)
        self.assertRaises(StopIteration, next, myGen)

    def testIncGenUngetAtEnd(self):
        """ListAsGenerator: inc. gen. and single send() after last next()."""
        myObj = ListGen.ListAsGenerator(list(range(2)))
        myGen = next(myObj)
        # Iterate
        myVal = next(myGen)
        self.assertEqual(myVal, 0)
        myVal = next(myGen)
        self.assertEqual(myVal, 1)
        myGen.send(42)
        myVal = next(myGen)
        self.assertEqual(myVal, 42)
        self.assertRaises(StopIteration, next, myGen)

    def testIncGenUngetOnEmptyList(self):
        """ListAsGenerator: inc. gen. and send() where the initialy empty."""
        myObj = ListGen.ListAsGenerator([])
        myGen = next(myObj)
        # Try an insert
        self.assertRaises(TypeError, myGen.send, 127)
        self.assertRaises(StopIteration, next, myGen)

    def testIncGenUngetMultipleCallsAtStart(self):
        """ListAsGenerator: inc. gen. where pairs of send() cancel each other."""
        myObj = ListGen.ListAsGenerator(list(range(2)))
        myGen = next(myObj)
        # Iterate
        myVal = next(myGen)
        self.assertEqual(myVal, 0)
        self.assertEqual(None, myGen.send(42))
        self.assertEqual(42, myGen.send(84))
        # 84 is thrown away by the external loop of UnitGen.next()
        myVal = next(myGen)
        self.assertEqual(myVal, 1)
        self.assertRaises(StopIteration, next, myGen)

class TestContinuationGenUnget(unittest.TestCase):
    """Tests getting and ungetting a token."""

    def testContinuationSimpleInit(self):
        """ListAsGenerator: simple list with list comprehension and continuation."""
        myCont = ListGen.ListAsGenerator(list(range(4, 8)))
        myObj = ListGen.ListAsGenerator(list(range(4)), next(myCont))
        myGen = next(myObj)
        myResult = [x for x in myGen]
        self.assertRaises(StopIteration, next, myGen)
        self.assertEqual(myResult, list(range(8)))

    def testContinuationSendOnAlternate(self):
        """ListAsGenerator: Continuation with send on alternate yields."""
        myCont = ListGen.ListAsGenerator(list(range(4, 8)))
        myObj = ListGen.ListAsGenerator(list(range(4)), next(myCont))
        myGen = next(myObj)
        myResult = []
        for aVal in myGen:
            if aVal % 2 == 1:
                # Odd numbers
                myGen.send(aVal)
                myResult.append(next(myGen))
            else:
                myResult.append(aVal)
        self.assertRaises(StopIteration, next, myGen)
        self.assertEqual(myResult, list(range(8)))

    def testContinuationSendOnAlternateInList(self):
        """ListAsGenerator: Continuation with send on alternate yields in list part only."""
        myCont = ListGen.ListAsGenerator(list(range(4, 8)))
        myObj = ListGen.ListAsGenerator(list(range(4)), next(myCont))
        myGen = next(myObj)
        myResult = []
        for aVal in myGen:
            if aVal % 2 == 1 and not myObj.listIsEmpty:
                # Odd numbers
                myGen.send(aVal)
                myResult.append(next(myGen))
            else:
                myResult.append(aVal)
        self.assertRaises(StopIteration, next, myGen)
        self.assertEqual(myResult, list(range(8)))

    def testContinuationSendOnAlternateInGen(self):
        """ListAsGenerator: Continuation with send on alternate yields in continuation part only."""
        myCont = ListGen.ListAsGenerator(list(range(4, 8)))
        myObj = ListGen.ListAsGenerator(list(range(4)), next(myCont))
        myGen = next(myObj)
        myResult = []
        for aVal in myGen:
            if aVal % 2 == 1 and myObj.listIsEmpty:
                # Odd numbers
                myGen.send(aVal)
                myResult.append(next(myGen))
            else:
                myResult.append(aVal)
        self.assertRaises(StopIteration, next, myGen)
        self.assertEqual(myResult, list(range(8)))

    def testListIsEmpty_00(self):
        """ListAsGenerator: listIsEmpty flag is maintained [00]."""
        myCont = ListGen.ListAsGenerator(list('ABCDEFG'))
        myObj = ListGen.ListAsGenerator(list(range(4)), next(myCont))
        myGen = next(myObj)
        myResult = []
        #print
        for aVal in myGen:
            #print '%s  %s' % (myObj.listIsEmpty, aVal)
            myResult.append(aVal)
        self.assertRaises(StopIteration, next, myGen)
        self.assertEqual(myResult, list(range(4))+list('ABCDEFG'))

    def testListIsEmpty_01(self):
        """ListAsGenerator: listIsEmpty flag is maintained [01]."""
        myCont = ListGen.ListAsGenerator(list('ABCDEFG'))
        myObj = ListGen.ListAsGenerator(list(range(4)), next(myCont))
        myGen = next(myObj)
        myResult = []
        if not myObj.listIsEmpty:
            for aVal in myGen:
                myResult.append(aVal)
                if myObj.listIsEmpty:
                    break
        myRemainderResult = [x for x in myGen]
        self.assertRaises(StopIteration, next, myGen)
        self.assertEqual(myResult, list(range(4)))

    def testListIsEmpty_02(self):
        """ListAsGenerator: listIsEmpty flag is maintained [02]."""
        myCont = ListGen.ListAsGenerator(list('ABCDEFG'))
        myObj = ListGen.ListAsGenerator(list(range(4)), next(myCont))
        myGen = next(myObj)
        #print
        #print [x for x in myGen if myObj.listIsEmpty]
        #myResult = [x for x in myGen if myObj.listIsEmpty]
        if not myObj.listIsEmpty:
            for _aVal in myGen:
                if myObj.listIsEmpty:
                    break
        myResult = [x for x in myGen]
        self.assertRaises(StopIteration, next, myGen)
        self.assertEqual(myResult, list('ABCDEFG'))

    def testListIsEmpty_03(self):
        """ListAsGenerator: listIsEmpty flag is maintained [03]."""
        myCont = ListGen.ListAsGenerator(list('ABCDEFG'))
        myObj = ListGen.ListAsGenerator(list(range(4)), next(myCont))
        myGen = next(myObj)
        myResult = [x for x in myGen if myObj.listIsEmpty]
        #print
        #print myResult
        self.assertRaises(StopIteration, next, myGen)
        self.assertEqual(myResult, [3,] + list('ABCDEFG'))

    def testListIsEmpty_04(self):
        """ListAsGenerator: listIsEmpty flag is maintained [04]."""
        myCont = ListGen.ListAsGenerator(list('ABC'))
        myObj = ListGen.ListAsGenerator(list(range(3)), next(myCont))
        myGen = next(myObj)
        myResult = [x for x in myGen if not myObj.listIsEmpty]
        #print
        #print myResult
        self.assertRaises(StopIteration, next, myGen)
        self.assertEqual(myResult, [0, 1,])

class TestListIsEmpty_Special(unittest.TestCase):
    """Tests special case of testing list as empty."""

    def test_00(self):
        """TestListIsEmpty_Special: listIsEmpty flag is maintained [00]."""
        # INC == 1\n
        myGen = ListGen.ListAsGenerator([' ', '==', ' ', '1'])
        myObj = ListGen.ListAsGenerator(['INC',], next(myGen))
        resultS = []
        #print
        for aVal in next(myObj):
            #print 'aVal: %8s   %s' % ('"%s"' % aVal, myObj.listIsEmpty)
            resultS.append((aVal, myObj.listIsEmpty))
        #print resultS
        expResultS = [('INC', True), (' ', True), ('==', True), (' ', True), ('1', True)]
        self.assertEqual(resultS, expResultS)
        
    def test_01(self):
        """TestListIsEmpty_Special: listIsEmpty flag is maintained [01]."""
        # INC == 1\n
        myListGen = ListGen.ListAsGenerator([' ', '==', ' ', '1'])
        myObj     = ListGen.ListAsGenerator(['INC',], next(myListGen))
        myGen = next(myObj)
        #print
        resultS = []
        while not myObj.listIsEmpty:
            myVal = next(myGen)
            #print 'aVal: %8s   %s' % ('"%s"' % myVal, myObj.listIsEmpty)
            resultS.append((myVal, myObj.listIsEmpty))
        #print resultS
        expResultS = [('INC', True),]
        self.assertEqual(resultS, expResultS)
        #print '----'
        for aVal in myGen:
            #print 'aVal: %8s   %s' % ('"%s"' % aVal, myObj.listIsEmpty)
            resultS.append((aVal, myObj.listIsEmpty))
        #print resultS
        expResultS = [('INC', True), (' ', True), ('==', True), (' ', True), ('1', True)]
        self.assertEqual(resultS, expResultS)

    def test_02(self):
        """TestListIsEmpty_Special: listIsEmpty flag is maintained [02]."""
        # INC == 1\n
        myListGen = ListGen.ListAsGenerator([' ', '==', ' ', '1'])
        myObj     = ListGen.ListAsGenerator(['#', 'if', 'INC',], next(myListGen))
        myGen = next(myObj)
        #print
        resultS = []
        while not myObj.listIsEmpty:
            myVal = next(myGen)
            #print 'aVal: %8s   %s' % ('"%s"' % myVal, myObj.listIsEmpty)
            resultS.append((myVal, myObj.listIsEmpty))
        #print resultS
        expResultS = [('#', False), ('if', False), ('INC', True),]
        self.assertEqual(resultS, expResultS)
        #print '----'
        for aVal in myGen:
            #print 'aVal: %8s   %s' % ('"%s"' % aVal, myObj.listIsEmpty)
            resultS.append((aVal, myObj.listIsEmpty))
        #print resultS
        expResultS = [('#', False), ('if', False), ('INC', True), (' ', True), ('==', True), (' ', True), ('1', True)]
        self.assertEqual(resultS, expResultS)

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestListGen))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestListGenUnget))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestContinuationGenUnget))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestListIsEmpty_Special))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestListGen.py - A module that tests ListGen module.
Usage:
python TestListGen.py [-lh --help]

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
    print('TestListGen.py script version "%s", dated %s' % (__version__, __date__))
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
