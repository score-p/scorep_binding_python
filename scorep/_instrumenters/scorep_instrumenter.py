import abc
import inspect
import os
from scorep._instrumenters import base_instrumenter
import scorep._bindings


class ScorepInstrumenter(base_instrumenter.BaseInstrumenter):
    """Base class for all instrumenters using Score-P"""

    def __init__(self, enable_instrumenter=True):
        """
        @param enable_instrumenter true if the tracing shall be initialised.
            Please note, that it is still possible to enable the tracing later using register()
        """
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
        """Run the compiled command under this instrumenter.

        When the instrumenter is enabled it is registered prior to the invocation and unregistered afterwards
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

    def try_region_begin(self, code_object):
        """Tries to record a region begin event. Retruns True on success"""
        return scorep._bindings.try_region_begin(code_object)

    def region_begin(self, module_name, function_name, file_name, line_number, code_object=None):
        """Record a region begin event"""
        scorep._bindings.region_begin(
            module_name, function_name, file_name, line_number, code_object)

    def try_region_end(self, code_object):
        """Tries to record a region end event. Retruns True on success"""
        return scorep._bindings.try_region_end(code_object)

    def region_end(self, module_name, function_name, code_object=None):
        """Record a region end event"""
        scorep._bindings.region_end(module_name, function_name, code_object)

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

        scorep._bindings.rewind_begin(name, full_file_name, line_number)

    def rewind_end(self, name, value):
        """
        End of an Rewind region.
        @param name name of the user region
        @param value True or False, whenether the region shall be rewinded or not.
        """
        scorep._bindings.rewind_end(name, value)

    def user_enable_recording(self):
        """Enable writing of trace events in ScoreP"""
        scorep._bindings.enable_recording()

    def user_disable_recording(self):
        """Disable writing of trace events in ScoreP"""
        scorep._bindings.disable_recording()

    def user_parameter_int(self, name, val):
        """Record a parameter of type integer"""
        scorep._bindings.parameter_int(name, val)

    def user_parameter_uint(self, name, val):
        """Record a parameter of type unsigned integer"""
        scorep._bindings.parameter_string(name, val)

    def user_parameter_string(self, name, string):
        """Record a parameter of type string"""
        scorep._bindings.parameter_string(name, string)

    def force_finalize(self):
        scorep._bindings.force_finalize()

    def reregister_exit_handler(self):
        scorep._bindings.reregister_exit_handler()
