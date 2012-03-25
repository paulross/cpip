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

"""Converts an ITU to HTML."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import sys
import os
import time
import logging
from optparse import OptionParser

from cpip import ExceptionCpip
from cpip.core import ItuToTokens
from cpip.core import CppDiagnostic
from cpip.util import XmlWrite
from cpip.util import HtmlUtils
from cpip.util.MultiPassString import ExceptionMultiPass
from cpip import TokenCss

class ExceptionItuToHTML(ExceptionCpip):
    pass
    
class ItuToHtml(object):
    """Converts an ITU to HTML and write it to the output directory."""
    def __init__(self, theItuPath, theHtmlDir, keepGoing=False, macroRefMap=None):
        """Takes an input source file and an output directory.
        theItuPath - The original source file path
        theHtmlDir - The output directory for the HTML
        keepGoing - Bool, if True raise on error.
        macroRefMap - Map of {identifier : href_text, ...) to link to macro definitions."""
        self._fpIn = theItuPath
        self._fpOut = os.path.join(theHtmlDir, HtmlUtils.retHtmlFileName(self._fpIn))
        if not os.path.exists(theHtmlDir):
            os.makedirs(theHtmlDir)
        self._keepGoing = keepGoing
        # Map of {identifier : href_text, ...) to link to macro definitions.
        self._macroRefMap = macroRefMap or {}
        # Start at 0 as this gets incremented before write
        self._lineNum = 0
        self._convert()
    
    def _convert(self):
        """Convert ITU to HTML."""
        # Create reader
        myItt = self._initReader()
        # Create writer and iterate
        try:
            with XmlWrite.XhtmlStream(self._fpOut) as myS:
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
                        myS.characters('File: %s' % self._fpIn)
                with XmlWrite.Element(myS, 'body'):
                    with XmlWrite.Element(myS, 'h1'):
                        myS.characters('File: %s' % self._fpIn)
                    with XmlWrite.Element(myS, 'pre'):
                        myS.xmlSpacePreserve()
                        self._incAndWriteLine(myS)
                        for t, tt in myItt.genTokensKeywordPpDirective():
                            self._handleToken(myS, t, tt)
        except (ExceptionMultiPass, IOError) as err:
            raise ExceptionItuToHTML('%s line=%d, col=%d' \
                        % (
                            str(err),
                            myItt.fileLocator.lineNum,
                            myItt.fileLocator.colNum,
                        )
                    )
#===============================================================================
#        print 'TRACE: _convert() done: line=%d, col=%d' \
#                    % (
#                        myItt.fileLocator.lineNum,
#                        myItt.fileLocator.colNum,
#                    )
#===============================================================================
                    
    def _handleToken(self, theS, t, tt):
        logging.debug('_handleToken(): "%s", %s', t, tt)
        if tt == 'whitespace':
            self._writeTextWithNewlines(theS, t)
        elif tt in ('C comment', 'C++ comment'):
            with XmlWrite.Element(theS, 'span', {'class' : '%s' % TokenCss.retClass(tt)}):
                self._writeTextWithNewlines(theS, t)
        elif False and tt == 'preprocessing-op-or-punc':
            theS.characters(t)
        else:
            if tt == 'identifier' and t in self._macroRefMap:
                # Make a link to a macro definition
                with XmlWrite.Element(theS, 'a', {'href' : self._macroRefMap[t]}):
                    with XmlWrite.Element(theS, 'span', {'class' : '%s' % TokenCss.retClass(tt)}):
                        theS.characters(t)
            else:
                with XmlWrite.Element(theS, 'span', {'class' : '%s' % TokenCss.retClass(tt)}):
                    self._lineNum += t.count('\n')
                    theS.characters(t)
    
    def _writeTextWithNewlines(self, theS, theText):
        """Splits text by newlines and writes it out."""
        # Whitespace, line breaks
        myL = theText.split('\n')
        if len(myL) > 1:
            # Do all up to the last
            for s in myL[:-1]:
                theS.characters(s.replace('\t', '    '))
                theS.characters('\n')
                self._incAndWriteLine(theS)
        # Now the last
        theS.characters(myL[-1].replace('\t', '    '))
    
    def _incAndWriteLine(self, theS):
        self._lineNum += 1
        HtmlUtils.writeHtmlFileAnchor(
                theS,
                self._lineNum,
                '%8d: ' % self._lineNum,
                'line')
        
    def _initReader(self):
        """Create and return a reader, initialise internals."""
        if self._keepGoing:
            myDiagnostic = CppDiagnostic.PreprocessDiagnosticKeepGoing()
        else:
            myDiagnostic = None
        try:
            myItt = ItuToTokens.ItuToTokens(
                    theFileObj=open(self._fpIn),
                    theFileId=self._fpIn,
                    theDiagnostic=myDiagnostic,
                )
        except IOError as err:
            raise ExceptionItuToHTML(str(err))
        self._lineNum = 0
        return myItt
        
def main():
    usage = """usage: %prog [options] source out_dir
Converts a source code file to HTML in the output directory."""
    print('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=30,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )      
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    if len(args) != 2:
        optParser.print_help()
        optParser.error("No arguments!")
        return 1
    # Your code here
    TokenCss.writeCssToDir(args[1])
    myIth = ItuToHtml(args[0], args[1])
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    sys.exit(main())
