.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

#######################################
Building CPIP Output From a CMake Build
#######################################

With a project that is built using `CMake <https://cmake.org>`_ the CMake generated metadata can be used to create the
CPIP build.
The metadata is documented in the
`CMake metadata documentation <https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#cmake-file-api-7>`_
The metadata gives:

* Any ``#define`` that is made in the ``CMakeLists.txt`` typically with
  `add_compile_definitions() <https://cmake.org/cmake/help/latest/command/add_compile_definitions.html#command:add_compile_definitions>`_
* Search paths for included files. CMake does not distinguish between user and system search paths.
* The source files (ITUs) that make up the project.
* The system search paths for the toolchain.

====================
CMake Build Metadata
====================

The metadata is contained in the directory ``<CMAKE_BUILD_DIRECTORY>/.cmake``.
It is arranged like this:

.. code-block:: shell

    .cmake/
    └── api
        └── v1
            ├── query
            │   ├── cache-v2
            │   ├── cmakeFiles-v1
            │   ├── codemodel-v2
            │   └── toolchains-v1
            └── reply
                ├── cache-v2-849e6059f55d78b15468.json
                ├── cmakeFiles-v1-2592f079569bad70298b.json
                ├── codemodel-v2-456473262521f32c0361.json
                ├── directory-.-Debug-f5ebdc15457944623624.json
                ├── index-2025-09-04T20-17-55-0941.json
                ├── target-CPIPDemo-Debug-6354d69e1abf2e817afb.json
                └── toolchains-v1-6fd81e3fab63b46d5ade.json

Of particular interest is ``/api/v1/reply/``, for example ``cmake-build-debug/.cmake/api/v1/reply/``.

-------------------
The Index File
-------------------

The starting point in that directory is ``index-<timestamp>.json``, the format is
`described here <https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#v1-reply-index-file>`_

This leads to these files:

################################
CPIP Building From a CMake Build
################################

Looks like a fairly easy way to discover the necessary information for a Doxygen file can be obtained from the cmake build files.
For example: ``cmake-build-debug/.cmake/api/v1/reply/target-SkipList-Debug-091d871282c22504d7ce.json`` which has all the
``#define``s, include paths, source files, headers etc.

=====================
CMake Build Structure
=====================

The starting point is `index-<timestamp>.json <https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#v1-reply-index-file>`_
at ``cmake-build-debug/.cmake/api/v1/reply/index-2025-04-12T12-03-02-0210.json``.
In the path ``["objects"]`` where ``"kind" == "codemodel"`` then get the value for ``["jsonFile"]``.
This refers to
`codemodel-v2-....json <https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#object-kind-codemodel`_.
The has the target file at ``["configurations"][0]["targets"][0]["jsonFile"]`` the value ``"target-SkipList-Debug-091d871282c22504d7ce.json"``.

The `"target-SkipList-Debug-091d871282c22504d7ce.json" <https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#codemodel-version-2-target-object`_ file has:

- The project name at ``["artifacts"][0]["path"]``.
- ``#define``s at ``["compileGroups"][0]["defines"][n]["define"``.
- ``#includes``s at `["compileGroups"][0]["includes"][n]["path"``.
- ``["sourceGroups"]`` gives a list of indexes for ``"name" : "Header Files"` and `"name" : "Source Files"``.
  The actual values are in `["sources"][n]["path"]`.

See the `cmake documentation <https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#api-v1>`_.

Perhaps we can generate these files without doing the build, as CLion "Reload CMake Project" does:

``cmake -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_MAKE_PROGRAM=.../ninja" -G Ninja -S /Users/engun/CLionProjects/skiplist -B /Users/engun/CLionProjects/skiplist/cmake-build-debug``

Whereas the actual build is:

``cmake --build /Users/engun/CLionProjects/skiplist/cmake-build-release --target SkipList -j 6``
