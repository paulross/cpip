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

.. list-table:: CMake Metadata Files
   :widths: 10 30 30
   :header-rows: 1

   * - File Prefix
     - Json Path
     - Description
   * - ``codemodel``
     - ``["objects"][0]["jsonFile"] && ["objects"][0]["kind"] == "codemodel``
     - This Code Model file gives an overall picture of the build, in particular the location of the project
       and the target file name (see below).
       See the CMake documentation for `codemodel-v2-....json <https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#object-kind-codemodel>`_.
   * - ``toolchains``
     - ``["objects"][0]["jsonFile"] && ["objects"][0]["kind"] == "toolchains``
     - The tool chains file gives various information for the toolchain for a specific language (C, CXX etc.).
       In particular the toolchain identifies the location of the system headers.
       See the CMake documentation for `toolchains-v1-....json <https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#object-kind-toolchains>`_.

-------------------
The Target File
-------------------

This is identified by the ``target`` file and contains
(`CMake target documentation <https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#codemodel-version-2-target-object>`_):

.. list-table:: CMake Target File
   :widths: 10 30 30
   :header-rows: 1

   * - Information
     - Json Path
     - Description
   * - ``#define`` s
     - ``["compileGroups"][0]["defines"][n]["define"]``
     - These are only the ``#defines`` that are made in the ``CMakeLists.txt`` typically with
       `add_compile_definitions() <https://cmake.org/cmake/help/latest/command/add_compile_definitions.html#command:add_compile_definitions>`_.
       Other macros may need to  be specified to CPIP to ensure a successful build.
   * - Search paths
     - ``["compileGroups"][0]["includes"][n]["path"]``
     - These are only the search paths for includes.
       CMake does not distinguish between user and system search paths.
   * - Source files
     - ``["sources"][n]["path"]``
     - These are the source files (ITUs) that make up the project.

---------------------------
Building the CMake Metadata
---------------------------

Given that the ``PROJECT_DIRECTORY`` is one that contains a ``CMakeLists.txt``.

.. code-block:: shell

    cmake -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_MAKE_PROGRAM=ninja" -G Ninja -S <PROJECT_DIRECTORY> -B <PROJECT_DIRECTORY>/cmake-build-debug

====================
CPIPMain and CMake
====================

This is an example of creating a demonstratoin project with CMake and CPIP.

---------------------------
Example
---------------------------

In the directory ``CMake`` there is an example CMake project at ``CMake/CPIPDemo``.
This contains a CMake version of the demonstration C project at ``demo/``.
The CMake metadata is in ``CMake/CPIPDemo/cmake-build-debug/.cmake/api/v1/reply``

The CMake metadata can be built thus:

.. code-block:: shell

    $ cd CMake/CPIPDemo/
    $ cmake --build cmake-build-debug/ --target CPIPDemo

And the CPIP build can be created thus (shell is in the CPIP project root):

.. code-block:: shell

    $ cpipmain -l20 -o tmp/output_17 CMake/CPIPDemo/cmake-build-debug/ -D __GNUC__=4 -D __x86_64__
    2025-09-05 11:38:34,306 INFO     [79783] preProcessTheseFilesMP(): Setting multi-processing jobs to 3
    CPU time =    7.805 (S)
    Bye, bye!

Which produces:

.. code-block:: shell

    tmp/output_17/
    ├── cpip.css
    ├── index.html
    ├── main.c_fc01e7d1a84d760ca8074d5d1724798a
    │   ├── Availability.h_f1be37e1141314a140dc5a42df6f704a.html
    │   ├── AvailabilityInternal.h_58ad0b27ea9b59228ae12b04a905ae75.html
    │   ├── AvailabilityInternalLegacy.h_9461f6a8f02eae8cc35ba41afe1b65db.html
    │   ├── AvailabilityVersions.h_e00a9515977fb3d770f6a7aa20e2440a.html
    │   ├── _common.h_fed43917b67f1d628a89beb185c1e186.html
    │   ├── _ctermid.h_2e2560e090d4ae8451daaf3852c0137c.html
    │   ├── _int16_t.h_a7b530c04a675b3436ba57966460355e.html
    │   ├── _int32_t.h_20fc0ac84f2f03cc6164502ba17b4149.html
    │   ├── _int64_t.h_511bb40f50c30158e5ac291ff993f77a.html
    │   ├── _int8_t.h_7a3d100b8e9ffcc984e8052d0bcdfec7.html
    │   ├── _intptr_t.h_f507461a5f664cfd15c6c5c766338ae2.html
    │   ├── _null.h_36b66f5492b9d3122c61c2a1b26a4ee6.html
    │   ├── _off_t.h_ffa142c3d9778155363f00644ae7cf61.html
    │   ├── _posix_availability.h_0055a547e94dc4ba6e23cedbbbb2c616.html
    │   ├── _pthread_types.h_0f5bf2896c610e2d9a5ee4e5971a87de.html
    │   ├── _seek_set.h_401fb7a6bfd1b355e89b5cff0fcb52a2.html
    │   ├── _size_t.h_e99b7b16375d2a061c59e2b616026be5.html
    │   ├── _ssize_t.h_e2a21aec838fb003ba91ec1ee0fe8e29.html
    │   ├── _stdio.h_0cfcd667cb1c06df8d7c8f1a282f2fce.html
    │   ├── _stdio.h_ec39fa8df6525ce6e88d1b5037670060.html
    │   ├── _symbol_aliasing.h_d413b22dadf9eff099692d6e27ef527f.html
    │   ├── _types.h_175558f44d474c7ef486f906d7f4adb1.html
    │   ├── _types.h_807e7c8f1d6d0ace7d9073b48cb9a279.html
    │   ├── _types.h_b7386cf94931442fd10b3c0ec4a7e4bb.html
    │   ├── _types.h_e65c86482f6e0efd4e47cb0c78b4abb5.html
    │   ├── _u_int16_t.h_53f7f62510e8877a410409b735a8bf67.html
    │   ├── _u_int32_t.h_2551eabf1f57c84780d0a519b2380008.html
    │   ├── _u_int64_t.h_89ad847b32c3b1683689d8bff1c8a17e.html
    │   ├── _u_int8_t.h_b9460cd80e595ce951ac8cec91294782.html
    │   ├── _uintptr_t.h_f4695ba999b0b9e64c7210e52493758f.html
    │   ├── _va_list.h_7781fe1126c9cf1114050f3699b8385c.html
    │   ├── cdefs.h_ec6de5126d1e06b6c3b73489f62d7d60.html
    │   ├── cpip.css
    │   ├── index.html
    │   ├── index_main.c_fc01e7d1a84d760ca8074d5d1724798a.html
    │   ├── macros.html
    │   ├── macros_noref.html
    │   ├── macros_ref.html
    │   ├── main.c.ccg.html
    │   ├── main.c.html
    │   ├── main.c.include.svg
    │   ├── main.c.include.txt.html
    │   ├── main.c_fc01e7d1a84d760ca8074d5d1724798a.html
    │   ├── stdio.h_244ae8183814383a1d30d2ab5fd765b6.html
    │   ├── stdio.h_bbbf9f5daef7fd250b6b2819e8ab256f.html
    │   ├── system.h_3f2c07a4113e19ff2ba89c942703133a.html
    │   ├── types.h_24b1b0cf34bbb66daa4fbd9f0e5cbb4b.html
    │   ├── types.h_57c42f9dcdc1b60081a822542de8dfac.html
    │   └── user.h_be48f2c223a53b941527a89bb3998255.html
    ├── system.h_3f2c07a4113e19ff2ba89c942703133a
    │   ├── cpip.css
    │   ├── index.html
    │   ├── index_system.h_3f2c07a4113e19ff2ba89c942703133a.html
    │   ├── macros.html
    │   ├── macros_noref.html
    │   ├── macros_ref.html
    │   ├── system.h.ccg.html
    │   ├── system.h.html
    │   ├── system.h.include.svg
    │   ├── system.h.include.txt.html
    │   └── system.h_3f2c07a4113e19ff2ba89c942703133a.html
    └── user.h_be48f2c223a53b941527a89bb3998255
        ├── cpip.css
        ├── index.html
        ├── index_user.h_be48f2c223a53b941527a89bb3998255.html
        ├── macros.html
        ├── macros_noref.html
        ├── macros_ref.html
        ├── system.h_3f2c07a4113e19ff2ba89c942703133a.html
        ├── user.h.ccg.html
        ├── user.h.html
        ├── user.h.include.svg
        ├── user.h.include.txt.html
        └── user.h_be48f2c223a53b941527a89bb3998255.html

    3 directories, 74 files
