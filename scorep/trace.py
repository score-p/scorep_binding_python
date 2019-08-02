import logging

import scorep.trace_dummy
import scorep.trace_scorep


global_trace = None


def get_tracer(bindings=None, trace=False):
    global global_trace
    if global_trace is None:
        if bindings is None:
            global_trace = scorep.trace_dummy.DummyTrace(trace)
        else:
            global_trace = scorep.trace_scorep.ScorepTrace(bindings, trace)
    return global_trace
