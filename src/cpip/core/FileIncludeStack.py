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

"""This module represents a stack of file includes as used by the PpLexer
"""
__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

import logging
from cpip import ExceptionCpip
from cpip.core import PpTokeniser
from cpip.core import PpTokenCount
from cpip.core import FileIncludeGraph
from cpip.util import CommonPrefix

class ExceptionFileIncludeStack(ExceptionCpip):
    """Exception for FileIncludeStack object."""
    pass

class FileInclude(object):
    """Represents a single TU fragment with a PpTokeniser and a token counter."""
    def __init__(self, theFpo, theDiag):
        """Constructor
        theFpo     - A FilePathOrigin object that identifies the file.
        theDiag    - A CppDiagnostic object to give to the PpTokeniser."""
        self.fileName = theFpo.filePath
        # Create a new PpTokeniser
        self.ppt = PpTokeniser.PpTokeniser(
            theFileObj=theFpo.fileObj,
            theFileId=theFpo.filePath,
            theDiagnostic=theDiag,
        )
        self.tokenCounter = PpTokenCount.PpTokenCount()
    
    def tokenCounterAdd(self, theC):
        """Add a token counter to my token counter (used when a macro is
        declared)."""
        self.tokenCounter += theC

    def tokenCountInc(self, tok, isUnCond, num=1):
        """Increment the token counter."""
        self.tokenCounter.inc(tok, isUnCond, num)

class FileIncludeStack(object):
    """This maintains information about the stack of file includes.
    This holds several stacks (or representations of them):
    self._ppts is a stack of PpTokeniser.PpTokeniser() objects.
    self._figr is a FileIncludeGraph.FileIncludeGraphRoot() for tracking the #include graph.
    self._fns is a stack of file IDs as strings (e.g. the file path).
    self._tcs is a PpTokenCount.PpTokenCountStack() object for counting tokens.
    """
    def __init__(self, theDiagnostic):
        """Constructor, takes a CppDiagnostic object to give to the PpTokeniser."""
        self._diagnostic = theDiagnostic
        # Stack of FileInclude objects
        self._fincS = []
        # Allied to the file stack is the include graph recorder.
        self._figr = FileIncludeGraph.FileIncludeGraphRoot()
            
    @property
    def depth(self):
        """Returns the current include depth as an integer."""
        return len(self._fincS)
    
    @property
    def currentFile(self):
        """Returns the file ID from the top of the stack."""
        if self.depth < 1:
            raise ExceptionFileIncludeStack('FileIncludeStack.currentFile on zero length stack.')
        return self._fincS[-1].fileName
    
    @property
    def fileStack(self):
        """Returns a copy of the stack of file IDs."""
        return [fi.fileName for fi in self._fincS]
    
    @property
    def ppt(self):
        """Returns the PpTokeniser from the top of the stack."""
        if self.depth < 1:
            raise ExceptionFileIncludeStack('FileIncludeStack.ppt on zero length stack.')
        return self._fincS[-1].ppt
    
    @property
    def fileIncludeGraphRoot(self):
        """The FileIncludeGraph.FileIncludeGraphRoot() object."""
        return self._figr
    
    @property
    def fileLineCol(self):
        """Return an instance of FileLineCol from the current physical line column."""
        return self.ppt.fileLineCol

    def finalise(self):
        """Finalisation, may raise an ExceptionFileIncludeStack."""
        if self.depth != 0:
            raise ExceptionFileIncludeStack(
                'FileIncludeStack.finalise(): Non-zero length stack: %s' \
                                                % str(self.fileStack)
            )

    def _printFileList(self, thePref, theL):
        l = CommonPrefix.lenCommonPrefix(theL)
        print(thePref, [f[l+1:] for f in theL])

    def includeStart(self, theFpo, theLineNum, isUncond, condStr, incLogic):
        """Start an #include file.
        theFpo     - A FilePathOrigin object that identifies the file.
        theLineNum - The integer line number of the file that includes (None if Root).
        isUncond   - A boolean that is the conditional compilation state.
        condStr    - A string of the conditional compilation stack.
        incLogic   - A string that describes the find include logic.
        """
        if not theLineNum:
            logging.debug('FileIncludeStack.includeStart(): %s line=Unknown', 
                          theFpo.filePath, 
                      )
        else:
            logging.debug('FileIncludeStack.includeStart(): %s line=%d', 
                          theFpo.filePath, 
                          theLineNum
                      )
#        print 'FileIncludeStack.includeStart(): new file %s included from line=%s' % (theFpo.filePath, str(theLineNum))
        assert(len(self._fincS) == 0 and theLineNum is None or theLineNum == self._fincS[-1].ppt.pLineCol[0])
#        import traceback
#        print ''.join(traceback.format_list(traceback.extract_stack()))
        self._fincS.append(FileInclude(theFpo, self._diagnostic))
        # Now adjust the file graph, these could (but shouldn't!) raise as:
        # a. self._figr.addGraph just appends so can't raise.
        # b. FileIncludeGraph.__init__(...) just copies data so can't raise.
        # c. self._figr.graph() could raise if there is not a graph there but
        #    previous calls should ensure that.
        #    Thus assert(self._figr.numTrees() > 0)
        # d. addBranch can raise a ExceptionFileIncludeGraph if:
        #    0. The branch is zero length.
        #    1. The branch does not match the existing graph (this just
        #       immediately checks the first item on the branch but then
        #       recurses).
        #    2. theLine is a duplicate of an existing line.
        #    3. The branch has missing nodes.
        #
        # NOTE: Test is against 1 as we have appended to self._fincS above.
        if self.depth == 1:
            assert(theLineNum is None)
            # Add a new FileIncludeGraph
            self._figr.addGraph(
                FileIncludeGraph.FileIncludeGraph(theFpo.filePath, True, '', '',)
            )
        else:
            assert(self._figr.numTrees() > 0)
            # Add a branch to the existing FileIncludeGraph
            myFileStack = self.fileStack
#            print(' includeStart(): myFileStack %d:' % theLineNum, [os.path.basename(p)for p in self.fileStack])
#            self._printFileList(' includeStart(): myFileStack %d:' % theLineNum, self.fileStack)
#            print('                        As list:', self.fileStack)
            self._figr.graph.addBranch(
                        myFileStack[:-1],
                        # And subtract 1 as the "#include ...\\n" has been consumed
                        theLineNum-1,
                        myFileStack[-1],
                        isUncond,
                        condStr,
                        incLogic,
                        ) 
        
    def includeFinish(self):
        """End an #include file, returns the file ID that has been finished."""
        if self.depth < 1:
            raise ExceptionFileIncludeStack('FileIncludeStack.includeFinish() on zero length stack.')
#        print('includeFinish(): myFileStack:', [os.path.basename(p)for p in self.fileStack])
        myFileStack = [fi.fileName for fi in self._fincS]
#        self._printFileList('includeFinish(): myFileStack:', myFileStack)
#        import traceback
#        print ''.join(traceback.format_list(traceback.extract_stack()))
#        print
#        print
#        print 'includeFinish(): self._figr\n', self._figr
        logging.debug('FileIncludeStack.includeFinish(): %s', self._fincS[-1].fileName)
        # Can pop so update the token count of the parent
        #print 'TRACE: includeFinish() myFileStack', myFileStack
        myFinc = self._fincS.pop()
        self._figr.graph.retLatestNode(myFileStack).setTokenCounter(myFinc.tokenCounter)
#            try:
#                self._figr.graph.retLatestNode(myFileStack).setTokenCounter(myFi.tokenCounter)
#            except FileIncludeGraph.ExceptionFileIncludeGraph, err:
#                logging.error('FileIncludeStack.incFinish(): failed with "%s"', str(err))
        if self.depth > 0:
            logging.debug('FileIncludeStack.includeFinish(): passing control back to %s', self._fincS[-1].fileName)
        else:
            logging.debug('FileIncludeStack.includeFinish(): passing control back to NONE')
        return myFinc.fileName
    
    #===============================
    # Section: Token counter access.
    #===============================
    def tokenCounter(self):
        """Returns the Token Counter object at the tip of the stack."""
        if self.depth < 1:
            raise ExceptionFileIncludeStack('FileIncludeStack.tokenCounter on zero length stack.')
        return self._fincS[-1].tokenCounter
    
    def tokenCounterAdd(self, theC):
        """Add a token counter to my token counter (used when a macro is
        declared)."""
        if self.depth < 1:
            raise ExceptionFileIncludeStack('FileIncludeStack.tokenCounterAdd() on zero length stack.')
        self._fincS[-1].tokenCounterAdd(theC)
    
    def tokenCountInc(self, tok, isUnCond, num=1):
        """Increment the token counter."""
        self._fincS[-1].tokenCountInc(tok, isUnCond, num)
    #===========================
    # End: Token counter access.
    #===========================

