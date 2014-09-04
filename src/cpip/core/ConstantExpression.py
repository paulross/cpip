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

"""Handles the Python interpretation of a constant-expression.
See ISO/IEC 14882:1998(E)
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

#import sys
#import time
import logging
import pprint

# Ugggh
import re

#import PpToken
from cpip import ExceptionCpip 

class ExceptionConstantExpression(ExceptionCpip):
    """Simple specialisation of an exception class for the ConstantExpression classes."""
    pass

class ExceptionConditionalExpressionInit(ExceptionConstantExpression):
    """Exception when initialising a ConstantExpression class."""
    pass

class ExceptionConditionalExpression(ExceptionConstantExpression):
    """Exception when conditional expression e.g. ... ? ... : ... fails to evaluate."""
    pass

class ExceptionEvaluateExpression(ExceptionConstantExpression):
    """Exception when conditional expression e.g. 1 < 2 fails to evaluate."""
    pass

class ConstantExpression(object):
    """Class that interpret a stream of preprocessing tokens (class PpToken)
    and evaluate it as a constant expression.
    """
    # Regex for conditional-expression
    # For example: '(a) > (b) ? (a) : (b)'
    RE_CONDITIONAL_EXPRESSION = re.compile(r'^(.+)\?(.+):(.+)$')
    # Replacement string uses groups 1, 2, 3
    REPLACE_CONDITIONAL_EXPRESSION = 'if %s:\n  result = %s\nelse:\n  result = %s'
    def __init__(self, theTokTypeS):
        """Constructor takes a list pf PpToken."""
        self._tokTypeS = theTokTypeS[:]

    def __str__(self):
        return ''.join([t.t for t in self._tokTypeS])

    #def concatTokens(self):
    #    """Returns a string that is a simple concatenation of a the tokens
    #    regardless of type."""
    #    return ''.join([t.t for t in self._tokTypeS])

    def translateTokensToString(self):
        """Returns a string to be evaluated as a constant-expression.
        ISO/IEC ISO/IEC 14882:1998(E) 16.1 Conditional inclusion sub-section 4
        i.e. 16.1-4"""
        # all remaining identifiers and keywords 137) , except for true and false,
        # are replaced with the pp-number 0
#        print 'self._tokTypeS', self._tokTypeS[0]
        return ''.join([aTok.evalConstExpr() for aTok in self._tokTypeS])

    def evaluate(self):
        """Evaluates the constant expression and returns 0 or 1."""
        s = self.translateTokensToString()
        m = self.RE_CONDITIONAL_EXPRESSION.match(s)
        if m is not None:
            return self._evaluateConditionalExpression(m)
        return self._evaluateExpression(s)

    def _evaluateConditionalExpression(self, theMatch):
        """Evaluates a conditional expression e.g. expr ? t : f
        Which we convert with a regular expression to: ::
            if exp:
                t
            else:
                f
        """
        assert(theMatch is not None)
        compileString = self.REPLACE_CONDITIONAL_EXPRESSION \
                        % (theMatch.group(1), theMatch.group(2), theMatch.group(3))
#        print('compileString:', compileString)
#        result = None
        try:
            _locals = {'result' : None}
            c = compile(compileString, '<string>', 'exec')
            exec(c, {}, _locals)
#            pprint.pprint(locals())
            return _locals['result']
#            return locals()['result']
        except Exception as err:
            logging.error('ConstantExpression._evaluateConditionalExpression() can not evaluate: "%s"' % compileString)
            raise ExceptionConditionalExpression(str(err))
#        return result

    def _evaluateExpression(self, theStr):
        """Evaluates a conditional expression e.g. 1 < 2 """
        assert(self.RE_CONDITIONAL_EXPRESSION.match(self.translateTokensToString()) is None)
        try:
#            print '_evaluateExpression():', theStr
            return eval(theStr)
        except Exception as err:
            raise ExceptionEvaluateExpression(
                'Evaluation of "%s" gives error: %s' % (theStr, str(err))
                )

    #def _commaOperator(self):
    #    """Handles the comma operator.
    #    ISO/IEC 14882:1998(E) 5.18 Comma operator.
    #    And:
    #    ISO/IEC 9899:1999 (E) 6.5.17 Comma operator.
    #    [Example:
    #    f(a, (t=3, t+2), c);
    #    has three arguments, the second of which has the value 5. ]
    #
    #    But need we do anything as:
    #    $ cpp -E
    #    #if (t=3, t+2)
    #    ONE
    #    #else
    #    TWO
    #    #endif
    #
    #    # 1 "<stdin>"
    #    # 1 "<built-in>"
    #    # 1 "<command line>"
    #    # 1 "<stdin>"
    #    <stdin>:1:7: token "=" is not valid in preprocessor expressions
    #
    #    TWO
    #    """
    #    # TODO
    #    pass
