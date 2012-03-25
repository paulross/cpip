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

"""Writes out a macro history in HTML."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import os
import types

#from cpip.core import PpTokenCount
from cpip.util import XmlWrite
from cpip.util import HtmlUtils
from cpip.util import DictTree
from cpip import TokenCss

# Anchors
# Each macro in the table has the ID #macro_name
# Each macro that is the first of a letter ID #a.first_letter_of_macro_name
# Each macro history section has the ID #history.macro_name
ANCHOR_MACRO_ALPHA = 'a'
#ANCHOR_MACRO_HISTORY = 'history'
#ANCHOR_MACRO_TABLE = 'macro_table'
#ANCHOR_MACRO_HISTORY_SECTION = 'macro_history_section'

TITLE_ANCHOR_LINKTEXT_MACROS_TABLE = (
        'Macro Environment (all macros, alphabetical):',
        'macro_table',
        'Environment'
    )
TITLE_ANCHOR_LINKTEXT_MACROS_HISTORY = (
        'Macro Usage (referenced macros only)',
        'history',
        'usage'
    )
TITLE_ANCHOR_LINKTEXT_MACROS_IN_SCOPE = (
        'Macros In Scope',
        'Macros_In_Scope',
        'usage'
    )
TITLE_ANCHOR_LINKTEXT_MACROS_TESTED_WHEN_NOT_DEFINED = (
        'Macros Tested When Not Defined',
        'Macros_Never_Def',
        'tested'
    )

def writeTd(theStream, theStr):
    """Write a <td> element and contents."""
    with XmlWrite.Element(theStream, 'td'):
        theStream.characters(theStr)
            
def writeTh(theStream, theStr):
    """Write a <th> element and contents."""
    with XmlWrite.Element(theStream, 'th'):
        theStream.characters(theStr)
            
def _retMacroId(theMacro, theIndex=None):
    if theIndex is not None:
        return '%s_%d' % (theMacro.strIdentPlusParam(), theIndex)
    return theMacro.strIdentPlusParam()

def _writeTableOfMacros(theS, theEnv, theHtmlPath):
    """Writes the table of macros, where they are defined, their ref count etc.""" 
    # Return value is a map of {identifier : href_text, ...) to link to macro definitions.
    retVal = {}
    # Write table of all macros
    myMacroMap = theEnv.macroHistoryMap()
    myMacroNameS = list(myMacroMap.keys()) 
    if len(myMacroNameS) == 0:
        return retVal
    myMacroNameS.sort()
    # Now write tables of information
    with XmlWrite.Element(theS, 'a', {'name' : TITLE_ANCHOR_LINKTEXT_MACROS_TABLE[1]}):
        pass
    with XmlWrite.Element(theS, 'h1'):
        theS.characters(TITLE_ANCHOR_LINKTEXT_MACROS_TABLE[0])
    with XmlWrite.Element(theS, 'table', {
                                          'border' : "4",
                                          'cellspacing' : "2",
                                          'cellpadding' : "8",
                                          }):
        with XmlWrite.Element(theS, 'tr'):
            writeTh(theS, 'Declaration')
            writeTh(theS, 'Declared In')
            writeTh(theS, 'Ref. Count')
            writeTh(theS, 'Defined?')
        startLetter = ''
        for aMacroName in myMacroNameS:
            myUndefIdxS, isDefined = myMacroMap[aMacroName]
            # Write the undefined ones
            for anIndex in myUndefIdxS:
                myMacro = theEnv.getUndefMacro(anIndex)
                startLetter = writeTrMacro(theS, theHtmlPath, myMacro, anIndex, startLetter, retVal) 
            # Now the defined one
            if isDefined:
                myMacro = theEnv.macro(aMacroName)
                startLetter = writeTrMacro(theS, theHtmlPath, myMacro, len(myUndefIdxS), startLetter, retVal) 
    with XmlWrite.Element(theS, 'br'):
        pass
    # End: write table of all macros
    return retVal

def writeTrMacro(theS, theHtmlPath, theMacro, theIntOccurence, theStartLetter, retMap):
    """Write the macro as a row in the general table.
    theMacro is a PpDefine object."""
    with XmlWrite.Element(theS, 'tr'):
        if theMacro.identifier[0] != theStartLetter:
            theStartLetter = theMacro.identifier[0]
            writeTdMacro(theS, theMacro, theStartLetter, theIntOccurence)
        else:
            writeTdMacro(theS, theMacro, '', theIntOccurence)
        if theMacro.identifier not in retMap:
            # Add to the return value
            retMap[theMacro.identifier] = '%s#%s' \
                % (
                    os.path.basename(theHtmlPath),
                    _retMacroId(theMacro, theIntOccurence),
                )
        with XmlWrite.Element(theS, 'td'):
            HtmlUtils.writeHtmlFileLink(
                    theS,
                    theMacro.fileId,
                    theMacro.line,
                    '%s#%d' % (theMacro.fileId, theMacro.line),
                    'file_decl'
                )
        writeTdRefCount(theS, theMacro)
        writeTdMonospace(theS, str(theMacro.isCurrentlyDefined))
    return theStartLetter

def writeTdMacro(theS, theDef, startLetter, theIntOccurence):
    """Write the macro cell in the general table. theDef is a PpDefine object."""
    if len(theDef.strReplacements()):
        myReplStr = splitLine(' '.join([theDef.strIdentPlusParam(), theDef.strReplacements()]))[len(theDef.strIdentPlusParam()):]
    else:
        myReplStr = ''
    with XmlWrite.Element(theS, 'td'):
        if startLetter:
            with XmlWrite.Element(
                    theS,
                    'a',
                    {'name' : '%s.%s' % (ANCHOR_MACRO_ALPHA, startLetter)}):
                pass
        # Set an anchor
        with XmlWrite.Element(
                theS,
                'a',
                {'name' : _retMacroId(theDef, theIntOccurence)}):
            pass
        # Write the enclosing <span> element depending on the macro properties
        spanClass = 'macro'
        if theDef.isCurrentlyDefined:
            spanClass += '_s_t'
        else:
            spanClass += '_s_f'
        if theDef.refCount > 0:
            spanClass += '_r_t'
        else:
            spanClass += '_r_f'
        # Now definition and replacement list
        with XmlWrite.Element(theS, 'span', {'class' : spanClass + '_name'}):
            theS.characters(theDef.strIdentPlusParam())
        if myReplStr:
            with XmlWrite.Element(theS, 'span', {'class' : spanClass + '_repl'}):
                theS.charactersWithBr(myReplStr)
            
def writeTdMonospace(theStream, theStr):
    with XmlWrite.Element(theStream, 'td'):
        with XmlWrite.Element(theStream, 'span', {'class' : 'monospace'}):
            theStream.characters(theStr)

def writeTdRefCount(theS, theMacro):
    with XmlWrite.Element(theS, 'td'):
        with XmlWrite.Element(theS, 'span', {'class' : 'monospace'}):
            if theMacro.refCount > 0:
                # Write a link to the history
                with XmlWrite.Element(
                            theS,
                            'a', 
                            {
                                'href' : '#%s' % XmlWrite.nameFromString(macroId(theMacro))
                            }
                        ):
                    theS.characters(str(theMacro.refCount))
            else:
                theS.characters(str(theMacro.refCount))

def splitLineToList(sIn):
    """Splits a long string into a list of lines. This tries to do it nicely at
    whitespaces but will force a split if necessary."""
    splitLen = 60
    # This forces a split here, if zero or negative then do not split.
    splitLenHard = 80
    sIn = sIn.strip()
    if len(sIn) <= splitLen:
        return [sIn, ]
    strS = []
    while len(sIn) > splitLen:
        myStr = sIn[:splitLen]
        iMy = myStr.rfind(' ')
        iIn = sIn.find(' ', splitLen)
        if iIn == -1:
            iIn = len(sIn)
        if iMy != -1:
            if (len(myStr) - iMy) >= (iIn - splitLen):
                # Consume more of sIn
                myStr = sIn[:iIn]
            else:
                # Consume less of sIn
                myStr = sIn[:iMy]
        elif iIn != -1:
            # Consume more of sIn
            myStr = sIn[:iIn]
        else:
            myStr = sIn
        # Force split at 'hard' edge if too long
        if splitLenHard > 0 and len(myStr) > splitLenHard:
            myStr = myStr[:splitLenHard]
            inLenConsumed = splitLenHard
            myStr += '\\'
        else:
            # Soft Split
            inLenConsumed = len(myStr)
            myStr += ' \\'
        # Update the input
        sIn = sIn[inLenConsumed:]
        # Clean leading and trailing whitespace
        myStr = myStr.strip()
        strS.append(myStr)
        sIn = sIn.strip()
    if sIn:
        strS.append(sIn)
    return strS

def splitLine(theStr):
    """Splits a long string into string that is a set of lines with continuation characters."""
    return '\n    '.join(splitLineToList(theStr))

def macroId(theMacro):
    return '%s_%s#%d' % (theMacro.identifier, theMacro.fileId, theMacro.line)

def macroIdTestedWhenNotDefined(theMacroId):
    return '%s_testnotdef' % theMacroId

def pathSplit(p):
    """Split a path into its components, this keeps the trailing '/' for directories."""
    l = p.split(os.sep)
    retVal = ['%s%s' % (d, os.sep) for d in l[:-1]]
    retVal.append(l[-1])
    return retVal

def _writeSectionOnMacroHistory(theS, theEnv, theOmitFiles):
    # Write table of macro usage
    with XmlWrite.Element(theS, 'hr'):
        pass
    with XmlWrite.Element(theS, 'a', {'name' : TITLE_ANCHOR_LINKTEXT_MACROS_HISTORY[1]}):
        pass
    with XmlWrite.Element(theS, 'h1'):
        theS.characters(TITLE_ANCHOR_LINKTEXT_MACROS_HISTORY[0])
    # First the #undef'd one(s)
    doneTitle = False
    for aMacro in theEnv.genMacrosOutOfScope(None):
        if aMacro.refCount > 0:
            if not doneTitle:
                with XmlWrite.Element(theS, 'h2'):
                    theS.characters('Macros Out-of-scope')
                doneTitle = True
            writeMacroHistory(theS, aMacro, theOmitFiles)
    if doneTitle:
        with XmlWrite.Element(theS, 'hr'):
            pass
    # Now the existent one(s)
    doneTitle = False
    for aMacro in theEnv.genMacrosInScope(None):
        if aMacro.refCount > 0:
            if not doneTitle:
                with XmlWrite.Element(theS, 'h2'):
                    theS.characters('Macros In Scope')
                doneTitle = True
            writeMacroHistory(theS, aMacro, theOmitFiles)
    if doneTitle:
        with XmlWrite.Element(theS, 'hr'):
            pass
    # Now the ones that would have an effect if only they had been defined
    # This is a list of [identifiers, ...]
    myMacroNotDefS = theEnv.macroNotDefinedDependencyNames()
    myMacroNotDefS.sort()
    if len(myMacroNotDefS) > 0:
        with XmlWrite.Element(theS, 'a', {'name' : TITLE_ANCHOR_LINKTEXT_MACROS_TESTED_WHEN_NOT_DEFINED[1]}):
            with XmlWrite.Element(theS, 'h2'):
                theS.characters(TITLE_ANCHOR_LINKTEXT_MACROS_TESTED_WHEN_NOT_DEFINED[0])
        for aMacroId in myMacroNotDefS:
            writeMacrosTestedButNotDefined(theS, aMacroId, theEnv)
        with XmlWrite.Element(theS, 'hr'):
            pass

def writeMacroHistory(theS, theMacro, theOmitFiles):
    """Writes out the macro history from a PpDefine object."""
    anchorName = XmlWrite.nameFromString(macroId(theMacro))
    # Write out the macro title
    with XmlWrite.Element(theS, 'h3'):
        with XmlWrite.Element(theS, 'a', {'name' : anchorName}):
            theS.characters('%s [References: %d] Defined? %s' \
                % (
                   theMacro.identifier,
                   theMacro.refCount,
                   str(theMacro.isCurrentlyDefined)
                )
            )
    if theMacro.fileId in theOmitFiles:
        with XmlWrite.Element(theS, 'p'):
            HtmlUtils.writeHtmlFileLink(
                    theS,
                    theMacro.fileId,
                    theMacro.line,
                    '%s#%d' % (theMacro.fileId, theMacro.line),
                    'file_decl'
                )
    writeMacroReferencesTable(theS, theMacro.refFileLineColS)
    
def writeMacrosTestedButNotDefined(theS, theMacroId, theEnv):
    """Writes out the macro history for macros tested but not defined."""
    anchorName = XmlWrite.nameFromString(macroIdTestedWhenNotDefined(theMacroId))
    # This is a list of [class FileLineColumn, ...]
    myRefS = theEnv.macroNotDefinedDependencyReferences(theMacroId)
    # Write out the macro title
    with XmlWrite.Element(theS, 'h3'):
        with XmlWrite.Element(theS, 'a', {'name' : anchorName}):
            theS.characters('%s [References: %d]' \
                % (
                   theMacroId,
                   len(myRefS),
                )
            )
    writeMacroReferencesTable(theS, myRefS)
    
def writeMacroReferencesTable(theS, theFlcS):
    """Writes all the references to a file/line/col in a rowspan/colspan HTML
    table with links to the position in the HTML representation of the file
    that references something.
    This uses a particular design pattern that uses a  DictTree to sort out the
    rows and columns. In this case the DictTree values are lists of pairs
    (href, nav_text) where nav_text is the line_col of the referencing file."""
    myFileLineColS = []
    for aFlc in theFlcS:
        myFileLineColS.append(
            (
                aFlc.fileId,
                (
                    HtmlUtils.retHtmlFileLink(aFlc.fileId, aFlc.lineNum),
                    # Navigation text
                    '%d-%d' % (aFlc.lineNum, aFlc.colNum),
                ),
            )
        )
    HtmlUtils.writeFilePathsAsTable('list', theS, myFileLineColS, 'filetable', tdCallback)

def tdCallback(theS, attrs, k, v):
    """Callback function for the file reference table."""
    attrs['class'] = 'filetable'
    with XmlWrite.Element(theS, 'td', attrs):
        theS.characters('%s:' % k[-1])
        # Get the href/navtext from the value
        for h, n in v:
            theS.characters(' ')
            with XmlWrite.Element(theS, 'a', {'href' : h}):
                # Write the nav text
                theS.characters('%s' % n)
        
def _writeTocLetterLinks(theS, theSet):
    if len(theSet) > 0:
        letterList = list(theSet)
        letterList.sort()
        for aL in letterList:
            theS.literal(' &nbsp; ')
            with XmlWrite.Element(
                    theS,
                    'a',
                    {
                        'href' : '#%s.%s' \
                            % (ANCHOR_MACRO_ALPHA, aL),
                    }
                ):
                with XmlWrite.Element(theS, 'tt'):
                    theS.characters('%s' % aL)
                theS.characters('...')

def _retListMacroNamesOutOfScope(theEnv):
    return [m.identifier for m in theEnv.genMacrosOutOfScope(None)]

def _retListMacroNamesInScope(theEnv):
    return [m.identifier for m in theEnv.genMacrosInScope(None)]

def _writeToc(theS, theEnv):
    """Write out the table of contents."""
    with XmlWrite.Element(theS, 'h1'):
        theS.characters('Contents')
    with XmlWrite.Element(theS, 'ul'):
        numMacros = 0
        with XmlWrite.Element(theS, 'li'):
            with XmlWrite.Element(theS, 'p'):
                # Now write alphabetical list
                # First the #undef'd one(s), referenced or not
                letterSet = set()
                for aMacro in theEnv.genMacrosOutOfScope(None):
                    letterSet.add(aMacro.identifier[0])
                    numMacros += 1
                # Now the existent one(s)
                for aMacro in theEnv.genMacrosInScope(None):
                    letterSet.add(aMacro.identifier[0])
                    numMacros += 1
                if len(letterSet):
                    theS.characters('Macro ')
                    with XmlWrite.Element(theS, 'a', {'href' : '#%s' % TITLE_ANCHOR_LINKTEXT_MACROS_TABLE[1]}):
                        theS.characters(TITLE_ANCHOR_LINKTEXT_MACROS_TABLE[2])
                    theS.characters(' (all macros, alphabetical) [%d]: ' % numMacros)
                    _writeTocLetterLinks(
                        theS,
                        letterSet,
                    )
        # Now list all the referenced macros by name with links to the macro
        # table
        numMacros = 0
        with XmlWrite.Element(theS, 'li'):
            with XmlWrite.Element(theS, 'p'):
                nameS = set()
                for aMacro in theEnv.genMacrosOutOfScope(None):
                    if aMacro.refCount > 0:
                        numMacros += 1
                        nameS.add(aMacro.strIdentPlusParam())
                # Now the existent one(s)
                for aMacro in theEnv.genMacrosInScope(None):
                    if aMacro.refCount > 0:
                        numMacros += 1
                        nameS.add(aMacro.strIdentPlusParam())
                nameList = list(nameS)
                nameList.sort()
                theS.characters('Referenced macros [%d]: ' % numMacros)
                for aName in nameList:
                    theS.literal(' &nbsp; &nbsp; ')
                    with XmlWrite.Element(theS, 'tt'):
                        # Note: Use '_0' to reference the first one
                        with XmlWrite.Element(theS, 'a', {'href' : '#%s_0' % aName}):
                            theS.characters(aName)
        # Link to macro history section
        with XmlWrite.Element(theS, 'li'):
            with XmlWrite.Element(theS, 'p'):
                theS.characters('Macro ')
                with XmlWrite.Element(theS, 'a', {'href' : '#%s' \
                                    % TITLE_ANCHOR_LINKTEXT_MACROS_HISTORY[1]}):
                    theS.characters(TITLE_ANCHOR_LINKTEXT_MACROS_HISTORY[2])
                theS.characters(' (referenced macros only)')
        # Link to macros that are not defined but tested
        with XmlWrite.Element(theS, 'li'):
            with XmlWrite.Element(theS, 'p'):
                # TITLE_ANCHOR_LINKTEXT_MACROS_TESTED_WHEN_NOT_DEFINED = ('Macros Not Defined but Tested'
                theS.characters('Macros ')
                with XmlWrite.Element(theS,
                                      'a',
                                      {
                                        'href' : '#%s' % TITLE_ANCHOR_LINKTEXT_MACROS_TESTED_WHEN_NOT_DEFINED[1]
                                        }):
                    theS.characters(TITLE_ANCHOR_LINKTEXT_MACROS_TESTED_WHEN_NOT_DEFINED[2])
                theS.characters(' when not defined')
                # Now the ones that would have an effect if only they had been defined
                # This is a list of [identifiers, ...]
                myMacroNotDefS = theEnv.macroNotDefinedDependencyNames()
                myMacroNotDefS.sort()
                for anId in myMacroNotDefS:
                    theS.literal(' &nbsp; &nbsp; ')
                    with XmlWrite.Element(theS, 'tt'):
                        # Note: Use '_0' to reference the first one
                        myHref = XmlWrite.nameFromString(macroIdTestedWhenNotDefined(anId))
                        with XmlWrite.Element(
                                    theS,
                                    'a',
                                    {
                                        'href' : '#%s' % myHref,
                                    }
                                ):
                            theS.characters(anId)

def processMacroHistoryToHtml(theLex, theHtmlPath, theItu, theIndexPath):
    """Write out the macro history from the PpLexer as HTML.
    Returns a map of {identifier : href_text, ...) to link to macro definitions."""
    def _linkToIndex(theS, theIdx):
        with XmlWrite.Element(theS, 'p'):
            theS.characters('Return to ')
            with XmlWrite.Element(theS, 'a', {'href' : theIdx}):
                theS.characters('Index')
    # Return value is a map of {identifier : href_text, ...) to link to macro definitions.
    retVal = {}
    # Write CSS
    #open(os.path.join(os.path.dirname(theHtmlPath), TokenCss.TT_CSS_FILE), 'w').write(CSS_STRING_MACRO)
    TokenCss.writeCssToDir(os.path.dirname(theHtmlPath))
    # Grab the environment
    myEnv = theLex.macroEnvironment
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
                myS.characters('Macro Environment for: %s' % theItu)
        with XmlWrite.Element(myS, 'body'):
            with XmlWrite.Element(myS, 'h1'):
                myS.characters('Macro Environment for: %s' % theItu)
            _linkToIndex(myS, theIndexPath)
            # Write the TOC and get the sorted list all the macros in alphabetical order
            _writeToc(myS, myEnv)
            # Write table of macros gettign the map of links as a return value
            retVal = _writeTableOfMacros(myS, myEnv, theHtmlPath)
            # Write table of macro usage
            _writeSectionOnMacroHistory(myS, myEnv, [theLex.UNNAMED_FILE_NAME,])
            # Write back link
            _linkToIndex(myS, theIndexPath)
    # Now update the return link map with
    # theEnv.macroNotDefinedDependencyNames()
    for anId in myEnv.macroNotDefinedDependencyNames():
        if anId not in retVal:
            retVal[anId] = '%s#%s' \
                    % (
                        os.path.basename(theHtmlPath),
                        XmlWrite.nameFromString(macroIdTestedWhenNotDefined(anId))
                    )
    return retVal

import sys
from optparse import OptionParser
#import pprint

######################################
# Test code
######################################
import unittest

class NullClass(unittest.TestCase):
    pass

class TestSplitLine(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testSetUpTearDown(self):
        """TestCountDict: test setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestSplitLine.test_00(): Multi line."""
        myS = '_INIT_SECURITY_POLICY_C7(c1,c2,c3,c4,c5,c6,c7) { FOUR_TUINT8( (TUint8)TSecurityPolicy::ETypeC7, CAPABILITY_AS_TUINT8(c1), CAPABILITY_AS_TUINT8(c2), CAPABILITY_AS_TUINT8(c3) ), FOUR_TUINT8( CAPABILITY_AS_TUINT8(c4), CAPABILITY_AS_TUINT8(c5), CAPABILITY_AS_TUINT8(c6), CAPABILITY_AS_TUINT8(c7) ) } /* s:/epoc32/include\e32cmn.h#3997 Ref: 0 True */'
        #pprint.pprint(myS)
        #print
        #pprint.pprint(splitLineToList(myS))
        self.assertEqual(
                    [
                    '_INIT_SECURITY_POLICY_C7(c1,c2,c3,c4,c5,c6,c7) { FOUR_TUINT8( \\',
                    '(TUint8)TSecurityPolicy::ETypeC7, CAPABILITY_AS_TUINT8(c1), \\',
                    'CAPABILITY_AS_TUINT8(c2), CAPABILITY_AS_TUINT8(c3) ), FOUR_TUINT8( \\',
                    'CAPABILITY_AS_TUINT8(c4), CAPABILITY_AS_TUINT8(c5), \\',
                    'CAPABILITY_AS_TUINT8(c6), CAPABILITY_AS_TUINT8(c7) ) } /* \\',
                    's:/epoc32/include\\e32cmn.h#3997 Ref: 0 True */'
                    ],
                    splitLineToList(myS),
                )
        #print
        #print splitLine(myS)
        self.assertEqual(r"""_INIT_SECURITY_POLICY_C7(c1,c2,c3,c4,c5,c6,c7) { FOUR_TUINT8( \
    (TUint8)TSecurityPolicy::ETypeC7, CAPABILITY_AS_TUINT8(c1), \
    CAPABILITY_AS_TUINT8(c2), CAPABILITY_AS_TUINT8(c3) ), FOUR_TUINT8( \
    CAPABILITY_AS_TUINT8(c4), CAPABILITY_AS_TUINT8(c5), \
    CAPABILITY_AS_TUINT8(c6), CAPABILITY_AS_TUINT8(c7) ) } /* \
    s:/epoc32/include\e32cmn.h#3997 Ref: 0 True */""",
            splitLine(myS))

    def test_01(self):
        """TestSplitLine.test_00(): Short line."""
        myS = 'CONST_CAST(type,exp) (const_cast<type>(exp))'
        #pprint.pprint(myS)
        #print
        #pprint.pprint(splitLineToList(myS))
        self.assertEqual(
                    [
                    'CONST_CAST(type,exp) (const_cast<type>(exp))'
                    ],
                    splitLineToList(myS),
                )
        #print
        #print splitLine(myS)
        self.assertEqual(r"""CONST_CAST(type,exp) (const_cast<type>(exp))""",
            splitLine(myS))

    def test_02(self):
        """TestSplitLine.test_00(): Hard split."""
        myS='CAPABILITY_AS_TUINT8(cap)((TUint8)(int)((cap)==ECapability_None?(__invalid_capability_value(*)[1])(ECapability_None):(__invalid_capability_value(*)[((TUint)(cap+1)<=(TUint)ECapability_Limit)?1:2])(cap)))'
        #pprint.pprint(myS)
        #print
        #pprint.pprint(splitLineToList(myS))
        self.assertEqual(
                [
                    'CAPABILITY_AS_TUINT8(cap)((TUint8)(int)((cap)==ECapability_None?(__invalid_capab\\',
                    'ility_value(*)[1])(ECapability_None):(__invalid_capability_value(*)[((TUint)(cap\\',
                    '+1)<=(TUint)ECapability_Limit)?1:2])(cap)))',
                ],
                splitLineToList(myS)
            )
        #print
        #print splitLine(myS)
        self.assertEqual(r"""CAPABILITY_AS_TUINT8(cap)((TUint8)(int)((cap)==ECapability_None?(__invalid_capab\
    ility_value(*)[1])(ECapability_None):(__invalid_capability_value(*)[((TUint)(cap\
    +1)<=(TUint)ECapability_Limit)?1:2])(cap)))""",
                splitLine(myS)
            )

class Special(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSplitLine))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Special))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

def main():
    usage = "usage: %prog [options] file"
    print('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=30,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )
    unitTest()
    return 0
    
if __name__ == '__main__':
    sys.exit(main())
    