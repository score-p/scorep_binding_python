#!/usr/bin/env python3

# Copyright 2017, Technische Universitaet Dresden, Germany, all rights reserved.
# Author: Andreas Gocht
#
# portions copyright 2001, Autonomous Zones Industries, Inc., all rights...
# err...  reserved and offered to the public under the terms of the
# Python 2.2 license.
# Author: Zooko O'Whielacronx
# http://zooko.com/
# mailto:zooko@zooko.com
#
# Copyright 2000, Mojam Media, Inc., all rights reserved.
# Author: Skip Montanaro
#
# Copyright 1999, Bioreason, Inc., all rights reserved.
# Author: Andrew Dalke
#
# Copyright 1995-1997, Automatrix, Inc., all rights reserved.
# Author: Skip Montanaro
#
# Copyright 1991-1995, Stichting Mathematisch Centrum, all rights reserved.
#
#
# Permission to use, copy, modify, and distribute this Python software and
# its associated documentation for any purpose without fee is hereby
# granted, provided that the above copyright notice appears in all copies,
# and that both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of neither Automatrix,
# Bioreason, Mojam Media or TU Dresden be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#

__all__ = ['Trace']
import linecache
import os
import re
import sys
import token
import tokenize
import inspect
import gc
import dis
import pickle
import atexit
import subprocess
from warnings import warn as _warn

try:
    import threading
except ImportError:
    _settrace = sys.settrace

    def _unsettrace():
        sys.settrace(None)
else:
    def _settrace(func):
        threading.settrace(func)
        sys.settrace(func)

    def _unsettrace():
        sys.settrace(None)
        threading.settrace(None)


def _usage(outfile):
    outfile.write("""TODO
""" % sys.argv[0])


global_trace = None

cuda_support = None
opencl_support = None

"""
return a triple with (returncode, stdout, stderr) from the call to subprocess
"""


def call(arguments):
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


class Trace:
    def __init__(self, _scorep, trace=1):
        """
        @param trace true if there shall be any tracing at all
        """
        self.pathtobasename = {}  # for memoizing os.path.basename
        self.donothing = 0
        self.trace = trace
        self._scorep = _scorep
        if trace:
            self.globaltrace = self.globaltrace_lt
            self.localtrace = self.localtrace_trace
        else:
            # Ahem -- do nothing?  Okay.
            self.donothing = 1

    def register(self):
        if not self.donothing:
            _settrace(self.globaltrace)
            atexit.register(self.flush_scorep_groups)

    def run(self, cmd):
        import __main__
        dict = __main__.__dict__
        self.runctx(cmd, dict, dict)

    def runctx(self, cmd, globals=None, locals=None):
        if globals is None:
            globals = {}
        if locals is None:
            locals = {}
        if not self.donothing:
            _settrace(self.globaltrace)
        try:
            exec(cmd, globals, locals)
        finally:
            if not self.donothing:
                _unsettrace()

    def runfunc(self, func, *args, **kw):
        result = None
        if not self.donothing:
            sys.settrace(self.globaltrace)
        try:
            result = func(*args, **kw)
        finally:
            if not self.donothing:
                sys.settrace(None)
        return result

    def globaltrace_lt(self, frame, why, arg):
        """Handler for call events.

        If the code block being entered is to be ignored, returns `None',
        else returns self.localtrace.
        """
        if why == 'call':
            code = frame.f_code
            modulename = frame.f_globals.get('__name__', None)
            file_name = frame.f_globals.get('__file__', None)
            if file_name is not None:
                full_file_name = os.path.abspath(file_name)
            else:
                full_file_name = "None"
            line_number = frame.f_lineno
            if self.trace and code.co_name is not "_unsettrace":
                self._scorep.region_begin(
                    "%s:%s" %
                    (modulename, code.co_name), full_file_name, line_number)
            return self.localtrace
        else:
            return None

    def localtrace_trace(self, frame, why, arg):
        if why == "return":
            code = frame.f_code
            modulename = frame.f_globals.get('__name__', None)
            if self.trace:
                self._scorep.region_end("%s:%s" % (modulename, code.co_name))
        return self.localtrace

    def flush_scorep_groups(self):
        modules = sys.modules.keys()
        with open(self._scorep.get_expiriment_dir_name() + "/scorep.fgp", "w") as f:
            f.write("""
BEGIN OPTIONS
        MATCHING_STRATEGY=FIRST
        CASE_SENSITIVITY_FUNCTION_NAME=NO
        CASE_SENSITIVITY_MANGLED_NAME=NO
        CASE_SENSITIVITY_SOURCE_FILE_NAME=NO
END OPTIONS\n""")
            for module in sorted(modules, reverse=True):
                f.write("BEGIN FUNCTION_GROUP {}\n".format(module))
                f.write("\tNAME={}*\n".format(module))
                f.write("END FUNCTION_GROUP\n")

    def user_region_begin(self, name, file_name=None, line_number=None):
        """
        Begin of an User region. If file_name or line_number is None, both will
        bet determined automatically
        @param name name of the user region
        @param file_name file name of the user region
        @param line_number line number of the user region
        """
        if file_name is None or line_number is None:
            frame = inspect.currentframe().f_back
            file_name = frame.f_globals.get('__file__', None)
            line_number = frame.f_lineno
        if file_name is not None:
            full_file_name = os.path.abspath(file_name)
        else:
            full_file_name = "None"

        self._scorep.region_begin(name, full_file_name, line_number)

    def user_region_end(self, name):
        self._scorep.region_end(name)

    def oa_region_begin(self, name, file_name=None, line_number=None):
        """
        Begin of an Online Access region. If file_name or line_number is None, both will
        bet determined automatically
        @param name name of the user region
        @param file_name file name of the user region
        @param line_number line number of the user region
        """
        if file_name is None or line_number is None:
            frame = inspect.currentframe().f_back
            file_name = frame.f_globals.get('__file__', None)
            line_number = frame.f_lineno
        if file_name is not None:
            full_file_name = os.path.abspath(file_name)
        else:
            full_file_name = "None"

        self._scorep.oa_region_begin(name, full_file_name, line_number)

    def oa_region_end(self, name):
        self._scorep.oa_region_end(name)

    def user_enable_recording(self):
        self._scorep.enable_recording()

    def user_disable_recording(self):
        self._scorep.disable_recording()

    def user_parameter_int(self, name, val):
        self._scorep.parameter_int(name, val)

    def user_parameter_uint(self, name, val):
        self._scorep.parameter_string(name, val)

    def user_parameter_string(self, name, string):
        self._scorep.parameter_string(name, string)


def _err_exit(msg):
    sys.stderr.write("%s: %s\n" % (sys.argv[0], msg))
    sys.exit(1)


def main(argv=None):
    import getopt

    if argv is None:
        argv = sys.argv
    try:
        opts, prog_argv = getopt.getopt(argv[1:], "v",
                                        ["help", "version", "mpi"])

    except getopt.error as msg:
        sys.stderr.write("%s: %s\n" % (sys.argv[0], msg))
        sys.stderr.write("Try `%s --help' for more information\n"
                         % sys.argv[0])
        sys.exit(1)

    trace = 1
    timing = False
    mpi = False

    for opt, val in opts:
        if opt == "--help":
            _usage(sys.stdout)
            sys.exit(0)

        if opt == "--version":
            sys.stdout.write("scorep_trace 1.0\n")
            sys.exit(0)

        if opt == "--mpi":
            mpi = True

    if len(prog_argv) == 0:
        _err_exit("missing name of file to run")

    scorep = None

    if not mpi:
        scorep = __import__("_scorep")
    else:
        scorep = __import__("_scorep_mpi")

        # find the libscorep_init_mpi.so
        version = "{}.{}".format(
            sys.version_info.major,
            sys.version_info.minor)
        mpi_lib_name = "./libscorep_init_mpi-{}.so".format(version)

        scorep_subsystem = find_lib(
            mpi_lib_name, os.path.realpath(__file__), True)

        # look in ld library path
        if scorep_subsystem is None:
            ld_library_paths = os.environ['LD_LIBRARY_PATH'].split(":")
            for path in ld_library_paths:
                scorep_subsystem = find_lib(mpi_lib_name, path, False)
                if scorep_subsystem is not None:
                    break

        # look in python path
        if scorep_subsystem is None:
            python_path = os.environ['PYTHONPATH'].split(":")
            for path in python_path:
                scorep_subsystem = find_lib(mpi_lib_name, path, False)
                if scorep_subsystem is not None:
                    break

        # give up
        if scorep_subsystem is None:
            sys.stderr.write("cannot find {}.\n".format(mpi_lib_name))
            exit(-1)

        (_, scorep_location, _) = call(["which", "scorep"])

        # TODO this is dirty ... find a better way
        # can be fixed with IO branch, once release.
        path = scorep_location.replace("bin/scorep\n", "", 1).strip()
        path = path + "lib"
        scorep_libs = ["libscorep_adapter_user_event.so",
                       "libscorep_adapter_mpi_event.so",
                       "libscorep_adapter_pthread_event.so",
                       "libscorep_measurement.so",
                       "libscorep_adapter_user_mgmt.so",
                       "libscorep_adapter_mpi_mgmt.so",
                       "libscorep_mpp_mpi.so",
                       "libscorep_online_access_mpp_mpi.so",
                       "libscorep_thread_create_wait_pthread.so",
                       "libscorep_mutex_pthread_wrap.so",
                       "libscorep_alloc_metric.so",
                       "libscorep_adapter_utils.so",
                       "libscorep_adapter_pthread_mgmt.so",
                       "libscorep_adapter_compiler_event.so",
                       "libscorep_adapter_compiler_mgmt.so"]

        if cuda_support:
            scorep_libs.append("libscorep_adapter_cuda_event.so")
            scorep_libs.append("libscorep_adapter_cuda_mgmt.so")
        if opencl_support:
            scorep_libs.append("libscorep_adapter_opencl_event_static.so")
            scorep_libs.append("libscorep_adapter_opencl_mgmt_static.so")

        preload = scorep_subsystem
        for scorep_lib in scorep_libs:
            preload = preload + " " + path + "/" + scorep_lib

        if ("LD_PRELOAD" not in os.environ) or (
                "libscorep" not in os.environ["LD_PRELOAD"]):
            os.environ["LD_PRELOAD"] = preload
            """
            python -m starts the module as skript. i.e. sys.argv will loke like:
            ['/home/gocht/Dokumente/code/scorep_python/scorep.py', '--mpi', 'mpi_test.py']

            To restart python we need to remove this line, and add python -m scorep ... again
            """
            new_args = [sys.executable, "-m", "scorep"]
            for elem in sys.argv:
                if "scorep.py" in elem:
                    continue
                else:
                    new_args.append(elem)
            os.execve(sys.executable, new_args, os.environ)

    # everything is ready
    sys.argv = prog_argv
    progname = prog_argv[0]
    sys.path[0] = os.path.split(progname)[0]

    global_trace = Trace(scorep, True)
    try:
        with open(progname) as fp:
            code = compile(fp.read(), progname, 'exec')
        # try to emulate __main__ namespace as much as possible
        globs = {
            '__file__': progname,
            '__name__': '__main__',
            '__package__': None,
            '__cached__': None,
        }
        global_trace.runctx(code, globs, globs)
        # t.flush_scorep_groups()
    except OSError as err:
        _err_exit("Cannot run file %r because: %s" % (sys.argv[0], err))
    except SystemExit:
        pass


def register():
    '''
    If the module is impored using `import scorep` a call to register is requred to register the traing.
    '''
    global_trace.register()


def user_region_begin(name, file_name=None, line_number=None):
    """
    Begin of an User region. If file_name or line_number is None, both will
    bet determined automatically
    @param name name of the user region
    @param file_name file name of the user region
    @param line_number line number of the user region
    """
    if file_name is None or line_number is None:
        frame = inspect.currentframe().f_back
        file_name = frame.f_globals.get('__file__', None)
        line_number = frame.f_lineno
    if file_name is not None:
        full_file_name = os.path.abspath(file_name)
    else:
        full_file_name = "None"

    global_trace.user_region_begin(name, full_file_name, line_number)


def user_region_end(name):
    global_trace.user_region_end(name)


def oa_region_begin(name, file_name=None, line_number=None):
    """
    Begin of an Online Access region. If file_name or line_number is None, both will
    bet determined automatically
    @param name name of the user region
    @param file_name file name of the user region
    @param line_number line number of the user region
    """
    if file_name is None or line_number is None:
        frame = inspect.currentframe().f_back
        file_name = frame.f_globals.get('__file__', None)
        line_number = frame.f_lineno
    if file_name is not None:
        full_file_name = os.path.abspath(file_name)
    else:
        full_file_name = "None"

    global_trace.oa_region_begin(name, full_file_name, line_number)


def oa_region_end(name):
    global_trace.oa_region_end(name)


def user_enable_recording():
    global_trace.user_enable_recording()


def user_disable_recording():
    global_trace.user_disable_recording()


def user_parameter_int(name, val):
    global_trace.user_parameter_int(name, val)


def user_parameter_uint(name, val):
    global_trace.user_parameter_uint(name, val)


def user_parameter_string(name, string):
    global_trace.user_parameter_string(name, string)


try:
    (_, scorep_config, _) = call(["scorep-info", "config-summary"])
except FileNotFoundError:
    sys.stderr.write(
        "Cannot find scorep-info. Please check your Score-P installation. Exiting.\n")
    exit(-1)

for line in scorep_config.split("\n"):
    if "CUDA support:" in line:
        if "yes" in line:
            cuda_support = True
        else:
            cuda_support = False
    if "OpenCL support:" in line:
        if "yes" in line:
            opencl_support = True
        else:
            opencl_support = False

if __name__ == '__main__':
    main()
else:
    '''
    If Score-P is not intialised using the tracing module (`python -m scorep <script.py>`),
    we need to make sure that, if a user call gets called, scorep is still loaded.
    Moreover, if the module is loaded with `import scorep` we can't do any mpi support anymore
    '''
    scorep = __import__("_scorep")
    global_trace = Trace(scorep, True)
