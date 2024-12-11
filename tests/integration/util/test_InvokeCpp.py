#!/usr/bin/env python
# CPIP is a C/C++ Preprocessor implemented in Python.
# Copyright (C) 2008-2017 Paul Ross
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

import pytest

from cpip.util import InvokeCpp


@pytest.mark.parametrize(
    'stdin, remove_comments, remove_blank_lines, expected',
    (
        (b'', True, True, []),
        (
            b'\n'.join(
                [
                    b'#define SPAM EGGS',
                    b'#define EGGS SPAM',
                    b'#define CHIPS SPAM',
                    b'SPAM',
                    b'EGGS',
                    b'CHIPS',
                ]
            ),
            True, True,
            [
                'SPAM', 'EGGS', 'SPAM',
            ],
        ),
        (
            b'\n'.join(
                [
                    b'#define SPAM EGGS',
                    b'#define EGGS SPAM',
                    b'#define CHIPS SPAM',
                    b'SPAM',
                    b'EGGS',
                    b'CHIPS',
                ]
            ),
            False, False,
            [
                '# 1 "<stdin>"',
                '# 1 "<built-in>" 1',
                '# 1 "<built-in>" 3',
                '# 384 "<built-in>" 3',
                '# 1 "<command line>" 1',
                '# 1 "<built-in>" 2',
                '# 1 "<stdin>" 2',
                '',
                '',
                '',
                'SPAM',
                'EGGS',
                'SPAM',
            ],
        ),
        (
            b'\n'.join(
                [
                    b'#define SPAM EGGS',
                    b'#define EGGS SPAM',
                    b'#define CHIPS SPAM',
                    b'SPAM',
                    b'EGGS',
                    b'CHIPS',
                ]
            ),
            True, False,
            ['', '', '', 'SPAM', 'EGGS', 'SPAM'],
        ),
        (
            b'\n'.join(
                [
                    b'#define SPAM EGGS',
                    b'#define EGGS SPAM',
                    b'#define CHIPS SPAM',
                    b'SPAM',
                    b'EGGS',
                    b'CHIPS',
                ]
            ),
            False, True,
            [
                '# 1 "<stdin>"',
                '# 1 "<built-in>" 1',
                '# 1 "<built-in>" 3',
                '# 384 "<built-in>" 3',
                '# 1 "<command line>" 1',
                '# 1 "<built-in>" 2',
                '# 1 "<stdin>" 2',
                'SPAM',
                'EGGS',
                'SPAM',
            ],
        ),
    )
)
def test_capture_cpp_stdin_output(stdin, remove_comments, remove_blank_lines, expected):
    result = InvokeCpp.capture_cpp_stdin_output(stdin,
                                                remove_comments=remove_comments,
                                                remove_blank_lines=remove_blank_lines,
                                                )
    assert result == expected


@pytest.mark.parametrize(
    'stdin, expected',
    (
        # No space: EGGS(2,9)
        (
            b'\n'.join(
                [
                    b'#define SPAM(x,y) x + y',
                    b'#define EGGS SPAM',
                    b'EGGS(2,9)',
                ]
            ),
            ['2 + 9', ],
        ),
        # Extra space: EGGS(2, 9) gives ['2 +  9', ]
        (
            b'\n'.join(
                [
                    b'#define SPAM(x,y) x + y',
                    b'#define EGGS SPAM',
                    b'EGGS(2, 9)',
                ]
            ),
            ['2 +  9', ],
        ),
        # Extra two spaces: EGGS(2,  9) gives ['2 +   9', ]
        (
            b'\n'.join(
                [
                    b'#define SPAM(x,y) x + y',
                    b'#define EGGS SPAM',
                    b'EGGS(2,  9)',
                ]
            ),
            ['2 +   9', ],
        ),
        # Declaration x+y, no space: EGGS(2,9)
        (
            b'\n'.join(
                [
                    b'#define SPAM(x,y) x+y',
                    b'#define EGGS SPAM',
                    b'EGGS(2,9)',
                ]
            ),
            ['2 +9', ],
        ),
        # Declaration x+y, one space: EGGS(2, 9)
        (
            b'\n'.join(
                [
                    b'#define SPAM(x,y) x+y',
                    b'#define EGGS SPAM',
                    b'EGGS(2, 9)',
                ]
            ),
            ['2 + 9', ],
        ),
        # Declaration x+y but with spaces in arguments, no space: EGGS(2,9)
        (
            b'\n'.join(
                [
                    b'#define SPAM(x,  y) x+y',
                    b'#define EGGS SPAM',
                    b'EGGS(2,9)',
                ]
            ),
            ['2 +9', ],
        ),
    )
)
def test_capture_cpp_functional_substitution(stdin, expected):
    result = InvokeCpp.capture_cpp_stdin_output(stdin,
                                                remove_comments=True,
                                                remove_blank_lines=True,
                                                )
    assert result == expected
