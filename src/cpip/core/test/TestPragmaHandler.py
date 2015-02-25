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

from cpip.core import PpToken, PragmaHandler

import unittest

class TestPragmaHandlerSTDC(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testSetUpTearDown(self):
        """TestPragmaHandlerSTDC: Test setUp() and tearDown()."""
        pass
    
    def test_STDC_00(self):
        """TestPragmaHandlerSTDC: Test replaceTokens."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        self.assertNotEqual(myH.replaceTokens, True)

    def test_STDC_01(self):
        """TestPragmaHandlerEcho: Test isLiteral."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        self.assertFalse(myH.isLiteral)

    def test_STDC_FP_CONTRACT_ON_fail_00(self):
        """TestPragmaHandlerSTDC: Test missing STDC with FP_CONTRACT ON."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('FP_CONTRACT',          'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('ON',                   'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '')

    def test_STDC_FP_CONTRACT_ON_fail_01(self):
        """TestPragmaHandlerSTDC: Test FP_CONTRACT ON, no FP_CONTRACT."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('ON',                   'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '')

    def test_STDC_FP_CONTRACT_ON_fail_02(self):
        """TestPragmaHandlerSTDC: Test FP_CONTRACT ON no ON."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('FP_CONTRACT',     'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '')

    def test_STDC_FP_CONTRACT_ON_fail_03(self):
        """TestPragmaHandlerSTDC: Test FP_CONTRACT ON is SPAM."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('FP_CONTRACT',          'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('SPAM',                   'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '')

    def test_STDC_FP_CONTRACT_ON(self):
        """TestPragmaHandlerSTDC: Test FP_CONTRACT ON."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('FP_CONTRACT',     'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('ON',                   'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '#define FP_CONTRACT ON\n')

    def test_STDC_FP_CONTRACT_ON__00(self):
        """TestPragmaHandlerSTDC: Test FP_CONTRACT ON, extra whitespace."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('FP_CONTRACT',     'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('ON',                   'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '#define FP_CONTRACT ON\n')

    def test_STDC_FP_CONTRACT_OFF(self):
        """TestPragmaHandlerSTDC: Test FP_CONTRACT OFF."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('FP_CONTRACT',     'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('OFF',                  'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '#define FP_CONTRACT OFF\n')

    def test_STDC_FP_CONTRACT_DEFAULT(self):
        """TestPragmaHandlerSTDC: Test FP_CONTRACT DEFAULT."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('FP_CONTRACT',     'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('DEFAULT',              'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '#define FP_CONTRACT DEFAULT\n')

    def test_STDC_FENV_ACCESS_ON(self):
        """TestPragmaHandlerSTDC: Test FENV_ACCESS ON."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('FENV_ACCESS',     'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('ON',                   'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '#define FENV_ACCESS ON\n')

    def test_STDC_FENV_ACCESS_OFF(self):
        """TestPragmaHandlerSTDC: Test FENV_ACCESS OFF."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('FENV_ACCESS',     'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('OFF',                  'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '#define FENV_ACCESS OFF\n')

    def test_STDC_FENV_ACCESS_DEFAULT(self):
        """TestPragmaHandlerSTDC: Test FENV_ACCESS DEFAULT."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('FENV_ACCESS',     'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('DEFAULT',              'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '#define FENV_ACCESS DEFAULT\n')

    def test_STDC_CX_LIMITED_RANGE_ON(self):
        """TestPragmaHandlerSTDC: Test CX_LIMITED_RANGE ON."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('CX_LIMITED_RANGE',     'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('ON',                   'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '#define CX_LIMITED_RANGE ON\n')

    def test_STDC_CX_LIMITED_RANGE_OFF(self):
        """TestPragmaHandlerSTDC: Test CX_LIMITED_RANGE OFF."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('CX_LIMITED_RANGE',     'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('OFF',                  'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '#define CX_LIMITED_RANGE OFF\n')

    def test_STDC_CX_LIMITED_RANGE_DEFAULT(self):
        """TestPragmaHandlerSTDC: Test CX_LIMITED_RANGE DEFAULT."""
        myH = PragmaHandler.PragmaHandlerSTDC()
        myTokS = [
                PpToken.PpToken('STDC',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('CX_LIMITED_RANGE',     'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('DEFAULT',              'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '#define CX_LIMITED_RANGE DEFAULT\n')

class TestPragmaHandlerEcho(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testSetUpTearDown(self):
        """TestPragmaHandlerEcho: Test setUp() and tearDown()."""
        pass
    
    def test_echo_00(self):
        """TestPragmaHandlerEcho: Test replaceTokens."""
        myH = PragmaHandler.PragmaHandlerEcho()
        self.assertNotEqual(myH.replaceTokens, True)

    def test_echo_01(self):
        """TestPragmaHandlerEcho: Test isLiteral."""
        myH = PragmaHandler.PragmaHandlerEcho()
        self.assertTrue(myH.isLiteral)

    def test_STDC_FP_CONTRACT_ON(self):
        """TestPragmaHandlerSTDC: Test FP_CONTRACT ON."""
        myH = PragmaHandler.PragmaHandlerEcho()
        myTokS = [
                PpToken.PpToken('some',                 'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('pragma',               'identifier'),
                PpToken.PpToken(' ',                    'whitespace'),
                PpToken.PpToken('command',              'identifier'),
                PpToken.PpToken('\n',                   'whitespace'),
            ]
        self.assertEqual(myH.pragma(myTokS), '#pragma some pragma command\n')


def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPragmaHandlerSTDC)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPragmaHandlerEcho))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

if __name__ == "__main__":
    unitTest()
