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
import time
import logging

from cpip.util import StrTree

######################
# Section: Unit tests.
######################
import unittest

class TestStrTree(unittest.TestCase):
    """Tests StrTree."""
    def test_00(self):
        """StrTree: test_00(): simple test."""
        myV = set(('#',))
        mySt = StrTree.StrTree(myV)
        #print mySt.values()
        #print str(mySt)
        self.assertEqual(1, mySt.has('#'))
        self.assertEqual(1, mySt.has('##'))
        self.assertEqual(1, mySt.has('###'))
        self.assertEqual(1, mySt.has('####'))
        self.assertEqual(1, mySt.has('#####'))
        self.assertEquals(myV, set(mySt.values()))
        #self.assertRaises(StopIteration, myG.next)

    def test_01(self):
        """StrTree: test_01(): simple test."""
        myV = set(('#', '###',))
        mySt = StrTree.StrTree(myV)
        #print mySt.values()
        #print str(mySt)
        self.assertEqual(1, mySt.has('#'))
        self.assertEqual(1, mySt.has('##'))
        self.assertEqual(3, mySt.has('###'))
        self.assertEqual(3, mySt.has('####'))
        self.assertEqual(3, mySt.has('#####'))
        self.assertEquals(myV, set(mySt.values()))
        #self.assertRaises(StopIteration, myG.next)

    def test_02(self):
        """StrTree: test_02(): empty."""
        myV = set()
        mySt = StrTree.StrTree(myV)
        #print mySt.values()
        #print str(mySt)
        self.assertEqual(0, mySt.has(''))
        self.assertEqual(0, mySt.has('#'))
        self.assertEqual(0, mySt.has('##'))
        self.assertEqual(0, mySt.has('###'))
        self.assertEqual(0, mySt.has('####'))
        self.assertEqual(0, mySt.has('#####'))
        self.assertEquals(myV, set(mySt.values()))
        #self.assertRaises(StopIteration, myG.next)

    def test_10(self):
        """StrTree: test_10(): preprocessing operators."""
        myV = set((
                '{', '}', '[', ']', '#', '##', '(', ')',
                '<:', ':>', '<%', '%>', '%:', '%:%:', ';', ':', '...',
                'new', 'delete', '?', '::', '.', '.*',
                '+', '-', '*', '/', '%', '^', '&', '|', '~',
                '!', '=', '<', '>', '+=', '-=', '*=', '/=', '%=',
                '^=', '&=', '|=', '<<', '>>', '>>=', '<<=', '==', '!=',
                '<=', '>=', '&&', '||', '++', '--', ',', '->*', '->',
                'and', 'and_eq', 'bitand', 'bitor', 'compl', 'not', 'not_eq',
                'or', 'or_eq', 'xor', 'xor_eq',
                ))
        mySt = StrTree.StrTree(myV)
        #print()
        #print mySt.values()
        #print str(mySt)
        self.assertEqual(1, mySt.has('#'))
        self.assertEqual(2, mySt.has('##'))
        self.assertEqual(2, mySt.has('###'))
        self.assertEqual(2, mySt.has('####'))
        self.assertEqual(3, mySt.has('and'))
        self.assertEqual(3, mySt.has('and_'))
        self.assertEqual(3, mySt.has('and_e'))
        self.assertEqual(6, mySt.has('and_eq'))
        self.assertEquals(myV, set(mySt.values()))

    def test_11(self):
        """StrTree: test_11(): keywords (three)."""
        myV = set((
                'const',
                'const_cast',
                'continue',
                ))
        mySt = StrTree.StrTree(myV)
        #print()
        #print mySt.values()
        #print str(mySt)
        self.assertEqual(5, mySt.has('const'))
        self.assertEqual(5, mySt.has('const_'))
        self.assertEqual(5, mySt.has('const_c'))
        self.assertEqual(5, mySt.has('const_ca'))
        self.assertEqual(5, mySt.has('const_cas'))
        self.assertEqual(10, mySt.has('const_cast'))
        self.assertEquals("""False 0
"c"
 False 1
 "o"
  False 2
  "n"
   False 3
   "s"
    False 4
    "t"
     True 5
     "_"
      False 6
      "c"
       False 7
       "a"
        False 8
        "s"
         False 9
         "t"
          True 10
   "t"
    False 4
    "i"
     False 5
     "n"
      False 6
      "u"
       False 7
       "e"
        True 8""", str(mySt))
        self.assertEquals(myV, set(mySt.values()))

    def test_12(self):
        """StrTree: test_12(): keywords (a few)."""
        myV = set((
                'asm',
                'auto',
                'bool', 
                'break',
                'case',
                'catch',
                'char',
                'class',
                'const',
                'const_cast',
                'continue',
                'default',
                'delete',
                'do',
                'double',
                ))
        mySt = StrTree.StrTree(myV)
        #print()
        #print mySt.values()
        #print str(mySt)
        self.assertEqual(2, mySt.has('do'))
        self.assertEqual(2, mySt.has('dou'))
        self.assertEqual(2, mySt.has('doub'))
        self.assertEqual(2, mySt.has('doubl'))
        self.assertEqual(6, mySt.has('double'))
        self.assertEquals(myV, set(mySt.values()))
        
    def test_13(self):
        """StrTree: test_13(): keywords (all)."""
        myV = set((
                'asm', 'do', 'if', 'return', 'typedef',
                'auto', 'double', 'inline', 'short', 'typeid',
                'bool', 'dynamic_cast', 'int', 'signed', 'typename',
                'break', 'else', 'long', 'sizeof', 'union',
                'case', 'enum', 'mutable', 'static', 'unsigned',
                'catch', 'explicit', 'namespace', 'static_cast', 'using',
                'char', 'export', 'new', 'struct', 'virtual',
                'class', 'extern', 'operator', 'switch', 'void',
                'const', 'false', 'private', 'template', 'volatile',
                'const_cast', 'float', 'protected', 'this', 'wchar_t',
                'continue', 'for', 'public', 'throw', 'while',
                'default', 'friend', 'register', 'true',
                'delete', 'goto', 'reinterpret_cast', 'try',
                ))
        mySt = StrTree.StrTree(myV)
        #print()
        #print mySt.values()
        #print str(mySt)
        self.assertEqual(2, mySt.has('do'))
        self.assertEqual(2, mySt.has('dou'))
        self.assertEqual(2, mySt.has('doub'))
        self.assertEqual(2, mySt.has('doubl'))
        self.assertEqual(6, mySt.has('double'))
        self.assertEquals(myV, set(mySt.values()))
                
class TestStrTreeHas(unittest.TestCase):
    """Tests StrTree.has()."""
    def test_00(self):
        """TestStrTreeHas: test_00(): simple test."""
        myV = set(('#',))
        mySt = StrTree.StrTree(myV)
        #print mySt.values()
        #print str(mySt)
        self.assertEqual(1, mySt.has('#'))
        self.assertEqual(1, mySt.has('##'))
        self.assertEqual(1, mySt.has('###'))
        self.assertEqual(1, mySt.has('####'))
        self.assertEqual(1, mySt.has('#####'))
        self.assertEquals(myV, set(mySt.values()))
        #self.assertRaises(StopIteration, myG.next)

    def test_01(self):
        """TestStrTreeHas: test_01(): has() with offset."""
        mySt = StrTree.StrTree(['#', '##', '###'])
        #print mySt.values()
        #print str(mySt)
        self.assertEqual(1, mySt.has('#'))
        self.assertEqual(0, mySt.has(' #'))
        self.assertEqual(2, mySt.has(' #', 1))
        self.assertEqual(0, mySt.has('  #'))
        self.assertEqual(0, mySt.has('   #'))
        self.assertEqual(4, mySt.has('123#', 3))
        self.assertEqual(5, mySt.has('123##', 3))
        self.assertEqual(6, mySt.has('123###', 3))
        self.assertEqual(6, mySt.has('123####', 3))
        self.assertEqual(6, mySt.has('123#####', 3))


class TestStrTreePerf(unittest.TestCase):
    """Tests StrTree.has() performance."""
    def test_00(self):
        """TestStrTreePerf: test_00(): keyword performance."""
        myV = set((
                'asm', 'do', 'if', 'return', 'typedef',
                'auto', 'double', 'inline', 'short', 'typeid',
                'bool', 'dynamic_cast', 'int', 'signed', 'typename',
                'break', 'else', 'long', 'sizeof', 'union',
                'case', 'enum', 'mutable', 'static', 'unsigned',
                'catch', 'explicit', 'namespace', 'static_cast', 'using',
                'char', 'export', 'new', 'struct', 'virtual',
                'class', 'extern', 'operator', 'switch', 'void',
                'const', 'false', 'private', 'template', 'volatile',
                'const_cast', 'float', 'protected', 'this', 'wchar_t',
                'continue', 'for', 'public', 'throw', 'while',
                'default', 'friend', 'register', 'true',
                'delete', 'goto', 'reinterpret_cast', 'try',
                ))
        myVList = [
                'asm', 'do', 'if', 'return', 'typedef',
                'auto', 'double', 'inline', 'short', 'typeid',
                'bool', 'dynamic_cast', 'int', 'signed', 'typename',
                'break', 'else', 'long', 'sizeof', 'union',
                'case', 'enum', 'mutable', 'static', 'unsigned',
                'catch', 'explicit', 'namespace', 'static_cast', 'using',
                'char', 'export', 'new', 'struct', 'virtual',
                'class', 'extern', 'operator', 'switch', 'void',
                'const', 'false', 'private', 'template', 'volatile',
                'const_cast', 'float', 'protected', 'this', 'wchar_t',
                'continue', 'for', 'public', 'throw', 'while',
                'default', 'friend', 'register', 'true',
                'delete', 'goto', 'reinterpret_cast', 'try',
                ]
        mySt = StrTree.StrTree(myV)
        self.assertEquals(myV, set(mySt.values()))
        print()
        #print mySt.values()
        #print str(mySt)
        count = 10000
        print('Loop count: %d' % count)
        FW = 32
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if mySt.has('do'):
                cntrFound += 1
        #sys.stderr.write('has("do"):     %8d, Time: %8.3f (s)s ... ' % (count, time.clock() - cStart))
        print('%-*s Time: %8.3f (s)s ... ' % (FW, 'has("do")', time.clock() - cStart))
        self.assertEqual(count, cntrFound)
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if 'do' in myV:
                cntrFound += 1
        print('%-*s Time: %8.3f (s)s ... ' % (FW, '"do" in set:', time.clock() - cStart))
        self.assertEqual(count, cntrFound)
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if 'do' in myVList:
                cntrFound += 1
        print('%-*s Time: %8.3f (s)s ... ' % (FW, '"do" in list:', time.clock() - cStart))
        self.assertEqual(count, cntrFound)
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if mySt.has('double'):
                cntrFound += 1
        print('%-*s Time: %8.3f (s)s ... ' % (FW, 'has("double"):', time.clock() - cStart))
        self.assertEqual(count, cntrFound)
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if 'double' in myV:
                cntrFound += 1
        print('%-*s Time: %8.3f (s)s ... ' % (FW, '"double" in set:', time.clock() - cStart))
        self.assertEqual(count, cntrFound)
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if 'double' in myVList:
                cntrFound += 1
        print('%-*s Time: %8.3f (s)s ... ' % (FW, '"double" in list:', time.clock() - cStart))
        self.assertEqual(count, cntrFound)
        #'reinterpret_cast'
        self.assertEqual(count, cntrFound)
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if mySt.has('double'):
                cntrFound += 1
        print('%-*s Time: %8.3f (s)s ... ' % (FW, 'has("reinterpret_cast"):', time.clock() - cStart))
        self.assertEqual(count, cntrFound)
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if 'reinterpret_cast' in myV:
                cntrFound += 1
        print('%-*s Time: %8.3f (s)s ... ' % (FW, '"reinterpret_cast" in set:', time.clock() - cStart))
        self.assertEqual(count, cntrFound)
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if 'reinterpret_cast' in myVList:
                cntrFound += 1
        print('%-*s Time: %8.3f (s)s ... ' % (FW, '"reinterpret_cast" in list:', time.clock() - cStart))
        self.assertEqual(count, cntrFound)
        #'strubbish'
        self.assertEqual(count, cntrFound)
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if mySt.has('strubbish'):
                cntrFound += 1
        print('%-*s Time: %8.3f (s)s ... ' % (FW, 'has("strubbish"):', time.clock() - cStart))
        self.assertEqual(0, cntrFound)
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if 'strubbish' in myV:
                cntrFound += 1
        print('%-*s Time: %8.3f (s)s ... ' % (FW, '"strubbish" in set:', time.clock() - cStart))
        self.assertEqual(0, cntrFound)
        cntrFound = 0
        cStart = time.clock()
        for i in range(count):
            if 'strubbish' in myVList:
                cntrFound += 1
        print('%-*s Time: %8.3f (s)s ... ' % (FW, '"strubbish" in list:', time.clock() - cStart))
        self.assertEqual(0, cntrFound)

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStrTree))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStrTreeHas))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStrTreePerf))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print(\
"""TestStrTree.py - A module that tests StrTree module.
Usage:
python TestStrTree.py [-lh --help]

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
)
    
def main():
    """Invoke unit test code."""
    print('TestStrTree.py script version "%s", dated %s' % (__version__, __date__))
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
