__all__ = ['ScorepDummy']


class ScorepDummy:
    def __init__(self, scorep_bindings=None, enable_instrumenter=True):
        pass

    def register(self):
        pass

    def unregister(self):
        pass

    def get_registered(self):
        return None

    def run(self, cmd):
        pass

    def runctx(self, cmd, globals=None, locals=None):
        if globals is None:
            globals = {}
        if locals is None:
            locals = {}
        exec(cmd, globals, locals)

    def runfunc(self, func, *args, **kw):
        pass

    def region_begin(self, module_name, function_name, file_name, line_number):
        pass

    def region_end(self, module_name, function_name):
        pass

    def rewind_begin(self, name, file_name=None, line_number=None):
        pass

    def rewind_end(self, name, value):
        pass

    def oa_region_begin(self, name, file_name=None, line_number=None):
        pass

    def oa_region_end(self, name):
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
