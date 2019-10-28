__all__ = ['ScorepProfile']
import sys
import inspect
import os.path

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


class ScorepProfile:
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
        self.enable_instrumenter = enable_instrumenter

    def register(self):
        self.tracer_registered = True
        _setprofile(self.globaltrace)

    def unregister(self):
        _unsetprofile()
        self.tracer_registered = False

    def get_registered(self):
        return self.tracer_registered

    def run(self, cmd):
        self.runctx(cmd)

    def runctx(self, cmd, globals=None, locals=None):
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

    def runfunc(self, func, *args, **kw):
        result = None
        if self.enable_instrumenter:
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
            if not code.co_name == "_unsetprofile" and not modulename[:6] == "scorep":
                file_name = frame.f_globals.get('__file__', None)
                if file_name is not None:
                    full_file_name = os.path.abspath(file_name)
                else:
                    full_file_name = "None"
                line_number = frame.f_lineno
                self.scorep_bindings.region_begin(
                    modulename, code.co_name, full_file_name, line_number)
            return
        elif why == 'return':
            code = frame.f_code
            modulename = frame.f_globals.get('__name__', None)
            if modulename is None:
                modulename = "None"
            if not code.co_name == "_unsetprofile" and not modulename[:6] == "scorep":
                self.scorep_bindings.region_end(modulename, code.co_name)
        else:
            return

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
