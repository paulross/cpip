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
import sys
import time
import logging

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from cpip.util import XmlWrite
from cpip.plot import SVGWriter, Coord

######################
# Section: Unit tests.
######################
import unittest

class TestSVGWriter(unittest.TestCase):
    """Tests SVGWriter."""
    def test_00(self):
        """TestSVGWriter.test_00(): construction."""
        myF = StringIO.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(100, 'mm'),
            Coord.Dim(20, 'mm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort):
            pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="20mm" version="1.1" width="100mm" xmlns="http://www.w3.org/2000/svg"/>\n""")
        
    def test_01(self):
        """TestSVGlWriter.test_01(): <desc> and four rectangles.
        From second example in http://www.w3.org/TR/2003/REC-SVG11-20030114/struct.html#NewDocumentOverview"""
        myF = StringIO.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(5, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Four separate rectangles')
            myPt = Coord.Pt(Coord.Dim(0.5, 'cm'), Coord.Dim(0.5, 'cm'))
            myBx = Coord.Box(Coord.Dim(2.0, 'cm'), Coord.Dim(1.0, 'cm'))
            with SVGWriter.SVGRect(xS, myPt, myBx):
                pass
            myPt = Coord.Pt(Coord.Dim(0.5, 'cm'), Coord.Dim(2.0, 'cm'))
            myBx = Coord.Box(Coord.Dim(1.0, 'cm'), Coord.Dim(1.5, 'cm'))
            with SVGWriter.SVGRect(xS, myPt, myBx):
                pass
            myPt = Coord.Pt(Coord.Dim(3.0, 'cm'), Coord.Dim(0.5, 'cm'))
            myBx = Coord.Box(Coord.Dim(1.5, 'cm'), Coord.Dim(2.0, 'cm'))
            with SVGWriter.SVGRect(xS, myPt, myBx):
                pass
            myPt = Coord.Pt(Coord.Dim(3.5, 'cm'), Coord.Dim(3.0, 'cm'))
            myBx = Coord.Box(Coord.Dim(1.0, 'cm'), Coord.Dim(0.5, 'cm'))
            with SVGWriter.SVGRect(xS, myPt, myBx):
                pass
            myPt = Coord.Pt(Coord.Dim(0.01, 'cm'), Coord.Dim(0.01, 'cm'))
            myBx = Coord.Box(Coord.Dim(4.98, 'cm'), Coord.Dim(3.98, 'cm'))
            with SVGWriter.SVGRect(
                    xS,
                    myPt,
                    myBx,
                    attrs= {
                            'fill'          : "none",
                            'stroke'        : "blue",
                            'stroke-width'  : ".02cm",
                        }
                ):
                pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4cm" version="1.1" width="5cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Four separate rectangles</desc>
  <rect height="1.0cm" width="2.0cm" x="0.5cm" y="0.5cm"/>
  <rect height="1.5cm" width="1.0cm" x="0.5cm" y="2.0cm"/>
  <rect height="2.0cm" width="1.5cm" x="3.0cm" y="0.5cm"/>
  <rect height="0.5cm" width="1.0cm" x="3.5cm" y="3.0cm"/>
  <rect fill="none" height="3.98cm" stroke="blue" stroke-width=".02cm" width="4.98cm" x="0.01cm" y="0.01cm"/>
</svg>
""")
       
    def test_02(self):
        """TestSVGlWriter.test_02(): a circle.
        From http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#CircleElement"""
        myF = StringIO.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Example circle01 - circle filled with red and stroked with blue')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(1198), Coord.baseUnitsDim(398))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
            myPt = Coord.Pt(Coord.baseUnitsDim(600), Coord.baseUnitsDim(200))
            myRad = Coord.baseUnitsDim(100)
            with SVGWriter.SVGCircle(xS, myPt, myRad, {'fill':"red", 'stroke':"blue",'stroke-width':"10"}):
                pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4cm" version="1.1" width="12cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example circle01 - circle filled with red and stroked with blue</desc>
  <rect fill="none" height="398px" stroke="blue" stroke-width="2" width="1198px" x="1px" y="1px"/>
  <circle cx="600px" cy="200px" fill="red" r="100px" stroke="blue" stroke-width="10"/>
</svg>
""")

    def test_03(self):
        """TestSVGlWriter.test_03(): an elipse.
        Based on http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#EllipseElement"""
        myF = StringIO.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Example ellipse01 - examples of ellipses')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(1198), Coord.baseUnitsDim(398))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
            myPt = Coord.Pt(Coord.baseUnitsDim(600), Coord.baseUnitsDim(200))
            myRadX = Coord.baseUnitsDim(250)
            myRadY = Coord.baseUnitsDim(100)
            with SVGWriter.SVGElipse(xS, myPt, myRadX, myRadY, {'fill':"red", 'stroke':"blue",'stroke-width':"10"}):
                pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4cm" version="1.1" width="12cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example ellipse01 - examples of ellipses</desc>
  <rect fill="none" height="398px" stroke="blue" stroke-width="2" width="1198px" x="1px" y="1px"/>
  <elipse cx="600px" cy="200px" fill="red" rx="250px" ry="100px" stroke="blue" stroke-width="10"/>
</svg>
""")

    def test_04(self):
        """TestSVGlWriter.test_04(): a line.
        Based on http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#LineElement"""
        myF = StringIO.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Example line01 - lines expressed in user coordinates')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(1198), Coord.baseUnitsDim(398))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
            # Make a group
            with SVGWriter.SVGGroup(xS, {'stroke' : 'green'}):
                with SVGWriter.SVGLine(
                        xS,
                        Coord.Pt(Coord.baseUnitsDim(100), Coord.baseUnitsDim(300)), 
                        Coord.Pt(Coord.baseUnitsDim(300), Coord.baseUnitsDim(100)), 
                        {'stroke-width' : "5"}
                    ):
                    pass
                with SVGWriter.SVGLine(
                        xS,
                        Coord.Pt(Coord.baseUnitsDim(300), Coord.baseUnitsDim(300)), 
                        Coord.Pt(Coord.baseUnitsDim(500), Coord.baseUnitsDim(100)), 
                        {'stroke-width' : "10"}
                    ):
                    pass
                with SVGWriter.SVGLine(
                        xS,
                        Coord.Pt(Coord.baseUnitsDim(500), Coord.baseUnitsDim(300)), 
                        Coord.Pt(Coord.baseUnitsDim(700), Coord.baseUnitsDim(100)), 
                        {'stroke-width' : "15"}
                    ):
                    pass
                with SVGWriter.SVGLine(
                        xS,
                        Coord.Pt(Coord.baseUnitsDim(700), Coord.baseUnitsDim(300)), 
                        Coord.Pt(Coord.baseUnitsDim(900), Coord.baseUnitsDim(100)), 
                        {'stroke-width' : "20"}
                    ):
                    pass
                with SVGWriter.SVGLine(
                        xS,
                        Coord.Pt(Coord.baseUnitsDim(900), Coord.baseUnitsDim(300)), 
                        Coord.Pt(Coord.baseUnitsDim(1100), Coord.baseUnitsDim(100)), 
                        {'stroke-width' : "25"}
                    ):
                    pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4cm" version="1.1" width="12cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example line01 - lines expressed in user coordinates</desc>
  <rect fill="none" height="398px" stroke="blue" stroke-width="2" width="1198px" x="1px" y="1px"/>
  <g stroke="green">
    <line stroke-width="5" x1="100px" x2="300px" y1="300px" y2="100px"/>
    <line stroke-width="10" x1="300px" x2="500px" y1="300px" y2="100px"/>
    <line stroke-width="15" x1="500px" x2="700px" y1="300px" y2="100px"/>
    <line stroke-width="20" x1="700px" x2="900px" y1="300px" y2="100px"/>
    <line stroke-width="25" x1="900px" x2="1100px" y1="300px" y2="100px"/>
  </g>
</svg>
""")

    def test_05(self):
        """TestSVGlWriter.test_05(): a polyline.
        Based on http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#PolylineElement"""
        myF = StringIO.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort, {'viewBox' : "0 0 1200 400"}) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Example line01 - lines expressed in user coordinates')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(1198), Coord.baseUnitsDim(398))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
            # Make a group
            with SVGWriter.SVGPolyline(
                    xS,
                    [
                        Coord.Pt(Coord.baseUnitsDim(50), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(150), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(150), Coord.baseUnitsDim(325)),
                        Coord.Pt(Coord.baseUnitsDim(250), Coord.baseUnitsDim(325)),
                        Coord.Pt(Coord.baseUnitsDim(250), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(350), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(350), Coord.baseUnitsDim(250)),
                        Coord.Pt(Coord.baseUnitsDim(450), Coord.baseUnitsDim(250)),
                        Coord.Pt(Coord.baseUnitsDim(450), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(550), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(550), Coord.baseUnitsDim(175)),
                        Coord.Pt(Coord.baseUnitsDim(650), Coord.baseUnitsDim(175)),
                        Coord.Pt(Coord.baseUnitsDim(650), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(750), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(750), Coord.baseUnitsDim(100)),
                        Coord.Pt(Coord.baseUnitsDim(850), Coord.baseUnitsDim(100)),
                        Coord.Pt(Coord.baseUnitsDim(850), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(950), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(950), Coord.baseUnitsDim(25)),
                        Coord.Pt(Coord.baseUnitsDim(1050), Coord.baseUnitsDim(25)),
                        Coord.Pt(Coord.baseUnitsDim(1050), Coord.baseUnitsDim(375)),
                        Coord.Pt(Coord.baseUnitsDim(1150), Coord.baseUnitsDim(375)),
                    ],
                    {'fill' : 'none', 'stroke' : 'blue', 'stroke-width' : "5"}
                ):
                pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4cm" version="1.1" viewBox="0 0 1200 400" width="12cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example line01 - lines expressed in user coordinates</desc>
  <rect fill="none" height="398px" stroke="blue" stroke-width="2" width="1198px" x="1px" y="1px"/>
  <polyline fill="none" points="50,375 150,375 150,325 250,325 250,375 350,375 350,250 450,250 450,375 550,375 550,175 650,175 650,375 750,375 750,100 850,100 850,375 950,375 950,25 1050,25 1050,375 1150,375" stroke="blue" stroke-width="5"/>
</svg>
""")
        
    def test_06(self):
        """TestSVGlWriter.test_06(): a polygon.
        Based on http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#PolygonElement"""
        myF = StringIO.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort, {'viewBox' : "0 0 1200 400"}) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters('Example line01 - lines expressed in user coordinates')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(1198), Coord.baseUnitsDim(398))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
            # Make a group
            with SVGWriter.SVGPolygon(
                    xS,
                    [
                        Coord.Pt(Coord.baseUnitsDim(350), Coord.baseUnitsDim(75)),
                        Coord.Pt(Coord.baseUnitsDim(379), Coord.baseUnitsDim(161)),
                        Coord.Pt(Coord.baseUnitsDim(469), Coord.baseUnitsDim(161)),
                        Coord.Pt(Coord.baseUnitsDim(397), Coord.baseUnitsDim(215)),
                        Coord.Pt(Coord.baseUnitsDim(423), Coord.baseUnitsDim(301)),
                        Coord.Pt(Coord.baseUnitsDim(350), Coord.baseUnitsDim(250)),
                        Coord.Pt(Coord.baseUnitsDim(277), Coord.baseUnitsDim(301)),
                        Coord.Pt(Coord.baseUnitsDim(303), Coord.baseUnitsDim(215)),
                        Coord.Pt(Coord.baseUnitsDim(231), Coord.baseUnitsDim(161)),
                        Coord.Pt(Coord.baseUnitsDim(321), Coord.baseUnitsDim(161)),
                    ],
                    {'fill' : 'red', 'stroke' : 'blue', 'stroke-width' : "10"}
                ):
                pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4cm" version="1.1" viewBox="0 0 1200 400" width="12cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example line01 - lines expressed in user coordinates</desc>
  <rect fill="none" height="398px" stroke="blue" stroke-width="2" width="1198px" x="1px" y="1px"/>
  <polygon fill="red" points="350,75 379,161 469,161 397,215 423,301 350,250 277,301 303,215 231,161 321,161" stroke="blue" stroke-width="10"/>
</svg>
""")

    def test_07(self):
        """TestSVGlWriter.test_07(): text.
        Based on http://www.w3.org/TR/2003/REC-SVG11-20030114/text.html#TextElement"""
        myF = StringIO.StringIO()
        myViewPort = Coord.Box(
            Coord.Dim(12, 'cm'),
            Coord.Dim(4, 'cm'),
        )
        with SVGWriter.SVGWriter(myF, myViewPort, {'viewBox' : "0 0 1000 300"}) as xS:
            with XmlWrite.Element(xS, 'desc'):
                xS.characters("Example text01 - 'Hello, out there' in blue")
            myPt = Coord.Pt(Coord.baseUnitsDim(250), Coord.baseUnitsDim(150))
            with SVGWriter.SVGText(xS, myPt, "Verdans", 55, {'fill' : "blue"}):
                xS.characters('Hello, out there')
            #xS.comment(" Show outline of canvas using 'rect' element ")
            myPt = Coord.Pt(Coord.baseUnitsDim(1), Coord.baseUnitsDim(1))
            myBx = Coord.Box(Coord.baseUnitsDim(998), Coord.baseUnitsDim(298))
            with SVGWriter.SVGRect(xS, myPt, myBx, {'fill':"none", 'stroke':"blue",'stroke-width':"2"}):
                pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="4cm" version="1.1" viewBox="0 0 1000 300" width="12cm" xmlns="http://www.w3.org/2000/svg">
  <desc>Example text01 - &apos;Hello, out there&apos; in blue</desc>
  <text fill="blue" font-family="Verdans" font-size="55" x="250px" y="150px">Hello, out there</text>
  <rect fill="none" height="298px" stroke="blue" stroke-width="2" width="998px" x="1px" y="1px"/>
</svg>
""")

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSVGWriter))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print \
"""TestSVGWriter.py - A module that tests StrTree module.
Usage:
python TestSVGWriter.py [-lh --help]

Options:
-h, --help  Help (this screen) and exit

Options (debug):
-l:         Set the logging level higher is quieter.
             Default is 20 (INFO) e.g.:
                CRITICAL    50
                ERROR       40
                WARNING     30
                INFO        20
                DEBUG       10
                NOTSET      0
"""

def main():
    """Invoke unit test code."""
    print 'TestSVGWriter.py script version "%s", dated %s' % (__version__, __date__)
    print 'Author: %s' % __author__
    print __rights__
    print
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError:
        usage()
        print 'ERROR: Invalid options!'
        sys.exit(1)
    logLevel = logging.INFO
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o == '-l':
            logLevel = int(a)
    if len(args) != 0:
        usage()
        print 'ERROR: Wrong number of arguments!'
        sys.exit(1)
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    clkStart = time.clock()
    unitTest()
    clkExec = time.clock() - clkStart
    print 'CPU time = %8.3f (S)' % clkExec
    print 'Bye, bye!'

if __name__ == "__main__":
    main()
