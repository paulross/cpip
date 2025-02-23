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
import typing

# import logging
# import os
# import sys
# import time
# import unittest

import pytest

from cpip.core import IncludeHandler
from cpip.core import PpLexer
from cpip.core import PpToken
# File location test classes
# from cpip.core.IncludeHandler import CppIncludeStringIO, CppIncludeStdOs
from cpip.util import InvokeCpp


def simple_lexer_with_content(content: bytes) -> PpLexer.PpLexer:
    """Creates a PpLexer with the content."""
    return PpLexer.PpLexer(
        'mt.h',
        IncludeHandler.CppIncludeStringIO([], [], content.decode(), {}),
        preIncFiles=[],
        diagnostic=None,
    )


def run_lexer(lexer: PpLexer.PpLexer, include_ws: bool) -> typing.List[typing.Any]:
    """Causes the lexer to preprocess and returns the tokens.
    Include whitespace if include_ws is True."""
    if include_ws:
        tokens = [t for t in lexer.ppTokens()]
    else:
        tokens = [t for t in lexer.ppTokens() if not t.isWs()]
    lexer.finalise()
    return tokens


def pplexer_preprocess(stdin: bytes) -> typing.List[str]:
    """Preprocess the stdin content with a PpLexer and return the preprocessed content.
    Blank lines are omitted."""
    lexer = simple_lexer_with_content(stdin)
    tokens = run_lexer(lexer, include_ws=True)
    tokens_as_text = []
    line = []
    for token in tokens:
        if token.t == '\n':
            if line:
                tokens_as_text.append(''.join(line))
                line = []
        else:
            line.append(token.t)
    if line:
        tokens_as_text.append(''.join(line))
    return tokens_as_text


@pytest.mark.xfail(reason="FIXME")
@pytest.mark.parametrize(
    'stdin, expected',
    (
        (b'', []),
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
            [
                'SPAM', 'EGGS', 'SPAM',
            ],
        ),
        (
            b'\n'.join(
                [
                    b'#define f(a) a*g',
                    b'#define g(a) f(a)',
                    b'f(2)(9)',
                ]
            ),
            ['2*9*g', ],
        ),
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
    )
)
def test_pplexer_vs_cpp(stdin, expected):
    lines_cpp = InvokeCpp.capture_cpp_stdin_output(stdin, remove_comments=True, remove_blank_lines=True)
    assert lines_cpp == expected
    lines_pplexer = pplexer_preprocess(stdin)
    assert lines_pplexer == expected


@pytest.mark.xfail(reason="FIXME")
@pytest.mark.parametrize(
    'stdin, expected',
    (
        (
            b'\n'.join(
                [
                    b'#define SPAM(x,y) x + y',
                    b'#define EGGS SPAM',
                    b'EGGS(2, 9)',
                ]
            ),
            ['2 + 9', ],
        ),
    )
)
def test_pplexer_vs_cpp_debug(stdin, expected):
    lines_cpp = InvokeCpp.capture_cpp_stdin_output(stdin, remove_comments=True, remove_blank_lines=True)
    assert lines_cpp == expected
    lines_pplexer = pplexer_preprocess(stdin)
    assert lines_pplexer == expected
