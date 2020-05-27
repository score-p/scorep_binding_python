# Developing
We appreciate any contributions to the Score-P Python Bindings.
However, there are a few policies we agreed on and which are relevant for contributions.
These are detailed below. 

## Fromatting / Codestyle

Readable and consistent code makes it easy to understand your changes.
Therefore the GitHub CI system has checks using `clang-format-9` and `flake8` in place.
Please make sure that these test pass, before making a Pull Request.
If you do not use the GitHub CI process, you can use the provided `.flake8` and `.clang-format` files, to check your code manually.

## Build system

The official way to build and install this module is using `pip`.
Please make sure that all changes, you introduce, work with `pip install .`.

However, you might have noted that there is a CMake-based build system in place as well.
We do not support this build system, and it might be outdated or buggy.
Thorough, we do not actively maintain the CMake Buildsystem, and will not help you fix issues to that build system, Pull Requests against it might be accepted.

You might find this build system helpful for development, especially if you are doing C/C++ things:
* Include paths for C++ are correctly searched for and set up for use by IDEs or other tools. For example, Visual Studio Code, given the appropriate extensions (C++, Python, CMake)
* Creates a folder site-packages in the build folder where the C/C++ extension module and the scorep module are copied to on each build (e.g. make-call). Hence it is possible to add that folder to the PYTHONPATH environment variable, build the project and start debugging or execute the tests in test/test.py.

Please note, that changes to the Python source files are not reflected in that folder unless a build is executed. Also, if you delete Python files, we recommended to clear and recreate the build folder.
