#!/usr/bin/env python

from mpi4py import MPI
import numpy as np
import mpi4py
import instrumentation2
mpi4py.rc.thread_level = "funneled"


comm = mpi4py.MPI.COMM_WORLD

comm.Barrier()

# Prepare a vector of N=5 elements to be broadcasted...
N = 5
if comm.rank == 0:
    A = np.arange(N, dtype=np.float64)    # rank 0 has proper data
    instrumentation2.baz()
else:
    instrumentation2.bar()
    A = np.empty(N, dtype=np.float64)     # all other just an empty array

# Broadcast A from rank 0 to everybody
comm.Bcast([A, MPI.DOUBLE])

# Everybody should now have the same...
print("[%02d] %s" % (comm.rank, A))
