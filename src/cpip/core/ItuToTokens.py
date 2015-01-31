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

"""Converts an ITU (i.e. a file like object and tokenises it into extended
preprocessor tokens. This does not act on any preprocessing directives."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import logging

from cpip import ExceptionCpip
from cpip.core import PpLexer
from cpip.core import PpToken
from cpip.core import PpTokeniser
from cpip.util import BufGen
from cpip.util import MultiPassString

class ExceptionItuToTokens(ExceptionCpip):
    pass

ITU_TOKEN_TYPES = PpToken.LEX_PPTOKEN_TYPES + [
        'trigraph',
        PpTokeniser.COMMENT_TYPE_C,
        PpTokeniser.COMMENT_TYPE_CXX,
        'keyword',
        'preprocessing-directive',
        'Unknown',
    ]

class ItuToTokens(PpTokeniser.PpTokeniser):
    """Tokensises a file like object."""
    def __init__(self, theFileObj=None, theFileId=None, theDiagnostic=None):
        super(ItuToTokens, self).__init__(theFileObj, theFileId, theDiagnostic)
        self._mps = MultiPassString.MultiPassString(theFileObj)
        
    @property
    def multiPassString(self):
        return self._mps
        
    def genTokensKeywordPpDirective(self):
        """Process the file and generate tokens.
        This changes the type to a keyword or preprocessing-directive if it can
        do so."""
        self.translatePhases123()
        self._fileLocator.startNewPhase()
        # Token text and token type
        prevNonWs = ''
        for t, tt in self.multiPassString.genWords():
            assert(tt in ITU_TOKEN_TYPES), '%s not in %s' % (tt, str(ITU_TOKEN_TYPES))
            logging.debug('genTokensKeywordPpDirective() "%s", "%s"', t, tt)
            if tt == 'identifier':
                # This could be a keyword or a pre-processing directive,
                # if so then change its type
                # if/else will be confused so track previous '#'
                if prevNonWs == '#' and t in PpLexer.PREPROCESSING_DIRECTIVES:
                    yield t, 'preprocessing-directive'
                elif t in PpTokeniser.CHAR_SET_MAP['lex.key']['keywords']:
                    yield t, 'keyword'
                else:
                    yield t, tt
            # Special case where new/delete are operators but also keywords
            elif t in ('new', 'delete') and tt == 'preprocessing-op-or-punc':
                yield t, 'keyword'
            else:
                yield t, tt
            if tt != 'whitespace':
                prevNonWs = t
            self._fileLocator.update(t)

    def translatePhases123(self):
        self._translatePhase_1()
        self._translatePhase_2()
        self._translatePhase_3()    
    
    def _translatePhase_1(self):
        """Performs translation phase one.
        Note: We do not (yet) support universal-character-name conversion
        so this only does trigraphs."""
        logging.debug('ItuToTokens._translatePhase_1(): start.')
        # Construct a buffer generator
        myBg = BufGen.BufGen(self._mps.genChars())
        self._fileLocator.startNewPhase()
        try:
            i = 0
            while 1:
                # Note: We need to access the array to inch the marker to the
                # current character
                if myBg[i] == PpTokeniser.TRIGRAPH_PREFIX:
                    self._mps.setMarker()
                    if myBg[i+1] == PpTokeniser.TRIGRAPH_PREFIX \
                    and myBg[i+2] in PpTokeniser.TRIGRAPH_TABLE:
                        # Do the trigraph replacement
                        self._mps.removeSetReplaceClear(
                                isTerm=True,
                                theType='trigraph',
                                theRepl=PpTokeniser.TRIGRAPH_TABLE[myBg[i+2]],
                            )
                        i += PpTokeniser.TRIGRAPH_SIZE
                        self._fileLocator.incCol(PpTokeniser.TRIGRAPH_SIZE)
                    else:
                        self._mps.clearMarker()
                        i += 1
                        self._fileLocator.update(myBg[i])
                else:
                    i += 1
                    self._fileLocator.update(myBg[i])
        except IndexError:
            pass
        logging.debug('ItuToTokens._translatePhase_1(): end.')

    def _translatePhase_2(self):
        """Performs translation phase two. This does line continuation markers
        Note: We do not (yet) test for accidental UCN creation."""
        logging.debug('ItuToTokens._translatePhase_2(): start.')
        # Construct a buffer generator
        myBg = BufGen.BufGen(self._mps.genChars())
        self._fileLocator.startNewPhase()
        try:
            i = 0
            while 1:
                # Note: We need to access the array to inch the marker to the
                # current character
                if myBg[i] == '\\':
                    self._mps.setMarker()
                    if myBg[i+1] == '\n':
                        # Remove the continuation marker
                        self._mps.removeMarkedWord(isTerm=True)
                        i += 2
                        self._fileLocator.incLine()
                    else:
                        self._mps.clearMarker()
                        i += 1
                        self._fileLocator.update(myBg[i])
                else:
                    i += 1
                    self._fileLocator.update(myBg[i])
        except IndexError:
            pass
        logging.debug('ItuToTokens._translatePhase_2(): end.')

    def _translatePhase_3(self):
        """Performs translation phase three. Replaces comments and decomposes
        stream into preprocessing tokens."""
        logging.debug('ItuToTokens._translatePhase_3(): start.')
        # Note this is similar to the code in self.genLexPptokenAndSeqWs()
        ofsIdx = 0
        myBg = BufGen.BufGen(self._mps.genChars())
        self._fileLocator.startNewPhase()
        try:
            while 1:
                # Each pass through the loop we find either:
                # - Whitespace
                # - A comment that is converted to whitespace
                # - A preprocessing token
                # Reset the token type
                self._cppTokType = None
                # Poke the BufGen to inch the marker to the current position
                myBg[ofsIdx]
                self._mps.setMarker()
                sliceLen = self._sliceWhitespace(myBg, ofsIdx) \
                    or self._sliceLexComment(myBg, ofsIdx) \
                    or self._sliceLexPptoken(myBg, ofsIdx)
                if sliceLen > 0:
                    # Fix comments to replace them by a comment character
                    if self._cppTokType in PpTokeniser.COMMENT_TYPES:
                        # Turn the comment into a single whitespace
                        myIsTerm = self._cppTokType == PpTokeniser.COMMENT_TYPE_C
                        self._mps.removeSetReplaceClear(
                                isTerm=myIsTerm,
                                theType=self._cppTokType,
                                theRepl=' ')
                    else:
                        myIsTerm = self._cppTokType in (
                                'character-literal',
                                'string-literal',
                                'non-whitespace'
                            )
                        self._mps.setWordType(self._cppTokType, isTerm=myIsTerm)
                    ofsIdx += sliceLen
                else:
                    break
        except IndexError:
            pass
        # Poke input and report if incomplete
        try:
            myBg[ofsIdx]
            self._diagnostic.partialTokenStream(
                'lex.pptoken has unparsed tokens %s' % myBg[ofsIdx:],
                self.fileLocator)
        except IndexError:
            pass
        logging.debug('ItuToTokens._translatePhase_3(): end.')
