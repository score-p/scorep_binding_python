import abc
import inspect
import os
from scorep.instrumenters import base_instrumenter


class ScorepInstrumenter(base_instrumenter.BaseInstrumenter):
    """Base class for all instrumenters using Score-P"""

    def __init__(self, scorep_bindings, enable_instrumenter=True):
        """
        @param enable_instrumenter true if the tracing shall be initialised.
            Please note, that it is still possible to enable the tracing later using register()
        """
        self._scorep_bindings = scorep_bindings
        self._tracer_registered = False
        self._enabled = enable_instrumenter

    @abc.abstractmethod
    def _enable_instrumenter(self):
        """Actually enable this instrumenter to collect events"""

    @abc.abstractmethod
    def _disable_instrumenter(self):
        """Stop this instrumenter from collecting events"""

    def register(self):
        """Register this instrumenter (collect events)"""
        if not self._tracer_registered:
            self._enable_instrumenter()
            self._tracer_registered = True

    def unregister(self):
        """Unregister this instrumenter (stop collecting events)"""
        if self._tracer_registered:
            self._disable_instrumenter()
            self._tracer_registered = False

    def get_registered(self):
        """Return whether this instrumenter is currently collecting events"""
        return self._tracer_registered

    def run(self, cmd, globals=None, locals=None):
        """
        Run the compiled command.
        Registers this instrumenter for the duration of the command and unregisters it afterwards
        """
        if globals is None:
            globals = {}
        if locals is None:
            locals = {}
        if self._enabled:
            self.register()
        try:
            exec(cmd, globals, locals)
        finally:
            self.unregister()

    def region_begin(self, module_name, function_name, file_name, line_number):
        """Record a region begin event"""
        self._scorep_bindings.region_begin(
            module_name, function_name, file_name, line_number)

    def region_end(self, module_name, function_name):
        """Record a region end event"""
        self._scorep_bindings.region_end(module_name, function_name)

    def rewind_begin(self, name, file_name=None, line_number=None):
        """
        Begin of an Rewind region. If file_name or line_number is None, both will
        be determined automatically
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

        self._scorep_bindings.rewind_begin(name, full_file_name, line_number)

    def rewind_end(self, name, value):
        """
        End of an Rewind region.
        @param name name of the user region
        @param value True or False, whenether the region shall be rewinded or not.
        """
        self._scorep_bindings.rewind_end(name, value)

    def oa_region_begin(self, name, file_name=None, line_number=None):
        """
        Begin of an Online Access region. If file_name or line_number is None, both will
        be determined automatically
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

        self._scorep_bindings.oa_region_begin(name, full_file_name, line_number)

    def oa_region_end(self, name):
        """End an Online Access region."""
        self._scorep_bindings.oa_region_end(name)

    def user_enable_recording(self):
        """Enable writing of trace events in ScoreP"""
        self._scorep_bindings.enable_recording()

    def user_disable_recording(self):
        """Disable writing of trace events in ScoreP"""
        self._scorep_bindings.disable_recording()

    def user_parameter_int(self, name, val):
        """Record a parameter of type integer"""
        self._scorep_bindings.parameter_int(name, val)

    def user_parameter_uint(self, name, val):
        """Record a parameter of type unsigned integer"""
        self._scorep_bindings.parameter_string(name, val)

    def user_parameter_string(self, name, string):
        """Record a parameter of type string"""
        self._scorep_bindings.parameter_string(name, string)
