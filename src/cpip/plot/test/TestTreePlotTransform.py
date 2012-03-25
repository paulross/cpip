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
$ python c:/Python26/Lib/site-packages/coverage.py -x test/TestTreePlotTransform.py
"""

import os
import sys
import logging
import math

#sys.path.append(os.path.join(os.pardir + os.sep))
from cpip.plot import TreePlotTransform, Coord

######################
# Section: Unit tests.
######################
import unittest

class TestTreePlotTransformSimple(unittest.TestCase):
    """Tests the TreePlotTransform() class constructor."""

    def testCtorMt(self):
        """TreePlotTransform() constructor defaults."""
        myO = TreePlotTransform.TreePlotTransform(Coord.zeroBaseUnitsBox())
        self.assertEqual(myO.rootPos, 'top')
        self.assertEqual(myO.sweepDir, '-')

    def testCtorFail_RootPos(self):
        """TreePlotTransform() constructor rootPos out of range."""
        self.assertRaises(
            TreePlotTransform.ExceptionTreePlotTransformRangeCtor,
            TreePlotTransform.TreePlotTransform,
            Coord.zeroBaseUnitsBox(),
            rootPos='whatever')

    def testCtorFail_SweepDir(self):
        """TreePlotTransform() constructor sweepDir out of range."""
        self.assertRaises(
            TreePlotTransform.ExceptionTreePlotTransformRangeCtor,
            TreePlotTransform.TreePlotTransform,
            Coord.zeroBaseUnitsBox(),
            sweepDir='whatever')

class TestTreePlotTransformCanvas(unittest.TestCase):
    """Tests the TreePlotTransform() canvasP()."""

    def setUp(self):
        self._boxDefault = Coord.Box(
            Coord.Dim(300, None),
            Coord.Dim(500, None),
            )

    def tearDown(self):
        pass
    
    def test(self):
        """TestTreePlotTransformCanvas setUp() and tearDown()."""
        pass
    
    def testCanvasP_top(self):
        """TestTreePlotTransformCanvas.canvasP(): top."""
        myO = TreePlotTransform.TreePlotTransform(self._boxDefault, rootPos='top')
        expValue = Coord.Box(
            Coord.Dim(300, None),
            Coord.Dim(500, None),
            )
        self.assertEqual(
            myO.canvasP(),
            expValue,
            )

    def testCanvasP_left(self):
        """TestTreePlotTransformCanvas.canvasP(): left."""
        myO = TreePlotTransform.TreePlotTransform(self._boxDefault, rootPos='left')
        expValue = Coord.Box(
            Coord.Dim(500, None),
            Coord.Dim(300, None),
            )
        self.assertEqual(
            myO.canvasP(),
            expValue,
            )

    def testCanvasP_bottom(self):
        """TestTreePlotTransformCanvas.canvasP(): bottom."""
        myO = TreePlotTransform.TreePlotTransform(self._boxDefault, rootPos='bottom')
        expValue = Coord.Box(
            Coord.Dim(300, None),
            Coord.Dim(500, None),
            )
        self.assertEqual(
            myO.canvasP(),
            expValue,
            )

    def testCanvasP_right(self):
        """TestTreePlotTransformCanvas.canvasP(): right."""
        myO = TreePlotTransform.TreePlotTransform(self._boxDefault, rootPos='right')
        expValue = Coord.Box(
            Coord.Dim(500, None),
            Coord.Dim(300, None),
            )
        self.assertEqual(
            myO.canvasP(),
            expValue,
            )

class TestTreePlotTransformBoxP(unittest.TestCase):
    """Tests the TreePlotTransform.boxP()."""

    def setUp(self):
        self._canvas = Coord.Box(
            Coord.Dim(300, None),
            Coord.Dim(500, None),
            )
        self._box = Coord.Box(
            Coord.Dim(80, None),
            Coord.Dim(20, None),
            ) 

    def tearDown(self):
        pass
    
    def test(self):
        """TestTreePlotTransformBoxP setUp() and tearDown()."""
        pass

    def testIncWD_top(self):
        """TestTreePlotTransformBoxP.boxP(): top."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='top')
        self.assertEqual(
            myObj.boxP(self._box),
            Coord.Box(
                Coord.Dim(80, None),
                Coord.Dim(20, None),
                ),
            )

    def testIncWD_left(self):
        """TestTreePlotTransformBoxP.boxP(): left."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='left')
        self.assertEqual(
            myObj.boxP(self._box),
            Coord.Box(
                Coord.Dim(20, None),
                Coord.Dim(80, None),
                ),
            )

    def testIncWD_bottom(self):
        """TestTreePlotTransformBoxP.boxP(): bottom."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='bottom')
        self.assertEqual(
            myObj.boxP(self._box),
            Coord.Box(
                Coord.Dim(80, None),
                Coord.Dim(20, None),
                ),
            )

    def testIncWD_right(self):
        """TestTreePlotTransformBoxP.boxP(): right."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='right')
        self.assertEqual(
            myObj.boxP(self._box),
            Coord.Box(
                Coord.Dim(20, None),
                Coord.Dim(80, None),
                ),
            )

class TestTreePlotTransformBoxDatumP(unittest.TestCase):
    """Tests the TreePlotTransform.boxDatumP()."""

    def setUp(self):
        self._canvas = Coord.Box(
            Coord.Dim(300, None),
            Coord.Dim(500, None),
            )
        self._box = Coord.Box(
            Coord.Dim(80, None),
            Coord.Dim(20, None),
            ) 
        self._pt = Coord.Pt(
            Coord.Dim(17, None),
            Coord.Dim(29, None),
            ) 

    def tearDown(self):
        pass
    
    def test(self):
        """TestTreePlotTransformBoxDatumP setUp() and tearDown()."""
        pass

    def testIncWD_top(self):
        """TestTreePlotTransformBoxDatumP.boxDatumP(): top."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='top')
        self.assertEqual(
            myObj.boxDatumP(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(17, None),
                Coord.Dim(29, None),
            ),
        )

    def testIncWD_left(self):
        """TestTreePlotTransformBoxDatumP.boxDatumP(): left."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='left')
        self.assertEqual(
            myObj.boxDatumP(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(29, None),
                Coord.Dim(203, None),
            ),
        )

    def testIncWD_bottom(self):
        """TestTreePlotTransformBoxDatumP.boxDatumP(): bottom."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='bottom')
        self.assertEqual(
            myObj.boxDatumP(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(203, None),
                Coord.Dim(451, None),
            ),
        )

    def testIncWD_right(self):
        """TestTreePlotTransformBoxDatumP.boxDatumP(): right."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='right')
        self.assertEqual(
            myObj.boxDatumP(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(451, None),
                Coord.Dim(17, None),
            ),
        )

class TestTreePlotTransformPt(unittest.TestCase):
    """Tests the TreePlotTransform.pt()."""

    def setUp(self):
        self._canvas = Coord.Box(
            Coord.Dim(300, None),
            Coord.Dim(500, None),
            )
        self._pt = Coord.Pt(
            Coord.Dim(17, None),
            Coord.Dim(29, None),
            ) 

    def tearDown(self):
        pass
    
    def test(self):
        """TestTreePlotTransformPt setUp() and tearDown()."""
        pass

    def testPt_top(self):
        """TestTreePlotTransformPt.pt(): top."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='top')
        self.assertEqual(
            myObj.pt(self._pt),
            Coord.Pt(
                Coord.Dim(17, None),
                Coord.Dim(29, None),
            ),
        )

    def testPt_left(self):
        """TestTreePlotTransformPt.pt(): left."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='left')
        self.assertEqual(
            myObj.pt(self._pt),
            Coord.Pt(
                Coord.Dim(29, None),
                Coord.Dim(300-17, None),
            ),
        )

    def testPt_bottom(self):
        """TestTreePlotTransformPt.pt(): bottom."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='bottom')
        self.assertEqual(
            myObj.pt(self._pt),
            Coord.Pt(
                Coord.Dim(300-17, None),
                Coord.Dim(500-29, None),
            ),
        )

    def testPt_right(self):
        """TestTreePlotTransformPt.pt(): right."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='right')
        self.assertEqual(
            myObj.pt(self._pt),
            Coord.Pt(
                Coord.Dim(500-29, None),
                Coord.Dim(17, None),
            ),
        )

#incPhysicalChildPos
class TestTreePlotTransformIncPhysicalChildPos(unittest.TestCase):
    """Tests the TreePlotTransform.incPhysicalChildPos()."""

    def setUp(self):
        self._canvas = Coord.Box(
            Coord.Dim(300, None),
            Coord.Dim(800, None),
            )
        self._pt = Coord.Pt(
            Coord.Dim(400, None),
            Coord.Dim(250, None),
            )
        self._childIncS = [
            Coord.Dim(36, None),
            Coord.Dim(101, None),
            Coord.Dim(74, None),
            ] 

    def tearDown(self):
        pass
    
    def test(self):
        """TestTreePlotTransform.incPhysicalChildPos(): setUp() and tearDown()."""
        pass

    def test_top_neg(self):
        """TestTreePlotTransform.incPhysicalChildPos(): top, -"""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='top', sweepDir='-')
        childPhysicalPt = self._pt
        # Starting point
        self.assertEqual(myObj.pt(self._pt), childPhysicalPt)
        # First increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[0])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(400+36, None),
                Coord.Dim(250, None),
            )
        )
        # Second increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[1])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(400+36+101, None),
                Coord.Dim(250, None),
            )
        )
        # Third increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[2])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(400+36+101+74, None),
                Coord.Dim(250, None),
            )
        )

    def test_top_pos(self):
        """TestTreePlotTransform.incPhysicalChildPos(): top, +"""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='top', sweepDir='+')
        childPhysicalPt = self._pt
        # Starting point
        self.assertEqual(myObj.pt(self._pt), childPhysicalPt)
        # First increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[0])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(400-36, None),
                Coord.Dim(250, None),
            )
        )
        # Second increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[1])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(400-36-101, None),
                Coord.Dim(250, None),
            )
        )
        # Third increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[2])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(400-36-101-74, None),
                Coord.Dim(250, None),
            )
        )

    def test_left_neg(self):
        """TestTreePlotTransform.incPhysicalChildPos(): left, -"""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='left', sweepDir='-')
        childPhysicalPt = Coord.Pt(
                Coord.Dim(250, None),
                Coord.Dim(-100, None),
            )
        #print myObj.pt(self._pt)
        # Starting point
        self.assertEqual(myObj.pt(self._pt), childPhysicalPt)
        #return
        # First increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[0])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(250, None),
                Coord.Dim(-100-36, None),
            )
        )
        # Second increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[1])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(250, None),
                Coord.Dim(-100-36-101, None),
            )
        )
        # Third increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[2])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(250, None),
                Coord.Dim(-100-36-101-74, None),
            )
        )

    def test_left_pos(self):
        """TestTreePlotTransform.incPhysicalChildPos(): left, +"""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='left', sweepDir='+')
        childPhysicalPt = Coord.Pt(
                Coord.Dim(250, None),
                Coord.Dim(-100, None),
            )
        #print myObj.pt(self._pt)
        # Starting point
        self.assertEqual(myObj.pt(self._pt), childPhysicalPt)
        #return
        # First increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[0])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(250, None),
                Coord.Dim(-100+36, None),
            )
        )
        # Second increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[1])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(250, None),
                Coord.Dim(-100+36+101, None),
            )
        )
        # Third increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[2])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(250, None),
                Coord.Dim(-100+36+101+74, None),
            )
        )

    def test_bottom_neg(self):
        """TestTreePlotTransform.incPhysicalChildPos(): bottom, -"""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='bottom', sweepDir='-')
        childPhysicalPt = Coord.Pt(
                Coord.Dim(-100, None),
                Coord.Dim(550, None),
            )
        #print myObj.pt(self._pt)
        # Starting point
        self.assertEqual(myObj.pt(self._pt), childPhysicalPt)
        #return
        # First increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[0])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(-100-36, None),
                Coord.Dim(550, None),
            )
        )
        # Second increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[1])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(-100-36-101, None),
                Coord.Dim(550, None),
            )
        )
        # Third increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[2])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(-100-36-101-74, None),
                Coord.Dim(550, None),
            )
        )

    def test_bottom_pos(self):
        """TestTreePlotTransform.incPhysicalChildPos(): bottom, +"""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='bottom', sweepDir='+')
        childPhysicalPt = Coord.Pt(
                Coord.Dim(-100, None),
                Coord.Dim(550, None),
            )
        #print myObj.pt(self._pt)
        # Starting point
        self.assertEqual(myObj.pt(self._pt), childPhysicalPt)
        #return
        # First increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[0])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(-100+36, None),
                Coord.Dim(550, None),
            )
        )
        # Second increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[1])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(-100+36+101, None),
                Coord.Dim(550, None),
            )
        )
        # Third increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[2])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(-100+36+101+74, None),
                Coord.Dim(550, None),
            )
        )

    def test_right_neg(self):
        """TestTreePlotTransform.incPhysicalChildPos(): right, -"""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='right', sweepDir='-')
        childPhysicalPt = Coord.Pt(
                Coord.Dim(550, None),
                Coord.Dim(400, None),
            )
        #print myObj.pt(self._pt)
        # Starting point
        self.assertEqual(myObj.pt(self._pt), childPhysicalPt)
        #return
        # First increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[0])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(550, None),
                Coord.Dim(400+36, None),
            )
        )
        # Second increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[1])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(550, None),
                Coord.Dim(400+36+101, None),
            )
        )
        # Third increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[2])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(550, None),
                Coord.Dim(400+36+101+74, None),
            )
        )

    def test_right_pos(self):
        """TestTreePlotTransform.incPhysicalChildPos(): right, +"""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='right', sweepDir='+')
        childPhysicalPt = Coord.Pt(
                Coord.Dim(550, None),
                Coord.Dim(400, None),
            )
        #print myObj.pt(self._pt)
        # Starting point
        self.assertEqual(myObj.pt(self._pt), childPhysicalPt)
        #return
        # First increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[0])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(550, None),
                Coord.Dim(400-36, None),
            )
        )
        # Second increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[1])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(550, None),
                Coord.Dim(400-36-101, None),
            )
        )
        # Third increment
        childPhysicalPt = myObj.incPhysicalChildPos(childPhysicalPt, self._childIncS[2])
        self.assertEqual(
            childPhysicalPt,
            Coord.Pt(
                Coord.Dim(550, None),
                Coord.Dim(400-36-101-74, None),
            )
        )

class TestTreePlotTransformTDC(unittest.TestCase):
    """Tests the TreePlotTransform.tdcL() and TreePlotTransform.tdcP()."""

    def setUp(self):
        self._canvas = Coord.Box(
            Coord.Dim(300, None),
            Coord.Dim(500, None),
            )
        self._box = Coord.Box(
            Coord.Dim(80, None),
            Coord.Dim(20, None),
            ) 
        self._pt = Coord.Pt(
            Coord.Dim(17, None),
            Coord.Dim(29, None),
            ) 

    def tearDown(self):
        pass
    
    def test(self):
        """TestTreePlotTransformBoxDatumP setUp() and tearDown()."""
        pass

    def testIncWD_top(self):
        """TreePlotTransform.tdcL()/.tdcP(): top."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='top')
        self.assertEqual(
            myObj.tdcL(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(57, None),
                Coord.Dim(29, None),
            ),
        )
        self.assertEqual(
            myObj.tdcP(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(57, None),
                Coord.Dim(29, None),
            ),
        )

    def testIncWD_left(self):
        """TreePlotTransform.tdcL()/.tdcP(): left."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='left')
        self.assertEqual(
            myObj.tdcL(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(97, None),
                Coord.Dim(39, None),
            ),
        )
        self.assertEqual(
            myObj.tdcP(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(39, None),
                Coord.Dim(203, None),
            ),
        )

    def testIncWD_bottom(self):
        """TreePlotTransform.tdcL()/.tdcP(): bottom."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='bottom')
        self.assertEqual(
            myObj.tdcL(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(57, None),
                Coord.Dim(49, None),
            ),
        )
        self.assertEqual(
            myObj.tdcP(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(243, None),
                Coord.Dim(451, None),
            ),
        )

    def testIncWD_right(self):
        """TreePlotTransform.tdcL()/.tdcP(): right."""
        myObj = TreePlotTransform.TreePlotTransform(self._canvas, rootPos='right')
        self.assertEqual(
            myObj.tdcL(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(17, None),
                Coord.Dim(39, None),
            ),
        )
        self.assertEqual(
            myObj.tdcP(self._pt, self._box),
            Coord.Pt(
                Coord.Dim(461, None),
                Coord.Dim(17, None),
            ),
        )

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTreePlotTransformSimple)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTreePlotTransformCanvas))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTreePlotTransformBoxP))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTreePlotTransformBoxDatumP))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTreePlotTransformPt))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTreePlotTransformIncPhysicalChildPos))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTreePlotTransformTDC))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    print("""TestTreePlotTransform.py - Tests the TreePlotTransform module.
Usage:
python TestTreePlotTransform.py [-hl: --help]

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
""")

def main():
    print('TestTreePlotTransform.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
    print(__rights__)
    print()
    import getopt
    import time
    print('Command line:')
    print(' '.join(sys.argv))
    print()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError as myErr:
        usage()
        print('ERROR: Invalid option: %s' % str(myErr))
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
        print('ERROR: Wrong number of arguments[%d]!' % len(args))
        sys.exit(1)
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    unitTest()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
