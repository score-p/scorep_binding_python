#!/usr/bin/env python3

import unittest
import subprocess
import os
import shutil
import sys
import pkgutil


def call(arguments, env=os.environ.copy()):
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
        result = (
            out.returncode,
            out.stdout.decode("utf-8"),
            out.stderr.decode("utf-8"))
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


class TestScorepBindingsPython(unittest.TestCase):
    maxDiff = None
    python = sys.executable

    def assertRegex(self, in1, in2):
        if sys.version_info > (3, 5):
            super().assertRegex(in1, in2)
        else:
            super(TestScorepBindingsPython, self).assertRegexpMatches(in1, in2)

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

        out = call([self.python,
                    "-m",
                    "scorep",
                    "--nopython",
                    "test_user_regions.py"],
                   env=env)
        std_out = out[1]
        std_err = out[2]

        self.assertEqual(std_err, self.expected_std_err)
        self.assertEqual(
            std_out,
            "hello world\nhello world\nhello world3\nhello world4\n")

        out = call(["otf2-print", trace_path])
        std_out = out[1]
        std_err = out[2]

        self.assertRegex(std_out,
                         'ENTER[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region"')
        self.assertRegex(std_out,
                         'LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region"')
        self.assertRegex(std_out,
                         'ENTER[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region_2"')
        self.assertRegex(std_out,
                         'LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region_2"')
        self.assertRegex(std_out,
                         'ENTER[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo3"')
        self.assertRegex(std_out,
                         'LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo3"')
        self.assertRegex(std_out,
                         'ENTER[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region_4"')
        self.assertRegex(std_out,
                         'LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region_4"')

    def test_context(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_context"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"

        out = call([self.python,
                    "-m",
                    "scorep",
                    "--noinstrumenter",
                    "test_context.py"],
                   env=env)
        std_out = out[1]
        std_err = out[2]

        self.assertEqual(std_err, self.expected_std_err)
        self.assertEqual(std_out, "hello world\nhello world\nhello world\n")

        out = call(["otf2-print", trace_path])
        std_out = out[1]
        std_err = out[2]

        self.assertRegex(std_out,
                         'ENTER[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region"')
        self.assertRegex(std_out,
                         'LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "user:test_region"')
        self.assertRegex(std_out,
                         'ENTER[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"')
        self.assertRegex(std_out,
                         'LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"')

    def test_user_regions_no_scorep(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_user_regions_no_scorep"

        out = call([self.python,
                    "test_user_regions.py"],
                   env=env)
        std_out = out[1]
        std_err = out[2]

        self.assertEqual(std_err, self.expected_std_err)
        self.assertEqual(
            std_out,
            "hello world\nhello world\nhello world3\nhello world4\n")

    def test_user_rewind(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_user_rewind"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"

        out = call([self.python,
                    "-m",
                    "scorep",
                    "test_user_rewind.py"],
                   env=env)
        std_out = out[1]
        std_err = out[2]

        self.assertEqual(std_err, self.expected_std_err)
        self.assertEqual(std_out, "hello world\nhello world\n")

        out = call(["otf2-print", trace_path])
        std_out = out[1]
        std_err = out[2]

        self.assertRegex(std_out,
                         'MEASUREMENT_ON_OFF[ ]*[0-9 ]*[0-9 ]*Mode: OFF')
        self.assertRegex(std_out,
                         'MEASUREMENT_ON_OFF[ ]*[0-9 ]*[0-9 ]*Mode: ON')

    def test_oa_regions(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_oa_regions"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"

        out = call([self.python,
                    "-m",
                    "scorep",
                    "--nopython",
                    "test_oa_regions.py"],
                   env=env)
        std_out = out[1]
        std_err = out[2]

        self.assertEqual(std_err, self.expected_std_err)
        self.assertEqual(std_out, "hello world\n")

        out = call(["otf2-print", trace_path])
        std_out = out[1]
        std_err = out[2]

        self.assertEqual(std_err, "")
        self.assertRegex(std_out,
                         'ENTER[ ]*[0-9 ]*[0-9 ]*Region: "test_region"')
        self.assertRegex(std_out,
                         'LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "test_region"')

    def test_instrumentation(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_instrumentation"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"

        out = call([self.python,
                    "-m",
                    "scorep",
                    "--nocompiler",
                    "test_instrumentation.py"],
                   env=env)
        std_out = out[1]
        std_err = out[2]

        self.assertEqual(std_err, self.expected_std_err)
        self.assertEqual(std_out, "hello world\nbaz\nbar\n")

        out = call(["otf2-print", trace_path])
        std_out = out[1]
        std_err = out[2]

        self.assertEqual(std_err, "")
        self.assertRegex(std_out,
                         'ENTER[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"')
        self.assertRegex(std_out,
                         'LEAVE[ ]*[0-9 ]*[0-9 ]*Region: "__main__:foo"')

    @unittest.skipIf(len(pkgutil.extend_path([], "mpi4py")) == 0 or
                     len(pkgutil.extend_path([], "numpy")) == 0,
                     "no mpi4py present")
    def test_mpi(self):

        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_mpi"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"
        out = call(["mpirun",
                    "-n",
                    "2",
                    "-mca",
                    "btl",
                    "^openib",
                    self.python,
                    "-m",
                    "scorep",
                    "--mpp=mpi",
                    "--nocompiler",
                    "test_mpi.py"],
                   env=env)

        std_out = out[1]
        std_err = out[2]

        expected_std_err = ""
        expected_std_out = u"\[0[0-9]\] \[0. 1. 2. 3. 4.\]\\n\[0[0-9]] \[0. 1. 2. 3. 4.\]\\n"

        self.assertRegex(std_err,
                         '\[Score-P\] [\w/.: ]*MPI_THREAD_FUNNELED')
        self.assertRegex(std_out, expected_std_out)

        expected_std_out

    def test_call_main(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_call_main"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"
        out = call([self.python,
                    "-m",
                    "scorep",
                    "--nocompiler",
                    "test_call_main.py"],
                   env=env)
        std_out = out[1]
        std_err = out[2]

        expected_std_err = r"scorep: Someone called scorep\.__main__\.main"
        expected_std_out = ""
        self.assertRegex(std_err, expected_std_err)
        self.assertEqual(std_out, expected_std_out)

    def test_dummy(self):
        env = self.env
        env["SCOREP_EXPERIMENT_DIRECTORY"] += "/test_dummy"
        trace_path = env["SCOREP_EXPERIMENT_DIRECTORY"] + "/traces.otf2"

        out = call([self.python,
                    "-m",
                    "scorep",
                    "--instrumenter-type=dummy",
                    "test_instrumentation.py"],
                   env=env)
        std_out = out[1]
        std_err = out[2]

        self.assertEqual(std_err, self.expected_std_err)
        self.assertEqual(std_out, "hello world\nbaz\nbar\n")
        self.assertTrue(
            os.path.exists(
                env["SCOREP_EXPERIMENT_DIRECTORY"]),
            "Score-P directory exists for dummy test")

    def tearDown(self):
        shutil.rmtree(
            self.env["SCOREP_EXPERIMENT_DIRECTORY"],
            ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
