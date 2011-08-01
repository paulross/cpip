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
#import sys
#from cpip.core import FileIncludeGraph
from cpip.core import PpTokenCount
from cpip.util import XmlWrite
from cpip.plot import Coord
from cpip.plot import PlotNode
from cpip.plot import SVGWriter
#from cpip.plot import TreePlotTransform
import IncGraphSVGBase

class SVGTreeNodeMain(IncGraphSVGBase.SVGTreeNodeBase):
    COMMON_UNITS            = 'mm'
    WIDTH_PER_TOKEN         = Coord.Dim(1.0/1000.0,     COMMON_UNITS)
    WIDTH_MINIMUM           = Coord.Dim(5,              COMMON_UNITS)
    FILE_DEPTH              = Coord.Dim(32.0,           COMMON_UNITS)
    SPACE_PARENT_CHILD      = Coord.Dim(16.0,           COMMON_UNITS)
    FILE_PADDING            = Coord.Pad(
                                  Coord.Dim(4.0, COMMON_UNITS), # prev
                                  Coord.Dim(2.0, COMMON_UNITS), # next
                                  Coord.Dim(16.0, COMMON_UNITS), # parent
                                  Coord.Dim(16.0, COMMON_UNITS), # child
                                )
    # Lines joining root level children
    ATTRS_LINE_ROOT_CHILDREN_JOIN = {
        'stroke-width'   : "8",
        'stroke'         : "lightgrey",
    }
    # Node attributes (e.e. for rectangles)
    # Normal nodes
    ATTRS_NODE_NORMAL = {
        'fill'         : "mistyrose",
        'stroke'       : "black",
        'stroke-width' : "1",
    }
    # Nodes that are empty
    ATTRS_NODE_MT = {
        'fill'         : "aqua",
        'stroke'       : "black",
        'stroke-width' : "1",
    }
    # Conditionally compiled stuff
    ATTRS_NODE_CONDITIONAL = {
        'fill'                  : "salmon",#"orangered",
        'stroke'                : "black",
        #'stroke-dasharray'      : "4,4",
        'stroke-width'          : "1",
    }
    ATTRS_LINE_NORMAL_TO = {
        'stroke-width'   : "2",
        'stroke'         : "black",
    }
    ATTRS_LINE_NORMAL_FROM = {
        'stroke-width'   : "0.5",
        'stroke'         : "black",
    }
    ATTRS_LINE_MT_TO = {
        'stroke-width'      : "2",
        'stroke'            : "aqua",
        'stroke-dasharray'  : "8,8",
    }
    ATTRS_LINE_MT_FROM = {
        'stroke-width'      : "0.5",
        'stroke'            : "aqua",
        'stroke-dasharray'  : "8,8",
    }
    ATTRS_LINE_CONDITIONAL_TO = {
        'stroke-width'      : "0.5",
        'stroke'            : "black",
        'stroke-dasharray'  : "8,2,2,2",
    }
    ATTRS_LINE_CONDITIONAL_FROM = {
        'stroke-width'      : "0.25",
        'stroke'            : "black",
        'stroke-dasharray'  : "8,2,2,2",
    }
    # Chevron attributes
    CHEVRON_COLOUR_FILL         = "palegreen"#"cornflowerblue"
    CHEVRON_COLOUR_STROKE       = "black"
    CHEVRON_STROKE_WIDTH        = ".5"
    # Histogram plotting
    HIST_DEPTH                  = Coord.Dim(4.0, COMMON_UNITS)
    # This controls plot order as well as colour
    # Note: Unusually they are in sweep='-' i.e logical left-to-right order
    HIST_PP_TOKEN_TYPES_COLOURS = (
        ('header-name',                 'orange',), # Not used as 'derived' token
        ('identifier',                  'blue',), # Top 3!
        ('string-literal',              'cyan',),
        ('pp-number',                   'green',), # Next most popular after top 3
        ('character-literal',           'magenta',),
        ('preprocessing-op-or-punc',    'red',), # Top 3!
        ('non-whitespace',              'black',),
        ('concat',                      'yellow',),
        ('whitespace',                  'white',), # Top 3!
    )
    HIST_RECT_COLOUR_STROKE = "black"
    HIST_RECT_STROKE_WIDTH = ".5"
    HIST_LEGEND_ID = "HistogramLegend"
    # The placeholder text for JavaScript rollover
    POPUP_TEXT = ' ? '
#===============================================================================
#    # Attributes for alternate text
#    ALT_RECT_FILL = 'khaki'#'yellow'
#    ALT_ID_SUFFIX = '.alt'
#    ALT_FONT_FAMILY = 'monospace'
#    ALT_FONT_PROPERTIES = {
#        'Courier' : {
#                        'size'          : 10,
#                        'lenFactor'     : 0.8,
#                        'heightFactor'  : 1.5,
#            },
#        'monospace' : {
#                        'size'          : 10,
#                        'lenFactor'     : 0.7,
#                        'heightFactor'  : 1.2,
#            },
#        }
#===============================================================================
    def __init__(self, theFig, theLineNum):
        super(SVGTreeNodeMain, self).__init__(theFig, theLineNum)
        # PpTokenCount object for my children only, set on finalise
        self._tokenCounterChildren = PpTokenCount.PpTokenCount()
        ## PpTokenCount object for me and my my children , set on finalise
        #self._tokenCounterTotal = PpTokenCount.PpTokenCount()
        # Total number of significant tokens in all children
        self._numChildSigTokens = 0
        # Mandatory override of the bounding box object
        self._bb = PlotNode.PlotNodeBboxBoxy()
        if theFig is None:
            # Root node, children only
            self._dataMap = None
        else:
            self._dataMap = {}
            # Take a copy of the include graph data
            self._dataMap['numToks']        = theFig.numTokens
            self._dataMap['condComp']       = theFig.condComp
            # A PpTokenCount.PpTokenCount() object for this node only.
            self._dataMap['tokenCntr']      = theFig.tokenCounter
            self._dataMap['findLogic']      = theFig.findLogic
            
    #============================================
    # Section: Accessor methods used by ancestors
    #============================================    
    @property
    def tokenCounter(self):
        """This is the PpTokenCount.PpTokenCount() for me only."""
        if self.isRoot:
            return PpTokenCount.PpTokenCount()
        return self._dataMap['tokenCntr']
    
    @property
    def tokenCounterChildren(self):
        """This is the computed PpTokenCount.PpTokenCount() for all my descendents."""
        ##"""This is the PpTokenCount.PpTokenCount() for my children."""
        return self._tokenCounterChildren
    
    @property
    def tokenCounterTotal(self):
        """This is the computed PpTokenCount.PpTokenCount() me plus my descendents."""
        retVal = PpTokenCount.PpTokenCount()
        retVal += self.tokenCounter
        retVal += self.tokenCounterChildren
        return retVal
        #return self._tokenCounterTotal
#===============================================================================
#    @property
#    def tokenCounterSigma(self):
#        """This is the computed PpTokenCount.PpTokenCount() for me plus my children."""
#        retVal = PpTokenCount.PpTokenCount()
#        retVal += self.tokenCounter
#        retVal += self.tokenCounterChildren
#        return retVal
#===============================================================================
    
    @property
    def condComp(self):
        """A string of conditional tests."""
        assert(not self.isRoot)
        return self._dataMap['condComp']
    
    @property
    def findLogic(self):
        """The find logic as a string."""
        assert(not self.isRoot)
        return self._dataMap['findLogic']
    #========================================
    # End: Accessor methods used by ancestors
    #========================================
    
    #===================================
    # Section: Finalisation and plotting
    #===================================
    def finalise(self):
        """Finalisation this sets up all the bounding boxes of me and my children."""
        for aChild in self._children:
            aChild.finalise()
        # Now accumulate my children's bounding boxes and token counts
        self._tokenCounterChildren = PpTokenCount.PpTokenCount()
        #self._tokenCounterTotal = PpTokenCount.PpTokenCount()
        #if not self.isRoot:
        #    self._tokenCounterTotal += self.tokenCounter 
        self._numChildSigTokens = 0
        for aChild in self._children:
            self._bb.extendChildBbox(aChild.bb.bbSigma)
            self._tokenCounterChildren += aChild.tokenCounterTotal
            #self._tokenCounterTotal += aChild.tokenCounter
            self._numChildSigTokens += aChild.tokenCounterTotal.tokenCountNonWs(isAll=False)
        # Set up my bounding box only if non-root node
        if not self.isRoot:
            #self._bb.width = max(self.WIDTH_MINIMUM, self.WIDTH_PER_TOKEN.scale(self._tokenCount))
            self._bb.width = self.WIDTH_MINIMUM \
                + self.WIDTH_PER_TOKEN.scale(self.tokenCounterTotal.tokenCountNonWs(isAll=False))
            self._bb.depth = self.FILE_DEPTH
            self._bb.bbSelfPadding = self.FILE_PADDING
            if len(self._children) > 0:
                self._bb.bbSpaceChildren = self.SPACE_PARENT_CHILD
        # Bounding boxes now set up
            
    def plotInitialise(self, theSvg, theDatumL, theTpt):
        """Plot the histogram legend once only.""" 
        self._plotHistogramLegend(theSvg, theTpt)

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
        if self.condCompState:
            if self.numTokens > 0:
                myAttrs = self.ATTRS_NODE_NORMAL
            else:
                myAttrs = self.ATTRS_NODE_MT
        else:
            myAttrs = self.ATTRS_NODE_CONDITIONAL
        if self._bb.hasSetArea:
            myDatumL = self._bb.plotPointSelf(theDatumL)
            #myBox = Coord.Box(self._bb.width, self._bb.depth)
            myBox = self._bb.box
            #print 'myDatumL', myDatumL
            #print 'myBox', myBox  
            # Plot my box at:
            myBoxDatumP = theTpt.boxDatumP(myDatumL, myBox) 
            with SVGWriter.SVGRect(
                    theSvg,
                    myBoxDatumP,
                    theTpt.boxP(myBox),
                    myAttrs,
                ):
                pass
        self._plotSelfInternals(theSvg, theDatumL, theTpt)

    def _plotSelfToChildren(self, theSvg, theDatumL, theTpt):
        """Plot links from me to my children to a stream at the
        (self) logical datum point."""
        assert(len(self._children) > 0)
        assert(not self.isRoot)
        #print 'TRACE: plotSelfToChildren()', theDatumL
        myDatumL = self._bb.plotPointSelf(theDatumL)
        #nameP = self.nodeName
        for i, datumChildL in self._enumerateChildren(theDatumL, theTpt):
            if self._children[i].condCompState:
                if self._children[i].numTokens > 0:
                    myAttrsTo = self.ATTRS_LINE_NORMAL_TO
                    myAttrsFrom = self.ATTRS_LINE_NORMAL_FROM
                else:
                    myAttrsTo = self.ATTRS_LINE_MT_TO
                    myAttrsFrom = self.ATTRS_LINE_MT_FROM
            else:
                myAttrsTo = self.ATTRS_LINE_CONDITIONAL_TO
                myAttrsFrom = self.ATTRS_LINE_CONDITIONAL_FROM
            #nameC = self._children[i]._dataMap['name']
            if theTpt.positiveSweepDir:
                childOrd = len(self._children)-i-1
            else:
                childOrd = i
            # Parent to child
            linePtsFirst = [theTpt.pt(l) for l in (
                                       self._bb.pcRoll(myDatumL, childOrd),
                                       self._bb.pcTo(myDatumL, childOrd),
                                       self._children[i].bb.pcLand(datumChildL),
                                       self._children[i].bb.pcStop(datumChildL),
                                       )]
            # Now child to parent
            linePtsSecond = [theTpt.pt(l) for l in (
                                       self._children[i].bb.cpRoll(datumChildL),
                                       self._children[i].bb.cpTo(datumChildL),
                                       self._bb.cpLand(myDatumL, childOrd),
                                       self._bb.cpStop(myDatumL, childOrd),
                                       )]
            if theTpt.positiveSweepDir:
                linePtsSecond, linePtsFirst = linePtsFirst, linePtsSecond
            j = 1
            #theSvg.comment(' %s to %s ' % (nameP, nameC))
            while j < len(linePtsFirst):
                with SVGWriter.SVGLine(
                            theSvg,
                            linePtsFirst[j-1],
                            linePtsFirst[j],
                            myAttrsTo,
                        ):
                    pass
                j += 1
            j = 1
            #theSvg.comment(' %s to %s ' % (nameC, nameP))
            while j < len(linePtsSecond):
                with SVGWriter.SVGLine(
                            theSvg,
                            linePtsSecond[j-1],
                            linePtsSecond[j],
                            myAttrsFrom,
                        ):
                    pass
                j += 1
    
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
    
    def _plotSelfInternals(self, theSvg, theDl, theTpt):
        """Plot structures inside the box."""
        # Histograms of token types
        if self.__mustPlotSelfHistogram():
            # First the histogram of just me
            myHistDl = self._bb.plotPointSelf(theDl)
            self._plotHistogram(theSvg, myHistDl, theTpt, self.tokenCounter)
            # Now the histogram of my children
            if self.__mustPlotChildHistogram():
                # Shuffle down a bit
                myHistDl = Coord.newPt(myHistDl, None, self.HIST_DEPTH)
                self._plotHistogram(theSvg, myHistDl, theTpt, self._tokenCounterChildren)
        # Now the Chevron
        self._plotChevron(theSvg, theDl, theTpt)

    def _plotTextOverlay(self, theSvg, theDatumL, theTpt):
        """Plots all the text associated with the parent and child."""
        # Child information first
        if len(self._children) > 0 and not self.isRoot:
            self._plotTextOverlayChildren(theSvg, theDatumL, theTpt)
        # Now me
        # Filename
        if not self.isRoot:
            self._plotTextOverlayFileName(theSvg, theDatumL, theTpt)
        # Histogram
        if self.__mustPlotSelfHistogram():
            # Write a single '?' in the middle
            myHistDl = self._bb.plotPointSelf(theDatumL)
            self._plotTextOverlayHistogram(theSvg, myHistDl, theTpt)
            if self.__mustPlotChildHistogram():
                # Shuffle down a bit
                myHistDl = Coord.newPt(myHistDl, None, self.HIST_DEPTH)
                self._plotTextOverlayHistogram(theSvg, myHistDl, theTpt)
        if not self.isRoot:
            self._plotTextOverlayTokenCountTable(theSvg, theDatumL, theTpt)

    def _plotTextOverlayChildren(self, theSvg, theDatumL, theTpt):
        """Plot text associated with my children to a stream at the
        (self) logical datum point."""
        assert(len(self._children) > 0)
        assert(not self.isRoot)
        for i, datumChildL in self._enumerateChildren(theDatumL, theTpt):
            self._plotTextOverlayChild(theSvg, i, datumChildL, theTpt)
    
    def _plotTextOverlayChild(self, theSvg, iChild, theDatumL, theTpt):
        """Plot description of inclusion of the child to a stream at the
        (self) logical datum point.
        Returns the logical datum of the first child."""
        assert(not self.isRoot)
        assert(len(self._children) > 0)
        assert(iChild >=0 and iChild < len(self._children))
        #myDatumL = theDatumL
        #myDatumL = Coord.newPt(theDatumL, incX=self.FILE_PADDING.prev, incY=None)#self.FILE_PADDING.parent.scale(-1.0))
        myDatumL = self._children[iChild].bb.plotPointSelf(theDatumL)
        # Move logical datum logically 'up' and 'right' by half
        myDatumL = Coord.newPt(
                myDatumL,
                incX=self._children[iChild].bb.width.scale(0.5),
                incY=self.FILE_PADDING.parent.scale(-0.5),
        )
        myPointP = theTpt.pt(myDatumL)
        altTextS = []
        altTextS.append('Inc: %s#%d' \
                        % (self.nodeName, self._children[iChild].lineNum))
        if len(self._children[iChild].condComp) > 0:
            altTextS.append(
                ' As: %s since: %s' \
                % (
                    str(self._children[iChild].condCompState),
                    self._children[iChild].condComp
                    )
            )
        else:
            altTextS.append(
                ' As: %s' \
                    % (str(self._children[iChild].condCompState)
                    )
            )
        altTextS.append('How: %s' % ', '.join(self._children[iChild].findLogic))
        self.writeOnMouseOverTextAndAlternate(theSvg, myPointP, theSvg.id, self.POPUP_TEXT, altTextS)
    
    def _plotTextOverlayHistogram(self, theSvg, theHistDl, theTpt):
        """Plot the text associated with a histogram."""
        myCentreL = Coord.newPt(theHistDl, self._bb.width.scale(0.5), self.HIST_DEPTH.scale(0.5))
        myId = theSvg.id
        with  XmlWrite.Element(theSvg, 'defs'):
            with SVGWriter.SVGText(theSvg, None, 'Verdana', 12,
                        {
                            'id'                : myId,
                            'text-decoration'   : "underline",
                            #'font-weight'       : "bold",
                            #'text-anchor'       : "middle",
                            #'dominant-baseline' : "middle",
                            'text-anchor'       : "left",
                            'dominant-baseline' : "middle",
                        }
                    ):
                theSvg.characters(self.POPUP_TEXT)#'?')
        # Write the <use> element
        # <use xlink:href="#pre_include" onmouseover="switch_to_alt(evt)" onmouseout="switch_from_alt(evt)" />
        myPtP = theTpt.pt(myCentreL)
        useAttrs = {
            'xlink:href'    : '#%s' % myId, 
            #'onmouseover'   : "swap_id(evt, \"#%s\")" % self.HIST_LEGEND_ID,
            #'onmouseout'    : "swap_id(evt, \"#%s\")" % myId,
            'x'             : SVGWriter.dimToTxt(myPtP.x),
            'y'             : SVGWriter.dimToTxt(myPtP.y),
        }
        self._addECMAScriptSwapIdAttrs(useAttrs,
                                       self.BROWSER,
                                       "#%s" % self.HIST_LEGEND_ID,
                                       "#%s" % myId,
                                       )
        with  XmlWrite.Element(theSvg, 'use', useAttrs):
            pass


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
                    incX=self.FILE_PADDING.prev.scale(0.5),
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

    def _plotTextOverlayTokenCountTable(self, theSvg, theDatumL, theTpt):
        """Plots the token count table as text+alternate text."""
        assert(not self.isRoot)
        myDatumL = self._bb.plotPointSelf(theDatumL)
        # Move to center
        myDatumL = Coord.newPt(
                myDatumL,
                incX=self._bb.width.scale(0.5),
                incY=self._bb.depth.scale(0.5))
        # Make the three datum points: Me, and if necessary my children and combined
        # Plot these in right to left so each pop-up masks other text
        myDatumP = theTpt.pt(myDatumL)
        if len(self._children) > 0:
            nudgeDim = Coord.Dim(20, 'pt')
            myDatumPChild = Coord.newPt(myDatumP, incX=nudgeDim, incY=None)
            myDatumPTotal = Coord.newPt(myDatumPChild, incX=nudgeDim, incY=None)
            myCounterTotal = PpTokenCount.PpTokenCount()
            myCounterTotal += self.tokenCounter
            myCounterTotal += self.tokenCounterChildren
            # Plot total
            altTextS = self._altTextsForTokenCount('Me and my children:', myCounterTotal)
            self.writeOnMouseOverTextAndAlternate(theSvg,
                                                  myDatumPTotal,
                                                  theSvg.id,
                                                  self.POPUP_TEXT,
                                                  altTextS)
            # Plot for children
            altTextS = self._altTextsForTokenCount('My children:', self.tokenCounterChildren)
            self.writeOnMouseOverTextAndAlternate(theSvg,
                                                  myDatumPChild,
                                                  theSvg.id,
                                                  self.POPUP_TEXT,
                                                  altTextS)
        # Always do me
        altTextS = self._altTextsForTokenCount('Just me:', self.tokenCounter)
        self.writeOnMouseOverTextAndAlternate(theSvg,
                                              myDatumP,
                                              theSvg.id,
                                              self.POPUP_TEXT,
                                              altTextS)
    
    def _altTextsForTokenCount(self, theTitle, theCounter):
        """Returns a list of strings that are the alternate text for token
        counts of self."""
        assert(not self.isRoot)
        FIELD_WIDTH = 7
        myTokTypeS = [t[0] for t in self.HIST_PP_TOKEN_TYPES_COLOURS]
        typeLen = max([len(t) for t in myTokTypeS])
        altTextS = [theTitle,]
        altTextS.append('%*s %*s [%*s]' \
                        % (typeLen,
                           'Type',
                           FIELD_WIDTH,
                           'All',
                           FIELD_WIDTH,
                           'Sig.',
                           )
                        )
        cntrAll = cntrSig = 0
        for t in myTokTypeS:
            altTextS.append('%*s %*d [%*d]' \
                            % (typeLen,
                               t,
                               FIELD_WIDTH,
                               theCounter.tokenCount(t, isAll=True),
                               FIELD_WIDTH,
                               theCounter.tokenCount(t, isAll=False),
                               )
                            )
            cntrAll += theCounter.tokenCount(t, isAll=True)
            cntrSig += theCounter.tokenCount(t, isAll=False)
        altTextS.append('%*s %*d [%*d]' \
                        % (typeLen,
                           'Total',
                           FIELD_WIDTH,
                           cntrAll,
                           FIELD_WIDTH,
                           cntrSig,
                           )
                        )
        return altTextS
    
    def __mustPlotSelfHistogram(self):
        return self.tokenCounter.tokenCountNonWs(isAll=False) > 0
        
    def __mustPlotChildHistogram(self):
        return self.__mustPlotSelfHistogram() \
                and len(self._children) > 0 \
                and self._numChildSigTokens > 0
        
    def _plotHistogram(self, theSvg, theHistDl, theTpt, theTokCounter):
        myTokCountTotal = theTokCounter.totalAllUnconditional
        # Avoid divide by zero errors
        assert(theTokCounter.tokenCountNonWs(isAll=False) > 0)
        assert(myTokCountTotal > 0)
        #myPos = Coord.Dim(0, self.COMMON_UNITS)
        myHistDl = theHistDl#self._bb.plotPointSelf(theDl)
        for k, myFill in self.HIST_PP_TOKEN_TYPES_COLOURS:
            tCount = theTokCounter.tokenCount(k, isAll=False)
            if tCount > 0:
                myWidth = self._bb.width.scale(tCount/(1.0*myTokCountTotal))
                myBox = Coord.Box(myWidth, self.HIST_DEPTH)
                # Convert to physical and plot
                with SVGWriter.SVGRect(
                        theSvg,
                        theTpt.boxDatumP(myHistDl, myBox),
                        theTpt.boxP(myBox),
                        {
                            'fill'         : myFill,
                            'stroke'       : self.HIST_RECT_COLOUR_STROKE,
                            'stroke-width' : self.HIST_RECT_STROKE_WIDTH,
                        },
                    ):
                    pass
                # Increment the datum
                myHistDl = Coord.newPt(myHistDl, incX=myWidth, incY=None)

    def _plotHistogramLegend(self, theSvg, theTpt):
        """Plot a standardised legend. This is plotted as a group within a defs."""
        myDatumP = Coord.Pt(
            Coord.Dim(0.0, self.COMMON_UNITS),
            Coord.Dim(0.0, self.COMMON_UNITS),
        )
        with XmlWrite.Element(theSvg, 'defs'):
            with SVGWriter.SVGGroup(theSvg, {'id' : self.HIST_LEGEND_ID}):
                # Outline rectangle
                with SVGWriter.SVGRect(
                            theSvg,
                            myDatumP,
                            Coord.Box(
                                Coord.Dim(48.0, self.COMMON_UNITS),
                                Coord.Dim(40.0, self.COMMON_UNITS),
                            ),
                            { 'fill' : self.ALT_RECT_FILL },
                        ):
                    pass
                myDatumP = Coord.newPt(myDatumP,
                        incX=Coord.Dim(2.0, self.COMMON_UNITS),
                        incY=Coord.Dim(2.0, self.COMMON_UNITS),
                    )
                myTokIdxS = range(len(self.HIST_PP_TOKEN_TYPES_COLOURS))
                if theTpt.positiveSweepDir:
                    myTokIdxS.reverse()
                for iC in myTokIdxS:
                    myBox = Coord.Box(self.HIST_DEPTH, self.HIST_DEPTH)
                    # Convert to physical and plot
                    with SVGWriter.SVGRect(
                            theSvg,
                            myDatumP,
                            myBox,
                            {
                                'fill'         : self.HIST_PP_TOKEN_TYPES_COLOURS[iC][1],
                                'stroke'       : self.HIST_RECT_COLOUR_STROKE,
                                'stroke-width' : self.HIST_RECT_STROKE_WIDTH,
                            },
                        ):
                        pass
                    myTextDatumP = Coord.newPt(myDatumP,
                                           incX=self.HIST_DEPTH+Coord.Dim(2.0, self.COMMON_UNITS),
                                           incY=self.HIST_DEPTH.scale(0.5),
                        )
                    with SVGWriter.SVGText(theSvg, myTextDatumP, 'Verdana', 9,
                                {
                                    'dominant-baseline'       : "middle",
                                }
                            ):
                        theSvg.characters(self.HIST_PP_TOKEN_TYPES_COLOURS[iC][0])
                    # Increment the datum
                    myDatumP = Coord.newPt(
                        myDatumP,
                        incX=None,
                        incY=self.HIST_DEPTH)
        
    def _plotChevron(self, theSvg, theDl, theTpt):
        """Plots a wedge to represent the relative number of tokens in me and
        my children.
        D------------------.------------------|
        |                                     |
        |------------------.------------------|
        |                                     |
        A-----------B------.------D-----------|
        |            \     .     /            |
        |             \    .    /             |
        |              \   .   /              |
        |               \  .  /               |
        |                \ . /                |
        ------------------\C/------------------
        We plot in the order D moveto A moveto B lineto C lineto D lineto B
        """
        mySelfTokCount = self.tokenCounter.tokenCountNonWs(isAll=False)
        if mySelfTokCount == 0 and self._numChildSigTokens == 0:
            return
        # Find D
        myDl = self._bb.plotPointSelf(theDl)
        # Point C, all use this
        myPtC = Coord.newPt(myDl, self._bb.width.scale(0.5), self._bb.depth)
        # Increment by one or two histogram depths to point A
        if self.__mustPlotSelfHistogram():
            myDl = Coord.newPt(myDl, None, self.HIST_DEPTH)
        if self.__mustPlotChildHistogram():
            myDl = Coord.newPt(myDl, None, self.HIST_DEPTH)
        # Figure out move to B
        if self._numChildSigTokens == 0:
            # Chevron takes full width
            polyLogicalPtS = [
                    myDl,
                    myPtC,
                    Coord.newPt(myDl, self._bb.width, None),
                ]
        else:
            ratioChevron = 1.0 * mySelfTokCount / (self._numChildSigTokens + mySelfTokCount)
            myChevronOffset = self._bb.width.scale(0.5 * ratioChevron)
            #theSvg.comment(' Chevron offset: %s ' % str(myChevronOffset))
            # Offset to B
            myDl = Coord.newPt(myDl, self._bb.width.scale(0.5) - myChevronOffset, None)
            polyLogicalPtS = [
                    myDl,
                    myPtC,
                    Coord.newPt(myDl, myChevronOffset.scale(2.0), None),
                ]
            
        polyPhysicalPtS = [theTpt.pt(p) for p in polyLogicalPtS]
        #theSvg.comment(' \npolyPhysicalPtS: %s \n' % str([str(p) for p in polyPhysicalPtS]))
        j = 1
        while j < len(polyPhysicalPtS):
            with SVGWriter.SVGLine(theSvg, polyPhysicalPtS[j-1], polyPhysicalPtS[j], {
                                                               'stroke-width'   : "2",
                                                               'stroke'         : "black",
                                                               },
                                                               ):
                pass
            j += 1
