"""Provides various utilities for interfacing with the platform installaion of cpp.
This includes using cpp as a sub-process to extract macros.
This also provides some standard cpp like options used by both cpp.py and CPIPMain.py

Created on 24 Jan 2015

@author: paulross
"""
import io
import os
import subprocess

def invokeCppForPlatformMacros(*args):
    """Invoke the pre-processor as a sub-process with *args and return a list of macro
    definition strings.
    
    By default the preprocessor is 'cpp' but this is overridden if $CPP is set in
    the environment.
    
    May raise subprocess.CalledProcessError on failure."""
    try:
        cmdS = [os.environ['CPP']]
    except KeyError:
        cmdS = ['cpp']
    cmdS.extend(args)
    return subprocess.check_output(cmdS, universal_newlines=True, stdin=subprocess.DEVNULL)

def addStandardArguments(parser):
    """This adds standard command line arguments to an argparse argument parser."""
    # Macros
    parser.add_argument("-S", "--predefine", action="append", dest="predefines", default=[],
                      help="""Add standard predefined macro definitions of the
form name<=definition>. They are introduced into the
environment before anything else. They can not be
redefined. __DATE__ and __TIME__ will be automatically
allocated in here. __FILE__ and __LINE__ are defined dynamically.
See ISO/IEC 9899:1999 (E) 6.10.8 Predefined macro names. [default: %(default)s]""")
    parser.add_argument("-C", "--CPP", action="store_true", dest="call_cpp",
                         default=False,
                         help="""Sys call 'cpp -dM' to extract and use platform
specific macros. These are inserted after -S option and
before the -D option. [default: %(default)s]""")
    parser.add_argument("-D", "--define", action="append", dest="defines", default=[],
                      help="""Add macro definitions of the form name<=definition>.
These are introduced into the environment before
any pre-include. [default: %(default)s]""")
    parser.add_argument("-P", "--pre", action="append", dest="preInc", default=[],
                      help="""Add pre-include file path, this file precedes the
initial translation unit. [default: %(default)s]""")
    # Include handling
    parser.add_argument("-I", "--usr", action="append", dest="incUsr", default=[],
                      help="Add user include search path. [default: %(default)s]")
    parser.add_argument("-J", "--sys", action="append", dest="incSys", default=[],
                      help="Add system include search path. [default: %(default)s]")

def macroDefinitionDict(cmdLineArgS):
    """Given a list of command line arguments of the form n<=d> where n is the
    macro name and d the optional definition this returns an ordered dict of {n : d, ...}."""
    retMacros = {}
    for d in cmdLineArgS:
        _tup = d.split('=')
        if len(_tup) == 2:
            retMacros[_tup[0]] = _tup[1] + '\n'
        elif len(_tup) == 1:
            retMacros[_tup[0]] = '\n'
        else:
            raise ValueError('macroDefinitionDict(): Macro definition: "%s" has multiple "=" characters.' % d)
    return retMacros

def macroDefinitionString(cmdLineArgS):
    """Given a list of command line arguments of the form n<=d> where n is the
    macro name and d the optional definition this returns a same ordered multi-line
    string where each line is of the form '#define n d' or '#define n' if d is
    not present."""
    retMacros = []
    for d in cmdLineArgS:
        _tup = d.split('=')
        if len(_tup) == 2:
            retMacros.append('#define %s %s' % (_tup[0], _tup[1]))
        elif len(_tup) == 1:
            retMacros.append('#define %s' % _tup[0])
        else:
            raise ValueError('macroDefinitionString(): Macro definition: "%s" has multiple "=" characters.' % d)
    retMacros.append('')
    return '\n'.join(retMacros)

def stdPredefinedMacros(args):
    """Returns a dict of standard predefined macros specified on the command line.
    See ISO/IEC 9899:1999 (E) 6.10.8 Predefined macro names."""
    return macroDefinitionDict(args.predefines)
    
def predefinedFileObjects(args):
    """Returns a list of file like objects to be pre-processed before the ITU.
    This does in this order:
    1 Platform specific macros
    2 Any command line defines
    3 Any pre-included files
    """
    retVal = []
    # First platform specific macros
    if args.call_cpp:
#         print('Adding', invokeCppForPlatformMacros('-E', '-dM'))
        retVal.append(io.StringIO(invokeCppForPlatformMacros('-E', '-dM')))
    # Then any command line defines
    retVal.append(io.StringIO(macroDefinitionString(args.defines)))
    # Then pre-included files
    for preIncPath in args.preInc:
        retVal.append(open(preIncPath))
    return retVal
