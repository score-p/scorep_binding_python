'''
Created on 04.10.2019

@author: gocht
'''
import benchmark_helper
import pickle

bench = benchmark_helper.BenchmarkEnv()
tests = ["test_1.py", "test_2.py"]
resutls = {}

for test in tests:
    resutls[test] = {"profile": {}, "trace": {}, "dummy": {}}
    for elem in resutls[test]:
        scorep_settings = ["--instrumenter-type={}".format(elem)]
        print("#########")
        print("{}: {}".format(test, scorep_settings))
        print("#########")
        for reps in ["1000", "10000", "100000", "1000000", "10000000"]:
            times = bench.call(
                test,
                [reps],
                scorep_settings=scorep_settings)
            resutls[test][elem][reps] = times
            print("{:<8}: {}".format(reps, times))

with open("resutls.pkl", "wb") as f:
    pickle.dump(resutls,f)
