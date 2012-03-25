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
"""Writes XML and XHTML."""

__author__  = 'Paul Ross'
__date__    = '2009-09-15'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) Paul Ross'

import logging
#import traceback
import sys
#import htmlentitydefs
import base64
from cpip import ExceptionCpip

#: Global flag that sets the error behaviour
#: If True then this module may raise an ExceptionXml and that might mask other
#: exceptions. If False no ExceptionXml will be raised but a logging.error(...)
#: will be written. These will not mask other Exceptions. 
RAISE_ON_ERROR = True

class ExceptionXml(ExceptionCpip):
    """Exception specialisation for the XML writer."""
    pass

class ExceptionXmlEndElement(ExceptionXml):
    """Exception specialisation for end of element."""
    pass

#####################################
# Section: Encoding/decoding methods.
#####################################
def encodeString(theS, theCharPrefix='_'):
    """Returns a string that is the argument encoded.
    RFC3548::
    
                           Table 1: The Base 64 Alphabet
        Value Encoding  Value Encoding  Value Encoding  Value Encoding
            0 A            17 R            34 i            51 z
            1 B            18 S            35 j            52 0
            2 C            19 T            36 k            53 1
            3 D            20 U            37 l            54 2
            4 E            21 V            38 m            55 3
            5 F            22 W            39 n            56 4
            6 G            23 X            40 o            57 5
            7 H            24 Y            41 p            58 6
            8 I            25 Z            42 q            59 7
            9 J            26 a            43 r            60 8
           10 K            27 b            44 s            61 9
           11 L            28 c            45 t            62 +
           12 M            29 d            46 u            63 /
           13 N            30 e            47 v
           14 O            31 f            48 w         (pad) =
           15 P            32 g            49 x
           16 Q            33 h            50 y

    See section 3 of : http://www.faqs.org/rfcs/rfc3548.html
    """
    if len(theCharPrefix) != 1:
        errMsg = 'Prefix for encoding string must be a single character, not "%s"' % theCharPrefix
        if RAISE_ON_ERROR:
            raise ExceptionXml(errMsg)
        logging.error(errMsg)

    if sys.version_info[0] == 2:
        myBy = bytes(theS)
        retVal = base64.b64encode(myBy)
    elif sys.version_info[0] == 3:
        myBy = bytes(theS, 'ascii')
        retVal = base64.b64encode(myBy).decode()
    else:
        assert 0, 'Unknown Python version %d' % sys.version_info.major
#    if isinstance(theS, str):
#        retVal = base64.b64encode(bytes(theS, 'ascii')).decode()
#    else:
#        retVal = base64.b64encode(theS)

#    retVal = base64.b64encode(myBy)

    # post-fix base64
    retVal = retVal.replace('+', '-') \
                .replace('/', '.') \
                .replace('=', '_')
    # Lead with prefix
    return theCharPrefix + retVal
    
def decodeString(theS):
    """Returns a string that is the argument decoded. May raise a TypeError."""
    # pre-fix base64
    temp = theS[1:].replace('-', '+') \
                    .replace('.', '/') \
                    .replace('_', '=')
    temp = base64.b64decode(temp)
    return temp

def nameFromString(theStr):
    """Returns a name from a string.
    
    See http://www.w3.org/TR/1999/REC-html401-19991224/types.html#type-cdata
    
    "ID and NAME tokens must begin with a letter ([A-Za-z]) and may be
    followed by any number of letters, digits ([0-9]), hyphens ("-"),
    underscores ("_"), colons (":"), and periods (".").
    
    This also works for in namespaces as ':' is not used in the encoding."""
    return encodeString(theStr, 'Z')
#################################
# End: Encoding/decoding methods.
#################################

#############################
# Section: XML Stream writer.
#############################
class XmlStream(object):
    """Creates and maintains an XML output stream."""
    INDENT_STR = '  '
    ENTITY_MAP = {
                  '<'   : '&lt;',
                  '>'   : '&gt;',
                  '&'   : '&amp;',
                  "'"   : '&apos;', 
                  '"'   : '&quot;',
                  }
    def __init__(self, theFout, theEnc='utf-8', theDtdLocal=None, theId=0):
        """Initialise with a writable file like object or a file path.
        
        theFout - The file-like object or a string. If the latter it will be
        closed on __exit__.
        
        theEnc - The encoding to be used.
        
        theDtdLocal - Any local DTD as a string.
        
        id - An integer value to use as an ID string."""
        if type(theFout) == type(''):
            self._file = open(theFout, 'w')
            self._fileClose = True
        else:
            self._file = theFout
            self._fileClose = False
        self._enc = theEnc
        self._dtdLocal = theDtdLocal
        # Stack of strings
        self._elemStk = []
        self._inElem = False
        self._canIndentStk = []
        # An integer that represents a unique ID
        self._intId = theId
    
    @property
    def id(self):
        """A unique ID in this stream. The ID is incremented on each call."""
        self._intId += 1
        return '%d' % (self._intId-1)
    
    @property
    def _canIndent(self):
        """Returns True if indentation is possible (no mixed content etc.)"""
        for b in self._canIndentStk:
            if not b:
                return False
        return True
    
    def _flipIndent(self, theBool):
        assert(len(self._canIndentStk) > 0)
        self._canIndentStk.pop()
        self._canIndentStk.append(theBool)
        
    def xmlSpacePreserve(self):
        """Suspends indentation for this element and its descendants."""
        if len(self._canIndentStk) == 0:
            errMsg = 'xmlSpacePreserve() on empty stack.'
            if RAISE_ON_ERROR:
                raise ExceptionXml(errMsg)
            logging.error(errMsg)
        self._flipIndent(False)
    
    def startElement(self, name, attrs):
        """Opens a named element with attributes."""
        self._closeElemIfOpen()
        self._indent()
        self._file.write('<%s' % name)
        kS = sorted(attrs.keys())
        for k in kS:
            self._file.write(' %s="%s"' % (k, self._encode(attrs[k])))
        self._inElem = True
        self._canIndentStk.append(True)
        self._elemStk.append(name)

    def characters(self, theString):
        """Encodes the string and writes it to the output."""
        self._closeElemIfOpen()
        self._file.write(self._encode(theString))
        # mixed content - don't indent
        self._flipIndent(False)

    def literal(self, theString):
        """Writes theString to the output without encoding."""
        self._closeElemIfOpen()
        self._file.write(theString)
        # mixed content - don't indent
        self._flipIndent(False)

    def comment(self, theS):
        """Writes a comment to the output stream."""
        self._closeElemIfOpen()
        self._file.write('<!--%s-->' % self._encode(theS))
        # mixed content - don't indent
        #self._flipIndent(False)

    def pI(self, theS):
        """Writes a Processing Instruction to the output stream."""
        self._closeElemIfOpen()
        self._file.write('<?%s?>' % self._encode(theS))
        self._flipIndent(False)

    def endElement(self, name):
        """Ends an element."""
        if len(self._elemStk) == 0:
            errMsg = 'endElement() on empty stack'
            if RAISE_ON_ERROR:
                raise ExceptionXmlEndElement(errMsg)
            logging.error(errMsg)
        if name != self._elemStk[-1]:
            errMsg = 'endElement(%s) does not match %s' \
                                         % (name, self._elemStk[-1])
            if RAISE_ON_ERROR:
                raise ExceptionXmlEndElement(errMsg)
            logging.error(errMsg)
        myName = self._elemStk.pop()
        if self._inElem:
            self._file.write('/>')
            self._inElem = False
        else:
            self._indent()
            self._file.write('</%s>' % myName)
        self._canIndentStk.pop()
        
    def writeECMAScript(self, theScript):
        """Writes the ECMA script.
        
        Example::
        
            <script type="text/ecmascript">
            //<![CDATA[
            ...
            // ]]>
            </script>
        """
        self.startElement('script', {'type' : "text/ecmascript"})
        self._closeElemIfOpen()
        self.xmlSpacePreserve()
        self._file.write('\n//<![CDATA[\n')
        self._file.write(theScript)
        self._file.write('\n// ]]>\n')
        self.endElement('script')
    
    def _indent(self, offset=0):
        if self._canIndent:
            self._file.write('\n')
            self._file.write(self.INDENT_STR*(len(self._elemStk)-offset))
        
    def _closeElemIfOpen(self):
        if self._inElem:
            self._file.write('>')
            self._inElem = False

    def _encode(self, theStr):
        # TODO: This code does not seem to handle theStr bytes objects with '\x00' in them for example
        retL = []
        for c in theStr:
            try:
                retL.append(self.ENTITY_MAP[c])
            except KeyError:
                # Python 2.x code
                #u = unichr(ord(c))
                #retL.append(u.encode('ascii', 'xmlcharrefreplace'))
                # Python 3.x code
                retL.append(c)
        return ''.join(retL)#.encode(self._enc, 'xmlcharrefreplace')
    
    def __enter__(self):
        """Context manager support."""
        self._file.write("<?xml version='1.0' encoding=\"%s\"?>" % self._enc)
        # Write local DTD?
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager support."""
        while len(self._elemStk):
            self.endElement(self._elemStk[-1])
        self._file.write('\n')
        if self._fileClose:
            self._file.close()
        return False
#############################
# End: XML Stream writer.
#############################

###############################
# Section: XHTML Stream writer.
###############################
class XhtmlStream(XmlStream):
    def __enter__(self):
        """Context manager support."""
        super(XhtmlStream, self).__enter__()
        self._file.write("""\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">""")
        self.startElement(
                'html',
                {
                    'xmlns'     : 'http://www.w3.org/1999/xhtml',
                    'xml:lang'  : 'en',
                    'lang'      : 'en',
                }
            )
        return self

    def charactersWithBr(self, sIn):
        """Writes the string replacing any \\n characters with <br/> elements."""
        while len(sIn) > 0:
            i = sIn.find('\n')
            if i != -1:
                self.characters(sIn[:i])
                with Element(self, 'br'):
                    pass
                sIn = sIn[i+1:]
            else:
                self.characters(sIn)
                break
###############################
# Section: XHTML Stream writer.
###############################

##################################
# Section: Element for any writer.
##################################
class Element(object):
    """Represents an element in a markup stream."""
    def __init__(self, theXmlStream, theElemName, theAttrs=None):
        self._stream = theXmlStream
        self._name = theElemName
        self._attrs = theAttrs or {}

    def __enter__(self):
        """Context manager support."""
        # Write element and attributes to the stream
        self._stream.startElement(self._name, self._attrs)
        return self
    
    def __exit__(self, excType, excValue, tb):
        """Context manager support.
        TODO: Should respect RAISE_ON_ERROR here if excType is not None."""
#        if excType is not None:
#            print('excType=  ', excType)
#            print('excValue= ', excValue)
#            print('traceback=\n', '\n'.join(traceback.format_tb(tb)))
        # Close element on the stream
        self._stream.endElement(self._name)
        #return True
