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
import unittest
import logging

from cpip.core import PpWhitespace

########################################
# Section: Unit tests
########################################
class TestPpWhitespace(unittest.TestCase):
    """Tests the class PpWhitespace to ISO/IEC 9899:1999(E) Section 6
    and ISO/IEC 14882:1998(E)."""
    def setUp(self):
        """Create an PpWhitespace object."""
        self._ws = PpWhitespace.PpWhitespace()

    def test_sliceWhitespace(self):
        """PpWhitespace.sliceWhitespace()."""
        #'\t\v\f\n '
        self.assertEqual(0, self._ws.sliceWhitespace(''))
        self.assertEqual(1, self._ws.sliceWhitespace(' '))
        self.assertEqual(0, self._ws.sliceWhitespace('a b c '))
        self.assertEqual(1, self._ws.sliceWhitespace(' a b c '))
        self.assertEqual(5, self._ws.sliceWhitespace('\t\v\f\n '))

    def test_hasLeadingWhitespace(self):
        """PpWhitespace.hasLeadingWhitespace()."""
        self.assertEqual(False, self._ws.hasLeadingWhitespace(''))
        self.assertEqual(False, self._ws.hasLeadingWhitespace('abc'))
        self.assertEqual(False, self._ws.hasLeadingWhitespace('abc '))
        self.assertEqual(True, self._ws.hasLeadingWhitespace(' abc'))
        self.assertEqual(True, self._ws.hasLeadingWhitespace('\tabc'))
        self.assertEqual(True, self._ws.hasLeadingWhitespace('\vabc'))
        self.assertEqual(True, self._ws.hasLeadingWhitespace('\fabc'))
        self.assertEqual(True, self._ws.hasLeadingWhitespace('\nabc'))

    def test_isAllWhitespace(self):
        """PpWhitespace.isAllWhitespace()."""
        self.assertEqual(False, self._ws.isAllWhitespace(''))
        self.assertEqual(False, self._ws.isAllWhitespace('abc'))
        self.assertEqual(False, self._ws.isAllWhitespace(' abc '))
        self.assertEqual(True, self._ws.isAllWhitespace(' '))
        self.assertEqual(True, self._ws.isAllWhitespace('\t\v\f\n '))

    def test_isBreakingWhitespace(self):
        """PpWhitespace.isBreakingWhitespace()."""
        self.assertEqual(False, self._ws.isBreakingWhitespace(''))
        self.assertEqual(False, self._ws.isBreakingWhitespace(' \t '))
        self.assertEqual(False, self._ws.isBreakingWhitespace('abc'))
        self.assertEqual(True, self._ws.isBreakingWhitespace(' \n '))
        self.assertEqual(True, self._ws.isBreakingWhitespace('\t\v\f\n '))
        self.assertEqual(False, self._ws.isBreakingWhitespace('\t\v\f '))

    def test_isAllMacroWhitespace(self):
        """PpWhitespace.isAllMacroWhitespace() ISO/IEC 9899:1990(E) 6.10-5"""
        self.assertEqual(True, self._ws.isAllMacroWhitespace(''))
        self.assertEqual(True, self._ws.isAllMacroWhitespace(' \n '))
        self.assertEqual(True, self._ws.isAllMacroWhitespace(' \t '))
        self.assertEqual(False, self._ws.isAllMacroWhitespace('abc'))

    def test_preceedsNewline(self):
        """PpWhitespace.preceedsNewline()."""
        self.assertEqual(False, self._ws.preceedsNewline(''))
        self.assertEqual(False, self._ws.preceedsNewline(' \n '))
        self.assertEqual(False, self._ws.preceedsNewline(' \t '))
        self.assertEqual(False, self._ws.preceedsNewline('abc'))
        self.assertEqual(True, self._ws.preceedsNewline(' \n'))
        self.assertEqual(False, self._ws.preceedsNewline(' \na'))

    def test_sliceNonWhitespace(self):
        """PpWhitespace.sliceNonWhitespace()."""
        #'\t\v\f\n '
        self.assertEqual(0, self._ws.sliceNonWhitespace(''))
        self.assertEqual(0, self._ws.sliceNonWhitespace(' '))
        self.assertEqual(1, self._ws.sliceNonWhitespace('a b c '))
        self.assertEqual(0, self._ws.sliceNonWhitespace(' a b c '))
        self.assertEqual(6, self._ws.sliceNonWhitespace('bitand'))
        self.assertEqual(6, self._ws.sliceNonWhitespace('bitand     '))

def unitTest(theVerbosity=2):
    """Invoke unit tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestPpWhitespace
        )
    #suite.addTests(
    #    unittest.TestLoader().loadTestsFromTestCase(something else)
    #    )
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

#################
# End: Unit tests
#################


def usage():
    print("""TestPpWhitespace.py - Tests the PpWhitespace module.
Usage:
python TestPpWhitespace.py [-hl: --help]

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
""")

def main():
    print('TestPpWhitespace.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
    print(__rights__)
    print()
    import getopt
    import time
    print('Command line:')
    print(' '.join(sys.argv))
    print()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError as myErr:
        usage()
        print('ERROR: Invalid option: %s' % str(myErr))
        sys.exit(1)
    logLevel = logging.WARNING
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o == '-l':
            logLevel = int(a)
    if len(args) != 0:
        usage()
        print('ERROR: Wrong number of arguments[%d]!' % len(args))
        sys.exit(1)
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    unitTest()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
