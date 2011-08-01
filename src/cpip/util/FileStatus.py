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
import hashlib
import fnmatch
from optparse import OptionParser

from cpip import ExceptionCpip

class ExceptionFileStatus(ExceptionCpip):
    pass

class FileInfo(object):
    def __init__(self, thePath):
        self._path = thePath
        self._sloc = 0
        self._size = 0
        self._hash = hashlib.md5()
        self._count = 0
        if self._path is not None:
            if not os.path.isfile(thePath):
                raise ExceptionFileStatus('Not a file path: %s' % thePath)
            self._size = os.path.getsize(self._path)
            self._sloc = 1
            for aLine in open(self._path).readlines():
                self._hash.update(aLine)
                self._sloc += 1
            self._count += 1
        
    def writeHeader(self, theS=sys.stdout):
        theS.write('%8s  ' % 'SLOC')
        theS.write('%8s  ' % 'Size')
        theS.write('%s' % 'MD5')
    
    def write(self, theS=sys.stdout, incHash=True):
        theS.write('%8d  ' % self._sloc)
        theS.write('%8d  ' % self._size)
        if incHash:
            theS.write('%s' % self._hash.hexdigest())
    
    @property
    def sloc(self):
        return self._sloc
    
    @property
    def size(self):
        return self._size
    
    @property
    def count(self):
        return self._count
    
    def __iadd__(self, other):
        self._sloc += other.sloc
        self._size += other.size
        self._count += other.count
        return self
        
class FileInfoSet(object):
    def __init__(self, thePath, glob=None, isRecursive=False):
        # Map of (path : class FileInfo, ...}
        self._infoMap = {}
        self.processPath(thePath, glob, isRecursive)
    
    def processPath(self, theP, glob=None, isRecursive=False):
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
        kS = self._infoMap.keys()
        kS.sort()
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
    usage = """usage: %prog [options] dir
Counts files and sizes."""
    print 'Cmd: %s' % ' '.join(sys.argv)
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
    print 'CPU time = %8.3f (S)' % clkExec
    print 'Bye, bye!'
    return 0

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    sys.exit(main())
