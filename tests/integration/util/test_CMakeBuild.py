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
import os.path

import pytest

from cpip.util import CMakeBuild

EXAMPLE_CMAKE_BUILD_DIRECTORY = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'cmake-build-debug')
)


@pytest.mark.parametrize(
    'cmake_build_directory, expected',
    (
        (
            EXAMPLE_CMAKE_BUILD_DIRECTORY,
            CMakeBuild.CMakeIndex(
                cmake_build_directory=EXAMPLE_CMAKE_BUILD_DIRECTORY,
                cmake_version_str='3.24.2',
                codemodel_file_name='codemodel-v2-4c8c7c6b8e2ffd1cc209.json',
            ),
        ),
    )
)
def test_cmake_reply_index_from_build_directory(cmake_build_directory, expected):
    result = CMakeBuild.cmake_reply_index_from_build_directory(cmake_build_directory)
    assert result == expected


@pytest.mark.parametrize(
    'cmake_build_directory, expected',
    (
        (
            EXAMPLE_CMAKE_BUILD_DIRECTORY,
            CMakeBuild.CMakeIndex(
                cmake_build_directory=EXAMPLE_CMAKE_BUILD_DIRECTORY,
                cmake_version_str='3.24.2',
                codemodel_file_name='codemodel-v2-4c8c7c6b8e2ffd1cc209.json',
            ),
        ),
    )
)
def test_cmake_reply_index_from_build_directory(cmake_build_directory, expected):
    result = CMakeBuild.cmake_reply_index_from_build_directory(cmake_build_directory)
    assert result == expected


@pytest.mark.parametrize(
    'cmake_build_directory, expected',
    (
        (
            EXAMPLE_CMAKE_BUILD_DIRECTORY,
            CMakeBuild.CMakeCodeModel(
                cmake_build_directory=EXAMPLE_CMAKE_BUILD_DIRECTORY,
                codemodel_file_name='codemodel-v2-4c8c7c6b8e2ffd1cc209.json',
                project_path='/Users/USER/CLionProjects/skiplist',
                name='SkipList',
                target_file_name='target-SkipList-Debug-091d871282c22504d7ce.json',
            ),
        ),
    )
)
def test_cmake_reply_codemodel_from_cmake_index(cmake_build_directory, expected):
    cmake_index = CMakeBuild.cmake_reply_index_from_build_directory(cmake_build_directory)
    result = CMakeBuild.cmake_reply_codemodel_from_cmake_index(cmake_index)
    assert result == expected


@pytest.mark.parametrize(
    'cmake_build_directory, expected',
    (
        (
            EXAMPLE_CMAKE_BUILD_DIRECTORY,
            CMakeBuild.CMakeTarget(
                cmake_build_directory=EXAMPLE_CMAKE_BUILD_DIRECTORY,
                target_file_name='target-SkipList-Debug-091d871282c22504d7ce.json',
                name='SkipList',
                defines=['DEBUG', 'SKIPLIST_THREAD_SUPPORT=1'],
                includes=['/Users/USER/CLionProjects/skiplist/src/cpp',
                          '/Users/USER/CLionProjects/skiplist/src/cpp/test',
                          '/Users/USER/CLionProjects/skiplist/src/cpy',
                          '/Library/Frameworks/Python.framework/Versions/3.12/include/python3.12'],
                sources=['src/cpp/HeadNode.h',
                         'src/cpp/IntegrityEnums.h',
                         'src/cpp/main.cpp',
                         'src/cpp/Node.h',
                         'src/cpp/NodeRefs.h',
                         'src/cpp/RollingMedian.h',
                         'src/cpp/SkipList.cpp',
                         'src/cpp/SkipList.h',
                         'src/cpp/test/test_concurrent.cpp',
                         'src/cpp/test/test_concurrent.h',
                         'src/cpp/test/test_documentation.cpp',
                         'src/cpp/test/test_documentation.h',
                         'src/cpp/test/test_functional.cpp',
                         'src/cpp/test/test_functional.h',
                         'src/cpp/test/test_performance.cpp',
                         'src/cpp/test/test_performance.h',
                         'src/cpp/test/test_print.cpp',
                         'src/cpp/test/test_print.h',
                         'src/cpp/test/test_rolling_median.cpp',
                         'src/cpp/test/test_rolling_median.h',
                         'src/cpy/cmpPyObject.cpp',
                         'src/cpy/cmpPyObject.h',
                         'src/cpy/cOrderedStructs.cpp',
                         'src/cpy/cOrderedStructs.h',
                         'src/cpy/cSkipList.cpp',
                         'src/cpy/cSkipList.h',
                         'src/cpy/OrderedStructs.cpp',
                         'src/cpy/OrderedStructs.h'],
            ),
        ),
    )
)
def test_cmake_reply_target_from_codemodel(cmake_build_directory, expected):
    cmake_index = CMakeBuild.cmake_reply_index_from_build_directory(cmake_build_directory)
    cmake_codemodel = CMakeBuild.cmake_reply_codemodel_from_cmake_index(cmake_index)
    result = CMakeBuild.cmake_reply_target_from_codemodel(cmake_codemodel)
    assert result == expected


@pytest.mark.parametrize(
    'cmake_build_directory, expected',
    (
        (
            EXAMPLE_CMAKE_BUILD_DIRECTORY,
            CMakeBuild.CMakeTarget(
                cmake_build_directory=EXAMPLE_CMAKE_BUILD_DIRECTORY,
                target_file_name='target-SkipList-Debug-091d871282c22504d7ce.json',
                name='SkipList',
                defines=['DEBUG', 'SKIPLIST_THREAD_SUPPORT=1'],
                includes=['/Users/USER/CLionProjects/skiplist/src/cpp',
                          '/Users/USER/CLionProjects/skiplist/src/cpp/test',
                          '/Users/USER/CLionProjects/skiplist/src/cpy',
                          '/Library/Frameworks/Python.framework/Versions/3.12/include/python3.12'],
                sources=['src/cpp/HeadNode.h',
                         'src/cpp/IntegrityEnums.h',
                         'src/cpp/main.cpp',
                         'src/cpp/Node.h',
                         'src/cpp/NodeRefs.h',
                         'src/cpp/RollingMedian.h',
                         'src/cpp/SkipList.cpp',
                         'src/cpp/SkipList.h',
                         'src/cpp/test/test_concurrent.cpp',
                         'src/cpp/test/test_concurrent.h',
                         'src/cpp/test/test_documentation.cpp',
                         'src/cpp/test/test_documentation.h',
                         'src/cpp/test/test_functional.cpp',
                         'src/cpp/test/test_functional.h',
                         'src/cpp/test/test_performance.cpp',
                         'src/cpp/test/test_performance.h',
                         'src/cpp/test/test_print.cpp',
                         'src/cpp/test/test_print.h',
                         'src/cpp/test/test_rolling_median.cpp',
                         'src/cpp/test/test_rolling_median.h',
                         'src/cpy/cmpPyObject.cpp',
                         'src/cpy/cmpPyObject.h',
                         'src/cpy/cOrderedStructs.cpp',
                         'src/cpy/cOrderedStructs.h',
                         'src/cpy/cSkipList.cpp',
                         'src/cpy/cSkipList.h',
                         'src/cpy/OrderedStructs.cpp',
                         'src/cpy/OrderedStructs.h'],
            ),
        ),
    )
)
def test_cmake_reply_target_file_from_build_directory(cmake_build_directory, expected):
    result = CMakeBuild.cmake_reply_target_file_from_build_directory(cmake_build_directory)
    assert result == expected


@pytest.mark.parametrize(
    'cmake_build_directory, expected',
    (
        (EXAMPLE_CMAKE_BUILD_DIRECTORY, True,),
        ('foo', False,),
    )
)
def test_is_cmake_build_directory(cmake_build_directory, expected):
    result = CMakeBuild.is_cmake_build_directory(cmake_build_directory)
    assert result == expected
