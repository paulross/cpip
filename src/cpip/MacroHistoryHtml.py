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

"""Writes out a macro history in HTML.

Macros can be:
Active - In scope at the end of processing a translation unit (one per identifier). 
Inactive - Not in scope at the end of processing a translation unit (>=0 per identifier). 
And:
Referenced - Have had some influence over the processing of the translation unit.
Not Referenced - No influence over the processing of the translation unit.

Example test:

/* Source         Active?    Refs    ID   */
#define FOO    /*     N        0    FOO_0 */
#undef FOO
#define FOO    /*     N        2    FOO_1 */
FOO
FOO
#undef FOO
#define FOO    /*     Y        1    FOO_2 */
FOO
#define BAR    /*     Y        0    BAR_0 */

Macros with reference counts of zero are not that interesting so they are
relegated to a page (<file>_macros_noref.html) that just describes their
definition and where they where defined.

Macros _with_ reference counts are presented on a page (<file>_macros_ref.html)
with one section per macro. The section has:
definition, where defined,
[This macro depends on the following macros:],
[Macros that depend on this macro:], 

These two HTML pages are joined by a <file>_macros.html this lists (and links to)
the identifiers in this order:
- Active, ref count >0
- Inactive, ref count >0
- Active, ref count =0
- Inactive, ref count =0

Macro HTML IDs
--------------
This is identifier + '_' + n
For any active macro the value of n is the number of previously defined macros.
Current code is like this:

myUndefIdxS, isDefined = myMacroMap[aMacroName]
# Write the undefined ones
for anIndex in myUndefIdxS:
    myMacro = theEnv.getUndefMacro(anIndex)
    startLetter = _writeTrMacro(theS, theHtmlPath, myMacro,
                               anIndex, startLetter, retVal) 
# Now the defined one
if isDefined:
    myMacro = theEnv.macro(aMacroName)
    startLetter = _writeTrMacro(theS, theHtmlPath, myMacro,
                               len(myUndefIdxS), startLetter, retVal) 
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import os
import collections

from cpip.core import PpLexer
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

def _writeTd(theStream, theStr):
    """Write a <td> element and contents."""
    with XmlWrite.Element(theStream, 'td'):
        theStream.characters(theStr)
            
def _writeTh(theStream, theStr):
    """Write a <th> element and contents."""
    with XmlWrite.Element(theStream, 'th'):
        theStream.characters(theStr)
            
def _retMacroId(theMacro, theIndex=None):
    macroStr = theMacro.identifier#theMacro.strIdentPlusParam()
    if theIndex is not None:
        macroStr += '_%d' % theIndex
    return XmlWrite.encodeString(macroStr)

def _writeTableOfMacros(theS, theEnv, theHtmlPath):
    """Writes the table of macros, where they are defined, their ref count etc.""" 
    # Return value is a map of {identifier : href_text, ...) to link to macro
    # definitions.
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
            _writeTh(theS, 'Declaration')
            _writeTh(theS, 'Declared In')
            _writeTh(theS, 'Ref. Count')
            _writeTh(theS, 'Defined?')
        startLetter = ''
        for aMacroName in myMacroNameS:
            myUndefIdxS, isDefined = myMacroMap[aMacroName]
            # Write the undefined ones
            for anIndex in myUndefIdxS:
                myMacro = theEnv.getUndefMacro(anIndex)
                startLetter = _writeTrMacro(theS, theHtmlPath, myMacro,
                                           anIndex, startLetter, retVal) 
            # Now the defined one
            if isDefined:
                myMacro = theEnv.macro(aMacroName)
                startLetter = _writeTrMacro(theS, theHtmlPath, myMacro,
                                           len(myUndefIdxS), startLetter, retVal) 
    with XmlWrite.Element(theS, 'br'):
        pass
    # End: write table of all macros
    return retVal

def _writeTrMacro(theS, theHtmlPath, theMacro, theIntOccurence, theStartLetter, retMap):
    """Write the macro as a row in the general table.
    theMacro is a PpDefine object.
    theStartLetter is the current letter we are writing ['A', 'B', ...] which
    writes an anchor at the beginning of each letter section."""
    with XmlWrite.Element(theS, 'tr'):
        if theMacro.identifier[0] != theStartLetter:
            theStartLetter = theMacro.identifier[0]
            _writeTdMacro(theS, theMacro, theStartLetter, theIntOccurence)
        else:
            _writeTdMacro(theS, theMacro, '', theIntOccurence)
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
        _writeTdRefCount(theS, theMacro)
        _writeTdMonospace(theS, str(theMacro.isCurrentlyDefined))
    return theStartLetter

def _writeTdMacro(theS, theDef, startLetter, theIntOccurence):
    """Write the macro cell in the general table. theDef is a PpDefine object."""
    with XmlWrite.Element(theS, 'td'):
        return _writeMacroDefinitionAndAnchor(theS, theDef, startLetter, theIntOccurence)
        
def _writeMacroDefinitionAndAnchor(theS, theDef, theIntOccurence):
    """Writes a definition of the macro with an anchor that can be linked to.
    This also writes an anchor based on the first character of the macro name so
    that alphabetic links can reference it.
    """
    macroAnchorName = _retMacroId(theDef, theIntOccurence)
    if len(theDef.strReplacements()):
        rStr = splitLine(' '.join([theDef.strIdentPlusParam(),
                    theDef.strReplacements()]), splitLen=80, splitLenHard=132)
        myReplStr = rStr[len(theDef.strIdentPlusParam()):]
    else:
        myReplStr = ''
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
        theS.characters('#define ')
        theS.characters(theDef.strIdentPlusParam())
    if myReplStr:
        with XmlWrite.Element(theS, 'span', {'class' : spanClass + '_repl'}):
            theS.charactersWithBr(myReplStr)
    return macroAnchorName
            
def _writeTdMonospace(theStream, theStr):
    with XmlWrite.Element(theStream, 'td'):
        with XmlWrite.Element(theStream, 'span', {'class' : 'monospace'}):
            theStream.characters(theStr)

def _writeTdRefCount(theS, theMacro):
    with XmlWrite.Element(theS, 'td'):
        with XmlWrite.Element(theS, 'span', {'class' : 'monospace'}):
            if theMacro.refCount > 0:
                # Write a link to the history
                with XmlWrite.Element(
                            theS,
                            'a', 
                            {
                                'href' : '#%s' % XmlWrite.nameFromString(_macroId(theMacro))
                            }
                        ):
                    theS.characters(str(theMacro.refCount))
            else:
                theS.characters(str(theMacro.refCount))

def splitLineToList(sIn, splitLen=60, splitLenHard=80):
    """Splits a long string into a list of lines. This tries to do it nicely at
    whitespaces but will force a split if necessary."""
#     splitLen = 60
#     # This forces a split here, if zero or negative then do not split.
#     splitLenHard = 80
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

def splitLine(theStr, splitLen=60, splitLenHard=80):
    """Splits a long string into string that is a set of lines with continuation
    characters."""
    return '\n    '.join(splitLineToList(theStr, splitLen, splitLenHard))

def _macroId(theMacro):
    return '%s_%s#%d' % (theMacro.identifier, theMacro.fileId, theMacro.line)

def _macroIdTestedWhenNotDefined(theMacroId):
    return '%s_testnotdef' % theMacroId

def _getMacroDependencyTrees(theMacroAdjList, theMacro):
    """Returns the dependency trees (parent/child, child/parent) for the macro.
    Can be None."""
    if theMacroAdjList.hasParent(theMacro.identifier):
        pcTree = theMacroAdjList.treeParentChild(theMacro.identifier)
    else:
        pcTree = None
    if theMacroAdjList.hasChild(theMacro.identifier):
        cpTree = theMacroAdjList.treeChildParent(theMacro.identifier)
    else:
        cpTree = None
    return pcTree, cpTree

def _writeSectionOnMacroHistory(theS, theEnv, theOmitFiles, theHtmlPath, theItu, isReferenced):
    """Write the section that says where macros were used with links to the
    file/line/column.
    theEnv - A MacroEnv() object.
    theOmitFiles - a list of pseudo files not to link to e.g. ['Unnamed Pre-include',].
    """
    retMap = {}
    # Create macro dependency map of {identifier : util.Tree(), ...}
    macroAdjList = theEnv.allStaticMacroDependencies()
    # Write table of macro usage
    with XmlWrite.Element(theS, 'hr'):
        pass
    with XmlWrite.Element(theS, 'h1'):
        with XmlWrite.Element(theS, 'a', {'name' : TITLE_ANCHOR_LINKTEXT_MACROS_HISTORY[1]}):
            pass
        theS.characters(TITLE_ANCHOR_LINKTEXT_MACROS_HISTORY[0])
    # First the #undef'd one(s)
    declareCount = collections.defaultdict(int)
    doneTitle = False
    for aMacro in theEnv.genMacrosOutOfScope(None):
        if (isReferenced and aMacro.refCount > 0) \
        or (not isReferenced and aMacro.refCount == 0):
            if not doneTitle:
                with XmlWrite.Element(theS, 'h2'):
                    theS.characters('Macros Out-of-scope')
                doneTitle = True
            _writeMacroHistory(theS, aMacro, theOmitFiles, declareCount[aMacro.identifier])
            _writeMacroDependencies(theS, theEnv, aMacro, macroAdjList, theItu)
        declareCount[aMacro.identifier] += 1
    if doneTitle:
        with XmlWrite.Element(theS, 'hr'):
            pass
    # Now the existent one(s)
    doneTitle = False
    for aMacro in theEnv.genMacrosInScope(None):
        if (isReferenced and aMacro.refCount > 0) \
        or (not isReferenced and aMacro.refCount == 0):
            if not doneTitle:
                with XmlWrite.Element(theS, 'h2'):
                    theS.characters('Macros In Scope')
                doneTitle = True
            _writeMacroHistory(theS, aMacro, theOmitFiles, declareCount[aMacro.identifier])
            _writeMacroDependencies(theS, theEnv, aMacro, macroAdjList, theItu)
            if aMacro.identifier not in retMap:
                # Add to the return value
                retMap[aMacro.identifier] = '%s#%s' \
                    % (
                        os.path.basename(theHtmlPath),
                        _retMacroId(aMacro, declareCount[aMacro.identifier]),
                    )
        declareCount[aMacro.identifier] += 1
    if doneTitle:
        with XmlWrite.Element(theS, 'hr'):
            pass
    # Now the ones that would have an effect if only they had been defined
    # This is a list of [identifiers, ...]
    myMacroNotDefS = theEnv.macroNotDefinedDependencyNames()
    myMacroNotDefS.sort()
    if len(myMacroNotDefS) > 0:
        with XmlWrite.Element(theS, 'h2'):
            with XmlWrite.Element(theS, 'a',
                    {'name' : TITLE_ANCHOR_LINKTEXT_MACROS_TESTED_WHEN_NOT_DEFINED[1]}):
                pass
            theS.characters(TITLE_ANCHOR_LINKTEXT_MACROS_TESTED_WHEN_NOT_DEFINED[0])
        for aMacroId in myMacroNotDefS:
            _writeMacrosTestedButNotDefined(theS, aMacroId, theEnv)
        with XmlWrite.Element(theS, 'hr'):
            pass
    return retMap

def _writeMacroHistory(theS, theMacro, theOmitFiles, theIntOccurence):
    """Writes out the macro history from a PpDefine object.
    theMacro - a PpDefine() object.
    theOmitFiles - a list of pseudo files not to link to e.g. ['Unnamed Pre-include',].
    """
    anchorName = _retMacroId(theMacro, theIntOccurence)
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
    with XmlWrite.Element(theS, 'p'):
        anchorName = _writeMacroDefinitionAndAnchor(theS, theMacro,
                                                    theIntOccurence)
    with XmlWrite.Element(theS, 'p'):
        with XmlWrite.Element(theS, 'tt'):
            theS.characters('defined @ ')
#             theS.literal('&nbsp;')
#             theS.characters('@ ')
        HtmlUtils.writeHtmlFileLink(
                theS,
                theMacro.fileId,
                theMacro.line,
                '%s#%d' % (theMacro.fileId, theMacro.line),
                'file_decl'
            )
    _writeMacroReferencesTable(theS, theMacro.refFileLineColS)
    # If inactive then state where #undef'd
    if not theMacro.isCurrentlyDefined:
        with XmlWrite.Element(theS, 'p'):
            with XmlWrite.Element(theS, 'tt'):
                theS.characters('undef\'d @ ')
#                 theS.literal('&nbsp;&nbsp;')
#                 theS.characters('@ ')
            HtmlUtils.writeHtmlFileLink(
                    theS,
                    theMacro.undefFileId,
                    theMacro.undefLine,
                    '%s#%d' % (theMacro.undefFileId, theMacro.undefLine),
                    'file_decl'
                )

def _writeMacrosTestedButNotDefined(theS, theMacroId, theEnv):
    """Writes out the macro history for macros tested but not defined."""
    anchorName = XmlWrite.nameFromString(_macroIdTestedWhenNotDefined(theMacroId))
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
    _writeMacroReferencesTable(theS, myRefS)
    
def _writeMacroReferencesTable(theS, theFlcS):
    """Writes all the references to a file/line/col in a rowspan/colspan HTML
    table with links to the position in the HTML representation of the file
    that references something.
    This uses a particular design pattern that uses a  DictTree to sort out the
    rows and columns. In this case the DictTree values are lists of pairs
    (href, nav_text) where nav_text is the line-col of the referencing file."""
    myFileLineColS = []
    # This removes duplicates, it is a list of (fileId, lineNum, colNum).
    # If an include file is included N times there will be N-1 duplicate entries
    # for the header guard macro otherwise.
    hasSeen = []
    for aFlc in theFlcS:
        ident = (aFlc.fileId, aFlc.lineNum, aFlc.colNum)
        if ident not in hasSeen:
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
            hasSeen.append(ident)
    if len(myFileLineColS) > 0:
        HtmlUtils.writeFilePathsAsTable('list', theS, myFileLineColS, 'filetable', _tdFilePathCallback)

def _writeMacroDependencies(theS, theEnv, theMacro, theMacroAdjList, theItu):
    pcTree, cpTree = _getMacroDependencyTrees(theMacroAdjList, theMacro)
    if pcTree is not None:
        with XmlWrite.Element(theS, 'p', {}):
            theS.characters('I depend on these macros:')
        _writeMacroDependenciesTable(theS, theEnv, pcTree, theItu)
    if cpTree is not None:
        with XmlWrite.Element(theS, 'p', {}):
            theS.characters('These macros depend on me:')
        _writeMacroDependenciesTable(theS, theEnv, cpTree, theItu)

def _writeMacroDependenciesTable(theS, theEnv, theAdjList, theItu):
    """Writes all the macro dependencies to a rowspan/colspan HTML
    that references something.
    table with links to the position in the HTML representation of the file
    This uses a particular design pattern that uses a DictTree to sort out the
    rows and columns. In this case the DictTree values are lists of pairs
    (href, nav_text) where nav_text is the line_col of the referencing file."""
    myDt = DictTree.DictTreeHtmlTable('list')
    for branch in theAdjList.branches():
        # I might depend on a macro (that is referenced) but I am not referenced.
        if theEnv.macro(branch[-1]).refCount > 0:
            href = '%s#%s' % (
                _macroHistoryRefName(theItu),
                _retMacroId(theEnv.macro(branch[-1]), 0),
            )
        else:
            href = '%s#%s' % (
                _macroHistoryNorefName(theItu),
                _retMacroId(theEnv.macro(branch[-1]), 0),
            )
        # TODO: theIntOccurence is set 0 here
        myDt.add(branch, (href, branch[-1],))
    # Now iterate with rowspan/colspan
    if len(myDt) > 0:
        HtmlUtils.writeDictTreeAsTable(theS, myDt, tableAttrs={'class' :"filetable"}, includeKeyTail=False)

def _tdFilePathCallback(theS, attrs, k, v):
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

def _retSetMacros(theEnv, isReferenced, isActive):
    """Returns a set of {(Identifier, href_name), ...} of macros identifiers
    and their references. Multiple identifier that have been def'd/undef'd
    have unique, lexagraphically sequential hrefs (with a trailing integer).
    isReferenced - If True only macros that are referenced are included.
    isActive - Only currently active macros are included, undef'd ones are
    excluded."""  
    nameRefsS = set()
    declareCount = collections.defaultdict(int)
    for aMacro in theEnv.genMacrosOutOfScope(None):
        if not isActive \
        and (isReferenced and aMacro.refCount > 0 \
        or not isReferenced and aMacro.refCount == 0):
            visualName = aMacro.strIdentPlusParam()
            nameRefsS.add(
                (
                    visualName,
                    _retMacroId(aMacro, declareCount[aMacro.identifier]),
                )
            )
        declareCount[aMacro.identifier] += 1
    for aMacro in theEnv.genMacrosInScope(None):
        if isActive \
        and (isReferenced and aMacro.refCount > 0 \
        or not isReferenced and aMacro.refCount == 0):
            visualName = aMacro.strIdentPlusParam()
            nameRefsS.add(
                (
                    visualName,
                    _retMacroId(aMacro, declareCount[aMacro.identifier]),
                )
            )
        declareCount[aMacro.identifier] += 1
    return nameRefsS

def _writeTocMacros(theS, theEnv, isReferenced, filePrefix):
    """Write out the table of contents from the environment.
    isReferenced controls whether these are referenced macros (interesting) or
    non referenced macros (a larger, less interesting set).
    filePrefix - If not None this is the HTML file to link to.
    """
    with XmlWrite.Element(theS, 'h2'):
        if isReferenced:
            theS.characters('Referenced Macros:')
        else:
            theS.characters('Non-Referenced Macros:')
    with XmlWrite.Element(theS, 'ul'):
        # Now list all the referenced macros by name with links to the macro
        # table
        boolTitleS = (
                (False, 'Inactive'),
                (True, 'Active'),
            )
        for isActive, title in boolTitleS:
            nameRefsS = _retSetMacros(theEnv, isReferenced=isReferenced, isActive=isActive)
            if len(nameRefsS) > 0:
                nameList = list(nameRefsS)
                with XmlWrite.Element(theS, 'li'):
                    with XmlWrite.Element(theS, 'p'):
                        nameList.sort()
                        theS.characters('%s [%d]: ' % (title, len(nameRefsS)))
                        for aName, aHref in nameList:
                            theS.literal(' &nbsp; &nbsp; ')
                            with XmlWrite.Element(theS, 'tt'):
                                if filePrefix is not None:
                                    href = '%s#%s' % (filePrefix, aHref)
                                else:
                                    href = '#%s' % aHref
                                with XmlWrite.Element(theS, 'a',
                                        {'href' : href}):
                                    theS.characters(aName)

def _retMacroIdHrefNames(theEnv, theItu):
    """Returns a dict of {identifier : [(fileId, lineNum, href_name), ...], ...}
    for annotating HTML.
    The order in the list is the translation unit order in which macros are
    defined/undef'd.
    """
    # dict of {identifier : [(fileId, lineNum, href_name), ...], ...}
    retVal = {}
    declareCount = collections.defaultdict(int)
    for myGen in (theEnv.genMacrosOutOfScope(None), theEnv.genMacrosInScope(None)):
        for aMacro in myGen:
            if aMacro.refCount > 0:
                htmlFile = _macroHistoryRefName(theItu)
            else:
                htmlFile = _macroHistoryNorefName(theItu)
            hrefName = '%s#%s' % (
                htmlFile,
                _retMacroId(aMacro, declareCount[aMacro.identifier]),
            )
#             visualName = aMacro.strIdentPlusParam()
            try:
                retVal[aMacro.identifier].append((aMacro.fileId, aMacro.line, hrefName))
            except KeyError:
                retVal[aMacro.identifier] = [(aMacro.fileId, aMacro.line, hrefName)]
            declareCount[aMacro.identifier] += 1
    return retVal

def _macroHistoryIndexName(theItu):
    return os.path.basename(theItu) + '_macros' + '.html'

def _macroHistoryRefName(theItu):
    return os.path.basename(theItu) + '_macros' + '_ref' + '.html'

def _macroHistoryNorefName(theItu):
    return os.path.basename(theItu) + '_macros' + '_noref' + '.html'

def _linkToIndex(theS, theIdx):
    with XmlWrite.Element(theS, 'p'):
        theS.characters('Return to ')
        with XmlWrite.Element(theS, 'a', {'href' : theIdx}):
            theS.characters('Index')

def processMacroHistoryToHtml(theLex, theHtmlPath, theItu, theIndexPath):
    """Write out the macro history from the PpLexer as HTML.
    Returns a map of:
    {identifier : [(fileId, lineNum, href_name), ...], ...}
    which can be used by src->html generator for providing links to macro pages."""
    TokenCss.writeCssToDir(os.path.dirname(theHtmlPath))
    # Grab the environment
    myEnv = theLex.macroEnvironment
    # Write the index page that links to the referenced and non-referenced pages
    with XmlWrite.XhtmlStream(os.path.join(theHtmlPath, _macroHistoryIndexName(theItu))) as myS:
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
            _writeTocMacros(myS, myEnv, isReferenced=True, filePrefix=_macroHistoryRefName(theItu))
            _writeTocMacros(myS, myEnv, isReferenced=False, filePrefix=_macroHistoryNorefName(theItu))
            # Write back link
            _linkToIndex(myS, theIndexPath)
    # Write the page for referenced macros
    with XmlWrite.XhtmlStream(os.path.join(theHtmlPath, _macroHistoryRefName(theItu))) as myS:
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
                myS.characters('Referenced Macros for: %s' % theItu)
        with XmlWrite.Element(myS, 'body'):
            with XmlWrite.Element(myS, 'h1'):
                myS.characters('Referenced Macros for: %s' % theItu)
            _linkToIndex(myS, theIndexPath)
            _writeTocMacros(myS, myEnv, isReferenced=True, filePrefix=None)
            _writeSectionOnMacroHistory(
                    myS, myEnv, [PpLexer.UNNAMED_FILE_NAME,],
                    theHtmlPath, theItu, isReferenced=True)
            _linkToIndex(myS, theIndexPath)
    # Write the page for non-referenced macros
    with XmlWrite.XhtmlStream(os.path.join(theHtmlPath, _macroHistoryNorefName(theItu))) as myS:
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
                myS.characters('Non-Referenced Macros for: %s' % theItu)
        with XmlWrite.Element(myS, 'body'):
            with XmlWrite.Element(myS, 'h1'):
                myS.characters('Non-Referenced Macros for: %s' % theItu)
            _linkToIndex(myS, theIndexPath)
            _writeTocMacros(myS, myEnv, isReferenced=False, filePrefix=None)
            _writeSectionOnMacroHistory(
                    myS, myEnv, [PpLexer.UNNAMED_FILE_NAME,],
                    theHtmlPath, theItu, isReferenced=False)
            _linkToIndex(myS, theIndexPath)
    retVal = _retMacroIdHrefNames(myEnv, theItu)
#     print('retVal', retVal)
#     print('indexPath', indexPath)
    return retVal, _macroHistoryIndexName(theItu)
    