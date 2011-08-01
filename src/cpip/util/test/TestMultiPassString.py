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
#import os
import unittest
import time
import logging
#import pprint

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

#try:
#    from xml.etree import cElementTree as etree
#except ImportError:
#    from xml.etree import ElementTree as etree

#sys.path.append(os.path.join(os.pardir + os.sep))
#===============================================================================
# import pprint
# pprint.pprint(sys.path)
#===============================================================================
from cpip.util import MultiPassString

#######################################
# Section: Unit tests
########################################
class TestBase(unittest.TestCase):
    """Test the simple stuff."""
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_00(self):
        """TestBase.test_00(): setUp() and tearDown()."""
        pass

class TestMultiPassStringMarker(TestBase):
    """Test the simple stuff of MultiPassString."""
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_00(self):
        """TestMultiPassStringMarker.test_00(): setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestMultiPassStringMarker.test_01(): Empty string."""
        myMps = MultiPassString.MultiPassString(StringIO.StringIO(''))
        o = [c for c in myMps.genChars()]
        #print o
        self.assertEqual([], o)
        n = [c for c in myMps.genWords()]
        self.assertEqual([], n)
        self.assertEqual([], myMps.currentString)
        self.assertEqual(0, myMps.idxChar)
        self.assertEqual({}, myMps.idxTypeMap)
    
    def test_02(self):
        """TestMultiPassStringMarker.test_02(): C++ and line continuation using individual functions."""
        myStr = """
// Some comment \\
and \\
the rest

"""
        myMps = MultiPassString.MultiPassString(StringIO.StringIO(myStr))
        o = []
        for c in myMps.genChars():
            if c == '\n' and myMps.prevChar == '\\':
                myMps.removeMarkedWord(isTerm=True)
                # Note we don't myMps.setWordType('line-continuation')
                # as this is interlaced with the C++ comment.
            #prevChar = c
            myMps.setMarker()
        # Check the result of this pass
        o = [c for c in myMps.genChars()]
        #print 'Line continuation removed:'
        #print ''.join(o)
        #print 'Line continuation removed currentString:'
        #print myMps.currentString
        self.assertEqual('\n// Some comment and the rest\n\n', ''.join(o))
        #print 'idxTypeMap 0'
        #print myMps.idxTypeMap
        # Mark comment
        for c in myMps.genChars():
            if c == '\n' and myMps.hasWord:
                # Replace by a single space
                # remove and mark
                myMps.removeMarkedWord(isTerm=True)
                #print 'idxTypeMap 1'
                #print myMps.idxTypeMap
                myMps.setWordType('C++ comment', isTerm=True)
                myMps.setAtMarker(' ')
                myMps.clearMarker()
            elif c == '/' and myMps.prevChar != '/':
                # Start of comment
                myMps.setMarker()
            elif myMps.wordLength == 1 and c != '/':
                myMps.clearMarker()
        # Check the result of this pass
        o = [c for c in myMps.genChars()]
        #print 'Comment removed:'
        #print o
        #print 'Line continuation removed currentString:'
        #print myMps.currentString
        self.assertEqual('\n \n', ''.join(o))
        n = [c for c in myMps.genWords()]
        #print 'idxTypeMap'
        #print myMps.idxTypeMap
        #print 'Words'
        #print n
        self.assertEqual(
            [
                ('\n', 'Unknown'),
                ('// Some comment \\\nand \\\nthe rest\n', 'C++ comment'),
                ('\n', 'Unknown'),
            ],
            n,
        )

    def test_03_00(self):
        """TestMultiPassStringMarker.test_03_00(): C++ comment using removeSetReplaceClear()."""
        myStr = '// C\n\n'
        myMps = MultiPassString.MultiPassString(StringIO.StringIO(myStr))
        # Mark comment
        for c in myMps.genChars():
            if c == '\n' and myMps.hasWord:
                # Replace by a single space
                # remove and mark
                myMps.removeSetReplaceClear(True, 'C++ comment', ' ')
            elif c == '/' and myMps.prevChar != '/':
                # Start of comment
                myMps.setMarker()
            elif myMps.wordLength == 1 and c != '/':
                myMps.clearMarker()
        # Check the result of this pass
        o = [c for c in myMps.genChars()]
        self.assertEqual(' \n', ''.join(o))
        n = [c for c in myMps.genWords()]
        self.assertEqual(
            [
                ('// C\n', 'C++ comment'),
                ('\n', 'Unknown'),
            ],
            n,
        )

    def test_03_01(self):
        """TestMultiPassStringMarker.test_03_01(): C++ comment using removeSetReplaceClear()."""
        myStr = '// C\\\n\n'
        myMps = MultiPassString.MultiPassString(StringIO.StringIO(myStr))
        o = []
        myMps.setMarker()
        for c in myMps.genChars():
            if c == '\n' and myMps.prevChar == '\\':
                myMps.removeMarkedWord(isTerm=True)
                # Note we don't myMps.setWordType('line-continuation')
                # as this is interlaced with the C++ comment.
            myMps.setMarker()
        # Check the result of this pass
        o = [c for c in myMps.genChars()]
        self.assertEqual('// C\n', ''.join(o))
        # Mark comment
        for c in myMps.genChars():
            if c == '\n' and myMps.hasWord:
                # Replace by a single space
                # remove and mark
                myMps.removeSetReplaceClear(True, 'C++ comment', ' ')
            elif c == '/' and myMps.prevChar != '/':
                # Start of comment
                myMps.setMarker()
            elif myMps.wordLength == 1 and c != '/':
                myMps.clearMarker()
        # Check the result of this pass
        o = [c for c in myMps.genChars()]
        self.assertEqual(' ', ''.join(o))
        n = [c for c in myMps.genWords()]
        self.assertEqual(
            [
                ('// C\\\n\n', 'C++ comment'),
            ],
            n,
        )

    def test_03_02(self):
        """TestMultiPassStringMarker.test_03_02(): C++ comment using removeSetReplaceClear()."""
        myStr = '// C\\\n\n\n'
        myMps = MultiPassString.MultiPassString(StringIO.StringIO(myStr))
        o = []
        myMps.setMarker()
        for c in myMps.genChars():
            if c == '\n' and myMps.prevChar == '\\':
                myMps.removeMarkedWord(isTerm=True)
                # Note we don't myMps.setWordType('line-continuation')
                # as this is interlaced with the C++ comment.
            myMps.setMarker()
        # Check the result of this pass
        o = [c for c in myMps.genChars()]
        self.assertEqual('// C\n\n', ''.join(o))
        # Mark comment
        for c in myMps.genChars():
            if c == '\n' and myMps.hasWord:
                # Replace by a single space
                # remove and mark
                myMps.removeSetReplaceClear(True, 'C++ comment', ' ')
            elif c == '/' and myMps.prevChar != '/':
                # Start of comment
                myMps.setMarker()
            elif myMps.wordLength == 1 and c != '/':
                myMps.clearMarker()
        # Check the result of this pass
        o = [c for c in myMps.genChars()]
        self.assertEqual(' \n', ''.join(o))
        n = [c for c in myMps.genWords()]
        self.assertEqual(
            [
                ('// C\\\n\n', 'C++ comment'),
                ('\n', 'Unknown'),
            ],
            n,
        )

    def test_03(self):
        """TestMultiPassStringMarker.test_03(): C++ and line continuation using removeSetReplaceClear()."""
        myStr = """
// Some comment \\
and \\
the rest

"""
        myMps = MultiPassString.MultiPassString(StringIO.StringIO(myStr))
        o = []
        for c in myMps.genChars():
            if c == '\n' and myMps.prevChar == '\\':
                myMps.removeMarkedWord(isTerm=True)
                # Note we don't myMps.setWordType('line-continuation')
                # as this is interlaced with the C++ comment.
            myMps.setMarker()
        # Check the result of this pass
        o = [c for c in myMps.genChars()]
        self.assertEqual('\n// Some comment and the rest\n\n', ''.join(o))
        # Mark comment
        for c in myMps.genChars():
            if c == '\n' and myMps.hasWord:
                # Replace by a single space
                # remove and mark
                myMps.removeSetReplaceClear(True, 'C++ comment', ' ')
            elif c == '/' and myMps.prevChar != '/':
                # Start of comment
                myMps.setMarker()
            elif myMps.wordLength == 1 and c != '/':
                myMps.clearMarker()
        # Check the result of this pass
        o = [c for c in myMps.genChars()]
        self.assertEqual('\n \n', ''.join(o))
        n = [c for c in myMps.genWords()]
        self.assertEqual(
            [
                ('\n', 'Unknown'),
                ('// Some comment \\\nand \\\nthe rest\n', 'C++ comment'),
                ('\n', 'Unknown'),
            ],
            n,
        )

    def test_04(self):
        """TestMultiPassStringMarker.test_04(): Spaces and numbers, multiple passes."""
        myStr = """ 1  12   123    1234"""
        myMps = MultiPassString.MultiPassString(StringIO.StringIO(myStr))
        # Mark whitespace
        o = []
        myMps.clearMarker()
        for c in myMps.genChars():
            o.append(c)
            if c.isspace() and not myMps.hasWord:
                # Whitespace character
                myMps.setMarker()
            elif not c.isspace():
                # Stop whitespace
                if myMps.hasWord:
                    myMps.setWordType('whitespace', isTerm=False)
                myMps.clearMarker()
        # Trailing whitespace.
        if myMps.hasWord:
            myMps.setWordType('whitespace', isTerm=False)
        wordS = [w for w in myMps.genWords()]
        #print 'Characters:'
        #print o
        #print 'idxTypeMap'
        #print myMps.idxTypeMap
        #print 'Words'
        #print wordS
        self.assertEqual(
            [
                (' ', 'whitespace'),
                ('1', 'Unknown'),
                ('  ', 'whitespace'),
                ('12', 'Unknown'),
                ('   ', 'whitespace'),
                ('123', 'Unknown'),
                ('    ', 'whitespace'),
                #('1234', 'Unknown'),
            ],
            wordS,
        )
        # Now numbers
        o = []
        myMps.clearMarker()
        for c in myMps.genChars():
            o.append(c)
            if c.isdigit() and not myMps.hasWord:
                # Digit character
                myMps.setMarker()
            elif not c.isdigit():
                # Non-digit
                if myMps.hasWord:
                    myMps.setWordType('digit', isTerm=False)
                myMps.clearMarker()
        # Trailing digits.
        if myMps.hasWord:
            myMps.setWordType('digit', isTerm=False)
        wordS = [w for w in myMps.genWords()]
        #print 'Characters:'
        #print o
        #print 'idxTypeMap'
        #print myMps.idxTypeMap
        #print 'Words'
        #pprint.pprint(wordS)
        self.assertEqual(
            [
                (' ', 'whitespace'),
                ('1', 'digit'),
                ('  ', 'whitespace'),
                ('12', 'digit'),
                ('   ', 'whitespace'),
                ('123', 'digit'),
                ('    ', 'whitespace'),
                ('1234', 'digit'),
            ],
            wordS,
        )

    def test_05(self):
        """TestMultiPassStringMarker.test_05(): Spaces and numbers, single pass."""
        myStr = """ 1  12   123    1234"""
        myMps = MultiPassString.MultiPassString(StringIO.StringIO(myStr))
        o = []
        cType = MultiPassString.MultiPassString.UNKNOWN_TOKEN_TYPE
        myMps.setMarker()
        for c in myMps.genChars():
            o.append(c)
            if c.isspace():
                # Whitespace character
                if cType != 'whitespace' and myMps.hasWord:
                    myMps.setWordType(cType, isTerm=False)
                    myMps.setMarker()
                cType = 'whitespace'
            elif c.isdigit():
                # Digit character
                # Stop anything else
                if cType != 'digit' and myMps.hasWord:
                    myMps.setWordType(cType, isTerm=False)
                    myMps.setMarker()
                cType = 'digit'
        # Trailing tokens
        if myMps.hasWord:
            myMps.setWordType(cType, isTerm=False)
        wordS = [w for w in myMps.genWords()]
        #print 'Characters:'
        #print o
        #print 'idxTypeMap'
        #print myMps.idxTypeMap
        #print 'Words'
        #pprint.pprint(wordS)
        self.assertEqual(
            [
                (' ', 'whitespace'),
                ('1', 'digit'),
                ('  ', 'whitespace'),
                ('12', 'digit'),
                ('   ', 'whitespace'),
                ('123', 'digit'),
                ('    ', 'whitespace'),
                ('1234', 'digit'),
            ],
            wordS,
        )


class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    """Execute unit tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMultiPassStringMarker))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

#################
# End: Unit tests
#################

def usage():
    """Send the help to stdout."""
    print \
"""TestMultiPassString.py - A module that tests MultiPassString module.
Usage:
python TestItuToHtml.py [-lh --help]

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
    print 'TestItuToHtml.py script version "%s", dated %s' % (__version__, __date__)
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
