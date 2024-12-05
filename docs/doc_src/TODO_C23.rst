
==============
Supporting C23
==============

CPIP is based on C99 (ISO/IEC 9899:1999) and C++98 ISO/IEC 14882:1998(E).

The C23 standard (ISO/IEC 9899:2024) makes several changes to to preprocessor, a summary is here on
`Wikipedia <https://en.wikipedia.org/wiki/C23_(C_standard_revision)#Preprocessor>`_.
The C23 standard can be found as an open access draft from
`www.open-std.org <https://www.open-std.org>`_ as
`"ISO/IEC 9899:2024 (en) — N3220 working draft" <https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf>`_.

This document describes the impact on CPIP version 0.9.9, and moving to a superior version (1.0.0?).

Standard Support
================

The move to C23 suggests that CPIP should have a global configuration such that C23 is supported.

Check ISO/IEC 9899:1999 6.10.8 and  ISO/IEC 9899:2024 6.10.10 "Predefined macro names" for how use
``__STDC_VERSION__``.

The ``--std=`` values follow the `GCC -std <https://gcc.gnu.org/onlinedocs/gcc/C-Dialect-Options.html>`_ values.
Values are lower case.

Have a command line option ``--std=c23`` where the options are ``c99``, ``c23`` with the default ``c99``.

K&R C
-----

Notable preprocessor changes:

* Comments starting with ``//`` are **not** supported.
* ``__VA_ARGS__`` not supported.

``--std=`` supported
^^^^^^^^^^^^^^^^^^^^

* ``--std=k&r``

ANSI C
------

Notable preprocessor changes:

* Comments starting with ``//`` are **not** supported.
* ``__VA_ARGS__`` added???

``--std=`` supported
^^^^^^^^^^^^^^^^^^^^

* ``--std=ansi``
* ``--std=c89``
* ``--std=c90``
* ``--std=iso9899:1990``
* ``--std=iso9899:199409``

ANSI: ANSI X3.159-1989
ISO: ISO/IEC 9899:1990


C95
------

Notable preprocessor changes:

* Added ``__STDC_VERSION__``. ``__STDC_VERSION__ >= 199409L``
* Added digraphs.
* Added ``and`` for ``&&``.  See ``WORD_REPLACE_MAP`` in ``src/cpip/core/PpToken.py:168``.

Looks like much of this is supported by ``src/cpip/core/PpTokeniser.py DIGRAPH_TABLE``.

Not specified by `GCC -std <https://gcc.gnu.org/onlinedocs/gcc/C-Dialect-Options.html>`_.

``--std=`` supported
^^^^^^^^^^^^^^^^^^^^

* ``--std=c95``

ISO: ISO/IEC 9899:1990/AMD1:1995

C99
------

Notable preprocessor changes:

* Comments starting with ``//`` are supported from hereon.

``--std=`` supported
^^^^^^^^^^^^^^^^^^^^

* ``--std=c99``
* ``--std=c9x``
* ``--std=iso9899:1999``
* ``--std=iso9899:199x``

ISO: ISO/IEC 9899:1999

C11
------

Notable preprocessor changes:

* None?

``--std=`` supported
^^^^^^^^^^^^^^^^^^^^

* ``--std=c11``
* ``--std=c1x``
* ``--std=iso9899:2011``

ISO: ISO/IEC 9899:2011

C17/C18
--------

Notable preprocessor changes:

* None?

``--std=`` supported
^^^^^^^^^^^^^^^^^^^^

* ``--std=c17``
* ``--std=c18``
* ``--std=iso9899:2017``
* ``--std=iso9899:2018``

ISO: ISO/IEC 9899:2018

C23
------

See above, this is the subject of this document.

``--std=`` supported
^^^^^^^^^^^^^^^^^^^^

* ``--std=c23``

ISO: ISO/IEC 9899:2024



Macros ``__STDC__`` and ``__STDC_VERSION__``
----------------------------------------------

From `__STDC_VERSION__ and __STDC__ on Sourceforge <https://sourceforge.net/p/predef/wiki/Standards/>`_,
standards documents and Wikipedia.


======= =================================== =======================
C       ``__STDC__``                        Standard
======= =================================== =======================
C89     ``__STDC__``                        ANSI X3.159-1989
C90     ``__STDC__``                        ISO/IEC 9899:1990
======= =================================== =======================


======= =================================== ================================================
C       ``__STDC_VERSION__``                Standard
======= =================================== ================================================
C95     ``__STDC_VERSION__ = 199409L``      ISO/IEC 9899-1:1994, ISO/IEC 9899:1990/AMD1:1995
C99     ``__STDC_VERSION__ = 199901L``      ISO/IEC 9899:1999
C11     ``__STDC_VERSION__ = 201112L``      ISO/IEC 9899:2011
C17/C18 ``__STDC_VERSION__ = 201710L``      ISO/IEC 9899:2018
C23     ``__STDC_VERSION__ = 202311L``      ISO/IEC 9899:2024
======= =================================== ================================================

Solution and Impact
-------------------

In ``cpip.core.standards.py`` something like:

.. code-block:: python

    class CStandard:
        # {std : generic_standard, ...}
        C_STANDARDS_SUPPORTED = {
            'ansi' : 'ANSI',
            'c11' : 'C11',
            # ...
        }
        # {generic_standard : __STDC_VERSION__, ...}
        STDC_VERSION = {
            'C11' : '201112L',
            # Etc.
        }

        def __init__(self, standard: str):
            # Check and raise ValueError if appropriate.
            pass

        def stdc_version(self) -> str:
            return self.STDC_VERSION.get(self.std, '')

        def has_digraphs(self) -> bool:
            pass

        def has_cpp_style_comments(self) -> bool:
            pass


Add a required argument of type CStandard to ``cpip.core.PpLexer.PpLexer`` constructor and propagate from there.
And, of course, the appropriate tests.

Open Questions
^^^^^^^^^^^^^^

* What default value to use for the standard?
* When non compliance is detected warn or error? Simulate ``-Wpedantic``?

Effort: Medium to High.


Impact
------

This has to become general across the CPIP landscape, for example from ``cpip/CPIPMain.py`` through to
``cpip.core.PpTokeniser.PpTokeniser``.

Effort: High.

Removing Trigraphs
==================

The proposal to remove Trigraphs is here, with examples,
`WG14-N2940 (archived) <https://web.archive.org/web/20221026005747/https://www.open-std.org/jtc1/sc22/wg14/www/docs/n2940.pdf>`_.

Also relevant: `N2701 <https://www.open-std.org/jtc1/sc22/wg14/www/docs/n2701.htm>`_ and
`N4086 <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2014/n4086.html>`_.

Solution and Impact
-------------------

Trigraphs are processed here: ``cpip.core.ItuToTokens.ItuToTokens._translatePhase_1()`` and
``cpip.core.PpTokeniser.PpTokeniser._translateTrigraphs()``

This seems like a candidate for a configurable parser when the PpTokeniser takes a configuration option (or class).

Effort: Low.

``#elifdef`` and ``#elifndef`` directives
=========================================

The proposal is here, with examples,
`WG14-N2645 (archived) <https://web.archive.org/web/20221128133337/https://open-std.org/JTC1/SC22/WG14/www/docs/n2645.pdf>`_.

Solution and Impact
-------------------

This can be supported (fully?) in ``cpip/core/CppCond.py`` with appropriate tests.

Effort: Medium.

``#embed``
==========

This includes binary files such as images:
`Wikipedia on #embed <https://en.wikipedia.org/wiki/C_preprocessor#Binary_resource_inclusion>`_.
And `CppReference <https://en.cppreference.com/w/c/preprocessor/embed>`_.

As the Wikipedia page describes, the binary resource gets included in the manner of ``xxd -i``.
For example:

.. code-block:: bash

    xxd -i dist/cpip-0.9.9-py2.py3-none-any.whl

Gives:

.. code-block:: c

    unsigned char dist_cpip_0_9_9_py2_py3_none_any_whl[] = {
    /* This is what #embed should expand to. */
      0x50, 0x4b, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x08, 0x00, 0x30, 0x98,
      0x48, 0x58, 0xc2, 0x2f, 0xc7, 0x97, 0x2e, 0x3b, 0x00, 0x00, 0xf1, 0x08,
      0x01, 0x00, 0x10, 0x00, 0x00, 0x00, 0x63, 0x70, 0x69, 0x70, 0x2f, 0x43,
      0x50, 0x49, 0x50, 0x4d, 0x61, 0x69, 0x6e, 0x2e, 0x70, 0x79, 0xed, 0x7d,
      0x6b, 0x77, 0xe3, 0x36, 0x92, 0xe8, 0x77, 0xff, 0x0a, 0x8c, 0x7d, 0xfb,
      0x4a, 0x9a, 0xc8, 0xb4, 0xdd, 0x9d, 0xa7, 0x12, 0xf5, 0xac, 0x63, 0xbb,
    /* 8<---- Snip ---->8 */
      0x2e, 0x64, 0x69, 0x73, 0x74, 0x2d, 0x69, 0x6e, 0x66, 0x6f, 0x2f, 0x52,
      0x45, 0x43, 0x4f, 0x52, 0x44, 0x50, 0x4b, 0x05, 0x06, 0x00, 0x00, 0x00,
      0x00, 0x19, 0x00, 0x19, 0x00, 0x96, 0x06, 0x00, 0x00, 0x5f, 0x59, 0x01,
      0x00, 0x00, 0x00
    /* End of #embed expansion. */
    };
    unsigned int dist_cpip_0_9_9_py2_py3_none_any_whl_len = 90123;

The proposal is here, with examples,
`WG14-N3017 (archived) <https://web.archive.org/web/20221224045304/https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3017.htm>`_.

Other information:

* `Commentary on StackOverflow <https://stackoverflow.com/questions/74621610/what-is-the-purpose-of-the-new-C23-embed-directive>`_.
* Clang status (needs clang 19+) `here <https://stackoverflow.com/questions/74621610/what-is-the-purpose-of-the-new-C23-embed-directive>`_.

Solution and Impact
-------------------

Perhaps needs an ``EmbedHandler.py`` similar to (or sub-class) ``cpip/core/IncludeHandler.py``
within that file and with appropriate tests?

.. note::

    From the `standard <https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf>`_
    ISO/IEC 9899:2024 6.10.4.1 Description note 14: "A mechanism similar to, but distinct from, the
    implementation-defined search paths used for source file inclusion (6.10.3) is encouraged."

Other notes:

* ``#embed``: See ISO/IEC 9899:2024 6.10.4.1 #embed preprocessing directive.
* ``__has_embed`` is in the standard. See ISO/IEC 9899:2024 6.10.2 Conditional inclusion.
* ``__STDC_EMBED_NOT_FOUND__``, ``__STDC_EMBED_FOUND__``, ``__STDC_EMBED_EMPTY__`` must be respected.
   See ISO/IEC 9899:2024 6.10.2 Conditional inclusion.
   Also See ISO/IEC 9899:2024 6.10.2 paras 7, 21, 22 and 23 #embed preprocessing directive.

Effort: High+. We don't (yet) have a compiler that supports this for testing.
See ISO/IEC 9899:2024 6.10.4.1 ``#embed`` preprocessing directive which is complex.

``#warning``
============

ISO/IEC 9899:2024 6.10.7 "Diagnostic directives" adds warning messages, similar to ``#error``.

The proposal is here:
`WG14-N2686 (archived) <https://web.archive.org/web/20221128133337/https://open-std.org/JTC1/SC22/WG14/www/docs/n2686.pdf>`_.

Solution and Impact
-------------------

Little, as already supported in ``cpip/core/CppDiagnostic.py``.

See also ``cpip.core.PpLexer.PpLexer._cppWarning``.

Check this code and tests.

Check appropriate tests should be in ``tests/unit/test_core/test_CppDiagnostic.py`` and
``tests/unit/test_core/test_PpLexer.py``.

Effort: Low.


``__has_include``
=================

The proposal is here, with examples,
`WG14-N2799 (archived) <https://web.archive.org/web/20221128133337/https://open-std.org/JTC1/SC22/WG14/www/docs/n2686.pdf>`_.

Check ISO/IEC 9899:2024 6.10.10 "Predefined macro names".

Solution and Impact
-------------------

Affects:

* Predefined macros since ``__has_include`` is a predefined, function like, macro.
* The Include handler that needs an API to handle the query.
  Looks like ``cpip.core.IncludeHandler.CppIncludeStd.canInclude()`` is interesting, or is that post-include?

Effort: Medium.

``__has_c_attribute``
=========================

The proposal is here, with examples,
`WG14-N2553 (archived) <https://web.archive.org/web/20221014221314/https://open-std.org/JTC1/SC22/WG14/www/docs/n2553.pdf>`_.

Solution and Impact
-------------------

Affects:

* Predefined macros since ``__has_c_attribute`` is a predefined, function like, macro.
* Probably several other places as this macro queries the preprocessing environment.

Effort: Medium to high.

``__VA_OPT__``
==============

The proposal is here, with examples,
`WG14-N3033 (archived) <https://web.archive.org/web/20221227031727/https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3033.htm>`_.

Solution and Impact
-------------------

This mainly affects ``cpip.core.PpDefine.PpDefine`` and the appropriate tests.
The change should be contained by that class as it is really to use a different set of rules for macro expansion.
And, of course, the appropriate tests.

Effort: Medium.

Other
=====

Useful:

.. code-block:: bash

    (cpip_3.12)
    engun@Pauls-MBP  ~/Documents/workspace/cpip (C23)
    $ cpp --version
    Apple clang version 15.0.0 (clang-1500.0.40.1)
    Target: x86_64-apple-darwin22.6.0
    Thread model: posix
    InstalledDir: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin
    (cpip_3.12)
    engun@Pauls-MBP  ~/Documents/workspace/cpip (C23)
    $ cpp -dM -std=k
    error: invalid value 'k' in '-std=k'
    note: use 'c89', 'c90', or 'iso9899:1990' for 'ISO C 1990' standard
    note: use 'iso9899:199409' for 'ISO C 1990 with amendment 1' standard
    note: use 'gnu89' or 'gnu90' for 'ISO C 1990 with GNU extensions' standard
    note: use 'c99' or 'iso9899:1999' for 'ISO C 1999' standard
    note: use 'gnu99' for 'ISO C 1999 with GNU extensions' standard
    note: use 'c11' or 'iso9899:2011' for 'ISO C 2011' standard
    note: use 'gnu11' for 'ISO C 2011 with GNU extensions' standard
    note: use 'c17', 'iso9899:2017', 'c18', or 'iso9899:2018' for 'ISO C 2017' standard
    note: use 'gnu17' or 'gnu18' for 'ISO C 2017 with GNU extensions' standard
    note: use 'c2x' for 'Working Draft for ISO C2x' standard
    note: use 'gnu2x' for 'Working Draft for ISO C2x with GNU extensions' standard

Sources
-------

GCC
^^^^^^^^^^^

* `Standard support <https://gcc.gnu.org/onlinedocs/gcc/Standards.html>`_
* `GCC C options <https://gcc.gnu.org/onlinedocs/gcc/C-Dialect-Options.html>`_


Wikipedia
^^^^^^^^^

* `General C <https://en.wikipedia.org/wiki/C_(programming_language)>`_
* `K&R C <https://en.wikipedia.org/wiki/K%26R_C>`_
* `ANSI C/ISO C/C89/C90 <https://en.wikipedia.org/wiki/ANSI_C>`_
* `C95 <https://en.wikipedia.org/wiki/ANSI_C#C95>`_
* `C99 <https://en.wikipedia.org/wiki/C99>`_
* `C11 <https://en.wikipedia.org/wiki/C11_(C_standard_revision)>`_
* `C17/C18 <https://en.wikipedia.org/wiki/C17_(C_standard_revision)>`_
* `C23 <https://en.wikipedia.org/wiki/C23_(C_standard_revision)>`_


Other
^^^^^

* Definition of `__STDC_VERSION__ and __STDC__ <https://sourceforge.net/p/predef/wiki/Standards/>`_ for various
  standards.
* CPP reference on the `C Preprocessor <https://en.cppreference.com/w/c/preprocessor>`_.
* CPP reference on the `C history <https://en.cppreference.com/w/c/preprocessor>`_ with links to standards documents.
* The `rationale <https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf>`_ for the C99 standard.
* `nsz <https://port70.net/~nsz/c/>`_ has a great collated set of standards that can be obtained by
  ``wget -r -np -k -e robots=off https://port70.net/\~nsz/c/``

Miscellaneous
===============

``#pragma``
-----------

Review ISO/IEC 9899:1999 6.10.6 and ISO/IEC 9899:2024 6.10.8 "Pragma directive".
Is CPIP compliant?

``_Pragma``
-----------

We are not conforming to C99/C23 with ``_Pragma``.
See section 5.1.1.2 translation phase 4 in both standards.

Predefined Macros
-----------------

Are we complying with these
`predefined macros <https://en.cppreference.com/w/c/preprocessor/replace#Predefined_macros>`_ ?

``import`` and ``export``
-------------------------

Do we support this since C++20: https://en.cppreference.com/w/cpp/language/modules

No, there is no mention of ``import`` or ``export`` in the C23 standard.

Effort Summary
==============

=========   ======
Effort      Items
=========   ======
Low         2
Medium      4
High        2
High+       1
=========   ======
