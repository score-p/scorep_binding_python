from scorep._instrumenters.scorep_instrumenter import ScorepInstrumenter
from scorep import scorep_bindings


class ScorepCProfile(scorep_bindings.CInstrumenter, ScorepInstrumenter):
    def __init__(self, enable_instrumenter):
        scorep_bindings.CInstrumenter.__init__(self, tracingOrProfiling=False)
        ScorepInstrumenter.__init__(self, enable_instrumenter)
