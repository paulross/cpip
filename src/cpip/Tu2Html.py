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

"""Converts an initial translation unit to HTML.

TODO: For making anchors in the TU HTML that the conditional include graph
can link to. If we put an <a name="..." on every line most browsers can not
handle that many. What we could do here is to keep a copy of the conditional
include stack and for each token see if it has changed (like the file stack).
If so that write a marker that the conditional graph can later link to.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import os
import logging

from cpip.core import PpTokenCount
from cpip.util import XmlWrite
from cpip.util import HtmlUtils
from cpip import TokenCss

FILE_SHIFT_ACTIONS = ('Starting', 'Holding', 'Back in', 'Ending')
FILE_SHIFT_ACTION_WIDTH = max([len(a) for a in FILE_SHIFT_ACTIONS])

def _adjustFileStack(theS, lexStack, theFileStack, theIntId):
    """Adjust the file stacks and write to the stream."""
    # We add <a name="n"> and <a href="#n+1">...</a>
    # for each starting/holding/back in FILE output when len(theFileStack) == 1 
    # This gives a sort-of forward references for the ITU 
    indentStr = ''
    if lexStack != theFileStack:
        # File stack change so write out the differences
        # Unwind stack because EOF
        flagUnwind = False
        while (len(theFileStack) > len(lexStack)) \
        or (len(theFileStack) > 0 and lexStack[len(theFileStack)-1] != theFileStack[-1]):
            theIntId = _writeFileName(theS, len(theFileStack), theFileStack, 'Ending', theFileStack[-1], theIntId)
            theFileStack.pop()
            flagUnwind = True
        # Wind up stack as necessary
        while len(theFileStack) < len(lexStack):
            indentStr = '.' * (len(theFileStack)-1)
            theS.characters('\n%s' % indentStr)
            if len(theFileStack) > 0:
                theIntId = _writeFileName(theS, 0, theFileStack, 'Holding', theFileStack[-1], theIntId)
            theFileStack.append(lexStack[len(theFileStack)])
            theIntId = _writeFileName(theS, len(theFileStack)-1, theFileStack, 'Starting', lexStack[len(theFileStack)-1], theIntId)
        # Reaffirm the current file
        if flagUnwind and len(theFileStack) > 0:
            theIntId = _writeFileName(theS, len(theFileStack), theFileStack, 'Back in', theFileStack[-1], theIntId)
    return theIntId

def _writeFileName(theS, lenIndent, theFileStack, theAction, theFile, theIntId):
    assert(theAction in FILE_SHIFT_ACTIONS)
    if lenIndent > 0:
        theS.characters('\n%s' % ('.' * lenIndent))
    if len(theFileStack) == 1:
        with XmlWrite.Element(theS, 'a', {'name' : '%d' % theIntId}):
            pass
        theIntId += 1
        with XmlWrite.Element(theS, 'a', {'href' : '#%d' % theIntId}):
            with XmlWrite.Element(theS, 'span', {'class' : 'file'}):
                theS.characters(
                    '# %s FILE: %s' \
                        % ('%*s' % (FILE_SHIFT_ACTION_WIDTH, theAction), os.path.normpath(theFile))
                )
    else:
        with XmlWrite.Element(theS, 'span', {'class' : 'file'}):
            theS.characters(
                '# %s FILE: %s' \
                    % ('%*s' % (FILE_SHIFT_ACTION_WIDTH, theAction), os.path.normpath(theFile))
            )
    return theIntId

def linkToIndex(theS, theIdxPath):
    with XmlWrite.Element(theS, 'p'):
        theS.characters('Return to ')
        with XmlWrite.Element(theS, 'a', {'href' : theIdxPath}):
            theS.characters('Index')
            
def processTuToHtml(theLex, theHtmlPath, theTitle, theCondLevel, theIdxPath):
    """Processes the PpLexer and writes the tokens to the HTML file.
    Returns a PpTokenCount.PpTokenCount()."""
    if not os.path.exists(os.path.dirname(theHtmlPath)):
        os.makedirs(os.path.dirname(theHtmlPath))
    LINE_FIELD_WIDTH = 8
    LINE_BREAK_LENGTH = 100
    # Make a global token counter (this could be got from the file include graph
    # but this is simpler.
    myTokCntr = PpTokenCount.PpTokenCount()
    # Write CSS
    TokenCss.writeCssToDir(os.path.dirname(theHtmlPath))
    # Process the TU
    with XmlWrite.XhtmlStream(theHtmlPath) as myS:
        with XmlWrite.Element(myS, 'head'):
            with XmlWrite.Element(
                myS,
                'link',
                {
                    'href'  : TokenCss.TT_CSS_FILE,
                    'type'  : "text/css",
                    'rel'   : "stylesheet",
                    }
                ):
                pass
            with XmlWrite.Element(myS, 'title'):
                myS.characters(theTitle)
        myIntId = 0
        with XmlWrite.Element(myS, 'body'):
            with XmlWrite.Element(myS, 'h1'):
                myS.characters('Translation Unit: %s' % theLex.tuFileId)
            linkToIndex(myS, theIdxPath)
            with XmlWrite.Element(myS, 'pre'):
                # My copy of the file stack for annotating the output
                myFileStack = []
                indentStr = ''
                colNum = 1
                for t in theLex.ppTokens(incWs=True, minWs=True, condLevel=theCondLevel):
                    #print t
                    logging.debug('Token: %s', str(t))
                    myTokCntr.inc(t, isUnCond=t.isUnCond, num=1)
                    if t.isUnCond:
                        # Adjust the prefix depending on how deep we are in the file stack
                        myIntId = _adjustFileStack(myS, theLex.fileStack, myFileStack, myIntId)
                        indentStr = '.' * len(myFileStack)
                        # Write the token
                        if t.tt == 'whitespace':
                            if t.t != '\n' and colNum > LINE_BREAK_LENGTH:
                                myS.characters(' \\\n')
                                myS.characters(indentStr)
                                myS.characters(' ' * (LINE_FIELD_WIDTH + 8))
                                colNum = 1
                            else:
                                # Line break
                                myS.characters(t.t)
                                ## NOTE: This is removed as the cost to the
                                ## browser is enormous.
                                ## Set a marker
                                #with XmlWrite.Element(myS,
                                #                      'a',
                                #                      {'name' : myTuI.add(theLex.tuIndex)}):
                                #    pass
                        else:
                            if colNum > LINE_BREAK_LENGTH:
                                # Force a break
                                myS.characters('\\\n')
                                myS.characters(indentStr)
                                myS.characters(' ' * (LINE_FIELD_WIDTH + 8))
                                colNum = 1
                            with XmlWrite.Element(myS, 'span', {'class' : TokenCss.retClass(t.tt)}):
                                myS.characters(t.t)
                                colNum += len(t.t)
                        if t.t == '\n' and len(myFileStack) != 0:
                            # Write the line prefix
                            myS.characters(indentStr)
                            myS.characters('[')
                            myS.characters(' ' * (LINE_FIELD_WIDTH - len('%d' % theLex.lineNum)))
                            HtmlUtils.writeHtmlFileLink(
                                    myS,
                                    theLex.fileName,
                                    theLex.lineNum,
                                    '%d' % theLex.lineNum,
                                    theClass=None,
                                )
                            myS.characters(']: ')
                            colNum = 1
            linkToIndex(myS, theIdxPath)
    return myTokCntr
