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

"""An SVG writer."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

from cpip import ExceptionCpip
from cpip.util import XmlWrite
from cpip.plot import Coord

class ExceptionSVGWriter(ExceptionCpip):
    """Exception class for SVGWriter."""
    pass

def dimToTxt(theDim):
    """Converts a Coord.Dim() object to text for SVG units."""
    return Coord.UNIT_MAP_DEFAULT_FORMAT_WITH_UNITS[theDim.units] % (theDim.value, theDim.units)

class SVGWriter(XmlWrite.XmlStream):
    """Initialise the stream with a file and Coord.Box() object.
    The view port units must be the same for width and depth."""
    def __init__(self, theFile, theViewPort, rootAttrs=None, mustIndent=True):
        super(SVGWriter, self).__init__(theFile, mustIndent=mustIndent)
        self._viewPort = theViewPort
        self._rootAttrs = rootAttrs
            
    def __enter__(self):
        super(SVGWriter, self).__enter__()
        self._file.write("""\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">""")
        _attrs = {
            'xmlns'         : 'http://www.w3.org/2000/svg',
            'version'       : '1.1',
            'width'         : dimToTxt(self._viewPort.width),
            'height'        : dimToTxt(self._viewPort.depth),
        }
        if self._rootAttrs:
            _attrs.update(self._rootAttrs)
        self.startElement('svg', _attrs)
        return self
    
class SVGGroup(XmlWrite.Element):
    """Initialise the group with a stream.
    
    See: http://www.w3.org/TR/2003/REC-SVG11-20030114/struct.html#GElement
    
    Sadly we can't use ``**kwargs`` because of Python restrictions on keyword
    names. For example ``stroke-width`` that is not a valid keyword
    argument (although ``stroke_width`` would be). So instead we pass in an
    optional dictionary {string : string, ...}"""
    def __init__(self, theXmlStream, attrs=None):
        super(SVGGroup, self).__init__(theXmlStream, 'g', attrs)

class SVGRect(XmlWrite.Element):
    """Initialise the rectangle with a stream, a Coord.Pt() and a
    Coord.Box() objects.
    See: http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#RectElement
    Typical attributes:
    {'fill' : "blue", 'stroke' : "black", 'stroke-width' : "2", }
    """
    def __init__(self, theXmlStream, thePoint, theBox, attrs=None):
        myAttrs = {
                    'x'         : dimToTxt(thePoint.x),
                    'y'         : dimToTxt(thePoint.y),
                    'width'     : dimToTxt(theBox.width),
                    'height'    : dimToTxt(theBox.depth),
                }
        if attrs:
            myAttrs.update(attrs)
        super(SVGRect, self).__init__(theXmlStream, 'rect', myAttrs)
    
class SVGCircle(XmlWrite.Element):
    """A circle in SVG. See: http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#CircleElement
    
    Initialise the circle with a stream, a Coord.Pt() and a Coord.Dim() objects."""
    def __init__(self, theXmlStream, thePoint, theRadius, attrs=None):
        _attrs = {
                    'cx'        : dimToTxt(thePoint.x),
                    'cy'        : dimToTxt(thePoint.y),
                    'r'         : dimToTxt(theRadius),
                }
        if attrs:
            _attrs.update(attrs)
        super(SVGCircle, self).__init__(theXmlStream, 'circle', _attrs)
    
class SVGElipse(XmlWrite.Element):
    """An elipse in SVG. See: http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#EllipseElement
    
    Initialise the elipse with a stream, a Coord.Pt() and a Coord.Dim() objects."""
    def __init__(self, theXmlStream, ptFrom, theRadX, theRadY, attrs=None):
        _attrs = {
                    'cx'        : dimToTxt(ptFrom.x),
                    'cy'        : dimToTxt(ptFrom.y),
                    'rx'        : dimToTxt(theRadX),
                    'ry'        : dimToTxt(theRadY),
                }
        if attrs:
            _attrs.update(attrs)
        super(SVGElipse, self).__init__(theXmlStream, 'elipse', _attrs)
    
class SVGLine(XmlWrite.Element):
    """A line in SVG. See: http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#LineElement
    
    Initialise the line with a stream, and two Coord.Pt() objects."""
    def __init__(self, theXmlStream, ptFrom, ptTo, attrs=None):
        _attrs = {
                    'x1'        : dimToTxt(ptFrom.x),
                    'y1'        : dimToTxt(ptFrom.y),
                    'x2'        : dimToTxt(ptTo.x),
                    'y2'        : dimToTxt(ptTo.y),
                }
        if attrs:
            _attrs.update(attrs)
        super(SVGLine, self).__init__(theXmlStream, 'line', _attrs)
    
class SVGPointList(XmlWrite.Element):
    """An abstract class that takes a list of points, derived by polyline and polygon.
    
    Initialise the element with a stream, a name, and a list of Coord.Pt() objects.

    NOTE: The units of the points are ignored, it is up to the caller to convert
    them to the User Coordinate System."""
    def __init__(self, theXmlStream, name, pointS, attrs):
        _attrs = {
            'points' : ' '.join(['%s,%s' % (p.x.value, p.y.value) for p in pointS])
        }
        if attrs:
            _attrs.update(attrs)
        super(SVGPointList, self).__init__(theXmlStream, name, _attrs)

class SVGPolyline(SVGPointList):
    """A polyline in SVG. See: http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#PolylineElement
    
    Initialise the polyline with a stream, and a list of Coord.Pt() objects.

    NOTE: The units of the points are ignored, it is up to the caller to convert
    them to the User Coordinate System."""
    def __init__(self, theXmlStream, pointS, attrs=None):
        super(SVGPolyline, self).__init__(theXmlStream, 'polyline', pointS, attrs)
    
class SVGPolygon(SVGPointList):
    """A polygon in SVG. See: http://www.w3.org/TR/2003/REC-SVG11-20030114/shapes.html#PolygonElement
    
    Initialise the polygon with a stream, and a list of Coord.Pt() objects.

    NOTE: The units of the points are ignored, it is up to the caller to convert
    them to the User Coordinate System."""
    def __init__(self, theXmlStream, pointS, attrs=None):
        super(SVGPolygon, self).__init__(theXmlStream, 'polygon', pointS, attrs)
    
class SVGText(XmlWrite.Element):
    """Text in SVG. See: http://www.w3.org/TR/2003/REC-SVG11-20030114/text.html#TextElement
    
    Initialise the text with a stream, a Coord.Pt() and font as a string and
    size as an integer. If thePoint is None then no location will be specified
    (for example for use inside a <defs> element."""
    def __init__(self, theXmlStream, thePoint, theFont, theSize, attrs=None):
        _attrs = {}
        if theFont is not None:
            _attrs['font-family'] = theFont,
        if theSize is not None:
            _attrs['font-size'] = '%s' % theSize
        if thePoint is not None:
            _attrs['x'] = dimToTxt(thePoint.x)
            _attrs['y'] = dimToTxt(thePoint.y)
        if attrs:
            _attrs.update(attrs)
        super(SVGText, self).__init__(theXmlStream, 'text', _attrs)
