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

#import os
import sys
import logging
import time
#import types
from optparse import OptionParser
import io
#import pprint
#import subprocess
#import multiprocessing

#from cpip import ExceptionCpip
from cpip.core import PpLexer
from cpip.core import IncludeHandler
from cpip.core import CppDiagnostic
from cpip.core import FileIncludeGraph
from cpip.core import PragmaHandler

def retIncludedFileSet(theLexer):
    myFigr = theLexer.fileIncludeGraphRoot
    myFileNameVis = FileIncludeGraph.FigVisitorFileSet()
    myFigr.acceptVisitor(myFileNameVis)
    return myFileNameVis.fileNameSet

def preProcessForIncludes(theItu, incUsr, incSys, theDefineS, preIncS, keepGoing, ignorePragma):
    myIncH = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=incUsr or [],
        theSysDirs=incSys or [],
    )
    myPreIncFiles = []
    # Add macros in psuedo pre-include
    if theDefineS:
        myStr = '\n'.join(['#define '+' '.join(d.split('=')) for d in theDefineS])+'\n'
        myPreIncFiles = [io.StringIO(myStr), ]
    myPreIncFiles.extend([open(f) for f in preIncS])
    myDiag = None
    if keepGoing:
        myDiag = CppDiagnostic.PreprocessDiagnosticKeepGoing()
    myPh = None
    if ignorePragma:
        myPh = PragmaHandler.PragmaHandlerNull()
    # Create the lexer.
    myLexer = PpLexer.PpLexer(
                    theItu,
                    myIncH,
                    preIncFiles=myPreIncFiles,
                    diagnostic=myDiag,
                    pragmaHandler=myPh,
                    )
    logging.info('Preprocessing TU: %s' % theItu)
    for t in myLexer.ppTokens():
        pass
    logging.info('Preprocessing TU done.')
    retVal = retIncludedFileSet(myLexer)
    # Remove any artificial files
    try:
        retVal.remove(myLexer.UNNAMED_FILE_NAME)
    except KeyError:
        pass
    return retVal


def main():
    usage = """usage: %prog [options] files...
Preprocess the files and lists included files."""
    #print 'Cmd: %s' % ' '.join(sys.argv)
    optParser = OptionParser(usage, version='%prog ' + __version__)
#    optParser.add_option(
#            "-j", "--jobs",
#            type="int",
#            dest="jobs",
#            default=0,
#            help="Max processes when multiprocessing. Zero uses number of native CPUs [%d]" \
#                    % multiprocessing.cpu_count() \
#                    + " [default: %default]" 
#        )      
    optParser.add_option("-k", action="store_true", dest="keep_going", default=False, 
                      help="Keep going. [default: %default]")
    optParser.add_option(
            "-l", "--loglevel",
            type="int",
            dest="loglevel",
            default=30,
            help="Log Level (debug=10, info=20, warning=30, error=40, critical=50) [default: %default]"
        )      
    optParser.add_option("-n", action="store_true", dest="nervous", default=False, 
                      help="Nervous mode (do no harm). [default: %default]")
    optParser.add_option("-p", action="store_true", dest="ignore_pragma", default=False, 
                      help="Ignore pragma statements. [default: %default]")
    # List type options
    optParser.add_option("-I", "--usr", action="append", dest="incUsr", default=[],
                      help="Add user include search path. [default: %default]")
    optParser.add_option("-J", "--sys", action="append", dest="incSys", default=[],
                      help="Add system include search path. [default: %default]")
    optParser.add_option("-P", "--pre", action="append", dest="preInc", default=[],
                      help="Add pre-include file path. [default: %default]")
    optParser.add_option("-D", "--define", action="append", dest="defines", default=[],
                      help="""Add macro defintions of the form name<=defintion>.
                      These are introduced into the environment before any pre-include. [default: %default]""")
    opts, args = optParser.parse_args()
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=opts.loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    if len(args) > 0:
        # Result to print
        myFileSet = set()
        for anItu in args:
            myFileSet.update(
                preProcessForIncludes(
                    anItu,
                    opts.incUsr,
                    opts.incSys,
                    opts.defines,
                    opts.preInc,
                    opts.keep_going,
                    opts.ignore_pragma,
                )
            )
        logging.info('All done.')
        myFileS = list(myFileSet)
        myFileS.sort()
        message = ' Included files [%d] ' % len(myFileS)
        print(message.center(75, '-'))
        print('\n'.join(myFileS))
        print(' Included files '.center(75, '-'))
    else:
        optParser.print_help()
        optParser.error("No arguments!")
        return 1
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    sys.exit(main())
    