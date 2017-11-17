#!/usr/bin/env/python
# encoding: utf-8
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
"""
cpp.py -- Pretends to be like cpp, Will take options and a file (or stdin)
and process it.

@author:     Paul Ross

@copyright:  2015-2017 Paul Ross. All rights reserved.

.. code-block:: console

    (CPIP36) $ python src/cpip/cpp.py --help
    usage: cpp.py [-h] [-v] [-t] [-V] [-d MACROOPTIONS] -E [-S PREDEFINES] [-C]
                  [-D DEFINES] [-P PREINC] [-I INCUSR] [-J INCSYS]
                  [path]

    cpip.cpp -- Pretends to be like cpp, Will take options and a file (or stdin)

      Created by Paul Ross on 2015-01-16.
      Copyright 2015. All rights reserved.

      Licensed under the GPL License 2.0

    USAGE

    positional arguments:
      path                  Paths to source file. If absent then stdin is
                            processed. [default: None]

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         set verbosity level [default: 0]
      -t, --tokens          Show actual preprocessing tokens.
      -V, --version         show program's version number and exit
      -d MACROOPTIONS       Pre-processor options M, D and N. [default: []]
      -E                    Pre-process, required.
      -S PREDEFINES, --predefine PREDEFINES
                            Add standard predefined macro definitions of the form
                            name<=definition>. They are introduced into the
                            environment before anything else. They can not be
                            redefined. __DATE__ and __TIME__ will be automatically
                            allocated in here. __FILE__ and __LINE__ are defined
                            dynamically. See ISO/IEC 9899:1999 (E) 6.10.8
                            Predefined macro names. [default: []]
      -C, --CPP             Sys call 'cpp -dM' to extract and use platform
                            specific macros. These are inserted after -S option
                            and before the -D option. [default: False]
      -D DEFINES, --define DEFINES
                            Add macro definitions of the form name<=definition>.
                            These are introduced into the environment before any
                            pre-include. [default: []]
      -P PREINC, --pre PREINC
                            Add pre-include file path, this file precedes the
                            initial translation unit. [default: []]
      -I INCUSR, --usr INCUSR
                            Add user include search path. [default: []]
      -J INCSYS, --sys INCSYS
                            Add system include search path. [default: []]

Example:

.. code-block:: console

    (CPIP36) $ python src/cpip/cpp.py -E -J demo/sys/ -I demo/usr/ demo/src/main.cpp
    ----------------------------- Translation unit ----------------------------

    int main(char **argv, int argc)
    {
    printf("Bonjour tout le monde\\n");
    return 1;
    }
    -------------------------- END: Translation unit --------------------------

Using ``-t`` to show tokens:

.. code-block:: console

    (CPIP36) $ python src/cpip/cpp.py -t -E -J demo/sys/ -I demo/usr/ demo/src/main.cpp
    ----------------------------- Translation unit ----------------------------
    PpToken(t="\\n", tt=whitespace, line=False, prev=False, ?=False)
    PpToken(t="int", tt=identifier, line=True, prev=False, ?=False)
    PpToken(t=" ", tt=whitespace, line=False, prev=False, ?=False)
    PpToken(t="main", tt=identifier, line=True, prev=False, ?=False)
    PpToken(t="(", tt=preprocessing-op-or-punc, line=False, prev=False, ?=False)
    PpToken(t="char", tt=identifier, line=True, prev=False, ?=False)
    PpToken(t=" ", tt=whitespace, line=False, prev=False, ?=False)
    PpToken(t="*", tt=preprocessing-op-or-punc, line=False, prev=False, ?=False)
    PpToken(t="*", tt=preprocessing-op-or-punc, line=False, prev=False, ?=False)
    PpToken(t="argv", tt=identifier, line=True, prev=False, ?=False)
    PpToken(t=",", tt=preprocessing-op-or-punc, line=False, prev=False, ?=False)
    PpToken(t=" ", tt=whitespace, line=False, prev=False, ?=False)
    PpToken(t="int", tt=identifier, line=True, prev=False, ?=False)
    PpToken(t=" ", tt=whitespace, line=False, prev=False, ?=False)
    PpToken(t="argc", tt=identifier, line=True, prev=False, ?=False)
    PpToken(t=")", tt=preprocessing-op-or-punc, line=False, prev=False, ?=False)
    PpToken(t="\\n", tt=whitespace, line=False, prev=False, ?=False)
    PpToken(t="{", tt=preprocessing-op-or-punc, line=False, prev=False, ?=False)
    PpToken(t="\\n", tt=whitespace, line=False, prev=False, ?=False)
    PpToken(t="printf", tt=identifier, line=True, prev=False, ?=False)
    PpToken(t="(", tt=preprocessing-op-or-punc, line=False, prev=False, ?=False)
    PpToken(t=""Bonjour tout le monde\\n"", tt=string-literal, line=False, prev=False, ?=False)
    PpToken(t=")", tt=preprocessing-op-or-punc, line=False, prev=False, ?=False)
    PpToken(t=";", tt=preprocessing-op-or-punc, line=False, prev=False, ?=False)
    PpToken(t="\\n", tt=whitespace, line=False, prev=False, ?=False)
    PpToken(t="return", tt=identifier, line=True, prev=False, ?=False)
    PpToken(t=" ", tt=whitespace, line=False, prev=False, ?=False)
    PpToken(t="1", tt=pp-number, line=False, prev=False, ?=False)
    PpToken(t=";", tt=preprocessing-op-or-punc, line=False, prev=False, ?=False)
    PpToken(t="\\n", tt=whitespace, line=False, prev=False, ?=False)
    PpToken(t="}", tt=preprocessing-op-or-punc, line=False, prev=False, ?=False)
    PpToken(t="\\n", tt=whitespace, line=False, prev=False, ?=False)
    -------------------------- END: Translation unit --------------------------

"""
from __future__ import print_function

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

def _processFile(ituName,
                 incHandler,
                 stdPredefMacros,
                 preIncFiles,
                 showTokens,
                 dOptions):
    """Process the file."""
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
    program_version_message = '%%(prog)s %s (%s)' \
        % (program_version, program_build_date)
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
                        help="Paths to source file. "
                        "If absent then stdin is processed."
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
