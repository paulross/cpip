.. moduleauthor:: Paul Ross <cpipdev@googlemail.com>
.. sectionauthor:: Paul Ross <cpipdev@googlemail.com>

************************
Coord
************************

Main Classes
===============

Most classes in this module are ``collections.namedtuple`` objects.

=========== =============================== ========================================
Class       Description                     Attributes
=========== =============================== ========================================
``Dim``     Linear dimension                value units
``Box``     A Box                           width depth
``Pad``     Padding around a tree object    prev next, parent child
``Margin``  Padding around an  object       left right top bottom
``Pt``      A point in Cartesian space		x y
=========== =============================== ========================================

Reference
===========

.. toctree::
   :maxdepth: 2

.. automodule:: cpip.plot.Coord
	:member-order: bysource
	:members:
	:special-members:

Examples
==========

``Coord.Dim()``
--------------------------

Creation, addition and subtraction::

    d = Coord.Dim(1, 'in') + Coord.Dim(18, 'px')
    # d is 1.25 inches
    d = Coord.Dim(1, 'in') - Coord.Dim(18, 'px')
    # d is 0.75 inches
    d += Coord.Dim(25.4, 'mm')
    # d is 1.75 inches

Scaling and unit conversion returns a new object::

	a = Coord.Dim(12, 'px')
	b = myObj.scale(6.0)
	# b is 72 pixels
	c = b.convert('in')
	# 1 is 1 inch

Comparison::

	assert(Coord.Dim(1, 'in') == Coord.Dim(72, 'px'))
	assert(Coord.Dim(1, 'in') >= Coord.Dim(72, 'px'))
	assert(Coord.Dim(1, 'in') <= Coord.Dim(72, 'px'))
	assert(Coord.Dim(1, 'in') > Coord.Dim(71, 'px'))
	assert(Coord.Dim(1, 'in') < Coord.Dim(73, 'px'))

``Coord.Pt()``
--------------------------

Creation::

	p = Coord.Pt(
		Coord.Dim(12, 'px'),
		Coord.Dim(24, 'px'),
		)
	print(p)
	# Prints: 'Pt(x=Dim(12px), y=Dim(24px))'
	p.x # Coord.Dim(12, 'px'))
	p.y # Coord.Dim(24, 'px'))
	# Scale up by 6 and convert units
	pIn = p.scale(6).convert('in')
	# pIn now 'Pt(x=Dim(1in), y=Dim(2in))'

Testing
============

The unit tests are in :file:`test/TestCoord.py`.
