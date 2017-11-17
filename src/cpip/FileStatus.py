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
"""Provides a command line tool for finding out information on files:


Help:

.. code-block:: console

    $ python src/cpip/FileStatus.py --help
    Cmd: src/cpip/FileStatus.py --help
    Usage: FileStatus.py [options] dir
    Counts files and sizes.

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -g GLOB, --glob=GLOB  Space separated list of file match patterns. [default:
                            *.py]
      -l LOGLEVEL, --loglevel=LOGLEVEL
                            Log Level (debug=10, info=20, warning=30, error=40,
                            critical=50) [default: 30]
      -r                    Recursive. [default: False]

Example:

.. code-block:: console

    $ python3 src/cpip/FileStatus.py -r src/cpip/
    Cmd: src/cpip/FileStatus.py -r src/cpip/
    File                                     SLOC      Size                               MD5  Last modified
    src/cpip/CPIPMain.py                     1072     44829  4dee8712b7d51f978689ef257cf1fd34  Wed Sep 27 08:57:00 2017
    src/cpip/CppCondGraphToHtml.py            124      4862  4f0d5731ef6f3d47ec638f00e7646a9f  Fri Sep  8 15:30:41 2017
    src/cpip/DupeRelink.py                    269     11795  914ed2149dce6584e6f3f55ec0e2b923  Wed Sep 27 11:35:32 2017
    src/cpip/FileStatus.py                    218      8015  6db0658622e82d32a9a9b4c8eb9e82e5  Thu Sep 28 11:13:40 2017
    src/cpip/IncGraphSVG.py                  1026     45049  7b82651dadd44eb4ed65d390f6c052df  Fri Sep  8 15:30:41 2017
    ...
    src/cpip/util/Tree.py                     166      5719  cdb81d1eaaf6a1743e5182355f2e75bb  Fri Sep  8 15:30:41 2017
    src/cpip/util/XmlWrite.py                 425     15114  48563685ace3ec0f6d734695cac17ede  Tue Sep 12 15:38:55 2017
    src/cpip/util/__init__.py                  31      1161  208abac9edd9682f438945906a451473  Fri Sep  8 15:30:41 2017
    Total [54]                              19475    789349
    CPU time =    0.041 (S)
    Bye, bye!
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__rights__  = 'Copyright (c) 2008-2017 Paul Ross'

import datetime
import os
import sys
import time
import logging
import hashlib
import fnmatch
from optparse import OptionParser

from cpip import ExceptionCpip

class ExceptionFileStatus(ExceptionCpip):
    pass

class FileInfo(object):
    """Holds information on a text file."""
    def __init__(self, thePath):
        self._path = thePath
        self._sloc = 0
        self._size = 0
        self._hash = hashlib.md5()
        self._count = 0
        self._mod_time = 0
        if self._path is not None:
            if not os.path.isfile(thePath):
                raise ExceptionFileStatus('Not a file path: %s' % thePath)
            self._size = os.path.getsize(self._path)
            self._sloc = 1
            for aLine in open(self._path).readlines():
                self._hash.update(aLine.encode('utf-8'))
                self._sloc += 1
            self._count += 1
            self._mod_time = os.stat(self._path).st_mtime

    def writeHeader(self, theS=sys.stdout):
        """Writes header to stream."""
        theS.write('%8s  ' % 'SLOC')
        theS.write('%8s  ' % 'Size')
        theS.write('%32s  ' % 'MD5')
        theS.write('%s  ' % 'Last modified')

    def write(self, theS=sys.stdout, incHash=True):
        """Writes the number of lines and bytes (optionally MD5) to stream."""
        theS.write('%8d  ' % self._sloc)
        theS.write('%8d  ' % self._size)
        if incHash:
            theS.write('%32s' % self._hash.hexdigest())
        theS.write('  %s' % datetime.datetime.fromtimestamp(self._mod_time).strftime('%c'))
    
    @property
    def sloc(self):
        """Lines in file."""
        return self._sloc
    
    @property
    def size(self):
        """Size in bytes."""
        return self._size
    
    @property
    def count(self):
        """Files processed."""
        return self._count
    
    def __iadd__(self, other):
        """Add other to me."""
        self._sloc += other.sloc
        self._size += other.size
        self._count += other.count
        return self
        
class FileInfoSet(object):
    """Contains information on a set of files."""
    def __init__(self, thePath, glob=None, isRecursive=False):
        # Map of (path : class FileInfo, ...}
        self._infoMap = {}
        self.processPath(thePath, glob, isRecursive)
    
    def processPath(self, theP, glob=None, isRecursive=False):
        """Process a file or directory."""
        if os.path.isdir(theP):
            self.processDir(theP, glob, isRecursive)
        elif os.path.isfile(theP):
            self._infoMap[theP] = FileInfo(theP)
    
    def processDir(self, theDir, glob, isRecursive):
        """Read a directory and return a map of {path : class FileInfo, ...}"""
        assert(os.path.isdir(theDir))
        for aName in os.listdir(theDir):
            p = os.path.join(theDir, aName)
            if os.path.isfile(p):
                if glob is not None:
                    for aPat in glob:
                        if fnmatch.fnmatch(aName, aPat):
                            self.processPath(p, glob, isRecursive)
                            break
                else:
                    self.processPath(p, glob, isRecursive)
            elif os.path.isdir(p) and isRecursive:
                self.processPath(p, glob, isRecursive)
    
    def write(self, theS=sys.stdout):
        """Write summary to stream."""
        kS = sorted(self._infoMap.keys())
        fieldWidth = max([len(k) for k in kS])
        theS.write('%-*s  ' % (fieldWidth, 'File'))
        myTotal = FileInfo(None)
        myTotal.writeHeader(theS) 
        theS.write('\n')
        for k in kS:
            theS.write('%-*s  ' % (fieldWidth, k))
            self._infoMap[k].write(theS)
            theS.write('\n')
            myTotal += self._infoMap[k]
        theS.write('%-*s  ' % (fieldWidth, '%s [%d]' % ('Total', myTotal.count)))
        myTotal.write(theS, incHash=False)
        theS.write('\n')
        
def main():
    """Main entry point.
    """
    usage = """usage: %prog [options] dir
Counts files and sizes."""
    print('Cmd: %s' % ' '.join(sys.argv))
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option("-g", "--glob", type="string", dest="glob", default="*.py", 
                      help="Space separated list of file match patterns. [default: %default]")
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=30,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )      
    optParser.add_option("-r", action="store_true", dest="recursive", default=False, 
                      help="Recursive. [default: %default]")
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    #print opts
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    if len(args) != 1:
        optParser.print_help()
        optParser.error("No arguments!")
        return 1
    # Your code here
    myFis = FileInfoSet(args[0], glob=opts.glob.split(), isRecursive=opts.recursive)
    myFis.write()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    sys.exit(main())
