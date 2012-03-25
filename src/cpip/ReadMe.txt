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

CPIP - A 'C' Preprocessor Implemented in Python

2009-04-01
----------
TODO List
Accidental token pasting.


DONE: Tokens have a flag that says this token is unconditionally compiled.
This way we can still yield the token and the caller can ignore it.
Or the caller can specify whether it wants these tokens.
The caller can see the conditional state of the lexer when the caller sees
a conditional flag.


DONE: Support for detecting whether a string ends with a '\n' as '#' can only
appear after that.


Code coverage and testing
=========================

p2ross@4GBL06045 /cygdrive/c/wip/small_projects/PreProcess2.0/cpip/core
$ coverage -e

coverage -x test/UnitTests.py

coverage -b -d ../../htmlcov/

coverage -r -m <Module.py>

pylint checking:
================

p2ross@4GBL06045 /cygdrive/c/wip/small_projects/PreProcess2.0/cpip/core
$ pylint.bat --rcfile="C:\Python26\Scripts\pylint_sysdoc" PpToken.py


Clearing PyLint history:

p2ross@4GBL06045 /cygdrive/c/wip/small_projects/PreProcess2.0/cpip/core
$ ls ~/.pylint.d/
PpDefine1.stats  PpLexer1.stats  PpToken1.stats

p2ross@4GBL06045 /cygdrive/c/wip/small_projects/PreProcess2.0/cpip/core
$ ls -la /cygdrive/c/Documents\ and\ Settings/p2ross/.pylint.d/
total 12
drwx------+  2 p2ross         mkgroup-l-d    0 Jul  8 18:48 .
drwxrwx---+ 23 Administrators SYSTEM         0 Jul 14 16:49 ..
-rwx------+  1 p2ross         mkgroup-l-d 1590 Jul  8 18:51 PpDefine1.stats
-rwx------+  1 p2ross         mkgroup-l-d 1573 May 26 19:41 PpLexer1.stats
-rwx------+  1 p2ross         mkgroup-l-d 1158 Jul 14 18:41 PpToken1.stats


p2ross@4GBL06045 /cygdrive/c/wip/small_projects/PreProcess2.0/cpip/core
$ rm -r /cygdrive/c/Documents\ and\ Settings/p2ross/.pylint.d/

p2ross@4GBL06045 /cygdrive/c/wip/small_projects/PreProcess2.0/cpip/core
$ pylint.bat --rcfile="C:\Python26\Scripts\pylint_sysdoc" PpToken.py

2009-07-06
==========
Lessons learnt developing this and in this way:

- Goals can drift around if you are not careful.



2009-08-12
==========
Phases of translation from ISO/IEC 9899:1999 (E):

5.1.1.2 Translation phases
1 The precedence among the syntax rules of translation is specified by the following
phases.

Phase 1. Physical source file multibyte characters are mapped, in an implementation defined
manner, to the source character set (introducing new-line characters for
end-of-line indicators) if necessary. Trigraph sequences are replaced by
corresponding single-character internal representations.

Phase 2. Each instance of a backslash character (\) immediately followed by a new-line
character is deleted, splicing physical source lines to form logical source lines.
Only the last backslash on any physical source line shall be eligible for being part
of such a splice. A source file that is not empty shall end in a new-line character,
which shall not be immediately preceded by a backslash character before any such
splicing takes place.

Phase 3. The source file is decomposed into preprocessing tokens6) and sequences of
white-space characters (including comments). A source file shall not end in a
partial preprocessing token or in a partial comment. Each comment is replaced by
one space character. New-line characters are retained. Whether each nonempty
sequence of white-space characters other than new-line is retained or replaced by
one space character is implementation-defined.

Phase 4. Preprocessing directives are executed, macro invocations are expanded, and
_Pragma unary operator expressions are executed. If a character sequence that
matches the syntax of a universal character name is produced by token
concatenation (6.10.3.3), the behavior is undefined. A #include preprocessing
directive causes the named header or source file to be processed from phase 1
through phase 4, recursively. All preprocessing directives are then deleted.

Phase 5. Each source character set member and escape sequence in character constants and
string literals is converted to the corresponding member of the execution character
set; if there is no corresponding member, it is converted to an implementationdefined
member other than the null (wide) character.7)

Phase 6. Adjacent string literal tokens are concatenated.

Phase 7. White-space characters separating tokens are no longer significant. Each
preprocessing token is converted into a token. The resulting tokens are
syntactically and semantically analyzed and translated as a translation unit.

Phase 8. All external object and function references are resolved. Library components are
linked to satisfy external references to functions and objects not defined in the
current translation. All such translator output is collected into a program image
which contains information needed for execution in its execution environment.

Footnote 5) Implementations shall behave as if these separate phases occur, even though many are typically folded
together in practice.



2009-08-14
==========
Documentation and standards.
Important sections of 'C99' [ISO/IEC 9899:1999 (E)]

5.1.1.2 Translation phases
Describes translation phases 1, 2, 3
This is handled by, among others:
FileLocation.py
MatrixRep.py
PpTokeniser.py

6.4 Lexical elements
How translation phase 3 is decomposed into preprocessing tokens.
This is handled by, among others:
FileLocation.py
MatrixRep.py
PpToken.py
PpTokeniser.py

6.6 Constant expressions
We are a bit casual with this or are we?
This handled by ConstantExpression.py

6.10 Preprocessing directives
How these are handled, this is handled by, among others:
CppCond.py
IncludeHandler.py
MacroEnv.py
MacroTraceabilityIdeas.py
PpDefine.py
PpLexer.py


2009-09-21 [Revision 45]
========================
OK now builds the Kernel and (everything else?).

- Conditional state of include graph is wonky e.g.
    (True "[" ", "0", " "] && [" ", "0", " "]" etc.)

- PpLexer.ppTokens() make incCond (0, 1, 2) to handle different use cases
    (see _cppInclude where we check if self._condStack.isTrue():).

- Sig tokens should count #define/#undef so that the HRH is 'significant'
    Need a better file stack class in PpLexer?

- HTML a file with a variant of the PpTokeniser that handles comments, line
    splice markers, keywords pp-directives etc. This could use MaxMunchGen.

- We are overcounting include tokens in FileInclude that recurses when the
    upper level already includes the lower levels.
    
- Performance: profiling fingers the PpTokensiser, particularly:
    _sliceLongestMatchingWord() -> Use StrTree? [DONE]
    _sliceLexName()             -> ?
    _sliceLexOperators()        -> Use StrTree? [DONE]
    _translateTrigraphs()       -> Use MatrixRep? [DONE]
    _convertToLexCharset()      -> Use MatrixRep? [DONE]

- Need to set up a good all-round performance test.

$ python test/TestPpTokeniserPerf.py
TestPpLexer.py script version "0.8.0", dated 2009-09-15
Author: Paul Ross
Copyright (c) Paul Ross

TestPpTokeniserOverall: test_00() x   1. ... Count:      210, Rate:  15546.2 tokens/s ... ok
TestPpTokeniserOverall: test_00() x  10. ... Count:     2100, Rate:  14008.5 tokens/s ... ok
TestPpTokeniserOverall: test_00() x 100. ... Count:    21000, Rate:  12772.7 tokens/s ... ok
TestPpTokeniserOverall: test_00() x 200. ... Count:    42000, Rate:  11202.1 tokens/s ... ok

Use StrTree in _sliceLexOperators():
p2ross@4GBL06595 /cygdrive/c/wip/small_projects/cpip/src/cpip/core
$ python test/TestPpTokeniserPerf.py
TestPpLexer.py script version "0.8.0", dated 2009-09-15
Author: Paul Ross
Copyright (c) Paul Ross

TestPpTokeniserOverall: test_00() x   1. ... Count:      210, Rate:  33461.1 tokens/s ... ok
TestPpTokeniserOverall: test_00() x  10. ... Count:     2100, Rate:  26850.7 tokens/s ... ok
TestPpTokeniserOverall: test_00() x 100. ... Count:    21000, Rate:  23212.6 tokens/s ... ok

Twice as fast!
Overall effect:
PreProcBrdResult_a3facf_01.txt: Preprocess time:  102.936 (S)
PreProcBrdResult_a3facf_02.txt: Preprocess time:   82.620 (S)

Refactor _sliceUniversalCharacterName() - no sig diff.
Refactor translate trigraphs - very small improvement.

Various faffing around with PpTokeniser, some improvement (maybe 5-10%).

We are, as expected, not going to compete with cpp on performance so lets
concentrate on what we are good at.


2009-10-14
==========
TODO: See below
HTMLWriter is becoming essential so XMLWriter is also becoming essential.
SVGWriter follows on from that.
Decide on structure? utils/ has writers? Or new directory out/? output/? plot?
ItuToHtml is immature.

DictTree has HTML rowspan/colspan support.
DictTree has more coverage.

2009-10-28
==========
Trying to improve the flexibility (and performance) of the PpTokeniser with generators.

Low-level (Phase 0) performance:
--------------------------------

1) Read file completely

    def lexPhases_0(self):
        try:
            self._rewindFile()
            return self._file.readlines()
        except Exception, err:
            raise ExceptionCpipTokeniser(str(err))

This runs at:
TestPpTokeniserLexPhases: Phase 0 with "spam\n" *      2. ... Rate:   1456.5 kb/s ... ok
TestPpTokeniserLexPhases: Phase 0 with "spam\n" *      4. ... Rate:   2913.0 kb/s ... ok
TestPpTokeniserLexPhases: Phase 0 with "spam\n" *     10. ... Rate:   6722.4 kb/s ... ok
TestPpTokeniserLexPhases: Phase 0 with "spam\n" *    100. ... Rate:  26889.6 kb/s ... ok
TestPpTokeniserLexPhases: Phase 0 with "spam\n" *   1000. ... Rate:  66710.9 kb/s ... ok
TestPpTokeniserLexPhases: Phase 0 with "spam\n" *  10000. ... Rate: 102212.0 kb/s ... ok
TestPpTokeniserLexPhases: Phase 0 with "spam\n" * 100000. ... Rate:  62096.3 kb/s ... ok

2) Read file line by line
    def genStrTypRep_0(self):
        try:
            self._rewindFile()
            for line in self._file:
                yield line
        except Exception, err:
            raise ExceptionCpipTokeniser(str(err))

TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *      1. ... Rate:      0.3 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *      2. ... Rate:   1165.2 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *      4. ... Rate:   2589.4 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *     10. ... Rate:   5462.0 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *    100. ... Rate:  20089.9 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *   1000. ... Rate:  29325.9 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *  10000. ... Rate:  34473.9 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" * 100000. ... Rate:  28509.4 kb/s ... ok
i.e about 1/3 the speed of (1)
            
            
3) Read file byte by byte
    def genStrTypRep_0(self):
        try:
            while 1:
                b = self._file.read(1)
                if len(b) != 0:
                    yield b
                else:
                    break
        except Exception, err:
            raise ExceptionCpipTokeniser(str(err))

TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *      1. ... Rate:    230.0 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *      2. ... Rate:    743.8 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *      4. ... Rate:   1146.1 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *     10. ... Rate:   1696.9 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *    100. ... Rate:   2333.5 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *   1000. ... Rate:   2454.1 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *  10000. ... Rate:   2445.4 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" * 100000. ... Rate:   2348.1 kb/s ... ok
i.e about 1/10 the speed of (2) and 1/30 the speed of (1)

4) Read file byte by byte yielding StrTypRep objects

    def genStrTypRep_0(self):
        try:
            while 1:
                b = self._file.read(1)
                if len(b) != 0:
                    yield StrTypRep(b, STR_TYP_REP_CHAR, None)
                else:
                    break
        except Exception, err:
            raise ExceptionCpipTokeniser(str(err))

TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *      1. ... Rate:    422.9 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *      2. ... Rate:   1310.9 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *      4. ... Rate:   1487.5 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *     10. ... Rate:   2024.5 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *    100. ... Rate:   1922.1 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *   1000. ... Rate:   2207.1 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" *  10000. ... Rate:   2054.6 kb/s ... ok
TestPpTokeniser_run_genStrTypRep_0: Phase 0 with "spam\n" * 100000. ... Rate:   1520.9 kb/s ... ok
i.e. about 2/3 the speed of (3), 1/14 the speed of (2) and 1/40 the speed of (1)
            

2010-03-15
==========

