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

"""Plots a SVG diagram illustrating public/platfrom/internal state 
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import os
#import sys
#from cpip.core import FileIncludeGraph
#from cpip.core import PpTokenCount
from cpip.util import XmlWrite
from cpip.plot import Coord
from cpip.plot import PlotNode
from cpip.plot import SVGWriter
#from cpip.plot import TreePlotTransform
import IncGraphSVGBase

class SVGTreeNodePpi(IncGraphSVGBase.SVGTreeNodeBase):
    COMMON_UNITS            = 'mm'
    VIEWBOX_SCALE           = 8.0
    NODE_RADIUS             = Coord.Dim(3.0,           COMMON_UNITS)
    SPACE_PARENT_CHILD      = Coord.Dim(12.0,          COMMON_UNITS)
    NODE_PADDING            = Coord.Pad(
                                  Coord.Dim(2.0, COMMON_UNITS), # prev
                                  Coord.Dim(2.0, COMMON_UNITS), # next
                                  Coord.Dim(4.0, COMMON_UNITS), # parent
                                  Coord.Dim(4.0, COMMON_UNITS), # child
                                )
    # Lines joining root level children
    ATTRS_LINE_ROOT_CHILDREN_JOIN = {
        'stroke-width'   : "8",
        'stroke'         : "lightgrey",
    }
    ATTRS_LINE_NORMAL = {
        'stroke-width'   : "2",
        'stroke'         : "black",
    }
    # Node attributes
    # First common attributes
    ATTRS_NODE_COMMON = {
        'stroke'       : "black",
        'stroke-width' : "1",
    }
    # Now individual ones, these can update the common ones
    # The boolean is whether there are significant numbers of tokens or not
    ATTRS_NODE = {
        'public' : {
            True : {
                'fill'         : "Green",
            },
            False : {
                'fill'         : "PaleGreen",
            },
        },
        'platform' : {
            True : {
                'fill'         : "Blue",
            },
            False : {
                'fill'         : "SkyBlue",
            },
        },
        'internal' : {
            True : {
                'fill'         : "Red",
            },
            False : {
                'fill'         : "MistyRose",
            },
        },
        'None' : {
            True : {
                'fill'         : "White",
            },
            False : {
                'fill'         : "White",
            },
        },
    }
    # Enumerated possibilities    
    PPI_RANGE = ('public', 'platform', 'internal', 'None')
    def __init__(self, theFig, theLineNum):
        super(SVGTreeNodePpi, self).__init__(theFig, theLineNum)
        self._bb = PlotNode.PlotNodeBboxRoundy()
        if not self.isRoot:
            # Munge the path in some kind of cross platform way...
            myP = os.path.abspath(self._fileName)
            myP = os.path.normcase(os.path.normpath(myP))
            myP = os.path.splitdrive(myP)[1]
            # Note: splitdrive() after abspath() always has leading os.sep
            # regardless of platform (?)
            # TODO: This a bit of  hack. Perhaps the PpLexer should pass a
            # boolean to the FileIncludeGraph to say whether this is a real
            # file or not.
            if self._fileName == 'Unnamed Pre-include':
                self._ppi = 'None'
            elif myP.find(os.path.join(os.sep, 'epoc32', 'include', 'platform')) == 0:
                self._ppi = 'platform'
            elif myP.find(os.path.join(os.sep, 'epoc32', 'include')) == 0:
                self._ppi = 'public'
            else:
                self._ppi = 'internal'
        else:
            self._ppi = None
            
    #==========================
    # Section: Accessor methods
    #==========================    
    @property
    def ppi(self):
        """This is 'public', 'platform' or 'internal'."""
        assert(self._ppi in self.PPI_RANGE)
        return self._ppi
    
    #======================
    # End: Accessor methods
    #======================
    
    #===================================
    # Section: Finalisation and plotting
    #===================================
    def _retNodeAttrs(self):
        """Returns a dictionary of the common attributes updated by myAttrs."""
        myA = self.ATTRS_NODE[self.ppi][self._numTokens > 0]
        return self._retUpdatedNodeAttrs(myA)
    
    def _retUpdatedNodeAttrs(self, theAttrs):
        """Returns a dictionary of the common attributes updated by myAttrs."""
        r = {}
        r.update(self.ATTRS_NODE_COMMON)
        r.update(theAttrs)
        return r
    
    def finalise(self):
        """Finalisation this sets up all the bounding boxes of me and my children."""
        for aChild in self._children:
            aChild.finalise()
        # Now accumulate my children's bounding boxes
        for aChild in self._children:
            self._bb.extendChildBbox(aChild.bb.bbSigma)
        # Set up my bounding box only if non-root node
        if not self.isRoot:
            self._bb.width = self.NODE_RADIUS.scale(2.0)
            self._bb.depth = self.NODE_RADIUS.scale(2.0)
            self._bb.bbSelfPadding = self.NODE_PADDING
            if len(self._children) > 0:
                self._bb.bbSpaceChildren = self.SPACE_PARENT_CHILD
        # Bounding boxes now set up
            
    def plotFinalise(self, theSvg, theDatumL, theTpt):
        """Finish the plot. In this case we write the text overlays.""" 
        # Plot all text elements so that they are on top
        self._plotTextToSVGStream(theSvg, theDatumL, theTpt)

    def _plotTextToSVGStream(self, theSvg, theDatumL, theTpt):
        """Plot the text overlay to the SVG stream. This is depth first and
        recursive."""
        if len(self._children) > 0:
            # Reverse the order of child plotting, this is so the pop-up box
            # masks the sibling texts
            myChildS = [r for r in self._enumerateChildren(theDatumL, theTpt)]
            myChildS.reverse()
            for i, datumChildL in myChildS:
                # Recursive call
                self._children[i]._plotTextToSVGStream(theSvg, datumChildL, theTpt)
        self._plotTextOverlay(theSvg, theDatumL, theTpt)

    def _plotSelf(self, theSvg, theDatumL, theTpt):
        """Plot me to a stream at the logical datum point"""
        assert(not self.isRoot)
        theSvg.comment(' %s ' % self.nodeName)
        # Plot self
        if self._bb.hasSetArea:
            myDatumL = self._bb.plotPointCentre(theDatumL)
            # Plot my box at:
            myDatumP = theTpt.pt(myDatumL) 
            with SVGWriter.SVGCircle(
                    theSvg,
                    myDatumP,
                    self.NODE_RADIUS,
                    self._retNodeAttrs(),
                ):
                pass

    def _plotSelfToChildren(self, theSvg, theDatumL, theTpt):
        """Plot links from me to my children to a stream at the
        (self) logical datum point."""
        assert(len(self._children) > 0)
        assert(not self.isRoot)
        #print 'TRACE: plotSelfToChildren()', theDatumL
        myDatumL = theDatumL#self._bb.plotPointSelf(theDatumL)
        #nameP = self.nodeName
        for i, datumChildL in self._enumerateChildren(theDatumL, theTpt):
            if theTpt.positiveSweepDir:
                childOrd = len(self._children)-i-1
            else:
                childOrd = i
            myStart = theTpt.pt(self.bb.pcRoll(myDatumL, childOrd))
            myEnd = theTpt.pt(self._children[i].bb.pcStop(datumChildL))
            theSvg.comment('Start: %s' % str(myStart))
            theSvg.comment('End: %s' % str(myEnd))
            with SVGWriter.SVGLine(
                        theSvg,
                        myStart,
                        myEnd,
                        self.ATTRS_LINE_NORMAL,
                    ):
                pass
    
    def _plotRootChildToChild(self, theSvg, theDatumL, theTpt):
        """Join up children of root node with vertical lines."""
        assert(len(self._children) > 0)
        assert(self.isRoot)
        theSvg.comment('_plotRootChildToChild()')
        ptNextL = None
        for i, datumChildL in self._enumerateChildren(theDatumL, theTpt):
            if i > 0:
                ptPrevL = theTpt.prevdcL(
                        self._children[i].bb.plotPointSelf(datumChildL),
                        self._children[i].bb.box,
                    )
                with SVGWriter.SVGLine(
                            theSvg,
                            theTpt.pt(ptNextL),
                            theTpt.pt(ptPrevL),
                            self.ATTRS_LINE_ROOT_CHILDREN_JOIN,
                        ):
                    pass
            ptNextL = theTpt.nextdcL(
                    self._children[i].bb.plotPointSelf(datumChildL),
                    self._children[i].bb.box,
                )
    
    def _plotTextOverlay(self, theSvg, theDatumL, theTpt):
        """Plots all the text associated with the parent and child."""
        # Filename
        if not self.isRoot:
            self._plotTextOverlayFileName(theSvg, theDatumL, theTpt)
 
    def _plotTextOverlayFileName(self, theSvg, theDatumL, theTpt):
        """Writes out the file name at the top with a pop-up with the
        absolute path."""
        # Write the file name
        if self._bb.hasSetArea:
            myDatumL = self._bb.plotPointSelf(theDatumL)
            textPointL = theTpt.tdcL(myDatumL, self._bb.box)
            # Logical increment to previous child is 'logical left' i.e. -x
            textPointL = Coord.newPt(
                    textPointL,
                    incX=self.NODE_PADDING.prev.scale(0.5),
                    incY=None
                )
            textPointP = theTpt.pt(textPointL)
            #textPointP = theTpt.tdcP(myDatumL, self._bb.box)
            self.writeOnMouseOverTextAndAlternate(
                    theSvg,
                    textPointP,
                    theId=theSvg.id,
                    theText=os.path.basename(self.nodeName),
                    theAltS=[self.nodeName,])
