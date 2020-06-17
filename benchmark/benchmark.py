#!/usr/bin/env python
'''
Created on 04.10.2019

@author: gocht
'''
import argparse
import sys
import benchmark_helper
import pickle

# Available tests
tests = ["bm_baseline.py", "bm_simplefunc.py"]

# Available instrumenters
instrumenters = ["profile", "trace", "dummy", "None"]
if sys.version_info.major >= 3:
    instrumenters.extend(["cProfile", "cTrace"])

# Default values for: How many times the instrumented code is run during 1 test run
reps_x = {
    "bm_baseline.py": ["1000000", "2000000", "3000000", "4000000", "5000000"],
    "bm_simplefunc.py": ["100000", "200000", "300000", "400000", "500000"],
}


def str_to_int(s):
    try:
        return int(s)
    except ValueError:
        return int(float(s))


parser = argparse.ArgumentParser(description='Benchmark the instrumenters.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--test', '-t', metavar='TEST', nargs='+', default=tests,
                    choices=tests, help='Which test(s) to run')
parser.add_argument('--repetitions', '-r', default=51, type=str_to_int,
                    help='How many times a test invocation is repeated (number of timings per test instance)')
parser.add_argument('--loop-count', '-l', type=str_to_int, nargs='+',
                    help=('How many times the instrumented code is run during 1 test run. '
                          'Can be repeated and will create 1 test instance per argument'))
parser.add_argument('--instrumenter', '-i', metavar='INST', nargs='+', default=instrumenters,
                    choices=instrumenters, help='The instrumenter(s) to use')
parser.add_argument('--output', '-o', default='results.pkl', help='Output file for the results')
parser.add_argument('--dry-run', action='store_true', help='Print parsed arguments and exit')
args = parser.parse_args()

if args.dry_run:
    print(args)
    sys.exit(0)

bench = benchmark_helper.BenchmarkEnv(repetitions=args.repetitions)
results = {}

for test in args.test:
    results[test] = {}

    for instrumenter in args.instrumenter:
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
        loop_counts = args.loop_count if args.loop_count else reps_x[test]
        for reps in loop_counts:
            times = bench.call(test, [reps],
                               enable_scorep,
                               scorep_settings=scorep_settings)
            print("{:<8}: {}".format(reps, times))
            results[test][instrumenter][reps] = times

with open(args.output, "wb") as f:
    pickle.dump(results, f)
