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

"""Treats a string as a tree."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__rights__  = 'Copyright (c) 2008-2017 Paul Ross'

#import os
#import time
#import logging

class StrTree(object):
    """A string tree or Trie."""
    def __init__(self, theIterable=None):
        """Initialise the class with a optional sequence of strings.

        :param theIterable: A sequence of strings.
        :type theIterable: ``NoneType, set([str])``

        :returns: ``NoneType``"""
        self._ir = {}
        self._b = False
        if theIterable is not None:
            for aS in theIterable:
                self.add(aS)

    def __str__(self):
        return '\n'.join(self._str(0))
        
    def _str(self, d):
        p = ' ' * d
        sL = ['%s%s %d' % (p, self._b, d)]
        kS = self._ir.keys()
        for k in kS:
            sL.append('%s"%s"' % (p, k))
            sL.extend(self._ir[k]._str(d+1))
        return sL

    def add(self, s):
        """Add a string.

        :param s: The string to add.
        :type s: ``str``

        :returns: ``NoneType``"""
        if s:
            if s[0] not in self._ir:
                self._ir[s[0]] = StrTree()
            self._ir[s[0]].add(s[1:])
        else:
            self._b = True
            
    def has(self, s, i=0):
        """Returns the index of the end of s that match a complete word
        in the tree. i.e. ``[i:return_value]`` is in the dictionary.


        :param s: value
        :type s: :py:class:`cpip.util.BufGen.BufGen`, ``str``

        :param i: index
        :type i: ``int``

        :returns: ``int`` -- index.

        :raises: ``IndexError, KeyError`` NOTE: IndexError and KeyError are trapped here.
        """
        assert(i >= 0)
        try:
            myI = self._ir[s[i]].has(s, i+1)
            if myI > 0:
                return myI
            if self._b:
                return i
        except (IndexError, KeyError):
            if self._b:
                return i
        return 0
    
    def values(self):
        """Returns all values."""
        return self._values([])
    
    def _values(self, l):
        r = []
        if self._b:
            r.append(''.join(l))
        for k in self._ir.keys():
            l.append(k)
            r.extend(self._ir[k]._values(l))
            l.pop()
        return r
