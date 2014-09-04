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
"""Unit tests for DirWalk.py. Actually this does not 'test' anything as it
just prints out various things about the file system for human interpration.

Created on Jun 10, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = 'Jun 10, 2011'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2011 paulross.'

#import pprint
import sys
import os
import time
import logging
#import io

from cpip.util import DirWalk

######################
# Section: Unit tests.
######################
import unittest

class TestGenBigFirst(unittest.TestCase):
    """Tests genBigFirst"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestGenBigFirst.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestGenBigFirst.test_01(): Input only, defaults."""
        print()
        for v in DirWalk.genBigFirst('.'):
            print('{:8d}: {:s}'.format(os.path.getsize(v), v))

class TestDirWalk(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestDirWalk.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestDirWalk.test_01(): Input only, defaults."""
        print()
        for v in DirWalk.dirWalk('.'):
            print(v)

    def test_02(self):
        """TestDirWalk.test_02(): Input and output, no globbing or recursion."""
        print()
        for v in DirWalk.dirWalk('.', theOut='spam', theFnMatch=None, recursive=False):
            print(v)

    def test_03(self):
        """TestDirWalk.test_03(): Input only, *.py and recursion."""
        print()
        for v in DirWalk.dirWalk('.', theFnMatch='*.py', recursive=True):
            print(v)

    def test_04(self):
        """TestDirWalk.test_04(): Input and output, *.py and recursion."""
        print()
        for v in DirWalk.dirWalk('.', theOut='spam', theFnMatch='*.py', recursive=True):
            print(v)

    def test_05(self):
        """TestDirWalk.test_05(): Input and output, *.py, recursion and biggest first."""
        print()
        for v in DirWalk.dirWalk('.', theOut='spam', theFnMatch='*.py', recursive=True, bigFirst=True):
            print('{:8d}: {:s}'.format(os.path.getsize(v.filePathIn), v))

    def test_06(self):
        """TestDirWalk.test_06(): Input only, *.py, recursion and biggest first."""
        print()
        for v in DirWalk.dirWalk('.', theOut=None, theFnMatch='*.py', recursive=True, bigFirst=True):
            print('{:8d}: {:s}'.format(os.path.getsize(v), v))

    def test_10(self):
        """TestDirWalk.test_10(): Fails if input does not exist."""
        try:
            for v in DirWalk.dirWalk('no_existent'):
                print(v)
            self.fail('DirWalk.ExceptionDirWalk not raised.')
        except DirWalk.ExceptionDirWalk:
            pass

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDirWalk))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGenBigFirst))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestClass.py - A module that tests something.
Usage:
python TestClass.py [-lh --help]

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
    print(('TestClass.py script version "%s", dated %s' % (__version__, __date__)))
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
