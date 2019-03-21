import os
import sys
import importlib
import getopt

import scorep.trace
import scorep.helper
import scorep.subsystem


def _usage(outfile):
    outfile.write("""TODO
""" % sys.argv[0])


global_trace = None

cuda_support = None
opencl_support = None


def _err_exit(msg):
    sys.stderr.write("%s: %s\n" % ("scorep", msg))
    sys.exit(1)


def set_init_environment(scorep_config=[]):
    """
    Set the inital needed environmet variables, to get everythin up an running.
    As a few variables interact with LD env vars, the programms needs to be restarted after this.
    The function set the env var `SCOREP_PYTHON_BINDINGS_INITALISED` to true, once it is done with
    initalising.

    @param scorep_config configuration flags for score-p
    @return temp_dir to be deleted once the script is done
    """

    if ("LD_PRELOAD" in os.environ) and (
            "libscorep" in os.environ["LD_PRELOAD"]):
        raise RuntimeError("Score-P is already loaded. This should not happen at this point")

    subsystem_lib_name, temp_dir = scorep.subsystem.generate(scorep_config)
    scorep_ld_preload = scorep.helper.generate_ld_preload(scorep_config)

    scorep.helper.add_to_ld_library_path(temp_dir)
    
    preload_str = scorep_ld_preload + " " + subsystem_lib_name
    if "LD_PRELOAD" in os.environ:
        print("LD_PRELOAD is already specified. If Score-P is already loaded this might lead to errors.", file=sys.stderr)
        preload_str = preload_str + " " + os.environ["LD_PRELOAD"]
    os.environ["LD_PRELOAD"] = preload_str
    os.environ["SCOREP_PYTHON_BINDINGS_INITALISED"] = "true"


def scorep_main(argv=None):
    # print(sys.flags)
    if argv is None:
        argv = sys.argv

    scorep_config = []
    prog_argv = []
    parse_scorep_commands = True

    keep_files = False
    no_default_threads = False
    no_default_compiler = False

    for elem in argv[1:]:
        if parse_scorep_commands:
            if elem == "--mpi":
                scorep_config.append("--mpp=mpi")
            elif elem == "--keep-files":
                scorep_config.append(elem)
                keep_files = True
            elif "--thread=" in elem:
                scorep_config.append(elem)
                no_default_threads = True
            elif elem == "--nocompiler":
                scorep_config.append(elem)
                no_default_compiler = True
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

    if ("SCOREP_PYTHON_BINDINGS_INITALISED" not in os.environ) or (
            os.environ["SCOREP_PYTHON_BINDINGS_INITALISED"] != "true"):
        set_init_environment(scorep_config)

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
        "This is not supposed to happen, but might be triggered, if your application calls \"sys.modules['__main__'].main\".\n"
        "This python stacktrace might be helpfull to find the reason:\n%s" %
        call_stack_string)


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
