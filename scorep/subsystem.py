import os
import sys
import distutils.ccompiler
import tempfile
import shutil

import scorep.helper


def gen_subsystem_lib_name():
    """
    generate the name for the subsystem lib.
    """
    mpi_lib_name = "libscorep_init_subsystem-{}.so".format(
        scorep.helper.get_python_version())
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
    (_, scorep_adapter_init, _) = scorep.helper.call(
        scorep_config + ["--adapter-init"])

    return scorep_adapter_init


def generate(scorep_config, keep_files=False):
    """
    Uses the scorep_config to compile the scorep subsystem.
    Returns the name of the compiled subsystem, and the path the the temp folder, where the lib is located

    @param scorep_config scorep configuration to build subsystem
    @param keep_files whether to keep the generated files, or not.
    """

    (include, lib, lib_dir, macro,
     linker_flags_tmp) = scorep.helper.generate_compile_deps(scorep_config)
    scorep_adapter_init = generate_subsystem_code(scorep_config)

    # add -Wl,-no-as-needed to tell the compiler that we really want to link these. Actually this sould be default.
    # as distutils adds extra args at the very end we need to add all the libs
    # after this and skipt the libs later in the extension module
    linker_flags = ["-Wl,-no-as-needed"]
    linker_flags.extend(lib)
    linker_flags.extend(linker_flags_tmp)

    temp_dir = tempfile.mkdtemp(prefix="scorep.")
    if keep_files:
        sys.stderr.write(
            "Score-P files are keept at: {}".format(temp_dir),
            file=sys.stderr)

    with open(temp_dir + "/scorep_init.c", "w") as f:
        f.write(scorep_adapter_init)

    subsystem_lib_name = gen_subsystem_lib_name()

    cc = distutils.ccompiler.new_compiler()
    compiled_subsystem = cc.compile(
        [temp_dir + "/scorep_init.c"], output_dir=temp_dir)
    cc.link(
        "scorep_init_mpi",
        objects=compiled_subsystem,
        output_filename=subsystem_lib_name,
        output_dir=temp_dir,
        library_dirs=lib_dir,
        extra_postargs=linker_flags)

    os.environ["SCOREP_PYTHON_BINDINGS_TEMP_DIR"] = temp_dir
    return(subsystem_lib_name, temp_dir)


def init_environment(scorep_config=[], keep_files=False):  # should move to subsystem
    """
    Set the inital needed environmet variables, to get everythin up an running.
    As a few variables interact with LD env vars, the programms needs to be restarted after this.
    The function set the env var `SCOREP_PYTHON_BINDINGS_INITALISED` to true, once it is done with
    initalising.

    @param scorep_config configuration flags for score-p
    @param keep_files whether to keep the generated files, or not.
    """

    if ("LD_PRELOAD" in os.environ) and (
            "libscorep" in os.environ["LD_PRELOAD"]):
        raise RuntimeError(
            "Score-P is already loaded. This should not happen at this point")

    subsystem_lib_name, temp_dir = scorep.subsystem.generate(
        scorep_config, keep_files)
    scorep_ld_preload = scorep.helper.generate_ld_preload(scorep_config)

    scorep.helper.add_to_ld_library_path(temp_dir)

    preload_str = scorep_ld_preload + " " + subsystem_lib_name
    if "LD_PRELOAD" in os.environ:
        sys.stderr.write(
            "LD_PRELOAD is already specified. If Score-P is already loaded this might lead to errors.")
        preload_str = preload_str + " " + os.environ["LD_PRELOAD"]
        os.environ["LD_PRELOAD_SCOREP_BACKUP"] = os.environ["LD_PRELOAD"]
    os.environ["LD_PRELOAD"] = preload_str


def reset_pereload():
    """
    resets the environment variable `LD_PRELOAD` to the value before init_environment was called.
    """
    if "LD_PRELOAD_SCOREP_BACKUP" in os.environ:
        os.environ["LD_PRELOAD"] = os.environ["LD_PRELOAD_SCOREP_BACKUP"]
    else:
        del os.environ["LD_PRELOAD"]


def clean_up(keep_files=True):
    """
    deletes the files that are associated to subsystem

    @param keep_files do not delete the generated files. For debugging.
    """
    if keep_files:
        return
    else:
        if ("SCOREP_PYTHON_BINDINGS_TEMP_DIR" in os.environ) and (
                os.environ["SCOREP_PYTHON_BINDINGS_TEMP_DIR"] != ""):
            shutil.rmtree(os.environ["SCOREP_PYTHON_BINDINGS_TEMP_DIR"])
