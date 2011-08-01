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

"""Bounding Boxes
==============
Legend for the drawing below:
**** - Self sigma BB.
~~~~ - Self pad box
#### - Self width and depth.
.... - All children
++++ - Child[n] sigma BB.

i.e. For a child its ++++ is equivalent to my ****.

D      - Self datum point.
S      - Self plot datum point.
x[n]   - Child datum point.
Pl     - Parent landing point to self.
Pt     - Parent take-off point from self.
P[n]   - Self take off point and landing point to child n.
pl[n]  - Child n landing point from self.
pt[n]  - Child n take-off point to self.
tdc    - Top dead centre.

Box .... has depth of max(Boxes(++++).width) and
width max(Box(~~~~), sum(Boxes(++++).depth)). 

Each instance of class knows about the following:
Boxes:
**** - Self sigma BB as computed Dim() objects: self.bbSigmaDepth and
        self.bbSigmaWidth. Or as computed Box() object self.bbSigma
~~~~ - As computed Dim() objects: self.bbSelfWidth, self.bbSelfDepth
#### - Self width and depth as Dim() objects: self.width and self.depth
.... - All children as a Box() object: self.bbChildren
And padding between ~~~~ and .... as Dim() object self.bbSpaceChildren

i.e. not ++++ - Child[n] sigma BB. That the caller knows about its children.

Points:
Given D each instance of this class knows:
S, Pl, Pt, P[0] to P[N-1], x[0], tdc (only).

In the following diagrams where lines are adjacent that means that there is no
spacing between them.

-|-----> x increases
 |
 |
\/
y increases

D ***************************************************************************
*                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~                     *
*                ~                                    ~                     *
*                ~    S ### Pl ###tdc### Pt ######    ~                     *
*                ~    #                          #    ~                     *
*                ~    #                          #    ~                     *
*                ~    #                          #    ~                     *
*                ~    #                          #    ~                     *
*                ~    ## P[0] ## P[c] ## P[C-1] ##    ~                     *
*                ~                                    ~                     *
*                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~                     *
*                                        |                                  *
*                                        |= self._bbSpaceChildren           *
*                                        |                                  *
*...........................................................................*
*.x[0] + pl[0] + pt[0] +x[c] + pl[c] + pt[c] ++++++++++++x[C-1]+pl/pt[C-1]+.*
*.+                    ++                               ++                +.*
*.+                    ++                               ++                +.*
*.+++++++++++++++++++++++                               ++                +.*
*.                      +                               ++                +.*
*.                      +                               +++++++++++++++++++.*
*.                      +                               +                  .*
*.                      +++++++++++++++++++++++++++++++++                  .*
*...........................................................................*
*****************************************************************************

Note: .... can be narrower than ~~~~

Verticies
=========

The following show root at the left. Linking parent to child:

                    PC_land    PC_stop
                     |            |
                     x>>>>>>>>>>>>x
                    /
                   /
    x>>>>>>>>>>>>x/
    |            |
PC_roll        PC_to

PC_roll and PC_to are determined by the parent.
PC_land and PC_stop are determined by the child.

And child to parent:

CP_stop     CP_land
    |          |
    x<<<<<<<<<<x\
                 \
                  \
                   x<<<<<<<<<<<<x
                   |            |
                CP_to        CP_roll

CP_roll and CP_to are determined by the child.
CP_land and CP_stop are determined by the parent.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import Coord


from cpip import ExceptionCpip

class ExceptionPlotNode(ExceptionCpip):
    """Exception when handling PlotNodeBbox object."""
    pass

class PlotNodeBbox(object):
    """This is a class that can hold the width and depth of an object and
    the bounding box of self and the children.
    This can then compute various dimensions of self and children.""" 
    def __init__(self):
        """Constructor."""
        # Set directly
        # These are all Coord.Dim()
        self._width = None
        self._depth = None
        # Additional space between me and my children that is equal to how
        # all other sibling parents behave.
        # This will be set to a Coord.Dim()
        self._bbSpaceChildren = None
        # Padding around me. This will be a Coord.Pad()
        self._bbSelfPadding = None
        # The cumulative Bounding Box of the children.
        # This will be a Coord.Box()
        self._bbChildren = None
        self._numChildren = 0

    def __str__(self):
        retList = ['|.......PlotNode: w=%s, d=%s' % (self._width, self._depth)]
        retList.append('|bbSpaceChildren: %s' % str(self._bbSpaceChildren))
        retList.append('|..bbSelfPadding: %s' % str(self._bbSelfPadding))
        retList.append('|.....bbChildren: %s' % str(self._bbChildren))
        retList.append('|........bbSigma: %s' % str(self.bbSigma))
#===============================================================================
#        if self._bbSpaceChildren is not None \
#        and self._bbSelfPadding is not None:
#            retList.append('|........bbSigma: %s' % str(self.bbSigma))
#        else:
#            retList.append('|........bbSigma: N/A')
#===============================================================================
        return '\n'.join(retList)

    def _raiseOnChildIndexOutOfRange(self, childIndex):
        """Will raise a ExceptionPlotNode is the childIndex is out of range or
        I have no children."""
        if self._numChildren <= 0:
            raise ExceptionPlotNode('PlotNodeBboxBoxy.pcRoll() when no children %d' % self._numChildren)
        if childIndex < 0:
            raise ExceptionPlotNode('PlotNodeBboxBoxy.pcRoll() index %d < 0' % childIndex)
        if childIndex >= self._numChildren:
            raise ExceptionPlotNode('PlotNodeBboxBoxy.pcRoll() index %d out of range [0...%d]' \
                                    % (childIndex, self._numChildren-1))
            
    def extendChildBbox(self, theChildBbox):
        """Extends the child bounding box by the amount theChildBbox which
        should be a Coord.Box(). This extends the .... line."""
        if self._bbChildren is None:
            newWidth=theChildBbox.width
            newDepth=theChildBbox.depth
        else:
            newWidth = self._bbChildren.width + theChildBbox.width
            newDepth = max(self._bbChildren.depth, theChildBbox.depth)
        self._bbChildren = Coord.Box(width=newWidth, depth=newDepth)
        self._numChildren += 1

    # Properties that are set/get
    @property
    def numChildren(self):
        return self._numChildren
    
    @property
    def width(self):
        """The immediate width of the node, if None then no BB width is
        allocated. i.e. the width of box ####"""
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def depth(self):
        """The immediate depth of the node, if None then no BB depth or
        bbSpaceChildrend is allocated. i.e. the depth of box ####"""
        return self._depth

    @depth.setter
    def depth(self, value):
        self._depth = value
        
    @property
    def box(self):
        """The Coord.Box() of ####."""
        return Coord.Box(self._width, self._depth)
         
    @property
    def hasSetArea(self):
        """Returns True if width and depth are set, False otherwise."""
        return self.width is not None and self.depth is not None

    @property
    def bbSpaceChildren(self):
        """The additional distance to give to the children as a
        Coord.Dim()."""
        if self._bbSpaceChildren is None:
            return Coord.zeroBaseUnitsDim()
        return self._bbSpaceChildren

    @bbSpaceChildren.setter
    def bbSpaceChildren(self, value):
        self._bbSpaceChildren = value

    @property
    def bbSelfPadding(self):
        """The immediate padding around self as a Coord.Pad()."""
        if self._bbSelfPadding is None:
            return Coord.zeroBaseUnitsPad()
        return self._bbSelfPadding

    @bbSelfPadding.setter
    def bbSelfPadding(self, value):
        self._bbSelfPadding = value

    @property
    def bbChildren(self):
        """The bounding box of children as a Coord.Box() or None.
        i.e. the box ...."""
        return self._bbChildren

    @bbChildren.setter
    def bbChildren(self, value):
        self._bbChildren = value

    @property
    def bbChildrenWidth(self):
        """The bounding box width of children as a Coord.Dim() or None.
        i.e. the width of box ...."""
        if self._bbChildren is not None:
            return self._bbChildren.width

    @property
    def bbChildrenDepth(self):
        """The bounding box depth of children as a Coord.Dim() or None.
        i.e. the depth of box ...."""
        if self._bbChildren is not None:
            return self._bbChildren.depth

    # Computed properties
    @property
    def bbSelfWidth(self):
        """The width of self plus padding as a Coord.Dim() or None.
        i.e. the width of box ~~~~"""
        if self.width is None:
            return Coord.Dim(0, None)
        myPad = self.bbSelfPadding
        return myPad.prev + self.width + myPad.next

    @property
    def bbSelfDepth(self):
        """The depth of self plus padding as a Coord.Dim().
        i.e. the depth of box ~~~~"""
        if self.depth is None:
            return Coord.Dim(0, None)
        myPad = self.bbSelfPadding
        return myPad.parent + self.depth + myPad.child

    @property
    def bbSigmaWidth(self):
        """The depth of self+children as a Coord.Dim() or None in the case that
        I don't exist and I have no children.
        i.e. the width of box ****"""
        if self.width is None:
            # Don't leave space to plot me...
            return self.bbChildrenWidth
        elif self.bbChildrenWidth is not None:
            return max(self.bbSelfWidth, self.bbChildrenWidth)
        return self.bbSelfWidth

    @property
    def bbSigmaDepth(self):
        """The depth of self+children as a Coord.Dim() or None in the case that
        I don't exist and I have no children.
        i.e. the depth of box ****"""
        if self.depth is None:
            # Don't leave space to plot me...
            return self.bbChildrenDepth
        elif self.bbChildrenDepth is not None:
            retVal = self.bbSelfDepth + self.bbChildrenDepth
            # Additional spacing if available
            retVal += self.bbSpaceChildren
            return retVal
        return self.bbSelfDepth

    @property
    def bbSigma(self):
        """Bounding box of self and my children as a Coord.Box()."""
        return Coord.Box(width=self.bbSigmaWidth, depth=self.bbSigmaDepth)
    
    # Computed points
    # Given X each instance of this class knows:
    # S, Pl, Pt, P[0] to P[N-1], x[0] (only).
    def _incXToSelfDatum(self):
        """The amount to increment X to get from the logical datum point, D, to
        the logical point S."""
        assert(
               (self.numChildren == 0 and self.bbChildrenWidth is None)
               or (self.numChildren >= 0 and self.bbChildrenWidth is not None)
            )
        if self.bbChildrenWidth is not None \
        and self.bbChildrenWidth > self.bbSelfWidth:
            # Box .... is wider ~~~~
            incX = (self.bbChildrenWidth - self.bbSelfWidth).scale(0.5)
        else:
            # Box .... is narrower than ~~~~
            incX = Coord.zeroBaseUnitsDim()
        if self.width is not None:
            incX += self.bbSelfPadding.prev
        return incX
    
    def _incYToSelfDatum(self):
        """The amount to increment Y to get from the logical datum point, D, to
        the logical point S."""
        assert(
               (self.numChildren == 0 and self.bbChildrenWidth is None)
               or (self.numChildren >= 0 and self.bbChildrenWidth is not None)
            )
        if self.depth is None:
            # Don't leave space to plot me...
            incY = Coord.zeroBaseUnitsDim()
        else:
            incY = self.bbSelfPadding.parent
        return incY
    
    def plotPointSelf(self, theDatum):
        """The point S as a Coord.Pt() given theDatum as Coord.Pt()."""
        return Coord.newPt(theDatum, self._incXToSelfDatum(), self._incYToSelfDatum())

    def plotPointCentre(self, theLd):
        """Returns the logical point at the centre of the box shown as #### above."""
        incX = self._incXToSelfDatum()
        if self.width is not None:
            incX += self.width.scale(0.5)
        incY = self._incYToSelfDatum()
        if self.depth is not None:
            incY += self.depth.scale(0.5)
        return Coord.newPt(theLd, incX, incY)

    def childBboxDatum(self, theDatum):
        """The point x[0] as a Coord.Pt() given theDatum as Coord.Pt() or None
        if no children."""
        assert(
               (self.numChildren == 0 and self.bbChildrenWidth is None)
               or (self.numChildren >= 0 and self.bbChildrenWidth is not None)
            )
        if self._numChildren > 0:
            if self.bbChildrenWidth > self.bbSelfWidth:
                # Box .... is wider ~~~~
                incX = Coord.zeroBaseUnitsDim()
            else:
                # Box .... is narrower than ~~~~
                incX = (self.bbSelfWidth - self.bbChildrenWidth).scale(0.5)
            if self.depth is None:
                # Don't leave space to plot me...
                incY = Coord.zeroBaseUnitsDim()
            else:
                incY = self.bbSelfDepth + self.bbSpaceChildren
            return Coord.newPt(theDatum, incX, incY)
        # Returns None
    
class PlotNodeBboxBoxy(PlotNodeBbox):
    """Sub-class parent child edges that contact the corners of the
    box shown as #### above."""

    def _pcXForChild(self, childIndex):
        self._raiseOnChildIndexOutOfRange(childIndex)
        incX = Coord.zeroBaseUnitsDim()#self._incXToSelfDatum()
        if self.width is not None:
            # Now add/subtract according to the childIndex
            # Split evenly depending on number of children
            myInterval = self.width.scale(1.0/self._numChildren)
            incX += myInterval.scale(childIndex+0.5)
        return incX

    def pcRoll(self, theDatum, childIndex):
        """The me-as-parent-to-child logical start point given the logical datum
        as a Coord.Pt and the child ordinal. This gives equispaced points along
        the lower edge."""
        incX = self._pcXForChild(childIndex)
        if self.depth is None:
            # Don't leave space to plot me...
            incY = Coord.zeroBaseUnitsDim()
        else:
            #incY = self.bbSelfPadding.parent + self.depth
            incY = self.depth
        return Coord.newPt(theDatum, incX, incY)
        
    def pcTo(self, theDatum, childIndex):
        """The me-as-parent-to-child logical take off point given the logical
        datum as a Coord.Pt ind the child ordinal. This gives equispaced points
        along the lower edge."""
        incX = self._pcXForChild(childIndex)
        if self.depth is None:
            # Don't leave space to plot me...
            incY = Coord.zeroBaseUnitsDim()
        else:
            #incY = self.bbSelfPadding.parent + self.depth + self.bbSelfPadding.child
            incY = self.depth + self.bbSelfPadding.child
        return Coord.newPt(theDatum, incX, incY)
        
    def pcLand(self, theLd):
        """The parent-to-me-as-child landing point given the logical datum as a Coord.Pt."""
        return Coord.newPt(theLd, self._incXToSelfDatum(), Coord.zeroBaseUnitsDim())
        
    def pcStop(self, theLd):
        """The parent-to-me-as-child stop point given the logical datum as a Coord.Pt."""
        return Coord.newPt(theLd, self._incXToSelfDatum(), self._incYToSelfDatum())

    def cpRoll(self, theLd):
        """The me-as-child-to-parent start point given the logical datum as a Coord.Pt."""
        if self.width is not None:
            return Coord.newPt(theLd, self._incXToSelfDatum()+self.width, self._incYToSelfDatum())
        
    def cpTo(self, theLd):
        """The me-as-child-to-parent take off point given the logical datum as a Coord.Pt."""
        return Coord.newPt(theLd, self._incXToSelfDatum()+self.width, Coord.zeroBaseUnitsDim())

    def cpLand(self, theLd, childIndex):
        """The me-as-parent-from-child landing point given the logical datum as a Coord.Pt."""
        return self.pcTo(theLd, childIndex)
        
    def cpStop(self, theLd, childIndex):
        """The me-as-parent-from-child stop point given the logical datum as a Coord.Pt."""
        return self.pcRoll(theLd, childIndex)

class PlotNodeBboxRoundy(PlotNodeBbox):
    """Sub-class for parent child edges that contact the centre of the
    box shown as #### above."""
    
    def pcRoll(self, theDatumL, childIndex):
        """The me-as-parent-to-child logical start point given the logical datum
        as a Coord.Pt ind the child ordinal. This gives equispaced points along
        the lower edge."""
        self._raiseOnChildIndexOutOfRange(childIndex)
        return self.plotPointCentre(theDatumL)
        
    def pcTo(self, theDatumL, childIndex):
        """The me-as-parent-to-child logical take off point given the logical
        datum as a Coord.Pt ind the child ordinal. This gives equispaced points
        along the lower edge."""
        self._raiseOnChildIndexOutOfRange(childIndex)
        return Coord.newPt(self.plotPointCentre(theDatumL), incX=None, incY=self.depth.scale(0.5))
        #return self.plotPointCentre(theDatumL)

    def pcLand(self, theDatumL):
        """The parent-to-me-as-child landing point given the logical datum as a Coord.Pt."""
        return Coord.newPt(self.plotPointCentre(theDatumL), incX=None, incY=self.depth.scale(-0.5))
        #return theDatumL#self.plotPointCentre(theDatumL)
        
    def pcStop(self, theDatumL):
        """The parent-to-me-as-child stop point given the logical datum as a Coord.Pt."""
        return self.plotPointCentre(theDatumL)

    def cpRoll(self, theDatumL):
        """The me-as-child-to-parent start point given the logical datum as a Coord.Pt."""
        return self.pcStop(theDatumL)#theDatumL#self.plotPointCentre(theDatumL)
        
    def cpTo(self, theDatumL):
        """The me-as-child-to-parent take off point given the logical datum as a Coord.Pt."""
        return self.pcLand(theDatumL)#theDatumL#self.plotPointCentre(theDatumL)

    def cpLand(self, theDatumL, childIndex):
        """The me-as-parent-from-child landing point given the logical datum as a Coord.Pt."""
        return self.pcTo(theDatumL, childIndex)#theDatumL#self.plotPointCentre(theDatumL)
        
    def cpStop(self, theDatumL, childIndex):
        """The me-as-parent-from-child stop point given the logical datum as a Coord.Pt."""
        return self.pcRoll(theDatumL, childIndex)#theDatumL#self.plotPointCentre(theDatumL)

