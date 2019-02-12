import os
import sys
import importlib
import getopt

import scorep.trace
import scorep.helper


def _usage(outfile):
    outfile.write("""TODO
""" % sys.argv[0])


global_trace = None

cuda_support = None
opencl_support = None

def _err_exit(msg):
    sys.stderr.write("%s: %s\n" % ("scorep", msg))
    sys.exit(1)


def set_init_environment(mpi):
    """
    Set the inital needed environmet variables, to get everythin up an running.
    As a few variables interact with LD env vars, the programms needs to be restarted after this.
    The function set the env var `SCOREP_PYTHON_BINDINGS_INITALISED` to true, once it is done with
    initalising.

    @param mpi indicates if mpi is used.
    """

    """
    look for vampir_groups_writer, which will produce a groups file for vampir.
    This allows collored traces.
    """
    vampir_groups_writer_lib = "libscorep_substrate_vampir_groups_writer.so"
    vampir_groups_writer = scorep.helper.find_lib(vampir_groups_writer_lib)

    if vampir_groups_writer:
        scorep.helper.add_to_ld_library_path(
            os.path.dirname(vampir_groups_writer))
        if ("SCOREP_SUBSTRATE_PLUGINS" not in os.environ) or (
                os.environ["SCOREP_SUBSTRATE_PLUGINS"] == ""):
            os.environ["SCOREP_SUBSTRATE_PLUGINS"] = "vampir_groups_writer"
        else:
            os.environ["SCOREP_SUBSTRATE_PLUGINS"] += ",vampir_groups_writer"

    if mpi:
        if ("LD_PRELOAD" not in os.environ) or (
                "libscorep" not in os.environ["LD_PRELOAD"]):

            ld_preload, scorep_subsystem = scorep.helper.generate_ld_preload()
            scorep.helper.add_to_ld_library_path(
                os.path.dirname(scorep_subsystem))

            os.environ["LD_PRELOAD"] = ld_preload + " " + os.environ["LD_PRELOAD"]

    os.environ["SCOREP_PYTHON_BINDINGS_INITALISED"] = "true"


def scorep_main(argv=None):
    global target_code
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

    for opt in opts:
        key, value = opt
        if key == "--help":
            _usage(sys.stdout)
            sys.exit(0)

        if key == "--version":
            sys.stdout.write("scorep_trace 1.0\n")
            sys.exit(0)

        if key == "--mpi":
            mpi = True

    if len(prog_argv) == 0:
        _err_exit("missing name of file to run")

    if ("SCOREP_PYTHON_BINDINGS_INITALISED" not in os.environ) or (
            os.environ["SCOREP_PYTHON_BINDINGS_INITALISED"] != "true"):
        set_init_environment(mpi)

        """
        python -m starts the module as skript. i.e. sys.argv will loke like:
        ['/home/gocht/Dokumente/code/scorep_python/scorep.py', '--mpi', 'mpi_test.py']

        To restart python we need to remove this line, and add python -m scorep ... again
        """
        new_args = [sys.executable, "-m", "scorep"]
        for elem in sys.argv:
            if "scorep/__main__.py" in elem:
                continue
            else:
                new_args.append(elem)
        os.execve(sys.executable, new_args, os.environ)

    scorep_bindings = None
    if mpi:
        try:
            scorep_bindings = importlib.import_module(
                "scorep.scorep_bindings_mpi")
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "The MPI bindings are missing. Did you build Score-P with '--without-mpi'?")
    else:
        scorep_bindings = importlib.import_module("scorep.scorep_bindings")

    # everything is ready
    sys.argv = prog_argv
    progname = prog_argv[0]
    sys.path[0] = os.path.split(progname)[0]

    global_trace = scorep.trace.ScorepTrace(scorep_bindings, True)
    try:
        with open(progname) as fp:
            code = compile(fp.read(), progname, 'exec')
            target_code = code
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

def main(argv=None):
    import traceback
    call_stack = traceback.extract_stack()
    call_stack_array = traceback.format_list(call_stack)
    call_stack_string = ""
    for elem in call_stack_array[:-1]:
        call_stack_string+=elem
    _err_exit("Someone called scorep.__main__.main(argv).\n"
              "This is not supposed to happen, but might be triggered, if your application calls \"sys.modules['__main__'].main\".\n"
              "This python stacktrace might be helpfull to find the reason:\n%s" % call_stack_string)

if __name__ == '__main__':
    scorep_main()

else:
    '''
    If Score-P is not intialised using the tracing module (`python -m scorep <script.py>`),
    we need to make sure that, if a user call gets called, scorep is still loaded.
    Moreover, if the module is loaded with `import scorep` we can't do any mpi support anymore
    '''
    scorep_bindings = importlib.import_module("scorep.scorep_bindings")
    global_trace = scorep.trace.ScorepTrace(scorep_bindings, False)
