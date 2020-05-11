__all__ = ['BaseInstrumenter']

import abc
import os
import sys


def get_module_name(frame):
    modulename = frame.f_globals.get('__name__', None)
    if modulename is None:
        # this is a NUMPY special situation, see NEP-18, and Score-P Issue
        # issues #63
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


if sys.version_info >= (3, 4):
    class _BaseInstrumenter(abc.ABC):
        pass
else:
    class _BaseInstrumenter():
        __metaclass__ = abc.ABCMeta


class BaseInstrumenter(_BaseInstrumenter):
    @abc.abstractmethod
    def register(self):
        pass

    @abc.abstractmethod
    def unregister(self):
        pass

    @abc.abstractmethod
    def get_registered(self):
        return None

    @abc.abstractmethod
    def run(self, cmd):
        pass

    @abc.abstractmethod
    def runctx(self, cmd, globals=None, locals=None):
        pass

    @abc.abstractmethod
    def runfunc(self, func, *args, **kw):
        pass

    @abc.abstractmethod
    def region_begin(self, module_name, function_name, file_name, line_number):
        pass

    @abc.abstractmethod
    def region_end(self, module_name, function_name):
        pass

    @abc.abstractmethod
    def rewind_begin(self, name, file_name=None, line_number=None):
        pass

    @abc.abstractmethod
    def rewind_end(self, name, value):
        pass

    @abc.abstractmethod
    def oa_region_begin(self, name, file_name=None, line_number=None):
        pass

    @abc.abstractmethod
    def oa_region_end(self, name):
        pass

    @abc.abstractmethod
    def user_enable_recording(self):
        pass

    @abc.abstractmethod
    def user_disable_recording(self):
        pass

    @abc.abstractmethod
    def user_parameter_int(self, name, val):
        pass

    @abc.abstractmethod
    def user_parameter_uint(self, name, val):
        pass

    @abc.abstractmethod
    def user_parameter_string(self, name, string):
        pass
