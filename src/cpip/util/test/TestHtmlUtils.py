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
"""Unit tests for ...

Created on Jun 8, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = 'Jun 8, 2011'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2011 paulross.'

#import pprint
import sys
import os
import time
import logging
import io

from cpip.util import HtmlUtils
from cpip.util import XmlWrite

######################
# Section: Unit tests.
######################
import unittest

class Test_retHtmlFileName(unittest.TestCase):
    """Tests HtmlUtils.retHtmlFileName"""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestName.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """Test_retHtmlFileName.test_01(): retHtmlFileName() - basic functionality."""
        self.assertEqual('_85815d8fcaf4100c893e42ecf798ee68.html', HtmlUtils.retHtmlFileName(''))
        self.assertEqual('foo.lis_a2264fb27d01482d85fb07d540d99d29.html', HtmlUtils.retHtmlFileName('foo.lis'))
        myPathStr = 'a very long path that goes on and on and on and you think that it will never ever stop spam.lis'
        myPath = os.path.join(*myPathStr.split())
        self.assertEqual('a/very/long/path/that/goes/on/and/on/and/on/and/you/think/that/it/will/never/ever/stop/spam.lis', myPath)
        self.assertEqual(
            'spam.lis_eb53aeb1072ab90b9ba0304c5e2b6fd9.html',
            HtmlUtils.retHtmlFileName(myPath),
        )

    def test_02(self):
        """Test_retHtmlFileName.test_02(): retHtmlFileLink() - basic functionality."""
        self.assertEqual('_85815d8fcaf4100c893e42ecf798ee68.html#4', HtmlUtils.retHtmlFileLink('', 4))
        self.assertEqual('foo.lis_a2264fb27d01482d85fb07d540d99d29.html#4', HtmlUtils.retHtmlFileLink('foo.lis', 4))
        myPathStr = 'a very long path that goes on and on and on and you think that it will never ever stop spam.lis'
        myPath = os.path.join(*myPathStr.split())
        self.assertEqual('a/very/long/path/that/goes/on/and/on/and/on/and/you/think/that/it/will/never/ever/stop/spam.lis', myPath)
        self.assertEqual(
            'spam.lis_eb53aeb1072ab90b9ba0304c5e2b6fd9.html#4',
            HtmlUtils.retHtmlFileLink(myPath, 4),
        )

class Test_XhtmlWrite(unittest.TestCase):
    """Tests TestXhtmlWrite."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """TestName.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """TestXhtmlWrite.test_01(): writeHtmlFileLink() simple."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeHtmlFileLink(myS, 'spam/eggs/chips.lis', 47, theText='Navigation text', theClass=None)
#        print()
#        print(myF.getvalue())
#        self.maxDiff = None
        self.assertEqual("""<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <a href="chips.lis_5e410d3de8868d056cd4d3367f91e769.html#47">Navigation text</a>
</html>
""",
            myF.getvalue(),
        )

    def test_02(self):
        """TestXhtmlWrite.test_02(): writeHtmlFileLink() with class."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeHtmlFileLink(myS, 'spam/eggs/chips.lis', 47, theText='Navigation text', theClass='CSS_class')
#        print()
#        print(myF.getvalue())
#        self.maxDiff = None
        self.assertEqual("""<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <a href="chips.lis_5e410d3de8868d056cd4d3367f91e769.html#47">
    <span class="CSS_class">Navigation text</span>
  </a>
</html>
""",
            myF.getvalue()
        )

    def test_03(self):
        """TestXhtmlWrite.test_03(): writeHtmlFileAnchor()."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeHtmlFileAnchor(myS, 47, theText='Navigation text')
#        print()
#        print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <a name="47" />Navigation text</html>
""")
        
    def test_04(self):
        """TestXhtmlWrite.test_04(): writeHtmlFileAnchor() with class."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeHtmlFileAnchor(myS, 47, theText='Navigation text', theClass='CSS_class')
#        print()
#        print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <a name="47" />
  <span class="CSS_class">Navigation text</span>
</html>
""")

    def test_05(self):
        """TestXhtmlWrite.test_05(): writeHtmlFileAnchor() with class and href."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeHtmlFileAnchor(myS, 47,
                                          theText='Navigation text',
                                          theClass='CSS_class',
                                          theHref='HREF_TARGET')
#        print()
#        print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <a name="47" />
  <a href="HREF_TARGET">
    <span class="CSS_class">Navigation text</span>
  </a>
</html>
""")

class Test_PathSplit(unittest.TestCase):
    """Tests TestXhtmlWrite."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """Test_PathSplit.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """Test_PathSplit.test_01(): pathSplit()"""
        self.assertEqual(['.'], HtmlUtils.pathSplit(''))
        self.assertEqual(['spam/', 'eggs.lis'], HtmlUtils.pathSplit('spam/eggs.lis'))
        self.assertEqual(['../', 'spam/', 'eggs.lis'], HtmlUtils.pathSplit('../spam/eggs.lis'))
        self.assertEqual(['../', 'eggs.lis'], HtmlUtils.pathSplit('../spam/../eggs.lis'))
        self.assertEqual(['../', 'chips/', 'eggs.lis'], HtmlUtils.pathSplit('../spam/../chips/eggs.lis'))

class Test_writeFileListAsTable(unittest.TestCase):
    """Tests TestXhtmlWrite."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """Test_writeFileListAsTable.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """Test_writeFileListAsTable.test_01(): writeFileListAsTable() - Single file list"""
        myFileNameS = [
            'eggs.lis',
            'chips.lis',
            'beans.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f)) for f in myFileNameS]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListAsTable(myS, myFileLinkS, {}, False)
#         print()
#         print(myF.getvalue())
#         self.maxDiff = None
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td>
        <a href="beans.lis_37fe59d50e21a22f770f96832a3316be.html">beans.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="chips.lis_52ff1ebbb6b180864516ab041e20da65.html">chips.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="eggs.lis_1355f6695f856c9448c806cfa562a4c4.html">eggs.lis</a>
      </td>
    </tr>
  </table>
</html>
""")

    def test_02(self):
        """Test_writeFileListAsTable.test_02(): writeFileListAsTable() - Single directory list"""
        myFileNameS = [
            'spam/eggs.lis',
            'spam/chips.lis',
            'spam/beans.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f)) for f in myFileNameS]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListAsTable(myS, myFileLinkS, {}, False)
#         print()
#         print(myF.getvalue())
#         self.maxDiff = None
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td rowspan="3">spam/</td>
      <td>
        <a href="beans.lis_2cd7aad2a1a03013720d9cc5d83b860c.html">beans.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="chips.lis_78c24a9e68057387b3f7c7de7f57385d.html">chips.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="eggs.lis_afc193e8de9a2e06454b4bf92d5fefd8.html">eggs.lis</a>
      </td>
    </tr>
  </table>
</html>
""")

    def test_03(self):
        """Test_writeFileListAsTable.test_03(): writeFileListAsTable() - Multiple directory list"""
        myFileNameS = [
            'spam/eggs.lis',
            'spam/chips.lis',
            'spam/fishfingers/beans.lis',
            'spam/fishfingers/peas.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f)) for f in myFileNameS]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListAsTable(myS, myFileLinkS, {}, False)
#         print()
#         print(myF.getvalue())
#         self.maxDiff = None
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td rowspan="4">spam/</td>
      <td colspan="2">
        <a href="chips.lis_78c24a9e68057387b3f7c7de7f57385d.html">chips.lis</a>
      </td>
    </tr>
    <tr>
      <td colspan="2">
        <a href="eggs.lis_afc193e8de9a2e06454b4bf92d5fefd8.html">eggs.lis</a>
      </td>
    </tr>
    <tr>
      <td rowspan="2">fishfingers/</td>
      <td>
        <a href="beans.lis_8c05f2bb7fd4e4946ceae7a0f0a658f1.html">beans.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="peas.lis_93ee5d4c29eb90269e47d1e20daa4110.html">peas.lis</a>
      </td>
    </tr>
  </table>
</html>
""")

    def test_04(self):
        """Test_writeFileListAsTable.test_0(): writeFileListAsTable() - Multiple directory list, includeKeyTail=True"""
        myFileNameS = [
            'spam/eggs.lis',
            'spam/chips.lis',
            'spam/fishfingers/beans.lis',
            'spam/fishfingers/peas.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f)) for f in myFileNameS]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListAsTable(myS, myFileLinkS, {}, True)
#         print()
#         print(myF.getvalue())
#         self.maxDiff = None
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td rowspan="4">spam/</td>
      <td colspan="2">chips.lis:<a href="chips.lis_78c24a9e68057387b3f7c7de7f57385d.html">chips.lis</a></td>
    </tr>
    <tr>
      <td colspan="2">eggs.lis:<a href="eggs.lis_afc193e8de9a2e06454b4bf92d5fefd8.html">eggs.lis</a></td>
    </tr>
    <tr>
      <td rowspan="2">fishfingers/</td>
      <td>beans.lis:<a href="beans.lis_8c05f2bb7fd4e4946ceae7a0f0a658f1.html">beans.lis</a></td>
    </tr>
    <tr>
      <td>peas.lis:<a href="peas.lis_93ee5d4c29eb90269e47d1e20daa4110.html">peas.lis</a></td>
    </tr>
  </table>
</html>
""")

class Test_writeFileListTrippleAsTable(unittest.TestCase):
    """Tests writeFileListTrippleAsTable()."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """Test_writeFileListTrippleAsTable.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """Test_writeFileListTrippleAsTable.test_01(): writeFileListTrippleAsTable() - Single file list"""
        myFileNameS = [
            '0eggs.lis',
            '1chips.lis',
            '2beans.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f), 'Link text {:d}'.format(i)) for i, f in enumerate(myFileNameS)]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListTrippleAsTable(myS, myFileLinkS, {}, False)
#         print()
#         print(myF.getvalue())
#         self.maxDiff = None
#        print(myFileLinkS)
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td> <a href="0eggs.lis_4656d29aa36ca0c168a10dd3ffe2c9fa.html">Link text 0</a></td>
    </tr>
    <tr>
      <td> <a href="1chips.lis_6cb5a1758e21dad3dba0cc4a53d91c31.html">Link text 1</a></td>
    </tr>
    <tr>
      <td> <a href="2beans.lis_961d8a2ab0ecf325e12f11c8bdbbf817.html">Link text 2</a></td>
    </tr>
  </table>
</html>
""")

    def test_02(self):
        """Test_writeFileListTrippleAsTable.test_02(): writeFileListTrippleAsTable() - Single directory list"""
        myFileNameS = [
            'spam/beans.lis',
            'spam/chips.lis',
            'spam/eggs.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f), 'Link text {:d}'.format(i)) for i, f in enumerate(myFileNameS)]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListTrippleAsTable(myS, myFileLinkS, {}, False)
#         print()
#         print(myF.getvalue())
#         self.maxDiff = None
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td rowspan="3">spam/</td>
      <td> <a href="beans.lis_2cd7aad2a1a03013720d9cc5d83b860c.html">Link text 0</a></td>
    </tr>
    <tr>
      <td> <a href="chips.lis_78c24a9e68057387b3f7c7de7f57385d.html">Link text 1</a></td>
    </tr>
    <tr>
      <td> <a href="eggs.lis_afc193e8de9a2e06454b4bf92d5fefd8.html">Link text 2</a></td>
    </tr>
  </table>
</html>
""")

    def test_03(self):
        """Test_writeFileListTrippleAsTable.test_03(): writeFileListTrippleAsTable() - Multiple directory list"""
        myFileNameS = [
            'spam/chips.lis',
            'spam/eggs.lis',
            'spam/fishfingers/beans.lis',
            'spam/fishfingers/peas.lis',
        ]
        myFileLinkS = [(f, HtmlUtils.retHtmlFileName(f), 'Link text {:d}'.format(i)) for i, f in enumerate(myFileNameS)]
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFileListTrippleAsTable(myS, myFileLinkS, {}, False)
#         print()
#         print(myF.getvalue())
#         self.maxDiff = None
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td rowspan="4">spam/</td>
      <td colspan="2"> <a href="chips.lis_78c24a9e68057387b3f7c7de7f57385d.html">Link text 0</a></td>
    </tr>
    <tr>
      <td colspan="2"> <a href="eggs.lis_afc193e8de9a2e06454b4bf92d5fefd8.html">Link text 1</a></td>
    </tr>
    <tr>
      <td rowspan="2">fishfingers/</td>
      <td> <a href="beans.lis_8c05f2bb7fd4e4946ceae7a0f0a658f1.html">Link text 2</a></td>
    </tr>
    <tr>
      <td> <a href="peas.lis_93ee5d4c29eb90269e47d1e20daa4110.html">Link text 3</a></td>
    </tr>
  </table>
</html>
""")

class Special(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(Special)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_retHtmlFileName))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_XhtmlWrite))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_PathSplit))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_writeFileListAsTable))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_writeFileListTrippleAsTable))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestClass.py - A module that tests something.
Usage:
python TestClass.py [-lh --help]

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
    print(('TestClass.py script version "%s", dated %s' % (__version__, __date__)))
    print(('Author: %s' % __author__))
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
    print(('CPU time = %8.3f (S)' % clkExec))
    print('Bye, bye!')

if __name__ == "__main__":
    main()
