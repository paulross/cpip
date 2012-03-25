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

"""Makes replacements in a list of lines."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import cpip

class ExceptionMatrixRep(cpip.ExceptionCpip):
    """Simple specialisation of an exception class for MatrixRep."""
    pass

class MatrixRep(object):
    """Makes replacements in a list of lines."""
    def __init__(self):
        """Constructor."""
        self._ir = {}

    def addLineColRep(self, l, c, was, now):
        """Adds to the IR. No test is made to see if there is an existing
        or pre-existing conflicting entry or if a sequence of entries makes
        sense.
        It is expected that callers call this in line/column order of the
        original matrix. If not the results of a subsequent call to
        sideEffect() are undefined. 
        """
        try:
            self._ir[l][c] = (len(was), now)
        except KeyError:
            self._ir[l] = {}
            self._ir[l][c] = (len(was), now)
    
    def sideEffect(self, theMat):
        """Makes the replacement, if line/col is out of range and
        ExceptionMatrixRep will be raised and the state of theMat argument
        is undefined."""
        #lineS = self._ir.keys()
        #lineS.sort()
        for l in self._ir:
            if l >= len(theMat):
                raise ExceptionMatrixRep('Line index %d is out of range (max %d).' \
                                         % (l, len(theMat)-1))
            colInc = 0
            colS = sorted(self._ir[l].keys())
            for c in colS:
                if (c+colInc) >= len(theMat[l]):
                    raise ExceptionMatrixRep('Col index %d is out of range (max %d).' \
                                             % (c+colInc, len(theMat[l])-1))
                x, r = self._ir[l][c]
                myLine = theMat[l]
                theMat[l] = myLine[:c+colInc] + r + myLine[c+colInc+x:]
                colInc += len(r) - x
