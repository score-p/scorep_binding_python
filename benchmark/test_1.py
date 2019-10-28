import sys

result = 0
iterations = int(sys.argv[1])
iteration_list = list(range(iterations))

for i in iteration_list:
    result += 1

assert(result == iterations)
