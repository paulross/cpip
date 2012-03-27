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

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

"""Default handler for handling pragma statements.
See: ISO/IEC 9899:1999 (E) 6.10.5 Error directive
"""

from cpip import ExceptionCpip

class ExceptionPragmaHandler(ExceptionCpip):
    """Simple specialisation of an exception class for the PragmaHandler.
    If raised this will cause the PpLexer to register undefined behaviour."""
    pass

class ExceptionPragmaHandlerStopParsing(ExceptionPragmaHandler):
    """Exception class for the PragmaHandler to stop parsing token stream."""
    pass

class PragmaHandlerABC(object):
    """Abstract base class for a pragma handler."""

    @property
    def replaceTokens(self):
        """An boolean attribute that says whether the supplied tokens should
        be macro replaced before being passed to self."""
        raise NotImplementedError('replaceTokens attribute not implemented.')
                      
    def pragma(self, theTokS):
        """Takes a list of PpTokens, processes then and should return a newline
        terminated string that will be preprocessed in the current environment."""
        raise NotImplementedError('pragma() not implemented.')

class PragmaHandlerNull(PragmaHandlerABC):
    """A pragma handler that does nothing."""
    @property
    def replaceTokens(self):
        """Tokens do not require macro replacement."""
        return False
    
    def pragma(self, theTokS):
        """Consume and return."""
        return ''

class PragmaHandlerSTDC(PragmaHandlerABC):
    """Base class for a pragma handler that implements ISO/IEC 9899:1999 (E)
    6.10.5 Error directive para. 2."""
    #: Standard C macro
    STDC = 'STDC'
    #: Standard C acceptable macro directives
    DIRECTIVES = (
        'FP_CONTRACT',
        'FENV_ACCESS',
        'CX_LIMITED_RANGE',
    )
    #: Standard C macro states
    ON_OFF_SWITCH_STATES = (
        'ON',
        'OFF',
        'DEFAULT',
    )

    @property
    def replaceTokens(self):
        """STDC lines do not require macro replacement."""
        return False
    
    def _consumeWs(self, theTokS, i):
        retVal = 0
        while theTokS[i].isWs():
            i += 1
            retVal += 1
        return retVal
        
    def pragma(self, theTokS):
        """Inject a macro declaration into the environment.
        
        See ISO/IEC 9899:1999 (E) 6.10.5 Error directive para. 2."""
        myTokS = []
        try:
            i = self._consumeWs(theTokS, 0)
            if theTokS[i].t == self.STDC:
                # Just consume it
                i += 1
            else:
                raise ExceptionPragmaHandlerStopParsing()
            i += self._consumeWs(theTokS, i)
            if theTokS[i].t in self.DIRECTIVES:
                myTokS.append(theTokS[i].t)
                i += 1
            else:
                raise ExceptionPragmaHandlerStopParsing()
            i += self._consumeWs(theTokS, i)
            if theTokS[i].t in self.ON_OFF_SWITCH_STATES:
                myTokS.append(' ')
                myTokS.append(theTokS[i].t)
                i += 1
            else:
                raise ExceptionPragmaHandlerStopParsing()
        except (IndexError, ExceptionPragmaHandlerStopParsing):
            myTokS = []
        if len(myTokS) > 0:
            return '#define %s\n' % ''.join([s for s in myTokS])
        return ''
