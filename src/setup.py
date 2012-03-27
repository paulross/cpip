#!/usr/bin/env python
# CPIP is a C/C++ Preprocessor implemented in Python.
# Copyright (C) 2008-2012 Paul Ross
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
__date__    = '2012-03-26'
__version__ = '0.8.1'
__rights__  = 'Copyright (c) 2008-2012 Paul Ross'

from distutils.core import setup

setup(
    name='CPIP',
    version='0.8.1',
    description='A C Preprocessor implemented in Python.',
    author='Paul Ross',
    author_email='cpipdev@googlemail.com',
    url='http://cpip.sourceforge.net/',
    packages=[
        'cpip',
        'cpip.core',
        'cpip.util',
        'cpip.plot',
        'cpip.core.test',
        'cpip.util.test',
        'cpip.plot.test',
        'cpip.test',
    ],
#    py_modules=[
#        'CPIPMain',
#        'CppCondGraphToHtml',
#        'IncGraphSVG',
#        'IncGraphSVGBase',
#        'IncGraphSVGPpi',
#        'IncGraphXML',
#        'IncList',
#        'ItuToHtml',
#        'MacroHistoryHtml',
#        'TokenCss',
#        'Tu2Html',
#        'TuIndexer',
#    ],
)
