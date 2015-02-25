#!/usr/bin/env python
#!/usr/bin/env python
# CPIP is a C/C++ Preprocessor implemented in Python.
# Copyright (C) 2008-2014 Paul Ross
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

"""Provides a means of linking to a translation unit to HTML.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

from cpip import ExceptionCpip
from cpip.util import OaS

class ExceptionTuIndexer(ExceptionCpip):
    """Exception when handling PpLexer object."""
    pass

class TuIndexer(object):
    """Provides a means of indexing into a TU html file."""
    def __init__(self, tuFileName):
        self._tuName = tuFileName
        self._tuMarkerS = []
        
    def __str__(self):
        if len(self._tuMarkerS) == 0:
            return 'TuIndexer for "%s", no values' % self._tuName
        return 'TuIndexer for "%s". number of values=%d from %d to %d' % \
            (self._tuName, len(self._tuMarkerS), self._tuMarkerS[0], self._tuMarkerS[-1])
    
    def add(self, theTuIndex):
        """Adds an integer index to the list of markers, returns the href name."""
        if len(self._tuMarkerS) > 0 \
        and theTuIndex < self._tuMarkerS[-1]:
            raise ExceptionTuIndexer('Out of sequence: %s' % theTuIndex)
        self._tuMarkerS.append(theTuIndex)
        return '_%d' % theTuIndex
        
    def href(self, theTuIndex, isLB):
        """Returns an href string for the TuIndex. If isLB is true returns
        the nearest lower bound, otherwise the nearest upper bound."""
        if isLB:
            myIdx = OaS.indexLB(self._tuMarkerS, theTuIndex)
        else:
            myIdx = OaS.indexUB(self._tuMarkerS, theTuIndex)
        if myIdx >= len(self._tuMarkerS):
            raise ExceptionTuIndexer('Over-range index, isLB=%s: %s' % (isLB, theTuIndex))
        if myIdx == -1:
            raise ExceptionTuIndexer('Under-range index, isLB=%s: %s' % (isLB, theTuIndex))
        return '%s#_%d' % (self._tuName, self._tuMarkerS[myIdx])
