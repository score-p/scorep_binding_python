# Developing
We appreciate any contributions to the Score-P Python Bindings.
However, there are a few policies we agreed on and which are relevant for contributions.
These are detailed below. 

## Formatting / Codestyle

Readable and consistent code makes it easy to understand your changes.
Therefore the CI system has checks using `clang-format-9` and `flake8` in place.
Please make sure that these test pass, when making a Pull Request.
These tests will tell you the issues and often also how to fix them.
Prior to opening a Pull Request you can use the provided `.flake8` and `.clang-format` files, to check your code locally and run `clang-format-9` or `autopep8` to fix most of them automatically.

## Build system

The official way to build and install this module is using `pip`.
Please make sure that all changes, you introduce, work with `pip install .`.

However, you might have noticed that there is a CMake-based build system in place as well.
We do not support this build system, and it might be outdated or buggy.
Although, we do not actively maintain the CMake build system, and will not help you fix issues related to it, Pull Requests against it might be accepted.

You might find this build system helpful for development, especially if you are doing C/C++ things:
* Include paths for C++ are correctly searched for and set up for use by IDEs or other tools. For example Visual Studio Code works out of the box, given the appropriate extensions (C++, Python, CMake) are installed.
* A folder `site-packages` is created in the build folder where the C/C++ extension module and the scorep module are copied to on each build (e.g. `make`-call). Hence it is possible to add that folder to the PYTHONPATH environment variable, build the project and start debugging or execute the tests in test/test.py.
* A `test` target exists which can be run to execute all tests.

Please note, that changes to the Python source files are not reflected in the build folder unless a build is executed.
Also, if you delete Python files, we recommended to clear and recreate the build folder.
