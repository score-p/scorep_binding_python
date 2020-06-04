from scorep._instrumenters.scorep_instrumenter import ScorepInstrumenter
from scorep import scorep_bindings


class ScorepCTrace(scorep_bindings.CInstrumenter, ScorepInstrumenter):
    def __init__(self, enable_instrumenter):
        scorep_bindings.CInstrumenter.__init__(self, tracingOrProfiling=True)
        ScorepInstrumenter.__init__(self, enable_instrumenter)

    def _enable_instrumenter(self):
        if self._threading:
            self._threading.settrace(self)
        super()._enable_instrumenter()

    def _disable_instrumenter(self):
        super()._disable_instrumenter()
        if self._threading:
            self._threading.settrace(None)
