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

import os
import sys
import time
import logging

from cpip.util import MatrixRep

######################
# Section: Unit tests.
######################
import unittest

class TestMatrixRep(unittest.TestCase):
    """Tests the generator."""
    def test_00(self):
        """TestMatrixRep: constructor."""
        myObj = MatrixRep.MatrixRep()
        
    def test_01(self):
        """TestMatrixRep: expand a word."""
        myObj = MatrixRep.MatrixRep()
        myObj.addLineColRep(0, 4, 'two', 'twelve')
        myLines = [
                   'one two three',
                   'one two three',
                   'one two three',
                   ]
        myObj.sideEffect(myLines)
        self.assertEqual(
            [
               'one twelve three',
               'one two three',
               'one two three',
            ],
            myLines)
        
    def test_02(self):
        """TestMatrixRep: expand several words."""
        myObj = MatrixRep.MatrixRep()
        myObj.addLineColRep(0, 4, 'two', 'twelve')
        myObj.addLineColRep(1, 4, 'two', 'seven')
        myObj.addLineColRep(2, 4, 'two', 'six')
        myLines = [
                   'one two three',
                   'one two three',
                   'one two three',
                   ]
        myObj.sideEffect(myLines)
        self.assertEqual(
            [
               'one twelve three',
               'one seven three',
               'one six three',
            ],
            myLines)
        
    def test_03(self):
        """TestMatrixRep: expand a word at column end."""
        myObj = MatrixRep.MatrixRep()
        myObj.addLineColRep(0, 8, 'three', 'twelve')
        myLines = [
                   'one two three',
                   ]
        myObj.sideEffect(myLines)
        self.assertEqual(
            [
               'one two twelve',
            ],
            myLines)
        
    def test_04(self):
        """TestMatrixRep: replace a word at column end."""
        myObj = MatrixRep.MatrixRep()
        myObj.addLineColRep(0, 8, 'three', '')
        myLines = [
                   'one two three',
                   ]
        myObj.sideEffect(myLines)
        self.assertEqual(
            [
               'one two ',
            ],
            myLines)
        
    def test_05(self):
        """TestMatrixRep: consecutive replacements contract then expand."""
        myObj = MatrixRep.MatrixRep()
        myObj.addLineColRep(0, 3, 'two', '')
        myObj.addLineColRep(0, 6, 'three', ' twelve')
        myLines = [
                   'onetwothree',
                   ]
        myObj.sideEffect(myLines)
        self.assertEqual(
            [
               'one twelve',
            ],
            myLines)
        
    def test_06(self):
        """TestMatrixRep: consecutive replacements expand then contract."""
        myObj = MatrixRep.MatrixRep()
        myObj.addLineColRep(0, 3, 'two', ' twelve')
        myObj.addLineColRep(0, 6, 'three', ' six')
        myLines = [
                   'onetwothree',
                   ]
        myObj.sideEffect(myLines)
        self.assertEqual(
            [
               'one twelve six',
            ],
            myLines)
        
class TestMatrixRepException(unittest.TestCase):
    """Tests MatrixRep exceptions."""
    def test_00(self):
        """TestMatrixRepException: line overrun."""
        myObj = MatrixRep.MatrixRep()
        myObj.addLineColRep(4, 0, '', '')
        myLines = [
                   'abc',
                   'abcdef',
                   'abcdefghi',
                   ]
        self.assertRaises(
                MatrixRep.ExceptionMatrixRep,
                myObj.sideEffect,
                myLines)
        
    def test_00_00(self):
        """TestMatrixRepException: line overrun on empty."""
        myObj = MatrixRep.MatrixRep()
        myObj.addLineColRep(0, 0, '', '')
        myLines = [
                   ]
        self.assertRaises(
                MatrixRep.ExceptionMatrixRep,
                myObj.sideEffect,
                myLines)

    def test_01(self):
        """TestMatrixRepException: column overrun."""
        myObj = MatrixRep.MatrixRep()
        myObj.addLineColRep(1, 172, '', '')
        myLines = [
                   'abc',
                   'abcdef',
                   'abcdefghi',
                   ]
        self.assertRaises(
                MatrixRep.ExceptionMatrixRep,
                myObj.sideEffect,
                myLines)
        
    def test_01_00(self):
        """TestMatrixRepException: column overrun on empty."""
        myObj = MatrixRep.MatrixRep()
        myObj.addLineColRep(0, 0, '', '')
        myLines = [
                   ]
        self.assertRaises(
                MatrixRep.ExceptionMatrixRep,
                myObj.sideEffect,
                myLines)

#===============================================================================
#    def test_01(self):
#        """TestMatrixRepException: column overrun."""
#        myObj = MatrixRep.MatrixRep()
#        myObj.addLineColRep(0, 0, '', '')
#        myLines = [
#                   'abc',
#                   'abcdef',
#                   'abcdefghi',
#                   ]
#        myObj.sideEffect(myLines)
#===============================================================================

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMatrixRep))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMatrixRepException))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print \
"""TestMatrixRep.py - A module that tests MatrixRep module.
Usage:
python TestMatrixRep.py [-lh --help]

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
    print 'TestMatrixRep.py script version "%s", dated %s' % (__version__, __date__)
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
