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

"""Converts an ITU to HTML.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import logging
import collections

from cpip import ExceptionCpip

class ExceptionMultiPass(ExceptionCpip):
    pass

Word = collections.namedtuple(
    'Word',
    'wordLen wordType',
    )

class MultiPassString(object):
    """Reads a file, the file can be translated any number of times and marked
    with word types. The latter can then be generated using BufGen for example:
    myBg = BufGen.BufGen(self._mps.genChars())
    try:
        i = 0
        while 1:
            print myBg[i]
            i += 1
    except IndexError:
        pass
    """
    UNKNOWN_TOKEN_TYPE = 'Unknown'
    EMPTY_TOKEN = ''
    MARKER_CLEAR = -1
    def __init__(self, theFileObj):
        # This is a map {int : class Word, ...}
        # Where int is the index, len the word length and type the word type
        self._idxTypeMap = {}
        self._origStr = theFileObj.read()
        # This is a list of char, string or None
        # empty string - char has been replaced by something smaller
        # one char string - normal.
        # longer string - char has been replaced by something bigger
        # The length of this is always the length of self._origStr 
        self._current = list(self._origStr)
        self._idxGenChar = self._retZeroIndex()
        self._idxMarker = self.MARKER_CLEAR
        # Helper API, this is the previously generated character
        self._prevChar = ''

    def _retZeroIndex(self):
        """Returns the index to the first non-empty token in the current list."""
        i = 0
        while i < len(self._current):
            # if len(self._current[i]) > 0: might be a bit faster but
            # less consistent/readable
            if self._current[i] != self.EMPTY_TOKEN:
                break
            i += 1
        return i 

    #==============================
    # Section: Read-only properties
    #==============================
    @property
    def idxChar(self):
        return self._idxGenChar    

    @property
    def idxCharStart(self):
        return self._retZeroIndex()

    @property
    def currentString(self):
        return self._current
    
    @property
    def idxTypeMap(self):
        return self._idxTypeMap
    
    @property
    def prevChar(self):
        """The previous character of the input.
        A slight nod to K&R this is (not) a bit like putc()."""
        return self._prevChar

    #==============================
    # End: Read-only properties
    #==============================

    #========================================
    # Section: Markers and setting at marker.
    #========================================
    def setMarker(self):
        """Sets a mark at this point in the input."""
        logging.debug('MultiPassString.setMarker() at %d', self._idxGenChar)
        self._idxMarker = self._idxGenChar

    def clearMarker(self):
        """The mark at this point in the input."""
        self._idxMarker = self.MARKER_CLEAR

    @property
    def wordLength(self):
        """The length of the current word."""
        if self._idxMarker == self.MARKER_CLEAR:
            return 0
        return self._idxGenChar - self._idxMarker

    @property
    def hasWord(self):
        """True if the length of the current word is > 0."""
        return self.wordLength > 0

    def setWordType(self, theType, isTerm):
        """Marks a word in the input as a word of type theType starting from the
        marker up to the current place.
        See removeMarkedWord() for an explanation of isTerm."""
        logging.debug('MultiPassString.setWordType() "%s", isTerm=%s', theType, isTerm)
        if self._idxMarker == self.MARKER_CLEAR:
            raise ExceptionMultiPass('setWordType(): when no marker present.')
        if self._idxTypeMap.has_key(self._idxMarker):
            raise ExceptionMultiPass('setWordType(): Duplicate key: %s' % self._idxMarker)
        myLen = self.wordLength
        if isTerm:
            myLen += 1
        if myLen <= 0:
            raise ExceptionMultiPass('Marking word with illegal length: %s' % myLen)
        self._idxTypeMap[self._idxMarker] = Word(wordLen=myLen, wordType=theType)

    def removeMarkedWord(self, isTerm):
        """Remove the current marked word. isTerm is a boolean that is True
        if the current position is a terminal character.
        For example if you want to split a string into lines then \\n is a
        terminal character and you would call this with isTerm=True.
        However if you were splitting a string into words and whitespace then
        a whitespace following a word is not the terminal character so at the
        pint of receiving the whitespace character you would call this with
        isTerm=False
        """
        if self._idxMarker == self.MARKER_CLEAR:
            raise ExceptionMultiPass('removeMarkedWord(): when no marker present.')
        # NOTE: Do not manipulate self._idxMarker here as a typical use case
        # is to replace by calling removeMarkedWord() and then setAtMarker().
        # Changing self._idxMarker here would cause errors for setAtMarker.
        myLen = self.wordLength
        if isTerm:
            myLen += 1
        if myLen <= 0:
            raise ExceptionMultiPass('removeMarkedWord() with illegal length: %s' % myLen)
        logging.debug(
            'MultiPassString.removeMarkedWord() removing "%s" length=%d',
            self._current[self._idxMarker:self._idxMarker+myLen],
            myLen,
        )
        for l in range(myLen):
            self.__set(self._idxMarker+l, self.EMPTY_TOKEN)
    
    def setAtMarker(self, theRepl):
        """Sets the token at the current marker to be theRepl."""
        if self._idxMarker == self.MARKER_CLEAR:
            raise ExceptionMultiPass('setAtMarker(): when no marker present.')
        self._current[self._idxMarker] = theRepl
        
    def __set(self, idx, repl):
        assert(len(self._origStr) == len(self._current))
        if idx > self._idxGenChar:
            raise ExceptionMultiPass(
                'Marking word at %s when generator only at index=%s' \
                    % (idx, self._idxGenChar)
            )
        self._current[idx] = repl
    
    def removeSetReplaceClear(self, isTerm, theType, theRepl):
        """This provides a helper combination function for a common operation of:
        - Removing the marked word from the output.
        - Setting the word type in the input.
        - Replacing the marked word with a replacement string.
        - Clearing the current marker.
        See removeMarkedWord() for an explanation of isTerm and theType.
        See setAtMarker() for an explanation of theRepl."""
        self.removeMarkedWord(isTerm=isTerm)
        self.setWordType(theType, isTerm=isTerm)
        self.setAtMarker(theRepl)
        self.clearMarker()
    #==============================
    # End: Markers and setting at marker.
    #==============================

    #==============================
    # Section: Generators
    #==============================
    def genChars(self):
        """Generates the current set of characters.
        This can be used as the generator for the BufGen and that BufGen can
        be passed to the PpTokeniser _slice... Functions."""
        assert(len(self._origStr) == len(self._current))
        self._prevChar = ''
        self._idxGenChar = self._retZeroIndex()
        for v in self._current:
            for c in v:
                yield c
                self._prevChar = c 
            self._idxGenChar += 1

    def genWords(self):
        """Generates pairs (word, type) from the original string.
        TODO: Solve the overlap problem."""
        idx = 0
        k = 0
        keys = self._idxTypeMap.keys()
        keys.sort()
        for k in keys:
            if k > idx:
                logging.debug(
                    'MultiPassString.genWords() 0: k=%d, idx=%d, str="%s" type="%s"',
                    k,
                    idx,
                    self._origStr[idx:k],
                    self.UNKNOWN_TOKEN_TYPE,
                )
                yield self._origStr[idx:k], self.UNKNOWN_TOKEN_TYPE
            elif k < idx:
                raise ExceptionMultiPass('Overlap: from %s to %s' % (k, idx))
            w = self._idxTypeMap[k]
            assert(w.wordLen > 0)
            idx = k + w.wordLen
            logging.debug(
                'MultiPassString.genWords() 1: k=%d, idx=%d, str="%s" type="%s"',
                k,
                idx,
                self._origStr[k:idx],
                w.wordType,
            )
            yield self._origStr[k:idx], w.wordType
        # Finally the tail
        if k+idx < len(self._origStr):
            logging.debug(
                'MultiPassString.genWords() 2: k=%d, idx=%d, str="%s" type="%s"',
                k,
                idx,
                self._origStr[k+idx:],
                self.UNKNOWN_TOKEN_TYPE,
            )
            yield self._origStr[k+idx:], self.UNKNOWN_TOKEN_TYPE

    #==============================
    # End: Generators
    #==============================
