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

"""Provides a means of re-interpreting the coordinate system when plotting
trees so that the the tree root can be top/left/bottom/right and the child
order plotted anti-clockwise or clockwise.

This can convert 'logical' positions into 'physical' positions. Where a
'logical' position is one with the root of the tree at the top and the
child nodes in left-to-right (i.e. anti-clockwise) order.
A 'physical' position is a plot-able position where the root of the tree is
top/left/bottom or right and the child nodes are in anti-clockwise or
clockwise order.

Transfoming sizes and positions
-------------------------------
Given:
If the first suffix is 'l' this is the "logical" coordinate system.                                
If the first suffix is 'p' this is the "physical" coordinate system.                                
                                
C    The canvas dimension, Cpw is "Canvas physical width"                            
W    Width dimension, physical and logical.                            
D    Depth dimension, physical and logical.                            
B    Box datum position ("top-left"), physical and logical, x and y.                            
P    Arbitrary point, physical and logical, x and y.                            
                                
So this "logical view" of the tree graph ('top' and '-'):
i.e. Root(s) is a top and children are written in an anti-clockwise.

 ---> x
 |
 \/
 y

<------------------------ Clw ------------------------>
|                                  To Parent
|                                     |
|             Blx, Bly -->*************************
|                         *                  |    *
Cld                       *                 Dl    *
|                         *<-------- Wl -----|--->*
|                         *                  |    *
|       Plx, Ply ->.      *                  |    *
|                         *************************
|                             |        |       |
|                        To C[0]  To C[c]   To C[C-1]

                                
Origin Cpw    Cpd    Wp    Dp    Bpx            Bpy            Ppx        Ppy
------ ---    ---    --    --    ---            ---            ---        ---
top    Clw    Cld    Wl    Dl    Blx            Bly            Plx        Ply
left   Cld    Clw    Dl    Wl    Bly            (Clw-Plx-Wl)   Ply        Clw-Plx
bottom Clw    Cld    Wl    Dl    (Clw-Plx-Wl)   (Cld-Ply-Dl)   Clw-Plx    Cld-Ply
right  Cld    Clw    Dl    Wl    (Cld-Ply-Dl)   Blx            Cld-Ply    Plx

Note the diagonal top-right to bottom-left transference between each pair of
columns. That is because with each successive line we are doing a 90 degree
rotation (anti-clockwise) plus a +ve y translation by Clw (top->left or 
bottom->right) or Cld (left->bottom or right->top).

Incrementing child positions
----------------------------
Moving from one child to another is done in the following combinations:

Origin    '-'    '+'
------    ---    ---
top       right  left
left      up     down
bottom    left   right
right     down   up
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

from cpip import ExceptionCpip
import Coord

class ExceptionTreePlotTransform(ExceptionCpip):
    """Exception class for TreePlotTransform."""
    pass

class ExceptionTreePlotTransformRangeCtor(ExceptionTreePlotTransform):
    """Exception class for out of range input on construction."""

class TreePlotTransform(object):
    """Provides a means of re-interpreting the coordinate system when plotting trees.
    
    rootPosition = frozenset(['top', 'bottom', 'left', 'right'])
    default: 'top'

    sweepDirection = frozenset(['+', '-'])
    default: '-'

    Has functionality for interpreting width/depth to actual postions
    given rootPostion.
    """
    # position of the root node in the plot
    RANGE_ROOTPOS = ['top', 'left', 'bottom', 'right']
    RANGE_ROOTPOS_INT = range(len(RANGE_ROOTPOS))
    # Sweep direction of the children in the plot
    RANGE_SWEEPDIR = ['-', '+']
    RANGE_SWEEPDIR_INT = range(len(RANGE_SWEEPDIR))
    def __init__(self, theLogicalCanvas, rootPos='top', sweepDir='-'):
        """Constructor, takes a 'logical' Canvas as a Coord.Box and the orientation."""
        # canvas is stored as we need it for internal manipulations
        # Clw
        self._clw = theLogicalCanvas.width
        # Cld
        self._cld = theLogicalCanvas.depth
        try:
            # As integer for comparison speed
            self._rootPos = self.RANGE_ROOTPOS.index(rootPos)
        except ValueError:
            raise ExceptionTreePlotTransformRangeCtor(
                '"%s" not in: %s' % (rootPos, self.RANGE_ROOTPOS)
                )
        try:
            # As integer for comparison speed
            self._sweepDir = self.RANGE_SWEEPDIR.index(sweepDir)
        except ValueError:
            raise ExceptionTreePlotTransformRangeCtor(
                '"%s" not in: %s' % (sweepDir, self.RANGE_SWEEPDIR)
                )

    @property
    def rootPos(self):
        assert(self._rootPos in self.RANGE_ROOTPOS_INT)
        return self.RANGE_ROOTPOS[self._rootPos]

    @property
    def sweepDir(self):
        assert(self._sweepDir in self.RANGE_SWEEPDIR_INT)
        return self.RANGE_SWEEPDIR[self._sweepDir]

    @property
    def positiveSweepDir(self):
        """True if positive sweep, false otherwise."""
        assert(self._sweepDir in self.RANGE_SWEEPDIR_INT)
        return self.RANGE_SWEEPDIR[self._sweepDir] == '+'

    def genRootPos(self):
        """Yield all possible root positions."""
        for aPos in self.RANGE_ROOTPOS:
            yield aPos 

    def genSweepDir(self):
        """Yield all possible root positions."""
        for aDir in self.RANGE_SWEEPDIR:
            yield aDir

#assert(self._rootPos in self.RANGE_ROOTPOS_INT)
#if self._rootPos == 0: #'top':
#elif self._rootPos == 1: #'left':
#elif self._rootPos == 2: #'bottom':
##'right':
    
    def canvasP(self):
        """Returns a Coord.Box that describes the physical canvass."""
        #Origin     Cpw    Cpd
        #------     ---    ---
        #top        Clw    Cld
        #left       Cld    Clw
        #bottom     Clw    Cld
        #right      Cld    Clw
        assert(self._rootPos in self.RANGE_ROOTPOS_INT)
        if self._rootPos == 0: #'top'
            return Coord.Box(self._clw, self._cld)
        elif self._rootPos == 1: #'left'
            return Coord.Box(self._cld, self._clw)
        elif self._rootPos == 2: #'bottom'
            return Coord.Box(self._clw, self._cld)
        #'right'
        return Coord.Box(self._cld, self._clw)

    def boxP(self, theBl):
        """Given a logical box this returns a Coord.Box that describes the physical box."""
        #Origin    Wp    Dp
        #top       Wl    Dl
        #left      Dl    Wl
        #bottom    Wl    Dl
        #right     Dl    Wl
        assert(self._rootPos in self.RANGE_ROOTPOS_INT)
        if self._rootPos == 0: #'top'
            return Coord.Box(theBl.width, theBl.depth)
        elif self._rootPos == 1: #'left'
            return Coord.Box(theBl.depth, theBl.width)
        elif self._rootPos == 2: #'bottom'
            return Coord.Box(theBl.width, theBl.depth)
        #'right'
        return Coord.Box(theBl.depth, theBl.width)

    def boxDatumP(self, theBlxy, theBl):
        """Given a logical point and logical box this returns a physical
        point that is the box datum ("upper left")."""
        #Origin Bpx            Bpy
        #------ ---            ---
        #top    Blx            Bly
        #left   Bly            (Clw-Plx-Wl)
        #bottom (Clw-Plx-Wl)   (Cld-Ply-Dl)
        #right  (Cld-Ply-Dl)   Blx
        assert(self._rootPos in self.RANGE_ROOTPOS_INT)
        if self._rootPos == 0: #'top'
            return Coord.Pt(theBlxy.x, theBlxy.y)
        elif self._rootPos == 1: #'left'
            return Coord.Pt(theBlxy.y, self._clw - theBlxy.x - theBl.width)
        elif self._rootPos == 2: #'bottom'
            return Coord.Pt(
                self._clw - theBlxy.x - theBl.width,
                self._cld - theBlxy.y - theBl.depth
                )
        #'right'
        return Coord.Pt(
            self._cld - theBlxy.y - theBl.depth,
            theBlxy.x
        )

    def tdcL(self, theBlxy, theBl):
        """Given a logical datum (logical top left) and a logical box this
        returns logical top dead centre of a box."""
        assert(self._rootPos in self.RANGE_ROOTPOS_INT)
        if self._rootPos == 0: #'top' so return logical top
            return Coord.Pt(theBlxy.x+theBl.width.scale(0.5), theBlxy.y)
        elif self._rootPos == 1: #'left' so return logical right
            return Coord.Pt(theBlxy.x+theBl.width, theBlxy.y+theBl.depth.scale(0.5))
        elif self._rootPos == 2: #'bottom' so return logical bottom
            return Coord.Pt(theBlxy.x+theBl.width.scale(0.5), theBlxy.y+theBl.depth)
        #'right' so return logical left
        return Coord.Pt(theBlxy.x, theBlxy.y+theBl.depth.scale(0.5))
    
    def bdcL(self, theBlxy, theBl):
        """Given a logical datum (logical top left) and a logical box this
        returns logical bottom dead centre of a box."""
        assert(self._rootPos in self.RANGE_ROOTPOS_INT)
        if self._rootPos == 0: #'top' so return logical bottom
            return Coord.Pt(theBlxy.x+theBl.width.scale(0.5), theBlxy.y+theBl.depth)
        elif self._rootPos == 1: #'left' so return logical left
            return Coord.Pt(theBlxy.x, theBlxy.y+theBl.depth.scale(0.5))
        elif self._rootPos == 2: #'bottom' so return logical top
            return Coord.Pt(theBlxy.x+theBl.width.scale(0.5), theBlxy.y)
        #'right' so return logical right
        return Coord.Pt(theBlxy.x+theBl.width, theBlxy.y+theBl.depth.scale(0.5))
    
    def prevdcL(self, theBlxy, theBl):
        """Given a logical datum (logical top left) and a logical box this
        returns logical 'previous' dead centre of a box."""
        assert(self._sweepDir in self.RANGE_SWEEPDIR_INT)
        if self._sweepDir == 0: # '-' so left dead centre
            return Coord.Pt(theBlxy.x, theBlxy.y+theBl.depth.scale(0.5))
        # '+' so right dead centre
        return Coord.Pt(theBlxy.x+theBl.width, theBlxy.y+theBl.depth.scale(0.5))
    
    def nextdcL(self, theBlxy, theBl):
        """Given a logical datum (logical top left) and a logical box this
        returns logical 'next' dead centre of a box."""
        assert(self._sweepDir in self.RANGE_SWEEPDIR_INT)
        if self._sweepDir == 0: # '-' so right dead centre
            return Coord.Pt(theBlxy.x+theBl.width, theBlxy.y+theBl.depth.scale(0.5))
        # '+' so left dead centre
        return Coord.Pt(theBlxy.x, theBlxy.y+theBl.depth.scale(0.5))
        
    def tdcP(self, theBlxy, theBl):
        """Given a logical datum (logical top left) and a logical box this
        returns physical top dead centre of a box."""
        assert(self._rootPos in self.RANGE_ROOTPOS_INT)
        return self.pt(self.tdcL(theBlxy, theBl))

    def bdcP(self, theBlxy, theBl):
        """Given a logical datum (logical top left) and a logical box this
        returns physical bottom dead centre of a box."""
        assert(self._rootPos in self.RANGE_ROOTPOS_INT)
        return self.pt(self.bdcL(theBlxy, theBl))

    def pt(self, thePt, units=None):
        """Given an arbitrary logical point as a Coord.Pt(), this returns the
        physical point as a Coord.Pt().
        If units is supplied then the return value will be in those units."""
        #Origin Ppx        Ppy
        #------ ---        ---
        #top    Plx        Ply
        #left   Ply        Clw-Plx
        #bottom Clw-Plx    Cld-Ply
        #right  Cld-Ply    Plx
        assert(self._rootPos in self.RANGE_ROOTPOS_INT)
        if self._rootPos == 0: #'top':
            retVal = Coord.Pt(thePt.x, thePt.y)
        elif self._rootPos == 1: #'left':
            retVal = Coord.Pt(thePt.y, self._clw-thePt.x)            
        elif self._rootPos == 2: #'bottom':
            retVal = Coord.Pt(self._clw-thePt.x, self._cld-thePt.y)
        else: #'right':
            retVal = Coord.Pt(self._cld-thePt.y, thePt.x)
        if units is not None:
            return retVal.convert(units)
        return retVal            

    def startChildrenLogicalPos(self, thePt, theBox):
        """Returns the starting child logical datum point ('top-left') given
        the children logical datum point and the children.bbSigma.
        Returns a Coord.Pt().
        This takes into account the sweep direction."""
        assert(self._sweepDir in self.RANGE_SWEEPDIR_INT)
        if self._sweepDir == 0: # '-' so right
            return thePt
        # '+' so left
        return Coord.Pt(thePt.x+theBox.width, thePt.y)

    def preIncChildLogicalPos(self, thePt, theBox):
        """Pre-incrempents the child logical datum point ('top-left') given
        the child logical datum point and the child.bbSigma.
        Returns a Coord.Pt().
        This takes into account the sweep direction."""
        assert(self._sweepDir in self.RANGE_SWEEPDIR_INT)
        if self._sweepDir == 0: # '-' so right
            return thePt
        # '+' so left
        return Coord.Pt(thePt.x-theBox.width, thePt.y)
        
    def postIncChildLogicalPos(self, thePt, theBox):
        """Post-incrempents the child logical datum point ('top-left') given
        the child logical datum point and the child.bbSigma.
        Returns a Coord.Pt().
        This takes into account the sweep direction."""
        assert(self._sweepDir in self.RANGE_SWEEPDIR_INT)
        if self._sweepDir == 0: # '-' so right
            return Coord.Pt(thePt.x+theBox.width, thePt.y)
        # '+' so left
        return thePt
        
    def incPhysicalChildPos(self, thePt, theDim):
        """Given a child physical datum point and a distance to next child this
        returns the next childs physical datum point.
        TODO: Remove this as redundant?""" 
        #Origin    '-'    '+'
        #------    ---    ---
        #top       right  left
        #left      up     down
        #bottom    left   right
        #right     down   up
        assert(self._rootPos in self.RANGE_ROOTPOS_INT)
        assert(self._sweepDir in self.RANGE_SWEEPDIR_INT)
        #assert(0)
        # We need to think about this as it is incomplete. We need a
        # 'where do I start' and a 'how do I increment'. These can be both
        # entirely logical coordinates.
        if self._rootPos == 0: # 'top'
            if self._sweepDir == 0: # '-' so right
                return Coord.Pt(thePt.x+theDim, thePt.y)
            # '+' so left
            return Coord.Pt(thePt.x-theDim, thePt.y)
        elif self._rootPos == 1: # 'left'
            if self._sweepDir == 0: # '-' so up
                return Coord.Pt(thePt.x, thePt.y-theDim)
            # '+' so down
            return Coord.Pt(thePt.x, thePt.y+theDim)
        elif self._rootPos == 2: # 'bottom'
            if self._sweepDir == 0: # '-' so left
                return Coord.Pt(thePt.x-theDim, thePt.y)
            # '+' so right
            return Coord.Pt(thePt.x+theDim, thePt.y)
        # 'right'
        if self._sweepDir == 0: # '-' so down
            return Coord.Pt(thePt.x, thePt.y+theDim)
        # '+' so up
        return Coord.Pt(thePt.x, thePt.y-theDim)



