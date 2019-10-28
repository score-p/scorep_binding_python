'''
Created on 04.10.2019

@author: gocht
'''
import sys


def add(val):
    return val + 1


result = 0
iterations = int(sys.argv[1])
iteration_list = list(range(iterations))

for i in iteration_list:
    result = add(result)

assert(result == iterations)
