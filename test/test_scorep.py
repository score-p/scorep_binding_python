#!/usr/bin/env pytest

import os
import pkgutil
import platform
import pytest
import re
import sys
import numpy

import utils
from utils import OTF2_Trace, OTF2_Region, OTF2_Parameter


def version_tuple(v):
    return tuple(map(int, (v.split("."))))


def has_package(name):
    return len(pkgutil.extend_path([], name)) > 0


def requires_package(name):
    return pytest.mark.skipif(not has_package(name), reason="%s is required" % name)


def functions_in_trace(function, otf2_print):
    for event in ("ENTER", "LEAVE"):
        assert re.search(
            '%s[ ]*[0-9 ]*[0-9 ]*Region: "%s"' % (event, function), otf2_print
        )


cinstrumenter_skip_mark = pytest.mark.skipif(
    platform.python_implementation() == "PyPy",
    reason="CInstrumenter only available in CPython and not in PyPy",
)
# All instrumenters (except dummy which isn't a real one)
ALL_INSTRUMENTERS = [
    "profile",
    "trace",
    pytest.param("cProfile", marks=cinstrumenter_skip_mark),
    pytest.param("cTrace", marks=cinstrumenter_skip_mark),
]

foreach_instrumenter = pytest.mark.parametrize("instrumenter", ALL_INSTRUMENTERS)


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


@cinstrumenter_skip_mark
def test_has_c_instrumenter():
    from scorep.instrumenter import has_c_instrumenter

    assert has_c_instrumenter()


@foreach_instrumenter
def test_user_regions(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    std_out, std_err = utils.call_with_scorep(
        "cases/user_regions.py",
        ["--nopython", "--instrumenter-type=" + instrumenter],
        env=scorep_env,
    )

    assert std_err == ""
    assert (
        std_out
        == "hello world\nhello world\nhello world3\nhello world3\nhello world4\n"
    )

    trace = OTF2_Trace(trace_path)
    assert OTF2_Region("user:test_region") in trace
    assert OTF2_Region("user:test_region_2") in trace
    assert len(trace.findall(OTF2_Region("__main__:foo3"))) == 4
    assert OTF2_Region("user:test_region_4") in trace


@foreach_instrumenter
def test_context(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    std_out, std_err = utils.call_with_scorep(
        "cases/context.py",
        ["--noinstrumenter", "--instrumenter-type=" + instrumenter],
        env=scorep_env,
    )

    assert std_err == ""
    assert std_out == "hello world\nhello world\nhello world\n"

    trace = OTF2_Trace(trace_path)
    assert OTF2_Region("user:test_region") in trace
    assert OTF2_Region("__main__:foo") in trace


@foreach_instrumenter
def test_decorator(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    std_out, std_err = utils.call_with_scorep(
        "cases/decorator.py",
        ["--noinstrumenter", "--instrumenter-type=" + instrumenter],
        env=scorep_env,
    )

    assert std_err == ""
    assert std_out == "hello world\nhello world\nhello world\n"

    trace = OTF2_Trace(trace_path)
    assert len(trace.findall(OTF2_Region("__main__:foo"))) == 6


def test_user_regions_no_scorep():
    std_out, std_err = utils.call([sys.executable, "cases/user_regions.py"])

    assert std_err == ""
    assert (
        std_out
        == "hello world\nhello world\nhello world3\nhello world3\nhello world4\n"
    )


@foreach_instrumenter
def test_user_rewind(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    std_out, std_err = utils.call_with_scorep(
        "cases/user_rewind.py", ["--instrumenter-type=" + instrumenter], env=scorep_env
    )

    assert std_err == ""
    assert std_out == "hello world\nhello world\n"

    trace = OTF2_Trace(trace_path)
    assert re.search("MEASUREMENT_ON_OFF[ ]*[0-9 ]*[0-9 ]*Mode: OFF", str(trace))
    assert re.search("MEASUREMENT_ON_OFF[ ]*[0-9 ]*[0-9 ]*Mode: ON", str(trace))


@pytest.mark.parametrize("instrumenter", ALL_INSTRUMENTERS + [None])
def test_instrumentation(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    # Also test when no instrumenter is given
    instrumenter_type = ["--instrumenter-type=" + instrumenter] if instrumenter else []
    std_out, std_err = utils.call_with_scorep(
        "cases/instrumentation.py", ["--nocompiler"] + instrumenter_type, env=scorep_env
    )

    assert std_err == ""
    assert std_out == "hello world\nbaz\nbar\n"

    trace = OTF2_Trace(trace_path)
    assert OTF2_Region("__main__:foo") in trace
    assert OTF2_Region("instrumentation2:bar") in trace
    assert OTF2_Region("instrumentation2:baz") in trace


@foreach_instrumenter
def test_user_instrumentation(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    std_out, std_err = utils.call_with_scorep(
        "cases/user_instrumentation.py",
        ["--nocompiler", "--noinstrumenter", "--instrumenter-type=" + instrumenter],
        env=scorep_env,
    )

    assert std_err == ""
    assert std_out == "hello world\nbar\nhello world2\nbaz\n"

    trace = OTF2_Trace(trace_path)
    assert OTF2_Region("__main__:foo") in trace
    assert OTF2_Region("__main__:foo2") in trace
    assert OTF2_Region("instrumentation2:bar") in trace
    assert OTF2_Region("instrumentation2:baz") in trace


@foreach_instrumenter
def test_external_user_instrumentation(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    std_out, std_err = utils.call_with_scorep(
        "cases/instrumentation.py",
        ["--nocompiler", "--noinstrumenter", "--instrumenter-type=" +
            instrumenter, "--instrumenter-file=cases/external_instrumentation.py"],
        env=scorep_env,
    )

    assert std_err == ""
    assert std_out == "hello world\nbaz\nbar\n"

    trace = OTF2_Trace(trace_path)
    assert OTF2_Region("instrumentation2:bar") in trace
    assert OTF2_Region("instrumentation2:baz") in trace


@foreach_instrumenter
def test_error_region(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    std_out, std_err = utils.call_with_scorep(
        "cases/error_region.py",
        ["--nocompiler", "--noinstrumenter", "--instrumenter-type=" + instrumenter],
        env=scorep_env,
    )

    assert (
        std_err
        == "SCOREP_BINDING_PYTHON ERROR: There was a region exit without an enter!\n"
        + 'SCOREP_BINDING_PYTHON ERROR: For details look for "error_region" in the trace or profile.\n'
    )
    assert std_out == ""

    trace = OTF2_Trace(trace_path)
    assert OTF2_Region("error_region") in trace
    assert OTF2_Parameter("leave-region", "user:test_region") in trace
    assert OTF2_Parameter("leave-region", "user:test_region_2") in trace


@requires_package("mpi4py")
@requires_package("numpy")
@foreach_instrumenter
def test_mpi(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)
    std_out, std_err = utils.call(
        [
            "mpirun",
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
            "--noinstrumenter",
            "--instrumenter-type=" + instrumenter,
            "cases/mpi.py",
        ],
        env=scorep_env,
    )

    assert re.search(r"\[Score-P\] [\w/.: ]*MPI_THREAD_\(SERIALIZED\|MULTIPLE\) ", std_err)
    assert "[00] [0. 1. 2. 3. 4.]\n" in std_out
    assert "[01] [0. 1. 2. 3. 4.]\n" in std_out
    assert "bar\n" in std_out
    assert "baz\n" in std_out

    trace = OTF2_Trace(trace_path)
    assert OTF2_Region("instrumentation2:bar") in trace
    assert OTF2_Region("instrumentation2:baz") in trace


@foreach_instrumenter
def test_call_main(scorep_env, instrumenter):
    std_out, std_err = utils.call_with_scorep(
        "cases/call_main.py",
        ["--nocompiler", "--instrumenter-type=" + instrumenter],
        expected_returncode=1,
        env=scorep_env,
    )

    expected_std_err = r"scorep: Someone called scorep\.__main__\.main"
    expected_std_out = ""
    assert re.search(expected_std_err, std_err)
    assert std_out == expected_std_out


@foreach_instrumenter
def test_classes(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)
    std_out, std_err = utils.call_with_scorep(
        "cases/classes.py",
        ["--nocompiler", "--instrumenter-type=" + instrumenter],
        expected_returncode=0,
        env=scorep_env,
    )

    expected_std_err = ""
    expected_std_out = "foo-2\ndoo\nfoo\nbar\nasdgh\nfoo-2\n"

    assert std_out == expected_std_out
    assert std_err == expected_std_err

    trace = OTF2_Trace(trace_path)

    region_ids = []
    foo_count = 0
    for line in str(trace).split("\n"):
        m = re.search('ENTER[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo" <([0-9]*)>', line)
        if m is not None:
            foo_count += 1
            r_id = m.group(1)

            if foo_count == 1:
                region_ids.append(r_id)
                continue

            if foo_count < 4:
                assert region_ids[-1] < r_id  # check if foo regions are different
            else:
                assert r_id == region_ids[0]  # check if last foo is fist foo
            region_ids.append(r_id)

    assert len(region_ids) == 4


def test_dummy(scorep_env):
    std_out, std_err = utils.call_with_scorep(
        "cases/instrumentation.py", ["--instrumenter-type=dummy"], env=scorep_env
    )

    assert std_err == ""
    assert std_out == "hello world\nbaz\nbar\n"
    assert os.path.exists(
        scorep_env["SCOREP_EXPERIMENT_DIRECTORY"]
    ), "Score-P directory exists for dummy test"


@pytest.mark.skipif(sys.version_info.major < 3, reason="not tested for python 2")
@requires_package("numpy")
@pytest.mark.skipif(version_tuple(numpy.version.version) >= version_tuple("1.22.0"),
                    reason="There are some changes regarding __array_function__ in 1.22.0,"
                    "so the test is no longer needed")
@foreach_instrumenter
def test_numpy_dot(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    std_out, std_err = utils.call_with_scorep(
        "cases/numpy_dot.py",
        ["--nocompiler", "--noinstrumenter", "--instrumenter-type=" + instrumenter],
        env=scorep_env,
    )

    assert std_out == "[[ 7 10]\n [15 22]]\n"
    assert std_err == ""

    trace = OTF2_Trace(trace_path)
    assert OTF2_Region("numpy.__array_function__:dot") in trace


@foreach_instrumenter
def test_threads(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    std_out, std_err = utils.call_with_scorep(
        "cases/use_threads.py",
        ["--nocompiler", "--instrumenter-type=" + instrumenter],
        env=scorep_env,
    )

    assert std_err == "" or "warning: Thread after main " in std_err
    assert "hello world\n" in std_out
    assert "Thread 0 started\n" in std_out
    assert "Thread 1 started\n" in std_out
    assert "bar\n" in std_out
    assert "baz\n" in std_out

    trace = OTF2_Trace(trace_path)
    assert OTF2_Region("__main__:foo") in trace
    assert OTF2_Region("instrumentation2:bar") in trace
    assert OTF2_Region("instrumentation2:baz") in trace


@pytest.mark.skipif(sys.version_info.major < 3, reason="not tested for python 2")
@foreach_instrumenter
def test_io(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    print("start")
    std_out, std_err = utils.call_with_scorep(
        "cases/file_io.py",
        [
            "--nocompiler",
            "--instrumenter-type=" + instrumenter,
            "--noinstrumenter",
            "--io=runtime:posix",
        ],
        env=scorep_env,
    )

    assert std_err == ""
    assert "test\n" in std_out

    trace = utils.OTF2_Trace(trace_path)

    file_regex = "\\[POSIX I\\/O\\][ \\w:/]*test\\.txt"
    # print_regex = "STDOUT_FILENO"

    ops = {
        "open": {"ENTER": "open64", "IO_CREATE_HANDLE": file_regex, "LEAVE": "open64"},
        "seek": {"ENTER": "lseek64", "IO_SEEK": file_regex, "LEAVE": "lseek64"},
        "write": {
            "ENTER": "write",
            "IO_OPERATION_BEGIN": file_regex,
            "IO_OPERATION_COMPLETE": file_regex,
            "LEAVE": "write",
        },
        "read": {
            "ENTER": "read",
            "IO_OPERATION_BEGIN": file_regex,
            "IO_OPERATION_COMPLETE": file_regex,
            "LEAVE": "read",
        },
        # for some reason there is no print in pytest
        # "print": {
        #     "ENTER": "read",
        #     "IO_OPERATION_BEGIN": print_regex,
        #     "IO_OPERATION_COMPLETE": print_regex,
        #     "LEAVE": "read",
        # },
        "close": {"ENTER": "close", "IO_DESTROY_HANDLE": file_regex, "LEAVE": "close"},
    }

    io_trace = ""
    io_trace_after = ""
    in_expected_io = False
    after_expected_io = False

    for line in str(trace).split("\n"):
        if ("user_instrumenter:expect io" in line) and (in_expected_io is False):
            in_expected_io = True
        elif ("user_instrumenter:expect io" in line) and (in_expected_io is True):
            in_expected_io = False
            after_expected_io = True
        if in_expected_io:
            io_trace += line + "\n"
        if after_expected_io:
            io_trace_after += line + "\n"

    for _, details in ops.items():
        for event, data in details.items():
            regex_str = '{event:}[ ]*[0-9 ]*[0-9 ]*(Region|Handle): "{data:}"'.format(
                event=event, data=data
            )
            print(regex_str)
            assert re.search(regex_str, io_trace)


@foreach_instrumenter
def test_force_finalize(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)

    # Also test when no instrumenter is given
    instrumenter_type = ["--instrumenter-type=" + instrumenter]
    std_out, std_err = utils.call_with_scorep(
        "cases/force_finalize.py", instrumenter_type, env=scorep_env
    )

    assert std_err == ""
    assert std_out == "foo\nbar\n"

    trace = OTF2_Trace(trace_path)
    assert OTF2_Region("__main__:foo") in trace
    assert OTF2_Region("__main__:bar") not in trace
