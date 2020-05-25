cmake_minimum_required(VERSION 3.12)
project(scorep_bindings)

message(AUTHOR_WARNING
  "CMake is only useful to develop this project, no support is provided."
  "To install the module properly use pip. See the Readme for details.")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

find_package(Scorep REQUIRED)
find_package(Python REQUIRED COMPONENTS Interpreter Development)

Python_add_library(scorep_bindings src/scorep.cpp)
target_link_libraries(scorep_bindings PRIVATE Scorep::Scorep)
target_compile_features(scorep_bindings PRIVATE cxx_std_11)
set_target_properties(scorep_bindings PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/site-packages/scorep
)
add_custom_target(ScorepModule ALL
  ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_LIST_DIR}/scorep $<TARGET_FILE_DIR:scorep_bindings>
  COMMENT "Copying module files to build tree"
)

enable_testing()
add_test(NAME ScorepPythonTests
         COMMAND Python::Interpreter test.py
         WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/test
)
set(pythonPath ${CMAKE_CURRENT_BINARY_DIR}/site-packages)
if(ENV{PYTHONPATH})
  string(PREPEND pythonPath "$ENV{PYTHONPATH}:")
endif()
set_tests_properties(ScorepPythonTests PROPERTIES ENVIRONMENT "PYTHONPATH=${pythonPath}")

set(INSTALL_DIR "lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/site-packages")

install(DIRECTORY scorep DESTINATION ${INSTALL_DIR})
install(TARGETS scorep_bindings DESTINATION ${INSTALL_DIR}/scorep)
