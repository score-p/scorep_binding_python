import argparse
import pickle
import numpy
from scipy.stats import linregress

parser = argparse.ArgumentParser(description='Compare two benchmarks.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('left', help='First input for comparison')
parser.add_argument('right', help='Second input for comparison')
parser.add_argument('-s', help='short output', action='store_false')
args = parser.parse_args()


with open(args.left, "rb") as f:
    left = pickle.load(f)

with open(args.right, "rb") as f:
    right = pickle.load(f)

if left.keys()!=right.keys():
    raise ValueError("Different Experiments")

experiment = right.keys()

for exp in experiment:
    print("\nExperiment: {}".format(exp))
    if left[exp].keys()!=right[exp].keys():
        raise ValueError("Different Instrumenters")
    instrumenters = left[exp].keys()
    
    for inst in instrumenters:
        print("\n\tInstrumenter: {}".format(inst))
        if left[exp][inst].keys()!=right[exp][inst].keys():
            raise ValueError("Different Iterations")
        iterations = left[exp][inst].keys()
        Y_left = []
        Y_right =  []
        X = []
        for it in iterations:
            left_val = left[exp][inst][it]
            right_val = right[exp][inst][it]
            if len(left_val)!=len(right_val):
                raise ValueError("Different Repetitons")

            Y_left.append(left_val)
            Y_right.append(right_val)
            X.append(numpy.full([len(left_val)], it))

            if args.s:
                print("\t\tInterations {}".format(it))
                print("\t\tMean:     {:>7.4f} s  {:>7.4f} s".format(numpy.mean(left_val), numpy.mean(right_val)))
                print("\t\tMedian:   {:>7.4f} s  {:>7.4f} s".format(numpy.quantile(left_val, 0.50), numpy.quantile(right_val, 0.50)))
                print("\t\t5%:       {:>7.4f} s  {:>7.4f} s".format(numpy.quantile(left_val, 0.05), numpy.quantile(right_val, 0.05)))
                print("\t\t95%:      {:>7.4f} s  {:>7.4f} s".format(numpy.quantile(left_val, 0.95), numpy.quantile(right_val, 0.95)))
        Y_left = numpy.asarray(Y_left,dtype=float).flatten()
        Y_right = numpy.asarray(Y_right,dtype=float).flatten()
        X = numpy.asarray(X,dtype=float).flatten()

        cost_left = linregress(X, Y_left)
        cost_right = linregress(X, Y_right)

        if args.s:
            print("")
        print("\tSlope     {:>7.4f} ns {:>7.4f} ns".format(cost_left.slope * 1e6, cost_right.slope* 1e6))
        print("\tIntercept {:>7.4f} s  {:>7.4f} s".format(cost_left.intercept, cost_right.intercept))
            
        
    
