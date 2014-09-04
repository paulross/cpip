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

"""This handles definition, undefinition, redefintion, replacement
and rescaning of macro declarations

It implements: ISO/IEC 9899:1999(E) section 6 (aka 'C99')
and/or: ISO/IEC 14882:1998(E) section 16 (aka 'C++98')

"""
__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import logging
import copy

# Debug and trace imports - consider removing these from production code
#import traceback

from cpip import ExceptionCpip
from cpip.core import PpToken
from cpip.core import PpTokenCount
from cpip.core import PpWhitespace
from cpip.core import FileLocation
#from ListGen import ListAsGenerator

class ExceptionCpipDefine(ExceptionCpip):
    """Exception when handling PpDefine object."""
    pass

class ExceptionCpipDefineInit(ExceptionCpipDefine):
    """Exception when creating PpDefine object fails."""
    pass

class ExceptionCpipDefineMissingWs(ExceptionCpipDefineInit):
    """Exception when calling missing ws between identifier and replacement tokens.
    
    See: ISO/IEC 9899:1999(E) Section 6.10.3-3 and ISO/IEC 14882:1998(E) Section ???
    
    Note: cpp says for "#define PLUS+":
    src.h:1:13: warning: ISO C requires whitespace after the macro name"""
    pass

class ExceptionCpipDefineBadWs(ExceptionCpipDefineInit):
    """Exception when calling bad whitespace is in a define statement.
    See: ISO/IEC 9899:1999(E) Section 6.10-f and ISO/IEC 14882:1998(E) 16-2"""
    pass

class ExceptionCpipDefineInvalidCmp(ExceptionCpipDefineInit):
    """Exception for a redefinition where the identifers are different."""
    pass

class ExceptionCpipDefineDupeId(ExceptionCpipDefineInit):
    """Exception for a function-like macro has duplicates
    in the identifier-list."""
    pass

class ExceptionCpipDefineInitBadLine(ExceptionCpipDefineInit):
    """Exception for a bad line number given as argument."""
    pass

class ExceptionCpipDefineReplace(ExceptionCpipDefine):
    """Exception when replacing a macro definition fails."""
    pass

class ExceptionCpipDefineBadArguments(ExceptionCpipDefine):
    """Exception when scanning an argument list for a function style macro
    fails.
    NOTE: This is only raised during replacement not during
    initialisation."""
    pass

class PpDefine(object):
    """Represents a single #define directive and performs ISO/IEC 9899:1999 (E) 6.10.3 Macro replacement.
    
    theTokGen is a PpToken generator that is expected to
    generate pp-tokens that appear after the start of the #define directive
    from the first non-whitespace token onwards i.e. the __init__ will,
    itself, consume leading whitespace.
    
    theFileId is a string that represents the file ID.
    
    theLine is a positive integer that represents the line in theFile that
    the #define statement occurred.
    
    Definition example, object-like macros: ::
    
        [identifier, [replacement-list (opt)], new-line, ...]
    
    Or function-like macros: ::
    
        [
            identifier,
            lparen,
            [identifier-list(opt),],
            ')',
            replacement-list,
            new-line,
            ...
        ]
    
    NOTE: No whitespace is allowed between the identifier and the lparen
    of function-like macros.
    
    The ``identifier-list`` of parameters is stored as a list of names.
    The replacement-list is stored as a list of
    preprocessor tokens.
    Leading and trailing whitespace in the replacement
    list is removed to facilitate redefinition comparison.
    """
    #: C standard definition of left parenthesis
    LPAREN                      = '('
    #: C standard definition of right parenthesis
    RPAREN                      = ')'
    #: C standard definition of identifier separator in function-like macros
    IDENTIFIER_SEPERATOR        = ','
    #: C standard definition of string'izing operator
    CPP_STRINGIZE_OP            = '#'
    #: C standard definition of concatenation operator
    CPP_CONCAT_OP               = '##'
    #: Our representation of a placemarker token
    PLACEMARKER                 = None
    #: Whitespace runs are replaced by a single space
    #: ISO/IEC 9899:1999 (E) 6.10.3.2-2
    STRINGIZE_WHITESPACE_CHAR   = ' '
    #: Variable argument (variadic) macro definitions
    VARIABLE_ARGUMENT_IDENTIFIER = '...'
    #: Variable argument (variadic) macro substitution
    VARIABLE_ARGUMENT_SUBSTITUTE = '__VA_ARGS__'
    #: This is what the reference count is set to on construction
    INITIAL_REF_COUNT = 0
    ########################
    # Section: Construction.
    ########################
    def __init__(self, theTokGen, theFileId, theLine):
        """Takes a preprocess token generator and creates a macro.
        The generator (e.g. a instance of PpTokeniser.next()) can
        generate pp-tokens that appear after the start of the #define directive
        from the first non-whitespace token onwards i.e. this __init__ will,
        itself, consume leading whitespace.
        
        theFileId is a string that represents the file ID.
        
        theLine is a positive integer that represents the line in theFile that
        the #define statement occurred. This must be >= 1.
        
        Definition example, object-like macros:
        [identifier, [replacement-list (opt)], new-line, ...]
        Or function-like macros: ::
        
            [
                identifier,
                lparen,
                [identifier-list(opt),
                ],
                ')',
                replacement-list,
                new-line,
                ...
            ]
        
        NOTE: No whitespace is allowed between the identifier and the lparen
        of function-like macros.
        
        The replacement-list is stored as a list of
        preprocessor tokens. The identifier-list is stored as a list of names.
        Leading and trailing whitespace in the replacement
        list is removed to facilitate redefinition comparison.
        """
        if theLine < FileLocation.START_LINE:
            raise ExceptionCpipDefineInitBadLine(
                'Irresponsible line number: %s' % theLine
                )            
        # Capture arguments
        self._fileLine = FileLocation.FileLine(theFileId, theLine)
        # This is indicates where this instance of a macro was #undef'd
        # It is set to None now as the macro is currently defined
        self._undefFileLine = None
        # Set up internals
        self._tokenCount = PpTokenCount.PpTokenCount()
        # A PpToken.PpToken object
        self._identifier = None
        # This is a list of PpToken.PpToken objects
        self._replaceTokTypesS = []
        # identifier-list for the declared parameters of function like macros
        # NOTE: This is a list of strings _not_
        # PpToken.PpToken objects
        self._paramS = None
        # Used by various methods to detect whitespacey things
        self._wsHandler = PpWhitespace.PpWhitespace()
        # Flag use to control whether arguments are expanded.
        # For object like macros this will be False
        # For function like macros this will be False if there is a
        # stringize ('#') or a token pasting operator ('##'). True otherwise.
        self._expandArguments = None
        # Reference count incremented on replacement or testing
        self._refCount = self.INITIAL_REF_COUNT
        # List of FileLocation.FileLineCol objects where replacement
        # has happened
        self._refFileLineColS = []
        # Variadic macro flag
        self._isVariadic = False
        try:
            myTtt = self._nextNonWsOrNewline(theTokGen)
            if self._wsHandler.isBreakingWhitespace(myTtt.t):
                # This is '#define pp-tokens\n', a non-directive
                # cpp.exe reports this as:
                # <stdin>:1:11: no macro name given in #define directive
                raise ExceptionCpipDefineInit(
                    'Premature newline in token stream.'
                    )
            if not myTtt.isIdentifier():
                self._consumeAndRaise(
                    theTokGen,
                    ExceptionCpipDefineInit(
                        'Missing #define <name> but token type "%s" value "%s" in token stream at %s' \
                                            % (myTtt.tt, myTtt.t, self._fileLine)))
            self._identifier = myTtt
            myTtt = self._retToken(theTokGen)
            # Next token must be LPAREN for function type macros or
            # whitespace for object type macros (6.10.3-3)
            if myTtt.t == self.LPAREN:
                # Function type macro
                self._ctorFunctionMacro(theTokGen)
            elif not myTtt.isWs():
                self._consumeAndRaise(
                    theTokGen,
                    ExceptionCpipDefineMissingWs(
                        'Missunderstood (6.10.3-3) token "%s" type "%s"' \
                            % (myTtt.t, myTtt.tt)))
            else:
                # Object type macros
                self._paramS = None
                self._isVariadic = False
                # If myTtt is a newline then this is #define FOO\n
                if not self._wsHandler.isBreakingWhitespace(myTtt.t):
                    self._appendToReplacementList(theTokGen)
                self._expandArguments = False
            # Integrity check
            self.assertReplListIntegrity()
            # Check that this has been set
            assert(self._expandArguments is not None)
        except StopIteration:
            raise ExceptionCpipDefineInit('Token stream is too short')
        assert(self.isCurrentlyDefined)

    def _appendArgIdentifier(self, theTok, theGenTok):
        """Appends the token text to the argument identifier list."""
        if theTok.t in self._paramS:
            self._consumeAndRaise(
                theGenTok,
                ExceptionCpipDefineDupeId(
                    'Token %s already in %s' \
                    % (theTok.t, self._paramS)
                    )
                )
        self._paramS.append(theTok.t)
    
    def _ctorFunctionMacro(self, theGenTok):
        """Construct function type macros.
        [[identifier-list,] ,')', replacement-list, new-line, ...]
        The identifier-list is not specified in the specification but there
        seems to be some disparity between the standards and cpp.exe.
        The relevant bits of the standards [C: ISO/IEC 9899:1999(E) 6.10.3-10
        and -11 and C++: ISO/IEC 14882:1998(E) 16.3-9 (C++)] appear, to me,
        to suggest that left and right parenthesis are allowed in the
        identifier-list and that (,) is ignored. But cpp.exe will not accept
        that.
        
        Playing with cpp -E it seems that it is a comma separated
        list where whitespace is ignored, nothing else is allowed.
        See unit tests testInitFunction_70(), 71 and 72.
        cpp.exe also is not so strict when it comes the the above sections. For
        example in this:
        #define FOO(a,b,c) a+b+c
        FOO (1,(2),3)
        The whitespace between FOO and LPAREN is ignored and the replacement
        occurs."""
        assert(self.isCurrentlyDefined)
        self._paramS = []
        # This will be set to False if stringize or token pasting is used
        self._expandArguments = True
        while 1:
            aTtt = self._retToken(theGenTok)
            if not aTtt.isWs():
                if aTtt.t == self.RPAREN:
                    break
                elif aTtt.t == ',':
                    pass
                elif aTtt.isIdentifier():
                    # An identifier-list token
                    self._appendArgIdentifier(aTtt, theGenTok)
                elif aTtt.t == self.VARIABLE_ARGUMENT_IDENTIFIER:
                    # An variadic identifier
                    self._appendArgIdentifier(aTtt, theGenTok)
                else:
                    self._consumeAndRaise(
                        theGenTok,
                        ExceptionCpipDefineInit(
                            'Don\'t understand token "%s" type %s in function like macro' \
                                                          % (aTtt.t, aTtt.tt)))
            elif self._wsHandler.isBreakingWhitespace(aTtt.t):
                raise ExceptionCpipDefineInit(
                    'Premature newline in function like macro'
                    )
        # Include a single placeholder if the identifier list is empty
        # TODO: Explain the comment above
        if len(self._paramS) == 0:
            pass
            #self._paramS.append(self.PLACEMARKER)
        # Check the identifier list to see if I am a variadic macro
        self._isVariadic = False
        for aId in self._paramS:
            if aId == self.VARIABLE_ARGUMENT_IDENTIFIER:
                self._isVariadic = True
            elif self._isVariadic:
                self._consumeAndRaise(
                    theGenTok,
                    ExceptionCpipDefineInit(
                        'Variadic identifier seen but not as last identifier in argument list'
                        )
                    )
        self._appendToReplacementList(theGenTok)

    def _appendToReplacementList(self, theGenTok):
        """Takes a token sequence up to a newline and assign it
        to the replacement-list. Leading and trailing whitespace is ignored.
        TODO: Set setPrevWs flag where necessary."""
        assert(self.isCurrentlyDefined)
        # Whitespace is lazily evaluated so that trailing
        # whitespace is only added when necessary.
        trailingWs = []
        # Check for stringize operator that must be followed by a identifier
        # the identifier list
        flagNextNonWsIsId = False
        while 1:
            aTok = self._retToken(theGenTok)
            if aTok.isWs():
                if self._wsHandler.isBreakingWhitespace(aTok.t):
                    break
                # only add non-leading whitespace
                if len(self._replaceTokTypesS) != 0:
                    trailingWs.append(aTok)
            else:
                # Check for '#'
                # See ISO/IEC 9899:1999(E) Section 6.10.3.2-1
                # TODO: Test this
                if flagNextNonWsIsId:
                    if aTok.t in self._paramS \
                    or (self._isVariadic and aTok.t == self.VARIABLE_ARGUMENT_SUBSTITUTE):
                        # Unset flag as constraint is passed
                        flagNextNonWsIsId = False
                    else:
                        self._consumeAndRaise(
                            theGenTok,
                            ExceptionCpipDefineInit(
                                '\'#\' is not followed by a macro parameter but "%s" of type %s' \
                                    % (aTok.t, aTok.tt)))
                # Set flags on '#' or '##'
                if not self.isObjectTypeMacro:
                    if aTok.t == self.CPP_STRINGIZE_OP:
                        flagNextNonWsIsId = True
                        # Do not expand arguments if I involve stringizing
                        self._expandArguments = False
                    if aTok.t == self.CPP_CONCAT_OP:
                        # Do not expand arguments if I involve token pasting
                        self._expandArguments = False
                # End check for '#' or '##'
                #
                # Non-whitespace so we are compelled to add the stack
                if len(trailingWs):
                    for t in trailingWs:
                        self.__addTokenAndTypeToReplacementList(t)
                    trailingWs = []
                self.__addTokenAndTypeToReplacementList(aTok)
        # Check that '##' is not the first or last token
        # See ISO/IEC 9899:1999(E) Section 6.10.3.3-1
        # TODO: Test this
        if len(self._replaceTokTypesS) > 0:
            if self._replaceTokTypesS[0].t == self.CPP_CONCAT_OP:
                self._consumeAndRaise(
                    theGenTok,
                    ExceptionCpipDefineInit(
                        '\'##\' cannot appear at the begining of a macro expansion'))
            if self._replaceTokTypesS[-1].t == self.CPP_CONCAT_OP:
                self._consumeAndRaise(
                    theGenTok,
                    ExceptionCpipDefineInit(
                    '\'##\' cannot appear at the end of a macro expansion'))
        # Variadic tests
        if not self._isVariadic:
            # If I am not a variadic macro then I can not have __VA_ARGS__
            # ISO/IEC 9899:1999(E) Section 6.10.3-5
            for aRepTtt in self._replaceTokTypesS:
                #print 'TRACE: aRepTtt', aRepTtt
                if aRepTtt.t == self.VARIABLE_ARGUMENT_SUBSTITUTE:
                    raise ExceptionCpipDefineInit(
                        '%s can only appear in the expansion of a C99 variadic macro' \
                        % self.VARIABLE_ARGUMENT_SUBSTITUTE
                        )

    def __addTokenAndTypeToReplacementList(self, theTtt):
        """Adds a token and a token type to the replacment list. Runs of
        whitespace tokens are concatenated."""
        assert(self.isCurrentlyDefined)
        if len(self._replaceTokTypesS) > 0 \
        and theTtt.isWs() and self._replaceTokTypesS[-1].isWs():
            self._replaceTokTypesS[-1].merge(theTtt)
        else:
            self._replaceTokTypesS.append(theTtt)
    ####################
    # End: Construction.
    ####################

    #############################
    # Section: Utility functions.
    #############################
    def _isPlacemarker(self, theTok):
        """Returns True if the Tok represents a PLACEMARKER token.
        This is the correct comparison operator can be used if self.PLACEMARKER
        is defined as None."""
        return theTok is self.PLACEMARKER
    
    def strIdentPlusParam(self):
        """Returns the identifier name and parameters if a function-like macro
        as a string."""
        retList = [self.identifier, ]
        if not self.isObjectTypeMacro:
            # Function type macros
            idList = []
            for anId in self._paramS:
                # This is needed when a function macro is
                # #define p() something
                # and that means there is a single identifier that is a
                # self.PLACEMARKER
                if self._isPlacemarker(anId):
                    anId = ''
                idList.append(anId)
            retList.append('(%s)' % (','.join(idList)))
        return ''.join(retList)

    def strReplacements(self):
        """Returns the replacements tokens with minimised whitespace as a string."""
        retList = []
        if len(self._replaceTokTypesS) > 0:
            for aTok in self._replaceTokTypesS:
                if aTok.isWs():
                    retList.append(' ')
                else:
                    retList.append(aTok.t)
        return ''.join(retList)

    def __str__(self):
        retList = ['#define %s' % (self.strIdentPlusParam()), ]
#===============================================================================
#        if not self.isObjectTypeMacro:
#            # Function type macros
#            idList = []
#            for anId in self._paramS:
#                # This is needed when a function macro is
#                # #define p() something
#                # and that means there is a single identifier that is a
#                # self.PLACEMARKER
#                if self._isPlacemarker(anId):
#                    anId = ''
#                idList.append(anId)
#            retList.append('(%s)' % (','.join(idList)))
#===============================================================================
        if len(self._replaceTokTypesS) > 0:
            retList.append(' ')
            retList.append(self.strReplacements())
        
#===============================================================================
#        if len(self._replaceTokTypesS) > 0:
#            #retList.append(' %s' % (PpToken.tokensStr(self._replaceTokTypesS)))
#            myStrS = []
#            for aTok in self._replaceTokTypesS:
#                if aTok.isWs():
#                    myStrS.append(' ')
#                else:
#                    myStrS.append(aTok.t)
#            retList.append(' %s' % (''.join(myStrS)))
#===============================================================================
        cmtStr = '%s#%d Ref: %d %s' \
                       % (
                          self.fileId,
                          self.line,
                          self.refCount,
                          self.isCurrentlyDefined,
                          )
        if not self.isCurrentlyDefined:
            cmtStr += ' %s#%d' % (self.undefFileId, self.undefLine)  
        retList.append(' /* %s */' % cmtStr)
        return ''.join(retList)

    def _retToken(self, theGen):
        """Returns the next token object and increments the IR."""
        assert(self.isCurrentlyDefined)
        retTok = next(theGen)
        # Note: True is always used as this is always unconditionally compiled
        self._tokenCount.inc(retTok, True)
        # Check for bad whitespace
        if retTok.isWs() \
        and not self._wsHandler.isAllMacroWhitespace(retTok.t):
            # ISO/IEC 14882:1998(E) 16-2 only ' ' and '\t' as ws
            if self._wsHandler.isBreakingWhitespace(retTok.t):
                # '\n' consumed so straightforward raise
                raise ExceptionCpipDefineBadWs(
                    'Invalid macro whitespace in "%s"' % retTok.t
                )
            else:
                # Consume to '\n'  and raise
                self._consumeAndRaise(
                    theGen,
                    ExceptionCpipDefineBadWs(
                        'Invalid macro whitespace in "%s"' % retTok.t
                        )
                )
        return retTok

    def _nextNonWsOrNewline(self, theGen):
        """Returns the next non-whitespace token or whitespace that contains a
        newline."""
        assert(self.isCurrentlyDefined)
        while 1:
            myTtt = self._retToken(theGen)
            if not myTtt.isWs() \
            or self._wsHandler.isBreakingWhitespace(myTtt.t):
                return myTtt
            # Non-breaking whitespace so continue

    def _consumeNewline(self, theGen):
        """Consumes all tokens up to and including the next newline."""
        assert(self.isCurrentlyDefined)
        while 1:
            myTtt = self._retToken(theGen)
            if self._wsHandler.isBreakingWhitespace(myTtt.t):
                break

    def _consumeAndRaise(self, theGen, theException):
        """Consumes all tokens up to and including the next newline then raises
        an exception. This is commonly used to get rid of bad token streams but
        allow the caller to catch the exception, report the error and
        continue."""
        assert(self.isCurrentlyDefined)
        self._consumeNewline(theGen)
        raise theException

    def assertReplListIntegrity(self):
        """Tests that any identifier tokens in the replacement list are
        actually replaceable. This will raise an assertion failure if
        not. It is really an integrity tests to see if an external entity
        has grabbed a reference to the replacement list and set a token
        to be not replaceable."""
        assert(self.isCurrentlyDefined)
        for aTtt in self._replaceTokTypesS:
            assert(not aTtt.isIdentifier() or aTtt.canReplace), \
                'Token %s is invalid' % str(aTtt)
    #########################
    # End: Utility functions.
    #########################

    ############################################
    # Section: Replacement i.e. Macro expansion.
    ############################################
    def incRefCount(self, theFileLineCol=None):
        """Increment the reference count. Typically callers do this when
        replacement is certain of in the event of definition testing e.g.
        ``#ifdef SPAM or defined(SPAM)`` etc. Or if the macro is expanded e.g.
        ``#define SPAM_N_EGGS spam and eggs``
        The menu is SPAM_N_EGGS.
        theFileLineCol is a FileLocation.FileLineCol object.
        """ 
        if not self.isCurrentlyDefined:
            raise ExceptionCpipDefine(
                "incRefCount() on already #undef'd macro instance of self"
                )            
        self._refCount += 1
        if theFileLineCol is not None:
            self._refFileLineColS.append(theFileLineCol)
    
    #=============================================
    # Section: Replacement of object style macros.
    #=============================================
    def replaceObjectStyleMacro(self):
        """Returns a list of [(token, token_type), ...] from the replacement
        of an object style macro."""
        assert(self.isCurrentlyDefined)
        assert(self.isObjectTypeMacro), \
            'replaceObjectStyleMacro() called on function style macro'
        return self._objectLikeReplacement()

    def _objectLikeReplacement(self):
        """Returns the replacement list for an object like macro.
        This handles the '##' token i.e. [cpp.concat].
        Returns a list of pairs i.e. [(token, token_type), ...]"""
        assert(self.isCurrentlyDefined)
        assert(self.isObjectTypeMacro), \
            '_objectLikeReplacement() called on non-object like macro'
        retReplList = []
        flagConcatSeen = False
        # Take a copy of the replacement list as we want to set
        # the canRpelace flag independently
        #assert(0), '[:] on mutable'
        for aTtt in copy.deepcopy(self._replaceTokTypesS):
            if aTtt.t == self.CPP_CONCAT_OP:
                flagConcatSeen = True
                # Unwind any whitespace tokens
                while 1:
                    assert(len(retReplList) > 0), \
                        'Leading ## has crept through the constructor'
                    rTtt = retReplList[-1]
                    if not rTtt.isWs():
                        break
                    else:
                        retReplList.pop()
            else:
                if flagConcatSeen:
                    if not aTtt.isWs():
                        # Add this token to the one on the end of
                        # the retReplList
                        retReplList[-1].merge(aTtt)
                        # Done with the '##'
                        flagConcatSeen = False
                    # Otherwise ignore whitespace after '##'
                else:
                    # Normal, no '##' involved
                    retReplList.append(aTtt)
        assert(not flagConcatSeen), \
            'Trailing ## has crept through the constructor'
        return retReplList
    #=========================================
    # End: Replacement of object style macros.
    #=========================================

    #========================================================
    # Section: Replacement of function style macros.
    #
    # NOTE: This is more complex because of the interaction
    # between this class and the MacroReplacementEnv class.
    # See MacroReplacementEnv.replace() for more information.
    #========================================================
    def consumeFunctionPreamble(self, theGen):
        """This consumes tokens to the preamble of a Function style macro
        invocation. This really means consuming whitespace and the opening
        ``LPAREN``.
        
        This will return either:
        
        * None - Tokens including the leading LPAREN have been consumed.
        * List of (token, token_type) if the LPAREN is not found.
        
        For example given this: ::

            #define t(a) a+2
            t   (21) - t  ;

        For the first ``t`` this would consume ``'   ('`` and return None leaving the
        next token to be ('21', 'pp-number').
        
        For the second ``t`` this would consume ``'  ;'`` and return: ::

            [
                ('  ', 'whitespace'),
                (';',   'preprocessing-op-or-punc'),
            ]

        This allows the MacroReplacementEnv to generate the correct result: ::
        
            21 +2 - t ;
        """
        assert(self.isCurrentlyDefined)
        assert(not self.isObjectTypeMacro), \
            'consumeFunctionPreamble() called on object like macro'
        # Function type macros need to look ahead for the identifiers
        # The relevant bits of the standards [C: ISO/IEC 9899:1999(E) 6.10.3-10
        # and -11 and C++: ISO/IEC 14882:1998(E) 16.3-9 (C++)] say that the
        # next token must be LPAREN but cpp.exe is not so strict. For example:
        # #define FOO(a,b,c) a+b+c
        # FOO (1,2,3)
        # The whitespace between FOO and LPAREN is ignored and the replacement
        # occurs.
        # We do the same as cpp.exe here.
        #
        # This lists stores tokens processed but that do not lead to a macro
        # replacement. These will be returned on failure.
        failTokList = []
        while 1:
            # This emulates cpp.exe that allows any amount of ws
            # between the identifier and LPAREN
            try:
                myTtt = self._retToken(theGen)
            except StopIteration:
                return failTokList
            if not myTtt.isWs():
                break
            failTokList.append(myTtt)
            # ws range check not done [ISO/IEC 14882:1998(E) 16-2 only ' ' and
            # '\t' as ws]
        if myTtt.t != self.LPAREN:
            # Failure so return what we have seen
            # This can happen like this:
            # #define t(a) a
            # #define f(a) a+2
            # f(t(1) + t )
            # Expands to:
            # f(1 + t ) //< t ) does not expand
            # 1 + t+2
            # In this case the failTokList is [t, ' ', ')'] that can be used
            # for further processing
            # TODO: Test case
            #
            # Send the token back to the generator for further processing
            # and return the failed token list for further processing
            theGen.send(myTtt)
            return failTokList
        # OK consumed to LPAREN
        return None

    def retArgumentListTokens(self, theGen):
        """For a function macro this reads the tokens following a ``LPAREN`` and
        returns a list of arguments where each argument is a list of
        PpToken objects.
        
        Thus this function returns a list of lists of PpToken objects,
        for example given this: ::
        
            #define f(x,y) ...
            f(a,b)
        
        This function, then passed "a,b)" returns: ::
        
            [
                [
                    PpToken.PpToken('a', 'identifier'),
                ],
                [
                    PpToken.PpToken('b', 'identifier'),
                ],
            ]
        
        And an invocation of:
        ``f(1(,)2,3)`` i.e. this gets passed via the generator ``"1(,)2,3)"``
        and returns two argunments: ::
        
            [
                [
                    PpToken('1', 'pp-number'),
                    PpToken('(', 'preprocessing-op-or-punc'),
                    PpToken(',', 'preprocessing-op-or-punc'),
                    PpToken(')', 'preprocessing-op-or-punc'),
                    PpToken('2', 'pp-number'),
                ],
                [
                    PpToken('3', 'pp-number'),
                ],
            ]
        
        So this function supports two cases:
        
        1. Parsing function style macro declarations.
        2. Interpreting function style macro invocations where the argument list
           is subject to replacement before invoking the macro.
        
        In the case that an argument is missing a ``PpDefine.PLACEMARKER``
        token is inserted. For example: ::
        
            #define FUNCTION_STYLE(a,b,c) ...
            FUNCTION_STYLE(,2,3)
        
        Gives: ::
        
            [
                PpDefine.PLACEMARKER,
                [
                    PpToken.PpToken('2',       'pp-number'),
                ],
                [
                    PpToken.PpToken('3',       'pp-number'),
                ],
            ]
        
        Placemarker tokens are not used if the macro is defined with no
        arguments.
        This might raise a ExceptionCpipDefineBadArguments if the list
        does not match the prototype or a StopIteration if the token list is
        too short.
        This ignores leading and trailing whitespace for each argument.
        
        TODO: Raise an ExceptionCpipDefineBadArguments if there is a #define
        statement. e.g.: ::
        
            #define f(x) x x
            f (1
            #undef f
            #define f 2
            f)
        
        """
        assert(self.isCurrentlyDefined)
        assert(not self.isObjectTypeMacro), \
            'retArgumentListTokens() called on object like macro'
        # Count '(' and ')'
        pDepth = 1
        # Argument is a list of (token, token-type)
        # So the argument '1+7' would be (types are shown as text for clarity,
        # in practice they would be enumerated):
        #[
        #    ('1', 'pp-number'),
        #    ('+', 'preprocessing-op-or-punc'),
        #    ('7', 'pp-number')
        #]
        myArg = []
        # List of arguments, this is a list of lists of class PpToken that we
        # are going to return
        myArgS = []
        # Whitespace is lazily evaluated so that trailing
        # whitespace is only added when necesary.
        # Leading whitespace is ignored.
        trailingWs = []
        while 1:
            myTtt = self._retToken(theGen)
            if myTtt.t == self.LPAREN:
                pDepth += 1
                myArg.append(myTtt)
            elif myTtt.t == self.RPAREN \
            or myTtt.t == ',':
                if myTtt.t == self.RPAREN:
                    pDepth -= 1
                if pDepth == 0 \
                or (pDepth == 1 and myTtt.t == ','):
                    # Accumulate the arguments
                    if len(myArg) == 0:
                        # We use [] as a placemarker token to represent a
                        # missing argument between commas
                        # ISO/IEC 9899:1999 6.10.3.3-2, -3
                        # [There does not seem to be a reference in the C++
                        # standard but we behave the same like cpp.exe does]
                        myArgS.append(self.PLACEMARKER)
                    #elif pDepth != 0 or len(myArg):
                    else:
                        myArgS.append(myArg)
                    myArg = []
                    trailingWs = []
                    if pDepth == 0:
                        break
                else:
                    assert(not self._wsHandler.isAllWhitespace(myTtt.t))
                    # Non-whitespace token so we are forced to add
                    # whitespace prefix
                    myArg += trailingWs
                    trailingWs = []
                    myArg.append(myTtt)
            else:
                # Potiential addition, depends on whitespace
                if self._wsHandler.isAllWhitespace(myTtt.t):
                    if len(myArg) > 0:
                        # Lazy accumulation
                        trailingWs.append(myTtt)
                    else:
                        # This is leading whitespace that we ignore
                        pass
                else:
                    # Non-whitespace token so we are forced to add
                    # whitespace prefix
                    myArg += trailingWs
                    trailingWs = []
                    myArg.append(myTtt)
        # The above code will generate a placemarker token for a macro
        # with no arguments called with no arguments so fix this.
        if len(self._paramS) == 0 \
        and len(myArgS) == 1 \
        and self._isPlacemarker(myArgS[0]):
            myArgS = []
        # Now check against the macro definition
        # Have all the arguments, check the length matches
        # cpp.exe behaviour:
        # #define FOO(a,b,c) a+b+c
        # FOO(1,2)
        # Gives:
        #
        # src.h:2:8: macro "FOO" requires 3 arguments, but only 2 given
        # FOO
        # Or if to many given:
        # src.h:2:12: macro "FOO" passed 4 arguments, but takes just 3
        # TODO: Remove Kludge on next line
        # Kludge:
        #if len(myArgS) == 1 and len(myArgS[0]) == 0:
        #    myArgS = []
        # TODO: Refactor this conditional to take account of variable
        # arguments without duplication
        if not self._isVariadic:
            if len(myArgS) != len(self._paramS):
                if len(myArgS) < len(self._paramS):
                    msg = 'macro "%s" requires %d arguments, but only %d given' \
                          % (self.identifier, len(self._paramS), len(myArgS))
                else:
                    msg = 'macro "%s" passed %d arguments, but takes just %d' \
                          % (self.identifier, len(myArgS), len(self._paramS))
                raise ExceptionCpipDefineBadArguments(msg)
        else:
            # Variadic macros, any number of supplied arguments because
            # they can be turned into PLACEHOLDERS
            # For example, this is OK
            # #define F(a,...) A a B __VA_ARGS__ C
            # F()
            # it becomes:
            # A B C
            # But #define F(a,b,...)
            # F() is an error
            #assert(0)
            if len(myArgS) < (len(self._paramS)-1):
                msg = 'macro "%s" requires %d arguments, but only %d given' \
                      % (self.identifier, (len(self._paramS)-1), len(myArgS))
                raise ExceptionCpipDefineBadArguments(msg)
        return myArgS

    def replaceArgumentList(self, theArgList):
        """Given an list of arguments this does argument substitution and
        returns the replacement token list. The argument list is of the form
        given by retArgumentListTokens(). The caller must have replaced any
        macro invocations in theArgList before calling this method.
        NOTE: For function style macros only."""
        assert(self.isCurrentlyDefined)
        assert(not self.isObjectTypeMacro), \
            'replaceArgumentList() called on object like macro'
        myReplaceMap = self._retReplacementMap(theArgList)
        myReplacements = self._functionLikeReplacement(myReplaceMap)
        return myReplacements

    def _retReplacementMap(self, theArgs):
        """Given a list of lists of (token, type) this returns a map of:
        {identifier : [replacement_token and token types, ...], ...}
        For example for:
        #define FOO(c,b,a) a+b+c
        FOO(1+7,2,3)
        i.e theArgs is (types are shown as text for clarity, in practice they
        would be enumerated):
        [
            [
                PpToken.PpToken('1', 'pp-number'),
                PpToken.PpToken('+', 'preprocessing-op-or-punc'),
                PpToken.PpToken('7', 'pp-number')
            ],
            [
                PpToken.PpToken('2', 'pp-number'),
            ],
            [
                PpToken.PpToken('3', 'pp-number'),
            ],
        ]
        Map would be:
        {
            'a' : [
                    PpToken.PpToken('3', 'pp-number'),
                ],
            'b' : [
                    PpToken.PpToken('2', 'pp-number'),
                ],
            'c' : [
                    PpToken.PpToken('1', 'pp-number'),
                    PpToken.PpToken('+', 'preprocessing-op-or-punc'),
                    PpToken.PpToken('7', 'pp-number')
                ],
        }
        Note that values that are placemarker tokens are
        PpDefine.PLACEMARKER. For example:
        #define FOO(a,b,c) a+b+c
        FOO(,2,)
        Generates:
        {
            'a' : PpDefine.PLACEMARKER,
            'b' : [
                    ('2', 'pp-number'),
                ]
            'c' : PpDefine.PLACEMARKER,
        }
        PERF: See TODO below.
        TODO: Return a map of identifiers to indexes in the supplied argument as
        this will save making a copy of the argument tokens?
        So:
        #define FOO(c,b,a) a+b+c
        FOO(1+7,2,3)
        Would return a map of:
        {
            'a' : 2,
            'b' : 1,
            'c' : 0,
        }
        And use index -1 for a placemarker token???:
        #define FOO(a,b,c) a+b+c
        FOO(,2,)
        Generates:
        {
            'a' : -1,
            'b' : 1
            'c' : -1,
        }
        """
        assert(self.isCurrentlyDefined)
        assert(not self.isObjectTypeMacro), \
            '_retReplacementMap() called on object like macro'
        assert(self._isVariadic or (len(theArgs) == len(self._paramS)))
        retMap = {}
        # NOTE: self._paramS is a list of strings _not_ PpToken.PpToken objects
        #print
        #print '_retReplacementMap(): self._paramS:', self._paramS
        #print '_retReplacementMap():      theArgs:', theArgs
        for i, tok in enumerate(self._paramS):
            assert(not tok in retMap), \
                'Duplicate identifier in function macro has slipped through the constructor.'
            if self._isVariadic and i >= len(theArgs):
                # This is the case where:
                # #define FV(a,b,c,...) a - b - c - __VA_ARGS__\n. ...
                # Invoked with FV(1,2,3)
                # Internally this will give rise to:
                # self._paramS ['a', 'b', 'c', '...']
                # theArgs [["1"], ["2"], ["3"]]
                break
            #print '_retReplacementMap(): self._paramS[%d]: %s' % (i, tok)
            #print '_retReplacementMap():      theArgs[%d]: %s' % (i, theArgs[i])
            # Only add to map is it is not a placeholder token
            if not self._isPlacemarker(theArgs[i]):
                myArgList = []
                if self._isVariadic and tok == self.VARIABLE_ARGUMENT_IDENTIFIER:
                    myArgList.extend(theArgs[i])
                    i += 1
                    while i < len(theArgs):
                        myArgList.append(PpToken.PpToken(',', 'preprocessing-op-or-punc'))
                        if not self._isPlacemarker(theArgs[i]):
                            myArgList.extend(theArgs[i])
                        i += 1
                    retMap[tok] = myArgList
                    #print 'Breaking'
                    break
                else:
                    for aTtt in theArgs[i]:
                        if aTtt.isWs():
                            # Replace newline with a single whitespace character
                            # C ISO/IEC 9899:1999(E) 6.10-3 and
                            # C++ ISO/IEC 14882:1998(E) 16.3-9
                            aTtt.replaceNewLine()
                        myArgList.append(aTtt)
                    retMap[tok] = myArgList
            else:
                if self._isVariadic and tok == self.VARIABLE_ARGUMENT_IDENTIFIER:
                    myArgList = []
                    #myArgList.append(self.PLACEMARKER)
                    i += 1
                    while i < len(theArgs):
                        myArgList.append(PpToken.PpToken(',', 'preprocessing-op-or-punc'))
                        if self._isPlacemarker(theArgs[i]):
                            #myArgList.append(self.PLACEMARKER)
                            pass
                        else:
                            myArgList.extend(theArgs[i])
                        i += 1
                    retMap[tok] = myArgList
                    #print 'Breaking'
                    break
                elif not self._isPlacemarker(tok):
                    retMap[tok] = self.PLACEMARKER
        return retMap

    def _functionLikeReplacement(self, theArgMap):
        """Returns the replacement list where if a token is encountered that
        is a key in the map then the value in the map is inserted into the
        replacement list.
        theArgMap is of the form returned by _retReplacementMap().
        This also handles the '#' token i.e. [cpp.stringize]
        and '##' token i.e. [cpp.concat].
        Returns a list of pairs i.e. [(token, token_type), ...]"""
        assert(self.isCurrentlyDefined), \
            '_functionLikeReplacement() called on undefined macro'
        assert(not self.isObjectTypeMacro), \
            '_functionLikeReplacement() called on object like macro'
        retReplList = []
        flagStringize = False
        flagConcatSeen = False
        # Take a copy of the replacement list so that we can set
        # the canReplace flag independently
        #assert(0), '[:] on mutable'
        for myTtt in copy.deepcopy(self._replaceTokTypesS):
            if myTtt.t in theArgMap:
                if self._isPlacemarker(theArgMap[myTtt.t]):
                    if flagStringize:
                        retReplList.append(
                                self._cppStringize(''),
                            )
                        flagStringize = False
                else:
                    if flagStringize:
                        retReplList.append(
                                self._cppStringize(theArgMap[myTtt.t]),
                            )
                        flagStringize = False
                    else:
                        # Respect flagConcatSeen here and concat theArgMap[t]
                        # on to the retReplList[-1]
                        # Set type to 'concat_result' or at least not
                        # 'identifier'
                        # to make sure that the result is not
                        # subject to further replacement?
                        # NO, it can be:
                        ##define AB something
                        ##define q(x,y) x ## y
                        #q(A,B);
                        # Results in:
                        # AB
                        if flagConcatSeen:
                            if len(retReplList) > 0:
                                # Merge the first token from the map
                                #print
                                #print str(self)
                                #print 'theArgMap', theArgMap
                                #print 'retReplList[-1]', retReplList[-1]
                                #print 'theArgMap[myTtt.t]', theArgMap[myTtt.t]
                                retReplList[-1].merge(theArgMap[myTtt.t][0])
                                # Append the remainder from the map
                                retReplList += theArgMap[myTtt.t][1:]
                            else:
                                retReplList += theArgMap[myTtt.t]
                            flagConcatSeen = False
                        else:
                            retReplList += copy.deepcopy(theArgMap[myTtt.t])
            elif myTtt.t == self.CPP_STRINGIZE_OP:
                flagStringize = True
                if flagConcatSeen:
                    self.__logWarningHashHashHash()
            elif myTtt.t == self.CPP_CONCAT_OP:
                flagConcatSeen = True
                if flagStringize:
                    self.__logWarningHashHashHash()
                # Unwind any whitespace tokens
                while len(retReplList) > 0 and retReplList[-1].isWs():
                    retReplList.pop()
            # Variable argument processing
            elif self._isVariadic and myTtt.t == self.VARIABLE_ARGUMENT_SUBSTITUTE:
                # Anly add if a variable argument is available e.g. not here
                # #define F1(a,...) |a| __VA_ARGS__ EOL
                # F1()  // | | EOL
                if self.VARIABLE_ARGUMENT_IDENTIFIER in theArgMap:
                    if flagStringize:
                        retReplList.append(
                                self._cppStringize(theArgMap[self.VARIABLE_ARGUMENT_IDENTIFIER]),
                            )
                        flagStringize = False
                    else:
                        retReplList.extend(theArgMap[self.VARIABLE_ARGUMENT_IDENTIFIER])
                # Subtle bug here, if I have:
                # __ASM_SEL(a,b) a,b
                # __ASM_SIZE(inst, ...) __ASM_SEL(inst##l##__VA_ARGS__, inst##q##__VA_ARGS__)
                # And I call __ASM_SIZE(a) i.e. __VA__ARGS__ is empty then without
                # the following line the ',' will be pasted on to 'al' i.e.
                # ['__ASM_SEL', '(', 'al,', 'aq', ')']
                # Rather than the correct tokens:
                # ['__ASM_SEL', '(', 'al', ',', 'aq', ')']
                flagConcatSeen = False
            else:
                if flagConcatSeen:
                    if not myTtt.isWs():
                        retReplList[-1].merge(myTtt)
                        # Done with the '##'
                        flagConcatSeen = False
                    # Otherwise ignore whitespace after '##'
                else:
                    # Normal, no '#' or '##' involved
                    retReplList.append(myTtt)
        #assert(not flagStringize), 'Trailing # has crept through the constructor'
        #assert(not flagConcatSeen), 'Trailing ## has crept through the constructor'
        return retReplList

    def __logWarningHashHashHash(self):
        """Emit a warning to the log that # and ## are dangerous together."""
        logging.warning(
            "Using both '#' and '##' gives rise to unspecified behaviour."
        )

    def _cppStringize(self, theArgTokens):
        """Applies the '#' operator to function style macros
        ISO/IEC ISO/IEC 14882:1998(E) 16.3.2 The # operator [cpp.stringize]"""
        assert(self.isCurrentlyDefined)
        assert(not self.isObjectTypeMacro), \
            '_cppStringize called but # character not significant in a object like macro.'
        # tempList is a list of strings
        #print 'TRACE: _cppStringize():', theArgTokens
        tempList = []
        for aTtt in theArgTokens:
            if aTtt.isWs():
                # Leading whitespace is ignored
                # and whitespace runs are represented by a single ' '
                # ISO/IEC 9899:1999 (E) 6.10.3.2-2
                if len(tempList) > 0 \
                and tempList[-1] != self.STRINGIZE_WHITESPACE_CHAR:
                    tempList.append(self.STRINGIZE_WHITESPACE_CHAR)
            else:
                tempList.append(aTtt.t)
        # Trailing whitespace is ignored
        # ISO/IEC 9899:1999 (E) 6.10.3.2-2
        if len(tempList) > 0 \
        and tempList[-1] == self.STRINGIZE_WHITESPACE_CHAR:
            tempList.pop()
        return PpToken.PpToken(
            '"%s"' % ''.join(tempList).replace('"', '\\"'),
            'string-literal')

    #===============================================
    # Section: Replacement of function style macros.
    #===============================================
    ########################################
    # End: Replacement i.e. Macro expansion.
    ########################################

    ########################################################
    # Section: Accessors and comparison (i.e. redefinition).
    ########################################################
    #============================
    # Section: Read only methods.
    #============================
    @property
    def isObjectTypeMacro(self):
        """True if this is an object type macro and
        False if it is a function type macro."""
        return self._paramS is None

    @property
    def identifier(self):
        """The macro identifier i.e. the name as a string."""
        return self._identifier.t

    @property
    def tokenCounter(self):
        """The PpTokenCount object that counts tokens that have been consumed
        from the input."""
        return self._tokenCount
    
    @property
    def tokensConsumed(self):
        """The total number of tokens consumed by the class."""
        return self._tokenCount.totalAll

    @property
    def replacements(self):
        """The list of zero or more replacement tokens as strings."""
        return [t.t for t in self._replaceTokTypesS]

    @property
    def replacementTokens(self):
        """The list of zero or more replacement token
        i.e. [class PpToken, ...]."""
        return self._replaceTokTypesS

    @property
    def parameters(self):
        """The list of parameter names as strings for a function like macros
        or None if this is an object type Macro."""
        return self._paramS

    @property
    def expandArguments(self):
        """The flag that says whether arguments should be expanded.
        For object like macros this will be False. For function like macros
        this will be False if there is a stringize ('#') or a token pasting
        operator ('##'). True otherwise."""
        return self._expandArguments
    
    @property
    def fileId(self):
        """The file ID given as an argument in the constructor."""
        return self._fileLine.fileId

    @property
    def line(self):
        """The line number given as an argument in the constructor."""
        return self._fileLine.lineNum
    
    @property
    def refCount(self):
        """Returns the current reference count as an integer less its initial
        value on construction."""
        return self._refCount - self.INITIAL_REF_COUNT

    @property
    def isReferenced(self):
        """Returns True if the reference count has been incremented since
        construction."""
        return self._refCount > self.INITIAL_REF_COUNT 

    @property
    def isCurrentlyDefined(self):
        """Returns True if the current instance is a valid definition
        i.e. it has not been #undef'd."""
        return self._undefFileLine is None

    @property
    def undefFileId(self):
        """The file ID where this macro was undef'd or None."""
        if self._undefFileLine is not None:
            return self._undefFileLine.fileId

    @property
    def undefLine(self):
        """The line number where this macro was undef'd or None."""
        if self._undefFileLine is not None:
            return self._undefFileLine.lineNum
        
    @property
    def refFileLineColS(self):
        """Returns the list of FileLineCol objects where this macro was referenced."""
        return self._refFileLineColS
    #============================
    # End: Read only methods.
    #============================

    #=============================
    # Comparison and redefinition.
    #=============================
    def __eq__(self, other):
        return self.isSame(other) == 0
    
    def isSame(self, other):
        """Tests 'sameness'. Returns:
        -1 if the identifiers are different.
        1 if the identifiers are the same but redefinition is NOT allowed.
        0 if the identifiers are the same but redefinition is allowed i.e. the
        macros are equivelent."""
        if not self.isCurrentlyDefined:
            raise ExceptionCpipDefine(
                "#undef on already #undef'd instance of self macro"
                )            
        if not other.isCurrentlyDefined:
            raise ExceptionCpipDefine(
                "#undef on already #undef'd instance of other macro"
                )            
        if self.identifier != other.identifier:
            return -1
        if self.isValidRefefinition(other):
            return 0
        return 1

    def isValidRefefinition(self, other):
        """Returns True if this is a valid redefinition of *other*, False otherwise.
        Will raise an ``ExceptionCpipDefineInvalidCmp`` if the identifiers are
        different.
        Will raise an ``ExceptionCpipDefine`` if either is not currently defined.
        
        From: **ISO/IEC 9899:1999 (E) 6.10.3:**
        
        #. Two replacement lists are identical if and only if the preprocessing
            tokens in both have the same number, ordering, spelling, and white-space
            separation, where all white-space separations are considered identical.
        #. An identifier currently defined as a macro without use of lparen
            (an object-like macro) may be redefined by another #define preprocessing
            directive provided that the second definition is an object-like macro
            definition and the two replacement lists are identical, otherwise the
            program is ill-formed.
        #. An identifier currently defined as a macro using lparen (a
            function-like macro) may be redefined by another #define preprocessing
            directive provided that the second definition is a function-like macro
            definition that has the same number and spelling of parameters, and the
            two replacement lists are identical, otherwise the program is
            ill-formed.

        See also: **ISO/IEC 14882:1998(E) 16.3 Macro replacement [cpp.replace]**"""
        if not self.isCurrentlyDefined:
            raise ExceptionCpipDefine(
                "isValidRefefinition() on already #undef'd macro instance of self."
                )            
        if not other.isCurrentlyDefined:
            raise ExceptionCpipDefine(
                "isValidRefefinition() on already #undef'd macro instance of other."
                )            
        if self.identifier != other.identifier:
            raise ExceptionCpipDefineInvalidCmp(
                'isValidRefefinition() "%s" != "%s"' \
                    % (self.identifier, other.identifier)
                )
        # Check the type of the macro
        if (self.isObjectTypeMacro and not other.isObjectTypeMacro) \
        or (not self.isObjectTypeMacro and other.isObjectTypeMacro):
            return False
        if not self.isObjectTypeMacro:
            # If a function type then check identifiers
            # ISO/IEC 14882:1998(E) 16.3-3 Macro replacement [cpp.replace]
            assert(not other.isObjectTypeMacro)
            assert(self._paramS is not None)
            assert(other.parameters is not None)
            if self._paramS != other.parameters:
                return False
        if len(self.replacements) != len(other.replacements):
            # ISO/IEC 14882:1998(E) 16.3-1 Macro replacement [cpp.replace]
            return False
        for s, o in zip(self.replacements, other.replacements):
            # Treat ws runs as equivelent
            if self._wsHandler.isAllWhitespace(s):
                if not self._wsHandler.isAllWhitespace(o):
                    return False
            elif self._wsHandler.isAllWhitespace(o):
                if not self._wsHandler.isAllWhitespace(s):
                    return False
            elif s != o:
                return False
        return True
    #==================================
    # End: Comparison and redefinition.
    #==================================
    
    def undef(self, theFileId, theLineNum):
        """Records this instance of a macro #undef'd at a particular file
        and line number. May raise an ExceptionCpipDefine if already undefined
        of the line number is bad."""
        if not self.isCurrentlyDefined:
            raise ExceptionCpipDefine(
                "#undef on already #undef'd instance of macro"
                )            
        if theLineNum < FileLocation.START_LINE:
            raise ExceptionCpipDefine(
                'Irresponsible line number: %s' % theLineNum
                )            
        self._undefFileLine = FileLocation.FileLine(theFileId, theLineNum)
    ####################################################
    # End: Accessors and comparison (i.e. redefinition).
    ####################################################
