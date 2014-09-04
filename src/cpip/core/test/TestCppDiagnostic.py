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

import os
import sys
import time
import logging
from cpip.core import CppDiagnostic

######################
# Section: Unit tests.
######################
import unittest
# Define unit test classes

class DummyLocator(object):
    def __init__(self):
        self.fileId = 'fileName'
        self.lineNum = 21
        self.colNum = 45

class TestCppDiagnostic(unittest.TestCase):
    """Tests the CppDiagnostic class."""
    def testUndefined(self):
        """Undefined behaviour raises an ExceptionCppDiagnosticUndefined."""
        myObj = CppDiagnostic.PreprocessDiagnosticStd()
        self.assertEqual(0, myObj._cntrUndefined)
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticUndefined,
                        myObj.undefined, "Some message")
        self.assertEqual(1, myObj._cntrUndefined)
        try:
            myObj.undefined("Some message")
        except CppDiagnostic.ExceptionCppDiagnosticUndefined as err:
            self.assertEqual("Some message", str(err))
        self.assertEqual(2, myObj._cntrUndefined)

    def testPartialTokenStream(self):
        """Partial token stream raises an ExceptionCppDiagnosticPartialTokenStream."""
        myObj = CppDiagnostic.PreprocessDiagnosticStd()
        self.assertEqual(0, myObj._cntrPartialTokenStream)
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                        myObj.partialTokenStream, "Some message")
        self.assertEqual(1, myObj._cntrPartialTokenStream)
        try:
            myObj.partialTokenStream("Some message")
        except CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream as err:
            self.assertEqual("Some message", str(err))
        self.assertEqual(2, myObj._cntrPartialTokenStream)

    def testImplementationDefined(self):
        """Implementation defined behaviour logs a warning."""
        myObj = CppDiagnostic.PreprocessDiagnosticStd()
        self.assertEqual(0, myObj._cntrImplDefined)
        myObj.implementationDefined("Some warning message")
        self.assertEqual(1, myObj._cntrImplDefined)

    def testError(self):
        """Error behaviour logs an error."""
        myObj = CppDiagnostic.PreprocessDiagnosticStd()
        self.assertEqual(0, myObj._cntrError)
        myObj.error("Some error message")
        self.assertEqual(1, myObj._cntrError)

    def testWarning(self):
        """Warining behaviour logs an error."""
        myObj = CppDiagnostic.PreprocessDiagnosticStd()
        self.assertEqual(0, myObj._cntrWarning)
        myObj.warning("Some warning message")
        self.assertEqual(1, myObj._cntrWarning)

    def testUnspecified(self):
        """Unspecified behaviour logs an information message."""
        myObj = CppDiagnostic.PreprocessDiagnosticStd()
        self.assertEqual(0, myObj._cntrUnspecified)
        myObj.unspecified("Some message about unspecified.")
        self.assertEqual(1, myObj._cntrUnspecified)

    def testUndefinedLoc(self):
        """Undefined behaviour raises an ExceptionCppDiagnosticUndefined using a locator."""
        myObj = CppDiagnostic.PreprocessDiagnosticStd()
        self.assertEqual(0, myObj._cntrUndefined)
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticUndefined,
                        myObj.undefined, "Some message", DummyLocator())
        self.assertEqual(1, myObj._cntrUndefined)
        try:
            myObj.undefined("Some message", DummyLocator())
        except CppDiagnostic.ExceptionCppDiagnosticUndefined as err:
            self.assertEqual('Some message at line=21, col=45 of file "fileName"', str(err))
        self.assertEqual(2, myObj._cntrUndefined)

    def testPartialTokenStreamLoc(self):
        """Partial token stream raises an ExceptionCppDiagnosticPartialTokenStream using a locator."""
        myObj = CppDiagnostic.PreprocessDiagnosticStd()
        self.assertEqual(0, myObj._cntrPartialTokenStream)
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                        myObj.partialTokenStream, "Some message", DummyLocator())
        self.assertEqual(1, myObj._cntrPartialTokenStream)
        try:
            myObj.partialTokenStream("Some message", DummyLocator())
        except CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream as err:
            self.assertEqual('Some message at line=21, col=45 of file "fileName"', str(err))
        self.assertEqual(2, myObj._cntrPartialTokenStream)

    def testImplementationDefinedLoc(self):
        """Implementation defined behaviour logs a warning with a locator."""
        myObj = CppDiagnostic.PreprocessDiagnosticStd()
        self.assertEqual(0, myObj._cntrImplDefined)
        myObj.implementationDefined("Some warning", DummyLocator())
        self.assertEqual(1, myObj._cntrImplDefined)

    def testErrorLoc(self):
        """Error behaviour logs an error with a locator."""
        myObj = CppDiagnostic.PreprocessDiagnosticStd()
        self.assertEqual(0, myObj._cntrError)
        myObj.error("Some error", DummyLocator())
        self.assertEqual(1, myObj._cntrError)

    def testUnspecifiedLoc(self):
        """Unspecified behaviour logs an information message with a locator."""
        myObj = CppDiagnostic.PreprocessDiagnosticStd()
        self.assertEqual(0, myObj._cntrUnspecified)
        myObj.unspecified("Some message about unspecified.", DummyLocator())
        self.assertEqual(1, myObj._cntrUnspecified)

class TestCppDiagnosticKeepGoing(unittest.TestCase):
    """Tests the PreprocessDiagnosticKeepGoing class."""
    def testUndefined(self):
        """Undefined behaviour does not raise an ExceptionCppDiagnosticUndefined."""
        myObj = CppDiagnostic.PreprocessDiagnosticKeepGoing()
        self.assertEqual(0, myObj._cntrUndefined)
        myObj.undefined("PreprocessDiagnosticKeepGoing.undefined()")
        self.assertEqual(1, myObj._cntrUndefined)

    def testPartialTokenStream(self):
        """Partial token stream does not raise an ExceptionCppDiagnosticPartialTokenStream."""
        myObj = CppDiagnostic.PreprocessDiagnosticKeepGoing()
        self.assertEqual(0, myObj._cntrPartialTokenStream)
        myObj.partialTokenStream("PreprocessDiagnosticKeepGoing.partialTokenStream()")
        self.assertEqual(1, myObj._cntrPartialTokenStream)

class TestCppDiagnosticRaiseOnError(unittest.TestCase):
    """Tests the PreprocessDiagnosticRaiseOnError class."""
    def testError(self):
        """On error report and raise an ExceptionCppDiagnosticUndefined."""
        myObj = CppDiagnostic.PreprocessDiagnosticRaiseOnError()
        self.assertEqual(0, myObj._cntrError)
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnostic,
                        myObj.error, "Some message")
        self.assertEqual(1, myObj._cntrError)

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCppDiagnostic)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppDiagnosticKeepGoing))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppDiagnosticRaiseOnError))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestCppDiagnostic.py - A module that tests CppDiagnostic module.
Usage:
python TestCppDiagnostic.py [-lh --help]

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
    print('TestCppDiagnostic.py script version "%s", dated %s' % (__version__, __date__))
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
