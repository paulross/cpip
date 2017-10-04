.. include:: ../../CONTRIBUTING.rst

Release Checklist
------------------------

In the following the example the version we are moving to, ``M.m.p``, is ``0.9.7``.

Current version should be something like ``M.m.(p)rcX``, for example ``0.9.7rc4``.

Increment version
~~~~~~~~~~~~~~~~~~~

Change the version to ``M.m.p`` in these places:

    * *setup.cfg*
    * *setup.py*
    * *src/cpip/CPIPmain.py* 
    * *src/cpip/__init__.py*

In *src/cpip/__init__.py* change ``CPIP_VERSION = (0, 9, 7)``

Update the history:

    * *HISTORY.rst*
    * *src/cpip/__init__.py*

Update any Trove classifiers in *setup.py*, https://pypi.python.org/pypi?%3Aaction=list_classifiers

Build and Test
~~~~~~~~~~~~~~~~~~~

Build and test for Python 3.6:

.. code-block:: console

    $ . ~/venvs/CPIP36/bin/activate    
    (CPIP36) $ python setup.py install
    (CPIP36) $ python setup.py test

And for Python 2.7

.. code-block:: console

    $ . ~/venvs/CPIP27/bin/activate    
    (CPIP27) $ python setup.py install
    (CPIP27) $ python setup.py test

Build the docs HTML to test them, from an environment that has Sphinx:

.. code-block:: console

    (Sphinx) $ cd docs
    (Sphinx) $ make clean
    (Sphinx) $ make html

Commit and Tag
~~~~~~~~~~~~~~~~~~~

Commit, tag and push:

.. code-block:: console

    $ git add .
    $ git commit -m 'Release version 0.9.7'
    $ git tag -a v0.9.7 -m 'Version 0.9.7'
    $ git push
    $ git push origin v0.9.7

PyPi
~~~~~~~~~~~~~~~~~~~

Prepare release to PyPi for Python 3.6:

Build the egg and the source distribution:

.. code-block:: console

    (CPIP36) $ python setup.py install sdist

And for Python 2.7

.. code-block:: console

    (CPIP27) $ python setup.py install

Check the contents of ``dist/*``, unpack into ``tmp/`` if you want:

.. code-block:: console

    $ cp dist/* tmp/
    $ cd tmp/
    $ unzip cpip-0.9.7-py2.7.egg -d py27egg
    $ unzip cpip-0.9.7-py3.6.egg -d py36egg
    $ tar -xzf cpip-0.9.7.tar.gz

Release to PyPi, https://pypi.python.org/pypi/cpip:

.. code-block:: console

    (CPIP36) $ twine upload dist/*

ReadTheDocs
~~~~~~~~~~~~~~~~~~~

Build the documentation: https://readthedocs.org/projects/cpip/builds/

Prepare Next Release Candidate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally change the version to ``M.m.(p+1)rc0``, in this example ``0.9.8rc0`` in these places:

    * *setup.cfg*
    * *setup.py*
    * *src/cpip/CPIPmain.py* 
    * *src/cpip/__init__.py*, also change ``CPIP_VERSION = (0, 9, 8, 'rc0')``

Commit and push:

.. code-block:: console

    $ git add .
    $ git commit -m 'Release candidate v0.9.8rc0'
    $ git push

