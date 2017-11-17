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

"""Converts an Initial Translation Unit (ITU) i.e. a file, to HTML."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__rights__  = 'Copyright (c) 2008-2017 Paul Ross'

import sys
import os
import time
import logging
from optparse import OptionParser

import cpip
from cpip import ExceptionCpip
from cpip.core import ItuToTokens
from cpip.core import CppDiagnostic
from cpip.util import XmlWrite
from cpip.util import HtmlUtils
from cpip import TokenCss

class ExceptionItuToHTML(ExceptionCpip):
    pass
    
class ItuToHtml(object):
    """Converts an ITU to HTML and write it to the output directory."""
    _condCompClassMap = {
        -1 : 'Maybe',
        0 : 'False',
        1 : 'True',
    }
    def __init__(self, theItu, theHtmlDir, keepGoing=False,
                 macroRefMap=None, cppCondMap=None, ituToTuLineSet=None):
        """Takes an input source file and an output directory.

        :param theItu: The original source file path (or file like object for the input).
        :type theItu: ``str``

        :param theHtmlDir: The output directory for the HTML or a file-like object
            for the output.
        :type theHtmlDir: ``str``

        :param keepGoing: If ``True`` keep going as far as possible.
        :type keepGoing: ``bool``

        :param macroRefMap: Map of ``{identifier : href_text, ...)`` to link to macro definitions.
        :type macroRefMap: ``dict({str : [list([tuple([<class 'str'>, <class 'int'>, str])]), list([tuple([<class 'str'>, int, str])]), list([tuple([str, int, str])])]})``

        :param cppCondMap: Conditional compilation map.
        :type cppCondMap: :py:class:`cpip.core.CppCond.CppCondGraphVisitorConditionalLines`

        :param ituToTuLineSet: Set of integer line numbers which are lines that
            can be linked to the translation unit representation.
        :type ituToTuLineSet: ``NoneType, set([int])``

        :returns: ``NoneType``
        """
        try:
            # Assume string or unicode first
            self._fpIn = theItu
            self._ituFileObj = open(self._fpIn)
        except TypeError:
            self._fpIn = 'Unknown'
            self._ituFileObj = theItu
        if isinstance(theHtmlDir, str):
            if not os.path.exists(theHtmlDir):
                os.makedirs(theHtmlDir)
            self._fOut = open(os.path.join(theHtmlDir, HtmlUtils.retHtmlFileName(self._fpIn)), 'w')
        else:
            self._fOut = theHtmlDir
        self._keepGoing = keepGoing
        # Map of {identifier : href_text, ...) to link to macro definitions.
        self._macroRefMap = macroRefMap or {}
        self._cppCondMap = cppCondMap
        self._ituToTuLineSet = ituToTuLineSet
        # Start at 0 as this gets incremented before write
        self._lineNum = 0
        self._convert()
    
    def _convert(self):
        """Convert ITU to HTML.

        :returns: ``NoneType``

        :raises: ``ExceptionItuToHTML`` on failure.
        """
        # Create reader
        myItt = self._initReader()
        # Create writer and iterate
        if self._fOut is None:
            return
        try:
            with XmlWrite.XhtmlStream(self._fOut, mustIndent=cpip.INDENT_ML) as myS:
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
                    with XmlWrite.Element(myS, 'p'):
                        myS.characters("""Green shading in the line number column
means the source is part of the translation unit, red means it is conditionally excluded.
Highlighted line numbers link to the translation unit page. Highlighted macros link to
the macro page.""")
                    with XmlWrite.Element(myS, 'pre'):
                        myS.xmlSpacePreserve()
                        self._incAndWriteLine(myS)
                        for t, tt in myItt.genTokensKeywordPpDirective():
                            self._handleToken(myS, t, tt)
        except (IOError) as err:
            raise ExceptionItuToHTML('%s line=%d, col=%d' \
                        % (
                            str(err),
                            myItt.fileLocator.lineNum,
                            myItt.fileLocator.colNum,
                        )
                    )
                    
    def _handleToken(self, theS, t, tt):
        """Handle a token.

        :param theS: The HTML stream.
        :type theS: :py:class:`cpip.util.XmlWrite.XhtmlStream`

        :param t: The token text.
        :type t: ``str``

        :param tt: The token type.
        :type tt: ``str``

        :returns: ``NoneType``
        """
        logging.debug('_handleToken(): "%s", %s', t, tt)
        if tt == 'whitespace':
            self._writeTextWithNewlines(theS, t, None)
        elif tt in ('C comment', 'C++ comment'):
            self._writeTextWithNewlines(theS, t, TokenCss.retClass(tt))
        elif False and tt == 'preprocessing-op-or-punc':
            theS.characters(t)
        else:
            if tt == 'identifier' and t in self._macroRefMap:
                # As we can not definitively determine which particular
                # definition of the macro is relevant for this source file
                # we just use the last definition in the list.
                assert len(self._macroRefMap[t]) > 0
                href = self._macroRefMap[t][-1][2]
                with XmlWrite.Element(theS, 'a', {'href' : href}):
                    with XmlWrite.Element(theS, 'span', {'class' : '%s' % TokenCss.retClass(tt)}):
                        theS.characters(t)
            else:
                with XmlWrite.Element(theS, 'span', {'class' : '%s' % TokenCss.retClass(tt)}):
                    self._lineNum += t.count('\n')
                    theS.characters(t)
    
    def _writeTextWithNewlines(self, theS, theText, spanClass):
        """Splits text by newlines and writes it out.

        :param theS: The HTML stream.
        :type theS: :py:class:`cpip.util.XmlWrite.XhtmlStream`

        :param theText: The text to write.
        :type theText: ``str``

        :param spanClass: CSS class.
        :type spanClass: ``NoneType, str``

        :returns: ``NoneType``
        """
        # Whitespace, line breaks
        myL = theText.split('\n')
        if len(myL) > 1:
            # Do all up to the last
            for s in myL[:-1]:
                if spanClass is not None:
                    with XmlWrite.Element(theS, 'span', {'class' : spanClass}):
                        theS.characters(s.replace('\t', '    '))
                else:
                    theS.characters(s.replace('\t', '    '))
                theS.characters('\n')
                self._incAndWriteLine(theS)
        # Now the last
        if spanClass is not None:
            with XmlWrite.Element(theS, 'span', {'class' : spanClass}):
                theS.characters(myL[-1].replace('\t', '    '))
        else:
            theS.characters(myL[-1].replace('\t', '    '))
    
    def _incAndWriteLine(self, theS):
        """Write a line.

        :param theS: The HTML stream.
        :type theS: :py:class:`cpip.util.XmlWrite.XhtmlStream`

        :returns: ``NoneType``
        """
        self._lineNum += 1
        classAttr = 'line'
        if self._cppCondMap is not None:
            try:
                lineIsCompiled = self._cppCondMap.isCompiled(self._fpIn, self._lineNum)
            except KeyError:
                logging.error('_incAndWriteLine(): Ambiguous compilation: path: "{!r:s}" Line: {!r:s}'.format(self._fpIn, self._lineNum))
                pass
            else:
                classAttr = self._condCompClassMap[lineIsCompiled]
#       # Write a link to the TU representation if I am the ITU
        if self._ituToTuLineSet is not None \
        and self._lineNum in self._ituToTuLineSet:
            myHref = '%s.html#%d' % (os.path.basename(self._fpIn), self._lineNum)
        else:
            myHref = None
        HtmlUtils.writeHtmlFileAnchor(
                theS,                   # The html stream
                self._lineNum,          # <a name="self._lineNum"
                '%8d:' % self._lineNum, # Characters to write
                classAttr,              # <span class="classAttr"> to wrap the characters
                theHref=myHref)         # In not None then insert <a href="theHref"
        theS.characters(' ')
        
    def _initReader(self):
        """Create and return a reader, initialise internals.

        :returns: :py:class:`cpip.core.ItuToTokens.ItuToTokens`
            -- The file tokeniser.
        """
        if self._keepGoing:
            myDiagnostic = CppDiagnostic.PreprocessDiagnosticKeepGoing()
        else:
            myDiagnostic = None
        try:
            myItt = ItuToTokens.ItuToTokens(
                    theFileObj=self._ituFileObj,
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
                    stream=sys.stdout)
    if len(args) != 2:
        optParser.print_help()
        optParser.error("No arguments!")
        return 1
    TokenCss.writeCssToDir(args[1])
    ItuToHtml(args[0], args[1])
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    sys.exit(main())
