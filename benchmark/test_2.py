'''
Created on 04.10.2019

@author: gocht
'''
import sys


def add(val):
    return val + 1


result = 0
for i in range(int(sys.argv[1])):
    result = add(result)
print(result)
