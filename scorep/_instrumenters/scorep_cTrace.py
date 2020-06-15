from scorep._instrumenters.scorep_instrumenter import ScorepInstrumenter
import scorep._bindings


class ScorepCTrace(scorep._bindings.CInstrumenter, ScorepInstrumenter):
    def __init__(self, enable_instrumenter):
        scorep._bindings.CInstrumenter.__init__(self, interface='Trace')
        ScorepInstrumenter.__init__(self, enable_instrumenter)
