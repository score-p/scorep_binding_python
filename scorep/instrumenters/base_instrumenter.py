__all__ = ['BaseInstrumenter']

import abc
import os

def get_module_name(frame):
    modulename = frame.f_globals.get('__name__', None)
    if modulename is None:
        # this is a NUMPY special situation, see NEP-18, and Score-P Issue issues #63
        if frame.f_code.co_filename == "<__array_function__ internals>":
            modulename = "numpy.__array_function__"
        else:
            modulename = "unkown"
    return modulename

def get_file_name(frame):
    file_name = frame.f_code.co_filename
    if file_name is not None:
        full_file_name = os.path.abspath(file_name)
    else:
        full_file_name = "None"
    return full_file_name


class BaseInstrumenter(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def register(self):
        pass

    @abc.abstractclassmethod
    def unregister(self):
        pass

    @abc.abstractclassmethod
    def get_registered(self):
        return None

    @abc.abstractclassmethod
    def run(self, cmd):
        pass

    @abc.abstractclassmethod
    def runctx(self, cmd, globals=None, locals=None):
        pass

    @abc.abstractclassmethod
    def runfunc(self, func, *args, **kw):
        pass

    @abc.abstractclassmethod
    def region_begin(self, module_name, function_name, file_name, line_number):
        pass

    @abc.abstractclassmethod
    def region_end(self, module_name, function_name):
        pass

    @abc.abstractclassmethod
    def rewind_begin(self, name, file_name=None, line_number=None):
        pass

    @abc.abstractclassmethod
    def rewind_end(self, name, value):
        pass

    @abc.abstractclassmethod
    def oa_region_begin(self, name, file_name=None, line_number=None):
        pass

    @abc.abstractclassmethod
    def oa_region_end(self, name):
        pass

    @abc.abstractclassmethod
    def user_enable_recording(self):
        pass

    @abc.abstractclassmethod
    def user_disable_recording(self):
        pass

    @abc.abstractclassmethod
    def user_parameter_int(self, name, val):
        pass

    @abc.abstractclassmethod
    def user_parameter_uint(self, name, val):
        pass

    @abc.abstractclassmethod
    def user_parameter_string(self, name, string):
        pass
