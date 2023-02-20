import subprocess
import sys
import os
import re


def print_err(*args):
    """Print to stderr"""
    sys.stderr.write(' '.join(map(str, args)) + '\n')


def call(arguments):
    """
    return a triple with (returncode, stdout, stderr) from the call to subprocess
    """
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


def get_python_version():
    version = "{}.{}".format(
        sys.version_info.major,
        sys.version_info.minor)
    return version


def get_scorep_version():
    (return_code, std_out, std_err) = call(["scorep", "--version"])
    if (return_code != 0):
        raise RuntimeError("Cannot call Score-P, reason {}".format(std_err))
    me = re.search("([0-9.]+)", std_out)
    version_str = me.group(1)
    try:
        version = float(version_str)
    except TypeError:
        raise RuntimeError(
            "Can not decode the Score-P Version. The version string is: \"{}\"".format(std_out))
    return version


def get_scorep_config(config_line=None):
    (return_code, std_out, std_err) = call(["scorep-info", "config-summary"])
    if (return_code != 0):
        raise RuntimeError("Cannot call Score-P, reason {}".format(std_err))
    if config_line is None:
        return std_out.split("\n")
    else:
        for line in std_out.split("\n"):
            if config_line in line:
                return line
    return None


def add_to_ld_library_path(path):
    """
    adds the path to the LD_LIBRARY_PATH.
    @param path path to be added
    """
    library_path = os.environ.get("LD_LIBRARY_PATH", "")
    library_paths = library_path.split(":") if library_path else []
    if path not in library_paths:
        os.environ["LD_LIBRARY_PATH"] = ':'.join([path] + library_paths)


def generate_compile_deps(config):
    """
    Generates the data needed for compilation.
    """

    scorep_config = ["scorep-config"] + config

    (return_code, stdout, stderr) = call(scorep_config)
    if return_code != 0:
        raise ValueError(
            "given config {} is not supported\nstdout: {}\nstrerr: {}".format(config, stdout, stderr))

    (_, ldflags, _) = call(scorep_config + ["--ldflags"])
    (_, libs, _) = call(scorep_config + ["--libs"])
    (_, mgmt_libs, _) = call(scorep_config + ["--mgmt-libs"])
    (_, cflags, _) = call(scorep_config + ["--cflags"])

    libs = " " + libs + " " + mgmt_libs
    ldflags = " " + ldflags
    cflags = " " + cflags

    lib_dir = re.findall(r" -L[/+-@.\w]*", ldflags)
    lib = re.findall(r" -l[/+-@.\w]*", libs)
    include = re.findall(r" -I[/+-@.\w]*", cflags)
    macro = re.findall(r" -D[/+-@.\w]*", cflags)
    linker_flags = re.findall(r" -Wl[/+-@.\w]*", ldflags)

    def remove_flag3(x): return x[3:]

    def remove_space1(x): return x[1:]

    lib_dir = list(map(remove_flag3, lib_dir))
    lib = list(map(remove_space1, lib))
    include = list(map(remove_flag3, include))
    macro = list(map(remove_flag3, macro))
    linker_flags = list(map(remove_space1, linker_flags))

    macro = list(map(lambda x: tuple([x, 1]), macro))

    return (include, lib, lib_dir, macro, linker_flags)
