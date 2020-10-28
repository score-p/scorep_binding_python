import os
import sys
import distutils.ccompiler
import tempfile
import shutil

import scorep.helper


def generate_subsystem_lib_name():
    """
    generate the name for the subsystem lib.
    """
    mpi_lib_name = "libscorep_init_subsystem-{}.so".format(
        scorep.helper.get_python_version())
    return mpi_lib_name


def generate_ld_preload(scorep_config):
    """
    This functions generates a string that needs to be passed to $LD_PRELOAD.
    After this string is passed, the tracing needs to be restarted with this $LD_PRELOAD in env.

    @return ld_preload string which needs to be passed to LD_PRELOAD
    """

    (_, preload, _) = scorep.helper.call(
        ["scorep-config"] + scorep_config + ["--user", "--preload-libs"])
    return preload


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
    if ("-lscorep_adapter_opari2_mgmt" in lib):
        scorep_adapter_init += "\n"
        scorep_adapter_init += "/* OPARI dependencies */\n"
        scorep_adapter_init += "void POMP2_Init_regions(){}\n"
        scorep_adapter_init += "size_t POMP2_Get_num_regions(){return 0;};\n"
        scorep_adapter_init += "void POMP2_USER_Init_regions(){};\n"
        scorep_adapter_init += "size_t POMP2_USER_Get_num_regions(){return 0;};\n"

    # add -Wl,-no-as-needed to tell the compiler that we really want to link these. Actually this sould be default.
    # as distutils adds extra args at the very end we need to add all the libs
    # after this and skipt the libs later in the extension module
    linker_flags = ["-Wl,-no-as-needed"]
    linker_flags.extend(lib)
    linker_flags.extend(linker_flags_tmp)

    temp_dir = tempfile.mkdtemp(prefix="scorep.")
    if keep_files:
        sys.stderr.write(
            "Score-P files are keept at: {}\n".format(temp_dir))
        sys.stderr.flush()

    with open(temp_dir + "/scorep_init.c", "w") as f:
        f.write(scorep_adapter_init)

    subsystem_lib_name = generate_subsystem_lib_name()

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


def init_environment(scorep_config=[], keep_files=False):
    """
    Set the inital needed environmet variables, to get everythin up an running.
    As a few variables interact with LD env vars, the programms needs to be restarted after this.

    @param scorep_config configuration flags for score-p
    @param keep_files whether to keep the generated files, or not.
    """

    if "libscorep" in os.environ.get("LD_PRELOAD", ""):
        raise RuntimeError(
            "Score-P is already loaded. This should not happen at this point")

    subsystem_lib_name, temp_dir = scorep.subsystem.generate(
        scorep_config, keep_files)
    scorep_ld_preload = generate_ld_preload(scorep_config)

    scorep.helper.add_to_ld_library_path(temp_dir)

    preload_str = scorep_ld_preload + " " + subsystem_lib_name
    if "LD_PRELOAD" in os.environ:
        sys.stderr.write(
            "LD_PRELOAD is already specified. If Score-P is already loaded this might lead to errors.")
        preload_str = os.environ["LD_PRELOAD"] + " " + preload_str
        os.environ["SCOREP_LD_PRELOAD_BACKUP"] = os.environ["LD_PRELOAD"]
    else:
        os.environ["SCOREP_LD_PRELOAD_BACKUP"] = ""
    os.environ["LD_PRELOAD"] = preload_str


def reset_preload():
    """
    resets the environment variable `LD_PRELOAD` to the value before init_environment was called.
    """
    if "SCOREP_LD_PRELOAD_BACKUP" in os.environ:
        if os.environ["SCOREP_LD_PRELOAD_BACKUP"] == "":
            del os.environ["LD_PRELOAD"]
        else:
            os.environ["LD_PRELOAD"] = os.environ["SCOREP_LD_PRELOAD_BACKUP"]


def clean_up(keep_files=True):
    """
    deletes the files that are associated to subsystem

    @param keep_files do not delete the generated files. For debugging.
    """
    if keep_files:
        return
    else:
        if os.environ.get("SCOREP_PYTHON_BINDINGS_TEMP_DIR"):
            shutil.rmtree(os.environ["SCOREP_PYTHON_BINDINGS_TEMP_DIR"])
