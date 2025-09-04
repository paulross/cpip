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
import pytest

from cpip.util import CMakeBuild

EXAMPLE_JSON_INDEX = """{
    "cmake" : 
    {
        "generator" : 
        {
            "multiConfig" : false,
            "name" : "Ninja"
        },
        "paths" : 
        {
            "cmake" : "/Users/USER/Library/Application Support/JetBrains/Toolbox/apps/CLion/ch-1/223.8836.42/CLion.app/Contents/bin/cmake/mac/bin/cmake",
            "cpack" : "/Users/USER/Library/Application Support/JetBrains/Toolbox/apps/CLion/ch-1/223.8836.42/CLion.app/Contents/bin/cmake/mac/bin/cpack",
            "ctest" : "/Users/USER/Library/Application Support/JetBrains/Toolbox/apps/CLion/ch-1/223.8836.42/CLion.app/Contents/bin/cmake/mac/bin/ctest",
            "root" : "/Users/USER/Library/Application Support/JetBrains/Toolbox/apps/CLion/ch-1/223.8836.42/CLion.app/Contents/bin/cmake/mac/share/cmake-3.24"
        },
        "version" : 
        {
            "isDirty" : false,
            "major" : 3,
            "minor" : 24,
            "patch" : 2,
            "string" : "3.24.2",
            "suffix" : ""
        }
    },
    "objects" : 
    [
        {
            "jsonFile" : "codemodel-v2-4c8c7c6b8e2ffd1cc209.json",
            "kind" : "codemodel",
            "version" : 
            {
                "major" : 2,
                "minor" : 4
            }
        },
        {
            "jsonFile" : "cache-v2-f12a03d93d698b3b02f1.json",
            "kind" : "cache",
            "version" : 
            {
                "major" : 2,
                "minor" : 0
            }
        },
        {
            "jsonFile" : "cmakeFiles-v1-b665052c260ca2cc5efb.json",
            "kind" : "cmakeFiles",
            "version" : 
            {
                "major" : 1,
                "minor" : 0
            }
        },
        {
            "jsonFile" : "toolchains-v1-9f362175f2e3b763898b.json",
            "kind" : "toolchains",
            "version" : 
            {
                "major" : 1,
                "minor" : 0
            }
        }
    ],
    "reply" : 
    {
        "cache-v2" : 
        {
            "jsonFile" : "cache-v2-f12a03d93d698b3b02f1.json",
            "kind" : "cache",
            "version" : 
            {
                "major" : 2,
                "minor" : 0
            }
        },
        "cmakeFiles-v1" : 
        {
            "jsonFile" : "cmakeFiles-v1-b665052c260ca2cc5efb.json",
            "kind" : "cmakeFiles",
            "version" : 
            {
                "major" : 1,
                "minor" : 0
            }
        },
        "codemodel-v2" : 
        {
            "jsonFile" : "codemodel-v2-4c8c7c6b8e2ffd1cc209.json",
            "kind" : "codemodel",
            "version" : 
            {
                "major" : 2,
                "minor" : 4
            }
        },
        "toolchains-v1" : 
        {
            "jsonFile" : "toolchains-v1-9f362175f2e3b763898b.json",
            "kind" : "toolchains",
            "version" : 
            {
                "major" : 1,
                "minor" : 0
            }
        }
    }
}
"""


@pytest.mark.parametrize(
    'example, expected',
    (
        (
            EXAMPLE_JSON_INDEX,
            CMakeBuild.CMakeIndex(
                cmake_build_directory='cmake-build-debug',
                cmake_version_str='3.24.2',
                codemodel_file_name='codemodel-v2-4c8c7c6b8e2ffd1cc209.json',
                toolchains_file_name='toolchains-v1-9f362175f2e3b763898b.json',
            ),
        ),
    )
)
def test_cmake_reply_index_from_json(example, expected):
    result = CMakeBuild.cmake_reply_index_from_json('cmake-build-debug', example)
    assert result == expected


EXAMPLE_JSON_CODEMODEL = """{
    "configurations" : 
    [
        {
            "directories" : 
            [
                {
                    "build" : ".",
                    "jsonFile" : "directory-.-Debug-f5ebdc15457944623624.json",
                    "minimumCMakeVersion" : 
                    {
                        "string" : "3.13"
                    },
                    "projectIndex" : 0,
                    "source" : ".",
                    "targetIndexes" : 
                    [
                        0
                    ]
                }
            ],
            "name" : "Debug",
            "projects" : 
            [
                {
                    "directoryIndexes" : 
                    [
                        0
                    ],
                    "name" : "SkipList",
                    "targetIndexes" : 
                    [
                        0
                    ]
                }
            ],
            "targets" : 
            [
                {
                    "directoryIndex" : 0,
                    "id" : "SkipList::@6890427a1f51a3e7e1df",
                    "jsonFile" : "target-SkipList-Debug-091d871282c22504d7ce.json",
                    "name" : "SkipList",
                    "projectIndex" : 0
                }
            ]
        }
    ],
    "kind" : "codemodel",
    "paths" : 
    {
        "build" : "/Users/USER/CLionProjects/skiplist/cmake-build-debug",
        "source" : "/Users/USER/CLionProjects/skiplist"
    },
    "version" : 
    {
        "major" : 2,
        "minor" : 4
    }
}
"""


@pytest.mark.parametrize(
    'example, file_name, expected',
    (
        (
            EXAMPLE_JSON_CODEMODEL,
            'codemodel-v2-4c8c7c6b8e2ffd1cc209.json',
            CMakeBuild.CMakeCodeModel(
                cmake_build_directory='cmake-build-debug',
                codemodel_file_name='codemodel-v2-4c8c7c6b8e2ffd1cc209.json',
                project_path='/Users/USER/CLionProjects/skiplist',
                name='SkipList',
                target_file_name='target-SkipList-Debug-091d871282c22504d7ce.json'),
        ),
    )
)
def test_cmake_reply_codemodel_from_json(example, file_name, expected):
    result = CMakeBuild.cmake_reply_codemodel_from_json(
        'cmake-build-debug', file_name, example,
    )
    assert result == expected


EXAMPLE_JSON_TOOLCHAINS = """{
    "kind" : "toolchains",
    "toolchains" : 
    [
        {
            "compiler" : 
            {
                "id" : "AppleClang",
                "implicit" : 
                {
                    "includeDirectories" : 
                    [
                        "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/15.0.0/include",
                        "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.0.sdk/usr/include",
                        "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include"
                    ],
                    "linkDirectories" : [],
                    "linkFrameworkDirectories" : [],
                    "linkLibraries" : []
                },
                "path" : "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc",
                "version" : "15.0.0.15000040"
            },
            "language" : "C",
            "sourceFileExtensions" : 
            [
                "c",
                "m"
            ]
        },
        {
            "compiler" : 
            {
                "id" : "AppleClang",
                "implicit" : 
                {
                    "includeDirectories" : 
                    [
                        "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.0.sdk/usr/include/c++/v1",
                        "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/15.0.0/include",
                        "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.0.sdk/usr/include",
                        "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include"
                    ],
                    "linkDirectories" : [],
                    "linkFrameworkDirectories" : [],
                    "linkLibraries" : 
                    [
                        "c++"
                    ]
                },
                "path" : "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++",
                "version" : "15.0.0.15000040"
            },
            "language" : "CXX",
            "sourceFileExtensions" : 
            [
                "C",
                "M",
                "c++",
                "cc",
                "cpp",
                "cxx",
                "mm",
                "mpp",
                "CPP",
                "ixx",
                "cppm"
            ]
        }
    ],
    "version" : 
    {
        "major" : 1,
        "minor" : 0
    }
}
"""


@pytest.mark.parametrize(
    'example, file_name, expected_language_dict',
    (
        (
            EXAMPLE_JSON_TOOLCHAINS,
            'toolchains-v1-9f362175f2e3b763898b.json',
            {
                'C': CMakeBuild.CMakeToolChainLanguageInformation(
                    system_include_directories=[
                        '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/15.0.0/include',
                        '/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.0.sdk/usr/include',
                        '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include'],
                ),
                'CXX': CMakeBuild.CMakeToolChainLanguageInformation(
                    system_include_directories=[
                        '/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.0.sdk/usr/include/c++/v1',
                        '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/15.0.0/include',
                        '/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.0.sdk/usr/include',
                        '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include',
                    ],
                ),
            },
        ),
    )
)
def test_cmake_reply_toolchains_from_json(example, file_name, expected_language_dict):
    result = CMakeBuild.cmake_reply_toolchains_from_json(
        'cmake-build-debug', file_name, example,
    )
    assert result.toolchains_file_name == file_name
    assert result.language_dict == expected_language_dict


EXAMPLE_JSON_TARGET = """{
    "artifacts" : 
    [
        {
            "path" : "SkipList"
        }
    ],
    "backtrace" : 1,
    "backtraceGraph" : 
    {
        "commands" : 
        [
            "add_executable",
            "link_directories",
            "target_link_libraries",
            "add_compile_options",
            "target_compile_options",
            "add_compile_definitions",
            "include_directories",
            "INCLUDE_DIRECTORIES"
        ],
        "files" : 
        [
            "CMakeLists.txt"
        ],
        "nodes" : 
        [
            {
                "file" : 0
            },
            {
                "command" : 0,
                "file" : 0,
                "line" : 29,
                "parent" : 0
            },
            {
                "command" : 1,
                "file" : 0,
                "line" : 25,
                "parent" : 0
            },
            {
                "command" : 2,
                "file" : 0,
                "line" : 83,
                "parent" : 0
            },
            {
                "command" : 3,
                "file" : 0,
                "line" : 20,
                "parent" : 0
            },
            {
                "command" : 4,
                "file" : 0,
                "line" : 85,
                "parent" : 0
            },
            {
                "command" : 5,
                "file" : 0,
                "line" : 11,
                "parent" : 0
            },
            {
                "command" : 5,
                "file" : 0,
                "line" : 7,
                "parent" : 0
            },
            {
                "command" : 6,
                "file" : 0,
                "line" : 64,
                "parent" : 0
            },
            {
                "command" : 7,
                "file" : 0,
                "line" : 78,
                "parent" : 0
            }
        ]
    },
    "compileGroups" : 
    [
        {
            "compileCommandFragments" : 
            [
                {
                    "fragment" : "-g -arch x86_64 -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.0.sdk -mmacosx-version-min=13.5 -fcolor-diagnostics"
                },
                {
                    "backtrace" : 4,
                    "fragment" : "-Wall"
                },
                {
                    "backtrace" : 4,
                    "fragment" : "-Wpedantic"
                },
                {
                    "backtrace" : 4,
                    "fragment" : "-Wextra"
                },
                {
                    "backtrace" : 4,
                    "fragment" : "-fexceptions"
                },
                {
                    "backtrace" : 4,
                    "fragment" : "-O0"
                },
                {
                    "backtrace" : 4,
                    "fragment" : "-g3"
                },
                {
                    "backtrace" : 4,
                    "fragment" : "-ggdb"
                },
                {
                    "backtrace" : 5,
                    "fragment" : "-Wno-c99-extensions"
                },
                {
                    "backtrace" : 5,
                    "fragment" : "-pedantic"
                },
                {
                    "fragment" : "-std=gnu++17"
                }
            ],
            "defines" : 
            [
                {
                    "backtrace" : 6,
                    "define" : "DEBUG"
                },
                {
                    "backtrace" : 7,
                    "define" : "SKIPLIST_THREAD_SUPPORT=1"
                }
            ],
            "includes" : 
            [
                {
                    "backtrace" : 8,
                    "path" : "/Users/USER/CLionProjects/skiplist/src/cpp"
                },
                {
                    "backtrace" : 8,
                    "path" : "/Users/USER/CLionProjects/skiplist/src/cpp/test"
                },
                {
                    "backtrace" : 8,
                    "path" : "/Users/USER/CLionProjects/skiplist/src/cpy"
                },
                {
                    "backtrace" : 9,
                    "path" : "/Library/Frameworks/Python.framework/Versions/3.12/include/python3.12"
                }
            ],
            "language" : "CXX",
            "languageStandard" : 
            {
                "backtraces" : 
                [
                    1
                ],
                "standard" : "17"
            },
            "sourceIndexes" : 
            [
                2,
                6,
                8,
                10,
                12,
                14,
                16,
                18,
                20,
                22,
                24,
                26
            ]
        }
    ],
    "id" : "SkipList::@6890427a1f51a3e7e1df",
    "link" : 
    {
        "commandFragments" : 
        [
            {
                "fragment" : "-g",
                "role" : "flags"
            },
            {
                "fragment" : "",
                "role" : "flags"
            },
            {
                "backtrace" : 2,
                "fragment" : "-L/Library/Frameworks/Python.framework/Versions/3.11/lib",
                "role" : "libraryPath"
            },
            {
                "fragment" : "-Wl,-rpath,/Library/Frameworks/Python.framework/Versions/3.11/lib",
                "role" : "libraries"
            },
            {
                "backtrace" : 3,
                "fragment" : "/Library/Frameworks/Python.framework/Versions/3.12/lib/libpython3.12.dylib",
                "role" : "libraries"
            }
        ],
        "language" : "CXX"
    },
    "name" : "SkipList",
    "nameOnDisk" : "SkipList",
    "paths" : 
    {
        "build" : ".",
        "source" : "."
    },
    "sourceGroups" : 
    [
        {
            "name" : "Header Files",
            "sourceIndexes" : 
            [
                0,
                1,
                3,
                4,
                5,
                7,
                9,
                11,
                13,
                15,
                17,
                19,
                21,
                23,
                25,
                27
            ]
        },
        {
            "name" : "Source Files",
            "sourceIndexes" : 
            [
                2,
                6,
                8,
                10,
                12,
                14,
                16,
                18,
                20,
                22,
                24,
                26
            ]
        }
    ],
    "sources" : 
    [
        {
            "backtrace" : 1,
            "path" : "src/cpp/HeadNode.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "path" : "src/cpp/IntegrityEnums.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpp/main.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpp/Node.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "path" : "src/cpp/NodeRefs.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "path" : "src/cpp/RollingMedian.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpp/SkipList.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpp/SkipList.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpp/test/test_concurrent.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpp/test/test_concurrent.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpp/test/test_documentation.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpp/test/test_documentation.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpp/test/test_functional.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpp/test/test_functional.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpp/test/test_performance.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpp/test/test_performance.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpp/test/test_print.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpp/test/test_print.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpp/test/test_rolling_median.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpp/test/test_rolling_median.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpy/cmpPyObject.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpy/cmpPyObject.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpy/cOrderedStructs.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpy/cOrderedStructs.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpy/cSkipList.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpy/cSkipList.h",
            "sourceGroupIndex" : 0
        },
        {
            "backtrace" : 1,
            "compileGroupIndex" : 0,
            "path" : "src/cpy/OrderedStructs.cpp",
            "sourceGroupIndex" : 1
        },
        {
            "backtrace" : 1,
            "path" : "src/cpy/OrderedStructs.h",
            "sourceGroupIndex" : 0
        }
    ],
    "type" : "EXECUTABLE"
}
"""


@pytest.mark.parametrize(
    'example, file_name, expected',
    (
        (
            EXAMPLE_JSON_TARGET,
            'target-SkipList-Debug-091d871282c22504d7ce.json',
            CMakeBuild.CMakeTarget(
                cmake_build_directory='cmake-build-debug',
                target_file_name='target-SkipList-Debug-091d871282c22504d7ce.json',
                project_path='/Users/USER/CLionProjects/skiplist',
                name='SkipList',
                defines=[
                    'DEBUG',
                    'SKIPLIST_THREAD_SUPPORT=1',
                ],
                include_paths=[
                    '/Users/USER/CLionProjects/skiplist/src/cpp',
                    '/Users/USER/CLionProjects/skiplist/src/cpp/test',
                    '/Users/USER/CLionProjects/skiplist/src/cpy',
                    '/Library/Frameworks/Python.framework/Versions/3.12/include/python3.12',
                ],
                sources=[
                    'src/cpp/HeadNode.h',
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
                    'src/cpy/OrderedStructs.h',
                ],
            ),
        ),
    )
)
def test_cmake_reply_target_from_json(example, file_name, expected):
    result = CMakeBuild.cmake_reply_target_from_json(
        'cmake-build-debug', file_name, example,
    )
    assert result == expected
