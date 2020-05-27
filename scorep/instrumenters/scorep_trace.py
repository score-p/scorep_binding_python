__all__ = ['ScorepTrace']

import sys
import inspect
import os.path
import scorep.instrumenters.base_instrumenter as base_instrumenter

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


class ScorepTrace(base_instrumenter.BaseInstrumenter):
    def __init__(self, scorep_bindings, enable_instrumenter=True):
        """
        @param enable_instrumenter true if the tracing shall be initialised.
            Please note, that it is still possible to enable the tracing later using register()
        """
        global global_instrumenter
        global_instrumenter = self
        self.tracer_registered = False

        self.scorep_bindings = scorep_bindings
        self.globaltrace = self.globaltrace_lt
        self.localtrace = self.localtrace_trace
        self.enable_instrumenter = enable_instrumenter

    def register(self):
        self.tracer_registered = True
        _settrace(self.globaltrace)

    def unregister(self):
        _unsettrace()
        self.tracer_registered = False

    def get_registered(self):
        return self.tracer_registered

    def run(self, cmd, globals=None, locals=None):
        if globals is None:
            globals = {}
        if locals is None:
            locals = {}
        if self.enable_instrumenter:
            self.register()
        try:
            exec(cmd, globals, locals)
        finally:
            self.unregister()

    def globaltrace_lt(self, frame, why, arg):
        """Handler for call events.
        @return self.localtrace or None
        """
        if why == 'call':
            code = frame.f_code
            modulename = base_instrumenter.get_module_name(frame)
            if not code.co_name == "_unsettrace" and not modulename[:6] == "scorep":
                full_file_name = base_instrumenter.get_file_name(frame)
                line_number = code.co_firstlineno
                self.scorep_bindings.region_begin(
                    modulename, code.co_name, full_file_name, line_number)
                return self.localtrace
        return None

    def localtrace_trace(self, frame, why, arg):
        if why == 'return':
            code = frame.f_code
            modulename = base_instrumenter.get_module_name(frame)
            self.scorep_bindings.region_end(modulename, code.co_name)
        return self.localtrace

    def region_begin(self, module_name, function_name, file_name, line_number):
        self.scorep_bindings.region_begin(
            module_name, function_name, file_name, line_number)

    def region_end(self, module_name, function_name):
        self.scorep_bindings.region_end(module_name, function_name)

    def rewind_begin(self, name, file_name=None, line_number=None):
        """
        Begin of an Rewind region. If file_name or line_number is None, both will
        bet determined automatically
        @param name name of the user region
        @param file_name file name of the user region
        @param line_number line number of the user region
        """
        if file_name is None or line_number is None:
            frame = inspect.currentframe().f_back
            file_name = frame.f_globals.get('__file__', None)
            line_number = frame.f_lineno
        if file_name is not None:
            full_file_name = os.path.abspath(file_name)
        else:
            full_file_name = "None"

        self.scorep_bindings.rewind_begin(name, full_file_name, line_number)

    def rewind_end(self, name, value):
        """
        End of an Rewind region.
        @param name name of the user region
        @param value True or False, whenether the region shall be rewinded or not.
        """
        self.scorep_bindings.rewind_end(name, value)

    def oa_region_begin(self, name, file_name=None, line_number=None):
        """
        Begin of an Online Access region. If file_name or line_number is None, both will
        bet determined automatically
        @param name name of the user region
        @param file_name file name of the user region
        @param line_number line number of the user region
        """
        if file_name is None or line_number is None:
            frame = inspect.currentframe().f_back
            file_name = frame.f_globals.get('__file__', None)
            line_number = frame.f_lineno
        if file_name is not None:
            full_file_name = os.path.abspath(file_name)
        else:
            full_file_name = "None"

        self.scorep_bindings.oa_region_begin(name, full_file_name, line_number)

    def oa_region_end(self, name):
        self.scorep_bindings.oa_region_end(name)

    def user_enable_recording(self):
        self.scorep_bindings.enable_recording()

    def user_disable_recording(self):
        self.scorep_bindings.disable_recording()

    def user_parameter_int(self, name, val):
        self.scorep_bindings.parameter_int(name, val)

    def user_parameter_uint(self, name, val):
        self.scorep_bindings.parameter_string(name, val)

    def user_parameter_string(self, name, string):
        self.scorep_bindings.parameter_string(name, string)
