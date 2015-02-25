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

"""Provides a state stack of booleans to facilitate conditional compilation as:
ISO/IEC 9899:1999(E) section 6.10.1 ('C') and  ISO/IEC 14882:1998(E) section 16.1 ('C++') \[cpp.cond\]

This does not interpret any semantics of either standard but instead provides
a state class that callers that do interpret the language semantics can use.

In particular this provides state change operations that might be triggered by
the following six pre-processing directives: ::

    #if constant-expression new-line group opt
    #ifdef identifier new-line group opt
    #ifndef identifier new-line group opt
    #elif constant-expression new-line group opt
    #else new-line group opt
    #endif new-line

In this module a single CppCond object has a stack of ConditionalState objects.
The latter has both a boolean state and an 'explanation' of that state at any
point in the translation.
The latter is represented by a list of string representations of either
constant-expression or identifier tokens.

The stack i.e. CppCond can also be queried for its net boolean state and its
net 'explanation'.

Basic boolean stack operations ::

    Directive   Argument                Stack, s, boolean operation
    ---------   --------                -----------------------
    #if         constant-expression     s.push(bool)
    #ifdef      identifier              s.push(bool)
    #ifndef     identifier              s.push(!bool)
    #elif       constant-expression     s.pop(), s.push(bool)
    #else       N/A                     Either s.push(!s.pop()) or s.flip()
    #endif      N/A                     s.pop()

Basic boolean 'explanation' string operations:
NOTE: The '!' prefix is parameterised as TOKEN_NEGATION so that any subsequent
processing can recognise '!!' as '' and '!!!' as '!'. ::

    Directive   Argument                Matrix, m, strings
    ---------   --------                ------------------
    #if         constant-expression     m.push(['%s' % tokens,])
    #ifdef      identifier              m.push(['(defined %s)' % identifier)])
    #ifndef     identifier              m.push(['!(defined %s)' % identifier)])
    #elif       constant-expression     m[-1].push('!%s' % m[-1].pop()),
                                        m[-1].push(['%s' % tokens,])
                                        Note: Here we flip the existing state via
                                        a push(!pop())) then push the additional
                                        condition so that we have multiple
                                        contitions that are and'd together.
    #else       N/A                     m[-1].push('!%s' % m[-1].pop())
                                        Note: This is the negation of the sum of
                                        the previous #if, #elif statements.
    #endif      N/A                     m.pop()

Note: The above does not include error checking such as pop() from
an empty stack.

Stringifying the matrix m: ::

    flatList = []
    for aList in m:
        assert(len(aList) > 0)
        if len(aList) > 1:
            # Add parenthesis so that when flatList is flattened then booleans are
            # correctly protected.
            flatList.append('(%s)' % ' && '.join(aList))
        else:
            flatList.append(aList[0])
    return ' && '.join(flatList)

This returns for something like m is: ``[['a < 0',], ['!b', 'c > 45'], ['d < 27',],]``

Then this gives: ``\"a < 0 && (!b && c > 45) && d < 27\"``

CppCondGraph adds file/line tracing so that we know where the conditional
state was set.
This would mean the PpLexer adding a FileLineCol as a argument to
oIf() etc. Then this gets passed to ConditionalState.__init__().
Also instead of a PpLexer passing str(CppCond) it passes deepcopy of CppCond.
There will be a performance hit here, might it be significant?
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import logging
import collections
import bisect

from cpip import ExceptionCpip

CPP_COND_DIRECTIVES = ('if', 'ifdef', 'ifndef', 'elif', 'else', 'endif')
CPP_COND_IF_DIRECTIVES = ('if', 'ifdef', 'ifndef')
CPP_COND_ALT_DIRECTIVES = ('else', 'elif')
CPP_COND_END_DIRECTIVE = 'endif'
            
TOKEN_NEGATION  = '!'
TOKEN_AND       = '&&'
TOKEN_OR        = '||'
TOKEN_PAD       = ' '
TOKEN_JOIN_AND  = '%s%s%s' % (TOKEN_PAD, TOKEN_AND, TOKEN_PAD)
TOKEN_JOIN_OR   = '%s%s%s' % (TOKEN_PAD, TOKEN_OR, TOKEN_PAD)

class ExceptionCppCond(ExceptionCpip):
    """Simple specialisation of an exception class for the CppCond."""
    pass

class ExceptionCppCondGraph(ExceptionCppCond):
    """Simple specialisation of an exception class for the CppCondGraph."""
    pass

class ExceptionCppCondGraphElif(ExceptionCppCondGraph):
    """When the CppCondGraph sees an #elif preprocessing directive in the wrong sequence."""
    pass

class ExceptionCppCondGraphElse(ExceptionCppCondGraph):
    """When the CppCondGraph sees an #endif preprocessing directive in the wrong sequence."""
    pass

class ExceptionCppCondGraphNode(ExceptionCppCondGraph):
    """When the CppCondGraphNode sees an preprocessing directive in the wrong sequence."""
    pass

class ExceptionCppCondGraphIfSection(ExceptionCppCondGraph):
    """Exception for a CppCondGraphIfSection."""
    pass

class ConditionalState(object):
    """Holds a single conditional state."""
    def __init__(self, theState, theIdOrCondExpr):
        """theState is a boolean and theIdOrCondExpr is a string representing
        a constant-expression or identifier.
        The boolean state of this has restrictions appropriate to
        #if/#elif/#else processing in that the can not transition
        True->False->True i.e. can only have one True state.
        Of course False->True->False is permitted."""
        # The current boolean state
        self._state = theState
        # Persistent flag to record whether state has ever been True
        self._hasBeenTrue = self._state
        # List of constant-expression or identifier that can be combined
        # For example: ['!b', 'c > 45'] can be combined to (!b && c > 45)
        self._condList = []
        self._add(theIdOrCondExpr)

    def _add(self, theConstExpr):
        """Add a string to the list of constant expressions. Newline is replaced
        with a single space."""
        self._condList.append(theConstExpr.replace('\n', ' '))

    @property
    def state(self):
        """Returns boolean state of self."""
        assert(len(self._condList) > 0)
        return self._state
    
    @property
    def hasBeenTrue(self):
        """Return True if the state has been True at any time in the lifetime
        of this object."""
        return self._hasBeenTrue

    def flip(self):
        """Inverts the boolean such as for #else directive."""
        assert(len(self._condList) > 0)
        #print 'flip() state was: %s' % self._state
        if not self._hasBeenTrue or self._state:
            self._state = not self._state
            if self._state:
                self._hasBeenTrue = True
        # Handle "!!"?
        self.negateLastState()
        #print 'flip() state now: %s' % self._state
    
    def flipAndAdd(self, theBool, theConstExpr):
        """This handles an #elif command on this item in the stack.
        This flips the state (if theBool is True) and negates the last
        expression on the condition list then appends theConstExpr
        onto the condition list."""
        assert(len(self._condList) > 0)
        #print 'flipAndAdd() state was: %s' % self._state
        if (not self._hasBeenTrue or self._state):
            if theBool:
                self.flip()
            else:
                # flip() not called so we have to do this ourselves
                self.negateLastState()
                self._state = theBool
        else:
            # flip() not called so we have to do this ourselves
            self.negateLastState()
        #self._condList.append(theConstExpr)
        self._add(theConstExpr)
        #print 'flipAndAdd() state now: %s' % self._state
        #print

    def negateLastState(self):
        """Inverts the state of the last item on the stack."""
        myStr = self._condList.pop()
        if not (myStr.startswith('(') and myStr.endswith(')')):
            myStr = ('(%s)' % myStr)
        self._condList.append('%s%s' % (TOKEN_NEGATION, myStr))

    def constExprStr(self, invert=False):
        """Returns self as a string which is the concatenation of constant-expressions."""
        assert(len(self._condList) > 0)
        # If multiple states then parenthesise as these strings might be and'ed.
        if invert:
            # do the not or thing
            return '%s(%s)' % (TOKEN_NEGATION, TOKEN_JOIN_OR.join(self._condList))
        # Do not invert
        if len(self._condList) > 1:
            return '(%s)' % TOKEN_JOIN_AND.join(self._condList)
        return self._condList[0]

class CppCond(object):
    """Provides a state stack to handle conditional compilation.
    This could be used by an implementation of conditional inclusion e.g.
    ISO/IEC 14882:1998(E) section 16.1 Conditional inclusion [cpp.cond]
    Essentially this class provides a state machine that can be created altered
    and queried.
    The APIs available to the caller correspond to the if-section part of the
    the applicable standard (i.e. #if #elif etc). Most APIs take two arguments;
    
    theBool
        Is a boolean that is the result of the callers evaluation of a
        constant-expression.
    theIce
        A string that represents the identifier or constant-expression
        in a way that the caller sees fit (i.e. this is not evaluated
        locally in any way).
        Combinations of such strings _are_ merged by use of boolean
        logic ('!') and ``LPAREN`` and ``RPAREN``.
    """
    def __init__(self):
        """Constructor, this just initialise the internal state."""
        # Stack of [class ConditionalState, ...]
        self._stateStack = []

    def close(self):
        """Finalisation, may raise ExceptionCppCond is stack non-empty."""
        if len(self._stateStack) > 0:
            raise ExceptionCppCond('CppCond.close() on stack %s' % str(self))#str(self._stateStack))

    def __str__(self):
        """Returns a string representation of the stack.
        NOTE: This returns a string that says 'if my state were True
        then this is why. This string does not explain actual state, for
        that consult isTrue()."""
        return '%s' % (TOKEN_JOIN_AND.join([x.constExprStr() for x in self._stateStack]))

    @property
    def stackDepth(self):
        """Returns the depth of the conditional stack as an integer."""
        return len(self._stateStack)

    #========================
    # Section: Local methods.
    #========================
    def _push(self, theBool, theIce):
        """Pushes a new ConditionalState object onto the stack."""
        self._stateStack.append(ConditionalState(theBool, theIce))

    def _pop(self):
        """Removes a ConditionalState object from the stack.
        The removed object is returned."""
        if len(self._stateStack) == 0:
            raise ExceptionCppCond('CppCond._pop() on empty stack.')
        return self._stateStack.pop()

    def _flip(self):
        """Changes the state of the top ConditionalState object on the stack."""
        if len(self._stateStack) == 0:
            raise ExceptionCppCond('CppCond._flip() on empty stack.')
        self._stateStack[-1].flip()
    #====================
    # End: Local methods.
    #====================

    #==================================
    # Section: Preprocessor invocation.
    # This section handles the callers
    # interpretation of preprocessor
    # directives.
    #==================================
    def oIf(self, theBool, theConstExpr):
        """Deal with the result of a ``#if``.
        
        *theBool* Is a boolean that is the result of the callers evaluation of a
        constant-expression.
        
        *theConstExpr* A string that represents the identifier or
        constant-expression in a way that the caller sees fit (i.e. this is not
        evaluated locally in any way).
        Combinations of such strings _are_ merged by use of boolean
        logic ('!') and ``LPAREN`` and ``RPAREN``.
        """
        self._push(theBool, theConstExpr)

    def oIfdef(self, theBool, theConstExpr):
        """Deal with the result of a ``#ifdef``.
        
        *theBool* Is a boolean that is the result of the callers evaluation of a
        constant-expression.
        
        *theConstExpr* A string that represents the identifier or
        constant-expression in a way that the caller sees fit (i.e. this is not
        evaluated locally in any way).
        Combinations of such strings _are_ merged by use of boolean
        logic ('!') and ``LPAREN`` and ``RPAREN``.
        """
        self._push(theBool, theConstExpr)

    def oIfndef(self, theBool, theConstExpr):
        """Deal with the result of a ``#ifndef``.
        
        *theBool* Is a boolean that is the result of the callers evaluation of a
        constant-expression.
        
        *theConstExpr* A string that represents the identifier or
        constant-expression in a way that the caller sees fit (i.e. this is not
        evaluated locally in any way).
        Combinations of such strings _are_ merged by use of boolean
        logic ('!') and ``LPAREN`` and ``RPAREN``.
        """
        # NOTE: Could be push and flip
        self._push(not theBool, theConstExpr)

    def oElif(self, theBool, theConstExpr):
        """Deal with the result of a ``#elif``.
        
        *theBool* Is a boolean that is the result of the callers evaluation of a
        constant-expression.
        
        *theConstExpr* A string that represents the identifier or
        constant-expression in a way that the caller sees fit (i.e. this is not
        evaluated locally in any way).
        Combinations of such strings _are_ merged by use of boolean
        logic ('!') and ``LPAREN`` and ``RPAREN``.
        """
        if len(self._stateStack) == 0:
            raise ExceptionCppCond('CppCond.oElif() on empty stack.')
        self._stateStack[-1].flipAndAdd(theBool, theConstExpr)

    def oElse(self):
        """Deal with the result of a ``#else``."""
        self._flip()

    def oEndif(self):
        """Deal with the result of a ``#endif``."""
        if len(self._stateStack) == 0:
            raise ExceptionCppCond('CppCond.oEndif() on empty stack.')
        self._pop()
    #==============================
    # End: Preprocessor invocation.
    #==============================

    #============================
    # Section: Determining state.
    #============================
    def __bool__(self):
        """Syntactic sugar for truth testing, wraps isTrue()."""
        return self.isTrue()

    def isTrue(self):
        """Returns True if all of the states in the stack are True, False otherwise."""
        if len(self._stateStack) == 0:
            # An empty stack is always True
            return True
        for anObj in self._stateStack:
            if not anObj.state:
                return False
        return True
    
    def hasBeenTrueAtCurrentDepth(self):
        """Return True if the ConditionalState at the current depth has ever been
        True. This is used to decide whether to evaluate #elif expressions. They
        don't need to be if the ConditionalState has already been True, and in
        fact, the C Rationale (6.10) says that bogus #elif expressions should
        _not_ be evaluated in this case - i.e. ignore syntax errors.""" 
        if len(self._stateStack) == 0:
            # An empty stack is always True
            return True
        return self._stateStack[-1].hasBeenTrue
    #========================
    # End: Determining state.
    #========================

#========================================================
# Section: Graph of conditional preprocessing directives.
#========================================================
# Simple POD for state where:
# fileId - The file ID
# lineNum - The line number of the file
# tuIndex - See PpLexer that generates this which has this documentation:
#     Integer counter that indicates where in the Translation Unit we are.
#     This increases monotonically and approximates to the size of the
#     Translation Unit seen so far.
# state - Boolean True/False/None
# const_expr - A constant-expression as a string or None
# None is used for #else and #elif
StateConstExprFileLine = collections.namedtuple(
    'StateConstExprLoc',
    'fileId lineNum tuIndex state const_expr',
    verbose=False,
    )

class CppCondGraphVisitorBase(object):
    """Base class for a CppCondGraph visitor object."""
    def visitPre(self, theCcgNode, theDepth):
        """Pre-traversal call with a CppCondGraphNode and the integer depth in
        the tree."""
        raise NotImplementedError('CppCondGraphVisitorBase.visitPre() not implemented.')

    def visitPost(self, theCcgNode, theDepth):
        """Post-traversal call with a CppCondGraphNode and the integer depth in
        the tree."""
        raise NotImplementedError('CppCondGraphVisitorBase.visitPost() not implemented.')

class CppCondGraph(object):
    """Represents a graph of conditional preprocessing directives."""
    def __init__(self):
        super(CppCondGraph, self).__init__()
        # A list of sibling CppCondGraphIfSection objects
        # i.e. Containers of:
        # (#if | #ifdef | #ifndef) [#elif...] [#else] #endif
        self._ifSectS = []
    
    def __str__(self):
        return '\n'.join(self.retStrList(0))

    def visit(self, theVisitor):
        """Take a visitor object and pass it around giving it each
        CppCondGraphNode object."""
        for anIfSect in self._ifSectS:
            anIfSect.visit(theVisitor, 0)
        
    def retStrList(self, theDepth):
        retList = []
        for aSibling in self._ifSectS:
            retList.extend(aSibling.retStrList(theDepth))
        return retList
        
    @property
    def isComplete(self):
        """True if the last if-section, if present is completed with an #endif."""
        logging.debug('CppCondGraph.isComplete(): %s', str(self._ifSectS))
        return len(self._ifSectS) == 0 or self._ifSectS[-1].isSectionComplete 

    def _raiseIfComplete(self, theCppD):
        """Raise an exception if I can not accept this directive, does not
        apply to #if statements so should not be called for them."""
        assert(theCppD in CPP_COND_ALT_DIRECTIVES
               or theCppD == CPP_COND_END_DIRECTIVE)
        if self.isComplete:
            raise ExceptionCppCondGraph('Graph can not handle #%s when complete' % theCppD)
        
    def _oIfIfDefIfndef(self, theCppD, theFlc, theTuIdx, theBool, theCe):
        assert(theCppD in CPP_COND_IF_DIRECTIVES)
        if self.isComplete:
            # Append a new sibling if section
            logging.debug('CppCondGraph._oIfIfDefIfndef(): adding new sibling "%s" %s %s %s', 
                          theFlc, theTuIdx, theBool, theCe)
            self._ifSectS.append(CppCondGraphIfSection(theCppD, theFlc, theTuIdx, theBool, theCe))
        else:
            # Pass to child in list
            logging.debug('CppCondGraph._oIfIfDefIfndef(): passing "%s" to child %s %s %s', 
                          theFlc, theTuIdx, theBool, theCe)
            if theCppD == 'if':
                self._ifSectS[-1].oIf(theFlc, theTuIdx, theBool, theCe)
            elif theCppD == 'ifdef':
                self._ifSectS[-1].oIfdef(theFlc, theTuIdx, theBool, theCe)
            elif theCppD == 'ifndef':
                self._ifSectS[-1].oIfndef(theFlc, theTuIdx, theBool, theCe)

    def oIf(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#if``."""
        logging.debug('CppCondGraph.oIf():     %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        self._oIfIfDefIfndef('if', theFlc, theTuIdx, theBool, theCe)

    def oIfdef(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#ifdef``."""
        logging.debug('CppCondGraph.oIfdef():  %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        self._oIfIfDefIfndef('ifdef', theFlc, theTuIdx, theBool, theCe)

    def oIfndef(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#ifndef``."""
        logging.debug('CppCondGraph.oIfndef(): %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        self._oIfIfDefIfndef('ifndef', theFlc, theTuIdx, theBool, theCe)

    def oElif(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#elif``."""
        logging.debug('CppCondGraph.oElif():   %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        self._raiseIfComplete('elif')
        assert(len(self._ifSectS) > 0)
        self._ifSectS[-1].oElif(theFlc, theTuIdx, theBool, theCe)

    def oElse(self, theFlc, theTuIdx, theBool):
        """Deal with the result of a ``#else``."""
        logging.debug('CppCondGraph.oElse():   %s %s', theFlc, theTuIdx)
        self._raiseIfComplete('else')
        assert(len(self._ifSectS) > 0)
        self._ifSectS[-1].oElse(theFlc, theTuIdx, theBool)

    def oEndif(self, theFlc, theTuIdx, theBool):
        """Deal with the result of a ``#endif``."""
        logging.debug('CppCondGraph.oEndif():  %s %s', theFlc, theTuIdx)
        self._raiseIfComplete('endif')
        assert(len(self._ifSectS) > 0)
        self._ifSectS[-1].oEndif(theFlc, theTuIdx, theBool)

class CppCondGraphNode(object):
    """Base class for all nodes in the CppCondGraph."""
    # Number of spaces to pad out the text dump
    DUMP_PAD_SPACES = 4
    def __init__(self, theCppDirective, theFileLineCol, theTuIdx, theBool, theConstExpr=None):
        super(CppCondGraphNode, self).__init__()
        if theCppDirective not in CPP_COND_DIRECTIVES:
            raise ExceptionCppCondGraphNode('Unknown directive: %s' \
                                            % theCppDirective) 
        self._cppDir = theCppDirective
        # Location and constant expression StateConstExprFileLine
        # Make consistent rather than True/1
        if theBool:
            theBool = True
        else:
            theBool = False 
        self._cppDirLoc = StateConstExprFileLine(
                            theFileLineCol.fileId,
                            theFileLineCol.lineNum,
                            theTuIdx,
                            theBool,
                            theConstExpr,
                            )
        # List of CppCondGraphIfSection child objects as if-sections
        self._childIfSectS = []

    def __str__(self):
        return '\n'.join(self.retStrList(0))
    
    def visit(self, theVisitor, theDepth):
        """Take a visitor object make the pre/post calls."""
        theVisitor.visitPre(self, theDepth)
        for aChild in self._childIfSectS:
            aChild.visit(theVisitor, theDepth+1)
        theVisitor.visitPost(self, theDepth)
        
    def padStr(self, depth):
        return ' ' * (depth * self.DUMP_PAD_SPACES)

    def retStrList(self, theDepth):
        """Returns a list of string representation."""
        retList = ['%s%s %s' % (
                                    self.padStr(theDepth),
                                    self.cppDirString,
                                    self.commentString)
                            ]
        for aChild in self._childIfSectS:
            retList.extend(aChild.retStrList(theDepth+1))
        return retList
        
    @property
    def cppDirective(self):
        return self._cppDir
    
    @property
    def fileId(self):
        return self._cppDirLoc.fileId
    
    @property
    def lineNum(self):
        return self._cppDirLoc.lineNum
    
    @property
    def tuIndex(self):
        return self._cppDirLoc.tuIndex
    
    @property
    def state(self):
        return self._cppDirLoc.state
    
    @property
    def constExpr(self):
        return self._cppDirLoc.const_expr

    @property
    def cppDirString(self):
        if self._cppDirLoc.const_expr is None:
            return '#%s' % self._cppDir
        return '#%s %s' % (self._cppDir, self._cppDirLoc.const_expr) 

    @property
    def commentString(self):
        return '/* %s "%s" %s %s */' \
            % (self._cppDirLoc.state,
               self._cppDirLoc.fileId,
               self._cppDirLoc.lineNum,
               self._cppDirLoc.tuIndex)
        
    def canAccept(self, theCppD):
        """True if I can accept a Preprocessing Directive; theCppD."""
        assert(theCppD in CPP_COND_DIRECTIVES)
        # If I am an #endif then I can not accept descendants
        if self.cppDirective == CPP_COND_END_DIRECTIVE:
            assert(len(self._childIfSectS) == 0)
            return False
        # We can always accept an #if as a descendant
        if theCppD in CPP_COND_IF_DIRECTIVES:
            return True
        # #elif, #else, #endif are acceptable if I have children and
        # they are incomplete
        assert(theCppD in CPP_COND_ALT_DIRECTIVES \
               or theCppD == CPP_COND_END_DIRECTIVE)
        if len(self._childIfSectS) == 0:
            return False
        return not self._childIfSectS[-1].isSectionComplete
    
    def _raiseIfCanNotAccept(self, theCppD):
        """Raise an exception if I can not accept this directive."""
        assert(theCppD in CPP_COND_DIRECTIVES)
        if not self.canAccept(theCppD):
            raise ExceptionCppCondGraphNode('Can not handle #%s when complete' % theCppD)
        
    def _oIfIfDefIfndef(self, theCppD, theFlc, theTuIdx, theBool, theCe):
        assert(theCppD in CPP_COND_IF_DIRECTIVES)
        self._raiseIfCanNotAccept(theCppD)
        # Decide to pass this down or create new if-section
        if len(self._childIfSectS) == 0 \
        or self._childIfSectS[-1].isSectionComplete:
            # Append a new child if-section
            self._childIfSectS.append(CppCondGraphIfSection(theCppD, theFlc, theTuIdx, theBool, theCe))
        else:
            # Pass to child in list
            assert(len(self._childIfSectS) > 0)
            if theCppD == 'if':
                self._childIfSectS[-1].oIf(theFlc, theTuIdx, theBool, theCe)
            elif theCppD == 'ifdef':
                self._childIfSectS[-1].oIfdef(theFlc, theTuIdx, theBool, theCe)
            elif theCppD == 'ifndef':
                self._childIfSectS[-1].oIfndef(theFlc, theTuIdx, theBool, theCe)

    def oIf(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#if``."""
        logging.debug('CppCondGraphNode.oIf():     %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        self._oIfIfDefIfndef('if', theFlc, theTuIdx, theBool, theCe)

    def oIfdef(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#ifdef``."""
        logging.debug('CppCondGraphNode.oIfdef():  %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        self._oIfIfDefIfndef('ifdef', theFlc, theTuIdx, theBool, theCe)

    def oIfndef(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#ifndef``."""
        logging.debug('CppCondGraphNode.oIfndef(): %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        self._oIfIfDefIfndef('ifndef', theFlc, theTuIdx, theBool, theCe)

    def oElif(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#elif``."""
        logging.debug('CppCondGraphNode.oElif():   %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        self._raiseIfCanNotAccept('elif')
        # Pass to child in list
        assert(len(self._childIfSectS) > 0)
        self._childIfSectS[-1].oElif(theFlc, theTuIdx, theBool, theCe)

    def oElse(self, theFlc, theTuIdx, theBool):
        """Deal with the result of a ``#else``."""
        logging.debug('CppCondGraphNode.oElse():   %s %s', theFlc, theTuIdx)
        self._raiseIfCanNotAccept('else')
        # Pass to child in list
        assert(len(self._childIfSectS) > 0)
        self._childIfSectS[-1].oElse(theFlc, theTuIdx, theBool)

    def oEndif(self, theFlc, theTuIdx, theBool):
        """Deal with the result of a ``#endif``."""
        logging.debug('CppCondGraphNode.oEndif():  %s %s', theFlc, theTuIdx)
        self._raiseIfCanNotAccept('endif')
        # Pass to child in list
        assert(len(self._childIfSectS) > 0)
        self._childIfSectS[-1].oEndif(theFlc, theTuIdx, theBool)

class CppCondGraphIfSection(object):
    """Class that represents a conditionally compiled section starting with
    #if... and ending with #endif.""" 
    def __init__(self, theIfCppD, theFlc, theTuIdx, theBool, theCe):
        """Constructor with:
        theIfCppD - A string, one of '#if', '#ifdef', '#ifndef'.
        theFlc - a FileLineColumn object that identifies the position in the file.
        theTuIndex - An integer that represents the position in the translation unit.
        theBool - The current state of the conditional stack.
        theCe - The constant expression to be evaluated as a string.
        """
        super(CppCondGraphIfSection, self).__init__()
        assert(theIfCppD in CPP_COND_IF_DIRECTIVES)
        # A list of sibling CppCondGraphNode objects representing
        # (#if | #ifdef | #ifndef) [#elif...] [#else] #endif
        # Each of those, except endif can have children
        # This list always has at least one item in it
        self._siblingNodeS = [
                CppCondGraphNode(theIfCppD, theFlc, theTuIdx, theBool, theCe),
            ]
    
    def __str__(self):
        return '\n'.join(self.retStrList(0))
    
    def visit(self, theVisitor, theDepth):
        """Take a visitor object make the pre/post calls."""
        for aSibling in self._siblingNodeS:
            aSibling.visit(theVisitor, theDepth)
        
    def retStrList(self, theDepth):
        retList = []
        for aSibling in self._siblingNodeS:
            retList.extend(aSibling.retStrList(theDepth))
        return retList
            
    @property
    def isSectionComplete(self):
        assert(len(self._siblingNodeS) > 0)
        retVal = self._siblingNodeS[-1].cppDirective == 'endif'
        logging.debug(
                'CppCondGraphIfSection.isSectionComplete(): %s %s',
                retVal,
                str(self._siblingNodeS)
            )
        return retVal
    
    def _raiseIfSectionComplete(self, theCppD):
        if self.isSectionComplete:
            raise ExceptionCppCondGraphIfSection(
                'CppCondGraphIfSection: #%s in if-section that is complete.' \
                                    % theCppD)
    
    def _oIfIfDefIfndef(self, theCppD, theFlc, theTuIdx, theBool, theCe):
        assert(theCppD in CPP_COND_IF_DIRECTIVES)
        assert(len(self._siblingNodeS) > 0)
        self._raiseIfSectionComplete(theCppD)
        # Pass to sibling (and thus to their children)
        if theCppD == 'if':
            self._siblingNodeS[-1].oIf(theFlc, theTuIdx, theBool, theCe)
        elif theCppD == 'ifdef':
            self._siblingNodeS[-1].oIfdef(theFlc, theTuIdx, theBool, theCe)
        elif theCppD == 'ifndef':
            self._siblingNodeS[-1].oIfndef(theFlc, theTuIdx, theBool, theCe)

    def oIf(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#if``."""
        logging.debug('CppCondGraphIfSection.oIf():     %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        self._oIfIfDefIfndef('if', theFlc, theTuIdx, theBool, theCe)

    def oIfdef(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#ifdef``."""
        logging.debug('CppCondGraphIfSection.oIfdef():  %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        self._oIfIfDefIfndef('ifdef', theFlc, theTuIdx, theBool, theCe)

    def oIfndef(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#ifndef``."""
        logging.debug('CppCondGraphIfSection.oIfndef(): %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        self._oIfIfDefIfndef('ifndef', theFlc, theTuIdx, theBool, theCe)

    def oElif(self, theFlc, theTuIdx, theBool, theCe):
        """Deal with the result of a ``#elif``."""
        logging.debug('CppCondGraphIfSection.oElif():   %s %s %s "%s"', theFlc, theTuIdx, theBool, theCe)
        assert(len(self._siblingNodeS) > 0)
        self._raiseIfSectionComplete('elif')
        if self._siblingNodeS[-1].canAccept('elif'):
            # Pass to sibling (and thus to their children)
            self._siblingNodeS[-1].oElif(theFlc, theTuIdx, theBool, theCe)
        else:
            # Raise on #if/#else/#elif
            if self._siblingNodeS[-1].cppDirective == 'else':
                raise ExceptionCppCondGraphElif('#elif follows %s' \
                                        % self._siblingNodeS[-1].cppDirective)
            else:
                self._siblingNodeS.append(CppCondGraphNode('elif', theFlc, theTuIdx, theBool, theCe))

    def oElse(self, theFlc, theTuIdx, theBool):
        """Deal with the result of a ``#else``."""
        logging.debug('CppCondGraphIfSection.oElse():   %s %s', theFlc, theTuIdx)
        assert(len(self._siblingNodeS) > 0)
        self._raiseIfSectionComplete('else')
        if self._siblingNodeS[-1].canAccept('else'):
            # Pass to sibling (and thus to their children)
            self._siblingNodeS[-1].oElse(theFlc, theTuIdx, theBool)
        else:
            # Raise on #if/#else/#else
            if self._siblingNodeS[-1].cppDirective == 'else':
                raise ExceptionCppCondGraphElse('#else follows by %s' \
                                        % self._siblingNodeS[-1].cppDirective)
            else:
                self._siblingNodeS.append(CppCondGraphNode('else', theFlc, theTuIdx, theBool))

    def oEndif(self, theFlc, theTuIdx, theBool):
        """Deal with the result of a ``#endif``."""
        logging.debug('CppCondGraphIfSection.oEndif():  %s %s', theFlc, theTuIdx)
        assert(len(self._siblingNodeS) > 0)
        self._raiseIfSectionComplete('endif')
        if self._siblingNodeS[-1].canAccept('endif'):
            # Pass to sibling (and thus to their children)
            self._siblingNodeS[-1].oEndif(theFlc, theTuIdx, theBool)
        else:
            # Otherwise append to me, this makes self.isSectionComplete == True
            self._siblingNodeS.append(CppCondGraphNode('endif', theFlc, theTuIdx, theBool))

class LineConditionalInterpretation(object):
    """Class that represents the conditional compilation state of every line in
    a file. This takes a list of [(line_num, boolean), ...] and interprets
    individual line numbers as to whether they are compiled or not.
    If the same file is included twice with a different macro environment then
    it is entirely possible that line_num is not monotonic.
    We have to sort theList by line_num and if there are duplicate line_num
    with different boolean values then the conditional compilation state at
    then point is ambiguos.
    """
    def __init__(self, theList):
        self._lines = []
        self._bools = []
        # Only keep unique values then sort, this means we might have:
        # [(10, False), (10, True), ...]
        for l, b in sorted(set(theList)):
            self._lines.append(l)
            self._bools.append(b)
            
    def isCompiled(self, lineNum):
        """Returns 1 if this line is compiled, 0 if not or -1 if it is ambiguos
        i.e. sometimes it is and somtimes not when multiply included."""
        idx = bisect.bisect_right(self._lines, lineNum)
        if idx == 0:
            raise ValueError('LineConditionInterpretation.isCompiled(): Can not find %s in %s' % (lineNum, self._lines))
        idx -= 1
        if idx > 0 \
        and self._lines[idx-1] == self._lines[idx] \
        and self._bools[idx-1] != self._bools[idx]:
            return -1
        return 1 if self._bools[idx] else 0
    
    def __str__(self):
        return str(zip(self._lines, self._bools))

class CppCondGraphVisitorConditionalLines(CppCondGraphVisitorBase):
    """Allows you to find out if any particular line in a file is compiled or
    not. This is useful to be handed to the ITU to HTML generator that can
    colourize the HTML depending if any line is compiled or not.
    
    This is a visitor class that walks the graph creating a dict of:
    {file_id : [(line_num, boolean), ...], ...}
    It then decomposes those into a map of {file_id : LineConditionalInterpretation(), ...}
    which can perfom the actual conditional state determination.
    
    API is really isCompiled(file, line): and this returns -1, 0, 1.
    0 means NO. 1 means YES and -1 means sometimes - for re-included files in a
    different macro environment perhaps.
    """
    def __init__(self):
        super(CppCondGraphVisitorConditionalLines, self).__init__()
        # {file_id : [(line_num, boolean), ...], ...}
        self._fileMap = {}
        self._prevFile = None
        self._prevState = True
        # Lazy evaluation of a {file_id : LineConditionalInterpretation(), ...}
        self._fileLineCondition = None
        
    #---------------------
    # Visitor methods
    #---------------------
    def visitPre(self, theCcgNode, theDepth):
        """Capture the fileID, line number and state."""
        # Carry over state from previous file
        if self._prevFile != theCcgNode.fileId:
            self._addFileLineState(theCcgNode.fileId, 0, self._prevState)
        self._prevFile = theCcgNode.fileId
        self._prevState = theCcgNode.state
        # Add current state
        self._addFileLineState(theCcgNode.fileId, theCcgNode.lineNum, theCcgNode.state)
        
    def _addFileLineState(self, file, line, state):
        try:
            self._fileMap[file].append((line, state))
        except KeyError:
            self._fileMap[file] = [(line, state),]
            
    def visitPost(self, theCcgNode, theDepth):
        pass
    #---------------------
    # END: Visitor methods
    #---------------------
    
    #---------------------
    # Accessor methods
    #---------------------
    @property
    def fileIdS(self):
        """An unordered list of file IDs."""
        return self._fileMap.keys()
    
    @property
    def fileLineCondition(self):
        if self._fileLineCondition is None:
            self._fileLineCondition = dict(((k, LineConditionalInterpretation(v)) for k, v in self._fileMap.items()))
        return self._fileLineCondition
    
    # Testing only
    def _lineCondition(self, theFile):
        """An ordered list of (line_num, boolean)."""
        return self._fileMap[theFile]
    
    def pprint(self):
        for f in sorted(self.fileLineCondition.keys()):
            print(f, str(self.fileLineCondition[f]))

    def isCompiled(self, fileId, lineNum):
        """Returns 1 if this line is compiled, 0 if not or -1 if it is ambiguos
        i.e. sometimes it is and somtimes not when multiply included."""
        return self.fileLineCondition[fileId].isCompiled(lineNum)
    #---------------------
    # END: Accessor methods
    #---------------------
