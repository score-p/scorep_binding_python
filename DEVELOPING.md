# Developing

## Formatting / Codestyle

C/C++ code must be formatted by clang-format-9 according to the .clang-format file.   
Python code must pass flake8 checks as defined in the .flake8 file.

Besides that being consistent and readable is key.

## Build system

The only officially supported way to install this module is by `pip`.

However there exists a semi-supported CMake-based build system suitable for development.
No issues against that are allowed but PRs fixing it in case of problems are welcome.
This build system is especially suitable for development as e.g. include paths for C++ are correctly searched for and set up for use by IDEs or other tools.
For example it works well with Visual Studio Code given the approriate extensions (C++, Python, CMake) are installed, see their documentation for details.

The CMake build system creates a folder `site-packages` in the build folder where the C/C++ extension module and the `scorep` module are copied to on each build (e.g. `make`-call).
It is hence possible to add that folder to the `PYTHONPATH` environment variable, build the project and start debugging or execute the tests in `test/test.py`.

Note that changes to the Python source files are not reflected in that folder unless a build is executed.
Also when deleting Python files it is recommended to clear and recreate the build folder.
