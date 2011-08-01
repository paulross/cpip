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

"""Temporary test module to explore unget() with a generator class.
Most of this code (and the test code) has ended up in PpTokeniser.py
and so on."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import time
import logging
from cpip import ExceptionCpip

class ExceptionUngetGen(ExceptionCpip):
    """Exception class for the UngetGen class."""
    pass

class UngetGen(object):
    """Class that is a generator with send() support."""
    def __init__(self, theIterable):
        self._iterable =  theIterable
        self._unget = None

    def __iter__(self):
        return self

    def next(self):
        """yield the next value."""
        for aVal in self._iterable:
            r = yield aVal
            if r is not None:
                # Caller has invoked send() and that call also returns the next yield.
                # So we yield None as the 'return' value of send() otherwise
                # send() gets back its argument rather than persisting it to
                # the subsequent next() call.
                yield None
                # Now when the caller invokes next() after send() we yield the
                # value passed in by the caller in the previous send()
                yield r
                # Only one send() between next() calls so we continue
                # with the iteration...

######################
# Section: Unit tests.
######################
import unittest
# Define unit test classes

class TestUngetGen(unittest.TestCase):

    def testAsimpleInit(self):
        """Tests UngetGen with a list comprehension."""
        myObj = UngetGen(range(8))
        myGen = myObj.next()
        myResult = [x for x in myGen]
        self.assertRaises(StopIteration, myGen.next)
        self.assertEqual(myResult, range(8))

    def testIncGen(self):
        """Tests UngetGen with incremental generation."""
        myObj = UngetGen(range(2))
        myGen = myObj.next()
        # Iterate
        myVal = myGen.next()
        self.assertEqual(myVal, 0)
        myVal = myGen.next()
        self.assertEqual(myVal, 1)
        self.assertRaises(StopIteration, myGen.next)

    def testIncGenUnget(self):
        """Tests UngetGen with incremental generation and single send()."""
        myObj = UngetGen(range(2))
        myGen = myObj.next()
        # Iterate
        myVal = myGen.next()
        self.assertEqual(myVal, 0)
        # sned() after next
        myGen.send(myVal)
        myVal = myGen.next()
        self.assertEqual(myVal, 0)
        myVal = myGen.next()
        self.assertEqual(myVal, 1)
        self.assertRaises(StopIteration, myGen.next)

    def testIncGenUngetAtStart(self):
        """Tests UngetGen with incremental generation and single send() before next()."""
        myObj = UngetGen(range(2))
        myGen = myObj.next()
        # Try sending before iterating
        self.assertRaises(TypeError, myGen.send, 42)
        myVal = myGen.next()
        self.assertEqual(myVal, 0)
        myVal = myGen.next()
        self.assertEqual(myVal, 1)
        self.assertRaises(StopIteration, myGen.next)

    def testIncGenUngetAtEnd(self):
        """Tests UngetGen with incremental generation and single send() after last next()."""
        myObj = UngetGen(range(2))
        myGen = myObj.next()
        # Iterate
        myVal = myGen.next()
        self.assertEqual(myVal, 0)
        myVal = myGen.next()
        self.assertEqual(myVal, 1)
        myGen.send(42)
        myVal = myGen.next()
        self.assertEqual(myVal, 42)
        self.assertRaises(StopIteration, myGen.next)

    def testIncGenUngetOnEmptyList(self):
        """Tests UngetGen with incremental generation and send() where the initial list is empty."""
        myObj = UngetGen([])
        myGen = myObj.next()
        # Try an insert
        self.assertRaises(TypeError, myGen.send, 127)
        self.assertRaises(StopIteration, myGen.next)

    def testIncGenUngetMultipleCallsAtStart(self):
        """Tests UngetGen with incremental generation where pairs of send() cancel each other."""
        myObj = UngetGen(range(2))
        myGen = myObj.next()
        # Iterate
        myVal = myGen.next()
        self.assertEqual(myVal, 0)
        self.assertEqual(None, myGen.send(42))
        self.assertEqual(42, myGen.send(84))
        # 84 is thrown away by the external loop of UnitGen.next()
        myVal = myGen.next()
        self.assertEqual(myVal, 1)
        self.assertRaises(StopIteration, myGen.next)

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUngetGen)
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(another class))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################


def usage():
    print \
"""TestUngetGen.py - Tests UngetGen
Usage:
python TestUngetGen.py [-hl: --help]

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
"""

def main():
    print 'TestUngetGen.py script version "%s", dated %s' % (__version__, __date__)
    print 'Author: %s' % __author__
    print __rights__
    print
    import getopt
    import sys
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
