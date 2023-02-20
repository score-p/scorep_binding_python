import sys


def add(val):
    return val + 1


result = 0
iterations = int(sys.argv[1])

for i in range(iterations):
    result = add(result)

assert result == iterations
