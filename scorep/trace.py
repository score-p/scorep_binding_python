__all__ = ['ScorepTrace']
import sys
import inspect
import os.path
import scorep.trace_dummy

try:
    import threading
except ImportError:
    _settrace = sys.setprofile

    def _unsettrace():
        sys.setprofile(None)

else:
    def _settrace(func):
        threading.setprofile(func)
        sys.setprofile(func)

    def _unsettrace():
        sys.setprofile(None)
        threading.setprofile(None)

global_trace = scorep.trace_dummy.ScorepTraceDummy()


class ScorepTrace:
    def __init__(self, scorep_bindings, trace=True):
        """
        @param trace true if the tracing shall be initialised.
            Please note, that it is still possible to enable the tracing later using register()
        """
        global global_trace
        global_trace = self

        self.scorep_bindings = scorep_bindings
        self.globaltrace = self.globaltrace_lt
        self.no_init_trace = not trace

    def register(self):
        _settrace(self.globaltrace)

    def unregister(self):
        _unsettrace()

    def run(self, cmd):
        self.runctx(cmd)

    def runctx(self, cmd, globals=None, locals=None):
        if globals is None:
            globals = {}
        if locals is None:
            locals = {}
        if not self.no_init_trace:
            self.register()
        try:
            exec(cmd, globals, locals)
        finally:
            self.unregister()

    def runfunc(self, func, *args, **kw):
        result = None
        if not self.no_init_trace:
            self.register()
        try:
            result = func(*args, **kw)
        finally:
            self.unregister()
        return result

    def globaltrace_lt(self, frame, why, arg):
        """Handler for call events.

        If the code block being entered is to be ignored, returns `None',
        else returns self.localtrace.
        """
        if why == 'call':
            code = frame.f_code
            modulename = frame.f_globals.get('__name__', None)
            if modulename is None:
                modulename = "None"
            file_name = frame.f_globals.get('__file__', None)
            if file_name is not None:
                full_file_name = os.path.abspath(file_name)
            else:
                full_file_name = "None"
            line_number = frame.f_lineno
            if not code.co_name == "_unsettrace" and not modulename == "scorep.trace":
                self.scorep_bindings.region_begin(
                    modulename, code.co_name, full_file_name, line_number)
            return
        elif why == 'return':
            code = frame.f_code
            modulename = frame.f_globals.get('__name__', None)
            if modulename is None:
                modulename = "None"
            self.scorep_bindings.region_end(modulename, code.co_name)
        else:
            return
          
    def user_region_begin(self, name, file_name=None, line_number=None):
        """
        Begin of an User region. If file_name or line_number is None, both will
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

        self.scorep_bindings.region_begin(
            "user", name, full_file_name, line_number)

    def user_region_end(self, name):
        self.scorep_bindings.region_end("user", name)

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
