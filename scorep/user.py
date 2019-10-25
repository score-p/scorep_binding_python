import inspect
import os.path
import scorep.instrumenter
import functools
from scorep import instrumenter


def region_begin(name, file_name=None, line_number=None):
    """
    Begin of an User region. If file_name or line_number is None, both will
    bet determined automatically
    @param name name of the user region
    @param file_name file name of the user region
    @param line_number line number of the user region
    """
    with scorep.instrumenter.disable():
        if file_name is None or line_number is None:
            frame = inspect.currentframe().f_back
            file_name = frame.f_globals.get('__file__', None)
            line_number = frame.f_lineno
        if file_name is not None:
            full_file_name = os.path.abspath(file_name)
        else:
            full_file_name = "None"

        scorep.instrumenter.get_instrumenter().region_begin(
            "user", name, full_file_name, line_number)


def region_end(name):
    scorep.instrumenter.get_instrumenter().region_end("user", name)


class region(object):
    """
    Context manager or decorator for regions:
    ```
    with region("some name"):
        do stuff

    @region()
    def fun():
        do stuff
    ```

    details for decorator stuff:
    https://github.com/python/cpython/blob/3.8/Lib/contextlib.py#L71

    """

    def __init__(self, region_name=""):
        self.region_name = region_name
        if region_name == "":
            self.user_region_name = False
        else:
            self.user_region_name = True
        self.module_name = ""
        self.func = None

    def _recreate_cm(self):
        return self

    def __call__(self, func):
        with scorep.instrumenter.disable():
            self.func = func

            @functools.wraps(func)
            def inner(*args, **kwds):
                with self._recreate_cm():
                    return func(*args, **kwds)

            return inner

    def __enter__(self):
        initally_registered = instrumenter.get_instrumenter().get_registered()
        with scorep.instrumenter.disable():
            if(self.user_region_name):
                self.module_name = "user"
                frame = inspect.currentframe().f_back
                file_name = frame.f_globals.get('__file__', None)
                line_number = frame.f_lineno
                if file_name is not None:
                    full_file_name = os.path.abspath(file_name)
                else:
                    full_file_name = "None"

                scorep.instrumenter.get_instrumenter().region_begin(
                    self.module_name, self.region_name, full_file_name, line_number)
            elif(callable(self.func)):
                """
                looks like the decorator is invoked
                """
                if not initally_registered:
                    self.region_name = self.func.__name__
                    self.module_name = self.func.__module__
                    file_name = self.func.__code__.co_filename
                    line_number = self.func.__code__.co_firstlineno

                    if file_name is not None:
                        full_file_name = os.path.abspath(file_name)
                    else:
                        full_file_name = "None"

                    scorep.instrumenter.get_instrumenter().region_begin(
                        self.module_name, self.region_name, full_file_name, line_number)
                else:
                    """
                    do not need to decorate a function, when we are registerd. It is instrumented any way.
                    """
                    pass
            else:
                raise RuntimeError("a region name needs to be specified")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if (callable(self.func)
            and instrumenter.get_instrumenter().get_registered()
                and not self.user_region_name):
            """
            looks like there is a decorator, we are registered and the name is not specified by the user,
            so we do not need to do anything. The Instrumentation will take care.
            """
            return False
        else:
            scorep.instrumenter.get_instrumenter().region_end(
                self.module_name, self.region_name)
            return False


def rewind_begin(name, file_name=None, line_number=None):
    """
    Begin of an User region. If file_name or line_number is None, both will
    bet determined automatically
    @param name name of the user region
    @param file_name file name of the user region
    @param line_number line number of the user region
    """
    with scorep.instrumenter.disable():
        if file_name is None or line_number is None:
            frame = inspect.currentframe().f_back
            file_name = frame.f_globals.get('__file__', None)
            line_number = frame.f_lineno
        if file_name is not None:
            full_file_name = os.path.abspath(file_name)
        else:
            full_file_name = "None"

        scorep.instrumenter.get_instrumenter().rewind_begin(
            name, full_file_name, line_number)


def rewind_end(name, value):
    """
    End of an Rewind region.
    @param name name of the user region
    @param value True or False, whenether the region shall be rewinded or not.
    """
    scorep.instrumenter.get_instrumenter().rewind_end(name, value)


def oa_region_begin(name, file_name=None, line_number=None):
    """
    Begin of an Online Access region. If file_name or line_number is None, both will
    bet determined automatically
    @param name name of the user region
    @param file_name file name of the user region
    @param line_number line number of the user region
    """

    with scorep.instrumenter.disable():

        if file_name is None or line_number is None:
            frame = inspect.currentframe().f_back
            file_name = frame.f_globals.get('__file__', None)
            line_number = frame.f_lineno
        if file_name is not None:
            full_file_name = os.path.abspath(file_name)
        else:
            full_file_name = "None"

        scorep.instrumenter.get_instrumenter().oa_region_begin(
            name, full_file_name, line_number)


def oa_region_end(name):
    scorep.instrumenter.get_instrumenter().oa_region_end(name)


def enable_recording():
    scorep.instrumenter.get_instrumenter().user_enable_recording()


def disable_recording():
    scorep.instrumenter.get_instrumenter().user_disable_recording()


def parameter_int(name, val):
    scorep.instrumenter.get_instrumenter().user_parameter_int(name, val)


def parameter_uint(name, val):
    scorep.instrumenter.get_instrumenter().user_parameter_uint(name, val)


def parameter_string(name, string):
    scorep.instrumenter.get_instrumenter().user_parameter_string(name, string)
