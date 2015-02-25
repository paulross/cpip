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

"""Treats a list as a generator with an optional additional generator. This is
used for macro replacement for example.
"""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.9.1'
__rights__  = 'Copyright (c) 2008-2014 Paul Ross'

#import os
#import time
#import logging

class ListAsGenerator(object):
    """Class that takes a list and provides a generator on that list. If the
    list is exhausted and call for another object is made then it is pulled of
    the generator (if available).
    
    The attribute ``listIsEmpty`` is True if the immediate list is empty.
    
    Iterating through the result and stopping when the list is exhausted using
    the flag listIsEmpty:
    
    To be clear: when this flag is set, for example if we have a list [0,1,2,3]
    followed by ['A', 'B', 'C'] thus::
    
        myObj = ListAsGenerator(range(3), ListAsGenerator(list('ABC')).next())
    
    And we try to iterate over it with list comprehension::
    
        myGen = myObj.next()
        myResult = [x for x in myGen if not myObj.listIsEmpty]
        
    myResult will be [0, 1,] because when 3 is yielded the flag is False as
    it refers to the _next_ item.
    
    Similarly the list comprehension::
    
        myResult = [x for x in myGen if myObj.listIsEmpty]
    
    Will be [3, 'A', 'B', 'C']
    
    If you want to recover the then this the technique::
    
        myResult = []
        if not myObj.listIsEmpty:
            for aVal in myGen:
                myResult.append(aVal)
                if myObj.listIsEmpty:
                    break
    
    
    Or exclude the list then this the technique::
    
        if not myObj.listIsEmpty:
            for aVal in myGen:
                if myObj.listIsEmpty:
                    break
        myResult = [x for x in myGen]
    
    The rationale for this behaviour is for generating macro replacement tokens
    in that the list contains tokens for re-examination and the last token may
    turn out to be a function like macro that needs the generator to (possibly)
    complete the expansion. Once that last token has been re-examined we do
    not want to consume any more tokens than necessary.
    """
    def __init__(self, theList, theGen=None):
        """Initialise the class with a list of objects to yield and,
        optionally, a generator. If the generator is present it will be used
        as a continuation of the list."""
        self._list = theList
        self._gen = theGen
        self._listIdx = 0

    #def __iter__(self):
    #    return self

    def __next__(self):
        """yield the next value. The attribute listIsEmpty will be set True
        immediately before yielding the last value."""
        #print 'ListGen.next()'
        self._listIdx = 0
        for aVal in self._list:
            #print 'ListGen yields', aVal
            self._listIdx += 1
            r = yield aVal
            if r is not None:
                self._listIdx -= 1
                # Caller has invoked send() and that call also returns the
                # next yield.
                # So we yield None as the 'return' value of send() otherwise
                # send() gets back its argument rather than persisting it to
                # the subsequent next() call.
                yield None
                # Now when the caller invokes next() after send() we yield the
                # value passed in by the caller in the previous send()
                yield r
                # Only one send() between next() calls so we continue
                # with the iteration...
        #print 'ListGen MT'
        # Optional continuation
        if self._gen is not None:
            while 1:
                r = yield next(self._gen)
                # See comments above for the handling of r
                if r is not None:
                    yield None
                    yield r

    # Backward compatibility with Python 2.x
    next = __next__

    @property
    def listIsEmpty(self):
        """True if the next yield would come from the generator, not the list."""
        return self._listIdx >= len(self._list)
