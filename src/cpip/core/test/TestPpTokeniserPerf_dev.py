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

import time
import logging
import sys
import os
import unittest
try:
    import io as StringIO
except ImportError:
    import io
import subprocess

from cpip.core import PpTokeniser

class TestPpTokeniserPerfBase(unittest.TestCase):
    """Helper class for the performance tests."""

    def retPpTokeniser(self, theContent):
        """Returns a PpTokeniser object with the supplied content."""
        return PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(theContent)
                )

    def runTokGen(self, thePpTok, incWs=True):
        """causes theLex to preprocess and returns:
        (tokens, time_in_seconds_as_a_float)."""
        myTimStart = time.clock()
        if incWs:
            myToks = [t for t in next(thePpTok)]
        else:
            myToks = [t for t in next(thePpTok) if not t.isWs()]
        myTime = time.clock() - myTimStart
        myCntr = len(myToks)
        sys.stderr.write('Count: %8d, Rate: %8.1f tokens/s ... ' % (myCntr, myCntr / myTime))
        return myToks, myTime

    def countTokGen(self, thePpTok):
        """causes theLex to preprocess and returns:
        (number_of_tokens, time_in_seconds_as_a_float)."""
        myCntr = 0
        myTimStart = time.clock()
        for t in next(thePpTok):
            myCntr += 1
        myTime = time.clock() - myTimStart
        sys.stderr.write('Count: %8d, Rate: %8.1f tokens/s ... ' % (myCntr, myCntr / myTime))
        return myCntr, myTime

    def run_lexPhases_0(self, thePpTok):
        myTimStart = time.clock()
        myLines = thePpTok.lexPhases_0()
        myTime = time.clock() - myTimStart
        c = 0
        for aLine in myLines:
            c += len(aLine)
        sys.stderr.write('Time: %10.6f Rate: %8.1f kb/s ... ' % (myTime, c / (1024*myTime)))
        #sys.stderr.write('Rate: %8.1f kb/s ... ' % (c / (1024*myTime)))
        return myLines, myTime
        
    def run_genStrTypRep_0(self, thePpTok):
        myTimStart = time.clock()
        myLines = [t for t in thePpTok.genStrTypRep_0()]
        myTime = time.clock() - myTimStart
        c = 0
        for aLine in myLines:
            c += len(aLine)
        sys.stderr.write('Time: %10.6f Rate: %8.1f kb/s ... ' % (myTime, c / (1024*myTime)))
        return myLines, myTime
    
    def run_lexPhases_01(self, thePpTok):
        myLines_0 = thePpTok.lexPhases_0()
        myTimStart = time.clock()
        #tt = [t for t in thePpTok.genLexPhase1(myLines_0)]
        for t in thePpTok.genLexPhase1(myLines_0):
            pass
        myTime = time.clock() - myTimStart
        c = 0
        for aLine in myLines_0:
            c += len(aLine)
        sys.stderr.write('Rate: %8.1f kb/s ... ' % (c / (1024*myTime)))
        return myLines_0, myTime
    
    def run__convertToLexCharset(self, thePpTok):
        """Part of phase 1."""
        myTimStart = time.clock()
        myLines_0 = thePpTok.lexPhases_0()
        thePpTok._convertToLexCharset(myLines_0)
        myTime = time.clock() - myTimStart
        c = 0
        for aLine in myLines_0:
            c += len(aLine)
        sys.stderr.write('Rate: %8.1f kb/s ... ' % (c / (1024*myTime)))
        return myLines_0, myTime

    def run__translateTrigraphs(self, thePpTok):
        """Part of phase 1."""
        myTimStart = time.clock()
        myLines_0 = thePpTok.lexPhases_0()
        thePpTok._convertToLexCharset(myLines_0)
        for t in thePpTok._genTrigraphs(myLines_0):
            pass
        myTime = time.clock() - myTimStart
        c = 0
        for aLine in myLines_0:
            c += len(aLine)
        sys.stderr.write('Rate: %8.1f kb/s ... ' % (c / (1024*myTime)))
        return myLines_0, myTime

    def run_lexPhases_012(self, thePpTok):
        myTimStart = time.clock()
        myLines_0 = thePpTok.lexPhases_0()
        for t in thePpTok.genLexPhase1(myLines_0):
            pass
        #assert(0)
        #thePpTok.genLexPhase1(myLines_0)
        myTime = time.clock() - myTimStart
        c = 0
        for aLine in myLines_0:
            c += len(aLine)
        sys.stderr.write('Rate: %8.1f kb/s ... ' % (c / (1024*myTime)))
        return myLines_0, myTime
                
#===============================================================================
#    def timeCpp(self, theStr):
#        """Sends the string to cpp and rturns
#        (number_of_bytes, time_in_seconds_as_a_float)."""
#        myFobj = StringIO.StringIO(theStr)
#        myTimStart = time.clock()
#        c, s = self.sysCallCpp(myFobj, thePreIncS=None)
#        print 'TRACE:', c, s
#        self.assertEquals(0, c)
#        myTime = time.clock() - myTimStart
#        myCntr = len(s)
#        sys.stderr.write('Bytes: %8d, Rate: %8.1f bytes/s ... ' % (myCntr, myCntr / myTime))
#        return myCntr, myTime
# 
#    def sysCallCpp(self, fileObj, thePreIncS=None):
#        """Sends the file object contents to cpp
#        and returns  pair of (return code, the result as a string)."""
#        myCmd = 'cpp -E -P'
#        if thePreIncS is not None:
#            for aInc in thePreIncS:
#                myCmd += ' -include %s' % aInc
#        # We use file
#        myCmd += ' - -'
#        print 'myCmd', myCmd
#        p = subprocess.Popen(myCmd,
#                             shell=True,
#                             stdin=subprocess.PIPE,
#                             stdout=subprocess.PIPE,
#                             stderr=subprocess.PIPE)
#        #fileObj.seek(0)
#        p.stdin.write(fileObj.read())
#        p.stdin.close()
#        p.wait()
#        #print 'TRACE OUT:', p.stdout.read()
#        return p.returncode, p.stdout.read()
#===============================================================================

class TestPpTokeniserLexPhases_0(TestPpTokeniserPerfBase):

    def test_0_00(self):
        """TestPpTokeniserLexPhases: Phase 0 with "spam\\n" *      1."""
        myInput = 'spam\n' * 1
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_0(myP)

    def test_0_00_01(self):
        """TestPpTokeniserLexPhases: Phase 0 with "spam\\n" *      2."""
        myInput = 'spam\n' * 2
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_0(myP)

    def test_0_00_02(self):
        """TestPpTokeniserLexPhases: Phase 0 with "spam\\n" *      4."""
        myInput = 'spam\n' * 4
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_0(myP)

    def test_0_01(self):
        """TestPpTokeniserLexPhases: Phase 0 with "spam\\n" *     10."""
        myInput = 'spam\n' * 10
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_0(myP)

    def test_0_02(self):
        """TestPpTokeniserLexPhases: Phase 0 with "spam\\n" *    100."""
        myInput = 'spam\n' * 100
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_0(myP)

    def test_0_03(self):
        """TestPpTokeniserLexPhases: Phase 0 with "spam\\n" *   1000."""
        myInput = 'spam\n' * 1000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_0(myP)

    def test_0_04(self):
        """TestPpTokeniserLexPhases: Phase 0 with "spam\\n" *  10000."""
        myInput = 'spam\n' * 10000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_0(myP)

    def test_0_05(self):
        """TestPpTokeniserLexPhases: Phase 0 with "spam\\n" * 100000."""
        myInput = 'spam\n' * 100000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_0(myP)

class TestPpTokeniserLexPhases_0_0(TestPpTokeniserPerfBase):
    def test_1_00_00(self):
        """TestPpTokeniserLexPhases: Phase 0+_convertToLexCharset with "spam\\n" *      1."""
        myInput = 'spam\n' * 1
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__convertToLexCharset(myP)
                
    def test_1_00_00_01(self):
        """TestPpTokeniserLexPhases: Phase 0+_convertToLexCharset with "spam\\n" *      2."""
        myInput = 'spam\n' * 2
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__convertToLexCharset(myP)
                
    def test_1_00_00_02(self):
        """TestPpTokeniserLexPhases: Phase 0+_convertToLexCharset with "spam\\n" *      4."""
        myInput = 'spam\n' * 4
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__convertToLexCharset(myP)
                
    def test_1_00_00_03(self):
        """TestPpTokeniserLexPhases: Phase 0+_convertToLexCharset with "spam\\n" *      8."""
        myInput = 'spam\n' * 8
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__convertToLexCharset(myP)
                
    def test_1_00_01(self):
        """TestPpTokeniserLexPhases: Phase 0+_convertToLexCharset with "spam\\n" *     10."""
        myInput = 'spam\n' * 10
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__convertToLexCharset(myP)
        
    def test_1_00_02(self):
        """TestPpTokeniserLexPhases: Phase 0+_convertToLexCharset with "spam\\n" *    100."""
        myInput = 'spam\n' * 100
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__convertToLexCharset(myP)
        
    def test_1_00_03(self):
        """TestPpTokeniserLexPhases: Phase 0+_convertToLexCharset with "spam\\n" *   1000."""
        myInput = 'spam\n' * 1000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__convertToLexCharset(myP)
        
    def test_1_00_04(self):
        """TestPpTokeniserLexPhases: Phase 0+_convertToLexCharset with "spam\\n" *  10000."""
        myInput = 'spam\n' * 10000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__convertToLexCharset(myP)
        
    def test_1_00_05(self):
        """TestPpTokeniserLexPhases: Phase 0+_convertToLexCharset with "spam\\n" * 100000."""
        myInput = 'spam\n' * 100000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__convertToLexCharset(myP)
        
class TestPpTokeniserLexPhases_0_1(TestPpTokeniserPerfBase):
    def test_1_01_00(self):
        """TestPpTokeniserLexPhases: Phase 0+_translateTrigraphs with "spam\\n" *      1."""
        myInput = 'spam\n' * 1
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__translateTrigraphs(myP)
                
    def test_1_01_00_01(self):
        """TestPpTokeniserLexPhases: Phase 0+_translateTrigraphs with "spam\\n" *      2."""
        myInput = 'spam\n' * 2
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__translateTrigraphs(myP)
                
    def test_1_01_00_02(self):
        """TestPpTokeniserLexPhases: Phase 0+_translateTrigraphs with "spam\\n" *      4."""
        myInput = 'spam\n' * 4
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__translateTrigraphs(myP)
                
    def test_1_01_00_03(self):
        """TestPpTokeniserLexPhases: Phase 0+_translateTrigraphs with "spam\\n" *      8."""
        myInput = 'spam\n' * 8
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__translateTrigraphs(myP)
                
    def test_1_01_01(self):
        """TestPpTokeniserLexPhases: Phase 0+_translateTrigraphs with "spam\\n" *     10."""
        myInput = 'spam\n' * 10
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__translateTrigraphs(myP)
        
    def test_1_01_02(self):
        """TestPpTokeniserLexPhases: Phase 0+_translateTrigraphs with "spam\\n" *    100."""
        myInput = 'spam\n' * 100
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__translateTrigraphs(myP)
        
    def test_1_01_03(self):
        """TestPpTokeniserLexPhases: Phase 0+_translateTrigraphs with "spam\\n" *   1000."""
        myInput = 'spam\n' * 1000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__translateTrigraphs(myP)
        
    def test_1_01_04(self):
        """TestPpTokeniserLexPhases: Phase 0+_translateTrigraphs with "spam\\n" *  10000."""
        myInput = 'spam\n' * 10000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__translateTrigraphs(myP)
        
    def test_1_01_05(self):
        """TestPpTokeniserLexPhases: Phase 0+_translateTrigraphs with "spam\\n" * 100000."""
        myInput = 'spam\n' * 100000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run__translateTrigraphs(myP)
        
class TestPpTokeniserLexPhases_1_0(TestPpTokeniserPerfBase):
    def test_1_02_00(self):
        """TestPpTokeniserLexPhases: Phase 0+1 with "spam\\n" *      1."""
        myInput = 'spam\n' * 1
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_01(myP)

    def test_1_02_00_01(self):
        """TestPpTokeniserLexPhases: Phase 0+1 with "spam\\n" *      2."""
        myInput = 'spam\n' * 2
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_01(myP)

    def test_1_02_00_02(self):
        """TestPpTokeniserLexPhases: Phase 0+1 with "spam\\n" *      4."""
        myInput = 'spam\n' * 4
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_01(myP)

    def test_1_02_01(self):
        """TestPpTokeniserLexPhases: Phase 0+1 with "spam\\n" *     10."""
        myInput = 'spam\n' * 10
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_01(myP)

    def test_1_02_02(self):
        """TestPpTokeniserLexPhases: Phase 0+1 with "spam\\n" *    100."""
        myInput = 'spam\n' * 100
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_01(myP)

    def test_1_02_03(self):
        """TestPpTokeniserLexPhases: Phase 0+1 with "spam\\n" *   1000."""
        myInput = 'spam\n' * 1000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_01(myP)

    def test_1_02_04(self):
        """TestPpTokeniserLexPhases: Phase 0+1 with "spam\\n" *  10000."""
        myInput = 'spam\n' * 10000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_01(myP)

    def test_1_02_05(self):
        """TestPpTokeniserLexPhases: Phase 0+1 with "spam\\n" * 100000."""
        myInput = 'spam\n' * 100000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_01(myP)

    def test_2_00(self):
        """TestPpTokeniserLexPhases: Phase 0+1+2 with "spam\\n" *      1."""
        myInput = 'spam\n' * 1
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_012(myP)

    def test_2_00_01(self):
        """TestPpTokeniserLexPhases: Phase 0+1+2 with "spam\\n" *      2."""
        myInput = 'spam\n' * 2
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_012(myP)

    def test_2_00_02(self):
        """TestPpTokeniserLexPhases: Phase 0+1+2 with "spam\\n" *      4."""
        myInput = 'spam\n' * 4
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_012(myP)

    def test_2_01(self):
        """TestPpTokeniserLexPhases: Phase 0+1+2 with "spam\\n" *     10."""
        myInput = 'spam\n' * 10
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_012(myP)

    def test_2_02(self):
        """TestPpTokeniserLexPhases: Phase 0+1+2 with "spam\\n" *    100."""
        myInput = 'spam\n' * 100
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_012(myP)

    def test_2_03(self):
        """TestPpTokeniserLexPhases: Phase 0+1+2 with "spam\\n" *   1000."""
        myInput = 'spam\n' * 1000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_012(myP)

    def test_2_04(self):
        """TestPpTokeniserLexPhases: Phase 0+1+2 with "spam\\n" *  10000."""
        myInput = 'spam\n' * 10000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_012(myP)

    def test_2_05(self):
        """TestPpTokeniserLexPhases: Phase 0+1+2 with "spam\\n" * 100000."""
        myInput = 'spam\n' * 100000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_lexPhases_012(myP)


class TestPpTokeniserSimpleText(TestPpTokeniserPerfBase):

    def test_00(self):
        """TestPpTokeniserSimpleText: Test with "spam\\n" *      1."""
        myText = 'spam\n' * 1
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_00_00(self):
        """TestPpTokeniserSimpleText: Test with "spam\\n" *      2."""
        myText = 'spam\n' * 2
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_00_01(self):
        """TestPpTokeniserSimpleText: Test with "spam\\n" *      4."""
        myText = 'spam\n' * 4
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_01(self):
        """TestPpTokeniserSimpleText: Test with "spam\\n" *     10."""
        myText = 'spam\n' * 10
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_02(self):
        """TestPpTokeniserSimpleText: Test with "spam\\n" *    100."""
        myText = 'spam\n' * 100
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_03(self):
        """TestPpTokeniserSimpleText: Test with "spam\\n" *   1000."""
        myText = 'spam\n' * 1000
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_04(self):
        """TestPpTokeniserSimpleText: Test with "spam\\n" *  10000."""
        myText = 'spam\n' * 10000
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

class TestPpTokeniserInteger(TestPpTokeniserPerfBase):

    def test_00(self):
        """TestPpTokeniserInteger: Test with "1\\n" *      1."""
        myText = '1\n' * 1
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_00_00(self):
        """TestPpTokeniserInteger: Test with "1\\n" *      2."""
        myText = '1\n' * 2
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_00_01(self):
        """TestPpTokeniserInteger: Test with "1\\n" *      4."""
        myText = '1\n' * 4
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_01(self):
        """TestPpTokeniserInteger: Test with "1\\n" *     10."""
        myText = '1\n' * 10
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_02(self):
        """TestPpTokeniserInteger: Test with "1\\n" *    100."""
        myText = '1\n' * 100
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_03(self):
        """TestPpTokeniserInteger: Test with "1\\n" *   1000."""
        myText = '1\n' * 1000
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_04(self):
        """TestPpTokeniserInteger: Test with "1\\n" *  10000."""
        myText = '1\n' * 10000
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_05(self):
        """TestPpTokeniserInteger: Test with "1\\n" * 100000."""
        myText = '1\n' * 100000
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

class TestPpTokeniserFloat(TestPpTokeniserPerfBase):

    def test_00(self):
        """TestPpTokeniserFloat: Test with "999.25\\n" *      1."""
        myText = '999.25\n' * 1
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_00_00(self):
        """TestPpTokeniserFloat: Test with "999.25\\n" *      2."""
        myText = '999.25\n' * 2
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_00_01(self):
        """TestPpTokeniserFloat: Test with "999.25\\n" *      4."""
        myText = '999.25\n' * 4
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_01(self):
        """TestPpTokeniserFloat: Test with "999.25\\n" *     10."""
        myText = '999.25\n' * 10
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_02(self):
        """TestPpTokeniserFloat: Test with "999.25\\n" *    100."""
        myText = '999.25\n' * 100
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_03(self):
        """TestPpTokeniserFloat: Test with "999.25\\n" *   1000."""
        myText = '999.25\n' * 1000
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_04(self):
        """TestPpTokeniserFloat: Test with "999.25\\n" *  10000."""
        myText = '999.25\n' * 10000
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

    def test_05(self):
        """TestPpTokeniserFloat: Test with "999.25\\n" *  10000."""
        myText = '999.25\n' * 10000
        myP = self.retPpTokeniser(myText)
        myToks, myTime = self.runTokGen(myP)

class TestPpTokeniserIsInCharSet(TestPpTokeniserPerfBase):
    CNTR_LOOP = 10000

    def setUp(self):
        self._txt = ''.join([chr(x) for x in range(256)])
        self._txtChrSet = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_{}[]#()<>%:;.?*+-/^&|~!=,\\"'\t\v\f\n """
        self._ordS = list(range(9,13))+list(range(32,36))+list(range(37,64))+list(range(65,96))+list(range(97,127))
        
    def isInCharSet(self, c):
        # This takes ~4x as long
        #return ord(c) in self._ordS
        o = ord(c)
        # Note the 'most likely' character ranges are tested first for speed
        if (o > 36 and o < 64) \
        or (o > 64 and o < 96) \
        or (o > 96 and o < 127) \
        or (o > 8 and o < 13) \
        or (o > 31 and o < 36):
            return True
        return False

    def test_00(self):
        """TestPpTokeniserIsInCharSet: self._txt with using character set           ."""
        mySet = set(self._txtChrSet)
        myTimStart = time.clock()
        for i in range(self.CNTR_LOOP):
            for aChr in self._txt:
                myBool = aChr in mySet
        myTime = time.clock() - myTimStart
        sys.stderr.write('Rate: %8.1f kchars/s ... ' % (i * 256 / (myTime*1024)))

    def test_01(self):
        """TestPpTokeniserIsInCharSet: self._txt with using isInCharSet             ."""
        def isInCharSet(c):
            o = ord(c)
            # Note the 'most likely' character ranges are tested first for speed
            if (o > 36 and o < 64) \
            or (o > 64 and o < 96) \
            or (o > 96 and o < 127) \
            or (o > 8 and o < 13) \
            or (o > 31 and o < 36):
                return True
            return False
        myTimStart = time.clock()
        for i in range(self.CNTR_LOOP):
            for aChr in self._txt:
                myBool = isInCharSet(aChr)
        myTime = time.clock() - myTimStart
        sys.stderr.write('Rate: %8.1f kchars/s ... ' % (i * 256 / (myTime*1024)))

    def test_02(self):
        """TestPpTokeniserIsInCharSet: self._txt with using self.isInCharSet        ."""
        myTimStart = time.clock()
        for i in range(self.CNTR_LOOP):
            for aChr in self._txt:
                myBool = self.isInCharSet(aChr)
        myTime = time.clock() - myTimStart
        sys.stderr.write('Rate: %8.1f kchars/s ... ' % (i * 256 / (myTime*1024)))

    def test_10(self):
        """TestPpTokeniserIsInCharSet: self._txtChrSet with using character set     ."""
        mySet = set(self._txtChrSet)
        myTimStart = time.clock()
        for i in range(self.CNTR_LOOP):
            for aChr in self._txtChrSet:
                myBool = aChr in mySet
        myTime = time.clock() - myTimStart
        sys.stderr.write('Rate: %8.1f kchars/s ... ' % (i * 256 / (myTime*1024)))

    def test_11(self):
        """TestPpTokeniserIsInCharSet: self._txtChrSet with using isInCharSet()     ."""
        def isInCharSet(c):
            o = ord(c)
            # Note the 'most likely' character ranges are tested first for speed
            if (o > 36 and o < 64) \
            or (o > 64 and o < 96) \
            or (o > 96 and o < 127) \
            or (o > 8 and o < 13) \
            or (o > 31 and o < 36):
                return True
            return False
        myTimStart = time.clock()
        for i in range(self.CNTR_LOOP):
            for aChr in self._txtChrSet:
                myBool = isInCharSet(aChr)
        myTime = time.clock() - myTimStart
        sys.stderr.write('Rate: %8.1f kchars/s ... ' % (i * 256 / (myTime*1024)))

    def test_12(self):
        """TestPpTokeniserIsInCharSet: self._txtChrSet with using self.isInCharSet()."""
        myTimStart = time.clock()
        for i in range(self.CNTR_LOOP):
            for aChr in self._txtChrSet:
                myBool = self.isInCharSet(aChr)
        myTime = time.clock() - myTimStart
        sys.stderr.write('Rate: %8.1f kchars/s ... ' % (i * 256 / (myTime*1024)))

class TestPpTokeniser_run_genStrTypRep_0(TestPpTokeniserPerfBase):
    """Tests run_genStrTypRep_0()."""
    def test_0_00(self):
        """TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\\n" *      1."""
        myInput = 'spam\n' * 1
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_genStrTypRep_0(myP)

    def test_0_00_01(self):
        """TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\\n" *      2."""
        myInput = 'spam\n' * 2
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_genStrTypRep_0(myP)

    def test_0_00_02(self):
        """TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\\n" *      4."""
        myInput = 'spam\n' * 4
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_genStrTypRep_0(myP)

    def test_0_01(self):
        """TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\\n" *     10."""
        myInput = 'spam\n' * 10
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_genStrTypRep_0(myP)

    def test_0_02(self):
        """TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\\n" *    100."""
        myInput = 'spam\n' * 100
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_genStrTypRep_0(myP)

    def test_0_03(self):
        """TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\\n" *   1000."""
        myInput = 'spam\n' * 1000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_genStrTypRep_0(myP)

    def test_0_04(self):
        """TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\\n" *  10000."""
        myInput = 'spam\n' * 10000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_genStrTypRep_0(myP)

    def test_0_05(self):
        """TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\\n" * 100000."""
        myInput = 'spam\n' * 100000
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.run_genStrTypRep_0(myP)


class TestPpTokeniserOverallBase(TestPpTokeniserPerfBase):
    """Test the time taken to process a 'typical' file."""
    INPUT_STR = """#define str(s) # s
#define xstr(s) str(s)
#define debug(s, t) printf("x" # s "= %d, x" # t "= %s", \\
x ## s, x ## t)
#define INCFILE(n) vers ## n // from previous #include example
#define glue(a, b) a ## b
#define xglue(a, b) glue(a, b)
#define HIGHLOW "hello"
#define LOW LOW ", world"
debug(1, 2);
fputs(str(strncmp("abc\\0d", "abc", '\\4') // this goes away
== 0) str(: @\\n), s);
#include xstr(INCFILE(2).h)
glue(HIGH, LOW);
xglue(HIGH, LOW)
"""

class TestPpTokeniserOverall(TestPpTokeniserOverallBase):
    """Test the time taken to process a 'typical' file with CPIP."""
    def test_00(self):
        """TestPpTokeniserOverall: test_00() x   1."""
        myInput = self.INPUT_STR * 1
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.countTokGen(myP)

    def test_01(self):
        """TestPpTokeniserOverall: test_00() x  10."""
        myInput = self.INPUT_STR * 10
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.countTokGen(myP)

    def test_02(self):
        """TestPpTokeniserOverall: test_00() x 100."""
        myInput = self.INPUT_STR * 100
        myP = self.retPpTokeniser(myInput)
        myOutput, myTime = self.countTokGen(myP)

#===============================================================================
# class TestPpTokeniserOverallCpp(TestPpTokeniserOverallBase):
#    """Test the time taken to process a 'typical' file with cpp."""
#    def test_00(self):
#        """TestPpTokeniserOverall: test_00() x   1."""
#        myInput = self.INPUT_STR * 1
#        self.timeCpp(myInput)
#===============================================================================

class Special(TestPpTokeniserPerfBase):
    pass
    
class NullClass(TestPpTokeniserPerfBase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserLexPhases_0))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserLexPhases_0_0))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserLexPhases_0_1))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserLexPhases_1_0))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniser_run_genStrTypRep_0))
#===============================================================================
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserSimpleText))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserInteger))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserFloat))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserIsInCharSet))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserOverall))
#===============================================================================
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpTokeniserOverallCpp))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestPpLexerLimits.py - A module that tests the implementation limits of
the PpLexer module.
Usage:
python TestPpLexerLimits.py [-lh --help]

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
    print('TestPpLexer.py script version "%s", dated %s' % (__version__, __date__))
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
