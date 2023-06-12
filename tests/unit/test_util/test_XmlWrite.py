#!/usr/bin/env python
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
__author__  = 'Paul Ross'
__date__    = '2009-09-15'
__rights__  = 'Copyright (c) Paul Ross'

"""Tests XmlWrite."""

import os
import sys
import time
import logging
import io

from cpip.util import XmlWrite

######################
# Section: Unit tests.
######################
import unittest

class TestXmlWrite_encode_decode(unittest.TestCase):
    """Tests XmlWrite encode and decode string."""
    def test_encodeString(self):
        self.assertEqual(XmlWrite.encodeString('foo'), '_Zm9v')
        self.assertEqual(XmlWrite.encodeString('foo', '_'), '_Zm9v')
        self.assertEqual(XmlWrite.encodeString('foo', '+'), '+Zm9v')
        self.assertEqual(XmlWrite.encodeString('http://www.w3.org/TR/1999/REC-html401-19991224/types.html#type-cdata'),
                         '_aHR0cDovL3d3dy53My5vcmcvVFIvMTk5OS9SRUMtaHRtbDQwMS0xOTk5MTIyNC90eXBlcy5odG1sI3R5cGUtY2RhdGE_')

    def test_encodeString_bad_prefix_raises(self):
        self.assertTrue(XmlWrite.RAISE_ON_ERROR)
        self.assertRaises(XmlWrite.ExceptionXml, XmlWrite.encodeString, 'foo', 'bar')

    def test_decodeString(self):
        self.assertEqual(XmlWrite.decodeString('_Zm9v'), b'foo')

    def test_nameFromString(self):
        self.assertEqual(XmlWrite.nameFromString('foo'), 'ZZm9v')
        self.assertEqual(XmlWrite.nameFromString('http://www.w3.org/TR/1999/REC-html401-19991224/types.html#type-cdata'),
                         'ZaHR0cDovL3d3dy53My5vcmcvVFIvMTk5OS9SRUMtaHRtbDQwMS0xOTk5MTIyNC90eXBlcy5odG1sI3R5cGUtY2RhdGE_')

class TestXmlWrite(unittest.TestCase):
    """Tests XmlWrite."""
    def test_00(self):
        """TestXmlWrite.test_00(): construction."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF):
            pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>\n""")
        
    def test_01(self):
        """TestXmlWrite.test_01(): simple elements."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                with XmlWrite.Element(xS, 'A', {'attr_1' : '1'}):
                    pass
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0">
  <A attr_1="1" />
</Root>
""")
       
    def test_02(self):
        """TestXmlWrite.test_02(): mixed content."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                with XmlWrite.Element(xS, 'A', {'attr_1' : '1'}):
                    xS.characters(u'<&>')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0">
  <A attr_1="1">&lt;&amp;&gt;</A>
</Root>
""")
       
    def test_03(self):
        """TestXmlWrite.test_03(): processing instruction."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                with XmlWrite.Element(xS, 'A', {'attr_1' : '1'}):
                    xS.pI('Do <&> this')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0">
  <A attr_1="1"><?Do &lt;&amp;&gt; this?></A>
</Root>
""")
        
    def test_04(self):
        """TestXmlWrite.test_04(): raise on endElement when empty."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            pass
        #print
        #print myF.getvalue()
        self.assertRaises(XmlWrite.ExceptionXmlEndElement, xS.endElement, '')
        
    def test_05(self):
        """TestXmlWrite.test_05(): raise on endElement missmatch."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                self.assertRaises(XmlWrite.ExceptionXmlEndElement, xS.endElement, 'NotRoot')
                with XmlWrite.Element(xS, 'A', {'attr_1' : '1'}):
                    self.assertRaises(XmlWrite.ExceptionXmlEndElement, xS.endElement, 'NotA')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0">
  <A attr_1="1" />
</Root>
""")
                       
    def test_06(self):
        """TestXmlWrite.test_06(): encoded text in 'latin-1'."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF, 'latin-1') as xS:
            with XmlWrite.Element(xS, 'Root'):
                with XmlWrite.Element(xS, 'A'):
                    xS.characters("""<&>"'""")
#                 with XmlWrite.Element(xS, 'A'):
#                     xS.characters('%s' % chr(147))
#                 with XmlWrite.Element(xS, 'A'):
#                     xS.characters(chr(65))
#                 with XmlWrite.Element(xS, 'A'):
#                     xS.characters(chr(128))
#         print()
#         print(repr(myF.getvalue()))
        # FIXME: This test is correct
#         self.assertEqual("""<?xml version='1.0' encoding="latin-1"?>
# <Root>
#   <A>&lt;&amp;&gt;&quot;&apos;</A>
#   <A>&#147;</A>
#   <A>A</A>
#   <A>&#128;</A>
# </Root>
# """,
#             myF.getvalue(),
#         )
       
    def test_07(self):
        """TestXmlWrite.test_07(): comments."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                xS.comment(u' a comment ')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0"><!-- a comment -->
</Root>
""")
       
    def test_08(self):
        """TestXmlWrite.test_08(): raise during write."""
        myF = io.StringIO()
        try:
            with XmlWrite.XmlStream(myF) as xS:
                with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                    self.assertRaises(XmlWrite.ExceptionXmlEndElement, xS.endElement, 'NotRoot')
                    with XmlWrite.Element(xS, 'E', {'attr_1' : '1'}):
                        xS._elemStk.pop()
                        xS._elemStk.append('F')
                        raise Exception('Some exception')
        except Exception as e:
            print(e)
        else:
            print('No exception raised')
#        print()
#        print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0">
  <E attr_1="1" />
</Root>
""")
                       
    def test_09(self):
        """TestXmlWrite.test_09(): literal."""
        myF = io.StringIO()
        with XmlWrite.XmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
                xS.literal(u'literal&nbsp;text')
        # print()
        # print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<Root version="12.0">literal&nbsp;text</Root>
""")



class TestXhtmlWrite(unittest.TestCase):
    """Tests TestXhtmlWrite."""
    def test_00(self):
        """TestXhtmlWrite.test_00(): construction."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF):
            pass
#        print()
#        print(myF.getvalue())
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml" />
""")
        
    def test_01(self):
        """TestXhtmlWrite.test_01(): simple example."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'head'):
                with XmlWrite.Element(xS, 'title'):
                    xS.characters(u'Virtual Library')
            with XmlWrite.Element(xS, 'body'):
                with XmlWrite.Element(xS, 'p'):
                    xS.characters(u'Moved to ')
                    with XmlWrite.Element(xS, 'a', {'href' : 'http://example.org/'}):
                        xS.characters(u'example.org')
                    xS.characters(u'.')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Virtual Library</title>
  </head>
  <body>
    <p>Moved to <a href="http://example.org/">example.org</a>.</p>
  </body>
</html>
""")
        
    def test_charactersWithBr_00(self):
        """TestXhtmlWrite.test_00(): simple example."""
        myF = io.StringIO()
        with XmlWrite.XhtmlStream(myF) as xS:
            with XmlWrite.Element(xS, 'head'):
                pass
            with XmlWrite.Element(xS, 'body'):
                with XmlWrite.Element(xS, 'p'):
                    xS.charactersWithBr(u'No break in this line.')
                with XmlWrite.Element(xS, 'p'):
                    xS.charactersWithBr(u"""Several
breaks in
this line.""")           
                with XmlWrite.Element(xS, 'p'):
                    xS.charactersWithBr(u'\nBreak at beginning.')
                with XmlWrite.Element(xS, 'p'):
                    xS.charactersWithBr(u'Break at end\n')
                with XmlWrite.Element(xS, 'p'):
                    xS.charactersWithBr(u'\nBreak at beginning\nmiddle and end\n')
        #print
        #print myF.getvalue()
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head />
  <body>
    <p>No break in this line.</p>
    <p>Several<br />breaks in<br />this line.</p>
    <p><br />Break at beginning.</p>
    <p>Break at end<br /></p>
    <p><br />Break at beginning<br />middle and end<br /></p>
  </body>
</html>
""")
        
class NullClass(unittest.TestCase):
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(NullClass)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXmlWrite))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXhtmlWrite))
    myResult = unittest.TextTestRunner(verbosity=theVerbosity).run(suite)
    return (myResult.testsRun, len(myResult.errors), len(myResult.failures))
##################
# End: Unit tests.
##################

def usage():
    """Send the help to stdout."""
    print("""TestXmlWrite.py - A module that tests StrTree module.
Usage:
python TestXmlWrite.py [-lh --help]

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
    print('TestXmlWrite.py script version "%s", dated %s' % (__version__, __date__))
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
    clkStart = time.perf_counter()
    unitTest()
    clkExec = time.perf_counter() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')

if __name__ == "__main__":
    main()
