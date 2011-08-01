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

"""HTML utility functions."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

import os
import hashlib
import types

import XmlWrite
from cpip.util import DictTree
    
def retHtmlFileName(thePath):
    """Creates a unique, short, human readable file name base on the input
    file path."""
    myHash = hashlib.md5(os.path.abspath(thePath)).hexdigest()
    return '%s_%s%s' % (os.path.basename(thePath), myHash, '.html')

def retHtmlFileLink(theSrcPath, theLineNum):
    return "%s#%d" % (retHtmlFileName(theSrcPath), theLineNum)

def writeHtmlFileLink(theS, theSrcPath, theLineNum, theText='', theClass=None):
    """Writes a link to another HTML file that represents source code.
    theS is an XHTML stream.
    theSrcPath is the path of the original source, whis will be encoded with retHtmlFileName().
    theLineNum is an integer line number in the target.
    theText is optional navigation text.
    theClass is optional CSS class for the navigational text."""
    with XmlWrite.Element(
            theS,
            'a',
            {
                'href' : retHtmlFileLink(theSrcPath, theLineNum),
            },
        ):
        if theText:
            if theClass is None:
                theS.characters(theText)
            else:
                with XmlWrite.Element(theS, 'span', {'class' : theClass}):
                    theS.characters(theText)
                
def writeHtmlFileAnchor(theS, theLineNum, theText='', theClass=None):
    with XmlWrite.Element(theS, 'a', {'name' : "%d" % theLineNum}):
        if theText:
            if theClass is None:
                theS.characters(theText)
            else:
                with XmlWrite.Element(theS, 'span', {'class' : theClass}):
                    theS.characters(theText)

def pathSplit(p):
    """Split a path into its components."""
    #print 'TRACE: pathSplit(%s):' % p
    #p = os.path.splitdrive(p)[1]
    l = p.split(os.sep)
    retVal = ['%s%s' % (d, os.sep) for d in l[:-1]]
    retVal.append(l[-1])
    #print 'TRACE: pathSplit(%s): returns %s' % (p, str(retVal))
    return retVal

def writeFileListAsTable(theS, theFileLinkS, tableAttrs, includeKeyTail):
    """Writes a list of file names as an HTML table looking like a directory
    structure. theFileLinkS is a list of pairs (file_path, href).
    The navigation text in the cell will be the basename of the file_path."""
    #myList = [(f, h, os.path.basename(f)) for f, h in theFileLinkS]
    #writeFileListTrippleAsTable(theS, myList, tableAttrs, includeKeyTail)
    #print 'TRACE: theFileLinkS', theFileLinkS
    myDict = DictTree.DictTreeHtmlTable(None)
    for f, h in theFileLinkS:
        keyList = pathSplit(f)
        myDict.add(keyList, (h, os.path.basename(f)))
    writeDictTreeAsTable(theS, myDict, tableAttrs, includeKeyTail)

def writeFileListTrippleAsTable(theS, theFileLinkS, tableAttrs, includeKeyTail):
    """Writes a list of file names as an HTML table looking like a directory
    structure. theFileLinkS is a list of triples (file_name, href, nav_text)."""
    #print 'TRACE: theFileLinkS', theFileLinkS
    myDict = DictTree.DictTreeHtmlTable('list')
    for f, h, n in theFileLinkS:
        keyList = pathSplit(f)
        myDict.add(keyList, (h, n))
    #print 'TRACE:   myDict.keys():', myDict.keys()
    #print 'TRACE: myDict.values():', myDict.values()
    writeDictTreeAsTable(theS, myDict, tableAttrs, includeKeyTail)

def writeDictTreeAsTable(theS, theDt, tableAttrs, includeKeyTail):
    """Writes a DictTreeHtmlTable object as a table, for example as a directory
    structure.
    The key list in the DictTreeHtmlTable object is the path to the file
    i.e. os.path.abspath(p).split(os.sep) and the value is expected to be a
    pair of (link, nav_text) or None."""
    # Write: <table border="2" width="100%">
    # Propogate table class attribute
    myAttrs = {}
    try:
        myAttrs['class'] = tableAttrs['class']
    except KeyError:
        pass
    with XmlWrite.Element(theS, 'table', tableAttrs):
        for anEvent in theDt.genColRowEvents():
            if anEvent == theDt.ROW_OPEN:
                # Write out the '<tr>' element
                theS.startElement('tr', {})
            elif anEvent == theDt.ROW_CLOSE:
                # Write out the '</tr>' element
                theS.endElement('tr')
            else:
                #print 'TRACE: anEvent', anEvent
                k, v, r, c = anEvent
                # Write '<td rowspan="%d" colspan="%d">%s</td>' % (r, c, txt[-1])
                myTdAttrs = {}
                myTdAttrs.update(myAttrs)
                if r > 1:
                    myTdAttrs['rowspan'] = "%d" % r
                if c > 1:
                    myTdAttrs['colspan'] = "%d" % c
                with XmlWrite.Element(theS, 'td', myTdAttrs):
                    if v is not None:
                        if includeKeyTail:
                            theS.characters('%s:' % k[-1])                        
                        # Output depending on the type of the value
                        if type(v) == types.ListType:
                            for h, n in v:
                                theS.characters(' ')
                                with XmlWrite.Element(theS, 'a', {'href' : h}):
                                    # Write the nav text
                                    theS.characters('%s' % n)
                        elif type(v) == types.TupleType and len(v) == 2:
                            with XmlWrite.Element(theS, 'a', {'href' : v[0]}):
                                # Write the nav text
                                theS.characters(v[1])
                        else:
                            # Treat as string
                            theS.characters(str(v))
                    else:
                        theS.characters(k[-1])
    # Write: </table>
    
def writeFilePathsAsTable(valueType, theS, theKvS, tableStyle, fnTd):
    """Writes file paths as a table, for example as a directory structure.
    valueType - The type of the value; None, |'list' | 'set'
    theKvS - A list of pairs (file_path, value).
    tableStyle - The style used for the table.
    fnTd - A callback function that is executed for a <td> element when
    there is a non-None value. This is called with the following arguments:
    theS - The HTML stream.
    attrs - A map of attrs that include the rowspac/colspan for the <td>
    k - The key as a list of path components.
    v - The value given by the caller.
    """
    myDict = DictTree.DictTreeHtmlTable(valueType)
    for k, v in theKvS:
        myDict.add(pathSplit(k), v)
    # Propogate table class attribute
    with XmlWrite.Element(theS, 'table', {'class' : tableStyle}):
        for anEvent in myDict.genColRowEvents():
            if anEvent == myDict.ROW_OPEN:
                # Write out the '<tr>' element
                theS.startElement('tr', {})
            elif anEvent == myDict.ROW_CLOSE:
                # Write out the '</tr>' element
                theS.endElement('tr')
            else:
                #print 'TRACE: anEvent', anEvent
                k, v, r, c = anEvent
                # Write '<td rowspan="%d" colspan="%d">%s</td>' % (r, c, txt[-1])
                myTdAttrs = {'class' : tableStyle}
                if r > 1:
                    myTdAttrs['rowspan'] = "%d" % r
                if c > 1:
                    myTdAttrs['colspan'] = "%d" % c
                if v is not None:
                    fnTd(theS, myTdAttrs, k, v)
                else:
                    with XmlWrite.Element(theS, 'td', myTdAttrs):
                        # Write out part of the file name
                        theS.characters(k[-1])
#===============================================================================
#                        if includeKeyTail:
#                            theS.characters('%s:' % k[-1])                        
#                        # Output depending on the type of the value
#                        if type(v) == types.ListType:
#                            for h, n in v:
#                                theS.characters(' ')
#                                with XmlWrite.Element(theS, 'a', {'href' : h}):
#                                    # Write the nav text
#                                    theS.characters('%s' % n)
#                        elif type(v) == types.TupleType and len(v) == 2:
#                            with XmlWrite.Element(theS, 'a', {'href' : v[0]}):
#                                # Write the nav text
#                                theS.characters(v[1])
#                        else:
#                            # Treat as string
#                            theS.characters(str(v))
#===============================================================================
    # Write: </table>

