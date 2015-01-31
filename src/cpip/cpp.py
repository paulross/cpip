#!/usr/local/bin/python2.7
# encoding: utf-8
"""
cpip.cpp -- Pretends to be like cpp, Will take options and a file (or stdin) and process it.

cpip.cpp is a description

It defines classes_and_methods

@author:     Paul Ross

@copyright:  2015 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
"""
import argparse
import os
import sys

from cpip.core import PpLexer
from cpip.core import IncludeHandler
from cpip.util import Cpp

__all__ = []
__version__ = 0.1
__date__ = '2015-01-16'
__updated__ = '2015-01-16'

def _processFile(ituName, incHandler, stdPredefMacros, preIncFiles, showTokens, dOptions):
    myLexer = PpLexer.PpLexer(
                              ituName,
                              incHandler,
                              preIncFiles=preIncFiles,
                              stdPredefMacros=stdPredefMacros,
                              )
    tokenS = [tok for tok in myLexer.ppTokens(incWs=True, minWs=True, condLevel=0)]
    if 'D' in dOptions or len(dOptions) == 0:
        print(' Translation unit '.center(75, '-'))
        for tok in tokenS:
            if showTokens:
                print(tok)
            else:
                print(tok.t, end='')
        print(' END: Translation unit '.center(75, '-'))
    if 'M' in dOptions or 'D' in dOptions or 'N' in dOptions:
        print(' Macros '.center(75, '-'))
        if 'N' in dOptions:
            for m in sorted(myLexer.macroEnvironment.macros()):
                print(m)
        else:
            print(myLexer.macroEnvironment)
        print(' END: Macros '.center(75, '-'))

def main(argv=None):
    """Command line options."""

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = """%s

  Created by Paul Ross on %s.
  Copyright 2015. All rights reserved.

  Licensed under the GPL License 2.0

USAGE
""" % (program_shortdesc, str(__date__))

    # Setup argument parser
    parser = argparse.ArgumentParser(description=program_license,
                            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", dest="verbose",
                        action="count", default=0,
                        help="set verbosity level [default: %(default)s]")
    parser.add_argument("-t", '--tokens', dest="tokens", action="store_true",
                        help="Show actual preprocessing tokens.")
    parser.add_argument('-V', '--version', action='version',
                        version=program_version_message)
    parser.add_argument(dest="path", metavar="path", nargs='?',
                        help="Paths to source file. If absent then stdin is processed."
                        " [default: %(default)s]")
    
    # cpp like options
    parser.add_argument("-d", dest="macroOptions", action='append',
                        default=[],
                        help="Pre-processor options M, D and N."
                        " [default: %(default)s]")
    parser.add_argument("-E", dest="preprocess", action="store_true",
                        required=True,
                        help="Pre-process, required.")
    Cpp.addStandardArguments(parser)
    args = parser.parse_args()
    if args.path is None:
        # stdin
        myIncH = IncludeHandler.CppIncludeStdin(
                    theUsrDirs=args.incUsr or [],
                    theSysDirs=args.incSys or [],
        )
        ituName = 'stdin'
    else:
        myIncH = IncludeHandler.CppIncludeStdOs(
                    theUsrDirs=args.incUsr or [],
                    theSysDirs=args.incSys or [],
        )
        ituName = args.path
    _processFile(ituName,
                 myIncH,
                 Cpp.stdPredefinedMacros(args),
                 Cpp.predefinedFileObjects(args),
                 args.tokens,
                 args.macroOptions)
    return 0

if __name__ == "__main__":
    sys.exit(main())