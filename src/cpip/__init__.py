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

from .__version__ import __version__

__author__  = 'Paul Ross'
__date__    = '2014-03-03'
__rights__  = 'Copyright (c) 2008-2017 Paul Ross'

__all__ = ['core', 'util', 'plot']

"""CPIP: 'C' Preprocessor in Python.
"""

CPIP_VERSION = (0, 9, 8, 'rc0')

RELEASE_NOTES = [
    """Release Notes (latest at top).
==============================
2017-10-04: Version 0.9.7. Tested on Python 2.7 and 3.6.

2017-10-03: Version 0.9.5, migrate to GitHub. Tested on Python 2.7 and 3.6.

2014-09-03: Version 0.9.1, various minor fixes. Tested on Python 2.7 and 3.3.

2014-01-11: Revisited SVG and HTML code to make it faster and cross browser.

2012-03-26: Updated to Python 3.

2011-07-10: First public release of CPIP.
""",
]

class ExceptionCpip(Exception):
    """Simple specialisation of an exception class for CPIP and its modules."""
    pass

###########################
# Constants for trace/debug
###########################
# Whitespace indent and bloat the HTML/SVG files.
INDENT_ML = True
# Write the function name in a SVG comment.
SVG_COMMENT_FUNCTIONS = False
###########################
# Constants for trace/debug
###########################

