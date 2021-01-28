#!/usr/bin/env python
# CPIP is a C/C++ Preprocessor implemented in Python.
# Copyright (C) 2008-2017 Paul Ross
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
# Paul Ross: apaulross@gmail.com

"""Various classes for use by the preprocessor for keeping track of the
location in a set of files.

This consists of three related classes:

:py:class:`LogicalPhysicalLineMap`:

This low-level class maintains and internal theoretical relationship between
the logical position in a string and the physical position. These differ when
physical characters are replaced by logical ones.

This is not usually used directly by other modules.

:py:class:`FileLocation`:

This consists of a stack of one or more LogicalPhysicalLineMap objects each
of which represents a phase of translation. This understands what it means to
replace a trigraph or encounter a line continuation phrase.

Typically this is used by a :py:class:`cpip.core.PpTokensiser.PpTokeniser`.

:py:class:`CppFileLocation`:

This consists of a stack of one or more FileLocation objects each
of which represents an ITU or included file. Conceptually this is a table of
columns (each a FileLocation object) and cells (each a LogicalPhysicalLineMap).
The public API gives access to the 'current' LogicalPhysicalLineMap i.e. the top
right one in the table. The public API allows pushing (adding a column when a
file is #include'd) and popping (removing the last column at the end of
#include processing).

Typically this is used by a :py:class:`cpip.core.PpLexer.PpLexer`.


Using line continuation in :py:class:`LogicalPhysicalLineMap`:


class FileLocation needs to poke the underlying LogicalPhysicalLineMap
in the right way...

This is accomplished by calling from class FileLocation the underlying
:py:meth:`LogicalPhysicalLineMap._addToIr()`

This makes calls occur in N pairs.

N = The number of '\\n' phrases.

L(n) is the length of the physical line n (0 <= n < N) not including the '\\n'

Make N calls to _addIr(...)

NOTE: The use of 1+ and -1* here ``_addToIr(theLogicalLine=a, theLogicalCol=1+b, dLine=c, dColumn=-1*d)``

Where::

    a(n) = The current logical line number (starting at 1), constant for the group
    b(n) = Sigma[L(n) for 0...n)]
    c(n) = 1
    d(n) = L(n)

Examples::

    myPstrS = ['abc\\n', '\\n', 'd\\n', 'ef\\n',]
    N = 3
    L(n) -> (3, 0, 1)
    a = 1, c = 1
    (b, d)
    (3, 3)
    (3, 0)
    (4, 1)

    myPstrS = ['abc\\n', 'd\\n', '\\n', 'ef\\n',]
    N = 3
    L(n) -> (3, 1, 0)
    a = 1, c = 1
    (b, d)
    (3, 3)
    (4, 1)
    (4, 0)

    myPstrS = ['ab\\n', 'c\\n', 'd\\n', 'ef\\n',]
    N = 3
    L(n) -> (2, 1, 1)
    a = 1, c = 1
    (b, d)
    (2, 2)
    (3, 1)
    (4, 1)

The second call of the pair is as follows, this needs to know N so has
to be done after all first-of-pair calls::

    _addToIr(theLogicalLine=d, theLogicalCol=1, dLine=e, dColumn=f)

Where::

    d = n+2 where n is the number of the '\\n' in the group starting at 0
    e = N-n-1 where N is the total number of '\\n' in the group.
    f = Length of the last physical line spliced, not including the '\\n'

Programatically::

    for n in range(N):
        myLplm._addToIr(theLogicalLine=n+2, theLogicalCol=1, dLine=N-n-1, dColumn=f)

In all the examples above f = 2
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__rights__  = 'Copyright (c) 2008-2017 Paul Ross'

import collections

from cpip import ExceptionCpip

class ExceptionFileLocation(ExceptionCpip):
    """Simple specialisation of an exception class for the FileLocation classes."""
    pass

#: See ISO/IEC 14882:1998(E) 16.4 Line control [cpp.line] note 2
#: Means that lines start at 1.
#: We also take the first column to be number 1.
START_LINE   = 1
START_COLUMN = 1

#: Simple PODs for file location for anyone that wants to use them
FileLine = collections.namedtuple(
    'FileLine',
    'fileId lineNum',
    )

FileLineCol = collections.namedtuple(
    'FileLineCol',
    FileLine._fields + ('colNum',),
    )

class LogicalPhysicalLineMap(object):
    """Class that can map logical positions (i.e. after text substitution) back
    to the original physical line columns.
    The effect of various substitutions is as follows:
    
    Phase 1: Trigraph replacement - logical is same or smaller than physical.
    Phase 1: Mapping non lex.charset to universal-character-name - logical is larger than physical.
    Phase 2: Line splicing - if done logical is smaller that physical.
    Phase 3: Digraph replacement - logical is same or smaller that physical.
    """
    def __init__(self):
        # This is a map of:
        # {line_num: [(col, line_increment, col_increment)], ...}
        # Increments are to get from logical to physical number
        self._ir = {}

    def __str__(self):
        prefix = '    '
        retList = ['{line_num: [(col, line_increment, col_increment)], ...}']
        if len(self._ir) == 0:
            retList.append('%s%s' % (prefix, 'Empty'))
        else:
            for aK in sorted(self._ir.keys()):
                retList.append('%s:' % aK)
                for t in self._ir[aK]:
                    retList.append('%s%s' % (prefix, str(t)))
        return '\n'.join(retList)

    def _addToIr(self, theLogicalLine, theLogicalCol, dLine, dColumn):
        """Adds, or updates a record to the internal representation."""
        addTup = (theLogicalCol, dLine, dColumn)
        if theLogicalLine not in self._ir:
            self._ir[theLogicalLine] = [addTup]
        else:
            # Scan for existing entry and update it
            for i, tup in enumerate(self._ir[theLogicalLine]):
                c, dl, dc = tup
                if c == theLogicalCol:
                    # Edit and reinsert
                    dl += dLine
                    dc += dColumn
                    self._ir[theLogicalLine][i] = (c, dl, dc)
                    # Ordered so can break
                    break
            else:
                # No existing entry found so scan for a entry to insert before
                for i, tup in enumerate(self._ir[theLogicalLine]):
                    c, dl, dc = tup
                    if c > theLogicalCol:
                        self._ir[theLogicalLine].insert(i, addTup)
                        break
                else:
                    # Append as no break
                    self._ir[theLogicalLine].append(addTup)

    def substString(self, theLogicalLine, theLogicalCol, lenPhysical, lenLogical):
        """Records a string substitution."""
        self._addToIr(theLogicalLine, theLogicalCol, 0, lenPhysical-lenLogical)

    def pLineCol(self, lLine, lCol):
        """Returns the (physical line number, physical column number) from
        a logical line and logical column.

        :param theLline: Logical line number.
        :type theLline: ``int``

        :param theLcol: Logical column number.
        :type theLcol: ``int``

        :returns: ``tuple([int, int])`` -- Physical line and column.
        """
        pLine = lLine
        pCol = lCol
        if lLine in self._ir:
            for lc, dl, dc in self._ir[lLine]:
                if lCol >= lc:
                    pLine += dl
                    pCol += dc
                else:
                    break
        return pLine, pCol

    def offsetAbsolute(self, theLineCol):
        """Given a pair of integers that represent line/column starting at
        zero this returns a tuple pair of the absolute line/column."""
        return theLineCol[0] + START_LINE, theLineCol[1] + START_COLUMN

    def offsetRelative(self, theLineCol):
        """Given a pair of integers that represent line/column starting at
        START_LINE, START_COLUMN this returns a tuple pair of the relative
        line/column i.e. starting at (0, 0)."""
        return theLineCol[0] - START_LINE, theLineCol[1] - START_COLUMN

class FileLocation(object):
    """Class that persists the line/column location in a source file.
    This also handles various passes of the same file for the PpTokeniser."""
    def __init__(self, theFileName):
        """Initialise with a file name (actually an ID)

        NOTE: We do not check for it's existence as we are not allied to the
        file system (we could get the files from a database instead.

        :param theFileName: File ID for example the file path.
        :type theFileName: ``NoneType, str``

        :returns: ``NoneType``
        """
        self._fileName = theFileName
        self._lineNum = START_LINE
        self._colNum = START_COLUMN
        # This is a stack of LogicalPhysicalLineMap objects, one for each
        # phase of processing
        self._logicalPhysMapStack = [LogicalPhysicalLineMap(), ]
        # Variables that are used internally in line splicing
        # This is the number of line splices seen in a group
        self._lineSpliceCount = 0
        # This is the sigma of the characters spliced
        self._lineSpliceColInc = 0

    def __str__(self):
        retList = ['FileLocation with %d maps:' % len(self._logicalPhysMapStack), ]
        for i in range(len(self._logicalPhysMapStack)-1, -1, -1):
            retList.append('Map [%d]:' % i)
            retList.append(str(self._logicalPhysMapStack[i]))
        return '\n'.join(retList)

    def startNewPhase(self):
        """Starts a new processing phase e.g. a translation phase.
        This adds a new LogicalPhysicalLineMap() to the stack.

        :returns: ``NoneType``
        """
        assert(len(self._logicalPhysMapStack) > 0)
        self._lineNum = START_LINE
        self._colNum = START_COLUMN
        self._logicalPhysMapStack.append(LogicalPhysicalLineMap())

    def retPredefinedMacro(self, theName):
        """Returns the value of __FILE__ or __LINE__.
        Applies ISO/IEC 14882:1998(E) 16 Predefined macro names [cpp.predefined] note 2
        May raise ExceptionFileLocation if theName is something else."""
        if theName == '__FILE__':
            return self.fileName
        elif theName == '__LINE__':
            return '%d' % self.lineNum
        raise ExceptionFileLocation('Unknown predefined macro name "%s"' % theName)

    def logicalToPhysical(self, theLline, theLcol):
        """Returns the physical line and column number for a
        logical line and column.

        :param theLline: Logical line number.
        :type theLline: ``int``

        :param theLcol: Logical column number.
        :type theLcol: ``int``

        :returns: ``tuple([int, int])`` -- Physical line and column.
        """
        assert(len(self._logicalPhysMapStack) > 0)
        retL = theLline
        retC = theLcol
        for i in range(len(self._logicalPhysMapStack)-1, -1, -1):
            retL, retC = self._logicalPhysMapStack[i].pLineCol(retL, retC)
        return retL, retC

    ###############################
    # Section: Getters and setters.
    ###############################
    def retLineNum(self):
        """
        :returns: ``int`` -- Line number.
        """
        return self._lineNum

    def setLineNum(self, theNum):
        self._lineNum = theNum

    lineNum = property(retLineNum, setLineNum)

    def retColNum(self):
        """
        :returns: ``int`` -- Column number.
        """
        return self._colNum

    def setColNum(self, theNum):
        self._colNum = theNum

    colNum = property(retColNum, setColNum)

    @property
    def fileName(self):
        """
        :returns: ``str`` -- <insert documentation for return values>
        """
        return self._fileName

    @property
    def pLineCol(self):
        """Returns the current physical line and column number.

        :returns: ``tuple([int, int])`` -- Location.
        """
        assert(len(self._logicalPhysMapStack) > 0)
        return self.logicalToPhysical(self._lineNum, self._colNum)

    @property
    def lineCol(self):
        """Returns the current line and column number as a pair."""
        assert(len(self._logicalPhysMapStack) > 0)
        return self._lineNum, self._colNum

    @property
    def lineSpliceCount(self):
        """The number of line splices in the current splice group."""
        return self._lineSpliceCount
    
    def fileLineCol(self):
        """Return an instance of FileLineCol from the current settings.

        :returns: :py:class:`cpip.core.FileLocation.FileLineCol([str, int, int])`
            -- File location.
        """
        pLine, pCol = self.pLineCol
        return FileLineCol(self.fileName, pLine, pCol)
    ###############################
    # End: Getters and setters.
    ###############################

    ########################################################################
    # Section: Incrementers.
    # This section contains methods that the caller can use each time they
    # process a token. The self object will keep track of which logical line
    # and column the processing is in.
    ########################################################################
    def incCol(self, num=1):
        """Increment the column by num. There is no range check on num.

        :param num: Amount to increment, default 1.
        :type num: ``int``

        :returns: ``NoneType``
        """
        self._colNum += num

    def incLine(self, num=1):
        """Increment the line by num. There is no range check on num.

        :param num: Amount to increment, default 1.
        :type num: ``int``

        :returns: ``NoneType``
        """
        self._lineNum += num
        if num:
            self._colNum = START_COLUMN

    def update(self, theString):
        """Increment line and column counters from a string.

        :param theString: Source code.
        :type theString: ``str``

        :returns: ``NoneType``
        """
        self.incLine(theString.count('\n'))
        self.incCol(len(theString) - theString.rfind('\n') - 1)

    @property
    def logicalPhysicalLineMap(self):
        """Return the current top level LogicalPhysicalLineMap Read Only instance."""
        assert(len(self._logicalPhysMapStack) > 0)
        return self._logicalPhysMapStack[-1]

    def substString(self, lenPhysical, lenLogical):
        """Records a string substitution at the current logical location.
        This does NOT update the current line or column, use update(...) to do that."""
        self._logicalPhysMapStack[-1].substString(self.lineNum, self.colNum, lenPhysical, lenLogical)

    def setTrigraph(self):
        """Records that a trigraph has be substituted at the current place."""
        # Note hard coded lengths of trigraph and their substitute
        myTriLen = 3
        self._logicalPhysMapStack[-1].substString(self.lineNum, self.colNum+1, myTriLen, 1)
        
    def spliceLine(self, thePhysicalLine):
        """Update the line/column mapping to record a line splice."""
        assert(thePhysicalLine.endswith('\\\n'))
        lP = len(thePhysicalLine)-len('\\\n')
        if self._lineSpliceCount == 0:
            self._lineSpliceColInc = lP
        else:
            self._lineSpliceColInc += lP
        self.logicalPhysicalLineMap._addToIr(
                            theLogicalLine=self.lineNum,
                            theLogicalCol=1+self._lineSpliceColInc,
                            dLine=1,
                            dColumn=-1*lP,
                            )
        self._lineSpliceCount +=1
        self._colNum += lP

    ####################
    # End: Incrementers.
    ####################

    ########################
    # Section: Test support.
    ########################

    def pformatLogicalToPhysical(self, theLfile, thePfile):
        """Given a logical and a physical representation this goes through
        character by both character, pretty formats the comparison and
        returns the formatted string."""
        strList = ['Logical -> Physical']
        for rLl in range(len(theLfile)):
            for rLc in range(len(theLfile[rLl])):
                absLogPair = self.logicalPhysicalLineMap.offsetAbsolute((rLl, rLc))
                pLine, pCol = self.logicalPhysicalLineMap.pLineCol(absLogPair[0], absLogPair[1])
                rPl, rPc = self.logicalPhysicalLineMap.offsetRelative((pLine, pCol))
                if rLc == 0 and theLfile[rLl][rLc] == '\n':
                    myPchar = '\n'
                else:
                    myPchar = thePfile[rPl][rPc]
                if myPchar == '\n':
                    myPchar = '\\n'
                myLchar = theLfile[rLl][rLc]
                if myLchar == '\n':
                    myLchar = '\\n'
                if myLchar != myPchar:
                    theMsg = '%s != %s' % (myLchar, myPchar)
                else:
                    #theMsg = 'OK'
                    theMsg = '%s == %s' % (myLchar, myPchar)
                strList.append('%s -> %s %s' % (str(absLogPair), str((pLine, pCol)), theMsg))
        return '\n'.join(strList)

    ####################
    # End: Test support.
    ####################
