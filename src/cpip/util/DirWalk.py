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
"""Provides various ways of walking a directory tree

Created on Jun 9, 2011
"""

__author__  = 'Paul Ross'
__date__    = '2011-06-09'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

import os
import fnmatch
import collections

#: A pair of (in, out) file paths
FileInOut = collections.namedtuple('FileInOut', 'filePathIn, filePathOut')

class ExceptionDirWalk(Exception):
    """Exception class for this module."""
    pass

def genBigFirst(d):
    """Generator that yields the biggest files (name not path) first.
    This is fairly simple in that it it only looks the current directory not
    only sub-directories. Useful for multiprocessing."""
    # Use DSU technique
    fileSizeS = []
    for n in os.listdir(d):
        p = os.path.join(d, n)
        if os.path.isfile(p):
            fileSizeS.append((os.path.getsize(p), n))
    for _s, n in reversed(sorted(fileSizeS)):
        yield n

def dirWalk(theIn, theOut=None, theFnMatch=None, recursive=False, bigFirst=False):
    """Walks a directory tree generating file paths.

    theIn - The input directory.

    theOut - The output directory. If None then input file paths as strings
    will be generated If non-None this function will yield
    FileInOut(in, out) objects.
    NOTE: This does not create the output directory structure, it is up to
    the caller to do that.

    theFnMatch - A glob like match pattern for file names (not tested for directory names).

    recursive - Boolean to recurse or not.

    bigFirst - If True then the largest files in  directory are given first. If False it is alphabetical.
    """
    if not os.path.isdir(theIn):
        raise ExceptionDirWalk('{:s} is not a directory.'.format(theIn))
    if bigFirst:
        # First files
        for fn in genBigFirst(theIn):
            fp = os.path.join(theIn, fn)
            if theFnMatch is None or fnmatch.fnmatch(fp, theFnMatch):
                if theOut is None:
                    yield fp
                else:
                    yield FileInOut(fp, os.path.join(theOut, fn))
        # Now directories
        if recursive:
            for n in os.listdir(theIn):
                fp = os.path.join(theIn, n)
                if os.path.isdir(fp):
                    if theOut is None:
                        outP = None
                    else:
                        outP = os.path.join(theOut, n)
                    for aFp in dirWalk(fp, outP, theFnMatch, recursive, bigFirst):
                        yield aFp
    else:
        # Straightforward list in alphanumeric order
        for fn in os.listdir(theIn):
            fp = os.path.join(theIn, fn)
            if os.path.isfile(fp) \
            and (theFnMatch is None or fnmatch.fnmatch(fp, theFnMatch)):
                if theOut is None:
                    yield fp
                else:
                    yield FileInOut(fp, os.path.join(theOut, fn))
            elif os.path.isdir(fp) and recursive:
                if theOut is None:
                    outP = None
                else:
                    outP = os.path.join(theOut, fn)
                for aFp in dirWalk(fp, outP, theFnMatch, recursive):
                    yield aFp
