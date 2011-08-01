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

"""Understands whitespacey things about source code character streams.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'


LEX_WHITESPACE = set('\t\v\f\n ')
LEN_WHITESPACE_CHARACTER_SET = 5
LEX_NEWLINE = '\n'
# Whitespace characters that are significant in define statements
# ISO/IEC 14882:1998(E) 16-2 only ' ' and '\t' as ws
DEFINE_WHITESPACE = set('\n\t ')

class PpWhitespace(object):
    """A class that does whitespacey type things in accordance with
    ISO/IEC 9899:1999(E) Section 6 and ISO/IEC 14882:1998(E)."""
    def sliceWhitespace(self, theBuf, theOfs=0):
        """Returns the length of whitespace characters that are in theBuf from
        position theOfs."""
        i = theOfs
        try:
            # Only access theBuf with [i] so that __getitem__() is called
            while theBuf[i] in LEX_WHITESPACE:
                i += 1
        except IndexError:
            pass
        # NOTE: Return size of slice not the index of the end of the slice
        return i - theOfs

    def sliceNonWhitespace(self, theBuf, theOfs=0):
        """Returns the length of non-whitespace characters that are in
        theBuf from position theOfs."""
        i = theOfs
        try:
            # Only access theBuf with [i] so that __getitem__() is called
            while theBuf[i] not in LEX_WHITESPACE:
                i += 1
        except IndexError:
            pass
        # NOTE: Return size of slice not the index of the end of the slice
        return i - theOfs

    def hasLeadingWhitespace(self, theCharS):
        """Returns True if any leading whitespace, False if zero length or
        starts with non-whitespace."""
        return len(theCharS) > 0 and (theCharS[0] in LEX_WHITESPACE)

    def isAllWhitespace(self, theCharS):
        """Returns True if the supplied string is all whitespace."""
        return len(theCharS) > 0 \
        and self.sliceWhitespace(theCharS) == len(theCharS)

    def isBreakingWhitespace(self, theCharS):
        """Returns True if whitespace leads theChars and that whitespace
        contains a newline."""
        i = 0
        #traceChars = [ord(x) for x in theCharS]
        while i < len(theCharS) \
        and theCharS[i] in LEX_WHITESPACE:
            if theCharS[i] == LEX_NEWLINE:
                return True
            i += 1
        return False

    def isAllMacroWhitespace(self, theCharS):
        """"Return True if theCharS is zero length or only has allowable
        whitespace for preprocesing macros.
        ISO/IEC 14882:1998(E) 16-2 only ' ' and '\t' as whitespace."""
        for c in theCharS:
            if c not in DEFINE_WHITESPACE:
                return False
        return True

    def preceedsNewline(self, theCharS):
        """Returns True if theChars ends with a newline. i.e. this immediately
        precedes a new line."""
        return theCharS.endswith(LEX_NEWLINE)
