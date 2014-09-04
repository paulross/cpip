#! /usr/bin/env python
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

"""This an environment of macro declarations

It implements ISO/IEC 9899:1999(E) section 6 (aka 'C')
and ISO/IEC 14882:1998(E) section 16 (aka 'C++')

TODO: Record macro related events in the order that they happen.::

    [
        (
            macro_ident,         - string
            event,               - string e.g. 'define', 'replace', 'undef'
            None or PpDefine,    - the latter if undef (or define???)
            file,                - string
            line,                - int
            col,                 - int
        ),
    ]

Can remap this on output to:
{macro_ident : [index, ...], ...}

TODO: Record #ifdef, #ifndef, #if defined and #elif defined when no macro is
defined in a separate data structure so that we can say that these macros, if
present, could alter the outcome i.e. it is a NOT dependency.
"""
__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import logging
import traceback
import types
import io

from cpip import ExceptionCpip
from cpip.core import PpToken
from cpip.core import PpTokeniser
from cpip.core import PpDefine
from cpip.core import PpWhitespace
from cpip.util.ListGen import ListAsGenerator
from cpip.util.Tree import DuplexAdjacencyList

class ExceptionMacroEnv(ExceptionCpip):
    """Exception when handling MacroEnv object."""
    pass

class ExceptionMacroEnvInvalidRedefinition(ExceptionMacroEnv):
    """Exception for a invalid redefinition of a macro.
    NOTE: Under C rules (C Rationale 6.10.3) callers should merely issue a
    suitable diagnostic."""
    pass

class ExceptionMacroReplacementInit(ExceptionMacroEnv):
    """Exception in the constructor."""
    pass

class ExceptionMacroReplacementPredefinedRedefintion(ExceptionMacroEnv):
    """Exception for a redefinition of a macro id that is predefined."""
    pass

class ExceptionMacroEnvNoMacroDefined(ExceptionMacroEnv):
    """Exception when trying to access a PpDefine that is not currently defined."""
    pass

class ExceptionMacroIndexError(ExceptionMacroEnv):
    """Exception when an access to a PpDefine that generates a IndexError."""
    pass

class MacroEnv(object):
    """Represents a set of #define directives that represent a macro processing
    environment. This provides support for #define and #undef directives.
    It also provides support for macro replacement see:
    ISO/IEC 9899:1999 (E) 6.10.3 Macro replacement.
    
    *enableTrace* allows calls to _debugTokenStream() that may or may not
    produce log output (depending on logging level).
    If True this makes this code run slower, typically 3x slower
        
    *stdPredefMacros* if present should be a dictionary of:
    ``{identifier : replacement_string_\\n_terminated, ...}``
    For example: ::
    
        {
            '__DATE__' : 'First of June\\n',
            '__TIME__' : 'Just before lunchtime.\\n',
        }
        
    Each identifier must be in ``STD_PREDEFINED_NAMES``
    """
    # ISO/IEC 14882:1998(E) 16.8-3 that means we can
    # raise an ExceptionMacroReplacementPredefinedRedefintion if any code
    # tries to define a name that is in cpp.predefined
    # Note the special case of 'defined' as per ISO/IEC 14882:1998(E) 16.8-3
    # This rule is applied by making these are invariant after construction
    # and any attempt to use define(...) that results in the macro having one
    # of these names as an identifier will raise a
    # ExceptionMacroReplacementPredefinedRedefintion
    # __LINE__ and __FILE__ can be redefined dynamically by the methods
    # set__LINE__(...) and set__FILE__(...)
    # __DATE__ and __TIME__ should be set by the caller.
    #
    # Macro identifiers that can never, ever be redefined
    # There is some variety among the standards with '__cplusplus'
    # ISO/IEC 9899:1999 (C99)  6.10.8 "The implementation shall not predefine the
    #   macro __cplusplus, nor shall it define it in any standard header."
    # N3242=11-0012 (C++11) 16.8 "The following macro names shall be defined by
    #   the implementation: The name __cplusplus is defined to the value 201103L
    #   when compiling a C++ translation unit.
    # ISO/IEC 9899:201x (C11) 6.10.8 "The implementation shall not predefine the
    #   macro __cplusplus, nor shall it define it in any standard header."
    #
    # So we do not specifically exclude '__cplusplus' but leave it to the user
    # to pre-define it or not.
    NAMES_NO_REDEFINITION = set(
        (
            # This has a special semantics and can not be redefined
            'defined',
        )
    )
    STD_PREDEFINED_NEVER_REDEFINED = set(
            ['__LINE__', '__FILE__', '__DATE__', '__TIME__']
        ) | NAMES_NO_REDEFINITION 
    def __init__(self, enableTrace=False, stdPredefMacros=None):
        """Constructor.
        enableTrace allows calls to _debugTokenStream() that may or may not
        produce log output (depending on logging level).
        stdPredefMacros, if present should be a dictionary of:
        {identifier : replacement_string_\n_terminated, ...}
        These identifiers are not permitted to be redefined.
        This also increments the count is the number of times that the
        identifier has been referenced in the lifetime of me.
        A 'reference' is defined as: replacement or if defined.
        So:
        - Count set to zero on self.define()
        - Increment on:
            self.isDefined()
            self.defined()
            self._expand()
        """
        # If True makes calls to _debugTokenStream() that may or may not
        # produce log output (depending on logging level).
        self._enableTrace = enableTrace
        # Used by various methods to detect whitespacey things
        self._wsHandler = PpWhitespace.PpWhitespace()
        # Standard predefined macro map
        # {identifier : replacement_string_\n_terminated, ...}
        self._stdPredefMacros = stdPredefMacros
        # Initialise the dynamic stuff
        self._reset()
        
    def _reset(self):
        """Initialises the dynamic values."""
        # A map of predefined macros and those discovered in the translation
        # unit. This is a map of:
        # {identifier : class PpDefine, ...}
        # Where identifier is a string.
        self._defineMap = {}
        # This is a list of PpDefine objects that have been #undef'd and
        # successfully removed from self._defineMap
        self._undefS = []
        # A set of macros that have been expanded during macro processing:
        self._expandedSet = set()
        # Can be set by a caller and will be written once to debug output before
        # any internal call to _debugTokenStream()
        self.debugMarker = None
        # The macro identifier set of macros that can not be redefined
        # This is composed of a static and dynamic part:
        # Static: __LINE__, __FILE__, __DATE__, __TIME__
        # Dynamic: Things like __STDC__ and that all depends on which standard
        # you support. This you express through stdPredefMacros.keys()
        self._noDefineIdentifiers = set(self.STD_PREDEFINED_NEVER_REDEFINED)
        if self._stdPredefMacros is not None:
            # Check all keys not in self.NAMES_NO_REDEFINITION as these can never
            # ever be re/defined
            for k in self._stdPredefMacros.keys():
                if k in self.NAMES_NO_REDEFINITION:
                    raise ExceptionMacroReplacementInit(
                            '"%s" is not a predefined identifier' % k)
            # Add identifier to set of those that can not be redefined
            # NOTE: set() is used for 2.x compatibility
            self._noDefineIdentifiers |= set(self._stdPredefMacros.keys())
            # Now insert the definitions in the internal representation.
            for k in self._stdPredefMacros.keys():
                # We use __setString here to avoid raising an
                # ExceptionMacroReplacementPredefinedRedefintion
                self.__setString(u'%s %s' % (k, self._stdPredefMacros[k]))
        # This is a map of {identifier : [class FileLineColumn, ...], ...}
        # Where there has been an #ifdef and nothing is defined
        # Then these macros, if present, could alter the outcome
        # i.e. it is a NOT dependency.
        self._ifDefAbsentMacros = {}

    def clear(self):
        """Clears the macro environment."""
        self._reset()

    ###################
    # Section: Utility.
    ###################
    def __str__(self):
        retStr = []
        for k in sorted(self._defineMap.keys()):
            retStr.append('%s' % str(self._defineMap[k]))
        return '\n'.join(retStr)

    def __len__(self):
        return len(self._defineMap)

    def _assertDefineMapIntegrity(self):
        """Returns True if dynamic tests on self._defineMap and
        self._expandedSet pass. i.e. every entry in self._expandedSet
        must be in self._defineMap.keys()."""
        return self._expandedSet.issubset(set(self._defineMap.keys()))

    def _debugTokenStream(self, thePrefix, theArg=''):
        """Writes to logging.debug() an interpretation of the token stream
        provided by theList. It will be preceded by the debugMarker value
        (if set) and that will always be cleared."""
        assert(self._enableTrace)
        if type(theArg) == list:
            # Assume list of class PpToken
            debugStr = '[%d] %s' \
                % (len(theArg), PpToken.tokensStr(theArg, shortForm=True))
        elif type(theArg) == str:
            debugStr = theArg
        elif theArg is None:
            debugStr = 'None'
        else:
            raise ExceptionMacroEnv(
                'Unknown argument type %s, %s passed to _debugTokenStream()' \
                            % (type(theArg), theArg))
        if self.debugMarker is not None:
            logging.debug(self.debugMarker)
        self.debugMarker = None
        stackPrefix = ' ' * len(traceback.extract_stack())
        logging.debug('[%2d]%s%s: %s' \
                      % (len(stackPrefix), stackPrefix, thePrefix, debugStr))

    #def _nextNonWsOrNewline(self, theGen):
    #    """Returns the next non-whitespace token or whitespace that contains a
    #    newline."""
    #    while 1:
    #        myTtt = theGen.next()
    #        if not myTtt.isWs() \
    #        or self._wsHandler.isBreakingWhitespace(myTtt.t):
    #            return myTtt
    #        # Non-breaking whitespace so continue
    #
    #def _consumeNewline(self, theGen):
    #    """Consumes all tokens up to and including the next newline."""
    #    while 1:
    #        myTtt = self._retToken(theGen)
    #        if self._wsHandler.isBreakingWhitespace(myTtt.t):
    #            break
    #
    #def _consumeAndRaise(self, theGen, theException):
    #    """Consumes all tokens up to and including the next newline then raises
    #    an exception. This is commonly used to get rid of bad token streams but
    #    allow the caller to catch the exception, report the error and
    #    continue."""
    #    self._consumeNewline(theGen)
    #    raise theException
    ###############
    # End: Utility.
    ###############

    #######################################################################
    # Section: Handling #define... and #undef... and specials like __LINE__
    #######################################################################
    def define(self, theGen, theFile, theLine):
        """Defines a macro. theGen should be in the state immediately after the
        ``#define`` i.e. this will consume leading whitespace and the trailing
        newline.
        
        Will raise a ExceptionMacroEnvInvalidRedefinition if the redefinition
        is not valid. May raise a ExceptionCpipDefineInit (or sub class) on failure.
        
        On success it returns the identifier of the macro as a string..
        The insertion is stable i.e. a valid re-definition does not replace
        the existing definition so that the existing state of the macro
        definition (file, line, reference count etc. are preserved."""
        try:
            myDef = PpDefine.PpDefine(theGen, theFile, theLine)
        except PpDefine.ExceptionCpipDefineInit as err:
            raise ExceptionMacroReplacementInit(str(err))
        # Test if attempting to redefine a predefined or undefineable identifier
        if myDef.identifier in self._noDefineIdentifiers:
            raise ExceptionMacroReplacementPredefinedRedefintion(
                'Attempting to redefine predefined identifier "%s"' \
                % myDef.identifier
                )
        return self.__define(myDef)

    def __define(self, ppD):
        """Takes a PpDefine.PpDefine object and adds it to
        the map of objects. Does NOT check if it is a redefinition of
        a predefined macro. Does check if it is a valid redefinition.
        On success it returns the identifier of the macro.
        The insertion is stable i.e. a valid re-definition does not replace
        the existing definition so that the definition file, line and reference
        count are preserved."""
        # Test for redefinition
        if ppD.identifier in self._defineMap:
            if not ppD.isValidRefefinition(self._defineMap[ppD.identifier]):
                raise ExceptionMacroEnvInvalidRedefinition(
                    'Ignoring invalid redefinition of "%s" as "%s"' \
                    % (self._defineMap[ppD.identifier], ppD)
                    )
            else:
                # Already exists so preserve it to give a stable insert
                pass
        else:
            # It is currently undefined so define it
            self._defineMap[ppD.identifier] = ppD
        return ppD.identifier

    def undef(self, theGen, theFile, theLine):
        """Removes a definition from the map and adds the PpDefine to
        self._undefS. It returns None.
        If no definition exists this has no side-effects on the internal
        representation."""
        myDef = PpDefine.PpDefine(theGen, '', 1)
        try:
            myMacro = self._defineMap.pop(myDef.identifier)
            myMacro.undef(theFile, theLine)
            self._undefS.append(myMacro)
        except KeyError:
            pass

    def set__LINE__(self, theStr):
        """This sets the ``__LINE__`` macro directly."""
        self.__setString('__LINE__ %s\n' % theStr)

    def set__FILE__(self, theStr):
        """This sets the ``__FILE__`` macro directly."""
        self.__setString('__FILE__ %s\n' % theStr)

    def __setString(self, theStr):
        """Takes a string 'identifier replacement\n' and sets the macro map.
        This uses __defien(...) so only a redefinition exception is raised."""
        myCpp = PpTokeniser.PpTokeniser(
            theFileObj=io.StringIO(theStr)
            )
        myGen = myCpp.next()
        # Set file to '' and line to 1 as these are builtin macros
        myDef = PpDefine.PpDefine(myGen, '', 1)
        self.__define(myDef)
    ###################################################################
    # End: Handling #define... and #undef... and specials like __LINE__
    ###################################################################

    ############################################################
    # Section: Support for #ifdef, #if defined and #elif defined
    ############################################################
    def isDefined(self, theTtt, theFileLineCol=None):
        """Returns True theTtt is an identifier that is currently defined,
        False otherwise. If True this increments the macro reference.
        See: ISO/IEC 9899:1999 (E) 6.10.1.
        theFileLineCol is a FileLocation.FileLineCol object."""
        if theTtt.isIdentifier():# and self._defineMap.has_key(theTtt.t):
            try:
                self._defineMap[theTtt.t].incRefCount(theFileLineCol)
                return True
            except KeyError:
                try:
                    self._ifDefAbsentMacros[theTtt.t].append(theFileLineCol)
                except KeyError:
                    self._ifDefAbsentMacros[theTtt.t] = [theFileLineCol,]
        return False

    def defined(self, theTtt, flagInvert, theFileLineCol=None):
        """If the PpToken theTtt is an identifier that is currently defined
        then this returns 1 as a PpToken, 0 as a PpToken otherwise.
        If the macro exists in the environment its reference count is
        incremented.
        See: ISO/IEC 9899:1999 (E) 6.10.1.
        theFileLineCol is a FileLocation.FileLineCol object."""
        # If myTtt is newline then raise as this is #if defined\n
        if not theTtt.isIdentifier():
            raise ExceptionMacroEnv(
                'defined() on non-identifier but: %s' % theTtt)
        try:
            self._defineMap[theTtt.t].incRefCount(theFileLineCol)
            if flagInvert:
                return PpToken.PpToken('0', 'pp-number')
            return PpToken.PpToken('1', 'pp-number')
        except KeyError:
            try:
                self._ifDefAbsentMacros[theTtt.t].append(theFileLineCol)
            except KeyError:
                self._ifDefAbsentMacros[theTtt.t] = [theFileLineCol,]
        # No macro of this name defined
        if flagInvert:
            return PpToken.PpToken('1', 'pp-number')
        return PpToken.PpToken('0', 'pp-number')
                
    ########################################################
    # End: Support for #ifdef, #if defined and #elif defined
    ########################################################

    ########################################################
    # Section: Handling macro replacement and reexamination.
    ########################################################
    def mightReplace(self, theTtt):
        """Returns True if theTok might be able to be expanded.
        'Might' is not 'can' or 'will' because of this: ::
        
            #define FUNC(a,b) a-b
            FUNC FUNC(45,3)
        
        Becomes: ::
            
            FUNC 45 -3
        
        Thus ``mightReplace('FUNC', ...)`` is True in both cases but actual
        replacement only occurs once for the second ``FUNC``."""
        assert(self._assertDefineMapIntegrity())
        return theTtt.canReplace and theTtt.t in self._defineMap

    def _hasExpanded(self, theTtt):
        """Returns True if theTok represents a macro name that has already
        been expanded."""
        assert(self._assertDefineMapIntegrity())
        return theTtt.t in self._expandedSet

    def replace(self, theTtt, theGen, theFileLineCol=None):
        """Given a PpToken this returns the replacement as a list of
        [class PpToken, ...] that is the result of the substitution of
        macro definitions.
        theGen is a generator that might be used in the case of function-like
        macros to consume their argument lists.
        theFileLineCol is a FileLocation.FileLineCol object."""
        assert(len(self._expandedSet) == 0)
        try:
            retVal = self._expand(theTtt, theGen, theFileLineCol)
        finally:
            # Zap the expanded set so that the next replace() call will not assert
            self._expandedSet = set()
        assert(len(self._expandedSet) == 0)
        return retVal

    def _expand(self, theTtt, theGen, theFileLineCol):
        """Recursive call to expand macro symbols.
        theFileLineCol is a FileLocation.FileLineCol object."""
        if self._enableTrace:
            self._debugTokenStream('_expand("%s")' % theTtt)
        if not self.mightReplace(theTtt):
            if self._enableTrace:
                self._debugTokenStream('_expand("%s") nothing to do' % theTtt)
            return [theTtt, ]
        if self._hasExpanded(theTtt):
            if self._enableTrace:
                self._debugTokenStream(
                            '_expand("%s") already expanded' % theTtt)
            theTtt.canReplace = False
            return [theTtt, ]
        if self._enableTrace:
            self._debugTokenStream('_expand() examining "%s"' % theTtt.t)
        hasReplaced = False
        myMacro = self._defineMap[theTtt.t]
        #myMacro.assertReplListIntegrity()
        if myMacro.isObjectTypeMacro:
            # Object-like macro
            rTokS = myMacro.replaceObjectStyleMacro()
            if self._enableTrace:
                self._debugTokenStream(
                                '_expand("%s") object replacement' % theTtt,
                                rTokS)
            hasReplaced = True
        else:
            # Function-like macro
            myPreamble = myMacro.consumeFunctionPreamble(theGen)
            if self._enableTrace:
                self._debugTokenStream('_expand() func preamble', myPreamble)
            if myPreamble is not None:
                rTokS = [theTtt, ] + myPreamble
                hasReplaced = False
                if self._enableTrace:
                    self._debugTokenStream(
                        '_expand("%s") function preamble failed' % theTtt,
                        rTokS)
            else:
                if self._enableTrace:
                    self._debugTokenStream('_expand() extracting arguments')
                myArgS = myMacro.retArgumentListTokens(theGen)
                if self._enableTrace:
                    self._debugTokenStream('_expand() arguments %s' % myArgS)
                if myMacro.expandArguments:
                    # Expand out each argument
                    myExpandedArgS = []
                    for argTokS in myArgS:
                        if self._enableTrace:
                            self._debugTokenStream(
                                '_expand("%s") function argument was' \
                                % theTtt, argTokS)
                        if argTokS != myMacro.PLACEMARKER:
                            myGen = next(ListAsGenerator(argTokS, None))
                            myExpArgTokS = []
                            while 1:
                                try:
                                    myExpArgTokS += self._expand(
                                                                 next(myGen),
                                                                 myGen,
                                                                 theFileLineCol,
                                                                 )
                                except StopIteration:
                                    break
                            #for aTok in myExpArgTokS:
                            #    if aTok.canReplace:
                            #        aTok.canReplace = False
                            if self._enableTrace:
                                self._debugTokenStream(
                                        '_expand("%s") function argument now' \
                                        % theTtt, myExpArgTokS)
                            myExpandedArgS.append(myExpArgTokS)
                        else:
                            myExpandedArgS.append(myMacro.PLACEMARKER)
                    rTokS = myMacro.replaceArgumentList(myExpandedArgS)
                else:
                    rTokS = myMacro.replaceArgumentList(myArgS)
                if self._enableTrace:
                    self._debugTokenStream(
                                '_expand("%s") function now' % theTtt, rTokS)
                hasReplaced = True
        if hasReplaced:
            # Increment the reference count for this macro
            myMacro.incRefCount(theFileLineCol)
        else:
            if self._enableTrace:
                self._debugTokenStream(
                            '_expand("%s") not hasReplaced.' % theTtt, rTokS)
            return rTokS
        # Reexamination
        reexTokS = []
        if self._enableTrace:
            self._debugTokenStream('_expand("%s") reexamine' % theTtt, rTokS)
        self._expandedSet.add(theTtt.t)
        myListAsGen = ListAsGenerator(rTokS, theGen)
        myGen = next(myListAsGen)
        while not myListAsGen.listIsEmpty:
            reexTokS += self._expand(next(myGen), myGen, theFileLineCol)
            #print 'myListAsGen.listIsEmpty', myListAsGen.listIsEmpty
        self._expandedSet.remove(theTtt.t)
        if self._enableTrace:
            self._debugTokenStream(
                            '_expand("%s") reexamined' % theTtt, reexTokS)
        return reexTokS

    ############################
    # Section: Accessor methods.
    ############################
    def genMacrosOutOfScope(self, theIdent=None):
        """Generates PpDefine objects encountered during my existence but then
        undefined in the order of un-definition.
        If theIdent is not None then only that named macros will be yielded."""
        # First the #undef'd one(s)
        for aM in self._undefS:
            if theIdent is None \
            or aM.identifier == theIdent:
                yield aM

    def genMacrosInScope(self, theIdent=None):
        """Generates PpDefine objects encountered during my existence and still
        in scope i.e. not yet un-defined.
        If theIdent is not None then only that named macros will be yielded."""
        # Now the existent one(s)
        if theIdent is None:
            # yield all of them
            for anId in sorted(self._defineMap.keys()):
                yield self._defineMap[anId]
        else:
            try:
                yield self._defineMap[theIdent]
            except KeyError:
                pass
    
    def genMacros(self, theIdentifier=None):
        """Generates PpDefine objects encountered during my existence.
        Macros that have been undefined will be generated first in order of
        un-definition followed by the currently defined macros in identifier
        order.
        Macros that have been #undef'd will have the attribute 
        isCurrentlyDefined as False."""
        # First the #undef'd one(s)
        for aM in self.genMacrosOutOfScope(theIdentifier):
            yield aM
        # Now the existent one(s)
        for aM in self.genMacrosInScope(theIdentifier):
            yield aM

    def hasMacro(self, theIdentifier):
        """Returns True if the environment has the macro.
        NOTE: This does _not_ increment the reference count so should not be
        used when processing #ifdef ..., #if defined ... or #if !defined ...
        for those use isDefined() and defined() instead."""
        return theIdentifier in self._defineMap
        
    def macros(self):
        """Returns and unsorted list of strings of current macro identifiers."""
        return list(self._defineMap.keys())
        
    def macro(self, theIdentifier):
        """Returns the macro identified by the identifier.
        Will raise a ExceptionMacroEnvNoMacroDefined is undefined."""
        try:
            return self._defineMap[theIdentifier]
        except KeyError:
            raise ExceptionMacroEnvNoMacroDefined(
                    'Macro %s is not currently defined' % theIdentifier
                    )
    
    #---------------------------
    # Macro dependencies
    #---------------------------
    def allStaticMacroDependencies(self):
        """Returns a DuplexAdjacencyList() of macro dependencies for the
        Macro environment. All objects in the DuplexAdjacencyList() are macro
        identifiers as strings.
        A DuplexAdjacencyList() can be converted to a util.Tree() and that
        can be converted to a DictTree()"""
        ret = DuplexAdjacencyList()
        for macroIdentifier in self.macros():
            for depMacro in self._staticMacroDependencies(macroIdentifier):
                ret.add(macroIdentifier, depMacro)
        return ret

    def _staticMacroDependencies(self, theIdentifier):
        """Returns the immediate dependencies as a list of strings for a macro
        identified by the string."""
        ret = []
        macro = self.macro(theIdentifier)
        for tok in macro.replacementTokens:
            if tok.tt == 'identifier' \
            and self.hasMacro(tok.t) \
            and tok.t not in ret:
                ret.append(tok.t)
        return ret

    #---------------------------
    # END: Macro dependencies
    #---------------------------
    
    def getUndefMacro(self, theIdx):
        """Returns the PpDefine object from the undef list for the given index.
        Will raise an ExceptionMacroIndexError if the index is out of range."""
        try:
            return self._undefS[theIdx]
        except IndexError:
            raise ExceptionMacroIndexError(
                'Index %d is not in range 0-%d' \
                    % (theIdx, len(self._undefS)-1)
                )
    
    def referencedMacroIdentifiers(self, sortedByRefcount=False):
        """Returns an unsorted list of macro identifiers that have a reference
        count > 0. If sortedByRefcount is True the list will be in increasing
        order of reference count then by name. Use reverse() on the result to get decreasing
        order.
        If sortedByRefcount is False the return value is unsorted."""
        if sortedByRefcount:
            myPairs = []
            # Sort by name
            for k in sorted(self._defineMap.keys()):
                rc = self._defineMap[k].refCount
                if rc > 0:
                    myPairs.append((k, rc))
            # Sort by DSU
            # D
            listD = [(x[1], x) for x in myPairs]
            # S
            listD.sort()
            # U
            myPairs = [v[1] for v in listD]
            return [x[0] for x in myPairs] 
        return [mId for mId in self._defineMap.keys() if self._defineMap[mId].refCount > 0]
    
    def macroHistory(self, incEnv=True, onlyRef=True):
        """Returns the macro history as a multi-line string"""
        retList = []
        if incEnv:
            retList.append('Macro Environment:')
            retList.append(str(self))
            retList.append('')
        if onlyRef:
            retList.append('Macro History (referenced macros only):')
        else:
            retList.append('Macro History (all macros):')
        doneTitle = False
        # First the #undef'd one(s)
        for aMacro in self.genMacrosOutOfScope(None):
            if not doneTitle:
                retList.append('Out-of-scope:')
                doneTitle = True
            if not onlyRef or aMacro.refCount > 0:
                retList.append(str(aMacro))
                for aFlc in aMacro.refFileLineColS:
                    retList.append('    %s %s %s' % (aFlc.fileId, aFlc.lineNum, aFlc.colNum))
        doneTitle = False
        # Now the existent one(s)
        for aMacro in self.genMacrosInScope(None):
            if not doneTitle:
                retList.append('In scope:')
                doneTitle = True
            if not onlyRef or aMacro.refCount > 0:
                retList.append(str(aMacro))
                for aFlc in aMacro.refFileLineColS:
                    retList.append('    %s %s %s' % (aFlc.fileId, aFlc.lineNum, aFlc.colNum))
        return '\n'.join(retList)
    
    def macroHistoryMap(self):
        """Returns a map of {ident : ([ints, ...], True/False), ...}
        Where the macro identifier is mapped to a pair where:
        pair[0] is a list of indexes into getUndefMacro().
        pair[1] is boolean, True if the identifier is currently defined
        i.e. it is the value ofself.hasMacro(ident).
        The macro can be obtained by self.macro()."""
        # A temporary map of {ident : [undef_index, ...], ...]
        undefMap = {}
        for i, aMacro in enumerate(self.genMacrosOutOfScope(None)):
            try:
                undefMap[aMacro.identifier].append(i)
            except KeyError:
                undefMap[aMacro.identifier] = [i]
        # The returned object
        retMap = {}
        # Now the existent one(s)
        for aMacro in self.genMacrosInScope(None):
            try:
                retMap[aMacro.identifier] = (
                        undefMap[aMacro.identifier],
                        True,
                    )
            except KeyError:
                # Caused by: undefMap[aMacro.identifier]
                retMap[aMacro.identifier] = ([], True)
        # Finally mark the undef'd ones
        for k in undefMap.keys():
            if k not in retMap:
                retMap[k] = (
                        undefMap[k],
                        False,
                    )
        return retMap
    
    def macroNotDefinedDependencies(self):
        """Returns a map of {identifier : [class FileLineColumn, ...], ...}
        where there has been an #ifdef and nothing is defined.
        Thus these macros, if present, could alter the outcome
        i.e. it is dependency on them NOT being defined."""
        return self._ifDefAbsentMacros

    def macroNotDefinedDependencyNames(self):
        """Returns an unsorted list of identifies
        where there has been an #ifdef and nothing is defined.
        Thus these macros, if present, could alter the outcome
        i.e. it is dependency on them NOT being defined."""
        return list(self._ifDefAbsentMacros.keys())

    def macroNotDefinedDependencyReferences(self, theIdentifier):
        """Returns an ordered list of class FileLineColumn for an identifier
        where there has been an #ifdef and nothing is defined.
        Thus these macros, if present, could alter the outcome
        i.e. it is dependency on them NOT being defined."""
        try:
            return self._ifDefAbsentMacros[theIdentifier][:]
        except KeyError:
            raise ExceptionMacroEnvNoMacroDefined(
                    'Macro %s is not currently present in the macroNotDefinedDependancies.' \
                        % theIdentifier
                    )
    ############################
    # End: Accessor methods.
    ############################
