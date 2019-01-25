import os
import subprocess
import re
import sys
import stat
import platform
import functools
import distutils.ccompiler
import tempfile
import shutil

import scorep.helper


def gen_subsystem_lib_name():
    """
    generate the name for the subsystem lib.
    """
    mpi_lib_name = "libscorep_init_subsystem-{}.so".format(scorep.helper.get_python_version())
    return mpi_lib_name


def generate_subsystem_code(config=[]):
    """
    Generates the data needed to be preloaded.
    """

    scorep_config = ["scorep-config"] + config + ["--user"]

    (retrun_code, _, _) = scorep.helper.call(scorep_config)
    if retrun_code != 0:
        raise ValueError(
            "given config {} is not supported".format(scorep_config))
    (_, scorep_adapter_init, _) = scorep.helper.call(scorep_config + ["--adapter-init"])

    return scorep_adapter_init


def generate(scorep_config):
    """
    Uses the scorep_config to compile the scorep subsystem.
    Returns the name of the compiled subsystem, and the path the the temp folder, where the lib is located
    """

    (include, lib, lib_dir, macro, linker_flags_tmp) = scorep.helper.generate_compile_deps(scorep_config)
    scorep_adapter_init = generate_subsystem_code(scorep_config)

    # add -Wl,-no-as-needed to tell the compiler that we really want to link these. Actually this sould be default.
    # as distutils adds extra args at the very end we need to add all the libs
    # after this and skipt the libs later in the extension module
    linker_flags = ["-Wl,-no-as-needed"]
    linker_flags.extend(lib)
    linker_flags.extend(linker_flags_tmp)

    temp_dir = tempfile.mkdtemp(prefix="scorep.")
    with open(temp_dir + "/scorep_init.c", "w") as f:
        f.write(scorep_adapter_init)

    subsystem_lib_name = gen_subsystem_lib_name()

    cc = distutils.ccompiler.new_compiler()
    compiled_subsystem = cc.compile([temp_dir + "/scorep_init.c"], output_dir=temp_dir)
    cc.link(
        "scorep_init_mpi",
        objects=compiled_subsystem,
        output_filename=subsystem_lib_name,
        output_dir=temp_dir,
        library_dirs=lib_dir,
        extra_postargs=linker_flags)

    os.environ["SCOREP_PYTHON_BINDINGS_TEMP_DIR"] = temp_dir
    return(subsystem_lib_name, temp_dir)


def clean_up(keep_files=True):
    """
    deletes the files that are associated to subsystem

    @param keep_files do not delete the generated files. For debugging.
    """
    if keep_files:
        return
    else:
        if ("SCOREP_PYTHON_BINDINGS_TEMP_DIR" in os.environ) and (os.environ["SCOREP_PYTHON_BINDINGS_TEMP_DIR"] != ""):
            shutil.rmtree(os.environ["SCOREP_PYTHON_BINDINGS_TEMP_DIR"])
            
