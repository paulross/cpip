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
__date__    = '2015-01-24'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2015 Paul Ross'

import logging
import sys
import time
import unittest

from cpip.util import Cpp

class TestCppSubprocess(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testCppInvoke(self):
        result = Cpp.invokeCppForPlatformMacros('-dM')
#         print(result)
        self.assertTrue(len(result) > 0)

class TestCppMacroDefinitionDict(unittest.TestCase):
    
    def testMacroDefinitionDict_00(self):
        self.assertEqual({}, Cpp.macroDefinitionDict([]))

    def testMacroDefinitionDict_01(self):
        self.assertEqual({'FOO' : '\n'}, Cpp.macroDefinitionDict(['FOO']))

    def testMacroDefinitionDict_02(self):
        self.assertEqual({'FOO' : 'BAR\n'}, Cpp.macroDefinitionDict(['FOO=BAR']))

    def testMacroDefinitionDict_03(self):
        self.assertEqual({'FOO(n)' : 'n * BAR\n'}, Cpp.macroDefinitionDict(['FOO(n)=n * BAR']))

class TestCppMacroDefinitionString(unittest.TestCase):
    
    def testMacroDefinitionString_00(self):
        self.assertEqual('', Cpp.macroDefinitionString([]))

    def testMacroDefinitionString_01(self):
        self.assertEqual('#define FOO\n', Cpp.macroDefinitionString(['FOO']))

    def testMacroDefinitionString_02(self):
        self.assertEqual('#define FOO BAR\n', Cpp.macroDefinitionString(['FOO=BAR']))

    def testMacroDefinitionString_03(self):
        self.assertEqual('#define FOO(n) n * BAR\n', Cpp.macroDefinitionString(['FOO(n)=n * BAR']))


class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    """Execute unit tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppSubprocess))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppMacroDefinitionDict))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppMacroDefinitionString))
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
