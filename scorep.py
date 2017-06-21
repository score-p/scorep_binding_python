#!/usr/bin/python3.5

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


class Trace:
    def __init__(self, _scorep, trace=1):
        """
        @param trace true if there shall be any tracing at all
        """
        self.pathtobasename = {} # for memoizing os.path.basename
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
        if globals is None: globals = {}
        if locals is None: locals = {}
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
            if self.trace and code.co_name is not "_unsettrace":
                self._scorep.region_begin("%s:%s"% (modulename, code.co_name))
            return self.localtrace
        else:
            return None


    def localtrace_trace(self, frame, why, arg):
        if why == "return":
            code = frame.f_code
            modulename = frame.f_globals.get('__name__', None)
            if self.trace:
                self._scorep.region_end("%s:%s"% (modulename, code.co_name))
        return self.localtrace
    
    def flush_scorep_groups(self):
        modules = sys.modules.keys()
        with open(self._scorep.get_expiriment_dir_name() + "/scorep.fgp","w") as f:
            f.write("""
BEGIN OPTIONS
        MATCHING_STRATEGY=FIRST
        CASE_SENSITIVITY_FUNCTION_NAME=NO
        CASE_SENSITIVITY_MANGLED_NAME=NO
        CASE_SENSITIVITY_SOURCE_FILE_NAME=NO
END OPTIONS\n""")
            for module in sorted(modules,reverse=True):
                f.write("BEGIN FUNCTION_GROUP {}\n".format(module))
                f.write("\tNAME={}*\n".format(module))
                f.write("END FUNCTION_GROUP\n")
                

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
        
        scorep_subsystem = "/usr/local/lib/libscorep_init_mpi.so"
        
        p = subprocess.Popen(["which","scorep"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        p.wait()
        if p.returncode != 0:
            raise Exception("which scorep: " + stderr.decode("utf-8"))
        #TODO this is dirty ... find a better way
        path = stdout.decode("utf-8").replace("bin/scorep\n","",1).strip()
        path = path + "lib"
        scorep_libs = [ "libscorep_adapter_user_event.so.0",
            "libscorep_adapter_cuda_event.so.0",
            "libscorep_adapter_opencl_event_static.so.0",
            "libscorep_adapter_mpi_event.so.0",
            "libscorep_adapter_pthread_event.so.0",
            "libscorep_measurement.so.0",
            "libscorep_adapter_user_mgmt.so.0",
            "libscorep_adapter_cuda_mgmt.so.0",
            "libscorep_adapter_opencl_mgmt_static.so.0",
            "libscorep_adapter_mpi_mgmt.so.0",
            "libscorep_mpp_mpi.so.0",
            "libscorep_online_access_mpp_mpi.so.0",
            "libscorep_thread_create_wait_pthread.so.0",
            "libscorep_mutex_pthread_wrap.so.0",
            "libscorep_alloc_metric.so.0",
            "libscorep_adapter_utils.so.0",
            "libscorep_adapter_pthread_mgmt.so.0"]
        
        preload = scorep_subsystem
        for scorep_lib in scorep_libs:
            preload = preload + " " +path + "/" + scorep_lib
            
        if "LD_PRELOAD" not in os.environ:
            os.environ["LD_PRELOAD"] = preload
            os.execve(os.path.realpath(__file__), sys.argv, os.environ)
        elif("libscorep" not in os.environ["LD_PRELOAD"]): 
            os.environ["LD_PRELOAD"] = preload
            os.execve(os.path.realpath(__file__), sys.argv, os.environ)
        

    # everything is ready
    sys.argv = prog_argv
    progname = prog_argv[0]
    sys.path[0] = os.path.split(progname)[0]

    t = Trace(scorep,True)
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
        t.runctx(code, globs, globs)
        #t.flush_scorep_groups()
    except OSError as err:
        _err_exit("Cannot run file %r because: %s" % (sys.argv[0], err))
    except SystemExit:
        pass

def user_region_begin(name):
    _scorep.region_begin(name)
    
def user_region_end(name):
    _scorep.region_end(name)
    
def user_enable_recording():
    _scorep.enable_recording()

def user_disable_recording():
    _scorep.disable_recording()
    
def user_parameter_int(name, val):
    _scorep.parameter_int(name, val)

def user_parameter_uint(name, val):
    _scorep.parameter_string(name, val)

def user_parameter_string(name, string):
    _scorep.parameter_string(name, string)

if __name__=='__main__':
    main()

