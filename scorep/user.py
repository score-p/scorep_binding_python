import inspect
import os.path
import scorep.trace

from scorep.trace import global_trace

def region_begin(name, file_name=None, line_number=None):
    """
    Begin of an User region. If file_name or line_number is None, both will
    bet determined automatically
    @param name name of the user region
    @param file_name file name of the user region
    @param line_number line number of the user region
    """
    global_trace.unregister()
    if file_name is None or line_number is None:
        frame = inspect.currentframe().f_back
        file_name = frame.f_globals.get('__file__', None)
        line_number = frame.f_lineno
    if file_name is not None:
        full_file_name = os.path.abspath(file_name)
    else:
        full_file_name = "None"

    global_trace.user_region_begin(name, full_file_name, line_number)
    global_trace.register()


def region_end(name):
    global_trace.user_region_end(name)
    

def oa_region_begin(name, file_name=None, line_number=None):
    global_trace.unregister()
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

    global_trace.oa_region_begin(name, full_file_name, line_number)
    global_trace.register()


def oa_region_end(name):
    global_trace.oa_region_end(name)
    

def enable_recording():
    global_trace.user_enable_recording()


def disable_recording():
    global_trace.user_disable_recording()


def parameter_int(name, val):
    global_trace.user_parameter_int(name, val)


def parameter_uint(name, val):
    global_trace.user_parameter_uint(name, val)


def parameter_string(name, string):
    global_trace.user_parameter_string(name, string)
