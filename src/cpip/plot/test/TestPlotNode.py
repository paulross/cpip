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

"""
paulross@L071183 /cygdrive/d/wip/small_projects/PlotTree/src/python
$ python c:/Python26/Lib/site-packages/coverage.py -x test/TestPlotNode.py
"""

import os
import sys
import logging
#import StringIO

#sys.path.append(os.path.join(os.pardir + os.sep))
from cpip.plot import PlotNode
from cpip.plot import Coord

######################
# Section: Unit tests.
######################
import unittest

class TestPlotNodeCtor(unittest.TestCase):
    """Tests the PlotNode() class constructor."""

    def testCtor(self):
        """Tests PlotNode() constructor empty."""
        myObj = PlotNode.PlotNodeBbox()
        self.assertEqual(myObj.width, None)
        self.assertEqual(myObj.depth, None)

class TestPlotNodeSetting(unittest.TestCase):
    """Tests the PlotNode() direct settings."""

    def testWidthDepth(self):
        """Tests PlotNode() set/get width and depth."""
        myObj = PlotNode.PlotNodeBbox()
        myObj.width = Coord.Dim(42, 'in')
        myObj.depth = Coord.Dim(1, 'in')
        self.assertEqual(myObj.width, Coord.Dim(42, 'in'))
        self.assertEqual(myObj.depth, Coord.Dim(1, 'in'))

    def testBbSpaceChildren(self):
        """Tests PlotNode() set/get bbSpaceChildren."""
        myObj = PlotNode.PlotNodeBbox()
        #print '\nTRACE myObj', myObj
        myObj.bbSpaceChildren = Coord.Dim(42, 'px')
        #print '\nTRACE myObj', myObj
        self.assertEqual(myObj.bbSpaceChildren, Coord.Dim(42, 'px'))

    def testBbSpacePadding(self):
        """Tests PlotNode() set/get bbSpacePadding."""
        myObj = PlotNode.PlotNodeBbox()
        myObj.width = Coord.Dim(12, 'px')
        myObj.depth = Coord.Dim(6, 'px')
        #print '\nTRACE myObj', myObj
        myPad = Coord.Pad(
            Coord.Dim(1, 'px'),   # prev
            Coord.Dim(2, 'px'),   # next
            Coord.Dim(3, 'px'),   # parent
            Coord.Dim(4, 'px'),   # child
            )
        #print '\nTRACE myPad setting', myPad
        myObj.bbSelfPadding = myPad
        #print '\nTRACE myObj setting done', myObj
        a = myObj.bbSelfPadding
        self.assertEqual(
            myObj.bbSelfPadding,
            Coord.Pad(
                Coord.Dim(1, 'px'),
                Coord.Dim(2, 'px'),
                Coord.Dim(3, 'px'),
                Coord.Dim(4, 'px'),
                )
            )
        #print '\nTRACE myObj', myObj
        self.assertEqual(
            myObj.bbSelfWidth,
            # 1 + 12 + 2 = 15
            Coord.Dim(15, 'px'),
            )
        self.assertEqual(
            myObj.bbSelfDepth,
            # 3 + 6 + 4
            Coord.Dim(13, 'px'),
            )
        #print
        #print str(myObj)
        self.assertEqual(
            str(myObj),
            """|.......PlotNode: w=Dim(12px), d=Dim(6px)
|bbSpaceChildren: None
|..bbSelfPadding: Pad(prev=Dim(1px), next=Dim(2px), parent=Dim(3px), child=Dim(4px))
|.....bbChildren: None
|........bbSigma: Box(width=Dim(15px), depth=Dim(13px))""",
            )
        #print 'TRACE myObj', myObj

    def testBbSpacePaddingNullNode(self):
        """Tests PlotNode() set/get bbSpacePadding on a null node."""
        myObj = PlotNode.PlotNodeBbox()
        myObj.width = None
        myObj.depth = None
        myPad = Coord.Pad(
            Coord.Dim(1, 'px'),   # prev
            Coord.Dim(2, 'px'),   # next
            Coord.Dim(3, 'px'),   # parent
            Coord.Dim(4, 'px'),   # child
            )
        myObj.bbSelfPadding = myPad
        self.assertEqual(
            myObj.bbSelfPadding,
            Coord.Pad(
                Coord.Dim(1, 'px'),
                Coord.Dim(2, 'px'),
                Coord.Dim(3, 'px'),
                Coord.Dim(4, 'px'),
                )
            )
        self.assertEqual(
            myObj.bbSelfWidth,
            Coord.Dim(0, None),
            )
        self.assertEqual(
            myObj.bbSelfDepth,
            Coord.Dim(0, None),
            )

    def testBbChildren(self):
        """Tests PlotNode() set/get bbChildren."""
        myObj = PlotNode.PlotNodeBbox()
        myObj.bbChildren = Coord.Box(
            Coord.Dim(1, 'px'),
            Coord.Dim(2, 'px'),
            )
        self.assertEqual(
            myObj.bbChildren,
            Coord.Box(
            Coord.Dim(1, 'px'),
            Coord.Dim(2, 'px'),
            )
            )
        self.assertEqual(
            myObj.bbChildrenWidth,
            Coord.Dim(1, 'px'),
            )
        self.assertEqual(
            myObj.bbChildrenDepth,
            Coord.Dim(2, 'px'),
            )

    def testSigma_00(self):
        """Tests PlotNode() get sigma width and depth (children dominate width)."""
        myObj = PlotNode.PlotNodeBbox()
        myObj.width = Coord.Dim(2, 'in')
        self.assertEqual(myObj.width, Coord.Dim(2, 'in'))
        myObj.depth = Coord.Dim(1, 'in')
        self.assertEqual(myObj.depth, Coord.Dim(1, 'in'))
        myPad = Coord.Pad(
            Coord.Dim(0.5, 'in'),   # prev
            Coord.Dim(0.5, 'in'),   # next
            Coord.Dim(0.5, 'in'),   # parent
            Coord.Dim(0.5, 'in'),   # child
            )
        myObj.bbSelfPadding = myPad
        myObj.bbSpaceChildren = Coord.Dim(0.5, 'in')
        self.assertEqual(myObj.bbSpaceChildren, Coord.Dim(0.5, 'in'))
        myObj.bbChildren = Coord.Box(
            Coord.Dim(4, 'in'),
            Coord.Dim(2.5, 'in'),
            )
        self.assertEqual(
            myObj.bbChildrenWidth,
            Coord.Dim(4, 'in'),
            )
        self.assertEqual(
            myObj.bbChildrenDepth,
            Coord.Dim(2.5, 'in'),
            )
        self.assertEqual(
            myObj.bbChildren,
            Coord.Box(
                Coord.Dim(4, 'in'),
                Coord.Dim(2.5, 'in'),
                )
            )
        self.assertEqual(
            myObj.bbSigmaWidth,
            Coord.Dim(4.0, 'in'),
            )
        self.assertEqual(
            myObj.bbSigmaDepth,
            Coord.Dim(5.0, 'in'),
            )
        self.assertEqual(
            myObj.bbSigma,
            Coord.Box(
                Coord.Dim(4.0, 'in'),
                Coord.Dim(5.0, 'in'),
                )
            )

    def testSigma_01(self):
        """Tests PlotNode() get sigma width and depth (parent dominates width)."""
        myObj = PlotNode.PlotNodeBbox()
        myObj.width = Coord.Dim(6, 'in')
        self.assertEqual(myObj.width, Coord.Dim(6, 'in'))
        myObj.depth = Coord.Dim(1, 'in')
        self.assertEqual(myObj.depth, Coord.Dim(1, 'in'))
        myPad = Coord.Pad(
            Coord.Dim(0.5, 'in'),   # prev
            Coord.Dim(0.5, 'in'),   # next
            Coord.Dim(0.5, 'in'),   # parent
            Coord.Dim(0.5, 'in'),   # child
            )
        myObj.bbSelfPadding = myPad
        myObj.bbSpaceChildren = Coord.Dim(0.5, 'in')
        self.assertEqual(myObj.bbSpaceChildren, Coord.Dim(0.5, 'in'))
        myObj.bbChildren = Coord.Box(
            Coord.Dim(4, 'in'),
            Coord.Dim(2.5, 'in'),
            )
        self.assertEqual(
            myObj.bbChildrenWidth,
            Coord.Dim(4, 'in'),
            )
        self.assertEqual(
            myObj.bbChildrenDepth,
            Coord.Dim(2.5, 'in'),
            )
        self.assertEqual(
            myObj.bbChildren,
            Coord.Box(
                Coord.Dim(4, 'in'),
                Coord.Dim(2.5, 'in'),
                )
            )
        self.assertEqual(
            myObj.bbSigmaWidth,
            Coord.Dim(7.0, 'in'),
            )
        self.assertEqual(
            myObj.bbSigmaDepth,
            Coord.Dim(5.0, 'in'),
            )
        self.assertEqual(
            myObj.bbSigma,
            Coord.Box(
                Coord.Dim(7.0, 'in'),
                Coord.Dim(5.0, 'in'),
                )
            )

    def testSigma_02(self):
        """Tests PlotNode() get sigma width and depth (parent/children equal width)."""
        myObj = PlotNode.PlotNodeBbox()
        myObj.width = Coord.Dim(3, 'in')
        self.assertEqual(myObj.width, Coord.Dim(3, 'in'))
        myObj.depth = Coord.Dim(1, 'in')
        self.assertEqual(myObj.depth, Coord.Dim(1, 'in'))
        myPad = Coord.Pad(
            Coord.Dim(0.5, 'in'),   # prev
            Coord.Dim(0.5, 'in'),   # next
            Coord.Dim(0.5, 'in'),   # parent
            Coord.Dim(0.5, 'in'),   # child
            )
        myObj.bbSelfPadding = myPad
        myObj.bbSpaceChildren = Coord.Dim(0.5, 'in')
        self.assertEqual(myObj.bbSpaceChildren, Coord.Dim(0.5, 'in'))
        myObj.bbChildren = Coord.Box(
            Coord.Dim(4, 'in'),
            Coord.Dim(2.5, 'in'),
            )
        self.assertEqual(
            myObj.bbChildrenWidth,
            Coord.Dim(4, 'in'),
            )
        self.assertEqual(
            myObj.bbChildrenDepth,
            Coord.Dim(2.5, 'in'),
            )
        self.assertEqual(
            myObj.bbChildren,
            Coord.Box(
                Coord.Dim(4, 'in'),
                Coord.Dim(2.5, 'in'),
                )
            )
        self.assertEqual(
            myObj.bbSigmaWidth,
            Coord.Dim(4.0, 'in'),
            )
        self.assertEqual(
            myObj.bbSigmaDepth,
            Coord.Dim(5.0, 'in'),
            )
        self.assertEqual(
            myObj.bbSigma,
            Coord.Box(
                Coord.Dim(4.0, 'in'),
                Coord.Dim(5.0, 'in'),
                )
            )

    def testSigma_03(self):
        """Tests PlotNode() get sigma width and depth (parent is null node)."""
        myObj = PlotNode.PlotNodeBbox()
        myObj.width = None
        self.assertEqual(myObj.width, None)
        myObj.depth = None
        self.assertEqual(myObj.depth, None)
        myPad = Coord.Pad(
            Coord.Dim(0.5, 'in'),   # prev
            Coord.Dim(0.5, 'in'),   # next
            Coord.Dim(0.5, 'in'),   # parent
            Coord.Dim(0.5, 'in'),   # child
            )
        myObj.bbSelfPadding = myPad
        myObj.bbSpaceChildren = Coord.Dim(0.5, 'in')
        self.assertEqual(myObj.bbSpaceChildren, Coord.Dim(0.5, 'in'))
        myObj.bbChildren = Coord.Box(
            Coord.Dim(4, 'in'),
            Coord.Dim(2.5, 'in'),
            )
        self.assertEqual(
            myObj.bbChildrenWidth,
            Coord.Dim(4, 'in'),
            )
        self.assertEqual(
            myObj.bbChildrenDepth,
            Coord.Dim(2.5, 'in'),
            )
        self.assertEqual(
            myObj.bbChildren,
            Coord.Box(
                Coord.Dim(4, 'in'),
                Coord.Dim(2.5, 'in'),
                )
            )
        self.assertEqual(
            myObj.bbSigmaWidth,
            Coord.Dim(4.0, 'in'),
            )
        self.assertEqual(
            myObj.bbSigmaDepth,
            Coord.Dim(2.5, 'in'),
            )
        self.assertEqual(
            myObj.bbSigma,
            Coord.Box(
                Coord.Dim(4.0, 'in'),
                Coord.Dim(2.5, 'in'),
                )
            )

    def testCentre_02(self):
        """Tests PlotNode() get the centre point."""
        myObj = PlotNode.PlotNodeBbox()
        myObj.width = Coord.Dim(3, 'in')
        self.assertEqual(myObj.width, Coord.Dim(3, 'in'))
        myObj.depth = Coord.Dim(1, 'in')
        self.assertEqual(myObj.depth, Coord.Dim(1, 'in'))
        myPad = Coord.Pad(
            Coord.Dim(0.1, 'in'),   # prev
            Coord.Dim(0.3, 'in'),   # next
            Coord.Dim(0.5, 'in'),   # parent
            Coord.Dim(0.7, 'in'),   # child
            )
        myObj.bbSelfPadding = myPad
        myObj.bbSpaceChildren = Coord.Dim(0.9, 'in')
        self.assertEqual(
            myObj.plotPointCentre(
                    Coord.Pt(
                             Coord.Dim(0.0, 'in'),
                             Coord.Dim(0.0, 'in'),
                            ),
                    ),
                Coord.Pt(
                         Coord.Dim(1.6, 'in'),
                         Coord.Dim(1.0, 'in'),
                        ),
            )


class TestPlotNodeBboxWithChildren(unittest.TestCase):
    """Tests PlotNodeBbox when adding children."""
    def testBbChildren_00(self):
        """TestPlotNodeBboxWithChildren.testBbChildren_00() - three children."""
        myObj = PlotNode.PlotNodeBbox()
        myObj.width = Coord.Dim(12, 'mm')
        myObj.depth = Coord.Dim(8, 'mm')
        #print '\nTRACE myObj', myObj
        myObj.bbSelfPadding = Coord.Pad(
                Coord.Dim(1, 'mm'),   # prev
                Coord.Dim(3, 'mm'),   # next
                Coord.Dim(5, 'mm'),   # parent
                Coord.Dim(7, 'mm'),   # child
            )
        myObj.bbSpaceChildren = Coord.Dim(16, 'mm')
        self.assertEqual(True, myObj.bbChildrenWidth is None)
        self.assertEqual(True, myObj.bbChildrenDepth is None)
        self.assertEqual(0, myObj.numChildren)
        myObj.extendChildBbox(
            Coord.Box(
                Coord.Dim(15, 'mm'),
                Coord.Dim(7, 'mm'),
                )
        )
        # Child box now w:15, d:7
        self.assertEqual(1, myObj.numChildren)
        self.assertEqual(myObj.bbChildrenWidth, Coord.Dim(15, 'mm'))
        self.assertEqual(myObj.bbChildrenDepth, Coord.Dim(7, 'mm'))
        myObj.extendChildBbox(
            Coord.Box(
                Coord.Dim(31, 'mm'),
                Coord.Dim(29, 'mm'),
                )
        )
        # Child box now w:15+31=46, d:max(7,29)=29
        self.assertEqual(2, myObj.numChildren)
        self.assertEqual(myObj.bbChildrenWidth, Coord.Dim(46, 'mm'))
        self.assertEqual(myObj.bbChildrenDepth, Coord.Dim(29, 'mm'))
        myObj.extendChildBbox(
            Coord.Box(
                Coord.Dim(11, 'mm'),
                Coord.Dim(9, 'mm'),
                )
        )
        # Child box now w:46+11=57, d:max(29,9)=29
        self.assertEqual(3, myObj.numChildren)
        self.assertEqual(myObj.bbChildrenWidth, Coord.Dim(57, 'mm'))
        self.assertEqual(myObj.bbChildrenDepth, Coord.Dim(29, 'mm'))
        # bbSigma:
        # Width is 57mm as children are wider than me
        # Depth is 5 + 8 + 7 + 16 + 29 = 65mm
        #print
        #print 'myObj.bbSigma:', myObj.bbSigma
        self.assertEqual(
            myObj.bbSigma,
            Coord.Box(
                Coord.Dim(57, 'mm'),
                Coord.Dim(65, 'mm'),
                )
            )
        # Set my datum up
        myD = Coord.Pt(
            Coord.Dim(135, 'mm'),
            Coord.Dim(19, 'mm'),
        )
        # x should be 135 + 0.5 * (57-(1+12+3) + 1) = 135 + 0.5 * 41 + 1 = 156.5
        #print
        #print 'myObj.plotPointSelf:', myObj.plotPointSelf(myD)
        self.assertEqual(
            myObj.plotPointSelf(myD),
            Coord.Pt(
                Coord.Dim(156.5, 'mm'),
                Coord.Dim(24, 'mm'),
                )
            )
        #childBboxDatum
        #print
        #print 'myObj.childBboxDatum:', myObj.childBboxDatum(myD)
        self.assertEqual(
            myObj.childBboxDatum(myD),
            Coord.Pt(
                Coord.Dim(135, 'mm'),
                Coord.Dim(55, 'mm'),
                )
            )

class TestPlotNodeBboxBoxy(unittest.TestCase):
    """Tests PlotNodeBboxBoxy when adding children."""
    def setUp(self):
        self._pnbcObj = PlotNode.PlotNodeBboxBoxy()
        self._pnbcObj.width = Coord.Dim(12, 'mm')
        self._pnbcObj.depth = Coord.Dim(8, 'mm')
        #print '\nTRACE self._pnbcObj', self._pnbcObj
        self._pnbcObj.bbSelfPadding = Coord.Pad(
                Coord.Dim(1, 'mm'),   # prev
                Coord.Dim(3, 'mm'),   # next
                Coord.Dim(5, 'mm'),   # parent
                Coord.Dim(7, 'mm'),   # child
            )
        self._pnbcObj.bbSpaceChildren = Coord.Dim(16, 'mm')
        self.assertEqual(True, self._pnbcObj.bbChildrenWidth is None)
        self.assertEqual(True, self._pnbcObj.bbChildrenDepth is None)
        self.assertEqual(0, self._pnbcObj.numChildren)
        self._pnbcObj.extendChildBbox(
            Coord.Box(
                Coord.Dim(15, 'mm'),
                Coord.Dim(7, 'mm'),
                )
        )
        # Child box now w:15, d:7
        self.assertEqual(1, self._pnbcObj.numChildren)
        self.assertEqual(self._pnbcObj.bbChildrenWidth, Coord.Dim(15, 'mm'))
        self.assertEqual(self._pnbcObj.bbChildrenDepth, Coord.Dim(7, 'mm'))
        self._pnbcObj.extendChildBbox(
            Coord.Box(
                Coord.Dim(31, 'mm'),
                Coord.Dim(29, 'mm'),
                )
        )
        # Child box now w:15+31=46, d:max(7,29)=29
        self.assertEqual(2, self._pnbcObj.numChildren)
        self.assertEqual(self._pnbcObj.bbChildrenWidth, Coord.Dim(46, 'mm'))
        self.assertEqual(self._pnbcObj.bbChildrenDepth, Coord.Dim(29, 'mm'))
        self._pnbcObj.extendChildBbox(
            Coord.Box(
                Coord.Dim(11, 'mm'),
                Coord.Dim(9, 'mm'),
                )
        )
        # Child box now w:46+11=57, d:max(29,9)=29
        self.assertEqual(3, self._pnbcObj.numChildren)
        self.assertEqual(self._pnbcObj.bbChildrenWidth, Coord.Dim(57, 'mm'))
        self.assertEqual(self._pnbcObj.bbChildrenDepth, Coord.Dim(29, 'mm'))
        # Logical datum
        self._logicalDatum = Coord.Pt(
            Coord.Dim(21, 'mm'),
            Coord.Dim(180, 'mm'),
        )
    
    def tearDown(self):
        pass
    
    def test_00(self):
        """TestPlotNodeBboxBoxy.test_00() - test setUp() and tearDown()."""
        pass
    
    def test_pcLand(self):
        """TestPlotNodeBboxBoxy.test_01() - test pcLand()."""
        #print
        #print 'myObj.pcLand', self._pnbcObj.pcLand(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(22, 'mm'),
                Coord.Dim(180, 'mm')
            ),
            self._pnbcObj.pcLand(self._logicalDatum),
        )

    def test_pcStop(self):
        """TestPlotNodeBboxBoxy.test_01() - test pcStop()."""
        #print
        #print 'myObj.pcStop', self._pnbcObj.pcStop(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(22, 'mm'),
                Coord.Dim(180+5, 'mm')
            ),
            self._pnbcObj.pcStop(self._logicalDatum),
        )

    def test_cpRoll(self):
        """TestPlotNodeBboxBoxy.test_01() - test cpRoll()."""
        #print
        #print 'myObj.cpStart', self._pnbcObj.cpStart(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(22+12, 'mm'),
                Coord.Dim(180+5, 'mm')
            ),
            self._pnbcObj.cpRoll(self._logicalDatum),
        )

    def test_cpTo(self):
        """TestPlotNodeBboxBoxy.test_01() - test cpTo()."""
        #print
        #print 'myObj.cpTo', self._pnbcObj.cpTo(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(22+12, 'mm'),
                Coord.Dim(180, 'mm')
            ),
            self._pnbcObj.cpTo(self._logicalDatum),
        )

    def test_pcRoll(self):
        #parentChildTakeoffPoint
        #print
        #print 'myObj.parentChildTakeoffPoint[0]:', myObj.parentChildTakeoffPoint(myD, 0)
        self.assertEqual(
            self._pnbcObj.pcRoll(self._logicalDatum, 0),
            Coord.Pt(
                Coord.Dim(158.5, 'mm'),
                Coord.Dim(32, 'mm'),
                )
            )
        #print
        #print 'myObj.parentChildTakeoffPoint[1]:', myObj.parentChildTakeoffPoint(myD, 1)
        self.assertEqual(
            self._pnbcObj.pcRoll(self._logicalDatum, 1),
            Coord.Pt(
                Coord.Dim(162.5, 'mm'),
                Coord.Dim(32, 'mm'),
                )
            )
        #print
        #print 'myObj.parentChildTakeoffPoint[2]:', myObj.parentChildTakeoffPoint(myD, 2)
        self.assertEqual(
            self._pnbcObj.pcRoll(self._logicalDatum, 2),
            Coord.Pt(
                Coord.Dim(166.5, 'mm'),
                Coord.Dim(32, 'mm'),
                )
            )

class TestPlotNodeBboxBoxy(unittest.TestCase):
    """Tests PlotNodeBboxBoxy with no children."""
    def setUp(self):
        self._pnbcObj = PlotNode.PlotNodeBboxBoxy()
        self._pnbcObj.width = Coord.Dim(12, 'mm')
        self._pnbcObj.depth = Coord.Dim(8, 'mm')
        #print '\nTRACE self._pnbcObj', self._pnbcObj
        self._pnbcObj.bbSelfPadding = Coord.Pad(
                Coord.Dim(1, 'mm'),   # prev
                Coord.Dim(3, 'mm'),   # next
                Coord.Dim(5, 'mm'),   # parent
                Coord.Dim(7, 'mm'),   # child
            )
        self._pnbcObj.bbSpaceChildren = Coord.Dim(16, 'mm')
        self.assertEqual(True, self._pnbcObj.bbChildrenWidth is None)
        self.assertEqual(True, self._pnbcObj.bbChildrenDepth is None)
        self.assertEqual(0, self._pnbcObj.numChildren)
        # Logical datum
        self._logicalDatum = Coord.Pt(
            Coord.Dim(21, 'mm'),
            Coord.Dim(180, 'mm'),
        )
    
    def tearDown(self):
        pass
    
    def test_00(self):
        """TestPlotNodeBboxBoxy.test_00() - test setUp() and tearDown()."""
        pass
    
    def test_pcLand(self):
        """TestPlotNodeBboxBoxy.test_pcLand() - test pcLand()."""
        #print
        #print 'myObj.pcLand', self._pnbcObj.pcLand(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(22, 'mm'),
                Coord.Dim(180, 'mm')
            ),
            self._pnbcObj.pcLand(self._logicalDatum),
        )

    def test_pcStop(self):
        """TestPlotNodeBboxBoxy.test_pcStop() - test pcStop()."""
        #print
        #print 'myObj.pcStop', self._pnbcObj.pcStop(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(22, 'mm'),
                Coord.Dim(180+5, 'mm')
            ),
            self._pnbcObj.pcStop(self._logicalDatum),
        )

    def test_cpRoll(self):
        """TestPlotNodeBboxBoxy.test__pcRoll() - test cpRoll()."""
        #print
        #print 'myObj.cpStart', self._pnbcObj.cpStart(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(22+12, 'mm'),
                Coord.Dim(180+5, 'mm')
            ),
            self._pnbcObj.cpRoll(self._logicalDatum),
        )

    def test_cpTo(self):
        """TestPlotNodeBboxBoxy.test__pcTo() - test cpTo()."""
        #print
        #print 'myObj.cpTo', self._pnbcObj.cpTo(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(22+12, 'mm'),
                Coord.Dim(180, 'mm')
            ),
            self._pnbcObj.cpTo(self._logicalDatum),
        )

    def test_raise(self):
        """TestPlotNodeBboxBoxy.test_raise() - raises Exception on pcRoll()."""
        self.assertRaises(
            PlotNode.ExceptionPlotNode,
            self._pnbcObj.pcRoll,
            self._logicalDatum,
            0,
        )
    
class TestPlotNodeBboxBoxyChildren(unittest.TestCase):
    """Tests PlotNodeBboxBoxy with children."""
    def setUp(self):
        self._pnbcObj = PlotNode.PlotNodeBboxBoxy()
        self._pnbcObj.width = Coord.Dim(12, 'mm')
        self._pnbcObj.depth = Coord.Dim(8, 'mm')
        #print '\nTRACE self._pnbcObj', self._pnbcObj
        self._pnbcObj.bbSelfPadding = Coord.Pad(
                Coord.Dim(1, 'mm'),   # prev
                Coord.Dim(3, 'mm'),   # next
                Coord.Dim(5, 'mm'),   # parent
                Coord.Dim(7, 'mm'),   # child
            )
        self._pnbcObj.bbSpaceChildren = Coord.Dim(16, 'mm')
        self.assertEqual(True, self._pnbcObj.bbChildrenWidth is None)
        self.assertEqual(True, self._pnbcObj.bbChildrenDepth is None)
        self.assertEqual(0, self._pnbcObj.numChildren)
        self._pnbcObj.extendChildBbox(
            Coord.Box(
                Coord.Dim(15, 'mm'),
                Coord.Dim(7, 'mm'),
                )
        )
        # Child box now w:15, d:7
        self.assertEqual(1, self._pnbcObj.numChildren)
        self.assertEqual(self._pnbcObj.bbChildrenWidth, Coord.Dim(15, 'mm'))
        self.assertEqual(self._pnbcObj.bbChildrenDepth, Coord.Dim(7, 'mm'))
        self._pnbcObj.extendChildBbox(
            Coord.Box(
                Coord.Dim(31, 'mm'),
                Coord.Dim(29, 'mm'),
                )
        )
        # Child box now w:15+31=46, d:max(7,29)=29
        self.assertEqual(2, self._pnbcObj.numChildren)
        self.assertEqual(self._pnbcObj.bbChildrenWidth, Coord.Dim(46, 'mm'))
        self.assertEqual(self._pnbcObj.bbChildrenDepth, Coord.Dim(29, 'mm'))
        self._pnbcObj.extendChildBbox(
            Coord.Box(
                Coord.Dim(11, 'mm'),
                Coord.Dim(9, 'mm'),
                )
        )
        # Child box now w:46+11=57, d:max(29,9)=29
        self.assertEqual(3, self._pnbcObj.numChildren)
        self.assertEqual(self._pnbcObj.bbChildrenWidth, Coord.Dim(57, 'mm'))
        self.assertEqual(self._pnbcObj.bbChildrenDepth, Coord.Dim(29, 'mm'))
        # Logical datum
        self._logicalDatum = Coord.Pt(
            Coord.Dim(21, 'mm'),
            Coord.Dim(180, 'mm'),
        )
    
    def tearDown(self):
        pass
    
    def test_00(self):
        """TestPlotNodeBboxBoxyChildren.test_00() - test setUp() and tearDown()."""
        pass
    
    def test_pcLand(self):
        """TestPlotNodeBboxBoxyChildren.test_01() - test pcLand()."""
        #print
        #print 'myObj.pcLand', self._pnbcObj.pcLand(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(42.5, 'mm'),
                Coord.Dim(180, 'mm')
            ),
            self._pnbcObj.pcLand(self._logicalDatum),
        )

    def test_pcStop(self):
        """TestPlotNodeBboxBoxyChildren.test_01() - test pcStop()."""
        #print
        #print 'myObj.pcStop', self._pnbcObj.pcStop(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(42.5, 'mm'),
                Coord.Dim(180+5, 'mm')
            ),
            self._pnbcObj.pcStop(self._logicalDatum),
        )

    def test_cpRoll(self):
        """TestPlotNodeBboxBoxyChildren.test_01() - test cpRoll()."""
        #print
        #print 'myObj.cpStart', self._pnbcObj.cpStart(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(42.5+12, 'mm'),
                Coord.Dim(180+5, 'mm')
            ),
            self._pnbcObj.cpRoll(self._logicalDatum),
        )

    def test_cpTo(self):
        """TestPlotNodeBboxBoxyChildren.test_01() - test cpTo()."""
        #print
        #print 'myObj.cpTo', self._pnbcObj.cpTo(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(42.5+12, 'mm'),
                Coord.Dim(180, 'mm')
            ),
            self._pnbcObj.cpTo(self._logicalDatum),
        )

    def test_pcRoll(self):
        """TestPlotNodeBboxBoxyChildren.test_pcRoll() - test pcRoll()."""
        #parentChildTakeoffPoint
        #print
        #print 'myObj.parentChildTakeoffPoint[0]:', myObj.parentChildTakeoffPoint(myD, 0)
        self.assertEqual(
            self._pnbcObj.pcRoll(self._logicalDatum, 0),
            Coord.Pt(
                Coord.Dim(23, 'mm'),
                Coord.Dim(188, 'mm'),
                )
            )
        #print
        #print 'myObj.parentChildTakeoffPoint[1]:', myObj.parentChildTakeoffPoint(myD, 1)
        self.assertEqual(
            self._pnbcObj.pcRoll(self._logicalDatum, 1),
            Coord.Pt(
                Coord.Dim(27, 'mm'),
                Coord.Dim(188, 'mm'),
                )
            )
        #print
        #print 'myObj.parentChildTakeoffPoint[2]:', myObj.parentChildTakeoffPoint(myD, 2)
        self.assertEqual(
            self._pnbcObj.pcRoll(self._logicalDatum, 2),
            Coord.Pt(
                Coord.Dim(31, 'mm'),
                Coord.Dim(188, 'mm'),
                )
            )

    def test_pcTo(self):
        """TestPlotNodeBboxBoxyChildren.test_pcTo() - test pcTo()."""
        self.assertEqual(
            self._pnbcObj.pcTo(self._logicalDatum, 0),
            Coord.Pt(
                Coord.Dim(23, 'mm'),
                Coord.Dim(195, 'mm'),
                )
            )
        self.assertEqual(
            self._pnbcObj.pcTo(self._logicalDatum, 1),
            Coord.Pt(
                Coord.Dim(27, 'mm'),
                Coord.Dim(195, 'mm'),
                )
            )
        self.assertEqual(
            self._pnbcObj.pcTo(self._logicalDatum, 2),
            Coord.Pt(
                Coord.Dim(31, 'mm'),
                Coord.Dim(195, 'mm'),
                )
            )

    def test_raise(self):
        """TestPlotNodeBboxBoxyChildren.test_raise() - raises Exception on pcRoll()."""
        self.assertRaises(
            PlotNode.ExceptionPlotNode,
            self._pnbcObj.pcRoll,
            self._logicalDatum,
            -1,
        )
        self.assertRaises(
            PlotNode.ExceptionPlotNode,
            self._pnbcObj.pcRoll,
            self._logicalDatum,
            3,
        )
    
class TestPlotNodeBboxRoundy(unittest.TestCase):
    """Tests PlotNodeBboxRoundy specific stuff."""
    def setUp(self):
        self._pnbcObj = PlotNode.PlotNodeBboxRoundy()
        self._pnbcObj.width = Coord.Dim(12, 'mm')
        self._pnbcObj.depth = Coord.Dim(8, 'mm')
        #print '\nTRACE self._pnbcObj', self._pnbcObj
        self._pnbcObj.bbSelfPadding = Coord.Pad(
                Coord.Dim(1, 'mm'),   # prev
                Coord.Dim(3, 'mm'),   # next
                Coord.Dim(5, 'mm'),   # parent
                Coord.Dim(7, 'mm'),   # child
            )
        self._pnbcObj.bbSpaceChildren = Coord.Dim(16, 'mm')
        self.assertEqual(True, self._pnbcObj.bbChildrenWidth is None)
        self.assertEqual(True, self._pnbcObj.bbChildrenDepth is None)
        self.assertEqual(0, self._pnbcObj.numChildren)
        # Logical datum
        self._logicalDatum = Coord.Pt(
            Coord.Dim(21, 'mm'),
            Coord.Dim(180, 'mm'),
        )
    
    def tearDown(self):
        pass
    
    def test_00(self):
        """TestPlotNodeBboxRoundy.test_00() - test setUp() and tearDown()."""
        pass
    
    def test_pcLand(self):
        """TestPlotNodeBboxRoundy.test_01() - test pcLand()."""
        #print
        #print 'myObj.pcLand', self._pnbcObj.pcLand(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(28, 'mm'),
                Coord.Dim(189, 'mm')
            ),
            self._pnbcObj.pcLand(self._logicalDatum),
        )

    def test_pcStop(self):
        """TestPlotNodeBboxRoundy.test_01() - test pcStop()."""
        #print
        #print 'myObj.pcStop', self._pnbcObj.pcStop(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(28, 'mm'),
                Coord.Dim(189, 'mm')
            ),
            self._pnbcObj.pcStop(self._logicalDatum),
        )

    def test_cpRoll(self):
        """TestPlotNodeBboxRoundy.test_01() - test cpRoll()."""
        #print
        #print 'myObj.cpStart', self._pnbcObj.cpStart(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(28, 'mm'),
                Coord.Dim(189, 'mm')
            ),
            self._pnbcObj.cpRoll(self._logicalDatum),
        )

    def test_cpTo(self):
        """TestPlotNodeBboxRoundy.test_01() - test cpTo()."""
        #print
        #print 'myObj.cpTo', self._pnbcObj.cpTo(self._logicalDatum)
        self.assertEqual(
            Coord.Pt(
                Coord.Dim(28, 'mm'),
                Coord.Dim(189, 'mm')
            ),
            self._pnbcObj.cpTo(self._logicalDatum),
        )

class Special(unittest.TestCase):
    pass

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotNodeCtor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotNodeSetting))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotNodeBboxWithChildren))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotNodeBboxBoxy))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotNodeBboxBoxyChildren))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlotNodeBboxRoundy))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Special))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    print \
"""TestPlotNode.py - Tests the PlotNode module.
Usage:
python TestPlotNode.py [-hl: --help]

Options:
-h, --help ~ Help (this screen) and exit.
-l:        ~ set the logging level higher is quieter.
             Default is 30 (WARNING) e.g.:
                CRITICAL    50
                ERROR       40
                WARNING     30
                INFO        20
                DEBUG       10
                NOTSET      0
"""

def main():
    print 'TestPlotNode.py script version "%s", dated %s' % (__version__, __date__)
    print 'Author: %s' % __author__
    print __rights__
    print
    import getopt
    import time
    print 'Command line:'
    print ' '.join(sys.argv)
    print
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError, myErr:
        usage()
        print 'ERROR: Invalid option: %s' % str(myErr)
        sys.exit(1)
    logLevel = logging.WARNING
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o == '-l':
            logLevel = int(a)
    if len(args) != 0:
        usage()
        print 'ERROR: Wrong number of arguments[%d]!' % len(args)
        sys.exit(1)
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    unitTest()
    clkExec = time.clock() - clkStart
    print 'CPU time = %8.3f (S)' % clkExec
    print 'Bye, bye!'

if __name__ == "__main__":
    main()
