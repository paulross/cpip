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
import pprint

import io

from cpip.core import PpLexer
from cpip.core import CppDiagnostic
from cpip.core import PpTokeniser
from cpip.core import PpToken
from cpip.core import CppCond
from cpip.core import PragmaHandler
import TestBase
# File location test classes
from cpip.core.IncludeHandler import CppIncludeStringIO

######################
# Section: Unit tests.
######################
import unittest

class TestPpLexer(TestBase.TestCpipBase):
    """Helper class for the unit tests."""
    pass

class TestPpLexerCtor(TestPpLexer):
    """Tests the construction of a PpLexer object."""
    def test_00(self):
        """Default construction and finalisation."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 )
        myToks = [t for t in myLexer.ppTokens()]
        self.assertEqual([], myToks)
        myLexer.finalise()

    def test_01(self):
        """Simple construction and finalisation."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 preIncFiles=None,
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens()]
        self.assertEqual([], myToks)
        myLexer.finalise()

    def test_02(self):
        """Simple construction and finalisation with two calls to ppTokens()."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 preIncFiles=None,
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens()]
        self.assertEqual([], myToks)
        try:
            myToks = [t for t in myLexer.ppTokens()]
            self.fail('Failed to raise ExceptionPpLexerAlreadyGenerating')
        except PpLexer.ExceptionPpLexerAlreadyGenerating:
            pass

class TestPpLexerLowLevel(TestPpLexer):
    """Tests PpLexer low level functionality."""
    def test_retListReplacedTokens_00(self):
        """TestPpLexerLowLevel.test_retListReplacedTokens_00(): Token replacement of a list."""
        myLexer = PpLexer.PpLexer(
            'mt.h',
            CppIncludeStringIO([], [], '', {}),
            preIncFiles=[
                io.StringIO('#define SPAM(x,y) x+y\n#define EGGS SPAM\n'),
            ],
            diagnostic=None,
        )
        for t in myLexer.ppTokens():
            pass
#         self.assertEqual(
#             myLexer.definedMacros,
#             """#define EGGS SPAM /* Unnamed Pre-include#2 Ref: 0 True */
# #define SPAM(x,y) x+y /* Unnamed Pre-include#1 Ref: 0 True */""")
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['EGGS', 'SPAM', '__DATE__', '__TIME__'],
        )
        myTokS = []
        self.assertEqual([], myLexer._retListReplacedTokens(myTokS))
        myTokS = [
            PpToken.PpToken('EGGS',         'identifier'),
            PpToken.PpToken('\n',          'whitespace'),
        ]
        self.assertEqual(
                [
                    PpToken.PpToken('SPAM',         'identifier'),
                    PpToken.PpToken('\n',          'whitespace'),
                ],
                myLexer._retListReplacedTokens(myTokS))
        # Replace using EGGS then SPAM(...)
        myTokS = [
            PpToken.PpToken('EGGS',         'identifier'),
            PpToken.PpToken('(',            'preprocessing-op-or-punc'),
            PpToken.PpToken('  ',           'whitespace'),
            PpToken.PpToken('1',            'pp-number'),
            PpToken.PpToken('  ',           'whitespace'),
            PpToken.PpToken(',',            'preprocessing-op-or-punc'),
            PpToken.PpToken('  ',           'whitespace'),
            PpToken.PpToken('2',            'pp-number'),
            PpToken.PpToken('  ',           'whitespace'),
            PpToken.PpToken(')',            'preprocessing-op-or-punc'),
            PpToken.PpToken('  ',           'whitespace'),
            PpToken.PpToken('\n',           'whitespace'),
                  ]
        self.assertEqual(
                [
                    PpToken.PpToken('1',            'pp-number'),
                    PpToken.PpToken('+',            'preprocessing-op-or-punc'),
                    PpToken.PpToken('2',            'pp-number'),
                    PpToken.PpToken('  ',           'whitespace'),
                    PpToken.PpToken('\n',           'whitespace'),
                    ],
                myLexer._retListReplacedTokens(myTokS))
        # Replace using EGGS(...) EGGS
        myTokS = [
            PpToken.PpToken('EGGS',         'identifier'),
            PpToken.PpToken('(',            'preprocessing-op-or-punc'),
            PpToken.PpToken('  ',           'whitespace'),
            PpToken.PpToken('1',            'pp-number'),
            PpToken.PpToken('  ',           'whitespace'),
            PpToken.PpToken(',',            'preprocessing-op-or-punc'),
            PpToken.PpToken('  ',           'whitespace'),
            PpToken.PpToken('2',            'pp-number'),
            PpToken.PpToken('  ',           'whitespace'),
            PpToken.PpToken(')',            'preprocessing-op-or-punc'),
            PpToken.PpToken('  ',           'whitespace'),
            PpToken.PpToken('EGGS',         'identifier'),
            PpToken.PpToken('  ',           'whitespace'),
            PpToken.PpToken('\n',           'whitespace'),
                  ]
        self.assertEqual(
                [
                    PpToken.PpToken('1',            'pp-number'),
                    PpToken.PpToken('+',            'preprocessing-op-or-punc'),
                    PpToken.PpToken('2',            'pp-number'),
                    PpToken.PpToken('  ',           'whitespace'),
                    PpToken.PpToken('SPAM',         'identifier'),
                    PpToken.PpToken('  ',           'whitespace'),
                    PpToken.PpToken('\n',           'whitespace'),
                    ],
                myLexer._retListReplacedTokens(myTokS))
        #myLexer.finalise()

    def test_retCountNonWsTokens_00(self):
        """TestPpLexerLowLevel.test_retCountNonWsTokens_00(): Whitespace token count in a list."""
        myLexer = PpLexer.PpLexer(
            'mt.h',
            CppIncludeStringIO([], [], '', {}),
            preIncFiles=[
                io.StringIO('#define SPAM(x,y) x+y\n#define EGGS SPAM\n'),
                         ],
            diagnostic=None,
        )
        for t in myLexer.ppTokens():
            pass
#         self.assertEqual(
#             myLexer.definedMacros,
#             """#define EGGS SPAM /* Unnamed Pre-include#2 Ref: 0 True */
# #define SPAM(x,y) x+y /* Unnamed Pre-include#1 Ref: 0 True */""")
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['EGGS', 'SPAM', '__DATE__', '__TIME__'],
        )
        myTokS = []
        self.assertEqual(0, myLexer._countNonWsTokens(myTokS))
        myTokS = [
            PpToken.PpToken(' ',           'whitespace'),
                  ]
        self.assertEqual(0, myLexer._countNonWsTokens(myTokS))
        myTokS = [
            PpToken.PpToken('\n',          'whitespace'),
                  ]
        self.assertEqual(0, myLexer._countNonWsTokens(myTokS))
        myTokS = [
            PpToken.PpToken('   ',         'whitespace'),
            PpToken.PpToken(' ',           'whitespace'),
            PpToken.PpToken(' ',           'whitespace'),
            PpToken.PpToken('\n',          'whitespace'),
                  ]
        self.assertEqual(0, myLexer._countNonWsTokens(myTokS))
        myTokS = [
            PpToken.PpToken('   ',         'whitespace'),
            PpToken.PpToken('something',   'identifier'),
            PpToken.PpToken(' ',           'whitespace'),
            PpToken.PpToken('0',           'pp-number'),
            PpToken.PpToken('\n',          'whitespace'),
                  ]
        self.assertEqual(2, myLexer._countNonWsTokens(myTokS))
        #myLexer.finalise()

class TestPpLexerPreDefine(TestPpLexer):
    """Tests the construction of a PpLexer object with predefined macros.
    This does:
    Multiple pre-defines - see test_07() and test_08()
    Single empty pre-define - see test_00_01()
    Single predefine with just a newline - see test_00_02()
    Multiple pre-defines that are empty or just newlines - see test_00_03()
    """
    # TODO: More tests with:
    # Predefines that redefine well (in single and multiple predfines).
    # Predefines that redefine badly (in single and multiple predfines).
    # ITU that redefines well/badly with predefines.
    def test_00_00(self):
        """TestPpLexerPreDefine.test_00_00(): Ctor and finalisation with simple, single, predefined macro."""
        myPiS = [
                 """#define SPAM 1
""",
        ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 preIncFiles=[
                              io.StringIO(x) for x in myPiS
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens()]
        expToks = [
                   PpToken.PpToken('\n', 'whitespace'),
                   ]
        self.assertEqual(expToks, myToks)
        myLexer.finalise()
        # Some tests
        #print
        #print myLexer.definedMacros
        #print myLexer.fileIncludeGraphRoot
#         self.assertEqual(
#             str(myLexer.definedMacros),
#             '#define SPAM 1 /* Unnamed Pre-include#1 Ref: 0 True */')
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['SPAM', '__DATE__', '__TIME__'],
        )
        self.assertEqual(
            str(myLexer.fileIncludeGraphRoot),
            """Unnamed Pre-include [7, 4]:  True "" ""
mt.h [0, 0]:  True "" \"\"""",
            )

    def test_00_01(self):
        """TestPpLexerPreDefine.test_00_01(): Ctor and finalisation with empty predefine."""
        myPiS = ['', ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 preIncFiles=[
                              io.StringIO(x) for x in myPiS
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens()]
        self.assertEqual([], myToks)
        myLexer.finalise()
        # Some tests
        #print
        #print myLexer.definedMacros
        #print myLexer.fileIncludeGraphRoot
#         self.assertEqual(str(myLexer.definedMacros), '')
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['__DATE__', '__TIME__'],
        )
        self.assertEqual(
            str(myLexer.fileIncludeGraphRoot),
            """Unnamed Pre-include [0, 0]:  True "" ""
mt.h [0, 0]:  True "" \"\"""",
            )

    def test_00_02(self):
        """TestPpLexerPreDefine.test_00_02(): Ctor and finalisation with predefine as single newline."""
        myPiS = ['\n', ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 preIncFiles=[
                              io.StringIO(x) for x in myPiS
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens()]
        expToks = [
                   PpToken.PpToken('\n', 'whitespace'),
                   ]
        self.assertEqual(expToks, myToks)
        myLexer.finalise()
        # Some tests
        #print
        #print myLexer.definedMacros
        #print myLexer.fileIncludeGraphRoot
#         self.assertEqual(str(myLexer.definedMacros), '')
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['__DATE__', '__TIME__'],
        )
        self.assertEqual(
            str(myLexer.fileIncludeGraphRoot),
            """Unnamed Pre-include [1, 0]:  True "" ""
mt.h [0, 0]:  True "" \"\"""",
            )

    def test_00_03(self):
        """TestPpLexerPreDefine.test_00_03(): Ctor and finalisation with multiple predefines as empty or newlines."""
        myPiS = [
                 '\n',
                 '',
                 '\n\n\n\n',
                 '',
                 '\n',
                 '',
                 '\n\n',
                 ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 preIncFiles=[
                              io.StringIO(x) for x in myPiS
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens()]
        expToks = [
                   PpToken.PpToken('\n', 'whitespace'),
                   PpToken.PpToken('\n\n\n\n', 'whitespace'),
                   PpToken.PpToken('\n', 'whitespace'),
                   PpToken.PpToken('\n\n', 'whitespace'),
                   ]
        self.assertEqual(expToks, myToks)
        myLexer.finalise()
        # Some tests
        #print
        #print myLexer.definedMacros
        #print myLexer.fileIncludeGraphRoot
#         self.assertEqual(str(myLexer.definedMacros), '')
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['__DATE__', '__TIME__'],
        )
        self.assertEqual(
            str(myLexer.fileIncludeGraphRoot),
            """Unnamed Pre-include [1, 0]:  True "" ""
Unnamed Pre-include [0, 0]:  True "" ""
Unnamed Pre-include [1, 0]:  True "" ""
Unnamed Pre-include [0, 0]:  True "" ""
Unnamed Pre-include [1, 0]:  True "" ""
Unnamed Pre-include [0, 0]:  True "" ""
Unnamed Pre-include [1, 0]:  True "" ""
mt.h [0, 0]:  True "" \"\"""",
            )

    def test_00(self):
        """TestPpLexerPreDefine.test_00(): Ctor and finalisation with simple predefined macros."""
        myPiS = [
                 """#define SPAM(x,y) x+y
#define EGGS SPAM
""",
        ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 preIncFiles=[
                              io.StringIO(x) for x in myPiS
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens()]
        expToks = [
                   PpToken.PpToken('\n', 'whitespace'),
                   PpToken.PpToken('\n', 'whitespace'),
                   ]
        self.assertEqual(expToks, myToks)
        myLexer.finalise()
        # Some tests
        #print
        #print myLexer.definedMacros
        #print myLexer.fileIncludeGraphRoot
#         self.assertEqual(str(myLexer.definedMacros), """#define EGGS SPAM /* Unnamed Pre-include#2 Ref: 0 True */
# #define SPAM(x,y) x+y /* Unnamed Pre-include#1 Ref: 0 True */""")
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['EGGS', 'SPAM', '__DATE__', '__TIME__'],
        )
        self.assertEqual(
            str(myLexer.fileIncludeGraphRoot),
            """Unnamed Pre-include [21, 15]:  True "" ""
mt.h [0, 0]:  True "" \"\"""")

    def test_01(self):
        """TestPpLexerPreDefine.test_01(): Ctor and finalisation, whitespace handling."""
        myPiS = [
                """#define SPAM(x,y) x+y
#    define EGGS SPAM
#    define       CHIPS      EGGS
""",
        ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 preIncFiles=[
                              io.StringIO(x) for x in myPiS
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens()]
        expToks = [
                   PpToken.PpToken('\n', 'whitespace'),
                   PpToken.PpToken('\n', 'whitespace'),
                   PpToken.PpToken('\n', 'whitespace'),
                   ]
        self.assertEqual(expToks, myToks)
        myLexer.finalise()
        # Some tests
        #print
        #print myLexer.definedMacros
        #print myLexer.fileIncludeGraphRoot
#         self.assertEqual(
#                          str(myLexer.definedMacros),
#                          """#define CHIPS EGGS /* Unnamed Pre-include#3 Ref: 0 True */
# #define EGGS SPAM /* Unnamed Pre-include#2 Ref: 0 True */
# #define SPAM(x,y) x+y /* Unnamed Pre-include#1 Ref: 0 True */""")
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['CHIPS', 'EGGS', 'SPAM', '__DATE__', '__TIME__'],
        )
        self.assertEqual(
            str(myLexer.fileIncludeGraphRoot),
            """Unnamed Pre-include [28, 19]:  True "" ""
mt.h [0, 0]:  True "" \"\"""")

    def test_02(self):
        """TestPpLexerPreDefine.test_02(): Ctor and finalisation, missing prefix in pre-define."""
        # NOTE: this does not raise an exception (neither does cpp.exe) because
        # 'define' is just seen as another identifier
        myPiS = [
                """define SPAM 1
 """,
        ]
        #print 'WTF', [StringIO.StringIO(x) for x in myPiS]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 preIncFiles=[
                              io.StringIO(x) for x in myPiS
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens()]
        expToks = [
                   PpToken.PpToken('define', 'identifier'),
                   PpToken.PpToken(' ', 'whitespace'),
                   PpToken.PpToken('SPAM', 'identifier'),
                   PpToken.PpToken(' ', 'whitespace'),
                   PpToken.PpToken('1', 'pp-number'),
                   PpToken.PpToken('\n ', 'whitespace'),
                   ]
        self.assertEqual(expToks, myToks)
        myLexer.finalise()
        # Some tests
        #print
        #print myLexer.definedMacros
        #print
        #print myLexer.fileIncludeGraphRoot
#         self.assertEqual(str(myLexer.definedMacros), '')
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['__DATE__', '__TIME__'],
        )
        self.assertEqual(
            str(myLexer.fileIncludeGraphRoot),
            """Unnamed Pre-include [6, 3]:  True "" ""
mt.h [0, 0]:  True "" \"\"""")

    def test_03(self):
        """TestPpLexerPreDefine.test_03(): Ctor and finalisation, missing "define" in pre-define."""
        preDefMacros= [
               '# SPAM 1\n',
               ]
        myLexer = PpLexer.PpLexer(
            'mt.h',
            CppIncludeStringIO([], [], '', {}),
            preIncFiles=[
                          io.StringIO(x) for x in preDefMacros
                          ],
            diagnostic=None,
            )
        try:
            myToks = [t for t in myLexer.ppTokens()]
            self.fail('PpLexer.ExceptionPpLexerDefine not raised.')
        except PpLexer.ExceptionPpLexerDefine:
            pass
 
    def test_04(self):
        """TestPpLexerPreDefine.test_04(): Ctor and finalisation, missing prefix and "define" in pre-define."""
        # NOTE: this does not raise an exception (neither does cpp.exe) because
        # SPAM is just seen as another identifier
        preDefMacros=[
           'SPAM 1\n',
           ]
        myLexer = PpLexer.PpLexer(
            'mt.h',
            CppIncludeStringIO([], [], '', {}),
            preIncFiles=[
                          io.StringIO(x) for x in preDefMacros
                          ],
            diagnostic=None,
            )

        myToks = [t for t in myLexer.ppTokens()]
        expToks = [
                   PpToken.PpToken('SPAM', 'identifier'),
                   PpToken.PpToken(' ', 'whitespace'),
                   PpToken.PpToken('1', 'pp-number'),
                   PpToken.PpToken('\n', 'whitespace'),
                   ]
        self.assertEqual(expToks, myToks)
        myLexer.finalise()
 
    def test_05(self):
        """TestPpLexerPreDefine.test_05(): Ctor and finalisation, missing \\n in pre-define."""
        preDefMacros=[
           '#define SPAM 1',
           ]
        myLexer = PpLexer.PpLexer(
            'mt.h',
            CppIncludeStringIO([], [], '', {}),
            preIncFiles=[
                          io.StringIO(x) for x in preDefMacros
                          ],
            diagnostic=None,
            )
        try:
            myToks = [t for t in myLexer.ppTokens()]
            self.fail('PpLexer.ExceptionPpLexerDefine not raised.')
        except PpLexer.ExceptionPpLexerPreInclude:
            pass
 
    def test_06(self):
        """TestPpLexerPreDefine.test_06(): Ctor and finalisation, empty string in pre-define."""
        preDefMacros=[
               '\n',
               ]
        myLexer = PpLexer.PpLexer(
            'mt.h',
            CppIncludeStringIO([], [], '', {}),
            preIncFiles=[
                          io.StringIO(x) for x in preDefMacros
                          ],
            diagnostic=None,
            )
        myToks = [t for t in myLexer.ppTokens()]
        expToks = [
                   PpToken.PpToken('\n', 'whitespace'),
                   ]
        self.assertEqual(expToks, myToks)
        myLexer.finalise()
 
    def test_07(self):
        """TestPpLexerPreDefine.test_07(): Ctor and finalisation with multiple predefined macros in multiple predefined files."""
        # In this case we have two predefined files each with their own macro
        myPiS = [
                 '#define SPAM(x,y) x+y\n',
                 '#define EGGS SPAM\n'
        ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 preIncFiles=[
                              io.StringIO(x) for x in myPiS
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens()]
        expToks = [
                   PpToken.PpToken('\n', 'whitespace'),
                   PpToken.PpToken('\n', 'whitespace'),
                   ]
        self.assertEqual(expToks, myToks)
        myLexer.finalise()
        # Some tests
        #print
        #print myLexer.definedMacros
        #print
        #print myLexer.fileIncludeGraphRoot
#         self.assertEqual(
#             str(myLexer.definedMacros),
#             """#define EGGS SPAM /* Unnamed Pre-include#1 Ref: 0 True */
# #define SPAM(x,y) x+y /* Unnamed Pre-include#1 Ref: 0 True */""")
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['EGGS', 'SPAM', '__DATE__', '__TIME__'],
        )
        self.assertEqual(
            str(myLexer.fileIncludeGraphRoot),
            """Unnamed Pre-include [14, 11]:  True "" ""
Unnamed Pre-include [7, 4]:  True "" ""
mt.h [0, 0]:  True "" \"\"""")

    def test_08(self):
        """TestPpLexerPreDefine.test_07(): Ctor and finalisation with multiple predefined macros in multiple predefined files (spurious newlines)."""
        # In this case we have two predefined files each with their own macro
        myPiS = [
                 '\n\n\n#define SPAM(x,y) x+y\n',
                 '\n#define EGGS SPAM\n'
        ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 preIncFiles=[
                              io.StringIO(x) for x in myPiS
                              ],
                 diagnostic=None,
                 )
        myToks = [t for t in myLexer.ppTokens()]
        expToks = [
                   PpToken.PpToken('\n\n\n', 'whitespace'),
                   PpToken.PpToken('\n', 'whitespace'),
                   PpToken.PpToken('\n', 'whitespace'),
                   PpToken.PpToken('\n', 'whitespace'),
                   ]
        self.assertEqual(expToks, myToks)
        myLexer.finalise()
        # Some tests
        #print 'myLexer.definedMacros'
        #print myLexer.definedMacros
        #print 'File Include Graph'
        #print myLexer.fileIncludeGraphRoot
#         self.assertEqual(
#             str(myLexer.definedMacros),
#             """#define EGGS SPAM /* Unnamed Pre-include#2 Ref: 0 True */
# #define SPAM(x,y) x+y /* Unnamed Pre-include#4 Ref: 0 True */""")
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['EGGS', 'SPAM', '__DATE__', '__TIME__'],
        )
        self.assertEqual(
            str(myLexer.fileIncludeGraphRoot),
            """Unnamed Pre-include [15, 11]:  True "" ""
Unnamed Pre-include [8, 4]:  True "" ""
mt.h [0, 0]:  True "" \"\"""")

class TestPpLexerNull(TestPpLexer):
    """Tests the construction of a PpLexer object and process #\\n statement."""
    def test_00(self):
        """TestPpLexerNull - null preprocessor directive."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#
""",
                    {}),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """
""")
        myLexer.finalise()

class TestPpLexerInvalidDirective(TestPpLexer):
    """Tests the construction of a PpLexer object and process #"hello"\\n statement."""
    def test_00(self):
        """TestPpLexerInvalidDirective.test_00() - invalid preprocessor directive #"hello"."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#"hello"
""",
                    {}),
                 )
        try:
            result = ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('ExceptionCppDiagnosticUndefined not raised')
        except CppDiagnostic.ExceptionCppDiagnosticUndefined:
            pass
#        self.assertEqual(result, """ABC
#""")
        #myLexer.finalise()

    def test_01(self):
        """TestPpLexerInvalidDirective.test_01() - invalid preprocessor directive #hello."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#hello
""",
                    {}),
                 )
        try:
            result = ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('ExceptionCppDiagnosticUndefined not raised')
        except CppDiagnostic.ExceptionCppDiagnosticUndefined:
            pass
#        self.assertEqual(result, """ABC
#""")
        #myLexer.finalise()

class TestPpLexerDefine(TestPpLexer):
    """Tests the construction of a PpLexer object and process #define statements."""
    def test_00(self):
        """Simple #define and expansion."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define SPAM 5
SPAM
""",
                    {}),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """
5
""")
        myLexer.finalise()

    def test_01(self):
        """Simple #define, #undef, redfine and expansion."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define SPAM 5
#undef SPAM
#define SPAM 10
SPAM
""",
                    {},
                    ),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """


10
""")
        myLexer.finalise()

    def test_fail_01(self):
        """Misspelt #define as #DefINE."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#DefINE SPAM 5
SPAM
""",
                    {},
                    ),
                 )

        try:
            result = ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('CppDiagnostic.ExceptionCppDiagnosticUndefined not raised.')
        except CppDiagnostic.ExceptionCppDiagnosticUndefined as err:
            self.assertEqual(
                str(err),
                ' identifier "# DefINE" at line=1, col=2 of file "define.h"'
            )

class TestPpLexerDefineFromStandard(TestPpLexer):
    """Tests some examples from the C standard ISO/IEC 9899:1999 (E)."""
    def test_00(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.3-4 EXAMPLE 2"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define hash_hash # ## #
#define mkstr(a) # a
#define in_between(a) mkstr(a)
#define join(c, d) in_between(c hash_hash d)
char p[] = join(x, y);
""",
                    {}),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """



char p[] =  "x ## y";
""")
        myLexer.finalise()

    def test_01(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.5-5 EXAMPLE 3"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define x 3
#define f(a) f(x * (a))
#undef x
#define x 2
#define g f
#define z z[0]
#define h g(~
#define m(a) a(w)
#define w 0,1
#define t(a) a
#define p() int
#define q(x) x
#define r(x,y) x ## y
#define str(x) # x
f(y+1) + f(f(z)) % t(t(g)(0) + t)(1);
g(x+(3,4)-w) | h 5) & m
(f)^m(m);
p() i[q()] = { q(1), r(2,3), r(4,), r(,5), r(,) };
char c[2][6] = { str(hello), str() };
""",
                    {}),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\n\n\n\n\n\n\n\n\n\n\n
f(2 * (y+1)) + f(2 * (f(2 * (z[0])))) % f(2 * (0)) + t(1);
f(2 * (2+(3,4)-0,1)) | f(2 * (~ 5)) & f(2 * (0,1))^m(0,1);
int i[] = { 1, 23, 4, 5,  };
char c[2][6] = {  "hello",  "" };
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_02_00(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.5-6 EXAMPLE 4 [0]"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define str(s) # s
#define xstr(s) str(s)
#define debug(s, t) printf("x" # s "= %d, x" # t "= %s", \\
x ## s, x ## t)
#define INCFILE(n) vers ## n // from previous #include example
#define glue(a, b) a ## b
#define xglue(a, b) glue(a, b)
#define HIGHLOW "hello"
#define LOW LOW ", world"
debug(1, 2);
""",
                    {}),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\n\n\n\n\n
printf("x"  "1" "= %d, x"  "2" "= %s", x1, x2);
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_02_01(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.5-6 EXAMPLE 4 [1]"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define str(s) # s
#define xstr(s) str(s)
#define debug(s, t) printf("x" # s "= %d, x" # t "= %s", \\
x ## s, x ## t)
#define INCFILE(n) vers ## n // from previous #include example
#define glue(a, b) a ## b
#define xglue(a, b) glue(a, b)
#define HIGHLOW "hello"
#define LOW LOW ", world"
fputs(str(strncmp("abc\\0d", "abc", '\\4') // this goes away
== 0) str(: @\\n), s);
""",
                    {}),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        # cpp:
        # fputs("strncmp(\"abc\\0d\", \"abc\", '\\4') == 0" ": @\\n", s);
#        expectedResult = """\n\n\n\n\n\n\n\n
#fputs( "strncmp(\\"abc\\u0000d\\", \\"abc\\", '\\u0004') == 0"  ": @\n", s);
#"""
        expectedResult = """\n\n\n\n\n\n\n
fputs( "strncmp(\\"abc\\0d\\", \\"abc\\", \'\\4\') == 0"  ": @\\n", s);
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_02_02(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.5-6 EXAMPLE 4 [2]"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define str(s) # s
#define xstr(s) str(s)
#define debug(s, t) printf("x" # s "= %d, x" # t "= %s", \\
x ## s, x ## t)
#define INCFILE(n) vers ## n // from previous #include example
#define glue(a, b) a ## b
#define xglue(a, b) glue(a, b)
#define HIGHLOW "hello"
#define LOW LOW ", world"
#include xstr(INCFILE(2).h)
""",
                    {
                        "vers2.h" : """CONTENTS_OF_VERS2.H
""",
                    }
                    ),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\n\n\n\n\n
CONTENTS_OF_VERS2.H

"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_02_03(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.5-6 EXAMPLE 4 [3]"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define str(s) # s
#define xstr(s) str(s)
#define debug(s, t) printf("x" # s "= %d, x" # t "= %s", \\
x ## s, x ## t)
#define INCFILE(n) vers ## n // from previous #include example
#define glue(a, b) a ## b
#define xglue(a, b) glue(a, b)
#define HIGHLOW "hello"
#define LOW LOW ", world"
glue(HIGH, LOW);
xglue(HIGH, LOW)
""",
                    {}),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\n\n\n\n\n
"hello";
"hello" ", world"
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_02(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.5-6 EXAMPLE 4"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define str(s) # s
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
""",
                    {
                        "vers2.h" : """CONTENTS_OF_VERS2.H
""",
                    }
                    ),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        #
        expectedResult = """\n\n\n\n\n\n\n
printf("x"  "1" "= %d, x"  "2" "= %s", x1, x2);
fputs( "strncmp(\\"abc\\0d\\", \\"abc\\", \'\\4\') == 0"  ": @\\n", s);
CONTENTS_OF_VERS2.H

"hello";
"hello" ", world"
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot

    def test_03(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.5-7 EXAMPLE 5"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define t(x,y,z) x ## y ## z
int j[] = { t(1,2,3), t(,4,5), t(6,,7), t(8,9,),
t(10,,), t(,11,), t(,,12), t(,,) };
""",
                    {}),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """
int j[] = { 123, 45, 67, 89,
10, 11, 12,  };
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_04(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.5-8 EXAMPLE 6"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define OBJ_LIKE (1-1)
#define OBJ_LIKE /* white space */ (1-1) /* other */
#define FUNC_LIKE(a) ( a )
#define FUNC_LIKE( a )( /* note the white space */ \
a /* other stuff on this line */ )
""",
                    {}),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_05(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.5-9 EXAMPLE 7 "Finally, to show the variable argument list macro facilities:" """
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define debug(...) fprintf(stderr, __VA_ARGS__)
#define showlist(...) puts(#__VA_ARGS__)
#define report(test, ...) ((test)?puts(#test):\
printf(__VA_ARGS__))
debug("Flag");
debug("X = %d\n", x);
showlist(The first, second, and third items.);
report(x>y, "x is %d but y is %d", x, y);
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\nfprintf(stderr, "Flag");
fprintf(stderr, "X = %d\n",x);
puts("The first,second,and third items.");
((x>y)?puts("x>y"):printf("x is %d but y is %d",x,y));\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_05_00(self):
        """ISO/IEC 9899:1999 (E) 6.10.3.5-9 EXAMPLE 7 [00]"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define showlist(...) puts(#__VA_ARGS__)
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = '\n'
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

class TestIncludeHandlerBase(TestPpLexer):
    """ABC for testing #include processing."""
    def setUp(self):
        # Translation unit contents
        initialTuContents = """#include "spam.h"
"""
        self._incSim = CppIncludeStringIO(
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

class TestIncludeHandler_Simple(TestIncludeHandlerBase):
    """Tests #include statements. Note: This is similar to stuff
    in TestIncludeHandler.py"""
    def __init__(self, *args):
        self._pathsUsr = []
        self._pathsSys = []
        self._initialTuContents = """#include "spam.h"
"""
        self._incFileMap = {
            os.path.join('src', 'spam.h') : """\"Content of:\" CP, spam.h
""",
        }
        super(TestIncludeHandler_Simple, self).__init__(*args)

    def testSimpleInclude(self):
        """TestIncludeHandler_Simple.testSimpleInclude(): Tests a simple #include statement from the CP."""
        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
        #for aTok in myLexer.ppTokens():
        #    print 'HI', aTok, myLexer.fileStack
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """"Content of:" CP, spam.h\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        self.assertEqual([], myLexer.fileStack)
        myLexer.finalise()

class TestIncludeHandler_NotFound(TestIncludeHandlerBase):
    """Tests #include statements where the file can not be found."""
    def __init__(self, *args):
        self._pathsUsr = []
        self._pathsSys = []
        self._initialTuContents = """#include "eggs.h"
"""
        self._incFileMap = {
            os.path.join('src', 'spam.h') : """\"Content of:\" CP, spam.h
""",
        }
        super(TestIncludeHandler_NotFound, self).__init__(*args)

    def testSimpleIncludeFails(self):
        """TestIncludeHandler_NotFound.testSimpleIncludeFails(): Tests a simple #include statement from the CP that does not resolve."""
        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
        #for aTok in myLexer.ppTokens():
        #    print 'HI', aTok, myLexer.fileStack
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = '\n'
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        self.assertEqual([], myLexer.fileStack)
        myLexer.finalise()

class TestIncludeHandler_IllFormed(TestIncludeHandlerBase):
    """Tests #include statements where the file can not be found."""
    def __init__(self, *args):
        self._pathsUsr = []
        self._pathsSys = []
        self._initialTuContents = """#include SPAM.H
"""
        self._incFileMap = {
            os.path.join('src', 'spam.h') : """\"Content of:\" CP, spam.h
""",
        }
        super(TestIncludeHandler_IllFormed, self).__init__(*args)

    def testSimpleIncludeFails(self):
        """TestIncludeHandler_IllFormed.testSimpleIncludeFails(): Tests a ill-formed #include statement."""
        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
        #for aTok in myLexer.ppTokens():
        #    print 'HI', aTok, myLexer.fileStack
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = '\n'
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        self.assertEqual([], myLexer.fileStack)
        myLexer.finalise()

class TestIncludeHandler_UsrSys(TestIncludeHandlerBase):
    """Tests #include statements. Note: This is similar to stuff
    in TestIncludeHandler.py"""
    def __init__(self, *args):
        self._pathsUsr = [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ]
        self._pathsSys = [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ]
        self._initialTuContents = """#include "spam.h"
#include "inc/spam.h"
#include <spam.h>
#include <inc/spam.h>
"""
        self._incFileMap = {
                os.path.join('usr', 'spam.h') : """Content of: user, spam.h
""",
                os.path.join('usr', 'inc', 'spam.h') : """Content of: user, include, spam.h
""",
                os.path.join('sys', 'spam.h') : """Content of: system, spam.h
""",
                os.path.join('sys', 'inc', 'spam.h') : """Content of: system, include, spam.h
""",
            }
        super(TestIncludeHandler_UsrSys, self).__init__(*args)

    def testSimpleInclude(self):
        """TestIncludeHandler_CpUsrSys.testSimpleInclude(): Tests multiple #include statements that resolve to usr/sys."""
        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """Content of: user, spam.h

Content of: user, include, spam.h

Content of: system, spam.h

Content of: system, include, spam.h

"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
#        print('FileIncludeGraph:')
#        print(myLexer.fileIncludeGraphRoot)
        expGraph = """src/spam.c [0, 0]:  True "" ""
000001: #include usr\spam.h
  usr\spam.h [12, 8]:  True "" "['"spam.h"', 'CP=None', 'usr=usr']"
000002: #include usr\inc\spam.h
  usr\inc\spam.h [15, 10]:  True "" "['"inc/spam.h"', 'CP=None', 'usr=usr']"
000003: #include sys\spam.h
  sys\spam.h [12, 8]:  True "" "['<spam.h>', 'sys=sys']"
000004: #include sys\inc\spam.h
  sys\inc\spam.h [15, 10]:  True "" "['<inc/spam.h>', 'sys=sys']\"""".replace('\\', os.sep)
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

class TestIncludeHandler_UsrSys_Conditional(TestIncludeHandlerBase):
    """Tests #include statements. Note: This is similar to stuff
    in TestIncludeHandler.py"""
    def __init__(self, *args):
        self._pathsUsr = [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ]
        self._pathsSys = [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ]
        self._initialTuContents = """#if INC == 0
#include "spam.h"
#elif INC == 1
#include "inc/spam.h"
#elif INC == 2
#include <spam.h>
#elif INC == 3
#include <inc/spam.h>
#endif
"""
        self._incFileMap = {
                os.path.join('usr', 'spam.h') : """Content of: user, spam.h
""",
                os.path.join('usr', 'inc', 'spam.h') : """Content of: user, include, spam.h
""",
                os.path.join('sys', 'spam.h') : """Content of: system, spam.h
""",
                os.path.join('sys', 'inc', 'spam.h') : """Content of: system, include, spam.h
""",
            }
        super(TestIncludeHandler_UsrSys_Conditional, self).__init__(*args)

    def testSimpleInclude_00(self):
        """TestIncludeHandler_UsrSys_Conditional.testSimpleInclude_00(): Tests conditional #include statements."""
        # Note: Using line splicing in the predef
        preDefMacros=[
                      """#define INC \\
0
""",
                      ]
        myLexer = PpLexer.PpLexer(
                                  'src/spam.c',
                                  self._incSim,
                                  preIncFiles=[
                                               io.StringIO(x) for x in preDefMacros
                                               ],
                                  )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nContent of: user, spam.h\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        expGraph = """Unnamed Pre-include [7, 4]:  True "" ""
src/spam.c [0, 0]:  True "" ""
000002: #include usr\spam.h
  usr\spam.h [12, 8]:  True "INC == 0" "['"spam.h"', 'CP=None', 'usr=usr']\"""".replace('\\', os.sep)
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

    def testSimpleInclude_01(self):
        """TestIncludeHandler_UsrSys_Conditional.testSimpleInclude_01(): Tests conditional #include statements."""
        # Note using comments in the predef
        preDefMacros=[
                      """#define INC /* comment */ 1
""",
                      ]
        myLexer = PpLexer.PpLexer(
                                  'src/spam.c',
                                  self._incSim,
                                  preIncFiles=[
                                               io.StringIO(x) for x in preDefMacros
                                               ],
                                  )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nContent of: user, include, spam.h\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        expGraph = """Unnamed Pre-include [9, 4]:  True "" ""
src/spam.c [0, 0]:  True "" ""
000004: #include usr\inc\spam.h
  usr\inc\spam.h [15, 10]:  True "(!(INC == 0) && INC == 1)" "['"inc/spam.h"', 'CP=None', 'usr=usr']\"""".replace('\\', os.sep)
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

    def testSimpleInclude_02(self):
        """TestIncludeHandler_UsrSys_Conditional.testSimpleInclude_02(): Tests conditional #include statements."""
        # Note using comments and line splicing in the predef
        preDefMacros=[
                      """#define /* C comment */ INC \\
 2
// C++ comment
""",
                      ]
        myLexer = PpLexer.PpLexer(
                                  'src/spam.c',
                                  self._incSim,
                                  preIncFiles=[
                                               io.StringIO(x) for x in preDefMacros
                                               ],
                                  )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n \n\nContent of: system, spam.h\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        expGraph = """Unnamed Pre-include [11, 4]:  True "" ""
src/spam.c [0, 0]:  True "" ""
000006: #include sys\spam.h
  sys\spam.h [12, 8]:  True "(!(INC == 0) && !(INC == 1) && INC == 2)" "['<spam.h>', 'sys=sys']\"""".replace('\\', os.sep)
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

    def testSimpleInclude_03(self):
        """TestIncludeHandler_UsrSys_Conditional.testSimpleInclude_03(): Tests conditional #include statements."""
        preDefMacros=[
                      """#define INC 3
""",
                      ]
        myLexer = PpLexer.PpLexer(
                                  'src/spam.c',
                                  self._incSim,
                                  preIncFiles=[
                                               io.StringIO(x) for x in preDefMacros
                                               ],
                                  )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nContent of: system, include, spam.h\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        expGraph = """Unnamed Pre-include [7, 4]:  True "" ""
src/spam.c [0, 0]:  True "" ""
000008: #include sys\inc\spam.h
  sys\inc\spam.h [15, 10]:  True "(!(INC == 0) && !(INC == 1) && !(INC == 2) && INC == 3)" "['<inc/spam.h>', 'sys=sys']\"""".replace('\\', os.sep)
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

class TestIncludeHandler_PreInclude_Includes(TestIncludeHandlerBase):
    """Tests when a pre-include includes in TestIncludeHandler.py"""
    def __init__(self, *args):
        self._pathsUsr = [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ]
        self._pathsSys = [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ]
        self._initialTuContents = """#include "spam.h"
#include "inc/spam.h"
#include <spam.h>
#include <inc/spam.h>
"""
        self._incFileMap = {
                os.path.join('usr', 'spam.h') : """Content of: user, spam.h
""",
                os.path.join('usr', 'inc', 'spam.h') : """Content of: user, include, spam.h
""",
                os.path.join('sys', 'spam.h') : """Content of: system, spam.h
""",
                os.path.join('sys', 'inc', 'spam.h') : """Content of: system, include, spam.h
""",
            }
        super(TestIncludeHandler_PreInclude_Includes, self).__init__(*args)

    def testPreInclude_00(self):
        """TestIncludeHandler_PreInclude_Includes.testPreInclude_00(): Failure StringIO tries to include file."""
        # TODO: Test with HcharString.
        preIncludeS=[
                      """
#include "somefile.h"
""",
                      ]
        myLexer = PpLexer.PpLexer(
                                  'src/spam.c',
                                  self._incSim,
                                  preIncFiles=[
                                               io.StringIO(x) for x in preIncludeS
                                               ],
                                  )
        try:
            result = ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('Failed to raise ExceptionPpLexerPreIncludeIncNoCp')
        except PpLexer.ExceptionPpLexerPreIncludeIncNoCp:
            pass
        return
        expectedResult = """\n\nContent of: user, spam.h\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        expGraph = """Unnamed Pre-include [7, 4]:  True "" ""
src/spam.c [0, 0]:  True "" ""
000002: #include usr\spam.h
        usr\spam.h [12, 8]:  True "INC == 0" "['"spam.h"', 'CP=None', 'usr=usr']\""""
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

class TestIncludeHandlerMacroBase(TestIncludeHandlerBase):
    """Tests #include statements that have macros that expand to the
    file identifier.
    in TestIncludeHandler.py"""
    def __init__(self, *args):
        self._pathsUsr = [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ]
        self._pathsSys = [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ]
        # Child classes inplement this
        #self._initialTuContents = ...
        self._incFileMap = {
                os.path.join('usr', 'spam.h') : """Content of: user, spam.h
""",
                os.path.join('usr', 'inc', 'spam.h') : """Content of: user, include, spam.h
""",
                os.path.join('sys', 'spam.h') : """Content of: system, spam.h
""",
                os.path.join('sys', 'inc', 'spam.h') : """Content of: system, include, spam.h
""",
            }
        super(TestIncludeHandlerMacroBase, self).__init__(*args)

class TestIncludeHandlerMacro_Simple(TestIncludeHandlerMacroBase):
    """Tests #include statements. Note: This is similar to stuff
    in TestIncludeHandler.py"""
    def __init__(self, *args):
        self._initialTuContents = """#define FILE "spam.h"
#include FILE
"""
        super(TestIncludeHandlerMacro_Simple, self).__init__(*args)

    def testSimpleInclude(self):
        """TestIncludeHandlerMacro_Simple.testSimpleInclude(): Tests multiple #include statements that resolve to usr/sys when expanded."""
        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """
Content of: user, spam.h

"""
        #print '  Actual:\n%s' % result
        #print 'Expected:\n%s' % expectedResult
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

class TestIncludeHandlerMacro_SimpleUndef(TestIncludeHandlerMacroBase):
    """Tests #include statements. Note: This is similar to stuff
    in TestIncludeHandler.py"""
    def __init__(self, *args):
        self._initialTuContents = """#define FILE "spam.h"
#include FILE
#undef FILE
#define FILE "inc/spam.h"
#include FILE
"""
        super(TestIncludeHandlerMacro_SimpleUndef, self).__init__(*args)

    def testSimpleInclude(self):
        """TestIncludeHandlerMacro_SimpleUndef.testSimpleInclude(): Tests multiple #include statements that resolve to usr/sys when expanded."""
        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """
Content of: user, spam.h



Content of: user, include, spam.h

"""
        #print '  Actual:\n%s' % result
        #print 'Expected:\n%s' % expectedResult
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

class TestIncludeHandler_UsrSys_MacroObject(TestIncludeHandlerMacroBase):
    """Tests #include statements using object-like macros. Note: This is similar to stuff
    in TestIncludeHandler.py"""
    def __init__(self, *args):
        self._initialTuContents = """#define FILE "spam.h"
#include FILE
#undef FILE
#define FILE "inc/spam.h"
#include FILE
#undef FILE
#define FILE <spam.h>
#include FILE
#undef FILE
#define FILE <inc/spam.h>
#include FILE
"""
        super(TestIncludeHandler_UsrSys_MacroObject, self).__init__(*args)

    def testSimpleInclude(self):
        """TestIncludeHandler_UsrSys_MacroObject.testSimpleInclude(): Tests multiple #include statements with object-like macros."""
        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """
Content of: user, spam.h
\n\n
Content of: user, include, spam.h
\n\n
Content of: system, spam.h
\n\n
Content of: system, include, spam.h
\n"""
        #print '  Actual:\n%s' % result
        #print 'Expected:\n%s' % expectedResult
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

class TestIncludeHandler_UsrSys_MacroFunction(TestIncludeHandlerMacroBase):
    """Tests #include statements. Note: This is similar to stuff
    in TestIncludeHandler.py"""
    def __init__(self, *args):
        self._initialTuContents = """#define FILE(f) # f
#include FILE(spam.h)
#include FILE(inc/spam.h)
#undef FILE
#define FILE(f) <f>
#include FILE(spam.h)
#include FILE(inc/spam.h)
"""
        super(TestIncludeHandler_UsrSys_MacroFunction, self).__init__(*args)

    def testSimpleInclude(self):
        """TestIncludeHandler_UsrSys_MacroFunction.testSimpleInclude(): Tests multiple #include statements with function-like macros."""
        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """
Content of: user, spam.h

Content of: user, include, spam.h
\n\n
Content of: system, spam.h

Content of: system, include, spam.h
\n"""
        #print '  Actual:\n%s' % result
        #print 'Expected:\n%s' % expectedResult
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

class TestIncludeHandler_UsrSys_MultipleDepth(TestIncludeHandlerBase):
    """Tests #include statements that are multiple depth."""
    def __init__(self, *args):
        self._pathsUsr = [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ]
        self._pathsSys = [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ]
        # The next two arguments mean that:
        # src/spam.c
        #   |-> usr/spam.h
        #       |-> usr/inc/spam.h
        #           |-> sys/spam.h
        #               |-> sys/inc/spam.h
        #                   |-> "Content of: system, include, spam.h"
        # Initial TU:
        self._initialTuContents = """#include "spam.h"
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
        super(TestIncludeHandler_UsrSys_MultipleDepth, self).__init__(*args)

    def testSimpleInclude(self):
        """TestIncludeHandler_UsrSys_MultipleDepth.testSimpleInclude(): Tests multiple depth #include statements that resolve to usr/sys."""
        #print
        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """Content of: system, include, spam.h\n\n\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        expGraph = """src/spam.c [0, 0]:  True "" ""
000001: #include usr\spam.h
  usr\spam.h [0, 0]:  True "" "['"spam.h"', 'CP=None', 'usr=usr']"
  000001: #include usr\inc\spam.h
    usr\inc\spam.h [0, 0]:  True "" "['"inc/spam.h"', 'CP=usr']"
    000001: #include sys\spam.h
      sys\spam.h [0, 0]:  True "" "['<spam.h>', 'sys=sys']"
      000001: #include sys\inc\spam.h
        sys\inc\spam.h [15, 10]:  True "" "['<inc/spam.h>', 'sys=sys']\"""".replace('\\', os.sep)
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

    def testSimpleIncludeTwice(self):
        """TestIncludeHandler_UsrSys_MultipleDepth.testSimpleInclude(): Tests multiple depth #include statements that resolve to usr/sys invoked twice."""
        expectedResult = """Content of: system, include, spam.h\n\n\n\n\n"""
        expGraph = """src/spam.c [0, 0]:  True "" ""
000001: #include usr/spam.h
  usr/spam.h [0, 0]:  True "" "['"spam.h"', 'CP=None', 'usr=usr']"
  000001: #include usr/inc/spam.h
    usr/inc/spam.h [0, 0]:  True "" "['"inc/spam.h"', 'CP=usr']"
    000001: #include sys/spam.h
      sys/spam.h [0, 0]:  True "" "['<spam.h>', 'sys=sys']"
      000001: #include sys/inc/spam.h
        sys/inc/spam.h [15, 10]:  True "" "['<inc/spam.h>', 'sys=sys']\"""".replace('\\', os.sep)
        myLexer = PpLexer.PpLexer('src/spam.c', self._incSim)
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
#        print('FileIncludeGraph:')
#        print(myLexer.fileIncludeGraphRoot)
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))
        # Do it again, this should raise
        try:
            result = ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('Failed to raise ExceptionPpLexerAlreadyGenerating')
        except PpLexer.ExceptionPpLexerAlreadyGenerating:
            pass

class TestIncludeHandler_HeaderGuard(TestIncludeHandlerBase):
    """Tests #include statements where the same file is included that has header guards."""
    def __init__(self, *args):
        self._pathsUsr = []
        self._pathsSys = []
        self._initialTuContents = """#include "spam.h"
#include "spam.h"
"""
        self._incFileMap = {
            os.path.join('spam.h') : """#ifndef __SPAM_H__
#define __SPAM_H__
ONCE
#endif
""",
        }
        super(TestIncludeHandler_HeaderGuard, self).__init__(*args)

    def test_00(self):
        """TestIncludeHandler_HeaderGuard.test_00(): Tests a two #include statements with header guards."""
        myLexer = PpLexer.PpLexer('spam.c', self._incSim)
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nONCE\n\n\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        self.assertEqual([], myLexer.fileStack)
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        expGraph = """spam.c [0, 0]:  True "" ""
000001: #include spam.h
  spam.h [7, 4]:  True "" "['"spam.h"', 'CP=']"
000002: #include spam.h
  spam.h [2, 0]:  True "" "['"spam.h"', 'CP=']\""""
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

class TestPpLexerConditional_LowLevel(TestPpLexer):
    """Tests PpLexer low level funcitonality for conditional source code handling."""
    def test_00(self):
        """TestPpLexerConditional_LowLevel.test_00(): test _retDefinedSubstitution()"""
        preDefMacros=[
            '#define SPAM\n',
            '#define EGGS\n',
            ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """\n""",
                    {}
                    ),
                 preIncFiles=[io.StringIO(x) for x in preDefMacros],
                 diagnostic=None,
                 )
        myTestS = (
            ('defined SPAM\n', self.stringToTokens(' 1\n')),
            ('defined EGGS\n', self.stringToTokens(' 1\n')),
            ('defined NOWT\n', self.stringToTokens(' 0\n')),
            ('!defined SPAM\n', self.stringToTokens(' 0\n')),
            ('!defined EGGS\n', self.stringToTokens(' 0\n')),
            ('!defined NOWT\n', self.stringToTokens(' 1\n')),
            ('   ! defined SPAM\n',
                [
                    PpToken.PpToken('   ',         'whitespace'),
                    PpToken.PpToken(' ',           'whitespace'),
                    PpToken.PpToken(' ',           'whitespace'),
                    PpToken.PpToken('0',           'pp-number'),
                    PpToken.PpToken('\n',          'whitespace'),
                ],
            ),
            ('(defined(SPAM))\n', self.stringToTokens('((1))\n')),
            ('!(defined(SPAM))\n', self.stringToTokens('((0))\n')),
            ('(!defined(SPAM))\n', self.stringToTokens('((0))\n')),
            ('(((defined(((SPAM))))))\n', self.stringToTokens('((((((1))))))\n')),
            )
        # Need to provoke ppTokens() to read the pre-includes and the ITU
        # that sets the macro envorinment up
        myToks = [tok for tok in myLexer.ppTokens()]
        #print
        for aStr, expectedTokS in myTestS:
            #print 'TRACE TestPpLexerConditional_LowLevel.test_00(): %s' % aStr
            myCpp = PpTokeniser.PpTokeniser(
                theFileObj=io.StringIO(aStr)
                )
            repTokS, rawTokS = myLexer._retDefinedSubstitution(myCpp.next())
            self._printDiff(repTokS, expectedTokS)
            self.assertEqual(repTokS, expectedTokS)
            self.assertEqual(self.stringToTokens(aStr), rawTokS)
            #print 'repTokS:', repTokS
            #print 'rawTokS:', rawTokS
            #print
        #myLexer.finalise()

class TestPpLexerConditional(TestPpLexer):
    """Tests PpLexer with conditional source code."""
    def test_00(self):
        """TestPpLexerConditional.test_00(): Simple #if 1"""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 1
PASS
#else
FAIL
#endif
""",
                    {}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        #print
        #print str(myLexer.condCompGraph)
        self.assertEqual("""#if 1 /* True "mt.h" 1 0 */
#else /* False "mt.h" 3 9 */
#endif /* True "mt.h" 5 12 */""", str(myLexer.condCompGraph))

    def test_01(self):
        """TestPpLexerConditional.test_01(): Simple #if 0"""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 0
PASS
#else
FAIL
#endif
""",
                    {}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\nFAIL\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        #print
        #print str(myLexer.condCompGraph)
        self.assertEqual("""#if 0 /* False "mt.h" 1 0 */
#else /* True "mt.h" 3 3 */
#endif /* True "mt.h" 5 12 */""", str(myLexer.condCompGraph))

    def test_02(self):
        """TestPpLexerConditional.test_02(): Simple #if SPAM when SPAM is defined as 1"""
        preDefMacros = ['#define SPAM 1\n',]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if SPAM
PASS
#else
FAIL
#endif
""",
                    {}
                    ),
                preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_03(self):
        """TestPpLexerConditional.test_03(): Simple #if SPAM when SPAM is defined as 0"""
        preDefMacros = ['#define SPAM 0\n',]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if SPAM
PASS
#else
FAIL
#endif
""",
                    {}
                    ),
                preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nFAIL\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_04(self):
        """TestPpLexerConditional.test_04(): #if SPAM #elif EGGS when SPAM 0, EGGS 1"""
        preDefMacros = [
            '#define SPAM 0\n',
            '#define EGGS 1\n',
            ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if SPAM
FAIL
#elif EGGS
PASS
#else
FAIL
#endif
""",
                    {}
                    ),
                    preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_05(self):
        """TestPpLexerConditional.test_05(): #if SPAM < EGGS when SPAM 0, EGGS 1"""
        preDefMacros = [
                    '#define SPAM 0\n',
                    '#define EGGS 1\n',
                    ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if SPAM < EGGS
PASS
#else
FAIL
#endif
""",
                    {}
                    ),
                preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_06(self):
        """TestPpLexerConditional.test_06(): compare SPAM and EGGS when SPAM 1, EGGS 2"""
        preDefMacros = [
            '#define SPAM 1\n',
            '#define EGGS 2\n',
            ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if SPAM < EGGS
PASS
#else
FAIL
#endif

#if SPAM > EGGS
FAIL
#else
PASS
#endif

#if SPAM == EGGS
FAIL
#else
PASS
#endif

#if SPAM >= EGGS
FAIL
#else
PASS
#endif

#if SPAM <= EGGS
PASS
#else
FAIL
#endif

#if SPAM + EGGS == 3
PASS
#else
FAIL
#endif
""",
                    {}
                    ),
                preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\nPASS\n\n\nPASS\n\n\nPASS\n\n\nPASS\n\n\nPASS\n\n\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_07_00(self):
        """TestPpLexerConditional.test_07_00(): #ifdef and #else with SPAM defined."""
        preDefMacros = [
            '#define SPAM\n',
            ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#ifdef SPAM
PASS
#else
FAIL
#endif

#ifdef EGGS
FAIL
#else
PASS
#endif
""",
                    {}
                    ),
                preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nPASS\n\n\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_07_01(self):
        """TestPpLexerConditional.test_07_01(): #ifdef and #ifndef with SPAM defined."""
        preDefMacros = [
            '#define SPAM\n',
            ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#ifdef SPAM
PASS
#else
FAIL
#endif

#ifndef EGGS
PASS
#else
FAIL
#endif

#ifndef SPAM
FAIL
#else
PASS
#endif

#ifdef EGGS
FAIL
#else
PASS
#endif
""",
                    {}
                    ),
                preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nPASS\n\n\nPASS\n\n\nPASS\n\n\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_08(self):
        """TestPpLexerConditional.test_08(): #if defined SPAM."""
        preDefMacros = [
            '#define SPAM\n',
            ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if defined SPAM
PASS
#else
FAIL
#endif
""",
                    {}
                    ),
                preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_09(self):
        """TestPpLexerConditional.test_09(): #if !defined SPAM."""
        preDefMacros = [
            '#define SPAM\n',
            ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if !defined SPAM
FAIL
#else
PASS
#endif
""",
                    {}
                    ),
                preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_10(self):
        """TestPpLexerConditional.test_10(): #if !defined NOWT."""
        preDefMacros = [
            '#define SPAM\n',
            ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if !defined NOWT
PASS
#else
FAIL
#endif
""",
                    {}
                    ),
                preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_11(self):
        """TestPpLexerConditional.test_11(): #if ((defined (SPAM)))."""
        preDefMacros = [
            '#define SPAM\n',
            ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if ((defined (SPAM)))
PASS
#else
FAIL
#endif
""",
                    {}
                    ),
                preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_12(self):
        """TestPpLexerConditional.test_12(): #if ((defined (SPAM))) && (!defined NOWT)."""
        preDefMacros = [
            '#define SPAM\n',
            ]
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if ((defined (SPAM))) && (!defined NOWT)
PASS
#else
FAIL
#endif
""",
                    {}
                    ),
                preIncFiles=[io.StringIO(x) for x in preDefMacros],
                )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_13(self):
        """TestPpLexerConditional.test_13(): #if 1, #elif 0, #else."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 1
PASS
#elif 0
FAIL_0
#else
FAIL_1
#endif
""",
                    {}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
    
    def test_14_00(self):
        """TestPpLexerConditional.test_14_00(): #if/#elif/#else with spurious indentation."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """           #if 0
FAIL
     #else
PASS
    #endif

""",
                    {}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """           \nPASS\n    \n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
    
    def test_14_01(self):
        """TestPpLexerConditional.test_14_01(): #if/#elif/#else with spurious indentation."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define ONE 1
           #if (ONE + 1) < 2
FAIL
   #elif (ONE + 1) > 2
FAIL
     #else
PASS
    #endif
""",
                    {}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\nPASS\n    \n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
            
class TestPpLexerConditionalProblems(TestPpLexer):
    """Tests PpLexer with conditional source code with problems."""
    def test_00(self):
        """TestPpLexerConditionalProblems.test_00(): Raises on #if defned NOT_DEFINED"""
        #print
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if defned NOT_DEFINED
#endif
""",
                    {}
                    ),
                 )
        try:
            result = ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('ExceptionCppDiagnosticUndefined not raised')
        except CppDiagnostic.ExceptionCppDiagnosticUndefined:
            self.assertTrue(True)
            
    def test_00_00(self):
        """TestPpLexerConditionalProblems.test_00_00(): No raise on #if defned NOT_DEFINED with PreprocessDiagnosticKeepGoing()"""
        #print
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if defned NOT_DEFINED
#endif
""",
                    {}
                    ),
                 diagnostic=CppDiagnostic.PreprocessDiagnosticKeepGoing()
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
            
    def test_01(self):
        """TestPpLexerConditionalProblems.test_01(): Raises on #if 1 2"""
        #print
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 1 2
#endif
""",
                    {}
                    ),
                 )
        try:
            result = ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('ExceptionCppDiagnosticUndefined not raised')
        except CppDiagnostic.ExceptionCppDiagnosticUndefined:
            self.assertTrue(True)
            
    def test_01_00(self):
        """TestPpLexerConditionalProblems.test_01_00(): Raises on #if 1 2 with PreprocessDiagnosticKeepGoing()"""
        #print
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 1 2
#endif
""",
                    {}
                    ),
                 diagnostic=CppDiagnostic.PreprocessDiagnosticKeepGoing()
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
#        try:
#            result = ''.join([t.t for t in myLexer.ppTokens()])
#            self.fail('CppCond.ExceptionCppCond not raised')
#        except CppCond.ExceptionCppCond:
#            self.assertTrue(True)
                        
    def test_02(self):
        """TestPpLexerConditionalProblems.test_02(): Raises on #elif defned NOT_DEFINED"""
        #print
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 0
#elif defned NOT_DEFINED
#endif
""",
                    {}
                    ),
                 )
        try:
            result = ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('ExceptionCppDiagnosticUndefined not raised')
        except CppDiagnostic.ExceptionCppDiagnosticUndefined:
            self.assertTrue(True)
            
    def test_02_00(self):
        """TestPpLexerConditionalProblems.test_02_00(): Raises on #elif defned NOT_DEFINED with PreprocessDiagnosticKeepGoing()"""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 0
#elif defned NOT_DEFINED
#endif
""",
                    {}
                    ),
                 diagnostic=CppDiagnostic.PreprocessDiagnosticKeepGoing()
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        #print
        #print 'Result:'
        #print result
        self.assertEquals('\n', result)
            
    def test_03(self):
        """TestPpLexerConditionalProblems.test_03(): Raises on #elif 1 2"""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 0
#elif 1 2
#endif
""",
                    {}
                    ),
                 )
        try:
            result = ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('ExceptionCppDiagnosticUndefined not raised')
        except CppDiagnostic.ExceptionCppDiagnosticUndefined:
            self.assertTrue(True)
            
    def test_03_00(self):
        """TestPpLexerConditionalProblems.test_03_00(): Raises on #elif 1 2 with PreprocessDiagnosticKeepGoing()"""
        #print
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 0
#elif 1 2
#endif
""",
                    {}
                    ),
                 diagnostic=CppDiagnostic.PreprocessDiagnosticKeepGoing()
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEquals('\n', result)
                        
class TestPpLexerConditionalWithState(TestPpLexer):
    """Tests PpLexer with conditional source code."""
    def test_00(self):
        """TestPpLexerConditionalWithState.test_00(): Simple #if 1 testing conditional state for each token."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 1
PASS
#elif 0
FAIL_0
#else
FAIL_1
#endif
""",
                    {}
                    ),
                 )
        tokAndState = []
        #print
#===============================================================================
#        myGen = myLexer.ppTokensAndCondState()
#        for aResult in myGen:
#            tokAndState.append(aResult)
#            print 'Result:', aResult
#            print 'State: ', myLexer.condState
#===============================================================================
        myGen = myLexer.ppTokens(condLevel=1)
        for aResult in myGen:
            tokAndState.append((aResult, myLexer.condState))
            #print 'Result:', aResult
            #print 'State: ', myLexer.condState
        #print 'tokAndState'
        #print tokAndState
        expectedResult = [
            (
                PpToken.PpToken('\n',       'whitespace'),
                (True, '1'),
                ),
            (
                PpToken.PpToken('PASS',     'identifier'),
                (True, '1'),
                ),
            (
                PpToken.PpToken('\n',       'whitespace'),
                (True, '1'),
                ),
            (
                PpToken.PpToken('\n',       'whitespace'),
                (False, '(!(1) && 0)'),
                ),
            (
                PpToken.PpToken('FAIL_0',     'identifier'),
                (False, '(!(1) && 0)'),
                ),
            (
                PpToken.PpToken('\n',       'whitespace'),
                (False, '(!(1) && 0)'),
                ),
            (
                PpToken.PpToken('\n',       'whitespace'),
                (False, '(!(1) && !(0))'),
                ),
            (
                PpToken.PpToken('FAIL_1',     'identifier'),
                (False, '(!(1) && !(0))'),
                ),
            (
                PpToken.PpToken('\n',       'whitespace'),
                (False, '(!(1) && !(0))'),
                ),
            (
                PpToken.PpToken('\n',       'whitespace'),
                (True, ''),
                ),
            ]
        self.assertEqual(tokAndState, expectedResult)
        condBool = [t[0].isCond for t in tokAndState]
        #print 'condBool:', condBool
        self.assertEqual(
            condBool,
            [
                False, False, False, True, True, True, True, True, True, False,
                ],
            )
        myLexer.finalise()

    def test_01(self):
        """TestPpLexerConditionalWithState.test_01(): Simple #if with conditional #defines, macro environment is"""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 1
#define ONE_
#elif 0
#define ELIF_0
#else
#define ELSE_
#endif
""",
                    {}
                    ),
                 )
        tokAndState = []
        allTokS = []
        nonCondTokS = []
        myGen = myLexer.ppTokens(condLevel=1)
        for aResult in myGen:
            tokAndState.append((aResult.t, myLexer.condState))
            allTokS.append(aResult.t)
            if not aResult.isCond:
                nonCondTokS.append(aResult.t)
            #print 'Result:', aResult
            #print 'State: ', myLexer.condState
        myLexer.finalise()
        #print 'tokAndState:'
        #print tokAndState
        #pprint.pprint(tokAndState)
        #print 'allTokS:'
        #print ''.join(allTokS)
        #print 'nonCondTokS:'
        #print ''.join(nonCondTokS)
        # Check only one macro defined
#         self.assertEqual(myLexer.definedMacros, '#define ONE_ /* mt.h#2 Ref: 0 True */')
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['ONE_', '__DATE__', '__TIME__'],
        )
        expResult = [
                     ("\n", (True, '1')),
                     ("\n", (True, '1')),
                     ("\n", (False, '(!(1) && 0)')),
                     ("#", (False, '(!(1) && 0)')),
                     ("define", (False, '(!(1) && 0)')),
                     (" ", (False, '(!(1) && 0)')),
                     ("ELIF_0", (False, '(!(1) && 0)')),
                     ("\n", (False, '(!(1) && 0)')),
                     ("\n", (False, '(!(1) && !(0))')),
                     ("#", (False, '(!(1) && !(0))')),
                     ("define", (False, '(!(1) && !(0))')),
                     (" ", (False, '(!(1) && !(0))')),
                     ("ELSE_", (False, '(!(1) && !(0))')),
                     ("\n", (False, '(!(1) && !(0))')),
                     ("\n", (True, '')),
                     ]
        self.assertEqual(tokAndState, expResult)
        self.assertEqual(''.join(allTokS),"\n\n\n#define ELIF_0\n\n#define ELSE_\n\n")
        self.assertEqual(''.join(nonCondTokS),"\n\n\n")

    def test_02(self):
        """TestPpLexerConditionalWithState.test_02(): Simple #if with conditional #undef, macro environment is altered in conditional part."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define ONE 1
#if 0
#undef ONE
#else
PASS
#endif
""",
                    {}
                    ),
                 )
        tokAndState = []
        allTokS = []
        nonCondTokS = []
        myGen = myLexer.ppTokens(condLevel=1)
        for aResult in myGen:
            tokAndState.append((aResult.t, myLexer.condState))
            allTokS.append(aResult.t)
            if not aResult.isCond:
                nonCondTokS.append(aResult.t)
            #print 'Result:', aResult
            #print 'State: ', myLexer.condState
        myLexer.finalise()
        #print 'tokAndState:'
        #print tokAndState
        #pprint.pprint(tokAndState)
        #print 'allTokS:'
        #print ''.join(allTokS)
        #print 'nonCondTokS:'
        #print ''.join(nonCondTokS)
        # Check only one macro defined
#         self.assertEqual(myLexer.definedMacros, '#define ONE 1 /* mt.h#1 Ref: 0 True */')
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['ONE', '__DATE__', '__TIME__'],
        )
        expResult = [
                     ('\n',     (True, '')),
                     ('\n',     (False, '0')),
                     ('#',      (False, '0')),
                     ('undef',  (False, '0')),
                     (' ',      (False, '0')),
                     ('ONE',    (False, '0')),
                     ('\n',     (False, '0')),
                     ('\n',     (True, '!(0)')),
                     ('PASS',   (True, '!(0)')),
                     ('\n',     (True, '!(0)')),
                     ('\n',     (True, '')),
                     ]
        self.assertEqual(tokAndState, expResult)
        self.assertEqual(''.join(allTokS),"\n\n#undef ONE\n\nPASS\n\n")
        self.assertEqual(''.join(nonCondTokS),"\n\nPASS\n\n")
        #print myLexer.macroEnvironment

    def test_10(self):
        """TestPpLexerConditionalWithState.test_10(): Simple #if/#else/#endif state is correct."""
        # Simulating this, should process to: TRUE TRUE TRUE
        src = """TRUE
#if 1
TRUE
#else
FALSE
#endif
TRUE
"""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    src,
                    {}
                    ),
                 )
        tokAndState = []
        allTokS = []
        nonCondTokS = []
        myGen = myLexer.ppTokens(condLevel=1)
#        print()
        for aResult in myGen:
            tokAndState.append((aResult.t, myLexer.condState))
            allTokS.append(aResult.t)
            if not aResult.isCond:
                nonCondTokS.append(aResult.t)
#            print('Result:', aResult)
#            print('State: ', myLexer.condState)
        myLexer.finalise()
#        print('tokAndState:')
#        print(tokAndState)
#        pprint.pprint(tokAndState)
#        print('allTokS:')
#        print(''.join(allTokS))
#        print('nonCondTokS:')
#        print(''.join(nonCondTokS))
        # Check only one macro defined
#         self.assertEqual(myLexer.definedMacros, '')
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['__DATE__', '__TIME__'],
        )
        expResult = [
            ('TRUE',    (True, '')),
            ('\n',      (True, '')),
            ('\n',      (True, '1')),
            ('TRUE',    (True, '1')),
            ('\n',      (True, '1')),
            ('\n',      (False, '!(1)')), # Reduction of #else to a '\n'
            ('FALSE',   (False, '!(1)')),
            ('\n',      (False, '!(1)')),
            ('\n',      (True, '')), # Reduction of #endif to '\n'
            ('TRUE',    (True, '')),
            ('\n',      (True, '')),
        ]
        self.assertEqual(tokAndState, expResult)
        self.assertEqual(''.join(allTokS),"TRUE\n\nTRUE\n\nFALSE\n\nTRUE\n")
        self.assertEqual(''.join(nonCondTokS),"TRUE\n\nTRUE\n\nTRUE\n")
        #print myLexer.macroEnvironment
#        print()
#        print(myLexer.condCompGraph)
        expGraphStr = """#if 1 /* True "mt.h" 2 7 */
#else /* False "mt.h" 4 16 */
#endif /* True "mt.h" 6 26 */"""
        self.assertEqual(str(myLexer.condCompGraph), expGraphStr)

class TestPpLexerConditionalAllIncludes(TestIncludeHandlerBase):
    """Tests conditional #include statements i.e. when condLevel !=0. Note: This is similar to stuff
    in TestIncludeHandler_UsrSys_Conditional above."""
    def __init__(self, *args):
        self._pathsUsr = [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ]
        self._pathsSys = [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ]
        self._initialTuContents = """#if INC == 0
// Normally not examined
"Including spam.h when INC == 0"
#include "spam.h"
#elif INC == 1
// This should be examined
"Including spam.h when INC == 1"
#include "inc/spam.h"
#elif INC > 1
// Normally not examined
"Including spam.h when INC > 1"
#include <spam.h>
#endif
"""
        self._incFileMap = {
                os.path.join('usr', 'spam.h') : """Content of: user, spam.h
""",
                os.path.join('usr', 'inc', 'spam.h') : """Content of: user, include, spam.h
""",
                os.path.join('sys', 'spam.h') : """Content of: sys, include, spam.h
""",
                os.path.join('sys', 'inc', 'spam.h') : """Content of: system, include, spam.h
""",
            }
        super(TestPpLexerConditionalAllIncludes, self).__init__(*args)

    def test_00(self):
        """TestPpLexerConditionalAllIncludes.test_00(): Tests conditional #include statements; INC = 0, condLevel=0."""
        # Note: Using line splicing in the predef
        preDefMacros=[
                      """#define INC 0
""",
                      ]
        myLexer = PpLexer.PpLexer(
                                  'src/spam.c',
                                  self._incSim,
                                  preIncFiles=[
                                               io.StringIO(x) for x in preDefMacros
                                               ],
                                  )
        resultTokS = [t for t in myLexer.ppTokens(condLevel=0)]
        myLexer.finalise()
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('"Including spam.h when INC == 1"', 'string-literal'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('Content', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('of', 'identifier'),
            PpToken.PpToken(':', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('user', 'identifier'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('include', 'identifier'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('spam', 'identifier'),
            PpToken.PpToken('.', 'preprocessing-op-or-punc'),
            PpToken.PpToken('h', 'identifier'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        print()
        print('Expected result:')
        print(expTokS)
        print('Actual result:')
        self.pprintTokensAsCtors(resultTokS)
        self._printDiff(resultTokS, expTokS)
        self.assertEqual(resultTokS, expTokS)
        expGraph = """Unnamed Pre-include [7, 4]:  True "" ""
src/spam.c [12, 1]:  True "" ""
000008: #include usr/inc/spam.h
        usr/inc/spam.h [15, 10]:  True "(!(INC == 0) && INC == 1)" "['"inc/spam.h"', 'CP=None', 'usr=usr']\""""
#        print 'FileIncludeGraph:'
#        print myLexer.fileIncludeGraphRoot
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

    def test_01(self):
        """TestPpLexerConditionalAllIncludes.test_01(): Tests conditional #include statements; INC = 1, condLevel=0."""
        # Note: Using line splicing in the predef
        preDefMacros=[
                      """#define INC 1
""",
                      ]
        myLexer = PpLexer.PpLexer(
                                  'src/spam.c',
                                  self._incSim,
                                  preIncFiles=[
                                               io.StringIO(x) for x in preDefMacros
                                               ],
                                  )
        resultTokS = [t for t in myLexer.ppTokens(condLevel=0)]
        myLexer.finalise()
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('"Including spam.h when INC == 1"', 'string-literal'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('Content', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('of', 'identifier'),
            PpToken.PpToken(':', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('user', 'identifier'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('include', 'identifier'),
            PpToken.PpToken(',', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('spam', 'identifier'),
            PpToken.PpToken('.', 'preprocessing-op-or-punc'),
            PpToken.PpToken('h', 'identifier'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
#        print
#        print 'Expected result:'
#        print expTokS
#        print 'Actual result:'
#        self.pprintTokensAsCtors(resultTokS)
        self._printDiff(resultTokS, expTokS)
        self.assertEqual(resultTokS, expTokS)
        expGraph = """Unnamed Pre-include [7, 4]:  True "" ""
src/spam.c [12, 1]:  True "" ""
000008: #include usr/inc/spam.h
        usr/inc/spam.h [15, 10]:  True "(!(INC == 0) && INC == 1)" "['"inc/spam.h"', 'CP=None', 'usr=usr']\""""
#        print 'FileIncludeGraph:'
#        print myLexer.fileIncludeGraphRoot
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

class TestPpLexerError(TestPpLexer):
    """Tests the construction of a PpLexer object and process #error statement."""
    def test_00(self):
        """TestPpLexerError - simple error message."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#error some kind of error message
""",
                    {}),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """
""")
        myLexer.finalise()

    def test_01(self):
        """TestPpLexerError - error message with object-like macro substitution."""
        preDefMacros = [
                        '#define MY_ERROR SOME MACRO STUFF\n',
                        ]
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#error some kind of MY_ERROR message
""",
                    {}),
                 preIncFiles=[io.StringIO(x) for x in preDefMacros],
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, '\n\n')
        myLexer.finalise()

    def test_02(self):
        """TestPpLexerError - error message with function-like macro substitution."""
        preDefMacros = [
                        '#define MY_ERROR(x) # x\n',
                        ]
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#error some kind of MY_ERROR(wtf) message
""",
                    {}),
                 preIncFiles=[io.StringIO(x) for x in preDefMacros],
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, '\n\n')
        myLexer.finalise()

class TestPpLexerWarning(TestPpLexer):
    """Tests the construction of a PpLexer object and process #warning statement.
    NOTE: #warning is not in the standard at all but can occur, for example
    in:
    /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.9.sdk/usr/include/sys/cdefs.h
    78  /* This SDK is designed to work with clang and specific versions of
    79   * gcc >= 4.0 with Apple's patch sets */
    80  #if !defined(__GNUC__) || __GNUC__ < 4
    81  #warning "Unsupported compiler detected"
    82  #endif
    """
    def test_00(self):
        """TestPpLexerWarning - simple warning message."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#warning some kind of warning message
""",
                    {}),
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """
""")
        myLexer.finalise()

    def test_01(self):
        """TestPpLexerWarning - error message with object-like macro substitution."""
        preDefMacros = [
                        '#define MY_WARN SOME MACRO STUFF\n',
                        ]
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#warning some kind of MY_WARN message
""",
                    {}),
                 preIncFiles=[io.StringIO(x) for x in preDefMacros],
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, '\n\n')
        myLexer.finalise()

    def test_02(self):
        """TestPpLexerWarning - error message with function-like macro substitution."""
        preDefMacros = [
                        '#define MY_WARN(x) # x\n',
                        ]
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#warning some kind of MY_WARN(wtf) message
""",
                    {}),
                 preIncFiles=[io.StringIO(x) for x in preDefMacros],
                 )

        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, '\n\n')
        myLexer.finalise()

class TestPpLexerBadMacroDirective(TestPpLexer):
    """TestPpLexerBadMacroDirective."""
    def test_00(self):
        """TestPpLexerBadMacroDirective - # "hello" with CppDiagnostic.PreprocessDiagnosticStd."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """# "hello"
""",
                    {}),
                 )

        try:
            result = ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('ExceptionCppDiagnosticUndefined not raised')
        except CppDiagnostic.ExceptionCppDiagnosticUndefined:
            self.assertTrue(True)

    def test_01(self):
        """TestPpLexerBadMacroDirective - # "hello" with CppDiagnostic.PreprocessDiagnosticKeepGoing."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """# "hello"
""",
                    {}),
                 diagnostic=CppDiagnostic.PreprocessDiagnosticKeepGoing())

        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """# "hello"
""")
        myLexer.finalise()

class C99Rationale(TestPpLexer):
    """Tests examples found in C99RationaleV5.10.pdf."""
    def test_6_10_00_00(self):
        """C99Rationale.6.10 [00] - Whitespace preceeding #if."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define BLAH 1
/* here a comment */ #if BLAH
PASS
#endif
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n  \nPASS\n\n""")
        myLexer.finalise()

    def test_6_10_00_01(self):
        """C99Rationale.6.10 [01] - Whitespace preceeding #if."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define BLAH 1
#/* there a comment */ if BLAH
PASS
#endif
# if /* every-
 where a comment */ BLAH""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\nPASS\n\n""")
        myLexer.finalise()

    def test_6_10_00_02(self):
        """C99Rationale.6.10 [02] - Whitespace preceeding #if."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define BLAH 1
# if /* every-
 where a comment */ BLAH
PASS
#endif
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\nPASS\n\n""")
        myLexer.finalise()

    def test_6_10_00_03(self):
        """C99Rationale.6.10 [03] - Invalid comparison in conditional #elif."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """# ifndef xxx
# define xxx "abc"
PASS
# elif xxx > 0
FAIL
# endif
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\nPASS\n\n""")
        myLexer.finalise()

    def test_6_10_3_00(self):
        """C99Rationale.6.10.3 [00] - Redefinition of NBUFS "with diagnostics generated only if the definitions differ."."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """# define NUFS 10
# define NUFS 12
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
#        print myLexer.macroEnvironment
        self.assertTrue(myLexer.macroEnvironment.hasMacro('NUFS'))
        self.assertEqual('#define NUFS 10 /* spam.h#1 Ref: 0 True */', str(myLexer.macroEnvironment.macro('NUFS')))

    def test_6_10_3_01(self):
        """C99Rationale.6.10.3 [01] - Valid redefinition of NULL_DEV."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define NULL_DEV /* the first time */ 0
#define NULL_DEV /* the second time */ 0
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\n""")
        myLexer.finalise()

    def test_6_10_3_02(self):
        """C99Rationale.6.10.3 [02] - Function like macros with missing arguments."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define TENTH 0.1
#define F f
#define D // expands into no preprocessing tokens
#define LD L
#define glue(a, b) a ## b
#define xglue(a, b) glue(a, b)
float f = xglue(TENTH, F) ;
double d = xglue(TENTH, D) ;
long double ld = xglue(TENTH, LD);
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        myExpResult = """\n\n\n\n\n\nfloat f = 0.1f ;
double d = 0.1 ;
long double ld = 0.1L;
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(myExpResult))
        self.assertEqual(result, myExpResult)
        myLexer.finalise()

    def test_6_10_3_03_00(self):
        """C99Rationale.6.10.3 [03_00] - Variable argument example with macro DEBUG not defined."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#ifdef DEBUG
#define dfprintf(stream, ...) \
fprintf(stream, "DEBUG: " __VA_ARGS__)
#else
#define dfprintf(stream, ...) ((stream, __VA_ARGS__, 0))
#endif
#define dprintf(...) dfprintf(stderr, __VA_ARGS__)
dprintf("X = %d\n", x);
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        myExpResult = """\n\n\n
((stderr, "X = %d\n",x, 0));
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(myExpResult))
        self.assertEqual(result, myExpResult)
        myLexer.finalise()

    def test_6_10_3_03_01(self):
        """C99Rationale.6.10.3 [03_01] - Variable argument example with macro DEBUG defined."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define DEBUG
#ifdef DEBUG
#define dfprintf(stream, ...) \
fprintf(stream, "DEBUG: " __VA_ARGS__)
#else
#define dfprintf(stream, ...) ((stream, __VA_ARGS__, 0))
#endif
#define dprintf(...) dfprintf(stderr, __VA_ARGS__)
dprintf("X = %d\n", x);
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        myExpResult = """\n\n\n\n
fprintf(stderr, "DEBUG: " "X = %d\n",x);
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(myExpResult))
        self.assertEqual(result, myExpResult)
        myLexer.finalise()

    def test_6_10_3_3_00(self):
        """C99Rationale.6.10.3.3 - Token pasting."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define a(n) aaa ## n
#define b 2
a(b)
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\naaab\n""")
        myLexer.finalise()

    def test_6_10_3_4_00(self):
        """C99Rationale.6.10.3.4 - Rescanning with no ambiguity."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define f(a) a*g
#define g f
f(2)(9)
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\n2*f(9)\n""")
        myLexer.finalise()

    def test_6_10_3_4_01(self):
        """C99Rationale.6.10.3.4 - Rescanning with ambiguity.."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define f(a) a*g
#define g(a) f(a)
f(2)(9)
""",
                    {}),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\n2*f(9)\n""")
        myLexer.finalise()

class TestPpLexerFileIncludeGraph(TestPpLexer):
    """Tests PpLexer file include graph representaiton."""
    def test_00(self):
        """TestPpLexerFileIncludeGraph.test_00():"""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define INC 1
#if INC == 1
#include "spam.h"
#else
#include "eggs.h"
#endif
""",
                    {
                     'spam.h'   : """PASS\n""",
                     'eggs.h'   : """FAIL\n""",
                     }
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\nPASS\n\n\n""")
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        expGraph = """spam.h [7, 4]:  True "" ""
000003: #include spam.h
  spam.h [2, 1]:  True "INC == 1" "['"spam.h"', 'CP=']\""""
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

    def test_01(self):
        """TestPpLexerFileIncludeGraph.test_01():"""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define INC 1
#if defined INC
#include "spam.h"
#else
#include "eggs.h"
#endif
""",
                    {
                     'spam.h'   : """PASS\n""",
                     'eggs.h'   : """FAIL\n""",
                     }
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\nPASS\n\n\n""")
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        expGraph = """spam.h [7, 4]:  True "" ""
000003: #include spam.h
  spam.h [2, 1]:  True "defined INC" "['"spam.h"', 'CP=']\""""
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

    def test_02(self):
        """TestPpLexerFileIncludeGraph.test_02():"""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define INC 1
#if !defined UNDEF
#include "spam.h"
#else
#include "eggs.h"
#endif
""",
                    {
                     'spam.h'   : """PASS\n""",
                     'eggs.h'   : """FAIL\n""",
                     }
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\nPASS\n\n\n""")
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        expGraph = """spam.h [7, 4]:  True "" ""
000003: #include spam.h
  spam.h [2, 1]:  True "!defined UNDEF" "['"spam.h"', 'CP=']\""""
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

    def test_03(self):
        """TestPpLexerFileIncludeGraph.test_03():"""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define INC 1
#if UNDEF == 0
#include "spam.h"
#else
#include "eggs.h"
#endif
""",
                    {
                     'spam.h'   : """PASS\n""",
                     'eggs.h'   : """FAIL\n""",
                     }
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\nPASS\n\n\n""")
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        expGraph = """spam.h [7, 4]:  True "" ""
000003: #include spam.h
  spam.h [2, 1]:  True "UNDEF == 0" "['"spam.h"', 'CP=']\""""
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

    def test_04(self):
        """TestPpLexerFileIncludeGraph.test_04():"""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define INC 1
#if ! UNDEF
#include "spam.h"
#else
#include "eggs.h"
#endif
""",
                    {
                     'spam.h'   : """PASS\n""",
                     'eggs.h'   : """FAIL\n""",
                     }
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        self.assertEqual(result, """\n\nPASS\n\n\n""")
        myLexer.finalise()
        #print 'FileIncludeGraph:'
        #print myLexer.fileIncludeGraphRoot
        expGraph = """spam.h [7, 4]:  True "" ""
000003: #include spam.h
  spam.h [2, 1]:  True "! UNDEF" "['"spam.h"', 'CP=']\""""
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

class TestPpLexerFileIncludeGraphReplacement(TestPpLexer):
    """Tests PpLexer macro replacement in a file include graph."""
    def test_00(self):
        """TestPpLexerFileIncludeGraphReplacement.test_00():"""
        myLexer = PpLexer.PpLexer(
                 'ITU.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define SPAM Original in ITU.h
#if defined SPAM
PASS
#else
FAIL
#endif

print SPAM

#undef SPAM

print SPAM

#if !defined SPAM
PASS
#else
FAIL
#endif

#define SPAM Redefined in ITU.h

print SPAM

#include "spam_undef.h"

print SPAM

#if defined SPAM
FAIL
#else
PASS
#endif

#define SPAM Redefined again in ITU.h

print SPAM

#include "spam_redef.h"

print SPAM

#if defined SPAM
PASS
#else
FAIL
#endif

print SPAM
EOF
""",
                    {
                     'spam_undef.h'   : """SOF: spam_undef.h
#if defined SPAM
#undef SPAM
#endif
EOF: spam_undef.h
""",
                     'spam_redef.h'   : """SOF: spam_redef.h
#if defined SPAM
#undef SPAM
#endif
#define SPAM Redefined in spam_redef.h
EOF: spam_redef.h
""",
                     }
                    ),
                    autoDefineDateTime=False,
                 )
        #print
        result = ''.join([t.t for t in myLexer.ppTokens()])
        #print 'Result:'
        #print result
        #print '---'
        expResult = """

PASS

print Original in ITU.h


print SPAM


PASS


print Redefined in ITU.h

SOF: spam_undef.h



EOF: spam_undef.h

print SPAM


PASS


print Redefined again in ITU.h

SOF: spam_redef.h




EOF: spam_redef.h

print Redefined in spam_redef.h


PASS

print Redefined in spam_redef.h
EOF
"""
        self.assertEqual(result, expResult)
        myLexer.finalise()
#        print 'FileIncludeGraph:'
#        print myLexer.fileIncludeGraphRoot
        expGraph = """ITU.h [92, 47]:  True "" ""
000025: #include spam_undef.h
  spam_undef.h [19, 13]:  True "" "['"spam_undef.h"', 'CP=']"
000039: #include spam_redef.h
  spam_redef.h [32, 21]:  True "" "['"spam_redef.h"', 'CP=']\""""
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))
        expHistory = """Macro Environment:
#define SPAM Redefined in spam_redef.h /* spam_redef.h#5 Ref: 3 True */

Macro History (referenced macros only):
Out-of-scope:
#define SPAM Original in ITU.h /* ITU.h#1 Ref: 2 False ITU.h#10 */
    ITU.h 2 13
    ITU.h 8 7
#define SPAM Redefined in ITU.h /* ITU.h#20 Ref: 2 False spam_undef.h#3 */
    ITU.h 22 7
    spam_undef.h 2 13
#define SPAM Redefined again in ITU.h /* ITU.h#34 Ref: 2 False spam_redef.h#3 */
    ITU.h 36 7
    spam_redef.h 2 13
In scope:
#define SPAM Redefined in spam_redef.h /* spam_redef.h#5 Ref: 3 True */
    ITU.h 40 7
    ITU.h 42 13
    ITU.h 48 7"""
        #print
        #print myLexer.macroEnvironment.macroHistory()
        self.assertEqual(expHistory, myLexer.macroEnvironment.macroHistory())

class TestPpLexerConditionalSpurious(TestPpLexer):
    """Tests PpLexer with conditional source code that has spurious tokens."""
    def test_00(self):
        """TestPpLexerConditionalSpurious.test_00(): Simple spurious tokens on #else."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 1
PASS
#else spurious #else
FAIL
#endif     
""",
                    {}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_01(self):
        """TestPpLexerConditionalSpurious.test_01(): Simple spurious tokens on #endif."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 1
PASS
#else     
FAIL
#endif spurious #endif
""",
                    {}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_02(self):
        """TestPpLexerConditionalSpurious.test_02(): Simple spurious tokens on #else and #endif."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#if 1
PASS
#else     and something
FAIL
#endif spurious #endif
""",
                    {}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\nPASS\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

class TestPpLexerFileIncludeRecursion(TestPpLexer):
    """Tests PpLexer file recursive include graph."""
    def test_00(self):
        """TestPpLexerFileIncludeRecursion.test_00(): Recursive #include cycle=0"""
        # Note: cpp.exe reports: recursive.h:2:23: #include nested too deeply
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#include "recusive.h"
""",
                    {
                     'recusive.h'   : """#include "recusive.h"\n""",
                     }
                    ),
                 )
        try:
            ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('ExceptionPpLexerNestedInclueLimit not raised')
        except PpLexer.ExceptionPpLexerNestedInclueLimit:
            pass
        #self.assertEqual(result, """""")
        #myLexer.finalise()

    def test_01(self):
        """TestPpLexerFileIncludeRecursion.test_01(): Recursive #include cycle=1"""
        # Note: cpp.exe reports: <file>:2:23: #include nested too deeply
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#include "a.h"
""",
                    {
                     'a.h'   : """#include "b.h"\n""",
                     'b.h'   : """#include "a.h"\n""",
                     }
                    ),
                 )
        try:
            ''.join([t.t for t in myLexer.ppTokens()])
            print(myLexer.fileIncludeGraphRoot)
            self.fail('ExceptionPpLexerNestedInclueLimit not raised')
        except PpLexer.ExceptionPpLexerNestedInclueLimit:
            pass
    
    def test_02(self):
        """TestPpLexerFileIncludeRecursion.test_02(): Recursive #include cycle=2"""
        # Note: cpp.exe reports: <file>:2:23: #include nested too deeply
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#include "a.h"
""",
                    {
                     'a.h'   : """#include "b.h"\n""",
                     'b.h'   : """#include "c.h"\n""",
                     'c.h'   : """#include "a.h"\n""",
                     }
                    ),
                 )
        try:
            ''.join([t.t for t in myLexer.ppTokens()])
            print(myLexer.fileIncludeGraphRoot)
            self.fail('ExceptionPpLexerNestedInclueLimit not raised')
        except PpLexer.ExceptionPpLexerNestedInclueLimit:
            pass
    
    def test_03(self):
        """TestPpLexerFileIncludeRecursion.test_03(): Recursive #include cycle=3"""
        # Note: cpp.exe reports: <file>:2:23: #include nested too deeply
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#include "a.h"
""",
                    {
                     'a.h'   : """#include "b.h"\n""",
                     'b.h'   : """#include "c.h"\n""",
                     'c.h'   : """#include "d.h"\n""",
                     'd.h'   : """#include "a.h"\n""",
                     }
                    ),
                 )
        try:
            ''.join([t.t for t in myLexer.ppTokens()])
            print(myLexer.fileIncludeGraphRoot)
            self.fail('ExceptionPpLexerNestedInclueLimit not raised')
        except PpLexer.ExceptionPpLexerNestedInclueLimit:
            pass
    
    def test_04(self):
        """TestPpLexerFileIncludeRecursion.test_04(): Recursive #include cycle=4"""
        # Note: cpp.exe reports: <file>:2:23: #include nested too deeply
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#include "a.h"
""",
                    {
                     'a.h'   : """#include "b.h"\n""",
                     'b.h'   : """#include "c.h"\n""",
                     'c.h'   : """#include "d.h"\n""",
                     'd.h'   : """#include "e.h"\n""",
                     'e.h'   : """#include "a.h"\n""",
                     }
                    ),
                 )
        try:
            ''.join([t.t for t in myLexer.ppTokens()])
            print(myLexer.fileIncludeGraphRoot)
            self.fail('ExceptionPpLexerNestedInclueLimit not raised')
        except PpLexer.ExceptionPpLexerNestedInclueLimit:
            pass
    
    def test_05(self):
        """TestPpLexerFileIncludeRecursion.test_05(): Recursive #include cycle=5"""
        # Note: cpp.exe reports: <file>:2:23: #include nested too deeply
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#include "a.h"
""",
                    {
                     'a.h'   : """#include "b.h"\n""",
                     'b.h'   : """#include "c.h"\n""",
                     'c.h'   : """#include "d.h"\n""",
                     'd.h'   : """#include "e.h"\n""",
                     'e.h'   : """#include "f.h"\n""",
                     'f.h'   : """#include "a.h"\n""",
                     }
                    ),
                 )
        try:
            ''.join([t.t for t in myLexer.ppTokens()])
            print(myLexer.fileIncludeGraphRoot)
            self.fail('ExceptionPpLexerNestedInclueLimit not raised')
        except PpLexer.ExceptionPpLexerNestedInclueLimit:
            pass
    
class TestPpLexerRaiseOnError(TestIncludeHandlerBase):
    """Tests PpLexer when raising an exception in include graph."""
    def __init__(self, *args):
        self._pathsUsr = [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ]
        self._pathsSys = [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ]
        # The next two arguments mean that:
        # src/spam.c
        #   |-> usr/spam.h
        #       |-> usr/inc/spam.h
        #           |-> sys/spam.h
        #               |-> sys/inc/spam.h
        #                   |-> "Content of: system, include, spam.h"
        # Initial TU:
        self._initialTuContents = """#include "spam.h"
"""
        self._incFileMap = {
                os.path.join('usr', 'spam.h') : """#include "inc/spam.h"
""",
                os.path.join('usr', 'inc', 'spam.h') : """#include <spam.h>
""",
                os.path.join('sys', 'spam.h') : """#include <inc/spam.h>
""",
                os.path.join('sys', 'inc', 'spam.h') : """Content of: system, include, spam.h
#error Error in system, include, spam.h
""",
            }
        super(TestPpLexerRaiseOnError, self).__init__(*args)

    def test_00(self):
        """TestPpLexerRaiseOnError.test_00(): Raise from inside include graph."""
        myLexer = PpLexer.PpLexer(
                  'src/spam.c',
                  self._incSim,
                  diagnostic=CppDiagnostic.PreprocessDiagnosticRaiseOnError(),
                                  )
        # This should fail!
        try:
            result = ''.join([t.t for t in myLexer.ppTokens()])
            self.fail('CppDiagnostic.ExceptionCppDiagnostic not raised')
        except CppDiagnostic.ExceptionCppDiagnostic:
            myLexer._includeHandler.clearHistory()
            pass
        myLexer.finalise()
        expGraph = """src/spam.c [0, 0]:  True "" ""
000001: #include usr/spam.h
  usr/spam.h [0, 0]:  True "" "['"spam.h"', 'CP=None', 'usr=usr']"
  000001: #include usr/inc/spam.h
    usr/inc/spam.h [0, 0]:  True "" "['"inc/spam.h"', 'CP=usr']"
    000001: #include sys/spam.h
      sys/spam.h [0, 0]:  True "" "['<spam.h>', 'sys=sys']"
      000001: #include sys/inc/spam.h
        sys/inc/spam.h [15, 10]:  True "" "['<inc/spam.h>', 'sys=sys']\""""
#        print 'FileIncludeGraph:'
#        print 'Expected:'
#        print expGraph
#        print 'Actual:'
#        print myLexer.fileIncludeGraphRoot
        self.assertEqual(expGraph, str(myLexer.fileIncludeGraphRoot))

class PpLexerReadOnly(TestPpLexer):
    """Tests access of read only attributes while lexing."""
    def test_00(self):
        """PpLexerReadOnly - fileName."""
        myStr = """int main()
{
    printf("Hello WOrld.");
    return 0;
}
"""
        myLexer = PpLexer.PpLexer('hello.c', CppIncludeStringIO([], [], myStr, {}),)
        i = 0
        for t in myLexer.ppTokens():
            self.assertEqual('hello.c', myLexer.fileName)
            i += 1

    def test_01(self):
        """PpLexerReadOnly - lineNUm, colNum."""
        myStr = """int main()
{
    printf("Hello WOrld.");
    return 0;
}
"""
        myLexer = PpLexer.PpLexer('hello.c', CppIncludeStringIO([], [], myStr, {}),)
        l = c = 1
        i = 0
        for t in myLexer.ppTokens():
            myLexer.lineNum
            myLexer.colNum
#            print t, myLexer.lineNum, myLexer.colNum
#            self.assertEqual(l, myLexer.lineNum)
#            self.assertEqual(c, myLexer.colNum)
#            l += t.t.count('\n')
#            if '\n' in t.t:
#                c = len(t.t) - t.t.rfind('\n')
#            else:
#                c += 1
            i += 1

class PpLexerPragma(TestPpLexer):
    """Tests #pragma processing while lexing."""
    def test_none_00(self):
        """PpLexerPragma - no pragma handler"""
        myStr = """#pragma STDC FP_CONTRACT ON
"""
        myLexer = PpLexer.PpLexer(
                    'hello.c',
                    CppIncludeStringIO([], [], myStr, {}),
                    pragmaHandler=None,
                )
        i = 0
        myTokS = [t for t in myLexer.ppTokens()]
        expTokS = [
            PpToken.PpToken('\n',    'whitespace'),
        ]
        self.assertEqual(myTokS, expTokS)
        #print myTokS
        #print
        myEnv = myLexer.macroEnvironment
        self.assertEqual(
            sorted(myEnv.macros()),
            ['__DATE__', '__TIME__'],
        )

    def test_STDC_00(self):
        """PpLexerPragma - STDC."""
        myStr = """#pragma STDC FP_CONTRACT ON
"""
        myLexer = PpLexer.PpLexer(
                    'hello.c',
                    CppIncludeStringIO([], [], myStr, {}),
                    pragmaHandler=PragmaHandler.PragmaHandlerSTDC(),
                )
        i = 0
        myTokS = [t for t in myLexer.ppTokens()]
        expTokS = [
            PpToken.PpToken('\n',    'whitespace'),
            PpToken.PpToken('\n',   'whitespace'),
        ]
        self.assertEqual(myTokS, expTokS)
        #print myTokS
        #print
        myEnv = myLexer.macroEnvironment
        #print myEnv
        #print
        #print myEnv.macroHistory()
        self.assertEqual(myEnv.hasMacro('FP_CONTRACT'), True)
        self.assertEqual(
            sorted(myEnv.macros()),
            ['FP_CONTRACT', '__DATE__', '__TIME__'],
        )

    def test_pragma_raises_00(self):
        """PpLexerPragma - raising ExceptionPragmaHandler."""
        myStr = """#pragma STDC FP_CONTRACT ON
"""
        class PragmaHandlerRaises(PragmaHandler.PragmaHandlerABC):
            @property
            def replaceTokens(self):
                return False
                              
            def pragma(self, theTokS):
                raise PragmaHandler.ExceptionPragmaHandler('pragma() raised')
        myLexer = PpLexer.PpLexer(
                    'hello.c',
                    CppIncludeStringIO([], [], myStr, {}),
                    pragmaHandler=PragmaHandlerRaises(),
                )
        try:
            myTokS = [t for t in myLexer.ppTokens()]
            self.fail('ExceptionCppDiagnosticUndefined not raised')
        except CppDiagnostic.ExceptionCppDiagnosticUndefined as err:
            self.assertEqual(str(err), 'pragma() raised at line=1, col=2 of file "hello.c"')

class MinimalWhitespace(TestPpLexer):
    """Testign whitespace minimisation"""
    def test_00(self):
        """MinimalWhitespace.test_00(): Non-minimal whitespace."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """float f       = xglue(TENTH, F) ;

double d = xglue(TENTH,     D  ) ;

long double ld = xglue(TENTH,    
    LD  )   ;

""",
                    {}),
                 preIncFiles=[
                              io.StringIO("""#define TENTH 0.1

#define F f
a
#define D // expands into no preprocessing tokens

#define LD L

#define glue(a, b) a ## b

#define xglue(a, b) glue(a, b)
b
"""),
                              ],
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        myExpResult = """\n
a
\n\n\n
b
float f       = 0.1f ;

double d = 0.1 ;

long double ld = 0.1L   ;

"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(myExpResult))
        self.assertEqual(result, myExpResult)
        myLexer.finalise()

    def test_01(self):
        """MinimalWhitespace.test_01(): Minimal whitespace."""
        myLexer = PpLexer.PpLexer(
                 'spam.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """float f       = xglue(TENTH, F) ;

double d = xglue(TENTH,     D  ) ;

long double ld = xglue(TENTH,    
    LD  )   ;

""",
                    {}),
                 preIncFiles=[
                              io.StringIO("""#define TENTH 0.1

#define F f
a
#define D // expands into no preprocessing tokens

#define LD L

#define glue(a, b) a ## b

#define xglue(a, b) glue(a, b)
b
"""),
                              ],
                 )
        result = ''.join([t.t for t in myLexer.ppTokens(minWs=True)])
        myExpResult = """
a
b
float f = 0.1f ;
double d = 0.1 ;
long double ld = 0.1L ;
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(myExpResult))
        self.assertEqual(result, myExpResult)
        self.assertEqual(86, myLexer.tuIndex)
        myLexer.finalise()

class Unmaintainable(TestPpLexer):
    """From: http://mindprod.com/jgloss/unmaincamouflage.html"""
    def test_00(self):
        """Unmaintainable.test_00() from http://mindprod.com/jgloss/unmaincamouflage.html"""
        myStr = """#ifndef DONE
#ifdef TWICE
// put stuff here to declare 3rd time around
void g(char* str);
#define DONE
#else // TWICE
#ifdef ONCE
// put stuff here to declare 2nd time around
void g(void* str);
#define TWICE
#else // ONCE
// put stuff here to declare 1st time around
void g(std::string str);
#define ONCE
#endif // ONCE
#endif // TWICE
#endif // DONE
"""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], myStr, {}),
                 )
        #i = 0
        #for t in myLexer.ppTokens():
        #    print i, t
        #    i += 1
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\n \nvoid g(std::string str);\n\n\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        myCcg = myLexer.condCompGraph
        #print
        #print str(myCcg)
        self.assertEqual("""#ifndef DONE /* True "mt.h" 1 0 */
    #ifdef TWICE /* False "mt.h" 2 2 */
    #else /* True "mt.h" 6 21 */
        #ifdef ONCE /* False "mt.h" 7 23 */
        #else /* True "mt.h" 11 42 */
        #endif /* True "mt.h" 15 87 */
    #endif /* True "mt.h" 16 89 */
#endif /* True "mt.h" 17 91 */""", str(myCcg))

class TestPpLexerErrorInCondStack(TestPpLexer):
    """Simulation of a real problem where a tokenising error (no newline at EOF)
    causes the conditional stack to be wrong."""
    
    def test_00(self):
        """Handling no newline at EOF when inside an include stack (one include)."""
        myIncHandler = CppIncludeStringIO(
            [
                os.path.join('usr'),
                ],
            [
                ],
            """#ifndef UNDEFINED
#include "user.h"
#endif
""",
            # Map of paths to contents
            {
                os.path.join('usr', 'user.h') : """#ifndef __USER_H__
#define __USER_H__
USER
#endif // __USER_H__""",
            }
        )
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 myIncHandler,
                 diagnostic=CppDiagnostic.PreprocessDiagnosticKeepGoing(),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\nUSER\n\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        #print
        #print myLexer.fileIncludeGraphRoot

    def test_04(self):
        """Handling no newline at EOF when inside an include stack (four includes)."""
        myIncHandler = CppIncludeStringIO(
            [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ],
            [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ],
            """#ifndef UNDEFINED
#include "user.h"
#endif // UNDEFINED""",
            # Map of paths to contents
            {
                os.path.join('usr', 'user.h') : """#ifndef __USER_H__
#define __USER_H__
#include "user_inc.h"
#endif // __USER_H__""",
                os.path.join('usr', 'inc', 'user_inc.h') : """#ifndef __USER_INC_H__
#define __USER_INC_H__
#include <system.h>
#endif // __USER_INC_H__""",
                os.path.join('sys', 'system.h') : """#ifndef __SYSTEM_H__
#define __SYSTEM_H__
#include <system_inc.h>
#endif // __SYSTEM_H__""",
                os.path.join('sys', 'inc', 'system_inc.h') : """#ifndef __SYSTEM_INC_H__
#define __SYSTEM_INC_H__
SYSTEM_INC
#endif // __SYSTEM_INC_H__""",
            }
            )
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 myIncHandler,
                 diagnostic=CppDiagnostic.PreprocessDiagnosticKeepGoing(),
                 )
        #i = 0
        #for t in myLexer.ppTokens():
        #    print i, t
        #    i += 1
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """\n\n\n\n\n\n\n\n\nSYSTEM_INC\n\n\n\n\n\n\n\n\n\n"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        #print
        #print myLexer.fileIncludeGraphRoot

class TestDefineEMPTY(TestPpLexer):
    def test_05_00(self):
        """ISO/IEC 9899:1999 (E) 6.10-8 EXAMPLE using #define EMPTY [0]"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    """#define EMPTY
EMPTY #include <file.h>
""",
                    {'file.h' : 'Content of file.h\n'}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = '\n #include <file.h>'
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_05_01(self):
        """ISO/IEC 9899:1999 (E) 6.10-8 EXAMPLE using #define EMPTY [1]"""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    """#define EMPTY
EMPTY#include <file.h>
""",
                    {'file.h' : 'Content of file.h\n'}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = '\n #include <file.h>'
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_06_00(self):
        """ISO/IEC 9899:1999 (E) 6.10-8 EXAMPLE using #define EMPTY [0]."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define EMPTY
EMPTY #include "file.h"
""",
                    {'file.h' : 'Content of file.h\n'}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = '\n'
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_06_01(self):
        """ISO/IEC 9899:1999 (E) 6.10-8 EXAMPLE using #define EMPTY [1]."""
        myLexer = PpLexer.PpLexer(
                 'define.h',
                 CppIncludeStringIO(
                    [],
                    [],
                    """#define EMPTY
EMPTY #define NOT_EMPTY
""",
                    {}
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        #print myLexer.macroEnvironment
        #print myLexer.macroEnvironment.macros()
        self.assertEqual('EMPTY', myLexer.macroEnvironment.macros())
        expectedResult = '\n'
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    #pass

class TestPpLexerMacroLineContinuation(TestPpLexer):
    """Tests macro locations with line continuation.
    S:\epoc32\include\platform\cpudefs.h line 352
    """
    def test_00(self):
        """TestPpLexerMacroLineContinuation.test_00() """
        # NOTE: Use of \\ or raw string
        myStr = """#define __SWITCH_TO_ARM        asm("push {r0} ");\\
                            asm("add r0, pc, #4 ");\\
                            asm("bx r0 ");\\
                            asm("nop ");\\
                            asm(".align 2 ");\\
                            asm(".code 32 ");\\
                            asm("ldr r0, [sp], #4 ")
#define __END_ARM            asm(".code 16 ")
"""
        myStr = r"""#define __SWITCH_TO_ARM        asm("push {r0} ");\
                            asm("add r0, pc, #4 ");\
                            asm("bx r0 ");\
                            asm("nop ");\
                            asm(".align 2 ");\
                            asm(".code 32 ");\
                            asm("ldr r0, [sp], #4 ")
#define __END_ARM            asm(".code 16 ")
"""
        
        #print
        #print myStr
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], myStr, {}),
                 )
        #i = 0
        #for t in myLexer.ppTokens():
        #    print i, t
        #    i += 1
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = '\n\n'
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        #print
        #print '"%s"' % str(myLexer.macroEnvironment)
#         expStr = """#define __END_ARM asm(".code 16 ") /* mt.h#8 Ref: 0 True */
# #define __SWITCH_TO_ARM asm("push {r0} "); asm("add r0, pc, #4 "); asm("bx r0 "); asm("nop "); asm(".align 2 "); asm(".code 32 "); asm("ldr r0, [sp], #4 ") /* mt.h#1 Ref: 0 True */"""
#         #print
#         #print '"%s"' % expStr
#         #self.printStrDiff(expStr, str(myLexer.macroEnvironment))
#         self.assertEqual(expStr, str(myLexer.macroEnvironment))
        self.assertEqual(
            sorted(myLexer.macroEnvironment.macros()),
            ['__DATE__', '__END_ARM', '__SWITCH_TO_ARM', '__TIME__'],
        )
        self.assertEqual(
            myLexer.macroEnvironment.macro('__END_ARM').strReplacements(),
            'asm(".code 16 ")'
        )

class TestPpLexerHeaderName(TestPpLexer):
    """Tests #include statememts when a \\ is used."""
    def test_00(self):
        """TestPpLexerHeaderName.test_00(): #include "codeanalysis/sourceannotations.h"."""
        myStr = """This include:
#include "codeanalysis/sourceannotations.h"
ok.
"""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], myStr, {
                        os.path.join('codeanalysis', 'sourceannotations.h') : 'WORKS\n',
                                                    }),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        #print
        #print result
        #print self.pprintTokensAsCtors(result)
        expStr = """This include:
WORKS

ok.
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expStr))
        self.assertEqual(result, expStr)

    def test_01(self):
        """TestPpLexerHeaderName.test_01(): #include "codeanalysis\\sourceannotations.h"."""
        myStr = """This include:
#include "codeanalysis\\sourceannotations.h"
Fails because of backslash.
"""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], myStr, {
                        os.path.join('codeanalysis', 'sourceannotations.h') : 'FAILS\n',
                                                    }),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        #print
        #print result
        #print self.pprintTokensAsCtors(result)
        expStr = """This include:

Fails because of backslash.
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expStr))
        self.assertEqual(result, expStr)

    def test_02(self):
        """TestPpLexerHeaderName.test_02(): #include "codeanalysis\\sourceannotations.h" fails as bad backslash."""
        myStr = """This include:
#include "codeanalysis\\sourceannotations.h"
not OK.
"""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], myStr, {
                        os.path.join('codeanalysis', 'sourceannotations.h') : 'WORKS as fixBsInHdr=True\n',
                                                    }),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
#        print
#        print result
#        print self.pprintTokensAsCtors(result)
        expStr = """This include:

not OK.
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expStr))
        self.assertEqual(result, expStr)

    def test_10(self):
        """TestPpLexerHeaderName.test_10(): _retHeaderName(' "codeanalysis/sourceannotations.h" ') etc."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 )
        # Qstring
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(' "codeanalysis/sourceannotations.h" \n')
            )
        myResult = myLexer._retHeaderName(myCpp.next())
        #print
        #print myResult
        self.assertEqual(myResult, PpToken.PpToken('"codeanalysis/sourceannotations.h"', 'header-name'),)
        # Hstring
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(' <codeanalysis/sourceannotations.h> \n')
            )
        myResult = myLexer._retHeaderName(myCpp.next())
        self.assertEqual(myResult, PpToken.PpToken('<codeanalysis/sourceannotations.h>', 'header-name'),)
        # Qstring with \\
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(' "codeanalysis\\sourceannotations.h" \n')
            )
        myResult = myLexer._retHeaderName(myCpp.next())
        #print
        #print myResult
        self.assertTrue(myResult is None)

    def test_11(self):
        """TestPpLexerHeaderName.test_11(): _retHeaderName(' "codeanalysis/sourceannotations.h" ') etc. works correctly."""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], '', {}),
                 )
        # Qstring
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(' "codeanalysis/sourceannotations.h" \n')
            )
        myResult = myLexer._retHeaderName(myCpp.next())
        self.assertEqual(myResult, PpToken.PpToken('"codeanalysis/sourceannotations.h"', 'header-name'),)
        # Hstring
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(' <codeanalysis/sourceannotations.h> \n')
            )
        myResult = myLexer._retHeaderName(myCpp.next())
        self.assertEqual(myResult, PpToken.PpToken('<codeanalysis/sourceannotations.h>', 'header-name'),)
        # Qstring with \\
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(' "codeanalysis\\sourceannotations.h" \n')
            )
        myResult = myLexer._retHeaderName(myCpp.next())
        #print
        #print myResult
        self.assertEqual(myResult, None)

class TestLinux(TestPpLexer):
    """Various tests thrown up when processing the Linux Kernel."""
    FILE_STRINGIFY_H = """#ifndef __LINUX_STRINGIFY_H
#define __LINUX_STRINGIFY_H

/* Indirect stringification.  Doing two levels allows the parameter to be a
 * macro itself.  For example, compile with -DFOO=bar, __stringify(FOO)
 * converts to "bar".
 */

#define __stringify_1(x...)    #x
#define __stringify(x...)    __stringify_1(x)

#endif    /* !__LINUX_STRINGIFY_H */
"""
    # This is from include/trace/define_trace.h
    # It has been edited so that the #include TRACE_INCLUDE(TRACE_INCLUDE_FILE)
    # line is tested
    FILE_DEFINE_TRACE_H = """#include <linux/stringify.h>

#undef TRACE_INCLUDE
#undef __TRACE_INCLUDE

#ifndef TRACE_INCLUDE_FILE
# define TRACE_INCLUDE_FILE TRACE_SYSTEM
# define UNDEF_TRACE_INCLUDE_FILE
#endif

#ifndef TRACE_INCLUDE_PATH
# define __TRACE_INCLUDE(system) <trace/events/system.h>
# define UNDEF_TRACE_INCLUDE_PATH
#else
# define __TRACE_INCLUDE(system) __stringify(TRACE_INCLUDE_PATH/system.h)
#endif

# define TRACE_INCLUDE(system) __TRACE_INCLUDE(system)

#include TRACE_INCLUDE(TRACE_INCLUDE_FILE)
"""

    # Based (loosly) on asm-generic/div64.h
    FILE_DEFINE_DIV64_H = """
#if BITS_PER_LONG == 64

# define do_div(n,base) ({                    \
    uint32_t __base = (base);                \
    uint32_t __rem;                        \
    __rem = ((uint64_t)(n)) % __base;            \
    (n) = ((uint64_t)(n)) / __base;                \
    __rem;                            \
 })

#elif BITS_PER_LONG == 32

// extern uint32_t __div64_32(uint64_t *dividend, uint32_t divisor);

/* The unnecessary pointer compare is there
 * to check for type safety (n must be 64bit)
 */
# define do_div(n,base) ({                \
    uint32_t __base = (base);            \
    uint32_t __rem;                    \
    (void)(((typeof((n)) *)0) == ((uint64_t *)0));    \
    if (likely(((n) >> 32) == 0)) {            \
        __rem = (uint32_t)(n) % __base;        \
        (n) = (uint32_t)(n) / __base;        \
    } else                         \
        __rem = __div64_32(&(n), __base);    \
    __rem;                        \
 })

#else /* BITS_PER_LONG == ?? */

#define do_div(n,base)

# error do_div() does not yet support the C64

#endif /* BITS_PER_LONG */
"""
    def test_00(self):
        """TestLinux.test_00(): stringify.h"""
        myLexer = PpLexer.PpLexer(
                 'stringify.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    self.FILE_STRINGIFY_H,
                    {},
                    ),
                 )
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = '\n\n \n\n\n\n\n'
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

    def test_01(self):
        """TestLinux.test_01(): define_trace.h"""
        myLexer = PpLexer.PpLexer(
                 'define_trace.h',
                 CppIncludeStringIO(
                    ['.'],
                    [
                        '.',
#                        'linux',
#                        os.path.join('trace', 'events'),
                    ],
                    self.FILE_DEFINE_TRACE_H,
                    {
                        os.path.join('.', 'linux', 'stringify.h') : self.FILE_STRINGIFY_H,
                        os.path.join('.', 'trace', 'events', 'TRACE_SYSTEM.h') : """Contents
of
system.
""",
                    }
                    ),
                 )
#        result = ''.join([t.t for t in myLexer.ppTokens()])
        result = [t for t in myLexer.ppTokens()]
        resultStr = self.tokensToString(result)
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('\n\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('Contents', 'identifier'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('of', 'identifier'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('system', 'identifier'),
            PpToken.PpToken('.', 'preprocessing-op-or-punc'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        expectedResult = self.tokensToString(expTokS)
#        print
#        print result
#        print self.pprintTokensAsCtors(result)
        self._printDiff(result, expTokS)
        self.assertEqual(resultStr, expectedResult)
        myLexer.finalise()
#        print myLexer.macroEnvironment

    def test_02_00(self):
        """TestLinux.test_02_00(): #error processing in div64.h, macro is defined so there should be no error message."""
        myLexer = PpLexer.PpLexer(
                'div64.h',
                CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    self.FILE_DEFINE_DIV64_H,
                    {},
                ),
                preIncFiles=[
                    io.StringIO("#define BITS_PER_LONG 32\n")
                ],
            )
        resTokS = [t for t in myLexer.ppTokens()]
#        print 'Actual tokens:'
#        print self.pprintTokensAsCtors(resTokS)
        myLexer.finalise()
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('\n\n', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        self._printDiff(resTokS, expTokS)
        self.assertEqual(resTokS, expTokS)

    def test_02_01(self):
        """TestLinux.test_02_01(): #error processing in div64.h, macro is NOT defined so there should be an error message but verbatim i.e no expansion."""
        myLexer = PpLexer.PpLexer(
                'div64.h',
                CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    self.FILE_DEFINE_DIV64_H,
                    {},
                ),
                preIncFiles=[
                    io.StringIO("\n")
                ],
            )
        resTokS = [t for t in myLexer.ppTokens()]
#        print 'Actual tokens:'
#        print self.pprintTokensAsCtors(resTokS)
        myLexer.finalise()
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        self._printDiff(resTokS, expTokS)
        self.assertEqual(resTokS, expTokS)

class TestLinuxMacroInclude(TestPpLexer):
    """When processing the Linux Kernel a flaw in our code was noticed when macros are used to include."""
    def test_00(self):
        """TestLinuxMacroInclude.test_00(): #including an undefined macro, there should be a warning:"""
        myLexer = PpLexer.PpLexer(
                 'define_trace.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    """
/*
This contains a #include statment that uses a macro.
That macro is undefined.
*/
#include TRACE_INCLUDE(TRACE_INCLUDE_FILE) 
""",
                    {},
                    ),
                 )
        resultTokS = [t for t in myLexer.ppTokens()]
        myLexer.finalise()
#        resultStr = ''.join([t.t for t in resultTokS])
#        print
#        print self.pprintTokensAsCtors(resultTokS)
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        self._printDiff(resultTokS, expTokS)
        self.assertEqual(resultTokS, expTokS)

    def test_01(self):
        """TestLinuxMacroInclude.test_01(): #including an undefined macro conditional on that macro, there should be no warning."""
        myLexer = PpLexer.PpLexer(
                 'define_trace.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    """
/*
This conditionally contains a #include statment that uses a macro.
That macro is undefined.
*/
#ifdef TRACE_INCLUDE
#include TRACE_INCLUDE(TRACE_INCLUDE_FILE)
#endif 
""",
                    {},
                    ),
                 )
        resultTokS = [t for t in myLexer.ppTokens()]
        myLexer.finalise()
#        resultStr = ''.join([t.t for t in resultTokS])
#        print
#        print self.pprintTokensAsCtors(resultTokS)
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        self._printDiff(resultTokS, expTokS)
        self.assertEqual(resultTokS, expTokS)

    def test_02(self):
        """TestLinuxMacroInclude.test_02(): #including using a macro conditional on another macro, neither defined, there should be no warning."""
        myLexer = PpLexer.PpLexer(
                 'define_trace.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    """
/*
This conditionally contains a #include statment that uses a macro.
That macro is undefined.
*/
#ifdef UNDEF
#include TRACE_INCLUDE(TRACE_INCLUDE_FILE)
#endif 
""",
                    {},
                    ),
                 )
        resultTokS = [t for t in myLexer.ppTokens()]
        myLexer.finalise()
#        resultStr = ''.join([t.t for t in resultTokS])
#        print
#        print self.pprintTokensAsCtors(resultTokS)
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        self._printDiff(resultTokS, expTokS)
        self.assertEqual(resultTokS, expTokS)

    def test_03(self):
        """TestLinuxMacroInclude.test_03(): #including using a defined macro conditional on itself, there should be no warning."""
        myStr = """
/*
This conditionally contains a #include statment that uses a macro.
That include macro is defined.
*/
#define TRACE_INCLUDE(x) #x

#ifdef TRACE_INCLUDE
#include TRACE_INCLUDE(spam.h)
#endif 
"""
        myLexer = PpLexer.PpLexer(
                 'define_trace.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    myStr,
                    {
                        os.path.join('.', 'spam.h') : """Contents
of
spam.h
""",
                    }
                    ),
                 )
        resultTokS = [t for t in myLexer.ppTokens()]
        myLexer.finalise()
#        resultStr = ''.join([t.t for t in resultTokS])
#        print
#        print self.pprintTokensAsCtors(resultTokS)
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('Contents', 'identifier'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('of', 'identifier'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('spam', 'identifier'),
            PpToken.PpToken('.', 'preprocessing-op-or-punc'),
            PpToken.PpToken('h', 'identifier'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        self._printDiff(resultTokS, expTokS)
        self.assertEqual(resultTokS, expTokS)

    def test_04(self):
        """TestLinuxMacroInclude.test_04() - Macro replacement does not happen in h-str or q-str."""
        myStr = """#define current get_current()
#include <asm/current.h>
"""
        myLexer = PpLexer.PpLexer(
                 'define_trace.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    myStr,
                    {
                        os.path.join('.', 'asm', 'current.h') : """Contents of current header
""",
                    }
                    ),
                 )
        resultTokS = [t for t in myLexer.ppTokens()]
        myLexer.finalise()
        resultStr = ''.join([t.t for t in resultTokS])
#        print()
#        print('Result')
#        print(resultStr)
#        print('Result as tokens')
#        self.pprintTokensAsCtors(resultTokS)
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('Contents', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('of', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('get_current', 'identifier'),
            PpToken.PpToken('(', 'preprocessing-op-or-punc'),
            PpToken.PpToken(')', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('header', 'identifier'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
#        print('Diff')
        self._printDiff(resultTokS, expTokS)
        self.assertEqual(resultTokS, expTokS)


class TestLinuxMacroInTypesH(TestPpLexer):
    """Linux Kernel include/types.h warning that should not be there."""
    ITU_CONTENT = """#ifndef _LINUX_TYPES_H
#define _LINUX_TYPES_H
#ifndef __ASSEMBLY__
#ifdef    __KERNEL__
#define DECLARE_BITMAP(name,bits) \
    unsigned long name[BITS_TO_LONGS(bits)]
#else
#ifndef __EXPORTED_HEADERS__
#warning "Attempt to use kernel headers from user space, see http://kernelnewbies.org/KernelHeaders"
#endif /* __EXPORTED_HEADERS__ */
#endif    /* __KERNEL__ */
#endif /*  __ASSEMBLY__ */
#endif /* _LINUX_TYPES_H */
"""
    def test_00(self):
        """TestLinuxMacroInTypesH.test_00(): A #warning with an undefined macro, there should be a warning:"""
        myLexer = PpLexer.PpLexer(
                 'types.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    self.ITU_CONTENT,
                    {},
                    ),
                preIncFiles=[
                    io.StringIO("\n")
                ],
                diagnostic=CppDiagnostic.PreprocessDiagnosticKeepGoing()
            )
        resultTokS = [t for t in myLexer.ppTokens()]
        myLexer.finalise()
#         print('HERE')
#         print(resultTokS)
#         self.pprintTokensAsCtors(resultTokS)
#         print('HERE')
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        self._printDiff(resultTokS, expTokS)
        self.assertEqual(resultTokS, expTokS)

    def test_01(self):
        """TestLinuxMacroInTypesH.test_01(): A #warning with a defined macro, there should not be a warning:"""
        myLexer = PpLexer.PpLexer(
                 'types.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    self.ITU_CONTENT,
                    {},
                    ),
                preIncFiles=[
                    io.StringIO("#define __EXPORTED_HEADERS__\n")
                ],
                diagnostic=CppDiagnostic.PreprocessDiagnosticKeepGoing()
#                diagnostic=None
            )
        resultTokS = [t for t in myLexer.ppTokens()]
        myLexer.finalise()
#        print
#        print myLexer.macroEnvironment
#        print self.pprintTokensAsCtors(resultTokS)
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
        self._printDiff(resultTokS, expTokS)
        self.assertEqual(resultTokS, expTokS)

class TestLinuxOther(TestPpLexer):
    def test_00(self):
        """Sepecial.test_00()."""

class TestLinuxEvalProblem(TestPpLexer):
    def test_00(self):
        """Testing error in processing linux-3.13/arch/x86/include/asm/irq_vectors.h"""
        content = """#define SPURIOUS_APIC_VECTOR            0xff
/*
 * Sanity check
 */
#if ((SPURIOUS_APIC_VECTOR & 0x0F) != 0x0F)
# error SPURIOUS_APIC_VECTOR definition error
#endif
"""
        myLexer = PpLexer.PpLexer(
                 'irq_vectors.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    content,
                    {},
                    ),
                 )
        tokS = []
        for t in myLexer.ppTokens():
            tokS.append(t)
        result = ''.join([t.t for t in tokS])
#        self.pprintTokensAsCtors(tokS)
#        print('WTF')
#        print(result)
#        print('WTF')
        expectedResult = '\n \n\n'
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        
    def test_01(self):
        """Testing error in processing linux-3.13/include/linux/mm_types.h"""
        content = """#define BITS_PER_LONG 32
#define __AC(X,Y)    (X##Y)
#define _AC(X,Y) __AC(X,Y)
#define PAGE_SIZE (_AC(1,UL) << PAGE_SHIFT)

struct page_frag {
        struct page *page;
#if (BITS_PER_LONG > 32) || (PAGE_SIZE >= 65536)
        __u32 offset;
        __u32 size;
#else
        __u16 offset;
        __u16 size;
#endif
};
"""
        myLexer = PpLexer.PpLexer(
                 'mm_types.h',
                 CppIncludeStringIO(
                    ['.'],
                    ['.'],
                    content,
                    {},
                    ),
                 )
        tokS = []
        for t in myLexer.ppTokens():
            tokS.append(t)
        result = ''.join([t.t for t in tokS])
#        print('Result:\n', result)
#        self.pprintTokensAsCtors(tokS)
        expTokS = [
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('struct', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('page_frag', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('{', 'preprocessing-op-or-punc'),
            PpToken.PpToken('\n        ', 'whitespace'),
            PpToken.PpToken('struct', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('page', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('*', 'preprocessing-op-or-punc'),
            PpToken.PpToken('page', 'identifier'),
            PpToken.PpToken(';', 'preprocessing-op-or-punc'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('__u16', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('offset', 'identifier'),
            PpToken.PpToken(';', 'preprocessing-op-or-punc'),
            PpToken.PpToken('\n        ', 'whitespace'),
            PpToken.PpToken('__u16', 'identifier'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('size', 'identifier'),
            PpToken.PpToken(';', 'preprocessing-op-or-punc'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('\n', 'whitespace'),
            PpToken.PpToken('}', 'preprocessing-op-or-punc'),
            PpToken.PpToken(';', 'preprocessing-op-or-punc'),
            PpToken.PpToken('\n', 'whitespace'),
        ]
#        self._printDiff(self.stringToTokens(result), expTokS)
        self.assertEqual(tokS, expTokS)
        myLexer.finalise()
        
class Special(TestPpLexer):
    def test_00(self):
        """Sepecial.test_00()."""
        myStr = """    Debug::print(Debug::Classes,0,"  New class `%s' (sec=0x%08x)! #tArgLists=%d\\n",
        fullName.data(),root->section,root->tArgLists ? (int)root->tArgLists->count() : -1);
"""
        myLexer = PpLexer.PpLexer(
                 'mt.h',
                 CppIncludeStringIO([], [], myStr, {}),
                 )
        #i = 0
        #for t in myLexer.ppTokens():
        #    print i, t
        #    i += 1
        result = ''.join([t.t for t in myLexer.ppTokens()])
        expectedResult = """    Debug::print(Debug::Classes,0,"  New class `%s' (sec=0x%08x)! #tArgLists=%d\\n",
        fullName.data(),root->section,root->tArgLists ? (int)root->tArgLists->count() : -1);
"""
        self._printDiff(self.stringToTokens(result), self.stringToTokens(expectedResult))
        self.assertEqual(result, expectedResult)
        myLexer.finalise()

class NullClass(TestPpLexer):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerCtor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerLowLevel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerPreDefine))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerNull))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerInvalidDirective))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerDefine))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerDefineFromStandard))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandler_Simple))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandler_NotFound))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandler_IllFormed))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandler_UsrSys))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandler_UsrSys_Conditional))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandler_PreInclude_Includes))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandlerMacro_Simple))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandlerMacro_SimpleUndef))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandler_UsrSys_MacroObject))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandler_UsrSys_MacroFunction))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandler_UsrSys_MultipleDepth))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIncludeHandler_HeaderGuard))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerConditional))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerConditionalProblems))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerConditionalWithState))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerConditional_LowLevel))
    ## When condLevel != 0. We a re not interested in that just yet
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerConditionalAllIncludes))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerError))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerWarning))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerBadMacroDirective))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(C99Rationale))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerFileIncludeGraph))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerFileIncludeGraphReplacement))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerConditionalSpurious))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerFileIncludeRecursion))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerRaiseOnError))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(PpLexerReadOnly))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(PpLexerPragma))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MinimalWhitespace))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Unmaintainable))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerErrorInCondStack))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerMacroLineContinuation))
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDefineEMPTY))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPpLexerHeaderName))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLinux))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLinuxMacroInclude))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLinuxMacroInTypesH))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLinuxEvalProblem))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Special))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestPpLexer.py - A module that tests PpLexer module.
Usage:
python TestPpLexer.py [-lh --help]

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
