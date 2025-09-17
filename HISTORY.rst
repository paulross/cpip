
.. index::
   single: History

History
=======

.. index::
   single: History; 1.0.0 (TODO)

1.0.0 First Production Release (TODO)
----------------------------------------

TODO
^^^^

* TODO: Add support for C23. See ``docs/doc_src/TODO_C23.rst`` and annotations in the notebook.
* TODO: Add selectable support for the following C standards: K&R, ANSI/C89/C90, C95, C99, C11, C17/C18, C23.
* TODO: Add selectable support for GNU extensions.
* TODO: Fix Conditional stack closure failure when processing Linux cpu.c.
* TODO: Build Linux cpu.c using the Linux configure/build system without error, probably on a virtual machine.
* TODO: Fix MultiPassString off by one (or more) error.
* TODO: Add link to file HTML representation when showing a #include directive.
* TODO: Fix line/column counts (issue https://github.com/paulross/cpip/issues/1 ).
* TODO: Fix accidental token pasting (issue https://github.com/paulross/cpip/issues/2 ).
* TODO: Fix SVG zoom (issue https://github.com/paulross/cpip/issues/7 ).
* TODO: Fix macro replacement re-scanning issue to be conformant with other implementations (GCC, Clang) (issue TODO).
* TODO: Fix all xfailing tests.
* TODO: Clear any remaining issues: https://github.com/paulross/cpip/issues

DONE
^^^^

* Add CMake support. CPIP builds can be done using the existing CMake build metadata from a project.
* Add ``--sys-auto-lang=C`` and ``--sys-auto-lang=C++`` option to pick up platform system includes
  (not supported in Windows yet).
* Brought the tutorial for ``PpLexer.py`` and ``FileIncludeGraph.py`` up to date.
* Add test for tutorial code in ``build_all.sh`` for all Python versions
* Add per-module logging.
* Add a proposal for incremental builds (``docs/doc_src/IncrementalBuild.rst``).
* Support for Python versions 3.9, 3.10, 3.11, 3.12, 3.13.
* Drop explicit support for Python 3.6, 3.7, 3.8
* Development Status :: 5 - Production/Stable

.. index::
   single: History; 0.9.9 (2022-12-16)

0.9.9 Beta Release (2022-12-16)
--------------------------------

* Add strip_comments.py
* Add support for Python3 versions. Supported versions 3.6, 3.7, 3.8, 3.9, 3.10, 3.11.
* Remove support for Python 2.7 (although it might still work).

.. index::
   single: History; 0.9.8 (2021-01-28)

0.9.8 Beta Release (2021-01-28)
--------------------------------

* Minor fixes.

.. index::
   single: History; 0.9.7 (2017-10-04)

0.9.7 Beta Release (2017-10-04)
--------------------------------

* Minor fixes.
* Performance optimisations.
* Builds the CPython source tree in 5 hours with 2 CPUs.
* Documentation improvements.

.. index::
   single: History; 0.9.5 (2017-10-03)

0.9.5 Beta Release (2017-10-03)
--------------------------------

* Migrate from sourceforge to GitHub.

.. index::
   single: History; 0.9.1 (2014-09-03)

0.9.1 (2014-09-03)
------------------

Version 0.9.1, various minor fixes. Tested on Python 2.7 and 3.3.

.. index::
   single: History; Alpha+ (2014-09-04)

Alpha Plus Release (2014-09-04)
-------------------------------

Fairly thorough refactor. CPIP now tested on Python 2.7, 3.3. Version 0.9.1. Updated documentation.

.. index::
   single: History; Alpha (2012-03-25)

Alpha Release (2012-03-25)
---------------------------

Very little functional change. CPIP now tested on Python 2.6, 2.7, 3.2. Added loads of documentation.

.. index::
   single: History; Alpha (2011-07-14)

Alpha Release (2011-07-14)
---------------------------

This is a pre-release of CPIP. It is tested on BSD/Linux, it will probably work on Windows (although some unit tests will fail on that platform).

Project started in 2008.
