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

"""Tests the PpLexer with a single Translation Unit to see what the real world
code coverage actually is.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import logging
import sys
import os
try:
    import io as StringIO
except ImportError:
    import io
import pprint

from cpip.core import PpLexer, CppDiagnostic, FileLocation, PpTokeniser, PpToken, IncludeHandler, MacroEnv
import TestPpDefine

######################
# Section: Unit tests.
######################
import unittest

class TestPpLexerCoverageBase(TestPpDefine.TestPpDefine):
    """Helper class for the unit tests."""
    """Tests the code coverage of the CPIP core."""
    def setUp(self):
        self._incSim = IncludeHandler.CppIncludeStringIO(
            self._pathsUsr,
            self._pathsSys,
            self._initialTuContents,
            self._incFileMap,
            )
        self._incSim.validateCpStack()
        self.assertEqual([], self._incSim.cpStack)
        self.assertEqual(0, self._incSim.cpStackSize)

    def tearDown(self):
        self.assertEqual([], self._incSim.cpStack)
        self._incSim.validateCpStack()

    def testSetUpTearDown(self):
        """TestIncludeHandlerBase.testSetUpTearDown(): Tests setUp() and tearDown()."""
        self.assertEqual(1,1)

class TestPpLexerCoverage(TestPpLexerCoverageBase):
    """Tests the code coverage of the CPIP core."""
    def __init__(self, *args):
        # The next two arguments mean that:
        # src/spam.c
        #   |-> usr/spam.h
        #       |-> usr/inc/spam.h
        #           |-> sys/spam.h
        #               |-> sys/inc/spam.h
        #                   |-> "Content of: system, include, spam.h"
        # Initial TU:
        self._initialTuContents = """// Continuation line \
and this has a trigraph in it
??=define ONE 1
/* Function like macro with stringise */
#define FILE(f) # f
// Exercise function like macro without preamble
FILE
// Exercise Keywords???
#define CONST const
// Macros with parameters and ##
#define glue(a, b) a ## b
#define xglue(a, b) glue(a, b)
#define HIGHLOW "hello"
#define LOW LOW ", world"
glue(HIGH, LOW);
xglue(HIGH, LOW)
// Macro with variable arguemnts
#define VA(...) __VA_ARGS__
VA(1,,3)
// Redefinitions
#define ONE 1
#define glue(a, b)/* ... */ a ## b // Something

// Fraction
.14
// Floating point
+123.456e-2L

#if ONE
#include FILE(spam.h)
#else
#endif

#if !defined ONE
#elif defined ONE
#endif

#if defined NON_EXISTANT
#elif !defined NON_EXISTANT
#endif

#ifdef ONE
#endif

#ifndef NON_EXISTANT
#endif

#undef ONE
#undef NON_EXISTANT
"""
        self._incFileMap = {
                os.path.join('usr', 'spam.h') : """#include "inc/spam.h"
""",
                os.path.join('usr', 'inc', 'spam.h') : """#include <spam.h>
""",
                os.path.join('sys', 'spam.h') : """#include <inc/spam.h>
""",
                os.path.join('sys', 'inc', 'spam.h') : """Content of: system, include, spam.h
""",
            }
        self._pathsUsr = [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ]
        self._pathsSys = [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ]
        super(TestPpLexerCoverage, self).__init__(*args)

    def test_00(self):
        """TestPpLexerCoverage.test_00(): Tests code coverage."""
        #print
        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
        resultTokS = [t for t in myLexer.ppTokens()]
        #self.pprintReplacementList(resultTokS)
        return
        assert(0)
        result = ''.join([t.t for t in resultTokS])
        expectedResult = """ \n\n \n\nContent of: system, include, spam.h\n\n\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        expGraph = """src/spam.c [20, 10]:  True ""
000002: #include usr\spam.h
        usr\spam.h [0, 0]:  True ""
        000001: #include usr\inc\spam.h
                usr\inc\spam.h [0, 0]:  True ""
                000001: #include sys\spam.h
                        sys\spam.h [0, 0]:  True ""
                        000001: #include sys\inc\spam.h
                                sys\inc\spam.h [15, 10]:  True \"\""""
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))
    
#===============================================================================
# 
# class TestIncludeHandler_UsrSys_Conditional(TestPpLexerCoverageBase):
#    """Tests #include statements. Note: This is similar to stuff
#    in TestIncludeHandler.py"""
#    def __init__(self, *args):
#        self._pathsUsr = [
#                os.path.join('usr'),
#                os.path.join('usr', 'inc'),
#                ]
#        self._pathsSys = [
#                os.path.join('sys'),
#                os.path.join('sys', 'inc'),
#                ]
#        self._initialTuContents = """#if INC == 0
# #include "spam.h"
# #elif INC == 1
# #include "inc/spam.h"
# #elif INC == 2
# #include <spam.h>
# #elif INC == 3
# #include <inc/spam.h>
# #endif
# """
#        self._incFileMap = {
#                os.path.join('usr', 'spam.h') : """Content of: user, spam.h
# """,
#                os.path.join('usr', 'inc', 'spam.h') : """Content of: user, include, spam.h
# """,
#                os.path.join('sys', 'spam.h') : """Content of: system, spam.h
# """,
#                os.path.join('sys', 'inc', 'spam.h') : """Content of: system, include, spam.h
# """,
#            }
#        super(TestIncludeHandler_UsrSys_Conditional, self).__init__(*args)
# 
#    def testSimpleInclude_00(self):
#        """TestIncludeHandler_UsrSys_Conditional.testSimpleInclude_00(): Tests conditional #include statements."""
#        # Note: Using line splicing in the predef
#        preDefMacros=[
#                      """#define INC \\
# 0
# """,
#                      ]
#        myLexer = PpLexer.PpLexer(
#                                  'src/spam.c',
#                                  self._incSim,
#                                  preIncFiles=[
#                                               StringIO.StringIO(x) for x in preDefMacros
#                                               ],
#                                  )
#        result = ''.join([t.t for t in myLexer.ppTokens()])
#        expectedResult = """\nContent of: user, spam.h\n\n\n"""
#        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
#        self.assertEqual(result, expectedResult)
#        myLexer.finalise()
#        #print 'FileIncludeGraph:'
#        #print myLexer.fileIncludeGraphRoot
#        expGraph = """Unknown Pre-include [1, 0]:  True ""
# src/spam.c [63, 36]:  True ""
# 000002: #include usr\spam.h
#        usr\spam.h [12, 8]:  True "INC == 0"
# 000004: #include usr\inc\spam.h
#        usr\inc\spam.h [0, 0]: False "(!(INC == 0) && INC == 1)"
# 000006: #include sys\spam.h
#        sys\spam.h [0, 0]: False "(!(INC == 0) && !(INC == 1) && INC == 2)"
# 000008: #include sys\inc\spam.h
#        sys\inc\spam.h [0, 0]: False "(!(INC == 0) && !(INC == 1) && !(INC == 2) && INC == 3)\""""
#        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))
# 
#    def testSimpleInclude_01(self):
#        """TestIncludeHandler_UsrSys_Conditional.testSimpleInclude_01(): Tests conditional #include statements."""
#        # Note using comments in the predef
#        preDefMacros=[
#                      """#define INC /* comment */ 1
# """,
#                      ]
#        myLexer = PpLexer.PpLexer(
#                                  'src/spam.c',
#                                  self._incSim,
#                                  preIncFiles=[
#                                               StringIO.StringIO(x) for x in preDefMacros
#                                               ],
#                                  )
#        result = ''.join([t.t for t in myLexer.ppTokens()])
#        expectedResult = """\nContent of: user, include, spam.h\n\n\n"""
#        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
#        self.assertEqual(result, expectedResult)
#        myLexer.finalise()
#        #print 'FileIncludeGraph:'
#        #print myLexer.fileIncludeGraphRoot
#        expGraph = """Unknown Pre-include [1, 0]:  True ""
# src/spam.c [63, 36]:  True ""
# 000002: #include usr\spam.h
#        usr\spam.h [0, 0]: False "INC == 0"
# 000004: #include usr\inc\spam.h
#        usr\inc\spam.h [15, 10]:  True "(!(INC == 0) && INC == 1)"
# 000006: #include sys\spam.h
#        sys\spam.h [0, 0]: False "(!(INC == 0) && !(INC == 1) && INC == 2)"
# 000008: #include sys\inc\spam.h
#        sys\inc\spam.h [0, 0]: False "(!(INC == 0) && !(INC == 1) && !(INC == 2) && INC == 3)\""""
#        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))
# 
#    def testSimpleInclude_02(self):
#        """TestIncludeHandler_UsrSys_Conditional.testSimpleInclude_02(): Tests conditional #include statements."""
#        # Note using comments and line splicing in the predef
#        preDefMacros=[
#                      """#define /* C comment */ INC \\
# 2
# // C++ comment
# """,
#                      ]
#        myLexer = PpLexer.PpLexer(
#                                  'src/spam.c',
#                                  self._incSim,
#                                  preIncFiles=[
#                                               StringIO.StringIO(x) for x in preDefMacros
#                                               ],
#                                  )
#        result = ''.join([t.t for t in myLexer.ppTokens()])
#        expectedResult = """\nContent of: system, spam.h\n\n\n"""
#        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
#        self.assertEqual(result, expectedResult)
#        myLexer.finalise()
#        #print 'FileIncludeGraph:'
#        #print myLexer.fileIncludeGraphRoot
#        expGraph = """Unknown Pre-include [3, 0]:  True ""
# src/spam.c [63, 36]:  True ""
# 000002: #include usr\spam.h
#        usr\spam.h [0, 0]: False "INC == 0"
# 000004: #include usr\inc\spam.h
#        usr\inc\spam.h [0, 0]: False "(!(INC == 0) && INC == 1)"
# 000006: #include sys\spam.h
#        sys\spam.h [12, 8]:  True "(!(INC == 0) && !(INC == 1) && INC == 2)"
# 000008: #include sys\inc\spam.h
#        sys\inc\spam.h [0, 0]: False "(!(INC == 0) && !(INC == 1) && !(INC == 2) && INC == 3)\""""
#        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))
# 
#    def testSimpleInclude_03(self):
#        """TestIncludeHandler_UsrSys_Conditional.testSimpleInclude_03(): Tests conditional #include statements."""
#        preDefMacros=[
#                      """#define INC 3
# """,
#                      ]
#        myLexer = PpLexer.PpLexer(
#                                  'src/spam.c',
#                                  self._incSim,
#                                  preIncFiles=[
#                                               StringIO.StringIO(x) for x in preDefMacros
#                                               ],
#                                  )
#        result = ''.join([t.t for t in myLexer.ppTokens()])
#        expectedResult = """\nContent of: system, include, spam.h\n\n\n"""
#        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
#        self.assertEqual(result, expectedResult)
#        myLexer.finalise()
#        #print 'FileIncludeGraph:'
#        #print myLexer.fileIncludeGraphRoot
#        expGraph = """Unknown Pre-include [1, 0]:  True ""
# src/spam.c [63, 36]:  True ""
# 000002: #include usr\spam.h
#        usr\spam.h [0, 0]: False "INC == 0"
# 000004: #include usr\inc\spam.h
#        usr\inc\spam.h [0, 0]: False "(!(INC == 0) && INC == 1)"
# 000006: #include sys\spam.h
#        sys\spam.h [0, 0]: False "(!(INC == 0) && !(INC == 1) && INC == 2)"
# 000008: #include sys\inc\spam.h
#        sys\inc\spam.h [15, 10]:  True "(!(INC == 0) && !(INC == 1) && !(INC == 2) && INC == 3)\""""
#        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))
# 
# class TestIncludeHandlerMacroBase(TestIncludeHandlerBase):
#    """Tests #include statements that have macros that expand to the
#    file identifier.
#    in TestIncludeHandler.py"""
#    def __init__(self, *args):
#        self._pathsUsr = [
#                os.path.join('usr'),
#                os.path.join('usr', 'inc'),
#                ]
#        self._pathsSys = [
#                os.path.join('sys'),
#                os.path.join('sys', 'inc'),
#                ]
#        # Child classes inplement this
#        #self._initialTuContents = ...
#        self._incFileMap = {
#                os.path.join('usr', 'spam.h') : """Content of: user, spam.h
# """,
#                os.path.join('usr', 'inc', 'spam.h') : """Content of: user, include, spam.h
# """,
#                os.path.join('sys', 'spam.h') : """Content of: system, spam.h
# """,
#                os.path.join('sys', 'inc', 'spam.h') : """Content of: system, include, spam.h
# """,
#            }
#        super(TestIncludeHandlerMacroBase, self).__init__(*args)
# 
# class TestIncludeHandlerMacro_Simple(TestIncludeHandlerMacroBase):
#    """Tests #include statements. Note: This is similar to stuff
#    in TestIncludeHandler.py"""
#    def __init__(self, *args):
#        self._initialTuContents = """#define FILE "spam.h"
# #include FILE
# """
#        super(TestIncludeHandlerMacro_Simple, self).__init__(*args)
# 
#    def testSimpleInclude(self):
#        """TestIncludeHandlerMacro_Simple.testSimpleInclude(): Tests multiple #include statements that resolve to usr/sys when expanded."""
#        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
#        result = ''.join([t.t for t in myLexer.ppTokens()])
#        expectedResult = """
# Content of: user, spam.h
# 
# """
#        #print '  Actual:\n%s' % result
#        #print 'Expected:\n%s' % expectedResult
#        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
#        self.assertEqual(result, expectedResult)
#        myLexer.finalise()
# 
# class TestIncludeHandlerMacro_SimpleUndef(TestIncludeHandlerMacroBase):
#    """Tests #include statements. Note: This is similar to stuff
#    in TestIncludeHandler.py"""
#    def __init__(self, *args):
#        self._initialTuContents = """#define FILE "spam.h"
# #include FILE
# #undef FILE
# #define FILE "inc/spam.h"
# #include FILE
# """
#        super(TestIncludeHandlerMacro_SimpleUndef, self).__init__(*args)
# 
#    def testSimpleInclude(self):
#        """TestIncludeHandlerMacro_SimpleUndef.testSimpleInclude(): Tests multiple #include statements that resolve to usr/sys when expanded."""
#        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
#        result = ''.join([t.t for t in myLexer.ppTokens()])
#        expectedResult = """
# Content of: user, spam.h
# 
# 
# 
# Content of: user, include, spam.h
# 
# """
#        #print '  Actual:\n%s' % result
#        #print 'Expected:\n%s' % expectedResult
#        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
#        self.assertEqual(result, expectedResult)
#        myLexer.finalise()
# 
# class TestIncludeHandler_UsrSys_MacroObject(TestIncludeHandlerMacroBase):
#    """Tests #include statements using object-like macros. Note: This is similar to stuff
#    in TestIncludeHandler.py"""
#    def __init__(self, *args):
#        self._initialTuContents = """#define FILE "spam.h"
# #include FILE
# #undef FILE
# #define FILE "inc/spam.h"
# #include FILE
# #undef FILE
# #define FILE <spam.h>
# #include FILE
# #undef FILE
# #define FILE <inc/spam.h>
# #include FILE
# """
#        super(TestIncludeHandler_UsrSys_MacroObject, self).__init__(*args)
# 
#    def testSimpleInclude(self):
#        """TestIncludeHandler_UsrSys_MacroObject.testSimpleInclude(): Tests multiple #include statements with object-like macros."""
#        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
#        result = ''.join([t.t for t in myLexer.ppTokens()])
#        expectedResult = """
# Content of: user, spam.h
# \n\n
# Content of: user, include, spam.h
# \n\n
# Content of: system, spam.h
# \n\n
# Content of: system, include, spam.h
# \n"""
#        #print '  Actual:\n%s' % result
#        #print 'Expected:\n%s' % expectedResult
#        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
#        self.assertEqual(result, expectedResult)
#        myLexer.finalise()
# 
# class TestIncludeHandler_UsrSys_MacroFunction(TestIncludeHandlerMacroBase):
#    """Tests #include statements. Note: This is similar to stuff
#    in TestIncludeHandler.py"""
#    def __init__(self, *args):
#        self._initialTuContents = """#define FILE(f) # f
# #include FILE(spam.h)
# #include FILE(inc/spam.h)
# #undef FILE
# #define FILE(f) <f>
# #include FILE(spam.h)
# #include FILE(inc/spam.h)
# """
#        super(TestIncludeHandler_UsrSys_MacroFunction, self).__init__(*args)
# 
#    def testSimpleInclude(self):
#        """TestIncludeHandler_UsrSys_MacroFunction.testSimpleInclude(): Tests multiple #include statements with function-like macros."""
#        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
#        result = ''.join([t.t for t in myLexer.ppTokens()])
#        expectedResult = """
# Content of: user, spam.h
# 
# Content of: user, include, spam.h
# \n\n
# Content of: system, spam.h
# 
# Content of: system, include, spam.h
# \n"""
#        #print '  Actual:\n%s' % result
#        #print 'Expected:\n%s' % expectedResult
#        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
#        self.assertEqual(result, expectedResult)
#        myLexer.finalise()
# 
# class TestIncludeHandler_UsrSys_MultipleDepth(TestIncludeHandlerBase):
#    """Tests #include statements that are multiple depth."""
#    def __init__(self, *args):
#        self._pathsUsr = [
#                os.path.join('usr'),
#                os.path.join('usr', 'inc'),
#                ]
#        self._pathsSys = [
#                os.path.join('sys'),
#                os.path.join('sys', 'inc'),
#                ]
#        # The next two arguments mean that:
#        # src/spam.c
#        #   |-> usr/spam.h
#        #       |-> usr/inc/spam.h
#        #           |-> sys/spam.h
#        #               |-> sys/inc/spam.h
#        #                   |-> "Content of: system, include, spam.h"
#        # Initial TU:
#        self._initialTuContents = """#include "spam.h"
# """
#        self._incFileMap = {
#                os.path.join('usr', 'spam.h') : """#include "inc/spam.h"
# """,
#                os.path.join('usr', 'inc', 'spam.h') : """#include <spam.h>
# """,
#                os.path.join('sys', 'spam.h') : """#include <inc/spam.h>
# """,
#                os.path.join('sys', 'inc', 'spam.h') : """Content of: system, include, spam.h
# """,
#            }
#        super(TestIncludeHandler_UsrSys_MultipleDepth, self).__init__(*args)
# 
#    def testSimpleInclude(self):
#        """TestIncludeHandler_UsrSys_MultipleDepth.testSimpleInclude(): Tests multiple depth #include statements that resolve to usr/sys."""
#        #print
#        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
#        result = ''.join([t.t for t in myLexer.ppTokens()])
#        expectedResult = """Content of: system, include, spam.h\n\n\n\n\n"""
#        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
#        self.assertEqual(result, expectedResult)
#        myLexer.finalise()
#        #print 'FileIncludeGraph:'
#        #print myLexer.fileIncludeGraphRoot
#        expGraph = """src/spam.c [19, 10]:  True ""
# 000001: #include usr\spam.h
#        usr\spam.h [0, 0]:  True ""
#        000001: #include usr\inc\spam.h
#                usr\inc\spam.h [0, 0]:  True ""
#                000001: #include sys\spam.h
#                        sys\spam.h [0, 0]:  True ""
#                        000001: #include sys\inc\spam.h
#                                sys\inc\spam.h [15, 10]:  True \"\""""
#        
#        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))
#===============================================================================


def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPpLexerCoverage)
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerCoverage))
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Special))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestPpLexerCoverage.py - A module that tests code coverge in the PpLexer module.
Usage:
python TestPpLexerCoverage.py [-lh --help]

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
    print('TestPpLexerCoverage.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
    print(__rights__)
    print()
    import getopt
    import time
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
