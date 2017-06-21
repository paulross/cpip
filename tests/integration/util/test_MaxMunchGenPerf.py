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
import string
import io

from cpip import ExceptionCpip
from cpip.util import MaxMunchGen

class ExceptionTestMaximalMunchComment(ExceptionCpip):
    pass
#######################################
# Section: Unit tests
########################################

class TestMaximalMunchSimulPpTokeniserBase(unittest.TestCase):
    """Simulates Trigraph replacement."""
    SOURCE_CHARACTER_SET = set("""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_{}[]#()<>%:;.?*+-/^&|~!=,\\"'\t\v\f\n """)
    LEX_WHITESPACE = set('\t\v\f\n ')
    UCN_ORDINALS =  set((0x24, 0x40, 0x60))
    # NOTE: Constant prefix of '??' is absent from keys.
    TRIGRAPH_TABLE = {
        '='       : '#',
        '('       :  '[',
        '<'       : '{',
        '/'       : '\\',
        ')'       : ']',
        '>'       : '}',
        "'"       : '^',
        '!'       : '|',
        '-'       : '~',
    }
    TRIGRAPH_SIZE = 3
    def __init__(self, *args):
        super(TestMaximalMunchSimulPpTokeniserBase, self).__init__(*args)
        self._file = None
        self._fileOpen = False
        self._cntrAddNewLinesAfterCont = 0
        
    def lineContinuation(self, theGen):
        i = 0
        r = None
        try:
            aChar = next(theGen)
            if aChar == '\\' \
            and next(theGen) == '\n':
                r = ''
                i = 2
                self._cntrAddNewLinesAfterCont += 1
            elif aChar == '\n' and self._cntrAddNewLinesAfterCont > 0:
                r = '\n' * (1+self._cntrAddNewLinesAfterCont)
                i = 1
                self._cntrAddNewLinesAfterCont = 0
        except StopIteration:
            pass
        return i, 'lineContinuation', r
    
    def universalCharacterName(self, theGen):
        i = 0
        r = None
        try:
            myChr = next(theGen)
            if myChr not in self.SOURCE_CHARACTER_SET:
                i = 1
                myOrd = ord(myChr)
                # Expand to a universal-character-name
                if myOrd <= 0xFFFF:
                    if myOrd not in self.UCN_ORDINALS:
                        # This is not 0024 ($), 0040 (@), or 0060 (back tick)
                        r = '\\u%04X' % myOrd
                else:
                    #self._fileLocator.substString(1, 8)
                    r = '\\U%08X' % myOrd
        except StopIteration:
            pass
        return i, 'ucn', r
    
    def trigraph(self, theGen):
        i = 0
        r = None
        try:
            if next(theGen) == '?' \
            and next(theGen) == '?':
                try:
                    r = self.TRIGRAPH_TABLE[next(theGen)]
                    i = self.TRIGRAPH_SIZE
                except KeyError:
                    pass
        except StopIteration:
            pass
        #print 'TRACE:', i, 'trigraph', r
        return i, 'trigraph', r
    
    def whitespace(self, theGen):
        i = 0
        r = None
        try:
#===============================================================================
#            while 1:
#                aChr = theGen.next()
#                #print aChr
#                if aChr not in self.LEX_WHITESPACE:
#                    break
#                i += 1
#===============================================================================
            while next(theGen) in self.LEX_WHITESPACE:
                i += 1
        except StopIteration:
            pass
        return i, 'whitespace', r
    
    def singleNonWhitespace(self, theGen):
        i = 0
        r = None
        try:
#===============================================================================
#            while 1:
#                aChr = theGen.next()
#                #print aChr
#                if aChr in self.LEX_WHITESPACE:
#                    break
#                i += 1
#===============================================================================
            if next(theGen) not in self.LEX_WHITESPACE:
                i = 1
        except StopIteration:
            pass
        return i, 'whitespace', r
    
    def cComment(self, theGen):
        i = 0
        r = None
        try:
            aChar = next(theGen)
            if aChar == '/' \
            and next(theGen) == '*':
                r = ' '
                i = 2
                while 1:
                    if next(theGen) == '*':
                        i += 1
                        if next(theGen) == '/':
                            i += 1
                            break
                    else:
                        i += 1                        
        except StopIteration:
            # Raise here if i > 0 as unclosed comment
            if i > 0:
                raise ExceptionTestMaximalMunchComment()
            pass
        return i, 'cComment', r
    
    def cxxComment(self, theGen):
        i = 0
        r = None
        try:
            aChar = next(theGen)
            if aChar == '/' \
            and next(theGen) == '/':
                r = ' '
                i = 2
                while 1:
                    if next(theGen) == '\n':
                        #i += 1
                        break
                    i += 1                        
        except StopIteration:
            # Raise here if i > 0 as unclosed comment
            if i > 0:
                raise ExceptionTestMaximalMunchComment()
        return i, 'cxxComment', r

    def _resetStart(self):
        self._timStart = time.clock()
        
    def setUp(self):
        self._resetStart()
        self._size = 0
            
    def testNull(self):
        """TestMaximalMunchTrigraph: Test setUp() and tearDown()               ."""
        pass

    def tearDown(self):
        myTime = time.clock() - self._timStart
        sys.stderr.write('Bytes: %8d, time: %8.3f, rate: %8.1f kb/s ... ' \
                         % (self._size, myTime, (self._size / (myTime*1024))))
    
    def checkIOK(self):
        if self._fileOpen:
            raise Exception('File is already open.') 
        if self._file is None:
            raise Exception('No File to open.') 
 
    def close(self):
        """Resets the file."""
        self._file.close()
        self._fileOpen = False
    
    def genPhase0(self):
        """A psuedo-phase, this rewinds the input and reads it character by
        character."""
        #print 'genPhase0'
        self.checkIOK()
        try:
            self._file.seek(0)
            self._fileOpen = True
            #self._fileLocator.startNewPhase()
            for c in self._file.read():
                #logging.debug('genPhase0: %s' % c)
                yield c
        finally:
            self.close()
 
    def genPhase1(self):
        """Phase 1. Physical source file multibyte characters are mapped, in an
        implementation defined manner, to the source character set (introducing
        new-line characters for end-of-line indicators) if necessary. Trigraph
        sequences are replaced by corresponding single-character internal
        representations."""
        #print 'genPhase1'
        self.checkIOK()
        myBg = MaxMunchGen.MaxMunchGen(
                    self.genPhase0(),
                    [
                        self.universalCharacterName,
                        self.trigraph,
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=True,
                    )
        #self._fileLocator.startNewPhase()
        for aVal in myBg.gen():
            #logging.debug('genPhase1: %s' % str(aVal))
            yield ''.join(aVal[0])
 
    def genPhase2(self):
        """Phase 2. Each instance of a backslash character (\) immediately followed by
        a new-line character is deleted, splicing physical source lines to form
        logical source lines. Only the last backslash on any physical source line
        shall be eligible for being part of such a splice. A source file that is
        not empty shall end in a new-line character, which shall not be immediately
        preceded by a backslash character before any such splicing takes place."""
        self.checkIOK()
        myBg = MaxMunchGen.MaxMunchGen(
                    self.genPhase1(),
                    [
                        self.lineContinuation,
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=True,
                    )
        #self._fileLocator.startNewPhase()
        for aVal in myBg.gen():
            #logging.debug('genPhase2: %s' % str(aVal))
            yield ''.join(aVal[0])
 
    def genPhase3(self):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken].
        Phase 3. The source file is decomposed into preprocessing tokens6) and
        sequences of white-space characters (including comments). A source file
        shall not end in a partial preprocessing token or in a partial comment.
        Each comment is replaced by one space character. New-line characters are
        retained. Whether each nonempty sequence of white-space characters other
        than new-line is retained or replaced by one space character is
        implementation-defined.
        NOTE: Whitespace sequences are not merged so "  /**/ " will generate
        three tokens each of PpToken.PpToken(' ', 'whitespace').
        So this yields the tokens from translation phase 3 if supplied with
        the results of translation phase 2.
        NOTE: This does not generate 'header-name' tokens as these are context
        dependent i.e. they are only valid in the context of a #include
        directive. [ISO/IEC 9899:1999 (E) 6.4.7 Header names Para 3 says that:
        "A header name preprocessing token is recognized only within a #include
        preprocessing directive."]. Instead any token conumer can avail
        themselves of TODO ???() that can interpret a token stream as a header-name
        if possible.
        TODO: Update FileLocator correctly (?).
        """
        self.checkIOK()
        myBg = MaxMunchGen.MaxMunchGen(
                    self.genPhase2(),
                    [
                        # Whitespace
                        self.whitespace,
                        # Comments
                        self.cComment,
                        self.cxxComment,
#===============================================================================
#                        # We don't do header-name, see note above.
#                        # identifier
#                        self._sliceLexName,
#                        # pp-number
#                        self._sliceLexPpnumber,
#                        # character-literal
#                        self._sliceCharacterLiteral,
#                        # string-literal
#                        self._sliceStringLiteral,
#                        # preprocessing-op-or-punc
#                        self._sliceLexOperators,
#                        # "each non-white-space character that cannot be one of the above"
#                        self._sliceNonWhitespaceSingleChar,
#===============================================================================
                        self.singleNonWhitespace,
                    ],
                    isExclusive=False,
                    )
        #self._fileLocator.startNewPhase()
        for aVal in myBg.gen():
            #logging.debug('genPhase3: %s' % str(aVal))
            yield ''.join(aVal[0])
    
    def genPhase_(self):
        """Dummy phase to check MaxMunch.anyToken."""
        self.checkIOK()
        myBg = MaxMunchGen.MaxMunchGen(
                    self.genPhase0(),
                    [
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=True,
                    )
        #self._fileLocator.startNewPhase()
        for aVal in myBg.gen():
            #logging.debug('genPhase_: %s' % str(aVal))
            yield ''.join(aVal[0])
 
class TestMaximalMunchSimulPpTokeniser_00(TestMaximalMunchSimulPpTokeniserBase):
    
    def test_00(self):
        """TestMaximalMunchSimulPpTokeniser_00: Trigraph replacemnt, lines:    1"""
        myPStr = u'??=define arraycheck(a,b) a??(b??) ??!??! b??(a??)'
        myLStr = u'#define arraycheck(a,b) a[b] || b[a]'
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        myResult = [aVal for aVal in self.genPhase3()]
        #myResultStr = ''.join([''.join(v[0]) for v in myResult])
        ##print
        ##print myResultStr
        #self.assertEquals(myResultStr, myLStr)

    def test_01(self):
        """TestMaximalMunchSimulPpTokeniser_00: Trigraph replacemnt, lines:  128"""
        myPStr = u'??=define arraycheck(a,b) a??(b??) ??!??! b??(a??)\n' * 128
        myLStr = u'#define arraycheck(a,b) a[b] || b[a]\n' * 128
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        myResult = [aVal for aVal in self.genPhase3()]
        #myResultStr = ''.join([''.join(v[0]) for v in myResult])
        ##print
        ##print myResultStr
        #self.assertEquals(myResultStr, myLStr)

    def test_02(self):
        """TestMaximalMunchSimulPpTokeniser_00: Trigraph replacemnt, lines: 1024"""
        myPStr = u'??=define arraycheck(a,b) a??(b??) ??!??! b??(a??)\n' * 1024
        myLStr = u'#define arraycheck(a,b) a[b] || b[a]\n' * 1024
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        myResult = [aVal for aVal in self.genPhase3()]
        #myResultStr = ''.join([''.join(v[0]) for v in myResult])
        ##print
        ##print myResultStr
        #self.assertEquals(myResultStr, myLStr)

    def test_10(self):
        """TestMaximalMunchSimulPpTokeniser_00:          whitespace, lines:    1"""
        myPStr = u' ' * 80 + '\n'
        myLStr = myPStr
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        myResult = [aVal for aVal in self.genPhase3()]
        #myResultStr = ''.join([''.join(v[0]) for v in myResult])
        ##print
        ##print myResultStr
        #self.assertEquals(myResultStr, myLStr)

    def test_11(self):
        """TestMaximalMunchSimulPpTokeniser_00:          whitespace, lines:  128"""
        myPStr = (u' ' * 80 + '\n') * 128
        #print myPStr
        myLStr = myPStr
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        myResult = [aVal for aVal in self.genPhase3()]
        #myResultStr = ''.join([''.join(v[0]) for v in myResult])
        ##print
        ##print myResultStr
        #self.assertEquals(myResultStr, myLStr)

    def test_12(self):
        """TestMaximalMunchSimulPpTokeniser_00:          whitespace, lines: 1024"""
        myPStr = (u' ' * 80 + '\n') * 1024
        myLStr = myPStr
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        myResult = [aVal for aVal in self.genPhase3()]
        #myResultStr = ''.join([''.join(v[0]) for v in myResult])
        ##print
        ##print myResultStr
        #self.assertEquals(myResultStr, myLStr)

class TestMaximalMunchSimulPpTokeniser_01(TestMaximalMunchSimulPpTokeniserBase):
    def test_00(self):
        """TestMaximalMunchSimulPpTokeniser_00:     ph.: whitespace, lines: 1024"""
        myPStr = (u' ' * 80 + '\n') * 1024
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        self._resetStart()
        for c in self._file.read():
            pass

    def test_01(self):
        """TestMaximalMunchSimulPpTokeniser_00:     ph0: whitespace, lines: 1024"""
        myPStr = (u' ' * 80 + '\n') * 1024
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        self._resetStart()
        for aVal in self.genPhase0():
            pass

    def test_02(self):
        """TestMaximalMunchSimulPpTokeniser_00:     ph1: whitespace, lines: 1024"""
        myPStr = (u' ' * 80 + '\n') * 1024
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        self._resetStart()
        for aVal in self.genPhase1():
            pass

    def test_03(self):
        """TestMaximalMunchSimulPpTokeniser_00:     ph2: whitespace, lines: 1024"""
        myPStr = (u' ' * 80 + '\n') * 1024
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        self._resetStart()
        for aVal in self.genPhase2():
            pass

    def test_04(self):
        """TestMaximalMunchSimulPpTokeniser_00:     ph3: whitespace, lines: 1024"""
        myPStr = (u' ' * 80 + '\n') * 1024
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        self._resetStart()
        for aVal in self.genPhase3():
            pass

    def test_05(self):
        """TestMaximalMunchSimulPpTokeniser_00:     ph_: whitespace, lines: 1024"""
        myPStr = (u' ' * 80 + '\n') * 1024
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        self._resetStart()
        for aVal in self.genPhase_():
            pass

class TestMaximalMunchSimulPpTokeniser_Profile(TestMaximalMunchSimulPpTokeniserBase):
#    def test_04(self):
#        """TestMaximalMunchSimulPpTokeniser_00:     ph3: whitespace, lines: 0256"""
#        myPStr = (' a' * 40 + '\n') * 256
#        self._file = StringIO.StringIO(myPStr)
#        self._size = len(myPStr)
#        self._resetStart()
#        for aVal in self.genPhase3():
#            pass

    def test_00(self):
        """TestMaximalMunchSimulPpTokeniser_Profile.test_00: MaxMunch.anyToken(), lines: 1024"""
        myPStr = (u' ' * 80 + '\n') * 1024
        self._file = io.StringIO(myPStr)
        self._size = len(myPStr)
        self._resetStart()
        for aVal in self.genPhase_():
            pass

class TestMaximalMunchProfileNumbers(unittest.TestCase):
    """Max munches through numbers."""
    def __init__(self, *args):
        super(TestMaximalMunchProfileNumbers, self).__init__(*args)
        self._oct = set(string.octdigits)
        self._dec = set(string.digits)
        self._hex = set(string.hexdigits)

    def _gen(self, theFile):
        for c in theFile.read():
            #logging.debug('genPhase0: %s' % c)
            yield c
            
    def __munchSet(self, theGen, theSet, theType):
        i = 0
        try:
            while 1:
                c = next(theGen)
                if c == ' ':
                    break
                elif c in theSet:
                    i += 1
                else:
                    i = 0
                    break
        except StopIteration:
            pass
        return i, theType, None

    def _munchOct(self, theGen):
        return self.__munchSet(theGen, self._oct, 'oct')

    def _munchDec(self, theGen):
        return self.__munchSet(theGen, self._dec, 'dec')

    def _munchHex(self, theGen):
        return self.__munchSet(theGen, self._hex, 'hex')

    def test_00(self):
        """TestMaximalMunchProfileNumbers.test_00: dec, oct and hex digit runs * 1024"""
        myLine = u'%s %s %s\n' % (string.octdigits, string.digits, string.hexdigits)
        myPStr = myLine * 4 * 1024
        myFile = io.StringIO(myPStr)

        myBg = MaxMunchGen.MaxMunchGen(
                    self._gen(myFile),
                    [
                        self._munchOct,
                        self._munchDec,
                        self._munchHex,
                        MaxMunchGen.anyToken,
                    ],
                    isExclusive=True,
                    )
        for aVal in myBg.gen():
            pass

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    """Execute unit tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMaximalMunchSimulPpTokeniser_00))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMaximalMunchSimulPpTokeniser_01))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMaximalMunchSimulPpTokeniser_Profile))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMaximalMunchProfileNumbers))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

#################
# End: Unit tests
#################

def usage():
    """Send the help to stdout."""
    print("""TestMaxMunchGen.py - A module that tests PpToken module.
Usage:
python TestMaxMunchGen.py [-lh --help]

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
    print('TestMaxMunchGen.py script version "%s", dated %s' % (__version__, __date__))
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
