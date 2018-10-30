import os
import subprocess
import re
import sys
import stat
import platform
import functools
import distutils.ccompiler
import tempfile 

import scorep.helper


def compile_scorep_subsystem(scorep_config):
    """
    Uses the scorep_config to compile the scorep subsystem.
    Returns the name of the compiled subsystem, and the path the the temp folder, where the lib is located
    """

    (include, lib, lib_dir, macro, linker_flags_tmp) = scorep.helper.generate_compile_deps(scorep_config)
    scorep_adapter_init = scorep.helper.generate_compile_init(scorep_config)

    # add -Wl,-no-as-needed to tell the compiler that we really want to link these. Actually this sould be default.
    # as distutils adds extra args at the very end we need to add all the libs
    # after this and skipt the libs later in the extension module
    linker_flags = ["-Wl,-no-as-needed"]
    linker_flags.extend(lib)
    linker_flags.extend(linker_flags_tmp)

    temp_dir = tempfile.mkdtemp(None, "scorep.", None)
    with open(temp_dir + "/scorep_init.c", "w") as f:
        f.write(scorep_adapter_init)
        
    #(include_mpi, lib_mpi, lib_dir_mpi, macro_mpi, linker_flags_mpi_tmp,
     #scorep_adapter_init_mpi) = get_config(scorep_config_mpi)
    #(include_mpi_, lib_mpi_, lib_dir_mpi_, macro_mpi_,
     #linker_flags_mpi_tmp_) = scorep.helper.generate_compile_deps_mpi()
    #include_mpi.extend(include_mpi_)
    #lib_dir_mpi.extend(lib_dir_mpi_)
    #macro_mpi.extend(macro_mpi_)

    #linker_flags_mpi = ["-Wl,-no-as-needed"]
    #linker_flags_mpi.extend(linker_flags_mpi_tmp)
    #linker_flags_mpi.extend(linker_flags_mpi_tmp_)
    #linker_flags_mpi.extend(lib_mpi)
    #linker_flags_mpi.extend(lib_mpi_)

    #with open("./scorep_init_mpi.c", "w") as f:
        #f.write(scorep_adapter_init_mpi)

    subsystem_lib_name = scorep.helper.gen_subsystem_lib_name()

    cc = distutils.ccompiler.new_compiler()
    compiled_subsystem = cc.compile([temp_dir + "/scorep_init.c"])
    cc.link(
        "scorep_init_mpi",
        objects=compiled_subsystem,
        output_filename = subsystem_lib_name,
        output_dir = temp_dir,
        library_dirs = lib_dir,
        extra_postargs=linker_flags)
    
    return(subsystem_lib_name, temp_dir)
