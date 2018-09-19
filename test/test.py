#!/usr/bin/env python3

import unittest
import subprocess
import os
import shutil


class TestScorepBindingsPython(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.env = os.environ.copy()
        self.env["SCOREP_ENABLE_PROFILING"] = "false"
        self.env["SCOREP_ENABLE_TRACING"] = "true"
        self.env["SCOREP_PROFILING_MAX_CALLPATH_DEPTH"] = "98"
        self.env["SCOREP_TOTAL_MEMORY"] = "3G"
        self.env["SCOREP_EXPERIMENT_DIRECTORY"] = "test_bindings_dir"

        self.expected_std_err = ""

        shutil.rmtree(
            self.env["SCOREP_EXPERIMENT_DIRECTORY"],
            ignore_errors=True)
        os.mkdir(self.env["SCOREP_EXPERIMENT_DIRECTORY"])

    def test_user_regions(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_user_regions"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"

        out = subprocess.run(["python3",
                              "test_user_regions.py"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=env)
        self.assertEqual(out.stderr.decode("utf-8"), self.expected_std_err)
        self.assertEqual(out.stdout.decode("utf-8"), "hello world\n")

        out = subprocess.run(["otf2-print", trace_path],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(out.stderr.decode("utf-8"), "")
        self.assertRegex(out.stdout.decode("utf-8"),
                         'ENTER[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region"')
        self.assertRegex(out.stdout.decode("utf-8"),
                         'LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region"')

    def test_oa_regions(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_oa_regions"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"

        out = subprocess.run(["python3",
                              "test_oa_regions.py"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=env)
        self.assertEqual(out.stderr.decode("utf-8"), self.expected_std_err)
        self.assertEqual(out.stdout.decode("utf-8"), "hello world\n")

        out = subprocess.run(["otf2-print", trace_path],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(out.stderr.decode("utf-8"), "")
        self.assertRegex(out.stdout.decode("utf-8"),
                         'ENTER[ ]*[0-9 ]*[0-9 ]*Region: "test_region"')
        self.assertRegex(out.stdout.decode("utf-8"),
                         'LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "test_region"')

    def test_instrumentation(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_instrumentation"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"

        out = subprocess.run(["python3",
                              "-m",
                              "scorep",
                              "test_instrumentation.py"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=env)
        self.assertEqual(out.stderr.decode("utf-8"), self.expected_std_err)
        self.assertEqual(out.stdout.decode("utf-8"), "hello world\n")

        out = subprocess.run(["otf2-print", trace_path],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(out.stderr.decode("utf-8"), "")
        self.assertRegex(out.stdout.decode("utf-8"),
                         'ENTER[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"')
        self.assertRegex(out.stdout.decode("utf-8"),
                         'LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"')

    def test_mpi(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_mpi"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"
        out = subprocess.run(["mpirun",
                              "-n",
                              "2",
                              "python3",
                              "-m",
                              "scorep",
                              "--mpi",
                              "test_mpi.py"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=env)
        expected_std_err = \
            "[Score-P] src/adapters/compiler/scorep_compiler_symbol_table_libbfd.c:118: Error: The given size cannot be used: BFD: bfd_canonicalize_symtab(): < 1\n" + \
            "[Score-P] src/adapters/compiler/scorep_compiler_symbol_table_libbfd.c:118: Error: The given size cannot be used: BFD: bfd_canonicalize_symtab(): < 1\n"

        expected_std_out = \
            "[00] [0. 1. 2. 3. 4.]\n" +\
            "[01] [0. 1. 2. 3. 4.]\n"

        # TODO
        #self.assertEqual(out.stderr.decode("utf-8"), expected_std_err)
        #self.assertEqual(out.stdout.decode("utf-8"), "hello world\n")

    def test_call_main(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_call_main"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"
        out = subprocess.run(["python3",
                              "-m",
                              "scorep",
                              "test_call_main.py"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=env)
        expected_std_err = """scorep: Someone called scorep.__main__.main(argv).
This is not supposed to happen, but might be triggered, if your application calls "sys.modules['__main__'].main".
This python stacktrace might be helpfull to find the reason:
  File "/usr/lib/python3.6/runpy.py", line 193, in _run_module_as_main
    "__main__", mod_spec)
  File "/usr/lib/python3.6/runpy.py", line 85, in _run_code
    exec(code, run_globals)
  File "/home/gocht/virtenv/test_scorep_python_3.6/lib/python3.6/site-packages/scorep/__main__.py", line 161, in <module>
    scorep_main()
  File "/home/gocht/virtenv/test_scorep_python_3.6/lib/python3.6/site-packages/scorep/__main__.py", line 143, in scorep_main
    global_trace.runctx(code, globs, globs)
  File "/home/gocht/virtenv/test_scorep_python_3.6/lib/python3.6/site-packages/scorep/trace.py", line 57, in runctx
    exec(cmd, globals, locals)
  File "test_call_main.py", line 6, in <module>
    sys.modules['__main__'].main(sys.argv)

"""
        expected_std_out = ""
        self.assertEqual(out.stderr.decode("utf-8"), expected_std_err)
        self.assertEqual(out.stdout.decode("utf-8"), expected_std_out)

    def tearDown(self):
        shutil.rmtree(
            self.env["SCOREP_EXPERIMENT_DIRECTORY"],
            ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
