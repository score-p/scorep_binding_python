import subprocess
import os
import shutil
import sys
import time


class BenchmarkEnv():
    def __init__(self, repetitions=10):
        self.env = os.environ.copy()
        self.env["SCOREP_ENABLE_PROFILING"] = "false"
        self.env["SCOREP_ENABLE_TRACING"] = "false"
        self.env["SCOREP_PROFILING_MAX_CALLPATH_DEPTH"] = "98"
        self.env["SCOREP_TOTAL_MEMORY"] = "3G"
        self.exp_dir = "benchmark_dir"
        self.repetitions = repetitions

        shutil.rmtree(
            self.exp_dir,
            ignore_errors=True)
        os.mkdir(self.exp_dir)

    def __del__(self):
        pass
#         shutil.rmtree(
#             self.exp_dir,
#             ignore_errors=True)

    def call(self, script="", ops=[], enable_scorep=True, scorep_settings=[]):
        self.env["SCOREP_EXPERIMENT_DIRECTORY"] = self.exp_dir + \
            "/{}-{}-{}".format(script, ops, scorep_settings)

        arguments = [sys.executable]
        if enable_scorep:
            arguments.extend(["-m", "scorep"])
            arguments.extend(scorep_settings)
        arguments.append(script)
        arguments.extend(ops)

        runtimes = []
        for i in range(self.repetitions):
            begin = time.time()
            print(arguments)
            out = subprocess.run(
                arguments,
                env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            end = time.time()
            assert(out.returncode == 0)

            runtime = end - begin
            runtimes.append(runtime)

        return runtimes
