import subprocess
import sys
import os

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

def find_lib(lib_name, additional_lookup_path = []):
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
            target_path  = lookup_lib(lib_name, path, True)
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
    return version;

def gen_mpi_lib_name():
    mpi_lib_name = "libscorep_init_mpi-{}.so".format(get_version())
    return mpi_lib_name

def gen_mpi_link_name():
    mpi_link_name = "scorep_init_mpi-{}".format(get_version())
    return mpi_link_name

def add_to_ld_library_path(path):
    """
    adds the path to the LD_LIBRARY_PATH.
    @param path path to be added
    """
    if ("LD_LIBRARY_PATH" not in os.environ) or (path not in os.environ["LD_LIBRARY_PATH"]):
        if os.environ["LD_LIBRARY_PATH"] == "":
            os.environ["LD_LIBRARY_PATH"] = path
        else:
            os.environ["LD_LIBRARY_PATH"] = path + ":" + os.environ["LD_LIBRARY_PATH"]

def generate_ld_preload():
    """
    This functions generate a string that needs to be passed to $LD_PRELOAD and the path to the scorep subsystem.
    This is needed it MPI tracing is requested.
    After this sting is passed, the tracing needs to be restarted with this $LD_PRELOAD in env.

    @return ld_preload, scorep_subsystem_path
        ld_preload ... string which needs to be passed to LD_PRELOAD
        scorep_subsystem_path ... path to the scorep subsystem (e.g. libscorep_init_mpi)
    """
    # find the libscorep_init_mpi.so
    mpi_lib_name = gen_mpi_lib_name()

    scorep_subsystem_path = find_lib(mpi_lib_name, [os.path.realpath(__file__)])
    if scorep_subsystem_path is None:
        sys.stderr.write("cannot find {}.\n".format(mpi_lib_name))
        return "", "" 
        
    (_, preload, _) = call(["scorep-config", "--preload-libs"])
    preload += " " + scorep_subsystem_path
    return preload, scorep_subsystem_path
