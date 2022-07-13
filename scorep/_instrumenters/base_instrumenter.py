__all__ = ['BaseInstrumenter']

import abc
import sys


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
    def run(self, cmd, globals=None, locals=None):
        pass

    @abc.abstractmethod
    def region_begin(self, module_name, function_name, file_name, line_number, code_object):
        pass

    @abc.abstractmethod
    def region_end(self, module_name, function_name, code_object):
        pass

    @abc.abstractmethod
    def rewind_begin(self, name, file_name=None, line_number=None):
        pass

    @abc.abstractmethod
    def rewind_end(self, name, value):
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

    @abc.abstractmethod
    def force_finalize(self):
        pass

    @abc.abstractmethod
    def reregister_exit_handler(self):
        pass
