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

"""Provides basic functionality to take the #include graph of a preprocessed
file and plots it as a diagram in SVG.

Writing onmouseover/onmouseout event handlers to provide additional information.
================================================================================
The idea here is to use the <defs> and <use> elements n SVG. It seems that any
number of <defs> elements can be in an SVG document.

The original text and the replacement text are paired within a <defs> element
thus:

<defs>
    <text id="original" font-family="Verdana" font-size="12" text-anchor="middle" x="250" y="250">Original text.</text>
    <text id="original.alt" font-family="Courier" font-size="12" text-anchor="middle" x="250" y="250">
        <tspan xml:space="preserve"> One</tspan>
        <tspan x="250" dy="1em" xml:space="preserve"> Two</tspan>
        <tspan x="250" dy="1em" xml:space="preserve">Three</tspan>
    </text>
</defs>

Important features using <defs>
-------------------------------
- Pairs have an ID and and ID + ".alt"
- Original and alt must have the same location and centering otherwise
    onmouseover/onmouseout events might not match up. 
- xml:space="preserve" is on each tspan element (alternatively space padding
    could be suspended in the XmlWriter).
- The first tspan element does not need an x value (it inherits one).
- Subsequent tspan elements do need an x value as x has been incremented by the
    previous tspan.
- Indentation of tspan has no effect as xml:space="preserve" is not true
    at that point.
- Space padding needs to be made to line things up.
- xlink namespace must be declared.

Switching using <use>
---------------------
The use element and event handlers will establish the initial conditions on
document load:
 
<use xlink:href="#original" onmouseover="switch_to_alt(evt)" onmouseout="switch_from_alt(evt)" />

Generating ID values
--------------------
They just need to be unique with ".alt" as the alternate suffix. A clear way
would to be pass around an ever increasing integer around the graph.
Alternately use depth/width e.g. "1.3.5.2". There is no clear advantage to the
latter.

Javascript Event Handlers
-------------------------
Java script needs to be written within a script element thus:
<script type="text/ecmascript">
//<![CDATA[
...
// ]]>
</script>

Switch handlers work are like this (they are fairly defensive):

These work for IE/Firefox:
function switch_to_alt(evt) {
    var myTextTgt = evt.target;
    myOldLink = myTextTgt.getAttribute("xlink:href");
    if (myOldLink.lastIndexOf(".alt") == -1) {
        myTextTgt.setAttribute("xlink:href", myOldLink+".alt");
    }
}

function switch_from_alt(evt) {
    var myTextTgt = evt.target;
    myOldLink = myTextTgt.getAttribute("xlink:href");
    if (myOldLink.lastIndexOf(".alt") != -1) {
        myOldLink = myOldLink.substring(0, myOldLink.lastIndexOf(".alt"));
    }
    myTextTgt.setAttribute("xlink:href", myOldLink);
}

function swap_id(evt, theId) {
    var textTgt = evt.target;
    textTgt.setAttribute("xlink:href", theId);
}

Opera
=====
This works for Opera: when called with:
switch_to_alt(this)
switch_from_alt(this)
swap_id(this)

[swap_id() works with Firefox, none of this works with IE.]

  <script type="text/ecmascript">
//<![CDATA[
var altSuffix = ".alt";

function switch_to_alt(elem) {
    myHref = elem.getAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href');
    if (myHref.lastIndexOf(altSuffix) == -1) {
        elem.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', myHref + altSuffix);
    }
}

function switch_from_alt(elem) {
    myHref = elem.getAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href');
    if (myHref.lastIndexOf(altSuffix) != -1) {
        myHref = myHref.substring(0, myHref.lastIndexOf(altSuffix));
        elem.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', myHref);
    }
}

function swap_id(elem, theId) {
    elem.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', theId);
}

// ]]>
</script>

"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

#import os
import sys
from cpip.core import FileIncludeGraph
#from cpip.core import PpTokenCount
from cpip.util import XmlWrite
from cpip.plot import Coord
#from cpip.plot import PlotNode
from cpip.plot import SVGWriter
from cpip.plot import TreePlotTransform

CANVAS_PADDING = Coord.Pad(
          Coord.Dim(4.0, 'mm'), # prev i.e. left
          Coord.Dim(4.0, 'mm'), # next i.e. right
          Coord.Dim(4.0, 'mm'), # parent i.e. top
          Coord.Dim(4.0, 'mm'), # child i.e. bottom
    )

def processIncGraphToSvg(theLex, theFilePath, theClass, tptPos, tptSweep):
    """Convert a Include graph from a PpLexer to SVG in theFilePath."""
    myVis = FileIncludeGraph.FigVisitorTree(theClass)
    theLex.fileIncludeGraphRoot.acceptVisitor(myVis)
    # Tree is now a graph of: theClass
    myIgs = myVis.tree()
    # Pad the canvass
    myWidth = CANVAS_PADDING.prev \
                + myIgs.plotCanvas.width \
                + CANVAS_PADDING.next
    myDepth = CANVAS_PADDING.parent \
                + myIgs.plotCanvas.depth \
                + CANVAS_PADDING.child
    # Round up
    myWidth = Coord.Dim(int(myWidth.value+0.5), myWidth.units)
    myDepth = Coord.Dim(int(myDepth.value+0.5), myDepth.units)
    myCanvas = Coord.Box(myWidth, myDepth)
    #Create a plot configuration
    myTpt = TreePlotTransform.TreePlotTransform(myCanvas, tptPos, tptSweep)
    # Write to file
    myIgs.plotToFilePath(theFilePath, myTpt)

class SVGTreeNodeBase(FileIncludeGraph.FigVisitorTreeNodeBase):
    COMMON_UNITS            = 'mm'
    # User units for viewBox and ploygon
    UNNAMED_UNITS           = 'px'
    VIEWBOX_SCALE           = 8.0
#===============================================================================
#    CANVAS_PADDING          = Coord.Pad(
#              Coord.Dim(4.0, COMMON_UNITS), # prev i.e. left
#              Coord.Dim(4.0, COMMON_UNITS), # next i.e. right
#              Coord.Dim(4.0, COMMON_UNITS), # parent i.e. top
#              Coord.Dim(4.0, COMMON_UNITS), # child i.e. bottom
#        )
#===============================================================================
    # Attributes for alternate text
    ALT_RECT_FILL = 'khaki'#'yellow'
    ALT_ID_SUFFIX = '.alt'
    ALT_FONT_FAMILY = 'monospace'
    ALT_FONT_PROPERTIES = {
        'Courier' : {
                        'size'          : 10,
                        'lenFactor'     : 0.8,
                        'heightFactor'  : 1.5,
            },
        'monospace' : {
                        'size'          : 10,
                        'lenFactor'     : 0.7,
                        'heightFactor'  : 1.2,
            },
        }
    NAMESPACE_XLINK = 'http://www.w3.org/1999/xlink'
    BROWSER = 'Opera'
    def __init__(self, theFig, theLineNum):
        super(SVGTreeNodeBase, self).__init__(theLineNum)
        self._isRoot = theFig is None
        if theFig is None:
            # Root node, children only
            self._fileName = None
            # This does not include children
            self._numTokens = -1
            self._condCompState = None
        else:
            self._fileName = theFig.fileName
            # This is significant tokens only and does not include children
            self._numTokens = theFig.numTokensSig
            self._condCompState = theFig.condCompState
        # The bounding box, to be (re)set by derived classes
        self._bb = None

    def dumpToStream(self, theS=sys.stdout, p=''):
        """Debug/trace."""
        theS.write('%sFile: %s\n' % (p, self.nodeName))
        for aLine in str(self.bb).splitlines():
            theS.write('%s%s\n' % (p, aLine))
        for aChild in self._children:
            aChild.dumpToStream(theS, p+'  ')       

    #============================================
    # Section: Accessor methods used by ancestors
    #============================================
    @property
    def isRoot(self):
        return self._isRoot
    
    @property
    def numTokens(self):
        """The number of significant tokens for me only (not including children)."""
        return self._numTokens
        
    @property
    def nodeName(self):
        """This is the file name or 'Root'."""
        if self.isRoot:
            return 'Root'
        return self._fileName
    
    @property
    def condCompState(self):
        """True/False if conditionally compiled node."""
        assert(not self.isRoot)
        return self._condCompState
    
    @property
    def bb(self):
        """Returns a PlotNode.PlotNodeBboxBoxy() object for this node."""
        assert(self._bb is not None)
        return self._bb
    
    @property
    def plotCanvas(self):
        """The logical size of the plot canvas as a Coord.Box()."""
        return self.bb.bbSigma
    #========================================
    # End: Accessor methods used by ancestors
    #========================================
    
    #===================================
    # Section: Finalisation and plotting
    #===================================
    def finalise(self):
        """This will be called on finalisation.
        For depth first finalisation the child class should call finalise
        on each child first."""
        raise NotImplementedError('finalise() not implemented')
    
#===============================================================================
#    def finalise(self):
#        """Finalisation this sets up all the bounding boxes of me and my children."""
#        for aChild in self._children:
#            aChild.finalise()
#        # Now accumulate my children's bounding boxes and token counts
#        self._tokenCounterChildren = PpTokenCount.PpTokenCount()
#        self._tokenCounterChildren += self.tokenCounter
#        self._numChildSigTokens = 0
#        for aChild in self._children:
#            self._bb.extendChildBbox(aChild.bb.bbSigma)
#            self._tokenCount += aChild.tokenCount
#            self._tokenCounterChildren += aChild.tokenCounter
#            self._numChildSigTokens += aChild.tokenCounter.tokenCountNonWs(isAll=False)
#        # Set up my bounding box only if non-root node
#        if not self.isRoot:
#            #self._bb.width = max(self.WIDTH_MINIMUM, self.WIDTH_PER_TOKEN.scale(self._tokenCount))
#            self._bb.width = self.WIDTH_MINIMUM + self.WIDTH_PER_TOKEN.scale(self._tokenCount)
#            self._bb.depth = self.FILE_DEPTH
#            self._bb.bbSelfPadding = self.FILE_PADDING
#            if len(self._children) > 0:
#                self._bb.bbSpaceChildren = self.SPACE_PARENT_CHILD
#        # Bounding boxes set up
#===============================================================================
            
    def plotToFilePath(self, theFileName, theTpt):
        """Root level call to plot to a SVG file, theTpt is an
        TreePlotTransform object and is used to transform the internal logical
        coordinates to physical plot positions."""
        self.plotToFileObj(open(theFileName, 'w'), theTpt)
        
    def plotToFileObj(self, theFileObj, theTpt):
        """Root level call to plot to a file object. The SVG stream is
        created here."""
#===============================================================================
#        # Add a margin and round up
#        myWidth = self.CANVAS_PADDING.prev \
#                    + theTpt.canvasP().width \
#                    + self.CANVAS_PADDING.next
#        myWidth = Coord.Dim(int(myWidth.value+0.5), myWidth.units)
#        myDepth = self.CANVAS_PADDING.parent \
#                    + theTpt.canvasP().depth \
#                    + self.CANVAS_PADDING.child
#        myDepth = Coord.Dim(int(myDepth.value+0.5), myDepth.units)
#        myCanvasP = Coord.Box(myWidth, myDepth)
#===============================================================================
        # Make viewBox user coordinates * self.VIEWBOX_SCALE
        myRootAttrs = {
            'viewBox' : '0 0 %d %d' \
                % (
                    theTpt.canvasP().width.value * self.VIEWBOX_SCALE,
                    theTpt.canvasP().depth.value * self.VIEWBOX_SCALE,
                    ),
            'xmlns:xlink'   : self.NAMESPACE_XLINK,
        } 
        with SVGWriter.SVGWriter(theFileObj, theTpt.canvasP(), myRootAttrs) as myS:
            myDatum = Coord.Pt(
                         CANVAS_PADDING.prev,
                         CANVAS_PADDING.parent,
                    )
            #print 'TRACE: myDatum', myDatum
            self._writeECMAScriptOnMouseOver(myS, self.BROWSER)
            myS.comment(' Root position: %s, Sweep direction: %s ' \
                         % (theTpt.rootPos, theTpt.sweepDir))
            #<rect x="1" y="1" width="1198" height="398" fill="none" stroke="blue" stroke-width="2"/>
            with SVGWriter.SVGRect(
                    myS,
                    Coord.zeroBaseUnitsPt(),#myDatum,
                    theTpt.canvasP(),
                    {
                        'fill'         : 'none',
                        'stroke'       : 'grey',
                        'stroke-width' : '2',
                    },
                ):
                pass
            # Start the plot
            self.plotInitialise(myS, myDatum, theTpt)
            # Now plot all contents
            self.plotToSVGStream(myS, myDatum, theTpt)
            # Finish the plot
            self.plotFinalise(myS, myDatum, theTpt)

    def plotInitialise(self, theSvg, theDatumL, theTpt):
        """Called once immediately before the recursive plotToSVGStream().
        Can be overridden in child classes for specific use.""" 
        pass

    def plotFinalise(self, theSvg, theDatumL, theTpt):
        """Called once immediately before the plot is closed.
        Can be overridden in child classes for specific use.""" 
        pass

    def plotToSVGStream(self, theSvg, theDatumL, theTpt):
        """Plot me to a stream and my children at the logical datum point,
        this is a recursive call."""
        if len(self._children) > 0:
            if self.isRoot:
                self._plotRootChildToChild(theSvg, theDatumL, theTpt)
            else:
                self._plotSelfToChildren(theSvg, theDatumL, theTpt)
            # Recursive call
            for i, datumChildL in self._enumerateChildren(theDatumL, theTpt):
                self._children[i].plotToSVGStream(theSvg, datumChildL, theTpt)
        # Plot me last so I sit over any me-to-child lines
        if not self.isRoot:
            self._plotSelf(theSvg, theDatumL, theTpt)

    def _plotSelf(self, theSvg, theDatumL, theTpt):
        """Plot me to a stream at the logical datum point.
        Must be provided by child classes."""
        raise NotImplementedError('_plotSelf() not implemented')

    def _plotRootChildToChild(self, theSvg, theDatumL, theTpt):
        """In the case of me being root this plots child to child."""
        assert(self.isRoot)
        raise NotImplementedError('_plotRootChildToChild() not implemented')
        
    def _plotSelfToChildren(self, theSvg, theDatumL, theTpt):
        """In the case of me being not root this plots me to my children."""
        assert(self.isRoot)
        raise NotImplementedError('_plotSelfToChildren() not implemented')
    
    def _enumerateChildren(self, theDatumL, theTpt):
        """Generates a tuple of (index, logical_datum_point) for my children."""
        assert(len(self._children) > 0)
        datumChildL = theTpt.startChildrenLogicalPos(
                            self._bb.childBboxDatum(theDatumL),
                            self._bb.bbChildren,
                        )
        for i, aChild in enumerate(self._children):
            datumChildL = theTpt.preIncChildLogicalPos(datumChildL, aChild.bb.bbSigma)
            yield i, datumChildL
            datumChildL = theTpt.postIncChildLogicalPos(datumChildL, aChild.bb.bbSigma)

    #=============================================
    # Section: Writing SVG code to do pop-up text.
    #=============================================
    def _writeECMAScriptOnMouseOver(self, theSvg, theBrowser):
        """Writes the ECMA script for pop-up text switching."""
        myScriptS = []
        if theBrowser == 'Opera':
            myScriptS.append("""
var altSuffix = ".alt";
""")
            myScriptS.append("""
function switch_to_alt(elem) {
    myHref = elem.getAttributeNS('%s', 'xlink:href');
    if (myHref.lastIndexOf(altSuffix) == -1) {
        elem.setAttributeNS('%s', 'xlink:href', myHref + altSuffix);
    }
}
""" % (self.NAMESPACE_XLINK, self.NAMESPACE_XLINK))
            myScriptS.append("""
function switch_from_alt(elem) {
    myHref = elem.getAttributeNS('%s', 'xlink:href');
    if (myHref.lastIndexOf(altSuffix) != -1) {
        myHref = myHref.substring(0, myHref.lastIndexOf(altSuffix));
        elem.setAttributeNS('%s', 'xlink:href', myHref);
    }
}
""" % (self.NAMESPACE_XLINK, self.NAMESPACE_XLINK))
            myScriptS.append(""" 
function swap_id(elem, theId) {
    elem.setAttributeNS('%s', 'xlink:href', theId);
}
""" % self.NAMESPACE_XLINK)
        else:
            # This works in IE/Firefox
            myScriptS.append("""
var altSuffix = ".alt";
""")
            myScriptS.append("""
function switch_to_alt(evt) {
    var textTgt = evt.target;
    myOldLink = textTgt.getAttribute("xlink:href");
    if (myOldLink.lastIndexOf(altSuffix) == -1) {
        textTgt.setAttribute("xlink:href", myOldLink + altSuffix);
    }
}
""")
            myScriptS.append("""
function switch_from_alt(evt) {
    var textTgt = evt.target;
    myOldLink = textTgt.getAttribute("xlink:href");
    if (myOldLink.lastIndexOf(altSuffix) != -1) {
        myOldLink = myOldLink.substring(0, myOldLink.lastIndexOf(altSuffix));
    }
    textTgt.setAttribute("xlink:href", myOldLink);
}
""")
            myScriptS.append("""
function swap_id(evt, theId) {
    var textTgt = evt.target;
    textTgt.setAttribute("xlink:href", theId);
}
""")
        theSvg.writeECMAScript(''.join(myScriptS))

    def _addECMAScriptMouseOverAttrs(self, theAttrs, theBrowser):
        """Writes the ECMA script for pop-up text switching."""
        if theBrowser == 'Opera':
            theAttrs['onmouseover'] = "switch_to_alt(this)"
            theAttrs['onmouseout'] = "switch_from_alt(this)"
        else:
            theAttrs['onmouseover'] = "switch_to_alt(evt)"
            theAttrs['onmouseout'] = "switch_from_alt(evt)"

    def _addECMAScriptSwapIdAttrs(self, theAttrs, theBrowser, theIdOver, theIdOut):
        """Writes the ECMA script for pop-up text switching."""
        if theBrowser == 'Opera':
            theAttrs['onmouseover'] = "swap_id(this, \"%s\")" % theIdOver
            theAttrs['onmouseout'] = "swap_id(this, \"%s\")" % theIdOut
        else:
            theAttrs['onmouseover'] = "swap_id(evt, \"%s\")" % theIdOver
            theAttrs['onmouseout'] = "swap_id(evt, \"%s\")" % theIdOut

    def writeOnMouseOverTextAndAlternate(self, theSvg, thePoint, theId, theText, theAltS):
        """Writes the <defs> element for the pair of texts and the <use> element
        that references the first one.
        thePoint is the physical point to locate both texts."""
        altFontSize = self.ALT_FONT_PROPERTIES[self.ALT_FONT_FAMILY]['size']
        altFontLenFactor = self.ALT_FONT_PROPERTIES[self.ALT_FONT_FAMILY]['lenFactor']
        altFontHeightFactor = self.ALT_FONT_PROPERTIES[self.ALT_FONT_FAMILY]['heightFactor']
        with XmlWrite.Element(theSvg, 'defs'):
            # <text id="original" font-family="Verdana" font-size="12" text-anchor="middle" x="250" y="250">Original text.</text>
            with SVGWriter.SVGText(theSvg, thePoint, 'Verdana', 12,
                        {
                            'id'                : theId,
                            #'font-weight'       : "bold",
                            'text-decoration'   : "underline",
                            'text-anchor'       : "middle",
                            'dominant-baseline' : "middle",
                            #'dominant-baseline' : "text-after-edge",
                        }
                    ):
                theSvg.characters(theText)
            # Write a grouping element and give it the alternate ID
            with SVGWriter.SVGGroup(theSvg, {'id' : theId+self.ALT_ID_SUFFIX}):
                # Compute masking box for alternate
                maxChars = max([len(s) for s in theAltS])
                # Take 80% of character length
                boxWidth = Coord.Dim(altFontSize * maxChars * altFontLenFactor, 'pt')
                if len(theAltS) < 2:
                    boxHeight = Coord.Dim(altFontSize * 2, 'pt')
                else:
                    boxHeight = Coord.Dim(altFontSize * len(theAltS) * altFontHeightFactor, 'pt')
                with SVGWriter.SVGRect(
                        theSvg,
                        # Edge the plot point up and left by a bit
                        Coord.newPt(
                            thePoint,
                            incX=Coord.Dim(-1 * altFontSize * (1 + len(theText) * altFontLenFactor / 2.0), 'pt'),
                            incY=Coord.Dim(-1*altFontHeightFactor * altFontSize, 'pt'),
                        ),
                        Coord.Box(boxWidth, boxHeight),
                        { 'fill' : self.ALT_RECT_FILL },
                    ):
                    pass
                # As the main text is centered and the alt text is left
                # justified we need to move the text plot point left by a bit.
                myAltTextPt = Coord.newPt(
                    thePoint,
                    incX=Coord.Dim(-1 * altFontSize * len(theText) * altFontLenFactor / 2.0, 'pt'),
                    incY=None,
                )
                with SVGWriter.SVGText(theSvg, myAltTextPt, 'Courier', altFontSize,
                            {
                                'font-weight'       : "normal",
                            }
                        ):
                    self._writeStringListToTspan(theSvg, myAltTextPt, theAltS)
        # Write the <use> element
        # <use xlink:href="#pre_include" onmouseover="switch_to_alt(evt)" onmouseout="switch_from_alt(evt)" />
        useAttrs = {
            'xlink:href'    : '#%s' % theId,
        }
        self._addECMAScriptMouseOverAttrs(useAttrs, self.BROWSER)
        with  XmlWrite.Element(theSvg, 'use', useAttrs):
            pass
    
    def _writeStringListToTspan(self, theSvg, thePointX, theList):
        """Converts a multi-line string to tspan elements in monospaced format.
        theSvg is the SVG stream.
        theAttrs is the attributes of the enclosing <text> element.
        theStr is the string to write.
        
        This writes the tspan elements within an existing text element, thus:
        <text id="original.alt" font-family="Courier" font-size="12" text-anchor="middle" x="250" y="250">
            <tspan xml:space="preserve"> One</tspan>
            <tspan x="250" dy="1em" xml:space="preserve"> Two</tspan>
            <tspan x="250" dy="1em" xml:space="preserve">Three</tspan>
        </text>
        """
        #theSvg.xmlSpacePreserve()
        for i, aLine in enumerate(theList):
            elemAttrs = {'xml:space' : "preserve"}
            if i > 0:
                elemAttrs['x'] = SVGWriter.dimToTxt(thePointX.x) 
                elemAttrs['dy'] = "1.5em"
            with  XmlWrite.Element(theSvg, 'tspan', elemAttrs):
                theSvg.characters(aLine)
    #=============================================
    # End: Writing SVG code to do pop-up text.
    #=============================================
