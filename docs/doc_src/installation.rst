.. highlight:: shell

============
Installation
============

CPIP has been tested with Python 2.7 and 3.3 to 3.6. CPIP used to run just fine on Windows but I haven't had a recent opportunity (or reason) to test CPIP on a Windows box.

First make a virtual environment in your :file:`{<PYTHONVENVS>}`, say :file:`{~/pyvenvs}`:

.. code-block:: console

    $ python3 -m venv <PYTHONVENVS>/CPIP
    $ . <PYTHONVENVS>/CPIP/bin/activate
    (CPIP) $

Stable release
--------------

To install cpip, run this command in your terminal:

.. code-block:: console

    (CPIP) $ pip install cpip

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

    (CPIP) $ git clone git://github.com/paulross/cpip

Or download the `tarball`_:

.. code-block:: console

    (CPIP) $ curl -OL https://github.com/paulross/cpip/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    (CPIP) $ python setup.py install

Install the test dependencies and run CPIP's tests:

.. code-block:: console

    (CPIP) $ pip install pytest
    (CPIP) $ pip install pytest-runner
    (CPIP) $ python setup.py test

Developing with CPIP
----------------------------

If you are developing with CPIP you need test coverage and documentation tools.

Test Coverage
^^^^^^^^^^^^^^^^

Install ``pytest-cov``:

.. code-block:: console

    (CPIP) $ pip install pytest-cov

The most meaningful invocation that elimates the top level tools is:

.. code-block:: console

    (CPIP) $ pytest --cov=cpip.core --cov=cpip.plot --cov=cpip.util --cov-report html tests/

Documentation
^^^^^^^^^^^^^^^^

If you want to build the documentation you need to:

.. code-block:: console

    (CPIP) $ pip install Sphinx
    (CPIP) $ cd docs
    (CPIP) $ make html

The landing page is *docs/_build/html/index.html*.

Testing the Demo Code
--------------------------

See the :ref:`cpip.tutorial.PpLexer` for an example of running a CPIP ``PpLexer`` on the demonstration code. This gives the core CPIP software a good workout.

.. _Github repo: https://github.com/paulross/cpip
.. _tarball: https://github.com/paulross/cpip/tarball/master
