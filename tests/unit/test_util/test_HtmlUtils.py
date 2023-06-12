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
"""Unit tests for ...

Created on Jun 8, 2011

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = 'Jun 8, 2011'
__rights__  = 'Copyright (c) 2011 paulross.'

import hashlib
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
        """TestName.test_00(): Tests setUp() and tearDown().
        Also tests hashlib.md5"""
        # True for Python 2.7 and 3.6
        exp = 'd41d8cd98f00b204e9800998ecf8427e'
        self.assertEqual(hashlib.md5(b'').hexdigest(), exp)

    def test_01(self):
        """Test_retHtmlFileName.test_01(): retHtmlFileName() - basic functionality."""
#         exp = hashlib.md5(bytes(os.path.abspath(''), 'ascii')).hexdigest()
#         print(hashlib.md5(bytes(os.path.abspath(''), 'ascii')).hexdigest())
#         print(hashlib.md5(bytes(os.path.normpath(''), 'ascii')).hexdigest())
        self.assertEqual('_5058f1af8388633f609cadb75a75dc9d.html',
                         HtmlUtils.retHtmlFileName(''))
        self.assertEqual('foo.lis_7cc7c6edbd4c065f2406358e9211d9eb.html',
                         HtmlUtils.retHtmlFileName('foo.lis'))
        myPathStr = 'a very long path that goes on and on and on and you think that it will never ever stop spam.lis'
        myPath = os.path.join(*myPathStr.split())
        self.assertEqual('a/very/long/path/that/goes/on/and/on/and/on/and/you/think/that/it/will/never/ever/stop/spam.lis', myPath)
        self.assertEqual(
            'spam.lis_899456b1d7f9e35f3f5338b5883ae262.html',
            HtmlUtils.retHtmlFileName(myPath),
        )

    def test_02(self):
        """Test_retHtmlFileName.test_02(): retHtmlFileLink() - basic functionality."""
        self.assertEqual('_5058f1af8388633f609cadb75a75dc9d.html#4', HtmlUtils.retHtmlFileLink('', 4))
        self.assertEqual('foo.lis_7cc7c6edbd4c065f2406358e9211d9eb.html#4', HtmlUtils.retHtmlFileLink('foo.lis', 4))
        myPathStr = 'a very long path that goes on and on and on and you think that it will never ever stop spam.lis'
        myPath = os.path.join(*myPathStr.split())
        self.assertEqual('a/very/long/path/that/goes/on/and/on/and/on/and/you/think/that/it/will/never/ever/stop/spam.lis', myPath)
        self.assertEqual(
            'spam.lis_899456b1d7f9e35f3f5338b5883ae262.html#4',
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
  <a href="chips.lis_e62fa1654e1857c70203c398c0cbe27d.html#47">Navigation text</a>
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
  <a href="chips.lis_e62fa1654e1857c70203c398c0cbe27d.html#47">
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
        <a href="beans.lis_0041e5194bf9f9efa9f26d5a2139a418.html">beans.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="chips.lis_cb7a31031b69325af0e4d341041c4844.html">chips.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="eggs.lis_66b549ff0dd23f61d7ea822aa9549756.html">eggs.lis</a>
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
        <a href="beans.lis_85ae02d1d72c7fa819c834e55cd4b1c2.html">beans.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="chips.lis_cf88bd52fd64d0ee6dd7f9f7d465d22b.html">chips.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="eggs.lis_bc8a04943b99ef250322263f7f263272.html">eggs.lis</a>
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
        <a href="chips.lis_cf88bd52fd64d0ee6dd7f9f7d465d22b.html">chips.lis</a>
      </td>
    </tr>
    <tr>
      <td colspan="2">
        <a href="eggs.lis_bc8a04943b99ef250322263f7f263272.html">eggs.lis</a>
      </td>
    </tr>
    <tr>
      <td rowspan="2">fishfingers/</td>
      <td>
        <a href="beans.lis_a50e730e7b0104f5a34f3aca74fd03b0.html">beans.lis</a>
      </td>
    </tr>
    <tr>
      <td>
        <a href="peas.lis_08179aa1bc47182a36430dafec259742.html">peas.lis</a>
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
      <td colspan="2">chips.lis:<a href="chips.lis_cf88bd52fd64d0ee6dd7f9f7d465d22b.html">chips.lis</a></td>
    </tr>
    <tr>
      <td colspan="2">eggs.lis:<a href="eggs.lis_bc8a04943b99ef250322263f7f263272.html">eggs.lis</a></td>
    </tr>
    <tr>
      <td rowspan="2">fishfingers/</td>
      <td>beans.lis:<a href="beans.lis_a50e730e7b0104f5a34f3aca74fd03b0.html">beans.lis</a></td>
    </tr>
    <tr>
      <td>peas.lis:<a href="peas.lis_08179aa1bc47182a36430dafec259742.html">peas.lis</a></td>
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
#         print(myFileLinkS)
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td> <a href="0eggs.lis_55d1c28c70fa11242791f484339eb1be.html">Link text 0</a></td>
    </tr>
    <tr>
      <td> <a href="1chips.lis_9d8f17f73fd3f595dcdc0d6cb43efee2.html">Link text 1</a></td>
    </tr>
    <tr>
      <td> <a href="2beans.lis_c191c76d1f99127750d4f05f0d47e101.html">Link text 2</a></td>
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
      <td> <a href="beans.lis_85ae02d1d72c7fa819c834e55cd4b1c2.html">Link text 0</a></td>
    </tr>
    <tr>
      <td> <a href="chips.lis_cf88bd52fd64d0ee6dd7f9f7d465d22b.html">Link text 1</a></td>
    </tr>
    <tr>
      <td> <a href="eggs.lis_bc8a04943b99ef250322263f7f263272.html">Link text 2</a></td>
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
        # print()
        # print(myF.getvalue())
        self.maxDiff = None
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table>
    <tr>
      <td rowspan="4">spam/</td>
      <td colspan="2"> <a href="chips.lis_cf88bd52fd64d0ee6dd7f9f7d465d22b.html">Link text 0</a></td>
    </tr>
    <tr>
      <td colspan="2"> <a href="eggs.lis_bc8a04943b99ef250322263f7f263272.html">Link text 1</a></td>
    </tr>
    <tr>
      <td rowspan="2">fishfingers/</td>
      <td> <a href="beans.lis_a50e730e7b0104f5a34f3aca74fd03b0.html">Link text 2</a></td>
    </tr>
    <tr>
      <td> <a href="peas.lis_08179aa1bc47182a36430dafec259742.html">Link text 3</a></td>
    </tr>
  </table>
</html>
""")

class Test_writeFilePathsAsTable(unittest.TestCase):
    """Tests writeFilePathsAsTable()."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def test_00(self):
        """Test_writeFilePathsAsTable.test_00(): Tests setUp() and tearDown()."""
        pass

    def test_01(self):
        """Test_writeFilePathsAsTable.test_01(): writeFilePathsAsTable() - """
        myF = io.StringIO()
        myFileNameValueS = [
            # filename, (href, navText, file_data) where file data is count_inc, count_lines, count_bytes
            ('spam/chips.lis', ('chips.html', 'Chips', (1, 2, 3))),
            ('spam/eggs.lis', ('eggs.html', 'Eggs', (10, 11, 12))),
            ('spam/fishfingers/beans.lis', ('fishfingers/beans.html', 'Beans', (100, 101, 102))),
            ('spam/fishfingers/peas.lis', ('fishfingers/peas.html', 'Peas', (1000, 1001, 1002))),
        ]
        def _tdCallback(theS, attrs, _k, href_nav_text_file_data):
            """Callback function for the file count table. This comes from CPIPMain.py"""
            attrs['class'] = 'filetable'
            href, navText, file_data = href_nav_text_file_data
            with XmlWrite.Element(theS, 'td', attrs):
                with XmlWrite.Element(theS, 'a', {'href' : href}):
                    # Write the nav text
                    theS.characters(navText)
            td_attrs = {
                'width' : "36px",
                'class' : 'filetable',
                'align' : "right",
            }
            count_inc, count_lines, count_bytes = file_data
            with XmlWrite.Element(theS, 'td', td_attrs):
                # Write the file count of inclusions
                theS.characters('%d' % count_inc)
            with XmlWrite.Element(theS, 'td', td_attrs):
                # Write the file count of lines
                theS.characters('{:,d}'.format(count_lines))
            with XmlWrite.Element(theS, 'td', td_attrs):
                # Write the file count of bytes
                theS.characters('{:,d}'.format(count_bytes))
            with XmlWrite.Element(theS, 'td', td_attrs):
                # Write the file count of lines * inclusions
                theS.characters('{:,d}'.format(count_lines * count_inc))
            with XmlWrite.Element(theS, 'td', td_attrs):
                # Write the file count of bytes * inclusions
                theS.characters('{:,d}'.format(count_bytes * count_inc))

        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFilePathsAsTable(None, myS, myFileNameValueS, 'table_style', fnTd=_tdCallback, fnTrTh=None)
        # print()
        # print(myF.getvalue())
        # self.maxDiff = None
        # print(myFileLinkS)
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table class="table_style">
    <tr>
      <td class="table_style" rowspan="4">spam/</td>
      <td class="filetable" colspan="2">
        <a href="chips.html">Chips</a>
      </td>
      <td align="right" class="filetable" width="36px">1</td>
      <td align="right" class="filetable" width="36px">2</td>
      <td align="right" class="filetable" width="36px">3</td>
      <td align="right" class="filetable" width="36px">2</td>
      <td align="right" class="filetable" width="36px">3</td>
    </tr>
    <tr>
      <td class="filetable" colspan="2">
        <a href="eggs.html">Eggs</a>
      </td>
      <td align="right" class="filetable" width="36px">10</td>
      <td align="right" class="filetable" width="36px">11</td>
      <td align="right" class="filetable" width="36px">12</td>
      <td align="right" class="filetable" width="36px">110</td>
      <td align="right" class="filetable" width="36px">120</td>
    </tr>
    <tr>
      <td class="table_style" rowspan="2">fishfingers/</td>
      <td class="filetable">
        <a href="fishfingers/beans.html">Beans</a>
      </td>
      <td align="right" class="filetable" width="36px">100</td>
      <td align="right" class="filetable" width="36px">101</td>
      <td align="right" class="filetable" width="36px">102</td>
      <td align="right" class="filetable" width="36px">10,100</td>
      <td align="right" class="filetable" width="36px">10,200</td>
    </tr>
    <tr>
      <td class="filetable">
        <a href="fishfingers/peas.html">Peas</a>
      </td>
      <td align="right" class="filetable" width="36px">1000</td>
      <td align="right" class="filetable" width="36px">1,001</td>
      <td align="right" class="filetable" width="36px">1,002</td>
      <td align="right" class="filetable" width="36px">1,001,000</td>
      <td align="right" class="filetable" width="36px">1,002,000</td>
    </tr>
  </table>
</html>
""")


    def test_02(self):
        """Test_writeFilePathsAsTable.test_01(): writeFilePathsAsTable() - With header"""
        myF = io.StringIO()
        myFileNameValueS = [
            # filename, (href, navText, file_data) where file data is count_inc, count_lines, count_bytes
            ('spam/chips.lis', ('chips.html', 'Chips', (1, 2, 3))),
            ('spam/eggs.lis', ('eggs.html', 'Eggs', (10, 11, 12))),
            ('spam/fishfingers/beans.lis', ('fishfingers/beans.html', 'Beans', (100, 101, 102))),
            ('spam/fishfingers/peas.lis', ('fishfingers/peas.html', 'Peas', (1000, 1001, 1002))),
        ]
        def _tdCallback(theS, attrs, _k, href_nav_text_file_data):
            """Callback function for the file count table. This comes from CPIPMain.py"""
            attrs['class'] = 'filetable'
            href, navText, file_data = href_nav_text_file_data
            with XmlWrite.Element(theS, 'td', attrs):
                with XmlWrite.Element(theS, 'a', {'href' : href}):
                    # Write the nav text
                    theS.characters(navText)
            td_attrs = {
                'width' : "36px",
                'class' : 'filetable',
                'align' : "right",
            }
            count_inc, count_lines, count_bytes = file_data
            with XmlWrite.Element(theS, 'td', td_attrs):
                # Write the file count of inclusions
                theS.characters('%d' % count_inc)
            with XmlWrite.Element(theS, 'td', td_attrs):
                # Write the file count of lines
                theS.characters('{:,d}'.format(count_lines))
            with XmlWrite.Element(theS, 'td', td_attrs):
                # Write the file count of bytes
                theS.characters('{:,d}'.format(count_bytes))
            with XmlWrite.Element(theS, 'td', td_attrs):
                # Write the file count of lines * inclusions
                theS.characters('{:,d}'.format(count_lines * count_inc))
            with XmlWrite.Element(theS, 'td', td_attrs):
                # Write the file count of bytes * inclusions
                theS.characters('{:,d}'.format(count_bytes * count_inc))

        def _trThCallback(theS, theDepth):
            """This comes from CPIPMain.py. Create the table header:
              <tr>
                <th class="filetable" colspan="9">File Path&nbsp;</th>
                <th class="filetable">Include Count</th>
                <th class="filetable">Lines</th>
                <th class="filetable">Bytes</th>
                <th class="filetable">Total Lines</th>
                <th class="filetable">Total Bytes</th>
              </tr>
            """
            with XmlWrite.Element(theS, 'tr', {}):
                with XmlWrite.Element(theS, 'th', {
                            'colspan' : '%d' % theDepth,
                            'class' : 'filetable',
                        }
                    ):
                    theS.characters('File Path')
                with XmlWrite.Element(theS, 'th', {'class' : 'filetable'}):
                    theS.characters('Include Count')
                with XmlWrite.Element(theS, 'th', {'class' : 'filetable'}):
                    theS.characters('Lines')
                with XmlWrite.Element(theS, 'th', {'class' : 'filetable'}):
                    theS.characters('Bytes')
                with XmlWrite.Element(theS, 'th', {'class' : 'filetable'}):
                    theS.characters('Total Lines')
                with XmlWrite.Element(theS, 'th', {'class' : 'filetable'}):
                    theS.characters('Total Bytes')

        with XmlWrite.XhtmlStream(myF) as myS:
            HtmlUtils.writeFilePathsAsTable(None, myS, myFileNameValueS, 'table_style', fnTd=_tdCallback, fnTrTh=_trThCallback)
        # print()
        # print(myF.getvalue())
        # self.maxDiff = None
        # print(myFileLinkS)
        self.assertEqual(myF.getvalue(), """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <table class="table_style">
    <tr>
      <th class="filetable" colspan="3">File Path</th>
      <th class="filetable">Include Count</th>
      <th class="filetable">Lines</th>
      <th class="filetable">Bytes</th>
      <th class="filetable">Total Lines</th>
      <th class="filetable">Total Bytes</th>
    </tr>
    <tr>
      <td class="table_style" rowspan="4">spam/</td>
      <td class="filetable" colspan="2">
        <a href="chips.html">Chips</a>
      </td>
      <td align="right" class="filetable" width="36px">1</td>
      <td align="right" class="filetable" width="36px">2</td>
      <td align="right" class="filetable" width="36px">3</td>
      <td align="right" class="filetable" width="36px">2</td>
      <td align="right" class="filetable" width="36px">3</td>
    </tr>
    <tr>
      <td class="filetable" colspan="2">
        <a href="eggs.html">Eggs</a>
      </td>
      <td align="right" class="filetable" width="36px">10</td>
      <td align="right" class="filetable" width="36px">11</td>
      <td align="right" class="filetable" width="36px">12</td>
      <td align="right" class="filetable" width="36px">110</td>
      <td align="right" class="filetable" width="36px">120</td>
    </tr>
    <tr>
      <td class="table_style" rowspan="2">fishfingers/</td>
      <td class="filetable">
        <a href="fishfingers/beans.html">Beans</a>
      </td>
      <td align="right" class="filetable" width="36px">100</td>
      <td align="right" class="filetable" width="36px">101</td>
      <td align="right" class="filetable" width="36px">102</td>
      <td align="right" class="filetable" width="36px">10,100</td>
      <td align="right" class="filetable" width="36px">10,200</td>
    </tr>
    <tr>
      <td class="filetable">
        <a href="fishfingers/peas.html">Peas</a>
      </td>
      <td align="right" class="filetable" width="36px">1000</td>
      <td align="right" class="filetable" width="36px">1,001</td>
      <td align="right" class="filetable" width="36px">1,002</td>
      <td align="right" class="filetable" width="36px">1,001,000</td>
      <td align="right" class="filetable" width="36px">1,002,000</td>
    </tr>
  </table>
</html>
""")


class TestSpecial(unittest.TestCase):
    """Special tests."""
    pass

def unitTest(theVerbosity=2):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSpecial)
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
    clkStart = time.perf_counter()
    unitTest()
    clkExec = time.perf_counter() - clkStart
    print(('CPU time = %8.3f (S)' % clkExec))
    print('Bye, bye!')

if __name__ == "__main__":
    main()
