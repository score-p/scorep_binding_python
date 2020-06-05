#!/usr/bin/env pytest

import os
import pkgutil
import re
import subprocess
import sys
import pytest


def call(arguments, env=None):
    """
    return a triple with (returncode, stdout, stderr) from the call to subprocess
    """
    result = ()
    if sys.version_info > (3, 5):
        out = subprocess.run(
            arguments,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        result = (out.returncode, out.stdout.decode("utf-8"), out.stderr.decode("utf-8"))
    else:
        p = subprocess.Popen(
            arguments,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        p.wait()
        result = (p.returncode, stdout.decode("utf-8"), stderr.decode("utf-8"))
    return result


def call_with_scorep(file, scorep_arguments=None, env=None):
    """
    Shortcut for running a python file with the scorep module

    @return triple (returncode, stdout, stderr) from the call to subprocess
    """
    arguments = [sys.executable, "-m", "scorep"]
    if scorep_arguments:
        arguments.extend(scorep_arguments)
    return call(arguments + [file], env=env)


def has_package(name):
    return len(pkgutil.extend_path([], name)) > 0


def requires_package(name):
    return pytest.mark.skipif(not has_package(name), reason='%s is required' % name)


requires_python3 = pytest.mark.skipif(sys.version_info.major < 3, reason="not tested for python 2")


@pytest.fixture
def scorep_env(tmp_path):
    env = os.environ.copy()
    env["SCOREP_ENABLE_PROFILING"] = "false"
    env["SCOREP_ENABLE_TRACING"] = "true"
    env["SCOREP_PROFILING_MAX_CALLPATH_DEPTH"] = "98"
    env["SCOREP_TOTAL_MEMORY"] = "3G"
    env["SCOREP_EXPERIMENT_DIRECTORY"] = str(tmp_path / "test_bindings_dir")
    return env


def get_trace_path(env):
    """Return the path to the otf2 trace file given an environment dict"""
    return env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"


def test_has_version():
    import scorep
    assert scorep.__version__ is not None


def test_user_regions(scorep_env):
    trace_path = get_trace_path(scorep_env)

    out = call_with_scorep("cases/user_regions.py",
                           ["--nopython"],
                           env=scorep_env)
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert std_out == "hello world\nhello world\nhello world3\nhello world4\n"

    out = call(["otf2-print", trace_path])
    std_out = out[1]
    std_err = out[2]

    assert re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region"', std_out)
    assert re.search('LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region"', std_out)
    assert re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region_2"', std_out)
    assert re.search('LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region_2"', std_out)
    assert re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo3"', std_out)
    assert re.search('LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo3"', std_out)
    assert re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region_4"', std_out)
    assert re.search('LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region_4"', std_out)


def test_context(scorep_env):
    trace_path = get_trace_path(scorep_env)

    out = call_with_scorep("cases/context.py",
                           ["--noinstrumenter"],
                           env=scorep_env)
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert std_out == "hello world\nhello world\nhello world\n"

    out = call(["otf2-print", trace_path])
    std_out = out[1]
    std_err = out[2]

    assert re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region"', std_out)
    assert re.search('LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region"', std_out)
    assert re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"', std_out)
    assert re.search('LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"', std_out)


def test_user_regions_no_scorep(scorep_env):
    out = call([sys.executable,
                "cases/user_regions.py"],
               env=scorep_env)
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert std_out == "hello world\nhello world\nhello world3\nhello world4\n"


def test_user_rewind(scorep_env):
    trace_path = get_trace_path(scorep_env)

    out = call_with_scorep("cases/user_rewind.py", env=scorep_env)
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert std_out == "hello world\nhello world\n"

    out = call(["otf2-print", trace_path])
    std_out = out[1]
    std_err = out[2]

    assert re.search('MEASUREMENT_ON_OFF[ ]*[0-9 ]*[0-9 ]*Mode: OFF', std_out)
    assert re.search('MEASUREMENT_ON_OFF[ ]*[0-9 ]*[0-9 ]*Mode: ON', std_out)


def test_oa_regions(scorep_env):
    trace_path = get_trace_path(scorep_env)

    out = call_with_scorep("cases/oa_regions.py",
                           ["--nopython"],
                           env=scorep_env)
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert std_out == "hello world\n"

    out = call(["otf2-print", trace_path])
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "test_region"', std_out)
    assert re.search('LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "test_region"', std_out)


def test_instrumentation(scorep_env):
    trace_path = get_trace_path(scorep_env)

    out = call_with_scorep("cases/instrumentation.py",
                           ["--nocompiler"],
                           env=scorep_env)
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert std_out == "hello world\nbaz\nbar\n"

    out = call(["otf2-print", trace_path])
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"', std_out)
    assert re.search('LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"', std_out)


def test_user_instrumentation(scorep_env):
    trace_path = get_trace_path(scorep_env)

    out = call_with_scorep("cases/user_instrumentation.py",
                           ["--nocompiler", "--noinstrumenter"],
                           env=scorep_env)
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert std_out == "hello world\nbaz\nbar\n"

    out = call(["otf2-print", trace_path])
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"', std_out)
    assert re.search('LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"', std_out)


def test_error_region(scorep_env):
    trace_path = get_trace_path(scorep_env)

    out = call_with_scorep("cases/error_region.py",
                           ["--nocompiler", "--noinstrumenter"],
                           env=scorep_env)
    std_out = out[1]
    std_err = out[2]

    assert std_err == \
        'SCOREP_BINDING_PYTHON ERROR: There was a region exit without an enter!\n' + \
        'SCOREP_BINDING_PYTHON ERROR: For details look for "error_region" in the trace or profile.\n'
    assert std_out == ""

    out = call(["otf2-print", trace_path])
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "error_region"', std_out)
    assert re.search('LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "error_region"', std_out)
    assert re.search('PARAMETER_STRING[ ]*[0-9 ]*[0-9 ]*Parameter: "leave-region" <[0-9]*>,' +
                     ' Value: "user:test_region"', std_out)
    assert re.search('PARAMETER_STRING[ ]*[0-9 ]*[0-9 ]*Parameter: "leave-region" <[0-9]*>,' +
                     ' Value: "user:test_region_2"', std_out)


@requires_package('mpi4py')
@requires_package('numpy')
def test_mpi(scorep_env):
    out = call(["mpirun",
                "-n",
                "2",
                "-mca",
                "btl",
                "^openib",
                sys.executable,
                "-m",
                "scorep",
                "--mpp=mpi",
                "--nocompiler",
                "cases/mpi.py"],
               env=scorep_env)

    std_out = out[1]
    std_err = out[2]

    expected_std_out = r"\[0[0-9]\] \[0. 1. 2. 3. 4.\]\n\[0[0-9]] \[0. 1. 2. 3. 4.\]\n"

    assert re.search(r'\[Score-P\] [\w/.: ]*MPI_THREAD_FUNNELED', std_err)
    assert re.search(expected_std_out, std_out)


def test_call_main(scorep_env):
    out = call_with_scorep("cases/call_main.py",
                           ["--nocompiler"],
                           env=scorep_env)
    std_out = out[1]
    std_err = out[2]

    expected_std_err = r"scorep: Someone called scorep\.__main__\.main"
    expected_std_out = ""
    assert re.search(expected_std_err, std_err)
    assert std_out == expected_std_out


def test_dummy(scorep_env):
    out = call_with_scorep("cases/instrumentation.py",
                           ["--instrumenter-type=dummy"],
                           env=scorep_env)
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert std_out == "hello world\nbaz\nbar\n"
    assert os.path.exists(scorep_env["SCOREP_EXPERIMENT_DIRECTORY"]), "Score-P directory exists for dummy test"


@requires_python3
def test_numpy_dot(scorep_env):
    trace_path = get_trace_path(scorep_env)

    out = call_with_scorep("cases/numpy_dot.py",
                           ["--nocompiler", "--noinstrumenter"],
                           env=scorep_env)
    std_out = out[1]
    std_err = out[2]

    assert std_out == "[[ 7 10]\n [15 22]]\n"
    assert std_err == ""

    out = call(["otf2-print", trace_path])
    std_out = out[1]
    std_err = out[2]

    assert std_err == ""
    assert re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "numpy.__array_function__:dot"', std_out)
    assert re.search('LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "numpy.__array_function__:dot"', std_out)
