====
cpip
====

CPIP is a C/C++ Preprocessor implemented in Python. It faithfully records all aspects of preprocessing.


* Free software: GNU General Public License v2
* Documentation: https://cpip.readthedocs.io.

An Example
-----------

The top level script ``CPIPMain.py`` acts like a pre-processor that generates HTML and SVG output for a source code file or directory. This output makes it easy to understand what the pre-processor is doing to your source.

Here is that output when pre-processing a single Linux kernel file ``cpu.c``:

The ``index.html`` landing page shows how ``CPIPMain.py`` was invoked[#f1]_:

.. image:: docs/doc_src/examples/images/HTMLLinux_cpu.c_Index.png
        :alt: CPIPMain.py's index.html landing page.

This has a single link that takes you to the landing page for the file ``cpu.c``:

.. image:: docs/doc_src/examples/images/HTMLLinux_cpu.c_Home_Top.png
        :alt: CPIP landing page after preprocessing cpu.c from the Linux kernel.


.. image:: docs/doc_src/examples/images/HTMLLinux_cpu.c_Home_Top.png
        :alt: CPIP landing page after preprocessing cpu.c from the Linux kernel.

.. image:: docs/doc_src/examples/images/HTMLLinux_cpu.c_ITU_edit.png
        :alt: Annotated source code of cpu.c

.. image:: docs/doc_src/examples/images/HTMLLinux_cpu.c_TU_edit.png
        :alt: Annotated translation unit produced by cpu.c

.. image:: docs/doc_src/examples/images/SVG_CPU_FileDetail_FileStack.png
        :alt: Example of the file stack pop-up in the SVG include graph.

.. image:: docs/doc_src/examples/images/HTMLLinux_cpu.c_CondComp.png
        :alt: Conditional compilation in the translation unit.

.. image:: docs/doc_src/examples/images/HTMLLinux_cpu.c_Macro_Detail.png
        :alt: Macro BITMAP_LAST_WORD_MASK details: definition, where defined, where used and two way dependencies.


Features
--------

* TODO

Status
------

.. image:: https://img.shields.io/pypi/v/cpip.svg
        :target: https://pypi.python.org/pypi/cpip

.. image:: https://img.shields.io/travis/paulross/cpip.svg
        :target: https://travis-ci.org/paulross/cpip

.. image:: https://readthedocs.org/projects/cpip/badge/?version=latest
        :target: https://cpip.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/paulross/cpip/shield.svg
     :target: https://pyup.io/repos/github/paulross/cpip/
     :alt: Updates

Licence
-------

CPIP is a C/C++ Preprocessor implemented in Python.
Copyright (C) 2008-2017 Paul Ross

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


.. rubric:: Footnotes

.. [#f1] This was invoked by::

    python3 CPIPMain.py -kp -l20 -o ../../output/linux/cpu -S __STDC__=1 -D __KERNEL__ -D __EXPORTED_HEADERS__ -D BITS_PER_LONG=64 -D CONFIG_HZ=100 -D __x86_64__ -D __GNUC__=4 -D __has_feature(x)=0 -D __has_extension=__has_feature -D __has_attribute=__has_feature -D __has_include=__has_feature -P ~/dev/linux/linux-3.13/include/linux/kconfig.h -J /usr/include/ -J /usr/include/c++/4.2.1/ -J /usr/include/c++/4.2.1/tr1/ -J /Users/paulross/dev/linux/linux-3.13/include/ -J /Users/paulross/dev/linux/linux-3.13/include/uapi/ -J ~/dev/linux/linux-3.13/arch/x86/include/uapi/ -J ~/dev/linux/linux-3.13/arch/x86/include/ -J ~/dev/linux/linux-3.13/arch/x86/include/generated/ ~/dev/linux/linux-3.13/kernel/cpu.c



