cmake_minimum_required(VERSION 3.12)
project(scorep_bindings)

option(DEV_MODE "Set this to ON to use CMake. However: NO SUPPORT IS PROVIDED, PIP IS THE SUPPORTED INSTALL MODE" OFF)

if(NOT DEV_MODE)
message(SEND_ERROR
  "CMake is only useful to develop this project, no support is provided."
  "To install the module properly use pip. See the Readme for details."
  "To override this you might set DEV_MODE to ON"
  "However: AGAIN NO SUPPORT IS PROVIDED, PIP IS THE SUPPORTED INSTALL MODE")
endif()

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

find_package(Scorep REQUIRED)
find_package(Python REQUIRED COMPONENTS Interpreter Development)

Python_add_library(_bindings
  src/methods.cpp src/scorep_bindings.cpp src/scorepy/events.cpp
)
if(Python_VERSION_MAJOR GREATER_EQUAL 3)
  target_sources(_bindings PRIVATE src/classes.cpp src/scorepy/cInstrumenter.cpp src/scorepy/pythonHelpers.cpp)
endif()
target_link_libraries(_bindings PRIVATE Scorep::Plugin)
target_compile_features(_bindings PRIVATE cxx_std_11)
target_compile_definitions(_bindings PRIVATE PY_SSIZE_T_CLEAN)
target_include_directories(_bindings PRIVATE src)

set_target_properties(_bindings PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/site-packages/scorep
)
add_custom_target(ScorepModule ALL
  ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_LIST_DIR}/scorep $<TARGET_FILE_DIR:_bindings>
  COMMENT "Copying module files to build tree"
)

enable_testing()
add_test(NAME ScorepPythonTests
         COMMAND Python::Interpreter -m pytest
         WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/test
)
set(pythonPath ${CMAKE_CURRENT_BINARY_DIR}/site-packages)
if(ENV{PYTHONPATH})
  string(PREPEND pythonPath "$ENV{PYTHONPATH}:")
endif()
set_tests_properties(ScorepPythonTests PROPERTIES ENVIRONMENT "PYTHONPATH=${pythonPath}")

set(INSTALL_DIR "lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/site-packages")

install(DIRECTORY scorep DESTINATION ${INSTALL_DIR})
install(TARGETS _bindings DESTINATION ${INSTALL_DIR}/scorep)
