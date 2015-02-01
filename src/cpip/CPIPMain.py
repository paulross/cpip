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
"""
cpip.cpp -- Preprocess the file or the files in the directory.
"""
__author__ = 'Paul Ross'
__date__ = '2011-07-10'
__version__ = '0.9.1'
__rights__ = 'Copyright (c) 2008-2014 Paul Ross'

import argparse
import collections
import io
import logging
import multiprocessing
import os
import pprint
import subprocess
import sys
import time

from cpip import CppCondGraphToHtml
from cpip import ExceptionCpip
from cpip import IncGraphSVG
from cpip import IncGraphSVGBase
from cpip import INDENT_ML
from cpip import ItuToHtml
from cpip import MacroHistoryHtml
from cpip import TokenCss
from cpip import Tu2Html
from cpip.core import CppCond
from cpip.core import CppDiagnostic
from cpip.core import FileIncludeGraph
from cpip.core import IncludeHandler
from cpip.core import PpLexer
from cpip.core import PragmaHandler
from cpip.util import CommonPrefix
from cpip.util import Cpp
from cpip.util import DirWalk
from cpip.util import HtmlUtils
from cpip.util import XmlWrite

# POD class that contains the arguments for processing a file or directory
MainJobSpec = collections.namedtuple('MainJobSpec',
    [
        'incHandler',       # IncludeHandler.CppIncludeStdOs()
        'preDefMacros',     # A dictionary of standard predefined macros e.g. __STDC__
                            #   __DATE__, __TIME__ will be automatically allocated.
        'preIncStr',        # String that contains the predefined #defines
        'preIncPaths',      # List of file paths to be pre-included
                            # NOTE: Not open file-like objects as multiprocessing
                            # as these will fail to be deep copied.
        'diagnostic',       # CppDiagnostic.PreprocessDiagnosticKeepGoing() or None
        'pragmaHandler',    # PragmaHandler.PragmaHandlerNull() or None
        'keepGoing',        # boolean
        'conditionalLevel', # Integer level, whether to display conditionally compiled out files
        'dumpList',         # List of letters as to what to dump to stdout
        'helpMap',          # map of {opt_name : (value, help), ...}. See retOptionMap().
        'includeDOT',       # boolean, whether to try to use DOT to create a dependency SVG.
        'cmdLine',          # Invocation: ' '.join(sys.argv)
    ]
)

###################### Static introductory text. #########################
INCLUDE_GRAPH_INTRO = [
    """This is the relationships of the #include'd files
presented as a SVG graph or as text.
""",
    """The SVG graph shows the tree of included files
in a graphical fashion with each file as a node and the #include relationship
as an edge.
""",
    """You can choose the scale with the selectors at the top.
Mousing over the nodes in the SVG graph pops up information about
the #include process.
""",
]

SOURCE_CODE_INTRO = [
    """HTML representations of the source file and
the translation unit as seen by the compiler.
""",
    """Lines in the source file are
linked to the translation unit where appropriate. Macros in the source file
are linked to the macro page.
"""
]

CONDITIONAL_COMPILATION_INTRO = [
    """The conditional compilation statements as green (i.e. evaluates as True)
and red (evaluates as False). Each statement is linked to the source code it came from."""
]

MACROS_INTRO = [
    """A page describing the macros encountered during pre-processing, their definition, where defined,
where used and their dependencies. All linked to the source code.
""",
]

TOKEN_COUNT_INTRO = [
    """A table of the token types and their count.
""",
]

FILES_INCLUDED_INTRO = [
    """A table of the source files included, their directories and the number of times they
were included.
""",
    """The links lead to the source code.
""",
]
#################### END: Static introductory text. #######################

# Holds the result of preprocessFileToOutput()
# ituPath - the path to the input ITU
# indexPath - the path to the index.html that describes the job.
# tuIndexFileName - thePath to the index HTML page that describes the ITU
PpProcessResult = collections.namedtuple('PpProcessResult',
                            ['ituPath', 'indexPath', 'tuIndexFileName'])
class FigVisitorLargestCommanPrefix(FileIncludeGraph.FigVisitorBase):
    """Simple visitor that walks the tree and finds the largest common file name prefix."""
    def __init__(self):
        self._fileNameS = set()

    def visitGraph(self, theFigNode, theDepth, theLine):
        """Capture the file name."""
        if theFigNode.fileName != PpLexer.UNNAMED_FILE_NAME:
            self._fileNameS.add(os.path.abspath(theFigNode.fileName))

    def lenCommonPrefix(self):
        return CommonPrefix.lenCommonPrefix(self._fileNameS)

class FigVisitorDot(FileIncludeGraph.FigVisitorBase):
    """Simple visitor that collects parent/child links for plotting the graph with dot."""
    FILE_EXT_TO_NODE_COLOURS = {
        '.h'                    : 'yellow',
        '.c'                    : 'lawngreen',
        '.cpp'                  : 'limegreen',
        '.inl'                  : 'salmon',
    }
    def __init__(self, lenPrefix=0):
        super(FigVisitorDot, self).__init__()
        self._lenPrefix = lenPrefix
        self._nodeS = set()
        self._rootS = []
        self._lineS = []

    def __str__(self):
        retL = ['digraph FigVisitorDot {', ]
        retL.extend(sorted(self._nodeS))
        if len(self._rootS) > 1:
            retL.append('%s;' % ' -> '.join(self._rootS))
        retL.extend(self._lineS)
        retL.append('}\n')
        return '\n'.join(retL)

    def _fileName(self, theFigNode):
        """Treat the file name consistently."""
        if theFigNode.fileName == PpLexer.UNNAMED_FILE_NAME:
            return theFigNode.fileName
        myF = os.path.abspath(theFigNode.fileName)
        if self._lenPrefix > 0:
            myF = myF[self._lenPrefix:]
        return myF

    def _addNode(self, theFigNode):
        if theFigNode.numTokensSig > 0:
            myF = self._fileName(theFigNode)
            # Set the attributes according to the file extension
            nodeAttrStr = '"%s" [' % myF
            myExt = os.path.splitext(theFigNode.fileName)[1].lower()
            if myF == PpLexer.UNNAMED_FILE_NAME:
                nodeAttrStr += 'color=lightblue,style=filled'
            elif myExt in self.FILE_EXT_TO_NODE_COLOURS:
                nodeAttrStr += 'color=%s,style=filled' % self.FILE_EXT_TO_NODE_COLOURS[myExt]
            else:
                # Unknown
                nodeAttrStr += 'color=red,style=filled'
            nodeAttrStr += ',label="%s"' % myF
            nodeAttrStr += '];'
            self._nodeS.add(nodeAttrStr)

    def visitGraph(self, theFigNode, theDepth, theLine):
        """."""
        self._addNode(theFigNode)
        myF = self._fileName(theFigNode)
        # Set the attributes according to the file extension
        if theDepth == 1:
            self._rootS.append('"%s"' % (myF))
        hasC = False
        for aC in theFigNode.genChildNodes():
            self._lineS.append('"%s" -> "%s";' % (myF, self._fileName(aC)))
            hasC = True
        if not hasC:
            # Leaf node
            self._lineS.append('"%s";' % (myF))

def writeIncludeGraphAsDot(theOutDir, theItu, theLexer):
    logging.info('Creating include Graph for DOT...')
    myFigr = theLexer.fileIncludeGraphRoot
#    # Visitor to work out common prefix
#    myVis = FigVisitorLargestCommanPrefix()
#    myFigr.acceptVisitor(myVis)
    # Visitor for the DOT file
    myVis = FigVisitorDot()  # myVis.lenCommonPrefix())
    myFigr.acceptVisitor(myVis)
    dotPath = os.path.abspath(os.path.join(theOutDir, includeGraphFileNameDotTxt(theItu)))
    svgPath = os.path.abspath(os.path.join(theOutDir, includeGraphFileNameDotSVG(theItu)))
    f = open(dotPath, 'w')
    f.write(str(myVis))
    f.close()
    result = False
    # Now make a system call to dot
    try:
        retcode = subprocess.call("dot -Tsvg %s -o %s" % (dotPath, svgPath), shell=True)
        if retcode < 0:
            logging.error("dot was terminated by signal %d" % retcode)
        elif retcode > 0:
            logging.error("dot returned error code %d" % retcode)
        elif retcode == 0:
            result = True
            logging.info("dot returned %d" % retcode)
    except OSError as e:
        logging.error("dot execution failed: %s" % str(e))
    logging.info('Creating include Graph for DOT done.')
    return result

def retFileCountMap(theLexer):
    myFigr = theLexer.fileIncludeGraphRoot
    myFileNameVis = FileIncludeGraph.FigVisitorFileSet()
    myFigr.acceptVisitor(myFileNameVis)
    return myFileNameVis.fileNameMap

def _dumpCondCompGraph(theLexer):
    print()
    print(' Conditional Compilation Graph '.center(75, '-'))
    myFigr = theLexer.condCompGraph
    print(myFigr)
    print(' END Conditional Compilation Graph '.center(75, '-'))

def _dumpIncludeGraph(theLexer):
    print()
    print(' Include Graph '.center(75, '-'))
    myFigr = theLexer.fileIncludeGraphRoot
    print(myFigr)
    print(' END Include Graph '.center(75, '-'))

def _dumpFileCount(theFileCountMap):
    print()
    myList = list(theFileCountMap.keys())
    myList.sort()
    print()
    print(' Count of files encountered '.center(75, '-'))
    for f in myList:
        print('%4d  %s' % (theFileCountMap[f], f))
    print(' END Count of files encountered '.center(75, '-'))

def _dumpTokenCount(theTokenCounter):
    print()
    print(' Token count '.center(75, '-'))
    # print theTokenCounter
    myTotal = 0
    for tokType, tokCount in theTokenCounter.tokenTypesAndCounts(
                                        isAll=True,
                                        allPossibleTypes=True):
        print('%8d  %s' % (tokCount, tokType))
        myTotal += tokCount
    print('%8d  %s' % (myTotal, 'TOTAL'))
    print(' END Token count '.center(75, '-'))

def _dumpMacroEnv(theLexer):
    print()
    print(' Macro Environment and History '.center(75, '-'))
    print(theLexer.macroEnvironment.macroHistory())
    print(' END Macro Environment and History '.center(75, '-'))
    print()

def _dumpMacroEnvDot(theLexer):
    print()
    print(' Macro dependencies as a DOT file '.center(75, '-'))
    print('digraph MacroDependencyDot {')
    myMacEnv = theLexer.macroEnvironment
    for aPpDef in myMacEnv.genMacros():
        if aPpDef.isReferenced:
            for aRtok in aPpDef.replacementTokens:
                if aRtok.isIdentifier() and myMacEnv.hasMacro(aRtok.t):
                    print('"%s" -> "%s";' % (aPpDef.identifier, aRtok.t))
    print('}\n')
    print(' END Macro dependencies as a DOT file '.center(75, '-'))
    print()

def tuIndexFileName(theTu):
    return 'index_' + HtmlUtils.retHtmlFileName(theTu)

def tuFileName(theTu):
    return os.path.basename(theTu) + '.html'

# def macroHistoryFileName(theItu):
#     return os.path.basename(theItu)+'_macros'+'.html'

def includeGraphFileNameSVG(theItu):
    return os.path.basename(theItu) + '.include.svg'

def includeGraphFileNameCcg(theItu):
    return os.path.basename(theItu) + '.ccg.html'

def includeGraphFileNameText(theItu):
    return os.path.basename(theItu) + '.include.txt.html'

def includeGraphFileNameDotTxt(theItu):
    return os.path.basename(theItu) + '.include.dot'

def includeGraphFileNameDotSVG(theItu):
    return os.path.basename(theItu) + '.include.dot.svg'

def writeIncludeGraphAsText(theOutDir, theItu, theLexer):
    def _linkToIndex(theS, theItu):
        with XmlWrite.Element(theS, 'p'):
            theS.characters('Return to ')
            with XmlWrite.Element(theS, 'a', {'href' : tuIndexFileName(theItu)}):
                theS.characters('Index')
    outPath = os.path.join(theOutDir, includeGraphFileNameText(theItu))
    with XmlWrite.XhtmlStream(outPath, mustIndent=INDENT_ML) as myS:
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
                myS.characters('Included graph for %s' % theItu)
        with XmlWrite.Element(myS, 'body'):
            with XmlWrite.Element(myS, 'h1'):
                myS.characters('File include graph for: %s' % theItu)
            with XmlWrite.Element(myS, 'p'):
                myS.characters('A text dump of the include graph.')
            _linkToIndex(myS, theItu)
            with XmlWrite.Element(myS, 'pre'):
                myS.characters(str(theLexer.fileIncludeGraphRoot))
            _linkToIndex(myS, theItu)

def _writeParagraphWithBreaks(theS, theParas):
    for i, p in enumerate(theParas):
#         if i > 0:
#             with XmlWrite.Element(theS, 'br'):
#                 pass
        with XmlWrite.Element(theS, 'p'):
            theS.characters(p)
            
def writeTuIndexHtml(theOutDir, theTuPath, theLexer, theFileCountMap, theTokenCntr, hasIncDot, macroHistoryIndexName):
    with XmlWrite.XhtmlStream(
            os.path.join(theOutDir, tuIndexFileName(theTuPath)),
            mustIndent=INDENT_ML,
            ) as myS:
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
                myS.characters('CPIP Processing of %s' % theTuPath)
        with XmlWrite.Element(myS, 'body'):
            with XmlWrite.Element(myS, 'h1'):
                myS.characters('CPIP Processing of %s' % theTuPath)
            with XmlWrite.Element(myS, 'p'):
                myS.characters("""This has links to individual pages about the
pre-processing of this file.""")
            # ##
            # Translation unit
            # ##
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('1. Source Code')
            _writeParagraphWithBreaks(myS, SOURCE_CODE_INTRO)
            with XmlWrite.Element(myS, 'h3'):  # 'p'):
                myS.characters('The ')
                with XmlWrite.Element(myS, 'a', {'href' : HtmlUtils.retHtmlFileName(theTuPath), }):
                    myS.characters('source file')
                myS.characters(' and ')
                with XmlWrite.Element(myS, 'a', {'href' : tuFileName(theTuPath), }):
                    myS.characters('as a translation unit')
            # ##
            # Include graph
            # ##
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('2. Include Graphs')
            _writeParagraphWithBreaks(myS, INCLUDE_GRAPH_INTRO)
            with XmlWrite.Element(myS, 'h3'):  # 'p'):
                myS.characters('A ')
                with XmlWrite.Element(myS, 'a', {'href' : includeGraphFileNameSVG(theTuPath), }):
                    myS.characters('visual #include tree in SVG')
                # If we have successfully written a .dot file then link to it
                if hasIncDot:
                    myS.characters(', ')
                    with XmlWrite.Element(myS, 'a', {'href' : includeGraphFileNameDotSVG(theTuPath), }):
                        myS.characters('Dot dependency [SVG]')
                myS.characters(' or ')
                with XmlWrite.Element(myS, 'a', {'href' : includeGraphFileNameText(theTuPath), }):
                    myS.characters('as Text')
            # ##
            # Conditional compilation
            # ##
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('3. Conditional Compilation')
            _writeParagraphWithBreaks(myS, CONDITIONAL_COMPILATION_INTRO)
            with XmlWrite.Element(myS, 'h3'):  # 'p'):
                myS.characters('The ')
                with XmlWrite.Element(myS, 'a', {'href' : includeGraphFileNameCcg(theTuPath), }):
                    myS.characters('conditional compilation graph')
            # ##
            # Macro history
            # ##
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('4. Macros')
            _writeParagraphWithBreaks(myS, MACROS_INTRO)
            with XmlWrite.Element(myS, 'h3'):
                myS.characters('The ')
                with XmlWrite.Element(myS, 'a', {'href' : macroHistoryIndexName, }):
                    myS.characters('Macro Environment')
            # ##
            # Write out token counter as a table
            # ##
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('5. Token Count')
            _writeParagraphWithBreaks(myS, TOKEN_COUNT_INTRO)
            with XmlWrite.Element(myS, 'table', {'class' : "monospace"}):
                with XmlWrite.Element(myS, 'tr'):
                    with XmlWrite.Element(myS, 'th', {'class' : "monospace"}):
                        myS.characters('Token Type')
                    with XmlWrite.Element(myS, 'th', {'class' : "monospace"}):
                        myS.characters('Count')
                myTotal = 0
                for tokType, tokCount in theTokenCntr.tokenTypesAndCounts(
                                                    isAll=True,
                                                    allPossibleTypes=True):
                    with XmlWrite.Element(myS, 'tr'):
                        with XmlWrite.Element(myS, 'td', {'class' : "monospace"}):
                            myS.characters(tokType)
                        with XmlWrite.Element(myS, 'td', {'class' : "monospace"}):
                            # <tt> does not preserve space so force it to
                            myStr = '%10d' % tokCount
                            myStr = myStr.replace(' ', '&nbsp;')
                            myS.literal(myStr)
                        myTotal += tokCount
                with XmlWrite.Element(myS, 'tr'):
                    with XmlWrite.Element(myS, 'td', {'class' : "monospace"}):
                        with XmlWrite.Element(myS, 'b'):
                            myS.characters('Total:')
                    with XmlWrite.Element(myS, 'td', {'class' : "monospace"}):
                        with XmlWrite.Element(myS, 'b'):
                            # <tt> does not preserve space so force it to
                            myStr = '%10d' % myTotal
                            myStr = myStr.replace(' ', '&nbsp;')
                            myS.literal(myStr)
            with XmlWrite.Element(myS, 'br'):
                pass
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('6. Files Included and Count')
            _writeParagraphWithBreaks(myS, FILES_INCLUDED_INTRO)
            with XmlWrite.Element(myS, 'p'):
                myS.characters('Total number of unique files: %d' % len(theFileCountMap))
            # TODO: Value count
            # with XmlWrite.Element(myS, 'p'):
            #    myS.characters('Total files processed: %d' % sum(theFileCountMap.values()))
            myItuFileS = sorted(theFileCountMap.keys())
            # Create a list for the DictTree
            myFileLinkS = [
                (
                    p,
                    # Value is a tripple (href, basename, count)
                    (
                        HtmlUtils.retHtmlFileName(p),
                        os.path.basename(p),
                        theFileCountMap[p]),
                    )
                for p in myItuFileS if p != PpLexer.UNNAMED_FILE_NAME
            ]
            HtmlUtils.writeFilePathsAsTable(None, myS, myFileLinkS, 'filetable', _tdCallback)
            with XmlWrite.Element(myS, 'br'):
                pass
            # TODO...
            with XmlWrite.Element(myS, 'p'):
                myS.characters('Produced by %s version: %s' % ('CPIPMain', __version__))
            # Back link
            with XmlWrite.Element(myS, 'p'):
                myS.characters('Back to: ')
                with XmlWrite.Element(
                        myS,
                        'a',
                        {
                            'href' : 'index.html',
                        }
                    ):
                    myS.characters('Index Page')

def _tdCallback(theS, attrs, k, v):
    """Callback function for the file count table."""
    attrs['class'] = 'filetable'
    href, navText, count = v
    with XmlWrite.Element(theS, 'td', attrs):
        with XmlWrite.Element(theS, 'a', {'href' : href}):
            # Write the nav text
            theS.characters(navText)
    with XmlWrite.Element(
                    theS,
                    'td',
                    {
                        'width' : "36px",
                        'class' : 'filetable',
                        'align' : "right",
                    }
                ):
        # Write the nav text
        theS.characters('%d' % count)

def writeIndexHtml(theItuS, theOutDir, theJobSpec):
    """Writes the top level index.html page for a pre-processed file.
    
    theOutDir - The output directory.
    
    theTuS - The list of translation units processed.
    
    theCmdLine - The command line as a string.
    
    theOptMap is a map of {opt_name : (value, help), ...} from the
    command line options.
    TODO: This is fine but has too many levels of indent.
    """
    indexPath = os.path.join(theOutDir, 'index.html')
    assert len(theItuS) == 1, 'Can only process one TU to an output directory.'
    with XmlWrite.XhtmlStream(indexPath, mustIndent=INDENT_ML) as myS:
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
                myS.characters('CPIP Processing')
        with XmlWrite.Element(myS, 'body'):
            with XmlWrite.Element(myS, 'h1'):
                myS.characters('CPIP Processing in output location: %s' % theOutDir)
            # List of links to TU index pages
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('Files Processed as Translation Units:')
            with XmlWrite.Element(myS, 'ul'):
                for anItu in theItuS:
                    with XmlWrite.Element(myS, 'li'):
                        with XmlWrite.Element(myS, 'tt'):
                            with XmlWrite.Element(
                                      myS,
                                      'a',
                                      {'href' : tuIndexFileName(anItu)},
                                    ):
                                myS.characters(anItu)
            _writeCommandLineInvocationToHTML(myS, theJobSpec)
    return indexPath

def _writeCommandLineInvocationToHTML(theS, theJobSpec):
    # Command line
    with XmlWrite.Element(theS, 'h2'):
        theS.characters('CPIP Command line:')
    with XmlWrite.Element(theS, 'pre'):
        theS.characters(theJobSpec.cmdLine)
    # Command line options
    with XmlWrite.Element(theS, 'table', {'border' : "1"}):
        with XmlWrite.Element(theS, 'tr'):
            with XmlWrite.Element(theS, 'th', {'style' : "padding: 2px 6px 2px 6px"}):
                theS.characters('Option')
            with XmlWrite.Element(theS, 'th', {'style' : "padding: 2px 6px 2px 6px"}):
                theS.characters('Value')
            with XmlWrite.Element(theS, 'th', {'style' : "padding: 2px 6px 2px 6px"}):
                theS.characters('Description')
        optS = sorted(theJobSpec.helpMap.keys())
        for o in optS:
            with XmlWrite.Element(theS, 'tr'):
                # Option name
                with XmlWrite.Element(theS, 'td', {'style' : "padding: 2px 6px 2px 6px"}):
                    with XmlWrite.Element(theS, 'tt'):
                        theS.characters(str(o))
                # Option value
                with XmlWrite.Element(theS, 'td', {'style' : "padding: 2px 6px 2px 6px"}):
                    with XmlWrite.Element(theS, 'tt'):
                        myVal = theJobSpec.helpMap[o][0]
                        # Break up lists as these can be quite long
                        if type(myVal) == list \
                        or type(myVal) == tuple:
                            if len(myVal) > 0:
                                for i, aVal in enumerate(myVal):
                                    if i > 0:
                                        theS.characters(',')
                                        with XmlWrite.Element(theS, 'br'):
                                            pass
                                    theS.characters(str(aVal))
                            else:
                                theS.literal('&nbsp;')
                        else:
                            theS.characters(str(myVal))
                # Option help
                with XmlWrite.Element(theS, 'td', {'style' : "padding: 2px 6px 2px 6px"}):
                    # Substitute <br/> for "\n"
                    for i, aLine in enumerate(theJobSpec.helpMap[o][1].strip().split('\n')):
                        if i > 0:
                            with XmlWrite.Element(theS, 'br'):
                                pass
                        theS.characters(aLine)

def retOptionMap(theOptParser, theOpts):
    """Returns map of {opt_name : (value, help), ...} from the current options."""
    varsOpts = vars(theOpts)
    retMap = {}
    for k in sorted(theOptParser._option_string_actions.keys()):
        optDest = theOptParser._option_string_actions[k].dest
        optName = '/'.join(theOptParser._option_string_actions[k].option_strings)
        try:
            optValue = varsOpts[optDest]
            if hasattr(theOptParser._option_string_actions[k], 'help'):
                optHelp = theOptParser._option_string_actions[k].help.replace('[default: %(default)s]', '')
                retMap[optName] = (optValue, optHelp)
        except KeyError:
            pass
#     pprint.pprint(retMap)
    return retMap

################################
# Section: Multiprocessing code.
################################
def preProcessFilesMP(dIn, dOut, jobSpec, glob, recursive, jobs):
    """Multiprocessing code to preprocess directories. Returns a count of ITUs
    processed."""
    if jobs < 0:
        raise ValueError('preProcessFilesMP(): can not run with negative number of jobs: %d' % jobs)
    if jobs == 0:
        jobs = multiprocessing.cpu_count()
    assert jobs > 1, 'preProcessFilesMP(): number of jobs: %d???' % jobs
    logging.info('plotLogPassesMP(): Setting multi-processing jobs to %d' % jobs)
    myTaskS = [
        (t.filePathIn, t.filePathOut, jobSpec) \
            for t in DirWalk.dirWalk(dIn, dOut, glob, recursive, bigFirst=True)
    ]
    with multiprocessing.Pool(processes=jobs) as myPool:
        if jobSpec.keepGoing:
            fn = preprocessFileToOutputNoExcept
        else:
            fn = preprocessFileToOutput
        myResults = [
            r.get() for r in [
                myPool.apply_async(fn, t) for t in myTaskS
            ]
        ]
    return myResults
#     count = 0
#     for r in myResults:
#         count += 1
#     # TODO: Return titles and paths for caller to write the root index HTML.
#     return count

################################
# End: Multiprocessing code.
################################
def _removeCommonPrefixFromResults(titlePathTupleS):
    l = CommonPrefix.lenCommonPrefix([r.ituPath for r in titlePathTupleS])
    prefixOut = ''
    if l > 0:
        assert len(titlePathTupleS) > 0
#         prefixOut = titlePathTupleS[0][1][:l]
        for tpt in titlePathTupleS:
            if tpt[1] is not None:
                prefixOut = tpt[1][:l]
                break
    return prefixOut, sorted([PpProcessResult(t[l:], p, i) for t, p, i in titlePathTupleS])

def _writeDirectoryIndexHTML(theInDir, theOutDir, titlePathTupleS, theJobSpec):
    """Writes a super index.html when a directory has been processed.
    titlePathTuples is a list of:
        PpProcessResult(ituPath, indexPath, tuIndexFileName(ituPath))."""
    indexPath = os.path.join(theOutDir, 'index.html')
    TokenCss.writeCssToDir(theOutDir)
    _prefixOut, titlePathTupleS = _removeCommonPrefixFromResults(titlePathTupleS)
    # Write the HTML
    with XmlWrite.XhtmlStream(indexPath, mustIndent=INDENT_ML) as myS:
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
                myS.characters('CPIP Processing')
        with XmlWrite.Element(myS, 'body'):
            with XmlWrite.Element(myS, 'h1'):
                myS.characters('CPIP Directory Processing in output location: %s' \
                               % theOutDir)
            # List of links to TU index pages
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('Files Processed as Translation Units:')
            with XmlWrite.Element(myS, 'p'):
                myS.characters('Input: ')
                with XmlWrite.Element(myS, 'tt'):
                    myS.characters(theInDir)
            with XmlWrite.Element(myS, 'ul'):
                for title, indexHTMLPath, fileIndexHTMLPath in titlePathTupleS:
                    if indexHTMLPath is not None \
                    and fileIndexHTMLPath is not None:
                        indexHTMLPath = os.path.relpath(indexHTMLPath,
                                                        theOutDir,
                                                        )
                        # Redirect to page that describes actual file
                        indexHTMLPath = os.path.join(os.path.dirname(indexHTMLPath), fileIndexHTMLPath)
                    with XmlWrite.Element(myS, 'li'):
                        with XmlWrite.Element(myS, 'tt'):
                            if indexHTMLPath is not None:
                                with XmlWrite.Element(myS,
                                                      'a',
                                                      {'href' : indexHTMLPath}):
                                    myS.characters(title)
                            else:
                                myS.characters('%s [FAILED]' % title)
            _writeCommandLineInvocationToHTML(myS, theJobSpec)

def preprocessDirToOutput(inDir, outDir, jobSpec, globMatch, recursive, numJobs):
    """Pre-process all the files in a directory. Returns a count of the TUs.
    This uses multiprocessing where possible."""
    assert os.path.isdir(inDir)
    if numJobs != 1:
        results = preProcessFilesMP(inDir, outDir, jobSpec, globMatch, recursive, numJobs)
    else:
        results = []
        for t in DirWalk.dirWalk(inDir, outDir, globMatch, recursive, bigFirst=False):
            if jobSpec.keepGoing:
                fn = preprocessFileToOutputNoExcept
            else:
                fn = preprocessFileToOutput
            results.append(
                fn(t.filePathIn, t.filePathOut, jobSpec)
            )
    # Write the linking HTML from the title and file paths.
#     print('results', results)
    _writeDirectoryIndexHTML(inDir, outDir, results, jobSpec)

def preprocessFileToOutputNoExcept(ituPath, *args, **kwargs):
    """Preprocess a single file and catch all ExceptionCpip
    exceptions and log them."""
    try:
        return preprocessFileToOutput(ituPath, *args, **kwargs)
    except ExceptionCpip as err:
        logging.critical('preprocessFileToOutputNoExcept(): "%s" %s' % (err, ituPath))
    return PpProcessResult(ituPath, None, None)

def preprocessFileToOutput(ituPath, outDir, jobSpec):
    """Preprocess a single file. May raise ExceptionCpip (or worse!).
    Returns a PpProcessResult(ituPath, indexPath, tuIndexFileName(ituPath))."""
    assert os.path.isfile(ituPath)
    logging.info('preprocessFileToOutput(): %s' % ituPath)
    if not os.path.exists(outDir):
        try:
            os.makedirs(outDir)
        except OSError:
            pass
    myItuToHtmlFileSet = set()
    # Create the lexer.
    preIncFiles = []
    if len(jobSpec.preIncStr):
        preIncFiles.append(io.StringIO(jobSpec.preIncStr))
    preIncFiles.extend([open(f) for f in jobSpec.preIncPaths])
    myLexer = PpLexer.PpLexer(
                    ituPath,
                    jobSpec.incHandler,
                    preIncFiles=preIncFiles,
                    diagnostic=jobSpec.diagnostic,
                    pragmaHandler=jobSpec.pragmaHandler,
                    stdPredefMacros=jobSpec.preDefMacros,
                    )
    myDestFile = os.path.join(outDir, tuFileName(ituPath))
    logging.info('TU in HTML:')
    logging.info('  %s', myDestFile)
    myTokCntr, mySetItuLines = Tu2Html.processTuToHtml(
                            myLexer,
                            myDestFile,
                            ituPath,
                            jobSpec.conditionalLevel,
                            tuIndexFileName(ituPath),  # Path back to the index
                            incItuAnchors=True,
                        )
    logging.info('preprocessFileToOutput(): Processing TU done.')
    myFileCountMap = retFileCountMap(myLexer)
    # Write out the HTML for each source file
    for aSrc in sorted(myFileCountMap.keys()):
        myItuToHtmlFileSet.add(aSrc)
    # Now output state
    # Conditional compilation graph
    if 'C' in jobSpec.dumpList:
        _dumpCondCompGraph(myLexer)
    # File include graph
    if 'I' in jobSpec.dumpList:
        _dumpIncludeGraph(myLexer)
    # List files encountered
    if 'F' in jobSpec.dumpList:
        _dumpFileCount(myFileCountMap)
    # Token count
    if 'T' in jobSpec.dumpList:
        _dumpTokenCount(myTokCntr)
    # Macro environment
    if 'M' in jobSpec.dumpList:
        _dumpMacroEnv(myLexer)
    if 'R' in jobSpec.dumpList:
        _dumpMacroEnvDot(myLexer)
    # Macro environment and history
#     outPath = os.path.join(outDir, macroHistoryFileName(ituPath))
    logging.info('Macro history to:')
    logging.info('  %s', outDir)
    myMacroRefMap, macroHistoryIndexName = MacroHistoryHtml.processMacroHistoryToHtml(
            myLexer,
            outDir,
            ituPath,
            tuIndexFileName(ituPath),
        )
    # Write Include graph in SVG
    outPath = os.path.join(outDir, includeGraphFileNameSVG(ituPath))
    logging.info('Include graph (SVG) to:')
    logging.info('  %s', outPath)
    IncGraphSVGBase.processIncGraphToSvg(
            myLexer,
            outPath,
            IncGraphSVG.SVGTreeNodeMain,
            'left',
            '+',
        )
    # Write Include graph in Text
    logging.info('Writing include graph (TEXT) to:')
    logging.info('  %s', outPath)
    writeIncludeGraphAsText(outDir, ituPath, myLexer)
    # Include graph as a dot file
    if jobSpec.includeDOT:
        logging.info('Writing include graph (DOT) to:')
        logging.info('  %s', outPath)
        hasIncGraphDot = writeIncludeGraphAsDot(outDir, ituPath, myLexer)
    else:
        hasIncGraphDot = False
    # Write Conditional compilation graph in HTML
    outPath = os.path.join(outDir, includeGraphFileNameCcg(ituPath))
    logging.info('Conditional compilation graph in HTML:')
    logging.info('  %s', outPath)
    CppCondGraphToHtml.processCppCondGrphToHtml(
            myLexer,
            outPath,
            'Conditional Compilation Graph',
            tuIndexFileName(ituPath),
        )
    # This is an index for the TU
    writeTuIndexHtml(outDir, ituPath, myLexer, myFileCountMap, myTokCntr,
                     hasIncGraphDot, macroHistoryIndexName)
    logging.info('Done: %s', ituPath)
    # Write ITU HTML i.e. HTMLise the original files
    # Create a CppCondGraphVisitorConditionalLines
    myCcgvcl = CppCond.CppCondGraphVisitorConditionalLines()
    myLexer.condCompGraph.visit(myCcgvcl)
    for aSrc in sorted(myItuToHtmlFileSet):
        try:
            # Could be 'Unnamed Pre-include'
            if aSrc != PpLexer.UNNAMED_FILE_NAME:
                logging.info('ITU in HTML: .../%s', os.path.basename(aSrc))
                ItuToHtml.ItuToHtml(
                    aSrc,
                    outDir,
                    keepGoing=jobSpec.keepGoing,
                    macroRefMap=myMacroRefMap,
                    cppCondMap=myCcgvcl,
                    ituToTuLineSet=mySetItuLines if aSrc == ituPath else None,
                )
        except ItuToHtml.ExceptionItuToHTML as err:
            logging.error('Can not write ITU "%s" to HTML: %s', aSrc, str(err))
    indexPath = writeIndexHtml([ituPath, ], outDir, jobSpec)
    logging.info('preprocessFileToOutput(): %s DONE' % ituPath)
    # Return the path to the ITU and to the index.html path for consolidation
    # by the caller - to be used in multiprocessing.
    return PpProcessResult(ituPath, indexPath, tuIndexFileName(ituPath))

def main():
    """Processes command line to preprocess a file or a directory."""
    program_version = "v%s" % __version__
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = """%s
  Created by Paul Ross on %s.
  Copyright 2008-2015. All rights reserved.
  Licensed under GPL 2.0
USAGE
""" % (program_shortdesc, str(__date__))
    parser = argparse.ArgumentParser(description=program_license,
                            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-c", action="store_true", dest="plot_conditional", default=False,
                      help="Add conditionally included files to the plots. [default: %(default)s]")
    parser.add_argument("-d", "--dump", action="append", dest="dump", default=[],
                      help="""Dump output, additive. Can be:
C - Conditional compilation graph.
F - File names encountered and their count.
I - Include graph.
M - Macro environment.
T - Token count.
R - Macro dependencies as an input to DOT.
[default: %(default)s]""")
    parser.add_argument("-g", "--glob", type=str, dest="glob", default="*.*",
            help="Pattern match to use when processing directories. [default: %(default)s]")
    parser.add_argument("--heap", action="store_true", dest="heap", default=False,
                      help="Profile memory usage. [default: %(default)s]")
    parser.add_argument(
            "-j", "--jobs",
            type=int,
            dest="jobs",
            default=0,
            help="""Max simultaneous processes when pre-processing
directories. Zero uses number of native CPUs [%d].
1 means no multiprocessing."""
                    % multiprocessing.cpu_count() \
                    + " [default: %(default)s]"
        )
    parser.add_argument("-k", "--keep-going", action="store_true",
                         dest="keep_going", default=False,
                         help="Keep going. [default: %(default)s]")
    parser.add_argument(
            "-l", "--loglevel",
            type=int,
            dest="loglevel",
            default=30,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50)" \
            " [default: %(default)s]"
        )
    parser.add_argument("-o", "--output",
                         type=str,
                         dest="output",
                         default="out",
                         help="Output directory. [default: %(default)s]")
    parser.add_argument("-p", action="store_true", dest="ignore_pragma", default=False,
                      help="Ignore pragma statements. [default: %(default)s]")
    parser.add_argument("-r", "--recursive", action="store_true", dest="recursive",
                         default=False,
                      help="Recursively process directories. [default: %(default)s]")
    parser.add_argument("-t", "--dot", action="store_true", dest="include_dot",
                         default=False,
                      help="""Write an DOT include dependency table and execute DOT
on it to create a SVG file. [default: %(default)s]""")
    parser.add_argument(dest="path", nargs=1, help="Path to source file.")
    Cpp.addStandardArguments(parser)
    args = parser.parse_args()
#     print(' ARGS '.center(75, '-'))
#     print(args)
#     print(' END: ARGS '.center(75, '-'))
    clkStart = time.clock()
    # Initialise logging etc.
    inPath = args.path[0]
    if args.jobs != 1 and os.path.isdir(inPath):
        # Multiprocessing
        logFormat = '%(asctime)s %(levelname)-8s [%(process)5d] %(message)s'
    else:
        logFormat = '%(asctime)s %(levelname)-8s %(message)s'
    logging.basicConfig(level=args.loglevel,
                    format=logFormat,
                    # datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    # Memory usage dump
    if args.heap:
        try:
            from guppy import hpy
        except ImportError:
            print('Can not profile memory as you do not have guppy installed:' \
                  ' http://guppy-pe.sourceforge.net/')
            args.heap = False
    # Start memory profiling if requested
    if args.heap:
        myHeap = hpy()
        myHeap.setrelheap()
    else:
        myHeap = None
    # Create objects to pass to pre-processor
    myIncH = IncludeHandler.CppIncludeStdOs(
                    theUsrDirs=args.incUsr or [],
                    theSysDirs=args.incSys or [],
    )
    preDefMacros = {}
    if args.predefines:
        for d in args.predefines:
            _tup = d.split('=')
            if len(_tup) == 2:
                preDefMacros[_tup[0]] = _tup[1] + '\n'
            elif len(_tup) == 1:
                preDefMacros[_tup[0]] = '\n'
            else:
                raise ValueError('Can not read macro definition: %s' % d)
    # Add macros in psuedo pre-include
    preIncStr = ''
    if args.defines:
        preIncStr = u'\n'.join(['#define ' + ' '.join(d.split('=')) for d in args.defines]) + '\n'
    # Create the job specification
    jobSpec = MainJobSpec(
        incHandler=myIncH,
        preIncStr=preIncStr,
        preDefMacros=preDefMacros,
        preIncPaths=args.preInc,
        diagnostic=CppDiagnostic.PreprocessDiagnosticKeepGoing() if args.keep_going else None,
        pragmaHandler=PragmaHandler.PragmaHandlerNull() if args.ignore_pragma else None,
        keepGoing=args.keep_going,
        conditionalLevel=2 if args.plot_conditional else 0,
        dumpList=args.dump,
        helpMap=retOptionMap(parser, args),
        includeDOT=args.include_dot,
        cmdLine=' '.join(sys.argv),
    )
    if os.path.isfile(inPath):
        preprocessFileToOutput(inPath, args.output, jobSpec)
        writeIndexHtml([inPath], args.output, jobSpec)
    elif os.path.isdir(inPath):
        preprocessDirToOutput(
            inPath,
            args.output,
            jobSpec,
            globMatch=args.glob,
            recursive=args.recursive,
            numJobs=args.jobs,
            )
    else:
        logging.fatal('%s is neither a file or a directory!' % inPath)
        return 1
    if args.heap and myHeap is not None:
        print('Dump of heap:')
        h = myHeap.heap()
        print(h)
        print()
        print('Dump of heap byrcs:')
        print(h.byrcs)
        print()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
