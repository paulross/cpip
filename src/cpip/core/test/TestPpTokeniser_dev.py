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
import os
import unittest
import time
import logging
import io
import pprint

from cpip.core import PpTokeniser, FileLocation, CppDiagnostic, PpToken  

########################################
# Section: Unit tests
########################################

class TestPpTokeniserBase(unittest.TestCase):
    """Base class for test classes that provides common functionality."""
    def _printDiff(self, actual, expected):
        if actual != expected:
            print()
            i = 0
            for t, e in map(None, actual, expected):
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

class TestWordsFoundIn(TestPpTokeniserBase):
    """Tests PpTokeniser._wordFoundIn()."""

    def testWordFoundIn(self):
        """PpTokeniser._wordFoundIn()"""
        myObj = PpTokeniser.PpTokeniser()
        # Found
        self.assertEqual(0, myObj._wordFoundIn('Hello world', 'Hello'))
        self.assertEqual(6, myObj._wordFoundIn('Hello world', 'world'))
        # Not found
        self.assertEqual(-1, myObj._wordFoundIn('Hello world', 'earth'))
        self.assertEqual(-1, myObj._wordFoundIn('Hello world', ''))
        self.assertEqual(-1, myObj._wordFoundIn('Hello world', 'worldly'))

    def testWordsFoundIn(self):
        """PpTokeniser._wordsFoundIn()"""
        myObj = PpTokeniser.PpTokeniser()
        # Found
        self.assertEqual(0, myObj._wordsFoundIn('Hello world',
                                               ('Hello', 'world')))
        self.assertEqual(6, myObj._wordsFoundIn('Hello world',
                                               ('world', 'Hello')))
        self.assertNotEqual(-1, myObj._wordsFoundIn('Hello world',
                                               set(('world', 'Hello'))))
        # Not found
        self.assertEqual(-1, myObj._wordsFoundIn('Hello world',
                                                ('', 'earth', 'worldly')))
        self.assertEqual(-1, myObj._wordsFoundIn('Hello world',
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
    """Tests Trigraph replacement."""
    def setUp(self):
        pass

    def testDigraphs(self):
        """ISO/IEC 14882:1998(E) 2.5 Alternative tokens [lex.digraph]."""
        myObj = PpTokeniser.PpTokeniser()
        # Found
        # TODO: A few more variations
        myToks = ['<%',]
        myObj._translateDigraphs(myToks)
        self.assertEqual(['{',], myToks)

    def testDigraphs_no_change(self):
        """ISO/IEC 14882:1998(E) 2.5 Alternative tokens [lex.digraph]. no digraph."""
        myObj = PpTokeniser.PpTokeniser()
        myToks = ['a', 'b', 'c',]
        myObj._translateDigraphs(myToks)
        self.assertEqual(['a', 'b', 'c',], myToks)

class TestExpressionLexComment(TestPpTokeniserBase):
    """Test comment identification."""

    def testLexCommentCComplete(self):
        """ISO/IEC 14882:1998(E) 2.7 Header names [lex.comment] C comments complete."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(4, myObj._sliceLexComment(list('/**/')))
        self.assertEqual(5, myObj._sliceLexComment(list('/* */')))
        self.assertEqual(5, myObj._sliceLexComment(list('/* */   */')))
        self.assertEqual(8, myObj._sliceLexComment(list('/* // */')))
        self.assertEqual(8, myObj._sliceLexComment(list('/* // */ ')))

    def testLexCommentCIncomplete(self):
        """ISO/IEC 14882:1998(E) 2.7 Header names [lex.comment] C comments incomplete."""
        myObj = PpTokeniser.PpTokeniser()
        # Failures
        self.assertEqual(0, myObj._sliceLexComment(list(' /**/')))
        self.assertEqual(0, myObj._sliceLexComment(list('/ **/')))
        myStr = '/*'
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                          myObj._sliceLexComment, list(myStr))
        myStr = '/* *  '
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                          myObj._sliceLexComment, list(myStr))
        myStr = '/* * /'
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                          myObj._sliceLexComment, list(myStr))

    def testLexCommentCplusplusComplete(self):
        """ISO/IEC 14882:1998(E) 2.7 Header names [lex.comment] C++ comments complete."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(2, myObj._sliceLexComment(list('//\n')))
        self.assertEqual(3, myObj._sliceLexComment(list('// \n')))
        self.assertEqual(4, myObj._sliceLexComment(list('//  \n')))

    def testLexCommentCplusplusIncomplete(self):
        """ISO/IEC 14882:1998(E) 2.7 Header names [lex.comment] C++ comments incomplete."""
        myObj = PpTokeniser.PpTokeniser()
        # Failures
        self.assertEqual(0, myObj._sliceLexComment(list(' //')))
        self.assertEqual(0, myObj._sliceLexComment(list('/ /')))
        self.assertEqual(0, myObj._sliceLexComment(list(' //  ')))
        self.assertEqual(0, myObj._sliceLexComment(list('/ /  ')))
        myStr = '//'
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                          myObj._sliceLexComment, list(myStr))
        myStr = '// '
        self.assertRaises(CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
                          myObj._sliceLexComment, list(myStr))
        myStr = '//  '
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
        self.assertEqual(7, myObj._sliceLexHeader(list('"std.h"')))
        self.assertEqual(myObj.cppTokType, 'header-name')
        self.assertEqual(7, myObj._sliceLexHeader(list('<std.h>')))
        self.assertEqual(myObj.cppTokType, 'header-name')
        self.assertEqual(7, myObj._sliceLexHeader(list('"std.h" ')))
        self.assertEqual(myObj.cppTokType, 'header-name')
        self.assertEqual(7, myObj._sliceLexHeader(list('<std.h>   ')))
        self.assertEqual(myObj.cppTokType, 'header-name')
        # Failures

    def testLexHeaderWithNull(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - q-char-sequence with null char."""
        myObj = PpTokeniser.PpTokeniser()
        self.assertEqual(0, myObj._sliceLexHeader(list("abc\0xyz")))

    def testLexHeaderHcharSeq(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - h-char-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(5, myObj._sliceLexHeaderHcharSequence(list('std.h')))
        self.assertEqual(8, myObj._sliceLexHeaderHcharSequence(list('std.h   ')))
        ## Failures
        #for aWord in set(('\'', '\\', '/*', '//', '"')):
        #    myStr = 'std%s.h' % aWord
        #    self.assertRaises(PpTokeniser.ExceptionCpipTokeniserUndefinedLocal,
        #                      myObj._sliceLexHeaderHcharSequence, list(myStr))
        #    try:
        #        myObj._sliceLexHeaderHcharSequence(list(myStr))
        #    except PpTokeniser.ExceptionCpipTokeniserUndefinedLocal, err:
        #        self.assertEqual(list(myStr), err._localString)
        #        self.assertEqual(3, err._localIdx)

    def testLexHeaderQcharSeq(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - q-char-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(5, myObj._sliceLexHeaderQcharSequence(list('std.h')))
        self.assertEqual(8, myObj._sliceLexHeaderQcharSequence(list('std.h   ')))
        # Failures
        for aWord in set(('\'', '\\', '//', '/*')):
            myStr = """std%s.h""" % aWord
            self.assertEqual(0, myObj._sliceLexHeaderQcharSequence(list(myStr)))
            #self.assertRaises(PpTokeniser.ExceptionCpipTokeniserUndefinedLocal,
            #                  myObj._sliceLexHeaderQcharSequence, list(myStr))
            #try:
            #    myObj._sliceLexHeaderQcharSequence(list(myStr))
            #except PpTokeniser.ExceptionCpipTokeniserUndefinedLocal, err:
            #    self.assertEqual(list(myStr), err._localString)
            #    self.assertEqual(3, err._localIdx)

    def testLexHeaderHcharSeqExceptionString(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - h-char-sequence, bad characters."""
        myObj = PpTokeniser.PpTokeniser()
        for aWord in set(('\'', '\\', '"', '//', '/*')):
            myStr = """std%s.h""" % aWord
            self.assertEqual(0, myObj._sliceLexHeaderHcharSequence(list(myStr)))
            #try:
            #    self.assertEqual(5, myObj._sliceLexHeaderHcharSequence(list("std%s.h" % aWord)))
            #    self.fail('Excepton not raised')
            #except PpTokeniser.ExceptionCpipTokeniserUndefinedLocal, err:
            #    self.assertEqual('[\'s\', \'t\', \'d\', "\'", \'.\', \'h\'] [3]', str(err))

    def testLexHeaderQcharSeqExceptionString(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - q-char-sequence bad characters."""
        myObj = PpTokeniser.PpTokeniser()
        for aWord in set(('\'', '\\', '/*', '//')):
            self.assertEqual(0, myObj._sliceLexHeaderQcharSequence(list("std%s.h" % aWord)))
            #try:
            #    self.assertEqual(5, myObj._sliceLexHeaderQcharSequence(list("std%s.h" % aWord)))
            #    self.fail('Excepton not raised')
            #except PpTokeniser.ExceptionCpipTokeniserUndefinedLocal, err:
            #    self.assertEqual('[\'s\', \'t\', \'d\', "\'", \'.\', \'h\'] [3]', str(err))

    def testLexHeaderWithDirectorySeperatorBackslash(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - h/q-char-sequence with \\ fails."""
        myObj = PpTokeniser.PpTokeniser()
        self.assertEqual(0, myObj._sliceLexHeader(list('"inc\\src.h"')))
        self.assertEqual(0, myObj._sliceLexHeader(list('<inc\\src.h>')))

    def testLexHeaderWithDirectorySeperatorForwardslash(self):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - h/q-char-sequence with / succeeds."""
        myObj = PpTokeniser.PpTokeniser()
        self.assertEqual(11, myObj._sliceLexHeader(list('"inc/src.h"')))
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
        self.assertEqual(1, myObj._sliceLexPpnumber(list('1')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(2, myObj._sliceLexPpnumber(list('.1')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(5, myObj._sliceLexPpnumber(list('1.234')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(7, myObj._sliceLexPpnumber(list('1.234e+')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(7, myObj._sliceLexPpnumber(list('1.234E+')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(7, myObj._sliceLexPpnumber(list('1.234e-')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(7, myObj._sliceLexPpnumber(list('1.234E-')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(9, myObj._sliceLexPpnumber(list('1.234E-89')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(12, myObj._sliceLexPpnumber(list('1.234E-89e+4')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(3, myObj._sliceLexPpnumber(list('9ab')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(2, myObj._sliceLexPpnumber(list('1U')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(2, myObj._sliceLexPpnumber(list('1L')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(3, myObj._sliceLexPpnumber(list('1UL')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        # Failures


class TestExpressionLexName(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexName(self):
        """ISO/IEC 14882:1998(E) 2.10 Identifiers [lex.name]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(4, myObj._sliceLexName(list('ab_9')))
        self.assertEqual(myObj.cppTokType, 'identifier')
        self.assertEqual(10, myObj._sliceLexName(list('ab_9\\u0123')))
        self.assertEqual(myObj.cppTokType, 'identifier')
        self.assertEqual(10, myObj._sliceLexName(list('ab_\\u01239')))
        self.assertEqual(myObj.cppTokType, 'identifier')
        # Failures
        self.assertEqual(0, myObj._sliceLexName(list('9ab')))
        self.assertEqual(myObj.cppTokType, None)
        self.assertEqual(0, myObj._sliceLexName(list(' ab')))
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
        self.assertEqual(2, myObj._sliceLexOperators(list('<<')))
        self.assertEqual(3, myObj._sliceLexOperators(list('<<=')))
        # Failures
        self.assertEqual(0, myObj._sliceLexOperators(list('9ab')))
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
        self.assertEqual(6, myObj._sliceUniversalCharacterName(list('\\u0123')))
        self.assertEqual(6, myObj._sliceUniversalCharacterName(list('\\u1234')))
        self.assertEqual(6, myObj._sliceUniversalCharacterName(list('\\uabcd')))
        self.assertEqual(6, myObj._sliceUniversalCharacterName(list('\\uEEFF')))
        self.assertEqual(10, myObj._sliceUniversalCharacterName(list('\\U0123DEFA')))
        self.assertEqual(10, myObj._sliceUniversalCharacterName(list('\\U1234abcd')))
        self.assertEqual(10, myObj._sliceUniversalCharacterName(list('\\Uabcd0124')))
        self.assertEqual(10, myObj._sliceUniversalCharacterName(list('\\UEEFF01234')))
        # Failures
        # Space prefix
        self.assertEqual(0, myObj._sliceUniversalCharacterName(list('  abcd')))

class TestExpressionLexLiteral(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexLiteral(self):
        """ISO/IEC 14882:1998(E) 2.13 Literals [lex.literal]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        # Integers
        self.assertEqual(5, myObj._sliceLiteral(list('01234')))
        # Character
        self.assertEqual(3, myObj._sliceLiteral(list("'a'")))
        self.assertEqual(4, myObj._sliceLiteral(list("L'a'")))
        # Floating
        self.assertEqual(7, myObj._sliceLiteral(list('123.456')))
        self.assertEqual(10, myObj._sliceLiteral(list('123.456e12')))
        self.assertEqual(11, myObj._sliceLiteral(list('123.456e12f')))
        self.assertEqual(8, myObj._sliceLiteral(list('123.456f')))
        self.assertEqual(6, myObj._sliceLiteral(list('123e12')))
        self.assertEqual(7, myObj._sliceLiteral(list('123e12L')))
        # String
        self.assertEqual(2, myObj._sliceLiteral(list('""')))
        self.assertEqual(3, myObj._sliceLiteral(list('L""')))
        self.assertEqual(5, myObj._sliceLiteral(list('"abc"')))
        self.assertEqual(6, myObj._sliceLiteral(list('L"abc"')))
        # Bool
        self.assertEqual(4, myObj._sliceLiteral(list('true')))
        # Failures
        # Space prefix
        self.assertEqual(0, myObj._sliceLiteral(list(' 0123')))

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
        # TODO Confirm this
        # C spec says "An octal constant consists of the prefix 0 optionally followed by a sequence of the digits 0 through 7 only.

        self.assertEqual(0, myObj._sliceIntegerLiteral(list('0')))
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
        # Bad octal
        self.assertEqual(0, myObj._sliceIntegerLiteral(list('08')))




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
        self.assertEqual(2, myObj._sliceOctalLiteral(list('01')))
        self.assertEqual(4, myObj._sliceOctalLiteral(list('0123')))
        self.assertEqual(8, myObj._sliceOctalLiteral(list('01234567')))
        self.assertEqual(4, myObj._sliceOctalLiteral(list('0123 and something else')))
        # Failures
        # TODO is this true?
        self.assertEqual(0, myObj._sliceOctalLiteral(list('0')))
        # No leading zero
        self.assertEqual(0, myObj._sliceOctalLiteral(list('1')))
        self.assertEqual(0, myObj._sliceOctalLiteral(list('123')))
        # Out of range
        self.assertEqual(0, myObj._sliceOctalLiteral(list('99')))
        self.assertEqual(0, myObj._sliceOctalLiteral(list('099')))
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
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('u')))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('U')))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('l')))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('L')))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('ul')))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('uL')))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('Ul')))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('UL')))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('lu')))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('lU')))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('Lu')))
        self.assertEqual(2, myObj._sliceIntegerSuffix(list('LU')))
        # Partial
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('uu')))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('uU')))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('Uu')))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('UU')))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('ll')))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('lL')))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('Ll')))
        self.assertEqual(1, myObj._sliceIntegerSuffix(list('LL')))
        # Failures
        # No x
        self.assertEqual(0, myObj._sliceIntegerSuffix(list('0')))

    def testLexIconUnsignedSuffix(self):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - unsigned-suffix."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._sliceUnsignedSuffix(list('u')))
        self.assertEqual(1, myObj._sliceUnsignedSuffix(list('U')))
        self.assertEqual(1, myObj._sliceUnsignedSuffix(list('uu')))
        self.assertEqual(1, myObj._sliceUnsignedSuffix(list('UU')))
        # Failures
        # Long
        self.assertEqual(0, myObj._sliceUnsignedSuffix(list('l')))
        self.assertEqual(0, myObj._sliceUnsignedSuffix(list('L')))
        # Digit
        self.assertEqual(0, myObj._sliceIntegerSuffix(list('0')))

    def testLexIconLongSuffix(self):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - long-suffix."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._sliceLongSuffix(list('l')))
        self.assertEqual(1, myObj._sliceLongSuffix(list('L')))
        self.assertEqual(1, myObj._sliceLongSuffix(list('ll')))
        self.assertEqual(1, myObj._sliceLongSuffix(list('LL')))
        # Failures
        # Unsigned
        self.assertEqual(0, myObj._sliceLongSuffix(list('u')))
        self.assertEqual(0, myObj._sliceLongSuffix(list('U')))
        # Digit
        self.assertEqual(0, myObj._sliceLongSuffix(list('0')))

class TestExpressionLexCcon(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexCcon(self):
        """ISO/IEC 14882:1998(E) 2.13.1 Character literals [lex.ccon]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(3, myObj._sliceCharacterLiteral(list("'a'")))
        self.assertEqual(4, myObj._sliceCharacterLiteral(list("L'a'")))
        self.assertEqual(4, myObj._sliceCharacterLiteral(list("'\\b'")))
        self.assertEqual(5, myObj._sliceCharacterLiteral(list("L'\\b'")))
        # Failures
        myObj._sliceCharacterLiteral(list("''"))
        self.assertEqual(0, myObj._sliceCharacterLiteral(list("''")))
        self.assertEqual(0, myObj._sliceCharacterLiteral(list("'a")))
        self.assertEqual(0, myObj._sliceCharacterLiteral(list("'")))
        self.assertEqual(0, myObj._sliceCharacterLiteral(list("L''")))
        # Space prefix
        self.assertEqual(0, myObj._sliceCharacterLiteral(list(' 0123')))

    def testLexCconEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        # Simple
        self.assertEqual(2, myObj._sliceEscapeSequence(list('\\\\')))
        # Octal
        self.assertEqual(4, myObj._sliceEscapeSequence(list('\\000')))
        # Hex
        self.assertEqual(3, myObj._sliceEscapeSequence(list('\\x0')))
        # Failures
        self.assertEqual(0, myObj._sliceEscapeSequence(list('\\z')))

    def testLexCconSimpleEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - simple-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(2, myObj._sliceSimpleEscapeSequence(list('\\\\')))
        # TODO
        # Failures
        self.assertEqual(0, myObj._sliceSimpleEscapeSequence(list('\\z')))

    def testLexCconOctalEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - octal-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(2, myObj._sliceOctalEscapeSequence(list('\\0')))
        self.assertEqual(3, myObj._sliceOctalEscapeSequence(list('\\00')))
        self.assertEqual(4, myObj._sliceOctalEscapeSequence(list('\\000')))
        self.assertEqual(4, myObj._sliceOctalEscapeSequence(list('\\012')))
        self.assertEqual(4, myObj._sliceOctalEscapeSequence(list('\\345')))
        self.assertEqual(3, myObj._sliceOctalEscapeSequence(list('\\67')))
        self.assertEqual(4, myObj._sliceOctalEscapeSequence(list('\\0000')))
        self.assertEqual(4, myObj._sliceOctalEscapeSequence(list('\\00000')))
        self.assertEqual(2, myObj._sliceOctalEscapeSequence(list('\\09')))
        # Failures
        # No excape character
        self.assertEqual(0, myObj._sliceOctalEscapeSequence(list('0123')))
        # Bad character
        self.assertEqual(0, myObj._sliceOctalEscapeSequence(list('\\9')))

    def testLexCconHexadecimalEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - hexadecimal-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(3, myObj._sliceHexadecimalEscapeSequence(list('\\x0')))
        self.assertEqual(24, myObj._sliceHexadecimalEscapeSequence(list('\\x0123456789abcdefABCDEF')))
        # Failures
        # No excape character
        self.assertEqual(0, myObj._sliceHexadecimalEscapeSequence(list('0123')))
        # Bad character
        self.assertEqual(0, myObj._sliceHexadecimalEscapeSequence(list('\\xG')))

class TestExpressionLexFcon(TestPpTokeniserBase):
    """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon]."""
    def setUp(self):
        pass

    def testFloatingLiteral(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(7, myObj._sliceFloatingLiteral(list('123.456')))
        self.assertEqual(10, myObj._sliceFloatingLiteral(list('123.456e12')))
        self.assertEqual(11, myObj._sliceFloatingLiteral(list('123.456e12f')))
        self.assertEqual(8, myObj._sliceFloatingLiteral(list('123.456f')))
        self.assertEqual(6, myObj._sliceFloatingLiteral(list('123e12')))
        self.assertEqual(7, myObj._sliceFloatingLiteral(list('123e12L')))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteral(list('123')))
        self.assertEqual(0, myObj._sliceFloatingLiteral(list('g')))
        self.assertEqual(0, myObj._sliceFloatingLiteral(list('0g')))
        self.assertEqual(0, myObj._sliceFloatingLiteral(list('e + 123')))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteral(list(' 0123')))

    def testLexFconFractionalConstant(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - fractional-constant."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(7, myObj._sliceFloatingLiteralFractionalConstant(list('123.456')))
        self.assertEqual(4, myObj._sliceFloatingLiteralFractionalConstant(list('.456')))
        self.assertEqual(4, myObj._sliceFloatingLiteralFractionalConstant(list('123.')))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteralFractionalConstant(list('123')))
        self.assertEqual(0, myObj._sliceFloatingLiteralFractionalConstant(list('g')))
        self.assertEqual(0, myObj._sliceFloatingLiteralFractionalConstant(list('0g')))
        self.assertEqual(0, myObj._sliceFloatingLiteralFractionalConstant(list('e + 123')))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteralFractionalConstant(list(' 0123')))

    def testLexFconExponentPart(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - exponent-part."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(5, myObj._sliceFloatingLiteralExponentPart(list('e+123')))
        self.assertEqual(5, myObj._sliceFloatingLiteralExponentPart(list('E+123')))
        self.assertEqual(5, myObj._sliceFloatingLiteralExponentPart(list('e-123')))
        self.assertEqual(5, myObj._sliceFloatingLiteralExponentPart(list('E-123')))
        self.assertEqual(4, myObj._sliceFloatingLiteralExponentPart(list('e123')))
        self.assertEqual(4, myObj._sliceFloatingLiteralExponentPart(list('E123')))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('0123')))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('g')))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('0g')))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('e + 123')))
        # No number
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('e')))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('E')))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('e+')))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('E+')))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('e-')))
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list('E-')))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteralExponentPart(list(' 0123')))

    def testLexFconSign(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - sign."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._sliceFloatingLiteralSign(list('-')))
        self.assertEqual(1, myObj._sliceFloatingLiteralSign(list('+')))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteralSign(list('0123')))
        self.assertEqual(0, myObj._sliceFloatingLiteralSign(list('g')))
        self.assertEqual(0, myObj._sliceFloatingLiteralSign(list('0g')))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteralSign(list(' 0123')))

    def testLexFconDigitSequence(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - digit-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._sliceFloatingLiteralDigitSequence(list('0')))
        self.assertEqual(2, myObj._sliceFloatingLiteralDigitSequence(list('12')))
        self.assertEqual(3, myObj._sliceFloatingLiteralDigitSequence(list('123')))
        self.assertEqual(3, myObj._sliceFloatingLiteralDigitSequence(list('123a')))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteralDigitSequence(list('abc')))
        self.assertEqual(0, myObj._sliceFloatingLiteralDigitSequence(list('a12')))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteralDigitSequence(list(' 0123')))


    def testLexFconFloatingSuffix(self):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - floating-suffix."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(1, myObj._sliceFloatingLiteralFloatingSuffix(list('f')))
        self.assertEqual(1, myObj._sliceFloatingLiteralFloatingSuffix(list('l')))
        self.assertEqual(1, myObj._sliceFloatingLiteralFloatingSuffix(list('F')))
        self.assertEqual(1, myObj._sliceFloatingLiteralFloatingSuffix(list('L')))
        self.assertEqual(1, myObj._sliceFloatingLiteralFloatingSuffix(list('fg')))
        # Failures
        # Numbers, other letters
        self.assertEqual(0, myObj._sliceFloatingLiteralFloatingSuffix(list('0123')))
        self.assertEqual(0, myObj._sliceFloatingLiteralFloatingSuffix(list('g')))
        self.assertEqual(0, myObj._sliceFloatingLiteralFloatingSuffix(list('0g')))
        # Space prefix
        self.assertEqual(0, myObj._sliceFloatingLiteralFloatingSuffix(list(' 0123')))

class TestExpressionLexString(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexString(self):
        """ISO/IEC 14882:1998(E) 2.13.4 String literals [lex.string]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(2, myObj._sliceStringLiteral(list('""')))
        self.assertEqual(3, myObj._sliceStringLiteral(list('L""')))
        self.assertEqual(5, myObj._sliceStringLiteral(list('"abc"')))
        self.assertEqual(6, myObj._sliceStringLiteral(list('L"abc"')))
        # Failures
        # Single "
        self.assertEqual(0, myObj._sliceStringLiteral(list('"')))
        self.assertEqual(0, myObj._sliceStringLiteral(list('"as')))
        # Space prefix
        self.assertEqual(0, myObj._sliceStringLiteral(list(' 0123')))

    def testLexStringNull(self):
        """ISO/IEC 14882:1998(E) 2.13.4 String literals [lex.string] with NULL character."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(4, myObj._sliceStringLiteral(list(r'"\0"')))
        self.assertEqual(4, myObj._sliceStringLiteral(list('"\\0"')))
        self.assertEqual(10, myObj._sliceStringLiteral(list(r'"abc\0xyz"')))
        self.assertEqual(10, myObj._sliceStringLiteral(list('"abc\\0xyz"')))

class TestExpressionLexBool(TestPpTokeniserBase):
    def setUp(self):
        pass

    def testLexBool(self):
        """ISO/IEC 14882:1998(E) 2.13.5 Boolean literals [lex.bool]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(4, myObj._sliceBoolLiteral(list('true')))
        self.assertEqual(5, myObj._sliceBoolLiteral(list('false')))
        self.assertEqual(4, myObj._sliceBoolLiteral(list('truesomeething')))
        self.assertEqual(5, myObj._sliceBoolLiteral(list('falseotherthing')))
        # Failures
        # Partial
        self.assertEqual(0, myObj._sliceBoolLiteral(list('tru')))
        self.assertEqual(0, myObj._sliceBoolLiteral(list('f')))
        # Space prefix
        self.assertEqual(0, myObj._sliceBoolLiteral(list(' 0123')))

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
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(''))
        # Successes
        self.assertEqual([], myObj.lexPhases_0())

    def testPhase_0_EmptyWithEof(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, single new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('\n'))
        # Successes
        self.assertEqual(['\n',], myObj.lexPhases_0())

    def testPhase_0_OneString(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, one line, no new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('asd'))
        # Successes
        self.assertEqual(['asd',], myObj.lexPhases_0())

    def testPhase_0_OneLine(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, one line, has new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('asd\n'))
        # Successes
        self.assertEqual(['asd\n',], myObj.lexPhases_0())

    def testPhase_0_MultiLine_00(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, multi-line, has new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('asd\n\n'))
        # Successes
        self.assertEqual(['asd\n', '\n'], myObj.lexPhases_0())

    def testPhase_0_MultiLine_01(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, multi-line, no ending new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('abc\ndef'))
        # Successes
        self.assertEqual(['abc\n', 'def'], myObj.lexPhases_0())

    def testPhase_0_MultiLine_02(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 0, multi-line, has ending new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('abc\ndef\n'))
        self.assertEqual(['abc\n', 'def\n'], myObj.lexPhases_0())

class TestLexPhases_1(TestPpTokeniserBase):
    """Tests the phase zero and phase one."""
    def testPhase_1_00_ConvertCharSet(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, lex.charset expansion."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(''))
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
        self.assertEqual(['e'], myL)
        myL = ['\uFFFF',]
        myObj._convertToLexCharset(myL)
        self.assertEqual(['\\uFFFF'], myL)
        myL = ['\uffff',]
        myObj._convertToLexCharset(myL)
        self.assertEqual(['\\uFFFF'], myL)

    def testPhase_1_01_ConvertCharSet(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, lex.charset expansion, misc."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(''))
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
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(''))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual([], myPh_0)
        myStrTokS = [Str for Str in myObj.genLexPhase1(myPh_0)]
        self.assertEqual([], myStrTokS)

    def testPhase_1_EmptyWithEof(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, single new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('\n'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['\n'], myPh_0)
        myStrTokS = [Str.str for Str in myObj.genLexPhase1(myPh_0)]
        self.assertEqual(['\n'], myStrTokS)

    def testPhase_1_OneString(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, one line, no new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('asd'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['asd',], myPh_0)
        myStrTokS = [Str.str for Str in myObj.genLexPhase1(myPh_0)]
        self.assertEqual(['a', 's', 'd',], myStrTokS)

    def testPhase_1_OneLine(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, one line, has new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('asd\n'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['asd\n',], myPh_0)
        myStrTokS = [Str.str for Str in myObj.genLexPhase1(myPh_0)]
        self.assertEqual(['a', 's', 'd', '\n'], myStrTokS)

    def testPhase_1_MultiLine_00(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, multi-line, has new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('asd\n\n'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['asd\n', '\n'], myPh_0)
        myStrTokS = [Str.str for Str in myObj.genLexPhase1(myPh_0)]
        self.assertEqual(['a', 's', 'd', '\n', '\n'], myStrTokS)

    def testPhase_1_MultiLine_01(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, multi-line, no ending new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('abc\ndef'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['abc\n', 'def'], myPh_0)
        myStrTokS = [Str.str for Str in myObj.genLexPhase1(myPh_0)]
        self.assertEqual(['a', 'b', 'c', '\n', 'd', 'e', 'f',], myStrTokS)

    def testPhase_1_MultiLine_02(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, multi-line, has ending new-line."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('abc\ndef\n'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['abc\n', 'def\n'], myPh_0)
        myStrTokS = [Str.str for Str in myObj.genLexPhase1(myPh_0)]
        self.assertEqual(['a', 'b', 'c', '\n', 'd', 'e', 'f', '\n'], myStrTokS)

    def testPhase_1_Trigraph_Single_00(self):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase 1, trigraph, single "??="."""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('??=\n'))
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['??=\n',], myPh_0)
        myStrTokS = [s for s in myObj.genLexPhase1(myPh_0)]
        self.assertEqual(
            [
                PpTokeniser.StrTypRep('??=', 'trigraph', '#'), 
                PpTokeniser.StrTypRep('\n', PpTokeniser.STR_TYP_REP_UNTYPED, None), 
            ],
            myStrTokS
        )
        self.assertEqual(['??=', '\n'],         [s.str for s in myStrTokS])
        self.assertEqual(['trigraph', None],    [s.typ for s in myStrTokS])
        self.assertEqual(['#', None],           [s.rep for s in myStrTokS])
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
            myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO('%s\n' % t))
            myPh_0 = myObj.lexPhases_0()
            self.assertEqual(['%s\n' % t,], myPh_0)
            myStrTokS = [s for s in myObj.genLexPhase1(myPh_0)]
            self.assertEqual(
                [
                    PpTokeniser.StrTypRep(t, 'trigraph', r), 
                    PpTokeniser.StrTypRep('\n', PpTokeniser.STR_TYP_REP_UNTYPED, None), 
                ],
                myStrTokS
            )
            self.assertEqual([t, '\n'],             [s.str for s in myStrTokS])
            self.assertEqual(['trigraph', None],    [s.typ for s in myStrTokS])
            self.assertEqual([r, None],             [s.rep for s in myStrTokS])
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
            theFileObj=io.StringIO('??=??(\n')
            )
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['??=??(\n',], myPh_0)
        myStrTokS = [s for s in myObj.genLexPhase1(myPh_0)]
        self.assertEqual(
            [
                PpTokeniser.StrTypRep('??=', 'trigraph', '#'), 
                PpTokeniser.StrTypRep('??(', 'trigraph', '['), 
                PpTokeniser.StrTypRep('\n', PpTokeniser.STR_TYP_REP_UNTYPED, None), 
            ],
            myStrTokS
        )
        self.assertEqual(['??=', '??(', '\n'],              [s.str for s in myStrTokS])
        self.assertEqual(['trigraph', 'trigraph', None],    [s.typ for s in myStrTokS])
        self.assertEqual(['#', '[', None],                  [s.rep for s in myStrTokS])
        # Test file locator information
        # NOTE: A this is a pre-pass of a multi-pass system we need
        # to access the logicalPhysicalLineMap
        #print
        #print str(myObj.fileLocator.logicalPhysicalLineMap)
        #pprint.pprint(myObj.fileLocator.logicalPhysicalLineMap._ir)
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
                '??=??(??<??/??)??>??\'??!??-\n'
                )
            )
        myPh_0 = myObj.lexPhases_0()
        self.assertEqual(['??=??(??<??/??)??>??\'??!??-\n',], myPh_0)
        myStrTokS = [s for s in myObj.genLexPhase1(myPh_0)]
        #print
        #pprint.pprint(myStrTokS)
        self.assertEqual(
            [
                PpTokeniser.StrTypRep(str='??=', typ='trigraph', rep='#'),
                PpTokeniser.StrTypRep(str='??(', typ='trigraph', rep='['),
                PpTokeniser.StrTypRep(str='??<', typ='trigraph', rep='{'),
                PpTokeniser.StrTypRep(str='??/', typ='trigraph', rep='\\'),
                PpTokeniser.StrTypRep(str='??)', typ='trigraph', rep=']'),
                PpTokeniser.StrTypRep(str='??>', typ='trigraph', rep='}'),
                PpTokeniser.StrTypRep(str="??'", typ='trigraph', rep='^'),
                PpTokeniser.StrTypRep(str='??!', typ='trigraph', rep='|'),
                PpTokeniser.StrTypRep(str='??-', typ='trigraph', rep='~'),
                PpTokeniser.StrTypRep(str='\n', typ=None, rep=None),
            ],
            myStrTokS
        )
        # Test file locator information
        # NOTE: A this is a pre-pass of a multi-pass system we need
        # to access the logicalPhysicalLineMap
        #print
        #print str(myObj.fileLocator.logicalPhysicalLineMap)
        #pprint.pprint(myObj.fileLocator.logicalPhysicalLineMap._ir)
        for i in range(0, 9*3+1, 3):
            #print i
            self.assertEqual(
                (FileLocation.START_LINE, i+FileLocation.START_COLUMN),
                myObj.fileLocator.logicalPhysicalLineMap.pLineCol(
                    FileLocation.START_LINE,
                    (i/3)+FileLocation.START_COLUMN,
                    )
                )

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
        self.assertEqual(1, myObj._sliceLexPptoken(list('1')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(2, myObj._sliceLexPptoken(list('.1')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(5, myObj._sliceLexPptoken(list('1.234')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(7, myObj._sliceLexPptoken(list('1.234e+')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(7, myObj._sliceLexPptoken(list('1.234E+')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(7, myObj._sliceLexPptoken(list('1.234e-')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(7, myObj._sliceLexPptoken(list('1.234E-')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(9, myObj._sliceLexPptoken(list('1.234E-89')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(12, myObj._sliceLexPptoken(list('1.234E-89e+4')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        # Failures

    def testLexName(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.name]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(4, myObj._sliceLexPptoken(list('ab_9')))
        self.assertEqual(myObj.cppTokType, 'identifier')
        self.assertEqual(10, myObj._sliceLexPptoken(list('ab_9\\u0123')))
        self.assertEqual(myObj.cppTokType, 'identifier')
        self.assertEqual(10, myObj._sliceLexPptoken(list('ab_\\u01239')))
        self.assertEqual(myObj.cppTokType, 'identifier')
        # Failures
        self.assertEqual(3, myObj._sliceLexPptoken(list('9ab')))
        # Actually this resolves to a lex.ppnumber
        self.assertNotEqual(myObj.cppTokType, 'identifier')
        self.assertEqual(0, myObj._sliceLexPptoken(list(' ab')))
        self.assertEqual(myObj.cppTokType, None)

    def testLexCcon(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.ccon]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(3, myObj._sliceLexPptoken(list("'a'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(4, myObj._sliceLexPptoken(list("L'a'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(4, myObj._sliceLexPptoken(list("'\\b'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(5, myObj._sliceLexPptoken(list("L'\\b'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        # Failures
        # Space prefix
        self.assertEqual(0, myObj._sliceLexPptoken(list(' 0123')))
        self.assertEqual(myObj.cppTokType, None)

    def testLexCconEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.ccon] - escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        # Simple
        self.assertEqual(4, myObj._sliceLexPptoken(list("'\\\\'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        # Octal
        self.assertEqual(6, myObj._sliceLexPptoken(list("'\\000'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        # Hex
        self.assertEqual(5, myObj._sliceLexPptoken(list("'\\x0'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        # Failures
        self.assertEqual(1, myObj._sliceLexPptoken(list("'\\z'")))
        self.assertNotEqual(myObj.cppTokType, 'character-literal')

    def testLexCconSimpleEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.ccon] - simple-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(4, myObj._sliceLexPptoken(list("'\\\\'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        # Failures
        self.assertEqual(1, myObj._sliceLexPptoken(list("'\\z'")))
        self.assertNotEqual(myObj.cppTokType, 'character-literal')

    def testLexCconOctalEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.ccon] - octal-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(4, myObj._sliceLexPptoken(list("'\\0'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(5, myObj._sliceLexPptoken(list("'\\00'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(6, myObj._sliceLexPptoken(list("'\\000'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(6, myObj._sliceLexPptoken(list("'\\012'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(6, myObj._sliceLexPptoken(list("'\\345'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(5, myObj._sliceLexPptoken(list("'\\67'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(7, myObj._sliceLexPptoken(list("'\\0000'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(8, myObj._sliceLexPptoken(list("'\\00000'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(5, myObj._sliceLexPptoken(list("'\\09'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')

    def testLexCconHexadecimalEscapeSequence(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.ccon] - hexadecimal-escape-sequence."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(5, myObj._sliceLexPptoken(list("'\\x0'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')
        self.assertEqual(26, myObj._sliceLexPptoken(list("'\\x0123456789abcdefABCDEF'")))
        self.assertEqual(myObj.cppTokType, 'character-literal')

    def testLexString(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.string]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(2, myObj._sliceLexPptoken(list('""')))
        self.assertEqual(myObj.cppTokType, 'string-literal')
        self.assertEqual(3, myObj._sliceLexPptoken(list('L""')))
        self.assertEqual(myObj.cppTokType, 'string-literal')
        self.assertEqual(5, myObj._sliceLexPptoken(list('"abc"')))
        self.assertEqual(myObj.cppTokType, 'string-literal')
        self.assertEqual(6, myObj._sliceLexPptoken(list('L"abc"')))
        self.assertEqual(myObj.cppTokType, 'string-literal')
        # Failures
        # Space prefix
        myObj._sliceLexPptoken(list(' 0123'))
        self.assertEqual(0, myObj._sliceLexPptoken(list(' 0123')))
        self.assertEqual(myObj.cppTokType, None)

    def testLexOperators(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - [lex.operators]."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        self.assertEqual(2, myObj._sliceLexPptoken(list('<<')))
        self.assertEqual(myObj.cppTokType, 'preprocessing-op-or-punc')
        self.assertEqual(3, myObj._sliceLexPptoken(list('<<=')))
        self.assertEqual(myObj.cppTokType, 'preprocessing-op-or-punc')
        # Failures
        self.assertEqual(3, myObj._sliceLexPptoken(list('9ab')))
        self.assertEqual(myObj.cppTokType, 'pp-number')
        self.assertEqual(0, myObj._sliceLexPptoken(list(' ab')))
        self.assertEqual(myObj.cppTokType, None)

    def testLexNonWhitespace(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - single character."""
        myObj = PpTokeniser.PpTokeniser()
        # Successes
        # These should be found by _sliceNonWhitespaceSingleChar()
        self.assertEqual(1, myObj._sliceLexPptoken(list('"')))
        self.assertEqual(myObj.cppTokType, 'non-whitespace')
        self.assertEqual(1, myObj._sliceLexPptoken(list('\'')))
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
        #
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
        self.assertRaises(StopIteration, myGen.__next__)

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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
        #
        myGen = myObj.genLexPptokenAndSeqWs('//')
        self.assertRaises(
            CppDiagnostic.ExceptionCppDiagnosticPartialTokenStream,
            myGen.__next__
            )
        #myToks = [t for t in myGen]
        ##print '\n', myToks
        #eToks = [
        #        PpToken.PpToken(' ',           'whitespace'),
        #        ]
        #self._printDiff(myToks, eToks)
        #self.assertEqual(myToks, eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)

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
        myStr = '#include "spam.h"\n'
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myObj.initLexPhase12()
        self.assertEqual(myObj._transPhaseTwo, myStr)

    def testNextGenertor_01(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken] - token and token type generation."""
        myStr = '#include "spam.h"\n'
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = next(myObj)
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
        self.assertRaises(StopIteration, myTokTypeGen.__next__)

class TestGenerateLexPpTokensUnget(TestPpTokeniserBase):
    """Generates a preprocessing token stream using unget(0 to push token back on to the stream."""

    def testNextGenertorSend_00(self):
        """Token generation with send()."""
        myStr = '#include "spam.h"\n'
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = next(myObj)
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
        self.assertRaises(StopIteration, myTokTypeGen.__next__)

    def testNextGenertorSend_01(self):
        """Token generation with send(), simulates "F F (123)" ignoring first F and pushing back the second F."""
        myStr = 'F F (123)\n'
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = next(myObj)
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
        self.assertRaises(StopIteration, myTokTypeGen.__next__)

    def testNextGenertorSend_03(self):
        """Token generation with send(), simulates "F(123) F abc" pushing back "abc" when no LPAREN found for second F."""
        myStr = 'F(123) F abc\n'
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = next(myObj)
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
        self.assertRaises(StopIteration, myTokTypeGen.__next__)

class TestHeaderReconstuction(TestPpTokeniserBase):
    """Tests generating a token stream then re-interpreting it as a header-name."""
    def testQcharSeq_00(self):
        """TestHeaderReconstuction "q-char-sequence" [0]."""
        myObj = PpTokeniser.PpTokeniser()
        # q-char sequences
        myGen = myObj.genLexPptokenAndSeqWs('#include "foo"\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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

    def testQcharSeq_Fail_00(self):
        """TestHeaderReconstuction "q-char-sequence" fails [0]."""
        myObj = PpTokeniser.PpTokeniser()
        # Failures, well these do not correspond to a correct #include directive
        # as the sequence turns out wrong
        myGen = myObj.genLexPptokenAndSeqWs('#include "fo\no"\n')
        myToks = [t for t in myGen]
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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
        self.assertRaises(StopIteration, myGen.__next__)
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

class TestMisc(TestPpTokeniserBase):#TestGenerateLexPpTokens):
    def test_00(self):
        """TestMisc.test_00(): '@'"""
        myObj = PpTokeniser.PpTokeniser()
        # q-char sequences
        myGen = myObj.genLexPptokenAndSeqWs('@\n')
        myToks = [t for t in myGen]
        eToks = [
                PpToken.PpToken('@',           'non-whitespace'),
                PpToken.PpToken('\n',          'whitespace'),
                ]
        self._printDiff(myToks, eToks)
        self.assertEqual(myToks, eToks)
        # Check that all tokens have been consumed
        self.assertRaises(StopIteration, myGen.__next__)

class TestPpTokeniserFileLocator(TestPpTokeniserBase):
    def test_00(self):
        """TestPpTokeniserFileLocator.test_00()"""
        myStr = """#include "spam.h"
/*
A function definition
*/
#define F(x) f(x)

"""
        myObj = PpTokeniser.PpTokeniser(theFileObj=io.StringIO(myStr))
        myTokTypeGen = next(myObj)
        actToks = []
        for t in myTokTypeGen:
            #print '%2d %2d %s' % (t.lineNum, t.colNum, t)
            actToks.append((t.lineNum, t.colNum, t.t))
        #myToks = [t for t in myTokTypeGen]
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
        self.assertRaises(StopIteration, myTokTypeGen.__next__)
        self.assertEqual(actToks, eToks)
        #print
        #print myObj.fileLocator

class NullClass(TestPpTokeniserBase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
#===============================================================================
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestWordsFoundIn))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexCharset))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserTrigraphs))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserDigraphs))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexComment))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexHeader))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexPpnumber))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexName))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexKey))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexOperators))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexLiteral))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexIcon))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexCcon))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexFcon))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexString))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpressionLexBool))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLexPptoken))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGenerateLexPpTokens))
#===============================================================================
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLexPhases_0))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLexPhases_1))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLexPhases_2))
#===============================================================================
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGenerateLexPpTokensUnget))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHeaderReconstuction))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMisc))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserFileLocator))
#===============================================================================
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
