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
"""Represents a simple tree.

Created on 6 Mar 2014

@author: paulross
"""

class Tree(object):
    """Represents a simple tree of objects."""
    def __init__(self, obj):
        """Constructor, takes any object."""
        self._obj = obj
        self._children = []
    
    @property
    def obj(self):
        return self._obj
    
    @property
    def children(self):
        return self._children
    
    @property
    def youngestChild(self):
        """The latest child to be added, may raise IndexError if no children."""
        return self._children[-1]
    
    def __len__(self):
        return len(self._children)
    
    def __str__(self):
        return str(self.branches())
    
    def addChild(self, obj):
        self._children.append(Tree(obj))
    
    def branches(self):
        """Returns all the possible branches through the tree as a list of lists
        of self._obj."""
        return self._branches(None)
    
    def _branches(self, thisBranch):
        if thisBranch is None:
            thisBranch = []
        thisBranch.append(self._obj)
        myBranches = [thisBranch[:]]
        for aChild in self._children:
            myBranches.extend(aChild._branches(thisBranch))
        thisBranch.pop()
        return myBranches

class DuplexAdjacencyList(object):
    """Represents a set of parent/child relationships (and their inverse) as
    Adjacency Lists."""
    def __init__(self):
        # Will be map of {parent : [child, ...], ...}
        self._mapPc = {}
        # Will be map of {child : [parent, ...], ...}
        self._mapCp = {}
    
    def __str__(self):
        rList = ['Parent -> Children:']
        for p in sorted(self._mapPc.keys()):
            rList.append('%s -> %s' % (p, self._mapPc[p]))
        return '\n'.join(rList)
        
    def add(self, parent, child):
        self._add(self._mapPc, parent, child)
        self._add(self._mapCp, child, parent)
    
    def _add(self, theMap, k, v):
        try:
            theMap[k].append(v)
        except KeyError:
            theMap[k] = [v,]

    @property
    def allParents(self):
        """Returns an unordered list of objects that have at least one child."""
        return self._mapPc.keys()
    
    @property
    def allChildren(self):
        """Returns an unordered list of objects that have at least one parent."""
        return self._mapCp.keys()
    
    def hasParent(self, parent):
        """Returns True if the given parent has any children."""
        return parent in self._mapPc
    
    def hasChild(self, child):
        """Returns True if the given child has any parents."""
        return child in self._mapCp
    
    def children(self, parent):
        """Returns all immediate children of a given parent."""
        return self._mapPc[parent][:]
    
    def parents(self, child):
        """Returns all immediate parents of a given child."""
        return self._mapCp[child][:]
    
    def treeParentChild(self, theObj):
        """Returns a Tree() object where the links are the relationships
        between parent and child.
        Cycles are not reproduced i.e. if a -> b and b -> c and c-> a then
        treeParentChild('a') returns ['a', 'b', 'c',]
        treeParentChild('b') returns ['b', 'c', 'a',]
        treeParentChild('c') returns ['c', 'a', 'c',]
        """
        if theObj not in self._mapPc:
            raise ValueError('"%s" not in Parent/Child map' % theObj)
        return self._treeFromEither(theObj, self._mapPc)
#         if theObj in self._mapPc:
#             return self._treeFromEither(theObj, self._mapPc)
        
    def treeChildParent(self, theObj):
        """Returns a Tree() object where the links are the relationships
        between child and parent.
        Cycles are not reproduced i.e. if a -> b and b -> c and c-> a then
        treeChildParent('a') returns ['a', 'c', 'b',]
        treeChildParent('b') returns ['b', 'a', 'c',]
        treeChildParent('c') returns ['c', 'b', 'a',]
        """
        if theObj not in self._mapCp:
            raise ValueError('"%s" not in Child/Parent map' % theObj)
        return self._treeFromEither(theObj, self._mapCp)
        
    def _treeFromEither(self, theObj, theMap):
        assert theObj in theMap
        retTree = Tree(theObj)
        myStack = [theObj,]
        self._treeFromMap(theMap, myStack, retTree)
        assert len(myStack) == 1 and myStack[0] == theObj
        return retTree
        
    def _treeFromMap(self, theMap, theStack, theTree):
        if theStack[-1] in theMap:
            for val in theMap[theStack[-1]]:
                if val not in theStack:
                    theStack.append(val)
                    theTree.addChild(val)
                    self._treeFromMap(theMap, theStack, theTree.youngestChild)
                    v = theStack.pop()
                    assert v == val

