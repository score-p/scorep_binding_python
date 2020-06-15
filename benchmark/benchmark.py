'''
Created on 04.10.2019

@author: gocht
'''
import sys
import benchmark_helper
import pickle

bench = benchmark_helper.BenchmarkEnv(repetitions=51)
tests = ["bm_baseline.py", "bm_simplefunc.py"]
results = {}

reps_x = {}
reps_x["bm_baseline.py"] = ["1000000", "2000000", "3000000", "4000000", "5000000"]
reps_x["bm_simplefunc.py"] = ["100000", "200000", "300000", "400000", "500000"]

for test in tests:
    results[test] = {"profile": {}, "trace": {}, "dummy": {}, "None": {}}
    if sys.version_info.major >= 3:
        results.update({"cProfile": {}, "cTrace": {}})

    for instrumenter in results[test]:
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
            results[test][instrumenter][reps] = times
            print("{:<8}: {}".format(reps, times))

with open("results.pkl", "wb") as f:
    pickle.dump(results, f)
