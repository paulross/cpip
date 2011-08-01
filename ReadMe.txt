CPIP is a C/C++ Preprocessor implemented in Python.
Copyright (C) 2008-2011 Paul Ross

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

Paul Ross: cpipdev@googlemail.com

CPIP - A 'C' Preprocessor Implemented in Python

Alpha Release 2011-07-14
========================

This is a pre-release of CPIP. It is tested on BSD/Linux, it will probably work on Windows (although some unit tests will fail on that platform).

Requirements
------------
Python 2.6 or better, this will not (yet) work on Python 3. No special libraries are required.

Installation
------------
Expand this archive to <install_dir>
Set your PYTHONPATH to: <install_dir>/rel/alpha_00/src/cpip

Testing the Installation
------------------------
Navigate a command line to: <install dir>/rel/alpha_00/src/cpip
And type python CPIPMain.py
If you have got it right then you should see the CPIPMain help information.

Running Unit Tests
------------------
Navigate a command line to: <install dir>/rel/alpha_00/src/cpip/core

Execute: python test/UnitTests.py

(Known issues with Windows paths).

In this release
===============

demo/
-----
Some demo code in 'C', some code in Python that uses the PpLexer to process that and in output/ the
result of processing the demo 'C' code with CPIPMain.py.

doc/
----
Some documentation and tutorials, fairly limited at the moment.

src/
----
Source code of CPIP.

