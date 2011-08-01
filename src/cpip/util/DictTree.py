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

"""A dictionary that takes a list of hashables as a key and behaves like a tree."""

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__version__ = '0.8.0'
__rights__  = 'Copyright (c) 2008-2011 Paul Ross'

from cpip import ExceptionCpip

class ExceptionDictTree(ExceptionCpip):
    """Exception when handling a DictTree object."""
    pass

class DictTree(object):
    """A dictionary that takes a list of hashables as a key and behaves like a tree"""
    INDENT_STR = '  '
    ITERABLE_TYPE = (None, 'list', 'set')
    # HTML table events
    ROW_OPEN = (None, 0, 0)
    ROW_CLOSE = (None, -1, -1)
    def __init__(self, valIterable=None):
        if valIterable not in self.ITERABLE_TYPE:
            raise ExceptionDictTree('"%s" not in acceptble range: %s' \
                                    % (valIterable, self.ITERABLE_TYPE))
        self._vI = valIterable
        # Otherwise a dictionary
        self._ir = None
        # Otherwise anything
        self._v =None

    def retNewInstance(self):
        return DictTree(valIterable=self._vI)

    def add(self, k, v):
        """Add a key/value. k is a list of hashables."""
        if self._vI not in self.ITERABLE_TYPE:
            raise ExceptionDictTree('"%s" not in acceptble range: %s' \
                                    % (self._vI, self.ITERABLE_TYPE))
        if len(k) == 0:
            if self._vI is None:
                self._v = v
            elif self._vI == 'list':
                if self._v is None:
                    self._v = [v]
                else:
                    self._v.append(v)
            elif self._vI == 'set':
                if self._v is None:
                    self._v = set()
                self._v.add(v)
        else:
            if self._ir is None:
                self._ir = {}
            if not self._ir.has_key(k[0]):
                self._ir[k[0]] = self.retNewInstance()
            self._ir[k[0]].add(k[1:], v)
            
    def remove(self, k, v=None):
        """Remove a key/value. k is a list of hashables."""
        assert(self._vI in self.ITERABLE_TYPE)
        if len(k) == 0:
            if self._vI is None:
                self._v = None
            elif self._vI == 'list':
                if v is None:
                    self._v = None
                else:
                    if self._v is not None:
                        try:
                            self._v.remove(v)
                        except ValueError:#, err:
                            raise ExceptionDictTree('%s not in list %s' % (v, self._v))
                    else:
                        raise ExceptionDictTree('Value of key is None')
            elif self._vI == 'set':
                if v is None:
                    self._v = None
                else:
                    if self._v is not None:
                        try:
                            self._v.remove(v)
                        except KeyError:#, err:
                            raise ExceptionDictTree('%s not in set %s' % (v, self._v))
                    else:
                        raise ExceptionDictTree('Value of key is None')
        elif self._ir is not None:
            if self._ir.has_key(k[0]):
                self._ir[k[0]].remove(k[1:], v)
            else:
                raise ExceptionDictTree('No key: %s' % (k[0]))
        else:
            raise ExceptionDictTree('No key tree: %s' % (k))

    def value(self, k):
        """Value corresponding to a key or None. k is a list of hashables."""
        if len(k) == 0:
            return self._v
        if self._ir is None:
            return None
        try:
            return self._ir[k[0]].value(k[1:])
        except KeyError:
            pass
        return None
    
    def has_key(self, k):
        return self.value(k) is not None

    def values(self):
        """Returns a list of all values."""
        retV = []
        self._values(retV)
        return retV
    
    def _values(self, theVs):
        if self._v is not None:
            theVs.append(self._v)
        if self._ir is not None:
            for k in self._ir.keys():
                self._ir[k]._values(theVs)
                
    def keys(self):
        """Return a list of keys where each key is a list of hashables."""
        retK = []
        kStk = []
        self._keys(retK, kStk)
        assert(len(kStk) == 0)
        return retK
    
    def _keys(self, kS, kStk):
        if self._v is not None:
            kS.append(kStk[:])
        if self._ir is not None:
            for k in self._ir.keys():
                kStk.append(k)
                self._ir[k]._keys(kS, kStk)
                kStk.pop()

    def __len__(self):
        """Returns the number of keys."""
        return len(self.keys())

    def depth(self):
        """Returns the maximum tree depth as an integer."""
        return self._depth(0)

    def _depth(self, theD):
        """Recursively returns the maximum tree depth as an integer."""
        #print 'theDepth', theDepth
        myD = theD
        if self._ir is not None:
            for k in self._ir.keys():
                myD = max(myD, self._ir[k]._depth(theD+1))
        return myD

    def indentedStr(self):
        retL = []
        kStk = []
        self._indentedStr(retL, kStk)
        assert(len(kStk) == 0)
        return '\n'.join(retL)
        
    def _indentedStr(self, theL, kStk):
        if self._v is not None:
            theL.append('%s%s' % (self.INDENT_STR*len(kStk), self._v))
        if self._ir is not None:
            kS = self._ir.keys()
            kS.sort()
            for k in kS:
                theL.append('%s%s' % (self.INDENT_STR*len(kStk), k))
                kStk.append(k)
                self._ir[k]._indentedStr(theL, kStk)
                kStk.pop()
                
                
class DictTreeHtmlTable(DictTree):
    """A sub-class of DictTree that helps writing HTML row/col span tables
    Suppose we have a tree like this:

                            |- AAA
                            |
                    |- AA --|- AAB
                    |       |
                    |       |- AAC
            |- A ---|
    Root ---|       |- AB
            |       |
            |       |- AC ---- ACA
            |
            |- B
            |
            |- C ---- CA ---- CAA

    And we want to represent the tree like this when laid out as
    an HTML table:
    |-----------------------|
    | A     | AA    | AAA   |
    |       |       |-------|
    |       |       | AAB   |
    |       |       |-------|
    |       |       | AAC   |
    |       |---------------|
    |       | AB            |
    |       |---------------|
    |       | AC    | ACA   |
    |-----------------------|
    | B                     |
    |-----------------------|
    | C     | CA    | CAA   |
    |-----------------------|

    In this example the tree is loaded branch by branch thus:
    myTree = DictTreeHtmlTable()
    myTree.add(('A', 'AA', 'AAA'), None)
    myTree.add(('A', 'AA', 'AAB'), None)
    myTree.add(('A', 'AA', 'AAC'), None)
    myTree.add(('A', 'AB',), None)
    myTree.add(('A', 'AC', 'ACA'), None)
    myTree.add(('B',), None)
    myTree.add(('C', 'CA', 'CAA'), None)

    The HTML code generator can be used like this:
    # Write: <table border="2" width="100%">
    for anEvent in myTree.genColRowEvents():
        if anEvent == myTree.ROW_OPEN:
            # Write out the '<tr>' element
        elif anEvent == myTree.ROW_CLOSE:
            # Write out the '</tr>' element
        else:
            k, v, r, c = anEvent
            # Write '<td rowspan="%d" colspan="%d">%s</td>' % (r, c, v)
    # Write: </table>
    
    And the HTML will look like this:
    <table border="2" width="100%">
        <tr valign="top">
            <td rowspan="5">A</td>
            <td rowspan="3">AA</td>
            <td>AAA</td>
        </tr>
        <tr valign="top">
            <td>AAB</td>
        </tr>
        <tr valign="top">
            <td>AAC</td>
        </tr>
        <tr valign="top">
            <td colspan="2">AB</td>
        </tr>
        <tr valign="top">
            <td>AC</td>
            <td>ACA</td>
        </tr>
        <tr valign="top">
            <td colspan="3">B</td>
        </tr>
        <tr valign="top">
            <td>C</td>
            <td>CA</td>
            <td>CAA</td>
        </tr>
    </table>"""
    # HTML table events
    ROW_OPEN = (None, 0, 0)
    ROW_CLOSE = (None, -1, -1)
    def __init__(self, *args):
        super(DictTreeHtmlTable, self).__init__(*args)
        self._colSpan = self._rowSpan = 1

    def retNewInstance(self):
        return DictTreeHtmlTable(self._vI)

    @property
    def colSpan(self):
        return self._colSpan

    @property
    def rowSpan(self):
        return self._rowSpan

    def setColRowSpan(self):
        """Top level call that sets colspan and rowspan attributes."""
        self._setRowSpan()
        maxDepth = self.depth()
        self._setColSpan(maxDepth, -1)

    def _setColSpan(self, mD, d):
        """"""
        if self._ir is None:
            # Leaf node
            self._colSpan = mD- d
        else:
            # Non-leaf
            self._colSpan = 1
            for aTree in self._ir.values():
                aTree._setColSpan(mD, d+1)
    
    def _setRowSpan(self):
        """Sets self._rowSpan recursively."""
        retVal = 1
        if self._ir is None:
            self._rowSpan = 1
        else:
            # Non-leaf node
            self._rowSpan = 0
            for aTree in self._ir.values():
                self._rowSpan += aTree._setRowSpan()
        return self._rowSpan

    def genColRowEvents(self):
        """Returns a set of events that are quadruples.
        (key_branch, value, rowspan_int, colspan_int)
        The branch is a list of keys the from the branch of the tree.
        The rowspan and colspan are both integers.
        At the start of the a <tr> there will be a ROW_OPEN
        and at row end (</tr> a ROW_CLOSE will be yielded
        """
        self.setColRowSpan()
        hasYielded = False
        for anEvent in self._genColRowEvents([]):
            if not hasYielded:
                yield self.ROW_OPEN
                hasYielded = True
            yield anEvent
        if hasYielded:
            yield self.ROW_CLOSE
    
    def _genColRowEvents(self, keyBranch):
        """Returns a set of events that are a tuple of quadruples.
        (key_branch, value, rowspan_integer, colspan_integer)
        For example: (['a', 'b'], 'c', 3, 7)
        At the start of the a <tr> there will be a ROW_OPEN
        and at row end (</tr> a ROW_CLOSE will be yielded
        """
        if self._ir is not None:
            # Non-leaf
            keyS = self._ir.keys()
            keyS.sort()
            for i, k in enumerate(keyS):
                keyBranch.append(k)
                if i != 0:
                    yield self.ROW_CLOSE
                    yield self.ROW_OPEN
                yield (keyBranch[:], self._ir[k]._v, self._ir[k].rowSpan, self._ir[k].colSpan)
                # Recurse
                for anEvent in self._ir[k]._genColRowEvents(keyBranch):
                    yield anEvent
                keyBranch.pop()

    def walkColRowSpan(self):
        dMax = self.depth()
        #print 'dMax=%d' % dMax
        return self._walkColRowSpan(0, dMax)

    def _walkColRowSpan(self, d, dMax):
        #print '%srow=%d col=%d "%s"' \
        #    % ('  '*d, self.rowSpan(), dMax-self.colSpan(), self._v)
        retVal = ""
        if self._ir is not None:
            kS = self._ir.keys()
            kS.sort()
            for k in kS:
                retVal += '%s%s r=%d, c=%d\n' % ('  '*d, k, self._ir[k].rowSpan, self._ir[k].colSpan)
                retVal += self._ir[k]._walkColRowSpan(d+1, dMax)
        return retVal
                

        