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

"""Tests for the File Include Handlers."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import io
import os
import sys
import logging

from cpip.core import IncludeHandler

######################
# Section: Unit tests.
######################
import unittest

# Define unit test classes
class TestCppIncludeStd(unittest.TestCase):
    """Tests the CppIncludeStd."""

    def testConstructor(self):
        """Tests a simple CppIncludeStd constructor."""
        myObj = IncludeHandler.CppIncludeStd([], [])
        myObj.validateCpStack()

    def testClearHistory(self):
        """Tests a simple CppIncludeStd constructor and clearHistory()."""
        myObj = IncludeHandler.CppIncludeStd([], [])
        myObj.validateCpStack()
        myObj.clearHistory()
        self.assertEqual(myObj._cpStack, [])
        self.assertEqual(myObj._findLogic, [])
        
class TestCppIncludeStdAbc(unittest.TestCase):
    """Tests CppIncludeStd is an ABC."""

    def test_searchFileFails(self):
        """Tests _searchFile() is not implemented."""
        myObj = IncludeHandler.CppIncludeStd([], [])
        self.assertRaises(
            NotImplementedError,
            myObj._searchFile,
            'NonExistentFile',
            os.curdir
            )

    def test_initialTuFails(self):
        """Tests initialTu() is not implemented."""
        myObj = IncludeHandler.CppIncludeStd([], [])
        self.assertRaises(
            NotImplementedError,
            myObj.initialTu,
            'NonExistentFile',
            )

class TestCppIncludeLookup(unittest.TestCase):
    """Tests the CppIncludeStd."""
    # Simulate the following where -I usr -I usr/inc -J sys -J sys/inc
    """#include <spam.h>
#include <inc/spam.h>
#include "spam.h"
#include "inc/spam.h"
"""

    def setUp(self):
        self._incSim = IncludeHandler.CppIncludeStringIO(
            theUsrDirs = [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ],
            theSysDirs = [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ],
            theInitialTuContent = u"""Contents of src/spam.c
""",
            theFilePathToContent = {
                os.path.join('usr', 'inc', 'spam.h') : u"""User, include, spam.h
""",
                os.path.join('usr', 'spam.h') : u"""User, spam.h
""",
                os.path.join('sys', 'spam.h') : u"""System, spam.h
""",
                os.path.join('sys', 'inc', 'spam.h') : u"""System, include, spam.h
""",
            }
            )
        self._incSim.validateCpStack()
        self.assertEqual([], self._incSim.cpStack)
        self.assertEqual(0, self._incSim.cpStackSize)
        # Load the initial translation unit
        f = self._incSim.initialTu(u'src/spam.c')
        self._incSim.validateCpStack()
        self.assertEqual(['src',], self._incSim.cpStack)
        self.assertEqual(1, self._incSim.cpStackSize)
        self.assertNotEqual(None, f)
        # Test the return value
        self.assertEqual('Contents of src/spam.c\n', f.fileObj.read())
        self.assertEqual('src/spam.c', f.filePath)
        self.assertEqual('src', f.currentPlace)
        self.assertEqual('TU', f.origin)

    def tearDown(self):
        self.assertEqual(['src',], self._incSim.cpStack)
        self._incSim.validateCpStack()
        self._incSim.endInclude()
        self._incSim.validateCpStack()

    def testSys(self):
        """TestCppIncludeLookup: Simulate #include <spam.h>."""
        # #include <spam.h> should resolve to sys/spam.h
        f = self._incSim._includeHcharseq('spam.h')
        self.assertNotEqual(None, f)
        self.assertEqual('sys', self._incSim.currentPlace)
        self.assertEqual(['src', 'sys'], self._incSim.cpStack)
        # Test the return value
        self.assertEqual('System, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('sys', 'spam.h'), f.filePath)
        self.assertEqual('sys', f.currentPlace)
        self.assertEqual('sys', f.origin)
        self._incSim.endInclude()

    def testIncSys(self):
        """TestCppIncludeLookup: Simulate #include <inc/spam.h>."""
        # #include <inc/spam.h> should resolve to sys/inc/spam.h
        f = self._incSim._includeHcharseq('inc/spam.h')
        self.assertNotEqual(None, f)
        self.assertEqual(os.path.join('sys', 'inc'), self._incSim.currentPlace)
        self.assertEqual(['src', os.path.join('sys', 'inc')], self._incSim.cpStack)
        # Test the return value
        self.assertEqual('System, include, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('sys', 'inc', 'spam.h'), f.filePath)
        self.assertEqual(os.path.join('sys', 'inc'), f.currentPlace)
        self.assertEqual('sys', f.origin)
        self._incSim.endInclude()

    def testUsr(self):
        """TestCppIncludeLookup: Simulate #include "spam.h"."""
        self.assertEqual(['src',], self._incSim.cpStack)
        f = self._incSim._includeQcharseq('spam.h')
        self.assertNotEqual(None, f)
        self.assertEqual('usr', self._incSim.currentPlace)
        self.assertEqual(['src', 'usr'], self._incSim.cpStack)
        # Test the return value
        self.assertEqual('User, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('usr', 'spam.h'), f.filePath)
        self.assertEqual('usr', f.currentPlace)
        self.assertEqual('usr', f.origin)
        self._incSim.endInclude()

    def testIncUsr(self):
        """TestCppIncludeLookup: Simulate #include "inc/spam.h"."""
        f = self._incSim._includeQcharseq('inc/spam.h')
        self.assertNotEqual(None, f)
        self.assertEqual(os.path.join('usr', 'inc'), self._incSim.currentPlace)
        self.assertEqual(['src', os.path.join('usr', 'inc')], self._incSim.cpStack)
        # Test the return value
        self.assertEqual('User, include, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('usr', 'inc', 'spam.h'), f.filePath)
        self.assertEqual(os.path.join('usr', 'inc'), f.currentPlace)
        self.assertEqual('usr', f.origin)
        self._incSim.endInclude()

class TestCppIncludeLookupVanilla(TestCppIncludeLookup):
    """Tests the CppIncludeStd by calling a general function."""
    # Simulate the following
    """#include <spam.h>
#include <inc\spam.h>
#include "spam.h"
#include "inc\spam.h"
"""
    def testSys(self):
        """TestCppIncludeLookupVanilla: Simulate #include <spam.h>."""
        # #include <spam.h> should resolve to sys/spam.h
        f = self._incSim.includeHeaderName('<spam.h>')
        self.assertNotEqual(None, f)
        self.assertEqual('sys', self._incSim.currentPlace)
        self.assertEqual(['src', 'sys'], self._incSim.cpStack)
        self.assertEqual(['<spam.h>', 'sys=sys'], self._incSim.findLogic)
        # Test the return value
        self.assertEqual('System, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('sys', 'spam.h'), f.filePath)
        self.assertEqual('sys', f.currentPlace)
        self.assertEqual('sys', f.origin)
        self._incSim.endInclude()

    def testIncSys(self):
        """TestCppIncludeLookupVanilla: Simulate #include <inc/spam.h>."""
        # #include <inc/spam.h> should resolve to sys/inc/spam.h
        f = self._incSim.includeHeaderName('<inc%sspam.h>' % os.sep)
        self.assertNotEqual(None, f)
        self.assertEqual(os.path.join('sys', 'inc'), self._incSim.currentPlace)
        self.assertEqual(['src', os.path.join('sys', 'inc')], self._incSim.cpStack)
        self.assertEqual(['<inc%sspam.h>' % os.sep, 'sys=sys'], self._incSim.findLogic)
        # Test the return value
        self.assertEqual('System, include, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('sys', 'inc', 'spam.h'), f.filePath)
        self.assertEqual(os.path.join('sys', 'inc'), f.currentPlace)
        self.assertEqual('sys', f.origin)
        self._incSim.endInclude()

    def testUsr(self):
        """TestCppIncludeLookupVanilla: Simulate #include "spam.h"."""
        self.assertEqual(['src',], self._incSim.cpStack)
        f = self._incSim.includeHeaderName('"spam.h"')
        self.assertNotEqual(None, f)
        self.assertEqual('usr', self._incSim.currentPlace)
        self.assertEqual(['src', 'usr'], self._incSim.cpStack)
        self.assertEqual(
                ['"spam.h"', 'CP=None', 'usr=usr'],
                self._incSim.findLogic
            )
        # Test the return value
        self.assertEqual('User, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('usr', 'spam.h'), f.filePath)
        self.assertEqual('usr', f.currentPlace)
        self.assertEqual('usr', f.origin)
        self._incSim.endInclude()

    def testIncUsr(self):
        """TestCppIncludeLookupVanilla: Simulate #include "inc/spam.h"."""
        f = self._incSim.includeHeaderName('"inc%sspam.h"' % os.sep)
        self.assertNotEqual(None, f)
        self.assertEqual(os.path.join('usr', 'inc'), self._incSim.currentPlace)
        self.assertEqual(['src', os.path.join('usr', 'inc')], self._incSim.cpStack)
        self.assertEqual(
                ['"inc%sspam.h"' % os.sep, 'CP=None', 'usr=usr'],
                self._incSim.findLogic
            )
        # Test the return value
        self.assertEqual('User, include, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('usr', 'inc', 'spam.h'), f.filePath)
        self.assertEqual(os.path.join('usr', 'inc'), f.currentPlace)
        self.assertEqual('usr', f.origin)
        self._incSim.endInclude()

    def testRaises(self):
        """TestCppIncludeLookupVanilla: Simulate failure on #include spam.h."""
        self.assertRaises(
            IncludeHandler.ExceptionCppInclude,
            self._incSim.includeHeaderName,
            'spam.h',
            )
        self.assertRaises(
            IncludeHandler.ExceptionCppInclude,
            self._incSim.includeHeaderName,
            '<spam.h"',
            )
        self.assertRaises(
            IncludeHandler.ExceptionCppInclude,
            self._incSim.includeHeaderName,
            '"spam.h>',
            )

class TestCppIncludeFallback(unittest.TestCase):
    """Tests the CppIncludeStd when Qstring falls back to Hstring."""

    def setUp(self):
        self._incSim = IncludeHandler.CppIncludeStringIO(
            [
                os.path.join('usr'),
                ],
            [
                os.path.join('sys'),
                ],
            u"""Contents of src/spam.c
""",
            {
                os.path.join('usr', 'spam.hp') : u"""User, spam.hp
""",
                os.path.join('sys', 'spam.h') : u"""System, spam.h
""",
            }
            )
        self._incSim.validateCpStack()
        self.assertEqual([], self._incSim.cpStack)
        self.assertEqual(0, self._incSim.cpStackSize)
        # Load the initial translation unit
        f = self._incSim.initialTu('src/spam.c')
        self._incSim.validateCpStack()
        self.assertEqual(['src',], self._incSim.cpStack)
        self.assertEqual(1, self._incSim.cpStackSize)
        self.assertNotEqual(None, f)
        # Test the return value
        self.assertEqual('Contents of src/spam.c\n', f.fileObj.read())
        self.assertEqual('src/spam.c', f.filePath)
        self.assertEqual('src', f.currentPlace)
        self.assertEqual('TU', f.origin)

    def tearDown(self):
        self.assertEqual(['src',], self._incSim.cpStack)
        self._incSim.validateCpStack()
        self._incSim.endInclude()
        self._incSim.validateCpStack()

    def testUserDirect(self):
        """TestCppIncludeFallback: Simulate #include "spam.hp" suceeds."""
        f = self._incSim._includeQcharseq('spam.hp')
        self.assertNotEqual(None, f)
        self.assertEqual('usr', self._incSim.currentPlace)
        self.assertEqual(['src', 'usr'], self._incSim.cpStack)
        # Test the return value
        self.assertEqual('User, spam.hp\n', f.fileObj.read())
        self.assertEqual(os.path.join('usr', 'spam.hp'), f.filePath)
        self.assertEqual('usr', f.currentPlace)
        self.assertEqual('usr', f.origin)
        self._incSim.endInclude()

    def testReinterpret_00(self):
        """TestCppIncludeFallback: Simulate #include "spam.h" interpreted as #include <spam.h>."""
        # #include "spam.h"> should resolve to sys/spam.h
        f = self._incSim._includeQcharseq('spam.h')
        self.assertNotEqual(None, f)
        self.assertEqual('sys', self._incSim.currentPlace)
        self.assertEqual(['src', 'sys'], self._incSim.cpStack)
        # Note: No prefix in list as _includeQcharseq called directly
        # rather than includeHeaderName()
        self.assertEqual(
                ['CP=None', 'usr=None', 'sys=sys'],
                self._incSim.findLogic
            )
        # Test the return value
        self.assertEqual('System, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('sys', 'spam.h'), f.filePath)
        self.assertEqual('sys', f.currentPlace)
        self.assertEqual('sys', f.origin)
        self._incSim.endInclude()

    def testReinterpret_01(self):
        """TestCppIncludeFallback: Simulate #include "spam.h" interpreted as #include <spam.h> using includeHeaderName()."""
        # #include "spam.h"> should resolve to sys/spam.h
        f = self._incSim.includeHeaderName('"spam.h"')
        self.assertNotEqual(None, f)
        self.assertEqual('sys', self._incSim.currentPlace)
        self.assertEqual(['src', 'sys'], self._incSim.cpStack)
        self.assertEqual(
                ['"spam.h"', 'CP=None', 'usr=None', 'sys=sys'],
                self._incSim.findLogic
            )
        # Test the return value
        self.assertEqual('System, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('sys', 'spam.h'), f.filePath)
        self.assertEqual('sys', f.currentPlace)
        self.assertEqual('sys', f.origin)
        self._incSim.endInclude()

class TestCppIncludeCurrentPlace(unittest.TestCase):
    """Tests the CppIncludeStd when Qstring falls back to the current place."""

    def setUp(self):
        self._incSim = IncludeHandler.CppIncludeStringIO(
            [
                os.path.join('usr'),
                ],
            [
                os.path.join('sys'),
                ],
            u"""Contents of src/spam.c
""",
            {
                os.path.join('usr', 'spam.hp') : u"""User, spam.hp
""",
                os.path.join('sys', 'spam.h') : u"""System, spam.h
""",
                os.path.join('src', 'spam.h') : u"""Current place, spam.h
""",
            }
            )
        self._incSim.validateCpStack()
        self.assertEqual([], self._incSim.cpStack)
        self.assertEqual(0, self._incSim.cpStackSize)
        # Load the initial translation unit
        f = self._incSim.initialTu('src/spam.c')
        self._incSim.validateCpStack()
        self.assertEqual(['src',], self._incSim.cpStack)
        self.assertEqual(1, self._incSim.cpStackSize)
        self.assertNotEqual(None, f)
        # Test the return value
        self.assertEqual('Contents of src/spam.c\n', f.fileObj.read())
        self.assertEqual('src/spam.c', f.filePath)
        self.assertEqual('src', f.currentPlace)
        self.assertEqual('TU', f.origin)

    def tearDown(self):
        self.assertEqual(['src',], self._incSim.cpStack)
        self._incSim.validateCpStack()
        self._incSim.endInclude()
        self._incSim.validateCpStack()

    def testUserDirect(self):
        """TestCppIncludeCurrentPlace: Simulate #include "spam.hp" suceeds."""
        f = self._incSim._includeQcharseq('spam.hp')
        self.assertNotEqual(None, f)
        self.assertEqual('usr', self._incSim.currentPlace)
        self.assertEqual(['src', 'usr'], self._incSim.cpStack)
        # Note: No prefix in list as _includeQcharseq called directly
        # rather than includeHeaderName()
        self.assertEqual(
                ['CP=None', 'usr=usr'],
                self._incSim.findLogic
            )
        # Test the return value
        self.assertEqual('User, spam.hp\n', f.fileObj.read())
        self.assertEqual(os.path.join('usr', 'spam.hp'), f.filePath)
        self.assertEqual('usr', f.currentPlace)
        self.assertEqual('usr', f.origin)
        self._incSim.endInclude()

    def testHstringToSystem(self):
        """TestCppIncludeFallback: Simulate #include <spam.h> resolves to system include."""
        # #include <spam.h> should resolve to sys/spam.h
        f = self._incSim._includeHcharseq('spam.h')
        self.assertNotEqual(None, f)
        self.assertEqual('sys', self._incSim.currentPlace)
        self.assertEqual(['src', 'sys'], self._incSim.cpStack)
        # Note: No prefix in list as _includeHcharseq called directly
        # rather than includeHeaderName()
        self.assertEqual(
                ['sys=sys'],
                self._incSim.findLogic
            )
        # Test the return value
        self.assertEqual('System, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('sys', 'spam.h'), f.filePath)
        self.assertEqual('sys', f.currentPlace)
        self.assertEqual('sys', f.origin)
        self._incSim.endInclude()

    def testQstringToCp(self):
        """TestCppIncludeFallback: Simulate #include "spam.h" resolves to current place."""
        # #include "spam.h" should resolve to the current place: src/spam.h
        f = self._incSim._includeQcharseq('spam.h')
        self.assertNotEqual(None, f)
        self.assertEqual('src', self._incSim.currentPlace)
        self.assertEqual(['src', 'src'], self._incSim.cpStack)
        # Note: No prefix in list as _includeQcharseq called directly
        # rather than includeHeaderName()
        self.assertEqual(
                ['CP=src', ],
                self._incSim.findLogic
            )
        # Test the return value
        self.assertEqual('Current place, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('src', 'spam.h'), f.filePath)
        self.assertEqual('src', f.currentPlace)
        self.assertEqual('CP', f.origin)
        self._incSim.endInclude()

class TestCppIncludeFailure(unittest.TestCase):
    """Tests failures."""

    def setUp(self):
        self._incSim = IncludeHandler.CppIncludeStringIO(
            [
                os.path.join('usr'),
                ],
            [
                os.path.join('sys'),
                ],
            u"""Contents of src/spam.c
""",
            {
                os.path.join('usr', 'spam.hp') : """User, spam.hp
""",
                os.path.join('sys', 'spam.h') : """System, spam.h
""",
            }
            )
        self.assertEqual(False, self._incSim.canInclude())
        self.assertRaises(IncludeHandler.ExceptionCppInclude, self._incSim.endInclude)
        try:
            self._incSim.currentPlace
            self.fail('IncludeHandler.ExceptionCppInclude not raised for currentPlace')
        except IncludeHandler.ExceptionCppInclude:
            pass
        self._incSim.validateCpStack()
        self.assertEqual([], self._incSim.cpStack)
        self.assertEqual(0, self._incSim.cpStackSize)
        # Load the initial translation unit
        f = self._incSim.initialTu('src/spam.c')
        self._incSim.validateCpStack()
        self.assertEqual(['src',], self._incSim.cpStack)
        self.assertEqual(1, self._incSim.cpStackSize)
        self.assertNotEqual(None, f)
        # Test the return value
        self.assertEqual('Contents of src/spam.c\n', f.fileObj.read())
        self.assertEqual('src/spam.c', f.filePath)
        self.assertEqual('src', f.currentPlace)
        self.assertEqual('TU', f.origin)
        self.assertRaises(IncludeHandler.ExceptionCppInclude, self._incSim.finalise)

    def tearDown(self):
        self.assertEqual(['src',], self._incSim.cpStack)
        self._incSim.validateCpStack()
        self._incSim.endInclude()
        self._incSim.validateCpStack()

    def testIncludeFails(self):
        """TestCppIncludeFailure: Simulate #include "eggs.h" fails."""
        f = self._incSim._includeQcharseq('eggs.h')
        self.assertEqual(None, f)
        self._incSim.endInclude()

    def testValidateStackPasses(self):
        """TestCppIncludeFailure: validateCpStack() stack passes."""
        self.assertEqual(True, self._incSim.validateCpStack())
        self.assertEqual(True, self._incSim.canInclude())
        f = self._incSim._includeQcharseq('eggs.h')
        self.assertEqual(True, self._incSim.validateCpStack())
        self.assertEqual(False, self._incSim.canInclude())
        # Note: No prefix in list as _includeQcharseq called directly
        # rather than includeHeaderName()
        self.assertEqual(
                ['CP=None', 'usr=None', 'sys=None'],
                self._incSim.findLogic
            )
        self.assertEqual(None, f)
        self._incSim.endInclude()

    def testValidateStackFails(self):
        """TestCppIncludeFailure: validateCpStack() stack fails."""
        f = self._incSim._includeQcharseq('eggs.h')
        self.assertEqual(None, f)
        # Note: No prefix in list as _includeQcharseq called directly
        # rather than includeHeaderName()
        self.assertEqual(
                ['CP=None', 'usr=None', 'sys=None'],
                self._incSim.findLogic
            )
        self.assertRaises(IncludeHandler.ExceptionCppInclude, self._incSim._includeQcharseq, 'chips.h')
        self.assertRaises(IncludeHandler.ExceptionCppInclude, self._incSim._includeHcharseq, 'chips.h')
        self.assertEqual(True, self._incSim.validateCpStack())
        # Append a non-None
        self._incSim._cpStack.append('Something')
        self.assertEqual(False, self._incSim.canInclude())
        self.assertEqual(False, self._incSim.validateCpStack())
        try:
            self._incSim.currentPlace
            self.fail('IncludeHandler.ExceptionCppInclude not raised for currentPlace')
        except IncludeHandler.ExceptionCppInclude:
            pass
        self._incSim._cpStack.pop()
        self._incSim.endInclude()

    def testIncludeAfterFail(self):
        """TestCppIncludeFailure: Simulate #include after failure."""
        f = self._incSim._includeQcharseq('eggs.h')
        self.assertEqual(None, f)
        # Note: No prefix in list as _includeQcharseq called directly
        # rather than includeHeaderName()
        self.assertEqual(
                ['CP=None', 'usr=None', 'sys=None'],
                self._incSim.findLogic
            )
        self.assertRaises(IncludeHandler.ExceptionCppInclude, self._incSim._includeQcharseq, 'chips.h')
        #self.assertEqual('usr', self._incSim.currentPlace)
        #self.assertEqual(['src', 'usr'], self._incSim.cpStack)
        ## Test the return value
        #self.assertEqual('User, spam.hp\n', f.fileObj.read())
        #self.assertEqual(os.path.join('usr', 'spam.hp'), f.filePath)
        #self.assertEqual('usr', f.currentPlace)
        #self.assertEqual('usr', f.origin)
        self._incSim.endInclude()

    def testNoMultipleTuS(self):
        """TestCppIncludeFailure: multiple TUs fails."""
        self.assertRaises(
            IncludeHandler.ExceptionCppInclude,
            self._incSim.initialTu,
            ''
            )

class TestCppIncludeStdOs(unittest.TestCase):
    """Tests standard include behaviour from the OS file system."""
    def setUp(self):
        self._incSim = IncludeHandler.CppIncludeStdOs([], [])
        
    def _getRelFilePath(self, fileRelHere):
        return os.path.join(self._getRelDirPath(), fileRelHere)

    def _getRelDirPath(self):
        r = os.path.dirname(__file__)
        if r == os.sep:
            r = ''
        return r

    def testIncludeInitialTuPasses(self):
        """Tests standard TU find succeeds from the OS file system."""
        f = self._incSim.initialTu(self._getRelFilePath('mt.h'))
        self.assertNotEqual(None, f)
        self.assertEqual([self._getRelDirPath()], self._incSim.cpStack)
        # Test the return value
        self.assertEqual('', f.fileObj.read())
        self.assertEqual(os.path.join(self._getRelDirPath(), 'mt.h'), f.filePath)
        self.assertEqual(self._getRelDirPath(), f.currentPlace)
        self.assertEqual('TU', f.origin)

    def testIncludeInitialTuFails(self):
        """Tests standard TU find fails from the OS file system."""
        f = self._incSim.initialTu('NONEXITENT')
        self.assertEqual(None, f)

    def testIncludePasses(self):
        """Tests standard include succeeds from the OS file system."""
        f = self._incSim._searchFile(self._getRelFilePath('mt.h'), os.curdir)
        self.assertNotEqual(None, f)
        # Test the return value
        self.assertEqual('', f.fileObj.read())
        self.assertEqual(os.path.join(os.curdir, self._getRelDirPath(), 'mt.h'), f.filePath)
#         print(os.path.join(os.curdir, self._getRelDirPath()))
#         print('===========', self._getRelDirPath(), '||', f.currentPlace)
        expCurrentPlace = os.path.relpath(os.path.join(os.curdir, self._getRelDirPath()))
        if len(self._getRelDirPath()) > 0:
            expCurrentPlace = os.path.join(os.curdir, expCurrentPlace)
        self.assertEqual(os.path.abspath(expCurrentPlace),
                         os.path.abspath(f.currentPlace))
        self.assertEqual(None, f.origin)

    def testIncludeFails(self):
        """Tests standard include fails from the OS file system."""
        f = self._incSim._searchFile('NONEXITENT', os.curdir)
        self.assertEqual(None, f)

    def testNoMultipleTuS(self):
        """TestCppIncludeFailure: multiple ITUs fails."""
        f = self._incSim.initialTu(self._getRelFilePath('mt.h'))
        self.assertNotEqual(None, f)
        self.assertRaises(
            IncludeHandler.ExceptionCppInclude,
            self._incSim.initialTu,
            ''
            )

class TestCppIncludeStdin(unittest.TestCase):
    """Tests standard include behaviour from stdin and the OS file system."""
    def setUp(self):
        self._incSim = IncludeHandler.CppIncludeStdin([], [])
        
    def _getRelFilePath(self, fileRelHere):
        return os.path.join(self._getRelDirPath(), fileRelHere)

    def _getRelDirPath(self):
        r = os.path.dirname(__file__)
        if r == os.sep:
            r = ''
        return r

    def testIncludePasses(self):
        """Tests standard include succeeds from the OS file system."""
        f = self._incSim._searchFile(self._getRelFilePath('mt.h'), os.curdir)
        self.assertNotEqual(None, f)
        # Test the return value
        self.assertEqual('', f.fileObj.read())
        self.assertEqual(os.path.join(os.curdir, self._getRelDirPath(), 'mt.h'), f.filePath)
#         print(os.path.join(os.curdir, self._getRelDirPath()))
#         print('===========', self._getRelDirPath(), '||', f.currentPlace)
        expCurrentPlace = os.path.relpath(os.path.join(os.curdir, self._getRelDirPath()))
        if len(self._getRelDirPath()) > 0:
            expCurrentPlace = os.path.join(os.curdir, expCurrentPlace)
        self.assertEqual(os.path.abspath(expCurrentPlace),
                         os.path.abspath(f.currentPlace))
        self.assertEqual(None, f.origin)

    def testIncludeFails(self):
        """Tests standard include fails from the OS file system."""
        f = self._incSim._searchFile('NONEXITENT', os.curdir)
        self.assertEqual(None, f)

    def testNoMultipleTuS(self):
        """TestCppIncludeFailure: multiple ITUs fails."""
        f = self._incSim.initialTu(self._getRelFilePath('mt.h'))
        self.assertNotEqual(None, f)
        self.assertRaises(
            IncludeHandler.ExceptionCppInclude,
            self._incSim.initialTu,
            ''
            )
    
    def testStdinWriteRead(self):
        try:
            temp = sys.stdin
            content = u'Hello world\n'
            sys.stdin = io.StringIO(content)
            f = self._incSim.initialTu('stdin').fileObj
            self.assertEqual(content, f.read())
        finally:
            sys.stdin = temp

class TestCppIncludeNextLookup(TestCppIncludeLookup):
    """Tests the #include_next GCC extension."""
    # Simulate the following where -I usr -I usr/inc -J sys -J sys/inc
    """// Simulates the following:
#include_next <spam.h>      /* First one found at sys/spam.h, next one found as sys/inc/spam.h */
#include_next "spam.h"      /* First one found at usr/spam.h, next one found as usr/inc/spam.h */
#include_next <no_next.h>   /* First one found as sys/no_next.h, next one not found */
#include_next "no_next.h"   /* First one found as usr/no_next.h, next one not found */
"""

    def setUp(self):
        self._incSim = IncludeHandler.CppIncludeStringIO(
            theUsrDirs = [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ],
            theSysDirs = [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ],
            theInitialTuContent = u"""Contents of src/spam.c
""",
            theFilePathToContent = {
                # spam.h
                os.path.join('usr', 'inc', 'spam.h') : u"""User, include, spam.h
""",
                os.path.join('usr', 'spam.h') : u"""User, spam.h
""",
                os.path.join('sys', 'spam.h') : u"""System, spam.h
""",
                os.path.join('sys', 'inc', 'spam.h') : u"""System, include, spam.h
""",
                # no_next.h
                os.path.join('usr', 'no_next.h') : u"""User, no_next.h
""",
                os.path.join('sys', 'no_next.h') : u"""System, no_next.h
""",
            }
            )
        self._incSim.validateCpStack()
        self.assertEqual([], self._incSim.cpStack)
        self.assertEqual(0, self._incSim.cpStackSize)
        # Load the initial translation unit
        f = self._incSim.initialTu(u'src/spam.c')
        self._incSim.validateCpStack()
        self.assertEqual(['src',], self._incSim.cpStack)
        self.assertEqual(1, self._incSim.cpStackSize)
        self.assertNotEqual(None, f)
        # Test the return value
        self.assertEqual('Contents of src/spam.c\n', f.fileObj.read())
        self.assertEqual('src/spam.c', f.filePath)
        self.assertEqual('src', f.currentPlace)
        self.assertEqual('TU', f.origin)

    def tearDown(self):
        self.assertEqual(['src',], self._incSim.cpStack)
        self._incSim.validateCpStack()
        self._incSim.endInclude()
        self._incSim.validateCpStack()

    def testSysNext(self):
        """TestCppIncludeNextLookup: Simulate #include_next <spam.h>."""
        # #include_next <spam.h> should resolve to sys/inc/spam.h
        f = self._incSim.includeNextHeaderName('<spam.h>')
        self.assertNotEqual(None, f)
        self.assertEqual(os.path.join('sys', 'inc'), self._incSim.currentPlace)
        self.assertEqual(['src', os.path.join('sys', 'inc')], self._incSim.cpStack)
        # Test the return value
        self.assertEqual('System, include, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('sys', 'inc', 'spam.h'), f.filePath)
        self.assertEqual(os.path.join('sys', 'inc'), f.currentPlace)
        self.assertEqual('sys', f.origin)
        self._incSim.endInclude()

    def testUsrNext(self):
        """TestCppIncludeNextLookup: Simulate #include_next "spam.h"."""
        # #include_next "spam.h" should resolve to usr/inc/spam.h
        self.assertEqual(['src',], self._incSim.cpStack)
        f = self._incSim.includeNextHeaderName('"spam.h"')
        self.assertNotEqual(None, f)
        self.assertEqual(os.path.join('usr', 'inc'), self._incSim.currentPlace)
        self.assertEqual(['src', os.path.join('usr', 'inc')], self._incSim.cpStack)
        # Test the return value
        self.assertEqual('User, include, spam.h\n', f.fileObj.read())
        self.assertEqual(os.path.join('usr', 'inc', 'spam.h'), f.filePath)
        self.assertEqual(os.path.join('usr', 'inc'), f.currentPlace)
        self.assertEqual('usr', f.origin)
        self._incSim.endInclude()

    def testSysNoNext(self):
        """TestCppIncludeNextLookup: Simulate #include_next <no_next.h>."""
        f = self._incSim._includeHcharseq('no_next.h', include_next=True)
        self.assertTrue(f is None)

    def testUsrNoNext(self):
        """TestCppIncludeNextLookup: Simulate #include_next "no_next.h"."""
        f = self._incSim._includeQcharseq('no_next.h', include_next=True)
        self.assertTrue(f is None)

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCppIncludeStd)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppIncludeStdAbc))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppIncludeLookup))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppIncludeLookupVanilla))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppIncludeFallback))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppIncludeCurrentPlace))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppIncludeFailure))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppIncludeStdOs))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppIncludeStdin))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppIncludeNextLookup))
#     suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCppIncludeNextLookupVanilla))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    print("""TestIncludeHandler.py - Tests the IncludeHandler module.
Usage:
python TestIncludeHandler.py [-hl: --help]

Options:
-h, --help ~ Help (this screen) and exit.
-l:        ~ set the logging level higher is quieter.
             Default is 30 (WARNING) e.g.:
                CRITICAL    50
                ERROR       40
                WARNING     30
                INFO        20
                DEBUG       10
                NOTSET      0
""")

def main():
    print('TestIncludeHandler.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
    print(__rights__)
    print()
    import getopt
    import time
    print('Command line:')
    print(' '.join(sys.argv))
    print()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError as myErr:
        usage()
        print('ERROR: Invalid option: %s' % str(myErr))
        sys.exit(1)
    logLevel = logging.WARNING
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o == '-l':
            logLevel = int(a)
    if len(args) != 0:
        usage()
        print('ERROR: Wrong number of arguments[%d]!' % len(args))
        sys.exit(1)
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    unitTest()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
