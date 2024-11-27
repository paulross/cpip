
==============
Supporting C23
==============

The C23 standard makes several changes to to preprocessor, a summary is here on
`Wikipedia <https://en.wikipedia.org/wiki/C23_(C_standard_revision)#Preprocessor>`_
The C23 standard can be found as an open access draft from
`www.open-std.org <https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf>`_

This document describes the impact on CPIP version 0.9.9, and moving to a superior version.


General
====================

CPIP is based on C99 (ISO/IEC 9899:1999 (E)) that is invariant.

The move to C23 suggests that CPIP should have a global configuration such that C23 is supported, and perhaps at a more
granular level.

Internally this could be represented as a class representing a tree such as:

.. code-block::  python

    {
        'C23' : {
            'N2940'  : ('Trigraphs', True),
            'N3017'  : ('#embed', False),
            'XXXXX'  : ('XXXXX', 42),
        }
    }

An API would be to retrieve this information from, for example: ``get('C23.N2940')``.

For ``cpip/CPIPMain.py`` this could be implemented as an option ``--cfg C23.N2940=True`` which will be additive.
Could specify ``--cfg C23`` to apply all C23 defaults.

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
^^^^^^^^^^^^^^^^^^^^^^

Trigraphs are processed here: ``cpip.core.ItuToTokens.ItuToTokens._translatePhase_1()`` and
``cpip.core.PpTokeniser.PpTokeniser._translateTrigraphs()``

This seems like a candidate for a configurable parser when the PpTokeniser takes a configuration option (or class).

Effort: Low.

``#elifdef`` and ``#elifndef`` directives
=========================================

The proposal is here, with examples,
`WG14-N2645 (archived) <https://web.archive.org/web/20221128133337/https://open-std.org/JTC1/SC22/WG14/www/docs/n2645.pdf>`_.

Solution and Impact
^^^^^^^^^^^^^^^^^^^^^^

This can be supported (fully?) in ``cpip/core/CppCond.py`` with appropriate tests.

Effort: Medium.

``#embed``
==========

This includes binary files such as images:
`Wikipedia on #embed <https://en.wikipedia.org/wiki/C_preprocessor#Binary_resource_inclusion>`_.

As the Wikipedia page describes, the binary resource gets included in the manner of ``xxd -i``.
For example:

.. code-block:: bash

    xxd -i dist/cpip-0.9.9-py2.py3-none-any.whl

Gives:

.. code-block:: c

    unsigned char dist_cpip_0_9_9_py2_py3_none_any_whl[] = {
    /* This is what #embed expands to. */
      0x50, 0x4b, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x08, 0x00, 0x30, 0x98,
      0x48, 0x58, 0xc2, 0x2f, 0xc7, 0x97, 0x2e, 0x3b, 0x00, 0x00, 0xf1, 0x08,
      0x01, 0x00, 0x10, 0x00, 0x00, 0x00, 0x63, 0x70, 0x69, 0x70, 0x2f, 0x43,
      0x50, 0x49, 0x50, 0x4d, 0x61, 0x69, 0x6e, 0x2e, 0x70, 0x79, 0xed, 0x7d,
      0x6b, 0x77, 0xe3, 0x36, 0x92, 0xe8, 0x77, 0xff, 0x0a, 0x8c, 0x7d, 0xfb,
      0x4a, 0x9a, 0xc8, 0xb4, 0xdd, 0x9d, 0xa7, 0x12, 0xf5, 0xac, 0x63, 0xbb,
    /* Snip */
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
^^^^^^^^^^^^^^^^^^^^^^

Perhaps needs an ``EmbedHandler.py`` similar to ``cpip/core/IncludeHandler.py``
with appropriate tests?

.. note::

    From the `standard <https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf>`_
    6.10.4.1 Description note 14: "A mechanism similar to, but distinct from, the implementation-defined search paths
    used for source file inclusion (6.10.3) is encouraged."

Other notes:

* ``#embed``: See 6.10.4.1 #embed preprocessing directive.
* ``__has_embed`` is in the standard. See 6.10.2 Conditional inclusion.
* ``__STDC_EMBED_NOT_FOUND__``, ``__STDC_EMBED_FOUND__``, ``__STDC_EMBED_EMPTY__`` must be respected.
   See 6.10.2 Conditional inclusion.

Effort: High+. We don't (yet) have a compiler that supports this for testing.
See 6.10.4.1 #embed preprocessing directive which is complex.

``#warning``
============

Adds warning messages, similar to ``#error``.

The proposal is here:
`WG14-N2686 (archived) <https://web.archive.org/web/20221128133337/https://open-std.org/JTC1/SC22/WG14/www/docs/n2686.pdf>`_.

Solution and Impact
^^^^^^^^^^^^^^^^^^^^^^

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

Solution and Impact
^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^

Affects:

* Predefined macros since ``__has_c_attribute`` is a predefined, function like, macro.
* Probably several other places as this macro queries the preprocessing environment.

Effort: Medium to high.

``__VA_OPT__``
==============

The proposal is here, with examples,
`WG14-N3033 (archived) <https://web.archive.org/web/20221227031727/https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3033.htm>`_.

Solution and Impact
^^^^^^^^^^^^^^^^^^^^^^

This mainly affects ``cpip.core.PpDefine.PpDefine`` and the appropriate tests.
The change should be contained by that class as it is really to use a different set of rules for macro expansion.
And, of course, the appropriate tests.

Effort: Medium.

Other
===============
