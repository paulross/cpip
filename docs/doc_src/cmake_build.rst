.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>


################################
CPIP Building From a Cmake Build
################################

Looks like a fairly easy way to discover the necessary information for a Doxygen file can be obtained from the cmake build files.
For example: ``cmake-build-debug/.cmake/api/v1/reply/target-SkipList-Debug-091d871282c22504d7ce.json`` which has all the
``#define``s, include paths, source files, headers etc.

The starting point is `index-<timestamp>.json <https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#v1-reply-index-file>`_
at ``cmake-build-debug/.cmake/api/v1/reply/index-2025-04-12T12-03-02-0210.json``.
In the path ``"objects"][index]`` where ``"kind" : "codemodel",]["jsonFile"]`` refers to
`codemodel-v2-....json <https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#object-kind-codemodel`_.
This has at ``["configurations"][0]["targets"][0]["jsonFile"]`` the value ``"target-SkipList-Debug-091d871282c22504d7ce.json"``.

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
