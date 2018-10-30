import subprocess
import sys
import os
import re


def call(arguments):
    """
    return a triple with (returncode, stdout, stderr) from the call to subprocess
    """
    result = ()
    if sys.version_info > (3, 5):
        out = subprocess.run(
            arguments,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        result = (
            out.returncode,
            out.stdout.decode("utf-8"),
            out.stderr.decode("utf-8"))
    else:
        p = subprocess.Popen(
            arguments,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        p.wait()
        result = (p.returncode, stdout.decode("utf-8"), stderr.decode("utf-8"))
    return result


def lookup_lib(lib, lookup_path, recursive):
    """
    searches for the given lib along the given path.
    @param lib name of the lib including the leading lib and final .so
    @param lookup_path path to start the lookup
    @param recursive if ture search along the given path, if false search just in the given path
    @return path to the lib or None if not found
    """

    if os.path.isfile(lookup_path + "/" + lib):
        return lookup_path + "/" + lib
    else:
        if recursive:
            if lookup_path != "/" and lookup_path != "":
                lookup_path, _ = os.path.split(lookup_path)
                return lookup_lib(lib, lookup_path, recursive)
    return None


def find_lib(lib_name, additional_lookup_path=[]):
    """
    Tries to find the path the the given list.
    Searches additional_lookup_path, sys.path, LD_LIBRARY_PATH, and PYTHONPATH.

    @param lib_name full name of the list
    @param additional_lookup_path list of additional paths to look up
    @return path to the given library
    """
    target_path = None
    if target_path is None:
        for path in additional_lookup_path:
            target_path = lookup_lib(lib_name, path, True)
            if target_path is not None:
                break

    if target_path is None:
        for path in sys.path:
            target_path = lookup_lib(lib_name, path, True)
            if target_path is not None:
                break

    # look in ld library path
    if target_path is None:
        if "LD_LIBRARY_PATH" in os.environ:
            ld_library_paths = os.environ['LD_LIBRARY_PATH'].split(":")
            for path in ld_library_paths:
                target_path = lookup_lib(lib_name, path, True)
                if target_path is not None:
                    break

    # look in python path
    if target_path is None:
        if 'PYTHONPATH' in os.environ:
            python_path = os.environ['PYTHONPATH'].split(":")
            for path in python_path:
                target_path = lookup_lib(lib_name, path, True)
                if target_path is not None:
                    break

    return target_path


def get_version():
    version = "{}.{}".format(
        sys.version_info.major,
        sys.version_info.minor)
    return version


def gen_subsystem_lib_name():
    mpi_lib_name = "libscorep_init_subsystem-{}.so".format(get_version())
    return mpi_lib_name


def gen_subsystem_link_name():
    mpi_link_name = "scorep_init_subsystem-{}".format(get_version())
    return mpi_link_name


def add_to_ld_library_path(path):
    """
    adds the path to the LD_LIBRARY_PATH.
    @param path path to be added
    """
    if ("LD_LIBRARY_PATH" not in os.environ) or (
            path not in os.environ["LD_LIBRARY_PATH"]):
        if os.environ["LD_LIBRARY_PATH"] == "":
            os.environ["LD_LIBRARY_PATH"] = path
        else:
            os.environ["LD_LIBRARY_PATH"] = path + \
                ":" + os.environ["LD_LIBRARY_PATH"]


def generate_ld_preload(scorep_config):
    """
    This functions generate a string that needs to be passed to $LD_PRELOAD.
    After this sting is passed, the tracing needs to be restarted with this $LD_PRELOAD in env.
    
    @return ld_preload string which needs to be passed to LD_PRELOAD
    """
    
    (_, preload, _) = call(["scorep-config"] + scorep_config + ["--user", "--preload-libs"])
    return preload

def generate_compile_deps(config = []):
    """
    Generates the data needed for compilation.
    """
    
    scorep_config = ["scorep-config"] + config + ["--user"]
    
    (retrun_code, _, _) = call(scorep_config)
    if retrun_code != 0:
        raise ValueError(
            "given config {} is not supported".format(config))

    (_, ldflags, _) = call(scorep_config + ["--ldflags"])
    (_, libs, _) = call(scorep_config + ["--libs"])
    (_, mgmt_libs, _) = call(scorep_config + ["--mgmt-libs"])
    (_, cflags, _) = call(scorep_config + ["--cflags"])

    libs = " " + libs + " " + mgmt_libs
    ldflags = " " + ldflags
    cflags = " " + cflags

    lib_dir = re.findall(" -L[/+-@.\w]*", ldflags)
    lib = re.findall(" -l[/+-@.\w]*", libs)
    include = re.findall(" -I[/+-@.\w]*", cflags)
    macro = re.findall(" -D[/+-@.\w]*", cflags)
    linker_flags = re.findall(" -Wl[/+-@.\w]*", ldflags)

    def remove_flag3(x): return x[3:]
    def remove_space1(x): return x[1:]

    lib_dir = list(map(remove_flag3, lib_dir))
    lib = list(map(remove_space1, lib))
    include = list(map(remove_flag3, include))
    macro = list(map(remove_flag3, macro))
    linker_flags = list(map(remove_space1, linker_flags))

    macro = list(map(lambda x: tuple([x, 1]), macro))

    return (include, lib, lib_dir, macro, linker_flags)

def generate_compile_init(config = []):
    """
    Generates the data needed to be preloaded.
    """
    
    scorep_config = ["scorep-config"] + config + ["--user"]
    
    (retrun_code, _, _) = call(scorep_config)
    if retrun_code != 0:
        raise ValueError(
            "given config {} is not supported".format(scorep_config))
    (_, scorep_adapter_init, _) = call(scorep_config + ["--adapter-init"])
    
    return scorep_adapter_init
        
def generate_compile_deps_mpi():
    (_, mpi_version, mpi_version2) = scorep.helper.call(
        ["mpiexec", "--version"])
    mpi_version = mpi_version + mpi_version2
    if "OpenRTE" in mpi_version:
        print("OpenMPI detected")
        (_, ldflags, _) = scorep.helper.call(["mpicc", "-showme:link"])
        (_, compile_flags, _) = scorep.helper.call(
            ["mpicc", "-showme:compile"])
    elif ("Intel" in mpi_version) or ("MPICH" in mpi_version):
        print("Intel or MPICH detected")
        (_, ldflags, _) = scorep.helper.call(["mpicc", "-link_info"])
        (_, compile_flags, _) = scorep.helper.call(["mpicc", "-compile_info"])
    else:
        print("cannot determine mpi version: \"{}\"".format(mpi_version))
        exit(-1)

    ldflags = " " + ldflags
    compile_flags = " " + compile_flags

    lib_dir = re.findall(" -L[/+-@.\w]*", ldflags)
    lib = re.findall(" -l[/+-@.\w]*", ldflags)
    include = re.findall(" -I[/+-@.\w]*", compile_flags)
    macro = re.findall(" -D[/+-@.\w]*", compile_flags)
    linker_flags = re.findall(" -Wl[/+-@.\w]*", ldflags)
    linker_flags_2 = re.findall(" -Xlinker [/+-@.\w]*", ldflags)

    def remove_flag3(x): return x[3:]

    def remove_x_linker(x): return x[10:]

    def remove_space1(x): return x[1:]

    lib_dir = list(map(remove_flag3, lib_dir))
    lib = list(map(remove_space1, lib))
    include = list(map(remove_flag3, include))
    macro = list(map(remove_flag3, macro))
    linker_flags = list(map(remove_space1, linker_flags))
    linker_flags_2 = list(map(remove_x_linker, linker_flags_2))

    macro = list(map(lambda x: tuple([x, 1]), macro))

    linker_flags.extend(linker_flags_2)

    return (include, lib, lib_dir, macro, linker_flags)

