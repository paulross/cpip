.. highlight:: shell

============
Installation
============

CPIP has been tested with Python 2.7 and 3.3 to 3.6. CPIP used to run just fine on Windows but I haven't had a recent opportunity (or reason) to test CPIP on a Windows box.

Stable release
--------------

To install cpip, run this command in your terminal:

.. code-block:: console

    $ pip install cpip

This is the preferred method to install cpip, as it will always install the most recent stable release. 

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for cpip can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/paulross/cpip

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/paulross/cpip/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install

To run the tests:

.. code-block:: console

    $ python setup.py test


Testing the Demo Code
--------------------------

See the :ref:`cpip.tutorial.PpLexer` for an example of running a CPIP ``PpLexer`` on the demonstration code. This gives the core CPIP software a good workout.

.. _Github repo: https://github.com/paulross/cpip
.. _tarball: https://github.com/paulross/cpip/tarball/master
