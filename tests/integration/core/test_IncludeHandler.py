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

"""Tests for the File Include Handlers."""

__author__ = 'Paul Ross'
__date__ = '2025-09-08'
__rights__ = 'Copyright (c) 2008-2025 Paul Ross'

import pprint

import pytest

from cpip.core import IncludeHandler


@pytest.mark.parametrize(
    'language, expected',
    (
        (
            'C',
            [],
        ),
        (
            'C++',
            [],
        ),
    )
)
def test_get_platform_system_include_paths(language, expected):
    result = IncludeHandler.get_platform_system_include_paths(language)
    print()
    pprint.pprint(result)
    assert len(result) > 0


@pytest.mark.parametrize(
    'language, expected',
    (
        (
            'FOO',
            'Unknown language "FOO"',
        ),
    )
)
def test_get_platform_system_include_paths_raises(language, expected):
    with pytest.raises(ValueError) as err:
        IncludeHandler.get_platform_system_include_paths(language)
    assert err.value.args[0] == expected
