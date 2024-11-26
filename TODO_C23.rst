Supporting C23
==============

The C23 standard makes several changes to to preprocessor.

A summary is here on
`Wikipedia <https://en.wikipedia.org/wiki/C23_(C_standard_revision)#Preprocessor>`_

The C23 standard can be found in as open access draft form
`www.open-std.org <https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf>`_

This document describes the impact on CPIP.

``#elifdef`` and ``#elifndef`` directives
-------------------------------------------

The proposal is here, with examples,
`WG14-N2645 (archived) <https://web.archive.org/web/20221128133337/https://open-std.org/JTC1/SC22/WG14/www/docs/n2645.pdf>`_.

Solution and Impact
^^^^^^^^^^^^^^^^^^^^^^

This can be supported (fully?) in ``cpip/core/CppCond.py`` with appropriate tests.

``#embed``
-----------

This includes binary files such as images:
`Wikipedia <https://en.wikipedia.org/wiki/C_preprocessor#Binary_resource_inclusion>`_.

As the Wikipedia page describes, the binary resource gets included in the manner of ``xxd -i``.
For example ``cpip git:(C23) ✗ xxd -i dist/cpip-0.9.9-py2.py3-none-any.whl``:

.. code-block:: c

    unsigned char dist_cpip_0_9_9_py2_py3_none_any_whl[] = {
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
    };
    unsigned int dist_cpip_0_9_9_py2_py3_none_any_whl_len = 90123;

The proposal is here, with examples,
`WG14-N3017 (archived) <https://web.archive.org/web/20221224045304/https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3017.htm>`_.

Solution and Impact
^^^^^^^^^^^^^^^^^^^^^^

Perhaps needs an ``EmbedHandler.py`` similar to ``cpip/core/IncludeHandler.py``
with appropriate tests?

``#warning``
-------------

Adds warning messages, similar to ``#error``.

The proposal is here, with examples,
`WG14-N2686 (archived) <https://web.archive.org/web/20221128133337/https://open-std.org/JTC1/SC22/WG14/www/docs/n2686.pdf>`_.


Solution and Impact
^^^^^^^^^^^^^^^^^^^^^^

Already supported in ``cpip/core/CppDiagnostic.py``.
See also ``cpip.core.PpLexer.PpLexer._cppWarning``.

Check this.

Check appropriate tests should be in ``tests/unit/test_core/test_CppDiagnostic.py`` and
``tests/unit/test_core/test_PpLexer.py``.

TODO:

* ``__has_include``
* ``__has_c_attribute``
* ``__VA_OPT__``
