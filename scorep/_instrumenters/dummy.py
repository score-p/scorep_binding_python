__all__ = ['ScorepDummy']

import scorep._instrumenters.base_instrumenter as base_instrumenter


class ScorepDummy(base_instrumenter.BaseInstrumenter):
    def __init__(self, enable_instrumenter=True):
        pass

    def register(self):
        pass

    def unregister(self):
        pass

    def get_registered(self):
        return None

    def run(self, cmd, globals=None, locals=None):
        if globals is None:
            globals = {}
        if locals is None:
            locals = {}
        exec(cmd, globals, locals)

    def try_region_begin(self, code_object):
        pass

    def region_begin(self, module_name, function_name, file_name, line_number, code_object=None):
        pass

    def try_region_end(self, code_object):
        pass

    def region_end(self, module_name, function_name, code_object=None):
        pass

    def rewind_begin(self, name, file_name=None, line_number=None):
        pass

    def rewind_end(self, name, value):
        pass

    def user_enable_recording(self):
        pass

    def user_disable_recording(self):
        pass

    def user_parameter_int(self, name, val):
        pass

    def user_parameter_uint(self, name, val):
        pass

    def user_parameter_string(self, name, string):
        pass

    def force_finalize(self):
        pass

    def reregister_exit_handler(self):
        pass
