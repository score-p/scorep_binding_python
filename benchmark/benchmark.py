'''
Created on 04.10.2019

@author: gocht
'''
import benchmark_helper
import pickle

bench = benchmark_helper.BenchmarkEnv(repetitions=11)
tests = ["test_1.py", "test_2.py"]
results = {}

for test in tests:
    results[test] = {"profile": {}, "trace": {}, "dummy": {}, "None": {}}
    for instrumenter in results[test]:
        if instrumenter is "None":
            enable_scorep = False
            scorep_settings = []
        else:
            enable_scorep = True
            scorep_settings = ["--instrumenter-type={}".format(instrumenter)]

        print("#########")
        print("{}: {}".format(test, scorep_settings))
        print("#########")
        for reps in ["1000", "10000", "100000", "1000000", "10000000"]:
            times = bench.call(
                test,
                [reps],
                enable_scorep,
                scorep_settings=scorep_settings)
            results[test][instrumenter][reps] = times
            print("{:<8}: {}".format(reps, times))

with open("results.pkl", "wb") as f:
    pickle.dump(results, f)
