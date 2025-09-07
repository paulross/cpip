"""Provides an interface to the CMake build system information.

See: https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html
"""
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

import dataclasses
import fnmatch
import json
import os
import typing


class CMakeBuildException(Exception):
    """Specialised exception for this module."""
    pass


def cmake_reply_directory(cmake_build_directory: str) -> str:
    """Returns the cmake reply directory inside the build directory."""
    return os.path.join(cmake_build_directory, '.cmake', 'api', 'v1', 'reply')


def cmake_reply_index_file_path(cmake_build_directory: str) -> str:
    """Returns the cmake reply index file, this is the staring point of the CMake information.

    See: https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#v1-reply-index-file

    File name is index-<unspecified>.json
    There may be multiple index files, from the documentation:
    "the one with the largest name in lexicographic order is the current index file"
    """
    if not os.path.isdir(cmake_build_directory):
        raise CMakeBuildException(
            f'CMake build directory {cmake_build_directory} does not exist.'
        )
    cmake_reply_dir = cmake_reply_directory(cmake_build_directory)
    if not os.path.isdir(cmake_reply_dir):
        raise CMakeBuildException(
            f'CMake build directory {cmake_reply_dir} does not contain an .cmake/api/v1/reply directory.'
        )
    index_files = []
    for file_name in os.listdir(cmake_reply_dir):
        if fnmatch.fnmatch(file_name, 'index-*.json'):
            index_files.append(file_name)
    index_files.sort()
    if len(index_files) == 0:
        raise CMakeBuildException('No CMake build index JSON file found.')
    return os.path.join(cmake_reply_dir, index_files[-1])


@dataclasses.dataclass
class CMakeIndex:
    """Contains data extracted from the CMake index JSON file."""
    cmake_build_directory: str
    cmake_version_str: str
    codemodel_file_name: str
    toolchains_file_name: str


def cmake_reply_index_from_json(cmake_build_directory: str, json_str: str) -> CMakeIndex:
    """Returns a CMakeIndex instance from a JSON string from the reply/index file.

    See: https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#v1-reply-index-file
    """
    index_json = json.loads(json_str)
    cmake_version_str = index_json['cmake']['version']['string']
    # Make a temporary dict of all the 'kind' elements'
    object_kind_file = {}
    for obj in index_json['objects']:
        if obj['kind'] in object_kind_file:
            raise ValueError(f'Duplicate kind="{obj["kind"]}"')
        object_kind_file[obj['kind']] = obj['jsonFile']
    # reply_kind_file = {}
    # for key in index_json['reply']:
    #     obj = index_json['reply'][key]
    #     reply_kind_file[obj['kind']] = obj['jsonFile']
    codemodel_filename = object_kind_file['codemodel']
    toolchains_filename = object_kind_file['toolchains']
    return CMakeIndex(
        cmake_build_directory, cmake_version_str, codemodel_filename, toolchains_filename,
    )


def cmake_reply_index_from_build_directory(cmake_build_directory: str) -> CMakeIndex:
    """Returns the cmake reply index file, this is the staring point of the CMake information."""
    with open(cmake_reply_index_file_path(cmake_build_directory)) as index_file:
        return cmake_reply_index_from_json(cmake_build_directory, index_file.read())


@dataclasses.dataclass
class CMakeCodeModel:
    """Contains data extracted from the CMake codemodel JSON file."""
    cmake_build_directory: str
    codemodel_file_name: str
    # This comes from configurations[0].paths.source
    project_path: str
    name: str
    target_file_name: str


def cmake_reply_codemodel_from_json(cmake_build_directory: str, codemodel_file_name: str,
                                    json_str: str) -> CMakeCodeModel:
    """Returns a CMakeCodeModel from a codemodel JSON string.

    See: https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#object-kind-codemodel
    """
    codemodel_json = json.loads(json_str)
    configurations = codemodel_json['configurations']
    if len(configurations) != 1:
        raise CMakeBuildException(
            'No unique CMake configuration found, instead %d found.',
            len(configurations)
        )
    configuration = configurations[0]
    targets = configuration['targets']
    if len(targets) != 1:
        raise CMakeBuildException(
            'No unique CMake targets found, instead %d found.',
            len(targets)
        )
    project_path = codemodel_json['paths']['source']
    return CMakeCodeModel(
        cmake_build_directory, codemodel_file_name, project_path,
        targets[0]['name'], targets[0]['jsonFile'],
    )


def cmake_reply_codemodel_from_cmake_index(cmake_index: CMakeIndex) -> CMakeCodeModel:
    """Returns a CMakeCodeModel from a CMakeIndex."""
    file_path = os.path.join(
        cmake_reply_directory(cmake_index.cmake_build_directory),
        cmake_index.codemodel_file_name,
    )
    with open(file_path) as file:
        return cmake_reply_codemodel_from_json(
            cmake_index.cmake_build_directory,
            cmake_index.codemodel_file_name,
            file.read()
        )


@dataclasses.dataclass
class CMakeToolChainLanguageInformation:
    # These are system include directories
    system_include_directories: typing.List[str]


class CMakeToolChains:
    """Contains data extracted from the CMake toolchains JSON file."""

    def __init__(self, cmake_build_directory: str, toolchains_file_name: str, language_dict=None):
        self.cmake_build_directory = cmake_build_directory
        self.toolchains_file_name = toolchains_file_name
        self.language_dict: typing.Dict[str, CMakeToolChainLanguageInformation] = {}
        if language_dict is not None:
            self.language_dict = language_dict.copy()

    def add_language(self, json_node: dict) -> None:
        language = json_node['language']
        if language in self.language_dict:
            raise ValueError(f'Duplicate language {language}')
        compiler = json_node['compiler']
        include_directories = compiler['implicit']['includeDirectories']
        self.language_dict[language] = CMakeToolChainLanguageInformation(include_directories)

    # def __eq__(self, other):
    #     if self.__class__ != other.__class__:
    #         return False
    #     eq_list = []
    #     for attr in ('cmake_build_directory', 'toolchains_file_name', 'language_dict'):
    #         eq_list.append(getattr(self, attr) == getattr(other, attr))
    #     return all(eq_list)


def cmake_reply_toolchains_from_json(
    cmake_build_directory: str,
    toolchains_file_name: str,
    json_str: str,
) -> CMakeToolChains:
    """Returns a CMakeToolChains from a toolchains JSON string.

    See: https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#object-kind-toolchains
    """
    toolchains_json = json.loads(json_str)
    if 'kind' not in toolchains_json:
        raise ValueError(f'toolchains JSON does not have "kind" attribute')
    if toolchains_json['kind'] != 'toolchains':
        raise ValueError(f'toolchains JSON does not have "kind"="toolchains" but "kind"="{toolchains_json["kind"]}"')
    ret = CMakeToolChains(cmake_build_directory, toolchains_file_name)
    for toolchain_node in toolchains_json['toolchains']:
        ret.add_language(toolchain_node)
    return ret


def cmake_reply_toolchains_from_cmake_index(cmake_index: CMakeIndex) -> CMakeToolChains:
    """Returns a CMakeToolChains from a CMakeIndex."""
    file_path = os.path.join(
        cmake_reply_directory(cmake_index.cmake_build_directory),
        cmake_index.toolchains_file_name,
    )
    with open(file_path) as file:
        return cmake_reply_toolchains_from_json(
            cmake_index.cmake_build_directory,
            cmake_index.toolchains_file_name,
            file.read()
        )


@dataclasses.dataclass
class CMakeTarget:
    """Contains data extracted from the CMake target JSON file."""
    cmake_build_directory: str
    target_file_name: str
    project_path: str
    name: str
    defines: list[str]
    include_paths: list[str]
    sources: list[str]
    language: str


def cmake_reply_target_from_json(
    cmake_build_directory: str,
    target_file_name: str,
    project_path: str,
    json_str: str,
) -> CMakeTarget:
    """Returns a CMakeCodeModel from a target JSON string.

    See: https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#codemodel-version-2-target-object
    """
    sources_json = json.loads(json_str)
    compile_groups = sources_json['compileGroups']
    if len(compile_groups) != 1:
        raise CMakeBuildException(
            'No unique CMake compileGroups found, instead %d found.',
            len(compile_groups)
        )
    compile_group = compile_groups[0]
    # Example:
    # {
    #     "backtrace" : 7,
    #     "define" : "RAPIVOT_MEMORY_TRACE=1"
    # },
    if 'defines' in compile_group:
        defines = [d['define'] for d in compile_group['defines']]
    else:
        defines = []
    if 'include_paths' in compile_group:
        include_paths = [d['path'] for d in compile_group['include_paths']]
    else:
        include_paths = []
    sources = []
    if 'sources' in sources_json:
        for source_node in sources_json['sources']:
            sources.append(source_node['path'])
    language = compile_group['language']
    return CMakeTarget(
        cmake_build_directory, target_file_name, project_path, sources_json['name'],
        defines, include_paths, sources, language,
    )


def cmake_reply_target_from_codemodel(codemodel: CMakeCodeModel) -> CMakeTarget:
    """Return a CMakeTarget from a CMakeCodeModel object."""
    file_path = os.path.join(cmake_reply_directory(codemodel.cmake_build_directory), codemodel.target_file_name)
    with open(file_path) as file:
        return cmake_reply_target_from_json(
            codemodel.cmake_build_directory, codemodel.target_file_name,
            codemodel.project_path, file.read(),
        )


def cmake_reply_target_file_from_build_directory(cmake_build_directory: str) -> CMakeTarget:
    """Return a CMakeTarget from a CMake build directory."""
    cmake_index = cmake_reply_index_from_build_directory(cmake_build_directory)
    cmake_codemodel = cmake_reply_codemodel_from_cmake_index(cmake_index)
    cmake_target = cmake_reply_target_from_codemodel(cmake_codemodel)
    return cmake_target


def is_cmake_build_directory(cmake_build_directory: str) -> bool:
    """Returns True if this is a CMaake build directory and a CMakeTarget can be constructed."""
    ret = True
    try:
        cmake_target = cmake_reply_target_file_from_build_directory(cmake_build_directory)
        if cmake_target is None:
            ret = False
    except CMakeBuildException:
        ret = False
    return ret


@dataclasses.dataclass
class CMakeMetadata:
    """An aggregate class that holds index, codemodel, toolchains and target classes."""
    index: CMakeIndex
    codemodel: CMakeCodeModel
    toolchains: CMakeToolChains
    target: CMakeTarget

    @property
    def system_include_directories(self) -> typing.List[str]:
        language = self.target.language
        ret = self.toolchains.language_dict[language].system_include_directories
        return ret


def cmake_reply_metadata_from_build_directory(cmake_build_directory: str) -> CMakeMetadata:
    """Return a CMakeMetadata from a CMake build directory."""
    cmake_index = cmake_reply_index_from_build_directory(cmake_build_directory)
    cmake_codemodel = cmake_reply_codemodel_from_cmake_index(cmake_index)
    cmake_toolchains = cmake_reply_toolchains_from_cmake_index(cmake_index)
    cmake_target = cmake_reply_target_from_codemodel(cmake_codemodel)
    return CMakeMetadata(cmake_index, cmake_codemodel, cmake_toolchains, cmake_target)
