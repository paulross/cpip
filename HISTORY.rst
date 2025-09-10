History
=======

1.0.0 First Production Release (TODO)
----------------------------------------

* Development Status :: 5 - Production/Stable
* Add support for C23.
* Add selectable support for the following C standards: K&R, ANSI/C89/C90, C95, C99, C11, C17/C18, C23.
* Add selectable support for GNU extensions.
* Add CMake support. CPIP builds can be done using the existing CMake build metadata from a project.
* Fix line/column counts (issue https://github.com/paulross/cpip/issues/1 ).
* Fix accidental token pasting (issue https://github.com/paulross/cpip/issues/2 ).
* Fix SVG zoom (issue https://github.com/paulross/cpip/issues/7 ).
* Fix macro replacement re-scanning issue to be conformant with other implementations (GCC, Clang) (issue TODO).
* Support for Python versions 3.9, 3.10, 3.11, 3.12, 3.13.
* Drop explicit support for Python 3.6, 3.7, 3.8

0.9.9 Beta Release (2022-12-16)
--------------------------------

* Add strip_comments.py
* Add support for Python3 versions. Supported versions 3.6, 3.7, 3.8, 3.9, 3.10, 3.11.
* Remove support for Python 2.7 (although it might still work).

0.9.8 Beta Release (2021-01-28)
--------------------------------

* Minor fixes.

0.9.7 Beta Release (2017-10-04)
--------------------------------

* Minor fixes.
* Performance optimisations.
* Builds the CPython source tree in 5 hours with 2 CPUs.
* Documentation improvements.

0.9.5 Beta Release (2017-10-03)
--------------------------------

* Migrate from sourceforge to GitHub.

0.9.1 (2014-09-03)
------------------

Version 0.9.1, various minor fixes. Tested on Python 2.7 and 3.3.

Alpha Plus Release (2014-09-04)
-------------------------------

Fairly thorough refactor. CPIP now tested on Python 2.7, 3.3. Version 0.9.1. Updated documentation.

Alpha Release (2012-03-25)
---------------------------

Very little functional change. CPIP now tested on Python 2.6, 2.7, 3.2. Added loads of documentation.

Alpha Release (2011-07-14)
---------------------------

This is a pre-release of CPIP. It is tested on BSD/Linux, it will probably work on Windows (although some unit tests will fail on that platform).

Project started in 2008.

