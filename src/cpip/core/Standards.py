#!/usr/bin/env python
# CPIP is a C/C++ Preprocessor implemented in Python.
# Copyright (C) 2008-2025 Paul Ross
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Paul Ross: apaulross@gmail.com

"""
Provides standards information and standards support.
"""
import os.path
import sys
import typing


class Standards:
    #: These are our 'generic' standards in historical order.
    #: This allows selecting future support.
    #: For example trigraphs were discontinued from C23 onwards so has_trigraphs(self) can be implemented as:
    #: self.GENERIC_STANDARDS.index(self.generic_standard_name) < self.GENERIC_STANDARDS.index('C23')
    GENERIC_STANDARDS = ['K&R', 'ANSI', 'C90', 'C95', 'C99', 'C11', 'C17/C18', 'C23', ]
    #: This allows the caller to construct an instance of this class with a generic standard and then
    #: query that instance for has_... methods for example when generating a .rst file.
    GENERIC_STANDARD_ARGUMENT = {
        'K&R': 'k&r',
        'ANSI': 'ansi',
        'C90': 'c90',
        'C95': 'c95',
        'C99': 'c99',
        'C11': 'c11',
        'C17/C18': 'c17',
        'C23': 'c23',
    }
    #: Dict of ``{--std : generic_standard, ...}``
    C_STANDARDS_SUPPORTED = {
        # Original K&R
        'k&r': 'K&R',
        # Generic ANSI
        'ansi': 'ANSI',
        'c89': 'ANSI',
        # C90 is really no different to ANSI but we make the distinction here as the standards document is different.
        'c90': 'C90',
        'iso9899:1990': 'C90',
        'iso9899:199409': 'C95',
        # C95
        'c95': 'C95',
        # C99
        'c99': 'C99',
        'c9x': 'C99',
        'iso9899:1999': 'C99',
        'iso9899:199x': 'C99',
        # C11
        'c11': 'C11',
        'c1x': 'C11',
        'iso9899:2011': 'C11',
        # C17/C18
        'c17': 'C17/C18',
        'c18': 'C17/C18',
        'iso9899:2017': 'C17/C18',
        'iso9899:2018': 'C17/C18',
        # C23
        'c23': 'C23',
        'c2x': 'C23',
        'iso9899:2024': 'C23',
    }
    #: Is ``__STDC__`` pre-defined.
    STDC = {
        'K&R': False,
        'ANSI': True,
        'C90': True,
        'C95': True,
        'C99': True,
        'C11': True,
        'C17/C18': True,
        'C23': True,
    }
    #: Dict of ``{generic_standard : __STDC_VERSION__, ...}``
    STDC_VERSION = {
        'K&R': '',
        'ANSI': '',
        'C90': '',
        'C95': '199409L',
        'C99': '199901L',
        'C11': '201112L',
        'C17/C18': '201710L',
        'C23': '202311L',
    }
    #: Dict of ``{__STDC_VERSION__ : generic_standard, ...}``
    #: This allows specifying the ``__STDC_VERSION__`` on construction.
    STD_VERSION_REVERSED = {_v: _k for _k, _v in STDC_VERSION.items() if _v}
    #: Dict of ``{generic_standard : document_reference, ...}``
    C_STANDARDS_DOCUMENT = {
        'K&R': 'The C Programming Language, Kernighan and Ritchie, First Edition, ISBN 9780131101630',
        'ANSI': 'ANSI X3.159-1989',
        # C90 is really no different to ANSI, but we make the distinction here as the standards
        # document reference is different.
        'C90': 'ISO/IEC 9899:1990',
        'C95': 'ISO/IEC 9899-1:1994, ISO/IEC 9899:1990/AMD1:1995',
        'C99': 'ISO/IEC 9899:1999',
        'C11': 'ISO/IEC 9899:2011',
        'C17/C18': 'ISO/IEC 9899:2018',
        'C23': 'ISO/IEC 9899:2024',
    }
    #: Dict of ``{generic_standard : text, ...}``
    C_STANDARDS_NOTES = {
        'K&R': 'Not an internationally recognised standard.',
        'ANSI': 'This is really no different to C89 and C90.',
        'C90': 'This is really no different to ANSI C.',
        'C95': 'C90 unamended by ISO/IEC 9899:1990/AMD1:1995.',
    }
    # This declares some conditional macros that are mentioned in the standard and that user might want to use.
    # The CLI help and the documentation could use this.
    CONDITIONALLY_DEFINED_FEATURE_MACROS = {
        # K&R: Nothing

        # ANSI (C89)
        # From nsz/c/port70.net/~nsz/c/c89/
        # "3.8.8 Predefined macro names" there is nothing except __FILE__ etc.
        # Otherwise, nothing.

        # C90: Nothing

        # From n1256.pdf 6.10.8 Predefined macro names
        'C99': {
            '__STDC_HOSTED__': 'The integer constant 1 if the implementation is a hosted implementation or the'
                               ' integer constant 0 if it is not.',
            '__STDC_MB_MIGHT_NEQ_WC__': 'The integer constant 1, intended to indicate that, in the encoding for'
                                        ' wchar_t, a member of the basic character set need not have a code value equal'
                                        ' to its value when used as the lone character in an integer character'
                                        ' constant.',
            # "The following macro names are conditionally defined by the implementation:"
            '__STDC_IEC_559__': 'The integer constant 1, intended to indicate conformance to the specifications in'
                                ' annex F (IEC 60559 floating-point arithmetic).',
            '__STDC_IEC_559_COMPLEX__': 'The integer constant 1, intended to indicate adherence to the specifications'
                                        ' in informative annex G (IEC 60559 compatible complex arithmetic).',
            '__STDC_ISO_10646__': 'An integer constant of the form yyyymmL (for example, 199712L).'
                                  'If this symbol is defined, then every character in the Unicode required set, when'
                                  ' stored in an object of type wchar_t, has the same value as the short identifier of'
                                  ' that character.'
                                  ' The Unicode required set consists of all the characters that are defined by'
                                  ' ISO/IEC 10646, along with all amendments and technical corrigenda, as of the'
                                  ' specified year and month.',
        },

        # C11
        # From "N1570 Committee Draft — April 12, 2011 ISO/IEC 9899:201x" section "6.10.8 Predefined macro names"
        'C11': {
            # "The following macro names shall be defined by the implementation:"
            '__STDC_HOSTED__': 'The integer constant 1 if the implementation is a hosted implementation or the'
                               ' integer constant 0 if it is not.',
            '__STDC_ISO_10646__': 'An integer constant of the form yyyymmL (for example,'
                                  ' 199712L). If this symbol is defined, then every character in the Unicode'
                                  ' required set, when stored in an object of type wchar_t, has the same'
                                  ' value as the short identifier of that character. The Unicode required set'
                                  ' consists of all the characters that are defined by ISO/IEC 10646, along with'
                                  ' all amendments and technical corrigenda, as of the specified year and'
                                  ' month. If some other encoding is used, the macro shall not be defined and'
                                  ' the actual encoding used is implementation-defined.',
            '__STDC_MB_MIGHT_NEQ_WC__': 'The integer constant 1, intended to indicate that, in'
                                        ' the encoding for wchar_t, a member of the basic character set need not'
                                        ' have a code value equal to its value when used as the lone character in an'
                                        ' integer character constant.',
            '__STDC_UTF_16__': 'The integer constant 1, intended to indicate that values of type'
                               ' char16_t are UTF-16 encoded. If some other encoding is used, the'
                               ' macro shall not be defined and the actual encoding used is implementation-'
                               ' defined.',
            '__STDC_UTF_32__': 'The integer constant 1, intended to indicate that values of type'
                               ' char32_t are UTF-32 encoded. If some other encoding is used, the'
                               ' macro shall not be defined and the actual encoding used is implementation-'
                               ' defined.',
            # "The following macro names are conditionally defined by the implementation:"
            '__STDC_ANALYZABLE__': 'The integer constant 1, intended to indicate conformance to'
                                   ' the specifications in annex L (Analyzability).',
            '__STDC_IEC_559__': 'The integer constant 1, intended to indicate conformance to the'
                                ' specifications in annex F (IEC 60559 floating-point arithmetic).',
            '__STDC_IEC_559_COMPLEX__': 'The integer constant 1, intended to indicate'
                                        ' adherence to the specifications in annex G (IEC 60559 compatible complex'
                                        ' arithmetic).',
            '__STDC_LIB_EXT1__': 'The integer constant 201ymmL, intended to indicate support'
                                 ' for the extensions defined in annex K (Bounds-checking interfaces).179)',
            '__STDC_NO_ATOMICS__': 'The integer constant 1, intended to indicate that the'
                                   ' implementation does not support atomic types (including the _Atomic'
                                   ' type qualifier) and the <stdatomic.h> header.',
            '__STDC_NO_COMPLEX__': 'The integer constant 1, intended to indicate that the'
                                   ' implementation does not support complex types or the <complex.h>'
                                   ' header.',
            '__STDC_NO_THREADS__': 'The integer constant 1, intended to indicate that the'
                                   ' implementation does not support the <threads.h> header.',
            '__STDC_NO_VLA__': 'The integer constant 1, intended to indicate that the'
                               ' implementation does not support variable length arrays or variably'
                               ' modified types.',
            None: 'An implementation that defines ``__STDC_NO_COMPLEX__`` shall not define'
                  ' ``__STDC_IEC_559_COMPLEX__``.',
        },
        # From ISO/IEC 9899:2017 C17 ballot N2176
        'C17/C18': {
            # 6.10.8.1 Mandatory macros
            # "The following macro names shall be defined by the implementation:"
            '__STDC_HOSTED__': 'The integer constant 1 if the implementation is a hosted implementation or the'
                               ' integer constant 0 if it is not.',
            # 6.10.8.2 Environment macros
            # "The following macro names are conditionally defined by the implementation:"
            '__STDC_ISO_10646__': 'An integer constant of the form yyyymmL (for example,'
                                  ' 199712L). If this symbol is defined, then every character in the Unicode'
                                  ' required set, when stored in an object of type wchar_t, has the same'
                                  ' value as the short identifier of that character. The Unicode required set'
                                  ' consists of all the characters that are defined by ISO/IEC 10646, along with'
                                  ' all amendments and technical corrigenda, as of the specified year and'
                                  ' month. If some other encoding is used, the macro shall not be defined and'
                                  ' the actual encoding used is implementation-defined.',
            '__STDC_MB_MIGHT_NEQ_WC__': 'The integer constant 1, intended to indicate that, in'
                                        ' the encoding for wchar_t, a member of the basic character set need not'
                                        ' have a code value equal to its value when used as the lone character in an'
                                        ' integer character constant.',
            '__STDC_UTF_16__': 'The integer constant 1, intended to indicate that values of type'
                               ' char16_t are UTF-16 encoded. If some other encoding is used, the'
                               ' macro shall not be defined and the actual encoding used is implementation-'
                               ' defined.',
            '__STDC_UTF_32__': 'The integer constant 1, intended to indicate that values of type'
                               ' char32_t are UTF-32 encoded. If some other encoding is used, the'
                               ' macro shall not be defined and the actual encoding used is implementation-'
                               ' defined.',
            # 6.10.8.3 Conditional feature macros
            # "The following macro names are conditionally defined by the implementation:"
            '__STDC_ANALYZABLE__': 'The integer constant 1, intended to indicate conformance to'
                                   ' the specifications in annex L (Analyzability).',
            '__STDC_IEC_559__': 'The integer constant 1, intended to indicate conformance to the'
                                ' specifications in annex F (IEC 60559 floating-point arithmetic).',
            '__STDC_IEC_559_COMPLEX__': 'The integer constant 1, intended to indicate'
                                        ' adherence to the specifications in annex G (IEC 60559 compatible complex'
                                        ' arithmetic).',
            '__STDC_LIB_EXT1__': 'The integer constant 201ymmL, intended to indicate support'
                                 ' for the extensions defined in annex K (Bounds-checking interfaces).179)',
            '__STDC_NO_ATOMICS__': 'The integer constant 1, intended to indicate that the'
                                   ' implementation does not support atomic types (including the _Atomic'
                                   ' type qualifier) and the <stdatomic.h> header.',
            '__STDC_NO_COMPLEX__': 'The integer constant 1, intended to indicate that the'
                                   ' implementation does not support complex types or the <complex.h>'
                                   ' header.',
            '__STDC_NO_THREADS__': 'The integer constant 1, intended to indicate that the'
                                   ' implementation does not support the <threads.h> header.',
            '__STDC_NO_VLA__': 'The integer constant 1, intended to indicate that the'
                               ' implementation does not support variable length arrays or variably'
                               ' modified types.',
            None: 'An implementation that defines ``__STDC_NO_COMPLEX__`` shall not define'
                  ' ``__STDC_IEC_559_COMPLEX__``.',
        },

        # From n3220.pdf 6.10.10.4 Conditional feature macros
        'C23': {
            '__STDC_ANALYZABLE__': 'The integer constant 1, if the implementation conforms to the specifications'
                                   ' in Annex L (Analyzability).',
            '__STDC_IEC_60559_BFP__': 'The integer constant 202311L, intended to indicate conformance to Annex F'
                                      ' (ISO/IEC 60559 floating-point arithmetic) for binary floating-point'
                                      ' arithmetic.',
            '__STDC_IEC_559__': 'The integer constant 1, intended to indicate conformance to the specifications in'
                                ' Annex F (ISO/IEC 60559 floating-point arithmetic) for binary floating-point arithmetic.'
                                ' Use of this macro is an obsolescent feature.',
            '__STDC_IEC_60559_DFP__': 'The integer constant 202311L, intended to indicate support of decimal floating'
                                      ' types and conformance to Annex F (ISO/IEC 60559 floating-point arithmetic) for'
                                      ' decimal floating-point arithmetic.',
            '__STDC_IEC_60559_COMPLEX__': 'The integer constant 202311L, intended to indicate conformance to the'
                                          ' specifications in Annex G (ISO/IEC 60559 compatible complex arithmetic).',
            '__STDC_IEC_60559_TYPES__': 'The integer constant 202311L, intended to indicate conformance to the'
                                        ' specification in Annex H (ISO/IEC 60559 interchange and extended types).',
            '__STDC_IEC_559_COMPLEX__': 'The integer constant 1, intended to indicate adherence to the specifications'
                                        ' in Annex G (ISO/IEC 60559 compatible complex arithmetic).'
                                        ' Use of this macro is an obsolescent feature.',
            '__STDC_LIB_EXT1__': 'The integer constant 202311L, intended to indicate support for the extensions'
                                 ' defined in Annex K (Bounds-checking interfaces).',
            '__STDC_NO_ATOMICS__': 'The integer constant 1, intended to indicate that the implementation does not'
                                   ' support atomic types (including the _Atomic type qualifier) and the <stdatomic.h>'
                                   ' header.',
            '__STDC_NO_COMPLEX__': 'The integer constant 1, intended to indicate that the implementation does not'
                                   ' support complex types or the <complex.h> header.',
            '__STDC_NO_THREADS__': 'The integer constant 1,intended to indicate that the implementation does not'
                                   ' support the <threads.h> header.',
            '__STDC_NO_VLA__': 'The integer constant 1, intended to indicate that the implementation does not support'
                               ' variable length arrays with automatic storage duration.'
                               ' Parameters declared with variable length array types are adjusted and then define'
                               ' objects of automatic storage duration with pointer types.'
                               ' Thus, support for such declarations is mandatory.',
            None: 'The intention for the macros ``__STDC_LIB_EXT1__``, ``__STDC_IEC_60559_BFP__``,'
                  ' ``__STDC_IEC_60559_DFP__``, ``__STDC_IEC_60559_COMPLEX__``, and ``__STDC_IEC_60559_TYPES__``,'
                  ' with the value 202311L, is that this will remain an integer constant of type long int that is'
                  ' increased with each revision of this document.'
                  ' An implementation that defines ``__STDC_NO_COMPLEX__`` shall not define'
                  ' ``__STDC_IEC_60559_COMPLEX__`` or ``__STDC_IEC_559_COMPLEX__``.'
        },
    }

    def __init__(self, standard: str, gnu_extensions: bool):
        """Constructor.

        :param standard: The C standard to use as standard code or the ``__STDC_VERSION__``.
            For example 'c99' or '199901L'.
        :param gnu_extensions: See Extensions to the C Language Family
            https://gcc.gnu.org/onlinedocs/gcc/C-Extensions.html
        """
        # Check and raise ValueError if appropriate.
        if standard in self.STD_VERSION_REVERSED:
            generic_standard = self.STD_VERSION_REVERSED[standard]
            self.standard = self.GENERIC_STANDARD_ARGUMENT[generic_standard]
        else:
            if standard not in self.C_STANDARDS_SUPPORTED:
                raise ValueError(f'Unknown standard {standard}')
            self.standard = standard
        self.gnu_extensions = gnu_extensions

    def __str__(self) -> str:
        return f'{self.__class__}: Std: {self.standard} GNU: {self.gnu_extensions}'

    @property
    def generic_standard_name(self) -> str:
        return self.C_STANDARDS_SUPPORTED[self.standard]

    def stdc_version(self) -> str:
        return self.STDC_VERSION[self.generic_standard_name]

    def has_digraphs(self) -> bool:
        """Digraphs supported"""
        return self.generic_standard_name not in {'K&R', 'ANSI', }

    def has_va_args(self) -> bool:
        """``__VA_ARGS__`` supported"""
        return self.generic_standard_name not in {'K&R', }

    def has_cpp_style_comments(self) -> bool:
        """C++ style comments supported"""
        return self.generic_standard_name not in {'K&R', 'ANSI', 'C90'}

    # C23 onwards.
    def _is_c23_onwards(self) -> bool:
        """Is this C23 or beyond?"""
        return self.GENERIC_STANDARDS.index(self.generic_standard_name) >= self.GENERIC_STANDARDS.index('C23')

    def has_trigraphs(self) -> bool:
        """Trigraphs supported"""
        return not self._is_c23_onwards()

    def has_elifdef(self) -> bool:
        """``#elifdef`` supported"""
        return self._is_c23_onwards()

    def has_elifndef(self) -> bool:
        """``#elifndef`` supported"""
        return self._is_c23_onwards()

    def has_embed(self) -> bool:
        """``#embed`` supported"""
        return self._is_c23_onwards()

    def has_warning(self) -> bool:
        """``#warning`` supported"""
        return self._is_c23_onwards()

    def has_has_include(self) -> bool:
        """``__has_include`` supported"""
        return self._is_c23_onwards()

    def has_has_c_attribute(self) -> bool:
        """``__has_c_attribute`` supported"""
        return self._is_c23_onwards()

    def has_va_opt(self) -> bool:
        """``__VA_OPT__`` supported"""
        return self._is_c23_onwards()

    @classmethod
    def c_standards(cls) -> typing.Dict[str, typing.List[str]]:
        """Returns a dict of {generic_standard : [standard, ...], ...}
        For example {'ANSI' : ['ansi', 'c89'], ...}.
        Useful for creating help text and .rst files."""
        ret = {}
        for std, generic_standard in cls.C_STANDARDS_SUPPORTED.items():
            if generic_standard not in ret:
                ret[generic_standard] = [std]
            else:
                ret[generic_standard].append(std)
        for k in ret:
            ret[k].sort()
        return ret

    @classmethod
    def help_text(cls) -> typing.List[str]:
        ret = []
        c_standards = cls.c_standards()
        for generic_standard in cls.GENERIC_STANDARDS:
            temp = [f'For {generic_standard}']
            if cls.C_STANDARDS_DOCUMENT[generic_standard]:
                temp.append(f'({cls.C_STANDARDS_DOCUMENT[generic_standard]})')
            temp2 = []
            for c_std in c_standards[generic_standard]:
                temp2.append(f'--std={c_std}')
            temp.append(f'Use: {", ".join(temp2)}.')
            ret.append(' '.join(temp))
        return ret


def rst_heading(text: str, overline: str, underline: str) -> typing.List[str]:
    """Create a rst heading."""
    ret = []
    if overline:
        ret.append(f'{f"{overline}" * len(text)}')
    ret.append(f'{text}')
    ret.append(f'{f"{underline}" * len(text)}')
    ret.append('')
    return ret


def rst_simple_table(table: typing.List[typing.List[str]]) -> typing.List[str]:
    """Create a rst simple table. The first row contains the headings."""
    ret = []
    assert len(table) >= 2
    widths = [0] * len(table[0])
    for row in table:
        for c, col in enumerate(row):
            widths[c] = max(widths[c], len(col))
    delimeter_line = ' '.join(['=' * width for width in widths])
    ret.append(delimeter_line)
    ret.append('')
    for c, col in enumerate(table[0]):
        if c > 0:
            ret[-1] = ret[-1] + ' '
        ret[-1] = ret[-1] + f'{table[0][c]:<{widths[c]}}'
    # ret.append('')
    ret.append(delimeter_line)
    # ret.append('')
    for r, row in enumerate(table):
        if r:
            ret.append('')
            for c, col in enumerate(row):
                if c > 0:
                    ret[-1] = ret[-1] + ' '
                ret[-1] = ret[-1] + f'{table[r][c]:<{widths[c]}}'
    ret.append(delimeter_line)
    return ret


def rst_list_table(title: str, widths: typing.List[int], table: typing.List[typing.List[str]]) -> typing.List[str]:
    """Create a rst list-table. The first row contains the headings.
    Example:

    .. list-table:: Recommended Code Directories
       :widths: 10 10 10 10 10 30
       :header-rows: 1

       * - Category
         - Language
         - ``#include <Python.h>``?
         - Testable?
         - Where?
         - Description
       * - Pure Python
         - Python
         - No
         - Yes
         - ``py/``
         - Regular Python code tested by pytest or similar.

    """
    ret = [
        f'.. list-table:: {title}',
        f'   :widths: {" ".join(str(w) for w in widths)}',
        '   :header-rows: 1',
        '',
    ]
    assert len(table) >= 2
    assert len(widths) == len(table[0])
    assert all(len(row) == len(table[0]) for row in table)
    for row in table:
        for c, col in enumerate(row):
            if c == 0:
                ret.append(f'   * - {col}')
            else:
                ret.append(f'     - {col}')
    return ret


def get_rst() -> typing.List[str]:
    """Generate a .rst file of standards compliance/support."""
    doc_lines = []
    doc_lines.append('.. DO NOT EDIT. Auto-generated by cpip/core/Standards.py main().')
    doc_lines.append('.. SERIOUSLY DO NOT EDIT.')
    doc_lines.append('')
    doc_lines.append('.. moduleauthor:: Paul Ross <apaulross@gmail.com>')
    doc_lines.append('.. sectionauthor:: Paul Ross <apaulross@gmail.com>')
    doc_lines.append('')
    doc_lines.append('.. _cpip.C_Standards:')
    doc_lines.append('')
    doc_lines.append('.. index:: single: C Standards')
    doc_lines.append('')
    doc_lines.extend(rst_heading('C Standards', '', '='))
    doc_lines.append('This describes the C/C++ standards that are supported by CPIP.')
    doc_lines.append('This chapter is auto-generated by ``cpip/core/Standards.py`` function ``main()``.')
    doc_lines.append('Heading titles are the internal *generic* standard names.')
    doc_lines.append('')

    # TODO:
    # Dict of {attribute : {generic_standard : support, ...}, ...}
    attributes_dict = {}
    for generic_standard in Standards.GENERIC_STANDARDS:
        doc_lines.append(f'.. index::')
        doc_lines.append(f'   single: {generic_standard}')
        doc_lines.append(f'   single: C Standards; {generic_standard}')
        doc_lines.append('')
        doc_lines.extend(rst_heading(generic_standard, '', '-'))
        std = Standards(Standards.GENERIC_STANDARD_ARGUMENT[generic_standard], False)

        doc_lines.append(f'.. index:: single: {generic_standard}; Standards Document')
        doc_lines.append('')
        doc_lines.extend(rst_heading('Standards Document', '', '^'))
        doc_lines.append(f'{std.C_STANDARDS_DOCUMENT[generic_standard]}.')
        doc_lines.append('')

        if generic_standard in Standards.C_STANDARDS_NOTES:
            doc_lines.append('.. note::')
            doc_lines.append('')
            for line in Standards.C_STANDARDS_NOTES[generic_standard].split('\n'):
                doc_lines.append(f'    {line}')
            doc_lines.append('')

        c_standards = std.c_standards()
        doc_lines.append(f'.. index::')
        doc_lines.append(f'   pair: {generic_standard}; --std=')
        for c_std in c_standards[generic_standard]:
            doc_lines.append(f'   pair: {generic_standard}; --std={c_std}')
        doc_lines.append('')
        doc_lines.extend(rst_heading('``--std=`` Options', '', '^'))
        temp = []
        for c_std in c_standards[generic_standard]:
            temp.append(f'``--std={c_std}``')
        doc_lines.append(f'{", ".join(temp)}.')
        doc_lines.append('')

        doc_lines.append(f'.. index::')
        doc_lines.append(f'   pair: {generic_standard}; __STDC__')
        doc_lines.append('')
        doc_lines.extend(rst_heading('``__STDC__``', '', '^'))
        if std.STDC[generic_standard]:
            doc_lines.append(f'Defined.')
        else:
            doc_lines.append('Not defined.')
        doc_lines.append('')

        doc_lines.append(f'.. index::')
        doc_lines.append(f'   pair: {generic_standard}; __STDC_VERSION__')
        doc_lines.append('')
        doc_lines.extend(rst_heading('``__STDC_VERSION__`` Value', '', '^'))
        if std.STDC_VERSION[generic_standard]:
            doc_lines.append(f'``#define __STDC_VERSION__ {std.STDC_VERSION[generic_standard]}``')
        else:
            doc_lines.append('Not defined.')
        doc_lines.append('')

        # Conditionally defined macros
        if generic_standard in Standards.CONDITIONALLY_DEFINED_FEATURE_MACROS:
            # First the index.
            doc_lines.append(f'.. index::')
            for macro_name in Standards.CONDITIONALLY_DEFINED_FEATURE_MACROS[generic_standard]:
                if macro_name is not None:
                    doc_lines.append(f'   pair: {generic_standard}; {macro_name}')
            doc_lines.append('')
            # Heading
            doc_lines.extend(rst_heading('Conditionally Defined Macros', '', '^'))
            doc_lines.append(
                f'These are macros that the user might want to define according to the standard'
                f' {std.C_STANDARDS_DOCUMENT[generic_standard]}.'
            )
            doc_lines.append('')
            # Make a table of the macro/description
            table = [
                ['Macro', 'Description', ],
            ]
            for macro_name in Standards.CONDITIONALLY_DEFINED_FEATURE_MACROS[generic_standard]:
                if macro_name is not None:
                    table.append(
                        [
                            f'``{macro_name}``',
                            Standards.CONDITIONALLY_DEFINED_FEATURE_MACROS[generic_standard][macro_name],
                        ],
                    )
            doc_lines.extend(rst_list_table('Conditionally Defined Macros', [30, 70, ], table))
            doc_lines.append('')
            for macro_name in Standards.CONDITIONALLY_DEFINED_FEATURE_MACROS[generic_standard]:
                if macro_name is None:
                    doc_lines.append('.. note::')
                    doc_lines.append(
                        f'   {Standards.CONDITIONALLY_DEFINED_FEATURE_MACROS[generic_standard][macro_name]}'
                    )
                    doc_lines.append('')

        # Build a table of getattr(std, 'has...')
        function_dict = {getattr(std, f).__doc__: f for f in dir(std) if f.startswith('has_')}
        # Remove ' supported' from the key.
        for k in function_dict:
            if k.endswith(' supported'):
                new_key = k[:-len(' supported')]
                new_value = function_dict[k]
                del function_dict[k]
                function_dict[new_key] = new_value

        # print(function_dict)
        for doc, v in function_dict.items():
            result = getattr(std, function_dict[doc])()
            if doc not in attributes_dict:
                attributes_dict[doc] = {}
            attributes_dict[doc][generic_standard] = 'Yes' if result else 'No'

        # for doc in sorted(function_dict.keys()):
        #     result = getattr(std, function_dict[doc])()
        #     print(f'{doc}? {result}')

        # print_rst_heading('C Attributes Supported', '-', '-')
        # table = [
        #     ['Attribute', 'Supported', ]
        # ]
        # for doc in sorted(function_dict.keys()):
        #     result = getattr(std, function_dict[doc])()
        #     table.append([f'{doc}', f'{"Yes" if result else "No"}', ])
        # print_rst_simple_table(table)
        # print()

    # Print summary table
    table = [
        ['Attribute', ] + Standards.GENERIC_STANDARDS,
    ]
    for row_name in sorted(attributes_dict.keys()):
        row = [row_name, ]
        for std in attributes_dict[row_name]:
            row.append(attributes_dict[row_name][std])
        table.append(row)
    doc_lines.append('.. index:: single: C Standards; Summary of Attributes')
    doc_lines.append('')
    doc_lines.extend(rst_heading('Summary of Attributes', '', '-'))
    # doc_lines.extend(rst_simple_table(table))
    widths = [20, ] + ([12, ] * len(Standards.GENERIC_STANDARDS))
    doc_lines.extend(rst_list_table('Summary of Attributes', widths, table))
    # doc_lines.append('')
    return doc_lines


def main() -> int:
    """Write the .rst file of standards compliance/support.

    This file is: src/cpip/core/Standards.py
    Target file is: docs/doc_src/c_standards.rst """
    doc_lines = get_rst()
    file_path = os.path.normpath(
        os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'docs', 'doc_src', 'c_standards.rst',
        )
    )
    print(f'Writing {len(doc_lines)} lines to {file_path}')
    with open(file_path, 'w') as f:
        for line in doc_lines:
            f.write(line)
            f.write('\n')
    print(f'DONE Writing {len(doc_lines)} lines to {file_path}')
    print('Help text:')
    print('\n'.join(Standards.help_text()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
