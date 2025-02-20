
========================================
Supporting Different C standards and C23
========================================

CPIP is based on C99 (ISO/IEC 9899:1999) and C++98 ISO/IEC 14882:1998(E).

The C23 standard (ISO/IEC 9899:2024) makes several changes to to preprocessor, a summary is here on
`Wikipedia <https://en.wikipedia.org/wiki/C23_(C_standard_revision)#Preprocessor>`_.
The C23 standard can be found as an open access draft from
`www.open-std.org <https://www.open-std.org>`_ as
`"ISO/IEC 9899:2024 (en) — N3220 working draft" <https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf>`_.

This document also describes non-C23 improvements to CPIP.

This document describes the impact on CPIP version 0.9.9, and moving to a superior version (1.0.0?).

C Standards
======================

The move to C23 suggests that CPIP should have a global configuration such that C23 is supported.

Check ISO/IEC 9899:1999 6.10.8 and  ISO/IEC 9899:2024 6.10.10 "Predefined macro names" for how use
``__STDC_VERSION__``.

The ``--std=`` values follow the `GCC -std <https://gcc.gnu.org/onlinedocs/gcc/C-Dialect-Options.html>`_ values.
Values are lower case.

Have a command line option ``--std=c23`` where the options are ``c99``, ``c23`` with the default ``c99``.

-----
K&R C
-----

Notable preprocessor changes:

* Comments starting with ``//`` are **not** supported.
* ``__VA_ARGS__`` not supported.

Supported ``--std=`` Values
---------------------------

* ``--std=k&r``

------
ANSI C
------

Notable preprocessor changes:

* Comments starting with ``//`` are **not** supported.
* ``__VA_ARGS__`` added???

Supported ``--std=`` Values
---------------------------

* ``--std=ansi``
* ``--std=c89``
* ``--std=c90``
* ``--std=iso9899:1990``

ANSI: ANSI X3.159-1989
ISO: ISO/IEC 9899:1990


------
C95
------

Notable preprocessor changes:

* Added ``__STDC_VERSION__``. ``__STDC_VERSION__ >= 199409L``
* Added digraphs.
* Added ``and`` for ``&&``.  See ``WORD_REPLACE_MAP`` in ``src/cpip/core/PpToken.py:168``.

Looks like much of this is supported by ``src/cpip/core/PpTokeniser.py DIGRAPH_TABLE``.

Not specified by `GCC -std <https://gcc.gnu.org/onlinedocs/gcc/C-Dialect-Options.html>`_.

Supported ``--std=`` Values
---------------------------

* ``--std=c95``
* ``--std=iso9899:199409``

ISO: ISO/IEC 9899:1990/AMD1:1995

------
C99
------

Preprocessor changes (from `nsz c9x changes <https://port70.net/~nsz/c/c89/c9x_changes.html#Preprocessor>`_):

* The #pragma directive has three reserved forms, all starting with the pp-token STDC right after "pragma". These are used to specify certain characteristics of the floating point support to comply with IEC 559.
* The _Pragma unary operator allows the construction of pragmas through macro expansion.
* Predefined macro __STDC_VERSION__ has now the value 199901L. (In C94, it's value was 199409L, C89 didn't have it at all.) I suppose this value will be fixed in the final version of the new standard to reflect the date of its actual acceptance by ISO.
* There are two conditionally defined macros, __STDC_IEC_559__ and __STDC_IEC_559_COMPLEX__, indicating IEC 559 conformance for floating point and complex arithmetic, respectively. If defined, they're defined to the decimal constant 1. A third conditionally defined macro called __STDC_ISO_10646__ shall indicate that wchar_t is in accordance with ISO/IEC 10646. If defined, this macro has a value of the form yyyymmL.
* Macro expansion: empty arguments are explicitly allowed. (In C89, this resulted in undefined behavior.) Stringification (the # operator) of an empty argument yields the empty string, concatenation (##) of an empty argument with a non-empty argument produces the non-empty argument, and concatenation of two empty arguments produces nothing at all.
* Function-like macros with variable arguments, uses the ellipsis (...) notation. For replacement, the variable arguments (including the separating commas) are "collected" into one single extra argument that can be referenced as __VA_ARGS__ within the macro's replacement list. __VA_ARGS__ may occur only within the replacement list of a function-like macro having a variable argument list. It's possible to have only variable arguments, as in
  #define My_Macro(...) __VA_ARGS__
* The #line directive allows the specification of a line number up to 2**31-1. (In C89, the limit was 2**15-1, i.e. 32767.)
* The syntax of preprocessing numbers has been changed to allow for the new binary exponents present in hexadecimal floating point constants.
* Line-comments (starting with the pp-token "//" and extending up to the end of the line). As with normal comments, it's not possible to construct a comment as the result of macro replacement.

Supported ``--std=`` Values
---------------------------

* ``--std=c99``
* ``--std=c9x``
* ``--std=iso9899:1999``
* ``--std=iso9899:199x``

ISO: ISO/IEC 9899:1999

------
C11
------

Notable preprocessor changes:

Diff:

/Users/engun/Documents/standards/C_CPP_ProgrammingLanguage/nsz/c/port70.net/~nsz/c/c99/n1256.txt

/Users/engun/Documents/standards/C_CPP_ProgrammingLanguage/nsz/c/port70.net/~nsz/c/c11/n1570.txt

The latter has:

.. code-block:: text

    4   EXAMPLE There are cases where it is not clear whether a replacement is nested or not. For example,
        given the following macro definitions:
                #define f(a) a*g
                #define g(a) f(a)
        the invocation
                f(2)(9)
        may expand to either
                2*f(9)
        or
                2*9*g
        Strictly conforming programs are not permitted to depend on such unspecified behavior.

Other differences:

* 6.10.8 Predefined macro names
* 6.10.8.2 Environment macros
* 6.10.8.3 Conditional feature macros


Supported ``--std=`` Values
---------------------------

* ``--std=c11``
* ``--std=c1x``
* ``--std=iso9899:2011``

ISO: ISO/IEC 9899:2011

--------
C17/C18
--------

Notable preprocessor changes:

* None?

Supported ``--std=`` Values
---------------------------

* ``--std=c17``
* ``--std=c18``
* ``--std=iso9899:2017``
* ``--std=iso9899:2018``

ISO: ISO/IEC 9899:2018

------
C23
------

This has a large number of changes.

Supported ``--std=`` Values
---------------------------

* ``--std=c23``
* ``--std=iso9899:2024``

ISO: ISO/IEC 9899:2024


Specific Changes
---------------------------

Removing Trigraphs
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The proposal to remove Trigraphs is here, with examples,
`WG14-N2940 (archived) <https://web.archive.org/web/20221026005747/https://www.open-std.org/jtc1/sc22/wg14/www/docs/n2940.pdf>`_.

Also relevant: `N2701 <https://www.open-std.org/jtc1/sc22/wg14/www/docs/n2701.htm>`_ and
`N4086 <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2014/n4086.html>`_.

Solution and Impact
"""""""""""""""""""

Trigraphs are processed here: ``cpip.core.ItuToTokens.ItuToTokens._translatePhase_1()`` and
``cpip.core.PpTokeniser.PpTokeniser._translateTrigraphs()``

This seems like a candidate for a configurable parser when the PpTokeniser takes a configuration option (or class).

Effort: Low.

``#elifdef`` and ``#elifndef`` directives
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The proposal is here, with examples,
`WG14-N2645 (archived) <https://web.archive.org/web/20221128133337/https://open-std.org/JTC1/SC22/WG14/www/docs/n2645.pdf>`_.

Solution and Impact
"""""""""""""""""""

This can be supported (fully?) in ``cpip/core/CppCond.py`` with appropriate tests.

Effort: Medium.

``#embed``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
"""""""""""""""""""

Perhaps needs an ``EmbedHandler.py`` similar to (or sub-class) ``cpip/core/IncludeHandler.py``
within that file and with appropriate tests?

.. note::

    From the `standard <https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf>`_
    ISO/IEC 9899:2024 6.10.4.1 Description note 14: "A mechanism similar to, but distinct from, the
    implementation-defined search paths used for source file inclusion (6.10.3) is encouraged."

Other notes:

* Do we invent another CLI argument equivalent to ``-I`` and ``-J``  to specify the search directories. Say ``-K`` and ``-L``?
  If not given then revert to ``-I`` and ``-J``.
* ``#embed``: See ISO/IEC 9899:2024 6.10.4.1 #embed preprocessing directive.
* ``__has_embed`` is in the standard. See ISO/IEC 9899:2024 6.10.2 Conditional inclusion.
* ``__STDC_EMBED_NOT_FOUND__``, ``__STDC_EMBED_FOUND__``, ``__STDC_EMBED_EMPTY__`` must be respected.
   See ISO/IEC 9899:2024 6.10.2 Conditional inclusion.
   Also See ISO/IEC 9899:2024 6.10.2 paras 7, 21, 22 and 23 #embed preprocessing directive.

See ISO/IEC 9899:2024 6.10.4.1 ``#embed`` preprocessing directive which is complex.

Effort: High+. We don't (yet) have a compiler that supports this for testing.

``#warning``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

ISO/IEC 9899:2024 6.10.7 "Diagnostic directives" adds warning messages, similar to ``#error``.

The proposal is here:
`WG14-N2686 (archived) <https://web.archive.org/web/20221128133337/https://open-std.org/JTC1/SC22/WG14/www/docs/n2686.pdf>`_.

Do we want to forbid this prior to C23?

Solution and Impact
"""""""""""""""""""

Little, as already supported in ``cpip/core/CppDiagnostic.py``.

See also ``cpip.core.PpLexer.PpLexer._cppWarning``.

Check this code and tests.

Check appropriate tests should be in ``tests/unit/test_core/test_CppDiagnostic.py`` and
``tests/unit/test_core/test_PpLexer.py``.

Effort: Low.


``__has_include``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The proposal is here, with examples,
`WG14-N2799 (archived) <https://web.archive.org/web/20221128133337/https://open-std.org/JTC1/SC22/WG14/www/docs/n2686.pdf>`_.

Check ISO/IEC 9899:2024 6.10.10 "Predefined macro names".

Solution and Impact
"""""""""""""""""""

Affects:

* Predefined macros since ``__has_include`` is a predefined, function like, macro.
* The Include handler that needs an API to handle the query.
  Looks like ``cpip.core.IncludeHandler.CppIncludeStd.canInclude()`` is interesting, or is that post-include?

Effort: Medium.

``__has_c_attribute``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The proposal is here, with examples,
`WG14-N2553 (archived) <https://web.archive.org/web/20221014221314/https://open-std.org/JTC1/SC22/WG14/www/docs/n2553.pdf>`_.

See annex M of ISO/IEC 9899:2024 (en) — N3220 working draft.

For full C23 support this macro is defined as ``#define __has_c_attribute(attribute) 202311L``

Solution and Impact
"""""""""""""""""""

Affects:

* Predefined macros since ``__has_c_attribute`` is a predefined, function like, macro.
* Probably several other places as this macro queries the preprocessing environment.

Effort: Medium to high.

``__VA_OPT__``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The proposal is here, with examples,
`WG14-N3033 (archived) <https://web.archive.org/web/20221227031727/https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3033.htm>`_.

Solution and Impact
"""""""""""""""""""

This mainly affects ``cpip.core.PpDefine.PpDefine`` and the appropriate tests.
The change should be contained by that class as it is really to use a different set of rules for macro expansion.
And, of course, the appropriate tests.

Effort: Medium.

Macros ``__STDC__`` and ``__STDC_VERSION__``
============================================

From `__STDC_VERSION__ and __STDC__ on Sourceforge <https://sourceforge.net/p/predef/wiki/Standards/>`_,
standards documents and Wikipedia.


=========== =================================== =======================
C           ``__STDC__``                        Standard
=========== =================================== =======================
C89/ANSI    ``__STDC__``                        ANSI X3.159-1989
C90         ``__STDC__``                        ISO/IEC 9899:1990
=========== =================================== =======================


======= =================================== ================================================
C       ``__STDC_VERSION__``                Standard
======= =================================== ================================================
C95     ``__STDC_VERSION__ = 199409L``      ISO/IEC 9899-1:1994, ISO/IEC 9899:1990/AMD1:1995
C99     ``__STDC_VERSION__ = 199901L``      ISO/IEC 9899:1999
C11     ``__STDC_VERSION__ = 201112L``      ISO/IEC 9899:2011
C17/C18 ``__STDC_VERSION__ = 201710L``      ISO/IEC 9899:2018
C23     ``__STDC_VERSION__ = 202311L``      ISO/IEC 9899:2024
======= =================================== ================================================

The CStandards Class
====================

We need to create a new class ``CStandard`` that handles all of this.

-------------------
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

This class could also:

* Return a list of predefined macros and their definitions such as ``__STDC_VERSION__``.
* Generate the ``--std=...`` help text for ``CPIPMain.py``.
* Generate a ``c_standards.rst`` documentation chapter rather like this one.
* Pick up platform defined macros, for example, with ``$ cpp -dM -std=c99``.

Open Questions
--------------

* What default value to use for the standard?
* When non compliance is detected warn or error? Simulate ``-Wpedantic``?

Effort: Medium to High.


Impact
------

This has to become general across the CPIP landscape, for example from ``cpip/CPIPMain.py`` through to
``cpip.core.PpTokeniser.PpTokeniser``.

Effort: High.


Miscellaneous
===============

This also covers non-C23 compliance.

-----------------------------------
Source Code References to Standards
-----------------------------------

Within the CPIP source code there are many references to ISO/IEC 14882:1998(E), the C++98 standard but none to
ISO/IEC 9899:1999(E) the C99 standard.
This is probably as when CPIP was originally written we were targeting C++98.
Another reason is that the C++98 standard has useful section markers such as ``cpp.cond`` which are a bit more readable
than section numbers.
Since it is probably better that we default to C99 we should include the appropriate references to that standard.

Effort: Low.

-----------
``#pragma``
-----------

Review ISO/IEC 9899:1999 6.10.6 and ISO/IEC 9899:2024 6.10.8 "Pragma directive".
Is CPIP compliant?

Special ``#pragma`` Values
--------------------------

* Push and Pop: ``#pragma push_macro("X")`` and ``#pragma pop_macro("X")``.
  See `GNU <https://gcc.gnu.org/onlinedocs/gcc/Push_002fPop-Macro-Pragmas.html>`_,
  `MSVC <https://learn.microsoft.com/en-us/cpp/preprocessor/push-macro?view=msvc-170>`_.
  See also `GNU/MSVC compatibility <https://www.typeerror.org/docs/gcc~5/push_002fpop-macro-pragmas>`_
  and `Stack Overflow <https://stackoverflow.com/questions/45419020/what-will-happen-if-pragma-push-macro-without-pragma-pop-macro>`_ .

  This can be done at ``cpip.core.PpLexer.PpLexer._cppPragma`` which calls the pragma handler.
  Perhaps need a new pragma handler ``class PragmaHandlerGNU(PragmaHandlerSTDC)`` that handles these extensions?
  Need to and a pushed map to ``cpip.core.MacroEnv.MacroEnv`` and an API ``push_macro()`` and ``pop_macro()``.


See GNU extensions below.

Effort: Low/Medium.

-----------
``_Pragma``
-----------

Introduced in C99.
We are not conforming to C99/C23 with ``_Pragma``.
See section 5.1.1.2 translation phase 4 in both standards.
See also C99 specification "6.10.9 Pragma operator".

See also `GCC Pragmas <https://gcc.gnu.org/onlinedocs/cpp/Pragmas.html>`_

See GNU extensions below.

.. code-block:: bash

    $ cpp --version
    Apple clang version 15.0.0 (clang-1500.0.40.1)
    Target: x86_64-apple-darwin22.6.0
    Thread model: posix
    InstalledDir: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin
    $ cpp -E
    _Pragma("GCC dependency \"parse.y\"")
    # 1 "<stdin>"
    # 1 "<built-in>" 1
    # 1 "<built-in>" 3
    # 383 "<built-in>" 3
    # 1 "<command line>" 1
    # 1 "<built-in>" 2
    # 1 "<stdin>" 2
    #pragma  GCC dependency "parse.y"
    # 1 "<stdin>"

Note: This fails with a space after ``_Pragma``:

.. code-block:: bash

    $ cpp -E
    _Pragma ("GCC dependency \"parse.y\"")
    # 1 "<stdin>"
    # 1 "<built-in>" 1
    # 1 "<built-in>" 3
    # 383 "<built-in>" 3
    # 1 "<command line>" 1
    # 1 "<built-in>" 2
    # 1 "<stdin>" 2
    <stdin>:1:1: error: _Pragma takes a parenthesized string literal
    _Pragma ("GCC dependency \"parse.y\"")
    ^
     ("GCC dependency \"parse.y\"")

    1 error generated.

Although running that code in `godbolt <https://www.godbolt.org>`_ with clang 15.0.0 does not give that error.

Effort: Medium.

-----------------
Predefined Macros
-----------------

Are we complying with these
`predefined macros <https://en.cppreference.com/w/c/preprocessor/replace#Predefined_macros>`_ ?

Effort: Low.

-------------------------
``import`` and ``export``
-------------------------

Do we support this since C++20: https://en.cppreference.com/w/cpp/language/modules

No, there is no mention of ``import`` or ``export`` in the C23 standard.

Effort: None.

----------------------
Support GNU Extensions
----------------------

Do we support `Extensions to the C Language Family <https://gcc.gnu.org/onlinedocs/gcc/C-Extensions.html>`_ ?

Currently only `#include_next <https://gcc.gnu.org/onlinedocs/cpp/Wrapper-Headers.html>`_ is supported.

It would be extremely tedious to tie our support to specific GCC versions.
Instead support all the latest GNU extensions regardless of the C standard specified.

GNU `extensions <https://gcc.gnu.org/onlinedocs/gcc/C-Extensions.html>`_ that affect the pre-processor.

* 6.23 `Macros with a Variable Number of Arguments <https://gcc.gnu.org/onlinedocs/gcc/Variadic-Macros.html>`_
* 6.24 `Slightly Looser Rules for Escaped Newlines <https://gcc.gnu.org/onlinedocs/gcc/Escaped-Newlines.html>`_
* 6.43 `C++ Style Comments <https://gcc.gnu.org/onlinedocs/gcc/C_002b_002b-Comments.html>`_
  C99 onwards.
* 6.45 `The Character ESC in Constants <https://gcc.gnu.org/onlinedocs/gcc/Character-Escapes.html>`_ ?
* How far do we go with 6.67 `Pragmas Accepted by GCC <https://gcc.gnu.org/onlinedocs/gcc/Pragmas.html>`_ ?
* 6.70 `Binary Constants using the ‘0b’ Prefix <https://gcc.gnu.org/onlinedocs/gcc/Binary-constants.html>`_
  C99 onwards.

Effort: Medium.

---------------------
Macro Replacement Bug
---------------------

Given this:

.. code-block:: c

    #define f(a) a*g
    #define g(a) f(a)
    f(2)(9)

The steps are:

1. ``f(2)`` expands to ``2*g`` and ``g`` is a *possible* macro replacement.
2. Now consume and append ``(9)`` which is a certain macro replacement so we have ``g(9)``.
3. Reevaluate ``g(9)`` which expands to ``f(9)``
4. Reevaluate ``f(9)`` which expands to ``9*g``
5. The evaluation halts at token ``g`` as that can not be expanded as ``g`` requires a function like macro.

We get ``2*f(9)``, which is legal, but GCC/Clang/MSVC produce ``2*9*g``.
So we are missing step 4.

There is one test for this in ``tests.unit.test_core.test_MacroEnv.TestFromStandardMisc.test_ambiguos_01()`` and
another in ``tests.unit.test_core.test_PpLexer.TestC99Rationale.test_6_10_3_4_01()``.

The relevant code is ``cpip.core.MacroEnv.MacroEnv._expand()`` and the recursive call here
``reexTokS += self._expand(next(myGen), myGen, theFileLineCol)`` at ``src/cpip/core/MacroEnv.py:599`` which is failing
to expand ``f()`` a second time.

Also how well do we do with recursion?:

.. code-block:: bash

    $ cpp -E
    #define A(x) B(x)
    #define B(x) A(x)
    A(8)
    # 1 "<stdin>"
    # 1 "<built-in>" 1
    # 1 "<built-in>" 3
    # 384 "<built-in>" 3
    # 1 "<command line>" 1
    # 1 "<built-in>" 2
    # 1 "<stdin>" 2


    A(8)

There are tests for *object* like macros in ``tests.unit.test_core.test_MacroEnv.TestMacroEnvCycles``.

Effort: Medium.

------------------
Move this Document
------------------

This document contains a lot of useful information about standards and CPIP's compliance.
This information should moved to a specific chapter in the documentation.

Effort: Low.

------------------
Indexing
------------------

Hand index essential information, not just the reference section.

Effort: Medium.

Effort Summary
==============

=================================================================== ============
Item                                                                Effort
=================================================================== ============
Standard Support Class                                              High
Removing Trigraphs                                                  Low
``#elifdef`` and ``#elifndef`` directives                           Medium
``#embed``                                                          High+
``#warning``                                                        Low
``__has_include``                                                   Medium
``__has_c_attribute``                                               Medium/High
``__VA_OPT__``                                                      Medium
Miscellaneous/Source Code References to Standards                   Low
Miscellaneous/``#pragma``                                           Low/Medium
Miscellaneous/``_Pragma``                                           Medium
Miscellaneous/Predefined Macros                                     Low
Miscellaneous/``import`` and ``export``                             None
Miscellaneous/Support GNU Extensions                                Medium
Miscellaneous/Macro Replacement Bug                                 Medium
Miscellaneous/Move this Document                                    Low
Indexing                                                            Medium
=================================================================== ============

Totals:

=========   ======
Effort      Items
=========   ======
Low         5.5
Medium      8
High        1.5
High+       1
=========   ======

If Medium = 2 * Low, High = 2 * Medium, High+ = 2 * High then we have: 5.5 + 16 + 6 + 8 Low values = 35.5


Notes
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

-------
Sources
-------

GNU/GCC
----------------

* `Standard support <https://gcc.gnu.org/onlinedocs/gcc/Standards.html>`_
* `Extensions to the C Language Family <https://gcc.gnu.org/onlinedocs/gcc/C-Extensions.html>`_
* `GCC C options <https://gcc.gnu.org/onlinedocs/gcc/C-Dialect-Options.html>`_
* `Status of C99 features in GCC <https://gcc.gnu.org/c99status.html>`_

Clang
-----------

* `C Support in Clang <https://clang.llvm.org/c_status.html>`_
* `Language standards <https://github.com/llvm/llvm-project/blob/main/clang/include/clang/Basic/LangStandards.def>`_

Microsoft Visual Studio
------------------------

* `C/C++ Support <https://learn.microsoft.com/en-us/cpp/overview/visual-cpp-language-conformance?view=msvc-170>`_
* `/std: values <https://learn.microsoft.com/en-us/cpp/build/reference/std-specify-language-standard-version?view=msvc-170>`_

godbolt.org
----------------------

* `Online compiler <https://www.godbolt.org>`_ . Set the compiler flag ``-E`` (or ``/E`` for Visual Studio) for the
  preprocessor output.

Wikipedia
---------------------

* `General C <https://en.wikipedia.org/wiki/C_(programming_language)>`_
* `K&R C <https://en.wikipedia.org/wiki/K%26R_C>`_
* `ANSI C/ISO C/C89/C90 <https://en.wikipedia.org/wiki/ANSI_C>`_
* `C95 <https://en.wikipedia.org/wiki/ANSI_C#C95>`_
* `C99 <https://en.wikipedia.org/wiki/C99>`_
* `C11 <https://en.wikipedia.org/wiki/C11_(C_standard_revision)>`_
* `C17/C18 <https://en.wikipedia.org/wiki/C17_(C_standard_revision)>`_
* `C23 <https://en.wikipedia.org/wiki/C23_(C_standard_revision)>`_


Other
-----------

* Definition of `__STDC_VERSION__ and __STDC__ <https://sourceforge.net/p/predef/wiki/Standards/>`_ for various
  standards.
* CPP reference on the `C Preprocessor <https://en.cppreference.com/w/c/preprocessor>`_.
* CPP reference on the `C history <https://en.cppreference.com/w/c/preprocessor>`_ with links to standards documents.
* The `rationale <https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf>`_ for the C99 standard.
* `nsz <https://port70.net/~nsz/c/>`_ has a great collated set of standards that can be obtained by:

  ``wget -r -np -k -e robots=off https://port70.net/\~nsz/c/``

  This also has text versions of the standard which can be handy for diffing and copy/pasting since some PDFs prevent
  copying without the owners password.

nsz Tree
^^^^^^^^^^^^^^^^^^^

This is the file tree of `nsz <https://port70.net/~nsz/c/>`_:

.. code-block:: text

    $ tree ~/Documents/standards/C_CPP_ProgrammingLanguage/nsz/c/port70.net/~nsz/c
    Documents/standards/C_CPP_ProgrammingLanguage/nsz/c/port70.net/~nsz/c
    ├── c++
    │   ├── c++03_final.pdf
    │   ├── c++03_final.txt
    │   ├── c++03_n1804.pdf
    │   ├── c++03_n1804.txt
    │   ├── c++11_n3337.pdf
    │   ├── c++11_n3337.txt
    │   ├── c++14_n3797.pdf
    │   ├── c++14_n3797.txt
    │   ├── c++14_n3936.pdf
    │   ├── c++14_n3936.txt
    │   ├── c++14_n3936.txt.gz
    │   ├── c++98.pdf
    │   ├── c++98.txt
    │   ├── cdiffs.htm
    │   ├── index.html
    │   ├── keywords.txt
    │   ├── limits.txt
    │   ├── siblings_short.pdf
    │   └── turing.pdf
    ├── c11
    │   ├── ctypes.pdf
    │   ├── index.html
    │   ├── n1570.html
    │   ├── n1570.pdf
    │   ├── n1570.pre.html
    │   └── n1570.txt
    ├── c1x
    │   ├── index.html
    │   └── n1548.html
    ├── c23
    │   ├── index.html
    │   ├── n3096.pdf
    │   └── n3220.pdf
    ├── c2x
    │   ├── html.txt
    │   ├── index.html
    │   ├── n2434.pdf
    │   └── n3047.pdf
    ├── c89
    │   ├── c89-draft.html
    │   ├── c89-draft.txt
    │   ├── c94_na1.html
    │   ├── c9x_changes.html
    │   ├── dmr-on-noalias.html
    │   ├── dmr_the_development_of_the_c_language.pdf
    │   ├── index.html
    │   ├── longlong.html
    │   ├── rationale
    │   │   ├── a.html
    │   │   ├── b.html
    │   │   ├── c1.html
    │   │   ├── c2.html
    │   │   ├── c3.html
    │   │   ├── c4.html
    │   │   ├── c5.html
    │   │   ├── c6.html
    │   │   ├── c7.html
    │   │   ├── c8.html
    │   │   ├── c9.html
    │   │   ├── d1.html
    │   │   ├── d10.html
    │   │   ├── d11.html
    │   │   ├── d12.html
    │   │   ├── d13.html
    │   │   ├── d2.html
    │   │   ├── d3.html
    │   │   ├── d4.html
    │   │   ├── d5.html
    │   │   ├── d6.html
    │   │   ├── d7.html
    │   │   ├── d8.html
    │   │   ├── d9.html
    │   │   ├── e.html
    │   │   ├── index.html
    │   │   └── title.html
    │   ├── rationale.dvi
    │   ├── rationale.latex.tar.Z
    │   └── rationale.pdf
    ├── c99
    │   ├── C99RationaleV5.10.pdf
    │   ├── index.html
    │   ├── n1256.html
    │   ├── n1256.pdf
    │   ├── n1256.pre.html
    │   └── n1256.txt
    ├── index.html
    └── posix
        ├── README
        ├── README.txt
        ├── headers.txt
        ├── includes.txt
        ├── index.html
        └── reserved.txt
