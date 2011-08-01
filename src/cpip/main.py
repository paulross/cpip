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
import logging
import time
from optparse import OptionParser#, check_choice
#import pprint
#import subprocess
import multiprocessing

__version__ = '0.1.0'

def unitTest():
    pass

def main():
    usage = "usage: %prog [options] ..."
    optParser = OptionParser(usage, version='%prog ' + __version__)
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=30,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )      
    optParser.add_option(
            "-j", "--jobs",
            type="int",
            dest="jobs",
            default=0,
            help="Max processes when multiprocessing. Zero uses number of native CPUs [%d]" \
                    % multiprocessing.cpu_count() \
                    + " [default: %default]" 
        )      
    optParser.add_option("-u", "--unittest",
                         action="store_true",
                         dest="unit_test",
                         default=False, 
                         help="Execute unit tests. [default: %default]")
    optParser.add_option("-n", action="store_true", dest="nervous", default=False, 
                      help="Nervous mode (do no harm). [default: %default]")
    # List type options
    optParser.add_option("-I", "--usr", action="append", dest="incUsr",
                      help="Add user include search path. [default: %default]")
    optParser.add_option("-J", "--sys", action="append", dest="incSys",
                      help="Add system include search path. [default: %default]")
    optParser.add_option("-P", "--pre", action="append", dest="incPre",
                      help="Add pre-include file path. [default: %default]")
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    logging.critical('Test logging message')
    logging.critical('opts: %s' % opts)
    logging.critical('args: %s' % args)
    if opts.unit_test:
        unitTest()
    if len(args) > 0:
        # Your code here
        #
        pass
    else:
        optParser.print_help()
        optParser.error("No arguments!")
        return 1
    clkExec = time.clock() - clkStart
    print 'CPU time = %8.3f (S)' % clkExec
    print 'Bye, bye!'
    return 0

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    sys.exit(main())
    