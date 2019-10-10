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
    results[test] = {"profile": {}, "trace": {}, "dummy": {}}
    for elem in results[test]:
        scorep_settings = ["--instrumenter-type={}".format(elem)]
        print("#########")
        print("{}: {}".format(test, scorep_settings))
        print("#########")
        for reps in ["1000", "10000", "100000", "1000000", "10000000"]:
            times = bench.call(
                test,
                [reps],
                scorep_settings=scorep_settings)
            results[test][elem][reps] = times
            print("{:<8}: {}".format(reps, times))

with open("results.pkl", "wb") as f:
    pickle.dump(results,f)
