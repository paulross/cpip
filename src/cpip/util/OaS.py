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

"""Various utility functions etc. that don't obviously fit elsewhere.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

#import collections
from cpip import ExceptionCpip

class ExceptionOas(ExceptionCpip):
    """Simple specialisation of an exception class for this module."""
    pass

def indexMatch(l, v):
    """Returns the index of v in sorted list l or -1.
    This uses Jon Bentley's binary search algorithm.
    This uses operators > and <."""
    i = 0
    j = len(l) - 1
    while i <= j:
        m = i + ((j - i) // 2)
        if l[m] < v:
            i = m + 1
        elif l[m] > v:
            j = m - 1
        else:
            return m
    return -1

def indexLB(l, v):
    """Returns the lower bound index in a sorted list l of the value that is
    equal to v or the nearest lower value to v.
    Returns -1 if l empty or all values higher than v."""
    TRACE = 0
    if TRACE: print('TRACE indexLB(): l=%s, v=%s' % (l, v))
    i = 0
    j = len(l) - 1
    while i < j:
        m = i + ((j - i) // 2)
        if TRACE: print('TRACE indexLB(): i=%d, j=%d, m=%d l[m]=%d' % (i, j, m, l[m]))
        if m == i:
            # i and j are equal or just 1 apart
            if l[j] <= v:
                return j
            elif l[i] <= v:
                return i
            else:
                return -1
        if l[m] < v:
            i = m
        elif l[m] > v:
            j = m
        else:
            # Here: l[m] == v
            return m
    if TRACE: print('TRACE indexLB(): END i=%d, j=%d' % (i, j))
    if i >= j and j >= 0 and j < len(l) and l[j] <= v:
        return j
    return -1

def indexUB(l, v):
    """Returns the upper bound index in a sorted list l of the value that is
    equal to v or the nearest upper value to v.
    Returns -1 if l empty or all values lower than v."""
    iLB = indexLB(l, v)
    #print 'TRACE indexUB(): iLB=%d' % (iLB)
    if iLB == -1:
        if len(l) > 0:
            return 0
        else:
            return -1
    # Lower bound found
    if l[iLB] == v:
        return iLB
    # But lower bound entry is lower than v
    if iLB + 1 < len(l):
        return iLB + 1
    return -1
