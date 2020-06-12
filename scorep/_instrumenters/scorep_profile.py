__all__ = ['ScorepProfile']

import sys
from scorep._instrumenters.utils import get_module_name, get_file_name
from scorep._instrumenters.scorep_instrumenter import ScorepInstrumenter
from scorep import scorep_bindings
import inspect

try:
    import threading
except ImportError:
    _setprofile = sys.setprofile

    def _unsetprofile():
        sys.setprofile(None)

else:
    def _setprofile(func):
        threading.setprofile(func)
        sys.setprofile(func)

    def _unsetprofile():
        sys.setprofile(None)
        threading.setprofile(None)


class ScorepProfile(ScorepInstrumenter):
    def _enable_instrumenter(self):
        _setprofile(self._globaltrace)

    def _disable_instrumenter(self):
        _unsetprofile()

    def _globaltrace(self, frame, why, arg):
        """Handler for call events.

        If the code block being entered is to be ignored, returns `None',
        else returns self.localtrace.
        """
        if why == 'call':
            code = frame.f_code
            print("#########################################")
            if "arg" in frame.f_locals:
                print(code.co_name)
                print(code.co_varnames)
                print(code.co_cellvars)
                print(frame.f_globals.keys())
                print(frame.f_locals.keys())
                print(dir(frame.f_code))
                print(dir(frame.f_locals))
                #print(frame.f_globals.get('__name__', None))
            #print(code.co_name)
                #print(code.__dir__())
                #print(frame.f_locals["self"].__class__.__name__)
            #print(frame.f_globals)
            #print(frame.f_locals)
            
                #print(dir(frame.f_globals))
            
            print("#########################################")
            modulename = get_module_name(frame)
            if not code.co_name == "_unsetprofile" and not modulename[:6] == "scorep":
                full_file_name = get_file_name(frame)
                line_number = code.co_firstlineno
                scorep_bindings.region_begin(modulename, code.co_name, full_file_name, line_number)
        elif why == 'return':
            code = frame.f_code
            modulename = get_module_name(frame)
            if not code.co_name == "_unsetprofile" and not modulename[:6] == "scorep":
                scorep_bindings.region_end(modulename, code.co_name)
