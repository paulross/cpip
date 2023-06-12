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

"""A generator class with a buffer. This allows multiple inspections of the
stream issued by a generator. For example this is used by MaxMunchGen."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__rights__  = 'Copyright (c) 2008-2017 Paul Ross'

import types

from cpip import ExceptionCpip

class ExceptionBufGen(ExceptionCpip):
    """Exception specialisation for BufGen."""
    pass

class BufGen(object):
    """A generator class with a buffer."""
    def __init__(self, theGen):
        """Constructor with a generator as an argument.

        :param theGen: The generator to use.
        :type theGen: ``generator``

        :returns: ``NoneType``
        """
        self._gen = theGen
        self._buf = []
    
    def __str__(self):
        return 'BufGen: %s' % self._buf

    def __getitem__(self, key):
        """Implements indexing and slicing. Negative indexes will raise an
        IndexError.

        :param key: The index.
        :type key: ``int``

        :returns: ``str`` -- The buffer corresponding to the key.

        :raises: ``IndexError, StopIteration``
        """
        idx = key
        if isinstance(key, slice):
            idx = key.stop - 1
        if idx < 0:
            raise IndexError('BufGen can not handle negative indexes.')
        # Extend the buffer if necessary
        try:
            while len(self._buf) <= idx:
                self._buf.append(next(self._gen))
        except StopIteration:
            raise IndexError('BufGen index out of range')
        return self._buf[key]
            
    @property
    def lenBuf(self):
        """Returns the length of the existing buffer. NOTE: This may not be the
        final length as the generator might not be exhausted just yet."""
        return len(self._buf)
        
    def gen(self):
        """Yield objects from the generator via the buffer."""
        i = 0
        while 1:
            if len(self._buf) <= i:
                try:
                    self._buf.append(next(self._gen))
                except (StopIteration, RuntimeError):
                    return
            yield self._buf[i]
            i +=1
    
    def slice(self, sliceLen):
        """Returns a buffer slice of length sliceLen."""
        if sliceLen > len(self._buf):
            raise ExceptionBufGen('slice length %d > buffer size of %d' \
                                  % (sliceLen, len(self._buf)))
        # Profiling optimisation; slice of 1 is a common value so
        # treat it swiftly
        if sliceLen == 1:
            return [self._buf.pop(0)]
        # Slice > 1
        retList = []
        i = 0
        while i < sliceLen:
            retList.append(self._buf.pop(0))
            i += 1
        return retList

    def replace(self, theIdx, theLen, theValueS):
        """Replaces within the buffer starting at theIdx removing theLen objects
        and replacing them with theValueS."""
        myIdxEnd = theIdx + theLen
        if theIdx >= self.lenBuf:
            raise ExceptionBufGen('replace start index %d >= buffer size of %d' \
                                  % (theIdx, len(self._buf)))
        if (myIdxEnd) > self.lenBuf:
            raise ExceptionBufGen('replace end index %d > buffer size of %d' \
                                  % (myIdxEnd, len(self._buf)))
        if theIdx < 0:
            raise ExceptionBufGen('negative index %d' % theIdx)
        if (myIdxEnd) < 0:
            raise ExceptionBufGen('negative index+length %d' % myIdxEnd)
        self._buf[theIdx:myIdxEnd] = theValueS
