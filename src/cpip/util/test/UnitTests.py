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

"""Tests all the modules in this directory.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import os
import time
import logging
import collections

class TestResult(collections.namedtuple('TestResult', 'testsRun errors failures')):
    #__slots__ = ()
    def __iadd__(self, other):
        """+= implementation. other is None or TestResult(testsRun, errors, failures)."""
        if other is not None:
            self = self._replace(
                testsRun = self.testsRun + other.testsRun,
                errors = self.errors + other.errors,
                failures = self.failures + other.failures,
                )
        return self

    def __str__(self):
        return ''.join(
            [
                '   Tests: %d\n' % self.testsRun,
                '  Errors: %d\n' % self.errors,
                'Failures: %d\n' % self.failures,
            ]
            )

def retPyModuleList():
    retList = []
    for aName in os.listdir(os.path.dirname(__file__)):
        if aName != os.path.basename(__file__) \
        and os.path.splitext(aName)[1] == '.py':
            retList.append(os.path.splitext(aName)[0])
    return retList

def unitTest(theVerbosity=0):
    myResult = TestResult(0, 0, 0)
    print('File:', __file__)
    #print 'TRACE:', os.listdir(os.path.dirname(__file__))
    #print dir()
    #print globals()
    myModules = (
            'TestBufGen',
            'TestDictTree',
            'TestHtmlUtils',
            'TestListGen',
            'TestMatrixRep',
            'TestMaxMunchGen',            
            'TestStrTree',            
            'TestXmlWrite',            
            'TestMultiPassString',            
        )
    #myModules = retPyModuleList()
    #print 'myModules:'
    #print '\n'.join(["'%s'," % x for x in myModules])
    for aName in myModules:
        try:
            mod = __import__(aName)
            #print dir(mod)
            print('Testing %s' % aName)
            c = mod.unitTest(theVerbosity=theVerbosity) or (0, 0, 0)
            #print c
            myResult += TestResult(c[0], c[1], c[2])
        except ImportError as err:
            logging.error('Can not import "%s", error: %s' % (aName, err))
        except AttributeError as err:
            logging.error('Can not run unittests on "%s", error: %s' % (aName, err))
    print('Results')
    print(myResult)

##################
# End: Unit tests.
##################

def usage():
    print("""spam.py -
Usage:
python spam.py [-hl: --help]

Options:
-h, --help ~ Help (this screen) and exit.
-l:        ~ set the logging level higher is quieter.
             Default is 20 (INFO) e.g.:
                CRITICAL    50
                ERROR       40
                WARNING     30
                INFO        20
                DEBUG       10
                NOTSET      0
""")

def main():
    print('spam.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
    print(__rights__)
    print()
    import sys, getopt
    print('Command line:')
    print(' '.join(sys.argv))
    print()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError as myErr:
        usage()
        print('ERROR: Invalid option: %s' % str(myErr))
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
        print('ERROR: Wrong number of arguments[%d]!' % len(args))
        sys.exit(1)
    clkStart = time.clock()
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    #
    # Your code here
    #
    unitTest()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
