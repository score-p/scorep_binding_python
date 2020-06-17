'''
Created on 04.10.2019

@author: gocht
'''
import sys
import benchmark_helper
import pickle
import numpy as np

tests = ["bm_baseline.py", "bm_simplefunc.py"]

instrumenters = ["profile", "trace", "dummy", "None"]
if sys.version_info.major >= 3:
    instrumenters.extend(["cProfile", "cTrace"])

# How many times the instrumented code is run during 1 test run
reps_x = {
    "bm_baseline.py": ["1000000", "2000000", "3000000", "4000000", "5000000"],
    "bm_simplefunc.py": ["100000", "200000", "300000", "400000", "500000"],
}
# How many times a test invocation is repeated (number of timings per test instance)
test_repetitions = 51

bench = benchmark_helper.BenchmarkEnv(repetitions=test_repetitions)
results = {}

for test in tests:
    results[test] = {}

    for instrumenter in instrumenters:
        results[test][instrumenter] = {}

        if instrumenter == "None":
            enable_scorep = False
            scorep_settings = []
        else:
            enable_scorep = True
            scorep_settings = ["--instrumenter-type={}".format(instrumenter)]

        print("#########")
        print("{}: {}".format(test, scorep_settings))
        print("#########")
        for reps in reps_x[test]:
            times = bench.call(test, [reps],
                               enable_scorep,
                               scorep_settings=scorep_settings)
            times = np.array(times)
            print("{:>8}: Range={:{prec}}-{:{prec}} Mean={:{prec}} Median={:{prec}}".format(
                reps, times.min(), times.max(), times.mean(), np.median(times), prec='5.4f'))
            results[test][instrumenter][reps] = times

with open("results.pkl", "wb") as f:
    pickle.dump(results, f)
