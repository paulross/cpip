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

"""Writes out the Cpp Conditional processing graph as HTML."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__rights__  = 'Copyright (c) 2008-2017 Paul Ross'

import os

import cpip
from cpip.core import CppCond
from cpip.util import XmlWrite
from cpip.util import HtmlUtils
from cpip import TokenCss

def linkToIndex(theS, theIdxPath):
    """Write a back link to the index page.

    :param theS: The HTML stream.
    :type theS: :py:class:`cpip.util.XmlWrite.XhtmlStream`

    :param theIdxPath: <insert documentation for argument>
    :type theIdxPath: ``str``

    :returns: ``NoneType``
    """
    with XmlWrite.Element(theS, 'p'):
        theS.characters('Return to ')
        with XmlWrite.Element(theS, 'a', {'href' : theIdxPath}):
            theS.characters('Index')

class CcgVisitorToHtml(CppCond.CppCondGraphVisitorBase):
    """Writing CppCondGraph visitor object."""
    PAD_STR = '  '
    def __init__(self, theHtmlStream):
        """Constructor with an output XmlWrite.XhtmlStream.

        :param theHtmlStream: The HTML stream.
        :type theHtmlStream: :py:class:`cpip.util.XmlWrite.XhtmlStream`

        :returns: ``NoneType``
        """
        super(CcgVisitorToHtml, self).__init__()
        self._hs = theHtmlStream
        
    def visitPre(self, theCcgNode, theDepth):
        """Pre-traversal call with a CppCondGraphNode and the integer depth in
        the tree.

        :param theCcgNode: Graph node.
        :type theCcgNode: :py:class:`cpip.core.CppCond.CppCondGraphNode`

        :param theDepth: Node depth.
        :type theDepth: ``int``

        :returns: ``NoneType``
        """
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
        the tree.

        :param theCcgNode: Graph node.
        :type theCcgNode: :py:class:`cpip.core.CppCond.CppCondGraphNode`

        :param theDepth: Node depth.
        :type theDepth: ``int``

        :returns: ``NoneType``
        """
        pass

def processCppCondGrphToHtml(theLex,
                             theHtmlPath,
                             theTitle,
                             theIdxPath):
    """Given the PpLexer write out the Cpp Cond Graph to the HTML file.

    :param theLex: The lexer.
    :type theLex: :py:class:`cpip.core.PpLexer.PpLexer`

    :param theHtmlPath: Path to output HTML file.
    :type theHtmlPath: ``str``

    :param theTitle: Title.
    :type theTitle: ``str``

    :param theIdxPath: Path to index page for back links.
    :type theIdxPath: ``str``

    :returns: ``NoneType``
    """
    if not os.path.exists(os.path.dirname(theHtmlPath)):
        os.makedirs(os.path.dirname(theHtmlPath))
    # Note: Callers responsibility to write the CSS file
    ## Write CSS
    #TokenCss.writeCssToDir(os.path.dirname(theHtmlPath))
    # Process the TU
    with XmlWrite.XhtmlStream(theHtmlPath, mustIndent=cpip.INDENT_ML) as myS:
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
            with XmlWrite.Element(myS, 'p'):
                myS.characters("""The conditional compilation statements as green (i.e. evaluates as True)
and red (evaluates as False). Each statement is linked to the source code it came from.
""")
            linkToIndex(myS, theIdxPath)
            with XmlWrite.Element(myS, 'pre'):
                myVisitor = CcgVisitorToHtml(myS)
                theLex.condCompGraph.visit(myVisitor)
