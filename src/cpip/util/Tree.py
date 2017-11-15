#!/usr/bin/env python
# CPIP is a C/C++ Preprocessor implemented in Python.
# Copyright (C) 2008-2017 Paul Ross
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
# Paul Ross: apaulross@gmail.com
"""Represents a simple tree.

Created on 6 Mar 2014

@author: paulross
"""

class Tree(object):
    """Represents a simple tree of objects."""
    def __init__(self, obj):
        """Constructor, takes any object.

        :param obj: Any object, usually a string.
        :type obj: ``object``

        :returns: ``NoneType``
        """
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
        """The latest child to be added, may raise IndexError if no children.

        :returns: :py:class:`cpip.util.Tree.Tree` -- The youngest child."""
        return self._children[-1]
    
    def __len__(self):
        return len(self._children)
    
    def __str__(self):
        return str(self.branches())
    
    def addChild(self, obj):
        """Add a child.

        :param obj: Child.
        :type obj: ``str``

        :returns: ``NoneType``"""
        self._children.append(Tree(obj))
    
    def branches(self):
        """Returns all the possible branches through the tree as a list of lists
        of self._obj.

        :returns: ``list([list([str])])`` -- List of branches."""
        return self._branches(None)
    
    def _branches(self, thisBranch):
        """
        <insert documentation for function>

        :param thisBranch: Current branch, None initially.
        :type thisBranch: ``NoneType, list([str])``

        :returns: ``list([list([str])])`` -- List of branches.
        """
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
        """Constructor."""
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
        """Adds the parent/child to both internal maps.

        :param parent: Parent.
        :type parent: ``str``

        :param child: Child.
        :type child: ``str``

        :returns: ``NoneType``
        """
        self._add(self._mapPc, parent, child)
        self._add(self._mapCp, child, parent)
    
    def _add(self, theMap, k, v):
        """Adds the key/value to the existing map.

        :param theMap: Existing map.
        :type theMap: ``dict({})``

        :param k: Key.
        :type k: ``str``

        :param v: Value.
        :type v: ``str``

        :returns: ``NoneType``"""
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
        """Returns True if the given child has any parents.

        :param child: The child
        :type child: ``str``

        :returns: ``bool`` -- True if the argument is a child is in the map.
        """
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

        Cycles are not reproduced i.e. if ``a -> b`` and ``b -> c`` and ``c -> a`` then::

            treeChildParent('a') # returns ['a', 'c', 'b',]
            treeChildParent('b') # returns ['b', 'a', 'c',]
            treeChildParent('c') # returns ['c', 'b', 'a',]

        :param theObj: The object to create a tree from.
        :type theObj: ``str``

        :returns: :py:class:`cpip.util.Tree.Tree` -- The final tree."""
        if theObj not in self._mapPc:
            raise ValueError('"%s" not in Parent/Child map' % theObj)
        return self._treeFromEither(theObj, self._mapPc)
#         if theObj in self._mapPc:
#             return self._treeFromEither(theObj, self._mapPc)
        
    def treeChildParent(self, theObj):
        """Returns a Tree() object where the links are the relationships
        between child and parent.

        Cycles are not reproduced i.e. if ``a -> b`` and ``b -> c`` and ``c -> a`` then::

            treeChildParent('a') # returns ['a', 'c', 'b',]
            treeChildParent('b') # returns ['b', 'a', 'c',]
            treeChildParent('c') # returns ['c', 'b', 'a',]

        :param theObj: The object to create a tree from.
        :type theObj: ``str``

        :returns: :py:class:`cpip.util.Tree.Tree` -- The final tree."""
        if theObj not in self._mapCp:
            raise ValueError('"%s" not in Child/Parent map' % theObj)
        return self._treeFromEither(theObj, self._mapCp)
        
    def _treeFromEither(self, theObj, theMap):
        """Creates a tree from the object.

        :param theObj: The object to create a tree from.
        :type theObj: ``str``

        :param theMap: The map of str/str.
        :type theMap: ``dict({str : [list([str])]})``

        :returns: :py:class:`cpip.util.Tree.Tree` -- The final tree.
        """
        assert theObj in theMap
        retTree = Tree(theObj)
        myStack = [theObj,]
        self._treeFromMap(theMap, myStack, retTree)
        assert len(myStack) == 1 and myStack[0] == theObj
        return retTree
        
    def _treeFromMap(self, theMap, theStack, theTree):
        """Creates a ``Tree`` from a dict of list of strings.

        :param theMap: The dictionary.
        :type theMap: ``dict({str : [list([str])]})``

        :param theStack: The stack of strings.
        :type theStack: ``list([str])``

        :param theTree: An existing Tree.
        :type theTree: :py:class:`cpip.util.Tree.Tree`

        :returns: ``NoneType``
        """
        if theStack[-1] in theMap:
            for val in theMap[theStack[-1]]:
                if val not in theStack:
                    theStack.append(val)
                    theTree.addChild(val)
                    self._treeFromMap(theMap, theStack, theTree.youngestChild)
                    v = theStack.pop()
                    assert v == val

