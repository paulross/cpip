.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

.. FileIncludeGraph Tutorial

.. _cpip.tutorial.FileIncludeGraph:

*************************
FileIncludeGraph Tutorial
*************************

The PpLexer module collects the file *include graph*. This tutorial shows you how to use it for you own ends.

Creating a FileIncludeGraph
==============================

A ``FileIncludeGraph`` object is one of the artifacts produced by a ``PpLexer``
[see the tutorial here: :ref:`cpip.tutorial.PpLexer`].

Once the ``PpLexer`` has processed the Translation Unit it has and attribute ``fileIncludeGraphRoot``
which is an instance of the class ``FileIncludeGraph.FileIncludeGraphRoot``.

Here is the code to create a file include graph:

.. literalinclude:: demo/cpip_18.py
    :language: python
    :linenos:

Invoking this code thus (in the manner of the :ref:`cpip.tutorial.PpLexer`):

``$ python docs/doc_src/tutorial/demo/cpip_18.py docs/doc_src/tutorial/demo/proj/src/main.c``

Gives this output:

.. code-block:: console

    Processing: docs/doc_src/tutorial/demo/proj/src/main.c
    <cpip.core.FileIncludeGraph.FileIncludeGraphRoot object at 0x10ceb9be0>

FileIncludeGraph Structure
==============================

The structure is a tree with each node being an included file, the root being the *Initial Translation Unit*
i.e. the file being pre-processed. Source code order is 'left-to-right' and depth is the degree of ``#include``
statements.

The class ``FileIncludeGraph.FileIncludeGraphRoot`` has a fairly rich interface, reference documentation for the
module is here: :ref:`cpip.ref.FileIncludeGraph`

A File Graph Visitor
=======================

The ``FileIncludeGraph.FileIncludeGraphRoot`` has a method ``def acceptVisitor(self, visitor):`` can accept a
*visitor* object (that can inherit from ``FigVisitorBase``) for traversing the graph.
This takes the visitor object and calls ``visitor.visitGraph(self, theFigNode, theDepth, theLine)`` on that
object where depth is the current depth in the graph as an integer and line the line that is a non-monotonic
sibling node ordinal.

There are a number of visitor examples in the ``FileIncludeGraph`` test code.
``CPIPMain`` has a number of visitor implementations.

``visitGraph(self, theFigNode, theDepth, theLine)``
-----------------------------------------------------

``theFigNode`` is a ``cpip.core.FileIncludeGraph.FileIncludeGraph`` object. See :ref:`cpip.ref.FileIncludeGraph`

Example Visitor
-----------------

Here we create a simple visitor [lines 11-15].
After processing the Translation Unit [line 25] we create a visitor and traverse the include graph [line 26].
At each node in the graph the visitor merely prints out the file (node) name and the findLogic string
i.e. how this file was found for inclusion [line 27].

.. literalinclude:: demo/cpip_19.py
    :language: python
    :linenos:
    :emphasize-lines: 11-15, 26-27

Invoking this code thus (in the manner of the :ref:`cpip.tutorial.PpLexer`):

``$ python docs/doc_src/tutorial/demo/cpip_19.py docs/doc_src/tutorial/demo/proj/src/main.c``

Gives this output:

.. code-block:: console

    Processing: docs/doc_src/tutorial/demo/proj/src/main.c
    <stdio.h>: No such file or directory at line=3, col=1 of file "docs/doc_src/tutorial/demo/proj/src/main.c"
    main.c
    user.h ['"user.h"', 'CP=None', 'usr=cpip/docs/doc_src/tutorial/demo/proj/usr']
    system.h ['<system.h>', 'sys=cpip/docs/doc_src/tutorial/demo/proj/sys']

For example, in line 3, this means that the file :file:`../usr/user.h` was included with a ``#include "user.h"``
statement, first the "Current Place" (``CP``) was searched (unsuccessfully so result None),
then the user include directories were searched and the file was found in the :file:`usr/` directory.

Creating a Bespoke Tree From a FileIncludeGraph
================================================

The use case here is, given a FileIncludeGraph, can I simply create a tree of objects of my own definition from the
graph?
An example would be creating a structure that makes it easy to plot an SVG graph.
The class should sub-class ``cpip.core.FileIncludeGraph.FigVisitorTreeNodeBase``.

The solution is to create a ``cpip.core.FileIncludeGraph.FigVisitorTree`` object with a class definition for the node
objects.
This class definition must take in its constructor a file node (None for the root) and a line number.

Here is an example that is used to create a tree of file name and token counts.
A class ``MyVisitorTreeNode`` is defined that on construction extracts file name and token count data from the file
include graph node.
The other requirement is to implement finalise at the the end of tree construction that updates the token count with
those of the nodes children. Finally it suplies some string representation of itself.

The special code is on lines 11-36 where the ``FileIncludeGraph.FigVisitorTree`` visitor is created with a cls
specification of ``MyVisitorTreeNode``.
The file include graph is then presented with the visitor (line 47).
Finally a tree of ``MyVisitorTreeNode`` objects is retrieved with a call to ``tree()``.
The code is in *docs/doc_src/tutorial/demo/cpip_30.py*:

.. literalinclude:: demo/cpip_30.py
    :language: python
    :linenos:

Invoking this so:

``$ python docs/doc_src/tutorial/demo/cpip_30.py docs/doc_src/tutorial/demo/proj/src/main.c``

Gives this output:

.. code-block:: console

    $python docs/doc_src/tutorial/demo/cpip_30.py docs/doc_src/tutorial/demo/proj/src/main.c
    -001 None 63
      -001 docs/doc_src/tutorial/demo/proj/src/main.c 63
        0004 ../usr/user.h 20
          0005 ../sys/system.h 10

Further examples can be found in the code in :file:`IncGraphSVGBase.py` and :file:`IncGraphXML.py`
