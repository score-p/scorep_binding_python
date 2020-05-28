import numpy
import scorep.instrumenter

with scorep.instrumenter.enable():
    a = [[1, 2], [3, 4]]
    b = [[1, 2], [3, 4]]

    c = numpy.dot(a, b)
    print(c)
