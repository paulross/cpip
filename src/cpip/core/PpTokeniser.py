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

"""Performs translation phases 0, 1, 2, 3 on C/C++ source code.

Translation phases from ISO/IEC 9899:1999 (E):

5.1.1.2 Translation phases
5.1.1.2-1 The precedence among the syntax rules of translation is specified by
the following phases.

Phase 1. Physical source file multibyte characters are mapped, in an
implementation defined manner, to the source character set (introducing
new-line characters for end-of-line indicators) if necessary. Trigraph
sequences are replaced by corresponding single-character internal
representations.

Phase 2. Each instance of a backslash character (\) immediately followed by
a new-line character is deleted, splicing physical source lines to form
logical source lines. Only the last backslash on any physical source line
shall be eligible for being part of such a splice. A source file that is
not empty shall end in a new-line character, which shall not be immediately
preceded by a backslash character before any such splicing takes place.

Phase 3. The source file is decomposed into preprocessing tokens6) and
sequences of white-space characters (including comments). A source file
shall not end in a partial preprocessing token or in a partial comment.
Each comment is replaced by one space character. New-line characters are
retained. Whether each nonempty sequence of white-space characters other
than new-line is retained or replaced by one space character is
implementation-defined.

TODO: Do phases 0,1,2 as generators i.e. not in memory?

TODO: Check coverage with a complete but minimal example of every token

TODO: remove self._cppTokType and have it as a return value?

TODO: Remove commented out code.

TODO: Performance of phase 1 processing.

TODO: rename next() as genPpTokens()?

TODO: Perf rewrite slice functions to take an integer argument of where in the
array to start inspecting for a slice. This avoids calls to ...[x:] e.g.
myCharS = myCharS[sliceIdx:] in genLexPptokenAndSeqWs.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

# TODO: 'C' keywords
#: ISO/IEC 9899:1999 (E) 6.4.1 Keywords
C_KEYWORDS = tuple("""auto
break
case
char
const
continue
default
do
double
else
enum
extern
float
for
goto
if
inline
int
long
register
restrict
return
short
signed
sizeof
static
struct
switch
typedef
union
unsigned
void
volatile
while
_Bool
_Complex
_Imaginary
""".split())

#Removed to stop logging holding up the performance
#import logging
from cpip import ExceptionCpip
from cpip.core import FileLocation
from cpip.core import CppDiagnostic
from cpip.core import PpWhitespace
from cpip.core import PpToken
from cpip.util import StrTree, MatrixRep

######################################################################
# Section: Module level information that is based on ISO/IEC 9899:1999
######################################################################
#: Size of the source code character set
LEN_SOURCE_CHARACTER_SET = 96
#: Comments are replaced by a single space
COMMENT_REPLACEMENT = ' '
#: Map of Digraph alternates
DIGRAPH_TABLE = {
    '<%'        : '{',
    'and'       : '&&',
    'and_eq'    : '&=',
    '%>'        : '}',
    'bitor'     : '|',
    'or_eq'     : '|=',
    '<:'        : '[',
    'or'        : '||',
    'xor_eq'    : '^=',
    ':>'        : ']',
    'xor'       : '^',
    'not'       : '!',
    '%:'        : '#',
    'compl'     : '~',
    'not_eq'    : '!=',
    '%:%:'      : '##',
    'bitand'    : '&',
}
#: Map of Trigraph alternates after the ?? prefix
TRIGRAPH_TABLE = {
    '='       : '#',
    '('       :  '[',
    '<'       : '{',
    '/'       : '\\',
    ')'       : ']',
    '>'       : '}',
    "'"       : '^',
    '!'       : '|',
    '-'       : '~',
}
#: Note: This is redoubled
TRIGRAPH_PREFIX = '?'
#: Well it is a Trigraph
TRIGRAPH_SIZE = 3
# Preprocess character sets
CHAR_SET_MAP = {
    'lex.charset'   : {
        # The source character set should be 96 characters
        # i.e. 91 plus whitespace (5)
        # See assertions below that check length, if not content
        # Note: Before jumping to conclusions about how slow this might be
        # go and look at TestPpTokeniserIsInCharSet
        'source character set'  : set("""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_{}[]#()<>%:;.?*+-/^&|~!=,\\"'\t\v\f\n """),
        # NOTE: whitespace is now handled by the PpWhitespace class
        # and this entry is dynamically added to CHAR_SET_MAP on import
        #'whitespace'            : set('\t\v\f\n '),
        # Set of ordinal characters not treated as Universal Character
        # names i.e. treated literally.
        # NOTE: ISO/IEC 9899:1999 (E) 6.4.3-2 "A universal character name shall
        # not specify a character whose short identifier is less than 00A0 other
        # than 0024 ($), 0040 (@), or 0060 (back tick), nor one in the range D800 through
        # DFFF inclusive.61)
        'ucn ordinals'          : set((0x24, 0x40, 0x60)),
    },
    'lex.ppnumber' : {
        'digit'             : set('0123456789'),
        'nonzero-digit'     : set('123456789'),
        'octal-digit'       : set('01234567'),
        'hexadecimal-digit' : set('0123456789abcdefABCDEF'),
    },
    'lex.header'  : {
        # Characters to omit from the 'source character set'
        'h-char_omit'   : set('\n>'),
        'q-char_omit'   : set('\n"'),
        # ISO/IEC 9899:1999 (E) 6.4.7 Header names Para 3 i.e. 6.4.7-3
        'undefined_h_words'   : set(('\'', '\\', '"', '//', '/*')),
        'undefined_q_words'   : set(('\'', '\\', '/*', '//')),
    },
    'lex.name'  : {
        'part_non_digit'    : set((
            '_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
            'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D',
            'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
            'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            )),
    },
    # From: ISO/IEC 14882:1998(E) 2.11 Keywords [lex.key]
    # Note these are of no particular interest to the pre-processor as
    # they do not occur in phases 1 to 4. For example 'new' is an operator
    # but is re-interpreted after phase 4 (probably in phase 7) as a keyword.
    'lex.key'   : {
        'keywords' : set((
            'asm', 'do', 'if', 'return', 'typedef',
            'auto', 'double', 'inline', 'short', 'typeid',
            'bool', 'dynamic_cast', 'int', 'signed', 'typename',
            'break', 'else', 'long', 'sizeof', 'union',
            'case', 'enum', 'mutable', 'static', 'unsigned',
            'catch', 'explicit', 'namespace', 'static_cast', 'using',
            'char', 'export', 'new', 'struct', 'virtual',
            'class', 'extern', 'operator', 'switch', 'void',
            'const', 'false', 'private', 'template', 'volatile',
            'const_cast', 'float', 'protected', 'this', 'wchar_t',
            'continue', 'for', 'public', 'throw', 'while',
            'default', 'friend', 'register', 'true',
            'delete', 'goto', 'reinterpret_cast', 'try',
            )),
    },
    # From: ISO/IEC 14882:1998(E) 2.12 Operators and punctuators [lex.operators]
    # These contain Digraphs and "Alternative Tokens" e.g. 'and' so that 'and'
    # will be seen as an operator and an identifier. Similarly 'new' appears as
    # an operator but is re-interpreted after phase 4 (probably in phase 7) as
    # a keyword.
    'lex.op'    : {
        'operators' : set((
            '{', '}', '[', ']', '#', '##', '(', ')',
            '<:', ':>', '<%', '%>', '%:', '%:%:', ';', ':', '...',
            'new', 'delete', '?', '::', '.', '.*',
            '+', '-', '*', '/', '%', '^', '&', '|', '~',
            '!', '=', '<', '>', '+=', '-=', '*=', '/=', '%=',
            '^=', '&=', '|=', '<<', '>>', '>>=', '<<=', '==', '!=',
            '<=', '>=', '&&', '||', '++', '--', ',', '->*', '->',
            'and', 'and_eq', 'bitand', 'bitor', 'compl', 'not', 'not_eq',
            'or', 'or_eq', 'xor', 'xor_eq',
            )),
    },
    'lex.icon'  : {
        'unsigned-suffix'   : set('uU'),
        'long-suffix'       : set('lL'),
    },
    'lex.ccon'  : {
        # Note leading '\\' always omitted
        'simple-escape-sequence'   : set("""'"?\\abfnrtv"""),
        # Characters to omit from the 'source character set'
        'c-con_omit'   : set("""'\\\n"""),
        # NOTE: CHAR_SET_MAP['lex.ccon']['c-char'] is loaded below
    },
    'lex.fcon'  : {
        'floating-suffix'   : set('flFL'),
        'sign'              : set('-+'),
        'exponent_prefix'   : set('eE'),
    },
    'lex.string'  : {
        # Characters to omit from the 'source character set'
        's-char_omit'   : set('"\\\n'),
        # NOTE: CHAR_SET_MAP['lex.string']['s-char'] is loaded below
    },
    'lex.bool'  : {
        'set'   : set(('false', 'true')),
    },
    # Section 16, Preprocessing directives
    'cpp'       : {
        'lparen'    : '(',
        'new-line'  : '\n',

    },
}
#================================================================
# Section: Derived information that is based on ISO/IEC 9899:1999
#================================================================
#: This adds whitespace information to internal map
CHAR_SET_MAP['lex.charset']['whitespace'] = PpWhitespace.LEX_WHITESPACE

assert(len(CHAR_SET_MAP['lex.charset']['whitespace']) == PpWhitespace.LEN_WHITESPACE_CHARACTER_SET)
assert(len(CHAR_SET_MAP['lex.charset']['source character set']
        - CHAR_SET_MAP['lex.charset']['whitespace']) == \
        (LEN_SOURCE_CHARACTER_SET - PpWhitespace.LEN_WHITESPACE_CHARACTER_SET))

# This derived information is really just an optimisation when checking

#: h-char values
CHAR_SET_MAP['lex.header']['h-char'] = CHAR_SET_MAP['lex.charset']['source character set'] \
                                        - CHAR_SET_MAP['lex.header']['h-char_omit']
#: q-char values
CHAR_SET_MAP['lex.header']['q-char'] = CHAR_SET_MAP['lex.charset']['source character set'] \
                                        - CHAR_SET_MAP['lex.header']['q-char_omit']

#: Allowable character literals, see:
#: ISO/IEC 14882:2003(E) 2.13.2 Character literals [lex.ccon]
CHAR_SET_MAP['lex.ccon']['c-char'] = CHAR_SET_MAP['lex.charset']['source character set'] \
                                            - CHAR_SET_MAP['lex.ccon']['c-con_omit']
#: Add '@', '`' and '$'
CHAR_SET_MAP['lex.ccon']['c-char'] |= set([chr(o) for o in CHAR_SET_MAP['lex.charset']['ucn ordinals'] ])

# Allowable string literals, see:
# ISO/IEC 14882:2003(E) 2.13.4 String literals [lex.string]
CHAR_SET_MAP['lex.string']['s-char'] = \
    CHAR_SET_MAP['lex.charset']['source character set'] \
    - CHAR_SET_MAP['lex.string']['s-char_omit']
# Add '@', '`' and '$'
CHAR_SET_MAP['lex.string']['s-char'] |= set([chr(o) for o in CHAR_SET_MAP['lex.charset']['ucn ordinals'] ])

# Checking by asserts, and hey, magic numbers too.
assert(len(CHAR_SET_MAP['lex.charset']['source character set']) == LEN_SOURCE_CHARACTER_SET)

# Check that CHAR_SET_MAP['lex.op']['operators'] has all the Digraphs
for k in DIGRAPH_TABLE.keys():
    assert(k in CHAR_SET_MAP['lex.op']['operators']), \
        "Digraph %s not in CHAR_SET_MAP['lex.op']['operators']" % k 

# Create StrTree objects for fast look up for words
CHAR_SET_STR_TREE_MAP = {
    'lex.key'   : {
        'keywords' : StrTree.StrTree(CHAR_SET_MAP['lex.key']['keywords']),
        },
    'lex.op'   : {
        'operators' : StrTree.StrTree(CHAR_SET_MAP['lex.op']['operators']),
        },
    'lex.bool'   : {
        'set' : StrTree.StrTree(CHAR_SET_MAP['lex.bool']['set']),
        },
}
#============================================================
# End: Derived information that is based on ISO/IEC 9899:1999
#============================================================
##################################################################
# End: Module level information that is based on ISO/IEC 9899:1999
##################################################################

############################
# Section: Module exceptions
############################
class ExceptionCpipTokeniser(ExceptionCpip):
    """Simple specialisation of an exception class for the preprocessor."""
    pass

class ExceptionCpipTokeniserUcnConstraint(ExceptionCpipTokeniser):
    """Specialisation for when universal character name exceeds constraints."""
    pass

#===============================================================================
# class ExceptionCpipTokeniserEval(ExceptionCpipTokeniser):
#    """Specialisation of an exception class eval() failures."""
#    pass
# 
# class ExceptionCpipTokeniserUndefined(ExceptionCpipTokeniser):
#    """Specialisation of an exception class for representing undefined behaviour."""
#    pass
# 
# class ExceptionCpipTokeniserFileLock(ExceptionCpipTokeniser):
#    """Specialisation of an exception class for File locks or conflicts."""
#    pass
#===============================================================================
########################
# End: Module exceptions
########################

# Comment types used in comment tokens
COMMENT_TYPE_C = 'C comment'
COMMENT_TYPE_CXX = 'C++ comment'
COMMENT_TYPES = (COMMENT_TYPE_C, COMMENT_TYPE_CXX)

####################
# Section: Tokeniser
####################
class PpTokeniser(object):
    """Imitates a Preprocessor that conforms to ISO/IEC 14882:1998(E).
    
    Takes an optional file like object.
    If theFileObj has a 'name' attribute then that will be use as the name
    otherwise theFileId will be used as the file name.
    
    **Implementation note:** On all ``_slice...()`` and ``__slice...()`` functions:
    A ``_slice...()`` function takes a buffer-like object and an integer offset as
    arguments. The buffer-like object will be accessed by index so just needs
    to implement ``__getitem__()``. On overrun or other out of bounds index an
    IndexError must be caught by the ``_slice...()`` function.
    i.e. ``len()`` should not be called on the buffer-like object, or rather, if
    ``len()`` (i.e. ``__len__()``) is called a ``TypeError`` will be raised and propagated
    out of this class to the caller.
    
    StrTree, for example, conforms to these requirements.
    
    The function is expected to return an integer that represents the number
    of objects that can be consumed from the buffer-like object. If the
    return value is non-zero the PpTokeniser is side-affected in that
    ``self._cppTokType`` is set to a non-None value. Before doing that a test is
    made and if ``self._cppTokType`` is already non-None then an assertion error
    is raised.
    
    The buffer-like object should not be side-affected by the ``_slice...()``
    function regardless of the return value.
    
    So a ``_slice...()`` function pattern is::
    
        def _slice...(self, theBuf, theOfs):
            i = theOfs
            try:
                # Only access theBuf with [i] so that __getitem__() is called
                ...theBuf[i]...
                # Success as the absence of an IndexError!
                # So return the length of objects that pass
                # First test and set for type of slice found
                if i > theOfs:
                    assert(self._cppTokType is None), '_cppTokType was %s now %s' % (self._cppTokType, ...)
                    self._cppTokType = ...
                # NOTE: Return size of slice not the index of the end of the slice
                return i - theOfs
            except IndexError:
                pass
            # Here either return 0 on IndexError or i-theOfs
            return ...
    
    NOTE: Functions starting with ``__slice...`` do not trap the IndexError, the
    caller must do that.
    
    TODO: ISO/IEC 14882:1998(E) Escape sequences Table 5?
    """
    # We support translation phases (0), 1, 2, 3
    PHASES_SUPPORTED = range(0, 4)
    # Line continuation pattern
    CONT_STR = '\\\n'
    def __init__(self, theFileObj=None, theFileId=None, theDiagnostic=None):
        """Constructor. Takes an optional file like object.
        If theFileObj has a 'name' attribute then that will be use as the name
        otherwise theFileId will be used as the file name."""
        # Set up whitespace handler
        self._whitespaceHandler = PpWhitespace.PpWhitespace()
        self._file = theFileObj
        if self._file is not None and hasattr(self._file, 'name'):
            self._fileName = self._file.name
        else:
            self._fileName = theFileId
        # This will raise on non-existent file if self._fileName is not None
        self._fileLocator = FileLocation.FileLocation(self._fileName)
        self._diagnostic = theDiagnostic or CppDiagnostic.PreprocessDiagnosticStd()
        # A simple file lock to prevent two generators trying to read the same file
        self._fileOpen = False
        # Records the type of the last preprocessing-token
        # This is a string that maybe one of PpToken.LEX_PPTOKEN_TYPES
        self._cppTokType = None
        ## Represents the contents of a source file after translation phases 1, 2
        #self._transPhaseTwo = None
        # Controls whether slice functions do an assert logic check on change
        # of token type, see _sliceLongestMatch functions.
        self._changeOfTokenTypeIsOk = False

    @property
    def pLineCol(self):
        """Returns the current physical (line, column) as integers."""
        return self._fileLocator.pLineCol

    @property
    def fileLocator(self):
        """Returns the FileLocation object."""
        return self._fileLocator

    @property
    def fileName(self):
        """Returns the ID of the file."""
        return self._fileName

    @property
    def fileLineCol(self):
        """Return an instance of FileLineCol from the current physical line column."""
        return self._fileLocator.fileLineCol()

    @property
    def cppTokType(self):
        """Returns the type of the last preprocessing-token found by _sliceLexPptoken()."""
        # Sanity check of callees
        assert(self._cppTokType is None or self._cppTokType in PpToken.LEX_PPTOKEN_TYPES)
        return self._cppTokType

    ##############################################################################
    # Section: Phases of Translation.
    # These implement ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases]
    ##############################################################################
    def resetTokType(self):
        """Erases the memory of the previously seen token type."""
        self._cppTokType = None
    
    def _rewindFile(self):
        """Sets the file to position zero and resets the FileLocator."""
        if self._file is not None:
            self._file.seek(0)
        self._fileLocator.startNewPhase()

    #=================
    # Section: Phase 0
    #=================
    def lexPhases_0(self):
        """An non-standard phase that just reads the file and returns its
        contents as a list of lines (including EOL characters).
        May raise an ExceptionCpipTokeniser if self has been created with None
        or the file is unreadable"""
        try:
            self._rewindFile()
            return self._file.readlines()
        except Exception as err:
            raise ExceptionCpipTokeniser(str(err))

    def _convertToLexCharset(self, theLineS):
        """Converts a list of lines expanding non-lex.charset characters to
        universal-character-name and returns a set of lines so encoded.
        ISO/IEC 9899:1999 (E) 6.4.3
        NOTE: ISO/IEC 9899:1999 (E) 6.4.3-2 "A universal character name shall
        not specify a character whose short identifier is less than 00A0 other
        than 0024 ($), 0040 (@), or 0060 (back tick), nor one in the range D800 through
        DFFF inclusive.61).
        """
        myCharSet = CHAR_SET_MAP['lex.charset']['source character set']
        # myUcnOrdinals is not 0024 ($), 0040 (@), or 0060 (back tick)
        myUcnOrdinals = CHAR_SET_MAP['lex.charset']['ucn ordinals']
        myMr = MatrixRep.MatrixRep()
        l = 0
        while l < len(theLineS):
            c = 0
            for c, aChar in enumerate(theLineS[l]):
                if aChar not in myCharSet:
                    myOrd = ord(aChar)
                    # Expand to a universal-character-name
                    if myOrd <= 0xFFFF:
                        # ISO/IEC 9899:1999 (E) 6.4.3-2 Universal character names - Constraints
                        # TODO: explain if False and?
                        if False and (myOrd < 0xA0 and myOrd not in myUcnOrdinals) \
                        or (myOrd >= 0xD800 and myOrd <= 0xD8FF):
                            raise ExceptionCpipTokeniserUcnConstraint( \
                                'ISO/IEC 9899:1999 (E) 6.4.3-2 UCN constraint: 0x%x out of range, location=%s file=%s' \
                                % (myOrd, self._fileLocator.pLineCol, self._fileLocator.fileName)
                            )
                        elif myOrd not in myUcnOrdinals:
                            self._fileLocator.substString(1, 6)
                            repl = '\\u%04X' % myOrd
                            #print 'Replacing with %s' % repl
                            myMr.addLineColRep(l, c, aChar, repl)
                    else:
                        self._fileLocator.substString(1, 8)
                        repl = '\\U%08X' % myOrd
                        myMr.addLineColRep(l, c, aChar, repl)
                self._fileLocator.incCol()
            self._fileLocator.incLine()
            l += 1        
        myMr.sideEffect(theLineS)
        #print 'TRACE: theLineS', theLineS

    def lexPhases_1(self, theLineS):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase one
        Takes a list of lines (including EOL characters), replaces trigraphs
        and returns the new list of lines."""
        self._convertToLexCharset(theLineS)
        self._translateTrigraphs(theLineS)
        #return myConvertedLineS
    #=============
    # End: Phase 1
    #=============

    #=================
    # Section: Phase 2
    #=================
    def _spliceLineS(self, theLineS, i):
        assert(theLineS[i].endswith(self.CONT_STR))
        self._fileLocator.spliceLine(theLineS[i])
        j = 0
        while theLineS[i].endswith(self.CONT_STR):
            j += 1
            if i+j == len(theLineS):
                # Overrun
                self._diagnostic.undefined('Continuation character in last line of file.')
                # NOTE: Diagnostic does not have to raise so continuation is
                # possible here.
                break
            if theLineS[i+j].endswith(self.CONT_STR):
                self._fileLocator.spliceLine(theLineS[i+j])
            # Need to check if the spliced line generates a universal-character-name
            # \u hex-quad
            # \U hex-quad hex-quad
            # So this lines: ["\\u\\\n", "12FE\n"] should fail as it becomes "\\u12FE\n"
            possUcnIdx = len(theLineS[i]) - len(self.CONT_STR) - len('\\u')
            theLineS[i] = theLineS[i][:-1*len(self.CONT_STR)] + theLineS[i+j]
            theLineS[i+j] = PpWhitespace.LEX_NEWLINE
            # Report undefined if a universal-character-name is found
            if possUcnIdx >= 0 \
            and self.__sliceUniversalCharacterName(theLineS[i], possUcnIdx) > 0:
                self._diagnostic.undefined('Splicing line results in a universal-character-name.')
        i += j
        return i

    def lexPhases_2(self, theLineS):
        """ISO/IEC 14882:1998(E) 2.1 Phases of translation [lex.phases] - Phase two
        This joins physical to logical lines. NOTE: This side-effects the
        supplied lines and returns None."""        
        #print '\nlexPhases_2() was [%d]:' % len(theLineS), theLineS
        # Reset the file locator
        self._fileLocator.startNewPhase()
        i = 0
        while i < len(theLineS):
            if theLineS[i].endswith(self.CONT_STR):
                i = self._spliceLineS(theLineS, i)
            else:
                self._fileLocator.incLine()
                i += 1
        #print 'lexPhases_2() now [%d]:' % len(theLineS), theLineS

    #=============
    # End: Phase 2
    #=============

#===============================================================================
#    def initLexPhase12(self):
#        """Process phases one and two and returns the result as a string."""
#        # Represents the contents of a source file after translation phases 1, 2
#        # Always do Phase 0, a psuedo phase
#        myLines = self.lexPhases_0()
#        self.lexPhases_1(myLines)
#        # NOTE: This side-effects the lines
#        self.lexPhases_2(myLines)
#        return ''.join(myLines)
#===============================================================================

    def initLexPhase12(self):
        """Process phases one and two and returns the result as a string."""
        # Represents the contents of a source file after translation phases 1, 2
        # Always do Phase 0, a psuedo phase
        myLines = self.lexPhases_0()
        self.lexPhases_1(myLines)
        # NOTE: This side-effects the lines
        self.lexPhases_2(myLines)
        return ''.join(myLines)
    #################################
    # End: Phases of Translation.
    #################################

    ##################################
    # Section: Trigraphs and Digraphs
    ##################################
    def _translateTrigraphs(self, theLineS):
        """ISO/IEC 14882:1998(E) 2.3 Trigraph sequences [lex.trigraphs]
        This returns a new set of lines with the trigraphs replaced and
        updates the FileLocator so that the physical lines and columns
        can be recovered."""
        self._fileLocator.startNewPhase()
        myMr = MatrixRep.MatrixRep()
        # Trigraph replacement
        for lineNum, aLine in enumerate(theLineS):
            i = 0
            while i <= (len(aLine) - TRIGRAPH_SIZE):
                if aLine[i] == TRIGRAPH_PREFIX \
                and aLine[i+1] == TRIGRAPH_PREFIX \
                and aLine[i+2] in TRIGRAPH_TABLE:
                    # Trigraph replacement
                    myMr.addLineColRep(
                                lineNum,
                                i,
                                aLine[i:i+TRIGRAPH_SIZE],
                                TRIGRAPH_TABLE[aLine[i+2]]
                                )
                    self._fileLocator.setTrigraph()
                    i += TRIGRAPH_SIZE
                else:
                    i += 1
                self._fileLocator.incCol()
            self._fileLocator.incLine()
        #print 'TRACE: Trigraph self._fileLocator', self._fileLocator
        myMr.sideEffect(theLineS)

    def substAltToken(self, tok):
        """If a PpToken is a Digraph this alters its value to its alternative.
        If not the supplied token is returned unchanged.
        There are no side effects on self."""
        if tok.tt in ('identifier', 'preprocessing-op-or-punc') \
        and tok.t in DIGRAPH_TABLE:
            tok.subst(DIGRAPH_TABLE[tok.t], 'preprocessing-op-or-punc')
        return tok 
           
#===============================================================================
#    def _translateDigraphs(self, theLineS):
#        """ISO/IEC 14882:1998(E) 2.5 Alternative tokens [lex.digraph]
#        Alters a token list in-place with alternate tokens."""
#        assert(0), 'We don\'t do this we leave it to later phases of translation'
#        self._fileLocator.startNewPhase()
#        myMr = MatrixRep.MatrixRep()
#        #print 'TRACE: _translateDigraphs() theLines was:\n%s' % theLineS
#        # Digraph replacement
#        for lineNum, aLine in enumerate(theLineS):
#            i = 0
#            #print 'TRACE: _translateDigraphs() aLines:%s' % aLine
#            while i < len(aLine):
#                #print 'TRACE: _translateDigraphs() i=%d' % i
#                j = self._whitespaceHandler.sliceNonWhitespace(aLine, i)
#                #print 'TRACE: _translateDigraphs() non-ws j=%d' % j
#                if j == 0:
#                    j = self._whitespaceHandler.sliceWhitespace(aLine, i)
#                    #print 'TRACE: _translateDigraphs() ws j=%d' % j
#                else:
#                    mySlice = aLine[i:i+j]
#                    #print 'TRACE: _translateDigraphs() mySlice %s' % mySlice
#                    if DIGRAPH_TABLE.has_key(mySlice):
#                        theRepl = DIGRAPH_TABLE[mySlice]
#                        #print 'TRACE: digraph replacement was: "%s" now: "%s"' \
#                        #    % (mySlice, theRepl)
#                        myMr.addLineColRep(lineNum, i, mySlice, theRepl)
#                        self._fileLocator.substString(len(mySlice), len(theRepl))
#                assert(j > 0)
#                i += j
#                self._fileLocator.incCol(j)
#            self._fileLocator.incLine()
#        #print 'TRACE: Diigraph self._fileLocator', self._fileLocator
#        myMr.sideEffect(theLineS)
#        #print 'TRACE: _translateDigraphs() theLines now:\n%s' % theLineS
#===============================================================================
    ##################################
    # End: Trigraphs and Digraphs
    ##################################

    ###########################
    # Section: Token generators
    ###########################
    def next(self):
        """The token generator. On being called this performs translations phases
        1, 2 and 3 (unless already done) and then generates pairs of:
        (preprocessing token, token type)
        Token type is an enumerated integer from LEX_PPTOKEN_TYPES.
        Proprocessing tokens include sequences of whitespace characters and
        these are not necessarily concatenated i.e. this generator can produce
        more than one whitespace token in sequence.
        TODO: Rename this to ppTokens() or something"""
        for aTokTypeObj in self.genLexPptokenAndSeqWs(self.initLexPhase12()):
            r = yield aTokTypeObj
            if r is not None:
                # Caller has invoked send() and that call also returns the next yield.
                # So we yield None as the 'return' value of send() otherwise
                # send() gets back its argument rather than persisting it to
                # the subsequent next() call.
                yield None
                # Now when the caller invokes next() after send() we yield the
                # value passed in by the caller in the previous send()
                yield r
                # Only one send() between next() calls so we continue
                # with the iteration...

    def genLexPptokenAndSeqWs(self, theCharS):
        """Generates a sequence of PpToken objects. Either:
        
            * a sequence of whitespace (comments are replaces with a single whitespace).
            * a pre-processing token.
        
        This performs translation phase 3.
        
        NOTE: Whitespace sequences are not merged so ``'  /\*\*/ '`` will generate
        three tokens each of ``PpToken.PpToken(' ', 'whitespace')`` i.e. leading
        whitespace, comment replced by single space, trailing whitespace.
        
        So this yields the tokens from translation phase 3 if supplied with
        the results of translation phase 2.
        
        NOTE: This does not generate 'header-name' tokens as these are context
        dependent i.e. they are only valid in the context of a ``#include``
        directive. ISO/IEC 9899:1999 (E) 6.4.7 Header names Para 3 says that:
        *"A header name preprocessing token is recognised only within a #include
        preprocessing directive."*.
        """
        #print 'TRACE: genLexPptokenAndSeqWs():'
        self._fileLocator.startNewPhase()
        ofsIdx = 0
        try:
            while 1:
                # Each pass through the loop we yield either:
                # - Whitespace
                # - A comment that is converted to whitespace
                # - Something else
                # Take current position
                myLine = self._fileLocator.lineNum
                myCol = self._fileLocator.colNum
                self._cppTokType = None
                sliceLen = self._sliceWhitespace(theCharS, ofsIdx) \
                    or self._sliceLexComment(theCharS, ofsIdx) \
                    or self._sliceLexPptoken(theCharS, ofsIdx)
                #print 'TRACE: TOK slice=%d index=%d token="%s" type="%s"' \
                #    % (sliceLen, ofsIdx, theCharS[ofsIdx:ofsIdx+sliceLen], self._cppTokType) 
                if sliceLen > 0:
                    assert(self._changeOfTokenTypeIsOk or self._cppTokType is not None), \
                        'genLexPptokenAndSeqWs() sliceLen=%d but token type is None for: "%s"' \
                            % (sliceLen, theCharS[ofsIdx:ofsIdx+sliceLen])
                    # Fix comments to replace them by a comment character
                    mySlice = theCharS[ofsIdx:ofsIdx+sliceLen]
                    self._fileLocator.update(mySlice)
                    ofsIdx += sliceLen
                    if self._cppTokType in COMMENT_TYPES:
                        # Turn the comment into a single whitespace
                        myTok = PpToken.PpToken(COMMENT_REPLACEMENT,
                                              'whitespace',
                                              myLine,
                                              myCol)
                    else:
                        myTok = PpToken.PpToken(mySlice,
                                              self._cppTokType,
                                              myLine,
                                              myCol)
                    yield myTok
                else:
                    break
        except IndexError:
            pass
        # Poke input and report if incomplete
        try:
            theCharS[ofsIdx]
            self._diagnostic.partialTokenStream(
                'lex.pptoken has unparsed tokens %s' % theCharS[ofsIdx:],
                self.fileLocator)
        except IndexError:
            pass

    ###########################
    # End: Token generators
    ###########################

    #########################################
    # Section: Buffer slicing to find tokens.
    #########################################
    #================================
    # Sub-section: Utiltity functions
    #================================
    def _sliceLongestMatchOfs(self, theBuf, theOfs, theFnS, isExcl=False):
        """Returns the length of the longest slice of theBuf from theOfs using
        the functions theFnS, or 0.
        This preserves self._cppTokType to be the one that gives the longest match.
        Functions that raise an IndexError will be ignored.
        If isExcl is False (the default) then all functions are tested.
        If isExcl is True then functions after one returning a non-zero value
        are not tested.
        TODO (maybe): Have slice functions return (size, type) and get rid of
        self._changeOfTokenTypeIsOk and self._cppTokType
        """
        m = 0
        fMax = None
        # We do this because parsing ".1" could first look like a punctuator
        # bus subsequently as a numeric fraction
        # First save current state as this can be called recursively
        myCottio = self._changeOfTokenTypeIsOk
        self._changeOfTokenTypeIsOk = True
        for f in theFnS:
            try:
                prevTt = self._cppTokType
                j = f(theBuf, theOfs)
                #logging.debug('_sliceLongestMatchOfs(): j=%d f=%s', j, f)
                assert(j == 0 or j != m or fMax is None), \
                    '_sliceLongestMatchOfs(): In theBuf "%s", at offset %d [%s], dupe slice %d found and  f was %s now %s' \
                        % (theBuf, theOfs, theBuf[theOfs], m, fMax, f)
                if j > m:
                    m = j
                    fMax = f
                else:
                    # Revert any change by f()
                    self._cppTokType = prevTt
                if j > 0 and isExcl:
                    break
            except IndexError:
                pass
        self._changeOfTokenTypeIsOk = myCottio
        return m

    def _sliceAccumulateOfs(self, theBuf, theOfs, theFn):
        """Repeats the function as many times as possible on theBuf from theOfs.
        An IndexError raised by the function will be caught and not propagated."""
        i = 0
        try:
            while 1:
                j = theFn(theBuf, theOfs+i)
                if j == 0:
                    break
                i += j
        except IndexError:
            pass
        return i

    def _wordsFoundInUpTo(self, theBuf, theLen, theWordS):
        """Searches theCharS for any complete instance of any word in theWordS.
        Returns the index of the find or -1 if none found."""
        if theLen > 0:
            for aWord in theWordS:
                i = self._wordFoundInUpTo(theBuf, theLen, aWord)
                if i >= 0:
                    return i
        return -1

    def _wordFoundInUpTo(self, theBuf, theLen, theWord):
        """Searches theBuf for any complete instance of a word in theBuf.
        Returns the index of the find or -1 if none found."""
        if len(theWord) > 0:
            i = 0
            # Find first letter
            while i < theLen:
                if theBuf[i] != theWord[0]:
                    i += 1
                else:
                    break
            # If found then find rest of letters
            if i < theLen and theBuf[i] == theWord[0]:
                j = 0
                while i+j < theLen \
                and j < len(theWord) \
                and theBuf[i+j] == theWord[j]:
                    j += 1
                if j == len(theWord):
                    return i
        return -1

    #========================
    # End: Utiltity functions
    #========================

    """ Generic slice function:
    def _slice...(self, theBuf, theOfs):
        i = theOfs
        try:
            # Only access theBuf with [i] so that __getitem__() is called
            ...theBuf[i]...
            # Success as the absence of an IndexError!
            # So return the length of objects that pass
            # First test and set for type of slice found
            if i > theOfs:
                assert(self._changeOfTokenTypeIsOk or self._cppTokType is None), '_cppTokType was %s now %s' % (self._cppTokType, ...)
                self._cppTokType = ...
        except IndexError:
            i = theOfs
        # NOTE: Return size of slice not the index of the end of the slice
        return i - theOfs
    NOTE: Functions starting with __slice... do not trap the IndexError, the
    caller must do that.
    """
    
    def _sliceLexPptoken(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken].
        ISO/IEC 9899:1999 (E) 6.4 Lexical elements
        NOTE: Does not identify header-name tokens. See NOTE on
        genLexPptokenAndSeqWs()
        Note: _sliceLexPptokenGeneral is an exclusive search as 'bitand' can
        appear to be both an operator (correct) and an identifier (incorrect).
        The order of applying functions is therefore highly significant
        _sliceLexPpnumber must be before _sliceLexOperators as the leading '.'
        on a number can be seen as an operator.
        _sliceCharacterLiteral and _sliceStringLiteral must be before
        _sliceLexName as the leading 'L' on char/string can be seen as a name.
        
        self._sliceLexOperators has to be after self._sliceLexName as otherwise
        #define complex gets seen as:
        # - operator
        define - identifier
        compl - operator because of alternative tokens
        ex - identifier
        """
        retVal = self._sliceLexPptokenGeneral(
                                theBuf,
                                theOfs,
                                (
                                    # pp-number
                                    self._sliceLexPpnumber,
                                    # Moved to later because of #define complex
                                    # See doc string.
                                    ## preprocessing-op-or-punc
                                    #self._sliceLexOperators,
                                    # character-literal
                                    self._sliceCharacterLiteral,
                                    # string-literal
                                    self._sliceStringLiteral,
                                    # We don't do header-name, see note above.
                                    # identifier
                                    self._sliceLexName,
                                    # preprocessing-op-or-punc
                                    self._sliceLexOperators,
                                )
                            )
        if retVal == 0:
            # "each non-white-space character that cannot be one of the above"
            retVal = self._sliceNonWhitespaceSingleChar(theBuf, theOfs)
        return retVal

    def _sliceLexPptokenWithHeaderName(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.4 Preprocessing tokens [lex.pptoken].
        NOTE: This does identify header-name tokens where possible."""
        retVal = self._sliceLexPptokenGeneral(
                                theBuf,
                                theOfs,
                                (
                                    # header-name
                                    self._sliceLexHeader,
                                    # identifier
                                    self._sliceLexName,
                                    # pp-number
                                    self._sliceLexPpnumber,
                                    # character-literal
                                    self._sliceCharacterLiteral,
                                    ## string-literal
                                    #self._sliceStringLiteral,
                                    # preprocessing-op-or-punc
                                    self._sliceLexOperators,
                                )
                            )
        if retVal == 0:
            # "each non-white-space character that cannot be one of the above"
            retVal = self._sliceNonWhitespaceSingleChar(theBuf, theOfs)
        return retVal

    def _sliceLexPptokenGeneral(self, theBuf, theOfs, theFuncS):
        """Applies theFuncS to theCharS and returns the longest match."""
        #self._cppTokType = None
        return self._sliceLongestMatchOfs(theBuf, theOfs, theFuncS, isExcl=True)

    #============================================================
    # Sub-section: Low level slicers.
    # These take a buffer and try and do a single specific match.
    #============================================================    
    def _sliceWhitespace(self, theBuf, theOfs=0):
        i = self._whitespaceHandler.sliceWhitespace(theBuf, theOfs)
        if i > 0:
            assert(self._changeOfTokenTypeIsOk or self._cppTokType is None), '_cppTokType was %s now %s' \
                % (self._cppTokType, 'whitespace')
            self._cppTokType = 'whitespace'
        return i
    
    def _sliceNonWhitespaceSingleChar(self, theBuf, theOfs=0):
        """Returns 1 if the first character is non-whitespace, 0 otherwise.
        TODO: ISO/IEC 9899:1999 (E) 6.4-3 and ISO/IEC 14882:1998(E) 2.4.2 States that
        if the character is ' or " the behaviour is undefined."""
        i = theOfs
        try:
            # Only access theBuf with [i] so that __getitem__() is called
            if theBuf[i] not in CHAR_SET_MAP['lex.charset']['whitespace']:
                i += 1
                assert(self._changeOfTokenTypeIsOk or self._cppTokType is None), '_cppTokType was %s now %s' \
                    % (self._cppTokType, 'non-whitespace')
                self._cppTokType = 'non-whitespace'
            # NOTE: Return size of slice not the index of the end of the slice
            return i - theOfs
        except IndexError:
            pass
        # Here either return 0 on IndexError or i-theOfs
        return 0
    
    #=========================
    # Section: lex.charset
    #=========================
    def _sliceHexQuad(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.2 Character sets [lex.charset] - hex-quad."""
        retLen = 4
        try:
            for i in range(retLen):
                if theBuf[i+theOfs] not in CHAR_SET_MAP['lex.ppnumber']['hexadecimal-digit']:
                    return 0
            return retLen
        except IndexError:
            pass
        return 0
    
    def __sliceUniversalCharacterName(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.2 Character sets [lex.charset] - universal-character-name."""
        # \u hex-quad
        # \U hex-quad hex-quad
        if theBuf[theOfs] == '\\':
            if theBuf[theOfs+1] == 'u' \
            and self._sliceHexQuad(theBuf, theOfs+2) == 4:
                return 6
            elif theBuf[theOfs+1] == 'U' \
            and self._sliceHexQuad(theBuf, theOfs+2) == 4 \
            and self._sliceHexQuad(theBuf, theOfs+6) == 4:
                return 10
        return 0
    #=========================
    # End: lex.charset
    #=========================

    #=========================
    # Section: lex.comment
    #=========================
    def _sliceLexComment(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.7 Comments [lex.comment]."""
        i = theOfs
        cmtStyle = None
        try:
            if theBuf[i] == '/':
                if theBuf[i+1] == '*':
                    cmtStyle = COMMENT_TYPE_C
                    i += 2
                    while 1:
                        if theBuf[i] == '*' and theBuf[i+1] == '/':
                            i += 2
                            break
                        i += 1
                elif theBuf[i+1] == '/':
                    cmtStyle = COMMENT_TYPE_CXX
                    i += 2
                    while 1:
                        if theBuf[i] == PpWhitespace.LEX_NEWLINE:
                            # Do not increment i and leave the newline in the string
                            break
                        i += 1
            if i > theOfs:
                assert(self._changeOfTokenTypeIsOk or self._cppTokType is None), '_cppTokType was %s now %s' \
                    % (self._cppTokType, cmtStyle)
                self._cppTokType = cmtStyle
        except IndexError:
            if i > theOfs:
                # This may raise
                self._diagnostic.handleUnclosedComment('Unfinished %s style comment' % cmtStyle,
                                                        self._fileLocator.fileLineCol())
                # If diagnostic has not raised then keep going
                # i.e. assume EOF is comment terminator
                self._cppTokType = cmtStyle
#===============================================================================
#                if False:
#                    # Strict behaviour with un-closed comments
#                    self._diagnostic.partialTokenStream('Unfinished %s style comment' % cmtStyle,
#                                                        self._fileLocator)
#                    i = theOfs
#                else:
#                    # More relaxed bahaviour, assumes EOF terminates comment
#                    self._diagnostic.warning('Unfinished %s style comment' % cmtStyle,
#                                                        self._fileLocator)
#                    self._cppTokType = '%s comment' % cmtStyle
#===============================================================================
        return i - theOfs
    #=========================
    # End: lex.comment
    #=========================

    #=========================
    # Section: lex.header
    #=========================
    def reduceToksToHeaderName(self, theToks):
        """This takes a list of PpTokens and retuns a list of PpTokens
        that might have a header-name token type in them.
        May raise an ExceptionCpipTokeniser if tokens are not all consumed.
        This is used at lexer level for re-interpreting PpTokens in the
        context of a #include directive."""
        # Store token type as this function may be called whilst another
        # generator is active
        myTt = self._cppTokType
        retTokS = []
        myString = PpToken.tokensStr(theToks, shortForm=True)
        while len(myString):
            while 1:
                self._cppTokType = None
                # Consume whitespace
                sliceIdx = self._sliceWhitespace(myString)
                if sliceIdx == 0:
                    break
                retTokS.append(PpToken.PpToken(myString[:sliceIdx], 'whitespace')
                    )
                myString = myString[sliceIdx:]
            self._cppTokType = None
            sliceIdx = self._sliceLexPptokenWithHeaderName(myString, 0)
            if sliceIdx == 0:
                sliceIdx = self._sliceStringLiteral(myString, 0)
            if sliceIdx > 0:
                retTokS.append(PpToken.PpToken(myString[:sliceIdx], self._cppTokType))
                myString = myString[sliceIdx:]
            else:
                # Nothing found
                break
        # Restore token type
        self._cppTokType = myTt
        if len(myString) > 0:
            raise ExceptionCpipTokeniser(
                'reduceToksToHeaderName() has unparsed tokens: %s' % myString)
        return retTokS
    
    def filterHeaderNames(self, theToks):
        """Returns a list of 'header-name' tokens from the supplied stream.
        May raise ExceptionCpipTokeniser if un-parsable or theToks has
        non-(whitespace, header-name)."""
        ret = []
        for t in self.reduceToksToHeaderName(theToks):
            if t.tt != 'whitespace':
                if t.tt == 'header-name':
                    ret.append(t)
                else:
                    return []
#                    raise ExceptionCpipTokeniser(
#                        'retHeaderName(): wrong token type %s' % t)
#        print(theToks, ret)
        return ret
                    

    def _sliceLexHeader(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header].
        Might raise a ExceptionCpipUndefinedLocal."""
        i = theOfs
        try:
            if theBuf[i] == '<':
                i += 1
                j = self._sliceLexHeaderHcharSequence(theBuf, i)
                if j > 0 and theBuf[theOfs+i+j] == '>':
                    i += j + 1
                else:
                    i = 0
            elif theBuf[i] == '"':
                i += 1
                j = self._sliceLexHeaderQcharSequence(theBuf, i)
                if j > 0 and theBuf[theOfs+i+j] == '"':
                    i += j + 1
                else:
                    i = 0
            else:
                i = 0
            # Success as the absence of an IndexError!
            # So return the length of objects that pass
            # First test and set for type of slice found
            if i > 0:
                assert(self._changeOfTokenTypeIsOk or self._cppTokType is None), '_cppTokType was %s now %s' \
                    % (self._cppTokType, 'header-name')
                self._cppTokType = 'header-name'
        except IndexError:
            i = 0
        return i

    def _sliceLexHeaderHcharSequence(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - h-char-sequence.
        Might raise a ExceptionCpipUndefinedLocal."""
        retVal = self._sliceAccumulateOfs(theBuf, theOfs, self._sliceLexHeaderHchar)
        # undefined_h_words
        if retVal > 0:
            undefWordIndex = self._wordsFoundInUpTo(theBuf,
                                                    retVal,
                                                    CHAR_SET_MAP['lex.header']['undefined_h_words'])
            if undefWordIndex > 0:
                # Here we return 0 (not raising) as it is up to the caller to
                # decide if the behaviour is undefined. ISO/IEC 9899:1999 (E)
                # 6.4.7 Header names Para 3 says that "A header name
                # preprocessing token is recognized only within a #include
                # preprocessing directive."
                # Only the caller can know this so it is up to the caller
                # to deal with undefined behaviour.
                return 0
        return retVal

    def _sliceLexHeaderHchar(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - h-char character."""
        try:
            if theBuf[theOfs] in CHAR_SET_MAP['lex.header']['h-char']:
                return 1
        except IndexError:
            pass
        return 0

    def _sliceLexHeaderQcharSequence(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - q-char-sequence.
        Might raise a ExceptionCpipUndefinedLocal."""
        retVal = self._sliceAccumulateOfs(theBuf, theOfs, self._sliceLexHeaderQchar)
        # undefined_q_words
        if retVal > 0:
            undefWordIndex = self._wordsFoundInUpTo(theBuf,
                                                    retVal,
                                                    CHAR_SET_MAP['lex.header']['undefined_q_words'])
            if undefWordIndex > 0:
                return 0
                # Here we return 0 (not raising) as it is up to the caller to
                # decide if the behaviour is undefined. ISO/IEC 9899:1999 (E)
                # 6.4.7 Header names Para 3 says that "A header name
                # preprocessing token is recognized only within a #include
                # preprocessing directive."
                # Only the caller can know this so it is up to the caller
                # to deal with undefined behaviour.
                # TODO: explain this when "abc\0xyz"
        return retVal

    def _sliceLexHeaderQchar(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.8 Header names [lex.header] - q-char."""
        try:
            if theBuf[theOfs] in CHAR_SET_MAP['lex.header']['q-char']:
                return 1
        except IndexError:
            pass
        return 0
    #=========================
    # End: lex.header
    #=========================

    #=========================
    # Section: lex.ppnumber
    #=========================
    def _sliceLexPpnumber(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.9 Preprocessing numbers [lex.ppnumber].
        TODO: Spec says "Preprocessing number tokens lexically include all integral literal tokens (2.13.1) and all floating literal tokens (2.13.3)."
        But the pp-number list does not specify that.
        NOTE: ISO/IEC 9899:1999 Programming languages - C allows 'p' and 'P' suffixes.
        NOTE: The standard appears to allow '.1.2.3.4.'
        """
        #pp-number:
        #digit
        #. digit
        #pp-number digit
        #pp-number nondigit
        #pp-number e sign
        #pp-number E sign
        #pp-number .
        i = theOfs
        try:
            # Check prefix
            if theBuf[i] in CHAR_SET_MAP['lex.ppnumber']['digit']:
                i += 1
            elif theBuf[i] == '.' \
            and theBuf[i+1] in CHAR_SET_MAP['lex.ppnumber']['digit']:
                i += 2
            # No refix, no pp-number
            if i == theOfs:
                return 0
            # Check rest of the characters
            while 1:
                j = 0
                # Single characters; '.'
                if theBuf[i] == '.':
                    j = 1
                else:
                    # Handle multiple characters
                    j = self._sliceLongestMatchOfs(
                                        theBuf,
                                        i,
                                        (
                                            self.__sliceNondigit,
                                            self.__sliceLexPpnumberDigit,
                                            self.__sliceLexPpnumberExpSign
                                        )
                                    )
                if j > 0:
                    i += j
                else:
                    break
        except IndexError:
            pass#i = theOfs
        if i > theOfs:
            assert(self._changeOfTokenTypeIsOk or self._cppTokType is None), '_cppTokType was "%s" now "%s"' \
                % (self._cppTokType, 'pp-number')
            self._cppTokType = 'pp-number'
        return i - theOfs
        
    def __sliceLexPpnumberDigit(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.9 Preprocessing numbers [lex.ppnumber] - digit."""
        if theBuf[theOfs] in CHAR_SET_MAP['lex.ppnumber']['digit']:
            return 1
        return 0

    def __sliceLexPpnumberExpSign(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.9 Preprocessing numbers [lex.ppnumber] - exponent and sign.
        Returns 2 if theCharS is 'e' or 'E' followed by a sign."""
        if theBuf[theOfs] in CHAR_SET_MAP['lex.fcon']['exponent_prefix'] \
        and theBuf[theOfs+1] in CHAR_SET_MAP['lex.fcon']['sign']:
            return 2
        return 0
    #=========================
    # End: lex.ppnumber
    #=========================

    #=========================
    # Section: lex.name
    #=========================
    def _sliceLexName(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.10 Identifiers [lex.name]."""
        #2.10 Identifiers
        #identifier:
        #nondigit
        #identifier nondigit
        #identifier digit
        try:
            i = self.__sliceNondigit(theBuf, theOfs)
            if i == 0:
                return 0
            else:
                i += theOfs
        except IndexError:
            return 0
        try:
            while i > theOfs:
                # Concatenate
                j = self._sliceLongestMatchOfs(
                                            theBuf,
                                            i,
                                            (
                                                self.__sliceNondigit,
                                                self.__sliceLexPpnumberDigit,
                                            )
                                           )
                if j > 0:
                    i += j
                else:
                    break
            if i > theOfs:
                assert(self._changeOfTokenTypeIsOk or self._cppTokType is None), '_cppTokType was %s now %s' \
                            % (self._cppTokType, 'identifier')
                self._cppTokType = 'identifier'
        except IndexError:
            pass
        return i - theOfs

    def __sliceNondigit(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.10 Identifiers [lex.name] - nondigit."""
        #nondigit: one of
        #universal-character-name
        #_ a b c d e f g h i j k l m
        #n o p q r s t u v w x y z
        #A B C D E F G H I J K L M
        #N O P Q R S T U V W X Y Z
        i = self.__sliceUniversalCharacterName(theBuf, theOfs)
        if i == 0:
            # Try alternates
            if theBuf[theOfs] in CHAR_SET_MAP['lex.name']['part_non_digit']:
                return 1
        return i
    #=========================
    # End: lex.name
    #=========================

    #=========================
    # Section: lex.key
    #=========================
    def _sliceLexKey(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.11 Keywords [lex.key]."""
        try:
            return self.__sliceLexKey(theBuf, theOfs)
        except KeyError:
            pass
        return 0

    def __sliceLexKey(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.11 Keywords [lex.key]."""
        return CHAR_SET_STR_TREE_MAP['lex.key']['keywords'].has(theBuf, theOfs) - theOfs
    #=========================
    # End: lex.key
    #=========================

    #=========================
    # Section: lex.operators
    #=========================
    def _sliceLexOperators(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.12 Operators and punctuators [lex.operators].
        i.e. preprocessing-op-or-punc"""
        # Note: StrTree.has() traps IndexError so we don't have to
        i = CHAR_SET_STR_TREE_MAP['lex.op']['operators'].has(theBuf, theOfs) - theOfs
        if i > 0:
            assert(self._changeOfTokenTypeIsOk or self._cppTokType is None), '_cppTokType was %s now %s' \
                % (self._cppTokType, 'preprocessing-op-or-punc')
            self._cppTokType = 'preprocessing-op-or-punc'
        return i
    #=========================
    # End: lex.operators
    #=========================

    #==================
    # Literals.
    #==================
    def _sliceLiteral(self, theBuf, theOfs=0):
        """Returns the length of a slice of theCharS that matches the longest integer literal or 0.
        ISO/IEC 14882:1998(E) 2.13 Literals [lex.literal]."""
        return self._sliceLongestMatchOfs(
                                theBuf,
                                theOfs,
                                (
                                    self._sliceIntegerLiteral,
                                    self._sliceCharacterLiteral,
                                    self._sliceFloatingLiteral,
                                    self._sliceStringLiteral,
                                    self._sliceBoolLiteral,
                                )
                            )
    #==================
    # Integer literals.
    #==================
    def _sliceIntegerLiteral(self, theBuf, theOfs=0):
        """Returns the length of a slice of theCharS that matches the longest integer literal or 0.
        ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon]."""
        i = self._sliceLongestMatchOfs(
                                theBuf,
                                theOfs,
                                (
                                    self._sliceDecimalLiteral,
                                    self._sliceOctalLiteral,
                                    self._sliceHexadecimalLiteral,
                                )
                            )
        if i:
            i += self._sliceIntegerSuffix(theBuf, theOfs+i)
        return i

    def _sliceDecimalLiteral(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - decimal-literal."""
        i = theOfs
        try:
            if theBuf[i] in CHAR_SET_MAP['lex.ppnumber']['nonzero-digit']:
                i += 1
                while theBuf[i] in CHAR_SET_MAP['lex.ppnumber']['digit']:
                    i += 1
        except IndexError:
            pass
        return i - theOfs

    def _sliceOctalLiteral(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - octal-literal."""
        i = theOfs
        try:
            if theBuf[i] == '0':
                i = 1
                while theBuf[i] in CHAR_SET_MAP['lex.ppnumber']['octal-digit']:
                    i += 1
        except IndexError:
            # NOTE: "0" is octal literal 0, see ISO/IEC 14882:1998(E) 2.13.1
            # octal-literal:
            # 0
            # octal-literal octal-digit
            pass
        return i - theOfs

    def _sliceHexadecimalLiteral(self, theBuf, theOfs=0):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - hexadecimal-literal."""
        i = theOfs
        try:
            if theBuf[i] == '0' \
            and theBuf[i+1] in ('x', 'X'):
                i += 2
            else:
                return 0
            while theBuf[i] in CHAR_SET_MAP['lex.ppnumber']['hexadecimal-digit']:
                i += 1
        except IndexError:
            pass
        i -= theOfs
        if i > 2:
            return i
        return 0

    def _sliceIntegerSuffix(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - integer-suffix.
        integer-suffix:
            unsigned-suffix long-suffix opt
            long-suffix unsigned-suffix opt"""
        i = 0
        try:
            i = self.__sliceUnsignedSuffix(theBuf, theOfs)
            if i > 0:
                i += self.__sliceLongSuffix(theBuf, theOfs+1)
            else:
                i = self.__sliceLongSuffix(theBuf, theOfs)
                if i > 0:
                    i += self.__sliceUnsignedSuffix(theBuf, theOfs+1)
        except IndexError:
            pass
        return i

    def __sliceUnsignedSuffix(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - unsigned-suffix."""
        if theBuf[theOfs] in CHAR_SET_MAP['lex.icon']['unsigned-suffix']:
            return 1
        return 0

    def __sliceLongSuffix(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.1 Integer literals [lex.icon] - long-suffix."""
        if theBuf[theOfs] in CHAR_SET_MAP['lex.icon']['long-suffix']:
            return 1
        return 0
    #=======================
    # End: Integer literals.
    #=======================

    #====================
    # Character literals.
    #====================
    def _sliceCharacterLiteral(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon]."""
        #character-literal:
        #'c-char-sequence'
        #L'c-char-sequence'
        i = theOfs
        try:
            if theBuf[i] == 'L':
                i += 1
            if theBuf[i] == "'":
                i += 1
                j = self._sliceCCharSequence(theBuf, i)
                i += j
                # Has character run, check for closing "'"
                if theBuf[i] == "'":
                    # Good to go
                    i += 1
                else:
                    return 0
            else:
                # 'L' on its own or no opening "'"
                return 0
            if i > theOfs:
                assert(self._changeOfTokenTypeIsOk or self._cppTokType is None), '_cppTokType was %s now %s' \
                        % (self._cppTokType, 'character-literal')
                self._cppTokType = 'character-literal'
        except IndexError:
            i = theOfs
        return i - theOfs
    
    def _sliceCCharSequence(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - c-char-sequence."""
        return self._sliceAccumulateOfs(theBuf, theOfs, self._sliceCChar)

    def _sliceCChar(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - c-char."""
        return self._sliceLongestMatchOfs(
                                theBuf,
                                theOfs,
                                (
                                    self.__sliceCCharCharacter,
                                    self._sliceEscapeSequence,
                                    self.__sliceUniversalCharacterName,
                                )
                            )

    def __sliceCCharCharacter(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - c-char character."""
        if theBuf[theOfs] in CHAR_SET_MAP['lex.ccon']['c-char']: 
            return 1
        return 0

    def _sliceEscapeSequence(self, theBuf, theOfs):
        """Returns the length of a slice of theCharS that matches the longest integer literal or 0.
        ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - escape-sequence."""
        return self._sliceLongestMatchOfs(
                                    theBuf,
                                    theOfs,
                                    (
                                        self.__sliceSimpleEscapeSequence,
                                        self._sliceOctalEscapeSequence,
                                        self._sliceHexadecimalEscapeSequence,
                                    )
                                )

    def __sliceSimpleEscapeSequence(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - simple-escape-sequence."""
        if theBuf[theOfs] == '\\' \
        and theBuf[theOfs+1] in CHAR_SET_MAP['lex.ccon']['simple-escape-sequence']:
            return 2
        return 0

    def _sliceOctalEscapeSequence(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - octal-escape-sequence.
        octal-escape-sequence:
            \\ octal-digit
            \\ octal-digit octal-digit
            \\ octal-digit octal-digit octal-digit """
        i = theOfs
        s = CHAR_SET_MAP['lex.ppnumber']['octal-digit']
        try:
            if theBuf[i] == '\\' and theBuf[i+1] in s:
                i += 2
                while theBuf[i] in s:
                    i += 1
                    if (i - theOfs) == 4:
                        break
        except IndexError:
            pass
        return i - theOfs

    def _sliceHexadecimalEscapeSequence(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.2 Character literals [lex.ccon] - hexadecimal-escape-sequence.
        hexadecimal-escape-sequence:
            \\x hexadecimal-digit
            hexadecimal-escape-sequence hexadecimal-digit
        """
        i = theOfs
        s = CHAR_SET_MAP['lex.ppnumber']['hexadecimal-digit']
        try:
            if theBuf[i] == '\\' and theBuf[i+1] == 'x' and theBuf[i+2] in s:
                i += 3
                while theBuf[i] in s:
                    i += 1
        except IndexError:
            pass
        return i - theOfs

    #=========================
    # End: Character literals.
    #=========================

    #====================
    # Floating literals.
    #====================
    def _sliceFloatingLiteral(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon].
        floating-literal:
           fractional-constant exponent-part opt floating-suffix opt
           digit-sequence exponent-part floating-suffix opt
        """
        i = self._sliceFloatingLiteralFractionalConstant(theBuf, theOfs)
        if i > 0:
            # Look for: optional + exponent-part opt + floating-suffix opt
            i += self._sliceFloatingLiteralExponentPart(theBuf, theOfs+i)
            i += self._sliceFloatingLiteralFloatingSuffix(theBuf, theOfs+i)
        else:
            # Look for: digit-sequence + exponent-part + floating-suffix opt
            i = self._sliceFloatingLiteralDigitSequence(theBuf, theOfs)
            if i:
                j = self._sliceFloatingLiteralExponentPart(theBuf, theOfs+i)
                if j:
                    i = i + j
                    i += self._sliceFloatingLiteralFloatingSuffix(theBuf, theOfs+i)
                else:
                    # digit-sequence but no exponent-part
                    i = 0
        return i

    def _sliceFloatingLiteralFractionalConstant(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - fractional-constant.
        fractional-constant:
           digit-sequence opt . digit-sequence
           digit-sequence .
        i.e there are three posibilities:
        a: . digit-sequence
        b: digit-sequence .
        c: digit-sequence . digit-sequence
        """
        i = theOfs
        # Fractions
        try:
            if theBuf[i] == '.':
                i += 1
                j = self._sliceFloatingLiteralDigitSequence(theBuf, i)
                i += j
                if j > 0:
                    return i - theOfs
                else:
                    return 0
            else:
                j = self._sliceFloatingLiteralDigitSequence(theBuf, i)
                if j > 0 and theBuf[i+j] == '.':
                    i += j + 1
                    # Look for trailing digits
                    i += self._sliceFloatingLiteralDigitSequence(theBuf, i)
        except IndexError:
            pass
        return i - theOfs
    
    def _sliceFloatingLiteralExponentPart(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - exponent-part."""
        i = theOfs
        try:
            if theBuf[i] in CHAR_SET_MAP['lex.fcon']['exponent_prefix']:
                i += 1
            else:
                return 0
            # Optional
            i += self._sliceFloatingLiteralSign(theBuf, i)
        except IndexError:
            pass
        j = self._sliceFloatingLiteralDigitSequence(theBuf, i)
        if j == 0:
            # Need e/E, optional sign, and at least one digit
            return 0
        return i + j - theOfs

    def _sliceFloatingLiteralSign(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - floating-suffix."""
        try:
            if theBuf[theOfs] in CHAR_SET_MAP['lex.fcon']['sign']:
                return 1
        except IndexError:
            pass
        return 0

    def _sliceFloatingLiteralDigitSequence(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - digit-sequence."""
        i = theOfs
        try:
            while theBuf[i] in CHAR_SET_MAP['lex.ppnumber']['digit']:
                i += 1
        except IndexError:
            pass
        return i - theOfs

    def _sliceFloatingLiteralFloatingSuffix(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.3 Floating literals [lex.fcon] - floating-suffix."""
        try:
            if theBuf[theOfs] in CHAR_SET_MAP['lex.fcon']['floating-suffix']:
                return 1
        except IndexError:
            pass
        return 0

    #=========================
    # End: Floating literals.
    #=========================

    #====================
    # String literals.
    #====================
    def _sliceStringLiteral(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.4 String literals [lex.string]."""
        #string-literal:
        #"s-char-sequence opt "
        #L"s-char-sequence opt "
        # c.f. above, Note: contents optional
        #character-literal:
        #'c-char-sequence'
        #L'c-char-sequence'
        i = theOfs
        try:
            if theBuf[i] == 'L':
                i += 1
            if theBuf[i] == '"':
                i += 1
                j = self._sliceSCharSequence(theBuf, i)
                i += j
                #print 'TRACE: i=%d j=%d slice: "%s"' % (i,j, theBuf[theOfs:i])
                # Has character run, check for closing '"'
                if theBuf[i] == '"':
                    # Good to go
                    i += 1
                else:
                    return 0
            else:
                # 'L' on its own or no opening '"'
                #print 'Bailing out with i=%d "%s"' % (i, theBuf[i])
                return 0
            if i > theOfs:
                assert(self._changeOfTokenTypeIsOk or self._cppTokType is None), '_cppTokType was %s now %s' \
                        % (self._cppTokType, 'string-literal')
                self._cppTokType = 'string-literal'
        except IndexError:
            i = theOfs
        return i - theOfs

    def _sliceSCharSequence(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.4 String literals [lex.string] - s-char-sequence."""
        return self._sliceAccumulateOfs(theBuf, theOfs, self._sliceSChar)

    def _sliceSChar(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.4 String literals [lex.string] - s-char."""
        return self._sliceLongestMatchOfs(
                        theBuf,
                        theOfs,
                        (
                            self._sliceSCharCharacter,
                            self._sliceEscapeSequence,
                            self.__sliceUniversalCharacterName,
                        )
                    )

    def _sliceSCharCharacter(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.4 String literals [lex.string] - s-char character."""
        if theBuf[theOfs] in CHAR_SET_MAP['lex.string']['s-char']:
            return 1
        return 0
    #=========================
    # End: String literals.
    #=========================

    #====================
    # Boolean literals.
    #====================
    def _sliceBoolLiteral(self, theBuf, theOfs):
        """ISO/IEC 14882:1998(E) 2.13.5 String literals [lex.bool]."""
        return CHAR_SET_STR_TREE_MAP['lex.bool']['set'].has(theBuf, theOfs) - theOfs
    #====================
    # Boolean literals.
    #====================

    #==================
    # End: Literals.
    #==================

    #============================================================
    # End: Low level slicers.
    #============================================================

################
# End: Tokeniser
################
