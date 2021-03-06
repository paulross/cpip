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

"""Provides basic functionality to take the #include graph of a preprocessed
file and plots it as a diagram in SVG.

Event handlers for onmouseover/onmouseout
-----------------------------------------

We would like to have more detailed information available to the user when they
mouseover an object on the SVG image. After a lot of experiment the most cross
browser way this is done by providing an event handler to switch the opacity of
an element between 0 and 1. See :py:meth:`IncGraphSVG.writeAltTextAndMouseOverRect`.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__rights__  = 'Copyright (c) 2008-2017 Paul Ross'

import sys
import inspect
import pprint

import cpip
from cpip.core import FileIncludeGraph
#from cpip.core import PpTokenCount
from cpip.util import XmlWrite
from cpip.plot import Coord
#from cpip.plot import PlotNode
from cpip.plot import SVGWriter
from cpip.plot import TreePlotTransform

#: Canvas padding.
CANVAS_PADDING = Coord.Pad(
          Coord.Dim(4.0, 'mm'), # prev i.e. left
          Coord.Dim(4.0, 'mm'), # next i.e. right
          Coord.Dim(4.0, 'mm'), # parent i.e. top
          Coord.Dim(4.0, 'mm'), # child i.e. bottom
    )

def processIncGraphToSvg(theLex, theFilePath, theClass, tptPos, tptSweep):
    """Convert a Include graph from a PpLexer to SVG in theFilePath.

    :param theLex: The lexer.
    :type theLex: :py:class:`cpip.core.PpLexer.PpLexer`

    :param theFilePath: Where to write the SVG file.
    :type theFilePath: ``str``

    :param theClass: CSS class.
    :type theClass: ``type``

    :param tptPos: Transform position.
    :type tptPos: ``str``

    :param tptSweep: Sweep direction.
    :type tptSweep: ``str``

    :returns: ``NoneType``
    """
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
    """Sub-class of :py:class:`cpip.core.FileIncludeGraph.FigVisitorTreeNodeBase` for writing out
    the include graphs as an SVG file."""
    #: Units.
    COMMON_UNITS            = 'mm'
    #: User units for viewBox and ploygon
    UNNAMED_UNITS           = 'px'
    #: Viewbox scale.
    VIEWBOX_SCALE           = 8.0
#===============================================================================
#    CANVAS_PADDING          = Coord.Pad(
#              Coord.Dim(4.0, COMMON_UNITS), # prev i.e. left
#              Coord.Dim(4.0, COMMON_UNITS), # next i.e. right
#              Coord.Dim(4.0, COMMON_UNITS), # parent i.e. top
#              Coord.Dim(4.0, COMMON_UNITS), # child i.e. bottom
#        )
#===============================================================================
    #: Attributes for alternate text.
    ALT_RECT_FILL = 'khaki'#'yellow'
    #: Alternate text ID.
    ALT_ID_SUFFIX = '.alt'
    #: Alternate text font.
    ALT_FONT_FAMILY = 'monospace'
    #: Alternate text font properties.
    ALT_FONT_PROPERTIES = {
        'Courier' : {
                        'size'          : 10,
                        'lenFactor'     : 0.5,
                        'heightFactor'  : 1.2,
            },
        'monospace' : {
                        'size'          : 10,
                        'lenFactor'     : 0.5,
                        'heightFactor'  : 1.2,
            },
        }
    #: Namespace link.
    NAMESPACE_XLINK = 'http://www.w3.org/1999/xlink'
    #: Used to rescale SVG rather than zooming in the browser as the latter is
    #: slow with Chrome and Safari (both WebKit) and pretty much everything else.
    #: Initial, presentational, scale is chose depending on the size of the diagram.
    SCALE_FACTORS = (0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0,)
    #: Used to decide initial scale
    SCALE_MAX_Y = Coord.Dim(1000, 'mm')
#    POPUP_COORD_Y_OFFSET = Coord.Dim(20, 'pt')
    def __init__(self, theFig, theLineNum):
        """Constructor.

        :param theFig: The file include graph.
        :type theFig: ``NoneType, cpip.core.FileIncludeGraph.FileIncludeGraph``

        :param theLineNum: The line number of the parent file that included me.
        :type theLineNum: ``int``

        :returns: ``NoneType``
        """
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
        self.TRACE = cpip.SVG_COMMENT_FUNCTIONS
        # Number of passes to call plotSelf()
        self._numPassesToPlotSelf = 0

    #============================================
    # Section: Trace/Debug
    #============================================
    def dumpToStream(self, theS=sys.stdout, p=''):
        """Debug/trace."""
        theS.write('%sFile: %s\n' % (p, self.nodeName))
        for aLine in str(self.bb).splitlines():
            theS.write('%s%s\n' % (p, aLine))
        for aChild in self._children:
            aChild.dumpToStream(theS, p+'  ')
    
    def commentFunctionBegin(self, theSvg, **kwargs):
        """Injects a comment into the SVG with the start of the
        executing function name.
        ``self.TRACE`` must be ``True`` to enable this.

        :param theSvg: The SVG stream.
        :type theSvg: :py:class`cpip.plot.SVGWriter.SVGWriter`

        :returns: ``NoneType``
        """
        if self.TRACE:
            theSvg.comment(' %s(): %s %s'
                           % (inspect.stack()[1][3], 'BEGIN',
                              pprint.pformat(kwargs)), newLine=True)
          
    def commentFunctionEnd(self, theSvg, **kwargs):
        """Injects a comment into the SVG with the completion of the
        executing function name.
        ``self.TRACE`` must be ``True`` to enable this.

        :param theSvg: The SVG stream.
        :type theSvg: :py:class`cpip.plot.SVGWriter.SVGWriter`

        :returns: ``NoneType``
        """
        if self.TRACE:
            theSvg.comment(' %s(): %s %s'
                           % (inspect.stack()[1][3], 'END',
                              pprint.pformat(kwargs)), newLine=True)
          
    #============================================
    # End: Trace/Debug
    #============================================

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
        """Returns a :py:class:`cpip.plot.PlotNode.PlotNodeBboxBoxy` object for this node."""
        assert(self._bb is not None)
        return self._bb
    
    @property
    def plotCanvas(self):
        """The logical size of the plot canvas as a :py:class:`cpip.plot.Coord.Box`."""
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
                
    def plotToFilePath(self, theFileName, theTpt):
        """Root level call to plot to a SVG file, theTpt is an
        :py:class:`cpip.plot.TreePlotTransform.TreePlotTransform` object
        and is used to transform the internal logical
        coordinates to physical plot positions.

        :param theFileName: File path for output.
        :type theFileName: ``str``

        :param theTpt: The transformer used to transform the internal logical
            coordinates to physical plot positions.
        :type theTpt: :py:class:`cpip.plot.TreePlotTransform.TreePlotTransform`

        :returns: ``NoneType``
        """
        self.plotToFileObj(open(theFileName, 'w'), theTpt)
        
    def plotToFileObj(self, theFileObj, theTpt):
        """Root level call to plot to a file object. The SVG stream is
        created here.

        :param theFileObj: The output file object.
        :type theFileObj: ``_io.TextIOWrapper``

        :param theTpt: The transformer used to transform the internal logical
            coordinates to physical plot positions.
        :type theTpt: :py:class:`cpip.plot.TreePlotTransform.TreePlotTransform`

        :returns: ``NoneType``
        """
        if self._numPassesToPlotSelf < 1:
            raise ValueError('No self._numPassesToPlotSelf set!')
        # Make viewBox user coordinates * self.VIEWBOX_SCALE
        myRootAttrs = {
#             'viewBox' : '0 0 %d %d' \
#                 % (
#                     theTpt.canvasP().width.value * self.VIEWBOX_SCALE,
#                     theTpt.canvasP().depth.value * self.VIEWBOX_SCALE,
#                     ),
            'xmlns:xlink'   : self.NAMESPACE_XLINK,
        }
        # Bit of a hacky way to add enough margin for the pop-ups or rather
        # drop downs. This adds space for the bottom most boxes.
        canvasY = theTpt.canvasP().depth + Coord.Dim(60, 'mm') + Coord.Dim(8, 'mm')
        myCanvas = Coord.Box(
                    theTpt.canvasP().width + Coord.Dim(60, 'mm'),
                    canvasY,
        )
        # Shrink canvas if it is a large plot
        yOffsetForScalingText =  Coord.Dim(10, 'mm')
        scaleIdx = self.SCALE_FACTORS.index(1)
        assert scaleIdx >= 0
        while scaleIdx > 0 and canvasY > self.SCALE_MAX_Y:
            canvasY = canvasY.scale(0.5)
            scaleIdx -= 1
        self._scale = self.SCALE_FACTORS[scaleIdx]
        with SVGWriter.SVGWriter(theFileObj, myCanvas, myRootAttrs, mustIndent=cpip.INDENT_ML) as myS:
            # yOffsetForScalingText is applied wrong, should respect theTpt
            myDatum = Coord.Pt(
                         CANVAS_PADDING.prev - yOffsetForScalingText,
                         CANVAS_PADDING.parent,
                    )
            self.writePreamble(myS)
            myS.comment(' Root position: %s, Sweep direction: %s canvas=%s datum=%s' \
                         % (theTpt.rootPos, theTpt.sweepDir, theTpt.canvasP(), myDatum),
                         newLine=True)
            # Shift the drawing down a bit to make way for the scale buttons.
            with SVGWriter.SVGGroup(myS, {'transform' : "translate(0, 24)"}):
                with SVGWriter.SVGGroup(myS,
                        {
                            'id' : 'graphic',
                            'transform' : "scale(%s)" % self.SCALE_FACTORS[scaleIdx]
                        }):
                    # Apply a group element for scaling the plot
                    # More hackery: yOffsetForScalingText is applied wrong, should respect theTpt
                    with SVGWriter.SVGRect(
                            myS,
                            Coord.newPt(
                                        Coord.zeroBaseUnitsPt(),
                                        incX=None,
                                        incY=yOffsetForScalingText),
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
                    for p in range(self._numPassesToPlotSelf):
                        self.plotToSVGStream(myS, myDatum, theTpt, p, [])
                    # Finish the plot
                    self.plotFinalise(myS, myDatum, theTpt)

    def writePreamble(self, theS):
        """Write any preamble such as CSS or JavaScript.
        To be implemented by child classes."""
        raise NotImplementedError

    def plotInitialise(self, theSvg, theDatumL, theTpt):
        """Called once immediately before the recursive plotToSVGStream().
        Can be overridden in child classes for specific use.""" 
        pass

    def plotFinalise(self, theSvg, theDatumL, theTpt):
        """Called once immediately before the plot is closed.
        Can be overridden in child classes for specific use.""" 
        pass

    def plotToSVGStream(self, theSvg, theDatumL, theTpt, passNum, idStack):
        """Plot me to a stream and my children at the logical datum point,
        this is a recursive call.

        :param theSvg: The SVG stream.
        :type theSvg: :py:class`cpip.plot.SVGWriter.SVGWriter`

        :param theDatumL: The Datum.
        :type theDatumL: :py:class:`cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([float, <class 'str'>])])`

        :param theTpt: The transformer used to transform the internal logical
            coordinates to physical plot positions.
        :type theTpt: :py:class:`cpip.plot.TreePlotTransform.TreePlotTransform`

        :param passNum: The pass number.
        :type passNum: ``int``

        :param idStack: Stack of id's.
        :type idStack: ``list([]), list([int, str]), list([str])``

        :returns: ``NoneType``
        """
        self.commentFunctionBegin(theSvg, File=self._fileName, Pass=passNum)
        if not self.isRoot:
            if self.lineNum != -1:
                idStack.append(self.lineNum)
            idStack.append(self.nodeName)
        if len(self._children) > 0:
            if passNum == 0:
                if self.isRoot:
                    self._plotRootChildToChild(theSvg, theDatumL, theTpt)
                else:
                    self._plotSelfToChildren(theSvg, theDatumL, theTpt)
            # Recursive call
            # TODO: Consider reversing this so that drop-downs appear over
            # children.
#             for i, datumChildL in self._enumerateChildren(theDatumL, theTpt):
            for i, datumChildL in reversed(list(self._enumerateChildren(theDatumL, theTpt))):
                self._children[i].plotToSVGStream(theSvg, datumChildL, theTpt, passNum, idStack)
        # Plot me last so I sit over any me-to-child lines
        if not self.isRoot:
            self._plotSelf(theSvg, theDatumL, theTpt, passNum, idStack)
        else:
            self.plotRoot(theSvg, theDatumL, theTpt, passNum)
        if not self.isRoot:
            if self.lineNum != -1:
                idStack.pop()
            idStack.pop()
        self.commentFunctionEnd(theSvg, File=self._fileName, Pass=passNum)
        
    def plotRoot(self, theSvg, theDatumL, theTpt, passNum):
        """Call to plot any root node, for example our child class uses this
        to plot the histogram legend before starting on the text."""
        pass

    def _plotSelf(self, theSvg, theDatumL, theTpt, idStack):
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
        """Generates a tuple of (index, logical_datum_point) for my children.

        :param theDatumL: The coordinate.
        :type theDatumL: :py:class:`cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([float, <class 'str'>])])`

        :param theTpt: The transformer.
        :type theTpt: :py:class:`cpip.plot.TreePlotTransform.TreePlotTransform`

        :returns: ``NoneType,tuple([int, cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([float, <class 'str'>])])])`` -- The children
        """
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
    def _writeECMAScript(self, theSvg):
        """Writes the ECMA script for pop-up text switching.

        :param theSvg: The SVG stream.
        :type theSvg: :py:class`cpip.plot.SVGWriter.SVGWriter`

        :returns: ``NoneType``
        """
        myScriptS = []
        myScriptS.append("""
function swapOpacity(idFrom, idTo) {
    var svgFrom = document.getElementById(idFrom);
    var svgTo = document.getElementById(idTo);
    var attrFrom = svgFrom.getAttribute("opacity");
    var attrTo = svgTo.getAttribute("opacity");
    svgTo.setAttributeNS(null, "opacity", attrFrom);
    svgFrom.setAttributeNS(null, "opacity", attrTo);
}

function setOpacity(id, value) {
    var svgElem = document.getElementById(id);
    svgElem.setAttributeNS(null, "opacity", value);
}

""")
        # Pop-up for histogram that uses different technique
        myScriptS.append("""
function showHistogram(x, y) {
    var histElem = document.getElementById("HistogramLegend");
    // Use the ID to compute the y offset. The x offset is 8.0mm for text,
    // 2.0mm or 0mm for rect
    for (var i = 0; i < 38; i += 2) {
        var elem = histElem.children[i / 2]
        if (i == 0) {
            var xOffset = 0;
        } else if (elem.nodeName == "text") {
            var xOffset = 8;
        } else {
            var xOffset = 2;
        }
        elem.setAttributeNS(null, "x", x + xOffset + "mm");
        elem.setAttributeNS(null, "y", y + i + "mm");
    }
    histElem.setAttributeNS(null, "opacity", 1.0);
}
 
function hideHistogram() {
    setOpacity("HistogramLegend", 0.0)
}
 
""")
        # Scaling controls
        myScriptS.append("""
function scaleGraphic(scale, theId) {
    var graphicGroup = document.getElementById("graphic");
    graphicGroup.setAttributeNS(null, "transform", "scale(" + scale + ")");
    // Un-bold all then bold the txtId.
    var scaleGroup = document.getElementById("scaleGroup");
    for (var i = 0; i < scaleGroup.children.length; ++i) {
        var elem = scaleGroup.children[i];
        if (elem.id == theId) {
            elem.setAttributeNS(null, "font-weight", "bold");
        } else {
            elem.setAttributeNS(null, "font-weight", "normal");
        }
    }
}
""")
        theSvg.writeECMAScript(u''.join(myScriptS))

    def _writeAlternateText(self, theSvg, thePoint, theId, theText, theAltS, yOffs=Coord.Dim(0, 'pt')):
        """Composes and writes the (pop-up) alternate text.
        thePoint is the physical point to locate both texts."""
        # Write a grouping element and give it the alternate ID
        with SVGWriter.SVGGroup(theSvg, {'id' : 't%s%s' % (theId, self.ALT_ID_SUFFIX), 'opacity' : '0.0'}):
            altFontSize = self.ALT_FONT_PROPERTIES[self.ALT_FONT_FAMILY]['size']
            altFontLenFactor = self.ALT_FONT_PROPERTIES[self.ALT_FONT_FAMILY]['lenFactor']
            altFontHeightFactor = self.ALT_FONT_PROPERTIES[self.ALT_FONT_FAMILY]['heightFactor']
            # Compute masking box for alternate
            maxChars = max([len(s) for s in theAltS])
            # Take around 80% of character length
            boxWidth = Coord.Dim(altFontSize * maxChars * altFontLenFactor, 'pt')
            if len(theAltS) < 2:
                boxHeight = Coord.Dim(altFontSize * 2, 'pt')
            else:
                boxHeight = Coord.Dim(altFontSize * len(theAltS) * altFontHeightFactor, 'pt')
                 
            boxAttrs = { 'fill' : self.ALT_RECT_FILL }
            with SVGWriter.SVGRect(
                    theSvg,
                    # Edge the plot point up and left by a bit
                    Coord.newPt(
                        thePoint,
                        incX=Coord.Dim(-1 * altFontSize * (1 + len(theText) * altFontLenFactor / 2.0), 'pt'),
                        incY=Coord.Dim(-1*altFontHeightFactor * altFontSize, 'pt') + yOffs,
                    ),
                    Coord.Box(boxWidth, boxHeight),
                    boxAttrs,
                ):
                pass
            # As the main text is centered and the alt text is left
            # justified we need to move the text plot point left by a bit.
            myAltTextPt = Coord.newPt(
                thePoint,
                incX=Coord.Dim(-1 * altFontSize * len(theText) * altFontLenFactor / 2.0, 'pt'),
                incY=yOffs,
            )
            with SVGWriter.SVGText(theSvg, myAltTextPt, 'Courier', altFontSize,
                        {
                            'font-weight'       : "normal",
                        }
                    ):
                self._writeStringListToTspan(theSvg, myAltTextPt, theAltS)


    def _writeStringListToTspan(self, theSvg, thePointX, theList):
        """Converts a multi-line string to tspan elements in monospaced format.

        This writes the tspan elements within an existing text element, thus:

        .. code-block:: html

            <text id="original.alt" font-family="Courier" font-size="12" text-anchor="middle" x="250" y="250">
                <tspan xml:space="preserve"> One</tspan>
                <tspan x="250" dy="1em" xml:space="preserve"> Two</tspan>
                <tspan x="250" dy="1em" xml:space="preserve">Three</tspan>
            </text>

        :param theSvg: The SVG stream.
        :type theSvg: :py:class:`cpip.plot.SVGWriter.SVGWriter`

        :param thePointX: Coordinate.
        :type thePointX: :py:class:`cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([float, <class 'str'>])])`

        :param theList: List of strings to write.
        :type theList: ``list([str])``

        :returns: ``NoneType``
        """
        #theSvg.xmlSpacePreserve()
        for i, aLine in enumerate(theList):
            elemAttrs = {}#'xml:space' : "preserve"}
            if i > 0:
                elemAttrs['x'] = SVGWriter.dimToTxt(thePointX.x) 
                elemAttrs['dy'] = "1.5em"
            with XmlWrite.Element(theSvg, 'tspan', elemAttrs):
                theSvg.characters(aLine)
                theSvg.characters(' ')
    #=============================================
    # End: Writing SVG code to do pop-up text.
    #=============================================
