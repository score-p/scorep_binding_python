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

set(INSTALL_DIR "lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/site-packages")

install(DIRECTORY scorep DESTINATION ${INSTALL_DIR})
install(TARGETS scorep_bindings DESTINATION ${INSTALL_DIR}/scorep)
