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

"""A module that tests generator stacks.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'


import time
import logging
import sys
#import os
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

def gen_00(f):
    for b in f.read():
        yield b

def gen_01(f):
    for b in gen_00(f):
        yield b

def gen_02(f):
    for b in gen_01(f):
        yield b

def gen_03(f):
    for b in gen_02(f):
        yield b

def gen_04(f):
    for b in gen_03(f):
        yield b

def gen_05(f):
    for b in gen_04(f):
        yield b

def gen_06(f):
    for b in gen_05(f):
        yield b

def usage():
    """Send the help to stdout."""
    print \
"""TestGenStackPerf.py - A module that tests generator stacks

Usage:
python TestGenStackPerf.py [-lh --help]

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
    print 'TestGenStackPerf.py script version "%s", dated %s' % (__version__, __date__)
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
    siz = 1
    for s in range(8):
        print 'Size: %8d' % siz
        for func in (
                  gen_00,
                  gen_01,
                  gen_02,
                  gen_03,
                  gen_04,
                  gen_05,
                  gen_06,
                  ):
            myF = StringIO.StringIO(' ' * siz)
            genClkStart = time.clock()
            for b in func(myF):
                pass
            genClkExec = time.clock() - genClkStart
            print '  %s  %10.3f (s)  %10.3f (kb/s)' % (func, genClkExec, siz/(1024*genClkExec))
        siz *= 10
    clkExec = time.clock() - clkStart
    print 'CPU time = %8.3f (S)' % clkExec
    print 'Bye, bye!'

if __name__ == "__main__":
    main()
