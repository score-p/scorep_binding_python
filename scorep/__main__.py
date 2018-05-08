#!/usr/bin/env python

# Copyright 2017-2018, Technische Universitaet Dresden, Germany, all rights reserved.
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

import os
import sys

import scorep.strace
import scorep.helper
import importlib

def _usage(outfile):
    outfile.write("""TODO
""" % sys.argv[0])

global_trace = None

cuda_support = None
opencl_support = None

def _err_exit(msg):
    sys.stderr.write("%s: %s\n" % (sys.argv[0], msg))
    sys.exit(1)

try:
    (_, scorep_config, _) = scorep.helper.call(["scorep-info", "config-summary"])
except OSError as err:
    sys.stderr.write(
        "Cannot open scorep-info. Please check your Score-P installation.\nError was: {}\nExiting.\n".format(err))
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

    scorep_bindings = None
    
    """
    look for vampir_groups_writer, which will produce a groups file for vampir.
    This allows collored output.
    """
    vampir_groups_writer_lib = "libscorep_substrate_vampir_groups_writer.so"
    vampir_groups_writer = None
    ld_library_paths = os.environ['LD_LIBRARY_PATH'].split(":")
    for path in ld_library_paths:
        vampir_groups_writer = scorep.helper.find_lib(vampir_groups_writer_lib, path, False)
        if vampir_groups_writer is not None:
            break
    
    if vampir_groups_writer is not None:
        if ("SCOREP_SUBSTRATE_PLUGINS" not in os.environ) or (os.environ["SCOREP_SUBSTRATE_PLUGINS"]==""):
            os.environ["SCOREP_SUBSTRATE_PLUGINS"] = "vampir_groups_writer"
        else:
            os.environ["SCOREP_SUBSTRATE_PLUGINS"] += ",vampir_groups_writer"
    

    if not mpi:
        scorep_bindings = importlib.import_module("scorep.scorep_bindings")
    else:
        if ("LD_PRELOAD" not in os.environ) or (
                "libscorep" not in os.environ["LD_PRELOAD"]):
            ld_preload, scorep_subsystem = scorep.helper.generate_ld_preload()

            os.environ["LD_PRELOAD"] = ld_preload
            if os.environ["LD_LIBRARY_PATH"] == "":
                os.environ["LD_LIBRARY_PATH"] = os.path.dirname(
                    scorep_subsystem)
            else:
                os.environ["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"] + \
                    ":" + os.path.dirname(scorep_subsystem)

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
        else:
            scorep_bindings = importlib.import_module("scorep_bindings_mpi")

    # everything is ready
    sys.argv = prog_argv
    progname = prog_argv[0]
    sys.path[0] = os.path.split(progname)[0]

    global_trace = scorep.strace.ScorepTrace(scorep_bindings, True)
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
    except OSError as err:
        _err_exit("Cannot run file %r because: %s" % (sys.argv[0], err))
    except SystemExit:
        pass



if __name__ == '__main__':
    main()
    
else:
    '''
    If Score-P is not intialised using the tracing module (`python -m scorep <script.py>`),
    we need to make sure that, if a user call gets called, scorep is still loaded.
    Moreover, if the module is loaded with `import scorep` we can't do any mpi support anymore
    '''
    scorep_bindings = importlib.import_module("scorep.scorep_bindings")
    global_trace = scorep.strace.ScorepTrace(scorep_bindings, False)
