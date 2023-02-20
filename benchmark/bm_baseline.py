import sys

result = 0
iterations = int(sys.argv[1])

for i in range(iterations):
    result += 1

assert result == iterations
