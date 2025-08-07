#!/usr/bin/env pytest

import os
import pkgutil
import platform
import pytest
import re
import sys
import numpy

import otf2
from otf2.enums import MeasurementMode
from otf2.events import (
    Enter,
    IoCreateHandle,
    IoDestroyHandle,
    IoOperationBegin,
    IoOperationComplete,
    IoSeek,
    Leave,
    ParameterString,
)

import utils


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

    region_names = utils.get_region_names(trace_path)
    assert "user:test_region" in region_names
    assert "user:test_region_2" in region_names
    assert len(utils.findall_regions(trace_path, "__main__:foo3")) == 4
    assert "user:test_region_4" in region_names


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

    region_names = utils.get_region_names(trace_path)
    assert "user:test_region" in region_names
    assert "__main__:foo" in region_names


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

    assert len(utils.findall_regions(trace_path, "__main__:foo")) == 6


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

    measurement_on = False
    measurement_off = False
    with otf2.reader.open(trace_path) as trace:
        for _, event in trace.events:
            if isinstance(event, otf2.events.MeasurementOnOff):
                if event.measurement_mode == MeasurementMode.ON:
                    measurement_on = True
                elif event.measurement_mode == MeasurementMode.OFF:
                    measurement_off = True

    assert measurement_on
    assert measurement_off


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

    region_names = utils.get_region_names(trace_path)
    assert "__main__:foo" in region_names
    assert "instrumentation2:bar" in region_names
    assert "instrumentation2:baz" in region_names


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

    region_names = utils.get_region_names(trace_path)
    assert "__main__:foo" in region_names
    assert "__main__:foo2" in region_names
    assert "instrumentation2:bar" in region_names
    assert "instrumentation2:baz" in region_names


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

    region_names = utils.get_region_names(trace_path)
    assert "__main__:foo" not in region_names
    assert "instrumentation2:bar" in region_names
    assert "instrumentation2:baz" in region_names


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

    region_names = utils.get_region_names(trace_path)
    with otf2.reader.open(trace_path) as trace:
        parameters = [event for _, event in trace.events if isinstance(event, ParameterString)]
        assert "error_region" in region_names
        assert any(
            param for param in parameters
            if param.parameter.name == "leave-region"
            and param.string == "user:test_region"
        )
        assert any(
            param for param in parameters
            if param.parameter.name == "leave-region"
            and param.string == "user:test_region_2"
        )


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

    region_names = utils.get_region_names(trace_path)
    assert "instrumentation2:bar" in region_names
    assert "instrumentation2:baz" in region_names


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

    region_names = utils.get_region_names(trace_path)
    assert "__main__:foo" in region_names
    assert "__main__.TestClass:foo" in region_names
    assert "__main__.TestClass2:foo" in region_names


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

    region_names = utils.get_region_names(trace_path)
    assert "numpy.__array_function__:dot" in region_names


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

    region_names = utils.get_region_names(trace_path)
    assert "__main__:foo" in region_names
    assert "instrumentation2:bar" in region_names
    assert "instrumentation2:baz" in region_names


@pytest.mark.skipif(sys.version_info.major < 3, reason="not tested for python 2")
@foreach_instrumenter
def test_io(scorep_env, instrumenter):
    trace_path = get_trace_path(scorep_env)
    scorep_env["SCOREP_IO_POSIX"] = "true"

    std_out, std_err = utils.call_with_scorep(
        "cases/file_io.py",
        [
            "--nocompiler",
            "--instrumenter-type=" + instrumenter,
            "--noinstrumenter",
        ],
        env=scorep_env,
    )

    assert std_err == ""
    assert "test\n" in std_out

    file_regex = "[\\w:/]*test\\.txt"
    # print_regex = "STDOUT_FILENO"

    ops = {
        # CPython calls "int open64( const char*, int, ... )" but PyPy calls "int open( const char*, int, ... )"
        "open": {Enter: "open(64)?", IoCreateHandle: file_regex, Leave: "open(64)?"},
        "seek": {Enter: "lseek(64)?", IoSeek: file_regex, Leave: "lseek(64)?"},
        "write": {
            Enter: "write",
            IoOperationBegin: file_regex,
            IoOperationComplete: file_regex,
            Leave: "write",
        },
        "read": {
            Enter: "read",
            IoOperationBegin: file_regex,
            IoOperationComplete: file_regex,
            Leave: "read",
        },
        # for some reason there is no print in pytest
        # "print": {
        #     "ENTER": "read",
        #     "IO_OPERATION_BEGIN": print_regex,
        #     "IO_OPERATION_COMPLETE": print_regex,
        #     "LEAVE": "read",
        # },
        "close": {Enter: "close", IoDestroyHandle: file_regex, Leave: "close"},
    }

    io_trace = []
    io_trace_after = []
    in_expected_io = False
    after_expected_io = False

    with otf2.reader.open(trace_path) as trace:
        for _, event in trace.events:
            if isinstance(event, (Enter, Leave)) and event.region.name == "user_instrumenter:expect io":
                if not in_expected_io:
                    in_expected_io = True
                    continue
                else:
                    in_expected_io = False
                    after_expected_io = True
                    continue

            if in_expected_io:
                io_trace.append(event)
            elif after_expected_io:
                io_trace_after.append(event)

    for _, events in ops.items():
        for event_type, pattern in events.items():
            if issubclass(event_type, (Enter, Leave)):
                assert any(
                    isinstance(e, event_type) and re.search(pattern, e.region.canonical_name)
                    for e in io_trace
                )

            elif issubclass(event_type, (
                    IoCreateHandle, IoSeek, IoOperationBegin, IoOperationComplete, IoDestroyHandle)):
                assert any(
                    isinstance(e, event_type) and re.search(pattern, e.handle.file.name)
                    for e in io_trace
                )


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

    region_names = utils.get_region_names(trace_path)
    assert "__main__:foo" in region_names
    assert "__main__:bar" not in region_names
