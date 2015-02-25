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

"""Generates an XML file from an include graph.

This is implemented as a hierarchical visitor pattern. This could have be
implemented as a non-hierarchical visitor pattern using less memory
at the expense of more code.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

#import os
#import sys
from cpip.core import FileIncludeGraph
from cpip.core import PpToken
from cpip.core import PpTokenCount
from cpip.util import XmlWrite
#from cpip.plot import PlotNode

def processIncGraphToXml(theLex, theFilePath):
    """Convert a Include graph from a PpLexer to SVG in theFilePath."""
    myVis = FileIncludeGraph.FigVisitorTree(IncGraphXML)
    theLex.fileIncludeGraphRoot.acceptVisitor(myVis)
    # Tree is now a graph of class IncGraphXML objects
    myIgs = myVis.tree()
    # Write to file
    myIgs.writeToFilePath(theFilePath)

class IncGraphXML(FileIncludeGraph.FigVisitorTreeNodeBase):
    def __init__(self, theFig, theLineNum):
        super(IncGraphXML, self).__init__(theLineNum)
        self._isRoot = theFig is None
        self._tokenCounterChildren = PpTokenCount.PpTokenCount()
        if self._isRoot:
            # Root node, children only
            self._dataMap = None
        else:
            self._dataMap = {}
            # Take a copy of the include graph data
            self._dataMap['fileName']       = theFig.fileName
            self._dataMap['numToks']        = theFig.numTokens
            # This is a string - currently See core.CppCond for
            # how this might change.
            self._dataMap['condComp']       = theFig.condComp
            self._dataMap['condCompState']  = theFig.condCompState
            # A PpTokenCount.PpTokenCount() object.
            self._dataMap['tokenCntr']      = theFig.tokenCounter
            # Another string
            self._dataMap['findLogic']      = theFig.findLogic
    
    @property
    def tokenCounter(self):
        """This is the computed PpTokenCount.PpTokenCount() me only."""
        return self._dataMap['tokenCntr']

    @property
    def tokenCounterChildren(self):
        """This is the computed PpTokenCount.PpTokenCount() for all my children but not me."""
        return self._tokenCounterChildren

    #===================================
    # Section: Finalisation and plotting
    #===================================
    def finalise(self):
        """This will be called on finalisation. This just accumulates the
        child token counter."""
        self._tokenCounterChildren = PpTokenCount.PpTokenCount()
        for aChild in self._children:
            aChild.finalise()
        for aChild in self._children:
            self._tokenCounterChildren += aChild.tokenCounter
            self._tokenCounterChildren += aChild.tokenCounterChildren
    
    def writeToFilePath(self, theFileName):
        """Root level call to plot to a SVG file, theTpt is an
        TreePlotTransform object and is used to transform the internal logical
        coordinates to physical plot positions."""
        self.writeToFileObj(open(theFileName, 'w'))
        
    def writeToFileObj(self, theFileObj):
        """Root level call to plot to a file object. The SVG stream is
        created here."""
        with XmlWrite.XmlStream(theFileObj) as myS:
            self.writeToSVGStream(myS)

    def writeToSVGStream(self, theS):
        """Write me to a stream and my children at the logical datum point,
        this is a recursive call."""
        if not self._isRoot:
            self._writeSelf(theS)
        if len(self._children) > 0:
            for c in self._children:
                c.writeToSVGStream(theS)

    def _writeSelf(self, theS):
        """Plot me to a stream at the logical datum point.
        Must be provided by child classes."""
        assert(not self._isRoot)
        myAtrtrs = {
            'name' : self._dataMap['fileName'],
            'bool' : str(self._dataMap['condComp']),
        }
        with XmlWrite.Element(theS, 'File', myAtrtrs):
            pass
        
#===============================================================================
#            self._dataMap['numToks']
#            self._dataMap['condComp']
#            self._dataMap['condCompState']
#            # A PpTokenCount.PpTokenCount() object.
#            self._dataMap['tokenCntr']
#            self._dataMap['findLogic']
#===============================================================================
        
    def _writeTokenCounters(self, theS, theCntr):
        with XmlWrite.Element(theS, 'TokenCounts'):
            with XmlWrite.Element('TokenCountAll'):
                self._writeTokenCounter(theS, theCntr, True)
            with XmlWrite.Element(theS, 'TokenCountUnconditional'):
                self._writeTokenCounter(theS, theCntr, True)

    def _writeTokenCounter(self, theS, theCntr, isAll):
        for aType in PpToken.LEX_PPTOKEN_TYPES:
            myAttrs = {
                'type' : aType,
                'count' : '%d' % theCntr.tokenCount(aType, isAll),
            }
            with XmlWrite.Element(theS, 'Tokens', myAttrs):
                pass
