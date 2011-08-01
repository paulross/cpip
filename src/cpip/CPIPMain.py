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

import os
import sys
import logging
import time
import types
from optparse import OptionParser
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
#import pprint
#import subprocess
import multiprocessing

#from cpip import ExceptionCpip
from cpip.core import PpLexer
from cpip.core import IncludeHandler
from cpip.core import CppDiagnostic
from cpip.core import FileIncludeGraph
from cpip.core import PragmaHandler
from cpip.util import XmlWrite
from cpip.util import HtmlUtils
#from cpip.plot import TreePlotTransform
import Tu2Html
import MacroHistoryHtml
import IncGraphSVGBase
import IncGraphSVG
import IncGraphSVGPpi
import ItuToHtml
import TokenCss
import CppCondGraphToHtml

def unitTest():
    pass

class FigVisitorDot(FileIncludeGraph.FigVisitorBase):
    """Simple visitor that collects parent/child links for plotting the graph with dot."""
    def __init__(self):
        super(FigVisitorDot, self).__init__()
        self._rootS = []
        self._lineS = []
        
    def __str__(self):
        retL = ['digraph FigVisitorDot {',]
        if len(self._rootS) > 1:
            retL.append('%s;' % ' -> '.join(self._rootS))
        retL.extend(self._lineS)
        retL.append('}\n')
        return '\n'.join(retL)
        
    def visitGraph(self, theFigNode, theDepth, theLine): 
        """."""
        myF = theFigNode.fileName
        if theDepth == 1:
            self._rootS.append('"%s"' % myF)
        hasC = False
        for aC in theFigNode.genChildNodes():
            self._lineS.append('"%s" -> "%s";' % (myF, aC.fileName))
            hasC = True
        if not hasC:
            self._lineS.append('"%s";' % (myF))

def retFileCountMap(theLexer):
    myFigr = theLexer.fileIncludeGraphRoot
    myFileNameVis = FileIncludeGraph.FigVisitorFileSet()
    myFigr.acceptVisitor(myFileNameVis)
    return myFileNameVis.fileNameMap

def _dumpCondCompGraph(theLexer):
    print
    print ' Conditional Compilation Graph '.center(75, '-')
    myFigr = theLexer.condCompGraph
    print myFigr
    print ' END Conditional Compilation Graph '.center(75, '-')

def _dumpIncludeGraphDot(theLexer):
    print
    print ' Include Graph for DOT '.center(75, '-')
    myFigr = theLexer.fileIncludeGraphRoot
    myVis = FigVisitorDot()
    myFigr.acceptVisitor(myVis)
    print myVis
    print ' END Include Graph for DOT '.center(75, '-')

def _dumpIncludeGraph(theLexer):
    print
    print ' Include Graph '.center(75, '-')
    myFigr = theLexer.fileIncludeGraphRoot
    print myFigr
    print ' END Include Graph '.center(75, '-')

def _dumpFileCount(theFileCountMap):
    print
    myList = theFileCountMap.keys()
    myList.sort()
    print
    print ' Count of files encountered '.center(75, '-')
    for f in myList:
        print '%4d  %s' % (theFileCountMap[f], f)
    print ' END Count of files encountered '.center(75, '-')

def _dumpTokenCount(theTokenCounter):
    print
    print ' Token count '.center(75, '-')
    #print theTokenCounter
    myTotal = 0
    for tokType, tokCount in theTokenCounter.tokenTypesAndCounts(
                                        isAll=True,
                                        allPossibleTypes=True):
        print '%8d  %s' % (tokCount, tokType)
        myTotal += tokCount
    print '%8d  %s' % (myTotal, 'TOTAL')
    print ' END Token count '.center(75, '-')

def _dumpMacroEnv(theLexer):
    print
    print ' Macro Environment and History '.center(75, '-')
    print theLexer.macroEnvironment.macroHistory()
    print ' END Macro Environment and History '.center(75, '-')
    print

def _dumpMacroEnvDot(theLexer):
    print
    print ' Macro dependencies as a DOT file '.center(75, '-')
    print 'digraph MacroDependencyDot {'
    myMacEnv = theLexer.macroEnvironment
    for aPpDef in myMacEnv.genMacros():
        if aPpDef.isReferenced:
            for aRtok in aPpDef.replacementTokens:
                if aRtok.isIdentifier() and myMacEnv.hasMacro(aRtok.t):
                    print '"%s" -> "%s";' % (aPpDef.identifier, aRtok.t)
    print '}\n'
    print ' END Macro dependencies as a DOT file '.center(75, '-')
    print

def tuIndexFileName(theTu):
    return 'index_' + HtmlUtils.retHtmlFileName(theTu)

def tuFileName(theTu):
    return os.path.basename(theTu)+'.html'

def macroHistoryFileName(theItu):
    return os.path.basename(theItu)+'_macros'+'.html'

def includeGraphFileNameSVG(theItu):
    return os.path.basename(theItu)+'.include.svg'

def includeGraphFileNameSVGPpi(theItu):
    return os.path.basename(theItu)+'.include.ppi.svg'

def includeGraphFileNameCcg(theItu):
    return os.path.basename(theItu)+'.ccg.html'

def includeGraphFileNameText(theItu):
    return os.path.basename(theItu)+'.include.txt.html'

def writeIncludeGraphAsText(theOutDir, theItu, theLexer):
    def _linkToIndex(theS, theItu):
        with XmlWrite.Element(theS, 'p'):
            theS.characters('Return to ')
            with XmlWrite.Element(theS, 'a', {'href' : tuIndexFileName(theItu)}):
                theS.characters('Index')
    outPath = os.path.join(theOutDir, includeGraphFileNameText(theItu))
    with XmlWrite.XhtmlStream(outPath) as myS:
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
            _linkToIndex(myS, theItu)
            with XmlWrite.Element(myS, 'pre'):
                myS.characters(str(theLexer.fileIncludeGraphRoot))
            _linkToIndex(myS, theItu)

def writeTuIndexHtml(theOutDir, theTuPath, theLexer, theFileCountMap, theTokenCntr, incPpiLink):
    with XmlWrite.XhtmlStream(os.path.join(theOutDir, tuIndexFileName(theTuPath))) as myS:
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
            ###
            # Translation unit
            ###
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('1. Source Code')
            with XmlWrite.Element(myS, 'h3'):#'p'):
                myS.characters('As a ')
                with XmlWrite.Element(myS, 'a',{'href' : tuFileName(theTuPath),}):
                    myS.characters('Translation Unit')
                myS.characters(' or as ')
                with XmlWrite.Element(myS, 'a', {'href' : HtmlUtils.retHtmlFileName(theTuPath),}):
                    myS.characters('original source')
            ###
            # Include graph
            ###
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('2. Include Graphs')
            with XmlWrite.Element(myS, 'h3'):#'p'):
                myS.characters('As ')
                with XmlWrite.Element(myS, 'a',{'href' : includeGraphFileNameSVG(theTuPath),}):
                    myS.characters('Normal [SVG]')
                if incPpiLink:
                    myS.characters(', ')
                    with XmlWrite.Element(myS,'a', {'href' : includeGraphFileNameSVGPpi(theTuPath),}):
                        myS.characters('PPI [SVG]')
                myS.characters(' or ')
                with XmlWrite.Element(myS, 'a', {'href' : includeGraphFileNameText(theTuPath),}):
                    myS.characters('Text')
            ###
            # Conditional compilation
            ###
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('3. Conditional Compilation')
            with XmlWrite.Element(myS, 'h3'):#'p'):
                myS.characters('The conditional compilation ')
                with XmlWrite.Element(myS, 'a',{'href' : includeGraphFileNameCcg(theTuPath),}):
                    myS.characters('graph')
            ###
            # Macro history
            ###
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('4. Macros')
            with XmlWrite.Element(myS, 'h3'):
                myS.characters('The Macro ')
                with XmlWrite.Element(myS, 'a', {'href' : macroHistoryFileName(theTuPath),}):
                    myS.characters('Environment')
            ###
            # Write out token counter as a table
            ###
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('5. Token Count')
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
            with XmlWrite.Element(myS, 'p'):
                myS.characters('Number of individual files: %d' % len(theFileCountMap))
            # TODO: Value count
            #with XmlWrite.Element(myS, 'p'):
            #    myS.characters('Total files processed: %d' % sum(theFileCountMap.values()))
            myItuFileS = theFileCountMap.keys()
            myItuFileS.sort()
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
                for p in myItuFileS if p != theLexer.UNNAMED_FILE_NAME
            ]
            HtmlUtils.writeFilePathsAsTable(None, myS, myFileLinkS, 'filetable', tdCallback)
            with XmlWrite.Element(myS, 'br'):
                pass
            # TODO...
            with XmlWrite.Element(myS, 'p'):
                myS.characters('Produced by %s version: %s' % ('CPIPMain',  __version__))
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

def tdCallback(theS, attrs, k, v):
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
        
def writeIndexHtml(theOutDir, theTuS, theCmdLine, theOptMap):
    """Writes the top level index.html page.
    theOutDir - The output directory.
    theTuS - The list of translation units processed.
    theCmdLine - The command line as a string.
    theOptMap is a map of {opt_name : (value, help), ...} from the
        command line options."""
    theTuS.sort()
    with XmlWrite.XhtmlStream(os.path.join(theOutDir, 'index.html')) as myS:
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
                for aTu in theTuS:
                    with XmlWrite.Element(myS, 'li'):
                        with XmlWrite.Element(myS, 'tt'):
                            with XmlWrite.Element(myS, 'a', {'href' : tuIndexFileName(aTu)}):
                                myS.characters(aTu)
            # Command line
            with XmlWrite.Element(myS, 'h2'):
                myS.characters('CPIP Command line:')
            with XmlWrite.Element(myS, 'pre'):
                myS.characters(theCmdLine)
            # Command line options
            with XmlWrite.Element(myS, 'table', {'border' : "1"}):
                with XmlWrite.Element(myS, 'tr'):
                    with XmlWrite.Element(myS, 'th', {'style' : "padding: 2px 6px 2px 6px"}):
                        myS.characters('Option')
                    with XmlWrite.Element(myS, 'th', {'style' : "padding: 2px 6px 2px 6px"}):
                        myS.characters('Value')
                    with XmlWrite.Element(myS, 'th', {'style' : "padding: 2px 6px 2px 6px"}):
                        myS.characters('Description')
                optS = theOptMap.keys()
                optS.sort()
                for o in optS:
                    with XmlWrite.Element(myS, 'tr'):
                        # Option name
                        with XmlWrite.Element(myS, 'td', {'style' : "padding: 2px 6px 2px 6px"}):
                            with XmlWrite.Element(myS, 'tt'):
                                myS.characters(str(o))
                        # Option value
                        with XmlWrite.Element(myS, 'td', {'style' : "padding: 2px 6px 2px 6px"}):
                            with XmlWrite.Element(myS, 'tt'):
                                myVal = theOptMap[o][0]
                                # Break up lists as these can be quite long
                                if type(myVal) == types.ListType \
                                or type(myVal) == types.TupleType:
                                    if len(myVal) > 0:
                                        for i, aVal in enumerate(myVal):
                                            if i > 0:
                                                myS.characters(',')
                                                with XmlWrite.Element(myS, 'br'):
                                                    pass
                                            myS.characters(str(aVal))
                                    else:
                                        myS.literal('&nbsp;')
                                else:
                                    myS.characters(str(myVal))
                        # Option help
                        with XmlWrite.Element(myS, 'td', {'style' : "padding: 2px 6px 2px 6px"}):
                            # Substitute <br/> for "\n"
                            for i, aLine in enumerate(theOptMap[o][1].strip().split('\n')):
                                if i > 0:
                                    with XmlWrite.Element(myS, 'br'):
                                        pass
                                myS.characters(aLine)

def retOptionMap(theOptParser, theOpts):
    """Returns map of {opt_name : (value, help), ...} from the current options."""
    retMap = {}
    for o in theOptParser.option_list:
        myHelp = o.help.replace('[default: %default]', '')
#        if o.dest is not None:
#            retMap[o.dest] = (getattr(theOpts, o.dest), myHelp)
#        else:
#            retMap[o.dest] = (None, myHelp)
        if o.dest is not None:
            retMap[str(o)] = (getattr(theOpts, o.dest), myHelp)
        else:
            retMap[str(o)] = (None, myHelp)
    return retMap

def main():
    usage = """usage: %prog [options] files...
Preprocess the files."""
    #print 'Cmd: %s' % ' '.join(sys.argv)
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option("-c", action="store_true", dest="plot_conditional", default=False, 
                      help="Add conditionally included files to the plots. [default: %default]")
    optParser.add_option("-d", "--dump", action="append", dest="dump", default=[],
                      help="""Dump output, additive. Can be:
C - Conditional compilation graph.
F - File names encountered and their count.
I - Include graph.
M - Macro environment.
T - Token count.
D - Include graph as an input to DOT.
R - Macro dependencies as an input to DOT.
[default: %default]""")
    optParser.add_option("--heap", action="store_true", dest="heap", default=False, 
                      help="Profile memory usage. [default: %default]")
    optParser.add_option(
            "-j", "--jobs",
            type="int",
            dest="jobs",
            default=0,
            help="Max processes when multiprocessing. Zero uses number of native CPUs [%d]" \
                    % multiprocessing.cpu_count() \
                    + " [default: %default]" 
        )      
    optParser.add_option("-k", action="store_true", dest="keep_going", default=False, 
                      help="Keep going. [default: %default]")
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=30,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )      
    optParser.add_option("-n", action="store_true", dest="nervous", default=False, 
                      help="Nervous mode (do no harm). [default: %default]")
    optParser.add_option("-o", "--output",
                         type="string",
                         dest="output",
                         default="out", 
                         help="Output directory. [default: %default]")
    optParser.add_option("-p", action="store_true", dest="ignore_pragma", default=False, 
                      help="Ignore pragma statements. [default: %default]")
    # The PPI graph is optional
    optParser.add_option("-q", action="store_true", dest="write_ppi_graph", default=False, 
                      help="Writes a Public/Platform/Internal include graph in SVG. [default: %default]")
#    optParser.add_option("-u", "--unittest",
#                         action="store_true",
#                         dest="unit_test",
#                         default=False, 
#                         help="Execute unit tests. [default: %default]")
    # List type options
    optParser.add_option("-I", "--usr", action="append", dest="incUsr", default=[],
                      help="Add user include search path. [default: %default]")
    optParser.add_option("-J", "--sys", action="append", dest="incSys", default=[],
                      help="Add system include search path. [default: %default]")
    optParser.add_option("-P", "--pre", action="append", dest="preInc", default=[],
                      help="Add pre-include file path. [default: %default]")
    optParser.add_option("-D", "--define", action="append", dest="defines", default=[],
                      help="""Add macro defintions of the form name<=defintion>.
                      These are introduced into the environment before any pre-include. [default: %default]""")
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    #if opts.unit_test:
    #    unitTest()
    # Memory usage dump
    if opts.heap:
        try:
            from guppy import hpy
        except ImportError:
            print 'Can not profile memory as you do not have guppy installed: http://guppy-pe.sourceforge.net/'
            opts.heap = False
    if len(args) > 0:
        # Start memory profiling if requested
        if opts.heap:
            myHeap = hpy()
            myHeap.setrelheap()
        else:
            myHeap = None
        myIncH = IncludeHandler.CppIncludeStdOs(
                        theUsrDirs=opts.incUsr or [],
                        theSysDirs=opts.incSys or [],
                                                  )
        myItuToHtmlFileSet = set()
        # We treat the myMacroRefMap as global to a set of ITUs but
        # actually it is specific to an ITU. The reason is that there is an
        # optimisation in place that writes the ITH HTML files once per set
        # of ITUs rather than per ITU. Most times this won't matter but it
        # could be the cause of subtle bugs when myMacroRefMap gets over
        # written by successive calls to
        # MacroHistoryHtml.processMacroHistoryToHtml
        # So here we only update myMacroRefMap is there is a single argument.
        # TODO: A better idea?
        myMacroRefMap = {}
        for anItu in args:
            myPreIncFiles = []
            # Add macros in psuedo pre-include
            if opts.defines:
                myStr = '\n'.join(['#define '+' '.join(d.split('=')) for d in opts.defines])+'\n'
                myPreIncFiles = [StringIO.StringIO(myStr), ]
                #print 'TRACE: myStr', myStr
            myPreIncFiles.extend([open(f) for f in opts.preInc])
            myDiag = None
            if opts.keep_going:
                myDiag = CppDiagnostic.PreprocessDiagnosticKeepGoing()
            myPh = None
            if opts.ignore_pragma:
                myPh = PragmaHandler.PragmaHandlerNull()
            # Create the lexer.
            myLexer = PpLexer.PpLexer(
                            anItu,
                            myIncH,
                            preIncFiles=myPreIncFiles,
                            diagnostic=myDiag,
                            pragmaHandler=myPh,
                            )
            if opts.plot_conditional:
                myCondLevel = 2
            else:
                myCondLevel = 0
            myDestFile = os.path.join(opts.output, tuFileName(anItu))
            logging.info('TU in HTML:')
            logging.info('  %s', myDestFile)
            myTokCntr = Tu2Html.processTuToHtml(
                                    myLexer,
                                    myDestFile,
                                    anItu,
                                    myCondLevel,
                                    tuIndexFileName(anItu), # Path back to the index
                                )
            logging.info('Processing TU done.')
            myFileCountMap = retFileCountMap(myLexer)
            # Write out the HTML for each source file
            mySrcFileS = myFileCountMap.keys()
            mySrcFileS.sort()
            for aSrc in mySrcFileS:
                myItuToHtmlFileSet.add(aSrc)
            # Now output state
            # Conditional compilation graph
            if 'C' in opts.dump:
                _dumpCondCompGraph(myLexer)
            # Conditional compilation graph
            if 'D' in opts.dump:
                _dumpIncludeGraphDot(myLexer)
            # File include graph
            if 'I' in opts.dump:
                _dumpIncludeGraph(myLexer)
            # List files encountered
            if 'F' in opts.dump:
                _dumpFileCount(myFileCountMap)
            # Token count
            if 'T' in opts.dump:
                _dumpTokenCount(myTokCntr)
            # Macro environment
            if 'M' in opts.dump:
                _dumpMacroEnv(myLexer)
            if 'R' in opts.dump:
                _dumpMacroEnvDot(myLexer)
            # Macro environment and history
            outPath = os.path.join(opts.output, macroHistoryFileName(anItu))
            logging.info('Macro history to:')
            logging.info('  %s', outPath)
            tempMap = MacroHistoryHtml.processMacroHistoryToHtml(
                    myLexer,
                    outPath,
                    anItu,
                    tuIndexFileName(anItu),
                )
            if len(args) == 1:
                myMacroRefMap.update(tempMap)
            #print 'TRACE: myMacroRefMap', myMacroRefMap
            # Write Include graph in SVG
            outPath = os.path.join(opts.output, includeGraphFileNameSVG(anItu))
            logging.info('Include graph (SVG) to:')
            logging.info('  %s', outPath)
            IncGraphSVGBase.processIncGraphToSvg(
                    myLexer,
                    outPath,
                    IncGraphSVG.SVGTreeNodeMain,
                    'left',
                    '+',
                )
            if opts.write_ppi_graph:
                outPath = os.path.join(opts.output, includeGraphFileNameSVGPpi(anItu))
                logging.info('Include graph PPI (SVG) to:')
                logging.info('  %s', outPath)
                IncGraphSVGBase.processIncGraphToSvg(
                        myLexer,
                        outPath,
                        IncGraphSVGPpi.SVGTreeNodePpi,
                        'left',
                        '+',
                    )
            # Write Include graph in Text
            logging.info('Writing include graph (TEXT) to:')
            logging.info('  %s', outPath)
            writeIncludeGraphAsText(opts.output, anItu, myLexer)
            # Write Conditional compilation graph in HTML
            outPath = os.path.join(opts.output, includeGraphFileNameCcg(anItu))
            logging.info('Conditional compilation graph in HTML:')
            logging.info('  %s', outPath)
            CppCondGraphToHtml.processCppCondGrphToHtml(
                    myLexer,
                    outPath,
                    'Conditional Compilation Graph',
                    tuIndexFileName(anItu),
                )            
            # This is an index for the TU
            writeTuIndexHtml(opts.output, anItu, myLexer, myFileCountMap, myTokCntr, opts.write_ppi_graph)
            logging.info('Done: %s', anItu)
        mySrcFileS = list(myItuToHtmlFileSet)
        mySrcFileS.sort()
        for aSrc in mySrcFileS:
            try:
                # Could be 'Unnamed Pre-include'
                if aSrc != myLexer.UNNAMED_FILE_NAME:
                    logging.info('ITU in HTML: ...\\%s', os.path.basename(aSrc))
                    ItuToHtml.ItuToHtml(
                        aSrc,
                        opts.output,
                        opts.keep_going,
                        macroRefMap=myMacroRefMap,
                    )
            except ItuToHtml.ExceptionItuToHTML, err:
                logging.error('Can not write ITU "%s" to HTML: %s', aSrc, str(err))
        # An index.html for all the args with the command line and options
        writeIndexHtml(
                opts.output,
                args,
                ' '.join(sys.argv),
                retOptionMap(optParser, opts),
            )
        logging.info('All done.')
        if opts.heap and myHeap is not None:
            print 'Dump of heap:'
            h = myHeap.heap()
            print h
            print
            print 'Dump of heap byrcs:'
            print h.byrcs
            print
    else:
        optParser.print_help()
        optParser.error("No arguments!")
        return 1
    clkExec = time.clock() - clkStart
    print 'CPU time = %8.3f (S)' % clkExec
    print 'Bye, bye!'
    return 0

if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
    