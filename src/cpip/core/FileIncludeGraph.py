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

"""Captures the #include graph of a preprocessed file."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import collections
import re
import sys

from cpip import ExceptionCpip

class ExceptionFileIncludeGraph(ExceptionCpip):
    """Simple specialisation of an exception class for the
    FileincludeGraph classes."""
    pass

class ExceptionFileIncludeGraphRoot(ExceptionFileIncludeGraph):
    """Exception for issues for dummy file ID's."""
    pass

class ExceptionFileIncludeGraphTokenCounter(ExceptionFileIncludeGraph):
    """Exception for issues for token counters."""
    pass

#: The file ID for a 'dummy' file. This is used as the artificial root
#: node for all the pre-includes and the ITU
DUMMY_FILE_NAME = None
#: In the graph the line number is ignored for dummy roots and this one
#: used instead
DUMMY_FILE_LINENUM = -1
# Indentation of file include graph as text
DEFAULT_TEXT_INDENT = 2


class FileIncludeGraphRoot(object):
    """Root class of the file include graph. This is used when there is a
    virtual or dummy root. It contains a list of FileIncludeGraph objects.
    In this way it can represent the list of graphs that would result from a
    list of pre-includes followed by the ITU itself.
    
    In practice this is used by the PpLexer for this purpose where the
    dummy root is represented by None."""
    def __init__(self):
        """Constructor."""
        # List of [class FileIncludeGraph, ...]
        self._incGraphS = []
        
    def __str__(self):
        return '\n'.join([str(fig) for fig in self._incGraphS])
        
    def addGraph(self, theGraph):
        """Add a FileIncludeGraph object."""
        self._incGraphS.append(theGraph)
        
    @property
    def graph(self):
        """The latest FileIncludeGraph object I have.
        Will raise a ExceptionFileIncludeGraphRoot if nothing there."""
        if len(self._incGraphS) < 1:
            raise ExceptionFileIncludeGraphRoot('graph on zero length list.')
        return self._incGraphS[-1]

    def numTrees(self):
        """Returns the number of FileIncludeGraph objects."""
        return len(self._incGraphS)

    def acceptVisitor(self, visitor):
        """Hierarchical visitor pattern. This accepts a visitor object and calls
        visitor.visitGraph(self, depth, line) on that object where depth is the
        current depth in the graph as an integer and line the line that is a
        non-monotonic sibling node ordinal."""
        for aGraph in self._incGraphS:
            aGraph.acceptVisitor(visitor, 1, -1)

    def dumpGraph(self, theS=sys.stdout):
        """Dump the node for debug/trace."""
        for c in self._incGraphS:
            c.dumpGraph(theS, theI='')

class FileIncludeGraph(object):
    """Recursive class that holds a graph of include files and and line numbers
    of the file that included them.
    
    This class builds up a graph (actually a tree) of file includes. The
    insertion order is significant in that it is expected to be the order
    experienced by a translation unit processor.
    ``addBranch()`` is the way to add to the data structure.
    
    theFile - a file ID (e.g. a path)

    theState - a boolean conditional compilation state.

    theCondition - a conditional compilation condition string e.g. "a >= b+2".

    thelogic - a string explanation of how that the file was found.

    If theLogic is taken from an IncludeHandler as a list of items.
    e.g. ['<foo.h>, CP=None, sys=None, usr=include/foo.h']
    Each string after item[0] is of the form: key=value
    Where:

    key is a key in self.INCLUDE_ORIGIN_CODES
    = is the '=' character.
    value is the result, or 'None' if not found.

    [0] is the invocation
    [-1] is the final resolution.

    The intermediate ones are various tries in order.
    So ['<foo.h>', 'CP=None', 'sys=None', 'usr=include/foo.h'] would mean:

    0. '<foo.h>' the include directive was: ``#include <foo.h>``
    1. 'CP=None' the Current place was searched and nothing found.
    2. 'sys=None' the system include(s) were searched and nothing found.
    3. 'usr=include/foo.h' the user include(s) were searched and include/foo.h was found.
    
    This class does not distinguish between conditional compilation states
    that are True or False. Nor does this class evaluate theCondition in
    any way, it is merely stored for representation.
    """
    LINE_SEPERATOR = '#'
    RE_SPLIT_LINENUM = re.compile(r'^(.+?)%s([-+]?\d+)$' % LINE_SEPERATOR)
    def __init__(self, theFile, theState, theCondition, theLogic):
        """Constructor that takes:
        theFile - a file ID (e.g. a path)
        theState - a boolean conditional compilation state.
        theCondition - a conditional compilation condition string e.g. "a >= b+2".
        thelogic - a string explanation of how that the file was found.
        If theLogic is taken from an IncludeHandler as a list of items.
        e.g. ['<foo.h>, CP=None, sys=None, usr=include/foo.h']
        Each string after item[0] is of the form: key=value
        Where:
        key is a key in self.INCLUDE_ORIGIN_CODES
        = is the '=' character.
        value is the result, or 'None' if not found.
        [0] is the invocation
        [-1] is the final resolution.
        The intermediate ones are various tries in order.
        So ['<foo.h>', 'CP=None', 'sys=None', 'usr=include/foo.h'] would mean:
        [0]: '<foo.h>' the include directive was: #include <foo.h>
        [1]: 'CP=None' the Current place was searched and nothing found.
        [2]: 'sys=None' the system include(s) were searched and nothing found.
        [3]: 'usr=include/foo.h' the user include(s) were searched and include/foo.h was found.
        
        This class does not distinguish between conditional compilation states
        that are True or False. Nor does this class evaluate theCondition in
        any way, it is merely stored for representation."""
        self._fileName = theFile
        self._condCompState = theState
        self._condComp = theCondition
        self._findLogic = theLogic
        # Somewhat hacky support for Python 2.x. Otherwise the __str__ appears as
        #   sys/inc/spam.h [15, 10]:  True "" "[u\'<inc/spam.h>\', u\'CP=usr\']"
        # rather than:
        #   sys/inc/spam.h [15, 10]:  True "" "[\'<inc/spam.h>\', \'CP=usr\']"
        if isinstance(self._findLogic, list) and len(self._findLogic) > 0 \
        and sys.version_info.major == 2:
            for i in range(len(self._findLogic)):
                self._findLogic[i] = str(self._findLogic[i])
        # Recursive map of {line : class FileIncludeGraph, ...}
        # line is an integer type.
        self._graph = {}
        # A PpTokenCount object inserted by caller after the file has
        # been processed
        # This is set by the PpLexer at the end of the translation unit.
        self._tokCntr = None

    #===========================================================================
    # Section: Attribute getters and setters
    #===========================================================================
    @property
    def numTokens(self):
        """The total number of tokens seen by the PpLexer.
        Returns None if not initialised.
        Note: This is the number of tokens for this file only, it does not
        include the tokens that this file might include."""
        if self._tokCntr is not None:
            return self._tokCntr.totalAll

    @property
    def numTokensSig(self):
        """The number of significant tokens seen by the PpLexer. A significant
        token is a non-whitespace, non-conditionally compiled token.
        Returns None if not initialised.
        
        .. note::
            
            This is the number of tokens for this file only, it does not
            include the tokens that this file might include.
        """
        if self._tokCntr is not None:
            return self._tokCntr.tokenCountNonWs(False)
        
    @property
    def numTokensIncChildren(self):
        """The total number of tokens seen by the PpLexer including tokens
        from files included by this one. Returns None if not initialised.
        
        May raise ExceptionFileIncludeGraphTokenCounter is the token counters
        have been loaded inconsistently (i.e. the children have not been
        loaded)."""
        if self._tokCntr is not None:
            retToks = self.numTokens
            for aG in self._graph.values():
                myChildTokCount = aG.numTokensIncChildren
                if myChildTokCount is None:
                    raise ExceptionFileIncludeGraphTokenCounter(
                        'I have a token count but my child, %s, does not' % aG
                        )
                else:
                    retToks += myChildTokCount
            return retToks

    @property
    def numTokensSigIncChildren(self):
        """The number of significant tokens seen by the PpLexer including tokens
        from files included by this one. A significant
        token is a non-whitespace, non-conditionally compiled token.
        Returns None if not initialised.
        
        May raise ExceptionFileIncludeGraphTokenCounter is the token counters
        have been loaded inconsistently (i.e. the children have not been
        loaded)."""
        if self._tokCntr is not None:
            retToks = self.numTokensSig
            for aG in self._graph.values():
                myChildTokCount = aG.numTokensSigIncChildren
                if myChildTokCount is None:
                    raise ExceptionFileIncludeGraphTokenCounter(
                        'I have a token count but my child, %s, does not' % aG
                        )
                else:
                    retToks += myChildTokCount
            return retToks
        
    @property
    def fileName(self):
        """Returns the current file name."""
        return self._fileName

    @property
    def condCompState(self):
        """Returns the recorded conditional compilation state as a boolean."""
        return self._condCompState

    @property
    def condComp(self):
        """Returns the condition, as a string, under which this file was
        included e.g. ``"(a > b) && (1 > 0)"``."""
        return self._condComp
    
    @property
    def findLogic(self):
        """Returns the findLogic string passed in in the constructor."""
        return self._findLogic
    
    @property
    def tokenCounter(self):
        """Gets the token counter for this node, a PpTokenCount object."""
        return self._tokCntr

    def setTokenCounter(self, theTokCounter):
        """Sets the token counter for this node which is a PpTokenCount object.
        The PpLexer sets this as the token count for this file only. This
        files #includes are a separate token counter."""
        if self._tokCntr is not None:
            raise ExceptionFileIncludeGraph(
                'Calling setTokenCounter() when token counter already set.'
            )
        self._tokCntr = theTokCounter

    #===========================================================================
    # End: Attribute getters and setters
    #===========================================================================

    #===========================================================================
    # Section: Child node access
    #===========================================================================
    def genChildNodes(self):
        """Yields each child node as a FileIncludeGraph object."""
        for aLine in sorted(self._graph.keys()):
            yield self._graph[aLine]
    #===========================================================================
    # End: Child node access
    #===========================================================================

    #===========================================================================
    # Section: Branch addition and access 
    #===========================================================================
    def addBranch(self, theFileS, theLine, theIncFile, theState, theCondition, theLogic):
        """Adds a branch to the graph.
        
        theFileS is a list of files that form the branch.
        
        theLine is an integer value of the line number of the #include
        statement of the last named file in theFileS.
        
        theIncFile is the file that is included.
        
        theState is a boolean that describes the conditional compilation state.

        theCondition is the conditional compilation test e.g. '1>0'

        theLogic is a string representing how the branch was obtained.
        
        May raise ExceptionFileIncludeGraph if:

        0. The branch is zero length.
        
        1. The branch does not match the existing graph (this function just immediately
           checks the first item on the branch but the others are done recursively).
        
        2. theLine is a duplicate of an existing line.
        
        3. The branch has missing nodes.
        """
        if len(theFileS) == 0:
            # Case 0. above.
            raise ExceptionFileIncludeGraph('FileIncludeGraph.addBranch() with empty branch.')
        if theFileS[0] != self._fileName:
            # Case 1. above.
            raise ExceptionFileIncludeGraph('FileIncludeGraph.addBranch() was "%s", now "%s".' \
                                        % (self._fileName, theFileS[0]))
        if len(theFileS) == 1:
            # Base case
            if theLine in self._graph:
                # Case 2. above.
                raise ExceptionFileIncludeGraph('FileIncludeGraph.addBranch() dupe line %d in "%s".' \
                                            % (theLine, self._fileName))
            else:
                assert(len(self._graph) == 0 or theLine > max(self._graph.keys())), \
                    'File=%s line=%d maxLine=%d' % (theIncFile, theLine, max(self._graph.keys()))
                self._graph[theLine] = FileIncludeGraph(theIncFile,
                                                        theState,
                                                        theCondition,
                                                        theLogic)
        else:
            # Recursive case
            if len(self._graph) == 0:
                # Case 3. above. an empty graph
                raise ExceptionFileIncludeGraph('FileIncludeGraph.addBranch() "%s" has no includes.' \
                                            % (self._fileName))
            myLineNum = max(self._graph.keys())
            # The #include line of current file is the last one
            self._graph[myLineNum].addBranch(
                                           theFileS[1:],
                                           theLine,
                                           theIncFile,
                                           theState,
                                           theCondition,
                                           theLogic
                                           )

    def retBranches(self):
        """Returns a list of lists of the branches with '#' then the line number."""
        retList = []
        self._getBranches(retList, [])
        return retList

    def _retFileLine(self, theLine):
        """Returns '#d' appended to the filename.""" 
        return '%s%s%d' % (self.fileName, self.LINE_SEPERATOR, theLine)
    
    def _splitFileLine(self, theStr):
        """Splits a file name and line number, the latter is returned
        as an integer or None if no match."""
        mtch = self.RE_SPLIT_LINENUM.match(theStr)
        if mtch is not None:
            return mtch.group(1), int(mtch.group(2))
        return theStr, None
    
    def _getBranches(self, theBrancheS, aBranch):
        """Recursive call to the tree, adds each unique branch in full."""
        aBranch.append(self._fileName)
        theBrancheS.append(aBranch[:])
        aBranch.pop()
        for aLine in sorted(self._graph.keys()):
            aBranch.append(self._retFileLine(aLine))
            self._graph[aLine]._getBranches(theBrancheS, aBranch)
            aBranch.pop()
    
    def retLatestLeaf(self):
        """Returns the last inserted leaf, a FileIncludeGraph object."""
        if len(self._graph) == 0:
            return self
        else:
            return self._graph[max(self._graph.keys())].retLatestLeaf()
        
    def retLatestNode(self, theBranch):
        """Returns the last inserted node, a FileIncludeGraph object
        on the supplied branch.
        
        This is generally used during dynamic construction by a caller
        that understands the state of the file include branch."""
        if len(theBranch) == 0:
            raise ExceptionFileIncludeGraph('retLatestNode() on empty branch.')
        if theBranch[0] != self.fileName:
            raise ExceptionFileIncludeGraph('retLatestNode() requested leaf node %s does not match current node %s' \
                                            % (theBranch, self.fileName))
        if len(theBranch) == 1:
            return self
        else:
            return self._graph[max(self._graph.keys())].retLatestNode(theBranch[1:])
        
    def retLatestBranch(self):
        """Returns the branch to the last inserted leaf as a list of
        branch strings."""
        branchList = []
        self._retLatestBranch(branchList)
        return branchList
        
    def _retLatestBranch(self, theList):
        """Recursive call that returns the branch to the last inserted leaf.
        theList is modified in-place."""
        if len(self._graph) > 0:
            lastLine = max(self._graph.keys())
            theList.append(self._retFileLine(lastLine))
            self._graph[lastLine]._retLatestBranch(theList)
        else:
            theList.append(self.fileName)
            
    def retLatestBranchPairs(self):
        """Returns the branch to the last inserted leaf as a list of
        pairs (filename, integer_line)."""
        return [self._splitFileLine(x) for x in self.retLatestBranch()]
    
    def retLatestBranchDepth(self):
        """Walks the graph and returns an integer that is
        the depth of the latest branch."""
        return self._retLatestBranchDepth(0)
        
    def _retLatestBranchDepth(self, i):
        """Recursive call that returns an integer that is the depth of the
        latest branch."""
        if len(self._graph) > 0:
            return self._graph[max(self._graph.keys())]._retLatestBranchDepth(i+1)
        return i+1
    #===========================================================================
    # End: Branch addition and access 
    #===========================================================================

    #===========================================================================
    # Section: Representation and plotting
    #===========================================================================    
    def __str__(self):
        return self._retString(theIndent=0)
        
    def _retString(self, theIndent):
        """Returns an indented string recursively."""
        retList = []
        retList.append('%s%s [%s, %s]: %5s "%s" "%s"' \
                       % (
                          ' ' * theIndent,
                          self.fileName,
                          self.numTokens,
                          self.numTokensSig,
                          self.condCompState,
                          self.condComp,
                          self.findLogic,
                          )
                       )
        # NOTE: This use of fileName often contains '\\' characters on windows
        # These characters are specifically excluded from #include statements
        # and are thus misleading. Perhaps ee should normalise them to '/' e.g.
        # 000001: #include "usr/spam.h"
        for aLineNum in sorted(self._graph.keys()):
            retList.append('%s%06d: #include %s' \
                            % (
                               ' ' * theIndent,
                               aLineNum,
                               self._graph[aLineNum].fileName,
                               )
                            )
            retList.append(self._graph[aLineNum]._retString(theIndent+DEFAULT_TEXT_INDENT))
        return '\n'.join(retList)
    
    def dumpGraph(self, theS=sys.stdout, theI=''):
        """Writes out the graph to a stream."""
        theS.write('%s%s\n' % (theI, self.fileName))
        myI = theI + '  '
        for l in sorted(self._graph.keys()):
            theS.write('%s%06d:' % (myI, l))
            self._graph[l].dumpGraph(theS, myI)
                       
    #===========================================================================
    # End: Representation and plotting
    #===========================================================================    

    def acceptVisitor(self, visitor, depth, line):
        """Hierarchical visitor pattern. This accepts a visitor object and calls
        visitor.visitGraph(self, depth, line) on that object where depth is the
        current depth in the graph as an integer and line the line that is a
        non-monotonic sibling node ordinal."""
        visitor.visitGraph(self, depth, line)
        for l in sorted(self._graph.keys()):
            self._graph[l].acceptVisitor(visitor, depth+1, l)

###########################
# Section: Visitor support.
###########################
class FigVisitorBase(object):
    """Base class for visitors, see FigVisitorTreeNodeBase for base class for
    tree visitors."""
    def visitGraph(self, theFigNode, theDepth, theLine): 
        """Hierarchical visitor pattern. This is given a FileIncludeGraph as a
        graph node. theDepth is the current depth in the graph as an integer,
        theLine the line that is a non-monotonic sibling node ordinal."""
        raise NotImplementedError()

class FigVisitorTreeNodeBase(object):
    """Base class for nodes created by a tree visitor. See FigVisitorBase for
    the base class for non-tree visitors."""
    def __init__(self, theLineNum):
        self._lineNum = theLineNum
        self._children = []
    
    @property
    def lineNum(self):
        """The line number of the parent file that included me."""
        return self._lineNum
        
    def addChild(self, theObj):
        """Add the object as a child."""
        self._children.append(theObj)
        
    def finalise(self):
        """This will be called on finalisation. This is an opportunity
        for the root (None) not to accumulate properties from its immediate
        children for example.
        For depth first finalisation the child class should call finalise
        on each child first as this function does."""
        for aChild in self._children:
            aChild.finalise()
    
class FigVisitorTree(object):
    """This visitor can visit a graph of FileIncludeGraphRoot and
    FileIncludeGraph that recreates a tree of Node(s) the type of which are
    supplied by the user. Each node instance will be constructed with either an
    instance of a FileIncludeGraphRoot or FileIncludeGraph or, in the case of a
    pseudo root node then None."""
    def __init__(self, theNodeClass):
        self._nodeClass = theNodeClass
        self._stk = [self._nodeClass(None, -1)]
        
    @property
    def depth(self):
        """Returns the current depth in this graph representation. Changes to
        this determine if the node is a child, sibling or ancestor."""
        return len(self._stk) - 1
    
    def tree(self):
        """Returns the top level node object as the only copy.
        This also finalises the tree."""
        while len(self._stk) > 1:
            self._addAncestor()
        assert(self.depth == 0), 'self.depth = %d' % self.depth 
        retVal = self._stk.pop()
        retVal.finalise()
        # Eliminate tree
        self._stk = [self._nodeClass(None, -1)]
        return retVal
    
    def _addChild(self, theNode, theLine):
        self._stk.append(self._nodeClass(theNode, theLine))
        
    def _addAncestor(self):
        c = self._stk.pop()
        self._stk[-1].addChild(c)
    
    def _addSibling(self, theNode, theLine):
        if len(self._stk) > 1:
            self._addAncestor()
            self._addChild(theNode, theLine)
        else:
            self._stk[-1].addChild(self._nodeClass(theNode, theLine))
    
    def visitGraph(self, theFigNode, depth, line):
        """Visit the give node."""
        if self.depth < depth:
            assert((depth - self.depth) == 1)
            self._addChild(theFigNode, line)
        else:# i.e. self.depth >= depth:
            # Unwind children
            while self.depth > depth:
                self._addAncestor()
            # Now treat as sibling
            self._addSibling(theFigNode, line)
        assert(self.depth == depth)

class FigVisitorFileSet(FigVisitorBase):
    """Simple visitor that just collects the set of file IDs in the
    include graph and a count of how often they are seen."""
    def __init__(self):
        super(FigVisitorFileSet, self).__init__()
        self._fileNameMap = collections.defaultdict(int)
        
    def visitGraph(self, theFigNode, theDepth, theLine): 
        """Hierarchical visitor pattern. This is given a FileIncludeGraph as a
        graph node. theDepth is the current depth in the graph as an integer,
        theLine the line that is a non-monotonic sibling node ordinal."""
        self._fileNameMap[theFigNode.fileName] += 1
        
    @property
    def fileNameSet(self):
        """The set of file names seen."""
        return set(self._fileNameMap)
    
    @property
    def fileNameMap(self):
        """Dictionary of number of times each file is seen: {file : count, ...}."""
        return self._fileNameMap

#######################
# End: Visitor support.
#######################
