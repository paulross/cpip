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

"""Tests for Macro HTML generator.
"""

__author__  = 'Paul Ross'
__date__    = '2014-03-06'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import sys
import os
import unittest
import time
import logging
#import pprint

# import io

sys.path.append(os.path.join(os.pardir + os.sep))
# from cpip.core import PpToken, FileIncludeGraph, PpTokenCount, PpLexer
# from cpip.core.IncludeHandler import CppIncludeStringIO
# from cpip.plot import TreePlotTransform 
from cpip.MacroHistoryHtml import splitLineToList, splitLine

#######################################
# Section: Unit tests
########################################

class NullClass(unittest.TestCase):
    pass

class TestSplitLine(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testSetUpTearDown(self):
        """TestCountDict: test setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestSplitLine.test_00(): Multi line."""
        myS = '_INIT_SECURITY_POLICY_C7(c1,c2,c3,c4,c5,c6,c7) { FOUR_TUINT8( (TUint8)TSecurityPolicy::ETypeC7, CAPABILITY_AS_TUINT8(c1), CAPABILITY_AS_TUINT8(c2), CAPABILITY_AS_TUINT8(c3) ), FOUR_TUINT8( CAPABILITY_AS_TUINT8(c4), CAPABILITY_AS_TUINT8(c5), CAPABILITY_AS_TUINT8(c6), CAPABILITY_AS_TUINT8(c7) ) } /* s:/epoc32/include\e32cmn.h#3997 Ref: 0 True */'
        #pprint.pprint(myS)
        #print
        #pprint.pprint(splitLineToList(myS))
        self.assertEqual(
                    [
                    '_INIT_SECURITY_POLICY_C7(c1,c2,c3,c4,c5,c6,c7) { FOUR_TUINT8( \\',
                    '(TUint8)TSecurityPolicy::ETypeC7, CAPABILITY_AS_TUINT8(c1), \\',
                    'CAPABILITY_AS_TUINT8(c2), CAPABILITY_AS_TUINT8(c3) ), FOUR_TUINT8( \\',
                    'CAPABILITY_AS_TUINT8(c4), CAPABILITY_AS_TUINT8(c5), \\',
                    'CAPABILITY_AS_TUINT8(c6), CAPABILITY_AS_TUINT8(c7) ) } /* \\',
                    's:/epoc32/include\\e32cmn.h#3997 Ref: 0 True */'
                    ],
                    splitLineToList(myS),
                )
        #print
        #print splitLine(myS)
        self.assertEqual(r"""_INIT_SECURITY_POLICY_C7(c1,c2,c3,c4,c5,c6,c7) { FOUR_TUINT8( \
    (TUint8)TSecurityPolicy::ETypeC7, CAPABILITY_AS_TUINT8(c1), \
    CAPABILITY_AS_TUINT8(c2), CAPABILITY_AS_TUINT8(c3) ), FOUR_TUINT8( \
    CAPABILITY_AS_TUINT8(c4), CAPABILITY_AS_TUINT8(c5), \
    CAPABILITY_AS_TUINT8(c6), CAPABILITY_AS_TUINT8(c7) ) } /* \
    s:/epoc32/include\e32cmn.h#3997 Ref: 0 True */""",
            splitLine(myS))

    def test_01(self):
        """TestSplitLine.test_00(): Short line."""
        myS = 'CONST_CAST(type,exp) (const_cast<type>(exp))'
        #pprint.pprint(myS)
        #print
        #pprint.pprint(splitLineToList(myS))
        self.assertEqual(
                    [
                    'CONST_CAST(type,exp) (const_cast<type>(exp))'
                    ],
                    splitLineToList(myS),
                )
        #print
        #print splitLine(myS)
        self.assertEqual(r"""CONST_CAST(type,exp) (const_cast<type>(exp))""",
            splitLine(myS))

    def test_02(self):
        """TestSplitLine.test_00(): Hard split."""
        myS='CAPABILITY_AS_TUINT8(cap)((TUint8)(int)((cap)==ECapability_None?(__invalid_capability_value(*)[1])(ECapability_None):(__invalid_capability_value(*)[((TUint)(cap+1)<=(TUint)ECapability_Limit)?1:2])(cap)))'
        #pprint.pprint(myS)
        #print
        #pprint.pprint(splitLineToList(myS))
        self.assertEqual(
                [
                    'CAPABILITY_AS_TUINT8(cap)((TUint8)(int)((cap)==ECapability_None?(__invalid_capab\\',
                    'ility_value(*)[1])(ECapability_None):(__invalid_capability_value(*)[((TUint)(cap\\',
                    '+1)<=(TUint)ECapability_Limit)?1:2])(cap)))',
                ],
                splitLineToList(myS)
            )
        #print
        #print splitLine(myS)
        self.assertEqual(r"""CAPABILITY_AS_TUINT8(cap)((TUint8)(int)((cap)==ECapability_None?(__invalid_capab\
    ility_value(*)[1])(ECapability_None):(__invalid_capability_value(*)[((TUint)(cap\
    +1)<=(TUint)ECapability_Limit)?1:2])(cap)))""",
                splitLine(myS)
            )

class Special(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSplitLine))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Special))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

#################
# End: Unit tests
#################

def usage():
    """Send the help to stdout."""
    print("""TestMacroHistoryHTML.py - A module that tests MacroHistoryHTML module.
Usage:
python TestMacroHistoryHTML.py [-lh --help]

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
    print('MacroHistoryHTML.py script version "%s", dated %s' % (__version__, __date__))
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
