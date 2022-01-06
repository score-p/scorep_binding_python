__all__ = ['ScorepTrace']

import sys
from scorep._instrumenters.utils import get_module_name
from scorep._instrumenters.scorep_instrumenter import ScorepInstrumenter
import scorep._bindings

try:
    import threading
except ImportError:
    _settrace = sys.settrace

    def _unsettrace():
        sys.settrace(None)

else:
    def _settrace(func):
        threading.settrace(func)
        sys.settrace(func)

    def _unsettrace():
        sys.settrace(None)
        threading.settrace(None)


class ScorepTrace(ScorepInstrumenter):
    def _enable_instrumenter(self):
        _settrace(self._globaltrace)

    def _disable_instrumenter(self):
        _unsettrace()

    def _globaltrace(self, frame, why, arg):
        """Handler for call events.
        @return self.localtrace or None
        """
        if why == 'call':
            code = frame.f_code
            if not scorep._bindings.try_region_begin(code):
                if not code.co_name == "_unsetprofile":
                    modulename = get_module_name(frame)
                    if not modulename[:6] == "scorep":
                        full_file_name = code.co_filename
                        line_number = code.co_firstlineno
                        scorep._bindings.region_begin(modulename, code.co_name, full_file_name, line_number, code)
            return self._localtrace
        return None

    def _localtrace(self, frame, why, arg):
        if why == 'return':
            code = frame.f_code
            if not scorep._bindings.try_region_end(code):
                if not code.co_name == "_unsetprofile":
                    modulename = get_module_name(frame)
                    if not modulename[:6] == "scorep":
                        scorep._bindings.region_end(modulename, code.co_name, code)
        return self._localtrace
