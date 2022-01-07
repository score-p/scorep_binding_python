import numpy
import numpy.linalg
import scorep.instrumenter

with scorep.instrumenter.enable():
    a = []
    b = []

    for i in range(1000):
        a.append([])
        b.append([])
        for j in range(1000):
            a[i].append(i * j)
            b[i].append(i * j)

    c = numpy.dot(a, b)
    c = numpy.matmul(a, c)
    q, r = numpy.linalg.qr(c)
    print(q, r)
