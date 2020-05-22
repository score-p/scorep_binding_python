'''
Created on 04.10.2019

@author: gocht
'''
import benchmark_helper
import pickle

bench = benchmark_helper.BenchmarkEnv(repetitions=51)
tests = ["test_1.py", "test_2.py"]
results = {}

reps_x = {}
reps_x["test_1.py"] = ["1000000", "2000000", "3000000", "4000000", "5000000"]
reps_x["test_2.py"] = ["100000", "200000", "300000", "400000", "500000"]

for test in tests:
    results[test] = {"profile": {}, "trace": {}, "dummy": {}, "None": {}}
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
