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

"""CSS Support for ITU+TU files in HTML."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import os

from cpip import ExceptionCpip
from cpip.core import ItuToTokens
#from cpip.util import XmlWrite

import string

class ExceptionTokenCss(ExceptionCpip):
    pass

# Map of {token_type : enum_int, ...}
TT_ENUM_MAP = {}
# Reverse map of {enum_int : token_type, ...}
ENUM_TT_MAP = {}
for __i, __tt in enumerate(ItuToTokens.ITU_TOKEN_TYPES):
    __enum = string.ascii_lowercase[__i]
    TT_ENUM_MAP[__tt] = __enum
    ENUM_TT_MAP[__enum] = __tt

ITU_CSS_LIST = [
    """/* Conditionally compiled == %s. */
span.%s {
background-color: GreenYellow;
}""" % (True, True),
    """/* Conditionally compiled == %s. */
span.%s {
background-color: Salmon;
}""" % (False, False),
    """/* Conditionally compiled == %s. */
span.%s {
background-color: yellowgreen;
}""" % ('Maybe', 'Maybe'),
    """/* %s */
span.%s {
color:         Chartreuse;
font-style:    italic;
}""" % ('header-name', TT_ENUM_MAP['header-name']),
    """/* %s */
span.%s {
color:         BlueViolet;
font-style:    normal;
}""" % ('identifier', TT_ENUM_MAP['identifier']),
    """/* %s */
span.%s {
color:         HotPink;
font-style:    normal;
}""" % ('pp-number', TT_ENUM_MAP['pp-number']),
    """/* %s */
span.%s {
color:         orange;
font-style:    italic;
}""" % ('character-literal', TT_ENUM_MAP['character-literal']),
    """/* %s */
span.%s {
color:         LimeGreen;
font-style:    italic;
}""" % ('string-literal', TT_ENUM_MAP['string-literal']),
    """/* %s */
span.%s {
color:         black;
font-weight:   bold;
font-style:    normal;
}""" % ('preprocessing-op-or-punc', TT_ENUM_MAP['preprocessing-op-or-punc']),
    """/* %s */
span.%s {
color:         silver;
font-style:    normal;
}""" % ('non-whitespace', TT_ENUM_MAP['non-whitespace']),
    """/* %s */
span.%s {
color:         black;
font-style:    normal;
}""" % ('whitespace', TT_ENUM_MAP['whitespace']),
    """/* %s */
span.%s {
color:         black;
font-style:    normal;
}""" % ('concat', TT_ENUM_MAP['concat']),
    """/* %s */
span.%s {
color:         red;
font-style:    normal;
}""" % ('trigraph', TT_ENUM_MAP['trigraph']),
    """/* %s */
span.%s {
color:         sienna;
font-style:    normal;
}""" % ('C comment', TT_ENUM_MAP['C comment']),
    """/* %s */
span.%s {
color:         peru;
font-style:    normal;
}""" % ('C++ comment', TT_ENUM_MAP['C++ comment']),
    """/* %s */
span.%s {
color:         red;
font-style:    normal;
}""" % ('keyword', TT_ENUM_MAP['keyword']),
    """/* %s */
span.%s {
color:         blue;
font-style:    normal;
}""" % ('preprocessing-directive', TT_ENUM_MAP['preprocessing-directive']),
    """/* %s */
span.%s {
color:         red;
font-style:    italic;
}""" % ('Unknown', TT_ENUM_MAP['Unknown']),
    # Other non-enumerated styles
    # HTML styling
    """body {
font-size:      12px;
font-family:    arial,helvetica,sans-serif;
margin:         6px;
padding:        6px;
}""",

#===============================================================================
#    """h1 {
# font-family:     Sans-serif;
# font-size:       1.5em;
# color:           silver;
# font-style:    italic;
# }""",
#===============================================================================
    """h1 {
color:            darkgoldenrod;
font-family:      sans-serif;
font-size:        14pt;
font-weight:      bold;
}""",
    """h2 {
color:          IndianRed;
font-family:    sans-serif;
font-size:      14pt;
font-weight:    normal;
}""",
    """h3 {
color:          Black;
font-family:    sans-serif;
font-size:      12pt;
font-weight:    bold;
}""",
    """h4 {
color:          FireBrick;
font-family:    sans-serif;
font-size:      10pt;
font-weight:    bold;
}""",
    # Specialised classes
    # Line numbers
    """span.line {
color:           slategrey;
/*font-style:    italic; */
}""",
    # File names
    """span.file {
 color:         black;
 font-style:    italic;
}""",
    # Files in tables
    """table.filetable {
    border:         2px solid black;
    font-family:    monospace;
    color:          black;
}""",
    """th.filetable, td.filetable {
    /* border: 1px solid black; */
    border: 1px;
    border-top-style:solid;
    border-right-style:dotted;
    border-bottom-style:none;
    border-left-style:none;
    vertical-align:top;
    padding: 2px 6px 2px 6px; 
}""",
    # Monospaced tables e.g. for token counts
    """table.monospace {
border:            2px solid black;
border-collapse:   collapse;
font-family:       monospace;
color:             black;
}""",
"""th.monospace, td.monospace {
border:            1px solid black;
vertical-align:    top;
padding:           2px 6px 2px 6px; 
}""",
    # Macro presentation
    """span.macro_s_f_r_f_name{
    color:          DarkSlateGray;
    font-family:    monospace;
    font-weight:    normal;
    font-style:     italic;
}""",
    """span.macro_s_t_r_f_name {
    color:          DarkSlateGray;
    font-family:    monospace;
    font-weight:    normal;
    font-style:     normal;
}""",
    """span.macro_s_f_r_t_name {
    color:          Red; /* OrangeRed; */
    font-family:    monospace;
    font-weight:    bold;
    font-style:     italic;
}""",
    """span.macro_s_t_r_t_name{
    color:          Red; /* OrangeRed; */
    font-family:    monospace;
    font-weight:    bold;
    font-style:     normal;
}""",
    """span.macro_s_f_r_f_repl{
    color:          SlateGray;
    font-family:    monospace;
    font-weight:    normal;
    font-style:     italic;
}""",
    """span.macro_s_t_r_f_repl {
    color:          SlateGray;
    font-family:    monospace;
    font-weight:    normal;
    font-style:     normal;
}""",
    """span.macro_s_f_r_t_repl {
    color:          RosyBrown; /* Orange; */
    font-family:    monospace;
    font-weight:    bold;
    font-style:     italic;
}""",
    """span.macro_s_t_r_t_repl{
    color:          RosyBrown; /* Orange; */
    font-family:    monospace;
    font-weight:    bold;
    font-style:     normal;
}""",
    # File declarations in the macro pages
    """span.file_decl {
    color:          black;
    font-family:    monospace;
    /* font-weight:    bold;
    font-style:     italic; */
}""",
    # Conditional preprocessing directives - True
    """span.CcgNodeTrue {
    color:          LimeGreen;
    font-family:    monospace;
    /* font-weight:    bold; */
    /* font-style:     italic; */
}""",
    # Conditional preprocessing directives - False
    """span.CcgNodeFalse {
    color:          red;
    font-family:    monospace;
    /* font-weight:    bold; */
    /* font-style:     italic; */
}""",
    ]

TT_CSS_FILE = 'cpip.css'
TT_CSS_STRING = '\n'.join(ITU_CSS_LIST)

def writeCssToDir(theDir):
    """Writes the CSS file into to the directory."""
    try:
        if not os.path.exists(theDir):
            os.makedirs(theDir)
        open(os.path.join(theDir, TT_CSS_FILE), 'w').write(TT_CSS_STRING)
    except IOError as err:
        raise ExceptionTokenCss('writeCssToDir(): %s' % str(err))

def writeCssForFile(theFile):
    """Writes the CSS file into to the directory that the file is in."""
    return writeCssToDir(os.path.dirname(theFile))
    
def retClass(theTt):
    try:
        return TT_ENUM_MAP[theTt]
    except KeyError:
        raise ExceptionTokenCss('Unknown token type %s' % theTt)

