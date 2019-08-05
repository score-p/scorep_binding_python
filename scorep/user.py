import inspect
import os.path
import scorep.trace


def region_begin(name, file_name=None, line_number=None):
    """
    Begin of an User region. If file_name or line_number is None, both will
    bet determined automatically
    @param name name of the user region
    @param file_name file name of the user region
    @param line_number line number of the user region
    """
    tracer_registered = scorep.trace.get_tracer().get_registered()
    if tracer_registered:
        scorep.trace.get_tracer().unregister()

    scorep.trace.get_tracer().unregister()
    if file_name is None or line_number is None:
        frame = inspect.currentframe().f_back
        file_name = frame.f_globals.get('__file__', None)
        line_number = frame.f_lineno
    if file_name is not None:
        full_file_name = os.path.abspath(file_name)
    else:
        full_file_name = "None"

    scorep.trace.get_tracer().user_region_begin(name, full_file_name, line_number)
    if tracer_registered:
        scorep.trace.get_tracer().register()


def region_end(name):
    scorep.trace.get_tracer().user_region_end(name)


class region():
    """
    Context manager for regions:
    ```
    with region("some name"):
        do stuff
    ```
    """

    def __init__(self, region_name):
        self.region_name = region_name
        self.tracer_registered = None

    def __enter__(self):
        self.tracer_registered = scorep.trace.get_tracer().get_registered()
        if self.tracer_registered:
            scorep.trace.get_tracer().unregister()

        scorep.trace.get_tracer().unregister()
        frame = inspect.currentframe().f_back
        file_name = frame.f_globals.get('__file__', None)
        line_number = frame.f_lineno
        if file_name is not None:
            full_file_name = os.path.abspath(file_name)
        else:
            full_file_name = "None"

        scorep.trace.get_tracer().user_region_begin(
            self.region_name, full_file_name, line_number)

        if self.tracer_registered:
            scorep.trace.get_tracer().register()

    def __exit__(self, exc_type, exc_value, traceback):
        scorep.trace.get_tracer().user_region_end(self.region_name)


def rewind_begin(name, file_name=None, line_number=None):
    """
    Begin of an User region. If file_name or line_number is None, both will
    bet determined automatically
    @param name name of the user region
    @param file_name file name of the user region
    @param line_number line number of the user region
    """
    tracer_registered = scorep.trace.get_tracer().get_registered()
    if tracer_registered:
        scorep.trace.get_tracer().unregister()

    if file_name is None or line_number is None:
        frame = inspect.currentframe().f_back
        file_name = frame.f_globals.get('__file__', None)
        line_number = frame.f_lineno
    if file_name is not None:
        full_file_name = os.path.abspath(file_name)
    else:
        full_file_name = "None"

    scorep.trace.get_tracer().rewind_begin(name, full_file_name, line_number)

    if tracer_registered:
        scorep.trace.get_tracer().register()


def rewind_end(name, value):
    """
    End of an Rewind region.
    @param name name of the user region
    @param value True or False, whenether the region shall be rewinded or not.
    """
    scorep.trace.get_tracer().rewind_end(name, value)


def oa_region_begin(name, file_name=None, line_number=None):
    scorep.trace.get_tracer().unregister()
    """
    Begin of an Online Access region. If file_name or line_number is None, both will
    bet determined automatically
    @param name name of the user region
    @param file_name file name of the user region
    @param line_number line number of the user region
    """
    tracer_registered = scorep.trace.get_tracer().get_registered()
    if tracer_registered:
        scorep.trace.get_tracer().unregister()

    if file_name is None or line_number is None:
        frame = inspect.currentframe().f_back
        file_name = frame.f_globals.get('__file__', None)
        line_number = frame.f_lineno
    if file_name is not None:
        full_file_name = os.path.abspath(file_name)
    else:
        full_file_name = "None"

    scorep.trace.get_tracer().oa_region_begin(name, full_file_name, line_number)
    if tracer_registered:
        scorep.trace.get_tracer().register()


def oa_region_end(name):
    scorep.trace.get_tracer().oa_region_end(name)


def enable_recording():
    scorep.trace.get_tracer().user_enable_recording()


def disable_recording():
    scorep.trace.get_tracer().user_disable_recording()


def parameter_int(name, val):
    scorep.trace.get_tracer().user_parameter_int(name, val)


def parameter_uint(name, val):
    scorep.trace.get_tracer().user_parameter_uint(name, val)


def parameter_string(name, string):
    scorep.trace.get_tracer().user_parameter_string(name, string)
