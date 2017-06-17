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

import sys
#import os
import unittest
import time
import logging
import io
#import pprint

from cpip.core import PpTokeniser, FileLocation, CppDiagnostic, PpToken  
import TestBase

########################################
# Section: Unit tests
########################################

class TestPpTokeniserBase(TestBase.TestCpipBase):
    """Base class for test classes that provides common functionality."""
    def _printDiff(self, actual, expected):
        actual, expected = self._extendPair(actual, expected)
        if actual != expected:
            print()
#            print('Act:', actual)
#            print('Exp:', expected)
#            print('Map:', map)
            i = 0
            for t, e in map(lambda *args: args, actual, expected):
                if t is not None and e is not None:
                    if t != e:
                        print('%d: %s, != %s' \
                                          % (i,
                                             self.__stringiseToken(t),
                                             self.__stringiseToken(e)))
                else:
                    print('%d: %s, != %s' \
                                      % (i,
                                         self.__stringiseToken(t),
                                         self.__stringiseToken(e)))
                i += 1

    def __stringiseToken(self, theTtt):
        return str(theTtt).replace('\n', '\\n')

    def pprintTokensAsCtors(self, theList):
        """Pretty prints the list as PpToken constructors."""
        for aTtt in theList:
            print('PpToken.PpToken(\'%s\', \'%s\'),' % (aTtt.t.replace('\n', '\\n'), aTtt.tt))

class TestWordsFoundIn(TestPpTokeniserBase):
    """Tests PpTokeniser._wordFoundIn()."""

    def testWordFoundIn_00(self):
        """PpTokeniser._wordFoundIn_00()"""
        myObj = PpTokeniser.PpTokeniser()
        # Found
        self.assertEqual(0, myObj._wordFoundInUpTo('Hello world', 11, 'Hello'))
        self.assertEqual(6, myObj._wordFoundInUpTo('Hello world', 11, 'world'))
        # Not found
        self.assertEqual(-1, myObj._wordFoundInUpTo('Hello world', 11, 'earth'))
        self.assertEqual(-1, myObj._wordFoundInUpTo('Hello world', 11, ''))
        self.assertEqual(-1, myObj._wordFoundInUpTo('Hello world', 11, 'worldly'))

    def testWordsFoundIn_01(self):
        """PpTokeniser._wordsFoundIn_01()"""
        myObj = PpTokeniser.PpTokeniser()
        # Found
        self.assertEqual(0, myObj._wordsFoundInUpTo('Hello world', 11,
                                               ('Hello', 'world')))
        self.assertEqual(6, myObj._wordsFoundInUpTo('Hello world', 11,
                                               ('world', 'Hello')))
        self.assertNotEqual(-1, myObj._wordsFoundInUpTo('Hello world', 11,
                                               set(('world', 'Hello'))))
        # Not found
        self.assertEqual(-1, myObj._wordsFoundInUpTo('Hello world', 11,
                                                ('', 'earth', 'worldly')))
        self.assertEqual(-1, myObj._wordsFoundInUpTo('Hello world', 11,
                                                set(('', 'earth', 'worldly'))))

class TestWordsFoundInUpTo(TestPpTokeniserBase):
    """Tests PpTokeniser._wordFoundInUpTo().
    TODO: More tests with different lengths."""

    def testWordFoundInUpTo_00(self):
        """PpTokeniser._wordFoundInUpTo_00()"""
        myObj = PpTokeniser.PpTokeniser()
        # Found
        self.assertEqual(0, myObj._wordFoundInUpTo('Hello world', 11, 'Hello'))
        self.assertEqual(6, myObj._wordFoundInUpTo('Hello world', 11, 'world'))
        # Not found
        self.assertEqual(-1, myObj._wordFoundInUpTo('Hello world', 11, 'earth'))
        self.assertEqual(-1, myObj._wordFoundInUpTo('Hello world', 11, ''))
        self.assertEqual(-1, myObj._wordFoundInUpTo('Hello world', 11, 'worldly'))
        # Found/not found - constrained
        self.assertEqual(6, myObj._wordFoundInUpTo('Hello world', 10, 'worl'))
        self.assertEqual(-1, myObj._wordFoundInUpTo('Hello world', 10, 'world'))

    def testWordsFoundInUpTo_01(self):
        """PpTokeniser._wordFoundInUpTo_01()"""
        myObj = PpTokeniser.PpTokeniser()
        # Found
        self.assertEqual(0, myObj._wordsFoundInUpTo('Hello world', 11,
                                               ('Hello', 'world')))
        self.assertEqual(6, myObj._wordsFoundInUpTo('Hello world', 11,
                                               ('world', 'Hello')))
        # NOTE: assertNotEqual()
        self.assertNotEqual(-1, myObj._wordsFoundInUpTo('Hello world', 11,
                                               set(('world', 'Hello'))))
        # Not found
        self.assertEqual(-1, myObj._wordsFoundInUpTo('Hello world', 11,
                                                ('', 'earth', 'worldly')))
        self.assertEqual(-1, myObj._wordsFoundInUpTo('Hello world', 11,
                                                set(('', 'earth', 'worldly'))))

class TestPpTokeniserTrigraphs(TestPpTokeniserBase):
    """Tests Trigraph replacement."""

    #def _retAbsPair(self, thePair):
    #    return FileLocation.START_LINE+thePair[0], FileLocation.START_COLUMN+thePair[1]

    #def assertRelativePosition(self, theObj, logicalPair, physicalPair):
    #    """Converts logical and physical from relative to absolute and asserts that they are equal
    #    after translation."""
    #    self.assertEqual(
    #        (FileLocation.START_LINE+physicalPair[0], FileLocation.START_COLUMN+physicalPair[1]),
    #        theObj.fileLocator.logicalToPhysical(FileLocation.START_LINE+logicalPair[0],
    #                                             FileLocation.START_COLUMN++logicalPair[1])
    #        )

    def setUp(self):
        pass

    def testTrigraphs_00(self):
        """ISO/IEC 14882:1998(E) 2.3 Trigraph sequences [lex.trigraphs] - single replacement."""
        myObj = PpTokeniser.PpTokeniser()
        mySrc = ['??=',]
        myObj._translateTrigraphs(mySrc)
        self.assertEqual(['#',], mySrc)
        #print
        #print str(myObj._fileLocator.logicalPhysicalLineMap)
        self.assertEqual(
            (FileLocation.START_LINE+1, FileLocation.START_COLUMN),
            myObj.fileLocator.pLineCol
            )
        self.assertEqual(
            (FileLocation.START_LINE, FileLocation.START_COLUMN),
            myObj.fileLocator.logicalToPhysical(FileLocation.START_LINE, FileLocation.START_COLUMN)
            )

    def testTrigraphs_01(self):
        """ISO/IEC 14882:1998(E) 2.3 Trigraph sequences [lex.trigraphs] - double replacement[0]."""
        myObj = PpTokeniser.PpTokeniser()
        mySrc = ['??=??(',]
        myObj._translateTrigraphs(mySrc)
        self.assertEqual(['#[',], mySrc)
        #print
        #print str(myObj._fileLocator.logicalPhysicalLineMap)
        # Check current physical file position
        self.assertEqual(
            (FileLocation.START_LINE+1, FileLocation.START_COLUMN),
            myObj.fileLocator.pLineCol
            )
        self.assertEqual(
            (FileLocation.START_LINE, FileLocation.START_COLUMN),
            myObj.fileLocator.logicalToPhysical(FileLocation.START_LINE, FileLocation.START_COLUMN)
            )
        self.assertEqual(
            (FileLocation.START_LINE, FileLocation.START_COLUMN+3),
            myObj.fileLocator.logicalToPhysical(FileLocation.START_LINE, FileLocation.START_COLUMN+1)
            )

    def testTrigraphs_02(self):
        """ISO/IEC 14882:1998(E) 2.3 Trigraph sequences [lex.trigraphs] - double replacement[1]."""
        myObj = PpTokeniser.PpTokeniser()
        # This is from ISO/IEC 14882:1998(E) 2.3 Trigraph sequences [lex.trigraphs] note 2
        myPStr = ['??=??(',]
        myLStr = ['#[',]
        myObj._translateTrigraphs(myPStr)
        self.assertEqual(myPStr, myLStr)
        #print
        #print str(myObj._fileLocator)
        #print 'Physical:', myPStr
        #print ' Logical:', myLStr
        #myObj.fileLocator.pprintLogicalToPhysical(myLStr, myPStr)

    def testTrigraphs_03(self):
        """ISO/IEC 14882:1998(E) 2.3 Trigraph sequences [lex.trigraphs] - triple replacement[0]."""
        myObj = PpTokeniser.PpTokeniser()
        # This is from ISO/IEC 14882:1998(E) 2.3 Trigraph sequences [lex.trigraphs] note 2
        myPStr = ['??=??(??)',]
        myLStr = ['#[]',]
        myObj._translateTrigraphs(myPStr)
        self.assertEqual(myPStr, myLStr)
        #print
        #print str(myObj._fileLocator)
        #print 'Physical:', myPStr
        #print ' Logical:', myLStr
        #myObj.fileLocator.pprintLogicalToPhysical(myLStr, myPStr)

    def testTrigraphs_05(self):
        """ISO/IEC 14882:1998(E) 2.3 Trigraph sequences [lex.trigraphs] - five replacement[0]."""
        myObj = PpTokeniser.PpTokeniser()
        # This is from ISO/IEC 14882:1998(E) 2.3 Trigraph sequences [lex.trigraphs] note 2
        myPStr = ['??=??(??)??(??)',]
        myLStr = ['#[][]',]
        myObj._translateTrigraphs(myPStr)
        self.assertEqual(myPStr, myLStr)
        #print
        #print str(myObj._fileLocator)
        #print 'Physical:', myPStr
        #print ' Logical:', myLStr
        #myObj.fileLocator.pprintLogicalToPhysical(myLStr, myPStr)

    def testTrigraphs_10(self):
        """ISO/IEC 14882:1998(E) 2.3 Trigraph sequences [lex.trigraphs] - multiple replacement."""
        myObj = PpTokeniser.PpTokeniser()
        # This is from ISO/IEC 14882:1998(E) 2.3 Trigraph sequences [lex.trigraphs] note 2
        myPStr = ['??=define arraycheck(a,b) a??(b??) ??!??! b??(a??)',]
        myLStr = ['#define arraycheck(a,b) a[b] || b[a]',]
        myObj._translateTrigraphs(myPStr)
        self.assertEqual(myPStr, myLStr)
        #print
        #print str(myObj._fileLocator)
        #print 'Physical:', myPStr
        #print ' Logical:', myLStr
        #myObj._fileLocator.pprintLogicalToPhysical(myLStr, myPStr)
        """FileLocation: Logical -> Physical
(    1,   1) -> (    1,   1) # != ?
(    1,   2) -> (    1,   4) d == d
(    1,   3) -> (    1,   5) e == e
(    1,   4) -> (    1,   6) f == f
(    1,   5) -> (    1,   7) i == i
(    1,   6) -> (    1,   8) n == n
(    1,   7) -> (    1,   9) e == e
(    1,   8) -> (    1,  10)   ==
(    1,   9) -> (    1,  11) a == a
(    1,  10) -> (    1,  12) r == r
(    1,  11) -> (    1,  13) r == r
(    1,  12) -> (    1,  14) a == a
(    1,  13) -> (    1,  15) y == y
(    1,  14) -> (    1,  16) c == c
(    1,  15) -> (    1,  17) h == h
(    1,  16) -> (    1,  18) e == e
(    1,  17) -> (    1,  19) c == c
(    1,  18) -> (    1,  20) k == k
(    1,  19) -> (    1,  21) ( == (
(    1,  20) -> (    1,  22) a == a
(    1,  21) -> (    1,  23) , == ,
(    1,  22) -> (    1,  24) b == b
(    1,  23) -> (    1,  25) ) == )
(    1,  24) -> (    1,  26)   ==
(    1,  25) -> (    1,  27) a == a
(    1,  26) -> (    1,  28) [ != ?
(    1,  27) -> (    1,  31) b == b
(    1,  28) -> (    1,  32) ] != ?
(    1,  29) -> (    1,  35)   ==
(    1,  30) -> (    1,  36) | != ?
(    1,  31) -> (    1,  39) | != ?
(    1,  32) -> (    1,  42)   ==
(    1,  33) -> (    1,  43) b == b
(    1,  34) -> (    1,  44) [ != ?
(    1,  35) -> (    1,  47) a == a
(    1,  36) -> (    1,  48) ] != ?"""
        self.assertEqual((FileLocation.START_LINE+1, FileLocation.START_COLUMN), myObj.fileLocator.pLineCol)
        # Test positional informaton - well some of them
        self.assertEqual(myObj.fileLocator.logicalToPhysical(1,1), (1,1))
        self.assertEqual(myObj.fileLocator.logicalToPhysical(1,2), (1,4))
        self.assertEqual(myObj.fileLocator.logicalToPhysical(1,26), (1,28))
        self.assertEqual(myObj.fileLocator.logicalToPhysical(1,27), (1,31))
        self.assertEqual(myObj.fileLocator.logicalToPhysical(1,28), (1,32))
        self.assertEqual(myObj.fileLocator.logicalToPhysical(1,29), (1,35))
        self.assertEqual(myObj.fileLocator.logicalToPhysical(1,36), (1,48))

class TestPpTokeniserDigraphs(TestPpTokeniserBase):
    """Tests Digraph replacement."""
    
    """ From the standard.
Digraph table:
('<%', '{'),
('and', '&&'),
('and_eq', '&='), 
('%>', '}'),
('bitor', '|'),
('or_eq', '|='), 
('<:', '['),
('or', '||'),
('xor_eq', '^='), 
(':>', ']'),
('xor', '^'),
('not', '!'), 
('%:', '#'),
('compl', '~'),
('not_eq', '!='), 
('%:%:', '##'),
('bitand', '&'), 

Digraph keys:
'<%',
'and',
'and_eq', 
'%>',
'bitor',
'or_eq', 
'<:',
'or',
'xor_eq', 
':>',
'xor',
'not', 
'%:',
'compl',
'not_eq', 
'%:%:',
'bitand', 

Digraph values:
'{',
'&&',
'&=', 
'}',
'|',
'|=', 
'[',
'||',
'^=', 
']',
'^',
'!', 
'#',
'~',
'!=', 
'##',
'&', 

"""
    
    def setUp(self):
        pass

    def testDigraphs_00(self):
        """ISO/IEC 14882:1998(E) 2.5 Alternative tokens [lex.digraph] test[00]"""
        myStr = u"""and
bitand
<%
"""
        myObj = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myToks = [t for t in myObj.next()]
#        print
#        self.pprintTokensAsCtors(myToks)
        self.assertEqual(
                myToks,
                [
                    PpToken.PpToken('and',      'identifier'),
                    PpToken.PpToken('\n',       'whitespace'),
                    PpToken.PpToken('bitand',   'identifier'),
                    PpToken.PpToken('\n',       'whitespace'),
                    PpToken.PpToken('<%',       'preprocessing-op-or-punc'),
                    PpToken.PpToken('\n',       'whitespace'),
                ]
                )        
        for i in range (len(myToks)):
            myToks[i] = myObj.substAltToken(myToks[i])
#        print
#        self.pprintTokensAsCtors(myToks)
        self.assertEqual(
            myToks,
            [
                PpToken.PpToken('&&', 'preprocessing-op-or-punc'),
                PpToken.PpToken('\n', 'whitespace'),
                PpToken.PpToken('&', 'preprocessing-op-or-punc'),
                PpToken.PpToken('\n', 'whitespace'),
                PpToken.PpToken('{', 'preprocessing-op-or-punc'),
                PpToken.PpToken('\n', 'whitespace'),
            ]
        )        

    def testDigraphs_02(self):
        """ISO/IEC 14882:1998(E) 2.5 Alternative tokens [lex.digraph]. Test 02, file location."""
        myStr = u"""and
bitand
"""
        myObj = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(myStr)
            )
        myToks = [t for t in myObj.next()]
        #print
        #self.pprintTokensAsCtors(myToks)
        self.assertEqual(
                myToks,
                [
                    PpToken.PpToken('and', 'identifier'),
                    PpToken.PpToken('\n', 'whitespace'),
                    PpToken.PpToken('bitand', 'identifier'),
                    PpToken.PpToken('\n', 'whitespace'),
                ]
            )        
        # Test file locator information
        #print
        #print str(myObj.fileLocator.logicalPhysicalLineMap)
        #pprint.pprint(myObj.fileLocator.logicalPhysicalLineMap._ir)
        myLpMap = myObj.fileLocator.logicalPhysicalLineMap
        # Logical (0,0) maps to physical (0,0)
        pLine, pCol = myLpMap.pLineCol(
                                       FileLocation.START_LINE,
                                       FileLocation.START_COLUMN
                                       )
        self.assertEqual(FileLocation.START_LINE, pLine)
        self.assertEqual(FileLocation.START_COLUMN, pCol)
        # Logical (0,3) maps to physical (0,2)        
        pLine, pCol = myLpMap.pLineCol(
                                       FileLocation.START_LINE+0,
                                       FileLocation.START_COLUMN+2
                                       )
        self.assertEqual(FileLocation.START_LINE, pLine)
        self.assertEqual(FileLocation.START_COLUMN+2, pCol)
        # Logical (1,0) maps to physical (1,0)
        pLine, pCol = myLpMap.pLineCol(
                                       FileLocation.START_LINE+1,
                                       FileLocation.START_COLUMN
                                       )
        self.assertEqual(FileLocation.START_LINE+1, pLine)
        self.assertEqual(FileLocation.START_COLUMN, pCol)
        # TODO: Fix this as the test is wrong!
        # Logical (1,3) maps to physical (1,6)        
        pLine, pCol = myLpMap.pLineCol(
                                       FileLocation.START_LINE+1,
                                       FileLocation.START_COLUMN+3
                                       )
        self.assertEqual(FileLocation.START_LINE+1, pLine)
        self.assertEqual(FileLocation.START_COLUMN+3, pCol)
#===============================================================================
#        print 'Line 0:'
#        for c in range(10):
#            pLine, pCol = myLpMap.pLineCol(
#                                           FileLocation.START_LINE+0,
#                                           FileLocation.START_COLUMN+c
#                                           )
#            print 'Logical %d -> Physical %d' % (FileLocation.START_COLUMN+c, pCol)
#        print 'Line 1:'
#        for c in range(10):
#            pLine, pCol = myLpMap.pLineCol(
#                                           FileLocation.START_LINE+1,
#                                           FileLocation.START_COLUMN+c
#                                           )
#            print 'Logical %d -> Physical %d' % (FileLocation.START_COLUMN+c, pCol)
#===============================================================================

    def testDigraphs_10(self):
        """ISO/IEC 14882:1998(E) 2.5 Alternative tokens [lex.digraph]. Test 10, test all Digraphs."""
        myStr = u'\n'.join(list(PpTokeniser.DIGRAPH_TABLE.keys()))
        #print
        #print 'Input:'
        #print myStr
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs(myStr)
        myToks = [t for t in myGen]
        #print
        #for t in myToks:
        #    print t
        #self.pprintTokensAsCtors(myToks)

#===============================================================================
#    def testDigraphs_11(self):
#        """ISO/IEC 14882:1998(E) 2.5 Alternative tokens [lex.digraph]. Test 11, test all Digraphs."""
#        myStr = u'\n'.join(PpTokeniser.DIGRAPH_TABLE.keys())
#        myGen = myObj.genLexPptokenAndSeqWs('/* */')
#        myToks = [t for t in myGen]
#        
#        print
#        print 'Input:'
#        print myStr
#        myObj = PpTokeniser.PpTokeniser(
#            theFileObj=StringIO.StringIO(myStr)
#            )
#        #initLexPhase12
#        myToks = [t for t in myObj.next()]
#        print
#        for t in myToks:
#            print t
#        self.pprintTokensAsCtors(myToks)
#===============================================================================

class TestExpressionLexComment(TestPpTokeniserBase):
    """Test comment identification."""

    def testLexCommentCComplete(self):
        """ISO/IEC 14882:1998(E) 2.7 Header names [lex.comment] C comments complete."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLexComment(list('/**/')))
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexComment(list('/* */')))
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexComment(list('/* */   */')))
        myObj.resetTokType()
        self.assertEqual(8, myObj._sliceLexComment(list('/* // */')))
        myObj.resetTokType()
        self.assertEqual(8, myObj._sliceLexComment(list('/* // */ ')))

    def testLexCommentCIncomplete(self):
        """ISO/IEC 14882:1998(E) 2.7 Header names [lex.comment] C comments incomplete."""
        myObj = PpTokeniser.PpTokeniser()
        # Failures
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexComment(list(' /**/')))
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexComment(list('/ **/')))
        myStr = u'/*'
        myObj.resetTokType()
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                          myObj._sliceLexComment, list(myStr))
        myStr = u'/* *  '
        myObj.resetTokType()
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                          myObj._sliceLexComment, list(myStr))
        myStr = u'/* * /'
        myObj.resetTokType()
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                          myObj._sliceLexComment, list(myStr))

    def testLexCommentCplusplusComplete(self):
        """ISO/IEC 14882:1998(E) 2.7 Header names [lex.comment] C++ comments complete."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceLexComment(list('//\n')))
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLexComment(list('// \n')))
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLexComment(list('//  \n')))

    def testLexCommentCplusplusIncomplete(self):
        """ISO/IEC 14882:1998(E) 2.7 Header names [lex.comment] C++ comments incomplete."""
        myObj = PpTokeniser.PpTokeniser()
        # Failures
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexComment(list(' //')))
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexComment(list('/ /')))
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexComment(list(' //  ')))
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexComment(list('/ /  ')))
        myStr = u'//'
        myObj.resetTokType()
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                          myObj._sliceLexComment, list(myStr))
        myStr = u'// '
        myObj.resetTokType()
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                          myObj._sliceLexComment, list(myStr))
        myStr = u'//  '
        myObj.resetTokType()
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                          myObj._sliceLexComment, list(myStr))

class TestExpressionLexHeader(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexHeader(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(myObj.cppTokType, None)
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexHeader(list('"std.h"')))
        self.assertEqual(myObj.cppTokType, 'header-name')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexHeader(list('<std.h>')))
        self.assertEqual(myObj.cppTokType, 'header-name')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexHeader(list('"std.h" ')))
        self.assertEqual(myObj.cppTokType, 'header-name')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexHeader(list('<std.h>   ')))
        self.assertEqual(myObj.cppTokType, 'header-name')

    def testLexHeader_00(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] with \\ and / characters."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(myObj.cppTokType, None)
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexHeader(list('"st/.h"')))
        self.assertEqual(myObj.cppTokType, 'header-name')
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexHeader(list('"st\\.h" ')))
        self.assertEqual(myObj.cppTokType, None)
        myObj.resetTokType()

    def testLexHeader_fail(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - partial headers that fail."""
        myObj = PpTokeniser.PpTokeniser()
        self.assertEqual(myObj.cppTokType, None)
        # Failures
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexHeader(list('"std.h>')))
        self.assertEqual(myObj.cppTokType, None)
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexHeader(list('<std.h"')))
        self.assertEqual(myObj.cppTokType, None)
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexHeader(list('"std.h')))
        self.assertEqual(myObj.cppTokType, None)
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexHeader(list('<std.h')))
        self.assertEqual(myObj.cppTokType, None)

    def testLexHeaderWithNull(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - q-char-sequence with null char."""
        myObj = PpTokeniser.PpTokeniser()
        self.assertEqual(0, myObj._sliceLexHeader(list("abc\0xyz")))

    def testLexHeaderHcharSeq(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - h-char-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(5, myObj._sliceLexHeaderHcharSequence(list('std.h'), 0))
        self.assertEqual(8, myObj._sliceLexHeaderHcharSequence(list('std.h   '), 0))
        # Failures
        for aWord in set(('\'', '\\', '/*', '//', '"')):
            myStr = u'std%s.h' % aWord
            self.assertEqual(0, myObj._sliceLexHeaderHcharSequence(list(myStr), 0))

    def testLexHeaderQcharSeq(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - q-char-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexHeaderQcharSequence(list('std.h'), 0))
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexHeaderQcharSequence('std.h', 0))
        myObj.resetTokType()
        self.assertEqual(8, myObj._sliceLexHeaderQcharSequence(list('std.h   '), 0))
        # Failures
        for aWord in set(('\'', '\\', '//', '/*')):
            myStr = """std%s.h""" % aWord
            self.assertEqual(0, myObj._sliceLexHeaderQcharSequence(list(myStr), 0))

    def testLexHeaderHcharSeqExceptionString(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - h-char-sequence, bad characters."""
        myObj = PpTokeniser.PpTokeniser()
        for aWord in set(('\'', '\\', '"', '//', '/*')):
            myStr = u"""std%s.h""" % aWord
            self.assertEqual(0, myObj._sliceLexHeaderHcharSequence(list(myStr), 0))
            #try:
            #    self.assertEqual(5, myObj._sliceLexHeaderHcharSequence(list("std%s.h" % aWord)))
            #    self.fail('Excepton not raised')
            #except PpTokeniser.ExceptionCpipTokeniserUndefinedLocal, err:
            #    self.assertEqual('[\'s\', \'t\', \'d\', "\'", \'.\', \'h\'] [3]', str(err))

    def testLexHeaderQcharSeqExceptionString(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - q-char-sequence bad characters."""
        myObj = PpTokeniser.PpTokeniser()
        for aWord in set(('\'', '\\', '/*', '//')):
            self.assertEqual(0, myObj._sliceLexHeaderQcharSequence(list("std%s.h" % aWord), 0))
            #try:
            #    self.assertEqual(5, myObj._sliceLexHeaderQcharSequence(list("std%s.h" % aWord)))
            #    self.fail('Excepton not raised')
            #except PpTokeniser.ExceptionCpipTokeniserUndefinedLocal, err:
            #    self.assertEqual('[\'s\', \'t\', \'d\', "\'", \'.\', \'h\'] [3]', str(err))

    def testLexHeaderWithDirectorySeperatorBackslash(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - h/q-char-sequence with \\ fails."""
        myObj = PpTokeniser.PpTokeniser()
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexHeader(list('"inc\\src.h"')))
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexHeader(list('<inc\\src.h>')))

    def testLexHeaderWithDirectorySeperatorForwardslash(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - h/q-char-sequence with / succeeds."""
        myObj = PpTokeniser.PpTokeniser()
        myObj.resetTokType()
        self.assertEqual(11, myObj._sliceLexHeader(list('"inc/src.h"')))
        myObj.resetTokType()
        self.assertEqual(11, myObj._sliceLexHeader(list('<inc/src.h>')))

class TestExpressionLexPpnumber(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexPpnumber(self):
        """ISO/IEC 14882:1998(E) 2.9 Preprocessing numbers [lex.ppnumber]."""
        #pp-number:
        #digit
        #. digit
        #pp-number digit
        #pp-number nondigit
        #pp-number e sign
        #pp-number E sign
        #pp-number .
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(1, myObj._sliceLexPpnumber(list('1')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceLexPpnumber(list('.1')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexPpnumber(list('1.234')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexPpnumber(list('1.234e+')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexPpnumber(list('1.234E+')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexPpnumber(list('1.234e-')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexPpnumber(list('1.234E-')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(9, myObj._sliceLexPpnumber(list('1.234E-89')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(12, myObj._sliceLexPpnumber(list('1.234E-89e+4')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLexPpnumber(list('9ab')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceLexPpnumber(list('1U')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceLexPpnumber(list('1L')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLexPpnumber(list('1UL')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(1, myObj._sliceLexPpnumber('1   '))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceLexPpnumber('.1 '))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexPpnumber('1.234      '))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        # An odd case allowed by the standard
        myObj.resetTokType()
        self.assertEqual(8, myObj._sliceLexPpnumber('1.2.3.4.      '))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        # Failures
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexPpnumber(list('L')))

class TestExpressionLexName(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexName(self):
        """ISO/IEC 14882:1998(E) 2.10 Identifiers [lex.name]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLexName(list('ab_9'), 0))
        self.assertEqual(myObj.cppTokType, 'identifier')
        myObj.resetTokType()
        self.assertEqual(10, myObj._sliceLexName(list('ab_9\\u0123'), 0))
        self.assertEqual(myObj.cppTokType, 'identifier')
        myObj.resetTokType()
        self.assertEqual(10, myObj._sliceLexName(list('ab_\\u01239'), 0))
        self.assertEqual(myObj.cppTokType, 'identifier')
        # Failures
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexName(list('9ab'), 0))
        self.assertEqual(myObj.cppTokType, None)
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexName(list(' ab'), 0))
        self.assertEqual(myObj.cppTokType, None)

class TestExpressionLexKey(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexName(self):
        """ISO/IEC 14882:1998(E) 2.11 Keywords [lex.key]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(5, myObj._sliceLexKey(list('const')))
        self.assertEqual(10, myObj._sliceLexKey(list('const_cast')))
        # Failures
        self.assertEqual(0, myObj._sliceLexKey(list('9ab')))
        self.assertEqual(0, myObj._sliceLexKey(list(' ab')))

class TestExpressionLexOperators(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexOperators(self):
        """ISO/IEC 14882:1998(E) 2.12 Operators and punctuators [lex.operators]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceLexOperators(list('<<')))
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLexOperators(list('<<=')))
        myObj.resetTokType()
        self.assertEqual(1, myObj._sliceLexOperators(list('( )\n')))
        myObj.resetTokType()
        self.assertEqual(1, myObj._sliceLexOperators(list('(')))
        # Failures
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexOperators(list('9ab')))
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexOperators(list(' ab')))

class TestExpressionLexCharset(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexCharsetHexQuad(self):
        """ISO/IEC 14882:1998(E) 2.2 Character sets [lex.charset] - hex-quad."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(4, myObj._sliceHexQuad(list('0123')))
        self.assertEqual(4, myObj._sliceHexQuad(list('1234')))
        self.assertEqual(4, myObj._sliceHexQuad(list('abcd')))
        self.assertEqual(4, myObj._sliceHexQuad(list('EEFF')))
        # Failures

    def testLexCharsetHexQuad_fail_prefix(self):
        """ISO/IEC 14882:1998(E) 2.2 Character sets [lex.charset] - hex-quad, bad prefix."""
        myObj = PpTokeniser.PpTokeniser()
        # Space prefix
        self.assertEqual(0, myObj._sliceHexQuad(list('  abcd')))

    def testLexCharsetHexQuad_fail_short(self):
        """ISO/IEC 14882:1998(E) 2.2 Character sets [lex.charset] - hex-quad, too short."""
        myObj = PpTokeniser.PpTokeniser()
        # Not enough characters
        self.assertEqual(0, myObj._sliceHexQuad(list('')))
        self.assertEqual(0, myObj._sliceHexQuad(list('0')))
        self.assertEqual(0, myObj._sliceHexQuad(list('01')))
        self.assertEqual(0, myObj._sliceHexQuad(list('012')))

    def testLexCharsetUniversalCharacterName(self):
        """ISO/IEC 14882:1998(E) 2.2 Character sets [lex.charset] - universal-character-name."""
        # \u hex-quad
        # \U hex-quad hex-quad
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        #print dir(myObj)
        self.assertEqual(6, myObj._PpTokeniser__sliceUniversalCharacterName(list('\\u0123')))
        self.assertEqual(6, myObj._PpTokeniser__sliceUniversalCharacterName(list('\\u1234')))
        self.assertEqual(6, myObj._PpTokeniser__sliceUniversalCharacterName(list('\\uabcd')))
        self.assertEqual(6, myObj._PpTokeniser__sliceUniversalCharacterName(list('\\uEEFF')))
        self.assertEqual(10, myObj._PpTokeniser__sliceUniversalCharacterName(list('\\U0123DEFA')))
        self.assertEqual(10, myObj._PpTokeniser__sliceUniversalCharacterName(list('\\U1234abcd')))
        self.assertEqual(10, myObj._PpTokeniser__sliceUniversalCharacterName(list('\\Uabcd0124')))
        self.assertEqual(10, myObj._PpTokeniser__sliceUniversalCharacterName(list('\\UEEFF01234')))
        # Failures
        # Space prefix
        self.assertEqual(0, myObj._PpTokeniser__sliceUniversalCharacterName(list('  abcd')))

class TestExpressionLexLiteral(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexLiteral(self):
        """ISO/IEC 14882:1998(E) 2.13 Literals [lex.literal]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        # Integers
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLiteral(list('01234')))
        # Character
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLiteral(list("'a'")))
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLiteral(list("L'a'")))
        # Floating
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLiteral(list('123.456')))
        myObj.resetTokType()
        self.assertEqual(10, myObj._sliceLiteral(list('123.456e12')))
        myObj.resetTokType()
        self.assertEqual(11, myObj._sliceLiteral(list('123.456e12f')))
        myObj.resetTokType()
        self.assertEqual(8, myObj._sliceLiteral(list('123.456f')))
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceLiteral(list('123e12')))
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLiteral(list('123e12L')))
        # String
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceStringLiteral(list('""'), 0))
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceLiteral(list('""')))
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLiteral(list('L""')))
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLiteral(list('"abc"')))
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceLiteral(list('L"abc"')))
        # Bool
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLiteral(list('true')))
        # Failures
        # Space prefix
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLiteral(list(' 0123')))
        # Special
        myObj.resetTokType()
        myStr = u"""\"  New class `%s' (sec=0x%08x)! #tArgLists=%d\\n",
            fullName.data(),root->section,root->tArgLists ? (int)root->tArgLists->count() : -1);"""
        myLines = myStr.splitlines(True)
        myObj._convertToLexCharset(myLines)
        #print
        #print myLines
        self.assertEqual(48, myObj._sliceStringLiteral(''.join(myLines), 0))

    def testLexLiteralUcnOrdinals_string(self):
        """ISO/IEC 14882:1998(E) 2.13 Literals [lex.literal] with UCN Ordinals in string literals."""
        myObj = PpTokeniser.PpTokeniser()
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLiteral('"$"'))
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLiteral('"@"'))
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLiteral('"`"'))
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLiteral('"$@`"'))
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLiteral('"$@`"   \n'))

    def testLexLiteralUcnOrdinals_string_wide(self):
        """ISO/IEC 14882:1998(E) 2.13 Literals [lex.literal] with UCN Ordinals in wide string literals."""
        myObj = PpTokeniser.PpTokeniser()
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLiteral('L"$"'))
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLiteral('L"@"'))
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLiteral('L"`"'))
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceLiteral('L"$@`"'))
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceLiteral('L"$@`"   \n'))

    def testLexLiteralUcnOrdinals_char(self):
        """ISO/IEC 14882:1998(E) 2.13 Literals [lex.literal] with UCN Ordinals in character literals."""
        myObj = PpTokeniser.PpTokeniser()
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLiteral("'$'"))
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLiteral("'@'"))
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLiteral("'`'"))
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLiteral("'$@`'"))
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLiteral("'$@`'       "))

    def testLexLiteralUcnOrdinals_char_wide(self):
        """ISO/IEC 14882:1998(E) 2.13 Literals [lex.literal] with UCN Ordinals in wide character literals."""
        myObj = PpTokeniser.PpTokeniser()
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLiteral("L'$'"))
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLiteral("L'@'"))
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLiteral("L'`'"))
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceLiteral("L'$@`'"))
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceLiteral("L'$@`'       "))

class TestExpressionLexIcon(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexIcon(self):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        # Decimal
        self.assertEqual(1, myObj._sliceIntegerLiteral(list('1')))
        self.assertEqual(4, myObj._sliceIntegerLiteral(list('1234')))
        # Hex
        self.assertEqual(3, myObj._sliceIntegerLiteral(list('0x1')))
        self.assertEqual(5, myObj._sliceIntegerLiteral(list('0xAa1')))
        # Octal
        self.assertEqual(2, myObj._sliceIntegerLiteral(list('01')))
        self.assertEqual(3, myObj._sliceIntegerLiteral(list('001')))
        self.assertEqual(3, myObj._sliceIntegerLiteral(list('007')))
        # Suffixes
        # Decimal
        self.assertEqual(2, myObj._sliceIntegerLiteral(list('1U')))
        # Hex
        self.assertEqual(3, myObj._sliceIntegerLiteral(list('0x1')))
        # Octal
        self.assertEqual(3, myObj._sliceIntegerLiteral(list('001')))
        # Failures
        # C spec says "An octal constant consists of the prefix 0 optionally
        # followed by a sequence of the digits 0 through 7 only."
        self.assertEqual(1, myObj._sliceIntegerLiteral(list('0')))
        # Space prefix
        self.assertEqual(0, myObj._sliceIntegerLiteral(list(' 0123')))
        # Alpha
        self.assertEqual(0, myObj._sliceIntegerLiteral(list('abc')))
        # Empty
        self.assertEqual(0, myObj._sliceIntegerLiteral(list('')))
        # Space
        self.assertEqual(0, myObj._sliceIntegerLiteral(list(' 1')))
        # Bad hex
        self.assertEqual(0, myObj._sliceIntegerLiteral(list('ff')))
        # If I say:
        # int i = 08;
        # What happens?
        # Compiler says bad octal but for the preprocessor this is
        # octal 0 followed by decimal 8
        self.assertEqual(1, myObj._sliceIntegerLiteral(list('08')))

    def testLexIconDecimalLiteral(self):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - decimal-literal."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._sliceDecimalLiteral(list('1')))
        self.assertEqual(3, myObj._sliceDecimalLiteral(list('123')))
        self.assertEqual(10, myObj._sliceDecimalLiteral(list('1234567890')))
        self.assertEqual(10, myObj._sliceDecimalLiteral(list('1234567890abcdef')))
        self.assertEqual(10, myObj._sliceDecimalLiteral(list('1234567890 and something else')))
        # Failures
        # Leading zero
        self.assertEqual(0, myObj._sliceDecimalLiteral(list('0')))
        self.assertEqual(0, myObj._sliceDecimalLiteral(list('0123')))
        # Hex
        self.assertEqual(0, myObj._sliceDecimalLiteral(list('0x123')))
        self.assertEqual(0, myObj._sliceDecimalLiteral(list('0X123')))
        # Out of range
        self.assertEqual(0, myObj._sliceDecimalLiteral(list('a1F')))
        # Space prefix
        self.assertEqual(0, myObj._sliceDecimalLiteral(list(' 0123')))
        # Alpha
        self.assertEqual(0, myObj._sliceDecimalLiteral(list('abc')))

    def testLexIconOctalLiteral(self):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - octal-literal."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        # NOTE: "0" is octal literal 0, see ISO/IEC 14882:1998(E) 2.13.1
        self.assertEqual(1, myObj._sliceOctalLiteral(list('0')))
        self.assertEqual(2, myObj._sliceOctalLiteral(list('01')))
        self.assertEqual(4, myObj._sliceOctalLiteral(list('0123')))
        self.assertEqual(8, myObj._sliceOctalLiteral(list('01234567')))
        self.assertEqual(4, myObj._sliceOctalLiteral(list('0123 and something else')))
        # Failures
        # No leading zero
        self.assertEqual(0, myObj._sliceOctalLiteral(list('1')))
        self.assertEqual(0, myObj._sliceOctalLiteral(list('123')))
        # Out of range
        self.assertEqual(0, myObj._sliceOctalLiteral(list('99')))
        # This is octal 0 and the 8 is unconsumed
        self.assertEqual(1, myObj._sliceOctalLiteral(list('08')))
        # Space prefix
        self.assertEqual(0, myObj._sliceOctalLiteral(list(' 0123')))
        # Alpha
        self.assertEqual(0, myObj._sliceOctalLiteral(list('abc')))

    def testLexIconHexadecimalLiteral(self):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - hexadecimal-literal."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(3, myObj._sliceHexadecimalLiteral(list('0x1')))
        self.assertEqual(5, myObj._sliceHexadecimalLiteral(list('0x123')))
        self.assertEqual(24, myObj._sliceHexadecimalLiteral(list('0x0123456789abcdefABCDEF')))
        self.assertEqual(6, myObj._sliceHexadecimalLiteral(list('0x0123')))
        self.assertEqual(5, myObj._sliceHexadecimalLiteral(list('0x123 and something else')))
        self.assertEqual(5, myObj._sliceHexadecimalLiteral(list('0X123')))
        self.assertEqual(5, myObj._sliceHexadecimalLiteral(list('0X123 and something else')))
        # Failures
        # No x
        self.assertEqual(0, myObj._sliceHexadecimalLiteral(list('0')))
        self.assertEqual(0, myObj._sliceHexadecimalLiteral(list('01')))
        self.assertEqual(0, myObj._sliceHexadecimalLiteral(list('0123')))
        # Bad number
        self.assertEqual(0, myObj._sliceHexadecimalLiteral(list(' 0xG')))
        # No number
        self.assertEqual(0, myObj._sliceHexadecimalLiteral(list(' 0x')))
        # Space prefix
        self.assertEqual(0, myObj._sliceHexadecimalLiteral(list(' 0x123')))
        # Alpha
        self.assertEqual(0, myObj._sliceHexadecimalLiteral(list('abc')))

    def testLexIconIntegerSuffix(self):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - integer-suffix."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('u'), 0))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('U'), 0))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('l'), 0))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('L'), 0))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('ul'), 0))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('uL'), 0))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('Ul'), 0))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('UL'), 0))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('lu'), 0))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('lU'), 0))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('Lu'), 0))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('LU'), 0))
        # Partial
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('uu'), 0))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('uU'), 0))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('Uu'), 0))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('UU'), 0))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('ll'), 0))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('lL'), 0))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('Ll'), 0))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('LL'), 0))
        # Failures
        # No x
        self.assertEqual(0, myObj._sliceIntegerSuffix(list('0'), 0))

    def testLexIconUnsignedSuffix(self):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - unsigned-suffix."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._PpTokeniser__sliceUnsignedSuffix(list('u'), 0))
        self.assertEqual(1, myObj._PpTokeniser__sliceUnsignedSuffix(list('U'), 0))
        self.assertEqual(1, myObj._PpTokeniser__sliceUnsignedSuffix(list('uu'), 0))
        self.assertEqual(1, myObj._PpTokeniser__sliceUnsignedSuffix(list('UU'), 0))
        # Failures
        # Long
        self.assertEqual(0, myObj._PpTokeniser__sliceUnsignedSuffix(list('l'), 0))
        self.assertEqual(0, myObj._PpTokeniser__sliceUnsignedSuffix(list('L'), 0))
        # Digit
        self.assertEqual(0, myObj._sliceIntegerSuffix(list('0'), 0))

    def testLexIconLongSuffix(self):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - long-suffix."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._PpTokeniser__sliceLongSuffix(list('l'), 0))
        self.assertEqual(1, myObj._PpTokeniser__sliceLongSuffix(list('L'), 0))
        self.assertEqual(1, myObj._PpTokeniser__sliceLongSuffix(list('ll'), 0))
        self.assertEqual(1, myObj._PpTokeniser__sliceLongSuffix(list('LL'), 0))
        # Failures
        # Unsigned
        self.assertEqual(0, myObj._PpTokeniser__sliceLongSuffix(list('u'), 0))
        self.assertEqual(0, myObj._PpTokeniser__sliceLongSuffix(list('U'), 0))
        # Digit
        self.assertEqual(0, myObj._PpTokeniser__sliceLongSuffix(list('0'), 0))

class TestExpressionLexCcon(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexCcon(self):
        """ISO/IEC 14882:1998(E) 2.13.1 Character literals [lex.ccon]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceCharacterLiteral(list("''"), 0))
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceCharacterLiteral(list("L''"), 0))
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceCharacterLiteral(list("'a'"), 0))
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceCharacterLiteral(list("L'a'"), 0))
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceCharacterLiteral(list("'\\b'"), 0))
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceCharacterLiteral(list("L'\\b'"), 0))
        # Failures
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceCharacterLiteral(list("'a"), 0))
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceCharacterLiteral(list("'"), 0))
        # Space prefix
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceCharacterLiteral(list(' 0123'), 0))
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceCharacterLiteral(list('L""'), 0))

    def testLexCconEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        # Simple
        self.assertEqual(2, myObj._sliceEscapeSequence(list('\\\\'), 0))
        self.assertEqual(2, myObj._sliceEscapeSequence(list('   \\\\'), 3))
        # Octal
        self.assertEqual(4, myObj._sliceEscapeSequence(list('\\000'), 0))
        # Hex
        self.assertEqual(3, myObj._sliceEscapeSequence(list('\\x0'), 0))
        # Failures
        self.assertEqual(0, myObj._sliceEscapeSequence(list('\\z'), 0))

    def testLexCconSimpleEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - simple-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(2, myObj._PpTokeniser__sliceSimpleEscapeSequence(list('\\\\'), 0))
        # TODO
        # Failures
        self.assertEqual(0, myObj._PpTokeniser__sliceSimpleEscapeSequence(list('\\z'), 0))

    def testLexCconOctalEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - octal-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(2, myObj._sliceOctalEscapeSequence(list('\\0'), 0))
        self.assertEqual(2, myObj._sliceOctalEscapeSequence(list('xsfg\\0'), 4))
        self.assertEqual(3, myObj._sliceOctalEscapeSequence(list('\\00'), 0))
        self.assertEqual(4, myObj._sliceOctalEscapeSequence(list('\\000'), 0))
        self.assertEqual(4, myObj._sliceOctalEscapeSequence(list('\\012'), 0))
        self.assertEqual(4, myObj._sliceOctalEscapeSequence(list('\\345'), 0))
        self.assertEqual(3, myObj._sliceOctalEscapeSequence(list('\\67'), 0))
        self.assertEqual(4, myObj._sliceOctalEscapeSequence(list('\\0000'), 0))
        self.assertEqual(4, myObj._sliceOctalEscapeSequence(list('\\00000'), 0))
        self.assertEqual(2, myObj._sliceOctalEscapeSequence(list('\\09'), 0))
        # Failures
        # No excape character
        self.assertEqual(0, myObj._sliceOctalEscapeSequence(list('0123'), 0))
        # Bad character
        self.assertEqual(0, myObj._sliceOctalEscapeSequence(list('\\9'), 0))

    def testLexCconHexadecimalEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - hexadecimal-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(3, myObj._sliceHexadecimalEscapeSequence(list('\\x0'), 0))
        self.assertEqual(3, myObj._sliceHexadecimalEscapeSequence(list(' \\x0'), 1))
        self.assertEqual(24, myObj._sliceHexadecimalEscapeSequence(
                                    list('\\x0123456789abcdefABCDEF'),
                                    0
                                    )
                                )
        # Failures
        # No excape character
        self.assertEqual(0, myObj._sliceHexadecimalEscapeSequence(list('0123'), 0))
        # Bad character
        self.assertEqual(0, myObj._sliceHexadecimalEscapeSequence(list('\\xG'), 0))

class TestExpressionLexFcon(TestPpTokeniserBase):
    """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon]."""
    def setUp(self):
        pass

    def testFloatingLiteral(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(7, myObj._sliceFloatingLiteral(list('123.456'), 0))
        self.assertEqual(10, myObj._sliceFloatingLiteral(list('123.456e12'), 0))
        self.assertEqual(11, myObj._sliceFloatingLiteral(list('123.456e12f'), 0))
        self.assertEqual(8, myObj._sliceFloatingLiteral(list('123.456f'), 0))
        self.assertEqual(6, myObj._sliceFloatingLiteral(list('123e12'), 0))
        self.assertEqual(7, myObj._sliceFloatingLiteral(list('123e12L'), 0))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteral(list('123'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteral(list('g'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteral(list('0g'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteral(list('e + 123'), 0))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteral(list(' 0123'), 0))

    def testLexFconFractionalConstant(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - fractional-constant."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(7, myObj._sliceFloatingLiteralFractionalConstant(list('123.456'), 0))
        self.assertEqual(7, myObj._sliceFloatingLiteralFractionalConstant(list('.....123.456'), 5))
        self.assertEqual(4, myObj._sliceFloatingLiteralFractionalConstant(list('.456'), 0))
        self.assertEqual(4, myObj._sliceFloatingLiteralFractionalConstant(list('123.'), 0))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteralFractionalConstant(list('123'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralFractionalConstant(list('g'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralFractionalConstant(list('0g'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralFractionalConstant(list('e + 123'), 0))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteralFractionalConstant(list(' 0123'), 0))

    def testLexFconExponentPart(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - exponent-part."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(5, myObj._sliceFloatingLiteralExponentPart(list('e+123'), 0))
        self.assertEqual(5, myObj._sliceFloatingLiteralExponentPart(list('E+123'), 0))
        self.assertEqual(5, myObj._sliceFloatingLiteralExponentPart(list('e-123'), 0))
        self.assertEqual(5, myObj._sliceFloatingLiteralExponentPart(list('E-123'), 0))
        self.assertEqual(4, myObj._sliceFloatingLiteralExponentPart(list('e123'), 0))
        self.assertEqual(4, myObj._sliceFloatingLiteralExponentPart(list('E123'), 0))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('0123'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('g'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('0g'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('e + 123'), 0))
        # No number
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('e'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('E'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('e+'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('E+'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('e-'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('E-'), 0))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list(' 0123'), 0    ))

    def testLexFconSign(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - sign."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._sliceFloatingLiteralSign(list('-'), 0))
        self.assertEqual(1, myObj._sliceFloatingLiteralSign(list('....-'), 4))
        self.assertEqual(1, myObj._sliceFloatingLiteralSign(list('+'), 0))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteralSign(list('0123'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralSign(list('g'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralSign(list('0g'), 0))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteralSign(list(' 0123'), 0))

    def testLexFconDigitSequence(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - digit-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._sliceFloatingLiteralDigitSequence(list('0'), 0))
        self.assertEqual(2, myObj._sliceFloatingLiteralDigitSequence(list('12'), 0))
        self.assertEqual(3, myObj._sliceFloatingLiteralDigitSequence(list('123'), 0))
        self.assertEqual(3, myObj._sliceFloatingLiteralDigitSequence(list('123a'), 0))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteralDigitSequence(list('abc'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralDigitSequence(list('a12'), 0))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteralDigitSequence(list(' 0123'), 0))


    def testLexFconFloatingSuffix(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - floating-suffix."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._sliceFloatingLiteralFloatingSuffix(list('f'), 0))
        self.assertEqual(1, myObj._sliceFloatingLiteralFloatingSuffix(list('...f'), 3))
        self.assertEqual(1, myObj._sliceFloatingLiteralFloatingSuffix(list('l'), 0))
        self.assertEqual(1, myObj._sliceFloatingLiteralFloatingSuffix(list('F'), 0))
        self.assertEqual(1, myObj._sliceFloatingLiteralFloatingSuffix(list('L'), 0))
        self.assertEqual(1, myObj._sliceFloatingLiteralFloatingSuffix(list('fg'), 0))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteralFloatingSuffix(list('0123'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralFloatingSuffix(list('g'), 0))
        self.assertEqual(0, myObj._sliceFloatingLiteralFloatingSuffix(list('0g'), 0))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteralFloatingSuffix(list(' 0123'), 0))

class TestExpressionLexString(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexString(self):
        """ISO/IEC 14882:1998(E) 2.13.4 String literals [lex.string]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceStringLiteral(list('""'), 0))
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceStringLiteral(list('..""'), 2))
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceStringLiteral(list('.."" '), 2))
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceStringLiteral(list('..""  '), 2))
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceStringLiteral(list('L""'), 0))
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceStringLiteral(list('"abc"'), 0))
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceStringLiteral(list('L"abc"'), 0))
        # Failures
        # Single "
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceStringLiteral(list('"'), 0))
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceStringLiteral(list('"as'), 0))
        # Space prefix
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceStringLiteral(list(' 0123'), 0))

    def testLexStringNull(self):
        """ISO/IEC 14882:1998(E) 2.13.4 String literals [lex.string] with NULL character."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceStringLiteral(list(r'"\0"'), 0))
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceStringLiteral(list(r'....."\0"'), 5))
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceStringLiteral(list('"\\0"'), 0))
        myObj.resetTokType()
        self.assertEqual(10, myObj._sliceStringLiteral(list(r'"abc\0xyz"'), 0))
        myObj.resetTokType()
        self.assertEqual(10, myObj._sliceStringLiteral(list('"abc\\0xyz"'), 0))

class TestExpressionLexBool(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexBool(self):
        """ISO/IEC 14882:1998(E) 2.13.5 Boolean literals [lex.bool]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(4, myObj._sliceBoolLiteral(list('true'), 0))
        self.assertEqual(5, myObj._sliceBoolLiteral(list('false'), 0))
        self.assertEqual(4, myObj._sliceBoolLiteral(list('truesomeething'), 0))
        self.assertEqual(5, myObj._sliceBoolLiteral(list('falseotherthing'), 0))
        self.assertEqual(5, myObj._sliceBoolLiteral(list('..falseotherthing'), 2))
        # Failures
        # Partial
        self.assertEqual(0, myObj._sliceBoolLiteral(list('tru'), 0))
        self.assertEqual(0, myObj._sliceBoolLiteral(list('f'), 0))
        # Space prefix
        self.assertEqual(0, myObj._sliceBoolLiteral(list(' 0123'), 0))

class TestLexPhases_0(TestPpTokeniserBase):
    """Tests the psuedo-phase 0 that just reads a file."""

    def testPhase_0_NoFile(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, no file."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=None)
        # Fails as no file to read
        #myObj.lexPhases_0()
        self.assertRaises(PpTokeniser.ExceptionCpipTokeniser, myObj.lexPhases_0)

    def testPhase_0_Empty(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, empty file, no new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u''))
        # Successes
        self.assertEqual([], myObj.lexPhases_0())

    def testPhase_0_EmptyWithEof(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, single new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'\n'))
        # Successes
        self.assertEqual(['\n',], myObj.lexPhases_0())

    def testPhase_0_OneString(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, one line, no new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'asd'))
        # Successes
        self.assertEqual(['asd',], myObj.lexPhases_0())

    def testPhase_0_OneLine(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, one line, has new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'asd\n'))
        # Successes
        self.assertEqual(['asd\n',], myObj.lexPhases_0())

    def testPhase_0_MultiLine_00(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, multi-line, has new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'asd\n\n'))
        # Successes
        self.assertEqual(['asd\n', '\n'], myObj.lexPhases_0())

    def testPhase_0_MultiLine_01(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, multi-line, no ending new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'abc\ndef'))
        # Successes
        self.assertEqual(['abc\n', 'def'], myObj.lexPhases_0())

    def testPhase_0_MultiLine_02(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, multi-line, has ending new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'abc\ndef\n'))
        self.assertEqual(['abc\n', 'def\n'], myObj.lexPhases_0())

class TestLexPhases_1(TestPpTokeniserBase):
    """Tests the phase zero and phase one."""
    def testPhase_1_00_ConvertCharSet(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, lex.charset expansion."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u''))
        myL = ['',]
        myObj._convertToLexCharset(myL)
        self.assertEqual([''], myL)
        myL = ['abc',]
        myObj._convertToLexCharset(myL)
        self.assertEqual(['abc'], myL)
        # Copyright symbol
        myL = ['ab\xa9c',]
        myObj._convertToLexCharset(myL)
        self.assertEqual(['ab\\u00A9c'], myL)
        # Copyright symbol
        myL = ['\u0065',]
        myObj._convertToLexCharset(myL)
        if sys.version_info.major == 2:
            self.assertEqual(['\u0065'], myL)
        elif sys.version_info.major == 3:
            self.assertEqual(['e'], myL)
        myL = ['\uFFFF',]
        myObj._convertToLexCharset(myL)
        self.assertEqual(['\\uFFFF'], myL)
        myL = ['\uffff',]
        myObj._convertToLexCharset(myL)
        if sys.version_info.major == 2:
            self.assertEqual(['\\uffff'], myL)
        elif sys.version_info.major == 3:
            self.assertEqual(['\\uFFFF'], myL)

    def testPhase_1_01_ConvertCharSet(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, lex.charset expansion, misc."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u''))
        myTokS = ['@',]
        myObj._convertToLexCharset(myTokS)
        self.assertEqual(['@'], myTokS)
        myTokS = ['$',]
        myObj._convertToLexCharset(myTokS)
        self.assertEqual(['$'], myTokS)
        myTokS = [chr(0x60),]
        myObj._convertToLexCharset(myTokS)
        self.assertEqual([chr(0x60)], myTokS)

    def testPhase_1_Empty(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, empty file, no new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u''))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual([], myPh_0)
        myObj.lexPhases_1(myPh_0)
        self.assertEqual([], myPh_0)

    def testPhase_1_EmptyWithEof(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, single new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'\n'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['\n'], myPh_0)
        myObj.lexPhases_1(myPh_0)
        self.assertEqual(['\n'], myPh_0)

    def testPhase_1_OneString(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, one line, no new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'asd'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['asd',], myPh_0)
        myObj.lexPhases_1(myPh_0)
        self.assertEqual(['asd',], myPh_0)

    def testPhase_1_OneLine(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, one line, has new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'asd\n'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['asd\n',], myPh_0)
        myObj.lexPhases_1(myPh_0)
        self.assertEqual(['asd\n',], myPh_0)

    def testPhase_1_MultiLine_00(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, multi-line, has new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'asd\n\n'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['asd\n', '\n'], myPh_0)
        myObj.lexPhases_1(myPh_0)
        self.assertEqual(['asd\n', '\n'], myPh_0)

    def testPhase_1_MultiLine_01(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, multi-line, no ending new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'abc\ndef'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['abc\n', 'def'], myPh_0)
        myObj.lexPhases_1(myPh_0)
        self.assertEqual(['abc\n', 'def'], myPh_0)

    def testPhase_1_MultiLine_02(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, multi-line, has ending new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'abc\ndef\n'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['abc\n', 'def\n'], myPh_0)
        myObj.lexPhases_1(myPh_0)
        self.assertEqual(['abc\n', 'def\n'], myPh_0)

    def testPhase_1_Trigraph_Single_00(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, trigraph, single "??="."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'??=\n'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['??=\n',], myPh_0)
        myObj.lexPhases_1(myPh_0)
        self.assertEqual(['#\n',], myPh_0)
        # Test file locator information
        # NOTE: A this is a pre-pass of a multi-pass system we need
        # to access the logicalPhysicalLineMap
        self.assertEqual(
            (FileLocation.START_LINE, FileLocation.START_COLUMN),
            myObj.fileLocator.logicalPhysicalLineMap.pLineCol(
                FileLocation.START_LINE,
                FileLocation.START_COLUMN,
                )
            )

    def testPhase_1_Trigraph_Single_01(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, trigraph, single (all)."""
        for t, r in (
            ('??=', '#'),
            ('??(',  '['),
            ('??<', '{'),
            ('??/', '\\'),
            ('??)', ']'),
            ('??>', '}'),
            ("??'", '^'),
            ('??!', '|'),
            ('??-', '~'),
            ):
            myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(u'%s\n' % t))
            myPh_0 = myObj.lexPhases_0()
            self.assertEqual(['%s\n' % t,], myPh_0)
            myObj.lexPhases_1(myPh_0)
            self.assertEqual(['%s\n' % r,], myPh_0)
            # Test file locator information
            # NOTE: A this is a pre-pass of a multi-pass system we need
            # to access the logicalPhysicalLineMap
            self.assertEqual(
                (FileLocation.START_LINE, FileLocation.START_COLUMN),
                myObj.fileLocator.logicalPhysicalLineMap.pLineCol(
                    FileLocation.START_LINE,
                    FileLocation.START_COLUMN,
                    )
                )

    def testPhase_1_Trigraph_Double_00(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, trigraph, double 00."""
        myObj = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(u'??=??(\n')
            )
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['??=??(\n',], myPh_0)
        myObj.lexPhases_1(myPh_0)
        self.assertEqual(['#[\n',], myPh_0)
        # Test file locator information
        # NOTE: A this is a pre-pass of a multi-pass system we need
        # to access the logicalPhysicalLineMap
        #print '\ntestPhase_1_Trigraph_Double_00():'
        #print '\ntestPhase_1_Trigraph_Double_00(): myObj._fileLocator'
        #print str(myObj._fileLocator)
        #print '\ntestPhase_1_Trigraph_Double_00(): myObj._fileLocator.logicalPhysicalLineMap'
        #print str(myObj._fileLocator.logicalPhysicalLineMap)
        #print '\ntestPhase_1_Trigraph_Double_00(): myObj._fileLocator.logicalPhysicalLineMap._ir'
        #pprint.pprint(myObj._fileLocator.logicalPhysicalLineMap._ir)
        lLine = FileLocation.START_LINE
        lCol = FileLocation.START_COLUMN
        # Logical (0,0) maps to physical (0,0)
        pLine, pCol = myObj.fileLocator.logicalPhysicalLineMap.pLineCol(lLine, lCol)
        self.assertEqual(lLine, pLine)
        self.assertEqual(lCol, pCol)
        # Logical (0,1) maps to physical (0,3)
        lCol += 1
        pLine, pCol = myObj.fileLocator.logicalPhysicalLineMap.pLineCol(lLine, lCol)
        self.assertEqual(lLine, pLine)
        self.assertEqual(lCol+2, pCol)

    def testPhase_1_Trigraph_Multi_09(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, trigraph, multi 09."""
        myObj = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(
                u'??=??(??<??/??)??>??\'??!??-\n'
                )
            )
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['??=??(??<??/??)??>??\'??!??-\n',], myPh_0)
        myObj.lexPhases_1(myPh_0)
        self.assertEqual(['#[{\\]}^|~\n',], myPh_0)
        ## Test file locator information
        ## NOTE: A this is a pre-pass of a multi-pass system we need
        ## to access the logicalPhysicalLineMap
        #print
        #print str(myObj.fileLocator.logicalPhysicalLineMap)
        #pprint.pprint(myObj.fileLocator.logicalPhysicalLineMap._ir)
        #for i in range(0, 9*3+1, 3):
        #    print i
        #    self.assertEqual(
        #        (FileLocation.START_LINE, i+FileLocation.START_COLUMN),
        #        myObj.fileLocator.logicalPhysicalLineMap.pLineCol(
        #            FileLocation.START_LINE,
        #            (i/3)+FileLocation.START_COLUMN,
        #            )
        #        )


class TestLexPhases_2(TestPpTokeniserBase):
    """Tests the phase two only."""
    def testPhase_2_OneLine(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 2, single new-line."""
        myObj = PpTokeniser.PpTokeniser()
        myLines = ['\n',]
        self.assertEquals(None, myObj.lexPhases_2(myLines))
        self.assertEqual(['\n',], myLines)

    def testPhase_2_TwoLines(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 2, two new-lines."""
        myObj = PpTokeniser.PpTokeniser()
        myLines = [
            '\n',
            '\n',
            ]
        self.assertEquals(None, myObj.lexPhases_2(myLines))
        self.assertEqual(
            [
                '\n',
                '\n',
            ],
            myLines)

    def testPhase_2_Mt_continuation(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 2, empty continuation."""
        myObj = PpTokeniser.PpTokeniser()
        myLines = [
            '\\\n',
            '\n',
            ]
        self.assertEquals(None, myObj.lexPhases_2(myLines))
        self.assertEqual(
            [
                '\n',
                '\n',
            ],
            myLines)

    def testPhase_2_OneContinuation(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 2, one continuation char."""
        myObj = PpTokeniser.PpTokeniser()
        myLines = [
            'a\\\n',
            'b\n',
            ]
        self.assertEquals(None, myObj.lexPhases_2(myLines))
        self.assertEqual(
            [
                'ab\n',
                '\n',
            ],
            myLines)

    def testPhase_2_TwoContinuation(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 2, two continuation char."""
        myObj = PpTokeniser.PpTokeniser()
        myLines = [
            'a\\\n',
            'b\\\n',
            'c\n',
            ]
        self.assertEquals(None, myObj.lexPhases_2(myLines))
        self.assertEqual(
            [
                'abc\n',
                '\n',
                '\n',
            ],
            myLines)

    def testPhase_2_ContinuationAtEOF(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - continuation char at EOF."""
        myObj = PpTokeniser.PpTokeniser()
        myLines = [
            'a\\\n',
            ]
        self.assertRaises(
            CppDiagnostic.ExceptionCppDiagnosticUndefined,
            myObj.lexPhases_2,
            myLines
            )

    def testPhase_2_ContinuationMakesBadChar(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 2, continuation char makes universal-character-name."""
        # Need to check if the spliced line generates a universal-character-name
        # i.e.
        # \u hex-quad
        # \U hex-quad hex-quad
        # So this lines: ["\\u\\\n", "12FE\n"] should fail as it becomes
        # "\\u12FE\n"
        myObj = PpTokeniser.PpTokeniser()
        myLines = [
            "\\u\\\n",
            "12FE\n"
            ]
        self.assertRaises(
            CppDiagnostic.ExceptionCppDiagnosticUndefined,
            myObj.lexPhases_2,
            myLines
            )

    def testPhase_2_LineContinuationLocation_00(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 2, two continuation physical location."""
        myObj = PpTokeniser.PpTokeniser()
        myP = [
            'a\\\n',
            'b\\\n',
            'c\n',
            'd\n',
            ]
        myL = myP[:]
        self.assertEquals(None, myObj.lexPhases_2(myL))
        self.assertEqual(
            [
                'abc\n',
                '\n',
                '\n',
                'd\n',
            ],
            myL)
        #print myObj.fileLocator
        #print 'EOF Line: %d' % myObj.fileLocator.lineNum
        #print 'EOF  Col: %d' % myObj.fileLocator.colNum
        for lL in range(len(myL)):
            for cL in range(len(myL[lL])):
                lP, cP = myObj.fileLocator.logicalToPhysical(lL+1, cL+1)
                #print 'L:', lL+1, cL+1
                #print 'P:', lP, cP
                #print (lL+1, cL+1), myL[lL][cL], '->', (lP, cP), myP[lP][cP]

class TestLexPptoken(TestPpTokeniserBase):
    """Tests capture of a single preprocessing token."""
    #def testLexHeader(self):
    #    """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.header]."""
    #    myObj = PpTokeniser.PpTokeniser()
    #    # Successes
    #    self.assertEqual(myObj.cppTokType, None)
    #    self.assertEqual(7, myObj._sliceLexPptoken(list('"std.h"')))
    #    self.assertEqual(myObj.cppTokType, 'header-name')
    #    self.assertEqual(7, myObj._sliceLexPptoken(list('<std.h>')))
    #    self.assertEqual(myObj.cppTokType, 'header-name')
    #    self.assertEqual(7, myObj._sliceLexPptoken(list('"std.h" ')))
    #    self.assertEqual(myObj.cppTokType, 'header-name')
    #    self.assertEqual(7, myObj._sliceLexPptoken(list('<std.h>   ')))
    #    self.assertEqual(myObj.cppTokType, 'header-name')

    def testLexPpnumber(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.ppnumber]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(1, myObj._sliceLexPptoken(list('1'), 0))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceLexPptoken(list('.1'), 0))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexPptoken(list('1.234'), 0))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexPptoken(list('1.234e+'), 0))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexPptoken(list('1.234E+'), 0))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexPptoken(list('1.234e-'), 0))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexPptoken(list('1.234E-'), 0))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(9, myObj._sliceLexPptoken(list('1.234E-89'), 0))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(12, myObj._sliceLexPptoken(list('1.234E-89e+4'), 0))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        # Failures

    def testLexName(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.name]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLexPptoken(list('ab_9'), 0))
        self.assertEqual(myObj.cppTokType, 'identifier')
        myObj.resetTokType()
        self.assertEqual(10, myObj._sliceLexPptoken(list('ab_9\\u0123'), 0))
        self.assertEqual(myObj.cppTokType, 'identifier')
        myObj.resetTokType()
        self.assertEqual(10, myObj._sliceLexPptoken(list('ab_\\u01239'), 0))
        self.assertEqual(myObj.cppTokType, 'identifier')
        # Failures
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLexPptoken(list('9ab'), 0))
        # Actually this resolves to a lex.ppnumber
        self.assertNotEqual(myObj.cppTokType, 'identifier')
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexPptoken(list(' ab'), 0))
        self.assertEqual(myObj.cppTokType, None)

    def testLexCcon(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.ccon]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLexPptoken(list("'a'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLexPptoken(list("L'a'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLexPptoken(list("'\\b'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexPptoken(list("L'\\b'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        # Failures
        # Space prefix
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexPptoken(list(' 0123'), 0))
        self.assertEqual(myObj.cppTokType, None)

    def testLexCconEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.ccon] - escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        # Simple
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLexPptoken(list("'\\\\'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        # Octal
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceLexPptoken(list("'\\000'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        # Hex
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexPptoken(list("'\\x0'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        # Failures
        myObj.resetTokType()
        self.assertEqual(1, myObj._sliceLexPptoken(list("'\\z'"), 0))
        self.assertNotEqual(myObj.cppTokType, 'character-literal')

    def testLexCconSimpleEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.ccon] - simple-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLexPptoken(list("'\\\\'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        # Failures
        myObj.resetTokType()
        self.assertEqual(1, myObj._sliceLexPptoken(list("'\\z'"), 0))
        self.assertNotEqual(myObj.cppTokType, 'character-literal')

    def testLexCconOctalEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.ccon] - octal-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(4, myObj._sliceLexPptoken(list("'\\0'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexPptoken(list("'\\00'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceLexPptoken(list("'\\000'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceLexPptoken(list("'\\012'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceLexPptoken(list("'\\345'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexPptoken(list("'\\67'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(7, myObj._sliceLexPptoken(list("'\\0000'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(8, myObj._sliceLexPptoken(list("'\\00000'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexPptoken(list("'\\09'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')

    def testLexCconHexadecimalEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.ccon] - hexadecimal-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexPptoken(list("'\\x0'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        myObj.resetTokType()
        self.assertEqual(26, myObj._sliceLexPptoken(list("'\\x0123456789abcdefABCDEF'"), 0))
        self.assertEqual(myObj.cppTokType, 'character-literal')

    def testLexString(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.string]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceLexPptoken(list('""'), 0))
        self.assertEqual(myObj.cppTokType, 'string-literal')
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLexPptoken(list('L""'), 0))
        self.assertEqual(myObj.cppTokType, 'string-literal')
        myObj.resetTokType()
        self.assertEqual(5, myObj._sliceLexPptoken(list('"abc"'), 0))
        self.assertEqual(myObj.cppTokType, 'string-literal')
        myObj.resetTokType()
        self.assertEqual(6, myObj._sliceLexPptoken(list('L"abc"'), 0))
        self.assertEqual(myObj.cppTokType, 'string-literal')
        # Failures
        # Space prefix
        #myObj._sliceLexPptoken(list(' 0123'), 0)
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexPptoken(list(' 0123'), 0))
        self.assertEqual(myObj.cppTokType, None)

    def testLexOperators(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.operators]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        myObj.resetTokType()
        self.assertEqual(2, myObj._sliceLexPptoken(list('<<'), 0))
        self.assertEqual(myObj.cppTokType, 'preprocessing-op-or-punc')
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLexPptoken(list('<<='), 0))
        self.assertEqual(myObj.cppTokType, 'preprocessing-op-or-punc')
        # Failures
        myObj.resetTokType()
        self.assertEqual(3, myObj._sliceLexPptoken(list('9ab'), 0))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        myObj.resetTokType()
        self.assertEqual(0, myObj._sliceLexPptoken(list(' ab'), 0))
        self.assertEqual(myObj.cppTokType, None)

    def testLexNonWhitespace(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - single character."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        # These should be found by _sliceNonWhitespaceSingleChar()
        myObj.resetTokType()
        self.assertEqual(1, myObj._sliceLexPptoken(list('"'), 0))
        self.assertEqual(myObj.cppTokType, 'non-whitespace')
        myObj.resetTokType()
        self.assertEqual(1, myObj._sliceLexPptoken(list('\''), 0))
        self.assertEqual(myObj.cppTokType, 'non-whitespace')


class TestGenerateLexPpTokens(TestPpTokeniserBase):
    """Generates a preprocessing token stream to
    ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken]."""

    def testCommentReplacementC(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Comment replacement, C style."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('/* */')
        myToks = [t for t in myGen]
        #print '\n', myToks
        eToks = [
                PpToken.PpToken(' ',           'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        #
        myGen = myObj.genLexPptokenAndSeqWs('/* */\n')
        myToks = [t for t in myGen]
        #print '\n', myToks
        eToks = [
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        #
        #myGen = myObj.genLexPptokenAndSeqWs('(  )\n')
        #myToks = [t for t in myGen]
        #print '\nWTF?\n', myToks
        myGen = myObj.genLexPptokenAndSeqWs('if /* */ (  )\n')
        myToks = [t for t in myGen]
        #print '\n', myToks
        eToks = [
                PpToken.PpToken('if',          'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('(',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken(')',           'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)

    def testCommentReplacementC_unclosed(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Comment replacement, C style but unclosed."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('/* ')
        try:
            myToks = [t for t in myGen]
            self.fail('CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream not raised')
        except CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream:
            pass

    def testCommentReplacementCplusplus(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Comment replacement, C++ style."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('//\n')
        myToks = [t for t in myGen]
        #print '\n', myToks
        eToks = [
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        #
        myGen = myObj.genLexPptokenAndSeqWs('if // (  )\n')
        myToks = [t for t in myGen]
        #print '\n', myToks
        eToks = [
                PpToken.PpToken('if',          'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        #
        myGen = myObj.genLexPptokenAndSeqWs('//')
        self.assertRaises(
            CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
            next, myGen
            )
        #myToks = [t for t in myGen]
        ##print '\n', myToks
        #eToks = [
        #        PpToken.PpToken(' ',           'whitespace'),
        #        ]
        #self._printDiff(myToks, eToks)
        #self.assertEqual(myToks, eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)

    def testCommentReplacementMixed(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Comment replacement, mixed."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('/* //*/')
        myToks = [t for t in myGen]
        #print '\n', myToks
        eToks = [
                PpToken.PpToken(' ',           'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        #
        myGen = myObj.genLexPptokenAndSeqWs('// /**/\n')
        myToks = [t for t in myGen]
        #print '\n', myToks
        eToks = [
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)

    def testControlLineDefine_00(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Sect 16 control-line "define" [00]."""
        myObj = PpTokeniser.PpTokeniser()
        #print
        #for t in myObj.genLexPptokenAndSeqWs('#define SPAM 1\n'):
        #    print t
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#define SPAM 1\n')]
        self.assertEqual(
            myToks,
            [
                PpToken.PpToken('#',       'preprocessing-op-or-punc'),
                PpToken.PpToken('define',  'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('SPAM',    'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken('\n',      'whitespace'),
                ],
            )

    def testControlLineDefine_01(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Sect 16 control-line "define" [01]."""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('# define SPAM 1\n')]
        self.assertEqual(
            myToks,
            [
                PpToken.PpToken('#',       'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('define',  'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('SPAM',    'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken('\n',      'whitespace'),
                ],
            )

    def testControlLineDefine_02(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Sect 16 control-line "define" [02]."""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#   define SPAM 1\n')]
        eToks = [
                PpToken.PpToken('#',       'preprocessing-op-or-punc'),
                PpToken.PpToken('   ',       'whitespace'),
                PpToken.PpToken('define',  'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('SPAM',    'identifier'),
                PpToken.PpToken(' ',       'whitespace'),
                PpToken.PpToken('1',       'pp-number'),
                PpToken.PpToken('\n',      'whitespace'),
                ]
        #print '\n', myToks
        #print eToks
        self.assertEqual(myToks, eToks)

    def testControlLineDefine_03(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Sect 16 control-line "define" [03]."""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#define SPAM 123.456e42\n')]
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('define',      'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('SPAM',        'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('123.456e42',  'pp-number'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self.assertEqual(myToks, eToks)

    def testControlLineDefine_04(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Sect 16 control-line "define" [04]."""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#define SPAM(x  , y)  x*y+42\n')]
        #print '\n', myToks
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('define',      'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('SPAM',        'identifier'),
                PpToken.PpToken('(',           'preprocessing-op-or-punc'),
                PpToken.PpToken('x',           'identifier'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken(',',           'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('y',           'identifier'),
                PpToken.PpToken(')',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('x',           'identifier'),
                PpToken.PpToken('*',           'preprocessing-op-or-punc'),
                PpToken.PpToken('y',           'identifier'),
                PpToken.PpToken('+',           'preprocessing-op-or-punc'),
                PpToken.PpToken('42',          'pp-number'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testControlLineDefine_05(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Sect 16 control-line "define" [05]."""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#define SPAM "hello world"\n')]
        eToks = [
                PpToken.PpToken('#',               'preprocessing-op-or-punc'),
                PpToken.PpToken('define',          'identifier'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken('SPAM',            'identifier'),
                PpToken.PpToken(' ',               'whitespace'),
                # TODO: Surely this should be a lex.string but the standard
                # suggests that lex.header takes primacy
                PpToken.PpToken('"hello world"',   'string-literal'),
                PpToken.PpToken('\n',              'whitespace'),
                ]
        #print '\n', myToks
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testControlLineDefine_06(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Sect 16 control-line "define" [06]."""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#define OBJ_LIKE /* white space */ (1-1) /* other */\n')]
        eToks = [
                PpToken.PpToken('#',               'preprocessing-op-or-punc'),
                PpToken.PpToken('define',          'identifier'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken('OBJ_LIKE',        'identifier'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken('(',               'preprocessing-op-or-punc'),
                PpToken.PpToken('1',               'pp-number'),
                PpToken.PpToken('-',               'preprocessing-op-or-punc'),
                PpToken.PpToken('1',               'pp-number'),
                PpToken.PpToken(')',               'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken('\n',              'whitespace'),
                ]
        #print '\n', myToks
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testControlLineDefine_dollar_as_identifier(self):
        """From libCello: #define $ lit"""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#define $ lit\n')]
        eToks = [
                PpToken.PpToken('#',               'preprocessing-op-or-punc'),
                PpToken.PpToken('define',          'identifier'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken('$',               'identifier'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken('lit',             'identifier'),
                PpToken.PpToken('\n',              'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testControlLineDefine_at_symbol_as_identifier(self):
        """From libCello: #define @ lit"""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#define @ lit\n')]
        eToks = [
                PpToken.PpToken('#',               'preprocessing-op-or-punc'),
                PpToken.PpToken('define',          'identifier'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken('@',               'identifier'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken('lit',             'identifier'),
                PpToken.PpToken('\n',              'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testControlLineDefine_back_tick_as_identifier(self):
        """From libCello: #define ` lit"""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#define ` lit\n')]
        eToks = [
                PpToken.PpToken('#',               'preprocessing-op-or-punc'),
                PpToken.PpToken('define',          'identifier'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken('`',               'identifier'),
                PpToken.PpToken(' ',               'whitespace'),
                PpToken.PpToken('lit',             'identifier'),
                PpToken.PpToken('\n',              'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testControlLineNull(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - Sect 16 control-line Null."""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#\n')]
        eToks = [
                PpToken.PpToken('#',    'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',   'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('# \n')]
        eToks = [
                PpToken.PpToken('#',     'preprocessing-op-or-punc'),
                PpToken.PpToken(' \n',   'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#  \n')]
        eToks = [
                PpToken.PpToken('#',      'preprocessing-op-or-punc'),
                PpToken.PpToken('  \n',   'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testPreprocessingCppStringize(self):
        """ISO/IEC 14882:1998(E) 16.3.2 The # operator [cpp.stringize]."""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#\n')]
        eToks = [
                PpToken.PpToken('#',    'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',   'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('# \n')]
        eToks = [
                PpToken.PpToken('#',     'preprocessing-op-or-punc'),
                PpToken.PpToken(' \n',   'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('#  \n')]
        eToks = [
                PpToken.PpToken('#',      'preprocessing-op-or-punc'),
                PpToken.PpToken('  \n',   'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testPreprocessingCppConcat(self):
        """ISO/IEC 14882:1998(E) 16.3.3 The ## operator [cpp.concat]."""
        myObj = PpTokeniser.PpTokeniser()
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('##')]
        eToks = [
                PpToken.PpToken('##',   'preprocessing-op-or-punc'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('##\n')]
        eToks = [
                PpToken.PpToken('##',   'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',   'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('## \n')]
        eToks = [
                PpToken.PpToken('##',    'preprocessing-op-or-punc'),
                PpToken.PpToken(' \n',   'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('##  \n')]
        eToks = [
                PpToken.PpToken('##',     'preprocessing-op-or-punc'),
                PpToken.PpToken('  \n',   'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        myToks = [t for t in myObj.genLexPptokenAndSeqWs('# ## #\n')]
        eToks = [
                PpToken.PpToken('#',    'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',    'whitespace'),
                PpToken.PpToken('##',   'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',    'whitespace'),
                PpToken.PpToken('#',    'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',   'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testInitLexPhase123(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - phase 1, 2, 3 processing."""
        myStr = u'#include "spam.h"\n'
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        self.assertEqual(myObj.initLexPhase12(), myStr)

    def testNextGenertor_01(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - token and token type generation."""
        myStr = u'#include "spam.h"\n'
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = myObj.next()
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('#',           'preprocessing-op-or-punc'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('include',     'identifier'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken(' ',           'whitespace'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('"spam.h"',    'string-literal'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('\n',          'whitespace'))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myTokTypeGen)

class TestGenerateLexPpTokensUnget(TestPpTokeniserBase):
    """Generates a preprocessing token stream using unget(0 to push token back on to the stream."""

    def testNextGenertorSend_00(self):
        """Token generation with send()."""
        myStr = u'#include "spam.h"\n'
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = myObj.next()
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('#',           'preprocessing-op-or-punc'))
        myTokTypeGen.send(myTokType)
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('#',           'preprocessing-op-or-punc'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('include',     'identifier'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken(' ',           'whitespace'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('"spam.h"',    'string-literal'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('\n',          'whitespace'))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myTokTypeGen)

    def testNextGenertorSend_01(self):
        """Token generation with send(), simulates "F F (123)" ignoring first F and pushing back the second F."""
        myStr = u'F F (123)\n'
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = myObj.next()
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('F',        'identifier'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken(' ',           'whitespace'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('F',        'identifier'))
        # Not a LPAREN so push it back
        myTokTypeGen.send(myTokType)
        # Now get next token, it should have been pushed back
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('F',        'identifier'))
        # Carry on
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken(' ',           'whitespace'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('(',           'preprocessing-op-or-punc'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('123',         'pp-number'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken(')',           'preprocessing-op-or-punc'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('\n',          'whitespace'))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myTokTypeGen)

    def testNextGenertorSend_03(self):
        """Token generation with send(), simulates "F(123) F abc" pushing back "abc" when no LPAREN found for second F."""
        myStr = u'F(123) F abc\n'
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = myObj.next()
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('F',        'identifier'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('(',           'preprocessing-op-or-punc'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('123',         'pp-number'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken(')',           'preprocessing-op-or-punc'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken(' ',           'whitespace'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('F',        'identifier'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken(' ',           'whitespace'))
        myTokType = next(myTokTypeGen)
        #print str(myTokType)
        self.assertEqual(myTokType, PpToken.PpToken('abc',         'identifier'))
        # 'abc' not a LPAREN so push it back
        myTokTypeGen.send(PpToken.PpToken('abc',        'identifier'))
        # This represents subsequent processing
        myTokType = next(myTokTypeGen)
        #print str(myTokType)
        self.assertEqual(myTokType, PpToken.PpToken('abc',         'identifier'))
        myTokType = next(myTokTypeGen)
        self.assertEqual(myTokType, PpToken.PpToken('\n',          'whitespace'))
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myTokTypeGen)

class TestHeaderReconstuction(TestPpTokeniserBase):
    """Tests generating a token stream then re-interpreting it as a header-name."""
    def testQcharSeq_00(self):
        """TestHeaderReconstuction "q-char-sequence" [0]."""
        myObj = PpTokeniser.PpTokeniser()
        # q-char sequences
        myGen = myObj.genLexPptokenAndSeqWs('#include "foo"\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'string-literal'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'header-name'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testQcharSeq_01(self):
        """TestHeaderReconstuction "q-char-sequence" [1]."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('# include "foo"\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'string-literal'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'header-name'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testQcharSeq_02(self):
        """TestHeaderReconstuction "q-char-sequence" [2]."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('#  include "foo"\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'string-literal'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'header-name'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testQcharSeq_03(self):
        """TestHeaderReconstuction "q-char-sequence" [3]."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('#  include "foo"abc\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'string-literal'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'header-name'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testQcharSeq_04(self):
        """TestHeaderReconstuction "q-char-sequence" [4]."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('#  include "foo"\nabc\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'string-literal'),
                PpToken.PpToken('\n',          'whitespace'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'header-name'),
                PpToken.PpToken('\n',          'whitespace'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testQcharSeq_05(self):
        """TestHeaderReconstuction "q-char-sequence" [5]."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('#  include "foo" \nabc\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'string-literal'),
                PpToken.PpToken(' \n',         'whitespace'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'header-name'),
                PpToken.PpToken(' \n',         'whitespace'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testQcharSeq_06(self):
        """TestHeaderReconstuction "q-char-sequence" [6]."""
        myObj = PpTokeniser.PpTokeniser()
        # q-char sequences
        myGen = myObj.genLexPptokenAndSeqWs('#include "inc/src.h"\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"inc/src.h"', 'string-literal'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"inc/src.h"', 'header-name'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testQcharSeq_07(self):
        """TestHeaderReconstuction "q-char-sequence" [7]. ISO/IEC 9899:1999 (E) 6.4.7-3 'Header names' using \\ is undefined"""
        myObj = PpTokeniser.PpTokeniser()
        # q-char sequences
        myGen = myObj.genLexPptokenAndSeqWs('#include "codeanalysis\\\\sourceannotations.h"\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken(r'"codeanalysis\\sourceannotations.h"', 'string-literal'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
#        print
#        print self.pprintTokensAsCtors(myToks)
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#', 'preprocessing-op-or-punc'),
                PpToken.PpToken('include', 'identifier'),
                PpToken.PpToken(' ', 'whitespace'),
                PpToken.PpToken('"', 'non-whitespace'),
                PpToken.PpToken('codeanalysis', 'identifier'),
                PpToken.PpToken('\\', 'non-whitespace'),
                PpToken.PpToken('\\', 'non-whitespace'),
                PpToken.PpToken('sourceannotations', 'identifier'),
                PpToken.PpToken('.', 'preprocessing-op-or-punc'),
                PpToken.PpToken('h', 'identifier'),
                PpToken.PpToken('"', 'non-whitespace'),
                PpToken.PpToken('\n', 'whitespace'),
        ]
#        print 'After reduceToksToHeaderName()'
#        print self.pprintTokensAsCtors(myToks)
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testQcharSeq_Fail_00(self):
        """TestHeaderReconstuction "q-char-sequence" fails [0]."""
        myObj = PpTokeniser.PpTokeniser()
        # Failures, well these do not correspond to a correct #include directive
        # as the sequence turns out wrong
        myGen = myObj.genLexPptokenAndSeqWs('#include "fo\no"\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"',           'non-whitespace'),
                PpToken.PpToken('fo',          'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                PpToken.PpToken('o',           'identifier'),
                PpToken.PpToken('"',           'non-whitespace'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        # Should be no change
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    # h-char sequences
    def testHcharSeq_00(self):
        """TestHeaderReconstuction "h-char-sequence" [0]."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('#include <foo>\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<',           'preprocessing-op-or-punc'),
                PpToken.PpToken('foo',         'identifier'),
                PpToken.PpToken('>',           'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<foo>',       'header-name'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testHcharSeq_01(self):
        """TestHeaderReconstuction "h-char-sequence" [1]."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('# include <foo>\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<',           'preprocessing-op-or-punc'),
                PpToken.PpToken('foo',         'identifier'),
                PpToken.PpToken('>',           'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<foo>',       'header-name'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testHcharSeq_02(self):
        """TestHeaderReconstuction "h-char-sequence" [2]."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('#  include <foo>\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<',           'preprocessing-op-or-punc'),
                PpToken.PpToken('foo',         'identifier'),
                PpToken.PpToken('>',           'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<foo>',       'header-name'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testHcharSeq_03(self):
        """TestHeaderReconstuction "h-char-sequence" [3]."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('#  include <foo>abc\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<',           'preprocessing-op-or-punc'),
                PpToken.PpToken('foo',         'identifier'),
                PpToken.PpToken('>',           'preprocessing-op-or-punc'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<foo>',       'header-name'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testHcharSeq_04(self):
        """TestHeaderReconstuction "h-char-sequence" [4]."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('#  include <foo>\nabc\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<',           'preprocessing-op-or-punc'),
                PpToken.PpToken('foo',         'identifier'),
                PpToken.PpToken('>',           'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',          'whitespace'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<foo>',       'header-name'),
                PpToken.PpToken('\n',          'whitespace'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testHcharSeq_05(self):
        """TestHeaderReconstuction "h-char-sequence" [5]."""
        myObj = PpTokeniser.PpTokeniser()
        myGen = myObj.genLexPptokenAndSeqWs('#  include <foo> \nabc\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<',           'preprocessing-op-or-punc'),
                PpToken.PpToken('foo',         'identifier'),
                PpToken.PpToken('>',           'preprocessing-op-or-punc'),
                PpToken.PpToken(' \n',         'whitespace'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('  ',          'whitespace'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<foo>',       'header-name'),
                PpToken.PpToken(' \n',         'whitespace'),
                PpToken.PpToken('abc',         'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testHcharSeq_06(self):
        """TestHeaderReconstuction "h-char-sequence" [6]."""
        myObj = PpTokeniser.PpTokeniser()
        myObj = PpTokeniser.PpTokeniser()
        # q-char sequences
        myGen = myObj.genLexPptokenAndSeqWs('#include <inc/src.h>\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<',           'preprocessing-op-or-punc'),
                PpToken.PpToken('inc',         'identifier'),
                PpToken.PpToken('/',           'preprocessing-op-or-punc'),
                PpToken.PpToken('src',         'identifier'),
                PpToken.PpToken('.',           'preprocessing-op-or-punc'),
                PpToken.PpToken('h',           'identifier'),
                PpToken.PpToken('>',           'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<inc/src.h>', 'header-name'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testHcharSeq_Fail_00(self):
        """TestHeaderReconstuction "h-char-sequence" fails [0]."""
        myObj = PpTokeniser.PpTokeniser()
        # Failures, well these do not correspond to a correct #include directive
        # as the sequence turns out wrong
        myGen = myObj.genLexPptokenAndSeqWs('#include <fo\no>\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('#',           'preprocessing-op-or-punc'),
                PpToken.PpToken('include',     'identifier'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<',           'preprocessing-op-or-punc'),
                PpToken.PpToken('fo',          'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                PpToken.PpToken('o',           'identifier'),
                PpToken.PpToken('>',           'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.reduceToksToHeaderName(myToks)
        # Should be no change
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testQcharSeqPostInclude_00(self):
        """TestHeaderReconstuction "q-char-sequence" not with the #include prefix."""
        myObj = PpTokeniser.PpTokeniser()
        # q-char sequences
        myGen = myObj.genLexPptokenAndSeqWs(' "foo"\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'string-literal'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self.assertEqual(myToks, eToks)
        # Now convert to header-name
        myToks = myObj.filterHeaderNames(myToks)
        eToks = [
                PpToken.PpToken('"foo"',       'header-name'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

    def testQcharSeqPostInclude_fails_00(self):
        """TestHeaderReconstuction "q-char-sequence" not with the #include prefix."""
        myObj = PpTokeniser.PpTokeniser()
        # q-char sequences
        myGen = myObj.genLexPptokenAndSeqWs('x"foo"\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken('x',           'identifier'),
                PpToken.PpToken('"foo"',       'string-literal'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self.assertEqual(myToks, eToks)
        self.assertEqual(myObj.filterHeaderNames(myToks), [])

    def testQcharSeqPostInclude_fails_01(self):
        """TestHeaderReconstuction "q-char-sequence" not with the #include prefix."""
        myObj = PpTokeniser.PpTokeniser()
        # q-char sequences
        myGen = myObj.genLexPptokenAndSeqWs(' "foo" <bar>\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)
        eToks = [
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('"foo"',       'string-literal'),
                PpToken.PpToken(' ',           'whitespace'),
                PpToken.PpToken('<',           'preprocessing-op-or-punc'),
                PpToken.PpToken('bar',         'identifier'),
                PpToken.PpToken('>',           'preprocessing-op-or-punc'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        myToks = myObj.filterHeaderNames(myToks)
        eToks = [
                PpToken.PpToken('"foo"',       'header-name'),
                PpToken.PpToken('<bar>',       'header-name'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)

class TestMisc(TestPpTokeniserBase):#TestGenerateLexPpTokens):
    def test_00(self):
        """TestMisc.test_00(): '@'"""
        myObj = PpTokeniser.PpTokeniser()
        # q-char sequences
        myGen = myObj.genLexPptokenAndSeqWs('@\n')
        myToks = [t for t in myGen]
        eToks = [
                PpToken.PpToken('@',           'identifier'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myGen)

    def testSpecial_01(self):
        """TestMisc [01]: There is a digraph here."""
        myStr = u"""#if 1
PASS
#else     and something
FAIL
#endif spurious #endif
"""
        #myStr = u"""and """
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myToks = []
        #print
        for t in myObj.next():
            #print t
            myToks.append(t)
        expToks = [
                PpToken.PpToken('#',            'preprocessing-op-or-punc'),
                PpToken.PpToken('if',           'identifier'),
                PpToken.PpToken(' ',            'whitespace'),
                PpToken.PpToken('1',            'pp-number'),
                PpToken.PpToken('\n',           'whitespace'),
                PpToken.PpToken('PASS',         'identifier'),
                PpToken.PpToken('\n',           'whitespace'),
                PpToken.PpToken('#',            'preprocessing-op-or-punc'),
                PpToken.PpToken('else',         'identifier'),
                PpToken.PpToken('     ',        'whitespace'),
                PpToken.PpToken('and',          'identifier'),
                PpToken.PpToken(' ',            'whitespace'),
                PpToken.PpToken('something',    'identifier'),
                PpToken.PpToken('\n',           'whitespace'),
                PpToken.PpToken('FAIL',         'identifier'),
                PpToken.PpToken('\n',           'whitespace'),
                PpToken.PpToken('#',            'preprocessing-op-or-punc'),
                PpToken.PpToken('endif',        'identifier'),
                PpToken.PpToken(' ',            'whitespace'),
                PpToken.PpToken('spurious',     'identifier'),
                PpToken.PpToken(' ',            'whitespace'),
                PpToken.PpToken('#',            'preprocessing-op-or-punc'),
                PpToken.PpToken('endif',        'identifier'),
                PpToken.PpToken('\n',           'whitespace'),
                ]
        #print
        #print
        #self._printDiff(myToks, expToks)
        #self.pprintTokensAsCtors(myToks)
        self.assertEqual(
            myToks,
            expToks
            )

    def test_10(self):
        """TestMisc [10]: Function macro."""
        myStr = u"""#include "spam.h"
/*
A function definition
*/
#define F(x) f(x)

"""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = myObj.next()
        actToks = []
        for t in myTokTypeGen:
            #print '%2d %2d %s' % (t.lineNum, t.colNum, t)
            actToks.append((t.lineNum, t.colNum, t.t))
        #print 'Actual:'
        #pprint.pprint(actToks)
        eToks = [
                 (1, 1, '#'),
                 (1, 2, 'include'),
                 (1, 9, ' '),
                 (1, 10, '"spam.h"'),
                 (1, 18, '\n'),
                 (2, 1, ' '),
                 (4, 3, '\n'),
                 (5, 1, '#'),
                 (5, 2, 'define'),
                 (5, 8, ' '),
                 (5, 9, 'F'),
                 (5, 10, '('),
                 (5, 11, 'x'),
                 (5, 12, ')'),
                 (5, 13, ' '),
                 (5, 14, 'f'),
                 (5, 15, '('),
                 (5, 16, 'x'),
                 (5, 17, ')'),
                 (5, 18, '\n\n')
                 ]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myTokTypeGen)
        self._printDiff(actToks, eToks)
        self.assertEqual(actToks, eToks)
        #print
        #print myObj.fileLocator

class TestPpTokeniserFileLocator(TestPpTokeniserBase):
    """Tests the file locator in the PpTokeniser."""
    def _checkLogicalPhysicalLines(self, theFl, theL, theP):
        for lineL in range(1, len(theL)+1):
            for colL in range(1, len(theL[lineL-1])+1):
                charL = theL[lineL-1][colL-1]
                lineP, colP = theFl.fileLocator.logicalToPhysical(lineL, colL)
                if len(theL[lineL-1]) == 1:
                    charP = '\n'
                else:
                    charP = theP[lineP-1][colP-1]
                self.assertEqual(charL, charP)

    def _pprintLogicalToPhysical(self, theObj, theLfile, thePfile):
        print(theObj.pformatLogicalToPhysical(theLfile, thePfile))
            
    def _printLogicalPhysicalLines(self, theFl, theL, theP):
        for lineL in range(1, len(theL)+1):
            for colL in range(1, len(theL[lineL-1])+1):
                charL = theL[lineL-1][colL-1]
                lineP, colP = theFl.logicalToPhysical(lineL, colL)
                charP = theP[lineP-1][colP-1]
                if charL == '\n':
                    charL = '\\n'
                if charP == '\n':
                    charP = '\\n'
                print('%s -> %s: "%s" -> "%s"' \
                    % (
                       str((lineL, colL)),
                       str((lineP, colP)),
                       charL,
                       charP))
         
    def test_00(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 2, FileLocation, one continuation."""
        myPpt = PpTokeniser.PpTokeniser()
        myPstrS = ['a\\\n', 'b\n', 'c\n',]
        myLineS = myPstrS[:]
        self.assertEquals(None, myPpt.lexPhases_2(myLineS))
        self.assertEqual(['ab\n', '\n', 'c\n', ], myLineS)
        #print
        #print 'Was:', myPstrS
        #print 'Now:', myLineS
        #print myPpt.fileLocator
        #self._printLogicalPhysicalLines(myPpt.fileLocator, myLineS, myPstrS)
        self._checkLogicalPhysicalLines(myPpt, myLineS, myPstrS)

    def test_01(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 2, FileLocation, two continuations."""
        myPpt = PpTokeniser.PpTokeniser()
        myPstrS = ['a\\\n', 'b\\\n', 'c\n',]
        myLineS = myPstrS[:]
        self.assertEquals(None, myPpt.lexPhases_2(myLineS))
        self.assertEqual(['abc\n', '\n', '\n', ], myLineS)
        #print
        #print 'Was:', myPstrS
        #print 'Now:', myLineS
        #print myPpt.fileLocator
        #self._printLogicalPhysicalLines(myPpt.fileLocator, myLineS, myPstrS)
        self._checkLogicalPhysicalLines(myPpt, myLineS, myPstrS)

    def test_02(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 2, FileLocation, three continuations."""
        myPpt = PpTokeniser.PpTokeniser()
        myPstrS = ['ab\\\n', 'c\\\n', 'd\\\n', 'ef\n',]
        myLstrSExp = ['abcdef\n', '\n', '\n', '\n', ]
        myLineS = myPstrS[:]
        self.assertEquals(None, myPpt.lexPhases_2(myLineS))
        self.assertEqual(myLstrSExp, myLineS)
        #print
        #print 'Was:', myPstrS
        #print 'Now:', myLineS
        #print myPpt.fileLocator
        #self._printLogicalPhysicalLines(myPpt.fileLocator, myLineS, myPstrS)
        self._checkLogicalPhysicalLines(myPpt, myLineS, myPstrS)

    def test_10(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 2, PpTokeniser.pLineCol."""
        myPpt = PpTokeniser.PpTokeniser()
        myPstrS = ['ab\\\n', 'c\\\n', 'd\\\n', 'ef\n',]
        myLineS = myPstrS[:]
        self.assertEquals(None, myPpt.lexPhases_2(myLineS))
        myLstrSExp = ['abcdef\n', '\n', '\n', '\n', ]
        self.assertEqual(myLstrSExp, myLineS)
        #print
        #print 'Was:', myPstrS
        #print 'Now:', myLineS
        #print myPpt.fileLocator
        #self._printLogicalPhysicalLines(myPpt.fileLocator, myLineS, myPstrS)
        self._checkLogicalPhysicalLines(myPpt, myLineS, myPstrS)
#        self.assertEqual((5, 1), myPpt.pLineCol)
        self.assertEqual((2, 1), myPpt.pLineCol)

class TestPpTokeniserOddCharacters(TestPpTokeniserBase):
    def test_00(self):
        """TestPpTokeniserOddCharacters.test_00() \x92 in a comment block."""
        myStr = u"""/* object\x92s state */
object\x92s state
"""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = myObj.next()
        actToks = [t for t in myTokTypeGen]
        eToks = [
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken(r'object\u0092s', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('state', 'identifier'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
#        print('Actual:')
#        self.pprintTokensAsCtors(actToks)
#        print('Exp:')
#        self.pprintTokensAsCtors(eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myTokTypeGen)
        self._printDiff(actToks, eToks)
        self.assertEqual(actToks, eToks)

class TestPpTokeniserPartialTokenStream(TestPpTokeniserBase):
    """Various tests for partial token streams."""
    def test_00(self):
        """TestPpTokeniserPartialTokenStream.test_00(): No new line in C++ comment, standard diagnostic raises."""
        myStr = u"""// Some comment. """
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = myObj.next()
        try:
            actToks = [t for t in myTokTypeGen]
            self.fail('ExceptionCppDiagnosticPartialTokenStream not raised')
        except CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream:
            pass

    def test_01(self):
        """TestPpTokeniserPartialTokenStream.test_01(): No new line in C++ comment, keep-going diagnostic does not raise."""
        myStr = u"""// Some comment. """
        myObj = PpTokeniser.PpTokeniser(
                    theFileObj=io.StringIO(myStr),
                    theDiagnostic=CppDiagnostic.PreprocessDiagnosticKeepGoing(),
                    )
        myTokTypeGen = myObj.next()
        actToks = [t for t in myTokTypeGen]
        #print 'Actual:'
        #pprint.pprint(actToks)
        #self.pprintTokensAsCtors(actToks)
        eToks = [
                 PpToken.PpToken(' ', 'whitespace'),
                 ]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, next, myTokTypeGen)
        self._printDiff(actToks, eToks)
        self.assertEqual(actToks, eToks)

class TestPpTokeniserLinux(TestPpTokeniserBase):
    """Various tests from the Linux Kernel."""
    def test_00(self):
        """TestPpTokeniserLinux.test_00(): alternative.h."""
        myStr = u"""#ifndef _ASM_X86_ALTERNATIVE_H
#define _ASM_X86_ALTERNATIVE_H

#include <linux/types.h>
#include <linux/stddef.h>
#include <linux/stringify.h>
#include <linux/jump_label.h>
#include <asm/asm.h>

/*
 * Alternative inline assembly for SMP.
 *
 * The LOCK_PREFIX macro defined here replaces the LOCK and
 * LOCK_PREFIX macros used everywhere in the source tree.
 *
 * SMP alternatives use the same data structures as the other
 * alternatives and the X86_FEATURE_UP flag to indicate the case of a
 * UP system running a SMP kernel.  The existing apply_alternatives()
 * works fine for patching a SMP kernel for UP.
 *
 * The SMP alternative tables can be kept after boot and contain both
 * UP and SMP versions of the instructions to allow switching back to
 * SMP at runtime, when hotplugging in a new CPU, which is especially
 * useful in virtualized environments.
 *
 * The very common lock prefix is handled as special case in a
 * separate table which is a pure address list without replacement ptr
 * and size information.  That keeps the table sizes small.
 */

#ifdef CONFIG_SMP
#define LOCK_PREFIX_HERE \
        ".section .smp_locks,\"a\"\n"    \
        ".balign 4\n"            \
        ".long 671f - .\n" /* offset */    \
        ".previous\n"            \
        "671:"

#define LOCK_PREFIX LOCK_PREFIX_HERE "\n\tlock; "

#else /* ! CONFIG_SMP */
#define LOCK_PREFIX_HERE ""
#define LOCK_PREFIX ""
#endif

struct alt_instr {
    u8 *instr;        /* original instruction */
    u8 *replacement;
    u16 cpuid;        /* cpuid bit set for replacement */
    u8  instrlen;        /* length of original instruction */
    u8  replacementlen;    /* length of new instruction, <= instrlen */
#ifdef CONFIG_X86_64
    u32 pad2;
#endif
};

extern void alternative_instructions(void);
extern void apply_alternatives(struct alt_instr *start, struct alt_instr *end);

struct module;

#ifdef CONFIG_SMP
extern void alternatives_smp_module_add(struct module *mod, char *name,
                    void *locks, void *locks_end,
                    void *text, void *text_end);
extern void alternatives_smp_module_del(struct module *mod);
extern void alternatives_smp_switch(int smp);
extern int alternatives_text_reserved(void *start, void *end);
#else
static inline void alternatives_smp_module_add(struct module *mod, char *name,
                           void *locks, void *locks_end,
                           void *text, void *text_end) {}
static inline void alternatives_smp_module_del(struct module *mod) {}
static inline void alternatives_smp_switch(int smp) {}
static inline int alternatives_text_reserved(void *start, void *end)
{
    return 0;
}
#endif    /* CONFIG_SMP */

/* alternative assembly primitive: */
#define ALTERNATIVE(oldinstr, newinstr, feature)            \
                                    \
      "661:\n\t" oldinstr "\n662:\n"                    \
      ".section .altinstructions,\"a\"\n"                \
      _ASM_ALIGN "\n"                            \
      _ASM_PTR "661b\n"                /* label           */    \
      _ASM_PTR "663f\n"                /* new instruction */    \
      "     .word " __stringify(feature) "\n"    /* feature bit     */    \
      "     .byte 662b-661b\n"            /* sourcelen       */    \
      "     .byte 664f-663f\n"            /* replacementlen  */    \
      ".previous\n"                            \
      ".section .discard,\"aw\",@progbits\n"                \
      "     .byte 0xff + (664f-663f) - (662b-661b)\n" /* rlen <= slen */    \
      ".previous\n"                            \
      ".section .altinstr_replacement, \"ax\"\n"            \
      "663:\n\t" newinstr "\n664:\n"        /* replacement     */    \
      ".previous"

/*
 * This must be included *after* the definition of ALTERNATIVE due to
 * <asm/arch_hweight.h>
 */
#include <asm/cpufeature.h>

/*
 * Alternative instructions for different CPU types or capabilities.
 *
 * This allows to use optimized instructions even on generic binary
 * kernels.
 *
 * length of oldinstr must be longer or equal the length of newinstr
 * It can be padded with nops as needed.
 *
 * For non barrier like inlines please define new variants
 * without volatile and memory clobber.
 */
#define alternative(oldinstr, newinstr, feature)            \
    asm volatile (ALTERNATIVE(oldinstr, newinstr, feature) : : : "memory")

/*
 * Alternative inline assembly with input.
 *
 * Pecularities:
 * No memory clobber here.
 * Argument numbers start with 1.
 * Best is to use constraints that are fixed size (like (%1) ... "r")
 * If you use variable sized constraints like "m" or "g" in the
 * replacement make sure to pad to the worst case length.
 * Leaving an unused argument 0 to keep API compatibility.
 */
#define alternative_input(oldinstr, newinstr, feature, input...)    \
    asm volatile (ALTERNATIVE(oldinstr, newinstr, feature)        \
        : : "i" (0), ## input)

/* Like alternative_input, but with a single output argument */
#define alternative_io(oldinstr, newinstr, feature, output, input...)    \
    asm volatile (ALTERNATIVE(oldinstr, newinstr, feature)        \
        : output : "i" (0), ## input)

/* Like alternative_io, but for replacing a direct call with another one. */
#define alternative_call(oldfunc, newfunc, feature, output, input...)    \
    asm volatile (ALTERNATIVE("call %P[old]", "call %P[new]", feature) \
        : output : [old] "i" (oldfunc), [new] "i" (newfunc), ## input)

/*
 * use this macro(s) if you need more than one output parameter
 * in alternative_io
 */
#define ASM_OUTPUT2(a...) a

struct paravirt_patch_site;
#ifdef CONFIG_PARAVIRT
void apply_paravirt(struct paravirt_patch_site *start,
            struct paravirt_patch_site *end);
#else
static inline void apply_paravirt(struct paravirt_patch_site *start,
                  struct paravirt_patch_site *end)
{}
#define __parainstructions    NULL
#define __parainstructions_end    NULL
#endif

extern void *text_poke_early(void *addr, const void *opcode, size_t len);

/*
 * Clear and restore the kernel write-protection flag on the local CPU.
 * Allows the kernel to edit read-only pages.
 * Side-effect: any interrupt handler running between save and restore will have
 * the ability to write to read-only pages.
 *
 * Warning:
 * Code patching in the UP case is safe if NMIs and MCE handlers are stopped and
 * no thread can be preempted in the instructions being modified (no iret to an
 * invalid instruction possible) or if the instructions are changed from a
 * consistent state to another consistent state atomically.
 * More care must be taken when modifying code in the SMP case because of
 * Intel's errata. text_poke_smp() takes care that errata, but still
 * doesn't support NMI/MCE handler code modifying.
 * On the local CPU you need to be protected again NMI or MCE handlers seeing an
 * inconsistent instruction while you patch.
 */
extern void *text_poke(void *addr, const void *opcode, size_t len);
extern void *text_poke_smp(void *addr, const void *opcode, size_t len);

#if defined(CONFIG_DYNAMIC_FTRACE) || defined(HAVE_JUMP_LABEL)
#define IDEAL_NOP_SIZE_5 5
extern unsigned char ideal_nop5[IDEAL_NOP_SIZE_5];
extern void arch_init_ideal_nop5(void);
#else
static inline void arch_init_ideal_nop5(void) {}
#endif

#endif /* _ASM_X86_ALTERNATIVE_H */
"""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = myObj.next()
        actToks = [t for t in myTokTypeGen]

class TestLexPhases_2_Linux(TestPpTokeniserBase):
    """Tests the phase two only on some thorny Linux issues..."""
    STR_COMPILER_H_FULL = r"""#ifndef __LINUX_COMPILER_H
#define __LINUX_COMPILER_H

#ifndef __ASSEMBLY__

#ifdef __CHECKER__
# define __user        __attribute__((noderef, address_space(1)))
# define __kernel    __attribute__((address_space(0)))
# define __safe        __attribute__((safe))
# define __force    __attribute__((force))
# define __nocast    __attribute__((nocast))
# define __iomem    __attribute__((noderef, address_space(2)))
# define __acquires(x)    __attribute__((context(x,0,1)))
# define __releases(x)    __attribute__((context(x,1,0)))
# define __acquire(x)    __context__(x,1)
# define __release(x)    __context__(x,-1)
# define __cond_lock(x,c)    ((c) ? ({ __acquire(x); 1; }) : 0)
# define __percpu    __attribute__((noderef, address_space(3)))
#ifdef CONFIG_SPARSE_RCU_POINTER
# define __rcu        __attribute__((noderef, address_space(4)))
#else
# define __rcu
#endif
extern void __chk_user_ptr(const volatile void __user *);
extern void __chk_io_ptr(const volatile void __iomem *);
#else
# define __user
# define __kernel
# define __safe
# define __force
# define __nocast
# define __iomem
# define __chk_user_ptr(x) (void)0
# define __chk_io_ptr(x) (void)0
# define __builtin_warning(x, y...) (1)
# define __acquires(x)
# define __releases(x)
# define __acquire(x) (void)0
# define __release(x) (void)0
# define __cond_lock(x,c) (c)
# define __percpu
# define __rcu
#endif

#ifdef __KERNEL__

#ifdef __GNUC__
#include <linux/compiler-gcc.h>
#endif

#define notrace __attribute__((no_instrument_function))

/* Intel compiler defines __GNUC__. So we will overwrite implementations
 * coming from above header files here
 */
#ifdef __INTEL_COMPILER
# include <linux/compiler-intel.h>
#endif

/*
 * Generic compiler-dependent macros required for kernel
 * build go below this comment. Actual compiler/compiler version
 * specific implementations come from the above header files
 */

struct ftrace_branch_data {
    const char *func;
    const char *file;
    unsigned line;
    union {
        struct {
            unsigned long correct;
            unsigned long incorrect;
        };
        struct {
            unsigned long miss;
            unsigned long hit;
        };
        unsigned long miss_hit[2];
    };
};

/*
 * Note: DISABLE_BRANCH_PROFILING can be used by special lowlevel code
 * to disable branch tracing on a per file basis.
 */
#if defined(CONFIG_TRACE_BRANCH_PROFILING) \
    && !defined(DISABLE_BRANCH_PROFILING) && !defined(__CHECKER__)
void ftrace_likely_update(struct ftrace_branch_data *f, int val, int expect);

#define likely_notrace(x)    __builtin_expect(!!(x), 1)
#define unlikely_notrace(x)    __builtin_expect(!!(x), 0)

#define __branch_check__(x, expect) ({                    \
            int ______r;                    \
            static struct ftrace_branch_data        \
                __attribute__((__aligned__(4)))        \
                __attribute__((section("_ftrace_annotated_branch"))) \
                ______f = {                \
                .func = __func__,            \
                .file = __FILE__,            \
                .line = __LINE__,            \
            };                        \
            ______r = likely_notrace(x);            \
            ftrace_likely_update(&______f, ______r, expect); \
            ______r;                    \
        })

/*
 * Using __builtin_constant_p(x) to ignore cases where the return
 * value is always the same.  This idea is taken from a similar patch
 * written by Daniel Walker.
 */
# ifndef likely
#  define likely(x)    (__builtin_constant_p(x) ? !!(x) : __branch_check__(x, 1))
# endif
# ifndef unlikely
#  define unlikely(x)    (__builtin_constant_p(x) ? !!(x) : __branch_check__(x, 0))
# endif

#ifdef CONFIG_PROFILE_ALL_BRANCHES
/*
 * "Define 'is'", Bill Clinton
 * "Define 'if'", Steven Rostedt
 */
#define if(cond, ...) __trace_if( (cond , ## __VA_ARGS__) )
#define __trace_if(cond) \
    if (__builtin_constant_p((cond)) ? !!(cond) :            \
    ({                                \
        int ______r;                        \
        static struct ftrace_branch_data            \
            __attribute__((__aligned__(4)))            \
            __attribute__((section("_ftrace_branch")))    \
            ______f = {                    \
                .func = __func__,            \
                .file = __FILE__,            \
                .line = __LINE__,            \
            };                        \
        ______r = !!(cond);                    \
        ______f.miss_hit[______r]++;                    \
        ______r;                        \
    }))
#endif /* CONFIG_PROFILE_ALL_BRANCHES */

#else
# define likely(x)    __builtin_expect(!!(x), 1)
# define unlikely(x)    __builtin_expect(!!(x), 0)
#endif

/* Optimization barrier */
#ifndef barrier
# define barrier() __memory_barrier()
#endif

/* Unreachable code */
#ifndef unreachable
# define unreachable() do { } while (1)
#endif

#ifndef RELOC_HIDE
# define RELOC_HIDE(ptr, off)                    \
  ({ unsigned long __ptr;                    \
     __ptr = (unsigned long) (ptr);                \
    (typeof(ptr)) (__ptr + (off)); })
#endif

#endif /* __KERNEL__ */

#endif /* __ASSEMBLY__ */

#ifdef __KERNEL__
/*
 * Allow us to mark functions as 'deprecated' and have gcc emit a nice
 * warning for each use, in hopes of speeding the functions removal.
 * Usage is:
 *         int __deprecated foo(void)
 */
#ifndef __deprecated
# define __deprecated        /* unimplemented */
#endif

#ifdef MODULE
#define __deprecated_for_modules __deprecated
#else
#define __deprecated_for_modules
#endif

#ifndef __must_check
#define __must_check
#endif

#ifndef CONFIG_ENABLE_MUST_CHECK
#undef __must_check
#define __must_check
#endif
#ifndef CONFIG_ENABLE_WARN_DEPRECATED
#undef __deprecated
#undef __deprecated_for_modules
#define __deprecated
#define __deprecated_for_modules
#endif

/*
 * Allow us to avoid 'defined but not used' warnings on functions and data,
 * as well as force them to be emitted to the assembly file.
 *
 * As of gcc 3.4, static functions that are not marked with attribute((used))
 * may be elided from the assembly file.  As of gcc 3.4, static data not so
 * marked will not be elided, but this may change in a future gcc version.
 *
 * NOTE: Because distributions shipped with a backported unit-at-a-time
 * compiler in gcc 3.3, we must define __used to be __attribute__((used))
 * for gcc >=3.3 instead of 3.4.
 *
 * In prior versions of gcc, such functions and data would be emitted, but
 * would be warned about except with attribute((unused)).
 *
 * Mark functions that are referenced only in inline assembly as __used so
 * the code is emitted even though it appears to be unreferenced.
 */
#ifndef __used
# define __used            /* unimplemented */
#endif

#ifndef __maybe_unused
# define __maybe_unused        /* unimplemented */
#endif

#ifndef __always_unused
# define __always_unused    /* unimplemented */
#endif

#ifndef noinline
#define noinline
#endif

/*
 * Rather then using noinline to prevent stack consumption, use
 * noinline_for_stack instead.  For documentaiton reasons.
 */
#define noinline_for_stack noinline

#ifndef __always_inline
#define __always_inline inline
#endif

#endif /* __KERNEL__ */

/*
 * From the GCC manual:
 *
 * Many functions do not examine any values except their arguments,
 * and have no effects except the return value.  Basically this is
 * just slightly more strict class than the `pure' attribute above,
 * since function is not allowed to read global memory.
 *
 * Note that a function that has pointer arguments and examines the
 * data pointed to must _not_ be declared `const'.  Likewise, a
 * function that calls a non-`const' function usually must not be
 * `const'.  It does not make sense for a `const' function to return
 * `void'.
 */
#ifndef __attribute_const__
# define __attribute_const__    /* unimplemented */
#endif

/*
 * Tell gcc if a function is cold. The compiler will assume any path
 * directly leading to the call is unlikely.
 */

#ifndef __cold
#define __cold
#endif

/* Simple shorthand for a section definition */
#ifndef __section
# define __section(S) __attribute__ ((__section__(#S)))
#endif

/* Are two types/vars the same type (ignoring qualifiers)? */
#ifndef __same_type
# define __same_type(a, b) __builtin_types_compatible_p(typeof(a), typeof(b))
#endif

/* Compile time object size, -1 for unknown */
#ifndef __compiletime_object_size
# define __compiletime_object_size(obj) -1
#endif
#ifndef __compiletime_warning
# define __compiletime_warning(message)
#endif
#ifndef __compiletime_error
# define __compiletime_error(message)
#endif

/*
 * Prevent the compiler from merging or refetching accesses.  The compiler
 * is also forbidden from reordering successive instances of ACCESS_ONCE(),
 * but only when the compiler is aware of some particular ordering.  One way
 * to make the compiler aware of ordering is to put the two invocations of
 * ACCESS_ONCE() in different C statements.
 *
 * This macro does absolutely -nothing- to prevent the CPU from reordering,
 * merging, or refetching absolutely anything at any time.  Its main intended
 * use is to mediate communication between process-level code and irq/NMI
 * handlers, all running on the same CPU.
 */
#define ACCESS_ONCE(x) (*(volatile typeof(x) *)&(x))

#endif /* __LINUX_COMPILER_H */
"""
    STR_COMPILER_H_01 = r"""
#if defined(CONFIG_TRACE_BRANCH_PROFILING) \
    && !defined(DISABLE_BRANCH_PROFILING) && !defined(__CHECKER__)
"""
    STR_COMPILER_H_02 = r"""
1234567890 \
1234567890
"""
    STR_COMPILER_H_03 = r"""
1234567890 \
1234567890 \
1234567890
"""
    STR_COMPILER_H_04 = r"""
1234567890 \
1234567890 \
1234567890 \
1234567890
"""
    STR_COMPILER_H_05 = r"""
123 \
123 \
123 \
123
"""
    
    # This is not a valid preproc file as no #endif
    STR_COMPILER_H_09 = r"""/*
 * Note: DISABLE_BRANCH_PROFILING can be used by special lowlevel code
 * to disable branch tracing on a per file basis.
 */
#if defined(CONFIG_TRACE_BRANCH_PROFILING) \
    && !defined(DISABLE_BRANCH_PROFILING) && !defined(__CHECKER__)
void ftrace_likely_update(struct ftrace_branch_data *f, int val, int expect);

#define likely_notrace(x)    __builtin_expect(!!(x), 1)
#define unlikely_notrace(x)    __builtin_expect(!!(x), 0)

#define __branch_check__(x, expect) ({                    \
            int ______r;                    \
            static struct ftrace_branch_data        \
                __attribute__((__aligned__(4)))        \
                __attribute__((section("_ftrace_annotated_branch"))) \
                ______f = {                \
                .func = __func__,            \
                .file = __FILE__,            \
                .line = __LINE__,            \
            };                        \
            ______r = likely_notrace(x);            \
            ftrace_likely_update(&______f, ______r, expect); \
            ______r;                    \
        })

/*
 * Using __builtin_constant_p(x) to ignore cases where the return
 * value is always the same.  This idea is taken from a similar patch
 * written by Daniel Walker.
 */
"""
    def _dumpLines(self, theLineS):
        print('_dumpLines():')
        l = 1
        for aL in theLineS:
            sys.stdout.write('%4d:%s ' % (l, aL))
            l += 1
    
    def testPhase_2_00(self):
        """TestLexPhases_2_Linux.testPhase_2_00(): compiler.h"""
        return
        assert(0)
        myObj = PpTokeniser.PpTokeniser()
        myStr = self.STR_COMPILER_H_FULL
        myLines = [l+'\n' for l in myStr.split('\n')]
        print()
#        for aLine in myLines:
#            print '"%s"' % aLine
        self.assertEquals(None, myObj.lexPhases_2(myLines))
        print()
#        print '\n'.join(myLines)
        print()
        print(myObj.fileLocator)
#        self.assertEqual(['\n',], myLines)

    def testPhase_2_01(self):
        """TestLexPhases_2_Linux.testPhase_2_01(): compiler.h"""
        return
        assert(0)
        myObj = PpTokeniser.PpTokeniser()
        myStr = self.STR_COMPILER_H_01
        myLines = [l+'\n' for l in myStr.split('\n')]
        print()
        for aLine in myLines:
            print('"%s"' % aLine)
        self.assertEquals(None, myObj.lexPhases_2(myLines))
        print()
        print('\n'.join(myLines))
#        print
#        print myObj.fileLocator
#        self.assertEqual(['\n',], myLines)

    def testPhase_2_02(self):
        """TestLexPhases_2_Linux.testPhase_2_02(): compiler.h"""
        myObj = PpTokeniser.PpTokeniser()
        myStr = self.STR_COMPILER_H_02
        myLines = [l+'\n' for l in myStr.split('\n')]
#        print
#        self._dumpLines(myLines)
        self.assertEquals(None, myObj.lexPhases_2(myLines))
#        self._dumpLines(myLines)
        self.assertEqual(
            [
                '\n',
                '1234567890 1234567890\n',
                '\n',
                '\n',
            ],
            myLines,
        )

    def testPhase_2_03(self):
        """TestLexPhases_2_Linux.testPhase_2_03(): compiler.h"""
        myObj = PpTokeniser.PpTokeniser()
        myStr = self.STR_COMPILER_H_03
        myLines = [l+'\n' for l in myStr.split('\n')]
#        print
#        self._dumpLines(myLines)
        self.assertEquals(None, myObj.lexPhases_2(myLines))
#        self._dumpLines(myLines)
        self.assertEqual(
            [
                '\n',
                '1234567890 1234567890 1234567890\n',
                '\n',
                '\n',
                '\n',
            ],
            myLines,
        )

    def testPhase_2_04(self):
        """TestLexPhases_2_Linux.testPhase_2_04(): compiler.h"""
        myObj = PpTokeniser.PpTokeniser()
        myStr = self.STR_COMPILER_H_04
        myLines = [l+'\n' for l in myStr.split('\n')]
#        print
#        self._dumpLines(myLines)
        self.assertEquals(None, myObj.lexPhases_2(myLines))
#        self._dumpLines(myLines)
        self.assertEqual(
            [
                '\n',
                '1234567890 1234567890 1234567890 1234567890\n',
                '\n',
                '\n',
                '\n',
                '\n',
            ],
            myLines,
        )

    def testPhase_2_05(self):
        """TestLexPhases_2_Linux.testPhase_2_05(): compiler.h"""
        myObj = PpTokeniser.PpTokeniser()
        myStr = self.STR_COMPILER_H_05
        myLines = [l+'\n' for l in myStr.split('\n')]
#        print
#        self._dumpLines(myLines)
        self.assertEquals(None, myObj.lexPhases_2(myLines))
#        self._dumpLines(myLines)
        self.assertEqual(
            [
                '\n',
                '123 123 123 123\n',
                '\n',
                '\n',
                '\n',
                '\n',
            ],
            myLines,
        )

class Special(TestPpTokeniserBase):
    def test_00(self):
        """Special.test_00(): """
        myStr = u"""Debug::print(Debug::Classes,0,"  New class `%s' (sec=0x%08x)! #tArgLists=%d\n",
            fullName.data(),root->section,root->tArgLists ? (int)root->tArgLists->count() : -1);"""
        myStr = u"""\"  New class `%s' (sec=0x%08x)! #tArgLists=%d\n",
            fullName.data(),root->section,root->tArgLists ? (int)root->tArgLists->count() : -1);"""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        i = 0
        #print
        for t in myObj.next():
            #print i, t
            i += 1
    
    def test_01(self):
        """Special.test_01(): """
        myObj = PpTokeniser.PpTokeniser()
        myLines = [
            "\"  New class `%s' (sec=0x%08x)! #tArgLists=%d\\n\"",
            "fullName.data(),root->section,root->tArgLists ? (int)root->tArgLists->count() : -1);",
            ]
        myObj._convertToLexCharset(myLines)
        # Special
        myObj.resetTokType()
        myStr = u"""\"  New class `%s' (sec=0x%08x)! #tArgLists=%d\\n",
            fullName.data(),root->section,root->tArgLists ? (int)root->tArgLists->count() : -1);"""
        myStr = u''.join(myLines)
        #print 'myStr'
        #print myStr
        self.assertEqual(48, myObj._sliceStringLiteral(myStr, 0))

    def test_02(self):
        """Special.test_02(): """
        myStr = u"""/***
*math.h - definitions and declarations for math library
*
*       Copyright (c) Microsoft Corporation. All rights reserved.
*
*Purpose:
*       This file contains constant definitions and external subroutine
*       declarations for the math subroutine library.
*       [ANSI/System V]
*
*       [Public]
*
****/

#ifndef _INC_MATH
#define _INC_MATH

#include <crtdefs.h>

#ifdef  _MSC_VER
/*
 * Currently, all MS C compilers for Win32 platforms default to 8 byte
 * alignment.
 */
#pragma pack(push,_CRT_PACKING)
#endif  /* _MSC_VER */

#ifdef __cplusplus
extern "C" {
#endif

#ifndef __assembler /* Protect from assembler */

/* Definition of _exception struct - this struct is passed to the matherr
 * routine when a floating point exception is detected
 */

#ifndef _EXCEPTION_DEFINED
struct _exception {
        int type;       /* exception type - see below */
        char *name;     /* name of function where error occured */
        double arg1;    /* first argument to function */
        double arg2;    /* second argument (if any) to function */
        double retval;  /* value to be returned by function */
        } ;

#define _EXCEPTION_DEFINED
#endif


/* Definition of a _complex struct to be used by those who use cabs and
 * want type checking on their argument
 */

#ifndef _COMPLEX_DEFINED
struct _complex {
        double x,y; /* real and imaginary parts */
        } ;

#if     !__STDC__ && !defined (__cplusplus)
/* Non-ANSI name for compatibility */
#define complex _complex
#endif

#define _COMPLEX_DEFINED
#endif
#endif  /* __assembler */
"""
        myStr = u"""#if     !__STDC__ && !defined (__cplusplus)
/* Non-ANSI name for compatibility */
#define complex _complex
#endif

#define _COMPLEX_DEFINED
#endif
#endif  /* __assembler */
"""
        myStr = u"""#define complex _complex
"""
        myStr = u"#define complex _complex"
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        i = 0
#        print
#        for t in myObj.next():
#            print i, t
#            i += 1
    
class NullClass(TestPpTokeniserBase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestWordsFoundIn))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestWordsFoundInUpTo))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexCharset))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserTrigraphs))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserDigraphs))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexComment))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexHeader))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexPpnumber))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexName))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexKey))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexOperators))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexLiteral))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexIcon))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexCcon))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexFcon))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexString))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexBool))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLexPptoken))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGenerateLexPpTokens))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLexPhases_0))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLexPhases_1))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLexPhases_2))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGenerateLexPpTokensUnget))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHeaderReconstuction))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMisc))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserFileLocator))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserOddCharacters))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserPartialTokenStream))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserLinux))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLexPhases_2_Linux))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Special))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

#################
# End: Unit tests
#################

def usage():
    print("""TestPpTokeniser.py - Tests the PpTokeniser source code
    according to ISO/IEC 14882:1998(E).
Usage:
python TestPpTokeniser.py [-h --help]

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
    print('Pp.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
    print(__rights__)
    print()
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help",])
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
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    clkStart = time.clock()
    if len(args) != 0:
        usage()
        print('ERROR: Wrong number of arguments!')
        sys.exit(1)
    unitTest()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
