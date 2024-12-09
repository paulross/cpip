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
        'iso9899:199409': 'C90',
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
        'C95': False,
        'C99': False,
        'C11': False,
        'C17/C18': False,
        'C23': False,
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
        'ANSI': 'This is really no different from C90.',
        'C90': 'This is really no different from ANSI C.',
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
            temp = [f'{generic_standard}']
            if cls.C_STANDARDS_DOCUMENT[generic_standard]:
                temp.append(f'({cls.C_STANDARDS_DOCUMENT[generic_standard]})')
            temp2 = []
            for c_std in c_standards[generic_standard]:
                temp2.append(f'--std={c_std}')
            temp.append(f'{", ".join(temp2)}.')
            ret.append(' '.join(temp))
        return ret


def print_rst_heading(text: str, overline: str, underline: str):
    """Print a rst heading."""
    if overline:
        print(f'{f"{overline}" * len(text)}')
    print(f'{text}')
    print(f'{f"{underline}" * len(text)}')
    print()


def print_rst_simple_table(table: typing.List[typing.List[str]]):
    """Print a rst simple table. The first row contains the headings."""
    assert len(table) >= 2
    widths = [0] * len(table[0])
    for row in table:
        for c, col in enumerate(row):
            widths[c] = max(widths[c], len(col))
    delimeter_line = ' '.join(['=' * width for width in widths])
    print(delimeter_line)
    for c, col in enumerate(table[0]):
        if c > 0:
            print(' ', end='')
        print(f'{table[0][c]:<{widths[c]}}', end='')
    print()
    print(delimeter_line)
    for r, row in enumerate(table):
        if r:
            for c, col in enumerate(row):
                if c > 0:
                    print(' ', end='')
                print(f'{table[r][c]:<{widths[c]}}', end='')
            print()
    print(delimeter_line)


def main():
    """Generate a .rst file of standards compliance/support."""
    print('.. DO NOT EDIT. Auto-generated by cpip/core/Standards.py main().')
    print('.. moduleauthor:: Paul Ross <apaulross@gmail.com>')
    print('.. sectionauthor:: Paul Ross <apaulross@gmail.com>')
    print()
    print('.. _cpip.C_Standards:')
    print()
    print_rst_heading('Supported C Standards', '', '=')
    print('This describes the C/C++ standards that are supported by CPIP.')
    print()

    # TODO:
    # Dict of {attribute : {generic_standard : support, ...}, ...}
    attributes_dict = {}
    for generic_standard in Standards.GENERIC_STANDARDS:
        print_rst_heading(generic_standard, '', '-')
        std = Standards(Standards.GENERIC_STANDARD_ARGUMENT[generic_standard], False)

        print_rst_heading('Standards Document', '', '^')
        print(f'{std.C_STANDARDS_DOCUMENT[generic_standard]}.')
        print()

        print_rst_heading('``__STDC__``', '', '^')
        if std.STDC[generic_standard]:
            print(f'Defined.')
        else:
            print('Not defined.')
        print()

        print_rst_heading('``__STDC_VERSION__`` Value', '', '^')
        if std.STDC_VERSION[generic_standard]:
            print(f'``#define __STDC_VERSION__ {std.STDC_VERSION[generic_standard]}``')
        else:
            print('Not defined.')
        print()

        print_rst_heading('``--std=`` Options', '', '^')
        c_standards = std.c_standards()
        temp = []
        for c_std in c_standards[generic_standard]:
            temp.append(f'``--std={c_std}``')
        print(f'{", ".join(temp)}.')
        print()

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
    print_rst_heading('Summary of Attributes', '', '-')
    print_rst_simple_table(table)
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
