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

"""Tests for SVG graph.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import sys
import os
import unittest
import time
import logging
#import pprint

import io

sys.path.append(os.path.join(os.pardir + os.sep))
from cpip.core import PpToken, FileIncludeGraph, PpTokenCount, PpLexer
from cpip.core.IncludeHandler import CppIncludeStringIO
from cpip.plot import TreePlotTransform 
from cpip import IncGraphSVG

#######################################
# Section: Unit tests
########################################

class TestIncGraphSVGVisitor(unittest.TestCase):
    """Tests the IncGraphSVG class ."""
    def test_00(self):
        _pathsUsr = [
                os.path.join('usr'),
                os.path.join('usr', 'inc'),
                ]
        _pathsSys = [
                os.path.join('sys'),
                os.path.join('sys', 'inc'),
                ]
        _initialTuContents = """Include usr/spam:
#include "spam.h"
Include usr/inc/eggs:
#include "inc/eggs.h"
Include sys/chips:
#include <chips.h>
Include sys/inc/beans:
#include <inc/beans.h>
"""
        _incFileMap = {
                os.path.join('usr', 'spam.h') : """Content of: user, spam.h
""",
                os.path.join('usr', 'inc', 'eggs.h') : """Content of: user, include, eggs.h
Which is much bigger.""",
                os.path.join('sys', 'chips.h') : """chips.h
""",
                os.path.join('sys', 'inc', 'beans.h') : """Content of: system, include, beans.h
Which is very big, 1, def, 345,
and loads of other things.
""",
            }
        _incSim = CppIncludeStringIO(
            _pathsUsr,
            _pathsSys,
            _initialTuContents,
            _incFileMap,
            )
        _incSim.validateCpStack()
        self.assertEqual([], _incSim.cpStack)
        self.assertEqual(0, _incSim.cpStackSize)
        myLexer = PpLexer.PpLexer('src/spam.c', _incSim)
        result = ''.join([t.t for t in myLexer.ppTokens()])
#        print('Result:')
#        print(result)
        expectedResult = """Include usr/spam:
Content of: user, spam.h

Include usr/inc/eggs:
Content of: user, include, eggs.h
Which is much bigger.
Include sys/chips:
chips.h

Include sys/inc/beans:
Content of: system, include, beans.h
Which is very big, 1, def, 345,
and loads of other things.

"""
        self.assertEqual(result, expectedResult)
        myLexer.finalise()
        myFigr = myLexer.fileIncludeGraphRoot
#         print('FileIncludeGraph:')
#         print(myFigr)
        # WARN: excape \b (two places on last two lines
        expGraph = """src/spam.c [32, 24]:  True "" ""
000002: #include usr/spam.h
  usr/spam.h [12, 8]:  True "" "['"spam.h"', 'CP=None', 'usr=usr']"
000004: #include usr/inc/eggs.h
  usr/inc/eggs.h [23, 15]:  True "" "['"inc/eggs.h"', 'CP=None', 'usr=usr']"
000006: #include sys/chips.h
  sys/chips.h [4, 3]:  True "" "['<chips.h>', 'sys=sys']"
000008: #include sys/inc/beans.h
  sys/inc/beans.h [44, 27]:  True "" "['<inc/beans.h>', 'sys=sys']\""""
#         print('Exp FileIncludeGraph:')
#         print(expGraph)
#         self.maxDiff = None
        #for i, c in enumerate(str(myFigr)):
        #    if c != expGraph[i]:
        #        print '[%d] %s != %s' % (i, c, expGraph[i])
        self.assertEqual(expGraph, str(myFigr))
#         print()
#         myFigr.dumpGraph()
        self.assertEqual(expGraph, str(myFigr))
        # Now visit the graph
        myVis = FileIncludeGraph.FigVisitorTree(IncGraphSVG.SVGTreeNodeMain)
        myFigr.acceptVisitor(myVis)
        # Tree is now a graph of IncGraphSVG.SVGTreeNode
        myIgs = myVis.tree()
#         print()
#         print('myIgs')
        #print myIgs
#         myIgs.dumpToStream()
#         print()
        # Create a plot configuration
        myTpt = TreePlotTransform.TreePlotTransform(myIgs.plotCanvas, 'left', '+')
        mySvg = io.StringIO()
        myIgs.plotToFileObj(mySvg, myTpt)
#         print()
#         print(mySvg.getvalue())
        for aPos in myTpt.genRootPos():
            for aDir in myTpt.genSweepDir():
                aTpt = TreePlotTransform.TreePlotTransform(myIgs.plotCanvas, aPos, aDir)
                mySvg = io.StringIO()
                myIgs.plotToFileObj(mySvg, aTpt)
#                 print()
#                 print(mySvg.getvalue())
    
    
    def test_05(self):
        """TestIncGraphSVGVisitor: Two pre-includes and a graph."""
        return
        # First create an include graph
        myFigr = FileIncludeGraph.FileIncludeGraphRoot()
        myTcs = PpTokenCount.PpTokenCountStack()
        myFs = []
        # push ITU.h
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('ITU.h', True, '', 'CP=.'))
        myTcs.push()
        myFs.append('ITU.h')
        self.assertEqual(3, myFigr.numTrees())
        # push ITU.h/a.h
        myFigr.graph.addBranch(['ITU.h',], 15, 'a.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('a.h')
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), True, 1)
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), False, 1)
        # push ITU.h/a.h/aa.h
        myFigr.graph.addBranch(['ITU.h', 'a.h'], 17, 'aa.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('aa.h')
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), True, 2)
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), False, 2)
        # pop ITU.h/a.h/aa.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # push ITU.h/a.h/ab.h
        myFigr.graph.addBranch(['ITU.h', 'a.h'], 19, 'ab.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('ab.h')
        myTcs.counter().inc(PpToken.PpToken('ab.h', 'identifier'), True, 4)
        myTcs.counter().inc(PpToken.PpToken('ab.h', 'identifier'), False, 4)
        # pop ITU.h/a.h/ab.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # pop ITU.h/a.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 1)
        # push ITU.h/b.h
        myFigr.graph.addBranch(['ITU.h',], 115, 'b.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('b.h')
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), True, 8)
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), False, 8)
        # push ITU.h/b.h/ba.h
        myFigr.graph.addBranch(['ITU.h', 'b.h'], 117, 'ba.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('ba.h')
        myTcs.counter().inc(PpToken.PpToken('ba.h', 'identifier'), True, 16)
        myTcs.counter().inc(PpToken.PpToken('ba.h', 'identifier'), False, 16)
        # pop ITU.h/b.h/ba.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # push ITU.h/b.h/bb.h
        myFigr.graph.addBranch(['ITU.h', 'b.h'], 119, 'bb.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('bb.h')
        myTcs.counter().inc(PpToken.PpToken('bb.h', 'identifier'), True, 32)
        myTcs.counter().inc(PpToken.PpToken('bb.h', 'identifier'), False, 32)
        # pop ITU.h/b.h/bb.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # pop ITU.h/b.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 1)
        # ITU.h
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), True, 70)
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), False, 70)
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 0)
        myTcs.close()
        expGraph = """PreInclude_00 [156, 8]:  True "a >= b+2" "Forced PreInclude_00"
PreInclude_01 [83, 7]:  True "x > 1" "Forced PreInclude_00"
ITU.h [140, 70]:  True "" "CP=."
000015: #include a.h
        a.h [2, 1]:  True "" "CP=."
        000017: #include aa.h
                aa.h [4, 2]:  True "" "CP=."
        000019: #include ab.h
                ab.h [8, 4]:  True "" "CP=."
000115: #include b.h
        b.h [16, 8]:  True "" "CP=."
        000117: #include ba.h
                ba.h [32, 16]:  True "" "CP=."
        000119: #include bb.h
                bb.h [64, 32]:  True "" "CP=.\""""
        print()
        print(expGraph)
        print()
        print(str(myFigr))
        print()
        myFigr.dumpGraph()
        self.assertEqual(expGraph, str(myFigr))
        # Now visit the graph
        myVis = FileIncludeGraph.FigVisitorTree(IncGraphSVG.SVGTreeNode)
        myFigr.acceptVisitor(myVis)
        # Tree is now a graph of IncGraphSVG.SVGTreeNode
        myIgs = myVis.tree()
        print()
        print('myIgs')
        #print myIgs
        myIgs.dumpToStream()
        print()
        # Create a plot configuration
        myTpt = TreePlotTransform.TreePlotTransform(myIgs.plotCanvas, 'top', '-')
        mySvg = io.StringIO()
        myIgs.plotToFileObj(mySvg, myTpt)
        print()
        print(mySvg.getvalue())

    def test_10(self):
        """TestIncGraphSVGVisitor: Two pre-includes and a graph."""
        return
        # First create an include graph
        myFigr = FileIncludeGraph.FileIncludeGraphRoot()
        myTcs = PpTokenCount.PpTokenCountStack()
        myFs = []
        # push PreInclude_00
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('PreInclude_00', True, 'a >= b+2', 'Forced PreInclude_00'))
        myTcs.push()
        myFs.append('PreInclude_00')
        myTcs.counter().inc(PpToken.PpToken('PreInclude_00', 'identifier'), True, 8)
        myTcs.counter().inc(PpToken.PpToken('PreInclude_00', 'identifier'), False, 148)
        # pop PreInclude_00
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 0)
        # push PreInclude_01
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('PreInclude_01', True, 'x > 1', 'Forced PreInclude_00'))
        myTcs.push()
        myFs.append('PreInclude_01')
        myTcs.counter().inc(PpToken.PpToken('PreInclude_01', 'identifier'), True, 7)
        myTcs.counter().inc(PpToken.PpToken('PreInclude_01', 'identifier'), False, 76)
        # pop PreInclude_01
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 0)
        # push ITU.h
        myFigr.addGraph(FileIncludeGraph.FileIncludeGraph('ITU.h', True, '', 'CP=.'))
        myTcs.push()
        myFs.append('ITU.h')
        self.assertEqual(3, myFigr.numTrees())
        # push ITU.h/a.h
        myFigr.graph.addBranch(['ITU.h',], 15, 'a.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('a.h')
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), True, 1)
        myTcs.counter().inc(PpToken.PpToken('a.h', 'identifier'), False, 1)
        # push ITU.h/a.h/aa.h
        myFigr.graph.addBranch(['ITU.h', 'a.h'], 17, 'aa.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('aa.h')
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), True, 2)
        myTcs.counter().inc(PpToken.PpToken('aa.h', 'identifier'), False, 2)
        # pop ITU.h/a.h/aa.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # push ITU.h/a.h/ab.h
        myFigr.graph.addBranch(['ITU.h', 'a.h'], 19, 'ab.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('ab.h')
        myTcs.counter().inc(PpToken.PpToken('ab.h', 'identifier'), True, 4)
        myTcs.counter().inc(PpToken.PpToken('ab.h', 'identifier'), False, 4)
        # pop ITU.h/a.h/ab.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # pop ITU.h/a.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 1)
        # push ITU.h/b.h
        myFigr.graph.addBranch(['ITU.h',], 115, 'b.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('b.h')
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), True, 8)
        myTcs.counter().inc(PpToken.PpToken('b.h', 'identifier'), False, 8)
        # push ITU.h/b.h/ba.h
        myFigr.graph.addBranch(['ITU.h', 'b.h'], 117, 'ba.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('ba.h')
        myTcs.counter().inc(PpToken.PpToken('ba.h', 'identifier'), True, 16)
        myTcs.counter().inc(PpToken.PpToken('ba.h', 'identifier'), False, 16)
        # pop ITU.h/b.h/ba.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # push ITU.h/b.h/bb.h
        myFigr.graph.addBranch(['ITU.h', 'b.h'], 119, 'bb.h', True, '', 'CP=.')
        myTcs.push()
        myFs.append('bb.h')
        myTcs.counter().inc(PpToken.PpToken('bb.h', 'identifier'), True, 32)
        myTcs.counter().inc(PpToken.PpToken('bb.h', 'identifier'), False, 32)
        # pop ITU.h/b.h/bb.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 2)
        # pop ITU.h/b.h
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 1)
        # ITU.h
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), True, 70)
        myTcs.counter().inc(PpToken.PpToken('ITU.h', 'identifier'), False, 70)
        myFigr.graph.retLatestNode(myFs).setTokenCounter(myTcs.pop())
        myFs.pop()
        self.assertEqual(len(myFs), 0)
        myTcs.close()
        expGraph = """PreInclude_00 [156, 8]:  True "a >= b+2" "Forced PreInclude_00"
PreInclude_01 [83, 7]:  True "x > 1" "Forced PreInclude_00"
ITU.h [140, 70]:  True "" "CP=."
000015: #include a.h
        a.h [2, 1]:  True "" "CP=."
        000017: #include aa.h
                aa.h [4, 2]:  True "" "CP=."
        000019: #include ab.h
                ab.h [8, 4]:  True "" "CP=."
000115: #include b.h
        b.h [16, 8]:  True "" "CP=."
        000117: #include ba.h
                ba.h [32, 16]:  True "" "CP=."
        000119: #include bb.h
                bb.h [64, 32]:  True "" "CP=.\""""
        print()
        print(expGraph)
        print()
        print(str(myFigr))
        print()
        myFigr.dumpGraph()
        self.assertEqual(expGraph, str(myFigr))
        # Now visit the graph
        myVis = FileIncludeGraph.FigVisitorTree(IncGraphSVG.SVGTreeNode)
        myFigr.acceptVisitor(myVis)
        # Tree is now a graph of IncGraphSVG.SVGTreeNode
        myIgs = myVis.tree()
        print()
        print('myIgs')
        #print myIgs
        myIgs.dumpToStream()
        print()
        # Create a plot configuration
        myTpt = TreePlotTransform.TreePlotTransform(myIgs.plotCanvas, 'top', '-')
        mySvg = io.StringIO()
        myIgs.plotToFileObj(mySvg, myTpt)
        print()
        print(mySvg.getvalue())


def unitTest(theVerbosity=2):
    """Execute unit tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIncGraphSVGVisitor)
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhase_1))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

#################
# End: Unit tests
#################

def usage():
    """Send the help to stdout."""
    print("""TestIncGraphSVG.py - A module that tests IncGraphSVG module.
Usage:
python TestIncGraphSVG.py [-lh --help]

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
""")

def main():
    """Invoke unit test code."""
    print('IncGraphSVG.py script version "%s", dated %s' % (__version__, __date__))
    print('Author: %s' % __author__)
    print(__rights__)
    print()
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:", ["help",])
    except getopt.GetoptError:
        usage()
        print('ERROR: Invalid options!')
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
        print('ERROR: Wrong number of arguments!')
        sys.exit(1)
    # Initialise logging etc.
    logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    clkStart = time.clock()
    unitTest()
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
