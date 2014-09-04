#!/usr/bin/env python
# CPIP is a C/C++ Preprocessor implemented in Python.
# Copyright (C) 2008-2014 Paul Ross
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

"""Tests for ItuToHtml.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import sys
#import os
import unittest
import time
import logging
#import pprint

import io

#try:
#    from xml.etree import cElementTree as etree
#except ImportError:
#    from xml.etree import ElementTree as etree

#sys.path.append(os.path.join(os.pardir + os.sep))
#===============================================================================
# import pprint
# pprint.pprint(sys.path)
#===============================================================================
from cpip import ItuToHtml

#######################################
# Section: Unit tests
########################################
class TestBase(unittest.TestCase):
    """Test the simple stuff."""
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_00(self):
        """TestBase.test_00(): setUp() and tearDown()."""
        pass

class TestItuToHtmlPhase3(unittest.TestCase):
    """Test the ItuToHtml translation phase 3."""
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_00(self):
        """TestItuToHtmlPhase3.test_00(): setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestItuToHtmlPhase3.test_01(): Empty string."""
        myOutput = io.StringIO()
        ItuToHtml.ItuToHtml(io.StringIO(u''), myOutput, writeAnchors=True)
#         print(myOutput.getvalue())
        expVal = """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <link href="cpip.css" rel="stylesheet" type="text/css" />
    <title>File: Unknown</title>
  </head>
  <body>
    <h1>File: Unknown</h1>
    <pre><a name="1" /><span class="line">       1:</span> </pre>
  </body>
</html>
"""
        self.assertEquals(myOutput.getvalue(), expVal)
    
    def test_02(self):
        """TestItuToHtmlPhase3.test_02(): Macro."""
        myStr = u'#define OBJ_LIKE /* white space */ (1-1) /* other */\n'
        myOutput = io.StringIO()
        ItuToHtml.ItuToHtml(io.StringIO(myStr), myOutput, writeAnchors=True)
#         print(myOutput.getvalue())
        expVal = """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <link href="cpip.css" rel="stylesheet" type="text/css" />
    <title>File: Unknown</title>
  </head>
  <body>
    <h1>File: Unknown</h1>
    <pre><a name="1" /><span class="line">       1:</span> <span class="f">#</span><span class="n">define</span> <span class="b">OBJ_LIKE</span> <span class="k">/* white space */</span> <span class="f">(</span><span class="c">1</span><span class="f">-</span><span class="c">1</span><span class="f">)</span> <span class="k">/* other */</span>
<a name="2" /><span class="line">       2:</span> </pre>
  </body>
</html>
"""
        self.assertEquals(myOutput.getvalue(), expVal)
    
    def test_03(self):
        """TestItuToHtmlPhase3.test_03(): ISO/IEC 9899:1999 (E) 6.10.3.5-5 EXAMPLE 3"""
        myStr = u"""#define x 3
#define f(a) f(x * (a))
#undef x
#define x 2
#define g f
#define z z[0]
#define h g(~
#define m(a) a(w)
#define w 0,1
#define t(a) a
#define p() int
#define q(x) x
#define r(x,y) x ## y
#define str(x) # x
f(y+1) + f(f(z)) % t(t(g)(0) + t)(1);
g(x+(3,4)-w) | h 5) & m
(f)^m(m);
p() i[q()] = { q(1), r(2,3), r(4,), r(,5), r(,) };
char c[2][6] = { str(hello), str() };
"""
        myOutput = io.StringIO()
        ItuToHtml.ItuToHtml(io.StringIO(myStr), myOutput, writeAnchors=True)
#         print(myOutput.getvalue())
        expVal = """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <link href="cpip.css" rel="stylesheet" type="text/css" />
    <title>File: Unknown</title>
  </head>
  <body>
    <h1>File: Unknown</h1>
    <pre><a name="1" /><span class="line">       1:</span> <span class="f">#</span><span class="n">define</span> <span class="b">x</span> <span class="c">3</span>
<a name="2" /><span class="line">       2:</span> <span class="f">#</span><span class="n">define</span> <span class="b">f</span><span class="f">(</span><span class="b">a</span><span class="f">)</span> <span class="b">f</span><span class="f">(</span><span class="b">x</span> <span class="f">*</span> <span class="f">(</span><span class="b">a</span><span class="f">)</span><span class="f">)</span>
<a name="3" /><span class="line">       3:</span> <span class="f">#</span><span class="n">undef</span> <span class="b">x</span>
<a name="4" /><span class="line">       4:</span> <span class="f">#</span><span class="n">define</span> <span class="b">x</span> <span class="c">2</span>
<a name="5" /><span class="line">       5:</span> <span class="f">#</span><span class="n">define</span> <span class="b">g</span> <span class="b">f</span>
<a name="6" /><span class="line">       6:</span> <span class="f">#</span><span class="n">define</span> <span class="b">z</span> <span class="b">z</span><span class="f">[</span><span class="c">0</span><span class="f">]</span>
<a name="7" /><span class="line">       7:</span> <span class="f">#</span><span class="n">define</span> <span class="b">h</span> <span class="b">g</span><span class="f">(</span><span class="f">~</span>
<a name="8" /><span class="line">       8:</span> <span class="f">#</span><span class="n">define</span> <span class="b">m</span><span class="f">(</span><span class="b">a</span><span class="f">)</span> <span class="b">a</span><span class="f">(</span><span class="b">w</span><span class="f">)</span>
<a name="9" /><span class="line">       9:</span> <span class="f">#</span><span class="n">define</span> <span class="b">w</span> <span class="c">0</span><span class="f">,</span><span class="c">1</span>
<a name="10" /><span class="line">      10:</span> <span class="f">#</span><span class="n">define</span> <span class="b">t</span><span class="f">(</span><span class="b">a</span><span class="f">)</span> <span class="b">a</span>
<a name="11" /><span class="line">      11:</span> <span class="f">#</span><span class="n">define</span> <span class="b">p</span><span class="f">(</span><span class="f">)</span> <span class="m">int</span>
<a name="12" /><span class="line">      12:</span> <span class="f">#</span><span class="n">define</span> <span class="b">q</span><span class="f">(</span><span class="b">x</span><span class="f">)</span> <span class="b">x</span>
<a name="13" /><span class="line">      13:</span> <span class="f">#</span><span class="n">define</span> <span class="b">r</span><span class="f">(</span><span class="b">x</span><span class="f">,</span><span class="b">y</span><span class="f">)</span> <span class="b">x</span> <span class="f">##</span> <span class="b">y</span>
<a name="14" /><span class="line">      14:</span> <span class="f">#</span><span class="n">define</span> <span class="b">str</span><span class="f">(</span><span class="b">x</span><span class="f">)</span> <span class="f">#</span> <span class="b">x</span>
<a name="15" /><span class="line">      15:</span> <span class="b">f</span><span class="f">(</span><span class="b">y</span><span class="f">+</span><span class="c">1</span><span class="f">)</span> <span class="f">+</span> <span class="b">f</span><span class="f">(</span><span class="b">f</span><span class="f">(</span><span class="b">z</span><span class="f">)</span><span class="f">)</span> <span class="f">%</span> <span class="b">t</span><span class="f">(</span><span class="b">t</span><span class="f">(</span><span class="b">g</span><span class="f">)</span><span class="f">(</span><span class="c">0</span><span class="f">)</span> <span class="f">+</span> <span class="b">t</span><span class="f">)</span><span class="f">(</span><span class="c">1</span><span class="f">)</span><span class="f">;</span>
<a name="16" /><span class="line">      16:</span> <span class="b">g</span><span class="f">(</span><span class="b">x</span><span class="f">+</span><span class="f">(</span><span class="c">3</span><span class="f">,</span><span class="c">4</span><span class="f">)</span><span class="f">-</span><span class="b">w</span><span class="f">)</span> <span class="f">|</span> <span class="b">h</span> <span class="c">5</span><span class="f">)</span> <span class="f">&amp;</span> <span class="b">m</span>
<a name="17" /><span class="line">      17:</span> <span class="f">(</span><span class="b">f</span><span class="f">)</span><span class="f">^</span><span class="b">m</span><span class="f">(</span><span class="b">m</span><span class="f">)</span><span class="f">;</span>
<a name="18" /><span class="line">      18:</span> <span class="b">p</span><span class="f">(</span><span class="f">)</span> <span class="b">i</span><span class="f">[</span><span class="b">q</span><span class="f">(</span><span class="f">)</span><span class="f">]</span> <span class="f">=</span> <span class="f">{</span> <span class="b">q</span><span class="f">(</span><span class="c">1</span><span class="f">)</span><span class="f">,</span> <span class="b">r</span><span class="f">(</span><span class="c">2</span><span class="f">,</span><span class="c">3</span><span class="f">)</span><span class="f">,</span> <span class="b">r</span><span class="f">(</span><span class="c">4</span><span class="f">,</span><span class="f">)</span><span class="f">,</span> <span class="b">r</span><span class="f">(</span><span class="f">,</span><span class="c">5</span><span class="f">)</span><span class="f">,</span> <span class="b">r</span><span class="f">(</span><span class="f">,</span><span class="f">)</span> <span class="f">}</span><span class="f">;</span>
<a name="19" /><span class="line">      19:</span> <span class="m">char</span> <span class="b">c</span><span class="f">[</span><span class="c">2</span><span class="f">]</span><span class="f">[</span><span class="c">6</span><span class="f">]</span> <span class="f">=</span> <span class="f">{</span> <span class="b">str</span><span class="f">(</span><span class="b">hello</span><span class="f">)</span><span class="f">,</span> <span class="b">str</span><span class="f">(</span><span class="f">)</span> <span class="f">}</span><span class="f">;</span>
<a name="20" /><span class="line">      20:</span> </pre>
  </body>
</html>
"""
        self.assertEquals(myOutput.getvalue(), expVal)

class TestItuToHtmlTokenGen(unittest.TestCase):
    """Test the ItuToHtml token genreator."""
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_00(self):
        """TestItuToHtmlTokenGen.test_00(): setUp() and tearDown()."""
        pass
    
    def test_01(self):
        """TestItuToHtmlTokenGen.test_01(): Hello world."""
        myStr = u"""#include <iostream>

using namespace std;

void main()
{
    cout << "Hello World!" << endl;
    cout << "Welcome to C++ Programming" << endl;
}
"""
        myOutput = io.StringIO()
        ItuToHtml.ItuToHtml(io.StringIO(myStr), myOutput, writeAnchors=True)
#         print(myOutput.getvalue())
        expVal = """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <link href="cpip.css" rel="stylesheet" type="text/css" />
    <title>File: Unknown</title>
  </head>
  <body>
    <h1>File: Unknown</h1>
    <pre><a name="1" /><span class="line">       1:</span> <span class="f">#</span><span class="n">include</span> <span class="f">&lt;</span><span class="b">iostream</span><span class="f">&gt;</span>
<a name="2" /><span class="line">       2:</span> 
<a name="3" /><span class="line">       3:</span> <span class="m">using</span> <span class="m">namespace</span> <span class="b">std</span><span class="f">;</span>
<a name="4" /><span class="line">       4:</span> 
<a name="5" /><span class="line">       5:</span> <span class="m">void</span> <span class="b">main</span><span class="f">(</span><span class="f">)</span>
<a name="6" /><span class="line">       6:</span> <span class="f">{</span>
<a name="7" /><span class="line">       7:</span>     <span class="b">cout</span> <span class="f">&lt;&lt;</span> <span class="e">&quot;Hello World!&quot;</span> <span class="f">&lt;&lt;</span> <span class="b">endl</span><span class="f">;</span>
<a name="8" /><span class="line">       8:</span>     <span class="b">cout</span> <span class="f">&lt;&lt;</span> <span class="e">&quot;Welcome to C++ Programming&quot;</span> <span class="f">&lt;&lt;</span> <span class="b">endl</span><span class="f">;</span>
<a name="9" /><span class="line">       9:</span> <span class="f">}</span>
<a name="10" /><span class="line">      10:</span> </pre>
  </body>
</html>
"""
        self.assertEquals(myOutput.getvalue(), expVal)

    def test_02(self):
        """TestItuToHtmlTokenGen.test_02(): Literals."""
        myStr = u"""char c = 'c';
long l = 42L;
int i = 42;
float f = 1.234E-27 ;
int o = 0123;
int h = 0xABC;
const char* s = "Hello world";
"""
        myOutput = io.StringIO()
        ItuToHtml.ItuToHtml(io.StringIO(myStr), myOutput, writeAnchors=True)
#         print(myOutput.getvalue())
        expVal = """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <link href="cpip.css" rel="stylesheet" type="text/css" />
    <title>File: Unknown</title>
  </head>
  <body>
    <h1>File: Unknown</h1>
    <pre><a name="1" /><span class="line">       1:</span> <span class="m">char</span> <span class="b">c</span> <span class="f">=</span> <span class="d">&apos;c&apos;</span><span class="f">;</span>
<a name="2" /><span class="line">       2:</span> <span class="m">long</span> <span class="b">l</span> <span class="f">=</span> <span class="c">42L</span><span class="f">;</span>
<a name="3" /><span class="line">       3:</span> <span class="m">int</span> <span class="b">i</span> <span class="f">=</span> <span class="c">42</span><span class="f">;</span>
<a name="4" /><span class="line">       4:</span> <span class="m">float</span> <span class="b">f</span> <span class="f">=</span> <span class="c">1.234E-27</span> <span class="f">;</span>
<a name="5" /><span class="line">       5:</span> <span class="m">int</span> <span class="b">o</span> <span class="f">=</span> <span class="c">0123</span><span class="f">;</span>
<a name="6" /><span class="line">       6:</span> <span class="m">int</span> <span class="b">h</span> <span class="f">=</span> <span class="c">0xABC</span><span class="f">;</span>
<a name="7" /><span class="line">       7:</span> <span class="m">const</span> <span class="m">char</span><span class="f">*</span> <span class="b">s</span> <span class="f">=</span> <span class="e">&quot;Hello world&quot;</span><span class="f">;</span>
<a name="8" /><span class="line">       8:</span> </pre>
  </body>
</html>
"""
        self.assertEquals(myOutput.getvalue(), expVal)

class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    """Execute unit tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestItuToHtmlPhase3))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestItuToHtmlTokenGen))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))

#################
# End: Unit tests
#################

def usage():
    """Send the help to stdout."""
    print("""TestItuToHtml.py - A module that tests ItuToHtml module.
Usage:
python TestItuToHtml.py [-lh --help]

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
    print('TestItuToHtml.py script version "%s", dated %s' % (__version__, __date__))
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
