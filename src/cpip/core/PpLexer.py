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

"""Generates tokens from a C or C++ translation unit.

TODO: Fix accidental token pasting.

TODO: Preprocessor statements in arguments of function like macros. Sect. 3.9
of cpp.pdf and existing MacroEnv tests.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import logging
import os
import datetime

from cpip.core import ConstantExpression
from cpip.core import CppCond
from cpip.core import CppDiagnostic
from cpip.core import FileIncludeStack
from cpip.core import IncludeHandler
from cpip.core import MacroEnv
from cpip.core import PpToken
from cpip.core import PpTokeniser
from cpip.core import PpWhitespace
from cpip.core import PragmaHandler

from cpip.util import ListGen

######################
# Section: Exceptions.
######################
from cpip import ExceptionCpip

class ExceptionPpLexer(ExceptionCpip):
    """Exception when handling PpLexer object."""
    pass

class ExceptionPpLexerPreInclude(ExceptionPpLexer):
    """Exception when loading pre-include files."""
    pass

class ExceptionPpLexerPreIncludeIncNoCp(ExceptionPpLexerPreInclude):
    """Exception when loading a pre-include file that has no current place
    (e.g. a StringIO object) and the pre-include then has an #include
    statement."""
    pass

class ExceptionPpLexerDefine(ExceptionPpLexer):
    """Exception when loading predefined macro definitions."""
    pass

class ExceptionPpLexerNoFile(ExceptionPpLexer):
    """Exception when can not find file."""
    pass

class ExceptionPpLexerPredefine(ExceptionPpLexerDefine):
    """Exception when loading predefined macro definitions."""
    pass

class ExceptionPpLexerCallStack(ExceptionPpLexer):
    """Exception when finding issues with the call stack or nested includes."""
    pass

class ExceptionPpLexerCallStackTooSmall(ExceptionPpLexerCallStack):
    """Exception when sys.getrecursionlimit() is too small."""
    pass

class ExceptionPpLexerNestedInclueLimit(ExceptionPpLexerCallStack):
    """Exception when nested #include limit exceeded."""
    pass

class ExceptionPpLexerCondLevelOutOfRange(ExceptionPpLexer):
    """Exception when handling a conditional token generation level."""
    pass

class ExceptionPpLexerAlreadyGenerating(ExceptionPpLexer):
    """Exception when two generators are created then the internal state will become inconsistent."""
    def __init__(self):
        super(ExceptionPpLexerAlreadyGenerating, self).__init__(
            'A generator is already active and the PpLexer internal state will become inconsistent. Create a new PpLexer for each generator.'
        )

##################
# End: Exceptions.
##################

##################################################
# Section: PpLexer - the main point of this module.
##################################################

#: Allowable preprocessing directives
PREPROCESSING_DIRECTIVES = [        
    'if',
    'ifdef',
    'ifndef',
    'elif',
    'else',
    'endif',
    'include',
    'define',
    'undef',
    'line',
    'error',
    'pragma',
]

#: Used when file objects have no name
UNNAMED_FILE_NAME = 'Unnamed Pre-include'

class PpLexer(object):
    """Create a translation unit tokeniser that applies ISO/IEC 9899:1999(E)
    Section 6 and ISO/IEC 14882:1998(E) section 16.
    
    *tuFileId*
        A file ID that will be given to the include
        handler to find the translation unit.
        Typically this will be the file path (as a string)
        to the file that is the Initial Translation Unit
        (ITU) i.e. the file being preprocessed.
    
    *includeHandler*
        A handler to file ``#include``'d files typically a
        ``IncludeHandler.IncludeHandlerStd()``.
        This might have user and system include path
        information and a means of resolving file
        references.
    
    *preIncFiles*
        An ordered list of file like objects that are
        pre-include files. These are processed in order
        before the ITU is processed. Macro redefinition
        rules apply.
    
    *diagnostic*
        A diagnostic object, defaults to a
        CppDiagnostic.PreprocessDiagnosticStd().
    
    *pragmaHandler*
        A handler for #pragma statements. This shall have a
        function pragma() defined that takes a non-zero
        length list of PpTokens the last of which will be
        a newline token.
    
    *stdPredefMacros*
        A dictionary of Standard pre-defined macros.
        See for example:
        ISO/IEC 9899:1999 (E) 6.10.8 "Predefined macro names",
        ISO/IEC 14882:1998 (E) 16.8 "Predefined macro names"
        and N2800=08-0310 16.8 "Predefined macro names".
        The macros ``__DATE__`` and ``__TIME__`` will be automatically
        updated to current locale date/time (see autoDefineDateTime).
        
    *autoDefineDateTime*
        If True then the macros ``__DATE__`` and ``__TIME__`` will
        be automatically updated to current locale date/time.
        Mostly this is used for testing.
        
    *gccExtensions*
        Support GCC extensions. Currently just ``#include_next`` is supported.

    TODO: Set flags here rather than supplying them to a generator?
    This would make the API simply the ctor and ppTokens/next().
    Flags would be:
    
    incWs - Include whitespace tokens.
    
    condLevel - (0, 1, 2) thus:
    
    0. No conditionally compiled tokens. The fileIncludeGraphRoot will
        not have any information about conditionally included files.
    1. Conditionally compiled tokens are generated but not from 
        conditionally included files. The fileIncludeGraphRoot will have
        a reference to a conditionally included file but not that
        included file's includes.
    2. Conditionally compiled tokens including tokens from conditionally
        included files. The fileIncludeGraphRoot will have all the
        information about conditionally included files recursively.    
    """
    PP_DIRECTIVE_PREFIX = '#'
    #: The maximum value of nested #include's
    MAX_INCLUDE_DEPTH = 200
    #: Each include 
    #: The call stack depth, D = A + B + C*L
    #: Where L is the number of levels of nested includes and A is the call stack
    #" depth of the function that calls ppTokens()
    #: A above:
    CALL_STACK_DEPTH_ASSUMED_PPTOKENS = 10
    #: B above:
    CALL_STACK_DEPTH_FIRST_INCLUDE = 3
    #: C above:
    CALL_STACK_DEPTH_PER_INCLUDE = 3
    #: Conditianlity settings for token generation
    COND_LEVEL_DEFAULT = 0
    #: Conditionality level (0, 1, 2)
    COND_LEVEL_OPTIONS = range(3)
    ###########################################
    # Section: Initialisation and finalisation.
    ###########################################    
    def __init__(self,
                 tuFileId,
                 includeHandler,
                 preIncFiles=None,
                 diagnostic=None,
                 pragmaHandler=None,
                 stdPredefMacros=None,
                 autoDefineDateTime=True,
                 gccExtensions=False,
                 annotateLineFile=False,
                 ):
        """Create a translation unit tokeniser.
        tuFileId        - A file ID that will be given to the include
                            handler to find the translation unit.
                            Typically this will be the file path (as a string)
                            to the file that is the Initial Translation Unit
                            (ITU) i.e. the file being preprocessed.
        includeHandler  - A handler to file #includ'ed files typically a
                            IncludeHandler.IncludeHandlerStd().
                            This might have user and system include path
                            information and a means of resolving file
                            references.
        preIncFiles     - An ordered list of file like objects that are
                            pre-include files. These are processed in order
                            before the ITU is processed. Macro redefinition
                            rules apply.
        diagnostic      - A diagnostic object, defaults to a
                            CppDiagnostic.PreprocessDiagnosticStd().
        pragmaHandler   - A handler for #pragma statements. This shall have a
                            function pragma() defined that takes a non-zero
                            length list of PpTokens the last of which will be
                            a newline token. The tokens returned will be yielded.
                            Also the attirbute replaceTokens is to be
                            implemented, if True then the tokens stream will be
                            be macro replace before being passed to the pragma
                            handler.
        stdPredefMacros  - A dictionary of Standard pre-defined macros.
                            See for example:
                            ISO/IEC 9899:1999 (E) 6.10.8 Predefined macro names
                            ISO/IEC 14882:1998 (E) 16.8 Predefined macro names
                            N2800=08-0310 16.8 Predefined macro names
                            The macros __DATE__ and __TIME__ will be automatically
                            updated to current locale date/time (see autoDefineDateTime).
        autoDefineDateTime - If True then the macros __DATE__ and __TIME__ will
                                be automatically updated to current locale date/time.
                                Mostly this is used for testing.
        gccExtensions - Support GCC extensions. Currently just #include_next
        *annotateLineFile* - if True then PpToken will output line number and file as cpp.
        For example::
        
            # 22 "/usr/include/stdio.h" 3 4
            # 59 "/usr/include/stdio.h" 3 4
            # 1 "/usr/include/sys/cdefs.h" 1 3 4

        TODO: Set flags here rather than supplying them to a generator?
        This would make the API simply the ctor and ppTokens/next().
        Flags would be:
        incWs - Include whitespace tokens.
        condLevel - (0, 1, 2) thus:
            0: No conditionally compiled tokens. The fileIncludeGraphRoot will
                not have any information about conditionally included files.
            1: Conditionally compiled tokens are generated but not from 
                conditionally included files. The fileIncludeGraphRoot will have
                a reference to a conditionally included file but not that
                included file's includes.
            2: Conditionally compiled tokens including tokens from conditionally
                included files. The fileIncludeGraphRoot will have all the
                information about conditionally included files recursively.
        """
        # Capture constructor arguments
        self._tuFileId = tuFileId
        self._includeHandler = includeHandler
        self._preIncFiles = preIncFiles or []
        self._gccExtensions = gccExtensions
        self._annotateLineFile = annotateLineFile
        # Create the class members
        self._diagnostic = diagnostic or CppDiagnostic.PreprocessDiagnosticStd()
        self._pragmaHandler = pragmaHandler
        # Whitespace handler and state
        self._wsHandler = PpWhitespace.PpWhitespace()
        # Integer counter that indicates where in the Translation Unit we are.
        # This increases monotonically and approximates to the size of the
        # Translation Unit seen so far.
        self._tuIndex = 0
        # Despatch table for the preprocessor directive
        self._KEYWORD_DESPATCH = {
            'if'        : self._cppIf,
            'ifdef'     : self._cppIfdef,
            'ifndef'    : self._cppIfndef,
            'elif'      : self._cppElif,
            'else'      : self._cppElse,
            'endif'     : self._cppEndif,
            'include'   : self._cppInclude,
            'define'    : self._cppDefine,
            'undef'     : self._cppUndef,
            'line'      : self._cppLine,
            'error'     : self._cppError,
            'pragma'    : self._cppPragma,
            # Not in the standard but is often seen
            'warning'   : self._cppWarning,
        }
        if self._gccExtensions:
            self._KEYWORD_DESPATCH['include_next'] = self._cppIncludeNext
        # Sanity check
        for aType in PREPROCESSING_DIRECTIVES:
            assert(aType in self._KEYWORD_DESPATCH)
        # The Macro environment
        # Handle predefined macros
        if stdPredefMacros is None:
            stdPredefMacros = {}
        if autoDefineDateTime:
            # ISO/IEC 9899:1999 (E) 6.10.8 Predefined macro names
            # "Mmm dd yyyy" with no leading zero on dd
            dt = datetime.datetime.now()
            stdPredefMacros['__DATE__'] = dt.strftime("%b") + ' %2d' % dt.day \
                + dt.strftime(" %Y") + '\n'
            stdPredefMacros['__TIME__'] = dt.strftime("%H:%M:%S") + '\n'
        self._macroEnv = MacroEnv.MacroEnv(stdPredefMacros=stdPredefMacros)
        # Conditional level of compilation
        #0: No conditionally compiled tokens. The fileIncludeGraphRoot will
        #    not have any information about conditionally included files.
        #1: Conditionally compiled tokens are generated but not from 
        #    conditionally included files. The fileIncludeGraphRoot will have
        #    a reference to a conditionally included file but not that
        #    included file's includes.
        #2: Conditionally compiled tokens including tokens from conditionally
        #    included files. The fileIncludeGraphRoot will have all the
        #    information about conditionally included files recursively.
        self._condLevel = self.COND_LEVEL_DEFAULT
        # A conditional compilation state stack.
        # TODO: Combine this with CppCondGraph so that a single call is made
        # to oIf etc.
        # This needs to be finalised with close()
        self._condStack = CppCond.CppCond()
        # Conditional compilation graph
        self._condCompGraph = CppCond.CppCondGraph()
        # This flag records whether we are at the start of a new line
        # See ISO/IEC 9899:1999(E) Section 6.10-2 and example in
        # ISO/IEC 9899:1999(E) Section 6.10-8
        # This is set True at the beginning of the TU and at the beginning of
        # any #included file. It is set True after processing any #include'd
        # file.
        self._isNewline = True
        # Locate the Tu file from include handler, this is an instance of
        # IncludeHandler.FilePathOrigin
        self._tuFpo = None
        # This holds information about the #include'd files.
        self._fis = FileIncludeStack.FileIncludeStack(self._diagnostic)
        # Flag to say whether a generator is in play
        self._isGenerating = False

    def _genPreIncludeTokens(self):
        """Reads all the pre-include files and loads the macro environment."""
        for i, aFileObj in enumerate(self._preIncFiles):
            logging.debug('PpLexer._initialisePreIncludes() [%d] %s', i, aFileObj) 
            aFileObj.seek(0)
            try:
                fileId = aFileObj.name
                # This is a named file (not, for example, StringIO object) so
                # artificially push/pop the CP onto the file include stack
                currPlace = os.path.dirname(aFileObj.name)
            except AttributeError:
                # This can happen with StringIO file-like objects
                fileId = UNNAMED_FILE_NAME
                currPlace = None#'Pre-Include [%d]' % i
            # Create a FilePathOrigin object
            myFpo = IncludeHandler.FilePathOrigin(
                aFileObj,
                fileId,
                currPlace,
                'pre-include',
                )
            # As the FilePathOrigin is created directly and not through the
            # IncludeHandler search system we have to push/pop the CP on the
            # IncludeHandler stack directly in case any pre-include itself
            # includes file that the IncludeHandler is required to search for. 
            self._includeHandler.cpStackPush(myFpo)
            # Create a generator from the ITU
            myGen = self._pptPush(myFpo)
            for optionalLineFileToken in self._pptPostPush():
                yield optionalLineFileToken
            try:
                for aTok in self._genPpTokensRecursive(myGen):
                    #print 'TRACE: aTok:', aTok
                    yield aTok
            except CppDiagnostic.ExceptionCppDiagnosticUndefined as err:
                raise ExceptionPpLexerPredefine(err)
            except ExceptionCpip as err:
                raise ExceptionPpLexerPreInclude(
                    'Failed to process pre-include with error: %s' % str(err)
                )
            finally:
                # There is a very special case here where a pre-include file
                # that has no current place (e.g. a StringIO object) and that
                # pre-include then has an #include statement.
                # What happens here is that the #include will fail by virtue
                # of the missing CP and the finally clause in _cppInclude()
                # will clean up the CP stack by calling endInclude().
                # In that case the CP stack will be empty and that is when
                # we get to see it here - it means the pre-include has failed.
                if self._includeHandler.cpStackSize == 0:
                    raise ExceptionPpLexerPreIncludeIncNoCp(
                        'Pre-include [%d] attempted to #inlcude when there is no current place.' % i
                    )
                else:
                    self._includeHandler.cpStackPop()
                self._pptPop()
                for optionalLineFileToken in self._pptPostPop():
                    yield optionalLineFileToken
#===============================================================================
#                # Trap any exception in the finally block otherwise that
#                # may displace an exception generated above. 
#                try:
#                    self._includeHandler.cpStackPop()
#                except ExceptionCpip, err:
#                    pass
#                    #self._diagnostic.error(str(err))
#                    raise ExceptionPpLexerPreInclude('Failed to process pre-include "%s"' % myFpo.filePath)
#===============================================================================
            logging.debug('PpLexer._initialisePreIncludes() [%d] - Done', i) 
            
    def finalise(self):
        """Finalisation, may raise any Exception."""
        self._includeHandler.finalise()
        self._condStack.close()
        # Note: We don't do any closure/finalisation on self._condCompGraph
        # as we rely on self._condStack to complain if the conditional
        # directives are incomplete
        # TODO: Remove above comment when both are merged.
        self._fis.finalise()
    #######################################
    # End: Initialisation and finalisation.
    #######################################    
    
    #############################
    # Section: PpLexer generators
    #############################
    def ppTokens(self, incWs=True, minWs=False, condLevel=0):
        """A generator for providing PpToken.PpTokens to section 16 of ISO/IEC 14882:1998(E).
        
        *incWs* - if True than whitespace tokens are included (i.e. tok.isWs() == True).
        
        *minWs* - if True then whitespace runs will be minimised to a single
        space or, if  newline is in the whitespce run, a single newline
        
        *condLevel* - if True then conditionally compiled tokens will be yielded
        and they will have have tok.isCond == True. The fileIncludeGraphRoot
        will be marked up with the appropriate conditionality. Levels are::

            0: No conditionally compiled tokens. The fileIncludeGraphRoot will
            not have any information about conditionally included files.
    
            1: Conditionally compiled tokens are generated but not from 
            conditionally included files. The fileIncludeGraphRoot will have
            a reference to a conditionally included file but not that
            included file's includes.
    
            2: Conditionally compiled tokens including tokens from conditionally
            included files. The fileIncludeGraphRoot will have all the
            information about conditionally included files recursively.

        (see _cppInclude where we check if self._condStack.isTrue():).
        """
        if self._isGenerating:
            raise ExceptionPpLexerAlreadyGenerating()
        # Mark internal state as having a generator
        self._isGenerating = True
        if condLevel not in self.COND_LEVEL_OPTIONS:
            raise ExceptionPpLexerCondLevelOutOfRange(
                    'Conditional level %s not in %s.' \
                        % (condLevel, str(self.COND_LEVEL_OPTIONS))
                )
        self._condLevel = condLevel
        wsBuf = []
        # Pre-include tokens first
        for aTok in self._genPreIncludeTokens():
            if minWs and aTok.isWs():
                wsBuf.append(aTok)
            elif (incWs or not aTok.isWs()) \
            and (self._condLevel or not aTok.isCond):
                if not aTok.isWs() and len(wsBuf) > 0:
                    # Flush the whitespace buffer
                    for aWsT in wsBuf:
                        if self._wsHandler.isBreakingWhitespace(aWsT.t):
                            yield PpToken.PpToken('\n', 'whitespace')
                            break
                    else:
                        yield PpToken.PpToken(' ', 'whitespace')
                    wsBuf = []
                yield aTok            
                self._tuIndex += len(aTok.t)
        # Flush the whitespace buffer
        if len(wsBuf) > 0:
            for aWsT in wsBuf:
                if self._wsHandler.isBreakingWhitespace(aWsT.t):
                    yield PpToken.PpToken('\n', 'whitespace')
                    break
            else:
                yield PpToken.PpToken(' ', 'whitespace')
            wsBuf = []
        self._tuFpo = self._includeHandler.initialTu(self._tuFileId)
        if self._tuFpo is None:
            raise ExceptionPpLexerNoFile('Can not find file: "%s"' % self._tuFileId)
        # Rewind initial translation unit
        self._tuFpo.fileObj.seek(0)
        # Create a generator from the ITU
        myGen = self._pptPush(self._tuFpo)
        for optionalLineFileToken in self._pptPostPush():
            yield optionalLineFileToken
        try:
            for aTok in self._genPpTokensRecursive(myGen):
                if minWs and aTok.isWs():
                    wsBuf.append(aTok)
                elif (incWs or not aTok.isWs()) \
                and (self._condLevel or not aTok.isCond):
                    if not aTok.isWs() and len(wsBuf) > 0:
                        # Flush the whitespace buffer
                        for aWsT in wsBuf:
                            if self._wsHandler.isBreakingWhitespace(aWsT.t):
                                yield PpToken.PpToken('\n', 'whitespace')
                                break
                        else:
                            yield PpToken.PpToken(' ', 'whitespace')
                        wsBuf = []
                    yield aTok
                    self._tuIndex += len(aTok.t)
            # Flush the whitespace buffer
            if len(wsBuf) > 0:
                for aWsT in wsBuf:
                    if self._wsHandler.isBreakingWhitespace(aWsT.t):
                        yield PpToken.PpToken('\n', 'whitespace')
                        break
                else:
                    yield PpToken.PpToken(' ', 'whitespace')
                wsBuf = []
        finally:
            # Trap any exception in the finally block otherwise that
            # may displace an exception generated in the try block above.
            # TODO: Why not?
#             self._isGenerating = False
            try:
                # End the ITU
                self._includeHandler.endInclude()
                self._pptPop()
                for optionalLineFileToken in self._pptPostPop():
                    yield optionalLineFileToken
            except Exception as err:
                logging.fatal('PpLexer.ppTokens(): Encountered exception in finally clause: %s' % str(err))
                pass
        # TODO: should finalise be within the finally?
        self.finalise()

    def _genPpTokensRecursive(self, theGen):
        """Given a token generator this applies the lexical rules.
        This means handling preprocessor directives and macro replacement.
        With #included files this become recursive."""
        #print '_genPpTokensRecursive() enter', theGen
        # Token counters that influence the FileIncludeGraph
        self._diagnostic.debug('_genPpTokensRecursive() START', self._fis.fileLineCol)
        try:
            while 1:
                # Take the position just before the token
                myFlc = self.fileLineCol
                myTtt = next(theGen)
                # Now we evaluate the token in our context
                # 1. Is it a (potiential) directive?
                # 2. Otherwise is it unconditional?
                # 3. Otherwise?
                # TODO:
                # DEFECT:
                # BUG: With the following code:
                # #define MT
                # MT #define FOO
                # Then FOO should _not_ be defined but currently will be.
                # See: ISO/IEC 9899:1999 (E) 6.10-8 EXAMPLE using #define EMPTY
                if myTtt.t == self.PP_DIRECTIVE_PREFIX and self._isNewline:
                    # Possible ISO/IEC 9899:1999 (E) 6.10 group of tokens
                    for aTtt in self._processCppDirective(myTtt, theGen):
                        if self._condStack.isTrue():
                            yield aTtt
                            self._tuIndex += 1
                        else:
                            # The token is conditional so set condionality and yield
                            aTtt.setIsCond()
                            yield aTtt
                            self._tuIndex += 1
                elif self._condStack.isTrue():
                    # Increment the token count
                    self._fis.tokenCountInc(myTtt, True)
                    # Macro replacement
                    if self._macroEnv.mightReplace(myTtt):
                        # TODO: This try/except was put in as a hack
                        try:
                            for aTtt in self._macroEnv.replace(
                                            myTtt,
                                            theGen,
                                            myFlc):
                                yield aTtt
                                self._tuIndex += 1
                        except ExceptionCpip as err:
                            self._diagnostic.error(str(err), self._fis.fileLineCol)
                    else:
                        # Nothing to replace, just move right along
                        if self._wsHandler.preceedsNewline(myTtt.t):
                            self._isNewline = True
                        yield myTtt
                        self._tuIndex += 1
                else:
                    # Increment the token count
                    self._fis.tokenCountInc(myTtt, False)
                    # The token is conditional so set condionality and yield
                    myTtt.setIsCond()
                    yield myTtt
                    self._tuIndex += 1
        finally:
            # Trap any exception in the finally block otherwise that
            # may displace an exception generated in the try block above.
            try:
                # Update the FileIncludeStack
                self._diagnosticDebugMessage('_genPpTokens() END')
            except Exception as err:
                logging.fatal('PpLexer._genPpTokensRecursive(): Encountered exception in finally clause: %s' % str(err))
                pass

    #=========================================
    # Section: PpTokeniser generator handling.
    #=========================================
    def _pptPush(self, theFpo):
        """This takes a IncludeHandler.FilePathOrigin object and pushes it onto
        the FileIncludeStack which creates a PpTokneiser object on the stack.
        This returns that PpTokeniser generator function."""
        #print '_pptPush(): %s' % theFpo.filePath
        # Used to determine a bounded way of setting sys.setrecursionlimit(n)
        # (actually the call stack depth, not the recursion depth) so that
        # the desired #include depth can be accommodated.
        #myDepth = len(traceback.extract_stack())
        #print '_pptPush(): Depth is %d' % myDepth
        #if myDepth in (12, 15, 18):
        #    print ''.join(traceback.format_stack())
        if self._fis.depth > self.MAX_INCLUDE_DEPTH:
            raise ExceptionPpLexerNestedInclueLimit(
                'Include stack of %d is greater than allowable limit of %d' \
                % (self._fis.depth, self.MAX_INCLUDE_DEPTH)
                )
        myLine = self.lineNum
#        print 'PpLexer._pptPush(): myLine', myLine
        self._fis.includeStart(theFpo,
                            myLine,
                            self._condStack.isTrue(),
                            str(self._condStack),
                            self._includeHandler.findLogic)
        self._isNewline = True
        return self._fis.ppt.next()

    def _pptPop(self):
        """End a #included file."""
        self._fis.includeFinish()

    #------------- Handling line number and file output ------------------------
    def _pptPostPush(self):
        """Called immediately after _pptPush() this, optionally, returns a list
        of PpToken's that can be yielded."""
        if self._annotateLineFile:
            flags = ['1',]
            if self._fis.currentFileIsSystemFile:
                flags.append('3')
            return self._lineFileAnnotation(flags)
        return [] 

    def _pptPostPop(self):
        """Called immediately after _pptPop() this, optionally, returns a list
        of PpToken's that can be yielded."""
        if self._annotateLineFile:
            if self._fis.depth:
                flags = ['2',]
                if self._fis.currentFileIsSystemFile:
                    flags.append('3')
                return self._lineFileAnnotation(flags)
        return [] 

    def _lineFileAnnotation(self, flags):
        """Returns a list of PpTokens that represent the line number and file
        name. For example::

            # 22 "/usr/include/stdio.h" 3 4
            # 59 "/usr/include/stdio.h" 3 4
            # 1 "/usr/include/sys/cdefs.h" 1 3 4
        
        Trailing numbers are described here: https://gcc.gnu.org/onlinedocs/cpp/Preprocessor-Output.html
        '1' - This indicates the start of a new file. 
        '2' - This indicates returning to a file (after having included another file). 
        '3' - This indicates that the following text comes from a system header
                file, so certain warnings should be suppressed. 
        '4' - This indicates that the following text should be treated as being
                wrapped in an implicit extern "C" block.
        We don't support '4'
        """
        # Get the file name from self.currentFile
        # Line number from self.fileLineCol.lineNum
        ret_val = [
            PpToken.PpToken('#', 'preprocessing-op-or-punc'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('%d' % self.fileLineCol.lineNum, 'pp-number'),
            PpToken.PpToken(' ', 'whitespace'),
            PpToken.PpToken('"%s"' % self.currentFile, 'string-literal'),
        ]
        if len(flags):
            for flag in flags:
                ret_val.append(PpToken.PpToken(' ', 'whitespace'))
                ret_val.append(PpToken.PpToken(flag, 'pp-number'))
        ret_val.append(PpToken.PpToken('\n', 'whitespace'))
        return ret_val
    #------------- END: Handling line number and file output -------------------

    #=====================================
    # End: PpTokeniser generator handling.
    #=====================================
    #########################
    # End: PpLexer generators
    #########################
    
    ################################
    # Section: Read-only attributes.
    ################################    
    @property
    def fileStack(self):
        """Returns the file stack."""
        return self._fis.fileStack
    
    @property
    def includeDepth(self):
        """Returns the integer depth of the include stack."""
        return self._fis.depth
    
    @property
    def currentFile(self):
        """Returns the file ID on the top of the file stack."""
        return self._fis.currentFile
    
    @property
    def fileIncludeGraphRoot(self):
        """Returns the FileIncludeGraphRoot object."""
        return self._fis.fileIncludeGraphRoot
    
    @property
    def condState(self):
        """The conditional state as (boolean,  string)."""
        return self._condStack.isTrue(), str(self._condStack)
    
    @property
    def condCompGraph(self):
        """The conditional compilation graph as a CppCond.CppCondGraph object."""
        return self._condCompGraph
    
    @property
    def definedMacros(self):
        """Returns a string representing the currently defined macros."""
        return str(self._macroEnv)

    @property
    def macroEnvironment(self):
        """The current Macro environment as a MacroEnv object.
        Caution: Write to this at your own risk. Your write might be ignored or
        cause undefined behaviour."""
        return self._macroEnv
    
    @property
    def fileLineCol(self):
        """Returns a FileLineCol object or None"""
        if self._fis.depth > 0:
            return self._fis.fileLineCol
        
    #=============================================
    # Section: Read-only file location attributes.
    #=============================================
    @property
    def tuFileId(self):
        """Returns the user supplied ID of the translation unit."""
        return self._tuFileId
    
    @property
    def fileName(self):
        """Returns the current file name during processing."""
        return self._fis.currentFile

    @property
    def lineNum(self):
        """Returns the current line number as an integer during processing or None."""
        if self._fis.depth > 0:
            #import traceback
            #print 'lineNum', self._fis.ppt.pLineCol[0]
            #print ''.join(traceback.format_list(traceback.extract_stack()))
            return self._fis.ppt.pLineCol[0]
    
    @property
    def colNum(self):
        """Returns the current column number as an integer during processing."""
        return self._fis.ppt.pLineCol[1]
    #=========================================
    # End: Read-only file location attributes.
    #=========================================
    
    @property
    def tuIndex(self):
        return self._tuIndex
    ############################
    # End: Read-only attributes.
    ############################    

    ############################
    # Section: Helper functions.
    ############################
    def _diagnosticDebugMessage(self, theM):
        assert(self._diagnostic is not None)
        self._diagnostic.debug(theM, self.fileLineCol)

    def _nextNonWsOrNewline(self, theGen, theDiscardList=None):
        """Returns the next non-whitespace token or whitespace that contains a
        newline. If theDiscardList is non-None intermediate tokens will be
        appended to it."""
        while 1:
            myTtt = next(theGen)
            if not myTtt.isWs() \
            or self._wsHandler.isBreakingWhitespace(myTtt.t):
                return myTtt
            elif theDiscardList is not None:
                theDiscardList.append(myTtt)

    def _tokensToEol(self, theGen, macroReplace):
        """Returns a list of PpToken objects from a generator up to and
        including the first token that has a newline.
        If macroReplace is True then macros are replaced with the current
        environment."""
        retList = []
        while 1:
            # Take the position just before we read the token to give it
            # to self._macroEnv.replace(...)
            myFlc = self.fileLineCol
            myTtt = next(theGen)
            if self._wsHandler.isBreakingWhitespace(myTtt.t):
                retList.append(myTtt)
                break
            elif macroReplace:
                if self._macroEnv.mightReplace(myTtt):
#                    print 'mightReplace %s' % myTtt
                    try:
                        for aTtt in self._macroEnv.replace(
                                        myTtt,
                                        theGen,
                                        myFlc,
                                        ):
                            retList.append(aTtt)
                    except ExceptionCpip as err:
                        self._diagnostic.error(str(err), self._fis.fileLineCol)
                    if len(retList) > 0 \
                    and self._wsHandler.isBreakingWhitespace(retList[-1].t):
                        break
                else:
#                    print '  no Replace %s' % myTtt
                    retList.append(myTtt)
            else:
                retList.append(myTtt)
        return retList
    
    def _countNonWsTokens(self, theTokS):
        """Returns the integer count of non-whitespace tokens in the given list."""
        retCount = 0
        for aTok in theTokS:
            if not aTok.isWs():
                retCount += 1
        return retCount
    
    def _retListReplacedTokens(self, theTokS):
        """Takes a list of PpToken objects and returns a list of PpToken
        objects where macros are replaced in the current environment
        where possible.
        TODO: get pragma to use this."""
        retList = []
        if len(theTokS) > 0:
            myListAsGen = ListGen.ListAsGenerator(theTokS)
            myGen = next(myListAsGen)
            while not myListAsGen.listIsEmpty:
                myTok = next(myGen)
                #print '_retListReplacedTokens(): myTok', myTok
                if self._macroEnv.mightReplace(myTok):
                    for aTtt in self._macroEnv.replace(
                                        myTok,
                                        myGen,
                                        self.fileLineCol,
                                        ):
                        retList.append(aTtt)
                else:
                    retList.append(myTok)
        return retList
    ########################
    # End: Helper functions.
    ########################
    
    ##############################################
    # Section: Processing preprocessor directives.
    ##############################################
    def _processCppDirective(self, theTtt, theGen):
        """ISO/IEC ISO/IEC 14882:1998(E) 16 Preprocessing directives [cpp]
        This consumes tokens and generates others.
        Returns True of all tokens consumed OK, False otherwise.
        """
        assert(theTtt.t == self.PP_DIRECTIVE_PREFIX)
        assert(theTtt.tt == 'preprocessing-op-or-punc')
        # Take the current location
        myFlc = self.fileLineCol
        myUnresolvedTokens = [theTtt]
        myTtt = self._nextNonWsOrNewline(theGen, myUnresolvedTokens)
        myUnresolvedTokens.append(myTtt)
        if self._wsHandler.isBreakingWhitespace(myTtt.t):
            # This is "#\n" or equivelent
            yield PpToken.PpToken('\n', 'whitespace')
        else:
            if myTtt.tt != 'identifier':
                # This is an error of some sort e.g. '# "hello"'
                # cpp.exe: invalid preprocessing directive #"hello"
                self._diagnostic.undefined(
                    'invalid preprocessing directive "%s"' \
                        % (''.join([t.t for t in myUnresolvedTokens])),
                    self._fis.fileLineCol,
                    )
                if not self._wsHandler.isBreakingWhitespace(myTtt.t):
                    myUnresolvedTokens.extend(self._tokensToEol(theGen, macroReplace=False))
                for aTtt in myUnresolvedTokens:
                    yield aTtt
            else:
                # myTtt is a identifier such as 'define'
                #print '_processCppDirective() identifier:', myTtt
                # Take current location in case of error
                try:
                    mySubGenFn = self._KEYWORD_DESPATCH[myTtt.t]
                except KeyError:
                    if self._condStack.isTrue():
                        self._diagnostic.undefined(
                            ' identifier "# %s"' \
                                % myTtt.t,
                            myFlc,
                            )
                        if not self._wsHandler.isBreakingWhitespace(myTtt.t):
                            myUnresolvedTokens.extend(self._tokensToEol(theGen, macroReplace=False))
    #                    for aTtt in myUnresolvedTokens:
    #                        yield aTtt
                else:
                    # Handle the identifier
                    for aTok in mySubGenFn(theGen, myFlc):
                        yield aTok
                    myUnresolvedTokens = []
        self._isNewline = True
        

    #=============================================
    # Section: Helpers for conditional processing.
    #=============================================
    def _appendTokenMergingWhitespace(self, theList, theToken):
        """Adds a token to the list merging whitespace if possible."""
        if len(theList) and theList[-1].isWs() and theToken.isWs():
            # Make sure we have a copy on the list tail otherwise the merge
            # will be seen by any other list that has that token
            theList.append(theList.pop().copy())
            theList[-1].merge(theToken)
        else:
            theList.append(theToken)
    
    def _retDefinedSubstitution(self, theGen):
        """Returns a list of tokens from the supplied argument with defined...
        and !defined... handled appropriately and other tokens expanded where
        appropriate.
        This is used by #if, #elif.
        Reporting conditional state:
        For example:
        #define F(a) a % 2
        #define X 5

        What to say?     This?        Or?           Or?              Or?
        #if F(X) == 1    F(X) == 1    F(5) == 1    (5 % 2) == 1      1 == 1
        ...
        #else            !F(X) == 1   !F(5) == 1   !(5 % 2) == 1     !(1 == 1)
        ...
        #endif
        The current implementation takes the first as most useful: "F(X) == 1".
        This means capturing the original token stream as well
        as the (possibly replaced) evaluated token stream.
        
        TODO: There is an issue here is  with poorly specified #if/#elif statements
        For example:
        #if deeeefined SPAM
        cpp.exe: <stdin>:1:7: missing binary operator before token "SPAM"
        #if 1 SPAM
        cpp.exe: <stdin>:1:7: missing binary operator before token "SPAM"        
        """
        # Note: cpp.exe
        # Fails:
        # #if ((defined((S))))
        #Passes:
        # #if ((defined(S)))
        # The raw tokens
        rawTokS = []
        # The replaced or otherwise interpreted tokens
        repTokS = []
        flagInvert = flagHasSeenDefined = False
        macroReplacedTokS = []
        while 1:
            myFlc = self.fileLineCol
            if len(macroReplacedTokS) > 0:
                myTtt = macroReplacedTokS.pop(0)
            else:
                myTtt = next(theGen)
                rawTokS.append(myTtt)
            logging.debug('_retDefinedSubstitution(): %s' % myTtt)
            if self._wsHandler.isBreakingWhitespace(myTtt.t):
                self._appendTokenMergingWhitespace(repTokS, myTtt)
                break
            else:
                # Look for: '!', 'defined'
                if myTtt.t == '!':
                    flagInvert = True
                elif myTtt.t == 'defined':
                    flagHasSeenDefined = True
                elif myTtt.isIdentifier():
                    # Possible macro definition or expansion possibility
                    if flagHasSeenDefined:
                        # This is something like #if defined FOO where
                        # myTtt is 'FOO'.
                        # MyDefTok will be a pp-number of 0 or 1
                        repTokS.append(self._macroEnv.defined(
                                                myTtt,
                                                flagInvert,
                                                myFlc,
                                                ))
                        flagHasSeenDefined = flagInvert = False
                    elif self._macroEnv.mightReplace(myTtt):
                        # Macro replacement
                        for aTtt in self._macroEnv.replace(
                                        myTtt,
                                        theGen,
                                        myFlc,
                                        ):
                            #print '_retDefinedSubstitution(): replaced: %s' % aTtt
                            self._appendTokenMergingWhitespace(macroReplacedTokS, aTtt)
#                         if len(macroReplacedTokS) > 0 \
#                         and self._wsHandler.isBreakingWhitespace(macroReplacedTokS[-1].t):
#                             break
                    else:
                        if flagInvert:
                            # Something like #if !NOWT where NOWT is not defined
                            repTokS.append(PpToken.PpToken('1', 'pp-number'))
                        else:
                            # Something like #if NOWT where NOWT is not defined
                            repTokS.append(PpToken.PpToken('0', 'pp-number'))
                else:
                    self._appendTokenMergingWhitespace(repTokS, myTtt)
        #print '_retDefinedSubstitution(): returning rep: "%s"' % ''.join([t.t for t in repTokS])
        #print '_retDefinedSubstitution(): returning raw: "%s"' % ''.join([t.t for t in rawTokS])
        return repTokS, rawTokS

    def _retIfEvalAndTokens(self, theGen):
        """Returns (bool | None, tokenStr) from processing a #if or #elif
        conditional statement. This also handles defined... and !defined...
        bool - True/False based on the evaluation of the constant expression.
               This will be None on evaluation failure.
        tokenStr - A string of raw (original) PpTokens that made up the constant
                 expression.
        """
        myTokS, myRawTokS = self._retDefinedSubstitution(theGen)
        myTokStr = ''.join([t.t for t in myRawTokS]).strip()
        try:
            myCe = ConstantExpression.ConstantExpression(myTokS)
            myBool = myCe.evaluate()
        except ConstantExpression.ExceptionConstantExpression as err:
            myBool = None
            self._diagnostic.undefined(
                    'Can not evaluate constant expression "%s", error: %s' \
                        % (myTokStr, str(err)),
                    self._fis.fileLineCol)
        return myBool, myTokStr

    def _retDefineAndTokens(self, theGen):
        """Returns 1 or 0 if a macro is defined."""
        # Literal tokens as a list of strings
        myLiteralTokS = []
        # Tokens to be evaluated as a list of PpToken objects
        myEvalToks = []
        for aTok in self._tokensToEol(theGen, macroReplace=False):
            myLiteralTokS.append(aTok.t)
            if aTok.isIdentifier():
                myEvalToks.append(self._macroEnv.defined(
                                    aTok,
                                    False,
                                    self.fileLineCol,
                                    )
                )
            else:
                myEvalToks.append(aTok)
        myCe = ConstantExpression.ConstantExpression(myEvalToks)
        #print '_retDefineAndTokens() _fileLocator:\n', str(self._fileLocator)
        literalStr = ' '.join(myLiteralTokS)
        return myCe.evaluate(), literalStr.strip()

    def _reportSpuriousTokens(self, theCmd):
        """Reports the presence of spurious tokens in things like:
        #else spurious 1 ) tokens ...
        Used by #else and #endif which expect no semantically significant
        tokens to follow them.
        Typical cpp.exe behaviour:
        cpp.exe: <stdin>:3:7: warning: extra tokens at end of #else directive
        """
        self._diagnostic.implementationDefined(
                'extra tokens at end of #%s directive' % theCmd,
                self._fis.fileLineCol,
                )
    #===========================================
    # End: Helpers for pre-processing directives.
    #===========================================

    ##############################################
    # Section: Handling pre-processing directives.
    ##############################################
    #==========================================
    # Section: Handling conditional processing.
    #==========================================
    def _cppIf(self, theGen, theFlc):
        """Handles a if directive."""
        # Note: This use of LPAREN/RPAREN is not specified in the
        # standard but commonly appears
        ##define SPAM
        ##if (    (  (defined (SPAM))))
        myBool, myStr = self._retIfEvalAndTokens(theGen)
        # TODO: Why is this different to Ifdef/Ifndef?
        # myBool is None if the eval fails and self._diagnostic.undefined does not raise
        if myBool is not None:
#             print('_cppIf(): myStr: "%s"' % myStr)
            self._condStack.oIf(myBool, myStr)
            self._condCompGraph.oIf(theFlc,
                                    self._tuIndex,
                                    self._condStack.isTrue(),
                                    myStr)
#             print('_cppIf(): self._condStack:', self._condStack)
        yield PpToken.PpToken('\n', 'whitespace')

    def _cppElif(self, theGen, theFlc):
        """Handles a elif directive."""
        # If we have already seen the self._condStack as being True then we do
        # not tempt fate with self._retIfEvalAndTokens(theGen) as
        # the eval is irrelevant and macros may have syntax errors that are
        # 'safe' (according to the Rationale) to ignore.
        if self._condStack.hasBeenTrueAtCurrentDepth():
            # Some previous block is True so the evaluation of #elif is
            # irrelevent. See the C Rationale page 97/98.
            # So all we need to do here is consume the token to EOL
            # Test is in TestPpLexer.test_6_10_00_03()
            myTokS = self._tokensToEol(theGen, macroReplace=False)
            myStr = ''.join([t.t for t in myTokS]).strip()
            myBool = False
        else:
            # This might eveluate to True so we definitely want macro expansion
            # and eval
            myBool, myStr = self._retIfEvalAndTokens(theGen)
        if myBool is not None:
            self._condStack.oElif(myBool, myStr)
            self._condCompGraph.oElif(theFlc,
                                      self._tuIndex,
                                      self._condStack.isTrue(),
                                      myStr)
        yield PpToken.PpToken('\n', 'whitespace')

    def _cppIfdef(self, theGen, theFlc):
        """Handles a Ifdef directive."""
        myBool, myStr = self._retDefineAndTokens(theGen)
        #print '_cppIfdef(): myStr: "%s"' % myStr
        #print '_cppIfdef(): self._condStack was:', self._condStack
        #if myBool is not None:
        self._condStack.oIfdef(myBool, 'def %s' % myStr)
        self._condCompGraph.oIfdef(theFlc,
                                   self._tuIndex,
                                   self._condStack.isTrue(),
                                   myStr)
        #print '_cppIfdef(): self._condStack now:', self._condStack
        yield PpToken.PpToken('\n', 'whitespace')

    def _cppIfndef(self, theGen, theFlc):
        """Handles a ifndef directive."""
        myBool, myStr = self._retDefineAndTokens(theGen)
        #print '_cppIfndef(): myStr: "%s"' % myStr
        #print '_cppIfndef(): self._condStack was: %s, %s' % self.condState
        #print self.macroEnvironment
        #if myBool is not None:
        self._condStack.oIfndef(myBool, '!def %s' % myStr)
        self._condCompGraph.oIfndef(theFlc,
                                    self._tuIndex,
                                    self._condStack.isTrue(),
                                    myStr)
        #print '_cppIfndef(): self._condStack now: %s, %s' % self.condState
        yield PpToken.PpToken('\n', 'whitespace')

    def _cppElse(self, theGen, theFlc):
        """Handles a else directive."""
        # Consume tokens to new line
        # cpp.exe: <stdin>:3:7: warning: extra tokens at end of #else directive
        myTokS = self._tokensToEol(theGen, macroReplace=False)
        if self._countNonWsTokens(myTokS):
            self._reportSpuriousTokens('else')
        #print
        #print 'cppElse(): self._condStack was:', self._condStack
        self._condStack.oElse()
        self._condCompGraph.oElse(theFlc, self._tuIndex, self._condStack.isTrue())
        #print 'cppElse(): self._condStack now:', self._condStack
        yield PpToken.PpToken('\n', 'whitespace')

    def _cppEndif(self, theGen, theFlc):
        """Handles a endif directive."""
        # This is wrapped in a try/finally block so that if there is an error
        # in the _tokensToEol() the _condStack is always popped. This can happen
        # when the last line of a file is something like:
        # #endif // __SPAM_H__
        # And without a newline after __SPAM_H__.
        # This will cause an "Unfinished C++ style comment" error and, without
        # the finally clause, would corrupt the _condStack
        try:
            # Consume tokens to new line
            myTokS = self._tokensToEol(theGen, macroReplace=False)
            # Report spurious tokens
            # cpp.exe: <stdin>:3:7: warning: extra tokens at end of #endif directive
            if self._countNonWsTokens(myTokS):
                self._reportSpuriousTokens('endif')
        finally:
            # Trap any exception in the finally block otherwise that
            # may displace an exception generated in the try block above.
            try:
                # Take state for cond graph, we do this now so that self._condStack
                # is always called before self._condCompGraph as the former has
                # the exception handling. 
                self._condStack.oEndif()
                myEndifState = self._condStack.isTrue()
                self._condCompGraph.oEndif(theFlc, self._tuIndex, myEndifState)
                yield PpToken.PpToken('\n', 'whitespace')
            except Exception as err:
                logging.fatal('PpLexer._cppEndif(): Encountered exception in finally clause: %s' % str(err))
                pass
    #======================================
    # End: Handling conditional processing.
    #======================================

    #==================================
    # Section: Handling file inclusion.
    #==================================
    def _cppInclude(self, theGen, theFlc):
        """Handles an #include directive. This handles:
        # include <h-char-sequence> new-line
        # include "q-char-sequence" new-line
        This gathers a list of PpTokens up to, and including, a newline with
        macro replacement. Then we reinterpret the list using:
        PpTokeniser.reduceToksToHeaderName() to cast tokens to possible
        #include <header-name> token.
        Finally we try and resolve that to a 'file' that can be included.
        
        FWIW cpp.exe does not explore #include statements when they are
        conditional so will not error on unreachable files if they
        are conditionally included. 
        """
        return self._cppIncludeGeneric(theGen, theFlc,
                                       self._includeHandler.includeHeaderName)
        
    def _cppIncludeNext(self, theGen, theFlc):
        """Handles an #include_next GCC extension.
        This behaves in a very similar fashion to self._cppInclude but calls
        includeNextHeaderName() on the include handler
        """
        assert self._gccExtensions, \
            'Logic error: despatcher called _cppIncludeNext() but self._gccExtensions False'
        return self._cppIncludeGeneric(theGen, theFlc,
                                       self._includeHandler.includeNextHeaderName)
        
    def _cppIncludeGeneric(self, theGen, theFlc, theFileIncludeFunction):
        """Handles the target of an #include or #include_next directive.
        theFileIncludeFunction is the function to call to resolve the target to
        an actual file.
        """
        # NOTE: Error on #include\n
        # <stdin>:1:13: #include expects "FILENAME" or <FILENAME>
        myHeaderNameTok = self._retHeaderName(theGen)
        logging.debug('#include %s START', myHeaderNameTok)
        # We have to process the #include statement no matter what however
        # we only act on it (including errors) if we are conditionally
        # required to
        if self._condStack.isTrue():
            if myHeaderNameTok is None:
                # Failure to comprehend #include statement
                self._cppIncludeReportError('#include expects "FILENAME" or <FILENAME>')
            else:
                # Short circuit by enclosing this in an if conditional state block
                # unless the conditional level requires us to process it 
                if self._condStack.isTrue() or self._condLevel > 1:
                    try:
                        myFpo = theFileIncludeFunction(myHeaderNameTok.t)
                        logging.debug('Include search for %s finds %s', myHeaderNameTok.t, myFpo)
                        if myFpo is not None:
                            # Note: This call also handles self._fileStack.append()
                            myGen = self._pptPush(myFpo)
                            for optionalLineFileToken in self._pptPostPush():
                                yield optionalLineFileToken
                            try:
                                for aTtt in self._genPpTokensRecursive(myGen):
                                    #print 'aTtt.lineNum', aTtt.lineNum, aTtt.colNum, aTtt
                                    yield aTtt
                            finally:
                                # Trap any exception in the finally block otherwise that
                                # may displace an exception generated in the try block above.
                                try:
                                    self._pptPop()
                                    for optionalLineFileToken in self._pptPostPop():
                                        yield optionalLineFileToken
                                except Exception as err:
                                    logging.fatal('PpLexer._cppInclude(): [0] Encountered exception in finally clause : %s' % str(err))
                        else:
                            # Failure to find #included file
                            # <stdin>:1:24: asdsadasda.h: No such file or directory
                            self._cppIncludeReportError(
                                '%s: No such file or directory' % myHeaderNameTok.t
                                )
                    except IncludeHandler.ExceptionCppInclude as err:
                        logging.error('Include failed with %s', str(err))
                    finally:
                        # Trap any exception in the finally block otherwise that
                        # may displace an exception generated in the try block above.
                        try:
                            # Clean up after include
                            #print 'self._fileStack was:', self._fileStack
                            #print '    Line number was:', self._fileLocator.lineNum
                            #self._fileStack.pop()
                            self._includeHandler.endInclude()
                            #print 'self._fileStack now:', self._fileStack
                            #print '    Line number now:', self._fileLocator.lineNum
                            #print '_genPpTokens() exit'
                        except Exception as err:
                            logging.fatal('PpLexer._cppInclude(): [1] Encountered exception in finally clause : %s' % str(err))
        #logging.debug('#include %s END' % str(myHeaderNameTok))#.t)
        #logging.debug('self._fileStack now:\n    %s' % str('\n    '.join(self._fileStack)))
        #logging.debug('File node    : %s' % self._figr.graph.retLatestNode(self._fileStack))
        #logging.debug('File location: %s' % str(self._fileLocator))
        self._diagnosticDebugMessage('#include %s END' % str(myHeaderNameTok))
        yield PpToken.PpToken('\n', 'whitespace')

    def _cppIncludeReportError(self, theMsg=None):
        """Reports a consistent error message when #indlude is not processed and
        consumes all tokens up to and including the next newline."""
        myMsg = theMsg or '#include expects "FILENAME" or <FILENAME>'
        self._diagnostic.error(myMsg, self._fis.fileLineCol)

    def _retHeaderName(self, theGen):
        """This returns the first PpToken of type header-name it finds up
        to a newline token or None if none found. It handles:
        # include <h-char-sequence> new-line
        # include "q-char-sequence" new-line
        This gathers a list of PpTokens up to, and including, a newline with
        macro replacement. Then it reinterprets the list using
        PpTokeniser.reduceToksToHeaderName() to cast tokens to possible
        #include header-name token.
        """
        #print '_retHeaderName(): self._macroEnv', str(self._macroEnv)
        # TODO: This is wrongly expanding on Linux build
        # #define current get_current()
        # #include <asm/current.h>
        # Expands to: #include <asm/get_current().h>
        # TODO: Change to macroReplace=False and see below
        #
        myTokS = self._tokensToEol(theGen, macroReplace=False)
        myPpTokeniser = PpTokeniser.PpTokeniser()
        headerS = myPpTokeniser.filterHeaderNames(myTokS)
        if len(headerS) == 1:
            # Treat as a h-char-sequence or q-char-sequence
            return headerS[0]
        # Try a macro expansion
        myTokS = self._retListReplacedTokens(myTokS)
        headerS = myPpTokeniser.filterHeaderNames(myTokS)
        if len(headerS) == 1:
            # Treat as a h-char-sequence or q-char-sequence
            return headerS[0]

    #==============================
    # End: Handling file inclusion.
    #==============================

    #====================================
    # Section: Handling macro definition.
    # Note: These both increment the token count
    # unlike other preprocess directives.
    #====================================
    def _cppDefine(self, theGen, theFlc):
        """Handles a define directive."""
        ppTokenPrefix = [
                         PpToken.PpToken('#',       'preprocessing-op-or-punc'),
                         PpToken.PpToken('define',  'identifier'),
                ]
        if self._condStack.isTrue():
            try:
                myIdent = self._macroEnv.define(
                                                theGen,
                                                theFlc.fileId,
                                                theFlc.lineNum,
                                                      )
                #print 'TRACE: Macro defined:', myIdent, theFlc
                # Update token count
                for aPrefixTok in ppTokenPrefix:
                    self._fis.tokenCountInc(aPrefixTok, True, num=1)
                self._fis.tokenCounterAdd(self._macroEnv.macro(myIdent).tokenCounter)
            except MacroEnv.ExceptionMacroEnvInvalidRedefinition as err:
                # C99Rationale: 6.10.3 - "...with diagnostics generated only if the definitions differ."
                self._diagnostic.warning(str(err))
            # Note: this token will be counted by the ppTokens() generator but
            # the newline is already counted in the macro definition so there
            # is a duplicate count of a newline by one. 'Significant' tokens
            # are unaffected.
            yield PpToken.PpToken('\n', 'whitespace')
        else:
            # yield tokens without acting on them
            for aPrefixTok in ppTokenPrefix:
                yield aPrefixTok
            for aTtt in self._tokensToEol(theGen, macroReplace=False):
                yield aTtt

    def _cppUndef(self, theGen, theFlc):
        """Handles a undef directive."""
#===============================================================================
#        print 'TRACE: #undef %s %s %s' % (
#                        self._fileLocator.fileName,
#                        self._fileLocator.lineNum,
#                        self._condStack.isTrue()
#                        )
#===============================================================================
        ppTokenPrefix = [
                         PpToken.PpToken('#',     'preprocessing-op-or-punc'),
                         PpToken.PpToken('undef', 'identifier'),
                ]
        if self._condStack.isTrue():
            try:
                self._macroEnv.undef(theGen,
                                     theFlc.fileId,
                                     theFlc.lineNum)
                # We cheat a little here and rather than counting actual tokens
                # we count the prefix and two ws and an identifier
                for aPrefixTok in ppTokenPrefix:
                    self._fis.tokenCountInc(aPrefixTok, True, num=1)
                self._fis.tokenCountInc(
                                    PpToken.PpToken('\n', 'whitespace'),
                                    True,
                                    num=2)
                self._fis.tokenCountInc(
                                    PpToken.PpToken('whatever', 'identifier'),
                                    True,
                                    num=1)
            except MacroEnv.ExceptionMacroEnv as err:
                self._diagnostic.error(str(err))
#                raise ExceptionPpLexerDefine(str(err))
            yield PpToken.PpToken('\n', 'whitespace')
        else:
            # yield tokens without acting on them
            for aPrefixTok in ppTokenPrefix:
                yield aPrefixTok
            for aTtt in self. _tokensToEol(theGen, macroReplace=False):
                yield aTtt
    #================================
    # End: Handling macro definition.
    #================================

    #=======================================
    # Section: Misc. preprocessor direcives.
    #=======================================
    def _cppLine(self, theGen, theFlc):
        """Handles a line directive.
        This also handles ISO/IEC 9899:1999 (E) 6.10.4 Line control
        In particular 6.10.4-4 where the form is:
        # line digit-sequence "s-char-sequenceopt" new-line
        digit-sequence is a a token type pp-number.
        The s-char-sequenceopt is a token type 'string-literal', this
        will have the double quote delimeters and may have a 'L' prefix.
        for example L"abc"."""
        # TODO: Handle __LINE__
        #assert(0)
        # Consume tokens to new line
        # TODO: If no newline then raise an exception
        self._tokensToEol(theGen, macroReplace=False)
        yield PpToken.PpToken('\n', 'whitespace')

    def _cppError(self, theGen, theFlc):
        """Handles a error directive."""
        myTokS = self._tokensToEol(theGen, macroReplace=False)
        if self._condStack.isTrue():
            myErrMsg = ''.join([t.t for t in myTokS])
            myErrMsg = myErrMsg.strip()
            self._diagnostic.error(myErrMsg, theFlc)
        yield PpToken.PpToken('\n', 'whitespace')

    def _cppWarning(self, theGen, theFlc):
        """Handles a warning directive. Not in the standard but we support it."""
        myTokS = self._tokensToEol(theGen, macroReplace=False)
        if self._condStack.isTrue():
            myMsg = ''.join([t.t for t in myTokS])
            myMsg = myMsg.strip()
            self._diagnostic.warning(myMsg, theFlc)
        yield PpToken.PpToken('\n', 'whitespace')

    def _cppPragma(self, theGen, theFlc):
        """Handles a pragma directive.
        ISO/IEC 9899:1999 (E) 6.10.6 Pragma directive
Semantics
1 A preprocessing directive of the form
# pragma pp-tokensopt new-line
where the preprocessing token STDC does not immediately follow pragma in the
directive (prior to any macro replacement)146) causes the implementation to behave in an
implementation-defined manner. The behavior might cause translation to fail or cause the
translator or the resulting program to behave in a non-conforming manner. Any such
pragma that is not recognized by the implementation is ignored.

Footnote 146: An implementation is not required to perform macro replacement in pragmas, but it is permitted
except for in standard pragmas (where STDC immediately follows pragma). If the result of macro
replacement in a non-standard pragma has the same form as a standard pragma, the behavior is still
implementation-defined; an implementation is permitted to behave as if it were the standard pragma,
but is not required to.

In this implementation we have a special rule, if the PragmaHandler has .isLiteral as True
then we take its response and do no futher processing on it.
"""
        if self._pragmaHandler is not None:
            try:
                # It is up to the pragma handler
                myTokS = self._tokensToEol(
                                theGen,
                                macroReplace=self._pragmaHandler.replaceTokens
                            )
                pragmaStr = self._pragmaHandler.pragma(myTokS)
                if pragmaStr:
                    # Process return string
                    # Create a temporary, in-memory, file handler
                    fileId = 'pragma'
                    myFh = IncludeHandler.CppIncludeStringIO(
                                theUsrDirs=[],
                                theSysDirs=[],
                                theInitialTuContent=pragmaStr,
                                theFilePathToContent=fileId,
                            )
                    myFpo = myFh.initialTu(fileId)
                    # Preprocess the tokens
                    myGen = self._pptPush(myFpo)
                    for optionalLineFileToken in self._pptPostPush():
                        yield optionalLineFileToken
                    try:
                        if self._pragmaHandler.isLiteral:
                            # Do no further processing
                            for aTtt in myGen:
                                yield aTtt
                        else:
                            for aTtt in self._genPpTokensRecursive(myGen):
                                yield aTtt
                    finally:
                        # Trap any exception in the finally block otherwise that
                        # may displace an exception generated in the try block above.
                        try:
                            self._pptPop()
                            for optionalLineFileToken in self._pptPostPop():
                                yield optionalLineFileToken
                        except Exception as err:
                            logging.fatal('PpLexer._cppPragma(): Encountered exception in finally clause: %s' % str(err))
                            pass
            except PragmaHandler.ExceptionPragmaHandler as err:
                self._diagnostic.undefined(str(err), theFlc)
        else:
            # No pragma handler so warn (Was: report unspecified behaviour)
            myTokS = self._tokensToEol(theGen, macroReplace=False)
            self._diagnostic.warning(
                'Can not handle #pragma: %s' % ''.join([t.t for t in myTokS]),
                theFlc,
                )
        yield PpToken.PpToken('\n', 'whitespace')
    #===================================
    # End: Misc. preprocessor direcives.
    #===================================
    
    ##########################################
    # End: Processing preprocessor directives.
    ##########################################    

###############################################
# End: PpLexer - the main point of this module.
###############################################
