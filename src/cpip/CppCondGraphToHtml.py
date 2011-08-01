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

"""Writes out the Cpp Conditional processing graph as HTML."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import os

from cpip.core import CppCond
from cpip.util import XmlWrite
from cpip.util import HtmlUtils
import TokenCss

def linkToIndex(theS, theIdxPath):
    with XmlWrite.Element(theS, 'p'):
        theS.characters('Return to ')
        with XmlWrite.Element(theS, 'a', {'href' : theIdxPath}):
            theS.characters('Index')

class CcgVisitorToHtml(CppCond.CppCondGraphVisitorBase):
    """Writing CppCondGraph visitor object."""
    PAD_STR = '    '
    def __init__(self, theHtmlStream):
        """Constructor with an output XmlWrite.XhtmlStream and
        a a TuIndexer.TuIndexer object."""
        super(CcgVisitorToHtml, self).__init__()
        self._hs = theHtmlStream
        
    def visitPre(self, theCcgNode, theDepth):
        """Pre-traversal call with a CppCondGraphNode and the integer depth in
        the tree."""
        self._hs.characters(self.PAD_STR * theDepth)
        if theCcgNode.state:
            myCssClass = 'CcgNodeTrue'
        else:
            myCssClass = 'CcgNodeFalse'
        with XmlWrite.Element(self._hs, 'span', {'class' : myCssClass}):
            self._hs.characters('#%s' % theCcgNode.cppDirective)
            if theCcgNode.constExpr is not None:
                self._hs.characters(' %s' % theCcgNode.constExpr)
        self._hs.characters(' ')
        self._hs.characters(' /* ')
        HtmlUtils.writeHtmlFileLink(
                self._hs,
                theCcgNode.fileId,
                theCcgNode.lineNum,
                os.path.basename(theCcgNode.fileId),
                theClass=None,
            )
        self._hs.characters(' */')
        #with XmlWrite.Element(self._hs, 'span', {'class' : 'file'}):
        #    self._hs.characters(' [%s]' % theCcgNode.fileId)
        self._hs.characters('\n')
            
        
    def visitPost(self, theCcgNode, theDepth):
        """Post-traversal call with a CppCondGraphNode and the integer depth in
        the tree."""
        pass

def processCppCondGrphToHtml(theLex,
                             theHtmlPath,
                             theTitle,
                             theIdxPath):
    """Given the PpLexer write out the Cpp Cond Graph to the HTML file.
    theLex is a PpLexer.
    theHtmlPath is the file path of the output.
    theTitle is the page title.
    theIdxPath is the file name of the index page.
    theTuIndexer is a TuIndexer.TuIndexer object."""
    if not os.path.exists(os.path.dirname(theHtmlPath)):
        os.makedirs(os.path.dirname(theHtmlPath))
    # Note: Callers responsibility to write the CSS file
    ## Write CSS
    #TokenCss.writeCssToDir(os.path.dirname(theHtmlPath))
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
        with XmlWrite.Element(myS, 'body'):
            with XmlWrite.Element(myS, 'h1'):
                myS.characters('Preprocessing Conditional Compilation Graph: %s' % theLex.tuFileId)
            linkToIndex(myS, theIdxPath)
            with XmlWrite.Element(myS, 'pre'):
                myVisitor = CcgVisitorToHtml(myS)
                theLex.condCompGraph.visit(myVisitor)
