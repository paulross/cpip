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
#import pprint

from cpip.util import BufGen

#######################################
# Section: Unit tests
########################################
class StrGen(object):
    def __init__(self, theStr):
        self._str = theStr
        
    def __next__(self):
        i = 0
        while i < len(self._str):
            yield self._str[i]
            i += 1

class TestBufGen(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_00(self):
        """Test simple string buffer generation."""
        myStrGen = StrGen('abc')
        myBg = BufGen.BufGen(next(myStrGen))
        myGen = myBg.gen()
        for a in myGen:
            pass
            #print a
        self.assertEquals(3, myBg.lenBuf)
        self.assertEquals("BufGen: ['a', 'b', 'c']", str(myBg))
        self.assertEquals(['a', 'b', 'c'], myBg.slice(3))
        self.assertEquals(0, myBg.lenBuf)
        self.assertEquals('BufGen: []', str(myBg))

    def test_01(self):
        """Tests exceeding available slice size."""
        myStrGen = StrGen('abc')
        myBg = BufGen.BufGen(next(myStrGen))
        for a in myBg.gen():
            pass
            #print a
        self.assertEquals(3, myBg.lenBuf)
        self.assertRaises(BufGen.ExceptionBufGen, myBg.slice, 99)
        self.assertEquals(3, myBg.lenBuf)

    def tearDown(self):
        pass

class TestBufGenReplace(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_00(self):
        """TestBufGenReplace: Test simple string replacement "aaabbbccc" - > "aaaBBBccc"."""
        myStrGen = StrGen('aaabbbccc')
        myBg = BufGen.BufGen(next(myStrGen))
        myGen = myBg.gen()
        for a in myGen:
            pass
            #print a
        self.assertEquals(9, myBg.lenBuf)
        # Now replace 'bbb' with 'BBB'
        myBg.replace(3, 3, ['B', 'B', 'B'])
        # Inspect
        self.assertEquals(9, myBg.lenBuf)
        self.assertEquals(['a', 'a', 'a'], myBg.slice(3))
        self.assertEquals(6, myBg.lenBuf)
        self.assertEquals(['B', 'B', 'B'], myBg.slice(3))
        self.assertEquals(3, myBg.lenBuf)
        self.assertEquals(['c', 'c', 'c'], myBg.slice(3))
        self.assertEquals(0, myBg.lenBuf)

    def test_01(self):
        """TestBufGenReplace: Test simple string replacement "aaabbbccc" - > "aaaccc"."""
        myStrGen = StrGen('aaabbbccc')
        myBg = BufGen.BufGen(next(myStrGen))
        myGen = myBg.gen()
        for a in myGen:
            pass
            #print a
        self.assertEquals(9, myBg.lenBuf)
        # Now replace 'bbb' with nothing
        myBg.replace(3, 3, [])
        # Inspect
        self.assertEquals(6, myBg.lenBuf)
        self.assertEquals(['a', 'a', 'a'], myBg.slice(3))
        self.assertEquals(3, myBg.lenBuf)
        self.assertEquals(['c', 'c', 'c'], myBg.slice(3))
        self.assertEquals(0, myBg.lenBuf)

    def test_02(self):
        """TestBufGenReplace: Test simple string replacement "aaaccc" - > "aaaBBBccc"."""
        myStrGen = StrGen('aaaccc')
        myBg = BufGen.BufGen(next(myStrGen))
        myGen = myBg.gen()
        for a in myGen:
            pass
            #print a
        self.assertEquals(6, myBg.lenBuf)
        # Now insert 'BBB'
        myBg.replace(3, 0, ['B', 'B', 'B'])
        # Inspect
        self.assertEquals(9, myBg.lenBuf)
        self.assertEquals(['a', 'a', 'a'], myBg.slice(3))
        self.assertEquals(6, myBg.lenBuf)
        self.assertEquals(['B', 'B', 'B'], myBg.slice(3))
        self.assertEquals(3, myBg.lenBuf)
        self.assertEquals(['c', 'c', 'c'], myBg.slice(3))
        self.assertEquals(0, myBg.lenBuf)

    def test_03(self):
        """TestBufGenReplace: Test simple string replacement exceeds limits."""
        myStrGen = StrGen('aaaccc')
        myBg = BufGen.BufGen(next(myStrGen))
        myGen = myBg.gen()
        for a in myGen:
            pass
            #print a
        self.assertEquals(6, myBg.lenBuf)
        self.assertRaises(BufGen.ExceptionBufGen, myBg.replace, -1, 0, [])
        self.assertRaises(BufGen.ExceptionBufGen, myBg.replace, 0, -1, [])
        self.assertRaises(BufGen.ExceptionBufGen, myBg.replace, 6, 0, [])
        self.assertRaises(BufGen.ExceptionBufGen, myBg.replace, 5, 2, [])

class TestBufGenIndex(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_00(self):
        """Test simple string buffer indexing."""
        myStrGen = StrGen('abc')
        myBg = BufGen.BufGen(next(myStrGen))
        # Index into it provoking the generator
        self.assertEquals('a', myBg[0])
        self.assertEquals("BufGen: ['a']", str(myBg))
        self.assertEquals(1, myBg.lenBuf)
        self.assertEquals('b', myBg[1])
        self.assertEquals("BufGen: ['a', 'b']", str(myBg))
        self.assertEquals(2, myBg.lenBuf)
        self.assertEquals('c', myBg[2])
        self.assertEquals("BufGen: ['a', 'b', 'c']", str(myBg))
        self.assertEquals(3, myBg.lenBuf)

    def test_01(self):
        """Test string buffer indexing out of range."""
        myStrGen = StrGen('abc')
        myBg = BufGen.BufGen(next(myStrGen))
        try:
            myBg[-1]
            self.fail('IndexError not raised.')
        except IndexError:
            pass
        try:
            myBg[4]
            self.fail('IndexError not raised.')
        except IndexError:
            pass
        self.assertEquals("BufGen: ['a', 'b', 'c']", str(myBg))
        self.assertEquals(3, myBg.lenBuf)
        try:
            myBg[4]
            self.fail('IndexError not raised.')
        except IndexError:
            pass
        self.assertEquals("BufGen: ['a', 'b', 'c']", str(myBg))
        self.assertEquals(3, myBg.lenBuf)

    def test_02(self):
        """Test string buffer use of len() fails."""
        myStrGen = StrGen('abc')
        myBg = BufGen.BufGen(next(myStrGen))
        try:
            len(myBg)
            self.fail('TypeError not raised.')
        except TypeError:
            pass

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    """Execute unit tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBufGen))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBufGenReplace))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBufGenIndex))
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
