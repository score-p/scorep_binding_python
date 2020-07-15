import inspect
import os.path
import scorep.instrumenter
import functools


def region_begin(name, file_name=None, line_number=None):
    """
    Begin of an User region. If file_name or line_number is None, both will
    be determined automatically
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
        initally_registered = scorep.instrumenter.get_instrumenter().get_registered()
        with scorep.instrumenter.disable():
            if(self.user_region_name):
                # The user did specify a region name, so its a user_region
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
            elif callable(self.func) and not initally_registered:
                # The user did not specify a region name, and it's a callable, so it's a semi instrumented region
                self.region_name = self.func.__name__
                self.module_name = self.func.__module__
                self.code_obj = self.func.__code__
                file_name = self.func.__code__.co_filename
                line_number = self.func.__code__.co_firstlineno

                if file_name is not None:
                    full_file_name = os.path.abspath(file_name)
                else:
                    full_file_name = "None"

                scorep.instrumenter.get_instrumenter().region_begin(
                    self.module_name, self.region_name, full_file_name, line_number, self.code_obj)
            elif callable(self.func) and initally_registered:
                # The user did not specify a region name, and it's a callable, so it's a
                # semi instrumented region. However, the instrumenter is active, so there
                # is nothing to do.
                pass
            else:
                # The user did not specify a region name, and it's not a callable. So it
                # is a context region without a region name. Throw an error.
                raise RuntimeError("A region name needs to be specified.")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        initally_registered = scorep.instrumenter.get_instrumenter().get_registered()
        if self.user_region_name:
            # The user did specify a region name, so its a user_region
            scorep.instrumenter.get_instrumenter().region_end(
                self.module_name, self.region_name)
        elif callable(self.func) and not initally_registered:
            # The user did not specify a region name, and it's a callable, so it's a semi instrumented region
            scorep.instrumenter.get_instrumenter().region_end(
                self.module_name, self.region_name, self.code_obj)
        elif callable(self.func) and initally_registered:
            # The user did not specify a region name, and it's a callable, so it's a
            # semi instrumented region. However, the instrumenter is active, so there
            # is nothing to do.
            pass
        else:
            # The user did not specify a region name, and it's not a callable. So it
            # is a context region without a region name. Throw an error.
            raise RuntimeError("Something wen't wrong. Please do a Bug Report.")
        return False


def rewind_begin(name, file_name=None, line_number=None):
    """
    Begin of an User region. If file_name or line_number is None, both will
    be determined automatically
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
    be determined automatically
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
