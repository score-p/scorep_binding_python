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

def get_python_version():
    version = "{}.{}".format(
        sys.version_info.major,
        sys.version_info.minor)
    return version


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
