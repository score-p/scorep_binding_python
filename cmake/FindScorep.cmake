# Copyright (c) 2016, Technische Universität Dresden, Germany
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted
# provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions
#    and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
#    and the following disclaimer in the documentation and/or other materials provided with the
#    distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse
#    or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

IF(SCOREP_CONFIG_PATH)
    FIND_PROGRAM(SCOREP_CONFIG NAMES scorep-config
        PATHS
        ${SCOREP_CONFIG_PATH}
        /opt/scorep/bin
    )
ELSE(SCOREP_CONFIG_PATH)
    FIND_PROGRAM(SCOREP_CONFIG NAMES scorep-config
        PATHS
        /opt/scorep/bin
    )
ENDIF(SCOREP_CONFIG_PATH)

IF(NOT SCOREP_CONFIG)
    MESSAGE(STATUS "no scorep-config found")
    set(SCOREP_FOUND false)
ELSE(NOT SCOREP_CONFIG)

    message(STATUS "SCOREP library found. (using ${SCOREP_CONFIG})")

    execute_process(COMMAND ${SCOREP_CONFIG} "--user" "--cppflags" OUTPUT_VARIABLE SCOREP_CONFIG_FLAGS)

    string(REGEX MATCHALL "-I[^ ]*" SCOREP_CONFIG_INCLUDES "${SCOREP_CONFIG_FLAGS}")
    foreach(inc ${SCOREP_CONFIG_INCLUDES})
        string(SUBSTRING ${inc} 2 -1 inc)
        list(APPEND SCOREP_INCLUDE_DIRS ${inc})
    endforeach()

    string(REGEX MATCHALL "(^| +)-[^I][^ ]*" SCOREP_CONFIG_CXXFLAGS "${SCOREP_CONFIG_FLAGS}")
    foreach(flag ${SCOREP_CONFIG_CXXFLAGS})
        string(STRIP ${flag} flag)
        list(APPEND SCOREP_CXX_FLAGS ${flag})
    endforeach()

    unset(SCOREP_CONFIG_FLAGS)
    unset(SCOREP_CONFIG_INCLUDES)
    unset(SCOREP_CONFIG_CXXFLAGS)

    execute_process(COMMAND ${SCOREP_CONFIG} "--user" "--ldflags" OUTPUT_VARIABLE _LINK_LD_ARGS)
    STRING( REPLACE " " ";" _LINK_LD_ARGS ${_LINK_LD_ARGS} )
    FOREACH( _ARG ${_LINK_LD_ARGS} )
        IF(${_ARG} MATCHES "^-L")
            STRING(REGEX REPLACE "^-L" "" _ARG ${_ARG})
            SET(SCOREP_LINK_DIRS ${SCOREP_LINK_DIRS} ${_ARG})
        ENDIF(${_ARG} MATCHES "^-L")
    ENDFOREACH(_ARG)

    execute_process(COMMAND ${SCOREP_CONFIG} "--user" "--libs" OUTPUT_VARIABLE _LINK_LD_ARGS)
    STRING( REPLACE " " ";" _LINK_LD_ARGS ${_LINK_LD_ARGS} )
    FOREACH( _ARG ${_LINK_LD_ARGS} )
        IF(${_ARG} MATCHES "^-l")
            STRING(REGEX REPLACE "^-l" "" _ARG ${_ARG})
            FIND_LIBRARY(_SCOREP_LIB_FROM_ARG NAMES ${_ARG}
                PATHS
                ${SCOREP_LINK_DIRS}
            )
            IF(_SCOREP_LIB_FROM_ARG)
                SET(SCOREP_LIBRARIES ${SCOREP_LIBRARIES} ${_SCOREP_LIB_FROM_ARG})
            ENDIF(_SCOREP_LIB_FROM_ARG)
            UNSET(_SCOREP_LIB_FROM_ARG CACHE)
        ENDIF(${_ARG} MATCHES "^-l")
    ENDFOREACH(_ARG)

    set(SCOREP_FOUND true)
ENDIF(NOT SCOREP_CONFIG)

include (FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(
    Scorep DEFAULT_MSG
    SCOREP_CONFIG
    SCOREP_LIBRARIES
    SCOREP_INCLUDE_DIRS
)

add_library(Scorep::Scorep INTERFACE IMPORTED)
set_target_properties(Scorep::Scorep PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${SCOREP_INCLUDE_DIRS}"
    INTERFACE_LINK_LIBRARIES "${SCOREP_LIBRARIES}"
)

add_library(Scorep::Plugin INTERFACE IMPORTED)
set_target_properties(Scorep::Plugin PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${SCOREP_INCLUDE_DIRS}"
)

mark_as_advanced(SCOREP_CONFIG)
