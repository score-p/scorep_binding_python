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

def find_lib(lib, lookup_path, recursive):
    """
    searches for the given lib along the given path.
    @param lib name of the lib including the leading lib and final .so
    @param lookup_path path to start the lookup
    @param recursive if ture search along the given path, if false search just in the given path
    @return path to the lib or None if not found
    """
    lib_path = ""

    if os.path.isfile(lookup_path + "/" + lib):
        return lookup_path + "/" + lib
    else:
        if recursive:
            if lookup_path != "/":
                lookup_path, tail = os.path.split(lookup_path)
                return find_lib(lib, lookup_path, recursive)
    return None

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

    scorep_subsystem_path = find_lib(
        mpi_lib_name, os.path.realpath(__file__), True)

    # look in ld library path
    if scorep_subsystem_path is None:
        ld_library_paths = os.environ['LD_LIBRARY_PATH'].split(":")
        for path in ld_library_paths:
            scorep_subsystem_path = find_lib(mpi_lib_name, path, False)
            if scorep_subsystem_path is not None:
                break

    # look in python path
    if scorep_subsystem_path is None:
        python_path = os.environ['PYTHONPATH'].split(":")
        for path in python_path:
            scorep_subsystem_path = find_lib(mpi_lib_name, path, False)
            if scorep_subsystem_path is not None:
                break

    # give up
    if scorep_subsystem_path is None:
        sys.stderr.write("cannot find {}.\n".format(mpi_lib_name))
        return "", "" 
        
    (_, preload, _) = call(["scorep-config", "--preload-libs"])
    preload += " " + scorep_subsystem_path
    return preload, scorep_subsystem_path
