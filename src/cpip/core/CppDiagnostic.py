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

"""Describes how a preprocessor class behaves under abnormal conditions."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'


import logging

from cpip import ExceptionCpip

class ExceptionCppDiagnostic(ExceptionCpip):
    """Exception class for representing CppDiagnostic."""
    pass

class ExceptionCppDiagnosticUndefined(ExceptionCppDiagnostic):
    """Exception class for representing undefined behaviour."""
    pass

class ExceptionCppDiagnosticPartialTokenStream(ExceptionCppDiagnostic):
    """Exception class for representing partial remaining tokens."""
    pass

class PreprocessDiagnosticStd(object):
    """Describes how a preprocessor class behaves under abnormal conditions."""
    def __init__(self):
        """Constructor."""
        self._cntrUndefined = 0
        self._cntrImplDefined = 0
        self._cntrError = 0
        self._cntrWarning = 0
        self._cntrUnspecified = 0
        self._cntrPartialTokenStream = 0
        self._isWellFormed = True
        # List of events [(type, message), ...]
        # Note: Debugging/trace events are not accumulated here
        self._eventList = []
    
    def clear(self):
        self._eventList = []
        
    @property
    def isWellFormed(self):
        return self._isWellFormed
    
    @property
    def eventList(self):
        """A list of events in the order that they appear.
        An event is a pair of strings: (type, message)"""
        return self._eventList
    
    def _prepareMsg(self, event, msg, theLoc):
        """Prepares a message.
        event - The event e.g. 'error', if None it is not accumulated
        msg - The main message.
        theLoc - the file locator e.g. FileLocation.FileLineCol.
        If present it must have: (fileId, lineNum colNum) attributes."""
        if theLoc is None:
            myMsg = msg
        else:
            myMsg = '%s at line=%s, col=%s of file "%s"' \
                            % (
                    msg.rstrip(),
                    theLoc.lineNum,
                    theLoc.colNum,
                    theLoc.fileId,
                )
        if event is not None:
            self._eventList.append((event, myMsg))
        return myMsg

    def undefined(self, msg, theLoc=None):
        """Reports when an 'undefined' event happens.
        msg - The main message.
        theLoc - the file locator e.g. FileLocation.FileLineCol.
        If present it must have: (fileId, lineNum colNum) attributes."""
        self._cntrUndefined += 1
        self._isWellFormed = False
        raise ExceptionCppDiagnosticUndefined(
                        self._prepareMsg(
                                         'undefined',
                                         msg,
                                         theLoc
                                         )
                        )

    def partialTokenStream(self, msg, theLoc=None):
        """Reports when an partial token stream exists (e.g. an unclosed comment).
        msg - The main message.
        theLoc - the file locator e.g. FileLocation.FileLineCol.
        If present it must have: (fileId, lineNum colNum) attributes."""
        self._cntrPartialTokenStream += 1
        self._isWellFormed = False
        raise ExceptionCppDiagnosticPartialTokenStream(
                        self._prepareMsg(
                                         'partial token stream',
                                         msg,
                                         theLoc
                                         )
                        )

    def implementationDefined(self, msg, theLoc=None):
        """Reports when an 'implementation defined' event happens.
        msg - The main message.
        theLoc - the file locator e.g. FileLocation.FileLineCol.
        If present it must have: (fileId, lineNum colNum) attributes."""
        self._cntrImplDefined += 1
        logging.warning(
                        self._prepareMsg(
                                         'implementation defined',
                                         msg,
                                         theLoc
                                         )
                        )

    def error(self, msg, theLoc=None):
        """Reports when an error event happens.
        msg - The main message.
        theLoc - the file locator e.g. FileLocation.FileLineCol.
        If present it must have: (fileId, lineNum colNum) attributes."""
        self._cntrError += 1
        logging.error(self._prepareMsg(
                                       'error',
                                       msg, 
                                       theLoc
                                       )
        )

    def warning(self, msg, theLoc=None):
        """Reports when an warning event happens.
        msg - The main message.
        theLoc - the file locator e.g. FileLocation.FileLineCol.
        If present it must have: (fileId, lineNum colNum) attributes."""
        self._cntrWarning += 1
        logging.warning(self._prepareMsg(
                                         'warning',
                                         msg,
                                         theLoc
                                         )
        )
        
    def handleUnclosedComment(self, msg, theLoc=None):
        """Reports when an unclosed comment is seen at EOF.
        msg - The main message.
        theLoc - the file locator e.g. FileLocation.FileLineCol.
        If present it must have: (fileId, lineNum colNum) attributes."""
        self.partialTokenStream(msg, theLoc)

    def unspecified(self, msg, theLoc=None):
        """Reports when unspecified behaviour is happening.
        For example order of evaluation of '#' and '##'.
        msg - The main message.
        theLoc - the file locator e.g. FileLocation.FileLineCol.
        If present it must have: (fileId, lineNum colNum) attributes."""
        self._cntrUnspecified += 1
        logging.info(self._prepareMsg(
                                      'unspecified',
                                      msg,
                                      theLoc
                                      )
        )
    
    @property
    def isDebug(self):
        """Whether a call to debug() will result in any log output."""
        return logging.getLogger().getEffectiveLevel() <= logging.DEBUG

    def debug(self, msg, theLoc=None):
        """Reports a debug message.
        msg - The main message.
        theLoc - the file locator e.g. FileLocation.FileLineCol.
        If present it must have: (fileId, lineNum colNum) attributes."""
        logging.debug(self._prepareMsg(None, msg, theLoc))

class PreprocessDiagnosticKeepGoing(PreprocessDiagnosticStd):
    """Sub-class that does not raise exceptions."""
    def undefined(self, msg, theLoc=None):
        try:
            super(PreprocessDiagnosticKeepGoing, self).undefined(msg, theLoc)
        except ExceptionCppDiagnostic, err:
            self.warning('Undefined behaviour: %s' % str(err), theLoc)

    def partialTokenStream(self, msg, theLoc=None):
        try:
            super(PreprocessDiagnosticKeepGoing, self).partialTokenStream(msg, theLoc)
        except ExceptionCppDiagnostic, err:
            self.warning('Undefined behaviour: %s' % str(err), theLoc)

class PreprocessDiagnosticRaiseOnError(PreprocessDiagnosticStd):
    """Sub-class that raises an exception on a #'error directive.
    TODO: We really should return a value here so that the caller can
    decide if they need to raise an Exception after reporting the error."""
    def error(self, msg, theLoc=None):
        """Reports when an error event happens.
        msg - The main message.
        theLoc - the file locator e.g. FileLocation.FileLineCol.
        If present it must have: (fileId, lineNum colNum) attributes."""
        try:
            super(PreprocessDiagnosticRaiseOnError, self).error(msg, theLoc)
        except ExceptionCppDiagnostic:
            pass
        raise ExceptionCppDiagnostic(self._prepareMsg(
                                                      'error',
                                                      msg,
                                                      theLoc
                                                      )
        )
