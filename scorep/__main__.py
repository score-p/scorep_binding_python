import os
import sys

import scorep.instrumenter
import scorep.subsystem
from scorep.helper import print_err


def _err_exit(msg):
    print_err("scorep: " + msg)
    sys.exit(1)


def scorep_main(argv=None):
    if argv is None:
        argv = sys.argv

    scorep_config = []
    prog_argv = []
    parse_scorep_commands = True

    keep_files = False
    verbose = False
    no_default_threads = False
    no_default_compiler = False
    no_instrumenter = False
    if scorep.instrumenter.has_c_instrumenter():
        instrumenter_type = "cProfile"
    else:
        instrumenter_type = "profile"
    instrumenter_file = None

    for elem in argv[1:]:
        if parse_scorep_commands:
            if elem == "--":
                parse_scorep_commands = False
            elif elem == "--mpi":
                scorep_config.append("--mpp=mpi")
            elif elem == "--keep-files":
                keep_files = True
            elif elem == "--verbose" or elem == '-v':
                verbose = True
            elif "--thread=" in elem:
                scorep_config.append(elem)
                no_default_threads = True
            elif elem == "--nocompiler":
                scorep_config.append(elem)
                no_default_compiler = True
            elif elem == "--nopython":
                no_instrumenter = True
            elif elem == "--noinstrumenter":
                no_instrumenter = True
            elif "--instrumenter-type" in elem:
                param = elem.split("=")
                instrumenter_type = param[1]
            elif "--instrumenter-file" in elem:
                param = elem.split("=")
                instrumenter_file = param[1]
            elif elem[0] == "-":
                scorep_config.append(elem)
            else:
                prog_argv.append(elem)
                parse_scorep_commands = False
        else:
            prog_argv.append(elem)

    if not no_default_threads:
        scorep_config.append("--thread=pthread")

    if not no_default_compiler:
        scorep_config.append("--compiler")

    if len(prog_argv) == 0:
        _err_exit("Did not find a script to run")

    if os.environ.get("SCOREP_PYTHON_BINDINGS_INITIALISED") != "true":
        scorep.subsystem.init_environment(scorep_config, keep_files, verbose)
        os.environ["SCOREP_PYTHON_BINDINGS_INITIALISED"] = "true"
        """
        python -m starts the module as skript. i.e. sys.argv will loke like:
        ['/home/gocht/Dokumente/code/scorep_python/scorep.py', '--mpi', 'mpi_test.py']

        To restart python we need to remove this line, and add `python -m scorep ...` again
        """
        new_args = [sys.executable, "-m", "scorep"]
        for elem in sys.argv:
            if "scorep/__main__.py" in elem:
                continue
            else:
                new_args.append(elem)

        os.execve(sys.executable, new_args, os.environ)
    else:
        scorep.subsystem.reset_preload()

    # everything is ready
    sys.argv = prog_argv
    progname = prog_argv[0]
    sys.path[0] = os.path.split(progname)[0]

    tracer = scorep.instrumenter.get_instrumenter(not no_instrumenter,
                                                  instrumenter_type)

    if instrumenter_file:
        with open(instrumenter_file) as f:
            exec(f.read())

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

        tracer.run(code, globs, globs)
    except OSError as err:
        _err_exit("Cannot run file %r because: %s" % (sys.argv[0], err))
    finally:
        scorep.subsystem.clean_up(keep_files)


def main(argv=None):
    import traceback
    call_stack = traceback.extract_stack()
    call_stack_array = traceback.format_list(call_stack)
    call_stack_string = ""
    for elem in call_stack_array[:-1]:
        call_stack_string += elem
    _err_exit(
        "Someone called scorep.__main__.main(argv).\n"
        "This is not supposed to happen, but might be triggered, "
        "if your application calls \"sys.modules['__main__'].main\".\n"
        "This python stacktrace might be helpfull to find the reason:\n%s" %
        call_stack_string)


if __name__ == '__main__':
    scorep_main()
